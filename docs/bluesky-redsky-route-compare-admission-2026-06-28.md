# Bluesky/Redsky Route Compare Admission - 2026-06-28

## Context

The latest FFG lane produced a diagnostic one-call packet: toy checks passed,
but route-compare and count evidence did not justify residual, scanner, pod, or
handoff work. The existing route-compare helper detected dirty/no-edge outcomes
in its decision field, but its headline always printed
route_compare_admission=pass. That was too easy to misread in mailbox and
script output.

## Loop 1

Bluesky audit:
- Route or idea: Make route-compare output headline match the admission result.
- Best case: Workers can glance at the first field and avoid promoting a dirty
  diagnostic packet.
- Missing measurement: explicit admitted flag.
- Smallest useful experiment: dirty FFG-style fixture with baseline, candidate,
  and compare failures.
- Stop condition: dirty packet must say fail and admitted=0.

Redsky audit:
- Strongest objection: A decision string buried later in the row can be missed.
- Fastest falsifier: old output said pass for dirty candidate data.
- Decision: Add route_compare_admission=fail/hold/pass and admitted=0/1.

## Loop 2

Bluesky audit:
- Route or idea: Require BASE_SUMMARY, not only CAND and COMPARE.
- Best case: Baseline dirt cannot be hidden while candidate dirt is debated.
- Missing measurement: baseline channel cleanliness.
- Smallest useful experiment: baseline classical/phase dirt in the fixture.
- Stop condition: dirty baseline blocks admission.

Redsky audit:
- Strongest objection: If baseline is dirty, compare agreement is not enough.
- Fastest falsifier: baseline_classical or baseline_phase nonzero.
- Decision: Add baseline_clean and dirty-baseline-no-admission.

## Loop 3

Bluesky audit:
- Route or idea: Separate classifier mode from hard shell gating.
- Best case: Dashboards can keep parsing all rows, while launch scripts can
  require a hard pass.
- Missing measurement: exit status under strict mode.
- Smallest useful experiment: --require-admission exits nonzero for dirty,
  missing, and no-edge rows.
- Stop condition: only route-clean-score-edge exits zero with strict mode.

Redsky audit:
- Strongest objection: Existing callers may rely on classifier exit zero.
- Fastest falsifier: default mode still returns a row for every packet.
- Decision: Add --require-admission without breaking classifier mode.

## Loop 4

Bluesky audit:
- Route or idea: Treat clean but non-winning route-compare as fail for admission.
- Best case: Clean q1147 or q1133 diagnostics do not reopen compute when score
  arithmetic cannot beat the frontier.
- Missing measurement: strict score edge against supplied frontier score.
- Smallest useful experiment: clean no-edge fixture.
- Stop condition: score-no-edge fails strict admission.

Redsky audit:
- Strongest objection: Clean is not the same as useful.
- Fastest falsifier: q * avg_tof >= frontier score.
- Decision: No residual/pod/handoff from no-edge route-compare rows.

## Loop 5

Bluesky audit:
- Route or idea: Make the rule discoverable as a fleet skill.
- Best case: Workers use the same gate before residual, compute, pod, handoff,
  submit, or alert language.
- Missing measurement: public harness and skill bridge coverage.
- Smallest useful experiment: route-compare skill card plus harness assertions.
- Stop condition: public harness and redaction checks pass.

Redsky audit:
- Strongest objection: Hidden parser behavior drifts without skill docs.
- Fastest falsifier: missing public harness manifest entry.
- Decision: Add skill card, Codex bridge, and README entries.

## Result

Implemented process-control hardening only:

- scripts/storm-route-compare-admission.py now reports pass/hold/fail and
  admitted=0/1.
- --require-admission exits nonzero unless the packet is clean and has score
  edge.
- Dirty baseline, dirty candidate, dirty compare, missing summaries, and
  score-no-edge rows cannot be mistaken for admitted routes.

No candidate, no official clean run, no pod, no alert, and no submit authority.
