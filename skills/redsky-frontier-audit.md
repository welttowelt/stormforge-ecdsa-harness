# Skill: Redsky Frontier Audit

Use when doing an adversarial audit of an `ecdsa.fail` route, candidate diff,
submission note, compute request, or submit packet.

## Goal

Try to kill the route before paid compute, public claims, or submission. If it
survives, name the exact gate that makes the next action justified.

## Required Checks

1. Frontier freshness: current best, promoted source, and local base are known.
2. Edit legality: intended changes are inside benchmark-editable circuit paths.
3. Metric clarity: qubits, average Toffoli, and score are separated.
4. Evidence label: `Promoted`, `Local full run`, `Partial run`, `Prefilter`,
   `Paper score`, or `Historical clue`.
5. Correctness risk: classical, phase, ancilla, nonce, or measurement artifact.
6. Search economics: compute budget, expected survivor density, and stop rule.
7. Submit gate: fresh frontier, official validation, legal diff, public note,
   and explicit submit decision.

## Output

```text
Redsky audit:
- Target:
- Evidence label:
- Frontier state:
- Strongest objection:
- Fastest falsifier:
- Failure class:
- Search-economics risk:
- Smallest useful fix:
- Gate:
- Decision: proceed / measure / park / kill
```

## Kill Gate

Any unknown frontier, illegal edit path, missing validator, missing stop
condition, or unlabeled evidence blocks compute and submit.

## Credit

Repo-local companion to the Redsky audit discipline for public `ecdsa.fail`
frontier work. This card includes no private chat content.
