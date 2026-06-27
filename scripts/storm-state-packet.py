#!/usr/bin/env python3
"""Print a compact Storm control-loop packet from public-safe local files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def sentinel_status(item: str) -> tuple[str, str]:
    if "=" not in item:
        raise SystemExit(f"bad --sentinel {item!r}; expected name=path")
    name, value = item.split("=", 1)
    path = Path(value)
    if not path.exists():
        return name, "missing"
    return name, f"{path.stat().st_size}b"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", required=True)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--backlog", type=Path)
    parser.add_argument("--queue-status", default="unknown")
    parser.add_argument("--sentinel", action="append", default=[])
    parser.add_argument("--local-full-run-clean", action="store_true")
    parser.add_argument("--score-below-frontier", action="store_true")
    args = parser.parse_args()

    claims = read_jsonl(args.claims) if args.claims else []
    backlog = read_jsonl(args.backlog) if args.backlog else []
    open_backlog = [row for row in backlog if row.get("status") in {"OPEN", "CLAIMED"}]
    sentinels = [sentinel_status(item) for item in args.sentinel]
    alert_ok = args.local_full_run_clean and args.score_below_frontier

    print("storm_state_packet=v1")
    print(f"frontier={args.frontier}")
    print(f"claims_total={len(claims)} claims_tail={min(len(claims), 5)}")
    print(f"proof_backlog_total={len(backlog)} proof_backlog_open={len(open_backlog)}")
    print(f"queue_status={args.queue_status}")
    for name, status in sentinels:
        print(f"sentinel_{name}={status}")
    print(f"alert_decision={'ready_candidate' if alert_ok else 'no_candidate'}")
    print("submit_decision=closed")
    for row in open_backlog[:5]:
        print(
            "next_proof "
            f"status={row.get('status')} owner={row.get('owner') or '-'} "
            f"source={row.get('source_location')} route_id={row.get('route_id')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
