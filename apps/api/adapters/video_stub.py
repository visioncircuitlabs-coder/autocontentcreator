"""Free VideoGen adapter: looping stub card. Logo/disclaimer overlay happens after."""

from __future__ import annotations

import logging
from pathlib import Path

from adapters.image_stub import StubImageGen
from boxes.video_encode import loop_image_mp4

logger = logging.getLogger(__name__)

DURATION_S = 5.0


class StubVideoGen:
    """Unlocked zone only: a ~5s mp4 of the same dark card the still stub paints."""

    def generate(self, prompt: str, out_path: Path) -> Path:
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        card = dest.with_suffix(".stub.png")
        try:
            StubImageGen().generate(prompt, card)
            loop_image_mp4(card, dest, seconds=DURATION_S)
        finally:
            card.unlink(missing_ok=True)
        logger.info("stub video wrote %s", dest)
        return dest
