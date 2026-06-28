---
name: ffg-pair-proof-gate
description: Codex-discoverable bridge for the Storm FFG pair proof gate.
---

# FFG Pair Proof Gate

Codex-discoverable bridge to the repo-local skill:

    skills/ffg-pair-proof-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-ffg-pair-proof-gate.py \
      <redacted-ffg-proof-packet.txt> \
      --require-pass

Require pair-complete FFG call coverage, certified value/restore/phase proof,
source and candidate hashes, route_compare_admission=pass, admitted=1,
sufficient shot depth, positive score edge, and no-submit discipline before any
residual, compute, pod, handoff, submit, or alert language.
