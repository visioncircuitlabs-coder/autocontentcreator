"""Golden-set eval + chaos isolation tests. No network. Deterministic."""

from __future__ import annotations

from harness.eval import evaluate, load_cases, save_baseline, vs_baseline


def test_golden_strong_captions_pass():
    report = evaluate()
    weak_ok = [r for r in report["results"] if r["name"].startswith("weak-")]
    strong = [r for r in report["results"] if not r["name"].startswith("weak-")]
    # the craft bar: strong lines clear their bar, weak lines get REWRITE
    assert all(r["ok"] for r in strong), [
        (r["name"], r["checks"], r["mean"]) for r in strong if not r["ok"]
    ]
    assert all(r["verdict"] == "REWRITE" for r in weak_ok)


def test_overall_rate_meets_bar():
    report = evaluate()
    assert report["rate"] >= 0.9, report


def test_baseline_comparison_no_regression():
    first = evaluate()
    save_baseline(first)
    second = evaluate()
    cmp = vs_baseline(second)
    assert cmp.get("delta", 0) >= 0, "deterministic scorer must never regress"


def test_golden_set_includes_rubric_v2_cases():
    """Rubric v2 golden additions: 3 new strong lines clear the bar; the B2
    announce-voice weak line gets REWRITE with emotional_truth capped."""
    report = evaluate()
    names = {r["name"] for r in report["results"]}
    v2_strong = ("strong-command-gym-metro", "strong-confession-webcam", "strong-numbered-restraint")
    assert all(n in names for n in v2_strong), sorted(names)
    assert len([n for n in names if not n.startswith("weak-")]) >= 9

    excited = next(r for r in report["results"] if r["name"] == "weak-announce-excited")
    assert excited["verdict"] == "REWRITE"
    assert excited["dimensions"]["emotional_truth"] <= 2


# --- chaos: one dead component must not take down neighbors ---

def test_chaos_one_dead_source_does_not_kill_fetch():
    from boxes.fetcher import run_fetch
    from ports import TrendSource

    class Dead(TrendSource):
        name = "dead"

        def fetch(self, query_id):
            raise RuntimeError("connection reset")

    class Alive(TrendSource):
        name = "alive"

        def fetch(self, query_id):
            return []

    out = run_fetch(sources=[Dead(), Alive()], persist=False)
    assert isinstance(out, list)  # no exception; dead logged, alive honored


def test_chaos_breaker_stops_repeated_dead_upstream_calls():
    from harness.breaker import BreakerOpen, CircuitBreaker

    br = CircuitBreaker(threshold=2, cooldown_s=999)
    attempts = {"n": 0}

    def boom():
        attempts["n"] += 1
        raise RuntimeError("429 upstream")

    for _ in range(2):
        try:
            br.call(boom)
        except RuntimeError:
            pass
    # breaker open: further calls fail fast WITHOUT invoking fn
    try:
        br.call(boom)
    except BreakerOpen:
        pass
    assert attempts["n"] == 2


def test_chaos_loop_survives_chat_exception_via_template_fallback():
    from models import Draft
    from boxes.loop import run_loop

    class ExplodingChat:
        def complete_json(self, *a, **k):
            raise RuntimeError("upstream exploded")

    good = Draft(
        draft_id="dft_x",
        brief_id="brf_x",
        caption=(
            "Hydro Boost is dermatologist tested.\n\n"
            "Always patch-test. Consult a dermatologist for skin concerns."
        ),
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=0,
    )
    out = run_loop(good, max_rounds=1, chat=ExplodingChat())
    assert out is not None  # loop completed via deterministic gates only
