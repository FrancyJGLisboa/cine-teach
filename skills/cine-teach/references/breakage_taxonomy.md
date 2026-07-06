# Breakage Taxonomy

Every analogy breaks. The taxonomy below classifies HOW it breaks, so the break tag
on the card can be precise rather than vague. Each mapping in the deck carries a
`break_category` field drawn from this list.

The categories are mutually exclusive. If a mapping has multiple failure modes, pick
the one that is most likely to mislead a learner if left unstated.

---

## Categories

### `missing_mechanism`

The movie element lacks a mechanism that is central to the real concept.

**Pattern**: "The movie shows X, but the real system also does Y, and Y is the
important part."

**Example**: Groundhog Day × Statelessness. The townspeople reset every morning
(matches statelessness), but they exist inside a loop where tomorrow will happen
again. The LLM has no loop — there is no tomorrow. The missing mechanism is the
temporal container.

**Risk if unstated**: The learner assumes the concept includes persistence that it
does not have.

---

### `extra_mechanism`

The movie element has a mechanism that does NOT exist in the real concept.

**Pattern**: "The movie suggests X also does Y, but the real system only does X."

**Example**: The Matrix × Context Window. Neo downloads skills instantly into his
brain (matches loading information into a workspace), but his skills persist after
loading — they are permanent. The context window is wiped after every use.

**Risk if unstated**: The learner attributes a capability to the system that it does
not have.

---

### `reversed_agency`

The movie element assigns agency to the wrong entity — the character who acts in the
film is not the component that acts in the real system.

**Pattern**: "In the movie, A does the thing. In reality, B does it and A is
passive."

**Example**: Groundhog Day × Memory System. Bill Murray actively remembers (maps to
the memory system), but in the video's framing, the chat application — not the model
— is the entity that carries forward context. The model is passive. Murray's active
agency maps to the wrong component.

**Risk if unstated**: The learner attributes memory capability to the model itself
rather than to the surrounding infrastructure.

---

### `scale_mismatch`

The mechanism matches but operates at a fundamentally different scale, speed, or
magnitude in the real system.

**Pattern**: "The movie shows this happening to one person/thing. In reality, it
happens to millions simultaneously."

**Example**: Memento × Statelessness. Leonard's condition (no new long-term memories)
maps well to a stateless model. But Leonard is one person managing one investigation.
A stateless model serves millions of concurrent users — the scale is the architectural
reason for the design, not an affliction.

**Risk if unstated**: The learner understands the mechanism but misses the
engineering rationale behind it.

---

### `missing_adversary`

The real concept involves an adversarial or adversary-like dynamic that the movie
does not model.

**Pattern**: "The movie has no equivalent of someone deliberately exploiting this
mechanism."

**Example**: Any movie × Memory Poisoning. Most narrative films do not feature
adversarial memory manipulation. The concept of planting false data that persists
and resurfaces in a different context has no natural parallel in non-thriller films.

**Risk if unstated**: The learner builds a mental model that omits security as a
design consideration.

---

### `false_resolution`

The movie resolves or fixes the problem, but the real concept has no known solution.

**Pattern**: "In the movie, the character overcomes this. In reality, this is an open
problem."

**Example**: Groundhog Day × Forgetting on Purpose. Murray eventually "solves" his
loop by becoming a better person — a narrative resolution. The real problem of
deciding what to forget has no known general solution. It is an open research
challenge.

**Risk if unstated**: The learner assumes the problem is solved or solvable with
sufficient effort.

---

### `collapsed_distinction`

The movie merges two things that are distinct in the real system, making them appear
to be the same thing.

**Pattern**: "The movie treats X and Y as one thing. In reality, they are separate
mechanisms with different properties."

**Example**: Inception × Context Window vs. Long-Term Memory. Dream levels in
Inception could map to both the context window (the current level of the dream) and
long-term memory (the deeper levels). But the film treats all levels as the same
kind of thing — nested dreams. In reality, the context window and long-term memory
are architecturally different (RAM vs. disk), with different access patterns, costs,
and failure modes.

**Risk if unstated**: The learner conflates two mechanisms that must be understood
separately.

---

### `temporal_distortion`

The movie's timeline or sequencing does not match how the real process unfolds in
time.

**Pattern**: "The movie shows this as instant/slow/sequential, but in reality it is
slow/instant/parallel."

**Example**: The Matrix × RAG Retrieval. Trinity downloads the helicopter manual in
seconds (instant retrieval). Real RAG retrieval involves latency — embedding the
query, searching the vector store, ranking results, injecting into context. The
speed difference is not just quantitative; it changes the design constraints.

**Risk if unstated**: The learner underestimates the latency and cost of the real
operation.

---

## Usage in the mapping JSON

Each card carries one `break_category` from this list. The category informs the
break tag wording:

```json
{
  "break_point": "Unlike the townspeople, the LLM has no loop — there is no tomorrow.",
  "break_category": "missing_mechanism"
}
```

If the mapping has multiple breakage modes, pick the one that is MOST LIKELY TO
MISLEAD if left unstated. The goal is protecting the learner, not exhaustive
taxonomy.

---

## When no category fits

If the breakage does not fit any category, use `other` and write a clear
`break_point` sentence. If a pattern recurs across multiple decks, it is a candidate
for a new category. File it in the project's issue tracker.
