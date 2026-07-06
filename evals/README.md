# cine-teach eval suite

Eval-driven development for the skill: the mapping rules in `SKILL.md` are the
"prompt under test". Five movie × topic combinations (`combos.yaml`), four expected
to map well and one deliberately bad fit that must trigger the suitability refusal
instead of forced analogies.

## Two grader layers

**1. Code grader (deterministic)** — `checks.py` validates every case in `cases/`:
schema quality gates (shared with `scripts/render.py`), word limits, taxonomy
membership for `break_category`, coverage-ratio arithmetic, and refusal shape for
bad-fit cases.

```
python3 evals/checks.py          # exit 0 = all pass
```

**2. Model grader (LLM-as-judge)** — `judge.md` is an adversarial refutation prompt.
Run it per deck with a model that did NOT generate the mapping (never let the skill
grade its own homework). Judges score three axes per card: `mechanism_real`,
`movie_accurate`, `break_point_honest`. Deck passes at 100% movie-accurate,
≥80% mechanism-real, ≥80% honest breaks.

## Regeneration protocol

Each case in `cases/` was produced by an independent agent given only the skill
files and the combo's concept list — the generator is not told whether the combo is
expected to map or refuse. To regenerate a case, give a fresh session the prompt
pattern in `combos.yaml` plus the skill files, and let the suitability gate decide.

## Results

Run reports live in `results/` (one dated markdown file per full run).
