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
    assert "campaign type" in lower or "headline" in lower
    assert "super bowl" in lower or "campaign still" in lower
    assert "burst" in lower
    assert "no logo" in lower
    assert "disclaimer" in lower
    assert "neutrogena" not in lower
    assert "bathroom" in lower or "air-con" in lower


def test_video_prompt_is_product_true_and_unlocked() -> None:
    from boxes.visual import video_prompt

    prompt = video_prompt(
        _draft("Double cleanse after AC all day. Hydro Boost at night. Dermatologist tested.")
    )
    lower = prompt.lower()
    assert "five-second" in lower or "five second" in lower
    assert "jar" in lower or "lid" in lower
    assert "water gel" in lower or "hyaluronic" in lower
    assert "first frame" in lower or "campaign still" in lower or "campaign poster" in lower
    assert "frozen" in lower or "must not wander" in lower
    assert "burst" in lower
    assert "static" in lower
    assert "legal bar" in lower
    assert "watermark" in lower
    assert "neutrogena" not in lower
    assert "double cleanse after ac" not in lower
    assert "dermatologist tested" not in lower
    assert "chip" not in lower
    assert "lays" not in lower
    assert "jalapeño" not in lower and "jalapeno" not in lower


def test_chile_limon_video_is_lime_chilli_not_jalapeno() -> None:
    from boxes.visual import video_prompt, visual_prompt

    draft = _draft("Chile Limon crunch after the match.")
    still = visual_prompt(draft).lower()
    clip = video_prompt(draft).lower()
    assert "lime" in still and "chilli" in still
    assert "chip" in clip
    assert "burst" in clip or "tumble" in clip or "spill" in clip
    assert "flex" in clip or "tear" in clip or "open" in clip
    assert "static" in clip
    assert "lime" in clip and "chilli" in clip
    assert "wander" in clip
    assert "grok watermark" in clip
    assert "mind blown" not in still
    assert "dare a bite" not in still
    assert "crunch the explosion" not in still
    assert "jalapeño" not in still and "jalapeno" not in still
    assert "jalapeño" not in clip and "jalapeno" not in clip
    assert "lays" not in still
    assert "lays" not in clip
    assert "frozen" in clip


def test_monsoon_caption_stays_bright() -> None:
    from boxes.visual import visual_prompt

    lower = visual_prompt(_draft("Humidity ho, monsoon commute.")).lower()
    assert "bright" in lower
    assert "humidity ho" not in lower
