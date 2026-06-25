# Skill: Paper - MBU Modular Arithmetic

Use when a proposed lower-q route relies on measuring or venting arithmetic
workspace and must prove the deferred phase cleanup exactly.

## Source

- Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya
  Sireesh, "Measurement-based uncomputation of quantum circuits for modular
  arithmetic", arXiv:2407.20167.

## Why We Keep It

This paper is useful because it formalizes measurement-based uncomputation
for add, subtract, compare, modular add, and controlled modular-add variants.
That is the exact proof obligation behind vented carries, HMR cleanup, and
borrowed-workspace edits in ecdsa.fail circuits.

## Apply To

- phase-only failures after HMR or carry venting;
- comparator and conditional modular-add cleanup;
- controlled add/sub route edits that claim a measured workspace can be freed;
- lower-q routes that need a phase-correction circuit before count gates.

## Required Invariant

Every measured bit must have a known phase correction function on preserved
registers, and that correction must be implementable within the route's
Toffoli and qubit budget.

## Procedure

1. Name the measured register and the preserved registers.
2. Write the correction function induced by each measurement outcome.
3. Build a toy reduced-width ANF or simulator check for the correction.
4. If the phase function is dense or unsupported, park before full-circuit
   compute.
5. If it is sparse and implemented, run the standard count/residual gates.

## Output

```text
MBU modular arithmetic:
- Measured workspace:
- Preserved registers:
- Phase function:
- Toy/ANF evidence:
- Implementation hook:
- Decision: correct / redesign / park
```

## Kill Gate

Do not treat a value-clean residual as clean if phase batches remain. MBU only
helps when the exact phase correction is implemented and validated.
