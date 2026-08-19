"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { decideDraft, friendlyError, loadQueue } from "../../desk/api";
import { DeskShell } from "../../desk/DeskShell";
import { CLERK_KEY, REASON_HINT, canSubmitReview } from "../../desk/review";
import type { Decision, Draft } from "../../desk/types";
import { Alert, EmptyDesk, LoadingDesk, Stamp, Ticket } from "../../desk/ui";

function readClerk(): string {
  try {
    return sessionStorage.getItem(CLERK_KEY) ?? "";
  } catch {
    return "";
  }
}

export default function QueuePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [queue, setQueue] = useState<Draft[]>([]);
  const [user, setUser] = useState("");
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [last, setLast] = useState<Decision | null>(null);

  useEffect(() => {
    setUser(readClerk());
    let alive = true;
    loadQueue()
      .then((rows) => {
        if (alive) setQueue(rows);
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

  function setClerk(value: string) {
    setUser(value);
    try {
      sessionStorage.setItem(CLERK_KEY, value);
    } catch {
      /* private mode */
    }
  }

  async function decide(draft: Draft, verdict: "approve" | "reject") {
    const reason = (reasons[draft.draft_id] ?? "").trim();
    if (!canSubmitReview(user, reason)) return;
    setError(null);
    setBusy(draft.draft_id);
    try {
      const decision = await decideDraft(draft.draft_id, {
        user: user.trim(),
        verdict,
        reason,
      });
      setLast(decision);
      setQueue((rows) => rows.filter((row) => row.draft_id !== draft.draft_id));
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setBusy(null);
    }
  }

  const ready = useMemo(() => canSubmitReview(user, "x"), [user]);

  return (
    <DeskShell step="queue">
      <p className="section-kicker">Queue</p>
      {error ? <Alert>{error}</Alert> : null}
      {last ? (
        <Ticket tone={last.verdict === "approve" ? "pass" : "kill"}>
          <Stamp kind={last.verdict === "approve" ? "pass" : "kill"}>
            {last.verdict}
          </Stamp>
          <p>
            {last.user} stamped {last.verdict}. Reason filed the same day.
          </p>
          <Link className="btn btn-ink" href={`/preview/${last.draft_id}`}>
            Preview
          </Link>
        </Ticket>
      ) : null}
      {loading ? <LoadingDesk label="Pulling tickets that still need a human stamp." /> : null}
      {!loading && queue.length === 0 && !last ? (
        <EmptyDesk>
          Nothing waiting for a human stamp. Create a post from a deep-dive
          first.
        </EmptyDesk>
      ) : null}
      {queue.map((draft) => {
        const reason = reasons[draft.draft_id] ?? "";
        const enabled = canSubmitReview(user, reason) && busy !== draft.draft_id;
        const verdict = String(draft.judge?.verdict ?? "");
        return (
          <Ticket
            key={draft.draft_id}
            tone={draft.flag_human ? "kill" : "gate"}
          >
            <div className="row-between">
              <p className="meta">
                {draft.draft_id} · round {draft.round} · v{draft.variant}
              </p>
              {draft.flag_human ? (
                <Stamp kind="kill">needs human</Stamp>
              ) : verdict === "PASS" ? (
                <Stamp kind="pass">machine pass</Stamp>
              ) : (
                <Stamp kind="watch">{verdict || "queued"}</Stamp>
              )}
            </div>
            <p className="caption">{draft.caption}</p>
            <label className="field">
              <span>Clerk</span>
              <input
                name="user"
                autoComplete="name"
                value={user}
                onChange={(event) => setClerk(event.target.value)}
                placeholder="Your name"
              />
            </label>
            <label className="field">
              <span>Reason</span>
              <textarea
                name="reason"
                value={reason}
                onChange={(event) =>
                  setReasons((prev) => ({
                    ...prev,
                    [draft.draft_id]: event.target.value,
                  }))
                }
                placeholder={REASON_HINT}
                required
              />
            </label>
            {!canSubmitReview(user, reason) ? (
              <p className="quiet">
                {ready
                  ? "Type a reason before you stamp."
                  : "Name and reason are required. This is not a publish button."}
              </p>
            ) : null}
            <div className="btn-row">
              <button
                className="btn btn-approve"
                type="button"
                disabled={!enabled}
                onClick={() => decide(draft, "approve")}
              >
                Approve
              </button>
              <button
                className="btn btn-reject"
                type="button"
                disabled={!enabled}
                onClick={() => decide(draft, "reject")}
              >
                Reject
              </button>
            </div>
            <div className="spacer" />
            <Link className="btn btn-ink" href={`/preview/${draft.draft_id}`}>
              Preview
            </Link>
          </Ticket>
        );
      })}
    </DeskShell>
  );
}
