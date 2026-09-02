"""Free VideoGen adapter: loop the campaign still. Overlay happens after."""

from __future__ import annotations

import logging
from pathlib import Path

from adapters.image_stub import StubImageGen
from boxes.video_encode import loop_image_mp4

logger = logging.getLogger(__name__)

DURATION_S = 5.0


class StubVideoGen:
    """~5s mp4. Prefer the campaign still; fall back to the dark card if missing."""

    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        source_image: Path | None = None,
    ) -> Path:
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        still = Path(source_image) if source_image is not None else None
        card = dest.with_suffix(".stub.png")
        try:
            if still is not None and still.is_file():
                frame = still
            else:
                StubImageGen().generate(prompt, card)
                frame = card
            loop_image_mp4(frame, dest, seconds=DURATION_S)
        finally:
            card.unlink(missing_ok=True)
        logger.info("stub video wrote %s", dest)
        return dest
