#!/usr/bin/env python3
"""Gate compute restarts after Storm has closed the compute gate.

This public-safe parser checks redacted compute-unlock packets. It does not run
miners, build/eval, SSH job control, alerts, or submit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)
ROUTE_ID_RE = re.compile(r"\broute_id\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\b(?:owner|agent)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Local full run|Promoted)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|expected_ops_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
VALIDATION_OWNER_RE = re.compile(r"\b(?:validation_owner|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b", re.IGNORECASE)

COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|fire\s+up|spin\s+up|rent)\b.{0,100}\b(?:pods?|runpod|vast|akash|gpus?|cpus?|scanners?|fanout|nonce|search)\b|"
    r"\b(?:gpu_forever(?:\.sh)?|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|lower-q|count_tof)\b|"
    r"\bq1152[-_ ]fanout\b",
    re.IGNORECASE,
)
COMPUTE_CLOSED_RE = re.compile(
    r"\bcompute[_ -]?gate\s*(?:is\s*)?closed\b|"
    r"\bdo\s+not\s+restart\s+(?:fanout|gpu|cpu|pods?|scanners?)\b|"
    r"\bno\s+pod\s+expansion\b",
    re.IGNORECASE,
)
STORM_ACK_RE = re.compile(
    r"\bstorm_route_ack\s*[=:]\s*yes\b|"
    r"\broute_ack\s*[=:]\s*Storm-Codex\b|"
    r"\bStorm[- ]Codex\s+ACK(?:\b|[^\\n]{0,120}\broute\b)",
    re.IGNORECASE,
)
SOURCE_BOUND_RE = re.compile(r"\b(?:source-hash-bound|source_hash\s*[=:]|source-bound)\b", re.IGNORECASE)
VALUE_EXACT_RE = re.compile(r"\b(?:value[-_ ]?exact|value_exact_status)\b", re.IGNORECASE)
CERTIFIED_RE = re.compile(
    r"\b(?:value_exact_status|support_status|proof_status|source_support)\s*[=:]\s*CERTIFIED\b|"
    r"\bCERTIFIED\s+value[-_ ]?exact\b",
    re.IGNORECASE,
)
EXACT_DIFF_RE = re.compile(r"\b(?:exact_diff|diff_hash|patch_hash|changed_files|candidate_diff)\s*[=:]\s*\S+", re.IGNORECASE)
ALLOCATOR_RE = re.compile(r"\b(?:allocator_order|allocator_order_hash|allocator_unchanged|alloc_order)\s*[=:]\s*\S+", re.IGNORECASE)
BUDGET_RE = re.compile(r"\b(?:budget|max_budget|compute_budget|max_nonce|max_range|max_minutes|max_dollars|max_shots)\s*[=:]\s*\S+", re.IGNORECASE)
STOP_RE = re.compile(r"\b(?:stop_condition|kill_condition|kill_gate|stop_after|abort_if)\s*[=:]\s*\S+", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\b(?:studio|runpod:|vast:|owned pod|owned-pod)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
DIRTY_RE = re.compile(
    r"\b(?:dirty|rc\s*[=:]\s*1|classical|phase|ancilla)\b|"
    r"\bc\s*[=:]\s*[1-9][0-9]*\b|\bp\s*[=:]\s*[1-9][0-9]*\b|\ba\s*[=:]\s*[1-9][0-9]*\b",
    re.IGNORECASE,
)
PREFILTER_RE = re.compile(r"\bevidence_label\s*[=:]\s*Prefilter\b|\bPrefilter/dirty\b|\bprefilter survivor\b", re.IGNORECASE)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)


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
    return float(value.replace("_", ""))


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value.replace("_", ""))


def inspect(text: str, expected_source: str, expected_qubits: int, gate_closed: bool) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    qubits = first_int(QUBITS_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)
    validation_owner = first_match(VALIDATION_OWNER_RE, text)
    delta = first_float(DELTA_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)

    has_compute_request = bool(COMPUTE_REQUEST_RE.search(text))
    has_compute_closed = gate_closed or bool(COMPUTE_CLOSED_RE.search(text))
    has_storm_ack = bool(STORM_ACK_RE.search(text))
    has_source_hash = bool(SOURCE_HASH_RE.search(text))
    has_source_bound = bool(has_source_hash and SOURCE_BOUND_RE.search(text))
    has_value_exact = bool(VALUE_EXACT_RE.search(text))
    has_certified = bool(CERTIFIED_RE.search(text))
    has_exact_diff = bool(EXACT_DIFF_RE.search(text))
    has_allocator = bool(ALLOCATOR_RE.search(text))
    has_budget = bool(BUDGET_RE.search(text))
    has_stop = bool(STOP_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    has_local = bool(LOCAL_RE.search(text))
    has_dirty = bool(DIRTY_RE.search(text))
    has_prefilter = bool(PREFILTER_RE.search(text))
    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_premature = bool(PREMATURE_RE.search(text))
    has_negative_edge = (delta is not None and delta < 0) or (score_edge is not None and score_edge > 0)

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if has_local:
        failures.append("local_heavy_context")
    if has_dirty:
        failures.append("dirty_or_failed_validation_evidence")
    if has_prefilter:
        failures.append("prefilter_is_not_compute_unlock")
    if has_premature:
        failures.append("premature_submit_or_akash_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("compute_unlock_overclaims_result")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if has_compute_closed and has_compute_request:
        required = {
            "storm_route_ack": has_storm_ack,
            "source_hash_bound": has_source_bound,
            "value_exact": has_value_exact,
            "certified": has_certified,
            "exact_diff": has_exact_diff,
            "negative_score_edge": has_negative_edge,
            "allocator_order": has_allocator,
            "validation_owner": bool(validation_owner),
            "budget": has_budget,
            "stop_condition": has_stop,
        }
        missing_unlock = [name for name, ok in required.items() if not ok]
        if missing_unlock:
            failures.append("compute_closed_without_unlock_packet")
            failures.extend(f"missing_{name}" for name in missing_unlock)

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
    if not has_compute_request:
        holds.append("missing_compute_request")
    if not has_remote:
        holds.append("missing_remote_or_studio_route")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() != "partial":
        holds.append("evidence_label_not_partial_source_proof")
    if not has_storm_ack:
        holds.append("missing_storm_route_ack")
    if not has_source_bound:
        holds.append("missing_source_hash_bound_packet")
    if not has_value_exact:
        holds.append("missing_value_exact_packet")
    if not has_certified:
        holds.append("missing_certified_proof_status")
    if not has_exact_diff:
        holds.append("missing_exact_diff")
    if not has_negative_edge:
        holds.append("missing_negative_expected_edge")
    if not has_allocator:
        holds.append("missing_allocator_order")
    if not validation_owner:
        holds.append("missing_validation_owner")
    if not has_budget:
        holds.append("missing_budget")
    if not has_stop:
        holds.append("missing_stop_condition")
    if not has_compute_closed:
        warnings.append("compute_gate_not_declared_closed")

    if failures:
        gate = "fail"
        decision = "do-not-restart-compute"
    elif holds:
        gate = "hold"
        decision = "complete-compute-unlock-packet"
    else:
        gate = "pass"
        decision = "compute-unlock-ready-for-storm-dispatch-no-submit"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "frontier_score": frontier_score,
        "qubits": qubits,
        "expected_qubits": expected_qubits,
        "evidence_label": evidence_label,
        "validation_owner": validation_owner,
        "delta": delta,
        "score_edge": score_edge,
        "compute_gate_closed": has_compute_closed,
        "compute_request": has_compute_request,
        "storm_route_ack": has_storm_ack,
        "source_hash_bound": has_source_bound,
        "value_exact": has_value_exact,
        "certified": has_certified,
        "exact_diff": has_exact_diff,
        "negative_edge": has_negative_edge,
        "allocator_order": has_allocator,
        "budget": has_budget,
        "stop_condition": has_stop,
        "remote_host": has_remote,
        "local_host": has_local,
        "dirty_evidence": has_dirty,
        "prefilter": has_prefilter,
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
        f"compute_unlock_gate={row['gate']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"next={row['next_action'] or 'missing'} source_base={row['source_base'] or 'missing'} "
        f"expected_source={row['expected_source'] or 'none'} frontier_score={row['frontier_score']} "
        f"qubits={row['qubits']} expected_qubits={row['expected_qubits']} "
        f"evidence_label={row['evidence_label'] or 'missing'} validation_owner={row['validation_owner'] or 'missing'} "
        f"delta={row['delta']} score_edge={row['score_edge']} "
        f"compute_gate_closed={str(row['compute_gate_closed']).lower()} compute_request={str(row['compute_request']).lower()} "
        f"storm_route_ack={str(row['storm_route_ack']).lower()} source_hash_bound={str(row['source_hash_bound']).lower()} "
        f"value_exact={str(row['value_exact']).lower()} certified={str(row['certified']).lower()} "
        f"exact_diff={str(row['exact_diff']).lower()} negative_edge={str(row['negative_edge']).lower()} "
        f"allocator_order={str(row['allocator_order']).lower()} budget={str(row['budget']).lower()} "
        f"stop_condition={str(row['stop_condition']).lower()} remote_host={str(row['remote_host']).lower()} "
        f"dirty_evidence={str(row['dirty_evidence']).lower()} prefilter={str(row['prefilter']).lower()} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} decision={row['decision']} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--gate-open", action="store_true", help="do not assume the compute gate is closed")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        print(f"compute_unlock_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs), args.expected_source, args.expected_qubits, not args.gate_open)
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
