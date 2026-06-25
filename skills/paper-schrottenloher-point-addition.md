# Skill: Paper - Schrottenloher Point Addition

Use when comparing ecdsa.fail secp256k1 point-addition routes to the 2026
optimized logical-circuit architecture.

## Source

- Andre Schrottenloher, "Optimized Point Addition Circuits for Elliptic Curve
  Discrete Logarithms", arXiv:2606.02235.

## Why We Keep It

This is a fresh secp256k1-specific point-addition reference. It is useful for
spotting architecture-level route ideas, especially when a local TLM edit hits
a wall and needs a broader point-add or modular-arithmetic comparison.

## Apply To

- secp256k1 point-add architecture review;
- kickmix or modular-multiply route comparison;
- deciding whether a local fold edit is chasing the wrong component;
- cross-checking qubit/Toffoli tradeoffs against a public logical circuit.

## Required Invariant

Any borrowed idea must be mapped to the current ecdsa.fail circuit boundary
and validated by local count/residual gates. Paper-level resource estimates
are not enough.

## Procedure

1. Identify the analogous component in the TLM code.
2. Translate the idea into one local invariant or reject it.
3. Run a count-only experiment only after the invariant is falsifiable.
4. Compare score movement, not just paper-level qubit count.

## Output

```text
Schrottenloher point-add review:
- Paper component:
- TLM component:
- Local invariant:
- Score-relevant movement:
- Decision: test / hand off / park
```

## Kill Gate

Do not claim a secp256k1 paper resource estimate as an ecdsa.fail improvement
until the local harness validates the actual op stream.
