"""Imagine waits 10 minutes once. Timeouts must not retry or open the breaker."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from adapters.image_imagine import IMAGINE_URL


def _png() -> bytes:
    from PIL import Image
    import io

    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (20, 80, 40)).save(buf, "PNG")
    return buf.getvalue()


def test_imagine_timeout_default_is_600s(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters.image_imagine import DEFAULT_IMAGE_TIMEOUT_S, TIMEOUT_S, imagine_timeout_s

    monkeypatch.delenv("IMAGE_TIMEOUT_S", raising=False)
    assert DEFAULT_IMAGE_TIMEOUT_S == 600
    assert TIMEOUT_S == 600
    assert imagine_timeout_s() == 600.0


def test_imagine_timeout_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters.image_imagine import imagine_timeout_s

    monkeypatch.setenv("IMAGE_TIMEOUT_S", "120")
    assert imagine_timeout_s() == 120.0


def test_imagine_timeout_is_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_imagine import ImagineImageGen
    from harness.breaker import IMAGE_BREAKER

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.delenv("IMAGE_TIMEOUT_S", raising=False)
    hits = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        hits["n"] += 1
        raise httpx.ReadTimeout("slow imagine")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    IMAGE_BREAKER.reset()
    try:
        with pytest.raises(httpx.ReadTimeout):
            ImagineImageGen(client=client, key="xai-test").generate(
                "campaign still", tmp_path / "slow.png"
            )
        assert hits["n"] == 1
        assert IMAGE_BREAKER.state == "closed"
    finally:
        IMAGE_BREAKER.reset()


def test_one_imagine_timeout_does_not_open_breaker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_imagine import ImagineImageGen
    from harness.breaker import IMAGE_BREAKER

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    payload = _png()

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow imagine")

    def ok(request: httpx.Request) -> httpx.Response:
        if str(request.url) == IMAGINE_URL:
            return httpx.Response(
                200, json={"data": [{"url": "https://imgen.example/out.png"}]}
            )
        return httpx.Response(200, content=payload)

    IMAGE_BREAKER.reset()
    try:
        with pytest.raises(httpx.ReadTimeout):
            ImagineImageGen(
                client=httpx.Client(transport=httpx.MockTransport(boom)),
                key="xai-test",
            ).generate("campaign still", tmp_path / "a.png")
        assert IMAGE_BREAKER.state == "closed"
        dest = tmp_path / "b.png"
        ImagineImageGen(
            client=httpx.Client(transport=httpx.MockTransport(ok)),
            key="xai-test",
        ).generate("campaign still", dest)
        assert dest.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert IMAGE_BREAKER.state == "closed"
    finally:
        IMAGE_BREAKER.reset()


def test_imagine_5xx_retries_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_imagine import IMAGINE_RETRIES, ImagineImageGen
    from harness.breaker import IMAGE_BREAKER

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    payload = _png()
    hits = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == IMAGINE_URL:
            hits["n"] += 1
            if hits["n"] == 1:
                return httpx.Response(503, text="busy")
            return httpx.Response(
                200, json={"data": [{"url": "https://imgen.example/out.png"}]}
            )
        return httpx.Response(200, content=payload)

    IMAGE_BREAKER.reset()
    try:
        dest = tmp_path / "retry.png"
        ImagineImageGen(
            client=httpx.Client(transport=httpx.MockTransport(handler)),
            key="xai-test",
        ).generate("campaign still", dest)
        assert hits["n"] == IMAGINE_RETRIES + 1
        assert dest.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        IMAGE_BREAKER.reset()


def test_three_imagine_timeouts_open_breaker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_imagine import ImagineImageGen
    from harness.breaker import IMAGE_BREAKER

    monkeypatch.setenv("XAI_API_KEY", "xai-test")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow imagine")

    IMAGE_BREAKER.reset()
    gen = ImagineImageGen(
        client=httpx.Client(transport=httpx.MockTransport(boom)),
        key="xai-test",
    )
    try:
        for i in range(2):
            with pytest.raises(httpx.ReadTimeout):
                gen.generate("campaign still", tmp_path / f"{i}.png")
            assert IMAGE_BREAKER.state == "closed"
        with pytest.raises(httpx.ReadTimeout):
            gen.generate("campaign still", tmp_path / "third.png")
        assert IMAGE_BREAKER.state == "open"
    finally:
        IMAGE_BREAKER.reset()
