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
