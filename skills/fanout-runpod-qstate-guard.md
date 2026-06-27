# Fanout RunPod Qstate Guard

Use this when launching q1152 SINGLE_CCX_FANOUT GPU nonce workers.

## Gate

Before any worker scans, run:

    python3 scripts/storm-fanout-qstate-guard.py /tmp/qstate.bin --expect-sha256 KNOWN_FANOUT_QSTATE_SHA256

The guard must report:

- qstate_guard=ok
- n_ops=10221059
- tx0=0
- tx1=1
- expected sha256, if supplied

## Discipline

- Do not use a stale qstate when route shape changed.
- Do not launch a fanout worker from a canonical qstate.
- Treat GPU CLEAN nonce=N as a prefilter survivor only.
- Any survivor still needs local SINGLE_CCX_FANOUT_DISABLE=0 DIALOG_TAIL_NONCE=N build_circuit -> eval_circuit.
- No submit, winner sentinel, or alert without fresh official 0/0/0 plus frontier recheck.

## Known Good Example

2026-06-28 fanout qstate:

- route: q1152-single-ccx-fanout-count-edge
- source head: d44cad386f2e121e2d952edcdcc3693f97d13153
- base nonce: recorded in the private launch manifest
- sha256: b31bf549b5e0c090f477b8d7e74ced9ecf346801b8004cdbf14d23b2b771e5c1
- header: GPU1, n_ops=10221059, tx0=0, tx1=1
