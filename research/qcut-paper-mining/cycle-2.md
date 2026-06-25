# qcut-paper-mining — Cycle 2 (2026-06-25)

Workflow `wwtgwmuv4` (5 DEEPER clusters: Gidney-beyond-Fig5, Montgomery/Barrett modmul,
scalar-mult window, Kaliski GCD/inversion, width lower-bounds). 29 findings -> 28 closed -> 1 survivor.

## The one survivor
Conditionally-clean borrowed ancilla for the FIRST (j=0) carry only (Khattar-Gidney, Quantum 9:1752 /
arXiv:2407.17966). Ceiling 1152 (one carry; cascaded cuts blocked by live cout_{j-1} carry-in read).
Value-exact by construction (unitary-invertible -> anc==0). Blockers: (i) dead-resident-bit precondition
unverified; (ii) builder lacks unknown-state-borrow op (only loan_zero_qubit, assumes |0>). Caveat:
q1152 beats unfindable on live frontier (cls floor >18).

## The durable structural insights (-> skill q1153-peak-structural-map.md)
1. PEAK = 4 inter-chunk boundary cout ancillae of a graduated [4,3,2,1] staircase, NOT a ripple. Each
   reverse-erase reads carries[j-1] as LIVE carry-in. Per-adder/ripple-elimination tricks DON'T apply.
2. ANCELLA-GARBAGE KILL-TEST: 9024cls/141pha/141anc nonce-independent = inexact wide-suffix dirty-borrow
   restore (palindrome violation). Reproduced by dirty-suffix, Gidney-Fig5 port, g-reduction, spooky,
   HRS17, Zhang-Cho-Lee-Seo. Differentiator: unitary-invertible restore (safe) vs inexact (this wall).
3. MBU ALREADY BAKED IN for internal carries; the PEAK boundary carries are NON-MBU-able (each is the
   coherent cin of the next forward chunk — forward data-dependency wall, more fundamental than
   reverse-erase liveness). Re-proposing MBU on them duplicates shipped work on wrong carries.
4. TOFFOLI-AXIS vs WIDTH-AXIS confusion = #1 finding-bug source. Gidney-2018/Luongo-Miti/Remaud-Vandaele
   cut TOFFOLI, not width; on n<=4 suffix they blow up Toffoli -> score-neutral/negative.
5. DEAD-BIT-BORROW PRECONDITION: fold plateau has codec-tape/divstep-flags/shrunk-GCD-u all LIVE;
   divstep symbol bits dropped pre-apply (not borrowable). Liveness scan mandatory before any borrow.

## Implication for the Gidney Fig-5 port (a36f4c99)
Insight 3 says the peak boundary carries are NON-MBU-able by a FORWARD data-dependency — so even if the
stale-index falsifier (Codex) clears the dirt, the Gidney Fig-5 port may be structurally blocked on the
boundary carries. The conditionally-clean cascade (ada1c7ad) remains the safer bet (unitary-invertible).
