"""Plain-code belt. Radar then factory. Models sit inside steps. No CrewAI."""

from __future__ import annotations

import logging
from typing import NamedTuple

import httpx

from boxes.art_director import compose
from boxes.brief import build_brief
from boxes.copywriter import run_copywriter
from boxes.fetcher import build_client, run_fetch
from boxes.loop import run_loop
from boxes.researcher import run_research
from boxes.scorer import run_score
from boxes.strategist import run_strategist
from boxes.visual import visual_prompt
from db import get_draft, upsert_concepts, upsert_draft, upsert_reports
from models import Draft, Score, Signal, TrendReport
from obs import emit, emit_error
from ports import ChatModel, ImageGen, TrendSource

logger = logging.getLogger(__name__)

MAX_FACTORY_CONCEPTS = 1
MAX_DEEP_DIVES = 1
RADAR_RESEARCH_GETS = 3
RADAR_RESEARCH_SECONDS = 35.0


class RadarPack(NamedTuple):
    reports: list[TrendReport]
    signals: list[Signal]
    scores: list[Score]


def run_radar(
    *,
    sources: list[TrendSource] | None = None,
    client: httpx.Client | None = None,
    chat: ChatModel | None = None,
    persist: bool = True,
) -> RadarPack:
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
        dives = sorted(
            (score for score in scores if score.gate == "deep_dive"),
            key=lambda item: (item.brand_fit, item.velocity),
            reverse=True,
        )
        for score in dives[:MAX_DEEP_DIVES]:
            signal = by_id.get(score.signal_id)
            if signal is None:
                continue
            reports.append(
                run_research(
                    signal,
                    score,
                    chat=None,
                    client=client,
                    persist=persist,
                    max_gets=RADAR_RESEARCH_GETS,
                    max_seconds=RADAR_RESEARCH_SECONDS,
                )
            )
        if persist and reports:
            upsert_reports(reports)
        emit("radar_end", n_reports=len(reports), report_ids=[r.report_id for r in reports])
        logger.info("radar stored %s deep-dive reports", len(reports))
        return RadarPack(reports=reports, signals=signals, scores=scores)
    except Exception as exc:
        emit_error("radar_fail", exc)
        raise
    finally:
        if owns:
            client.close()


def run_factory(
    report_id: str,
    *,
    sku: str | None = None,
    chat: ChatModel | None = None,
    image_gen: ImageGen | None = None,
) -> list[Draft]:
    """brief → strategist → copywriter → loop. Picture waits until a version is picked."""
    _ = image_gen
    brief_id = build_brief(report_id, sku=sku)
    concepts = run_strategist(brief_id, chat=chat)
    upsert_concepts(concepts)
    queued: list[Draft] = []
    for concept in concepts[:MAX_FACTORY_CONCEPTS]:
        variants = run_copywriter(concept, round=1, chat=chat)
        for draft in variants:
            looped = run_loop(draft, chat=chat)
            upsert_draft(looped)
            queued.append(looped)
        if queued:
            break
    if not queued:
        raise ValueError("The factory could not produce a draft from that report.")
    logger.info("factory queued %s drafts from %s", len(queued), report_id)
    return queued


def paint_chosen(
    draft_id: str,
    *,
    image_gen: ImageGen | None = None,
) -> Draft:
    """One picture, after a person picks a caption version."""
    draft = get_draft(draft_id)
    if draft is None:
        raise ValueError("That draft is not in the queue.")
    emit("paint_start", draft_id=draft_id)
    composed = compose(draft, visual_prompt(draft), image_gen=image_gen)
    upsert_draft(composed)
    emit("paint_end", draft_id=draft_id, image=bool(composed.image_path))
    return composed
