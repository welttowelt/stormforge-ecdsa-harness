---
name: official-eval-isolation-gate
description: "Storm repo-local skill for checking official eval helpers are locked or isolated before their output is submit-grade evidence."
license: MIT
---

# Official Eval Isolation Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/official-eval-isolation-gate.md.

Before promoting remote eval output, read that card and run
scripts/storm-official-eval-isolation-gate.py on the helper script or safe-eval
log.

This bridge is local-only. It does not load private logs, endpoints, raw
nonces, telemetry, or always-on behavior.
