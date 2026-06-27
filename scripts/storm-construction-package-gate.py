#!/usr/bin/env python3
"""Gate lower-q construction packages by score economics and wall coverage."""

from __future__ import annotations

import argparse
import math


def parse_set(text: str) -> set[str]:
    return {item.strip() for item in text.split(",") if item.strip()}


def candidate_extra(args: argparse.Namespace) -> float:
    total = args.extra_avg_tof
    if args.extra_per_site is not None or args.charged_sites is not None:
        if args.extra_per_site is None or args.charged_sites is None:
            raise SystemExit("--extra-per-site and --charged-sites must be supplied together")
        total += args.extra_per_site * args.charged_sites
    return total


def clean_state(value: str) -> tuple[bool, str | None]:
    if value == "pass":
        return True, None
    if value == "unknown":
        return False, None
    return False, "dirty_candidate"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-score", type=float, default=1571592960.0)
    parser.add_argument("--current-qubits", type=int, default=1152)
    parser.add_argument("--current-avg-tof", type=float, default=1364230.0)
    parser.add_argument("--target-qubits", type=int, required=True)
    parser.add_argument("--extra-avg-tof", type=float, default=0.0)
    parser.add_argument("--extra-per-site", type=float)
    parser.add_argument("--charged-sites", type=int)
    parser.add_argument("--required-binders", default="", help="comma-separated wall binders the package must cover")
    parser.add_argument("--covered-binders", default="", help="comma-separated wall binders covered by this packet")
    parser.add_argument(
        "--candidate-clean",
        choices=("unknown", "pass", "fail"),
        default="unknown",
        help="trusted value/phase/ancilla status if already known",
    )
    args = parser.parse_args()

    if args.frontier_score <= 0 or args.current_avg_tof <= 0:
        parser.error("scores and average Toffoli must be positive")
    if args.current_qubits <= 0 or args.target_qubits <= 0:
        parser.error("qubit counts must be positive")
    if args.charged_sites is not None and args.charged_sites < 0:
        parser.error("--charged-sites must be non-negative")

    required = parse_set(args.required_binders)
    covered = parse_set(args.covered_binders)
    missing = sorted(required - covered)
    coverage_ok = not missing

    extra = candidate_extra(args)
    candidate_avg = args.current_avg_tof + extra
    candidate_score = candidate_avg * args.target_qubits
    max_avg_for_strict_beat = math.floor((args.frontier_score - 1) / args.target_qubits)
    headroom = max_avg_for_strict_beat - args.current_avg_tof
    score_edge = args.frontier_score - candidate_score
    count_ok = candidate_score < args.frontier_score
    clean_ok, clean_reason = clean_state(args.candidate_clean)

    reasons: list[str] = []
    if not coverage_ok:
        reasons.append("missing_coverage")
    if not count_ok:
        reasons.append("score_no_edge")
    if clean_reason is not None:
        reasons.append(clean_reason)

    if reasons:
        decision = "package-nack"
    elif clean_ok:
        decision = "ready-for-validation"
    else:
        decision = "count-prefilter-only"

    missing_text = ",".join(missing) if missing else "none"
    covered_text = ",".join(sorted(covered)) if covered else "none"
    required_text = ",".join(sorted(required)) if required else "none"
    reasons_text = ",".join(reasons) if reasons else "none"
    print(
        "construction_package_gate=pass "
        "evidence_label=Prefilter "
        f"frontier_score={args.frontier_score:.0f} "
        f"current_q={args.current_qubits} "
        f"current_avg_tof={args.current_avg_tof:.6f} "
        f"target_q={args.target_qubits} "
        f"target_max_avg_tof={max_avg_for_strict_beat} "
        f"headroom_avg_tof={headroom:.6f} "
        f"extra_avg_tof={extra:.6f} "
        f"candidate_avg_tof={candidate_avg:.6f} "
        f"candidate_score={candidate_score:.6f} "
        f"score_edge={score_edge:.6f} "
        f"required_binders={required_text} "
        f"covered_binders={covered_text} "
        f"missing_binders={missing_text} "
        f"coverage_ok={int(coverage_ok)} "
        f"count_ok={int(count_ok)} "
        f"candidate_clean={args.candidate_clean} "
        f"decision={decision} "
        f"reasons={reasons_text}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
