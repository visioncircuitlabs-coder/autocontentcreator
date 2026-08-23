"use client";

import { useEffect, useMemo, useState } from "react";
import { loadEvents, type MachineEvent } from "../desk/api";
import { BOXES, LAYERS } from "../desk/boxes";
import { BOX_STORY, LAYER_BLURB, liveLines } from "../desk/story";

const LIT: Record<number, string[]> = {
  1: ["fetcher", "scorer", "researcher"],
  2: ["reports", "brand", "facts"],
  3: ["brief", "strategist", "copy", "art", "judge", "rules", "loop"],
  4: ["review", "record"],
  5: ["export", "feedback"],
};

export function MachineGraph({
  beat,
  watching = false,
}: {
  beat: number;
  watching?: boolean;
}) {
  const lit = useMemo(() => new Set(LIT[beat] ?? []), [beat]);
  const defaultBox = (LIT[beat] ?? ["fetcher"])[0];
  const [picked, setPicked] = useState(defaultBox);
  const [events, setEvents] = useState<MachineEvent[]>([]);

  useEffect(() => {
    setPicked(defaultBox);
  }, [defaultBox]);

  useEffect(() => {
    let stop = false;
    async function pull() {
      try {
        const rows = await loadEvents(60);
        if (!stop) setEvents(rows);
      } catch {
        /* the walk still works without the log */
      }
    }
    void pull();
    if (!watching) {
      return () => {
        stop = true;
      };
    }
    const timer = setInterval(() => {
      void pull();
    }, 1200);
    return () => {
      stop = true;
      clearInterval(timer);
    };
  }, [watching]);

  const log = liveLines(events);
  const liveBox = watching ? log[log.length - 1]?.box : undefined;
  const active = liveBox && lit.has(liveBox) ? liveBox : picked;
  const story = BOX_STORY[active];
  const box = BOXES.find((row) => row.id === active);

  return (
    <section className="machine" aria-label="How the post is made">
      <p className="machine-kicker">How it is made — tap a box</p>
      <div className="machine-body">
        <div className="machine-cols">
          {LAYERS.map((layer) => (
            <div key={layer.id} className="machine-col">
              <p>{layer.label}</p>
              <span className="machine-blurb">{LAYER_BLURB[layer.id]}</span>
              {BOXES.filter((item) => item.layer === layer.id).map((item, index, list) => (
                <div key={item.id} className="machine-step">
                  <button
                    type="button"
                    className="node"
                    data-lit={lit.has(item.id) ? "true" : "false"}
                    data-sel={active === item.id ? "true" : "false"}
                    data-live={liveBox === item.id ? "true" : "false"}
                    onClick={() => setPicked(item.id)}
                  >
                    <span>{String(item.n).padStart(2, "0")}</span>
                    {item.name}
                  </button>
                  {layer.id === "radar" && index < list.length - 1 ? (
                    <p className="machine-then" aria-hidden="true">
                      ↓
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          ))}
        </div>
        <aside className="machine-story">
          <p className="machine-kicker">
            {box ? `${String(box.n).padStart(2, "0")} · ${box.name}` : "A step"}
          </p>
          {story ? (
            <dl>
              <dt>What it does</dt>
              <dd>{story.does}</dd>
              <dt>What comes in</dt>
              <dd>{story.takes}</dd>
              <dt>What it hands on</dt>
              <dd>{story.gives}</dd>
              <dt>Then</dt>
              <dd>{story.then}</dd>
              <dt>Does Grok run here?</dt>
              <dd>{story.grok}</dd>
            </dl>
          ) : (
            <p>Tap a box to see that step.</p>
          )}
          {log.length ? (
            <>
              <p className="machine-kicker">This look</p>
              <ol className="machine-log">
                {log.map((row, index) => (
                  <li
                    key={row.id}
                    data-now={index === log.length - 1 && watching ? "true" : "false"}
                  >
                    {row.line}
                  </li>
                ))}
              </ol>
            </>
          ) : watching ? (
            <p className="quiet">Looking… the log fills as each step finishes.</p>
          ) : null}
        </aside>
      </div>
    </section>
  );
}
