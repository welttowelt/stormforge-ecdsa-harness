#!/usr/bin/env python3
"""Gate CPU/GPU pod jobs before dispatch.

The script deliberately has no SSH, cloud, mailbox, alert, or submit code. It
answers one question: does this route packet meet the minimum public Storm gate
for a pod to spend compute?
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_JOB_CLASSES = {"canary", "certified_count", "trusted_eval"}
EVIDENCE_LABELS = {"Prefilter", "Partial", "Local full run", "Promoted"}
PROOF_STATUSES = {"CERTIFIED", "UNKNOWN", "COUNTEREXAMPLE", "UNPROVEN", "N/A"}


def load_job(args: argparse.Namespace) -> dict[str, Any]:
    job: dict[str, Any] = {}
    if args.job_json:
        job.update(json.loads(args.job_json.read_text(encoding="utf-8")))
    for item in args.field:
        if "=" not in item:
            raise SystemExit(f"bad --field {item!r}; expected key=value")
        key, value = item.split("=", 1)
        job[key] = value
    for name in [
        "job_class",
        "evidence_label",
        "proof_status",
        "frontier",
        "owner",
        "validator",
        "stop_condition",
    ]:
        value = getattr(args, name)
        if value:
            job[name] = value
    if args.canary_ok:
        job["canary_ok"] = True
    if args.count_edge_ok:
        job["count_edge_ok"] = True
    if args.clean_candidate:
        job["clean_candidate"] = True
    return job


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "ok", "pass"}


def deny(reason: str) -> tuple[bool, str]:
    return False, reason


def allow(reason: str) -> tuple[bool, str]:
    return True, reason


def evaluate(job: dict[str, Any]) -> tuple[bool, str]:
    job_class = str(job.get("job_class", ""))
    evidence = str(job.get("evidence_label", ""))
    proof = str(job.get("proof_status", ""))
    if job_class not in ALLOWED_JOB_CLASSES:
        return deny("job_class_not_pod_admissible")
    if evidence not in EVIDENCE_LABELS:
        return deny("bad_or_missing_evidence_label")
    if proof not in PROOF_STATUSES:
        return deny("bad_or_missing_proof_status")
    for required in ["frontier", "owner", "validator", "stop_condition"]:
        if not str(job.get(required, "")).strip():
            return deny(f"missing_{required}")
    if job_class == "canary":
        return allow("canary_route_packet_present")
    if proof != "CERTIFIED":
        return deny("proof_not_certified")
    if not as_bool(job.get("canary_ok")):
        return deny("canary_not_confirmed")
    if job_class == "certified_count":
        return allow("certified_count_allowed")
    if job_class == "trusted_eval":
        if not as_bool(job.get("count_edge_ok")):
            return deny("count_edge_not_confirmed")
        if not as_bool(job.get("clean_candidate")):
            return deny("clean_candidate_not_marked")
        return allow("trusted_eval_allowed")
    return deny("unhandled_job_class")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-json", type=Path)
    parser.add_argument("--field", action="append", default=[], help="extra job key=value field")
    parser.add_argument("--job-class", choices=sorted(ALLOWED_JOB_CLASSES))
    parser.add_argument("--evidence-label", choices=sorted(EVIDENCE_LABELS))
    parser.add_argument("--proof-status", choices=sorted(PROOF_STATUSES))
    parser.add_argument("--frontier")
    parser.add_argument("--owner")
    parser.add_argument("--validator")
    parser.add_argument("--stop-condition")
    parser.add_argument("--canary-ok", action="store_true")
    parser.add_argument("--count-edge-ok", action="store_true")
    parser.add_argument("--clean-candidate", action="store_true")
    args = parser.parse_args()

    job = load_job(args)
    ok, reason = evaluate(job)
    print(f"admission={'allow' if ok else 'deny'} reason={reason} job_class={job.get('job_class', '')}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
