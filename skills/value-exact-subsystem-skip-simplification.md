# Skill: Value-Exact Subsystem-Skip Simplification (reclaim/extend BitWonka's TLM_*_SKIP_*)

**Technique class:** remove provably-dead or exact-zero-remainder sub-circuits
value-exactly — a per-subsystem peephole/template simplification of the reversible
(Toffoli) circuit. This is the lever that moved the ecdsa.fail frontier from
1,577,850,522 → **1,576,955,794** (BitWonka `6dafa07`, ~746 Toffoli at peak 1153)
and is the path to beat it further.

**Canonical paper:** Markov, **"Scalable Simplification of Reversible Circuits"**
(iwls03) — Toffoli-gate cancellation + structural simplification; ~10% of gates
cancel in random Toffoli circuits via template/peephole rules. Companion work:
Maslov/Soeken/Wille on reversible-circuit peephole + window optimization;
"Wire Recycling for Quantum Circuit Optimization" (PRA 94, 042337) → skill
`paper-scalable-memory-recycling`.

## Why this is the live lever (not the cascade-blocked peak cut)
Two agents proved any **peak** cut cascades (LIFO lane-reassignment rewrites
qubit-ids → reseeds Fiat-Shamir → wrong function; see `ecdsafail-findability-wall`).
But a subsystem-skip removal is **value-exact on data qubits**: it deletes ops
WITHOUT changing the allocation timeline → no lane-reassignment → no cascade →
the function is identical, only fewer Toffoli. So it shaves `avg_executed_Toffoli`
at constant peak 1153 → directly lowers the score. (This is the "pair-complete
simplification" lever from the findability-wall memory, executed at scale.)

## BitWonka's instance — the `TLM_*_SKIP_*` suite (public, commit 6dafa07)
BitWonka removed `DROP_DEAD_ROBUST`/`DROP_DEAD_ROBUST_SECOND` (the stale-`.idx`
load-bearing dead-gate drops — those dirty islands per findability-wall) and added
a coordinated set of env-gated value-exact per-subsystem skips. Each subsystem
contributes two skip *families*:
- **`STRUCTURAL_DEAD_*`** — a sub-operation (call / carry / cswap / shift) that is
  provably a no-op on all valid inputs (e.g. a carry into a known-zero bit, a cswap
  on equal operands, a shift of a saturated register). Removable value-exactly.
- **`EXACT_*REMAINDER` / `EXACT_BOUNDARY_ZERO`** — a remainder/boundary term that
  evaluates to exactly zero on the schedule-fitting inputs (e.g. `EXACT_FOLD_REMAINDER`,
  `EXACT_SHIFT_REMAINDER`, `EXACT_CIN_REMAINDER`, `EXACT_TOP29_REMAINDER`,
  `EXACT_BOUNDARY_ZERO`). Removable because the term is identically zero.

Concrete skips observed in the diff (group by subsystem):
- **FFG** (the +f fold, arith.rs): `SKIP_STRUCTURAL_DEAD_CALLS`, `SKIP_TOP_CARRY31/30`,
  `SKIP_EXACT_TOP29_REMAINDER`, `SKIP_INVERSE_MOD_SUB_TOP29`, `INVERSE_TOP29_MAX_CALL=180`.
- **CUCCARO** (cuccaro_carry adder): `SKIP_STRUCTURAL_DEAD_CALLS`.
- **COMPARE** (comparator): `SKIP_STRUCTURAL_DEAD_CALLS`, `SKIP_EXACT_REMAINDER`,
  `SKIP_EXACT_CIN_REMAINDER`.
- **GIDNEY** (gidney adder): `SKIP_STRUCTURAL_DEAD_CALLS`, `SKIP_EXACT_REMAINDER`,
  `SKIP_EXACT_ERASE_ALL_CCZ`, `SKIP_SMALL_RESIDUAL_DEAD`.
- **CONST_CHUNK** (constant chunked add): `SKIP_STRUCTURAL_DEAD_CALLS`, `SKIP_EXACT_REMAINDER`.
- **FUSED** (fused mul-add): `SKIP_STRUCTURAL_DEAD_CARRIES`, `SKIP_STRUCTURAL_DEAD_SHIFT0`,
  `SKIP_EXACT_FOLD_REMAINDER`, `SKIP_STRUCTURAL_DEAD_DIRTY_FOLD`,
  `SKIP_STRUCTURAL_DEAD_CLEAN_WINDOW`, `SKIP_EXACT_BOUNDARY_ZERO`, `CLEAN_FOLD_SKIP_TOP31`.
- **ADD_CONST**: `SKIP_STRUCTURAL_DEAD_CARRIES`.
- **GCD** (jump-GCD dialog): `SKIP_STRUCTURAL_DEAD_CSWAPS`, `SKIP_EXACT_FORWARD_CSWAPS`,
  `SKIP_STRUCTURAL_DEAD_SHIFTS`, `SKIP_EXACT_SHIFT_REMAINDER`, `SKIP_REVERSE_DIAGONAL_EDGE`.

## How to apply
1. **Reclaim (port):** the diff is public — clone `welttowelt/ecdsafail-challenge`,
   `4cd1b2f..6dafa07`, and port the `TLM_*_SKIP_*` env-gated hooks into the matching
   subsystem functions (arith.rs FFG/const_chunk, gcd.rs GCD, gidney.rs, fused.rs,
   comparator.rs, cuccaro). Each skip is a guarded early-return / op-omit at a
   specific callsite. Verify each is value-exact (eval graded, not 9024) — a skip
   that changes the allocation timeline WILL cascade; only pure op-omits are safe.
2. **Extend (beat BitWonka):** BitWonka's ~746 Toffoli at avg 1,367,698 is not the
   floor. Hunt NEW structural-dead/exact-remainder sites BitWonka missed: instrument
   each subsystem (`TRACE_TLM_PROFILE`/op-id trace) for sub-ops whose control is
   known-zero or whose target is recomputed-then-discarded. Each new value-exact
   skip shaves avg further. The `EXACT_*REMAINDER` family is the richest vein — any
   fold/shift/carry remainder that is identically zero on the schedule inputs is free.
3. **Gate (per repo discipline):** count_tof (avg down, peak still 1153) → eval
   (0/0/0 on the committed nonce reseeds; graded cls/pha = island-miss = scanner_deep
   re-hunts) → benchmark.sh. NEVER claim a skip as a beat without the official gate.
   A skip that isn't truly value-exact will show as a cascade (9024) or dirty the island.

## Mapping to the score
At peak 1153, score = round(avg) × 1153. BitWonka avg 1,367,698 → 1,576,955,794.
Beat gate: avg < 1,367,697.5 (rounds to ≤ 1,367,697). So even ONE more executed-Toffoli
shaved (value-exact) + a clean-island re-hunt on the new circuit = a beat
(1,367,697 × 1153 = 1,576,954,641). Margins are razor-thin now → extend the skip
suite for a defensible margin.

## Sources
- Markov, "Scalable Simplification of Reversible Circuits," IWLS 2003 — https://web.eecs.umich.edu/~imarkov/pubs/misc/iwls03-loco.pdf
- Maslov & Miller, "Comparison of the template-based techniques for reversible logic synthesis,"
  and the Soeken/Wille peephole+window optimization line.
- "Wire Recycling for Quantum Circuit Optimization," PRA 94, 042337 → skill `paper-scalable-memory-recycling`.
- BitWonka public commit 6dafa07 (the `TLM_*_SKIP_*` instance), diff `4cd1b2f..6dafa07`.
- Internal: [[ecdsafail-findability-wall]] (why peak cuts cascade but value-exact skips don't),
  `paper-schrottenloher-point-addition` (the route's arithmetic structure).
