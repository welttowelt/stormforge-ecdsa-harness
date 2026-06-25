# Skill: Schrottenloher — Optimized secp256k1 Point-Addition Circuits (arXiv:2606.02235, Jun 2026)

**Paper:** André Schrottenloher, "Optimized Point Addition Circuits for Elliptic
Curve Discrete Logarithms," arXiv:2606.02235 (June 2026), Univ Rennes / Inria.
Open-source reference impl (Qarton): `gitlab.inria.fr/capsule/qarton-projects/ec-point-addition`.
Companion (the undisclosed Google circuit it reproduces): Babbush et al., arXiv:2603.28846.

**Why it matters for ecdsa.fail:** the benchmark IS reversible secp256k1 point-add
(score = Toffoli × peak_qubits). This paper gives a fully-detailed, **6.5–10 %
Toffoli reduction** for secp256k1 point-add vs the prior SOTA, with explicit,
reusable arithmetic tricks — several of which drop straight into the trailmix/
dialog-GCD route's `arith.rs` as value-exact (or controlled-approximate) cuts.
Use this to find avgT cuts on the q1153 circuit (a Toffoli cut + scanner_deep =
a real beat, dodging the qubit-cut findability wall).

---

## The cost breakdown (where the Toffoli goes) — Table 3 of the paper
For the space-optimized secp256k1 circuit:
- **In-place modular multiplier (+ inverse): 90 %** of all CCX.
  - Bézout reconstruction: 54 % ; GCD construction: 36 %.
- Modular squaring: 9 %.
- Sub-components: controlled-swap 19 %, **hybrid adder 22 %, controlled modular
  adder (+inverse) 39 %, modular double (+inverse) 8 %**, Gidney constant adder 15 %.
- For a GENERIC prime (non-pseudo-Mersenne) the constant adder balloons to **34 %**
  and modular double to 24 % — i.e. the pseudo-Mersenne structure is worth ~19 %
  of total Toffoli on its own. **This is the single biggest lever.**

> Implication for ecdsa.fail: the **controlled modular add/sub** and **constant
> adder** dominate. If the trailmix route does full-width `q`-adds/subs in
> `controlled_mod_add` / `controlled_mod_sub`, replacing them with the
> pseudo-Mersenne `f`-into-LSBs form is the highest-impact cut available.

---

## The techniques (ranked by transferability to ecdsa.fail's arith.rs)

### 1. Pseudo-Mersenne controlled modular addition  ★ HIGHEST-VALUE, directly testable
secp256k1 prime `q = 2^256 − f`, `f = 4294968273` (~32 bits, small). A controlled
mod-add `|x,y> → |x, y+x mod q>` can drop the full 256-bit subtract/add of `q` to:
a controlled non-modular add, then **if the MSB overflowed, add `f` into the LSBs
of y** (carry only propagates ~32+ bits), then erase the overflow bit by an MSB
comparison `y < x` (Algorithms 10/11). Because `f` is small, the constant add
touches only the low bits → roughly a **256-bit → ~40-bit constant add**, i.e. an
~6× cut on each constant-add step, and constant-adds are 15–34 % of total Toffoli.
- Two variants: Algorithm 10 (does NOT handle the rare `x+y = q`) and Algorithm 11
  (handles it via all-MSBs-1 / all-MSBs-0 checks). Use 10 inside the hot Bézout
  loop (random inputs, `x+y=q` negligible), 11 for the first c_iter·√n empty iters.
- **ecdsa.fail target:** `controlled_mod_add_k` / `controlled_mod_sub_vented` and
  the mod-reduce tail in `arith.rs`. If they subtract/add the full prime, port Alg 10.
- GATE: count_tof (CCX down) → eval (value-exact for Alg 10 on random inputs; the
  `x+y=q` edge only matters in the empty Bézout iters). Toy-proof the LSB-carry
  range vs f first.

### 2. Pseudo-Mersenne modular doubling
`|x> → |2x mod q>`: shift, then **if MSB set, erase MSB + add `f` into LSBs**,
uncompute the MSB via `cx(x[0], anc)` (Algorithm 7). Reduces doubling to ~one
small constant add — cuts modular-double from 24 % (generic) to 8 % (secp256k1).
- **ecdsa.fail target:** any `mod_double` / `shift_mod` in arith.rs.

### 3. Approximate MSB-only comparisons
Every comparison (in the GCD step and inside mod-add) is done on **the top 40–50
MSBs only**, not all 256 bits. This is the source of the circuit's small failure
probability (≤2^−13.3 on 10 000 random inputs) but a large Toffoli saving. The
comparison bit is then erased by a complementary MSB comparison.
- **ecdsa.fail target:** `compare_geq_*` / `lt_uint` calls. If the route does
  exact 256-bit compares, MSB-truncated (with `COMPARE_BITS` / `APPLY_CLEAN_COMPARE_BITS`
  already in the trailmix env set) is the knob — but check the committed config
  already tunes this (Vector's dump showed compare_bits=57). Pushing lower trades
  success-prob for Toffoli.

### 4. Strategic adder choice by ancilla availability (CDKM vs Gidney vs hybrid)
- **CDKM adder** (Cuccarro-Draper-Kutin-Moulton): 2n Toffoli for n-bit add, **0
  ancilla**; controlled add 3n Toffoli.
- **Gidney adder** ("Halving the cost of quantum addition", Quantum 2018): n
  Toffoli for n-bit add but needs ~n ancilla (measurement-based AND-uncompute);
  controlled add 2n Toffoli.
- **Rule:** use Gidney where ancillas are free (e.g. during the GCD step, ~n
  ancillas available), CDKM where they're not (Bézout reconstruction). The paper
  uses a **hybrid** that uses exactly the available ancilla count.
- **ecdsa.fail target:** the fold/register adders in `arith.rs`
  (`add_f_window_hybrid`, `controlled_clean_add_threaded`). The headroom-driven g
  schedule already picks clean-prefix vs dirty-suffix by ancilla — this is the same
  idea. A value-exact CDKM↔Gidney swap at a specific callsite (where ancilla is
  provably free) is a clean Toffoli cut without touching peak.

### 5. Dialog / EEA-split in-place modular multiplication (the 90 % block)
From Khattar et al. (arXiv:2510.10967): split the Extended Euclidean Algorithm
into (a) a **Euclidean step** that emits a garbage bit-vector `g` recording its
choices (div-by-2, swap, subtract), and (b) a **Bézout reconstruction** that
replays `g` onto `(r,s)`. Starting `(r,s)=(y,0)` yields `(0, y·x mod q)` — i.e.
**inversion + in-place multiply fused**, saving several modular multiplications.
- Garbage fits in **2.12 n + O(√n)** qubits via register sharing (the cleared
  high bits of shrinking (u,v) host the garbage). With a **3-iter→5-bit
  compression** gadget (5 Toffoli, Fig 1) the garbage register is fixed-size at
  ~2.355 n.
- **ecdsa.fail target:** this IS the trailmix/jump-GCD structure
  (`trailmix_ludicrous/gcd.rs` already does a Schrottenloher-style jump-GCD).
  The transferable pieces: the garbage-compression gadget (3 pairs → 5 bits) and
  register-sharing of cleared GCD bits — both are peak/qubit cuts on the GCD tape.
  Note: ecdsa.fail's route is already in this family, so the win is in the
  *details* (compression gadget, exact ancilla budgeting), not the high-level split.

### 6. Gidney constant adder with dirty ancillas (arXiv:2507.23079)
n-bit constant addition in **3n Toffoli using dirty (borrowed) ancillas**, constant
workspace. This is the adder used for the `q`/`f` constant adds inside the Bézout
reconstruction (where no clean ancilla exists). Reducing `q`→`f` (technique 1)
multiplies this gain.
- **ecdsa.fail target:** `controlled_mod_add_k` (add-by-constant) and the mod-reduce
  constant subtract. See skill `paper-gidney-constant-workspace-adder`.

---

## How to apply to ecdsa.fail (disciplined)
1. **Front-load technique 1** (pseudo-Mersenne controlled mod-add): biggest lever
   (15–34 % of Toffoli), most localised change, value-exact on random inputs.
   Toy-proof the `f`-LSB-carry range, then count_tof on `controlled_mod_add_k` /
   `controlled_mod_sub_vented` in an isolated 4cd1b2f tree, then eval.
2. Technique 2 (mod-double) second — small but clean.
3. Technique 4 (CDKM↔Gidney at a provably-ancilla-free callsite) — value-exact,
   peak-neutral Toffoli cut.
4. Technique 3 (MSB compare) only if the committed compare_bits isn't already at
   floor — it's a success-prob trade.
5. Every change reseeds Fiat-Shamir → needs scanner_deep to re-hunt a clean nonce
   (Codex owns that). So: land the value-exact Toffoli cut, then hand the new
   op-stream to scanner_deep.

## Gate (per repo discipline)
count_tof first (CCX/ops down, peak ≤ 1153) → eval (0/0/0 on the committed nonce
will go stale after reseed; anc=0 + construction proof = value-exact, graded
cls/pha = island-gated for scanner_deep). Never claim a beat without scanner_deep
finding a clean nonce + official `benchmark.sh`. Do NOT claim a paper resource
estimate as an ecdsa.fail improvement until the local harness validates the actual
op stream.

## Sources
- arXiv:2606.02235 (this paper) — https://arxiv.org/abs/2606.02235
- Babbush et al. arXiv:2603.28846 (the reproduced Google circuit)
- Gidney, "A classical-quantum adder with constant workspace and linear gates,"
  arXiv:2507.23079 (2025) → skill `paper-gidney-constant-workspace-adder`
- Gidney, "Halving the cost of quantum addition," Quantum 2:74 (2018)
- Häner–Roetteler et al., improved ECDLP circuits (2020) → skill `paper-haner-ecdlp-circuits`
- Khattar et al., arXiv:2510.10967 (dialog/EEA-split)
- Roetteler–Naehrig–Svore–Lauter (2017), the mod-add/mod-double starting circuits
- Chevignard–Fouque–Schrottenloher, EUROCRYPT 2026 (eprint 2026/280) — related
  qubit-reduction for ECDLP
