from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Signal(BaseModel):
    signal_id: str
    seen_at: datetime
    happened_at: datetime | None
    source: Literal["gdelt", "news_rss", "reddit", "rss"]
    url: str
    title: str
    snippet: str
    lang: str = "en"
    market: str = "IN"
    query_id: str
    raw_ref: str = ""


class Score(BaseModel):
    signal_id: str
    brand_fit: int  # 1-10
    velocity: int  # 1-10
    safety: Literal["ok", "watch", "kill"]
    reason: str
    gate: Literal["discard", "background", "deep_dive"]
    model: str
    prompt_version: str


class TrendReport(BaseModel):
    report_id: str
    signal_id: str
    what: str
    why_now: str
    who: str
    angles: list[str]
    risks: list[str]
    sources: list[dict]  # url, fetched_at, hash, quote
    skeptic: str
    spent: dict
    capped_at: str


class Claim(BaseModel):
    claim_id: str
    text: str
    sku: str
    market: str
    evidence_ref: str
    status: Literal["approved", "conditional", "forbidden"]
    expires_at: datetime | None


class Concept(BaseModel):
    concept_id: str
    brief_id: str
    angle: str
    persona: str
    claim_safe_pain: str
    channel: str
    indic_register: str
    hook: str = ""
    idea: str = ""


class Brief(BaseModel):
    brief_id: str
    report_id: str
    market: str = "IN"
    sku: str
    channel: str = "instagram"
    format: str = "instagram caption"
    report: dict
    brand_slice: dict
    claims: list[dict]
    wins: list[dict] = Field(default_factory=list)
    losses: list[dict] = Field(default_factory=list)


class Draft(BaseModel):
    draft_id: str
    brief_id: str
    caption: str
    variant: int
    image_path: str | None
    judge: dict | None
    rules: list[str]
    round: int
    flag_human: bool = False


class Decision(BaseModel):
    draft_id: str
    user: str
    verdict: Literal["approve", "reject"]
    reason: str = Field(min_length=1)
    decided_at: datetime
