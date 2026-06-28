# Qoffset Host Accounting Gate

Use this before promoting a source-integrated qoffset host-accounting packet or
closure from the current q1152 lane.

## Command

    python3 scripts/storm-qoffset-host-accounting-gate.py \
      <redacted-qoffset-packet.txt> \
      --require-pass

Defaults assume source `d44cad3` and q1152. Override only after a fresh frontier
lock changes the public source or target tier.

## Pass Requirements

- `source_base=d44cad3`, `q=1152`, source location, source hash, candidate hash,
  qoffset, route id, owner, next action, and `no_submit_ack=yes`.
- The packet is source-integrated and counted at q1152.
- Certified route packets need `expected_avgT_delta<0`, `support_status=CERTIFIED`,
  `proof_status=CERTIFIED`, `restore_proof=1`, and `phase_proof=1`.
- Counterexample closures need `support_status=COUNTEREXAMPLE`,
  `proof_status=COUNTEREXAMPLE`, restore and phase proof flags, and an explicit
  closure reason or artifact.
- No pod, GPU, CPU, scanner, residual, benchmark, alert, or submit request.

## Decisions

- `pass`: certified qoffset packet or counterexample closure, both no-compute.
- `hold`: source, candidate, qoffset, accounting, or proof fields are missing.
- `fail`: stale source, wrong q-tier, UNKNOWN/UNPROVEN proof, nonnegative
  certified delta, compute request, submit/alert language, or missing no-submit
  ACK.
