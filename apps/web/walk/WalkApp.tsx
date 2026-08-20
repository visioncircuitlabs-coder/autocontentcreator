"use client";

import { useEffect, useState } from "react";
import {
  draftImageUrl,
  downloadZip,
  friendlyError,
  loadBrief,
  openFixtureDive,
  runFactory,
  runRadar,
  decideDraft,
} from "../desk/api";
import { CLERK_KEY, canSubmitReview, missingSources, shouldOfferFixture } from "../desk/review";
import type { BriefPack, Decision, Draft, Score, Signal, TrendReport } from "../desk/types";
import { ReportSources } from "../desk/ui";
import {
  DOWNLOAD_BUTTON,
  LOOK_BUTTON,
  LOOKING_STEPS,
  MAKE_BUTTON,
  MAKING_STEPS,
  NAME_LABEL,
  NO_BUTTON,
  PAUSED_NOTE,
  REASON_HINT,
  SAMPLE_BUTTON,
  SAMPLE_NOTE,
  WHY_LABEL,
  YES_BUTTON,
  checkLines,
  emptySourceNote,
} from "../desk/words";
import { MachineGraph } from "./MachineGraph";
import { WalkShell } from "./WalkShell";

function useRotating(steps: string[], on: boolean): string {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (!on) {
      setIndex(0);
      return;
    }
    const timer = setInterval(() => {
      setIndex((n) => (n + 1) % steps.length);
    }, 2200);
    return () => clearInterval(timer);
  }, [on, steps]);
  return on ? steps[index] : "";
}

function readName(): string {
  try {
    return sessionStorage.getItem(CLERK_KEY) ?? "";
  } catch {
    return "";
  }
}

export function WalkApp({ initialBeat = 1 }: { initialBeat?: number }) {
  const [beat, setBeat] = useState(initialBeat);
  const [showMachine, setShowMachine] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [looking, setLooking] = useState(false);
  const [making, setMaking] = useState(false);
  const [sampleBusy, setSampleBusy] = useState(false);
  const lookText = useRotating(LOOKING_STEPS, looking);
  const makeText = useRotating(MAKING_STEPS, making);

  const [didRun, setDidRun] = useState(false);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [reports, setReports] = useState<TrendReport[]>([]);
  const [divesThisRun, setDivesThisRun] = useState(0);
  const [picked, setPicked] = useState<TrendReport | null>(null);
  const [sample, setSample] = useState(false);

  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [brief, setBrief] = useState<BriefPack | null>(null);
  const [chosen, setChosen] = useState<Draft | null>(null);

  const [user, setUser] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [imgBroken, setImgBroken] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setUser(readName());
  }, []);

  const quiet = missingSources(signals);
  const offerSample = shouldOfferFixture(didRun, divesThisRun);

  async function look() {
    setError(null);
    setLooking(true);
    setSample(false);
    setPicked(null);
    setDrafts([]);
    setChosen(null);
    setDecision(null);
    try {
      const out = await runRadar();
      const dives = out.deep_dives ?? [];
      const diveIds = new Set(dives.map((row) => row.signal_id));
      setDidRun(true);
      setDivesThisRun(dives.length);
      if (dives[0]) {
        setSignals((out.signals_seen ?? []).filter((row) => diveIds.has(row.signal_id)));
        setScores((out.scores ?? []).filter((row) => diveIds.has(row.signal_id)));
        setReports(dives);
        setPicked(dives[0]);
        setSample(false);
        setBeat(2);
        return;
      }
      const pack = await openFixtureDive();
      setSignals([pack.signal]);
      setScores([pack.score]);
      setReports([pack.report]);
      setPicked(pack.report);
      setSample(true);
      setBeat(2);
    } catch (err) {
      setError(friendlyError(err));
      setDidRun(true);
      setDivesThisRun(0);
      setBeat(2);
    } finally {
      setLooking(false);
    }
  }

  async function useSample() {
    setError(null);
    setSampleBusy(true);
    try {
      const pack = await openFixtureDive();
      setPicked(pack.report);
      setReports((rows) => [
        pack.report,
        ...rows.filter((row) => row.report_id !== pack.report.report_id),
      ]);
      setSample(true);
      setBeat(2);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSampleBusy(false);
    }
  }

  async function makePost() {
    if (!picked) return;
    setError(null);
    setMaking(true);
    try {
      const made = await runFactory(picked.report_id);
      setDrafts(made);
      setChosen(made[0] ?? null);
      const briefId = made[0]?.brief_id;
      if (briefId) {
        try {
          setBrief(await loadBrief(briefId));
        } catch {
          setBrief(null);
        }
      }
      setBeat(3);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setMaking(false);
    }
  }

  function saveName(value: string) {
    setUser(value);
    try {
      sessionStorage.setItem(CLERK_KEY, value);
    } catch {
      /* private mode */
    }
  }

  async function decide(verdict: "approve" | "reject") {
    if (!chosen || !canSubmitReview(user, reason)) return;
    setError(null);
    setBusy(true);
    try {
      const row = await decideDraft(chosen.draft_id, {
        user: user.trim(),
        verdict,
        reason: reason.trim(),
      });
      setDecision(row);
      setBeat(5);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  async function saveZip() {
    if (!chosen) return;
    setError(null);
    setSaving(true);
    try {
      await downloadZip(chosen.draft_id);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSaving(false);
    }
  }

  const canStamp = canSubmitReview(user, reason) && !busy && Boolean(chosen);

  return (
    <WalkShell
      beat={beat}
      showMachine={showMachine}
      onToggleMachine={() => setShowMachine((v) => !v)}
      onJump={(n) => setBeat(n)}
    >
      {showMachine ? <MachineGraph beat={beat} /> : null}
      {error ? (
        <p className="alert" role="alert">
          {error}
        </p>
      ) : null}

      {beat === 1 ? (
        <section className="panel">
          <h2>Look for ideas</h2>
          <p>One tap. We search the news and pick something you can turn into a post.</p>
          <button className="btn" type="button" disabled={looking} onClick={look}>
            {looking ? lookText || LOOKING_STEPS[0] : LOOK_BUTTON}
          </button>
        </section>
      ) : null}

      {beat === 2 ? (
        <section className="panel">
          <h2>{sample ? "Practice idea" : "This idea"}</h2>
          {looking ? <p className="loading">{lookText}</p> : null}
          {didRun && !picked && quiet.length > 0 ? (
            <ul className="quiet-list">
              {quiet.map((source) => (
                <li key={source}>{emptySourceNote(source)}</li>
              ))}
            </ul>
          ) : null}
          {!picked && offerSample ? (
            <div className="sample ticket">
              <p>{SAMPLE_NOTE}</p>
              <button
                className="btn btn-ink"
                type="button"
                disabled={sampleBusy}
                onClick={useSample}
              >
                {sampleBusy ? "Opening sample…" : SAMPLE_BUTTON}
              </button>
            </div>
          ) : null}
          {picked ? (
            <div className="picked ticket">
              {sample ? (
                <p className="tag">Practice idea. Live news did not give us a closer look.</p>
              ) : (
                <p className="tag">Closer look</p>
              )}
              <h3>{picked.what}</h3>
              <p>{picked.why_now}</p>
              <ReportSources sources={picked.sources} />
              <button className="btn" type="button" disabled={making} onClick={makePost}>
                {making ? makeText || MAKING_STEPS[0] : MAKE_BUTTON}
              </button>
            </div>
          ) : null}
        </section>
      ) : null}

      {beat === 3 ? (
        <section className="panel">
          <h2>Make a post</h2>
          {making ? <p className="loading">{makeText}</p> : null}
          {brief?.concepts?.length ? (
            <p className="quiet">
              Angle: {brief.concepts[0].angle}. Voice: {brief.concepts[0].persona}.
            </p>
          ) : null}
          <div className="versions">
            {drafts.map((draft) => (
              <button
                key={draft.draft_id}
                type="button"
                className="version"
                data-sel={chosen?.draft_id === draft.draft_id ? "true" : "false"}
                onClick={() => setChosen(draft)}
              >
                Version {draft.variant}
              </button>
            ))}
          </div>
          {chosen ? (
            <>
              <p className="caption-block">{chosen.caption}</p>
              <ul className="checks">
                {checkLines(chosen).map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
              <button className="btn" type="button" onClick={() => setBeat(4)}>
                Continue to your call
              </button>
            </>
          ) : !making ? (
            <p>Make a post from the idea you picked.</p>
          ) : null}
        </section>
      ) : null}

      {beat === 4 ? (
        <section className="panel">
          <h2>Your call</h2>
          {chosen ? <p className="caption-block">{chosen.caption}</p> : null}
          <label className="field">
            {NAME_LABEL}
            <input
              value={user}
              onChange={(event) => saveName(event.target.value)}
              autoComplete="name"
            />
          </label>
          <label className="field">
            {WHY_LABEL}
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              rows={4}
            />
          </label>
          <p className="quiet">{REASON_HINT}</p>
          <div className="row">
            <button
              className="btn"
              type="button"
              disabled={!canStamp}
              onClick={() => decide("approve")}
            >
              {YES_BUTTON}
            </button>
            <button
              className="btn btn-ink"
              type="button"
              disabled={!canStamp}
              onClick={() => decide("reject")}
            >
              {NO_BUTTON}
            </button>
          </div>
        </section>
      ) : null}

      {beat === 5 ? (
        <section className="panel">
          <h2>Phone preview</h2>
          {decision ? (
            <p>
              {decision.user} said {decision.verdict === "approve" ? "yes" : "no"}.
            </p>
          ) : null}
          {chosen ? (
            <div className="ig" aria-label="Phone preview, not live">
              <div className="ig-paused">{PAUSED_NOTE}</div>
              <div className="ig-top">
                <span className="ig-avatar" aria-hidden="true" />
                <div>
                  <div className="ig-name">Neutrogena (practice)</div>
                  <div className="ig-handle">not a Kenvue product</div>
                </div>
              </div>
              <div className="ig-photo">
                {imgBroken ? (
                  <div className="missing">No picture on this version yet.</div>
                ) : (
                  <img
                    src={draftImageUrl(chosen.draft_id)}
                    alt="Post picture"
                    onError={() => setImgBroken(true)}
                  />
                )}
              </div>
              <div className="ig-caption">{chosen.caption}</div>
            </div>
          ) : null}
          <p className="quiet">{PAUSED_NOTE}</p>
          <button className="btn" type="button" disabled={!chosen || saving} onClick={saveZip}>
            {saving ? "Saving…" : DOWNLOAD_BUTTON}
          </button>
        </section>
      ) : null}
    </WalkShell>
  );
}
