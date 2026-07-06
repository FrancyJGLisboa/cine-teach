#!/usr/bin/env python3
"""cine-teach Stage 3 renderer: mapping.json -> self-contained HTML deck.

Implements references/card_design.md. Stdlib only.

Usage: python3 scripts/render.py examples/groundhog-day-agent-memory/mapping.json [-o deck.html]
"""

import argparse
import json
import sys
from html import escape
from pathlib import Path

MAX_CARDS = 12


def validate(data):
    """Schema validation rules from references/card_schema.md."""
    errors = []
    cards = data.get("cards", [])
    if len(cards) > MAX_CARDS:
        errors.append(f"{len(cards)} cards exceeds MAX_CARDS={MAX_CARDS}")
    positions = [c.get("position") for c in cards]
    if positions != list(range(1, len(cards) + 1)):
        errors.append(f"positions must be 1..N with no gaps, got {positions}")
    for c in cards:
        cid = c.get("id", "?")
        if c.get("mapping_verdict") not in ("strong", "partial"):
            errors.append(f"{cid}: verdict '{c.get('mapping_verdict')}' does not belong in cards[]")
        if not c.get("break_point") or not c.get("bridge"):
            errors.append(f"{cid}: break_point and bridge are mandatory")
        s = c.get("scores", {})
        if s.get("overall", 0) < 3.0 or s.get("mechanism_fidelity", 0) < 3:
            errors.append(f"{cid}: scores below quality gate (overall>=3.0, mechanism_fidelity>=3)")
        if len(c.get("mapping_line", "").split()) > 20:
            errors.append(f"{cid}: mapping_line exceeds 20 words")
        # ponytail: jargon-blocklist check (rule 5) not implemented; add when a per-topic blocklist exists
    return errors


# SVG film grain, inlined as a data URI so the deck stays a single file.
GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E"
         "%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")

CSS = """
:root {
  --bg: #0A0908; --primary: #F2EDE4; --secondary: #A39A8B;
  --amber: #E5A00D; --velvet: #B4433C; --surface: #141110;
  --serif: 'Fraunces', Georgia, serif;
  --mono: 'Courier Prime', 'Courier New', monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; background: #000; }
html::before, html::after {
  content: ''; position: fixed; left: 0; right: 0; height: 14px;
  background: #000; z-index: 12; pointer-events: none;
}
html::before { top: 0; } html::after { bottom: 0; }
body { background: var(--bg); color: var(--primary); font-family: var(--serif); }
body::before {
  content: ''; position: fixed; inset: 0; z-index: 10; pointer-events: none;
  background: radial-gradient(ellipse at center, transparent 52%, rgba(0,0,0,0.5) 100%);
}
body::after {
  content: ''; position: fixed; inset: 0; z-index: 11; pointer-events: none;
  background-image: url("__GRAIN__"); opacity: 0.05;
}
.deck { scroll-snap-type: y mandatory; overflow-y: scroll; height: 100vh; height: 100dvh; }
.card {
  scroll-snap-align: start; min-height: 100vh; min-height: 100dvh;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  padding: 72px 28px 56px;
}
.card__frame { width: 100%; max-width: 640px; display: flex; flex-direction: column; min-height: 76vh; }
@supports (animation-timeline: view()) {
  .card__frame {
    animation: rise both; animation-timeline: view(); animation-range: entry 5% entry 55%;
  }
}
@keyframes rise { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: none; } }
@keyframes fadeup { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
.mono {
  font-family: var(--mono); font-weight: 400; font-size: 0.78rem;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--secondary);
}
.card__number { margin-bottom: 2.6rem; }
.card__number b { color: var(--amber); font-weight: 700; }
.anchor {
  font-weight: 900; font-size: clamp(2.1rem, 6vw, 3rem);
  letter-spacing: -0.01em; line-height: 1.06;
}
.sprockets {
  width: 128px; height: 11px; margin: 1.9rem 0;
  background: repeating-linear-gradient(90deg, var(--amber) 0 9px, transparent 9px 21px);
  opacity: 0.9;
}
.concept {
  font-family: var(--mono); font-weight: 700; font-size: 1.05rem;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--primary);
  display: inline-block; align-self: flex-start;
  border-bottom: 3px solid var(--amber); padding-bottom: 0.3rem; margin-bottom: 1.7rem;
}
.mapping { font-weight: 400; font-size: 1.25rem; line-height: 1.55; max-width: 30em; }
.spacer { flex: 1 1 2rem; min-height: 2rem; }
.break-tag {
  border-left: 3px solid var(--amber); background: rgba(229, 160, 13, 0.06);
  padding: 14px 18px; font-family: var(--mono); font-size: 0.88rem;
  line-height: 1.5; color: var(--secondary);
}
.break-tag strong {
  display: block; margin-bottom: 5px; color: var(--amber); font-weight: 700;
  font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase;
}
.bridge { margin-top: 1.1rem; }
.bridge__toggle {
  background: none; border: 1px solid var(--secondary); color: var(--primary);
  font-family: var(--mono); font-weight: 700; font-size: 0.74rem;
  letter-spacing: 0.14em; text-transform: uppercase;
  padding: 10px 16px; cursor: pointer; transition: all 0.15s ease;
}
.bridge__toggle:hover { background: var(--primary); color: var(--bg); border-color: var(--primary); }
.bridge__toggle:focus-visible { outline: 2px solid var(--amber); outline-offset: 2px; }
.bridge__text {
  display: none; margin-top: 0.9rem; border-left: 3px solid var(--primary);
  background: var(--surface); padding: 14px 18px;
  font-family: var(--mono); font-size: 0.92rem; line-height: 1.55;
}
.bridge.is-open .bridge__text { display: block; animation: fadeup 0.3s ease both; }
.card__footer { margin-top: 2.6rem; }
/* Title card */
.card--title .card__frame { justify-content: center; min-height: auto; }
.card--title .eyebrow { color: var(--amber); animation: fadeup 0.7s ease 0.1s both; }
.title-rule { width: 100%; height: 1px; background: var(--secondary); opacity: 0.5; margin: 1.8rem 0 2.4rem; animation: fadeup 0.7s ease 0.25s both; }
.card--title h1 {
  font-weight: 900; font-size: clamp(3rem, 10vw, 4.6rem); line-height: 1.02;
  letter-spacing: -0.015em; animation: fadeup 0.7s ease 0.4s both;
}
.card--title .cross {
  font-family: var(--mono); color: var(--amber); font-size: 1.5rem;
  margin: 1.4rem 0; animation: fadeup 0.7s ease 0.55s both;
}
.card--title .topic {
  font-family: var(--mono); font-weight: 700; font-size: 1.35rem;
  letter-spacing: 0.18em; text-transform: uppercase; animation: fadeup 0.7s ease 0.7s both;
}
.card--title .tagline { font-style: italic; font-size: 1.1rem; color: var(--secondary); margin-top: 2.2rem; animation: fadeup 0.7s ease 0.85s both; }
.card--title .count { margin-top: 2.4rem; animation: fadeup 0.7s ease 1s both; }
/* Limits card */
.card--limits .card__frame {
  background: rgba(180, 67, 60, 0.07); border: 1px solid rgba(180, 67, 60, 0.3);
  padding: 48px 40px; min-height: auto;
}
.card--limits h2 { font-weight: 900; font-style: italic; font-size: 2.1rem; color: var(--velvet); margin-bottom: 2rem; }
.limit-row { margin-bottom: 1.7rem; }
.limit-row h3 {
  font-family: var(--mono); font-weight: 700; font-size: 0.95rem;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--amber); margin-bottom: 0.4rem;
}
.limit-row p { font-size: 1.05rem; line-height: 1.55; }
/* Coverage card */
.card--coverage h2 { font-weight: 900; font-size: 1.8rem; margin-bottom: 1.8rem; }
.coverage-grid { width: 100%; border-collapse: collapse; }
.coverage-grid td {
  padding: 12px 10px; border-bottom: 1px solid var(--surface);
  font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--secondary); vertical-align: top;
}
.coverage-grid td:first-child { color: var(--primary); font-weight: 700; }
.badge { padding: 3px 10px; font-size: 0.7rem; font-weight: 700; white-space: nowrap; }
.badge--strong { background: var(--amber); color: var(--bg); }
.badge--partial { border: 1px solid var(--amber); color: var(--amber); }
.badge--none { background: var(--velvet); color: var(--primary); }
@media (max-width: 480px) {
  .card { padding: 44px 20px 36px; }
  .mapping { font-size: 1.1rem; }
}
@media (prefers-reduced-motion: reduce) {
  .card__frame, .card--title * { animation: none !important; }
}
""".replace("__GRAIN__", GRAIN)

JS = """
document.querySelectorAll('.bridge__toggle').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var bridge = btn.closest('.bridge');
    var open = bridge.classList.toggle('is-open');
    bridge.setAttribute('aria-hidden', String(!open));
    btn.setAttribute('aria-expanded', String(open));
  });
});
"""


def e(s):
    return escape(str(s))


def concept_card(c, total, movie):
    n = c["position"]
    return f"""
  <section class="card card--concept" data-position="{n}">
    <div class="card__frame">
      <div class="mono card__number"><b>{n:02d}</b> / {total:02d}</div>
      <div class="anchor">{e(c["movie_element"])}</div>
      <div class="sprockets"></div>
      <div class="concept">{e(c["concept"])}</div>
      <p class="mapping">{e(c["mapping_line"])}</p>
      <div class="spacer"></div>
      <div class="break-tag"><strong>Where it breaks</strong>{e(c["break_point"])}</div>
      <div class="bridge" aria-hidden="true">
        <button class="bridge__toggle" aria-expanded="false" aria-label="Show bridge to reality">Smash cut to: reality</button>
        <p class="bridge__text">{e(c["bridge"])}</p>
      </div>
      <div class="mono card__footer">cine-teach &middot; {e(movie)} &middot; {n}/{total}</div>
    </div>
  </section>"""


def render(data):
    meta = data["meta"]
    cards = sorted(data["cards"], key=lambda c: c["position"])
    unmapped = data.get("unmapped", [])
    movie, topic, total = meta["movie"], meta["topic"], len(cards)

    sections = [f"""
  <section class="card card--title">
    <div class="card__frame">
      <div class="mono eyebrow">A cine-teach production</div>
      <div class="title-rule"></div>
      <h1>{e(movie)}</h1>
      <div class="cross">&times;</div>
      <div class="topic">{e(topic)}</div>
      <p class="tagline">One concept, one scene, one card.</p>
      <div class="mono count">{total} cards &middot; coverage {meta["coverage_ratio"]:.0%}</div>
    </div>
  </section>"""]
    sections += [concept_card(c, total, movie) for c in cards]

    if unmapped:
        rows = "".join(
            f'<div class="limit-row"><h3>{e(u["concept"])}</h3><p>{e(u["direct_explanation"])}</p></div>'
            for u in unmapped
        )
        sections.append(f"""
  <section class="card card--limits">
    <div class="card__frame">
      <h2>Where the analogy ends</h2>
      {rows}
      <div class="mono card__footer">These ideas are genuinely new &mdash; the movie has no shape for them.</div>
    </div>
  </section>""")

    if total >= 5:
        rows = "".join(
            f'<tr><td>{e(c["concept"])}</td><td>{e(c["movie_element"])}</td>'
            f'<td><span class="badge badge--{c["mapping_verdict"]}">{c["mapping_verdict"]}</span></td></tr>'
            for c in cards
        ) + "".join(
            f'<tr><td>{e(u["concept"])}</td><td>&mdash;</td><td><span class="badge badge--none">none</span></td></tr>'
            for u in unmapped
        )
        sections.append(f"""
  <section class="card card--coverage">
    <div class="card__frame">
      <h2>Coverage</h2>
      <table class="coverage-grid">{rows}</table>
      <div class="mono card__footer">cine-teach &middot; {e(movie)} ({meta["movie_year"]}) &middot; generated {e(meta["generated_at"][:10])}</div>
    </div>
  </section>""")

    lang = {"EN": "en", "PT-BR": "pt-BR", "ES": "es"}.get(meta.get("language", "EN"), "en")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(movie)} &times; {e(topic)} &mdash; cine-teach</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,900;1,9..144,400;1,9..144,900&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="deck">{"".join(sections)}
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description="Render a cine-teach mapping.json to an HTML deck")
    p.add_argument("mapping", type=Path)
    p.add_argument("-o", "--output", type=Path, help="output path (default: deck.html beside mapping)")
    args = p.parse_args()

    data = json.loads(args.mapping.read_text())
    errors = validate(data)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    out = args.output or args.mapping.parent / "deck.html"
    out.write_text(render(data))
    print(f"Rendered {len(data['cards'])} cards -> {out}")


if __name__ == "__main__":
    main()
