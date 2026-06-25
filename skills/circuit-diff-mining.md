# Skill: Circuit Diff Mining

Use when looking for the next `ecdsa.fail` improvement from recent promoted
commits, submission notes, rejected low-qubit rows, or local route history.

## Goal

Turn frontier history into bounded candidate probes instead of broad rewrites or
stale knob copying.

## Source Order

1. Current public benchmark state.
2. Recent promoted source commits and diffs.
3. Public submission notes.
4. Local full-run output and generated metrics.
5. Historical clues from old branches or notes.

## Steps

1. Diff adjacent promoted commits, not old endpoints.
2. Separate peak-qubit moves from average-Toffoli moves.
3. Identify the changed mechanism: schedule width, carry/borrow lifetime,
   fold/add path, GCD window, codec, dead-op drop, nonce island, or validator
   behavior.
4. Ask what proof makes the removed work value-neutral.
5. Generate multiple candidate probes with distinct mechanisms.
6. Run the smallest check that can kill each probe.
7. Promote only validated mechanisms into a route packet.
8. Record dead mechanisms with the failure class.

## Candidate Ledger

```text
Candidate:
- Base commit/submission:
- Mechanism:
- Expected score movement:
- Evidence label:
- Failure class to watch:
- Cheap check:
- Full validator:
- Decision:
```

## Kill Gate

Do not scale a candidate if it only copies a knob across a changed op stream,
depends on a stale nonce, or lacks a reachable-support argument.

## Credit

Derived from repeated group-discussion process patterns around circuit
frontier-mining and mechanism isolation. This card includes no private chat
content.
