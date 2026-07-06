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


CSS = """
:root {
  --bg: #0D1117; --primary: #E6EDF3; --secondary: #8B949E;
  --warm: #E8964A; --cool: #58A6FF; --surface: #161B22;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--primary); font-family: 'Inter', sans-serif; }
.deck { scroll-snap-type: y mandatory; overflow-y: scroll; height: 100vh; }
.card {
  scroll-snap-align: start; min-height: 100vh; display: flex; flex-direction: column;
  justify-content: center; align-items: center; padding: 80px 24px 60px;
}
.card__frame { width: 100%; max-width: 680px; display: flex; flex-direction: column; min-height: 78vh; }
.meta-line {
  font-weight: 500; font-size: 0.75rem; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--secondary);
}
.card__number { margin-bottom: 2.5rem; }
.anchor {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2.4rem;
  letter-spacing: -0.02em; line-height: 1.15;
}
.accent-line { width: 48px; height: 2px; background: var(--warm); margin: 1.8rem 0; }
.concept {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.6rem;
  letter-spacing: 0.01em; display: inline-block; align-self: flex-start;
  border-bottom: 3px solid var(--warm); padding-bottom: 0.2rem; margin-bottom: 1.6rem;
}
.mapping { font-size: 1.1rem; line-height: 1.5; max-width: 34em; }
.spacer { flex: 1 1 2rem; min-height: 2rem; }
.break-tag {
  background: var(--surface); border-radius: 8px; padding: 12px 16px;
  font-size: 0.85rem; line-height: 1.4; color: var(--secondary);
}
.break-tag strong {
  color: var(--warm); font-weight: 500; font-size: 0.7rem;
  letter-spacing: 0.08em; text-transform: uppercase; display: block; margin-bottom: 4px;
}
.bridge { margin-top: 1rem; }
.bridge__toggle {
  background: none; border: 1px solid var(--cool); color: var(--cool);
  font-family: 'Inter', sans-serif; font-weight: 500; font-size: 0.8rem;
  padding: 8px 14px; border-radius: 999px; cursor: pointer;
}
.bridge__toggle:focus-visible { outline: 2px solid var(--cool); outline-offset: 2px; }
.bridge__text {
  display: none; margin-top: 0.8rem; background: var(--surface);
  border-left: 2px solid var(--cool); border-radius: 0 8px 8px 0;
  padding: 12px 16px; font-size: 1rem; line-height: 1.5;
}
.bridge.is-open .bridge__text { display: block; }
.card__footer { margin-top: 2.5rem; }
/* Title card */
.card--title .card__frame { justify-content: center; align-items: flex-start; min-height: auto; }
.title-rule { width: 100%; height: 1px; background: var(--cool); margin: 2rem 0; }
.card--title h1 {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 3.2rem; line-height: 1.1;
}
.card--title .topic { font-size: 1.1rem; color: var(--secondary); margin-top: 1rem; }
.card--title .count { margin-top: 2rem; }
/* Limits card */
.card--limits .card__frame { background: rgba(232, 150, 74, 0.08); border-radius: 12px; padding: 48px 40px; min-height: auto; }
.card--limits h2 {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2rem; color: var(--warm);
  margin-bottom: 2rem;
}
.limit-row { margin-bottom: 1.6rem; }
.limit-row h3 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.4rem; }
.limit-row p { font-size: 0.95rem; line-height: 1.5; color: var(--primary); }
/* Coverage card */
.card--coverage h2 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.6rem; margin-bottom: 1.6rem; }
.coverage-grid { width: 100%; border-collapse: collapse; }
.coverage-grid td {
  padding: 10px 12px; border-bottom: 1px solid var(--surface);
  font-weight: 500; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--secondary); vertical-align: top;
}
.coverage-grid td:first-child { color: var(--primary); }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 0.7rem; white-space: nowrap; }
.badge--strong { background: var(--cool); color: var(--bg); }
.badge--partial { border: 1px solid var(--cool); color: var(--secondary); }
.badge--none { background: var(--warm); color: var(--bg); }
@media (max-width: 480px) {
  .anchor { font-size: 1.8rem; }
  .card--title h1 { font-size: 2.4rem; }
  .card { padding: 48px 20px 40px; }
}
"""

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
      <div class="meta-line card__number">Card {n:02d}</div>
      <div class="anchor">{e(c["movie_element"])}</div>
      <div class="accent-line"></div>
      <div class="concept">{e(c["concept"])}</div>
      <p class="mapping">{e(c["mapping_line"])}</p>
      <div class="spacer"></div>
      <div class="break-tag"><strong>Where it breaks</strong>{e(c["break_point"])}</div>
      <div class="bridge" aria-hidden="true">
        <button class="bridge__toggle" aria-expanded="false" aria-label="Show bridge to reality">&#8617; Back to reality</button>
        <p class="bridge__text">{e(c["bridge"])}</p>
      </div>
      <div class="meta-line card__footer">cine-teach &middot; {e(movie)} &middot; {n}/{total}</div>
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
      <div class="meta-line">cine-teach</div>
      <div class="title-rule"></div>
      <h1>{e(movie)} &times; {e(topic)}</h1>
      <p class="topic">One concept, one scene, one card.</p>
      <div class="meta-line count">{total} cards &middot; coverage {meta["coverage_ratio"]:.0%}</div>
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
      <div class="meta-line card__footer">These ideas are genuinely new &mdash; the movie has no shape for them.</div>
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
      <div class="meta-line card__footer">cine-teach &middot; {e(movie)} ({meta["movie_year"]}) &middot; generated {e(meta["generated_at"][:10])}</div>
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
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
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
