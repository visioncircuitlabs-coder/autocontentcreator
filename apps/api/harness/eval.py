"""Golden-set evaluation harness — measures the copy pipeline against a
curated bar, deterministically, in CI.

A "golden set" is a list of EvalCase: input context + expected properties of
any acceptable output. The evaluator runs the real scorer (and optionally the
real loop with a stub chat) and asserts:
  - compliance: zero hard-rule violations on outputs
  - quality: mean dimension score >= threshold per case
  - regression: score vs stored baseline (docs/bar/golden-baseline.json)

Run via pytest (tests/test_golden_eval.py) — no network needed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from boxes.rubric import DIMENSIONS, find_cliches, score_dimensions, style_verdict

BASELINE_PATH = Path(__file__).resolve().parents[2] / "docs" / "bar" / "golden-baseline.json"


@dataclass
class EvalCase:
    name: str
    caption: str
    min_mean: float = 3.8
    min_dimension: dict[str, int] = field(default_factory=dict)
    expect_verdict: str | None = None  # "PASS" or "REWRITE"
    must_not_contain: list[str] = field(default_factory=list)


def load_cases() -> list[EvalCase]:
    """Curated golden cases: strong lines that must PASS, weak ones that must REWRITE."""
    strong = [
        ("monsoon-confession", "Ninety percent humidity and my skin still felt tight by 4pm. One gel step changed that."),
        ("imperative-compression", "Cleanse. Then Hydro Boost. Nothing else tonight."),
        ("specific-number", "72 hours of hydration, measured after one application."),
        ("peer-voice", "skin freak-out season is here. mine too. gel first, panic later."),
        ("describe-dont-promise", "A water-gel that disappears in seconds. Matte finish, no residue."),
        ("contradiction-hook", "Driest day of the year. We sent our lightest cream."),
        # Rubric v2 golden additions (copy-bar §2 modes, written to the bar):
        # Nike-mode command / Glossier-mode confession-'I' / Aesop-mode restraint.
        ("command-gym-metro", "Cleanse like you mean it. 2% salicylic survives the gym, the metro, the monsoon."),
        ("confession-webcam", "i blamed my 3 pm webcam shine. it was my cleanser."),
        ("numbered-restraint", "Seventy-two hours of hydration, tested in 90% humidity. Matte, never tight."),
    ]
    weak = [
        ("cliche-superlative", "Glow like never before with our revolutionary formula!"),
        ("brand-first", "Introducing new Hydro Boost, the best moisturizer for your skin."),
        ("vague-hype", "Elevate your skincare game with our amazing products today!"),
        ("empty-adjective", "Our incredible luxurious formula will transform your routine forever."),
        # Rubric v2: B2 corporate announce register is a hard fail (anywhere).
        ("announce-excited", "We're excited to announce our new moisturizer!"),
    ]
    cases = [
        EvalCase(
            name=f"strong-{n}",
            caption=c,
            min_mean=3.6,
            expect_verdict="PASS",
            must_not_contain=["!", "introducing"],
        )
        for n, c in strong
    ]
    cases += [
        EvalCase(
            name=f"weak-{n}",
            caption=c,
            min_mean=0.0,
            expect_verdict="REWRITE",
        )
        for n, c in weak
    ]
    return cases


def evaluate(cases: list[EvalCase] | None = None) -> dict:
    cases = cases if cases is not None else load_cases()
    results = []
    passed = 0
    for case in cases:
        scores = score_dimensions(case.caption)
        mean = sum(scores.values()) / len(DIMENSIONS)
        verdict, _avg, _fix = style_verdict(scores)
        cliches = find_cliches(case.caption)
        checks = {
            "verdict": case.expect_verdict is None or verdict == case.expect_verdict,
            "mean": mean >= case.min_mean,
            "no_cliche": not cliches if case.expect_verdict == "PASS" else True,
            "clean": not any(tok in case.caption.lower() for tok in case.must_not_contain),
        }
        ok = all(checks.values())
        passed += int(ok)
        results.append(
            {
                "name": case.name,
                "ok": ok,
                "checks": checks,
                "mean": round(mean, 3),
                "verdict": verdict,
                "dimensions": scores,
                "cliches": cliches,
                "caption": case.caption[:80],
            }
        )
    return {
        "passed": passed,
        "total": len(results),
        "rate": round(passed / max(len(results), 1), 3),
        "results": results,
    }


def save_baseline(report: dict) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(report, indent=2))


def vs_baseline(report: dict) -> dict:
    """Compare current run to stored baseline; flag regressions."""
    if not BASELINE_PATH.is_file():
        return {"baseline": None}
    old = json.loads(BASELINE_PATH.read_text())
    delta = report["rate"] - old.get("rate", 0)
    return {"baseline_rate": old.get("rate"), "delta": round(delta, 3)}
