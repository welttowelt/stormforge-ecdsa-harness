---
name: apply-cswap-support-gate
description: Codex-discoverable bridge for the Storm apply-cswap support gate.
---

# Apply Cswap Support Gate

Codex-discoverable bridge to the repo-local skill:

    skills/apply-cswap-support-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-apply-cswap-support-gate.py <redacted-proof-packet>

Require a machine-readable packet with `route_id`, `owner`, `next`,
`frontier_score`, q-tier, source hash, per-step/per-bit scope, a source-proof
evidence label, and `no_submit_ack=yes`.
