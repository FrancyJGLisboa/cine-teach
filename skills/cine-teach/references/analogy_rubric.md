# Analogy Rubric

Four dimensions, each scored 1–5. `overall_score` = simple mean rounded to 1
decimal. Apply scoring only to mappings with verdict `strong` or `partial`.

---

## Mechanism Fidelity

**Does the movie element operate by the same underlying mechanism as the concept?**

This is the most important dimension. A high-fidelity mapping survives follow-up
questions ("but what about...") without collapsing.

- **5**: The movie element and the concept share the same causal structure. The
  analogy holds under scrutiny — you can reason further using the movie element and
  arrive at correct conclusions about the concept.
- **4**: The causal structure matches for the core intuition. One secondary aspect
  diverges, but the divergence is easy to state as a caveat.
- **3**: The mechanism corresponds at a high level but diverges in specifics that
  matter. The analogy is useful for first contact but would mislead someone who took
  it literally.
- **2**: The correspondence is structural (same shape) but not mechanical (different
  cause). Looks like a match on a diagram; breaks immediately in conversation.
- **1**: The correspondence is naming or aesthetic only. The movie element does not
  behave like the concept in any operational sense.

Score <=2 should trigger reclassification to `mapping_verdict: "none"`.

---

## Recognizability

**How instantly will the target audience recall the movie element?**

The card must work in the first 3 seconds of viewing. If the movie reference
requires explanation, it has already failed as a hook.

- **5**: Iconic moment. Anyone who has seen the movie once will recognize it
  immediately. (e.g., "I am your father" in Star Wars, the red pill / blue pill in
  The Matrix)
- **4**: Memorable scene. Most viewers will recognize it, though some may need the
  character name or a short phrase to place it.
- **3**: Moderate. Fans remember it; casual viewers may not. The card will land for
  the right audience but not universally.
- **2**: Deep cut. Only dedicated fans will catch the reference. The card requires a
  secondary explanation that defeats the purpose.
- **1**: Obscure or easily confused with another scene. The reference adds friction
  rather than reducing it.

---

## Breakage Clarity

**How cleanly can the analogy's limits be stated?**

An analogy with murky limits is more dangerous than one with no mapping at all,
because the learner carries the false parts forward unknowingly.

- **5**: The break point is a single, crisp sentence. The learner immediately
  understands what the movie does NOT capture about the real concept.
- **4**: The break point can be stated in one sentence but requires a qualifier
  ("unlike X, the real system also...").
- **3**: The limits are real but require a short paragraph to explain. The break tag
  on the card will feel dense.
- **2**: Multiple independent failure modes. Hard to summarize. The analogy may
  confuse more than it clarifies for careful thinkers.
- **1**: The limits are so extensive or tangled that stating them undermines the
  mapping entirely. The learner would need to unlearn most of what the analogy
  suggested.

---

## Caption Writability

**Can the mapping be expressed in a single sentence (<=20 words) that a non-expert
understands?**

This dimension gates the visual output. A mapping that scores well on mechanism but
cannot be compressed into a caption will not survive the card format.

- **5**: The mapping line writes itself. The sentence is obvious once you see the
  connection, and it uses no jargon.
- **4**: A clean sentence is achievable with minor effort. One word might be
  borderline jargon but has a common-language substitute.
- **3**: The sentence is possible but requires compression that loses nuance. The
  card will work; the viewer who thinks carefully may find it slightly misleading.
- **2**: Compressing to one sentence forces either jargon or loss of the mechanism.
  The mapping may be better explained in prose than on a card.
- **1**: The connection is too abstract or multi-step to express in a caption. Better
  suited to a paragraph explanation than a visual card.

---

## Overall score

```
overall_score = round((mechanism_fidelity + recognizability + breakage_clarity + caption_writability) / 4, 1)
```

No weighting. If the user wants different weights, apply them downstream on the JSON
output.

---

## Interpretation

- **4.5–5.0**: Exceptional mapping. The card will be immediately understood and
  shared.
- **3.5–4.4**: Solid mapping. The card lands with minor caveats.
- **2.5–3.4**: Marginal. The mapping works for some audiences but not others. Include
  in the deck with a clear break tag; consider replacing if a better element exists.
- **1.5–2.4**: Weak. The analogy will confuse careful thinkers. Reclassify to `none`
  and provide a direct explanation instead.
- **<1.5**: Not a mapping. Should already be `verdict: "none"`.

---

## Decision rule

A concept enters the rendered deck only if `overall_score >= 3.0` AND
`mechanism_fidelity >= 3`. A mapping that scores 4.5 on recognizability but 2 on
mechanism fidelity is a trap — it is memorable and wrong. Exclude it.
