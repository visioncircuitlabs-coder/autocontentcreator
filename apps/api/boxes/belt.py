"""Plain-code belt. Radar then factory. Models sit inside steps. No CrewAI."""

from __future__ import annotations

import logging

import httpx

from boxes.art_director import compose
from boxes.brief import build_brief
from boxes.copywriter import run_copywriter
from boxes.fetcher import build_client, run_fetch
from boxes.loop import run_loop
from boxes.researcher import run_research
from boxes.scorer import run_score
from boxes.strategist import run_strategist
from db import upsert_concepts, upsert_draft, upsert_reports
from models import Draft, TrendReport
from obs import emit, emit_error
from ports import ChatModel, ImageGen, TrendSource

logger = logging.getLogger(__name__)

MAX_FACTORY_CONCEPTS = 1


def run_radar(
    *,
    sources: list[TrendSource] | None = None,
    client: httpx.Client | None = None,
    chat: ChatModel | None = None,
    persist: bool = True,
) -> list[TrendReport]:
    """fetch → score → research deep_dives → store reports."""
    owns = client is None
    client = client or build_client()
    try:
        emit("radar_start", chat=getattr(chat, "model", None))
        signals = run_fetch(sources=sources, client=client, persist=persist)
        scores = run_score(signals, chat=chat, persist=persist)
        gates: dict[str, int] = {}
        for score in scores:
            gates[score.gate] = gates.get(score.gate, 0) + 1
        emit(
            "radar_scored",
            n_signals=len(signals),
            gates=gates,
            chat=getattr(chat, "model", None),
            top=[
                {
                    "title": next(
                        (s.title for s in signals if s.signal_id == score.signal_id),
                        "",
                    )[:120],
                    "fit": score.brand_fit,
                    "gate": score.gate,
                    "reason": score.reason[:160],
                    "model": score.model,
                }
                for score in sorted(scores, key=lambda item: item.brand_fit, reverse=True)[
                    :8
                ]
            ],
        )
        by_id = {item.signal_id: item for item in signals}
        reports: list[TrendReport] = []
        for score in scores:
            if score.gate != "deep_dive":
                continue
            signal = by_id.get(score.signal_id)
            if signal is None:
                continue
            reports.append(
                run_research(
                    signal,
                    score,
                    chat=chat,
                    client=client,
                    persist=persist,
                )
            )
        if persist and reports:
            upsert_reports(reports)
        emit("radar_end", n_reports=len(reports), report_ids=[r.report_id for r in reports])
        logger.info("radar stored %s deep-dive reports", len(reports))
        return reports
    except Exception as exc:
        emit_error("radar_fail", exc)
        raise
    finally:
        if owns:
            client.close()


def _visual_prompt(draft: Draft) -> str:
    line = (draft.caption or "").split("\n")[0].strip()[:120]
    return f"Skincare still life, no text, no logo, no claims. Mood: {line}"


def run_factory(
    report_id: str,
    *,
    chat: ChatModel | None = None,
    image_gen: ImageGen | None = None,
) -> list[Draft]:
    """brief → strategist → copywriter → loop (rules+judge) → art_director → queue."""
    brief_id = build_brief(report_id)
    concepts = run_strategist(brief_id, chat=chat)
    upsert_concepts(concepts)
    queued: list[Draft] = []
    for concept in concepts[:MAX_FACTORY_CONCEPTS]:
        variants = run_copywriter(concept, round=1, chat=chat)
        for draft in variants:
            # Loop already runs hard_rules then judge each round.
            looped = run_loop(draft, chat=chat)
            composed = compose(looped, _visual_prompt(looped), image_gen=image_gen)
            upsert_draft(composed)
            queued.append(composed)
        if queued:
            break
    if not queued:
        raise ValueError("The factory could not produce a draft from that report.")
    logger.info("factory queued %s drafts from %s", len(queued), report_id)
    return queued
