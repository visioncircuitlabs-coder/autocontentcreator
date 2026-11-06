"use client";

import { useEffect, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent } from "react";
import {
  draftImageUrl,
  draftVideoUrl,
  downloadZip,
  friendlyError,
  loadBrief,
  openFixtureDive,
  paintDraft,
  filmDraft,
  runFactory,
  runRadar,
  decideDraft,
  logClient,
} from "../desk/api";
import {
  CLERK_KEY,
  canSubmitReview,
  missingSources,
  alsoTodayHeadlines,
  shouldOfferFixture,
} from "../desk/review";
import type { BriefPack, Decision, Draft, Score, Signal, TrendReport } from "../desk/types";
import {
  Alert,
  LoadingDesk,
  SkeletonLines,
  SourcesFold,
  VerdictBadge,
} from "../desk/ui";
import {
  ALSO_TODAY,
  ANGLE_PREFIX,
  CALL_TITLE,
  decisionLine,
  DOWNLOAD_BUTTON,
  EMPTY_MAKE_NOTE,
  gateLabel,
  LOOK_BUTTON,
  LOOK_SUB,
  LOOK_TITLE,
  LOOKING_STEPS,
  memoryLine,
  MAKE_BUTTON,
  MAKING_STEPS,
  MAKE_TITLE,
  NAME_LABEL,
  NAME_REQUIRED_NOTE,
  NO_BUTTON,
  NO_PICTURE_NOTE,
  NO_VIDEO_NOTE,
  PAUSED_NOTE,
  PICTURE_BUTTON,
  PICTURE_FIRST_VIDEO,
  PICTURE_WAIT,
  VIDEO_BUTTON,
  VIDEO_HINT,
  VIDEO_WAIT,
  PREVIEW_TITLE,
  NEWS_TAG,
  PICK_TITLE,
  PRACTICE_TAG,
  PRACTICE_TITLE,
  radarCountNote,
  REASON_HINT,
  REVIEW_FORM_TITLE,
  SAMPLE_BUTTON,
  SAMPLE_NOTE,
  SAMPLE_OPENING,
  SAVING_BUTTON,
  TODAY_HEADLINES,
  VARIANT_GROUP_LABEL,
  VARIANT_HINT,
  VERSION_LABEL,
  VOICE_PREFIX,
  WHY_LABEL,
  YES_BUTTON,
  checkLines,
  emptySourceNote,
} from "../desk/words";
import { MachineGraph } from "./MachineGraph";
import { WalkShell } from "./WalkShell";
import { OpsStrip } from "../desk/ops";

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
  const [painting, setPainting] = useState(false);
  const [filming, setFilming] = useState(false);
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
  const [videoBroken, setVideoBroken] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setUser(readName());
  }, []);

  const quiet = missingSources(signals);
  const offerSample = shouldOfferFixture(didRun, divesThisRun);
  const alsoToday = alsoTodayHeadlines(signals, scores, picked?.signal_id);

  async function look() {
    setError(null);
    setLooking(true);
    setDrafts([]);
    setChosen(null);
    setDecision(null);
    void logClient("look_click", {});
    try {
      const out = await runRadar();
      const dives = out.deep_dives ?? [];
      setDidRun(true);
      setDivesThisRun(dives.length);
      setSignals(out.signals_seen ?? []);
      setScores(out.scores ?? []);
      if (dives[0]) {
        setReports(dives);
        setPicked(dives[0]);
        setSample(false);
        setBeat(2);
        return;
      }
      const pack = await openFixtureDive();
      setReports([pack.report]);
      setPicked(pack.report);
      setSample(true);
      setBeat(2);
    } catch (err) {
      const message = friendlyError(err);
      setError(message);
      void logClient("look_fail", { error: message });
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

  async function makePicture() {
    if (!chosen) return;
    setError(null);
    setPainting(true);
    setImgBroken(false);
    try {
      const painted = await paintDraft(chosen.draft_id);
      setChosen(painted);
      setDrafts((rows) =>
        rows.map((row) => (row.draft_id === painted.draft_id ? painted : row)),
      );
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setPainting(false);
    }
  }

  async function makeVideo() {
    if (!chosen) return;
    if (!chosen.image_path) {
      setError(PICTURE_FIRST_VIDEO);
      return;
    }
    setError(null);
    setFilming(true);
    setVideoBroken(false);
    try {
      const filmed = await filmDraft(chosen.draft_id);
      setChosen(filmed);
      setDrafts((rows) =>
        rows.map((row) => (row.draft_id === filmed.draft_id ? filmed : row)),
      );
      setBeat(4);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setFilming(false);
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

  // Enter advances a pick step when focus is not already on an interactive
  // control (so buttons do not double-fire).
  function onPanelKey(event: ReactKeyboardEvent<HTMLElement>) {
    if (event.key !== "Enter") return;
    const target = event.target as HTMLElement | null;
    if (target?.closest("button, a, input, textarea, select, summary, [role='radio']")) {
      return;
    }
    if (beat === 1 && !looking && !sampleBusy) void look();
    else if (beat === 2 && picked && !making) void makePost();
    else if (beat === 3 && chosen && !painting && !filming) {
      if (!chosen.image_path) void makePicture();
      else if (!chosen.video_path) void makeVideo();
    }
  }

  function onVariantKeys(event: ReactKeyboardEvent<HTMLElement>) {
    if (!drafts.length) return;
    const index = Math.max(
      0,
      drafts.findIndex((draft) => draft.draft_id === chosen?.draft_id),
    );
    let next = -1;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      next = (index + 1) % drafts.length;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      next = (index - 1 + drafts.length) % drafts.length;
    }
    if (next < 0) return;
    event.preventDefault();
    const draft = drafts[next];
    setChosen(draft);
    document.getElementById(`variant-${draft.variant}`)?.focus();
  }

  return (
    <WalkShell
      beat={beat}
      showMachine={showMachine}
      onToggleMachine={() => setShowMachine((v) => !v)}
      onJump={(n) => setBeat(n)}
    >
      {showMachine ? (
        <MachineGraph beat={beat} watching={looking || making || painting || filming} />
      ) : null}
      {error ? <Alert>{error}</Alert> : null}

      {beat === 1 ? (
        <section className="panel" aria-labelledby="look-title" onKeyDown={onPanelKey}>
          <h2 id="look-title">{LOOK_TITLE}</h2>
          <p className="panel-sub">{LOOK_SUB}</p>
          {looking ? (
            <LoadingDesk label={lookText || LOOKING_STEPS[0]} />
          ) : null}
          <button className="btn" type="button" disabled={looking} onClick={look}>
            {looking ? lookText || LOOKING_STEPS[0] : LOOK_BUTTON}
          </button>
        </section>
      ) : null}

      {beat === 2 ? (
        <section className="panel" aria-labelledby="pick-title">
          <h2 id="pick-title">{sample ? PRACTICE_TITLE : PICK_TITLE}</h2>
          {didRun && signals.length > 0 ? (
            <p className="meta-line" role="status">
              {radarCountNote(signals.length, scores.length)}
            </p>
          ) : null}
          {sampleBusy ? <LoadingDesk label={SAMPLE_OPENING} /> : null}
          {didRun && !picked && quiet.length > 0 ? (
            <ul className="quiet-list">
              {quiet.map((source) => (
                <li key={source}>{emptySourceNote(source)}</li>
              ))}
            </ul>
          ) : null}
          {!picked && !sampleBusy && offerSample ? (
            <div className="sample ticket">
              <p>{SAMPLE_NOTE}</p>
              <button
                className="btn btn-ink"
                type="button"
                disabled={sampleBusy}
                onClick={useSample}
              >
                {sampleBusy ? SAMPLE_OPENING : SAMPLE_BUTTON}
              </button>
            </div>
          ) : null}
          {looking ? <SkeletonLines rows={3} /> : null}
          {!looking && picked ? (
            <div className="picked ticket">
              <p className="tag">{sample ? PRACTICE_TAG : NEWS_TAG}</p>
              <h3>{picked.what}</h3>
              <p>{sample ? SAMPLE_NOTE : picked.why_now}</p>
              {sample ? null : <SourcesFold sources={picked.sources} />}
              <button className="btn" type="button" disabled={making} onClick={makePost}>
                {making ? makeText || MAKING_STEPS[0] : MAKE_BUTTON}
              </button>
            </div>
          ) : null}
          {!looking && alsoToday.length > 0 ? (
            <div className="also-today">
              <h3>{sample ? TODAY_HEADLINES : ALSO_TODAY}</h3>
              <ul>
                {alsoToday.map((row) => (
                  <li key={row.signal_id}>
                    <span className="tag">
                      {gateLabel(scores.find((item) => item.signal_id === row.signal_id)?.gate)}
                    </span>{" "}
                    {row.title}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      ) : null}

      {beat === 3 ? (
        <section className="panel" aria-labelledby="make-title" onKeyDown={onPanelKey}>
          <h2 id="make-title">{MAKE_TITLE}</h2>
          {making ? <LoadingDesk label={makeText || MAKING_STEPS[0]} /> : null}
          {painting ? <LoadingDesk label={PICTURE_WAIT} /> : null}
          {filming ? <LoadingDesk label={VIDEO_WAIT} /> : null}
          {brief?.concepts?.length ? (
            <p className="quiet">
              {ANGLE_PREFIX} {brief.concepts[0].angle}. {VOICE_PREFIX}{" "}
              {brief.concepts[0].persona}.
            </p>
          ) : null}
          {making ? (
            <div className="variant-grid" aria-hidden="true">
              <SkeletonLines rows={2} />
              <SkeletonLines rows={2} />
              <SkeletonLines rows={2} />
            </div>
          ) : drafts.length > 0 ? (
            <>
              <div
                className="variant-grid"
                role="radiogroup"
                aria-label={VARIANT_GROUP_LABEL}
                onKeyDown={onVariantKeys}
              >
                {drafts.map((draft, index) => (
                  <button
                    key={draft.draft_id}
                    id={`variant-${draft.variant}`}
                    type="button"
                    role="radio"
                    tabIndex={chosen?.draft_id === draft.draft_id || index === 0 ? 0 : -1}
                    aria-checked={chosen?.draft_id === draft.draft_id}
                    data-sel={chosen?.draft_id === draft.draft_id ? "true" : "false"}
                    disabled={painting || filming}
                    onClick={() => setChosen(draft)}
                  >
                    <span className="variant-top">
                      <span className="tag">
                        {VERSION_LABEL} {draft.variant}
                      </span>
                      <VerdictBadge judge={draft.judge} />
                    </span>
                    <span className="snip">
                      {draft.caption.split("\n")[0]}
                    </span>
                  </button>
                ))}
              </div>
              <p className="hint-line">{VARIANT_HINT}</p>
              {chosen ? (
                <>
                  <p className="caption-block">{chosen.caption}</p>
                  <ul className="checks">
                    {checkLines(chosen).map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                  <button
                    className="btn"
                    type="button"
                    disabled={painting || filming}
                    onClick={() => void makePicture()}
                  >
                    {painting ? PICTURE_WAIT : PICTURE_BUTTON}
                  </button>
                  {chosen.image_path ? (
                    <>
                      <div className="make-still">
                        {imgBroken ? (
                          <p className="quiet">{NO_PICTURE_NOTE}</p>
                        ) : (
                          <img
                            src={draftImageUrl(chosen.draft_id)}
                            alt="Post picture"
                            onError={() => setImgBroken(true)}
                          />
                        )}
                      </div>
                      <p className="hint-line">{VIDEO_HINT}</p>
                      <button
                        className="btn"
                        type="button"
                        disabled={filming}
                        onClick={() => void makeVideo()}
                      >
                        {filming ? VIDEO_WAIT : VIDEO_BUTTON}
                      </button>
                    </>
                  ) : null}
                </>
              ) : null}
            </>
          ) : (
            <p className="quiet">{EMPTY_MAKE_NOTE}</p>
          )}
        </section>
      ) : null}

      {beat === 4 ? (
        <section className="panel" aria-labelledby="call-title">
          <h2 id="call-title">{CALL_TITLE}</h2>
          {chosen ? <p className="caption-block">{chosen.caption}</p> : null}
          {chosen?.image_path || chosen?.video_path ? (
            <div className="review-media">
              {chosen.video_path && !videoBroken ? (
                <video
                  src={draftVideoUrl(chosen.draft_id)}
                  poster={chosen.image_path ? draftImageUrl(chosen.draft_id) : undefined}
                  controls
                  muted
                  playsInline
                  loop
                  aria-label="Short product video, not live"
                  onError={() => setVideoBroken(true)}
                />
              ) : chosen.image_path && !imgBroken ? (
                <img
                  src={draftImageUrl(chosen.draft_id)}
                  alt="Post picture"
                  onError={() => setImgBroken(true)}
                />
              ) : (
                <p className="quiet">{videoBroken ? NO_VIDEO_NOTE : NO_PICTURE_NOTE}</p>
              )}
            </div>
          ) : null}
          <form
            className="review-form"
            aria-label={REVIEW_FORM_TITLE}
            onSubmit={(event) => {
              event.preventDefault();
              void decide("approve");
            }}
          >
            <h3>{REVIEW_FORM_TITLE}</h3>
            <label className="field" htmlFor="review-name">
              {NAME_LABEL}
              <input
                id="review-name"
                value={user}
                onChange={(event) => saveName(event.target.value)}
                autoComplete="name"
                required
                aria-describedby="review-hint"
              />
            </label>
            <label className="field" htmlFor="review-reason">
              {WHY_LABEL}
              <textarea
                id="review-reason"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                rows={4}
                required
                aria-describedby="review-hint"
              />
            </label>
            <p className="hint-line" id="review-hint">
              {canSubmitReview(user, reason) ? REASON_HINT : NAME_REQUIRED_NOTE}
            </p>
            <div className="btn-row">
              <button
                className="btn btn-approve"
                type="submit"
                disabled={!canStamp}
              >
                {YES_BUTTON}
              </button>
              <button
                className="btn btn-reject"
                type="button"
                disabled={!canStamp}
                onClick={() => decide("reject")}
              >
                {NO_BUTTON}
              </button>
            </div>
          </form>
        </section>
      ) : null}

      {beat === 5 ? (
        <section className="panel" aria-labelledby="preview-title">
          <h2 id="preview-title">{PREVIEW_TITLE}</h2>
          {decision ? (
            <>
              <p className="meta-line" role="status">
                {decisionLine(decision.user, decision.verdict === "approve")}
              </p>
              <p className="quiet">{memoryLine(decision.verdict === "approve")}</p>
            </>
          ) : null}
          {chosen ? (
            <div className="ig" aria-label="Phone preview, not live">
              <div className="ig-paused">{PAUSED_NOTE}</div>
              <div className="ig-top">
                <span className="ig-avatar" aria-hidden="true" />
                <div>
                  <div className="ig-name">Neutrogena</div>
                  <div className="ig-handle">skincare</div>
                </div>
              </div>
              <div className="ig-photo">
                {chosen.video_path && !videoBroken ? (
                  <video
                    src={draftVideoUrl(chosen.draft_id)}
                    poster={chosen.image_path ? draftImageUrl(chosen.draft_id) : undefined}
                    controls
                    muted
                    playsInline
                    loop
                    autoPlay
                    aria-label="Short product video, not live"
                    onError={() => setVideoBroken(true)}
                  />
                ) : imgBroken ? (
                  <div className="missing">{NO_PICTURE_NOTE}</div>
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
          ) : (
            <SkeletonLines rows={3} />
          )}
          <p className="quiet">{PAUSED_NOTE}</p>
          <button className="btn" type="button" disabled={!chosen || saving} onClick={saveZip}>
            {saving ? SAVING_BUTTON : DOWNLOAD_BUTTON}
          </button>
        </section>
      ) : null}

      <OpsStrip />
    </WalkShell>
  );
}
