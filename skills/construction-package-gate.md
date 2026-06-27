# Skill: Construction Package Gate

Use when a lower-q route claims that a new arithmetic construction, co-binder
package, or replacement primitive can beat the current `ecdsa.fail` frontier.

## Core Lesson

A clean local primitive is not a route if it leaves another q wall in place, and
a q-tier drop is not a win if the extra average Toffoli consumes the score edge.
Gate construction packages as one packet before source hooks, residuals, pods,
alerts, or submit language.

## Required Packet

```text
frontier_score:
current_qubits:
current_avg_tof:
target_qubits:
extra_avg_tof:
required_binders:
covered_binders:
candidate_clean: unknown / pass / fail
```

For per-site models, replace `extra_avg_tof` with:

```text
extra_per_site:
charged_sites:
```

## Software Gate

Run:

```bash
python3 scripts/storm-construction-package-gate.py \
  --target-qubits 1151 \
  --extra-per-site 1 \
  --charged-sites 2617 \
  --required-binders gidney,mcx,gcd,fold,register \
  --covered-binders gidney
```

Classifications:

- `package-nack`: missing wall coverage, no score edge, or dirty validation.
- `count-prefilter-only`: coverage and product pass, but clean validation is
  unknown.
- `ready-for-validation`: coverage, product, and clean status pass. This still
  requires the normal validation-submit gate before any win claim.

## Kill Gate

Do not port a construction or dispatch compute if:

- `coverage_ok=0`;
- `count_ok=0`;
- `candidate_clean=fail`;
- the packet names only one wall while the q-tier is a co-binder plateau.

For current `d44cad3/q1152`, use this gate after `q1152-structural-core` and
before `route-compute-gate`.
