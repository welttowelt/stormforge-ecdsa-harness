#!/usr/bin/env python3
"""Gate const-chunk dead-prefix carry allocation ideas with source and trace facts."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONST_CHUNK_CONTEXT_PREFIX = 0x0800_0000


@dataclass(frozen=True)
class DeadRange:
    call: int
    lo: int
    hi: int

    @property
    def is_prefix(self) -> bool:
        return self.lo == 0

    @property
    def saved_allocs(self) -> int:
        return self.hi + 1 if self.is_prefix else 0

    @property
    def saved_ccx(self) -> int:
        return self.hi + 1 if self.is_prefix else 0


@dataclass
class TraceSummary:
    rows: int = 0
    weight: int = 0
    bits: set[int] | None = None

    def add(self, bit: int, weight: int) -> None:
        self.rows += 1
        self.weight += weight
        if self.bits is None:
            self.bits = set()
        self.bits.add(bit)

    @property
    def bit_count(self) -> int:
        return len(self.bits or set())


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def parse_dead_ranges(path: Path) -> list[DeadRange]:
    text = read_text(path)
    start = text.find("CONST_CHUNK_DEAD_RANGES")
    if start < 0:
        raise SystemExit("const_chunk_dead_ranges_not_found")
    end = text.find("];", start)
    if end < 0:
        raise SystemExit("const_chunk_dead_ranges_unclosed")
    block = text[start:end]
    ranges: list[DeadRange] = []
    for call, lo, hi in re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", block):
        ranges.append(DeadRange(int(call), int(lo), int(hi)))
    if not ranges:
        raise SystemExit("const_chunk_dead_ranges_empty")
    return ranges


def as_int(value: object, default: int = 0) -> int:
    try:
        text = str(value if value is not None else "").strip()
        if not text:
            return default
        return int(text, 0)
    except ValueError:
        return default


def split_ints(text: str) -> set[int]:
    values: set[int] = set()
    for part in re.split(r"[,\s]+", text.strip()):
        if not part:
            continue
        values.add(as_int(part))
    return values


def read_context_rows(path: Path | None) -> Iterable[dict[str, str]]:
    if path is None:
        return []
    try:
        with path.open(newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))
    except FileNotFoundError as exc:
        raise SystemExit(f"contexts_not_found path={path}") from exc


def decode_call_bit(row: dict[str, str]) -> tuple[int | None, int | None]:
    call = row.get("call") or row.get("trace_context_call")
    bit = row.get("bit") or row.get("trace_context_bit")
    if call not in (None, "") and bit not in (None, ""):
        return as_int(call), as_int(bit)
    raw = row.get("context_hex") or row.get("trace_context_value") or row.get("context") or ""
    value = as_int(raw, -1)
    if value < 0 or (value & 0xFF00_0000) != CONST_CHUNK_CONTEXT_PREFIX:
        return None, None
    return (value >> 8) & 0xFFFF, value & 0xFF


def row_family(row: dict[str, str]) -> str:
    family = row.get("family") or row.get("trace_context_family") or ""
    if family:
        return family
    raw = row.get("context_hex") or row.get("trace_context_value") or row.get("context") or ""
    value = as_int(raw, -1)
    if value >= 0 and (value & 0xFF00_0000) == CONST_CHUNK_CONTEXT_PREFIX:
        return "const_chunk_carry"
    return ""


def row_weight(row: dict[str, str]) -> int:
    return as_int(row.get("count") or row.get("executed_weight") or row.get("emitted_weight") or "1", 1)


def parse_contexts(path: Path | None) -> dict[int, TraceSummary]:
    summaries: dict[int, TraceSummary] = collections.defaultdict(TraceSummary)
    for row in read_context_rows(path):
        if row_family(row) != "const_chunk_carry":
            continue
        call, bit = decode_call_bit(row)
        if call is None or bit is None:
            continue
        summaries[call].add(bit, row_weight(row))
    return summaries


def prefix_by_call(ranges: Iterable[DeadRange]) -> dict[int, DeadRange]:
    out: dict[int, DeadRange] = {}
    for dead_range in ranges:
        if not dead_range.is_prefix:
            continue
        current = out.get(dead_range.call)
        if current is None or dead_range.hi > current.hi:
            out[dead_range.call] = dead_range
    return out


def write_summary(
    path: Path,
    prefix_ranges: dict[int, DeadRange],
    traces: dict[int, TraceSummary],
    binding_calls: set[int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    all_calls = sorted(set(prefix_ranges) | set(traces) | binding_calls)
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "call",
                "prefix_lo",
                "prefix_hi",
                "saved_allocs",
                "saved_ccx",
                "traced_rows",
                "traced_weight",
                "traced_bits",
                "binding_call",
                "prefix_binding",
            ]
        )
        for call in all_calls:
            dead_range = prefix_ranges.get(call)
            trace = traces.get(call, TraceSummary())
            writer.writerow(
                [
                    call,
                    dead_range.lo if dead_range else "",
                    dead_range.hi if dead_range else "",
                    dead_range.saved_allocs if dead_range else 0,
                    dead_range.saved_ccx if dead_range else 0,
                    trace.rows,
                    trace.weight,
                    trace.bit_count,
                    1 if call in binding_calls else 0,
                    1 if call in binding_calls and dead_range is not None else 0,
                ]
            )


def decide(binding_calls: set[int], binding_prefix_calls: set[int], delta_toffoli: int, break_even: float) -> tuple[str, str]:
    if not binding_calls:
        return "unknown", "need-binding-call-trace"
    if not binding_prefix_calls:
        return "fail", "nack-no-prefix-binding-call"
    if delta_toffoli <= break_even:
        return "pass", "prefix-binding-candidate"
    return "fail", "nack-budget-over-break-even"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arith-source", type=Path, required=True, help="trailmix_ludicrous/arith.rs source")
    parser.add_argument("--contexts", type=Path, help="wall-owner contexts TSV with const_chunk_carry rows")
    parser.add_argument("--binding-calls", default="", help="comma/space separated const_chunk call indices proven to bind the target wall")
    parser.add_argument("--break-even-delta", type=float, default=1185.256, help="max allowed avg-Toffoli delta for q1152->q1151")
    parser.add_argument("--summary-out", type=Path, help="optional TSV ledger output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ranges = parse_dead_ranges(args.arith_source)
    prefix_ranges = prefix_by_call(ranges)
    traces = parse_contexts(args.contexts)
    binding_calls = split_ints(args.binding_calls)
    traced_prefix_calls = set(prefix_ranges).intersection(traces)
    binding_prefix_calls = binding_calls.intersection(prefix_ranges)
    saved_allocs = sum(prefix_ranges[call].saved_allocs for call in binding_prefix_calls)
    saved_ccx = sum(prefix_ranges[call].saved_ccx for call in binding_prefix_calls)
    delta_toffoli = -saved_ccx
    score_gate, decision = decide(binding_calls, binding_prefix_calls, delta_toffoli, args.break_even_delta)
    if args.summary_out:
        write_summary(args.summary_out, prefix_ranges, traces, binding_calls)
    print(
        "const_chunk_prefix_ledger=pass "
        f"source_ranges={len(ranges)} prefix_ranges={len(prefix_ranges)} max_prefix_hi={max(r.hi for r in prefix_ranges.values()) if prefix_ranges else 0} "
        f"trace_calls={len(traces)} traced_prefix_calls={len(traced_prefix_calls)} "
        f"binding_calls={len(binding_calls)} binding_prefix_calls={len(binding_prefix_calls)} "
        f"estimated_saved_allocs={saved_allocs} estimated_saved_ccx={saved_ccx} "
        f"estimated_delta_toffoli={delta_toffoli} break_even_delta={args.break_even_delta} "
        f"score_gate={score_gate} decision={decision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
