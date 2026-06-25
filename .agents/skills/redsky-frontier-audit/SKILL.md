---
name: redsky-frontier-audit
description: "Storm repo-local skill for adversarial ecdsa.fail frontier, route, compute, and submit audits."
license: MIT
---

# Redsky Frontier Audit

This is a Codex-discoverable bridge to the Storm prompt card at
`../../../skills/redsky-frontier-audit.md`.

Before compute or submit decisions, read that card and follow its required
checks, output, and kill gate. If the global `redsky` skill is available, load
it first and use this card as the repo-local operating wrapper.

This bridge is local-only. It does not load private chat logs, private
endpoints, raw logs, nonces, telemetry, or always-on behavior.
