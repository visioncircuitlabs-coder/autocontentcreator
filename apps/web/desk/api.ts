import type { BriefPack, Decision, Draft, RadarRun, Signal, Score, TrendReport } from "./types";

export type FixtureDive = {
  fixture: true;
  signal: Signal;
  score: Score;
  report: TrendReport;
};

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class DeskError extends Error {
  status: number;
  constructor(message: string, status = 0) {
    super(message);
    this.name = "DeskError";
    this.status = status;
  }
}

export function friendlyError(err: unknown): string {
  if (err instanceof DeskError) return err.message;
  if (err instanceof Error && err.message) return err.message;
  return "Something went wrong. Please try again.";
}

async function readError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { error?: string; detail?: unknown };
    if (body?.error) return String(body.error);
  } catch {
    /* ignore non-JSON */
  }
  if (res.status === 429) {
    return "Too many searches. Wait a minute and try again.";
  }
  return "Something went wrong. Please try again.";
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new DeskError(
      "The news engine is not running. Wait a moment and try Look for ideas again.",
      0,
    );
  }
  if (!res.ok) {
    throw new DeskError(await readError(res), res.status);
  }
  if (res.status === 204) return undefined as T;
  const ctype = res.headers.get("content-type") || "";
  if (ctype.includes("application/json")) {
    return (await res.json()) as T;
  }
  return undefined as T;
}

export function draftImageUrl(draftId: string): string {
  return `${API_URL}/drafts/${encodeURIComponent(draftId)}/image`;
}

export async function loadDesk(): Promise<{
  signals: Signal[];
  scores: Score[];
  reports: TrendReport[];
}> {
  const [signals, scores, reports] = await Promise.all([
    api<Signal[]>("/signals"),
    api<Score[]>("/scores"),
    api<TrendReport[]>("/reports"),
  ]);
  return { signals, scores, reports };
}

export function runRadar() {
  return api<RadarRun>("/radar/run", { method: "POST" });
}

export function openFixtureDive() {
  return api<FixtureDive>("/radar/fixture", { method: "POST" });
}

export function runFactory(reportId: string) {
  return api<Draft[]>("/factory/run", {
    method: "POST",
    body: JSON.stringify({ report_id: reportId }),
  });
}

export function loadBrief(briefId: string) {
  return api<BriefPack>(`/briefs/${encodeURIComponent(briefId)}`);
}

export function loadQueue() {
  return api<Draft[]>("/queue");
}

export function loadDraft(draftId: string) {
  return api<Draft>(`/drafts/${encodeURIComponent(draftId)}`);
}

export function loadReports() {
  return api<TrendReport[]>("/reports");
}

export function decideDraft(
  draftId: string,
  body: { user: string; verdict: "approve" | "reject"; reason: string },
) {
  return api<Decision>(`/review/${encodeURIComponent(draftId)}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function downloadZip(draftId: string): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/export/${encodeURIComponent(draftId)}`);
  } catch {
    throw new DeskError(
      "The news engine is not running. Wait a moment and try Look for ideas again.",
      0,
    );
  }
  if (!res.ok) {
    throw new DeskError(await readError(res), res.status);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${draftId}_paused.zip`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
