# Skill: Schrottenloher — Optimized secp256k1 Point-Addition Circuits (arXiv:2606.02235, Jun 2026)

**Paper:** André Schrottenloher, "Optimized Point Addition Circuits for Elliptic Curve
Discrete Logarithms," arXiv:2606.02235 (June 2026), Univ Rennes / Inria.
Open-source reference impl (Qarton): `gitlab.inria.fr/capsule/qarton-projects/ec-point-addition`.
Companion (the undisclosed Google circuit it reproduces): Babbush et al., arXiv:2603.28846.

## ⚠ STATUS (verified against the live trailmix tree @4cd1b2f, 2026-06-25)
**The paper's headline techniques are ALREADY IMPLEMENTED in our trailmix route** — the
ecdsa.fail frontier circuit IS a fully-realized Schrottenloher-class circuit. This skill is
therefore **confirmatory + diagnostic**, not a source of easy unbuilt cuts. Use it to (a) map
paper ideas to our code so future edits stay within the design, and (b) drive the cost-table
diagnostic below to find where any further Toffoli cut must come from. **Do not re-spend effort
"porting" Algorithm 10 / 7 / the garbage gadget — they are already in arith.rs / gcd.rs.**

### Evidence (paper technique → already in our code)
- **Alg 10 pseudo-Mersenne controlled mod-add** → `controlled_mod_add_k` (arith.rs:1214):
  `F_SECP256K1 = (1<<32)+977 = 4294968273` (paper's exact f); step 2 `add_f_window(&anc, y, LSBS,
  &f_bytes, …)` is the gated +f-into-LSBs reduction ("carry beyond LSBS dropped"); step 3
  `controlled_lt_msbs_conditional` erases the overflow anc over the top `MSBS=PAD=19` bits.
  `mod_add` / `mod_sub` / `mod_sub_vented` / `mod_add_lowpeak` are the uncontrolled / vented
  siblings — all pseudo-Mersenne. The authors literally comment "pseudo-Mersenne modular subtraction."
- **Alg 7 pseudo-Mersenne mod-double** → the doubling folds use the same `add_f_window`/`sub_f_window`
  gated +f/−f tail.
- **MSB-only approximate compare (§4)** → `controlled_lt_msbs_conditional` truncated to `MSBS=PAD=19`
  (more aggressive than the paper's 40–50 bits — `PAD` is the ludicrous success-prob knob).
- **CDKM-vs-Gidney-by-ancilla (§4 "Trade-offs")** → `add_f_window_hybrid` / `controlled_hybrid_add_cout_refs`:
  clean-prefix carries + graduated borrowed-dirty suffix, headroom-driven `g` schedule.
- **Dialog/EEA-split + garbage compression (§3, Fig 1)** → `gcd.rs` jump-GCD records the dialog
  `(subtracted, swap, s_2)` onto a tape compressed **inline per codec window** (`all-triple codec`,
  `dialog_tape_qubits`=603 for len-258) — a generalization of the paper's 3-iter→5-bit gadget,
  *more* compressed than the paper.

---

## The cost breakdown (where the Toffoli goes) — Table 3 of the paper
For the space-optimized secp256k1 circuit:
- **In-place modular multiplier (+ inverse): 90 %** of all CCX (Bézout 54 %, GCD 36 %).
- Modular squaring: 9 %.
- Sub-components: controlled-swap 19 %, hybrid adder 22 %, **controlled modular adder (+inverse)
  39 %**, modular double (+inverse) 8 %, Gidney constant adder 15 %.
- For a GENERIC prime the constant adder balloons to 34 % and mod-double to 24 % — so the
  pseudo-Mersenne structure is worth ~19 % on its own (already captured in our route).

> **Diagnostic use:** run `TRACE_TLM_PROFILE=1 build_circuit` on our tree and compare the per-phase
> Toffoli proportions to Table 3. If our controlled-mod-add share is ≫39 % or our constant-adder
> share ≫15 %, THAT is where a further cut pays off (and where the paper's micro-choices — e.g.
> the pure 3n-dirty Gidney constant adder [8] vs our graduated suffix — are worth diffing).
> Proportions matching Table 3 = our route is at the paper's frontier; only second-order grind
> or a non-paper structural cut (see [[ecdsafail-findability-wall]]) remains.

---

## Genuinely-remaining (second-order) opportunities from the paper
These are micro-optimizations the team is already grinding; list for completeness, NOT easy wins:
1. **Constant-add cost parity.** The Bézout reconstruction has no clean ancillas → the paper uses
   the pure Gidney dirty-ancilla constant adder (3n Toffoli, arXiv:2507.23079). Our `add_f_window`
   uses a graduated chunked clean-prefix + borrowed-dirty suffix. Audit whether any callsite pays
   MORE than 3n for the +f/−f and could drop to the pure dirty form. (Footprint-stable → avgT cut,
   scanner_deep-huntable; but small.)
2. **PAD floor.** `MSBS=PAD=19` is already far below the paper's 40–50. Pushing lower trades
   success-prob for Toffoli — only if the island hunt has slack.
3. **mod_add_exact on a hot path?** `mod_add_exact` (arith.rs:1316) runs the full-width n-bit
   compare (exact) for the `+3*ox` constant step. If any caller feeds it random (not fixed-constant)
   inputs, demoting to the truncated `mod_add` saves ~237 CCX/call. Verify callers first.

None of these dodge the findability wall on their own; each is an avgT shave for scanner_deep.

## Gate (per repo discipline)
count_tof first (CCX/ops down, peak ≤ 1153) → eval. Every change reseeds Fiat-Shamir → needs
scanner_deep (Codex-owned) to re-hunt a clean nonce. Never claim a beat without scanner_deep
finding a clean nonce + official `benchmark.sh`. NEVER claim a paper resource estimate — or a
paper technique — as a new ecdsa.fail improvement until the local harness confirms it is not
already realized (this skill exists because that check just caught technique #1 already in arith.rs).

## Sources
- arXiv:2606.02235 (this paper) — https://arxiv.org/abs/2606.02235
- Babbush et al. arXiv:2603.28846 (the reproduced Google circuit)
- Gidney, "A classical-quantum adder with constant workspace and linear gates," arXiv:2507.23079 (2025)
- Gidney, "Halving the cost of quantum addition," Quantum 2:74 (2018)
- Häner–Roetteler et al., improved ECDLP circuits (2020) → skill `paper-haner-ecdlp-circuits`
- Khattar et al., arXiv:2510.10967 (dialog/EEA-split)
- Roetteler–Naehrig–Svore–Lauter (2017), the mod-add/mod-double starting circuits
- Chevignard–Fouque–Schrottenloher, EUROCRYPT 2026 (eprint 2026/280) — qubit-reduction for ECDLP
