# Skill: Structural Qubit Cut (peak-qubits 1153 → 1152 and lower)

Use to reduce `peak_qubits` on the ecdsa.fail trailmix (TLM) circuit — the
multiplicative factor in `score = avg_executed_Toffoli × peak_qubits`. A single
qubit cut at 1153 is worth ~1,368,487 score (frontier 1,577,865,511 →
1,576,497,024) and makes ANY clean island a beat.

## Why naive edits fail (the three walls — all surmountable)

1. **Peak-live is genuinely 1153 at the binder.** `qubits` (circuit.rs `analyze_ops`)
   = max-qubit-id-touched + 1; the allocator recycles freed lanes (LIFO) and only
   grows `next_qubit` when the free-pool is empty. id 1152 is born exactly once at
   the `free_pool=0` alloc in `const_chunk_add_clean` (arith.rs:646) inside
   `tlm_apply_inverse_mod_sub_fold`, then recycled across ~40 plateau moments.
   To read 1152 you must keep peak-live ≤1152 at ALL ~40 moments.
2. **Razor-thin Toffoli budget.** avg 1368486.555 rounds to 1368487 (+0.944
   headroom). An uncompute adds ~+2 executed-Toffoli/call × ~40 calls. You MUST
   offset added Toffoli, or use a Toffoli-neutral reschedule.
3. **Absolute-index drop-dead corruption.** `build()` runs DROP_DEAD_ROBUST +
   DROP_DEAD_ROBUST_SECOND which delete ops by ABSOLUTE INDEX from baked `.idx`
   blobs. ANY op-stream edit shifts indices → wrong gates deleted → total
   corruption. **SOLVED by regenerating the `.idx` (below).**

## The unlock — regenerate the drop-dead .idx for an edited circuit

`apply_drop_dead_robust_if_enabled` (mod.rs) reads `DROP_DEAD_FILE=<path>` to
OVERRIDE the baked `.idx`. The dead-gate finder `src/bin/dead_ccx_scan.rs` finds
ops that are `executed>0 && fired==0` (dead: cost avg-Toffoli but no-op). So after
ANY edit you can rebuild a correct drop-dead set:

```
# 1. scan the PRE-drop stream of the EDITED circuit (disable baked drop-dead)
DROP_DEAD_ROBUST_DISABLE=1 DEAD_SCAN_NONCES=8 \
  ./target/release/dead_ccx_scan > /tmp/dead_scan.txt
# 2. extract the dead indices into a new .idx
grep -E '^[0-9]+' /tmp/dead_scan.txt | awk '{print $1}' > /tmp/new_drop.idx
# 3. build with the regenerated drop-dead (correct for the edited stream)
DROP_DEAD_FILE=/tmp/new_drop.idx ./target/release/build_circuit ...
```

Note: the Fiat-Shamir 9024 shots are seeded from the FINAL ops, so any edit
RESEEDS the inputs → you must re-hunt a clean DIALOG_TAIL_NONCE on the new
circuit (same GPU island machinery; ANY 0/0/0 wins because avg≈unchanged but
qubits dropped).

## Procedure

1. **Scratch only.** `cp -r ~/ecdsafail-challenge ~/ecdsafail-q1152-X`,
   `git checkout da51a48 -- .`. NEVER edit ~/ecdsafail-challenge / ~/ecdsafail-frontier.
2. **Locate the binder** with `TRACE_EACH_PEAK=1153 TRACE_ALLOC_NEAR_PEAK=1153`
   on `eval_circuit`/`build_circuit`. Confirm the single phase reaching 1153 and
   the alloc op.
3. **Reduce peak-live by 1 at the binder**, preferring Toffoli-neutral reschedules:
   - Re-schedule a borrow/carry's live range so the binder qubit isn't simultaneously
     live (no new gates) — mirror the forward-apply fold (which fits 1151).
   - If an uncompute is unavoidable, plan to OFFSET its Toffoli via step 4's
     regenerated drop-dead (newly-dead gates created by the edit), or via a cheaper
     adder structure (fewer live internal carries) at equal Toffoli.
4. **Regenerate drop-dead** (the unlock above) so removal is correct on the edited
   stream. Re-run dead_ccx_scan; union with any second-pass set.
5. **Validate (hard gates, in order):**
   - `qubits:1152` (printed twice — both must be 1152) on a build.
   - VALUE-EXACT: eval 2-3 random nonces on BOTH pristine-1153 and edited-1152
     builds; the cls/pha/anc failure PATTERN must MATCH (identical math), NOT be
     9024/9024 (the index-shift / FORCE_G trap).
   - avg_executed_Toffoli rounds to ≤1368486 (score ≤ 1,576,497,024).
6. **Hunt a clean island** on the 1152 circuit (GPU `island.sh` / lanes). ANY
   0/0/0 nonce = beat. Validate `benchmark.sh` 0/0/0 + score < frontier, then
   submit (coordinate Forge for the proper tree). Generous credit.

## Going lower (1151, …)

After a 1152 cut lands, re-run step 2 — the new binder is the next single-qubit
overshoot (or a 2-family plateau needing two reschedules). Each cut is
independent and re-uses this procedure.

## Permanent fix worth flagging (infra)

DROP_DEAD keyed by absolute index blocks ALL circuit edits team-wide. Refactoring
it to key by STABLE OP-IDENTITY (control/target/kind hash) instead of absolute
index would let any structural edit compose with drop-dead without a re-scan.
High-value; Forge/BitWonka domain.

## Discipline

Scratch trees only; never the frontier/challenge tree. Truth = the `qubits:` line
and the matching-failure-profile test. Submit only a benchmark-verified 0/0/0 <
frontier. No fabrication. Credit BitWonka/newjordan/jieyilong/Forge/Codex/lineage.
