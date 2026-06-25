# Skill: Reversible-Circuit Edit-Integration Safety (the "isolation-clean, full-circuit-dirty" desync)

Use when a circuit PRIMITIVE (a borrowed-ancilla adder, a measurement-vented uncompute, a new gate
or vent) tests VALUE-EXACT in isolation (0/0/0 on selftests) but the FULL circuit emits
**nonce-INDEPENDENT** dirt (classical / phase / ancilla identical across every Fiat-Shamir shot incl.
random) after you wire it in. This is the "integration desync" — and it is almost never the primitive's
math; it is a stream-edit / allocation interaction.

## Goal

Stop blaming the primitive. Diagnose and fix the two dominant integration-desync causes — **stale
stream-specific optimizations** and **free-pool ID-reuse aliasing** — with a 3-step falsifier ladder,
before any "deep math" investigation.

## The diagnostic signature (tells you this is the right skill)

After wiring in an edit, full-circuit eval gives `cls>0 AND pha>0 AND anc>0` that is **bit-for-bit
identical across ALL nonces including random** (nonce-INDEPENDENT). Nonce-independence = the failure is
structural/deterministic, not input-dependent → it is a construction/integration artifact, NOT a
correctness bug in the primitive's truth table. (If the dirt were input-dependent, you'd have a math bug.
It isn't, so you don't.) Bonus tell: a sub-count (e.g. `141 anc`) equals the number of new vents/allocs
you added → those allocs/vents are the leak source.

## The 3-step falsifier ladder (cheapest first)

1. **Stale stream-specific optimization (run with it DISABLED).** Any precomputed op-index optimization
   (dead-gate / CCX-CZ cancellation / template / drop-dead-robust `.idx`) was built for the BASELINE op
   stream. Your edit changed the stream (new gates/vents), so the baseline index now silently drops the
   WRONG ops → exactly nonce-independent dirt. Falsifier: re-run with the optimization DISABLED
   (e.g. `DROP_DEAD_ROBUST_DISABLE=1`), even 1-shot. Outcomes:
   - dirt CLEARS or changes → stale-index contamination. **Regenerate the index for the edited stream**
     before any further diagnosis. (Most common; cheapest fix.)
   - dirt IDENTICAL with optimization off → not the index; go to step 2.
   - (peak/ops too high with drops off is fine — diagnostic only.)
   Also state whether your reported op-count was PRE- or POST-optimization; if post-, rerun raw.

2. **Free-pool ID-reuse aliasing (transient allocs must avoid the free pool).** The full circuit recycles
   freed qubit IDs via a free pool. Your primitive's TRANSIENT allocations (dummy `|0>`, scratch,
   boundary carry-out) pulled from that pool can grab an ID that was just freed but is still LOGICALLY
   ENTANGLED with the in-flight computation → the transient aliases a live qubit → nonce-independent
   phase/ancilla leak at the vent/restore. Falsifier: allocate ALL transient borrowed ancilla at
   FRESH HIGH IDs (a dedicated range above the circuit's current max, never from the free pool). If the
   dirt clears → aliasing was the cause.

3. **Measurement-vent discharge target (palindrome violation).** A measurement-vent discharges
   `Z^{carry}` onto a target qubit. If that target is entangled with a control that is a LIVE carry-in
   read mid-vent (a control the restore is conditioned on), the discharge leaks. Fix: discharge onto a
   provably-unentangled fresh target, OR defer the vent until AFTER the conditioned control is restored,
   OR replace an assumed-`|0>` `zero_and_free` with a real measurement-vent (`Hmr`) so phase can't leak.

If all three are ruled out, THEN emit the first-divergence shot + first mismatching output bit + first
nonzero ancilla bit to localize a genuine schedule/shift bug.

## Output

For a wired-in primitive: a clean/disambiguated full-circuit result, plus which of the 3 causes applied
and the one-line fix. The durable rules to bake into any reversible-circuit build:
- **Regenerate every stream-specific optimization after any op-stream edit** (or gate it off for the
  diagnostic). Never apply a baseline dead-drop/peephole index to a modified stream.
- **Transient borrowed ancilla never come from the recycled free pool** — fresh high IDs, or
  measurement-vented.
- **Nonce-independent `anc>0 ∧ pha>0` after an edit = integration desync, not a math bug** — run the
  ladder before touching the primitive.

## Credit

Synthesized from the live ecdsa.fail secp256k1 Gidney-Fig-5 integration investigation (2026-06-25),
including Codex-Vector's stale-dead-drop falsifier and the free-pool-aliasing diagnosis. Related:
Gidney, "A Classical-Quantum Adder with Constant Workspace and Linear Gates," arXiv:2507.23079 (2025);
Khattar & Gidney, "Rise of conditionally clean ancillae," arXiv:2407.17966 (2025). Companion to
`conditionally-clean-cascade-cut.md`. To be extended with allocation/reuse-literature citations.
