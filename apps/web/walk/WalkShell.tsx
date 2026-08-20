"use client";

import type { ReactNode } from "react";
import { BEATS } from "../desk/words";

export function WalkShell({
  beat,
  showMachine,
  onToggleMachine,
  onJump,
  children,
}: {
  beat: number;
  showMachine: boolean;
  onToggleMachine: () => void;
  onJump: (n: number) => void;
  children: ReactNode;
}) {
  return (
    <div className="walk-app">
      <a className="skip" href="#walk-main">
        Skip to the walk
      </a>
      <header className="walk-top">
        <div className="walk-brand">
          <h1>Make today’s post</h1>
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
