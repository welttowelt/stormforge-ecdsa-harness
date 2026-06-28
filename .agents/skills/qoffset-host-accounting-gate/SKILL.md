---
name: qoffset-host-accounting-gate
description: Codex-discoverable bridge for the Storm qoffset host-accounting packet gate.
---

# Qoffset Host Accounting Gate

Codex-discoverable bridge to the repo-local skill:

    skills/qoffset-host-accounting-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-qoffset-host-accounting-gate.py \
      <redacted-qoffset-packet.txt> \
      --require-pass

A pass only admits a source-integrated qoffset packet or counterexample closure.
It does not authorize pods, residuals, alerts, or submit.
