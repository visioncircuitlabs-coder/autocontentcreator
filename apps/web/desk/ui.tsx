import type { ReactNode } from "react";
import { sourceFields, sourceLinkLabel } from "./review";
import type { TrendReport } from "./types";
import {
  SOURCES_BUTTON,
  VERDICT_FAIL,
  VERDICT_NONE,
  VERDICT_PASS,
} from "./words";

type TicketTone = "kill" | "gate" | "pass" | "plain";

export function Ticket({
  tone = "plain",
  children,
}: {
  tone?: TicketTone;
  children: ReactNode;
}) {
  return <article className={`ticket ticket-${tone}`}>{children}</article>;
}

export function Stamp({
  kind,
  children,
}: {
  kind: "kill" | "pass" | "gate" | "paused" | "watch";
  children: ReactNode;
}) {
  return <span className={`stamp stamp-${kind}`}>{children}</span>;
}

export function Alert({ children }: { children: ReactNode }) {
  return (
    <p className="alert" role="alert">
      {children}
    </p>
  );
}

export function LoadingDesk({ label }: { label: string }) {
  return (
    <p className="loading" role="status">
      <span className="pin" aria-hidden="true" />
      <span>{label}</span>
    </p>
  );
}

export function EmptyDesk({ children }: { children: ReactNode }) {
  return (
    <Ticket>
      <h2>Empty desk</h2>
      <p>{children}</p>
    </Ticket>
  );
}

export function VerdictBadge({
  judge,
}: {
  judge: Record<string, unknown> | null;
}) {
  const verdict = String(judge?.verdict ?? "");
  if (verdict === "PASS") {
    return <span className="badge badge-pass">{VERDICT_PASS}</span>;
  }
  if (verdict === "FAIL") {
    return <span className="badge badge-fail">{VERDICT_FAIL}</span>;
  }
  return <span className="badge badge-none">{VERDICT_NONE}</span>;
}

export function SkeletonLines({ rows = 3 }: { rows?: number }) {
  return (
    <div className="skel-card" aria-hidden="true">
      <span className="skel skel-tag" />
      {Array.from({ length: rows }, (_, index) => (
        <span key={index} className={index === rows - 1 ? "skel skel-short" : "skel"} />
      ))}
    </div>
  );
}

export function ReportSources({
  sources,
  heading = "Where we read this",
}: {
  sources: Array<Record<string, unknown>> | undefined;
  heading?: string | false;
}) {
  const rows = (sources ?? []).map((row, index) => ({
    key: `${sourceFields(row).url}-${index}`,
    ...sourceFields(row),
  }));
  const visible = rows.filter((row) => row.url || row.quote);
  if (!visible.length) {
    return (
      <p className="quiet">
        Could not open the article page. We still have the headline.
      </p>
    );
  }
  return (
    <>
      {heading ? <h3>{heading}</h3> : null}
      <ul className="source-list">
        {visible.map((row) => (
          <li key={row.key}>
            {row.url ? (
              <a href={row.url} target="_blank" rel="noreferrer">
                {sourceLinkLabel(row.url)}
              </a>
            ) : (
              <span>No url on this source.</span>
            )}
            {row.quote ? <p className="caption">{row.quote}</p> : null}
          </li>
        ))}
      </ul>
    </>
  );
}

export function SourcesFold({
  sources,
}: {
  sources: Array<Record<string, unknown>> | undefined;
}) {
  return (
    <details className="sources-fold">
      <summary>{SOURCES_BUTTON}</summary>
      <ReportSources sources={sources} heading={false} />
    </details>
  );
}

export function ReportCopy({ report }: { report: TrendReport }) {
  return (
    <>
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
      <ReportSources sources={report.sources} />
    </>
  );
}
