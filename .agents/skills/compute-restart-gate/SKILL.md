---
name: compute-restart-gate
description: "Use before restarting ECDSA.fail GPU/CPU scanner work after compute was closed or pod queue eligibility is unclear."
---

# Compute Restart Gate

Codex-discoverable bridge to the public harness skill:

- Read `skills/compute-restart-gate.md`.
- Run `python3 scripts/storm-compute-restart-gate.py <packet> --require-pass`.
- A pass only clears a scanner restart gate; it never authorizes submit, alerts,
  or win language.
