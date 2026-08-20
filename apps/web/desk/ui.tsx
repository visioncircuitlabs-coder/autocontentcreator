import type { ReactNode } from "react";
import { sourceFields } from "./review";
import type { TrendReport } from "./types";

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

export function ReportSources({
  sources,
}: {
  sources: Array<Record<string, unknown>> | undefined;
}) {
  const rows = (sources ?? []).map((row, index) => ({
    key: `${sourceFields(row).url}-${index}`,
    ...sourceFields(row),
  }));
  if (!rows.some((row) => row.url || row.quote)) {
    return <p className="quiet">No links on this idea yet.</p>;
  }
  return (
    <>
      <h3>Where we read this</h3>
      <ul className="source-list">
        {rows.map((row) => (
          <li key={row.key}>
            {row.url ? (
              <a href={row.url} target="_blank" rel="noreferrer">
                {row.url}
              </a>
            ) : (
              <span>No url on this source.</span>
            )}
            {row.quote ? <p className="caption">{row.quote}</p> : null}
            {row.hash ? <p className="hash">hash {row.hash}</p> : null}
          </li>
        ))}
      </ul>
    </>
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
