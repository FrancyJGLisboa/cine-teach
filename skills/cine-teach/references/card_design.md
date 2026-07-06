# Card Design System

The visual identity of cine-teach. Every rendered deck follows this system. The goal
is cinematic, not corporate — the cards should feel like they belong to the world of
the movie, not to a slide deck.

---

## Design philosophy

The card is not an infographic. It is a single moment of recognition: the viewer sees
a movie reference they already know, and in the same glance, acquires a new concept.
Everything on the card serves that moment. Nothing decorates.

The design has three principles:

1. **Cinematic presence.** Dark background, generous whitespace, dramatic type
   hierarchy. The cards should feel like title cards in a film, not cells in a
   spreadsheet.

2. **Glance legibility.** The movie anchor and concept label must be readable at
   phone-screen distance in a social media feed. If the type is too small to scan
   at a glance, the card has failed before the content is evaluated.

3. **Honest limits.** The break tag is visually distinct and always present. It is
   not hidden, footnoted, or de-emphasized into invisibility. The break is what
   earns the viewer's trust.

---

## Palette

Six colors. No gradients, no opacity effects on text.

| Role | Hex | Usage |
|---|---|---|
| Background | `#0D1117` | Card background, full bleed |
| Primary text | `#E6EDF3` | Movie anchor, concept label, mapping line |
| Secondary text | `#8B949E` | Break tag text, metadata, card numbers |
| Accent warm | `#E8964A` | Concept label underline, highlight on the Limits Card |
| Accent cool | `#58A6FF` | Movie anchor decorative element, links |
| Surface | `#161B22` | Break tag background, hover reveal background |

The palette is dark-first. A light-mode variant may be added later but is not in
scope for v1. Dark works better for cinematic feel and performs well on both mobile
OLED screens and projected presentations.

---

## Typography

Two typefaces. Load via Google Fonts.

**Display: `Space Grotesk`** (weights: 500, 700)
- Movie anchor: 700, 2.4rem, letter-spacing -0.02em
- Concept label: 700, 1.6rem, letter-spacing 0.01em
- Title card headings: 700, 3.2rem

**Body: `Inter`** (weights: 400, 500)
- Mapping line: 400, 1.1rem, line-height 1.5
- Break tag: 400, 0.85rem, line-height 1.4
- Bridge (on reveal/back): 400, 1.0rem
- Metadata and card numbers: 500, 0.75rem, letter-spacing 0.08em, uppercase

Import:
```
https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap
```

---

## Card layout

### Dimensions

The card is a fixed-ratio container. Two aspect ratios supported:

- **Social (4:5)**: width 1080px, height 1350px. Default for Instagram, LinkedIn.
- **Wide (16:9)**: width 1600px, height 900px. For X/Twitter, presentations.

In the HTML deck, cards render at a comfortable viewport size (max-width 680px for
social, max-width 960px for wide) and scale responsively. The PNG export uses the
full pixel dimensions.

### Zone structure (social 4:5)

```
┌─────────────────────────────┐
│                             │  <- 80px top padding
│  ┌─ CARD NUMBER ──────┐    │  <- 0.75rem, secondary text, top-left
│  │                     │    │
│  │  MOVIE ANCHOR       │    │  <- 2.4rem display, primary text
│  │  (2-3 lines max)    │    │
│  │                     │    │
│  │  ── accent line ──  │    │  <- 2px warm accent, 48px wide
│  │                     │    │
│  │  CONCEPT LABEL      │    │  <- 1.6rem display, primary text
│  │                     │    │     underlined with warm accent
│  │                     │    │
│  │  Mapping line that   │    │  <- 1.1rem body, primary text
│  │  connects the two.   │    │     max 2 lines at this size
│  │                     │    │
│  │                     │    │  <- flexible spacer
│  │  ┌─ BREAK TAG ────┐ │    │  <- surface background, rounded
│  │  │ Where it stops  │ │    │     0.85rem secondary text
│  │  │ being true.     │ │    │     12px padding
│  │  └─────────────────┘ │    │
│  │                     │    │
│  └─────────────────────┘    │
│                             │  <- 60px bottom padding
│  cine-teach · movie · N/M  │  <- footer metadata, secondary text
└─────────────────────────────┘
```

### Zone structure (wide 16:9)

Two-column layout. Left column (55%): movie anchor + accent line + concept label.
Right column (45%): mapping line + break tag. Footer spans full width.

---

## Special cards

### Title card

- Movie title in display font, 3.2rem
- Topic below in body font, 1.1rem, secondary text
- Card count: "6 cards" in metadata style
- No break tag zone
- Accent cool used for a decorative element (thin border, geometric shape, or
  character silhouette described in text — not an image)

### Limits card

- Titled "Where the analogy ends" in display font, warm accent
- Each unmapped concept as a row: concept label (display, 1.2rem) + direct
  explanation (body, 0.95rem)
- Background uses a subtle warm accent tint (#E8964A at 8% opacity) to visually
  differentiate from concept cards

### Coverage card (optional, 5+ cards)

- Compact grid: concept → movie element → verdict badge
- Verdict badges: `strong` = accent cool, `partial` = secondary text with cool
  border, `none` = warm accent
- Metadata font throughout
- Useful as a quick-reference when sharing the deck

---

## HTML structure

Single file. Structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{movie} × {topic} — cine-teach</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="..." rel="stylesheet">
  <style>
    /* Full design system here — no external CSS */
  </style>
</head>
<body>
  <div class="deck">
    <section class="card card--title"> ... </section>
    <section class="card card--concept" data-position="1"> ... </section>
    ...
    <section class="card card--limits"> ... </section>
    <section class="card card--coverage"> ... </section>
  </div>
</body>
</html>
```

CSS scroll-snap on `.deck` container:
```css
.deck {
  scroll-snap-type: y mandatory;
  overflow-y: scroll;
  height: 100vh;
}
.card {
  scroll-snap-align: start;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 60px 60px;
}
```

### Bridge reveal

The bridge sentence is hidden by default and revealed on click/tap:

```html
<div class="bridge" aria-hidden="true">
  <button class="bridge__toggle" aria-label="Show bridge to reality">
    ↩ Back to reality
  </button>
  <p class="bridge__text">{bridge sentence}</p>
</div>
```

Minimal JS — one event listener that toggles `aria-hidden` and a CSS class. No
framework, no build step.

---

## PNG export guidance

For the standalone CLI (scripts/render_png.py or equivalent):

1. Load the HTML in a headless browser (Playwright recommended).
2. Set viewport to card dimensions (1080×1350 for social, 1600×900 for wide).
3. Screenshot each `.card` section individually.
4. Output files named: `{deck_slug}_01_title.png`, `{deck_slug}_02_{concept_id}.png`,
   etc.

The HTML is the source of truth. The PNGs are derived artifacts. Any visual
discrepancy is a bug in the export, not a reason to modify the HTML.

---

## PDF export guidance

- One card per page.
- Page size matches card aspect ratio.
- Bridge sentence printed below the break tag (visible, unlike HTML).
- Final page: coverage grid + generation metadata.
- No headers, no page numbers, no margins beyond the card's own padding.

---

## Accessibility

- All text meets WCAG AA contrast against background (verified: #E6EDF3 on #0D1117
  is 13.1:1; #8B949E on #0D1117 is 4.6:1).
- Break tag background (#161B22) provides sufficient contrast for secondary text.
- Bridge toggle is keyboard-accessible.
- `lang` attribute set on `<html>` per the deck's language.
- Scroll-snap does not trap keyboard navigation.
