"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { friendlyError, loadDesk, openFixtureDive, runRadar } from "../../desk/api";
import { DeskShell } from "../../desk/DeskShell";
import { kolkata } from "../../desk/format";
import {
  FIXTURE_BUTTON,
  FIXTURE_NOTE,
  emptySourceNote,
  missingSources,
  shouldOfferFixture,
  sortSignals,
  ticketTone,
} from "../../desk/review";
import type { Score, Signal, TrendReport } from "../../desk/types";
import {
  Alert,
  EmptyDesk,
  LoadingDesk,
  ReportCopy,
  Stamp,
  Ticket,
} from "../../desk/ui";

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
  const [fixtureReport, setFixtureReport] = useState<TrendReport | null>(null);
  const [fixtureLoading, setFixtureLoading] = useState(false);

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
      setFixtureReport(null);
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
  const offerFixture = shouldOfferFixture(didRun, divesThisRun.length);

  async function openFixture() {
    setError(null);
    setFixtureLoading(true);
    try {
      const pack = await openFixtureDive();
      setFixtureReport(pack.report);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setFixtureLoading(false);
    }
  }

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
      {offerFixture && !running ? (
        <Ticket tone="gate">
          <div className="row-between">
            <p className="meta">unofficial fixture</p>
            <Stamp kind="gate">not this Fetch</Stamp>
          </div>
          <h2>No live deep-dive</h2>
          <p>{FIXTURE_NOTE}</p>
          {fixtureReport ? (
            <>
              <ReportCopy report={fixtureReport} />
              <Link
                className="btn btn-ink"
                href={`/factory?report_id=${encodeURIComponent(fixtureReport.report_id)}`}
              >
                Create post from unofficial fixture
              </Link>
            </>
          ) : (
            <button
              className="btn btn-ink"
              type="button"
              disabled={fixtureLoading}
              onClick={openFixture}
            >
              {fixtureLoading ? "Opening fixture…" : FIXTURE_BUTTON}
            </button>
          )}
        </Ticket>
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
                <ReportCopy report={report} />
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
