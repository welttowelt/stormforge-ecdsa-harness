# Skill: Frontier Escape Gate

Use after a measured local optimum or repeated corpus-level NACKs, when a route
claims it can still beat the current `ecdsa.fail` frontier.

## Core Lesson

Once deletion, extra venting, vent conversion, local knobs, and known lower-q
half-routes are closed, a packet must name its escape class. Current-corpus
knob repeats do not advance the route unless they bring fresh source evidence.

Admissible post-optimum escape classes:

- `source-theorem`: source-certified scored CCX/CCZ removal, discount, or
  equivalent average-Toffoli theorem;
- `construction-package`: a new arithmetic construction that passes co-binder,
  q-tier product, and clean-status gates;
- `nonce-retune`: a clean retuned island or official-clean result from a
  value-safe stream.

## Software Gate

Run:

```bash
python3 scripts/storm-frontier-escape-gate.py \
  --escape-class current-corpus-knob \
  --local-optimum measured
```

Classifications:

- `escape-nack`: cannot advance beyond Prefilter.
- `source-theorem-prefilter-only`: source theorem has score edge but still
  needs clean validation.
- `construction-prefilter-only`: construction has coverage and count edge but
  clean validation is unknown.
- `ready-for-validation`: packet can enter validation gates, not win language.
- `ready-for-submit-gate`: official-clean nonce-retune packet can move to the
  normal submit gate.

## Kill Gate

Do not run residuals, pods, benchmark, mobile alerts, or submit from:

- `current-corpus-knob` after `local_optimum=measured` without
  `--new-source-evidence`;
- any packet with `score_edge` absent or non-positive;
- source theorems without `source_support=certified`;
- construction packages without coverage and count passing;
- nonce retunes that are only `prefilter` or not clean.
