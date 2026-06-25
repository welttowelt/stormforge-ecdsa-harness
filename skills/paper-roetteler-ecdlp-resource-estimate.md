# Skill: Paper - Roetteler ECDLP Resource Estimate

Use when grounding ecdsa.fail point-add work against the classic prime-field
ECDLP Toffoli-network resource estimate.

## Source

- Martin Roetteler, Michael Naehrig, Krysta M. Svore, and Kristin Lauter,
  "Quantum resource estimates for computing elliptic curve discrete logarithms",
  arXiv:1706.06752.

## Why We Keep It

This paper provides a prime-field ECDLP reference built from simulated Toffoli
networks for controlled elliptic-curve point addition, reversible modular
addition, multiplication, and inversion. It is not a drop-in route, but it is a
useful baseline for state boundaries and resource accounting.

## Apply To

- deciding whether a local TLM route preserves the point-add boundary;
- comparing modular inversion and multiplication costs;
- explaining why controlled point-add validation must be gate-level, not only
  formula-level;
- public baseline notes.

## Required Invariant

Any borrowed architecture idea must preserve the same controlled point-add
semantic boundary under the local ecdsa.fail verifier.

## Procedure

1. Map the paper component to the local TLM module.
2. State the preserved state boundary.
3. Compare Q and Toffoli movement in local harness terms.
4. Run local count/residual gates before treating it as a route.

## Output

```text
Roetteler ECDLP baseline:
- Paper component:
- Local component:
- State boundary:
- Q/T comparison:
- Local validation:
- Decision: cite / test / park
```

## Kill Gate

Do not use asymptotic or whole-algorithm estimates as proof of a local point-add
improvement.

