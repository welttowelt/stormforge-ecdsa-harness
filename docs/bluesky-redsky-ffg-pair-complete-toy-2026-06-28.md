# Bluesky/Redsky FFG Pair-Complete Toy - 2026-06-28

## Context

The active structural lane asked whether the FFG graduated suffix carry chain
could be made pair-complete: finish a local suffix pair, free a boundary carry,
and lower the q1152 wall before spending pod time. The useful split is narrow:
the chunk carry value is locally predictable from final chunk bits only when
the previous carry-in is live or certified-recomputed, but the current HMR
erase of a successor carry still depends on that predecessor carry.

## Loop 1

Bluesky audit:
- Route or idea: Make FFG pair-complete proof work cheap and machine-readable.
- Best case: a recompute certificate can replace resident boundary carries.
- Missing measurement: whether the predecessor carry is still available when a
  successor HMR erase runs.
- Smallest useful experiment: reduced chunk-carry dependency toy.
- Decision: implement a public toy gate, not a source hook.

Redsky audit:
- Strongest objection: a local width drop can hide the fact that the successor
  carry erase still needs the freed predecessor.
- Fastest falsifier: free carry j before erase(carry j+1).
- Decision: no-recompute pair-complete is a NACK.

## Loop 2

Bluesky audit:
- Route or idea: Separate carry predictability from carry lifetime.
- Best case: carry_out can be recomputed from final low bits, constant, ctrl,
  and live carry-in.
- Missing measurement: exhaustive low-width proof for the predicate.
- Smallest useful experiment: enumerate all constants, controls, carry-ins, and
  inputs through width 6.
- Decision: include predictor enumeration in the gate.

Redsky audit:
- Strongest objection: recompute is only valid if the previous carry-in is live
  or itself certified-recomputed.
- Fastest falsifier: carry predictor passes while the dependency graph fails.
- Decision: predictor pass is not source_edit_ready.

## Loop 3

Bluesky audit:
- Route or idea: Preserve a recompute salvage path.
- Best case: on-demand recomputation gives a lower resident peak.
- Missing measurement: lower-bound predicate cost and phase proof obligations.
- Smallest useful experiment: count predecessor recompute predicates.
- Decision: classify recompute as hold, not fail.

Redsky audit:
- Strongest objection: recompute can easily lose the score edge or phase
  correction.
- Fastest falsifier: no restore_proof, no phase_proof, or no negative score
  edge.
- Decision: require a source-hash-bound recompute certificate before compute.

## Loop 4

Bluesky audit:
- Route or idea: Give the fleet a compact NACK fixture.
- Best case: workers stop repeating no-recompute pair-complete claims.
- Missing measurement: machine-readable witness.
- Smallest useful experiment: public no-recompute example.
- Decision: add the fixture.

Redsky audit:
- Strongest objection: a fixture can imply a candidate if it lacks no-submit
  language.
- Fastest falsifier: no_submit_ack missing or source_edit_ready not zero.
- Decision: fixture states no_submit_ack=yes and no compute unlock.

## Loop 5

Bluesky audit:
- Route or idea: Wire the toy into release checks.
- Best case: future edits cannot remove the dependency witness silently.
- Missing measurement: harness check output.
- Smallest useful experiment: check for fail, hold, witness, and required_next.
- Decision: add public harness assertions.

Redsky audit:
- Strongest objection: docs without executable checks drift.
- Fastest falsifier: script compiles but does not run in the release check.
- Decision: run the toy in `scripts/check-public-harness.sh`.

## Result

Implemented process-control hardening only:

- `scripts/storm-ffg-pair-complete-toy.py` exhaustively checks the reduced
  carry predictor through width 6.
- no-recompute pair-complete claims fail with an explicit predecessor/successor
  HMR dependency witness.
- recompute variants hold behind source-hash-bound restore, phase, and score
  proof obligations.

No candidate, no official clean run, no compute unlock, no pod, no alert, and
no submit authority.
