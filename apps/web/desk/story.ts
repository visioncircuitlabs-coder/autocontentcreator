const SOURCE_LABELS: Record<string, string> = {
  gdelt: "News wire",
  news_rss: "Google News",
  reddit: "Reddit",
  rss: "RSS",
  grok_web: "Grok search",
};

export type BoxStory = {
  does: string;
  takes: string;
  gives: string;
  then: string;
  grok: string;
};

export type LiveLine = {
  id: string;
  box: string;
  line: string;
};

export const LAYER_BLURB: Record<string, string> = {
  radar: "Find a story from today's news.",
  memory: "Hold the brand, the claims, and this idea.",
  factory: "Write a post and check every claim.",
  command: "You say yes or no. Nothing goes live.",
};

export const BOX_STORY: Record<string, BoxStory> = {
  fetcher: {
    does: "Looks at today's open web for skincare talk in India.",
    takes: "You tap Look for ideas.",
    gives: "A pile of headlines from Google News, a news wire, Reddit, and Grok search when a key is on.",
    then: "Those headlines go to the scorer.",
    grok: "Only as search. Locked India skincare query. Real article URLs. No scores.",
  },
  scorer: {
    does: "Drops unsafe stories. Scores the rest for brand-fit.",
    takes: "The pile of headlines.",
    gives: "Don't use, skip for now, or closer look.",
    then: "Only a closer look goes to the researcher.",
    grok: "Yes, on the best few. The rest use word matches.",
  },
  researcher: {
    does: "Opens the one story that earned a closer look and writes a short note.",
    takes: "One closer-look headline.",
    gives: "The idea you see on Pick.",
    then: "Memory keeps the note so you can make a post.",
    grok: "Sometimes, to split angles. The web page is data, never instructions.",
  },
  reports: {
    does: "Files the note: what, why now, who, and the links we read.",
    takes: "The researcher's note.",
    gives: "A stored idea Make a post can open.",
    then: "The brief builder packs this with the brand.",
    grok: "No. This is storage.",
  },
  brand: {
    does: "Keeps the unofficial Neutrogena voice for India Instagram.",
    takes: "The brand book on disk.",
    gives: "Tone and examples for the writer.",
    then: "The brief builder copies a slice, not the whole book.",
    grok: "No. People wrote this file.",
  },
  facts: {
    does: "Lists claims we may say, may say with a note, or must never say.",
    takes: "The claims file on disk.",
    gives: "Allowed phrases such as dermatologist tested.",
    then: "The judge and hard rules read this on every caption.",
    grok: "No. This is the claims list.",
  },
  record: {
    does: "Stores every human yes or no, with the reason, the same day.",
    takes: "Your name, your verdict, and why.",
    gives: "A line in the track record.",
    then: "Feedback writer can use that reason next time.",
    grok: "No. You wrote the reason.",
  },
  brief: {
    does: "Packs the idea, the brand slice, and the claims into one brief.",
    takes: "The stored idea plus brand and facts.",
    gives: "One brief. Same inputs, same pack.",
    then: "The strategist invents angles from that pack.",
    grok: "No. Code builds the brief.",
  },
  strategist: {
    does: "Invent a small grid of claim-safe angles. Disease is not a pain.",
    takes: "The brief.",
    gives: "A few angles, a person, a skin feel.",
    then: "The copywriter writes captions for one angle.",
    grok: "Yes, if it is on. Templates if it is not.",
  },
  copy: {
    does: "Writes two or three captions a person could paste.",
    takes: "One angle and the approved claims.",
    gives: "Version 1, 2, 3.",
    then: "Hard rules and the judge read every line.",
    grok: "Yes. If Grok writes junk, we drop it and use a plain fallback.",
  },
  art: {
    does: "Makes a bright 4:5 product photo. Logo and disclaimer sit in code.",
    takes: "The caption version you picked.",
    gives: "One Instagram-shaped still for the phone preview.",
    then: "The pack is ready for your call.",
    grok: "Yes, after you pick a version. One picture.",
  },
  judge: {
    does: "Checks every sentence against Product Facts.",
    takes: "A caption.",
    gives: "Allowed, or send it back.",
    then: "The loop may ask the writer to try again.",
    grok: "Yes, for implied claims. Hard rules still run in code.",
  },
  rules: {
    does: "Blocks banned words: cures, heals, best, only, guaranteed.",
    takes: "A caption.",
    gives: "A block list, or a clean pass.",
    then: "The judge still reads claims even if words look fine.",
    grok: "No. This is a word list.",
  },
  loop: {
    does: "Writer and judge are not the same step. Max three rounds.",
    takes: "A failing caption and the reasons.",
    gives: "A cleaned caption, or a flag for a person.",
    then: "You pick a version. Then we make the picture.",
    grok: "The writer may call Grok. The judge is a different call.",
  },
  review: {
    does: "Stops for a named human. Reason required. No publish.",
    takes: "The draft on your screen.",
    gives: "Yes, keep this, or no, do not use this.",
    then: "Preview still does not post it.",
    grok: "No. This is your call.",
  },
  export: {
    does: "Builds a paused Instagram frame and a ZIP.",
    takes: "The draft you kept.",
    gives: "A pack someone else would post in real life.",
    then: "Feedback writer files your reason.",
    grok: "No.",
  },
  feedback: {
    does: "Writes your reason back into memory the same day.",
    takes: "The yes or no you typed.",
    gives: "A note the next brief can see.",
    then: "The walk ends. Nothing went live.",
    grok: "No.",
  },
};

type EventIn = {
  id?: string;
  kind: string;
  payload?: Record<string, unknown>;
};

function sourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source;
}

export function lineForEvent(event: EventIn): LiveLine | null {
  const payload = event.payload ?? {};
  const id = String(event.id || event.kind);
  if (event.kind === "fetch_source") {
    const label = sourceLabel(String(payload.source ?? ""));
    const n = Number(payload.n ?? 0);
    const ok = Boolean(payload.ok);
    if (!ok || n <= 0) {
      return {
        id,
        box: "fetcher",
        line: `${label} sent nothing back. We kept going.`,
      };
    }
    return {
      id,
      box: "fetcher",
      line: `${label} sent ${n} headline${n === 1 ? "" : "s"}.`,
    };
  }
  if (event.kind === "radar_start") {
    return {
      id,
      box: "scorer",
      line: payload.chat
        ? "Grok is scoring the headlines that look on-brand."
        : "Scoring with word matches. Grok is off.",
    };
  }
  if (event.kind === "radar_scored") {
    const gates = (payload.gates ?? {}) as Record<string, number>;
    const closer = Number(gates.deep_dive ?? 0);
    const top = Array.isArray(payload.top) ? payload.top[0] : null;
    const title =
      top && typeof top === "object" && top !== null && "title" in top
        ? String((top as { title?: unknown }).title ?? "").trim()
        : "";
    if (closer > 0 && title) {
      return {
        id,
        box: "scorer",
        line: `Closer look: ${title.slice(0, 90)}`,
      };
    }
    if (closer > 0) {
      return {
        id,
        box: "scorer",
        line: `${closer} headline${closer === 1 ? "" : "s"} earned a closer look.`,
      };
    }
    return {
      id,
      box: "scorer",
      line: "No headline earned a closer look.",
    };
  }
  if (event.kind === "radar_end") {
    const n = Number(payload.n_reports ?? 0);
    return {
      id,
      box: "researcher",
      line: n
        ? "We read the one that matters and filed an idea."
        : "Nothing to read closely. A practice idea is next.",
    };
  }
  if (event.kind === "radar_fail") {
    return {
      id,
      box: "fetcher",
      line: "Look hit a snag. Try again.",
    };
  }
  return null;
}

export function liveLines(events: EventIn[]): LiveLine[] {
  const out: LiveLine[] = [];
  const seen = new Set<string>();
  for (const event of [...events].reverse()) {
    const line = lineForEvent(event);
    if (!line || seen.has(line.id)) continue;
    seen.add(line.id);
    out.push(line);
  }
  return out;
}
