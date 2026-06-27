#!/usr/bin/env python3
"""Gate route-compare outputs before residual, compute, or submit.

This is an admission filter, not a simulator. It parses public
BASE/CAND/COMPARE summary lines and blocks promotion unless the candidate is
channel-clean, agrees with the baseline comparison, and has a score edge against
the supplied frontier score.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any


SUMMARY_RE = re.compile(r"^(BASE|CAND|COMPARE)_SUMMARY\s+(.*)$")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def parse_keyvals(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in KV_RE.finditer(text)}


def load_summaries(path: Path) -> dict[str, dict[str, str]]:
    summaries: dict[str, dict[str, str]] = {}
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc
    for line in lines:
        match = SUMMARY_RE.match(line.strip())
        if not match:
            continue
        summaries[match.group(1).lower()] = parse_keyvals(match.group(2))
    return summaries


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except ValueError:
        return default


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(str(row.get(key, default)), 0)
    except ValueError:
        return default


def candidate_dirty_reasons(cand: dict[str, str]) -> list[str]:
    reasons = []
    for key, label in (
        ("classical", "candidate_classical"),
        ("phase_batches", "candidate_phase"),
        ("ancilla_batches", "candidate_ancilla"),
    ):
        if as_int(cand, key) != 0:
            reasons.append(label)
    return reasons


def compare_dirty_reasons(compare: dict[str, str]) -> list[str]:
    reasons = []
    if as_int(compare, "output_diff") != 0:
        reasons.append("compare_output_diff")
    if as_int(compare, "phase_diff_batches") != 0:
        reasons.append("compare_phase_diff")
    return reasons


def decide(summaries: dict[str, dict[str, str]], frontier_score: float) -> dict[str, Any]:
    missing = [name for name in ("cand", "compare") if name not in summaries]
    if missing:
        return {
            "candidate_clean": 0,
            "compare_clean": 0,
            "score_edge": 0,
            "score": "nan",
            "decision": "missing-summary",
            "reasons": ",".join(f"missing_{name}" for name in missing),
        }

    cand = summaries["cand"]
    compare = summaries["compare"]
    q = as_float(cand, "qubits")
    avg_tof = as_float(cand, "avg_tof")
    score = q * avg_tof
    cand_reasons = candidate_dirty_reasons(cand)
    compare_reasons = compare_dirty_reasons(compare)
    score_edge = bool(score and score < frontier_score)

    if cand_reasons:
        decision = "dirty-candidate-no-admission"
    elif compare_reasons:
        decision = "route-diff-no-admission"
    elif not score_edge:
        decision = "score-no-edge"
    else:
        decision = "route-clean-score-edge"

    return {
        "candidate_clean": int(not cand_reasons),
        "compare_clean": int(not compare_reasons),
        "score_edge": int(score_edge),
        "score": score,
        "decision": decision,
        "reasons": ",".join(cand_reasons + compare_reasons) or "none",
        "qubits": q,
        "avg_tof": avg_tof,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-compare", type=Path, required=True, help="route_compare.out-style summary log")
    parser.add_argument("--frontier-score", type=float, required=True, help="public score to beat")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summaries = load_summaries(args.route_compare)
    result = decide(summaries, args.frontier_score)
    score = result["score"]
    score_text = f"{score:.6f}" if isinstance(score, (int, float)) else str(score)
    print(
        "route_compare_admission=pass "
        f"candidate_clean={result['candidate_clean']} "
        f"compare_clean={result['compare_clean']} "
        f"score_edge={result['score_edge']} "
        f"score={score_text} "
        f"frontier_score={args.frontier_score:.6f} "
        f"qubits={result.get('qubits', 0):.0f} "
        f"avg_tof={result.get('avg_tof', 0):.6f} "
        f"decision={result['decision']} "
        f"reasons={result['reasons']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
