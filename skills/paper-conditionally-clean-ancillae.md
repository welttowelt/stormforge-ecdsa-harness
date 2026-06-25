# Skill: Paper - Conditionally Clean Ancillae

Use when a lower-Q route wants to borrow an existing qubit as if it were clean
only on the branch where a computation uses it.

## Source

- Tanuj Khattar and Craig Gidney, "Rise of conditionally clean ancillae for
  efficient quantum circuit constructions", arXiv:2407.17966.

## Why We Keep It

This paper is directly relevant to the ecdsa.fail low-qubit wall. It introduces
conditionally clean ancillae, which start and end in an unknown state like dirty
ancillae, but can be treated as clean inside a controlled computation when the
control condition guarantees a known value. The paper also gives low-ancilla
constructions for multi-controlled NOT, incrementers, comparators, unary
iteration, and dirty-ancilla toggle detection.

## Apply To

- inverse-fold carry and cout hosts;
- comparator controls whose inactive branch preserves a host;
- prefix incrementers and small suffix adders;
- any route currently blocked by a single clean carry lane.

## Required Invariant

The borrowed host must be provably clean under the exact control condition that
uses it, and restored on both active and inactive branches.

Do not use a conditionally clean host as temporary workspace for computations
that involve the same control qubits on which that host is conditioned. That is
the easiest way to turn an apparently clean carry loan into value or phase dirt.

## Procedure

1. Name the branch/control that makes the host conditionally clean.
2. Prove the host value under that branch with a source trace or toy model.
3. Replace one local clean host, not a whole family.
4. Run count, then fresh residual on the single-callsite route.
5. Widen only if the first host is value, phase, and ancilla clean.

## Current Applied Gate

A 2026-06-26 q1152 diagnostic separated the local primitive from integration:
the Gidney 3-clean toy selftest passed, but swapping borrowed/fresh transient
hosts and replaying old dead-drop lists changed trusted failure classes. Treat
that as a host-condition and stale-drop signal, not as proof that the paper
primitive is invalid.

## Output

```text
Conditionally clean ancillae:
- Source control:
- Borrowed host:
- Clean-on-branch proof:
- Restored-on-both-branches proof:
- Count/residual evidence:
- Decision: use / narrow / park
```

## Kill Gate

If the host is merely dirty, sampled clean, or clean on the wrong branch, park
the route before count gates.
