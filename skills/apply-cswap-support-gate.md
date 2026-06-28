# Skill: Apply Cswap Support Gate

Use before a worker promotes an apply-step cswap deletion, requests compute for
one, or writes FOR-AKASH/submit language around one.

## Command

    python3 scripts/storm-apply-cswap-support-gate.py <redacted-proof-packet>

Add `--require-pass` when the caller needs a hard shell gate.

## Pass Requirements

- route is explicitly apply-cswap / apply-step cswap;
- source is bound to the current frontier and includes a source hash;
- source location is a `gcd.rs` cswap site;
- proof is per-step and per-bit, not blanket/global;
- invariant is either `swp=0` or `x==y` / equal operands;
- support is `CERTIFIED` with a source-hash-bound public certificate;
- expected delta is negative;
- validation boundary is named;
- `no_submit_ack=yes` is present.

## Decisions

- `pass`: ready for source-proof review only; no submit.
- `hold`: proof packet is incomplete.
- `fail`: broad delete, counterexample, local-heavy context, premature Akash/submit language, missing no-submit ACK, or nonnegative edge.

This gate does not run build/eval, nonce search, pod commands, alerts, or submit.
