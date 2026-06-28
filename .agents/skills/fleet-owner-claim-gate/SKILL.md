---
name: fleet-owner-claim-gate
description: "Storm repo-local skill for checking paid fleet instances have owner, route, watcher/log, next action, and no-submit ACK before surviving audit."
license: MIT
---

# Fleet Owner Claim Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/fleet-owner-claim-gate.md.

Before keeping a paid instance online after an audit, read that card and run
scripts/storm-fleet-owner-claim-gate.py on the proposed owner packet.

This bridge is local-only. It does not load private logs, endpoints, raw
nonces, telemetry, or always-on behavior.
