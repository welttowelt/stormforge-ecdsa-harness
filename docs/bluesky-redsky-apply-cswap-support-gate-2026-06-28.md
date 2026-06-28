# Bluesky/Redsky Apply-Cswap Support Gate Audit - 2026-06-28

Context: current q1152 control work had apply-step cswap sites in the live
source buckets, but the broad deletion lane was counterexample-heavy. The
process failure to block is a worker turning a broad cswap intuition into pods,
Akash language, or submit language before a source-bound per-bit proof exists.

## Loop 1 - Frontier and Source Scope

Bluesky proposal: let workers send a compact apply-cswap proof packet before
requesting residual validation.

Redsky attack: a packet on the wrong source could still pass if stale
`source_base` was only a warning.

Implementation:

- `source_base` mismatch is now `stale_source_base` and fails.
- packets also carry `frontier_score` and q-tier.
- added `examples/apply-cswap-support-stale.example.txt`.

Evidence:

```text
apply_cswap_support_gate=fail ... source_base=deadbee ... failures=stale_source_base
```

## Loop 2 - Evidence Label and Claim Safety

Bluesky proposal: a source proof can be reviewed before full validation.

Redsky attack: if the packet says `Local full run` or `Promoted`, it is using a
validation label this gate cannot prove.

Implementation:

- pass requires `evidence_label=Partial` or `evidence_label=Prefilter`.
- `Local full run` and `Promoted` fail as
  `support_packet_overclaims_full_run`.

Evidence:

```text
apply_cswap_support_gate=fail ... evidence_label=Local full run ... failures=...support_packet_overclaims_full_run...
```

## Loop 3 - Compute Spend Gate

Bluesky proposal: after a clean proof packet, workers can ask for the next
validation step.

Redsky attack: packet text could smuggle in "launch GPUs" or similar spend
language before the proof review.

Implementation:

- explicit launch/scale/search language fails as `premature_compute_request`.
- bare remote provenance like `host=runpod` still passes when the rest of the
  packet is clean.

Evidence:

```text
apply_cswap_support_gate=fail ... compute_request=true ... failures=...premature_compute_request...
```

and a pass fixture with `host=runpod` still returns:

```text
apply_cswap_support_gate=pass ... remote_host=true compute_request=false
```

## Loop 4 - Machine-Readable Handoff

Bluesky proposal: make the packet parseable by the fleet instead of relying on
mailbox prose.

Redsky attack: missing owner, route, or next check leads to orphaned work and
duplicate compute.

Implementation:

- pass requires `route_id`, `owner`, and `next`.
- output now prints those fields in the first tokens of the summary line.

Evidence:

```text
apply_cswap_support_gate=pass route_id=apply-cswap-step-bit-proof owner=validator next=source-proof-review ...
```

## Loop 5 - Regression Harness

Bluesky proposal: make the new gate durable in the public harness check.

Redsky attack: examples can drift and still leave stale-source or overclaim
cases uncovered.

Implementation:

- `scripts/check-public-harness.sh` now includes pass, hold, fail, and stale
  fixtures for this gate.
- `skills/apply-cswap-support-gate.md` and the Codex bridge describe the new
  required fields.

Verification:

```text
python3 -m py_compile scripts/storm-apply-cswap-support-gate.py
scripts/check-public-harness.sh
public_harness_check=pass
```

Decision: proceed with this gate as a control-plane guard only. It does not
authorize pods, Akash handoff, alerts, or submit. A passing packet is only ready
for source-proof review before the candidate-validation packet gate.
