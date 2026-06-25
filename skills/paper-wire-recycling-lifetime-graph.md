# Skill: Paper - Wire Recycling Lifetime Graph

Use when a lower-Q route changes qubit allocation, free-pool reuse, borrowed
ancillae, measurement vents, or high-ID scratch policy and then fails with
nonce-independent classical, phase, or ancilla garbage.

## Sources

- Alexandru Paler, Robert Wille, and Simon J. Devitt, "Wire Recycling for
  Quantum Circuit Optimization", arXiv:1609.00803.
- Yongshan Ding, Xin-Chuan Wu, Adam Holmes, Ash Wiseth, Diana Franklin,
  Margaret Martonosi, and Frederic T. Chong, "SQUARE: Strategic Quantum Ancilla
  Reuse for Modular Quantum Programs via Cost-Effective Uncomputation",
  arXiv:2004.08539.
- Anouk Paradis, Benjamin Bichsel, and Martin Vechev, "Reqomp:
  Space-constrained Uncomputation for Quantum Circuits", arXiv:2212.10395.
- Kengo Hirata and Chris Heunen, "Qurts: Automatic Quantum Uncomputation by
  Affine Types with Lifetime", arXiv:2411.10835.

## Why We Keep It

The current Gidney/conditionally-clean route can pass local adder selftests and
still fail in the full circuit if transient qubits are recycled onto wires whose
previous logical value has not been proven dead. These papers all point to the
same operational discipline: reuse is not a free-list guess; it is a lifetime
and dependency proof.

## Apply To

- Gidney 3-clean suffix or conditionally-clean cascade ports;
- any `alloc_qubit` / `zero_and_free` / measurement-vent change;
- stale dead-drop suspicion after an op-stream edit;
- high-ID scratch experiments intended to bypass free-pool aliasing;
- attempts to regenerate dead-op indexes for an edited stream.

## Required Invariant

For every recycled or borrowed qubit, prove that all gates depending on the
previous logical value precede the recycle point, and that the qubit is either
uncomputed to `|0>` or measured/reset with its phase dependency discharged
before the next logical use.

## Procedure

1. Build a per-qubit lifetime ledger for the suspect callsite:
   allocation, first gate, last data-dependent gate, measurement/reset,
   `zero_and_free`, and next allocation of the same physical ID.
2. Add causal edges from each logical value's output to the next logical input
   that reuses the wire. If an input can reach a prior output, the reuse is
   illegal.
3. Run the route once with stale dead drops disabled. If the failure class
   changes, regenerate dead-drop indexes before diagnosing allocation.
4. If the failure survives raw/no-drop, run an A/B allocation experiment:
   baseline free-pool reuse versus forced fresh high IDs for only the suspect
   transient family.
5. Accept high-ID or recycle changes only if they preserve `0/0/0` under the
   trusted evaluator and the Toffoli penalty still beats the refreshed q tier.

## Output

```text
Wire recycling lifetime graph:
- Route:
- Suspect transient family:
- Previous logical owner:
- Last dependency before recycle:
- Reuse causal edge:
- Raw/no-drop result:
- Free-pool vs high-ID A/B:
- Count/residual evidence:
- Decision: safe reuse / force fresh / regenerate drops / park
```

## Kill Gate

Do not treat a high-ID allocation patch as a win if it only hides aliasing
without a lifetime proof. Do not trust any recycled-wire result until stale
dead-drop indexes are disabled or regenerated for the edited op stream.
