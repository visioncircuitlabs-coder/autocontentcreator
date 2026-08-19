"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  draftImageUrl,
  downloadZip,
  friendlyError,
  loadDraft,
} from "../../../desk/api";
import { DeskShell } from "../../../desk/DeskShell";
import type { Draft } from "../../../desk/types";
import { Alert, EmptyDesk, LoadingDesk, Ticket } from "../../../desk/ui";

export default function PreviewPage() {
  const params = useParams<{ id: string }>();
  const draftId = params.id;
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imgBroken, setImgBroken] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let alive = true;
    if (!draftId) return;
    loadDraft(draftId)
      .then((row) => {
        if (alive) setDraft(row);
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
  }, [draftId]);

  async function saveZip() {
    if (!draft) return;
    setError(null);
    setSaving(true);
    try {
      await downloadZip(draft.draft_id);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <DeskShell step="preview">
      <p className="section-kicker">Paused preview</p>
      {error ? <Alert>{error}</Alert> : null}
      {loading ? <LoadingDesk label="Loading the paused frame." /> : null}
      {!loading && !draft ? (
        <EmptyDesk>
          That draft is not on the shelf. Go back to the queue.
        </EmptyDesk>
      ) : null}
      {draft ? (
        <>
          <div className="ig" aria-label="Paused Instagram-shaped preview">
            <div className="ig-paused">Paused — not published</div>
            <div className="ig-top">
              <span className="ig-avatar" aria-hidden="true" />
              <div>
                <div className="ig-name">Neutrogena (unofficial fixture)</div>
                <div className="ig-handle">not a Kenvue product</div>
              </div>
            </div>
            <div className="ig-photo">
              {imgBroken ? (
                <div className="missing">
                  No picture on this ticket yet. The ZIP may still pack a card.
                </div>
              ) : (
                <img
                  src={draftImageUrl(draft.draft_id)}
                  alt="Paused composed card"
                  onError={() => setImgBroken(true)}
                />
              )}
            </div>
            <div className="ig-caption">{draft.caption}</div>
          </div>
          {draft.flag_human ? (
            <Ticket tone="kill">
              <h2>Human flag</h2>
              <p>
                The loop stopped without a clean pass. A named person still has
                to stamp this — export stays paused.
              </p>
            </Ticket>
          ) : null}
          <button className="btn" type="button" onClick={saveZip} disabled={saving}>
            {saving ? "Packing…" : "Download ZIP"}
          </button>
          <div className="spacer" />
          <Link className="btn btn-ghost" href="/queue">
            Back to queue
          </Link>
        </>
      ) : null}
    </DeskShell>
  );
}
