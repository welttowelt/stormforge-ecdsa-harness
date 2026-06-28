#!/usr/bin/env python3
"""Toy gate for FFG graduated suffix carry pair-complete claims.

This is a public-safe control-plane checker. It does not build, eval, submit,
or inspect private traces. It separates two facts that were easy to blur in the
live q1152 work:

1. A constant-add chunk carry is predictable from final chunk bits, the chunk
   constant, the control, and a live carry-in.
2. The current HMR erase for carry[j+1] still needs carry[j]. A no-recompute
   pair-complete plan that frees carry[j] early is therefore not a proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class CarryCase:
    width: int
    const: int
    ctrl: int
    cin: int
    original: int
    final: int
    carry: int
    predicted: int


def mask(width: int) -> int:
    return (1 << width) - 1


def addend(width: int, const: int, ctrl: int, cin: int) -> int:
    return (ctrl * (const & mask(width))) + cin


def carry_from_final(width: int, final: int, const: int, ctrl: int, cin: int) -> int:
    """Recover carry-out from final low bits for x + ctrl*const + cin.

    The addend can equal 2**width only in the all-ones-constant plus cin case.
    In that edge case the carry is always one and the low bits are unchanged.
    """

    modulus = 1 << width
    inc = addend(width, const, ctrl, cin)
    if inc == 0:
        return 0
    if inc == modulus:
        return 1
    return int(final < inc)


def iter_carry_cases(max_width: int) -> list[CarryCase]:
    cases: list[CarryCase] = []
    for width in range(1, max_width + 1):
        modulus = 1 << width
        for const in range(modulus):
            for ctrl in (0, 1):
                for cin in (0, 1):
                    inc = addend(width, const, ctrl, cin)
                    for original in range(modulus):
                        total = original + inc
                        final = total & (modulus - 1)
                        carry = int(total >= modulus)
                        predicted = carry_from_final(width, final, const, ctrl, cin)
                        cases.append(CarryCase(width, const, ctrl, cin, original, final, carry, predicted))
    return cases


def first_mismatch(cases: list[CarryCase]) -> CarryCase | None:
    for case in cases:
        if case.carry != case.predicted:
            return case
    return None


def dependency_violations(chunks: int) -> list[str]:
    """Model the unsafe early-free claim, not a recompute plan.

    In the current source shape, erase(carry[j+1]) needs carry[j] as the
    comparator carry-in. If carry[j] was freed before carry[j+1] was erased and
    no recompute certificate exists, the proof is missing.
    """

    violations: list[str] = []
    for j in range(chunks - 1):
        violations.append(f"erase_carry_{j + 1}_needs_freed_carry_{j}")
    return violations


def recompute_lower_bound(chunks: int) -> int:
    """Boundary-predicate lower bound for rebuilding predecessors on demand."""

    return chunks * (chunks - 1) // 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-width", type=int, default=6, help="exhaustive chunk width for carry predictor")
    parser.add_argument("--chunks", type=int, default=4, help="graduated suffix boundary carries to model")
    parser.add_argument(
        "--allow-recompute",
        action="store_true",
        help="classify the result as a recompute-proof hold instead of a no-recompute NACK",
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="exit nonzero unless this toy fully admits the route; current public toy never admits source edits",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.max_width < 1:
        raise SystemExit("--max-width must be positive")
    if args.chunks < 1:
        raise SystemExit("--chunks must be positive")

    cases = iter_carry_cases(args.max_width)
    mismatch = first_mismatch(cases)
    predictor_mismatches = 1 if mismatch else 0
    violations = dependency_violations(args.chunks)
    no_recompute_violations = len(violations)
    recompute_required = int(no_recompute_violations > 0)
    recompute_ops = recompute_lower_bound(args.chunks)

    if predictor_mismatches:
        gate = "fail"
        decision = "carry-predictor-bug"
        source_edit_ready = 0
    elif args.allow_recompute and recompute_required:
        gate = "hold"
        decision = "recompute-plan-needs-source-phase-score-proof"
        source_edit_ready = 0
    elif no_recompute_violations:
        gate = "fail"
        decision = "no-recompute-pair-complete-nack"
        source_edit_ready = 0
    else:
        gate = "hold"
        decision = "single-boundary-toy-only-no-source-edit"
        source_edit_ready = 0

    witness = violations[0] if violations else "none"
    print(
        f"ffg_pair_complete_toy={gate} "
        "evidence_label=Partial "
        f"max_width={args.max_width} "
        f"carry_predictor_cases={len(cases)} "
        f"carry_predictor_mismatches={predictor_mismatches} "
        f"chunks={args.chunks} "
        f"full_resident_carry_peak={args.chunks} "
        f"top_down_no_recompute_peak={args.chunks} "
        f"unsafe_early_free_peak={min(args.chunks, 2)} "
        f"no_recompute_dependency_violations={no_recompute_violations} "
        f"recompute_required={recompute_required} "
        f"recompute_predicates_lower_bound={recompute_ops} "
        f"source_edit_ready={source_edit_ready} "
        f"decision={decision} "
        f"witness={witness}"
    )
    if mismatch:
        print(
            "carry_predictor_witness "
            f"width={mismatch.width} const={mismatch.const} ctrl={mismatch.ctrl} "
            f"cin={mismatch.cin} original={mismatch.original} final={mismatch.final} "
            f"carry={mismatch.carry} predicted={mismatch.predicted}"
        )
    else:
        print(
            "carry_predictor=pass "
            "meaning=boundary-carry-can-be-recomputed-only-if-the-prior-carry-in-is-live-or-certified-recomputed"
        )
    print(
        "required_next=source-hash-bound-recompute-certificate-with-restore-proof-phase-proof-negative-score-edge "
        "no_compute_unlock=yes no_submit_ack=yes"
    )

    if args.require_pass and gate != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
