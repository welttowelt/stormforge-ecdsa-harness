#!/usr/bin/env python3
"""Gate pair-complete FFG suffix-carry proof packets before compute.

This public-safe parser checks redacted proof packets. It does not run miners,
build/eval, SSH job control, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Iterable


NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
AVG_T_RE = re.compile(r"\b(?:candidate_avgT|candidate_avg_tof|avgT|avg_tof|avg_toffoli)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_SCORE_RE = re.compile(r"\b(?:candidate_score|score)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\b(?:score_edge|route_score_edge)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
REQUIRED_CALLS_RE = re.compile(r"\brequired_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
COVERED_CALLS_RE = re.compile(r"\bcovered_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
PAIR_COMPLETE_RE = re.compile(r"\b(?:pair_complete|pair-complete)\s*[=:]\s*([A-Za-z0-9_.+-]+)\b", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source-hash-bound|source_bound\s*[=:]\s*yes|source_hash\s*[=:]|source-bound)\b", re.IGNORECASE)
FFG_CONTEXT_RE = re.compile(r"\b(?:FFG|TLM_FFG|suffix[-_ ]carry|ffg_prefix_carry|ffg[-_ ]pair)\b", re.IGNORECASE)
ROUTE_ADMISSION_RE = re.compile(r"\broute_compare_admission\s*[=:]\s*(pass|hold|fail)\b", re.IGNORECASE)
ADMITTED_RE = re.compile(r"\badmitted\s*[=:]\s*([01])\b", re.IGNORECASE)
SHOTS_RE = re.compile(r"\bshots\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
MIN_SHOTS_RE = re.compile(r"\bmin_shots\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
PROOF_FIELD_RE = re.compile(
    r"\b(value_proof|value_exact|exact_support|support_status|proof_status|restore_proof|restore|phase_proof|phase_clean)\s*[=:]\s*([A-Za-z0-9_.+-]+)\b",
    re.IGNORECASE,
)
DIRTY_RE = re.compile(
    r"\b(?:dirty|rc\s*[=:]\s*1)\b|"
    r"\bdirty_(?:classical|phase(?:_shots)?|any_fail)\s*[=:]\s*[1-9][0-9]*\b|"
    r"\b(?:classical|phase_batches|ancilla_batches|output_diff|phase_diff_batches)\s*[=:]\s*[1-9][0-9]*\b|"
    r"\bc\s*[=:]\s*[1-9][0-9]*\b|\bp\s*[=:]\s*[1-9][0-9]*\b|\ba\s*[=:]\s*[1-9][0-9]*\b",
    re.IGNORECASE,
)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)

TRUTHY = {"1", "yes", "true", "pass", "clean", "certified", "ok", "value-exact", "exact"}
FALSY = {"0", "no", "false", "fail", "dirty", "counterexample"}
UNKNOWN = {"unknown", "unproven", "missing", "pending", "none", "na", "n/a"}


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    try:
        parsed = float(value.replace("_", ""))
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    try:
        return int(value.replace("_", ""), 0)
    except ValueError:
        return None


def parse_call_set(text: str) -> set[str]:
    return {part.strip() for part in text.replace("_", "").split(",") if part.strip()}


def proof_values(text: str, names: set[str]) -> list[str]:
    values = []
    for match in PROOF_FIELD_RE.finditer(text):
        key = match.group(1).lower()
        if key in names:
            values.append(match.group(2).lower())
    return values


def proof_state(values: list[str]) -> tuple[bool, bool, bool]:
    has_ok = any(value in TRUTHY for value in values)
    has_bad = any(value in FALSY for value in values)
    has_unknown = any(value in UNKNOWN for value in values)
    return has_ok, has_bad, has_unknown


def inspect(text: str, expected_source: str, expected_qubits: int, required_calls_arg: str, min_shots: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    avg_t = first_float(AVG_T_RE, text)
    candidate_score = first_float(CANDIDATE_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    required_calls_packet = parse_call_set(first_match(REQUIRED_CALLS_RE, text))
    covered_calls = parse_call_set(first_match(COVERED_CALLS_RE, text))
    required_calls = parse_call_set(required_calls_arg)
    pair_complete_value = first_match(PAIR_COMPLETE_RE, text).lower()
    route_admission = first_match(ROUTE_ADMISSION_RE, text).lower()
    admitted = first_int(ADMITTED_RE, text)
    shots = first_int(SHOTS_RE, text)
    packet_min_shots = first_int(MIN_SHOTS_RE, text)

    computed_score = None
    if candidate_score is None and avg_t is not None and qubits is not None:
        computed_score = round(avg_t) * qubits
        candidate_score = computed_score
    if score_edge is None and frontier_score is not None and candidate_score is not None:
        score_edge = frontier_score - candidate_score

    value_values = proof_values(text, {"value_proof", "value_exact", "exact_support", "support_status", "proof_status"})
    restore_values = proof_values(text, {"restore_proof", "restore"})
    phase_values = proof_values(text, {"phase_proof", "phase_clean"})
    value_ok, value_bad, value_unknown = proof_state(value_values)
    restore_ok, restore_bad, restore_unknown = proof_state(restore_values)
    phase_ok, phase_bad, phase_unknown = proof_state(phase_values)

    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_source_bound = bool(source_hash and SOURCE_BOUND_RE.search(text))
    has_ffg_context = bool(FFG_CONTEXT_RE.search(text))
    has_dirty = bool(DIRTY_RE.search(text))
    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    pair_complete = pair_complete_value in TRUTHY
    pair_false = pair_complete_value in FALSY
    missing_calls = sorted(required_calls - covered_calls)
    packet_missing_calls = sorted(required_calls - required_calls_packet)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_dirty:
        failures.append("dirty_evidence")
    if value_bad:
        failures.append("value_proof_bad")
    if restore_bad:
        failures.append("restore_proof_bad")
    if phase_bad:
        failures.append("phase_proof_bad")
    if pair_false:
        failures.append("pair_complete_false")
    if missing_calls:
        failures.append("missing_required_ffg_calls")
    if route_admission and route_admission != "pass":
        failures.append("route_compare_not_pass")
    if admitted == 0:
        failures.append("route_compare_not_admitted")
    if shots is not None and shots < min_shots:
        failures.append("route_compare_shots_below_min")
    if packet_min_shots is not None and packet_min_shots < min_shots:
        failures.append("route_compare_min_shots_below_required")
    if score_edge is not None and score_edge <= 0:
        failures.append("score_no_edge")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("ffg_packet_overclaims_result")
    if has_compute_request:
        failures.append("premature_compute_or_residual_request")
    if has_premature:
        failures.append("premature_submit_or_akash_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")

    if not route_id:
        holds.append("missing_route_id")
    if not owner:
        holds.append("missing_owner")
    if not next_action:
        holds.append("missing_next_action")
    if not source_base:
        holds.append("missing_source_base")
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if not source_hash:
        holds.append("missing_source_hash")
    if not candidate_hash:
        holds.append("missing_candidate_hash")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_context")
    if not has_ffg_context:
        holds.append("missing_ffg_suffix_carry_context")
    if not required_calls_packet:
        holds.append("missing_required_calls")
    elif packet_missing_calls:
        holds.append("packet_required_calls_missing_expected")
    if not covered_calls:
        holds.append("missing_covered_calls")
    if not pair_complete_value:
        holds.append("missing_pair_complete_flag")
    if not value_ok:
        holds.append("missing_value_proof_certified")
    if not restore_ok:
        holds.append("missing_restore_proof_certified")
    if not phase_ok:
        holds.append("missing_phase_proof_certified")
    if value_unknown:
        holds.append("value_proof_unknown")
    if restore_unknown:
        holds.append("restore_proof_unknown")
    if phase_unknown:
        holds.append("phase_proof_unknown")
    if not route_admission:
        holds.append("missing_route_compare_admission")
    if admitted is None:
        holds.append("missing_admitted_flag")
    if shots is None:
        holds.append("missing_route_compare_shots")
    if packet_min_shots is None:
        holds.append("missing_route_compare_min_shots")
    if score_edge is None:
        holds.append("missing_score_edge")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial"}:
        holds.append("evidence_label_not_prefilter_or_partial")
    if not has_remote:
        warnings.append("missing_remote_or_studio_route")
    if avg_t is not None and computed_score is not None:
        warnings.append("candidate_score_computed_from_rounded_avgT")

    if failures:
        gate = "fail"
        decision = "do-not-promote-ffg-packet"
    elif holds:
        gate = "hold"
        decision = "complete-ffg-pair-proof-packet"
    else:
        gate = "pass"
        decision = "source-bound-ffg-proof-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_hash_bound": has_source_bound,
        "candidate_hash_bound": bool(candidate_hash),
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "avg_t": avg_t,
        "candidate_score": candidate_score,
        "computed_score": computed_score,
        "score_edge": score_edge,
        "evidence_label": evidence_label,
        "required_calls": sorted(required_calls),
        "packet_required_calls": sorted(required_calls_packet),
        "covered_calls": sorted(covered_calls),
        "missing_calls": missing_calls,
        "pair_complete": pair_complete,
        "ffg_context": has_ffg_context,
        "value_proof": value_ok,
        "restore_proof": restore_ok,
        "phase_proof": phase_ok,
        "route_compare_admission": route_admission,
        "admitted": admitted,
        "shots": shots,
        "min_shots": packet_min_shots,
        "required_min_shots": min_shots,
        "dirty_evidence": has_dirty,
        "remote_host": has_remote,
        "compute_request": has_compute_request,
        "no_submit_ack": has_no_submit,
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
        f"ffg_pair_proof_gate={row['gate']} route_id={row['route_id'] or 'missing'} "
        f"owner={row['owner'] or 'missing'} next={row['next_action'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} expected_source={row['expected_source'] or 'none'} "
        f"source_hash_bound={str(row['source_hash_bound']).lower()} "
        f"candidate_hash_bound={str(row['candidate_hash_bound']).lower()} "
        f"frontier_score={row['frontier_score']} qubits={row['qubits']} "
        f"expected_qubits={row['expected_qubits']} avgT={row['avg_t']} "
        f"candidate_score={row['candidate_score']} score_edge={row['score_edge']} "
        f"evidence_label={row['evidence_label'] or 'missing'} required_calls={join(row['required_calls'])} "
        f"packet_required_calls={join(row['packet_required_calls'])} covered_calls={join(row['covered_calls'])} "
        f"missing_calls={join(row['missing_calls'])} pair_complete={str(row['pair_complete']).lower()} "
        f"ffg_context={str(row['ffg_context']).lower()} value_proof={str(row['value_proof']).lower()} "
        f"restore_proof={str(row['restore_proof']).lower()} phase_proof={str(row['phase_proof']).lower()} "
        f"route_compare_admission={row['route_compare_admission'] or 'missing'} "
        f"admitted={row['admitted']} shots={row['shots']} min_shots={row['min_shots']} "
        f"required_min_shots={row['required_min_shots']} dirty_evidence={str(row['dirty_evidence']).lower()} "
        f"remote_host={str(row['remote_host']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} decision={row['decision']} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--required-calls", default="178,180,181")
    parser.add_argument("--min-shots", type=int, default=9024)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"ffg_pair_proof_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), args.expected_source, args.expected_qubits, args.required_calls, args.min_shots)
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
