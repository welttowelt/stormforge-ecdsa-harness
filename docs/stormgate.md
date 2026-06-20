# stormgate

`stormgate` is the public-safe name for the prefilter and validation gate used
inside the STORM harness in production.

Evidence label: `Partial run` plus `Prefilter`.

## Purpose

`stormgate` separates high-volume screening from trusted validation:

- screen candidate tails with a fast, circuit-aware prefilter,
- reject known hard failures before CPU validation,
- send only survivors to a trusted validator,
- stop validation on the first classical, phase, or ancilla failure,
- keep every scanner hit labeled `Prefilter` until official validation returns
  clean `0/0/0`.

The target shape is a GPU-friendly stage-1 predicate that can screen millions of
candidates per second, with CPU work reserved for a much smaller survivor set.

## Current Public Status

The safe public claim is narrow:

- The accepted clean canary is preserved by the current local `stormgate`
  prototype.
- The TrailMix jump-2 width/convergence screen rejects known GCD hard failures.
- The apply pseudo-Mersenne fold-risk screen rejects a subset of known dirty
  apply-path survivors.
- The apply screen is not complete yet; remaining dirty survivors still require
  trusted validation.
- A separate fused-fold heuristic was tested and rejected because it false
  rejected the accepted clean canary.
- The GPU wrapper now fail-closes if a TrailMix jump-2 state is searched with a
  non-TrailMix mode, preventing the stale state/mode mismatch that caused a
  false-negative canary path.
- Public frontier ingestion later observed a promoted `fed64cf` source row,
  submission `6c1a65d`, at `1159q` and rounded average Toffoli `1388180`
  (score `1608900620`) on 2026-06-20. That is public leaderboard state, not a
  `stormgate` proof.
- `stormgate` is currently a dispatch and validation gate. GPU prefilter output
  remains quarantined unless current-base clean and dirty canary artifacts exist.

This makes `stormgate` a useful gate, not a proof of cleanliness by itself.

## Redsky Hardening - 2026-06-20

The retake post-mortem added two hard rules to the `stormgate` contract:

- `stormgate` search must fail closed unless the runner is given at least one
  current-base full-clean canary through private validation state. The canary
  value is not published here; the public contract is that the predicate must
  preserve a canary derived from the current circuit/base before any search
  starts.
- Prefilter-only output must use `PREFILTER_SURVIVOR` or an equivalent
  evidence label. Reserve `FULL_CLEAN` / `clean 0/0/0` language for trusted
  validation or platform promotion.

This closes the stale-canary class: an old clean nonce can become dirty after a
base change, so a remembered value is never enough. The canary has to travel
with the exact source, op stream, predicate config, and validation record.

## Gate Contract

Use these labels consistently:

- `stage-1 reject`: deterministic prefilter reject.
- `stage-1 survivor`: prefilter passed, still not clean.
- `validator reject`: trusted replay found classical, phase, or ancilla failure.
- `full clean`: official validation completed with `0/0/0`.

Never publish win language from a `stage-1 survivor`.

## Implementation Shape

The implementation should stay circuit-resilient:

- derive predicates from the promoted source and baked schedules,
- keep unsafe diagnostics behind explicit opt-in flags,
- require canary safety before promoting any predicate,
- reject early in validator batches while preserving simulator transcript
  semantics,
- route GPU `clean` rows back through CPU trusted validation.

## Promotion Checklist

Before a `stormgate` predicate can be treated as production:

1. It must preserve the accepted clean canary.
2. It must reject at least one documented dirty class.
3. It must not depend on private raw scan logs.
4. It must pass the public harness redaction check before publication.
5. It must keep all unresolved survivors labeled `Prefilter`.
6. It must send every score-relevant survivor to official validation before the
   submit gate opens.
7. It must fail closed if no current-base canary is supplied.
8. It must not print prefilter-only rows as `CLEAN`.

## Public Boundary

Do not put private endpoints, raw ranges, local paths, raw logs, unreleased
candidate diffs, or raw tail values in public `stormgate` notes. Public artifacts
may describe the gate, evidence label, dirty class, validator class, and
redacted aggregate outcomes.
