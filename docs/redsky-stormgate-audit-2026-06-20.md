# Redsky Stormgate Audit - 2026-06-20

Evidence label: `Promoted` for the benchmark result; `Partial run` plus
`Prefilter` for stormgate.

## Frontier Lock

- Public benchmark check on 2026-06-20T10:08Z: current best `1614059832`.
- Source commit shown by benchmark: `94d44be`.
- Submission table was unavailable from the local CLI during this audit, so the
  promoted source and benchmark score are the strongest live evidence used here.

## Audit Scores

| Dimension | Score | Note |
|---|---:|---|
| Frontier freshness | 2 | Benchmark was refreshed during the audit. |
| Edit legality | 2 | No benchmark scoring or verifier edits are part of stormgate. |
| Metric clarity | 2 | Public docs now keep score, qubits, Toffoli, and evidence labels separate. |
| Structural leverage | 1 | stormgate improves search throughput; it is not the submitted source delta. |
| Correctness risk | 1 | Apply-path and phase predictors are still incomplete. |
| Island discipline | 2 | Survivors remain `Prefilter` until trusted validation. |
| Evidence quality | 1 | Good promoted result; incomplete public throughput/soundness matrix. |
| Reproducibility | 1 | Public repo documents the protocol, but private canary values stay out. |
| Handoff value | 2 | The new rules convert the post-mortem into operator gates. |

## Finding 1 - Stale Canary Risk

Problem: A strict predicate can be rejected or trusted against an old clean
nonce from a previous circuit/base.

Evidence: The post-mortem identified a stale hardcoded canary class. A nonce
that was clean on one circuit became dirty on the current base and correctly
tripped a strict-filter self-check.

Effect: Workers can either abort good predicates for the wrong reason or,
worse, run a search with a predicate whose false-negative behavior is unknown
for the current op stream.

Implementation check: `stormgate` mode must require a current-base full-clean
canary supplied from private validation state. The canary is public-redacted,
but the gate itself is public.

Smallest useful fix: fail closed when a stormgate search starts without a
current-base canary, and abort if that canary is false-rejected.

Gate: No stormgate compute until canary preservation passes on the exact source,
op stream, and predicate config being searched.

## Finding 2 - Prefilter Label Drift

Problem: Prefilter survivors can be mislabeled as clean in logs or mailbox
summaries.

Evidence: The operating model already says raw scanner hits stay `Prefilter`,
and the retake confirmed the submitted artifact was a trusted clean nonce
retake, not a prefilter proof.

Effect: A worker can route a survivor as a winner before official local
validation or platform promotion.

Implementation check: Prefilter-only output should be named
`PREFILTER_SURVIVOR` or equivalent. `FULL_CLEAN` and `clean 0/0/0` are reserved
for trusted validation.

Smallest useful fix: update runner labels and docs so downstream scripts parse
the evidence level directly from the line prefix.

Gate: No public claim or submit packet from `PREFILTER_SURVIVOR`; route it to
trusted validation first.

## Finding 3 - Throughput Metric Gap

Problem: stormgate has a clear strategic role, but the public repo does not yet
publish a sanitized speed/soundness matrix.

Evidence: The target is millions of candidates per second at stage 1, but the
public status is still `Partial run` plus `Prefilter`.

Effect: Operators can over-allocate compute to a predicate before knowing
false-positive rate, false-negative canary coverage, and validator load.

Implementation check: Track aggregate-only fields: source, predicate mode,
candidate rate, survivor rate, validator reject split, canary pass/fail, and
full-clean count. Do not include private ranges or raw nonce values.

Smallest useful fix: add a sanitized stormgate benchmark table once the next
measured run is available.

Gate: Treat stormgate as a useful prefilter, not a production moat, until the
speed/soundness matrix is measured on current source.

## Decision

Proceed with stormgate hardening. Do not call it a proof system. The next
improvement is a measured, current-base speed/soundness run with:

- current-base canary preserved,
- prefilter output labeled `PREFILTER_SURVIVOR`,
- trusted validation on every score-relevant survivor,
- aggregate false-positive and reject-class counts,
- no raw tail values, private ranges, endpoints, or logs in public artifacts.
