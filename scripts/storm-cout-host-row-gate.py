#!/usr/bin/env python3
"""Validate COUT borrowed-|0> host-row packets before count or source hooks.

This is an admission gate for Anvil/Kiln-style trace rows. It does not build a
trace, edit the challenge source, count a candidate, run residuals, or submit.
It checks whether one host-row packet has the fields needed for downstream
value/phase validation and rejects obvious alias, double-free, or no-host cases.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TRUTHY = {"1", "true", "yes", "y", "pass", "safe", "ok"}
FALSY = {"0", "false", "no", "n", "fail", "unsafe"}


@dataclass(frozen=True)
class HostDecision:
    result: str
    reason: str
    validator_ready: bool


def norm_key(key: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", key.strip().lower())).strip("_")


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        normalized[norm_key(key)] = str(value).strip()
    # Common aliases from mailbox wording and Kiln's validator schema.
    aliases = {
        "borrow_start": "borrow_start_op",
        "borrow_end": "borrow_end_op",
        "zero_op": "zero_free_op",
        "free_op": "zero_free_op",
        "owner_reads_writes_during_borrow": "owner_reads_or_writes_during_borrow",
        "disjoint_from_ctrl_a_b_cout_carry_operands": "disjoint_from_operands",
        "operand_qids_touched": "operand_qids",
    }
    for old, new in aliases.items():
        if old in normalized and new not in normalized:
            normalized[new] = normalized[old]
    for key, value in list(normalized.items()):
        if key.startswith("disjoint_from") and "operand" in key and "disjoint_from_operands" not in normalized:
            normalized["disjoint_from_operands"] = value
    return normalized


def parse_int(row: dict[str, str], key: str) -> int | None:
    value = row.get(key, "")
    if value == "":
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def parse_bool(row: dict[str, str], key: str) -> bool | None:
    value = row.get(key, "").strip().lower()
    if value in TRUTHY:
        return True
    if value in FALSY:
        return False
    return None


def parse_int_list(text: str) -> list[int]:
    if not text:
        return []
    out: list[int] = []
    for part in re.split(r"[\s,;|]+", text.strip()):
        if not part:
            continue
        try:
            out.append(int(part, 0))
        except ValueError:
            pass
    return out


def read_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    if text[0] in "[{":
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return [normalize_row(loaded)]
        if isinstance(loaded, list):
            return [normalize_row(item) for item in loaded if isinstance(item, dict)]
        raise SystemExit("host_row_gate=fail reason=json_must_be_object_or_list")
    if "\t" in text.splitlines()[0] or "," in text.splitlines()[0]:
        dialect = csv.excel_tab if "\t" in text.splitlines()[0] else csv.excel
        return [normalize_row(row) for row in csv.DictReader(text.splitlines(), dialect=dialect)]
    row: dict[str, str] = {}
    for part in re.split(r"\s+", text):
        if "=" in part:
            key, value = part.split("=", 1)
            row[key] = value
    return [normalize_row(row)] if row else []


def required_missing(row: dict[str, str]) -> list[str]:
    required = [
        "host_qid",
        "owner_family",
        "owner_call",
        "owner_bit",
        "alloc_op",
        "zero_free_op",
        "last_write_before_borrow",
        "borrow_start_op",
        "borrow_end_op",
        "owner_reads_or_writes_during_borrow",
        "disjoint_from_operands",
        "operand_qids",
    ]
    return [key for key in required if row.get(key, "") == ""]


def decide(row: dict[str, str]) -> HostDecision:
    missing = required_missing(row)
    if missing:
        return HostDecision("NO_HOST", f"missing:{','.join(missing)}", False)

    host_qid = parse_int(row, "host_qid")
    alloc_op = parse_int(row, "alloc_op")
    zero_free_op = parse_int(row, "zero_free_op")
    last_write = parse_int(row, "last_write_before_borrow")
    borrow_start = parse_int(row, "borrow_start_op")
    borrow_end = parse_int(row, "borrow_end_op")
    required_ints = {
        "host_qid": host_qid,
        "alloc_op": alloc_op,
        "zero_free_op": zero_free_op,
        "last_write_before_borrow": last_write,
        "borrow_start_op": borrow_start,
        "borrow_end_op": borrow_end,
    }
    bad_ints = [key for key, value in required_ints.items() if value is None]
    if bad_ints:
        return HostDecision("NO_HOST", f"bad_int:{','.join(bad_ints)}", False)

    assert host_qid is not None
    assert alloc_op is not None
    assert zero_free_op is not None
    assert last_write is not None
    assert borrow_start is not None
    assert borrow_end is not None

    if borrow_start > borrow_end:
        return HostDecision("NO_HOST", "borrow_window_inverted", False)
    if alloc_op > borrow_start:
        return HostDecision("NO_HOST", "host_not_allocated_before_borrow", False)
    if zero_free_op < borrow_start:
        return HostDecision("NO_HOST", "host_freed_before_borrow", False)
    if borrow_start <= zero_free_op <= borrow_end:
        return HostDecision("DOUBLE_FREE", "owner_zero_free_inside_borrow", False)
    if last_write >= borrow_start:
        return HostDecision("HARD_NACK_ALIAS", "owner_last_write_inside_or_after_borrow_start", False)

    owner_touch_ops = parse_int_list(row.get("owner_touch_ops", ""))
    overlap_touches = [op for op in owner_touch_ops if borrow_start <= op <= borrow_end]
    if overlap_touches:
        return HostDecision("HARD_NACK_ALIAS", f"owner_touch_inside_borrow:{overlap_touches[0]}", False)

    owner_touches = parse_bool(row, "owner_reads_or_writes_during_borrow")
    if owner_touches is not False:
        return HostDecision("HARD_NACK_ALIAS", "owner_reads_or_writes_during_borrow_not_no", False)

    disjoint = parse_bool(row, "disjoint_from_operands")
    operand_qids = parse_int_list(row.get("operand_qids", ""))
    if disjoint is not True:
        return HostDecision("HARD_NACK_ALIAS", "operand_disjointness_not_yes", False)
    if host_qid in operand_qids:
        return HostDecision("HARD_NACK_ALIAS", "host_qid_is_cout_operand", False)

    validator_ready = (
        parse_int(row, "chunk_width") is not None
        and parse_bool(row, "cin_present") is not None
        and parse_bool(row, "erase_is_inverse") is not None
        and row.get("owner_touch_ops", "") != ""
    )
    return HostDecision("SAFE_HOST_ROW", "qid_live_idle_disjoint", validator_ready)


def write_summary(path: Path, rows: Iterable[dict[str, str]], decisions: Iterable[HostDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["index", "host_qid", "owner_family", "owner_call", "owner_bit", "result", "reason", "validator_ready"])
        for index, (row, decision) in enumerate(zip(rows, decisions), start=1):
            writer.writerow(
                [
                    index,
                    row.get("host_qid", ""),
                    row.get("owner_family", ""),
                    row.get("owner_call", ""),
                    row.get("owner_bit", ""),
                    decision.result,
                    decision.reason,
                    int(decision.validator_ready),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="host-row TSV/CSV/JSON/key=value packet")
    parser.add_argument("--summary-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.input)
    if not rows:
        raise SystemExit("host_row_gate=fail reason=no_rows")
    decisions = [decide(row) for row in rows]
    if args.summary_out:
        write_summary(args.summary_out, rows, decisions)
    safe = sum(1 for decision in decisions if decision.result == "SAFE_HOST_ROW")
    alias = sum(1 for decision in decisions if decision.result == "HARD_NACK_ALIAS")
    double_free = sum(1 for decision in decisions if decision.result == "DOUBLE_FREE")
    no_host = sum(1 for decision in decisions if decision.result == "NO_HOST")
    validator_ready = sum(1 for decision in decisions if decision.validator_ready)
    first = decisions[0]
    print(
        "cout_host_row_gate=pass "
        f"rows={len(rows)} "
        f"safe={safe} "
        f"hard_nack_alias={alias} "
        f"double_free={double_free} "
        f"no_host={no_host} "
        f"validator_ready={validator_ready} "
        f"first_result={first.result} "
        f"first_reason={first.reason}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
