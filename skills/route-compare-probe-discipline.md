# Skill: Route-Compare Probe Discipline

**Technique class:** same-vector baseline/candidate localization for
op-stream-changing ecdsa.fail edits.

## Why this skill exists
`residual_probe` and the trusted evaluator derive point-add test vectors from the
operation stream hash. Any structural edit that inserts, removes, reorders, or
retargets ops changes that hash. A dirty candidate residual can therefore mean:

- the edit is actually wrong,
- the new op-hash sampled a bad island already latent in the baseline,
- phase masks changed while classical output stayed equivalent, or
- a stale dead-drop index corrupted a shifted stream.

This skill prevents agents from blaming an individual call just because one
edited stream's Fiat-Shamir sample is dirtier than another.

## When to invoke
Use this before localizing a dirty lower-Q route when any of these are true:

- a per-call env gate appears clean for some calls and dirty for adjacent calls,
- a local toy proof passes but full-circuit residual gets mixed dirt,
- the edit changes op count, order, target IDs, or nonce-tail placement,
- residual/eval results disagree between baseline and candidate after a small op
  change,
- you are about to widen a carry, fold, codec, or dead-op hypothesis based on
  partial residual evidence.

## Required probe shape
Create or reuse a diagnostic binary that:

1. Builds baseline ops and candidate ops from the same source tree.
2. Clears only the candidate env knobs for the baseline build.
3. Sets exactly the candidate env knobs for the candidate build.
4. Derives one vector set under an explicit mode:
   - `fixed`: independent deterministic vectors,
   - `baseline_fs`: vectors from the baseline op hash,
   - `candidate_fs`: vectors from the candidate op hash.
5. Runs both routes on the same point-add inputs.
6. Reports baseline and candidate classical/phase/ancilla counts, `output_diff`,
   `phase_diff_batches`, and first divergence masks.

Command template:

```bash
ROUTE_COMPARE_SHOTS=2048 \
ROUTE_COMPARE_VECTOR_MODE=candidate_fs \
ROUTE_COMPARE_CANDIDATE_ENV='TLM_FFG_CY0_PARK_CALLS=178,180,181' \
cargo run --release --bin route_compare_probe
```

For values containing commas, separate env edits with semicolons:

```bash
ROUTE_COMPARE_CANDIDATE_ENV='TLM_FFG_CY0_PARK_CALLS=178,180,181;TLM_FOLD_CALL_CODE_OVERRIDES=248:5,265:5'
```

## Interpretation rules

- `output_diff=0` and candidate failures match baseline failures:
  - do not blame the edit as a value bug from this sample;
  - suspect op-hash sample drift, baseline dirt, phase-only differences, or later
    composition.
- Candidate has new classical failures against a clean baseline:
  - value bug; localize inside the edit before widening.
- Candidate has phase-only failures:
  - classify the phase source before nonce search or dead-drop work.
- Candidate has ancilla-only failures:
  - lifetime/reclaim bug; check the host was truly zero at loan and restored at
    reclaim.
- Baseline is dirty:
  - treat the result as falsification only, or move to a cleaner checkout/vector
    mode.

## Gate discipline
Route compare is a localization/falsification tool, not a submission gate.

Do not claim `BEAT`, do not submit, and do not hand off from this evidence alone.
Promotion still requires:

```bash
PROBE_SHOTS=9024 cargo run --release --bin residual_probe
./benchmark.sh
jq . score.json
```

The result must be zero classical, zero phase, zero ancilla garbage and score
strictly below the refreshed frontier.

## Example live finding
In the q1146/cy0 lane, a per-call residual screen initially made call 182 look
like the first dirty inverse-fold FFG target. Same-vector route compare
falsified that interpretation:

```text
TLM_FFG_CY0_PARK_CALLS=178,180,181,182,183,185,190,192,194
candidate_fs 2048 shots:
base=3cls/3pha/0anc
cand=3cls/2pha/0anc
output_diff=0
```

The q1146 cy0+fold composition also preserved classical output relative to the
baseline under candidate-FS vectors:

```text
base=6cls/6pha/0anc
cand=6cls/3pha/0anc
output_diff=0
```

That proved the edit was not a simple new value bug, but it did not make the
route viable: q1146 still needed a large Toffoli/dead-op reduction before any
nonce work or submit path.

## Mailbox format

```markdown
## HH:MM from: <worker> - route-compare localization
Candidate=<name> baseline=<tree/hash> candidate_env=<env>.
Same-vector compare=<shots> mode=<fixed|baseline_fs|candidate_fs>
base=<c/p/a> cand=<c/p/a> output_diff=<n> phase_diff_batches=<n>.
Interpretation=<local-edit-falsified|value-bug|phase-bug|baseline-dirty>.
Gate=no winner/no submit; next=<bounded action>.
```
