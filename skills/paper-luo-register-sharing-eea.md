# Skill: Paper - Luo Register-Sharing EEA

Use when exploring lower-qubit modular inversion routes based on compact
register sharing and location-controlled arithmetic.

## Source

- Han Luo, Ziyi Yang, Ziruo Wang, Yuexin Su, and Tongyang Li, "Space-Efficient
  Quantum Algorithm for Elliptic Curve Discrete Logarithms with Resource
  Estimation", arXiv:2604.02311.

## Why We Keep It

This paper is useful as a structural prompt for going below local adder tweaks.
It focuses on modular inversion as the main space driver and uses register
sharing plus location-controlled arithmetic to reduce logical qubits.

## Apply To

- routes that move beyond one-callsite carry edits;
- transcript or codec rewrites that compact intermediate EEA state;
- location-controlled arithmetic ideas for inverse-GCD lanes;
- long-horizon q1152-and-lower architecture planning.

## Required Invariant

The compact state representation must be reversible and must expose exactly
the operands required by each arithmetic step without hidden decompression
peaks that erase the qubit win.

## Procedure

1. Draw the current live-register ledger for the inverse/GCD phase.
2. Mark which registers are mutually exclusive by source-level state.
3. Build a reduced EEA/location-control toy before touching the full circuit.
4. Count decompression and routing scratch explicitly.
5. Promote only if peak and score both improve locally.

## Software Gate

Use `scripts/resident-footprint-ledger.sh` on a `TLM_FFG` trace before changing
architecture. It tells you whether a lower tier needs a local carry cut or a
plateau-wide resident-footprint reduction.

```bash
scripts/resident-footprint-ledger.sh \
  --trace /tmp/codex_alloc_near_1145.err \
  --frontier 1577850522 \
  --q 1147 \
  --target-q 1146 \
  --route q1147-clean
```

If one-callsite adder/comparator cuts leave the max peak unchanged, apply the
Luo paper only as a resident-register sharing prompt: prove which live register
can be represented more compactly across every above-target call, then audit
the decompression peak.

## 2026-06-26 Application

## Output

```text
Luo register-sharing EEA:
- Registers considered:
- Mutual-exclusion invariant:
- Location-control toy:
- Hidden scratch audit:
- Decision: prototype / narrow / park
```

Current q1147 lower-Q trace:

- target q1146 requires a uniform 1-qubit reduction across the max inverse-fold
  plateau, not just a comparator or adder micro-cut;
- the relevant rows are the max `tlm_apply_inverse_mod_sub_fold` calls, with
  entry-active around 1105..1109 and local peak 1147;
- if a register-sharing idea hides even one decompression qubit inside those
  calls, it gives back the entire q cut.

## Kill Gate

If compacting a register requires a decompression peak equal to or above the
baseline, the route is architecture noise, not a lower-q improvement.
