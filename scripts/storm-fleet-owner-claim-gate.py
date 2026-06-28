#!/usr/bin/env python3
"""Gate paid fleet ownership claims before a pod survives audit.

This parser is intentionally public-safe: it checks for the presence of owner,
pod identity, route/range, active process/log evidence, next action, and
no_submit_ack=yes without requiring private endpoints or raw credentials.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable


OWNER_RE = re.compile(r"\b(?:from:\s*[A-Za-z0-9_-]+|owner\s*[=:]\s*[A-Za-z0-9_-]+|ACK\s+[A-Za-z0-9_-]+|CLAIM)\b", re.IGNORECASE)
POD_RE = re.compile(r"\b(?:pod(?:_id)?|runpod|vast|instance|name|machine)\s*[=:][^\s,;]+|\b[a-z0-9]{8,}\b", re.IGNORECASE)
ROUTE_RE = re.compile(r"\b(?:route|range|shard|chunk|target|current\s+range)\b\s*[=:]?[^\n]*|\[[0-9_, ]+,[0-9_, ]+\)", re.IGNORECASE)
ACTIVE_RE = re.compile(r"\b(?:active|pid|process|watch|guard|log(?:_path)?|gpu_forever|eval_circuit|build_circuit|fanout_nonce_eval|gpu_island2|safe-eval)\b", re.IGNORECASE)
NEXT_RE = re.compile(r"\bnext\s*=", re.IGNORECASE)
NO_SUBMIT_RE = re.compile(r"\bno_submit_ack\s*=\s*yes\b", re.IGNORECASE)


def read_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)


def inspect(text: str) -> dict[str, object]:
    checks = {
        "owner": bool(OWNER_RE.search(text)),
        "pod_identity": bool(POD_RE.search(text)),
        "route_or_range": bool(ROUTE_RE.search(text)),
        "active_process_or_log": bool(ACTIVE_RE.search(text)),
        "next_action": bool(NEXT_RE.search(text)),
        "no_submit_ack": bool(NO_SUBMIT_RE.search(text)),
    }
    missing = [name for name, ok in checks.items() if not ok]
    gate = "pass" if not missing else "fail"
    decision = "survives-owner-audit" if gate == "pass" else "terminate-or-hold"
    return {
        "gate": gate,
        "decision": decision,
        "missing": missing,
        **checks,
    }


def text_summary(row: dict[str, object]) -> str:
    flags = " ".join(
        f"{key}={str(row[key]).lower()}"
        for key in ["owner", "pod_identity", "route_or_range", "active_process_or_log", "next_action", "no_submit_ack"]
    )
    missing = ",".join(row["missing"]) if row["missing"] else "none"
    return f"fleet_owner_claim_gate={row['gate']} {flags} decision={row['decision']} missing={missing}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    missing_paths = [str(path) for path in args.inputs if not path.is_file()]
    if missing_paths:
        print(f"fleet_owner_claim_gate=fail missing_inputs={','.join(missing_paths)}", file=sys.stderr)
        return 2

    row = inspect(read_text(args.inputs))
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
