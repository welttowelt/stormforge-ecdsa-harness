# Compute Unlock Gate

Use this after Storm closes compute and before any worker restarts fanout, GPU,
CPU, nonce-search, proof, or validation work.

## Command

    python3 scripts/storm-compute-unlock-gate.py <redacted-compute-packet>

Add --require-pass when the caller needs a hard shell gate.

## Pass Requirements

- route_id, owner, next, current source/base, frontier_score, and q-tier;
- remote or studio route, never Mac-local context;
- evidence_label=Partial;
- source-hash-bound value-exact packet;
- CERTIFIED proof/support status;
- exact diff or patch hash;
- negative expected avgT delta or positive score_edge;
- allocator order or allocator-order hash;
- validation_owner;
- budget;
- stop_condition or kill_condition;
- storm_route_ack=yes;
- no_submit_ack=yes.

## Decisions

- pass: compute-unlock-ready-for-storm-dispatch-no-submit.
- hold: packet is incomplete; do not restart compute.
- fail: compute is closed and the packet requests GPU/CPU/fanout/nonce work
  without the full unlock proof, or it carries prefilter/dirty evidence, stale
  source, local-heavy context, missing no-submit ACK, or premature submit
  language.

This gate only parses redacted packets. It does not run miners, build/eval, SSH
job control, alerts, or submit.
