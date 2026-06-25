# Skill: Paper - Haener ECDLP Circuits

Use when reviewing ecdsa.fail point-addition architecture against established
ECDLP circuit tradeoffs.

## Source

- Thomas Haener, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias
  Soeken, "Improved quantum circuits for elliptic curve discrete logarithms",
  arXiv:2001.09580.

## Why We Keep It

This paper is a route-shaping reference rather than a direct patch. It
emphasizes adaptive uncomputation placement, low-level modular arithmetic, and
tradeoffs between qubits, depth, and T gates for elliptic-curve scalar
multiplication.

## Apply To

- deciding whether a q-cut is worth its Toffoli growth;
- scheduling uncompute around point-add peaks;
- comparing inversion and point-add architecture choices;
- building reduced tests for point-add arithmetic components.

## Required Invariant

Any adapted placement of uncompute must preserve the same logical point-add
state at the same transcript boundary.

## Procedure

1. Identify the arithmetic component and its current TLM boundary.
2. Compare qubit, Toffoli, and depth effects instead of optimizing one metric.
3. State the exact state boundary that remains unchanged.
4. Test the component in isolation before full circuit residual.

## Output

```text
Haener ECDLP circuit tradeoff:
- Component:
- Boundary preserved:
- Q/T/depth movement:
- Test evidence:
- Decision: adopt / adapt / park
```

## Kill Gate

Do not import a scheduling idea if it changes transcript timing or point-add
state without a matching verifier update.
