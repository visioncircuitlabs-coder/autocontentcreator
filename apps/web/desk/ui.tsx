import type { ReactNode } from "react";

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
