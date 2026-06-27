#!/usr/bin/env python3
"""Validate a q1152 fanout GPU qstate before spending fleet time.

This guard checks only public, non-secret properties of the CUDA state file:
magic, opcount, tail template ids, file size, and optional sha256. It is meant
to run before a RunPod/Vast/Akash worker is allowed to scan a claimed range.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys


DEFAULT_EXPECT_OPCOUNT = 10_221_059
DEFAULT_EXPECT_TX0 = 0
DEFAULT_EXPECT_TX1 = 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 32:
        raise ValueError(f"qstate too small: {len(data)} bytes")
    magic, = struct.unpack_from("<I", data, 0)
    n_ops, tx0, tx1 = struct.unpack_from("<QQQ", data, 4)
    base_pt, = struct.unpack_from("<I", data, 28)
    return {
        "path": str(path),
        "size": len(data),
        "sha256": sha256(path),
        "magic_hex": f"0x{magic:08x}",
        "magic_ok": magic == 0x47505531,
        "n_ops": n_ops,
        "tx0": tx0,
        "tx1": tx1,
        "base_pt": base_pt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qstate", type=Path)
    parser.add_argument("--expect-sha256", default="")
    parser.add_argument("--expect-opcount", type=int, default=DEFAULT_EXPECT_OPCOUNT)
    parser.add_argument("--expect-tx0", type=int, default=DEFAULT_EXPECT_TX0)
    parser.add_argument("--expect-tx1", type=int, default=DEFAULT_EXPECT_TX1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    row = inspect(args.qstate)
    failures: list[str] = []
    if not row["magic_ok"]:
        failures.append(f"bad_magic={row['magic_hex']}")
    if row["n_ops"] != args.expect_opcount:
        failures.append(f"bad_opcount={row['n_ops']} expected={args.expect_opcount}")
    if row["tx0"] != args.expect_tx0 or row["tx1"] != args.expect_tx1:
        failures.append(
            f"bad_tail_templates=tx0:{row['tx0']} tx1:{row['tx1']} "
            f"expected={args.expect_tx0}/{args.expect_tx1}"
        )
    if args.expect_sha256 and row["sha256"] != args.expect_sha256:
        failures.append(f"bad_sha256={row['sha256']} expected={args.expect_sha256}")

    row["ok"] = not failures
    row["failures"] = failures
    if args.json:
        print(json.dumps(row, sort_keys=True))
    elif failures:
        print("qstate_guard=fail " + " ".join(failures))
    else:
        print(
            "qstate_guard=ok "
            f"sha256={row['sha256']} n_ops={row['n_ops']} "
            f"tx0={row['tx0']} tx1={row['tx1']} base_pt={row['base_pt']} size={row['size']}"
        )
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
