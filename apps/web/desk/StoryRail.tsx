import Link from "next/link";
import { BOXES, LAYERS, padBox } from "./boxes";
import type { DeskStep } from "./types";

export function StoryRail({ step }: { step: DeskStep }) {
  return (
    <nav className="rail" aria-label="17-box belt">
      {LAYERS.map((layer) => (
        <div key={layer.id}>
          <div className="rail-layer">{layer.label}</div>
          {BOXES.filter((box) => box.layer === layer.id).map((box) => {
            const lit =
              box.step === step || (step === "home" && box.id === "fetcher");
            return (
              <Link
                key={box.id}
                href={box.href}
                className="rail-item"
                data-lit={lit ? "true" : "false"}
                title={`${padBox(box.n)} ${box.name}`}
                aria-label={`${padBox(box.n)} ${box.name}`}
                aria-current={lit ? "page" : undefined}
              >
                {padBox(box.n)}
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
