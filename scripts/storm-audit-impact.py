#!/usr/bin/env python3
"""Emit machine-readable exact-miner audit-impact metrics."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize exact-miner support/rank/ledger outputs as JSON."
    )
    parser.add_argument("--label", required=True, help="snapshot label")
    parser.add_argument("--frontier", default="", help="frontier label, e.g. score/commit")
    parser.add_argument("--supported", required=True, help="support-check JSONL")
    parser.add_argument("--ranked", required=True, help="ranked proof-packet JSONL")
    parser.add_argument("--nack-ledger", default="", help="optional NACK ledger JSONL")
    return parser.parse_args()


def load_jsonl(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"input_not_found path={path}")
    rows: list[dict[str, Any]] = []
    for line in p.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def weight(rows: list[dict[str, Any]], status: str) -> float:
    total = 0.0
    for row in rows:
        if row.get("proof_status") != status:
            continue
        total += abs(float(row.get("expected_avgT_delta") or 0.0))
    return total


def unknown_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if row.get("proof_status") != "UNKNOWN":
            continue
        out.append(
            {
                "site_rank": row.get("site_rank", ""),
                "source_location": row.get("source_location", ""),
                "op_class": row.get("op_class", ""),
                "expected_avgT_delta": float(row.get("expected_avgT_delta") or 0.0),
                "route_id": row.get("route_id", ""),
            }
        )
    return out


def main() -> None:
    args = parse_args()
    supported = load_jsonl(args.supported)
    ranked = load_jsonl(args.ranked)
    ledger_rows = load_jsonl(args.nack_ledger) if args.nack_ledger else []
    support_counts = collections.Counter(row.get("support_status", "") for row in supported)
    ranked_counts = collections.Counter(row.get("proof_status", "") for row in ranked)
    result = {
        "schema_version": 1,
        "label": args.label,
        "frontier": args.frontier,
        "inputs": {
            "supported": args.supported,
            "ranked": args.ranked,
            "nack_ledger": args.nack_ledger,
        },
        "support": {
            "total": len(supported),
            "certified": support_counts.get("CERTIFIED", 0),
            "unknown": support_counts.get("UNKNOWN", 0),
            "counterexample": support_counts.get("COUNTEREXAMPLE", 0),
        },
        "ranked": {
            "total": len(ranked),
            "unknown": ranked_counts.get("UNKNOWN", 0),
            "counterexample": ranked_counts.get("COUNTEREXAMPLE", 0),
            "unknown_weight_abs_avgT_delta": weight(ranked, "UNKNOWN"),
            "counterexample_weight_abs_avgT_delta": weight(ranked, "COUNTEREXAMPLE"),
            "unknown_rows": unknown_rows(ranked),
        },
        "nack_ledger_rows": len(ledger_rows),
        "candidate_gate": {
            "certified_rows": support_counts.get("CERTIFIED", 0),
            "ready_to_submit": False,
            "compute_dispatch_allowed": False,
            "reason": "no CERTIFIED value-exact skip and no trusted full 0/0/0 validation",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
