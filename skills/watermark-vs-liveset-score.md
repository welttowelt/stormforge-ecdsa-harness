# Skill: Watermark-vs-Live-Set Score Diagnosis (the FIRST check before any qubit-width cut)

Use before investing in ANY qubit-width-cut candidate on a reversible/quantum circuit benchmark. Determines whether the
score tracks (a) live-set peak qubits, (b) an id-watermark max(qubit_id)+1, or (c) an emitted-instruction count. This
single 2-line check OVERRULES ~15 candidate techniques if the benchmark is watermark-scored (as ecdsa.fail is).

## The check (do this FIRST)

Grep the score writer back to its qubit source. On ecdsa.fail: `write_score` / `append_results_row`
(src/bin/eval_circuit.rs) → `analyze_ops` (src/circuit.rs:348-386) = **max(qubit_id)+1** (an ID WATERMARK), NOT
`circ.peak_qubits` (the live-set, which is only a TRACE_TLM_PROFILE diagnostic). Conclusion: the scored "peak qubits" is
the highest qubit ID ever referenced + 1, NOT the max simultaneous live set.

## Why this overrules most width-cut techniques

Under lane reuse (a LIFO free-list, as at mod.rs:340 / loan_zero_qubit), a freed qubit's id is RECYCLED to a low value,
so the watermark is bounded by the max simultaneous live set — UNTIL a later op re-references a high id. So:
- **Ghosting, per-carry MBU, spooky pebbling, oblivious carry runways, ancilla-free adders, conditionally-clean ancillae,
  laddered toggle detection, Wallace/Dadda trees, borrow-bit cycling, reversible-rewrite-rule bases** are ALL dead on a
  watermark-scored benchmark, regardless of how cleanly they free a qubit mid-circuit, because a later op referencing that
  id keeps the watermark pinned.
- The **only** surviving lever: eliminate or relocate the SINGLE highest-id allocation (make next_qubit cap one lower).

## The ONE surviving lever: free-list hit at the high-water alloc instant

If a provably-|0⟩ qubit is on the free list at the exact ops_idx where next_qubit would mint the high-water id (1152 on
ecdsa.fail), that allocation takes the free-list branch (reuses a low id) instead of minting → next_qubit caps at 1152 →
score = 1152 × avgT. With the BitWonka-parity avgT (1,367,697.510) → ~1,575,695,338 (~1.26M under BitWonka 1,576,955,794).

**Value-exactness:** a clean free-list handoff is NOT a dirty-borrow → it CANNOT reproduce the 9024cls/141pha/141anc
ancilla-garbage wall (that wall only arises from dirty-borrow inexact restores on wide suffixes). The freed qubit must be
provably |0⟩ (a resident reserve bit freed via zero_and_free after its owning op uncomputed it) — else anc!=0 fires (caught
by the cls/pha/anc differential test). The TLM_TARGET_FOLD_CALL_RESERVE_OVERRIDES machinery (mod.rs:2170) already exists to
free reserve bits at precise call sites; the novel move is to AIM it at the single ops_idx that mints the high-water id.

**Caveat:** the alloc-timeline change reseeds FS (the op stream's qubit-id assignment changes downstream) → the old clean
nonce becomes dirty → need a new clean-island hunt. But anc=0 (no garbage wall) → the island is findable (not structurally
dead, unlike the dirty-borrow routes).

## Test recipe

1. `TRACE_ALLOC_NEAR_PEAK=1150 TRACE_EACH_PEAK=1 build_circuit` → find the exact alloc_qubit call (caller file:line from
   the eprintln at mod.rs:309-319) that first pushes active_qubits to id==1152 (next_qubit becomes 1153). Confirm it is a
   FRESH MINT (free_qubits was empty at that instant — line 340 fell through to 343).
2. Aim a `TLM_TARGET_FOLD_CALL_RESERVE_OVERRIDES` free at that ops_idx (free a provably-|0⟩ resident reserve bit just
   before the high-water alloc).
3. count_tof → confirm PEAK_QUBITS=1152 (next_qubit caps). eval canary + random → require 0/0/0 (anc=0 = the freed bit
   was genuinely |0⟩). If anc!=0 → the bit wasn't |0⟩ → kill.
4. If 0/0/0 + peak 1152 → q1152 watermark cut. Hunt a clean nonce (reseed). Measure score.
