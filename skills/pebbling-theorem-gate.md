# Pebbling Theorem Gate

Use this before converting a transcript/recompute/pebbling idea into route
packaging, residual work, or compute.

## Command

    python3 scripts/storm-pebbling-theorem-gate.py \
      <redacted-pebbling-packet.txt> \
      --require-pass

Defaults assume source `d44cad3`. Override only after a fresh frontier lock
changes the public source.

## Pass Requirements

- route id, owner, next action, source base, source location, source hash,
  candidate hash, and source-bound context are present;
- q/T economics include current q, target q, current average Toffoli, predicted
  candidate or extra average Toffoli, frontier score, candidate score, and
  positive score edge;
- peak rows and affected/overlap rows are positive, and every required call is
  covered;
- the DAG node, removed/delayed/recomputed value, producer, consumers,
  pebbling move, recompute path, and non-stale drop state are named;
- restore, phase, ancilla, support, and proof status are certified;
- evidence label is Prefilter or Partial;
- `no_submit_ack=yes` is present and there is no pod, GPU, CPU, scanner,
  residual, benchmark, alert, or submit request.

## Decisions

- `pass`: pebbling theorem review, no-compute.
- `hold`: packet is missing source, economics, DAG, recompute path, proof, or
  support fields.
- `fail`: counterexample, dirty probe, stale source, stale drop state,
  nonpositive score edge, uncovered required calls, park-only move, compute
  request, submit/alert language, overclaimed evidence label, or missing
  no-submit ACK.
