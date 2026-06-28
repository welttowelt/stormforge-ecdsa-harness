---
name: compute-unlock-gate
description: Codex-discoverable bridge for the Storm compute unlock gate.
---

# Compute Unlock Gate

Codex-discoverable bridge to the repo-local skill:

    skills/compute-unlock-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-compute-unlock-gate.py <redacted-compute-packet>

Require a machine-readable packet with route_id, owner, current source, q-tier,
source-hash-bound certified value-exact proof, exact diff, negative edge,
allocator order, validation owner, budget, stop condition, storm_route_ack=yes,
and no_submit_ack=yes.
