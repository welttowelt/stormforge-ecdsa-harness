# Skill: Paper - Takahashi No-Ancilla Adder

Use when evaluating exact no-ancilla or low-ancilla addition as a fallback for
peak carry pressure.

## Source

- Yasuhiro Takahashi, Seiichiro Tani, and Noboru Kunihiro, "Quantum Addition
  Circuits and Unbounded Fan-Out", arXiv:0910.2530.

## Why We Keep It

The paper gives an exact O(n)-depth, O(n)-size quantum adder with no ancillary
qubits, plus a family of depth/ancilla tradeoffs. For ecdsa.fail this is a
baseline fallback: it can remove carry workspace, but likely costs too much
unless applied to a small peak suffix.

## Apply To

- suffix-only carry-ladder replacement;
- score-headroom checks for no-ancilla routes;
- comparing newer zero-ancilla adder papers against an older exact baseline.

## Required Invariant

The replacement must be restricted to a segment whose carry-in and carry-out
interfaces match the original circuit exactly.

## Procedure

1. Do not apply full-width by default.
2. Choose a suffix whose clean carries overlap the known peak.
3. Build a toy with the same incoming carry and outgoing carry obligation.
4. Count added Toffolis against the refreshed q-tier threshold.
5. Run residual before any dead-drop or nonce search.

## Output

```text
Takahashi no-ancilla adder:
- Segment width:
- Carry interface:
- Q saved:
- Added gate estimate:
- Toy/count/residual:
- Decision: use / compare / park
```

## Kill Gate

Reject the route if the only benefit is depth or asymptotic elegance. The local
score needs lower peak qubits without unaffordable Toffoli growth.

