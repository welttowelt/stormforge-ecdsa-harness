# Skill: Paper - Gidney Constant-Workspace Adder

Use when trying to replace a clean carry ladder in an ecdsa.fail route with a
source-backed constant-workspace classical-quantum adder.

## Source

- Craig Gidney, "A Classical-Quantum Adder with Constant Workspace and Linear
  Gates", arXiv:2507.23079.
- Reference code: `Strilanc/classical-quantum-adder`.

## Why We Keep It

This paper is directly actionable for lower-q work. It gives:

- a 3-clean-ancilla classical-constant adder with linear Toffoli cost;
- a 2-clean plus dirty-ancilla adder;
- controlled variants that do not require extra workspace or Toffolis;
- a public generator that can be used as an executable reference.

It maps to TLM inverse-fold pressure where a resident clean carry ladder
creates the peak qubit.

## Apply To

- `src/point_add/trailmix_ludicrous/arith.rs`
- `const_chunk_add_clean`
- `controlled_add_const_chunked_graduated_off`
- `add_f_window`
- inverse-fold FFG calls at the live peak

## Required Invariant

The replacement must preserve target value, control qubit, carry-in, dirty
borrowed hosts, clean ancillae, and phase for every reachable input.

## Procedure

1. Generate or inspect the reference circuit for the same width, control mode,
   and carry-in mode.
2. Build a reduced-width exhaustive toy covering nonzero carry-in and arbitrary
   dirty borrowed hosts.
3. Only after the toy is value/phase/ancilla clean, port one callsite.
4. Run count first, then fresh serialized build plus `residual_probe`.
5. Widen to multiple callsites only after one callsite is clean.

## Output

```text
Gidney constant-workspace adder:
- Source reference:
- Width/control/carry mode:
- Borrowed hosts:
- Toy evidence:
- Count delta:
- Residual class:
- Decision: port / narrow / park
```

## Kill Gate

Park the route on any classical, phase, or borrowed-host dirt. A count-only
q-drop is not evidence of correctness.
