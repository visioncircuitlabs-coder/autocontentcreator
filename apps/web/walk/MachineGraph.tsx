"use client";

import { BOXES, LAYERS } from "../desk/boxes";

const LIT: Record<number, string[]> = {
  1: ["fetcher", "scorer", "researcher"],
  2: ["reports", "brand", "facts"],
  3: ["brief", "strategist", "copy", "art", "judge", "rules", "loop"],
  4: ["review", "record"],
  5: ["export", "feedback"],
};

export function MachineGraph({ beat }: { beat: number }) {
  const lit = new Set(LIT[beat] ?? []);
  return (
    <section className="machine" aria-label="How the post is made">
      <p className="machine-kicker">The machine (you do not need this to work)</p>
      <div className="machine-cols">
        {LAYERS.map((layer) => (
          <div key={layer.id} className="machine-col">
            <p>{layer.label}</p>
            {BOXES.filter((box) => box.layer === layer.id).map((box) => (
              <div
                key={box.id}
                className="node"
                data-lit={lit.has(box.id) ? "true" : "false"}
              >
                <span>{String(box.n).padStart(2, "0")}</span>
                {box.name}
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}
