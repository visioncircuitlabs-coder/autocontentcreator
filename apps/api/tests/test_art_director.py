"""Art Director — stub PNG, HTTP adapter off in stub mode, overlay in code."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from PIL import Image
import httpx
import pytest
from models import Draft

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
LOGO_NAVY = (11, 61, 145)  # #0B3D91 from fixtures/neutrogena/logo.svg
LOGO_SVG = (
    Path(__file__).resolve().parent.parent / "fixtures" / "neutrogena" / "logo.svg"
).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _free_image_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never hit a real image API. $5 budget stays closed."""
    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.delenv("IMAGE_GEN_URL", raising=False)
    monkeypatch.delenv("IMAGE_GEN_KEY", raising=False)


def _draft() -> Draft:
    return Draft(
        draft_id="dft_art_1",
        brief_id="b1",
        caption="Humidity ho, skin tight feel. Dermatologist tested.",
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def _png_bytes(color: tuple[int, int, int], size: tuple[int, int] = (1080, 1080)) -> bytes:
    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


def _open_rgb(path: Path):
    from PIL import Image

    return Image.open(path).convert("RGB")


def _has_color(
    path: Path,
    rgb: tuple[int, int, int],
    *,
    y0: float = 0.0,
    y1: float = 1.0,
    tol: int = 18,
) -> bool:
    img = _open_rgb(path)
    w, h = img.size
    top = int(h * y0)
    bot = max(top + 1, int(h * y1))
    for y in range(top, bot, 2):
        for x in range(0, w, 3):
            px = img.getpixel((x, y))
            if all(abs(px[i] - rgb[i]) <= tol for i in range(3)):
                return True
    return False


def test_stub_file_exists_and_is_png_http_not_called(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.art_director import compose

    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_GEN_URL", "https://paid.example/v1/images")
    monkeypatch.setenv("IMAGE_GEN_KEY", "sk-do-not-spend")

    http_generate_calls: list[str] = []
    posts: list[str] = []

    def boom_generate(self, prompt: str, out_path: Path) -> Path:  # noqa: ARG001
        http_generate_calls.append(prompt)
        raise AssertionError("HttpImageGen.generate must not run when IMAGE_GEN_MODE=stub")

    monkeypatch.setattr("adapters.image_http.HttpImageGen.generate", boom_generate)

    real_post = httpx.Client.post

    def spy_post(self, url, *args, **kwargs):  # noqa: ANN001
        posts.append(str(url))
        return real_post(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "post", spy_post)

    out = tmp_path / "card.png"
    result = compose(_draft(), "Humidity barrier card", out_path=out)

    path = Path(result.image_path)
    assert path.is_file()
    assert path.read_bytes()[:8] == PNG_MAGIC
    img = _open_rgb(path)
    assert img.format in (None, "PNG")
    assert path.suffix.lower() == ".png"
    assert img.size[0] >= 256 and img.size[1] >= 256
    assert http_generate_calls == []
    assert posts == []


def test_default_mode_is_stub_without_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.art_director import build_image_gen, compose

    monkeypatch.delenv("IMAGE_GEN_MODE", raising=False)
    gen = build_image_gen()
    assert type(gen).__name__ == "StubImageGen"

    result = compose(_draft(), "Monsoon commute card", out_path=tmp_path / "default.png")
    assert Path(result.image_path).read_bytes()[:8] == PNG_MAGIC


def test_imagine_adapter_saves_png_from_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_imagine import IMAGINE_URL, ImagineImageGen

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.delenv("IMAGE_GEN_MODEL", raising=False)
    payload = _png_bytes((40, 80, 120), size=(64, 64))

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == IMAGINE_URL:
            body = json.loads(request.content)
            assert body["model"] == "grok-imagine-image-2.0"
            assert body.get("aspect_ratio") == "3:4"
            assert body.get("resolution") == "2k"
            assert body.get("quality") == "medium"
            return httpx.Response(
                200, json={"data": [{"url": "https://imgen.example/out.png"}]}
            )
        if "imgen.example" in str(request.url):
            return httpx.Response(200, content=payload)
        return httpx.Response(404, text="missing")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    dest = tmp_path / "imagine.png"
    ImagineImageGen(client=client, key="xai-test").generate(
        "Photoreal still life, no text, no logo", dest
    )
    assert dest.read_bytes()[:8] == PNG_MAGIC


def test_legacy_imagine_model_maps_to_2_0(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters.image_imagine import ImagineImageGen, resolve_imagine_model

    monkeypatch.setenv("IMAGE_GEN_MODEL", "grok-imagine-image")
    gen = ImagineImageGen(key="xai-test")
    assert gen.model == "grok-imagine-image-2.0"
    assert resolve_imagine_model("grok-imagine-image") == "grok-imagine-image-2.0"
    assert resolve_imagine_model("grok-imagine-image-2.0") == "grok-imagine-image-2.0"


def test_imagine_http_error_logs_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import logging

    from adapters.image_imagine import IMAGINE_URL, ImagineImageGen

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.delenv("IMAGE_GEN_MODEL", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == IMAGINE_URL
        return httpx.Response(
            422, json={"error": {"message": "aspect_ratio 4:5 is not allowed"}}
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    from harness.breaker import IMAGE_BREAKER

    IMAGE_BREAKER.reset()
    try:
        with caplog.at_level(logging.WARNING, logger="adapters.image_imagine"):
            with pytest.raises(RuntimeError, match="Grok Imagine"):
                ImagineImageGen(client=client, key="xai-test").generate(
                    "nope", tmp_path / "imagine-fail.png"
                )
    finally:
        IMAGE_BREAKER.reset()
    assert "422" in caplog.text
    assert "aspect_ratio 4:5" in caplog.text


def test_compose_crop_covers_3x4_to_feed(tmp_path: Path) -> None:
    from PIL import Image

    class ThreeByFour:
        def generate(self, prompt: str, out_path: Path) -> Path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (768, 1024), (20, 80, 40)).save(out_path, "PNG")
            return out_path

    from boxes.art_director import compose

    result = compose(
        _draft(), "portrait still", image_gen=ThreeByFour(), out_path=tmp_path / "34.png"
    )
    assert Image.open(result.image_path).size == (1080, 1350)


def test_http_adapter_posts_prompt_size_and_bearer(tmp_path: Path) -> None:
    from adapters.image_http import HttpImageGen

    payload = _png_bytes((12, 40, 90))
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, content=payload)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    gen = HttpImageGen(
        client=client,
        url="https://image.example/v1/generate",
        key="test-key",
    )
    out = tmp_path / "http.png"
    returned = gen.generate("unlocked skincare still", out)

    assert returned == out
    assert out.read_bytes() == payload
    assert len(captured) == 1
    req = captured[0]
    assert req.method == "POST"
    assert str(req.url) == "https://image.example/v1/generate"
    assert req.headers["Authorization"] == "Bearer test-key"
    body = json.loads(req.content)
    assert body["prompt"] == "unlocked skincare still"
    assert body["size"]
    assert set(body) == {"prompt", "size"}
    assert "<svg" not in body["prompt"]
    assert LOGO_SVG not in body["prompt"]


def test_http_compose_overlays_logo_and_never_sends_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.image_http import HttpImageGen
    from boxes.art_director import compose

    monkeypatch.setenv("IMAGE_GEN_MODE", "http")
    red = _png_bytes((200, 16, 16))
    bodies: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(200, content=red)

    gen = HttpImageGen(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        url="https://image.example/v1/generate",
        key="k",
    )
    prompt = "soft gel texture, unlocked zone only"
    result = compose(_draft(), prompt, image_gen=gen, out_path=tmp_path / "http-card.png")
    path = Path(result.image_path)
    assert path.read_bytes()[:8] == PNG_MAGIC
    assert bodies == [{"prompt": prompt, "size": "1080x1350"}]
    assert not any("<svg" in (row.get("prompt") or "") for row in bodies)
    assert not any(LOGO_SVG in json.dumps(row) for row in bodies)
    assert _has_color(path, LOGO_NAVY, y0=0.0, y1=0.22)
    assert _has_color(path, (255, 255, 255), y0=0.0, y1=0.22, tol=40)
    assert _has_color(path, (200, 16, 16), y0=0.35, y1=0.75, tol=30)
    assert _has_color(path, (220, 220, 230), y0=0.88, y1=1.0, tol=40)
    assert Image.open(path).size == (1080, 1350)


def test_stub_overlay_pastes_logo_and_disclaimer(tmp_path: Path) -> None:
    from boxes.art_director import compose

    prompt = "Humidity barrier card"
    result = compose(_draft(), prompt, out_path=tmp_path / "stub-card.png")
    path = Path(result.image_path)
    assert path.read_bytes()[:8] == PNG_MAGIC
    assert _has_color(path, LOGO_NAVY, y0=0.0, y1=0.22)
    assert _has_color(path, (255, 255, 255), y0=0.0, y1=0.22, tol=40)
    assert _has_color(path, (220, 220, 230), y0=0.88, y1=1.0, tol=40)
    assert Image.open(path).size == (1080, 1350)
    assert result.caption == _draft().caption
    assert result.draft_id == "dft_art_1"


def test_compose_passes_prompt_verbatim_to_generator(tmp_path: Path) -> None:
    from PIL import Image

    seen: list[str] = []

    class Spy:
        def generate(self, prompt: str, out_path: Path) -> Path:
            seen.append(prompt)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (1080, 1080), (20, 22, 30)).save(out_path, "PNG")
            return out_path

    from boxes.art_director import compose

    prompt = "unlocked monsoon texture"
    compose(_draft(), prompt, image_gen=Spy(), out_path=tmp_path / "spy.png")
    assert seen == [prompt]


def test_http_adapter_refuses_empty_url(tmp_path: Path) -> None:
    from adapters.image_http import HttpImageGen

    gen = HttpImageGen(url="", key="k")
    with pytest.raises(RuntimeError, match="IMAGE_GEN_URL"):
        gen.generate("nope", tmp_path / "missing.png")
