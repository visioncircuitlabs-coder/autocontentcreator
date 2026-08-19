"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { friendlyError, loadDesk, runRadar } from "../../desk/api";
import { DeskShell } from "../../desk/DeskShell";
import { kolkata } from "../../desk/format";
import {
  emptySourceNote,
  missingSources,
  sortSignals,
  ticketTone,
} from "../../desk/review";
import type { Score, Signal, TrendReport } from "../../desk/types";
import { Alert, EmptyDesk, LoadingDesk, Stamp, Ticket } from "../../desk/ui";

function scoreFor(scores: Score[], id: string): Score | undefined {
  return scores.find((item) => item.signal_id === id);
}

function reportFor(reports: TrendReport[], signalId: string): TrendReport | undefined {
  return reports.find((item) => item.signal_id === signalId);
}

export default function RadarPage() {
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [reports, setReports] = useState<TrendReport[]>([]);
  const [divesThisRun, setDivesThisRun] = useState<string[]>([]);
  const [didRun, setDidRun] = useState(false);
  const [openId, setOpenId] = useState<string | null>(null);

  async function refresh() {
    const desk = await loadDesk();
    setSignals(desk.signals);
    setScores(desk.scores);
    setReports(desk.reports);
  }

  useEffect(() => {
    let alive = true;
    loadDesk()
      .then((desk) => {
        if (!alive) return;
        setSignals(desk.signals);
        setScores(desk.scores);
        setReports(desk.reports);
      })
      .catch((err) => {
        if (alive) setError(friendlyError(err));
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  async function fetchTrends() {
    setError(null);
    setRunning(true);
    try {
      const out = await runRadar();
      setSignals(out.signals_seen);
      setScores(out.scores);
      setReports(out.reports.length ? out.reports : out.deep_dives);
      setDidRun(true);
      setDivesThisRun(out.deep_dives.map((item) => item.report_id));
      const firstDive = out.deep_dives[0]?.signal_id;
      if (firstDive) setOpenId(firstDive);
    } catch (err) {
      setError(friendlyError(err));
      try {
        await refresh();
      } catch {
        /* keep the fetch error */
      }
    } finally {
      setRunning(false);
    }
  }

  const ordered = useMemo(
    () => sortSignals(signals, scores),
    [signals, scores],
  );
  const visible = useMemo(() => {
    if (!scores.length) return ordered;
    return ordered.filter((item) => scoreFor(scores, item.signal_id));
  }, [ordered, scores]);
  const missing = missingSources(signals);
  const unscored = Math.max(0, signals.length - visible.length);

  return (
    <DeskShell step="radar">
      <p className="section-kicker">Radar</p>
      <button className="btn" type="button" onClick={fetchTrends} disabled={running}>
        {running ? "Fetching…" : "Fetch trends"}
      </button>
      {running ? (
        <LoadingDesk label="Listening to GDELT, News, Reddit, then scoring. A deep-dive can take up to a minute." />
      ) : null}
      {error ? <Alert>{error}</Alert> : null}
      {loading && !running ? <LoadingDesk label="Opening the radar shelf." /> : null}
      {!loading && !running && visible.length === 0 ? (
        <EmptyDesk>
          No headlines on the desk. Fetch trends — GDELT, News, or Reddit may be
          quiet or blocked.
        </EmptyDesk>
      ) : null}
      {signals.length > 0 && missing.length > 0 ? (
        <Ticket>
          <h2>Quiet pipes</h2>
          {missing.map((source) => (
            <p key={source}>{emptySourceNote(source)}</p>
          ))}
        </Ticket>
      ) : null}
      {didRun && divesThisRun.length === 0 && scores.length > 0 && !running ? (
        <p className="quiet">
          Nothing passed the deep-dive gate this pass. Kill tickets stay off the
          factory belt.
        </p>
      ) : null}
      {unscored > 0 ? (
        <p className="quiet">
          {unscored} older headline{unscored === 1 ? "" : "s"} on the shelf have
          no score yet. The tickets below are the ones that passed through the
          scorer.
        </p>
      ) : null}
      {visible.map((signal) => {
        const score = scoreFor(scores, signal.signal_id);
        const report = reportFor(reports, signal.signal_id);
        const open = openId === signal.signal_id;
        const tone = ticketTone(score?.gate, score?.safety);
        const stampKind =
          score?.safety === "kill" || score?.gate === "discard"
            ? "kill"
            : score?.gate === "deep_dive"
              ? "gate"
              : "watch";
        return (
          <Ticket key={signal.signal_id} tone={tone}>
            <div className="row-between">
              <p className="meta">
                {signal.source} · {signal.market} · {kolkata(signal.seen_at)}
              </p>
              {score ? (
                <Stamp kind={stampKind}>
                  {score.gate}
                  {score.safety === "kill" ? " · kill" : ""}
                </Stamp>
              ) : (
                <Stamp kind="watch">unscored</Stamp>
              )}
            </div>
            <h2>{signal.title}</h2>
            <p>{signal.snippet || "No snippet on this signal."}</p>
            {score ? (
              <div className="scores">
                <div>
                  <span>brand-fit</span>
                  {score.brand_fit}/10
                </div>
                <div>
                  <span>velocity</span>
                  {score.velocity}/10
                </div>
              </div>
            ) : (
              <p className="quiet">No score on this ticket yet.</p>
            )}
            {score ? <p className="quiet">{score.reason}</p> : null}
            {score?.gate === "deep_dive" ? (
              <button
                className="btn btn-ink"
                type="button"
                onClick={() =>
                  setOpenId(open ? null : signal.signal_id)
                }
              >
                {open ? "Hide report" : "Open deep_dive"}
              </button>
            ) : null}
            {open && report ? (
              <div className="grid-card">
                <h3>Report {report.report_id}</h3>
                <p>
                  <strong>What. </strong>
                  {report.what}
                </p>
                <p>
                  <strong>Why now. </strong>
                  {report.why_now}
                </p>
                <p>
                  <strong>Who. </strong>
                  {report.who}
                </p>
                <p>
                  <strong>Angles. </strong>
                  {report.angles.join(" · ") || "None listed."}
                </p>
                <p>
                  <strong>Risks. </strong>
                  {report.risks.join(" · ") || "None listed."}
                </p>
                <p>
                  <strong>Skeptic. </strong>
                  {report.skeptic || "Nothing filed."}
                </p>
                <Link
                  className="btn btn-ink"
                  href={`/factory?report_id=${encodeURIComponent(report.report_id)}`}
                >
                  Create post
                </Link>
              </div>
            ) : null}
            {open && !report ? (
              <p className="quiet">
                Gate said deep_dive but no report landed on the shelf.
              </p>
            ) : null}
          </Ticket>
        );
      })}
    </DeskShell>
  );
}
