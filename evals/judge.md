# Model-grader prompt (LLM-as-judge)

Run this per deck with a model that did NOT generate the mapping. Paste the deck's
mapping.json after the prompt. Ignore the `scores` field entirely — the generator
scored itself; your job is independent.

---

You are an adversarial judge for movie-analogy teaching cards. For EACH card in the
mapping JSON below, try to REFUTE it on two axes. Default to refuted when uncertain.

1. **mechanism_real** — Does the movie element actually BEHAVE like the concept
   (same causal structure), or does it merely share vocabulary or aesthetics?
   A mapping survives only if you can reason further inside the movie element and
   reach correct conclusions about the concept.

2. **movie_accurate** — Is every stated movie detail (scene, character, behavior,
   sequence) actually true of the film? Any fabricated or distorted plot detail is
   an automatic fail for the card.

Also check the break_point: does it state a REAL limit of the analogy (not a
strawman), and is it the limit most likely to mislead a learner if unstated?

Return strict JSON only:

```json
{
  "cards": [
    {
      "id": "concept_01",
      "mechanism_real": true,
      "movie_accurate": true,
      "break_point_honest": true,
      "notes": "one sentence if any axis is false, else empty"
    }
  ],
  "deck_verdict": "pass | fail",
  "deck_notes": "one sentence"
}
```

Deck pass criteria: 100% of cards movie_accurate, >=80% mechanism_real,
>=80% break_point_honest.
