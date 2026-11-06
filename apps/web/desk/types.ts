export type Gate = "discard" | "background" | "deep_dive";
export type Safety = "ok" | "watch" | "kill";

export type Signal = {
  signal_id: string;
  seen_at: string;
  happened_at: string | null;
  source: "gdelt" | "news_rss" | "reddit" | "rss" | string;
  url: string;
  title: string;
  snippet: string;
  lang: string;
  market: string;
  query_id: string;
  raw_ref: string;
};

export type Score = {
  signal_id: string;
  brand_fit: number;
  velocity: number;
  safety: Safety | string;
  reason: string;
  gate: Gate | string;
  model: string;
  prompt_version: string;
};

export type TrendReport = {
  report_id: string;
  signal_id: string;
  what: string;
  why_now: string;
  who: string;
  angles: string[];
  risks: string[];
  sources: Array<Record<string, unknown>>;
  skeptic: string;
  spent: Record<string, unknown>;
  capped_at: string;
};

export type RadarRun = {
  reports: TrendReport[];
  scores: Score[];
  signals_seen: Signal[];
  deep_dives: TrendReport[];
};

export type Concept = {
  concept_id: string;
  brief_id: string;
  angle: string;
  persona: string;
  claim_safe_pain: string;
  channel: string;
  indic_register: string;
  hook: string;
  idea: string;
};

export type BriefPack = {
  brief_id: string;
  report_id: string;
  market: string;
  sku: string;
  channel: string;
  format: string;
  report: Record<string, unknown>;
  brand_slice: Record<string, unknown>;
  claims: Array<Record<string, unknown>>;
  wins: Array<Record<string, unknown>>;
  losses: Array<Record<string, unknown>>;
  concepts: Concept[];
};

export type Draft = {
  draft_id: string;
  brief_id: string;
  caption: string;
  variant: number;
  image_path: string | null;
  judge: Record<string, unknown> | null;
  rules: string[];
  round: number;
  flag_human: boolean;
};

export type Decision = {
  draft_id: string;
  user: string;
  verdict: "approve" | "reject";
  reason: string;
  decided_at: string;
};

export type BrandInfo = {
  slug: string;
  name: string;
  unofficial: boolean;
  unofficial_line: string;
  wordmark: string;
  market: string;
  timezone: string;
  currency: string;
  handle: string;
  category: string;
  disclaimer: string;
  hero_sku: string;
  look_sub: string;
  sample_note: string;
};

export type BrandProduct = {
  sku: string;
  name: string;
  flavour: string;
  chip_cut: string;
  pack_color: string;
  hero: boolean;
  notes: string;
  has_image: boolean;
  image_url: string | null;
};

export type DeskStep = "home" | "radar" | "factory" | "queue" | "preview";
