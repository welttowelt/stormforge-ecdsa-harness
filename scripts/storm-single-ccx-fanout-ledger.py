#!/usr/bin/env python3
"""Summarize the SINGLE_CCX_FANOUT count/eval gate."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUMMARY_RE = re.compile(
    r"SINGLE_CCX_FANOUT: SUMMARY input_ops=(\d+) output_ops=(\d+) passes=(\d+)"
)
STOP_RE = re.compile(
    r"SINGLE_CCX_FANOUT: STOP passes=(\d+) input_ops=(\d+) output_ops=(\d+) reason=(.*)"
)
EMITTED_RE = re.compile(r"emitted ops\s*:\s*(\d+)")
LOADED_RE = re.compile(r"loaded ops\s*:\s*(\d+)")
QUBITS_RE = re.compile(r"qubits\s*:\s*(\d+)")
CLASSICAL_RE = re.compile(r"classical mismatches\s*:\s*(\d+)")
PHASE_RE = re.compile(r"phase-garbage batches\s*:\s*(\d+)")
ANCILLA_RE = re.compile(r"ancilla-garbage batches\s*:\s*(\d+)")


def read_text(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(errors="replace")


def find_int(pattern: re.Pattern[str], text: str, default: int = 0) -> int:
    match = pattern.search(text)
    return int(match.group(1)) if match else default


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse SINGLE_CCX_FANOUT build/eval evidence.")
    parser.add_argument("--build-stdout", type=Path)
    parser.add_argument("--build-stderr", type=Path, required=True)
    parser.add_argument("--eval-stdout", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_stdout = read_text(args.build_stdout)
    build_stderr = read_text(args.build_stderr)
    eval_stdout = read_text(args.eval_stdout)

    summary = SUMMARY_RE.search(build_stderr)
    stop = STOP_RE.search(build_stderr)
    input_ops = int(summary.group(1)) if summary else (int(stop.group(2)) if stop else 0)
    output_ops = int(summary.group(2)) if summary else (int(stop.group(3)) if stop else 0)
    passes = int(summary.group(3)) if summary else (int(stop.group(1)) if stop else 0)
    emitted_ops = find_int(EMITTED_RE, build_stdout, output_ops)
    loaded_ops = find_int(LOADED_RE, eval_stdout, 0)
    qubits = find_int(QUBITS_RE, eval_stdout, 0)
    classical = find_int(CLASSICAL_RE, eval_stdout, 0)
    phase = find_int(PHASE_RE, eval_stdout, 0)
    ancilla = find_int(ANCILLA_RE, eval_stdout, 0)

    if loaded_ops:
        if classical or phase or ancilla:
            decision = "trusted-eval-nack"
        elif emitted_ops and loaded_ops == emitted_ops:
            decision = "trusted-eval-clean"
        else:
            decision = "loaded-ops-mismatch"
    elif passes == 0:
        decision = "no-safe-fanout-candidate"
    elif passes > 0:
        decision = "needs-trusted-eval"
    else:
        decision = "missing-fanout-summary"

    print(
        "single_ccx_fanout_ledger=pass "
        f"input_ops={input_ops} "
        f"output_ops={output_ops} "
        f"delta_ops={output_ops - input_ops if input_ops and output_ops else 0} "
        f"passes={passes} "
        f"emitted_ops={emitted_ops} "
        f"loaded_ops={loaded_ops} "
        f"qubits={qubits} "
        f"classical={classical} "
        f"phase={phase} "
        f"ancilla={ancilla} "
        f"decision={decision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
