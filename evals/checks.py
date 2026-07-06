#!/usr/bin/env python3
"""cine-teach deterministic eval grader (code grader).

Validates every case under evals/cases/. A case directory contains either
mapping.json (a full deck) or refusal.json (the suitability gate fired).

Usage: python3 evals/checks.py            # grade all cases
       python3 evals/checks.py <case_dir> # grade one case
Exit 0 = all pass, 1 = any failure.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from render import validate  # schema quality gates shared with the renderer

BREAK_CATEGORIES = {
    "missing_mechanism", "extra_mechanism", "reversed_agency", "scale_mismatch",
    "missing_adversary", "false_resolution", "collapsed_distinction", "temporal_distortion",
}


def check_deck(data):
    errors = list(validate(data))
    cards = data.get("cards", [])
    unmapped = data.get("unmapped", [])
    for c in cards:
        cid = c.get("id", "?")
        if c.get("break_category") not in BREAK_CATEGORIES:
            errors.append(f"{cid}: break_category '{c.get('break_category')}' not in taxonomy")
        for field, limit in (("break_point", 25), ("bridge", 25), ("definition", 25)):
            if len(c.get(field, "").split()) > limit:
                errors.append(f"{cid}: {field} exceeds {limit} words")
    for u in unmapped:
        if not u.get("direct_explanation") or not u.get("why_no_mapping"):
            errors.append(f"{u.get('id', '?')}: unmapped entries need direct_explanation and why_no_mapping")
    total = len(cards) + len(unmapped)
    if total:
        expected = len(cards) / total
        got = data.get("meta", {}).get("coverage_ratio", -1)
        if abs(expected - got) > 0.01:
            errors.append(f"meta.coverage_ratio {got} != computed {expected:.2f}")
    return errors


def check_refusal(data):
    errors = []
    if data.get("coverage_ratio", 1.0) >= 0.5:
        errors.append(f"refusal with coverage_ratio {data.get('coverage_ratio')} >= 0.5 — gate should not have fired")
    if not data.get("alternatives"):
        errors.append("refusal must suggest at least one alternative movie")
    if not data.get("explanation"):
        errors.append("refusal must carry a one-sentence explanation")
    return errors


def grade(case_dir):
    mapping, refusal = case_dir / "mapping.json", case_dir / "refusal.json"
    if mapping.exists():
        return "deck", check_deck(json.loads(mapping.read_text()))
    if refusal.exists():
        return "refusal", check_refusal(json.loads(refusal.read_text()))
    return "missing", ["no mapping.json or refusal.json"]


def main():
    root = Path(__file__).resolve().parent / "cases"
    dirs = [Path(a) for a in sys.argv[1:]] or sorted(p for p in root.iterdir() if p.is_dir())
    failed = False
    for d in dirs:
        kind, errors = grade(d)
        status = "PASS" if not errors else "FAIL"
        failed |= bool(errors)
        print(f"{status}  {d.name} ({kind})")
        for err in errors:
            print(f"      - {err}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
