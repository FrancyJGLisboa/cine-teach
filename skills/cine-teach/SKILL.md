---
name: cine-teach
description: >
  Map technical concepts onto movies the user knows to produce visual concept cards
  for learning and social sharing. Takes any concept payload (raw text, transcript,
  structured JSON) plus a movie title and produces a scored mapping with visual card
  deck output (HTML, PNG, PDF). Trigger on phrases like "explain using a movie",
  "map this to [movie]", "cine-teach this", "movie analogy for", "explain like
  [movie title]", "use [movie] to teach", "card deck from this", "make this
  graspable", "visual analogy", or any combination of technical content plus a movie
  reference. Also trigger when the user has already started a movie-concept
  discussion and wants to formalize it into shareable cards. Do NOT trigger for
  plain movie discussion, film reviews, or requests to summarize a movie plot.
---

# Cine-teach

Map technical concepts onto movies. One concept, one scene, one card.

The output is the product — a visual card deck where each card pairs one technical
concept with one movie element, designed for three-second comprehension on a social
media feed and lasting retention for the viewer.

## Pipeline

Three stages, strictly sequential. No stage begins before the previous one completes.

1. **Extract** — Identify distinct concepts from the source material.
2. **Map** — For each concept, find the best movie element, score the mapping,
   identify where it breaks, and write the bridge back to reality.
3. **Render** — Produce the card deck as HTML (primary), with optional PNG and PDF
   export.

The interchange format between stages is a JSON mapping file (schema in
`references/card_schema.md`). This separation means anyone can write a custom
renderer without touching the mapping logic.

---

## Stage 1 — Extract

### Input types

The skill accepts three input forms:

- **Raw text**: transcript, article, documentation, thread. The LLM extracts
  concepts.
- **Structured JSON**: an array of `{concept, definition}` objects. Skip extraction.
- **Prior conversation**: concepts already discussed in the current session. The LLM
  collects and deduplicates them.

### Extraction rules

When extracting from raw text:

- Each concept must be a distinct, nameable idea — not a subpoint or example of
  another concept. If two ideas are parent-child, keep the parent unless the child
  stands alone pedagogically.
- Emit a one-sentence definition per concept (<=25 words). The definition is for
  internal scoring, not shown on the card.
- Cap at 12 concepts per deck. If the material contains more, rank by pedagogical
  importance and take the top 12. Leftover concepts go into a `overflow` array in
  the output JSON for the user to review.
- Order concepts in the sequence a learner should encounter them — dependency order,
  not order of appearance in the source.

### Output

A JSON array:

```json
[
  {
    "id": "concept_01",
    "concept": "Statelessness",
    "definition": "The model retains nothing between requests; every turn starts from zero.",
    "source_location": "0:51–1:08"
  }
]
```

---

## Stage 2 — Map

This is where the skill earns its keep. Read `references/analogy_rubric.md` before
scoring.

### Inputs

- The concept array from Stage 1.
- A movie title provided by the user.

### Movie suitability check (mandatory, runs first)

Before generating any mappings, assess coverage:

1. For each concept, does the movie contain a character, mechanism, scene, or plot
   beat that behaves analogously — not just sounds similar?
2. Count how many concepts have at least a partial mapping.
3. Compute `coverage_ratio = mapped / total`.

If `coverage_ratio < 0.5`, report it to the user with a one-sentence explanation and
suggest up to 3 alternative movies with better expected coverage. Do not proceed
until the user confirms a movie.

If `coverage_ratio >= 0.5`, proceed. Concepts with no viable mapping get a
`mapping_verdict: "none"` and receive a direct explanation instead of a forced
analogy.

### Per-concept mapping

For each concept, produce:

**movie_element** — The specific character, scene, mechanism, rule, or plot beat
being used. Not a vague reference ("it is like the Matrix") but a precise one
("the moment Neo sees the green code for the first time — the raw data behind the
rendered world").

**mapping_line** — A single sentence (<=20 words) that connects the movie element to
the concept. This is the caption on the card. It must be comprehensible to someone
who has seen the movie but does not know the technical domain. No jargon in this
line.

**mechanism_match** — Does the movie element actually behave like the concept, or
does it merely share surface vocabulary? This is the critical quality gate.
Similarity of label is not a mapping. Similarity of mechanism is.

- `strong`: The movie element operates by the same underlying mechanism as the
  concept. The analogy survives a follow-up question.
- `partial`: The mechanism corresponds for the core intuition but diverges on
  specifics. Useful with explicit caveats.
- `surface`: The correspondence is verbal or aesthetic, not mechanical. Do not use —
  reclassify as `none` or find a different element.
- `none`: No viable mapping exists in this movie.

**break_point** — One sentence (<=25 words) stating where the analogy stops being
true. Every `strong` and `partial` mapping must have a break point. Omit only for
`none`.

The break point is not a footnote. It is the intellectual honesty differentiator that
prevents the analogy from teaching a false model. Treat it as mandatory content, not
a disclaimer.

**bridge** — One sentence (<=25 words) connecting the movie-grounded intuition back
to the technical reality. The bridge prevents the learner from getting stuck in the
metaphor. It answers: "now that you have the intuition, here is what is actually
happening."

**mapping_verdict** — `strong` | `partial` | `none`. Derived from `mechanism_match`.
Surface mappings are reclassified to `none`.

### Scoring

Apply the four-dimension rubric from `references/analogy_rubric.md` to every mapping
with verdict `strong` or `partial`. Concepts with verdict `none` are not scored.

### Sequencing

After all concepts are mapped, determine the card order:

1. Start with the concept that has the strongest, most instantly recognizable mapping
   — this is the hook card.
2. Follow dependency order from Stage 1, breaking ties by score (higher first).
3. End with the concept whose bridge best sets up "and here is what to learn next."

### Output

The mapping JSON (full schema in `references/card_schema.md`).

---

## Stage 3 — Render

Read `references/card_design.md` before rendering.

### Card anatomy

Each card has four zones, top to bottom:

1. **Movie anchor** — The scene or character name. Display font, large. This is the
   hook that stops the scroll.
2. **Concept label** — The technical term. Clean sans-serif, positioned so the eye
   hits it immediately after the anchor.
3. **Mapping line** — The single-sentence caption connecting the two.
4. **Break tag** — A visually distinct small block stating where the analogy breaks.
   Uses a contrasting accent color or a different typographic treatment (e.g.,
   italic, reduced size, bordered).

The bridge sentence does not appear on the front of the card. It appears on:
- A hover/click reveal in the HTML version.
- The back of the card in print/PDF versions.
- A follow-up slide in carousel formats.

### Deck structure

A full deck contains:

- **Title card** — Movie title + topic + card count. "Groundhog Day × Agent Memory
  — 6 cards."
- **Concept cards** — One per mapped concept, in the sequence from Stage 2.
- **Limits card** — A summary of all concepts with verdict `none`, with direct
  explanations. Titled "Where the analogy ends." This card is pedagogically
  important — it tells the learner which ideas are genuinely new.
- **Coverage card** — A compact grid: concept → movie element → verdict, for quick
  reference. Optional, included when the deck has 5+ cards.

### Output formats

**Primary: HTML** — A single self-contained `.html` file. Each card is a
scroll-snap section. Dark background, cinematic aspect ratio. The HTML is the
development format, the preview format, and the shareable-link format. No external
JS dependencies. CSS inline or in `<style>` block. Only external dependency: Google
Fonts. See `references/card_design.md` for the full design system.

**Secondary: PNG set** — Each card rendered as a standalone image at
social-media-native resolutions. Produced by screenshotting the HTML via headless
browser (Playwright). Resolution targets:
- 1080×1350 (Instagram/LinkedIn carousel, 4:5)
- 1600×900 (X/Twitter, 16:9)

**Tertiary: PDF** — The full deck as a downloadable document, one card per page,
with the bridge sentences visible below each card and a summary table on the final
page.

---

## Hard rules

- **Never force an analogy.** If the mechanism does not match, the mapping verdict is
  `none`. A bad analogy is worse than no analogy — it teaches a false model that the
  learner will carry forward.
- **Never omit the break point.** Every `strong` and `partial` mapping has a stated
  limit. An analogy presented without its limits is misinformation dressed as
  pedagogy.
- **Never use surface mappings.** "X is like Y because they sound similar" is not a
  mapping. If the only correspondence is naming or aesthetic resemblance, discard it.
- **Never put jargon in the mapping line.** The mapping line is written for someone
  who knows the movie but not the domain. If a technical term appears, the mapping
  has failed its audience.
- **Always include the limits card.** Even if every concept mapped strongly, the
  limits card shows the learner where the movie stops being a useful model. Omitting
  it is the single biggest failure mode of analogy-based teaching.
- **Movie knowledge must be accurate.** If the LLM is uncertain about a plot detail,
  scene sequence, or character behavior, it must flag the uncertainty rather than
  fabricate a movie reference. An inaccurate movie reference destroys trust with the
  audience — they know the film and will catch errors.
- **12 cards maximum per deck.** Attention budget is finite. A 20-card deck will not
  be viewed. If the concept set exceeds 12, split into multiple decks or prune.
- **The card must work at glance speed.** If the movie anchor + concept label +
  mapping line cannot be absorbed in 3-5 seconds of viewing, the card has too much
  text. Rewrite until it fits.

---

## Variables

| Name | Description | Default |
|---|---|---|
| `SOURCE` | Raw text, JSON array, or `conversation` | required |
| `MOVIE` | Movie title | required |
| `AUDIENCE` | Target audience for calibrating jargon threshold | `technical generalist` |
| `LANGUAGE` | Output language: `EN`, `PT-BR`, `ES` | matches input |
| `MAX_CARDS` | Maximum concept cards in the deck | `12` |
| `FORMAT` | Output format(s): `html`, `png`, `pdf`, `all` | `html` |
| `ASPECT_RATIO` | Card aspect ratio for PNG: `4:5` (social), `16:9` (wide) | `4:5` |

---

## References

- `references/analogy_rubric.md` — Four-dimension scoring rubric for mapping quality
- `references/card_schema.md` — Full JSON schema for the mapping interchange format
- `references/card_design.md` — Visual design system: palette, typography, layout, responsive rules
- `references/breakage_taxonomy.md` — Categories of analogy failure with examples
