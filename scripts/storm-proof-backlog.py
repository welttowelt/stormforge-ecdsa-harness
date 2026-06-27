#!/usr/bin/env python3
"""Manage a JSONL proof backlog generated from exact-miner ranked packets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any


OPEN_STATUSES = {"OPEN", "CLAIMED"}
RESOLVE_STATUSES = {"NACK", "CERTIFIED", "PARKED", "STALE"}


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def parse_time(text: str) -> dt.datetime | None:
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        value = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{lineno}: row must be an object")
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    os.replace(tmp, path)


def cmd_import_ranked(args: argparse.Namespace) -> int:
    ranked = read_jsonl(args.ranked)
    existing = {str(row.get("route_id", "")) for row in read_jsonl(args.out)}
    rows: list[dict[str, Any]] = []
    created = iso(now_utc())
    for packet in ranked:
        if packet.get("proof_status") != "UNKNOWN":
            continue
        route_id = str(packet.get("route_id", ""))
        if not route_id or route_id in existing:
            continue
        rows.append(
            {
                "schema": "storm.proof_backlog.v1",
                "created_at": created,
                "status": "OPEN",
                "owner": "",
                "frontier": packet.get("frontier", args.frontier),
                "route_id": route_id,
                "source_location": packet.get("source_location", ""),
                "expected_avgT_delta": packet.get("expected_avgT_delta", ""),
                "proof_status": "UNKNOWN",
                "evidence_label": packet.get("evidence_label", "Prefilter"),
                "artifact": "",
                "next": "one bounded source proof: certificate or counterexample",
                "expires_at": "",
                "note": "",
            }
        )
        if args.limit and len(rows) >= args.limit:
            break
    combined = read_jsonl(args.out) + rows
    write_jsonl(args.out, combined)
    print(f"proof_backlog_import=pass added={len(rows)} total={len(combined)}")
    return 0


def select_row(rows: list[dict[str, Any]], route_id: str) -> int:
    for index, row in enumerate(rows):
        if route_id and row.get("route_id") == route_id:
            return index
    for index, row in enumerate(rows):
        if row.get("status") == "OPEN":
            return index
    return -1


def cmd_claim(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.queue)
    index = select_row(rows, args.route_id)
    if index < 0:
        print("proof_backlog_claim=none reason=no_open_row")
        return 1
    row = rows[index]
    if row.get("status") not in OPEN_STATUSES:
        print(f"proof_backlog_claim=deny route_id={row.get('route_id')} status={row.get('status')}")
        return 2
    now = now_utc()
    row["status"] = "CLAIMED"
    row["owner"] = args.owner
    row["claimed_at"] = iso(now)
    row["expires_at"] = iso(now + dt.timedelta(minutes=args.ttl_minutes))
    row["next"] = args.next
    write_jsonl(args.queue, rows)
    print(f"proof_backlog_claim=pass route_id={row.get('route_id')} owner={args.owner} expires_at={row['expires_at']}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.queue)
    index = select_row(rows, args.route_id)
    if index < 0 or (args.route_id and rows[index].get("route_id") != args.route_id):
        print("proof_backlog_resolve=none reason=route_not_found")
        return 1
    row = rows[index]
    row["status"] = args.status
    row["resolved_at"] = iso(now_utc())
    row["proof_status"] = "CERTIFIED" if args.status == "CERTIFIED" else "COUNTEREXAMPLE"
    row["artifact"] = args.artifact
    row["note"] = args.note
    if args.next:
        row["next"] = args.next
    write_jsonl(args.queue, rows)
    print(f"proof_backlog_resolve=pass route_id={row.get('route_id')} status={args.status}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.queue)
    now = now_utc()
    counts: dict[str, int] = {}
    expired = 0
    for row in rows:
        status = str(row.get("status", "UNKNOWN"))
        counts[status] = counts.get(status, 0) + 1
        expires = parse_time(str(row.get("expires_at", "")))
        if row.get("status") == "CLAIMED" and expires and expires < now:
            expired += 1
    parts = " ".join(f"{key.lower()}={counts[key]}" for key in sorted(counts))
    print(f"proof_backlog_summary rows={len(rows)} {parts} expired_claims={expired}")
    for row in rows[: args.top]:
        print(
            "row "
            f"status={row.get('status')} owner={row.get('owner') or '-'} "
            f"route_id={row.get('route_id')} source={row.get('source_location')} "
            f"delta={row.get('expected_avgT_delta')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    import_ranked = sub.add_parser("import-ranked")
    import_ranked.add_argument("--ranked", type=Path, required=True)
    import_ranked.add_argument("--out", type=Path, required=True)
    import_ranked.add_argument("--frontier", default="")
    import_ranked.add_argument("--limit", type=int, default=0)
    import_ranked.set_defaults(func=cmd_import_ranked)

    claim = sub.add_parser("claim")
    claim.add_argument("--queue", type=Path, required=True)
    claim.add_argument("--owner", required=True)
    claim.add_argument("--route-id", default="")
    claim.add_argument("--ttl-minutes", type=int, default=45)
    claim.add_argument("--next", default="one bounded source proof: certificate or counterexample")
    claim.set_defaults(func=cmd_claim)

    resolve = sub.add_parser("resolve")
    resolve.add_argument("--queue", type=Path, required=True)
    resolve.add_argument("--route-id", required=True)
    resolve.add_argument("--status", choices=sorted(RESOLVE_STATUSES), required=True)
    resolve.add_argument("--artifact", default="")
    resolve.add_argument("--note", default="")
    resolve.add_argument("--next", default="")
    resolve.set_defaults(func=cmd_resolve)

    summary = sub.add_parser("summary")
    summary.add_argument("--queue", type=Path, required=True)
    summary.add_argument("--top", type=int, default=8)
    summary.set_defaults(func=cmd_summary)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
