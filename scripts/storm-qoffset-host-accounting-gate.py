#!/usr/bin/env python3
"""Gate source-integrated qoffset host-accounting packets.

This public-safe parser checks redacted qoffset packets or counterexample
closures. It does not run miners, build/eval, SSH job control, pods, alerts, or
submit.
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
OWNER_RE = re.compile(r"\b(?:owner|agent|validator)\s*[=:]\s*([A-Za-z0-9_.-]+)\b|\bACK\s+([A-Za-z0-9_.-]+)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*[=:]\s*([A-Za-z0-9_.:/@+-]+)\b", re.IGNORECASE)
SOURCE_BASE_RE = re.compile(r"\b(?:source_base|source|base|source commit)\s*[=:]\s*([0-9a-f]{6,40})\b", re.IGNORECASE)
SOURCE_HASH_RE = re.compile(r"\b(?:source_hash|source-hash|source_snippet_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
CANDIDATE_HASH_RE = re.compile(
    r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b",
    re.IGNORECASE,
)
SOURCE_LOCATION_RE = re.compile(
    r"\b(?:source_location|source_file|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs(?::[0-9]+)?)\b",
    re.IGNORECASE,
)
QUBITS_RE = re.compile(r"\b(?:q|qubits?)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"\b(?:expected_avgT_delta|expected_delta|avgT_delta|delta)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
QOFFSET_RE = re.compile(r"\b(?:qoffset|q_offset|host_qoffset|condition_qoffset)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
HOST_ACCOUNTING_RE = re.compile(r"\b(?:host_accounting|host_accounting_status|accounting)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
SOURCE_INTEGRATED_RE = re.compile(r"\b(?:source_integrated|source-integrated|source_backed|source-bound)\s*[=:]\s*(yes|true|1|source_integrated)\b", re.IGNORECASE)
COUNTED_RE = re.compile(r"\b(?:counted_q1152|counted|counted_delta|counted_expected_delta)\s*[=:]\s*(yes|true|1|q1152|source_integrated)\b", re.IGNORECASE)
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
RESTORE_RE = re.compile(r"\brestore_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
PHASE_RE = re.compile(r"\bphase_proof\s*[=:]\s*([01]|true|false|yes|no)\b", re.IGNORECASE)
CLOSURE_RE = re.compile(r"\b(?:closure_reason|close_reason|counterexample_artifact|counterexample_file|source_row_closed)\s*[=:]\s*\S+", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Counterexample|Local full run|Promoted)\b", re.IGNORECASE)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\bstudio\b", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def first_int(pattern: re.Pattern[str], text: str) -> int | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return int(value.replace("_", ""), 0)


def first_float(pattern: re.Pattern[str], text: str) -> float | None:
    value = first_match(pattern, text)
    if not value:
        return None
    return float(value.replace("_", ""))


def first_bool(pattern: re.Pattern[str], text: str) -> bool | None:
    value = first_match(pattern, text).lower()
    if not value:
        return None
    return value in {"1", "true", "yes"}


def normalized(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def inspect(text: str, expected_source: str, expected_qubits: int) -> dict[str, object]:
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    qubits = first_int(QUBITS_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    delta = first_float(DELTA_RE, text)
    qoffset = first_match(QOFFSET_RE, text)
    host_accounting = normalized(first_match(HOST_ACCOUNTING_RE, text))
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()
    restore_proof = first_bool(RESTORE_RE, text)
    phase_proof = first_bool(PHASE_RE, text)
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)

    has_no_submit = bool(NO_SUBMIT_RE.search(text))
    has_remote = bool(REMOTE_RE.search(text))
    has_source_integrated = bool(SOURCE_INTEGRATED_RE.search(text) or "source_integrated" in host_accounting)
    has_counted = bool(COUNTED_RE.search(text) or "counted" in host_accounting)
    closure = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE" or bool(CLOSURE_RE.search(text))
    certified = support_status == "CERTIFIED" and proof_status == "CERTIFIED"
    unknown = support_status in {"UNKNOWN", "UNPROVEN"} or proof_status in {"UNKNOWN", "UNPROVEN"}

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if LOCAL_RE.search(text):
        failures.append("local_heavy_context")
    if COMPUTE_REQUEST_RE.search(text):
        failures.append("premature_compute_or_residual_request")
    if PREMATURE_RE.search(text):
        failures.append("premature_submit_or_alert_language")
    if not has_no_submit:
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if expected_qubits > 0 and qubits is not None and qubits != expected_qubits:
        failures.append("wrong_qubit_tier")
    if support_status == "COUNTEREXAMPLE" and proof_status == "CERTIFIED":
        failures.append("mixed_support_proof_status")
    if support_status == "CERTIFIED" and proof_status == "COUNTEREXAMPLE":
        failures.append("mixed_support_proof_status")
    if unknown:
        failures.append("proof_unknown_close_as_nack")
    if certified and delta is not None and delta >= 0:
        failures.append("nonnegative_counted_delta")
    if certified and not has_counted:
        failures.append("certified_packet_missing_counted_q1152")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("packet_overclaims_result")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_source_hash", source_hash),
        ("missing_candidate_hash", candidate_hash),
        ("missing_source_location", source_location),
        ("missing_qoffset", qoffset),
    ]:
        if not value:
            holds.append(label)
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if qubits is None:
        holds.append("missing_qubits")
    if not host_accounting:
        holds.append("missing_host_accounting")
    if not has_source_integrated:
        holds.append("missing_source_integrated_host_accounting")
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if restore_proof is not True:
        holds.append("restore_proof_missing")
    if phase_proof is not True:
        holds.append("phase_proof_missing")

    if certified and delta is None:
        holds.append("missing_counted_negative_delta")
    if certified and delta is not None and delta < 0 and not has_counted:
        holds.append("missing_counted_q1152_evidence")
    if closure and not CLOSURE_RE.search(text):
        holds.append("missing_closure_reason_or_artifact")
    if not certified and not closure and not unknown:
        holds.append("missing_certified_or_counterexample_decision")
    if not has_remote:
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "close-qoffset-host-accounting-nack"
    elif holds:
        gate = "hold"
        decision = "complete-source-integrated-qoffset-packet"
    elif closure:
        gate = "pass"
        decision = "qoffset-host-accounting-counterexample-closed-no-compute"
    else:
        gate = "pass"
        decision = "qoffset-host-accounting-certified-no-compute-review"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "next_action": next_action,
        "source_base": source_base,
        "expected_source": expected_source,
        "source_hash_bound": bool(source_hash),
        "candidate_hash_bound": bool(candidate_hash),
        "source_location": source_location,
        "frontier_score": frontier_score,
        "q": qubits,
        "expected_q": expected_qubits,
        "qoffset": qoffset,
        "host_accounting": host_accounting,
        "source_integrated": has_source_integrated,
        "counted_q1152": has_counted,
        "delta": delta,
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "restore_proof": restore_proof,
        "phase_proof": phase_proof,
        "closure": closure,
        "remote_host": has_remote,
        "compute_request": bool(COMPUTE_REQUEST_RE.search(text)),
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
        f"qoffset_host_accounting_gate={row['gate']} decision={row['decision']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} q={row['q']} "
        f"qoffset={row['qoffset'] or 'missing'} host_accounting={row['host_accounting'] or 'missing'} "
        f"source_integrated={str(row['source_integrated']).lower()} counted_q1152={str(row['counted_q1152']).lower()} "
        f"delta={row['delta']} support_status={row['support_status']} proof_status={row['proof_status']} "
        f"restore_proof={row['restore_proof']} phase_proof={row['phase_proof']} "
        f"closure={row['closure']} "
        f"source_hash_bound={str(row['source_hash_bound']).lower()} candidate_hash_bound={str(row['candidate_hash_bound']).lower()} "
        f"remote_host={str(row['remote_host']).lower()} no_submit_ack={str(row['no_submit_ack']).lower()} "
        f"failures={join(row['failures'])} holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, nargs="+")
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--expected-qubits", type=int, default=1152)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in args.packet if not path.is_file()]
    if missing:
        print(f"qoffset_host_accounting_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    row = inspect(read_text(args.packet), args.expected_source, args.expected_qubits)
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
