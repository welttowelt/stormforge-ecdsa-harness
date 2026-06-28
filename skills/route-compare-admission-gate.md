# Route Compare Admission Gate

Use this before treating a route-compare packet as residual, compute, pod, or
handoff evidence.

## Command

    python3 scripts/storm-route-compare-admission.py \
      --route-compare <route-compare-summary.out> \
      --frontier-score 1571592960 \
      --require-admission

Omit --require-admission only when the caller wants a classifier row that does
not fail the shell.

## Pass Requirements

- BASE_SUMMARY, CAND_SUMMARY, and COMPARE_SUMMARY are all present;
- baseline classical, phase, and ancilla counts are zero;
- candidate classical, phase, and ancilla counts are zero;
- COMPARE_SUMMARY output_diff=0 and phase_diff_batches=0;
- candidate score is strictly below the supplied frontier score.

## Decisions

- pass: route-clean-score-edge.
- hold: required summary lines are missing.
- fail: dirty baseline, dirty candidate, route diff, or no score edge.

Toy proofs, one-call FFG checks, or route-local improvements do not authorize
residual, scanner, pod, submit, or alert work unless this gate admits the packet.
