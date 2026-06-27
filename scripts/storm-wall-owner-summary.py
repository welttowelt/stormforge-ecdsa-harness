#!/usr/bin/env python3
"""Summarize wall-owner op-site contexts for exact-miner scout intake."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path
from typing import Iterable


SourceKey = tuple[str, str, str, str, str]
FamilyKey = tuple[str, str]


TRACE_CONTEXT_FAMILIES = {
    0x0100_0000: "ffg_prefix_carry",
    0x0200_0000: "cuccaro_forward_carry",
    0x0300_0000: "cuccaro_reverse_carry",
    0x0400_0000: "comparator_top_carry",
    0x0500_0000: "gidney_thread_forward_carry",
    0x0600_0000: "gidney_thread_boundary_carry",
    0x0700_0000: "gidney_thread_sum",
    0x0800_0000: "const_chunk_carry",
    0x0900_0000: "gidney_erase_ccz",
    0x0A00_0000: "gidney_erase_capped_ccz",
    0x0B00_0000: "gcd_right_shift_cswap",
    0x0C00_0000: "gcd_left_shift_cswap",
    0x0D00_0000: "fused_clean_fold_carry",
    0x0E00_0000: "fused_chunk_fold_carry",
    0x0F00_0000: "fused_dirty_fold_carry",
    0x1000_0000: "fused_clean_window_carry",
    0x1100_0000: "add_const_carry",
    0x1200_0000: "gcd_reverse_cswap",
    0x1300_0000: "compare_cin_carry",
    0x1400_0000: "fused_cdouble_shift",
    0x1500_0000: "fused_cdouble_reverse_shift",
    0x1600_0000: "gidney_hybrid_forward_carry",
    0x1700_0000: "gidney_hybrid_sum",
    0x1800_0000: "gidney_hybrid_dirty_uncompute",
    0x1900_0000: "gidney_hybrid_uncompute",
    0x1A00_0000: "gidney_hybrid_low_sum",
    0x1B00_0000: "gcd_forward_cswap",
    0x1C00_0000: "fused_boundary_zero_carry",
}


def as_int(text: str) -> int:
    try:
        return int(str(text).strip())
    except ValueError:
        return 0


def read_contexts(path: Path) -> Iterable[dict[str, str]]:
    try:
        with path.open(newline="") as f:
            yield from csv.DictReader(f, delimiter="\t")
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def row_source_hash(row: dict[str, str], default: str) -> str:
    return (
        row.get("source_hash")
        or row.get("source_snippet_hash")
        or row.get("source_code_hash")
        or default
        or ""
    ).strip()


def decode_context_family(text: str) -> str:
    raw = str(text or "").strip()
    if not raw or raw.lower() in {"none", "unknown"}:
        return ""
    try:
        value = int(raw, 0)
    except ValueError:
        return ""
    return TRACE_CONTEXT_FAMILIES.get(value & 0xFF00_0000, "")


def source_file_line(row: dict[str, str]) -> tuple[str, str]:
    file_name = row.get("file") or row.get("source_file") or ""
    line = row.get("line") or row.get("source_line") or ""
    if file_name and line:
        return file_name, line
    location = row.get("source_location") or ""
    match = re.search(r"(.+\.rs):([0-9]+)$", location)
    if match:
        return match.group(1), match.group(2)
    return file_name, line


def row_family(row: dict[str, str]) -> str:
    return (
        row.get("family")
        or row.get("trace_context_family")
        or decode_context_family(
            row.get("context_hex")
            or row.get("trace_context_value")
            or row.get("context")
            or row.get("branch_context")
            or ""
        )
        or "unclassified"
    )


def row_count(row: dict[str, str]) -> int:
    return as_int(row.get("count") or row.get("executed_weight") or row.get("emitted_weight") or "0")


def sort_source(item: tuple[SourceKey, int]) -> tuple[int, str, int, str, str, str]:
    (file_name, line, family, kind, source_hash), count = item
    return (-count, file_name, as_int(line), family, kind, source_hash)


def sort_family(item: tuple[FamilyKey, int]) -> tuple[int, str, str]:
    (family, kind), count = item
    return (-count, family, kind)


def write_source_summary(path: Path, rows: list[tuple[SourceKey, int]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["file", "line", "family", "kind", "count", "source_hash"])
        for (file_name, line, family, kind, source_hash), count in selected:
            writer.writerow([file_name, line, family, kind, count, source_hash])


def write_family_summary(path: Path, rows: list[tuple[FamilyKey, int]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["family", "kind", "count"])
        for (family, kind), count in selected:
            writer.writerow([family, kind, count])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contexts", type=Path, required=True, help="wall-owner-contexts TSV")
    parser.add_argument("--source-line-out", type=Path, required=True, help="source-line-family-summary TSV")
    parser.add_argument("--family-kind-out", type=Path, required=True, help="family-kind-summary TSV")
    parser.add_argument("--source-hash", default="", help="default public source hash or source label")
    parser.add_argument("--limit", type=int, default=0, help="maximum rows per output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_counts: collections.Counter[SourceKey] = collections.Counter()
    family_counts: collections.Counter[FamilyKey] = collections.Counter()
    input_rows = 0
    for row in read_contexts(args.contexts):
        file_name, line = source_file_line(row)
        family = row_family(row)
        kind = row.get("kind", "").upper()
        count = row_count(row)
        source_hash = row_source_hash(row, args.source_hash)
        if not file_name or not line or not family or not kind or count <= 0:
            continue
        input_rows += 1
        source_counts[(file_name, line, family, kind, source_hash)] += count
        family_counts[(family, kind)] += count

    source_rows = sorted(source_counts.items(), key=sort_source)
    family_rows = sorted(family_counts.items(), key=sort_family)
    write_source_summary(args.source_line_out, source_rows, args.limit)
    write_family_summary(args.family_kind_out, family_rows, args.limit)
    print(
        "wall_owner_summary=pass "
        f"input_rows={input_rows} source_rows={len(source_rows)} family_rows={len(family_rows)} "
        f"source_line_out={args.source_line_out} family_kind_out={args.family_kind_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
