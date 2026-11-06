"use client";

import { useEffect, useState } from "react";
import { api } from "./api";
import {
  agoNote,
  breakerTone,
  formatMoney,
  formatPercent,
  OPS_BREAKER_LABELS,
  OPS_LABEL_APPROVE,
  OPS_LABEL_RUNS,
  OPS_LABEL_SPEND,
  OPS_LABEL_VIDEO_SPEND,
  OPS_TITLE,
  OPS_MAKE_WORD,
  OPS_RUN_WORD,
  spendFraction,
} from "./words";

type MetricsPayload = {
  approve_rate: number | null;
  image_spend_usd: number;
  image_budget_usd: number;
  video_spend_usd: number;
  video_budget_usd: number;
  breaker_state: string;
  last_radar_run_at: string | null;
  last_factory_run_at: string | null;
};

const POLL_MS = 30_000;

/**
 * Quiet desk telemetry. Polls /metrics every 30s through the engine proxy;
 * renders nothing until (and unless) the engine answers — an API that is
 * down simply leaves the strip blank instead of nagging the clerk.
 */
export function OpsStrip() {
  const [data, setData] = useState<MetricsPayload | null>(null);

  useEffect(() => {
    let alive = true;
    async function tick() {
      try {
        const next = await api<MetricsPayload>("/metrics");
        if (alive && next) setData(next);
      } catch {
        if (alive) setData(null);
      }
    }
    void tick();
    const timer = setInterval(tick, POLL_MS);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  if (!data) return null;

  const tone = breakerTone(data.breaker_state);
  const fillPct = Math.round(
    spendFraction(data.image_spend_usd, data.image_budget_usd) * 100,
  );
  const videoFillPct = Math.round(
    spendFraction(data.video_spend_usd ?? 0, data.video_budget_usd ?? 0) * 100,
  );
  const nowMs = Date.now();

  return (
    <aside className="ops-strip" aria-label={OPS_TITLE}>
      <span className="ops-cell">
        <span className="ops-k">{OPS_LABEL_APPROVE}</span>
        <span className="ops-v">{formatPercent(data.approve_rate)}</span>
      </span>
      <span className="ops-cell">
        <span className="ops-k">{OPS_LABEL_SPEND}</span>
        <span className="ops-v ops-spend">
          <span
            className="ops-fill"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={fillPct}
          >
            <span style={{ width: `${fillPct}%` }} />
          </span>
          {formatMoney(data.image_spend_usd)} / {formatMoney(data.image_budget_usd)}
        </span>
      </span>
      <span className="ops-cell">
        <span className="ops-k">{OPS_LABEL_VIDEO_SPEND}</span>
        <span className="ops-v ops-spend">
          <span
            className="ops-fill"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={videoFillPct}
          >
            <span style={{ width: `${videoFillPct}%` }} />
          </span>
          {formatMoney(data.video_spend_usd ?? 0)} / {formatMoney(data.video_budget_usd ?? 0)}
        </span>
      </span>
      <span className="ops-cell">
        <span className={`ops-dot ops-dot-${tone}`} aria-hidden="true" />
        <span className="ops-v">{OPS_BREAKER_LABELS[tone]}</span>
      </span>
      <span className="ops-cell">
        <span className="ops-k">{OPS_LABEL_RUNS}</span>
        <span className="ops-v ops-runs">
          {OPS_RUN_WORD} {agoNote(data.last_radar_run_at, nowMs)}
          {" · "}
          {OPS_MAKE_WORD} {agoNote(data.last_factory_run_at, nowMs)}
        </span>
      </span>
    </aside>
  );
}
