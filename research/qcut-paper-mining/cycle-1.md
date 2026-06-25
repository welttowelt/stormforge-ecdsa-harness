# qcut-paper-mining — Cycle 1 (2026-06-25)

Workflow `wdlqych4x` (5 parallel technique-family sweeps → adversarial verify → synthesize).
Target: ecdsa.fail secp256k1 reversible EC point-add, peak 1153 (fold-suffix graduated
clean-carries). 29 raw findings → **27 closed (not transferable) → 2 promising**.

## Top candidates (adversarially verified)

### Rank 1 — Conditionally-clean cascade (LOW value-exactness risk) → peak 1151
- **Nie-Zi-Sun** "Quantum circuit for multi-qubit Toffoli with optimal resource" arXiv:2402.05053 (2024);
  tightened by **Khattar & Gidney** "Rise of conditionally clean ancillae" arXiv:2407.17966 / Quantum 9:1752 (2025).
- Single-clean-ancilla conditionally-clean cascade for the suffix's carry chain. Restore is a
  **conditionally-clean dagger = exact by construction** → structurally CANNOT hit the
  ancilla-garbage wall (9024/141/141) that killed g-reduction / dirty-suffix / Gidney-Fig5-dirty.
- Realistic yield: 4 carries → 2–3, i.e. **peak 1151** (1150 needs a spare resident |0>, absent at fold entry).
- Test: port the forward carry stack (arith.rs:826-838) to the cascade; borrow workspace ONLY from a
  resident qubit INDEPENDENT of `carry_{j-1}` (not the live carry-in). Kill if cls>0 or anc>0
  (diagnostic — contradicts the exact-restore guarantee). Confirm `round(avg_T) × peak <` prior score.
- **Do this FIRST** — lowest risk on the killer axis, cheapest to pilot. → banked as skill
  `skills/conditionally-clean-cascade-cut.md`; pilot agent launched.

### Rank 2 — Gidney Fig-2 vented streaming adder (MEDIUM risk) → peak 1152
- **Gidney** "A Classical-Quantum Adder with Constant Workspace and Linear Gates" arXiv:2507.23079
  (2025), Sec 2.2 / Fig 2 — **2 CLEAN / 0 DIRTY** (NOT Fig 5, already tried; NOT Fig 4).
- X-basis measurement of Z-redundant carries → carry ancillae CEASE TO EXIST; no dirty-restore step
  at all. Distinct from the Fig-5 dirty-borrow port (which is one carry_h-discharge fix from value-exact).
- Risk: the mod-SUB fold conditionally subtracts p, toggling x'_high AFTER low carries vented →
  `carry(~target')` at fixup differs from vent → phase garbage (141-pha). Sharp falsifier:
  re-derive carry(~target',d,c0) at fixup time, compare bit-for-bit to vented carries.
- Gate strictly on pha==0 (GATE 1 bare add, GATE 2 mod-sub fold, GATE 3 nonce-independent).

## Skill-worthy insight (durable, transferable)

The **ancilla-garbage wall is a structural palindrome violation, not a probabilistic/numerical
artifact.** It fires whenever a dirty/conditionally-clean restore must run while a control it is
conditioned on is simultaneously a LIVE quantum carry-in read mid-restore. Diagnostic signature:
`anc>0 AND pha>0` identical across ALL 9024 nonces (nonce-INDEPENDENT, not input-dependent). If you
see that, stop tuning the dirty restore — it is structurally dead; switch to an exact-by-construction
restore (conditionally-clean cascade / measurement-vent). → encoded in the skill above.

## Closed avenues (27, do-not-re-walk)
Full per-finding closure reasons live in the workflow transcript. Summary of families closed:
dirty-borrow variants whose restore is inexact on the wide suffix; techniques needing clean ancilla
absent at the fold entry; Toffoli-axis-only techniques (not peak); techniques superseded by
constprop/drop-dead already in the build. Notable closed: several "borrow the live carry-in"
constructions (palindrome violation), and width claims depending on a spare resident |0> (absent).

## Next
- Rank-1 conditionally-clean cascade pilot (background agent) → value-exact q1151?
- Gidney Fig-5 port (separate agent) → value-exact q1152 via the carry_h-discharge fix.
- Cycle 2 (hourly cron 53da4644): deeper Gidney + Schrottenloher modmul width + reversible
  Montgomery/Barrett + Kaliski GCD width + width lower-bound theory.
