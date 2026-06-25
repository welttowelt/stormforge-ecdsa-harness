# Skill: Paper - Gidney Temporary Logical AND

Use when evaluating whether a lower-q route can reduce Toffoli/T-count or
uncompute arithmetic controls without keeping extra live workspace.

## Source

- Craig Gidney, "Halving the cost of quantum addition", arXiv:1709.06648.

## Why We Keep It

The temporary logical-AND construction is a reusable lens for ecdsa.fail
arithmetic: compute a control, use it, then erase it cheaply by measurement
and correction. It is less directly a q-cut than the 2025 adder paper, but it
is valuable for phase-clean uncompute and Toffoli budgeting.

## Apply To

- controlled add/sub uncompute;
- comparator-control cleanup;
- routes that add a small uncompute to lower peak qubits;
- Toffoli offset analysis after structural edits.

## Required Invariant

The temporary AND must only be used while its dependencies are still available
for the measurement-based erase correction.

## Procedure

1. Identify the computed control and all qubits it depends on.
2. Check whether those dependencies are alive at erase time.
3. Build a toy for the compute/use/erase sequence.
4. Account for Toffoli movement, not just peak-qubit movement.
5. Run residual before considering dead-drop or nonce search.

## Output

```text
Temporary logical AND:
- Control computed:
- Dependencies:
- Erase point:
- Toffoli delta:
- Phase/ancilla evidence:
- Decision: use / move / park
```

## Kill Gate

If the erase dependencies are no longer available, do not replace a reversible
uncompute with a measurement erase.
