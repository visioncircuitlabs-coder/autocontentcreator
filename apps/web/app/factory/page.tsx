"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  friendlyError,
  loadBrief,
  loadReports,
  openFixtureDive,
  runFactory,
} from "../../desk/api";
import { DeskShell } from "../../desk/DeskShell";
import { voiceLine } from "../../desk/format";
import { FIXTURE_BUTTON, FIXTURE_NOTE } from "../../desk/review";
import type { BriefPack, Draft, TrendReport } from "../../desk/types";
import {
  Alert,
  LoadingDesk,
  ReportCopy,
  ReportSources,
  Stamp,
  Ticket,
} from "../../desk/ui";

function FactoryDesk() {
  const params = useSearchParams();
  const reportId = params.get("report_id") ?? "";
  const [reports, setReports] = useState<TrendReport[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [brief, setBrief] = useState<BriefPack | null>(null);
  const [pickedId, setPickedId] = useState("");
  const [fixtureLoading, setFixtureLoading] = useState(false);

  useEffect(() => {
    let alive = true;
    loadReports()
      .then((rows) => {
        if (alive) setReports(rows);
      })
      .catch((err) => {
        if (alive) setError(friendlyError(err));
      })
      .finally(() => {
        if (alive) setLoadingList(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  async function createPost(id: string) {
    setError(null);
    setRunning(true);
    try {
      const made = await runFactory(id);
      setDrafts(made);
      const briefId = made[0]?.brief_id;
      if (briefId) {
        try {
          setBrief(await loadBrief(briefId));
        } catch {
          setBrief(null);
        }
      }
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setRunning(false);
    }
  }

  const activeId = pickedId || reportId;
  const selected = reports.find((item) => item.report_id === activeId) ?? null;
  const claims = brief?.claims ?? [];
  const concepts = brief?.concepts ?? [];
  const briefSources = Array.isArray(brief?.report?.sources)
    ? (brief?.report?.sources as Array<Record<string, unknown>>)
    : [];

  async function openFixture() {
    setError(null);
    setFixtureLoading(true);
    try {
      const pack = await openFixtureDive();
      setReports((rows) => {
        const rest = rows.filter((row) => row.report_id !== pack.report.report_id);
        return [pack.report, ...rest];
      });
      setPickedId(pack.report.report_id);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setFixtureLoading(false);
    }
  }

  return (
    <DeskShell step="factory">
      <p className="section-kicker">Factory</p>
      {error ? <Alert>{error}</Alert> : null}
      {running ? (
        <LoadingDesk label="Brief → grid → copy → rules → judge → picture. Stay on this ticket." />
      ) : null}
      {loadingList ? <LoadingDesk label="Reading reports on the shelf." /> : null}
      {!loadingList && reports.length === 0 && !drafts.length ? (
        <Ticket tone="gate">
          <div className="row-between">
            <p className="meta">unofficial fixture</p>
            <Stamp kind="gate">not this Fetch</Stamp>
          </div>
          <h2>No live deep-dive</h2>
          <p>{FIXTURE_NOTE}</p>
          <button
            className="btn btn-ink"
            type="button"
            disabled={fixtureLoading}
            onClick={openFixture}
          >
            {fixtureLoading ? "Opening fixture…" : FIXTURE_BUTTON}
          </button>
        </Ticket>
      ) : null}
      {!drafts.length && (activeId || reports.length > 0) ? (
        <Ticket tone="gate">
          <h2>Create post</h2>
          {activeId ? (
            <>
              <p className="meta">{activeId}</p>
              {selected ? (
                <ReportCopy report={selected} />
              ) : (
                <p>Run the belt on this deep-dive.</p>
              )}
              <button
                className="btn btn-ink"
                type="button"
                disabled={running}
                onClick={() => createPost(activeId)}
              >
                {running ? "Building…" : "Create post"}
              </button>
            </>
          ) : (
            <>
              <p>Pick a deep-dive report, then run the belt.</p>
              <div className="stack">
                {reports.map((report) => (
                  <Link
                    key={report.report_id}
                    className="btn btn-ink"
                    href={`/factory?report_id=${encodeURIComponent(report.report_id)}`}
                  >
                    {report.what.slice(0, 80) || report.report_id}
                  </Link>
                ))}
              </div>
            </>
          )}
        </Ticket>
      ) : null}

      {brief ? (
        <Ticket>
          <h2>Brief</h2>
          <p className="meta">
            {brief.brief_id} · {brief.market} · {brief.sku} · {brief.channel}
          </p>
          <p>{voiceLine(brief.brand_slice) || "Brand slice is on this pack."}</p>
          <p>
            <strong>Claims. </strong>
            {claims.length
              ? claims
                  .map(
                    (row) =>
                      `${String(row.text ?? row.claim_id ?? "claim")} (${String(row.status ?? "")})`,
                  )
                  .join(" · ")
              : "No claims packed."}
          </p>
          <p>
            <strong>Wins. </strong>
            {brief.wins?.length
              ? `${brief.wins.length} on file`
              : "No track-record wins yet."}
          </p>
          <p>
            <strong>Losses. </strong>
            {brief.losses?.length
              ? `${brief.losses.length} on file`
              : "No track-record losses yet."}
          </p>
          <ReportSources sources={briefSources} />
        </Ticket>
      ) : null}

      {drafts.length > 0 && concepts.length === 0 ? (
        <Ticket>
          <h2>Grid</h2>
          <p>No concept grid was stored on this ticket. Captions still ran the belt.</p>
        </Ticket>
      ) : null}

      {concepts.length > 0 ? (
        <Ticket>
          <h2>Grid</h2>
          <p className="quiet">One variable per row. First row went onto the belt.</p>
          {concepts.map((concept, index) => (
            <div className="grid-card" key={concept.concept_id}>
              <p className="meta">
                {index === 0 ? "on the belt · " : ""}
                {concept.indic_register} · {concept.channel}
              </p>
              <h3>{concept.angle}</h3>
              <p>
                {concept.persona} — {concept.claim_safe_pain}
              </p>
              <p className="quiet">{concept.hook || concept.idea}</p>
            </div>
          ))}
        </Ticket>
      ) : null}

      {drafts.map((draft) => {
        const verdict = String(draft.judge?.verdict ?? "");
        const reasons = Array.isArray(draft.judge?.reasons)
          ? (draft.judge?.reasons as unknown[]).map(String)
          : [];
        return (
          <Ticket
            key={draft.draft_id}
            tone={draft.flag_human ? "kill" : verdict === "PASS" ? "pass" : "plain"}
          >
            <div className="row-between">
              <p className="meta">
                {draft.draft_id} · v{draft.variant} · round {draft.round}
              </p>
              {draft.flag_human ? (
                <Stamp kind="kill">human flag</Stamp>
              ) : verdict === "PASS" ? (
                <Stamp kind="pass">judge pass</Stamp>
              ) : verdict ? (
                <Stamp kind="watch">{verdict}</Stamp>
              ) : null}
            </div>
            <h2>Caption</h2>
            <p className="caption">{draft.caption}</p>
            <h3>Hard rules</h3>
            {draft.rules?.length ? (
              <ul>
                {draft.rules.map((rule) => (
                  <li key={rule}>{rule}</li>
                ))}
              </ul>
            ) : (
              <p className="quiet">No hard-rule hits.</p>
            )}
            <h3>Judge trail</h3>
            <p className="quiet">
              implied {String(draft.judge?.implied_check ?? "skipped")}
            </p>
            {reasons.length ? (
              <ul>
                {reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            ) : (
              <p className="quiet">No numbered rewrite reasons.</p>
            )}
            <div className="btn-row">
              <Link className="btn btn-ink" href="/queue">
                Queue
              </Link>
              <Link className="btn btn-ink" href={`/preview/${draft.draft_id}`}>
                Preview
              </Link>
            </div>
          </Ticket>
        );
      })}
    </DeskShell>
  );
}

export default function FactoryPage() {
  return (
    <Suspense
      fallback={
        <DeskShell step="factory">
          <LoadingDesk label="Opening the factory desk." />
        </DeskShell>
      }
    >
      <FactoryDesk />
    </Suspense>
  );
}
