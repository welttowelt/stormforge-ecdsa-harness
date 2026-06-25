# qcut-paper-mining - Cycle 2 Memory Recycling Lead

Date: 2026-06-25

## Finding

The current q1152 Gidney-style route no longer looks blocked by the local
adder primitive alone. The useful paper direction is memory recycling and
space-constrained uncomputation:

- Reichental, Alon, Preminger, Vax, Naveh, "Scalable Memory Recycling for Large
  Quantum Programs", arXiv:2503.00822.
- Meuli, Soeken, Roetteler, Bjorner, De Micheli, "Reversible Pebbling Game for
  Quantum Memory Management", arXiv:1904.02121.
- Paradis, Bichsel, Vechev, "Reqomp: Space-constrained Uncomputation for
  Quantum Circuits", Quantum 8:1258 (2024).

## Local Mapping

These papers frame width reduction as a schedule and memory-reuse problem. For
the ecdsa.fail TLM route, that is exactly the current integration hazard: a
primitive can be correct in isolation, but if it changes active-qubit timing,
then dynamic headroom-driven choices such as FFG `g` can drift downstream.
That creates deterministic value dirt that no nonce search can fix.

## Actionable Skill

Added `skills/paper-scalable-memory-recycling.md` and the `.agents` bridge.
The skill requires:

- baseline schedule ledger before edit;
- frozen baseline schedule replay after edit;
- active-timeline diff separate from semantic schedule diff;
- explicit rebaked schedule table if the edited primitive changes downstream
  headroom decisions;
- no-drop residual before dead-drop or nonce work.

## Next Gate

For the q1152 Gidney branch, the next falsifiable gate is not another
boundary-carry toy. It is:

```text
Gidney suffix + forced baseline per-call FFG schedule -> no-drop eval.
```

If frozen-schedule mode is clean, the primitive is usable and the schedule must
be rebaked carefully. If frozen-schedule mode is dirty, the integration bug is
still in lifetime/free-list behavior around the primitive.
