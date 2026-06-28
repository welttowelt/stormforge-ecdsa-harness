#!/usr/bin/env python3
"""Gate recompute/pebbling theorem packets before route work or compute.

This public-safe parser checks redacted reversible-pebbling packets. It does
not run miners, build/eval, SSH job control, pods, alerts, or submit.
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
CANDIDATE_HASH_RE = re.compile(r"\b(?:candidate_index_hash|candidate_diff_hash|candidate_hash|diff_hash|index_hash)\s*[=:]\s*([0-9a-fA-F][0-9a-fA-F_.:-]{7,63})\b", re.IGNORECASE)
SOURCE_LOCATION_RE = re.compile(r"\b(?:source_location|source_file|site|file)\s*[=:]\s*((?:src/point_add)/[A-Za-z0-9_./+-]+\.rs(?::[0-9]+)?)\b", re.IGNORECASE)
SOURCE_BOUND_RE = re.compile(r"\b(?:source_bound|source-backed|source_backed|source-hash-bound)\s*[=:]\s*(yes|true|1)\b|\bsource_hash\s*[=:]", re.IGNORECASE)
FRONTIER_SCORE_RE = re.compile(r"\bfrontier(?:_score| score)?\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CURRENT_Q_RE = re.compile(r"\b(?:current_q|current_qubits)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
TARGET_Q_RE = re.compile(r"\b(?:target_q|target_qubits|q)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
CURRENT_AVG_RE = re.compile(r"\b(?:current_avg_tof|current_avgT|baseline_avg_tof)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
EXTRA_AVG_RE = re.compile(r"\b(?:extra_avg_tof|predicted_extra_avgT|extra_avgT|recompute_extra_avg_tof)\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_AVG_RE = re.compile(r"\b(?:candidate_avg_tof|predicted_avg_tof|candidate_avgT)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
CANDIDATE_SCORE_RE = re.compile(r"\b(?:candidate_score|predicted_score)\s*[=:]\s*([0-9][0-9_]*(?:\.[0-9]+)?)\b", re.IGNORECASE)
SCORE_EDGE_RE = re.compile(r"\bscore_edge\s*[=:]\s*(-?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)
PEAK_ROWS_RE = re.compile(r"\b(?:peak_rows|peak_calls|peak_binders)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
OVERLAP_ROWS_RE = re.compile(r"\b(?:overlap_rows|affected_rows|recompute_rows|peak_overlap_rows)\s*[=:]\s*([0-9][0-9_]*)\b", re.IGNORECASE)
REQUIRED_CALLS_RE = re.compile(r"\brequired_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
COVERED_CALLS_RE = re.compile(r"\bcovered_calls\s*[=:]\s*([0-9_,+-]+)\b", re.IGNORECASE)
NODE_RE = re.compile(r"\b(?:node|peak_node|dag_node)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
REMOVED_VALUE_RE = re.compile(r"\b(?:removed_value|delayed_value|recomputed_value)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
PRODUCER_RE = re.compile(r"\bproducer\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
CONSUMERS_RE = re.compile(r"\bconsumers?\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
MOVE_RE = re.compile(r"\b(?:move|pebbling_move)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
RECOMPUTE_PATH_RE = re.compile(r"\b(?:recompute_path|restore_path|inverse_path|replay_path)\s*[=:]\s*([A-Za-z0-9_.:/@,+-]+)\b", re.IGNORECASE)
DROP_STATE_RE = re.compile(r"\b(?:drop_state|dead_drop_state|stale_drop_state)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE)
PROOF_FIELD_RE = {
    "restore": re.compile(r"\b(?:restore_proof|restore_obligation)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE),
    "phase": re.compile(r"\bphase_(?:proof|obligation)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE),
    "ancilla": re.compile(r"\bancilla_(?:proof|obligation)\s*[=:]\s*([A-Za-z0-9_.:+-]+)\b", re.IGNORECASE),
}
SUPPORT_STATUS_RE = re.compile(r"\bsupport_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
PROOF_STATUS_RE = re.compile(r"\bproof_status\s*[=:]\s*(CERTIFIED|UNKNOWN|COUNTEREXAMPLE|UNPROVEN)\b", re.IGNORECASE)
EVIDENCE_LABEL_RE = re.compile(r"\bevidence_label\s*[=:]\s*(Prefilter|Partial|Paper score|Historical clue|Local full run|Promoted)\b", re.IGNORECASE)
DIRTY_RE = re.compile(
    r"\b(?:dirty|rc\s*[=:]\s*1)\b|"
    r"\bdirty_(?:classical|phase(?:_shots)?|ancilla|any_fail)\s*[=:]\s*[1-9][0-9]*\b|"
    r"\bc\s*[=:]\s*[1-9][0-9]*\b|\bp\s*[=:]\s*[1-9][0-9]*\b|\ba\s*[=:]\s*[1-9][0-9]*\b",
    re.IGNORECASE,
)
COMPUTE_REQUEST_RE = re.compile(
    r"\b(?:launch|start|restart|rearm|scale|dispatch|residual|benchmark|run|route_compare)\b.{0,100}\b(?:pods?|runpod|vast|gpus?|cpus?|scanner|residual|9024|benchmark|eval)\b|"
    r"\b(?:gpu_forever|gpu_island2|fanout_nonce_eval|build_circuit|eval_circuit|count_tof|drop_effect_probe|storm-exact-miner)\b",
    re.IGNORECASE,
)
PREMATURE_RE = re.compile(r"\b(?:FOR[- ]AKASH|WINNER|mobile alert|submit(?:ted)?|ready[- ]to[- ]submit|Akash-ready)\b", re.IGNORECASE)
LOCAL_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:mac|macbook|local|darwin)\b|\b(?:MacBook|mac-local|/Users/[A-Za-z0-9_.-]+)\b", re.IGNORECASE)
REMOTE_RE = re.compile(r"\b(?:host|machine)\s*[=:]\s*(?:studio|runpod|vast|pod|remote)\b|\bstudio\b", re.IGNORECASE)
NEGATED_GUARDRAIL_RE = re.compile(
    r"\b(?:no|never)\s+(?:compute|pods?|residual|route[-_ ]?compare|benchmark|alert|winner|akash|submit|submission)\b|"
    r"\b(?:do not|must not|cannot|can not)\s+(?:launch|start|restart|rearm|scale|dispatch|run|trigger|alert|write|submit)\b|"
    r"\b(?:does not|do not)\s+(?:authorize|license)\b|"
    r"\bnot\s+(?:authorized|licensed|allowed|a submit|a submission|ready[- ]to[- ]submit)\b|"
    r"\bwithout\s+storm[-_ ]?(?:compute[-_ ]?)?unlock\b",
    re.IGNORECASE,
)


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


def meaningful(value: str) -> bool:
    return value.lower() not in {"unknown", "none", "missing", "tbd", "todo", "n/a", "na", "null"}


def certified(value: str) -> bool:
    return value.lower() in {"certified", "yes", "true", "1", "clean"}


def parse_call_set(text: str) -> set[str]:
    return {part.strip() for part in text.replace("_", "").split(",") if part.strip()}


def risk_scan_text(text: str) -> str:
    kept: list[str] = []
    skip_continuation = False
    for line in text.splitlines():
        stripped = line.strip()
        if skip_continuation:
            if not stripped or re.search(r"[.!?]\s*$", stripped):
                skip_continuation = False
            continue
        if NEGATED_GUARDRAIL_RE.search(line):
            if stripped and not re.search(r"[.!?]\s*$", stripped):
                skip_continuation = True
            continue
        kept.append(line)
    return "\n".join(kept)


def inspect(text: str, expected_source: str) -> dict[str, object]:
    risk_text = risk_scan_text(text)
    route_id = first_match(ROUTE_ID_RE, text)
    owner = first_match(OWNER_RE, text)
    next_action = first_match(NEXT_RE, text)
    source_base = first_match(SOURCE_BASE_RE, text)
    source_hash = first_match(SOURCE_HASH_RE, text)
    candidate_hash = first_match(CANDIDATE_HASH_RE, text)
    source_location = first_match(SOURCE_LOCATION_RE, text)
    frontier_score = first_float(FRONTIER_SCORE_RE, text)
    current_q = first_int(CURRENT_Q_RE, text)
    target_q = first_int(TARGET_Q_RE, text)
    current_avg = first_float(CURRENT_AVG_RE, text)
    extra_avg = first_float(EXTRA_AVG_RE, text)
    candidate_avg = first_float(CANDIDATE_AVG_RE, text)
    candidate_score = first_float(CANDIDATE_SCORE_RE, text)
    score_edge = first_float(SCORE_EDGE_RE, text)
    peak_rows = first_int(PEAK_ROWS_RE, text)
    overlap_rows = first_int(OVERLAP_ROWS_RE, text)
    required_calls = parse_call_set(first_match(REQUIRED_CALLS_RE, text))
    covered_calls = parse_call_set(first_match(COVERED_CALLS_RE, text))
    node = first_match(NODE_RE, text)
    removed_value = first_match(REMOVED_VALUE_RE, text)
    producer = first_match(PRODUCER_RE, text)
    consumers = first_match(CONSUMERS_RE, text)
    move = first_match(MOVE_RE, text)
    recompute_path = first_match(RECOMPUTE_PATH_RE, text)
    drop_state = first_match(DROP_STATE_RE, text)
    restore_proof = first_match(PROOF_FIELD_RE["restore"], text)
    phase_proof = first_match(PROOF_FIELD_RE["phase"], text)
    ancilla_proof = first_match(PROOF_FIELD_RE["ancilla"], text)
    support_status = first_match(SUPPORT_STATUS_RE, text).upper()
    proof_status = first_match(PROOF_STATUS_RE, text).upper()
    evidence_label = first_match(EVIDENCE_LABEL_RE, text)

    if candidate_avg is None and current_avg is not None and extra_avg is not None:
        candidate_avg = current_avg + extra_avg
    computed_score = None
    if candidate_avg is not None and target_q is not None:
        computed_score = candidate_avg * target_q
    if candidate_score is None and candidate_avg is not None and target_q is not None:
        candidate_score = computed_score
    computed_edge = None
    if frontier_score is not None and candidate_score is not None:
        computed_edge = frontier_score - candidate_score
    if score_edge is None and frontier_score is not None and candidate_score is not None:
        score_edge = computed_edge

    missing_calls = sorted(required_calls - covered_calls)
    has_source_bound = bool(source_hash and SOURCE_BOUND_RE.search(text))
    support_certified = support_status == "CERTIFIED" and proof_status == "CERTIFIED"
    support_counter = support_status == "COUNTEREXAMPLE" or proof_status == "COUNTEREXAMPLE"
    support_unknown = support_status in {"UNKNOWN", "UNPROVEN", ""} or proof_status in {"UNKNOWN", "UNPROVEN", ""}
    score_edge_ok = score_edge is not None and score_edge > 0
    move_lower = move.lower()
    drop_state_lower = drop_state.lower()

    failures: list[str] = []
    holds: list[str] = []
    warnings: list[str] = []

    if LOCAL_RE.search(text):
        failures.append("local_heavy_context")
    if DIRTY_RE.search(text):
        failures.append("dirty_bounded_probe")
    if COMPUTE_REQUEST_RE.search(risk_text):
        failures.append("premature_compute_or_residual_request")
    if PREMATURE_RE.search(risk_text):
        failures.append("premature_submit_or_alert_language")
    if not NO_SUBMIT_RE.search(text):
        failures.append("missing_no_submit_ack")
    if expected_source and source_base and source_base != expected_source:
        failures.append("stale_source_base")
    if support_counter:
        failures.append("support_counterexample")
    if computed_score is not None and candidate_score is not None and abs(candidate_score - computed_score) > 0.5:
        failures.append("candidate_score_mismatch")
    if computed_edge is not None and score_edge is not None and abs(score_edge - computed_edge) > 0.5:
        failures.append("score_edge_mismatch")
    if score_edge is not None and score_edge <= 0:
        failures.append("nonpositive_score_edge")
    if missing_calls:
        failures.append("missing_required_peak_calls")
    if move_lower == "keep-and-park":
        failures.append("park_move_not_route")
    if drop_state_lower in {"historical", "mixed", "stale"}:
        failures.append("stale_drop_state")
    if evidence_label.lower() in {"local full run", "promoted"}:
        failures.append("pebbling_packet_overclaims_result")

    for label, value in [
        ("missing_route_id", route_id),
        ("missing_owner", owner),
        ("missing_next_action", next_action),
        ("missing_source_base", source_base),
        ("missing_source_hash", source_hash),
        ("missing_candidate_hash", candidate_hash),
        ("missing_source_location", source_location),
        ("missing_peak_node", node),
        ("missing_removed_value", removed_value),
        ("missing_producer", producer),
        ("missing_consumers", consumers),
        ("missing_pebbling_move", move),
        ("missing_recompute_path", recompute_path),
        ("missing_drop_state", drop_state),
    ]:
        if not value or not meaningful(value):
            holds.append(label)
    if frontier_score is None:
        holds.append("missing_frontier_score")
    if current_q is None:
        holds.append("missing_current_q")
    if target_q is None:
        holds.append("missing_target_q")
    if current_avg is None:
        holds.append("missing_current_avg_tof")
    if candidate_avg is None and extra_avg is None:
        holds.append("missing_candidate_or_extra_avg_tof")
    if candidate_score is None:
        holds.append("missing_candidate_score")
    if score_edge is None:
        holds.append("missing_score_edge")
    if peak_rows is None:
        holds.append("missing_peak_rows")
    elif peak_rows <= 0:
        failures.append("no_peak_rows")
    if overlap_rows is None:
        holds.append("missing_overlap_rows")
    elif overlap_rows <= 0:
        failures.append("no_overlap_rows")
    if not has_source_bound:
        holds.append("missing_source_bound_context")
    for label, value in [
        ("restore_proof_not_certified", restore_proof),
        ("phase_proof_not_certified", phase_proof),
        ("ancilla_proof_not_certified", ancilla_proof),
    ]:
        if not certified(value):
            holds.append(label)
    if not support_status:
        holds.append("missing_support_status")
    if not proof_status:
        holds.append("missing_proof_status")
    if not support_certified:
        holds.append("missing_exact_support_certified")
    if not evidence_label:
        holds.append("missing_evidence_label")
    elif evidence_label.lower() not in {"prefilter", "partial"}:
        holds.append("evidence_label_not_prefilter_or_partial")
    if support_unknown:
        warnings.append("support_unknown_not_pass_ready")
    if target_q is not None and current_q is not None and target_q >= current_q:
        warnings.append("target_q_not_lower_than_current_q")
    if not REMOTE_RE.search(text):
        warnings.append("missing_remote_or_studio_context")

    if failures:
        gate = "fail"
        decision = "no-pebbling-theorem"
    elif holds:
        gate = "hold"
        decision = "complete-pebbling-theorem-packet"
    else:
        gate = "pass"
        decision = "pebbling-theorem-review-no-compute"

    return {
        "gate": gate,
        "decision": decision,
        "route_id": route_id,
        "owner": owner,
        "source_base": source_base,
        "source_location": source_location,
        "source_hash_bound": has_source_bound,
        "candidate_hash": bool(candidate_hash),
        "frontier_score": frontier_score,
        "current_q": current_q,
        "target_q": target_q,
        "current_avg_tof": current_avg,
        "extra_avg_tof": extra_avg,
        "candidate_avg_tof": candidate_avg,
        "candidate_score": candidate_score,
        "computed_score": computed_score,
        "score_edge": score_edge,
        "computed_edge": computed_edge,
        "score_edge_ok": score_edge_ok,
        "peak_rows": peak_rows,
        "overlap_rows": overlap_rows,
        "required_calls": sorted(required_calls),
        "covered_calls": sorted(covered_calls),
        "missing_calls": missing_calls,
        "peak_node": bool(node and meaningful(node)),
        "removed_value": bool(removed_value and meaningful(removed_value)),
        "producer": bool(producer and meaningful(producer)),
        "consumers": bool(consumers and meaningful(consumers)),
        "pebbling_move": move or "missing",
        "recompute_path": bool(recompute_path and meaningful(recompute_path)),
        "drop_state": drop_state or "missing",
        "restore_proof": certified(restore_proof),
        "phase_proof": certified(phase_proof),
        "ancilla_proof": certified(ancilla_proof),
        "support_status": support_status or "missing",
        "proof_status": proof_status or "missing",
        "evidence_label": evidence_label,
        "no_submit_ack": bool(NO_SUBMIT_RE.search(text)),
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
        f"pebbling_theorem_gate={row['gate']} decision={row['decision']} "
        f"route_id={row['route_id'] or 'missing'} owner={row['owner'] or 'missing'} "
        f"source_base={row['source_base'] or 'missing'} source_location={row['source_location'] or 'missing'} "
        f"source_hash_bound={str(row['source_hash_bound']).lower()} candidate_hash={str(row['candidate_hash']).lower()} "
        f"current_q={row['current_q']} target_q={row['target_q']} current_avg_tof={row['current_avg_tof']} "
        f"extra_avg_tof={row['extra_avg_tof']} candidate_avg_tof={row['candidate_avg_tof']} "
        f"frontier_score={row['frontier_score']} candidate_score={row['candidate_score']} "
        f"computed_score={row['computed_score']} score_edge={row['score_edge']} "
        f"computed_edge={row['computed_edge']} score_edge_ok={str(row['score_edge_ok']).lower()} "
        f"peak_rows={row['peak_rows']} overlap_rows={row['overlap_rows']} "
        f"required_calls={join(row['required_calls'])} covered_calls={join(row['covered_calls'])} "
        f"missing_calls={join(row['missing_calls'])} peak_node={str(row['peak_node']).lower()} "
        f"removed_value={str(row['removed_value']).lower()} producer={str(row['producer']).lower()} "
        f"consumers={str(row['consumers']).lower()} pebbling_move={row['pebbling_move']} "
        f"recompute_path={str(row['recompute_path']).lower()} drop_state={row['drop_state']} "
        f"restore_proof={str(row['restore_proof']).lower()} phase_proof={str(row['phase_proof']).lower()} "
        f"ancilla_proof={str(row['ancilla_proof']).lower()} support_status={row['support_status']} "
        f"proof_status={row['proof_status']} evidence_label={row['evidence_label'] or 'missing'} "
        f"no_submit_ack={str(row['no_submit_ack']).lower()} failures={join(row['failures'])} "
        f"holds={join(row['holds'])} warnings={join(row['warnings'])}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, nargs="+")
    parser.add_argument("--expected-source", default="d44cad3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = [str(path) for path in args.packet if not path.is_file()]
    if missing:
        print(f"pebbling_theorem_gate=fail missing_inputs={','.join(missing)}", file=sys.stderr)
        return 2
    row = inspect(read_text(args.packet), args.expected_source)
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
