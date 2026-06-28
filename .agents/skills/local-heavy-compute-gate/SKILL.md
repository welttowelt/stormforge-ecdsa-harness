---
name: local-heavy-compute-gate
description: "Storm repo-local skill for blocking Mac-local heavy ECDSA.fail compute from redacted process snapshots while allowing lightweight harness checks."
license: MIT
---

# Local Heavy Compute Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/local-heavy-compute-gate.md.

After a HOT STOP or before maintaining any ECDSA.fail process on a laptop, read
that card and run scripts/storm-local-heavy-compute-gate.py on the redacted
snapshot.

This bridge is local-only. It does not inspect live processes, kill jobs, load
private endpoints, credentials, telemetry, or always-on behavior.
