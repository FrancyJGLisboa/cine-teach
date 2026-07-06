# Card Schema

The JSON interchange format produced by Stage 2 (Map) and consumed by Stage 3
(Render). This is the contract between the intelligence layer and the visual layer.

---

## Top-level structure

```json
{
  "meta": {
    "movie": "Groundhog Day",
    "movie_year": 1993,
    "topic": "AI Agent Memory",
    "source_type": "transcript",
    "language": "EN",
    "audience": "technical generalist",
    "coverage_ratio": 0.83,
    "generated_at": "2026-07-06T14:30:00Z"
  },
  "cards": [ ... ],
  "overflow": [ ... ],
  "unmapped": [ ... ]
}
```

### `meta`

| Field | Type | Description |
|---|---|---|
| `movie` | string | Movie title as the user provided it |
| `movie_year` | integer | Release year (for disambiguation) |
| `topic` | string | The subject being taught, 2–6 words |
| `source_type` | enum | `transcript` \| `article` \| `documentation` \| `structured` \| `conversation` |
| `language` | enum | `EN` \| `PT-BR` \| `ES` |
| `audience` | string | Target audience description |
| `coverage_ratio` | float | Mapped concepts / total concepts (0.0–1.0) |
| `generated_at` | ISO 8601 | Timestamp of generation |

---

## `cards` array

Ordered by the sequencing logic in SKILL.md Stage 2. Each element:

```json
{
  "id": "concept_01",
  "position": 1,
  "concept": "Statelessness",
  "definition": "The model retains nothing between requests; every turn starts from zero.",
  "source_location": "0:51–1:08",

  "movie_element": "The townspeople of Punxsutawney",
  "movie_element_detail": "Every morning, every person Bill Murray meets has zero memory of the previous loop. They greet him identically, react identically, and have no accumulation across days.",
  "mapping_line": "The LLM is everyone else in Punxsutawney — every turn is genuinely their first morning.",
  "mechanism_match": "strong",
  "mapping_verdict": "strong",

  "break_point": "Unlike the townspeople, the LLM has no loop running at all — there is no tomorrow where things might be different.",
  "break_category": "missing_mechanism",
  "bridge": "The chat application replaying history is the actual Bill Murray — the one accumulating context across turns.",

  "scores": {
    "mechanism_fidelity": 5,
    "recognizability": 5,
    "breakage_clarity": 5,
    "caption_writability": 5,
    "overall": 5.0
  }
}
```

### Field definitions

| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | string | `concept_XX` | Stable ID from extraction |
| `position` | integer | 1-indexed | Render order in the deck |
| `concept` | string | 1–5 words | The technical concept name |
| `definition` | string | <=25 words | Internal definition, not shown on card |
| `source_location` | string | — | Where in the source material this concept appears |
| `movie_element` | string | 3–15 words | The character, scene, or mechanism being used |
| `movie_element_detail` | string | 1–3 sentences | Expanded description for the LLM's reasoning; not shown on card |
| `mapping_line` | string | <=20 words, no jargon | The card caption |
| `mechanism_match` | enum | `strong` \| `partial` \| `surface` \| `none` | Raw assessment |
| `mapping_verdict` | enum | `strong` \| `partial` \| `none` | Final verdict (surface → none) |
| `break_point` | string | <=25 words | Where the analogy stops being true |
| `break_category` | enum | See breakage_taxonomy.md | Classification of the failure mode |
| `bridge` | string | <=25 words | Sentence connecting the intuition back to technical reality |
| `scores` | object | — | Four dimensions + overall, per analogy_rubric.md |

---

## `overflow` array

Concepts extracted but excluded from the deck due to `MAX_CARDS`. Same schema as
`cards` but without `position` or `scores`. Allows the user to manually include them
in a follow-up generation or split into a second deck.

```json
{
  "id": "concept_13",
  "concept": "Benchmark gaming",
  "definition": "Vendors score well on their own benchmarks; scores rarely survive independent testing.",
  "source_location": "6:36–6:57",
  "reason_excluded": "Ranked 13th by pedagogical importance; MAX_CARDS=12."
}
```

---

## `unmapped` array

Concepts where `mapping_verdict` is `none`. These appear on the Limits Card in the
rendered deck with a direct explanation instead of a movie analogy.

```json
{
  "id": "concept_07",
  "concept": "Memory poisoning",
  "definition": "An attacker plants false data in long-term memory that resurfaces in future privileged sessions.",
  "source_location": "7:00–7:51",
  "direct_explanation": "A prompt injection that normally dies with the session instead persists in memory and resurfaces days later in a different context — a sleeper exploit with no movie parallel.",
  "closest_movie_element": null,
  "why_no_mapping": "The film has no adversarial actors and no mechanism for planted false memories that persist across resets."
}
```

---

## Validation rules

Before passing the JSON to the renderer:

1. Every `cards` entry with `mapping_verdict` of `strong` or `partial` must have
   non-empty `break_point` and `bridge`.
2. Every `cards` entry must have `scores.overall >= 3.0` and
   `scores.mechanism_fidelity >= 3`.
3. `cards` must be ordered by `position` (1 to N) with no gaps.
4. `len(cards) <= MAX_CARDS`.
5. All `mapping_line` values must be <=20 words and contain no terms from a
   domain-jargon blocklist (maintained per topic).
6. No `mechanism_match` of `surface` should survive into `cards` — those must be in
   `unmapped`.
