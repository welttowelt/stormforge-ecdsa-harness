#!/usr/bin/env bash
(
  flock 9
  rm -f ops.bin score.json
  DIALOG_TAIL_NONCE="$1" target/release/build_circuit
  target/release/eval_circuit --note dirty-triage
) 9>/tmp/storm-official-eval.lock
