from models import Draft


def _draft(caption: str) -> Draft:
    return Draft(
        draft_id="dft_vis",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def test_ad_prompt_is_bright_feed_not_night_film() -> None:
    from boxes.visual import visual_prompt

    prompt = visual_prompt(
        _draft("Double cleanse after AC all day. Hydro Boost at night. Dermatologist tested.")
    )
    lower = prompt.lower()
    assert "4:5" in lower
    assert "white" in lower and "lid" in lower
    assert "night window" not in lower
    assert "double cleanse after ac" not in lower
    assert "no text" in lower
    assert "no logo" in lower
    assert "bathroom" in lower or "air-con" in lower


def test_video_prompt_is_product_true_and_unlocked() -> None:
    from boxes.visual import video_prompt

    prompt = video_prompt(
        _draft("Double cleanse after AC all day. Hydro Boost at night. Dermatologist tested.")
    )
    lower = prompt.lower()
    assert "five-second" in lower or "five second" in lower
    assert "jar" in lower
    assert "water gel" in lower or "water-gel" in lower
    assert "first frame" in lower or "campaign still" in lower
    assert "no new text" in lower or "no text" in lower
    assert "no extra logo" in lower or "no logo" in lower
    assert "no new legal disclaimer" in lower or "no legal disclaimer" in lower
    assert "neutrogena" not in lower
    assert "double cleanse after ac" not in lower
    assert "dermatologist tested" not in lower
    assert "chip" not in lower
    assert "lays" not in lower


def test_monsoon_caption_stays_bright() -> None:
    from boxes.visual import visual_prompt

    lower = visual_prompt(_draft("Humidity ho, monsoon commute.")).lower()
    assert "bright" in lower
    assert "humidity ho" not in lower
