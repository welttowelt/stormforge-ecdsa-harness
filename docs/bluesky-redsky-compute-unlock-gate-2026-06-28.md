# Bluesky/Redsky Compute Unlock Gate - 2026-06-28

## Frontier Context

The current frontier remains d44cad3/q1152/1571592960 in the latest mailbox
lock. Storm closed compute after repeated fanout survivors remained dirty and
after a source-line carry packet was proven counterexample-heavy. The immediate
fleet weakness is enforcement: scanner lanes restarted after the close order.

## Loop 1

Bluesky audit:
- Route or idea: Convert "compute closed" into a machine-checkable unlock
  contract.
- Best case: Workers cannot restart fanout or GPU work from stale Prefilter
  evidence.
- Missing measurement: Whether the packet has certified value-exact support and
  Storm route ACK.
- Smallest useful experiment: Parse a redacted compute packet and fail restarts
  lacking the full unlock contract.
- Bounded alternative: Hold incomplete packets instead of killing source-proof
  work.
- Hidden assumption: Compute requests can be recognized from mailbox text.
- Stop condition: Any fanout/GPU/CPU/nonce wording under a closed gate fails
  unless every unlock field is present.
- Decision: Add compute-unlock gate.

Redsky audit:
- Problem: Prefilter survivors are being treated like dispatch permission.
- Evidence: Latest mailbox reports restarted fanout ranges and dirty eval rows
  after compute was closed.
- Effect: Credits and reviewer attention go back into lanes already labeled
  Prefilter/dirty.
- Implementation check: Fail evidence_label=Prefilter and dirty rc/c/p/a text.
- Smallest useful fix: Parser gate with fail reasons.
- Gate: No compute restart from Prefilter or dirty evidence.

## Loop 2

Bluesky audit:
- Route or idea: Make the source theorem the only unlock path.
- Best case: Compute is spent only when there is a source-hash-bound certified
  value-exact packet.
- Missing measurement: source hash, value-exact term, and CERTIFIED status.
- Smallest useful experiment: Pass fixture with Partial evidence and certified
  value-exact proof.
- Bounded alternative: Pair this gate after source-packet novelty gate.
- Hidden assumption: A source proof alone is enough to justify bounded compute.
- Stop condition: Also require exact diff, allocator order, budget, and stop
  condition.
- Decision: Require all unlock fields.

Redsky audit:
- Problem: A theorem packet without exact diff or allocator order can be
  impossible to validate.
- Evidence: Recent NACKs repeatedly cite stale source, wrong source context, and
  missing proof boundaries.
- Effect: Dispatch can build the wrong stream or validate an unrelated edit.
- Implementation check: Require exact_diff and allocator_order.
- Smallest useful fix: Add hard holds for missing diff/order.
- Gate: Missing diff/order blocks pass.

## Loop 3

Bluesky audit:
- Route or idea: Require Storm route ACK as a separate field.
- Best case: A complete source packet cannot silently become an owned pod task.
- Missing measurement: storm_route_ack=yes or route_ack=Storm-Codex.
- Smallest useful experiment: Hold fixture missing only ACK/budget/stop.
- Bounded alternative: The packet can remain ready for Storm review.
- Hidden assumption: Route ACK is distinct from a worker self-ACK.
- Stop condition: Worker ACK does not satisfy storm_route_ack.
- Decision: Separate owner from Storm route ACK.

Redsky audit:
- Problem: Multi-agent ACKs can blur owner, validator, and authorizer.
- Evidence: Mailbox contains repeated ACK/CLAIM packets with pod ownership but
  not source-proof authorization.
- Effect: Pods restart while still carrying only ownership evidence.
- Implementation check: owner, validation_owner, and storm_route_ack are
  separate checks.
- Smallest useful fix: Distinct fields and output flags.
- Gate: Missing Storm route ACK holds/fails under closed compute.

## Loop 4

Bluesky audit:
- Route or idea: Keep the parser public-safe and schema-light.
- Best case: Any worker can paste a redacted packet into the gate.
- Missing measurement: Stable plain-text output for mailbox automation.
- Smallest useful experiment: pass/hold/fail/stale fixtures.
- Bounded alternative: JSON mode for future dashboards.
- Hidden assumption: Regex gates are enough for intake.
- Stop condition: Public harness tests cover the latest restart failure class.
- Decision: Add fixtures and public harness checks.

Redsky audit:
- Problem: A process-control gate can leak private endpoints if examples mimic
  live pods too closely.
- Evidence: Existing redaction check scans private endpoints and home paths.
- Effect: Public harness safety could regress.
- Implementation check: Use public-style packets only and run redaction check.
- Smallest useful fix: Avoid SSH commands, endpoints, and raw private paths.
- Gate: scripts/redaction-check.sh must pass.

## Loop 5

Bluesky audit:
- Route or idea: Chain gates into a durable funnel.
- Best case: novelty gate admits proof work, compute-unlock gate admits bounded
  compute, candidate-validation gate admits Storm handoff.
- Missing measurement: Which transition each gate owns.
- Smallest useful experiment: Skill bridge names the exact command and pass
  semantics.
- Bounded alternative: Keep compute-unlock independent of exact-miner internals.
- Hidden assumption: Workers will not read pass as submit authority.
- Stop condition: Decision string includes no-submit.
- Decision: Add compute-unlock skill and bridge.

Redsky audit:
- Problem: "Pass" can be overread as a win.
- Evidence: Prior mailbox required repeated no-submit and no-sentinel language.
- Effect: A dispatch packet could become a winner claim.
- Implementation check: Pass decision is
  compute-unlock-ready-for-storm-dispatch-no-submit.
- Smallest useful fix: Self-test decision text.
- Gate: Later candidate-validation and fresh frontier locks are still required.

## Result

Implemented:

- scripts/storm-compute-unlock-gate.py
- examples/compute-unlock-*.example.txt
- skills/compute-unlock-gate.md
- .agents/skills/compute-unlock-gate/SKILL.md

This is process-control alpha only. It creates no candidate, no official clean
run, no alert, and no submit authority.
