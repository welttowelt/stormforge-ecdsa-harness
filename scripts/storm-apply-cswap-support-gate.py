#!/usr/bin/env python3
"""Gate apply-cswap support packets before cswap delete work.

This is a public-safe parser for redacted proof packets. It does not run
build_circuit, eval_circuit, nonce search, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


APPLY_CSWAP_RE = re.compile(r"\b(?:apply[_ -]?cswap|apply[_ -]?step.*cswap|cswap.*apply)\b", re.IGNORECASE)
NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-f]{8,64})\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|file|site)\s*[=:]\s*[^\s]*gcd\.rs:[0-9]+\b", re.IGNORECASE)
STEP_RE = re.compile(r"\b(?:step|call|trace_context_call|apply_step)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
BIT_RE = re.compile(r"\b(?:bit|j|trace_context_bit|limb)\s*[=:]\s*([0-9]+)\b", re.IGNORECASE)
SUPPORT_CERT_RE = re.compile(r"\bsupport_(?:status|proof)\s*[=:]\s*CERTIFIED\b|\bproof_status\s*[=:]\s*CERTIFIED\b", re.IGNORECASE)
SUPPORT_UNKNOWN_RE = re.compile(r"\bsupport_(?:status|proof)\s*[=:]\s*UNKNOWN\b|\bproof_status\s*[=:]\s*UNKNOWN\b", re.IGNORECASE)
SUPPORT_COUNTER_RE = re.compile(r"\bsupport_(?:status|proof)\s*[=:]\s*COUNTEREXAMPLE\b|\bproof_status\s*[=:]\s*COUNTEREXAMPLE\b", re.IGNORECASE)
CERTIFICATE_RE = re.compile(r"\b(?:support_certificate|certificate|proof_method|proof)\s*[=:]\s*\S+", re.IGNORECASE)
SOURCE_BOUND_TEXT_RE = re.compile(r"\b(?:source-hash-bound|source_hash\s*[=:]|source-bound)\b", re.IGNORECASE)
SWP_ZERO_RE = re.compile(r"\b(?:swp|swap_flag|swap flag)\s*(?:==|=|is)\s*0\b|\bswp_zero\b", re.IGNORECASE)
XEQY_RE = re.compile(r"\b(?:x\s*==\s*y|x_eq_y|xeqy|x_reg\[[^\]]+\]\s*==\s*y_reg\[[^\]]+\]|operands_equal|equal operands)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|expected_ops_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
VALIDATION_RE = re.compile(r"\b(?:validation_target|candidate-validation-packet|trusted full|official|0/0/0|residual validation)\b", re.IGNORECASE)
BROAD_RE = re.compile(r"\b(?:blanket|global|all\s+(?:apply\s+)?cswaps?|all\s+bits|whole\s+(?:apply|block)|delete\s+all|final\s+block)\b", re.IGNORECASE)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    match = pattern.search(text)
    if not match:
        return None
    return int(match.group(1))


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    match = pattern.search(text)
    if not match:
        return None
    return float(match.group(1))


def inspect(text: str, expected_source: str) -> dict[str, object]:
    step = first_int(STEP_RE, text)
    bit = first_int(BIT_RE, text)
    delta = first_float(DELTA_RE, text)
    source_base_match = SOURCE_BASE_RE.search(text)
    source_base = source_base_match.group(1) if source_base_match else ""
    invariant_types = []
    if SWP_ZERO_RE.search(text):
        invariant_types.append("swp_zero")
    if XEQY_RE.search(text):
        invariant_types.append("x_eq_y")

    has_apply_cswap = bool(APPLY_CSWAP_RE.search(text))
    has_source_hash = bool(SOURCE_HASH_RE.search(text))
    has_source_location = bool(SOURCE_LOCATION_RE.search(text))
    has_exact_scope = step is not None and bit is not None
    has_support_certified = bool(SUPPORT_CERT_RE.search(text))
    has_support_unknown = bool(SUPPORT_UNKNOWN_RE.search(text))
    has_support_counter = bool(SUPPORT_COUNTER_RE.search(text))
    has_certificate = bool(CERTIFICATE_RE.search(text))
    has_source_bound = bool(has_source_hash and SOURCE_BOUND_TEXT_RE.search(text))
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_validation = bool(VALIDATION_RE.search(text))
    has_broad_scope = bool(BROAD_RE.search(text))
    has_premature_language = bool(PREMATURE_RE.search(text))
    has_local_host = bool(LOCAL_RE.search(text))
    has_remote_host = bool(REMOTE_RE.search(text))
    has_negative_delta = delta is not None and delta < 0

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_broad_scope:
        failures.append("broad_cswap_delete_scope")
    if has_premature_language:
        failures.append("premature_submit_or_akash_language")
    if has_local_host:
        failures.append("local_heavy_validation_context")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if has_support_counter:
        failures.append("support_counterexample")

    if not has_apply_cswap:
        holds.append("missing_apply_cswap_route")
    if not has_source_location:
        holds.append("missing_gcd_source_location")
    if not source_base:
        holds.append("missing_source_base")
    elif expected_source and source_base != expected_source:
        warnings.append("source_base_not_expected_frontier")
    if not has_source_hash:
        holds.append("missing_source_hash")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_certificate")
    if not has_exact_scope:
        holds.append("missing_per_step_per_bit_scope")
    if not invariant_types:
        holds.append("missing_swp_zero_or_xeqy_invariant")
    if has_support_unknown:
        holds.append("support_unknown")
    elif not has_support_certified:
        holds.append("missing_support_certified")
    if not has_certificate:
        holds.append("missing_support_certificate")
    if not has_validation:
        holds.append("missing_validation_boundary")
    if delta is None:
        warnings.append("missing_expected_delta")
    elif not has_negative_delta:
        failures.append("nonnegative_expected_delta")
    if not has_remote_host:
        warnings.append("missing_remote_or_owner_route")

    if failures:
        gate = "fail"
        decision = "do-not-delete-apply-cswap"
    elif holds:
        gate = "hold"
        decision = "complete-per-step-per-bit-proof"
    else:
        gate = "pass"
        decision = "ready-for-source-proof-review-no-submit"

    return {
        "gate": gate,
        "decision": decision,
        "source_base": source_base,
        "expected_source": expected_source,
        "step": step,
        "bit": bit,
        "delta": delta,
        "invariant_types": invariant_types,
        "apply_cswap": has_apply_cswap,
        "source_hash": has_source_hash,
        "source_location": has_source_location,
        "source_bound": has_source_bound,
        "exact_scope": has_exact_scope,
        "support_certified": has_support_certified,
        "support_unknown": has_support_unknown,
        "support_counterexample": has_support_counter,
        "certificate": has_certificate,
        "no_submit_ack": has_no_submit,
        "validation_boundary": has_validation,
        "broad_scope": has_broad_scope,
        "premature_language": has_premature_language,
        "remote_host": has_remote_host,
        "local_host": has_local_host,
        "failures": failures,
        "holds": holds,
        "warnings": warnings,
    }


def join(values: object) -> str:
    if not values:
        return "none"
    if isinstance(values, list):
        return ",".join(str(value) for value in values) if values else "none"
    return str(values)


def text_summary(row: dict[str, object]) -> str:
    return (
        f"apply_cswap_support_gate={row['gate']} "
        f"apply_cswap={str(row['apply_cswap']).lower()} exact_scope={str(row['exact_scope']).lower()} "
        f"step={row['step']} bit={row['bit']} invariants={join(row['invariant_types'])} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"source_hash={str(row['source_hash']).lower()} source_location={str(row['source_location']).lower()} "
        f"source_bound={str(row['source_bound']).lower()} support_certified={str(row['support_certified']).lower()} "
        f"certificate={str(row['certificate']).lower()} validation_boundary={str(row['validation_boundary']).lower()} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} remote_host={str(row['remote_host']).lower()} "
        f"delta={row['delta']} decision={row['decision']} failures={join(row['failures'])} "
        f"holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"apply_cswap_support_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), args.expected_source)
    if args.json:
        print(json.dumps(row, sort_keys=True))
    else:
        print(text_summary(row))

    if row["gate"] == "fail":
        return 1
    if args.require_pass and row["gate"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
