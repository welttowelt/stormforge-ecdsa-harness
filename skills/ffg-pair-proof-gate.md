# FFG Pair Proof Gate

Use this before treating an FFG suffix-carry packet as residual, compute, pod,
handoff, submit, or alert evidence.

## Command

    python3 scripts/storm-ffg-pair-proof-gate.py \
      <redacted-ffg-proof-packet.txt> \
      --require-pass

Defaults assume source d44cad3, q1152, required FFG calls 178,180,181, and
route-compare depth 9024 shots. Override only when the public frontier lock or
call map has changed.

## Pass Requirements

- route id, owner, next action, source base, source hash, and candidate
  index/diff hash are present;
- the packet is source-hash-bound and uses the current expected source base;
- FFG suffix-carry context is present;
- required_calls and covered_calls include all expected pair-complete calls;
- pair_complete=yes;
- value_proof, restore_proof, and phase_proof are certified/truthy;
- route_compare_admission=pass and admitted=1;
- route-compare shots and min_shots are at least 9024 by default;
- score_edge is positive against the supplied frontier score;
- evidence_label is Prefilter or Partial, not Local full run or Promoted;
- no local-heavy context, dirty evidence, compute request, submit, alert, or
  Akash language appears;
- no_submit_ack=yes is present.

## Decisions

- pass: source-bound-ffg-proof-review-no-compute.
- hold: complete the missing packet fields before any route handoff.
- fail: do not promote the packet; no residual, compute, pod, submit, or alert.

This gate is intended to stop one-call FFG toys from being misread as
pair-complete structural candidates.
