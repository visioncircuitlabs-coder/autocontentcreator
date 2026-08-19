import Link from "next/link";
import { BOXES, LAYERS, padBox } from "../desk/boxes";
import { DeskShell } from "../desk/DeskShell";

export default function HomePage() {
  return (
    <DeskShell step="home">
      <p className="section-kicker">The walk</p>
      <ol className="walk">
        <li>
          <Link href="/radar">
            <b>1</b>
            <span>Fetch trends — signals, scores, gates</span>
          </Link>
        </li>
        <li>
          <Link href="/radar">
            <b>2</b>
            <span>Open a deep_dive — the report</span>
          </Link>
        </li>
        <li>
          <Link href="/factory">
            <b>3</b>
            <span>Create post — brief, grid, captions, judge trail</span>
          </Link>
        </li>
        <li>
          <Link href="/queue">
            <b>4</b>
            <span>Queue — approve or reject, reason required</span>
          </Link>
        </li>
        <li>
          <Link href="/queue">
            <b>5</b>
            <span>Preview — paused IG frame + ZIP</span>
          </Link>
        </li>
      </ol>
      <Link href="/radar" className="btn">
        Fetch trends
      </Link>
      <div className="spacer" />
      {LAYERS.map((layer) => (
        <section className="layer-block" key={layer.id}>
          <p className="section-kicker">{layer.label}</p>
          {BOXES.filter((box) => box.layer === layer.id).map((box) => (
            <Link key={box.id} href={box.href} className="box-line">
              <span className="n">{padBox(box.n)}</span>
              <span>
                <strong>{box.name}</strong>
                <br />
                <span className="quiet">{box.job}</span>
              </span>
            </Link>
          ))}
        </section>
      ))}
    </DeskShell>
  );
}
