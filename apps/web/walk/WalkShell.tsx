"use client";

import type { ReactNode } from "react";
import { BEATS } from "../desk/words";

export function WalkShell({
  beat,
  showMachine,
  onToggleMachine,
  onJump,
  brandSlug,
  brandName,
  unofficialLine,
  children,
}: {
  beat: number;
  showMachine: boolean;
  onToggleMachine: () => void;
  onJump: (n: number) => void;
  brandSlug?: string;
  brandName?: string;
  unofficialLine?: string;
  children: ReactNode;
}) {
  return (
    <div className="walk-app" data-brand={brandSlug || undefined}>
      <a className="skip" href="#walk-main">
        Skip to the walk
      </a>
      <header className="walk-top">
        <div className="walk-brand">
          <h1>Make today’s post</h1>
          {brandName ? (
            <p className="walk-brand-meta">
              {brandName}
              {unofficialLine ? ` · ${unofficialLine}` : ""}
            </p>
          ) : null}
        </div>
        <ol className="beats" aria-label="Steps">
          {BEATS.map((item) => {
            const state =
              item.n === beat ? "now" : item.n < beat ? "done" : "todo";
            return (
              <li key={item.id}>
                <button
                  type="button"
                  className="beat"
                  data-state={state}
                  disabled={item.n > beat}
                  onClick={() => {
                    if (item.n <= beat) onJump(item.n);
                  }}
                >
                  <span className="beat-n">{item.n}</span>
                  <span className="beat-l">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ol>
      </header>
      <main id="walk-main">{children}</main>
      <p className="footer-note">
        Vision Circuit Labs · this pack does not go live
        {" · "}
        <button type="button" className="linkish" onClick={onToggleMachine}>
          {showMachine ? "Hide how it is made" : "How it is made"}
        </button>
      </p>
    </div>
  );
}
