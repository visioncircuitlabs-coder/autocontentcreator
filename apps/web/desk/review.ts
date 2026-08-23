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

export function alsoTodayHeadlines<T extends { signal_id: string }>(
  signals: T[],
  scores: { signal_id: string; gate: string; brand_fit: number }[],
  pickedId?: string,
  limit = 8,
): T[] {
  return sortSignals(signals, scores)
    .filter((row) => row.signal_id !== pickedId)
    .slice(0, limit);
}

export function shouldOfferFixture(
  didRun: boolean,
  deepDivesThisPass: number,
): boolean {
  return didRun && deepDivesThisPass === 0;
}

const PAGE_JUNK = [
  "window.",
  "document.",
  "function(",
  "wiz_global",
  "<script",
  "afy8hf",
  "subscribewithgoogle",
];

const JUNK_HOST_MARKERS = [
  "googleusercontent.com",
  "gstatic.com",
  "ggpht.com",
  "google-analytics.com",
  "googletagmanager.com",
  "googletagservices.com",
  "googleadservices.com",
  "googlesyndication.com",
  "doubleclick.net",
  "googleapis.com",
  "googleoptimize.com",
  "facebook.net",
  "scorecardresearch.com",
  "chartbeat.com",
  "hotjar.com",
  "cookiebot.com",
  "cookielaw.org",
  "onetrust.com",
  "amazon-adsystem.com",
];

export function isJunkSourceUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase();
    const path = parsed.pathname.toLowerCase();
    if (JUNK_HOST_MARKERS.some((token) => host.includes(token))) return true;
    if (/\.(png|jpe?g|gif|webp|svg|ico|js|css|woff2?)$/i.test(path)) return true;
    if (path.endsWith("/collect") || path.includes("/gtag/") || path.includes("/pagead/")) {
      return true;
    }
  } catch {
    return false;
  }
  return false;
}

export function readableQuote(quote: string): string {
  const text = quote.trim();
  if (!text) return "";
  const lower = text.toLowerCase();
  if (PAGE_JUNK.some((marker) => lower.includes(marker))) return "";
  if (lower.includes("ihdr") || lower.includes("idat") || text.includes("PNG")) {
    return "";
  }
  const letters = [...text].filter((ch) => /\p{L}/u.test(ch)).length;
  if (letters < 12) return "";
  return text;
}

export function sourceLinkLabel(url: string): string {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (host === "news.google.com" || host.endsWith(".news.google.com")) {
      return "Google News";
    }
    return host || url;
  } catch {
    return url;
  }
}

export function sourceFields(
  row: Record<string, unknown> | null | undefined,
): { url: string; quote: string; hash: string } {
  const url = String(row?.url ?? "").trim();
  if (isJunkSourceUrl(url)) {
    return { url: "", quote: "", hash: "" };
  }
  return {
    url,
    quote: readableQuote(String(row?.quote ?? "")),
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
