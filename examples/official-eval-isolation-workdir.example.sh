#!/usr/bin/env bash
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
cp -a challenge/. "$workdir/"
cd "$workdir"
DIALOG_TAIL_NONCE="$1" target/release/build_circuit
target/release/eval_circuit --note dirty-triage
