# Official Fast-Exit Eval

Use this when many fanout GPU survivors need trusted dirty triage.

## Purpose

The patch in patches/eval-fast-exit-dirty-triage.patch adds an
ISLAND_FAST_EXIT flag to eval_circuit. When set, trusted eval stops after the
first dirty 64-shot batch. Clean candidates still run all shots because the loop
only breaks after a detected failure.

This is an evaluation-speed helper, not a circuit edit and not submit evidence.

## Gate

Apply only to a local validation checkout:

    git apply --check patches/eval-fast-exit-dirty-triage.patch
    git apply patches/eval-fast-exit-dirty-triage.patch
    cargo build --release --locked --bin eval_circuit

For survivor triage:

    ISLAND_FAST_EXIT=1 target/release/eval_circuit --note dirty-triage

Then pass the eval stdout into:

    python3 scripts/storm-fanout-survivor-phase-gate.py eval.out --nonce N --mark-survivor

## Discipline

- Use fast exit only to reject dirty candidates faster.
- A clean or submit path must still run official full validation without relying
  on early-exit counts.
- Do not compare average Toffoli from fast-exit dirty failures to frontier
  scores; the denominator is intentionally the tested dirty prefix.
- Keep survivor rows labelled as survivor-only unless official full validation
  proves 0/0/0 and the frontier score still wins.
