# Skill: Paper - HRS Dirty Constant Adder

Use when a lower-q route needs to trade clean carries for dirty borrowed
workspace in a constant-adder or modular-multiplication subroutine.

## Source

- Thomas Haener, Martin Roetteler, and Krysta M. Svore, "Factoring using
  2n+2 qubits with Toffoli based modular multiplication", arXiv:1611.07995.

## Why We Keep It

This paper is useful as a dirty-ancilla discipline check. Its in-place
constant adder uses dirty ancillae with Toffoli-based arithmetic, which is
close to the pressure tradeoff needed when a clean carry lane is the TLM peak.

## Apply To

- replacing resident clean carry storage;
- borrowed dirty lanes inside modular add/sub;
- proofs that a dirty host is restored, not merely overwritten;
- scoring Toffoli growth against a lower qubit tier.

## Required Invariant

The dirty workspace must be returned exactly to its input value for all
reachable states, and the arithmetic target must match the clean baseline.

## Procedure

1. Identify which clean carries would be removed and which dirty hosts would
   replace them.
2. Prove the dirty host is not assumed zero at allocation.
3. Run a reduced-width dirty-host exhaustive toy.
4. Compare clean-ladder and dirty-ladder counts before circuit-wide residual.
5. Promote only if the score tier still has Toffoli headroom.

## Output

```text
HRS dirty constant adder:
- Clean carries removed:
- Dirty hosts borrowed:
- Host-restore evidence:
- Count/score trade:
- Residual class:
- Decision: continue / narrow / park
```

## Kill Gate

Any ancilla dirt or hidden zero-assumption kills the route. Dirty ancillae are
not scratch; they are borrowed state.
