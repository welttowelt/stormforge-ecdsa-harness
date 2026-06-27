#!/usr/bin/env python3
"""Gate post-local-optimum ECDSA.fail frontier escape packets."""

from __future__ import annotations

import argparse


def pass_flag(value: str) -> bool:
    return value == "pass"


def has_score_edge(value: float | None) -> bool:
    return value is not None and value > 0


def reason_text(reasons: list[str]) -> str:
    return ",".join(reasons) if reasons else "none"


def decide_current_corpus(args: argparse.Namespace, reasons: list[str]) -> str:
    if args.local_optimum == "measured" and not args.new_source_evidence:
        reasons.append("current_corpus_closed")
    if not has_score_edge(args.score_edge):
        reasons.append("score_no_edge")
    return "escape-nack" if reasons else "prefilter-only"


def decide_source_theorem(args: argparse.Namespace, reasons: list[str]) -> str:
    if args.source_support != "certified":
        reasons.append("source_support_not_certified")
    if args.expected_avg_saving <= 0:
        reasons.append("no_avg_saving")
    if not has_score_edge(args.score_edge):
        reasons.append("score_no_edge")
    if args.candidate_clean == "fail":
        reasons.append("dirty_candidate")
    if reasons:
        return "escape-nack"
    if args.candidate_clean == "pass":
        return "ready-for-validation"
    return "source-theorem-prefilter-only"


def decide_construction(args: argparse.Namespace, reasons: list[str]) -> str:
    if not pass_flag(args.coverage):
        reasons.append("missing_coverage")
    if not pass_flag(args.count):
        reasons.append("score_no_edge")
    if args.candidate_clean == "fail":
        reasons.append("dirty_candidate")
    if reasons:
        return "escape-nack"
    if args.candidate_clean == "pass":
        return "ready-for-validation"
    return "construction-prefilter-only"


def decide_nonce_retune(args: argparse.Namespace, reasons: list[str]) -> str:
    if args.nonce_retune_status == "none":
        reasons.append("no_retune_evidence")
    elif args.nonce_retune_status == "prefilter":
        reasons.append("prefilter_only")
    if not has_score_edge(args.score_edge):
        reasons.append("score_no_edge")
    if args.candidate_clean != "pass":
        reasons.append("candidate_not_clean")
    if reasons:
        return "escape-nack"
    if args.nonce_retune_status == "official-clean":
        return "ready-for-submit-gate"
    return "ready-for-validation"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--escape-class",
        required=True,
        choices=("current-corpus-knob", "source-theorem", "construction-package", "nonce-retune"),
    )
    parser.add_argument("--frontier-score", type=float, default=1571592960.0)
    parser.add_argument("--source", default="d44cad3")
    parser.add_argument("--local-optimum", choices=("unknown", "measured", "not-measured"), default="measured")
    parser.add_argument("--new-source-evidence", action="store_true")
    parser.add_argument("--score-edge", type=float, help="candidate score improvement versus frontier; positive means better")
    parser.add_argument("--source-support", choices=("none", "certified", "unknown", "counterexample"), default="none")
    parser.add_argument("--expected-avg-saving", type=float, default=0.0)
    parser.add_argument("--coverage", choices=("unknown", "pass", "fail"), default="unknown")
    parser.add_argument("--count", choices=("unknown", "pass", "fail"), default="unknown")
    parser.add_argument("--candidate-clean", choices=("unknown", "pass", "fail"), default="unknown")
    parser.add_argument(
        "--nonce-retune-status",
        choices=("none", "prefilter", "clean-island", "official-clean"),
        default="none",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.frontier_score <= 0:
        raise SystemExit("--frontier-score must be positive")

    reasons: list[str] = []
    if args.escape_class == "current-corpus-knob":
        decision = decide_current_corpus(args, reasons)
    elif args.escape_class == "source-theorem":
        decision = decide_source_theorem(args, reasons)
    elif args.escape_class == "construction-package":
        decision = decide_construction(args, reasons)
    elif args.escape_class == "nonce-retune":
        decision = decide_nonce_retune(args, reasons)
    else:  # pragma: no cover - argparse enforces choices.
        raise AssertionError(args.escape_class)

    score_edge = args.score_edge if args.score_edge is not None else "none"
    print(
        "frontier_escape_gate=pass "
        "evidence_label=Prefilter "
        f"frontier_score={args.frontier_score:.0f} "
        f"source={args.source} "
        f"escape_class={args.escape_class} "
        f"local_optimum={args.local_optimum} "
        f"new_source_evidence={int(args.new_source_evidence)} "
        f"score_edge={score_edge} "
        f"source_support={args.source_support} "
        f"expected_avg_saving={args.expected_avg_saving:.6f} "
        f"coverage={args.coverage} "
        f"count={args.count} "
        f"candidate_clean={args.candidate_clean} "
        f"nonce_retune_status={args.nonce_retune_status} "
        f"decision={decision} "
        f"reasons={reason_text(reasons)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
