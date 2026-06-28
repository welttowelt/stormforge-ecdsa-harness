---
name: pebbling-theorem-gate
description: Codex-discoverable bridge for Storm recompute/pebbling theorem packets.
---

# Pebbling Theorem Gate

Codex-discoverable bridge to the repo-local skill:

    skills/pebbling-theorem-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-pebbling-theorem-gate.py \
      <redacted-pebbling-packet.txt> \
      --require-pass

A pass only admits a source-bound pebbling theorem for review. It does not
authorize pods, residuals, alerts, or submit.
