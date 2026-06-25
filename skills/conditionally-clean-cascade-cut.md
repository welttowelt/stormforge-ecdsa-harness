# Skill: Conditionally-Clean Cascade Cut (exact ancilla cut that dodges the garbage wall)

Use when cutting the PEAK qubit width of a reversible modular-arithmetic / EC point-add /
Shor-style circuit, where the carries you want to free are restored by a reverse pass and
every dirty-borrow attempt has hit an ancilla-garbage wall.

## Goal

Cut clean-carry ancilla via a **conditionally-clean cascade** (restore is a conditionally-clean
dagger — *exact by construction*) instead of dirty-borrow (whose restore is inexact on a wide
suffix). This is the one structural route that **cannot** reproduce the ancilla-garbage wall.

## The diagnostic that makes this worth knowing

The recurring "ancilla-garbage wall" (e.g. `9024 classical / 141 phase / 141 ancilla`, identical
across ALL 9024 Fiat-Shamir nonces incl. random — nonce-INDEPENDENT) is **not probabilistic and
not a numerical bug**. It is a **structural palindrome violation**: it fires whenever a dirty or
conditionally-clean restore must run *while a control it is conditioned on is simultaneously a
LIVE quantum carry-in being read mid-restore*. Signature: `anc > 0 AND pha > 0` that is bit-for-bit
identical across every nonce. If you see nonce-independent anc/pha garbage, you have a palindrome
violation — stop tuning the dirty restore; switch to a route whose restore is exact by construction.

## Steps

1. Confirm the peak is a **clean-carry chain** with a reverse erase that reads `carry_{j-1}` as a
   LIVE quantum carry-in (the palindrome-violation setup). Measure: nonce-independent
   `anc>0 AND pha>0` after the candidate cut.
2. Port the forward carry stack to the **Nie-Zi-Sun / Khattar-Gidney single-clean-ancilla
   conditionally-clean cascade**: each stage borrows conditionally-clean workspace from a resident
   qubit **independent of `carry_{j-1}`** (NEVER the live carry-in).
3. The restore is a conditionally-clean dagger → exact by construction. Gate: on a 9024-shot
   random-nonce run require `cls==0 AND pha==0 AND anc==0`. **If `cls>0` or `anc>0`, kill
   immediately** — that would mean the "exact" restore leaked onto the wide suffix, contradicting
   the conditionally-clean guarantee, so the failure is diagnostic (a control-dependency clash),
   not ambiguous.
4. Realistic yield: a 4-carry suffix collapses to **2–3 carries (peak −1 to −2)**. Claiming peak −3
   requires a genuine spare resident `|0>` at the peak entry, verified absent (scratch tmp is full
   field-width, not `|0>`; GCD bits are allocating, not donatable).
5. Confirm the Toffoli penalty (~`2n−3` per cascade vs `~n` ripple) does NOT eat the qubit win:
   `round(avg_Toffoli) × peak` strictly below the prior score.

## Output

A value-exact peak cut (e.g. 1153 → 1151) with `0/0/0` on 9024 shots, plus the carry-independence
proof for the borrowed workspace. If the cut holds `0/0/0` but the control-dependency restriction
bites (no independent resident to borrow), report a STRUCTURAL wall, not a borrow-vs-allocate gap.

## Credit

Nie, Zi, Sun — "Quantum circuit for multi-qubit Toffoli gate with optimal resource",
arXiv:2402.05053 (2024). Khattar & Gidney — "Rise of conditionally clean ancillae for optimizing
quantum circuits", arXiv:2407.17966 / Quantum 9:1752 (2025). Mined by the qcut-paper-mining
workflow (cycle 1) for the ecdsa.fail secp256k1 point-add. Do not imply copied code.
