export const LOOK_BUTTON = "Look for ideas";
export const LOOKING_STEPS = [
  "Looking at news…",
  "Scoring what fits the brand…",
  "Reading the ones that matter…",
];

export const MAKE_BUTTON = "Make a post";
export const MAKING_STEPS = [
  "Writing a brief…",
  "Trying a few angles…",
  "Writing captions…",
  "Checking claims…",
];
export const PICTURE_BUTTON = "Make the picture";
export const PICTURE_WAIT = "Making the picture…";

export const SAMPLE_BUTTON = "Use a sample idea (practice)";
export const SAMPLE_NOTE =
  "Today's headlines were not a strong Neutrogena match. Here is a practice idea so you can still make a post.";
export const ALSO_TODAY = "Also in this look";
export const TODAY_HEADLINES = "Today's headlines";

export const REASON_HINT = "Say why. The next person will read this.";
export const NAME_LABEL = "Your name";
export const WHY_LABEL = "Why (required)";
export const YES_BUTTON = "Yes, keep this";
export const NO_BUTTON = "No, do not use this";
export const DOWNLOAD_BUTTON = "Download pack";
export const SOURCES_BUTTON = "Sources";
export const PAUSED_NOTE = "This does not go live. Someone still has to post it.";

export const LOOK_TITLE = "Look for ideas";
export const LOOK_SUB =
  "One tap. We search the news and pick something you can turn into a post.";
export const MAKE_TITLE = "Make a post";
export const CALL_TITLE = "Your call";
export const PREVIEW_TITLE = "Phone preview";
export const PICK_TITLE = "This idea";
export const PRACTICE_TITLE = "Practice idea";
export const PRACTICE_TAG = "Practice idea";
export const NEWS_TAG = "From today's news";
export const SAMPLE_OPENING = "Opening the sample…";
export const SAVING_BUTTON = "Saving…";
export const VERSION_LABEL = "Version";
export const VARIANT_GROUP_LABEL = "Caption versions";
export const VARIANT_HINT =
  "Pick a version. Left and right arrow keys switch between them.";
export const VERDICT_PASS = "Claim check: pass";
export const VERDICT_FAIL = "Claim check: failed";
export const VERDICT_NONE = "Not checked yet";
export const EMPTY_MAKE_NOTE = "Make a post from the idea you picked.";
export const NO_PICTURE_NOTE = "No picture on this version yet.";
export const REVIEW_FORM_TITLE = "Who made this call";
export const NAME_REQUIRED_NOTE = "Add your name and a reason to unlock Yes or No.";
export const ANGLE_PREFIX = "Angle:";
export const VOICE_PREFIX = "Voice:";

export function radarCountNote(seen: number, scored: number): string {
  const noun = seen === 1 ? "headline" : "headlines";
  return `This look read ${seen} ${noun} and scored ${scored} of them.`;
}

export function decisionLine(name: string, approved: boolean): string {
  return `${name} said ${approved ? "yes" : "no"} on this draft.`;
}

// The machine learns from every stamp. Say so plainly, once, at Preview.
export function memoryLine(approved: boolean): string {
  return approved
    ? "Saved to brand memory: this pattern is now a winner."
    : "Saved to brand memory: this reason is now an anti-pattern.";
}

export const SOURCE_LABELS: Record<string, string> = {
  gdelt: "News wire",
  news_rss: "Google News",
  reddit: "Reddit",
  rss: "RSS",
  grok_web: "Grok search",
};

export const BEATS = [
  { n: 1, id: "look", label: "Look" },
  { n: 2, id: "pick", label: "Pick" },
  { n: 3, id: "make", label: "Make" },
  { n: 4, id: "call", label: "Your call" },
  { n: 5, id: "preview", label: "Preview" },
] as const;

export function gateLabel(gate?: string): string {
  if (gate === "deep_dive") return "Closer look";
  if (gate === "background") return "Skip for now";
  if (gate === "discard") return "Don't use";
  return "Skip for now";
}

export function emptySourceNote(source: string): string {
  const label = SOURCE_LABELS[source] ?? source;
  return `${label} sent nothing back. We kept going.`;
}

export function checkLines(draft: {
  rules?: string[];
  flag_human?: boolean;
  round?: number;
  judge?: Record<string, unknown> | null;
}): string[] {
  const lines: string[] = [];
  for (const rule of draft.rules ?? []) {
    lines.push(`We blocked this: ${rule}`);
  }
  const round = Number(draft.round ?? 1);
  if (round > 1) lines.push(`Grok checked this again (round ${round}).`);
  const verdict = String(draft.judge?.verdict ?? "");
  if (verdict === "PASS") lines.push("This copy uses allowed claims.");
  if (verdict === "FAIL") lines.push("A claim check failed. Read the notes.");
  if (String(draft.judge?.craft ?? "") === "PASS") {
    lines.push("A second Grok pass said this reads like a post.");
  }
  if (draft.flag_human) lines.push("A person still has to decide.");
  const reasons = Array.isArray(draft.judge?.reasons)
    ? (draft.judge?.reasons as unknown[]).map(String)
    : [];
  for (const reason of reasons) {
    if (reason.startsWith("note:")) lines.push(reason.slice(5).trim());
    else if (!lines.includes(reason)) lines.push(reason);
  }
  if (!lines.length) lines.push("No extra checks fired.");
  return lines;
}

/* --- Ops strip (desk telemetry) ------------------------------------- */

export const OPS_TITLE = "Desk pulse";
export const OPS_LABEL_APPROVE = "Approve rate";
export const OPS_LABEL_SPEND = "Image spend";
export const OPS_LABEL_RUNS = "Last runs";
export const OPS_RUN_WORD = "Look";
export const OPS_MAKE_WORD = "Make";
export const OPS_NEVER_RUN = "not yet";

export function formatPercent(ratio: number | null | undefined): string {
  if (
    ratio === null ||
    ratio === undefined ||
    typeof ratio !== "number" ||
    !Number.isFinite(ratio)
  ) {
    return "—";
  }
  return `${Math.round(ratio * 100)}%`;
}

export function spendFraction(spent: number, budget: number): number {
  if (!Number.isFinite(spent) || !Number.isFinite(budget) || budget <= 0) {
    return 0;
  }
  return Math.min(1, Math.max(0, spent / budget));
}

export function formatMoney(amount: number): string {
  const value = Number.isFinite(amount) ? amount : 0;
  return `$${value.toFixed(2)}`;
}

export type BreakerTone = "ok" | "warn" | "down";

export function breakerTone(state: string | null | undefined): BreakerTone {
  if (state === "open") return "down";
  if (state === "half_open") return "warn";
  return "ok";
}

export const OPS_BREAKER_LABELS: Record<BreakerTone, string> = {
  ok: "Models steady",
  warn: "Trying again",
  down: "Model calls paused",
};

export function agoNote(iso: string | null | undefined, nowMs: number): string {
  if (!iso) return OPS_NEVER_RUN;
  const then = Date.parse(iso);
  if (!Number.isFinite(then)) return "—";
  const seconds = Math.max(0, Math.round((nowMs - then) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
