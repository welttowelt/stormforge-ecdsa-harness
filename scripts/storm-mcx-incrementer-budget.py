#!/usr/bin/env python3
"""Budget low-ancilla replacements for the KG incrementer wall calls."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MCX_RE = re.compile(
    r"TLM_MCX_INC call=(\d+) phase=([^ ]+) n=(\d+) "
    r"skip_lsb_x=([^ ]+) anc=(\d+) ops_start=(\d+) ops_end=(\d+)"
)


@dataclass(frozen=True)
class McxTraceRow:
    call: int
    phase: str
    n: int
    skip_lsb_x: str
    anc: int
    ops_start: int
    ops_end: int


@dataclass(frozen=True)
class KgCount:
    n: int
    ancilla: int
    total_ccx: int
    forward_ccx: int
    apply_ccx: int
    apply_cx: int
    apply_x: int
    layers: int


def kg_get_layer_id(x: int) -> int:
    layer_id = 0
    total = 0
    while total <= x:
        total += (1 << layer_id) + 1
        layer_id += 1
    return layer_id - 1


def kg_start_layer(layer_id: int) -> int:
    total = 0
    for i in range(layer_id):
        total += (1 << i) + 1
    return total


def kg_prefix_ancilla_count(n: int) -> int:
    if n <= 1:
        return 0
    targets_len = kg_get_layer_id(n - 1) + 1
    if targets_len <= 2:
        return 1
    return 2 + kg_prefix_ancilla_count(targets_len)


def kg_anc_index(length: int, idx: int) -> int:
    return idx if idx >= 0 else length + idx


def ccx_op(a: str, b: str, t: str) -> tuple[str, str, str, str]:
    return ("ccx", a, b, t)


def x_op(t: str) -> tuple[str, str]:
    return ("x", t)


def kg_get_layers_for_prefix_and(q: list[str], inp_anc: list[str]) -> list[dict[str, list]]:
    if not q:
        raise ValueError("q must be non-empty")
    if len(q) == 1:
        return [
            {"ctrls": [], "ops": []},
            {"ctrls": [q[0]], "ops": []},
        ]
    if len(inp_anc) < kg_prefix_ancilla_count(len(q)):
        raise ValueError("not enough ancillae")

    n = len(q)
    n_layers = kg_get_layer_id(len(q) - 1)
    ret: list[dict[str, list]] = [{"ctrls": [], "ops": []}]
    targets: list[str] = []
    anc: list[str] = [inp_anc[0]]

    for layer_id in range(n_layers + 1):
        st = kg_start_layer(layer_id)
        en = min(n, kg_start_layer(layer_id + 1))

        layer_ctrls = list(targets)
        layer_ctrls.append(q[st])
        ret.append({"ctrls": layer_ctrls, "ops": []})

        for i in range(st + 1, en):
            offset = i - st
            anc_len = len(anc)
            q0 = q[i]
            if offset == 1:
                q1 = q[i - 1]
                target = anc[kg_anc_index(anc_len, -1)]
            else:
                q1 = anc[kg_anc_index(anc_len, -(offset - 1))]
                target = anc[kg_anc_index(anc_len, -offset)]
            ops: list[tuple] = []
            if target == inp_anc[0]:
                ops.append(ccx_op(q0, q1, target))
            else:
                ops.append(x_op(target))
                ops.append(ccx_op(q0, q1, target))
            ctrls = list(targets)
            ctrls.append(target)
            ret.append({"ctrls": ctrls, "ops": ops})

        layer_len = en - st
        targets.append(anc[kg_anc_index(len(anc), 1 - layer_len)])

        slice_start = kg_anc_index(len(anc), 2 - layer_len)
        next_anc = list(anc[slice_start:])
        next_anc.extend(q[st:en])
        anc = next_anc

    if len(targets) <= 2:
        return ret

    ret.append({"ctrls": [], "ops": []})
    target_prefix_layers = kg_get_layers_for_prefix_and(targets, inp_anc[2:])
    for layer_id in range(1, n_layers + 1):
        st = kg_start_layer(layer_id)
        en = min(n, kg_start_layer(layer_id + 1))
        target_prefix_targets = list(target_prefix_layers[layer_id]["ctrls"])
        ret[st + 1]["ops"].extend(target_prefix_layers[layer_id]["ops"])

        if len(target_prefix_targets) == 1:
            temp_target = target_prefix_targets[0]
        else:
            if len(target_prefix_targets) != 2:
                raise ValueError("expected <=2 target prefix controls")
            ret[st + 1]["ops"].append(ccx_op(target_prefix_targets[0], target_prefix_targets[1], inp_anc[1]))
            temp_target = inp_anc[1]

        for i in range(st, en):
            local = ret[i + 1]["ctrls"][-1]
            ret[i + 1]["ctrls"] = [temp_target, local]

        if len(target_prefix_targets) == 2:
            ret[en + 1]["ops"].append(ccx_op(target_prefix_targets[0], target_prefix_targets[1], temp_target))

    return ret


def current_incrementer_count(n: int, skip_lsb_x: bool = True) -> KgCount:
    prefix_inputs = [f"q{i}" for i in range(n - 1)]
    ancilla = kg_prefix_ancilla_count(len(prefix_inputs))
    inp_anc = [f"a{i}" for i in range(ancilla)]
    layers = kg_get_layers_for_prefix_and(prefix_inputs, inp_anc)
    forward_ccx = sum(1 for layer in layers for op in layer["ops"] if op[0] == "ccx")
    apply_ccx = 0
    apply_cx = 0
    apply_x = 0
    for i, layer in reversed(list(enumerate(layers))):
        if i >= n or (i == 0 and skip_lsb_x):
            continue
        controls = len(layer["ctrls"])
        if controls == 2:
            apply_ccx += 1
        elif controls == 1:
            apply_cx += 1
        elif controls == 0:
            apply_x += 1
        else:
            raise ValueError(f"unexpected control count n={n} layer={i} controls={controls}")
    total_ccx = forward_ccx * 2 + apply_ccx
    return KgCount(n, ancilla, total_ccx, forward_ccx, apply_ccx, apply_cx, apply_x, len(layers))


def read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open() as f:
            yield from f
    except FileNotFoundError as exc:
        raise SystemExit(f"trace_not_found path={path}") from exc


def parse_mcx_trace(path: Path | None) -> list[McxTraceRow]:
    if path is None:
        return []
    rows: list[McxTraceRow] = []
    for raw_line in read_lines(path):
        match = MCX_RE.search(raw_line)
        if not match:
            continue
        rows.append(
            McxTraceRow(
                call=int(match.group(1)),
                phase=match.group(2),
                n=int(match.group(3)),
                skip_lsb_x=match.group(4),
                anc=int(match.group(5)),
                ops_start=int(match.group(6)),
                ops_end=int(match.group(7)),
            )
        )
    return rows


def parse_calls_by_n(text: str) -> collections.Counter[int]:
    calls: collections.Counter[int] = collections.Counter()
    for item in re.split(r"[,\s]+", text.strip()):
        if not item:
            continue
        n_text, sep, count_text = item.partition(":")
        if not sep:
            raise SystemExit(f"bad_calls_by_n item={item}")
        calls[int(n_text)] += int(count_text)
    return calls


def calls_from_trace(rows: list[McxTraceRow]) -> collections.Counter[int]:
    calls: collections.Counter[int] = collections.Counter()
    for row in rows:
        calls[row.n] += 1
    return calls


def write_rows(path: Path, calls: collections.Counter[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "n",
                "calls",
                "current_ancilla",
                "current_ccx_per_call",
                "current_ccx_total",
                "forward_ccx",
                "apply_ccx",
                "apply_cx",
                "layers",
            ]
        )
        for n in sorted(calls):
            count = current_incrementer_count(n)
            writer.writerow(
                [
                    n,
                    calls[n],
                    count.ancilla,
                    count.total_ccx,
                    calls[n] * count.total_ccx,
                    count.forward_ccx,
                    count.apply_ccx,
                    count.apply_cx,
                    count.layers,
                ]
            )


def decide(candidate_extra: float | None, budget: float) -> str:
    if candidate_extra is None:
        return "need-candidate-extra-count"
    if candidate_extra <= budget:
        return "candidate-budget-pass"
    return "candidate-budget-fail"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, help="optional raw trace with TLM_MCX_INC rows")
    parser.add_argument(
        "--calls-by-n",
        default="10:6,11:6,12:6,13:6,14:6,15:6,16:6,17:6",
        help="fallback n:count map when no MCX trace rows are available",
    )
    parser.add_argument("--break-even-delta", type=float, default=1185.256, help="allowed added avg-Toffoli for the saved qubits")
    parser.add_argument("--saved-qubits", type=float, default=1.0, help="qubits saved by the candidate package")
    parser.add_argument("--candidate-extra-total", type=float, help="candidate added Toffoli/CCX total across all calls")
    parser.add_argument("--candidate-extra-per-call", type=float, help="candidate added Toffoli/CCX per call")
    parser.add_argument("--summary-out", type=Path, help="optional TSV count ledger")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    trace_rows = parse_mcx_trace(args.trace)
    calls = calls_from_trace(trace_rows) if trace_rows else parse_calls_by_n(args.calls_by_n)
    total_calls = sum(calls.values())
    if total_calls <= 0:
        raise SystemExit("no_mcx_calls")
    current_total = sum(calls[n] * current_incrementer_count(n).total_ccx for n in calls)
    max_current_ancilla = max(current_incrementer_count(n).ancilla for n in calls)
    budget = args.break_even_delta * args.saved_qubits
    if args.candidate_extra_total is not None:
        candidate_extra = args.candidate_extra_total
    elif args.candidate_extra_per_call is not None:
        candidate_extra = args.candidate_extra_per_call * total_calls
    else:
        candidate_extra = None
    if args.summary_out:
        write_rows(args.summary_out, calls)
    print(
        "mcx_incrementer_budget=pass "
        f"trace_rows={len(trace_rows)} total_calls={total_calls} n_values={','.join(str(n) for n in sorted(calls))} "
        f"max_current_ancilla={max_current_ancilla} current_total_ccx={current_total} "
        f"break_even_delta={args.break_even_delta} saved_qubits={args.saved_qubits} budget={budget} "
        f"max_extra_per_call={budget / total_calls:.6f} "
        f"candidate_extra_total={candidate_extra if candidate_extra is not None else 'none'} "
        f"decision={decide(candidate_extra, budget)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
