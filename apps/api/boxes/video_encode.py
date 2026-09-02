"""ffmpeg helpers for the ~5s product clip. Overlay is code, not the model."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from boxes.art_director import FEED_SIZE

logger = logging.getLogger(__name__)

FEED_W, FEED_H = FEED_SIZE


class FfmpegMissing(RuntimeError):
    """Raised when the walk cannot encode a clip because ffmpeg is not installed."""


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if not found:
        raise FfmpegMissing(
            "Could not make the short video. ffmpeg is missing on this machine."
        )
    return found


def ffprobe_bin() -> str | None:
    return shutil.which("ffprobe")


def run_ffmpeg(args: list[str], *, friendly: str) -> None:
    cmd = [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", *args]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.warning("ffmpeg failed: %s", (exc.stderr or exc.stdout or "")[:400])
        raise RuntimeError(friendly) from exc


def loop_image_mp4(image_path: Path, dest: Path, *, seconds: float = 5.0) -> Path:
    """Turn one unlocked still into a real ~5s H.264 mp4."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale={FEED_W}:{FEED_H}:force_original_aspect_ratio=increase,"
        f"crop={FEED_W}:{FEED_H},format=yuv420p"
    )
    run_ffmpeg(
        [
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            vf,
            "-r",
            "10",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(dest),
        ],
        friendly="Could not build the short video file. Try again.",
    )
    return dest


def overlay_locks_on_video(
    src: Path,
    overlay_png: Path,
    dest: Path,
    *,
    seconds: float = 5.0,
) -> Path:
    """Scale to 4:5 feed, stamp the coded legal overlay, keep ~5 seconds."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    filt = (
        f"[0:v]scale={FEED_W}:{FEED_H}:force_original_aspect_ratio=increase,"
        f"crop={FEED_W}:{FEED_H},trim=duration={seconds:.3f},setpts=PTS-STARTPTS[v];"
        f"[v][1:v]overlay=0:0"
    )
    run_ffmpeg(
        [
            "-i",
            str(src),
            "-i",
            str(overlay_png),
            "-filter_complex",
            filt,
            "-t",
            f"{seconds:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(dest),
        ],
        friendly="Could not stamp the short video. Try again.",
    )
    return dest


def mp4_duration_s(path: Path) -> float:
    """Best-effort duration. Tests use this; missing ffprobe returns 0."""
    probe = ffprobe_bin()
    if not probe:
        return 0.0
    try:
        proc = subprocess.run(
            [
                probe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return float((proc.stdout or "0").strip() or 0)
    except (subprocess.CalledProcessError, ValueError):
        return 0.0
