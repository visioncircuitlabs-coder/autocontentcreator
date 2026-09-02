import type { BriefPack, BrandInfo, BrandProduct, Decision, Draft, RadarRun, Signal, Score, TrendReport } from "./types";

export type FixtureDive = {
  fixture: true;
  signal: Signal;
  score: Score;
  report: TrendReport;
};

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "/engine";

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

export function messageForHttpError(status: number, rawBody: string): string {
  const trimmed = rawBody.trim();
  if (trimmed) {
    try {
      const body = JSON.parse(trimmed) as { error?: unknown; detail?: unknown };
      if (body?.error) return String(body.error);
      if (typeof body?.detail === "string" && body.detail) return body.detail;
    } catch {
      /* HTML from a proxy, not the engine */
    }
  }
  if (status === 429) {
    return "Too many searches. Wait a minute and try again.";
  }
  if (status === 504) {
    return "That took too long. Try again.";
  }
  if (status === 502 || status === 503) {
    return "The news engine is not running. Start it, then try Look for ideas again.";
  }
  return "Something went wrong. Please try again.";
}

async function readError(res: Response): Promise<string> {
  const raw = await res.text();
  return messageForHttpError(res.status, raw);
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch (err) {
    void logClient("fetch_fail", {
      path,
      error: err instanceof Error ? err.message : "network",
    });
    throw new DeskError(
      "Could not reach the news engine through this page. Refresh and try Look for ideas again.",
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

export async function logClient(
  kind: string,
  payload: Record<string, unknown> = {},
): Promise<void> {
  try {
    await fetch(`${API_URL}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind, payload }),
    });
  } catch {
    /* never block the walk */
  }
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

export function runFactory(reportId: string, sku?: string) {
  return api<Draft[]>("/factory/run", {
    method: "POST",
    body: JSON.stringify(sku ? { report_id: reportId, sku } : { report_id: reportId }),
  });
}

export function paintDraft(draftId: string) {
  return api<Draft>("/factory/image", {
    method: "POST",
    body: JSON.stringify({ draft_id: draftId }),
  });
}

export function loadBrand() {
  return api<BrandInfo>("/brand");
}

export function loadProducts() {
  return api<{ products: BrandProduct[]; hero_sku: string }>("/brand/products");
}

export function productImageUrl(sku: string): string {
  return `${API_URL}/brand/products/${encodeURIComponent(sku)}/image`;
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

export type MachineEvent = {
  id: string;
  ts: string;
  kind: string;
  payload: Record<string, unknown>;
};

export function loadEvents(limit = 50) {
  return api<MachineEvent[]>(`/events?limit=${limit}`);
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
      "Could not download the pack. Refresh and try again.",
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
