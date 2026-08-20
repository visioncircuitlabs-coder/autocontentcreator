export const CLERK_KEY = "cm-clerk";

export const EXPECTED_SOURCES = ["gdelt", "news_rss", "reddit"] as const;

export function canSubmitReview(user: string, reason: string): boolean {
  return user.trim().length > 0 && reason.trim().length > 0;
}

export function missingSources(signals: { source: string }[]): string[] {
  const present = new Set(signals.map((item) => item.source));
  return EXPECTED_SOURCES.filter((source) => !present.has(source));
}

export function sortSignals<T extends { signal_id: string }>(
  signals: T[],
  scores: { signal_id: string; gate: string; brand_fit: number }[],
): T[] {
  const byId = new Map(scores.map((item) => [item.signal_id, item]));
  const rank = (gate: string) =>
    gate === "deep_dive" ? 0 : gate === "background" ? 1 : 2;
  return [...signals].sort((a, b) => {
    const sa = byId.get(a.signal_id);
    const sb = byId.get(b.signal_id);
    const ga = rank(sa?.gate ?? "discard");
    const gb = rank(sb?.gate ?? "discard");
    if (ga !== gb) return ga - gb;
    return (sb?.brand_fit ?? 0) - (sa?.brand_fit ?? 0);
  });
}

export function shouldOfferFixture(
  didRun: boolean,
  deepDivesThisPass: number,
): boolean {
  return didRun && deepDivesThisPass === 0;
}

export function sourceFields(
  row: Record<string, unknown> | null | undefined,
): { url: string; quote: string; hash: string } {
  return {
    url: String(row?.url ?? "").trim(),
    quote: String(row?.quote ?? "").trim(),
    hash: String(row?.hash ?? "").trim(),
  };
}

export function ticketTone(
  gate?: string,
  safety?: string,
): "kill" | "gate" | "pass" | "plain" {
  if (safety === "kill" || gate === "discard") return "kill";
  if (gate === "deep_dive") return "gate";
  if (safety === "ok" && gate === "background") return "plain";
  return "plain";
}
