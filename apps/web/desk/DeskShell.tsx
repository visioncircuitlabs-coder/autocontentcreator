import type { ReactNode } from "react";
import { StoryRail } from "./StoryRail";
import type { DeskStep } from "./types";

export function DeskShell({
  step,
  children,
}: {
  step: DeskStep;
  children: ReactNode;
}) {
  return (
    <div className="desk">
      <a className="skip" href="#desk-main">
        Skip to ticket
      </a>
      <aside className="rail-col">
        <StoryRail step={step} />
      </aside>
      <div className="desk-body">
        <header className="mast">
          <p className="tape">
            Unofficial Neutrogena fixture · not a Kenvue product
          </p>
          <h1>Content Machine</h1>
          <p className="mast-sub">
            Night inspection desk · a named human still stamps the last yes
          </p>
        </header>
        <main id="desk-main">{children}</main>
        <p className="footer-note">Vision Circuit Labs · paused export only</p>
      </div>
    </div>
  );
}
