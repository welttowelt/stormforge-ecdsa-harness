#!/usr/bin/env python3
"""Gate route-compare outputs before residual, compute, or submit.

This is an admission filter, not a simulator. It parses public
BASE/CAND/COMPARE summary lines and blocks promotion unless the baseline and
candidate are channel-clean, the comparison agrees, and the candidate has a
score edge against the supplied frontier score.
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


def summary_dirty_reasons(row: dict[str, str], prefix: str) -> list[str]:
    reasons = []
    for key, label in (
        ("classical", f"{prefix}_classical"),
        ("phase_batches", f"{prefix}_phase"),
        ("ancilla_batches", f"{prefix}_ancilla"),
    ):
        if as_int(row, key) != 0:
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
    missing = [name for name in ("base", "cand", "compare") if name not in summaries]
    if missing:
        return {
            "gate": "hold",
            "admitted": 0,
            "baseline_clean": 0,
            "candidate_clean": 0,
            "compare_clean": 0,
            "score_edge": 0,
            "score": "nan",
            "decision": "missing-summary",
            "reasons": ",".join(f"missing_{name}" for name in missing),
        }

    base = summaries["base"]
    cand = summaries["cand"]
    compare = summaries["compare"]
    q = as_float(cand, "qubits")
    avg_tof = as_float(cand, "avg_tof")
    score = q * avg_tof
    base_reasons = summary_dirty_reasons(base, "baseline")
    cand_reasons = summary_dirty_reasons(cand, "candidate")
    compare_reasons = compare_dirty_reasons(compare)
    score_edge = bool(score and score < frontier_score)

    if base_reasons:
        gate = "fail"
        decision = "dirty-baseline-no-admission"
    elif cand_reasons:
        gate = "fail"
        decision = "dirty-candidate-no-admission"
    elif compare_reasons:
        gate = "fail"
        decision = "route-diff-no-admission"
    elif not score_edge:
        gate = "fail"
        decision = "score-no-edge"
    else:
        gate = "pass"
        decision = "route-clean-score-edge"

    return {
        "gate": gate,
        "admitted": int(gate == "pass"),
        "baseline_clean": int(not base_reasons),
        "candidate_clean": int(not cand_reasons),
        "compare_clean": int(not compare_reasons),
        "score_edge": int(score_edge),
        "score": score,
        "decision": decision,
        "reasons": ",".join(base_reasons + cand_reasons + compare_reasons) or "none",
        "qubits": q,
        "avg_tof": avg_tof,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-compare", type=Path, required=True, help="route_compare.out-style summary log")
    parser.add_argument("--frontier-score", type=float, required=True, help="public score to beat")
    parser.add_argument("--require-admission", action="store_true", help="exit nonzero unless the gate admits the route")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summaries = load_summaries(args.route_compare)
    result = decide(summaries, args.frontier_score)
    score = result["score"]
    score_text = f"{score:.6f}" if isinstance(score, (int, float)) else str(score)
    print(
        f"route_compare_admission={result['gate']} "
        f"admitted={result['admitted']} "
        f"baseline_clean={result['baseline_clean']} "
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
    if args.require_admission and not result["admitted"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
