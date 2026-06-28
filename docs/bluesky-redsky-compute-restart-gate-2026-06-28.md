# Bluesky/Redsky Compute Restart Gate - 2026-06-28

## Context

After the q1152 compute gate was closed, two reachable fanout pods restarted
manual `gpu_island2` scanner work on stale fanout ranges. Pod status showed
`stale_gate_warning=manual_gpu_island2_missing_strict_stormgate_contract`,
while current-target state reported `queue=pod_dispatch=empty_or_no_eligible_job`.
The immediate operational fix was to stop only scanner/search processes and
leave official eval/build untouched.

## Loop 1 - Frontier And Queue

Bluesky audit:
- Route or idea: allow scanners only when the route packet is live and the queue
  has an eligible job.
- Best case: paid pods can still move fast after a certified packet appears.
- Missing measurement: compute_gate open plus route ACK.
- Smallest useful experiment: fail a redacted restart packet when
  compute_gate=closed or queue is empty.
- Bounded alternative: allow official eval-only packets to continue through the
  validation gates.
- Hidden assumption: scanner and eval language can be separated from text.
- Stop condition: closed compute plus scanner term fails.
- Decision: implement a scanner restart gate.

Redsky audit:
- Route or claim: stale q1152 fanout restart.
- Current public truth checked: d44cad3/q1152, score 1571592960; queue empty.
- Evidence label: Prefilter.
- Strongest objection: no certified source packet and no eligible dispatch row.
- Fastest falsifier: pod-status stale-gate warning.
- Failure class: search economics / route ownership.
- Missing gate: machine-readable closed-compute restart block.
- Decision: kill scanner restart, keep official eval path separate.
- Required verification: post-stop pod-status shows busy=0.

## Loop 2 - Source Proof

Bluesky audit:
- Route or idea: restart scanners after a source-hash-bound certificate.
- Best case: proof-first packets can still unlock pods quickly.
- Missing measurement: support_status/proof_status=CERTIFIED.
- Smallest useful experiment: pass a fixture with route_ack=yes and CERTIFIED.
- Bounded alternative: require full 0/0/0 official validation.
- Hidden assumption: certificate belongs to the current source.
- Stop condition: scanner without route ACK plus certificate fails.
- Decision: require both route ACK and certified evidence.

Redsky audit:
- Route or claim: "owner claimed the pod, so it can run."
- Current public truth checked: owner is necessary, not sufficient.
- Evidence label: Partial or Prefilter only.
- Strongest objection: owner metadata does not prove route quality.
- Fastest falsifier: missing route_ack or CERTIFIED support.
- Failure class: gate confusion.
- Missing gate: restart-specific route quality check.
- Decision: keep owner gate separate, add restart gate.
- Required verification: pass/hold/fail fixtures.

## Loop 3 - Eval Separation

Bluesky audit:
- Route or idea: do not kill official evals just because scanner restarts are
  blocked.
- Best case: pending validations can finish and produce real dirt evidence.
- Missing measurement: packet contains eval/build but no scanner term.
- Smallest useful experiment: eval-only fixture passes as no-scanner-restart.
- Bounded alternative: validation-submit gate still owns candidate claims.
- Hidden assumption: eval packet has isolation elsewhere.
- Stop condition: gate docs state this does not certify a candidate.
- Decision: pass eval-only through this scanner-specific gate.

Redsky audit:
- Route or claim: eval/build packet equals scanner restart.
- Current public truth checked: official eval can be useful triage.
- Evidence label: Partial until full validation.
- Strongest objection: killing evals loses dirt-class evidence.
- Fastest falsifier: no scanner regex hit.
- Failure class: overbroad process control.
- Missing gate: separation between scanner and official validation.
- Decision: scanner gate ignores eval-only packets.
- Required verification: eval pass fixture.

## Loop 4 - Claim Safety

Bluesky audit:
- Route or idea: let workers paste simple mailbox ACKs into the gate.
- Best case: fewer ambiguous restarts and less manual interpretation.
- Missing measurement: owner, pod, route/range, next, no-submit ACK.
- Smallest useful experiment: hold fixture with missing owner/pod/route.
- Bounded alternative: owner gate still runs first.
- Hidden assumption: regex parsing is enough for intake.
- Stop condition: missing metadata holds, not passes.
- Decision: add hold state.

Redsky audit:
- Route or claim: scanner pass implies win.
- Current public truth checked: no sentinel, no 0/0/0, no submit.
- Evidence label: Prefilter/Partial.
- Strongest objection: scanner output is not validation.
- Fastest falsifier: premature WINNER/Akash/submit language.
- Failure class: evidence-label overpromotion.
- Missing gate: alert/submit wording block.
- Decision: fail premature claim language.
- Required verification: harness checks output fields.

## Loop 5 - Regression Harness

Bluesky audit:
- Route or idea: make the live failure a permanent public-safe test.
- Best case: any future worker can run one command before restarting scanners.
- Missing measurement: check-public-harness coverage.
- Smallest useful experiment: py_compile plus pass/hold/fail/eval fixtures.
- Bounded alternative: keep the gate independent of private pod config.
- Hidden assumption: examples stay public-safe.
- Stop condition: redaction check passes.
- Decision: add skill bridge, examples, and harness tests.

Redsky audit:
- Route or claim: this process gate improved the operation.
- Current public truth checked: two pods went from busy stale scanners to idle.
- Evidence label: Local ops evidence, not candidate evidence.
- Strongest objection: process fix does not create a circuit win.
- Fastest falsifier: pod-status after stop.
- Failure class: operational burn, not correctness.
- Missing gate: none after tests pass.
- Decision: proceed with process-control patch only.
- Required verification: scripts/check-public-harness.sh and
  scripts/redaction-check.sh.

## Result

Implemented:

- `scripts/storm-compute-restart-gate.py`
- `examples/compute-restart-*.example.txt`
- `skills/compute-restart-gate.md`
- `.agents/skills/compute-restart-gate/SKILL.md`

This creates no candidate, no official clean run, no alert, and no submit
authority. It only blocks stale scanner restarts before they burn pod time.
