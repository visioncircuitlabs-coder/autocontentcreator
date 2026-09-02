"""POST /factory/video — dedicated step, stub mp4, no publish, picture first."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from models import Draft

FTYP = b"ftyp"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PICTURE_FIRST = "Make the picture first. Then we can make a short video."


def _write_still(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1080, 1350), (18, 90, 140)).save(path, "PNG")
    return path


def _draft(**kwargs) -> Draft:
    data = dict(
        draft_id="dft_vid",
        brief_id="brf_vid",
        caption="Hydro Boost after the commute. Dermatologist tested.",
        variant=1,
        image_path=None,
        video_path=None,
        judge={"verdict": "PASS", "flag_human": False},
        rules=[],
        round=1,
    )
    data.update(kwargs)
    return Draft(**data)


def test_factory_run_does_not_film(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from db import upsert_draft
    from main import app

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    still = _write_still(tmp_path / "images" / "dft_vid.png")
    upsert_draft(_draft(image_path=str(still)))
    client = TestClient(app)
    loaded = client.get("/drafts/dft_vid").json()
    assert loaded["video_path"] in (None, "")


def test_factory_video_refuses_without_picture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from db import init_db, upsert_draft
    from main import app

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    init_db()
    upsert_draft(_draft())
    client = TestClient(app)
    res = client.post("/factory/video", json={"draft_id": "dft_vid"})
    assert res.status_code == 400
    assert res.json()["error"] == PICTURE_FIRST
    assert "stack" not in str(res.json()).lower()


def test_factory_video_refuses_fixture_pack_photo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from db import init_db, upsert_draft
    from main import app

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    init_db()
    pack = _write_still(tmp_path / "fixtures" / "lays" / "pack.png")
    upsert_draft(_draft(image_path=str(pack)))
    client = TestClient(app)
    res = client.post("/factory/video", json={"draft_id": "dft_vid"})
    assert res.status_code == 400
    assert "picture first" in res.json()["error"].lower()


def test_factory_video_stub_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from db import init_db, upsert_draft
    from main import app

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    init_db()
    still = _write_still(tmp_path / "images" / "dft_vid.png")
    upsert_draft(_draft(image_path=str(still)))
    client = TestClient(app)
    res = client.post("/factory/video", json={"draft_id": "dft_vid"})
    assert res.status_code == 200
    body = res.json()
    assert body["draft_id"] == "dft_vid"
    assert body["video_path"]
    clip = Path(body["video_path"])
    assert clip.is_file()
    raw = clip.read_bytes()
    assert raw[4:8] == FTYP
    from boxes.video_encode import mp4_duration_s

    duration = mp4_duration_s(clip)
    if duration:
        assert 4.5 <= duration <= 5.6

    served = client.get("/drafts/dft_vid/video")
    assert served.status_code == 200
    assert "video/mp4" in served.headers.get("content-type", "")
    assert served.content[4:8] == FTYP

    missing = client.post("/factory/video", json={"draft_id": "dft_nope"})
    assert missing.status_code == 404
    assert "error" in missing.json()
    assert "stack" not in str(missing.json()).lower()


def test_factory_video_refuses_to_publish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from main import app

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    monkeypatch.setenv("IMAGE_OUT_DIR", str(tmp_path / "images"))
    monkeypatch.setenv("EXPORT_DIR", str(tmp_path / "exports"))
    from db import upsert_draft

    still = _write_still(tmp_path / "images" / "dft_zip.png")
    upsert_draft(_draft(draft_id="dft_zip", image_path=str(still)))
    client = TestClient(app)
    filmed = client.post("/factory/video", json={"draft_id": "dft_zip"})
    assert filmed.status_code == 200
    res = client.get("/export/dft_zip")
    assert res.status_code == 200
    with ZipFile(BytesIO(res.content)) as zf:
        names = {name.replace("\\", "/") for name in zf.namelist()}
        assert "clip.mp4" in names
        assert "meta.json" in names
        assert "MANIFEST.json" in names
        clip = zf.read("clip.mp4")
        assert clip[4:8] == FTYP
        meta = json.loads(zf.read("meta.json"))
        assert meta["published"] is False
        assert meta["status"] == "paused"
        assert "instagram" not in json.dumps(meta).lower()
        manifest = json.loads(zf.read("MANIFEST.json"))
        assert "clip.mp4" in manifest["files"]
        preview = zf.read("preview.html").decode("utf-8").lower()
        assert "paused" in preview
        assert "not published" in preview

    paths = [getattr(route, "path", "") or "" for route in app.routes]
    assert "/factory/video" in paths
    for path in paths:
        assert "publish" not in path.lower()
        assert "instagram" not in path.lower()


def test_imagine_video_is_image_to_video_from_still(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.video_imagine import (
        POLL_BUDGET_S,
        POLL_INTERVAL_S,
        POLL_TIMEOUT_S,
        SUBMIT_TIMEOUT_S,
        ImagineVideoGen,
    )
    from adapters.video_stub import StubVideoGen
    from boxes.visual import video_prompt
    from harness.breaker import VIDEO_BREAKER

    VIDEO_BREAKER.reset()

    assert POLL_BUDGET_S == 900.0
    assert POLL_INTERVAL_S == 5.0
    assert SUBMIT_TIMEOUT_S == 60.0
    assert POLL_TIMEOUT_S == 60.0

    monkeypatch.setenv("XAI_API_KEY", "sk-test")
    monkeypatch.setenv("VIDEO_BUDGET_USD", "2.00")
    posts: list[dict] = []
    stub_bytes = tmp_path / "seed.mp4"
    still = _write_still(tmp_path / "campaign.png")
    StubVideoGen().generate("seed", stub_bytes, source_image=still)
    blob = stub_bytes.read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if request.method == "POST" and url.endswith("/videos/generations"):
            posts.append(json.loads(request.content))
            return httpx.Response(200, json={"request_id": "req-vid-1"})
        if request.method == "GET" and "/videos/req-vid-1" in url:
            return httpx.Response(
                200,
                json={
                    "status": "done",
                    "video": {
                        "url": "https://vid.example/clip.mp4",
                        "duration": 5,
                        "respect_moderation": True,
                    },
                    "usage": {"cost_in_usd_ticks": 4_000_000_000},
                },
            )
        if "clip.mp4" in url:
            return httpx.Response(200, content=blob)
        return httpx.Response(404, text="nope")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    dest = tmp_path / "imagine.mp4"
    prompt = video_prompt(_draft())
    ImagineVideoGen(client=client, key="sk-test").generate(
        prompt, dest, source_image=still
    )
    assert dest.is_file()
    assert dest.read_bytes()[4:8] == FTYP
    assert len(posts) == 1
    payload = posts[0]
    dumped = json.dumps(payload).lower()
    assert payload["duration"] == 5
    assert payload["prompt"] == prompt
    assert payload["generate_audio"] is False
    assert payload["aspect_ratio"] == "3:4"
    assert payload["resolution"] == "720p"
    assert "reference_images" not in payload
    image = payload.get("image")
    assert isinstance(image, dict)
    url = image.get("url") or ""
    assert url.startswith("data:image/png;base64,")
    assert "neutrogena" not in dumped
    assert "disclaimer" not in dumped or "disclaimer" in prompt.lower()
    assert "<svg" not in dumped
    assert "always patch-test" not in dumped
    assert "dermatologist tested" not in dumped
    assert "fixtures" not in url.lower()


def test_imagine_video_refuses_text_to_video_without_still(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.video_imagine import ImagineVideoGen

    monkeypatch.setenv("XAI_API_KEY", "sk-test")
    dest = tmp_path / "nope.mp4"
    with pytest.raises(RuntimeError, match="picture first"):
        ImagineVideoGen(key="sk-test").generate("move the jar", dest)


def test_imagine_video_refuses_fixture_pack_photo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from adapters.video_imagine import ImagineVideoGen

    monkeypatch.setenv("XAI_API_KEY", "sk-test")
    pack = _write_still(tmp_path / "fixtures" / "pack.png")
    dest = tmp_path / "nope.mp4"
    with pytest.raises(RuntimeError, match="picture first"):
        ImagineVideoGen(key="sk-test").generate(
            "animate the bag", dest, source_image=pack
        )


def test_compose_video_refuses_passed_fixture_pack(tmp_path: Path) -> None:
    from boxes.video import compose_video

    pack = _write_still(tmp_path / "fixtures" / "lays" / "pack.png")
    with pytest.raises(ValueError, match="picture first"):
        compose_video(
            _draft(image_path=str(pack)),
            "animate the bag",
            source_image=pack,
            out_path=tmp_path / "clip.mp4",
        )


def test_spent_budget_falls_back_to_stub(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.belt import film_chosen
    from boxes.video_budget import record_video_spend
    from db import upsert_draft

    monkeypatch.setenv("VIDEO_GEN_MODE", "imagine")
    monkeypatch.setenv("XAI_API_KEY", "sk-do-not-spend")
    monkeypatch.setenv("VIDEO_BUDGET_USD", "0.10")
    monkeypatch.setenv("VIDEO_OUT_DIR", str(tmp_path / "videos"))
    record_video_spend(0.40)
    still = _write_still(tmp_path / "images" / "dft_broke.png")
    upsert_draft(_draft(draft_id="dft_broke", image_path=str(still)))
    filmed = film_chosen("dft_broke")
    clip = Path(filmed.video_path)
    assert clip.is_file()
    assert clip.read_bytes()[4:8] == FTYP


def test_stub_overlay_stamps_logo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.art_director import LOGO_NAVY
    from boxes.video import compose_video
    from boxes.visual import video_prompt
    from db import upsert_draft
    from PIL import Image as PilImage

    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    still = _write_still(tmp_path / "images" / "dft_lock.png")
    upsert_draft(_draft(draft_id="dft_lock", image_path=str(still)))
    dest = tmp_path / "locked.mp4"
    result = compose_video(
        _draft(draft_id="dft_lock", image_path=str(still)),
        video_prompt(_draft()),
        out_path=dest,
        source_image=still,
    )
    assert Path(result.video_path).is_file()
    import subprocess

    frame = tmp_path / "frame.png"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(dest),
            "-vframes",
            "1",
            str(frame),
        ],
        check=True,
    )
    img = PilImage.open(frame).convert("RGB")
    w, h = img.size
    found = False
    for y in range(0, max(1, int(h * 0.22)), 2):
        for x in range(0, w, 3):
            px = img.getpixel((x, y))
            if all(abs(px[i] - LOGO_NAVY[i]) <= 18 for i in range(3)):
                found = True
                break
        if found:
            break
    assert found, "coded wordmark missing from stamped clip"
    assert w == 1080 and h == 1350


def test_campaign_still_refuses_real_chile_limon_fixture() -> None:
    from boxes.pack_photo import chile_limon_pack_photo
    from boxes.video import campaign_still

    pack = chile_limon_pack_photo()
    assert pack is not None
    assert campaign_still(_draft(image_path=str(pack))) is None


def test_chile_limon_video_skips_wordmark_and_disclaimer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.art_director import LOGO_NAVY, compose
    from boxes.video import compose_video
    from boxes.visual import video_prompt, visual_prompt
    from PIL import Image as PilImage

    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("VIDEO_GEN_MODE", "stub")
    still_path = tmp_path / "images" / "dft_lays.png"
    painted = compose(
        _draft(
            draft_id="dft_lays",
            caption="Chile Limon crunch after the match.",
        ),
        visual_prompt(
            _draft(caption="Chile Limon crunch after the match.")
        ),
        out_path=still_path,
    )
    assert "fixtures" not in {part.lower() for part in Path(painted.image_path).resolve().parts}
    dest = tmp_path / "chile-clip.mp4"
    result = compose_video(
        painted,
        video_prompt(painted),
        out_path=dest,
        source_image=painted.image_path,
    )
    assert Path(result.video_path).is_file()
    import subprocess

    frame = tmp_path / "chile-frame.png"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(dest),
            "-vframes",
            "1",
            str(frame),
        ],
        check=True,
    )
    img = PilImage.open(frame).convert("RGB")
    w, h = img.size
    assert w == 1080 and h == 1350
    navy = 0
    for y in range(0, max(1, int(h * 0.22)), 2):
        for x in range(0, w, 3):
            px = img.getpixel((x, y))
            if all(abs(px[i] - LOGO_NAVY[i]) <= 12 for i in range(3)):
                navy += 1
    assert navy == 0, "Lays clip must not stamp a second LAY'S / Neutrogena wordmark"
    dark = 0
    samples = 0
    for x in range(0, w, 6):
        px = img.getpixel((x, h - 18))
        samples += 1
        if px[0] < 30 and px[1] < 32 and px[2] < 45:
            dark += 1
    assert dark < samples * 0.35, "Lays clip must not stamp the unofficial disclaimer bar"
