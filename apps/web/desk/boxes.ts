import type { DeskStep } from "./types";

export type Layer = "radar" | "memory" | "factory" | "command";

export type Box = {
  n: number;
  id: string;
  name: string;
  job: string;
  layer: Layer;
  href: string;
  step: DeskStep;
};

export const LAYERS: { id: Layer; label: string }[] = [
  { id: "radar", label: "Radar" },
  { id: "memory", label: "Memory" },
  { id: "factory", label: "Factory" },
  { id: "command", label: "Command" },
];

export const BOXES: Box[] = [
  {
    n: 1,
    id: "fetcher",
    name: "Source Fetcher",
    job: "GDELT, News, Reddit — one signal shape.",
    layer: "radar",
    href: "/radar",
    step: "radar",
  },
  {
    n: 2,
    id: "scorer",
    name: "Relevance Scorer",
    job: "Brand-fit, velocity, safety, then a gate.",
    layer: "radar",
    href: "/radar",
    step: "radar",
  },
  {
    n: 3,
    id: "researcher",
    name: "Deep-Dive Researcher",
    job: "Only deep_dive tickets become reports.",
    layer: "radar",
    href: "/radar",
    step: "radar",
  },
  {
    n: 4,
    id: "brand",
    name: "Brand Book",
    job: "Unofficial Neutrogena voice, India Instagram.",
    layer: "memory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 5,
    id: "facts",
    name: "Product Facts",
    job: "Approved, conditional, forbidden claims.",
    layer: "memory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 6,
    id: "reports",
    name: "Trend Reports",
    job: "What, why now, who, angles, skeptic.",
    layer: "memory",
    href: "/radar",
    step: "radar",
  },
  {
    n: 7,
    id: "record",
    name: "Track Record",
    job: "Every human yes/no, same day.",
    layer: "memory",
    href: "/queue",
    step: "queue",
  },
  {
    n: 8,
    id: "brief",
    name: "Brief Builder",
    job: "Code pack. Same inputs, same brief.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 9,
    id: "strategist",
    name: "Strategist",
    job: "Claim-safe grid. Disease is not a pain.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 10,
    id: "copy",
    name: "Copywriter",
    job: "Two or three captions. Approved phrases only.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 11,
    id: "art",
    name: "Art Director",
    job: "Picture, then a short video. Logo and disclaimer in code.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 12,
    id: "judge",
    name: "Compliance Judge",
    job: "Every sentence against Product Facts.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 13,
    id: "rules",
    name: "Hard Rules",
    job: "No cures, heals, best, only, guaranteed.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 14,
    id: "loop",
    name: "Improvement Loop",
    job: "Writer ≠ judge. Max three rounds.",
    layer: "factory",
    href: "/factory",
    step: "factory",
  },
  {
    n: 15,
    id: "review",
    name: "Review & Approve",
    job: "Named human. Reason required. No publish.",
    layer: "command",
    href: "/queue",
    step: "queue",
  },
  {
    n: 16,
    id: "export",
    name: "Preview & Export",
    job: "Paused IG frame + ZIP. Media ops owns go-live.",
    layer: "command",
    href: "/queue",
    step: "preview",
  },
  {
    n: 17,
    id: "feedback",
    name: "Feedback Writer",
    job: "The reason writes back into memory today.",
    layer: "command",
    href: "/queue",
    step: "queue",
  },
];

export function padBox(n: number): string {
  return String(n).padStart(2, "0");
}
