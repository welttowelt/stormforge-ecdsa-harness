# Bluesky / Redsky Audit - FFG Pair Proof Gate - 2026-06-28

## Frontier Snapshot

- Public frontier at mailbox check: source d44cad3, score 1571592960,
  q1152 / avg Toffoli 1364230.
- Active weakness: FFG suffix-carry one-call toy packets can look promising
  even when calls 178,180,181 are not pair-complete, route compare is dirty or
  shallow, and value/restore/phase proof is incomplete.
- Compute boundary: MacBook remains control-plane only; this audit adds
  fixture-only parser coverage.

## Five-Pass Decision

1. Public frontier pass: no validated winner; latest FFG cy0 evidence is dirty
   and short-shot, so no compute unlock.
2. Code archaeology pass: existing transcript and route-compare gates cover
   separate hazards but do not join FFG pair coverage with proof/admission.
3. Correctness pass: one-call coverage can miss value, restore, and phase
   failure classes across the peak-call pair.
4. Search economics pass: pod work should not reopen until a source-bound,
   candidate-hash-bound, positive-edge packet passes review.
5. Handoff pass: add storm-ffg-pair-proof-gate.py, fixtures, skill bridge, and
   public harness checks so the fleet gets a reusable preflight.

## Implemented Gate

The gate requires:

- expected source base and q-tier;
- source hash and candidate index/diff hash;
- FFG suffix-carry context;
- required and covered calls including 178,180,181;
- pair_complete=yes;
- certified value, restore, and phase proof;
- route_compare_admission=pass, admitted=1, sufficient shots, and positive
  score edge;
- no local-heavy, dirty, compute, submit, alert, or Akash language;
- no_submit_ack=yes.

Pass means review only: source-bound-ffg-proof-review-no-compute.
