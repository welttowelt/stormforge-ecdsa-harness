# Official Eval Isolation Gate

Use this before treating remote build_circuit -> eval_circuit output as
submit-grade validation evidence.

## Problem

Remote survivor helpers can rebuild shared ops.bin and score.json in one
checkout while another eval is still running. That can make logs useful for
dirty triage but unsafe as clean-candidate evidence.

## Gate

Inspect the helper script or safe-eval log:

    python3 scripts/storm-official-eval-isolation-gate.py ev.sh --require-pass

The gate passes only when it sees one of:

- a lock around shared official eval artifacts, such as flock on a stable lock
  file; or
- an isolated per-run workspace, such as mktemp -d or a git worktree.

The gate fails when build_circuit and eval_circuit touch shared ops.bin,
score.json, or results.tsv without lock/isolation evidence.

## Discipline

- Failed isolation means triage-only evidence, even if the log says clean.
- Any apparent clean from a remote helper must still get local full official
  validation and a fresh frontier check before Akash/submit language.
- Fast-exit dirty triage can use the same lock or isolated workspace.
- Do not publish endpoints, raw private logs, or raw nonce ranges in public
  reports.

## Output

    official_eval_isolation_gate=<pass|hold|fail> has_build=... has_eval=... shared_artifact=... lock=... isolated=... decision=...
