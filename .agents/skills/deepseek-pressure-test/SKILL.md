---
name: deepseek-pressure-test
description: "Storm repo-local skill for external pressure-test worker prompts that try to kill ecdsa.fail routes before action."
license: MIT
---

# External Pressure-Test Worker

This is a Codex-discoverable bridge to the Storm prompt card at
`../../../skills/deepseek-pressure-test.md`.

Before sending a route to an external advisory worker, read that card and follow
its prompt shape, scoring, and output contract.

This bridge is local-only. It does not load private chat logs, private
endpoints, raw logs, nonces, telemetry, or always-on behavior.
