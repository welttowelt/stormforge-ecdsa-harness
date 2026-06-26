#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/dialog-codec-entropy-ledger.sh --symbols K --states-per-symbol N --current-bits B [options]

Options:
  --candidate-bits B    Proposed encoded bits for the same window.
  --route NAME          Route or checkout label.
  --candidate NAME      Codec candidate label.
  --source TEXT         Paper/source label.
  --notes TEXT          One-line notes.

The script emits the paper-schrottenloher-dialog-codec-audit output shape.
USAGE
}

symbols=""
states_per_symbol=""
current_bits=""
candidate_bits=""
route="unknown"
candidate="unknown"
source="Schrottenloher arXiv:2606.02235"
notes=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --symbols) symbols="${2:?missing symbols}"; shift 2 ;;
    --states-per-symbol) states_per_symbol="${2:?missing states per symbol}"; shift 2 ;;
    --current-bits) current_bits="${2:?missing current bits}"; shift 2 ;;
    --candidate-bits) candidate_bits="${2:?missing candidate bits}"; shift 2 ;;
    --route) route="${2:?missing route}"; shift 2 ;;
    --candidate) candidate="${2:?missing candidate}"; shift 2 ;;
    --source) source="${2:?missing source}"; shift 2 ;;
    --notes) notes="${2:?missing notes}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$symbols" ] || [ -z "$states_per_symbol" ] || [ -z "$current_bits" ]; then
  usage >&2
  exit 2
fi

case "$symbols:$states_per_symbol:$current_bits${candidate_bits:+:$candidate_bits}" in
  *[!0-9:]*)
    printf 'numeric arguments must be non-negative integers\n' >&2
    exit 2
    ;;
esac

awk -v symbols="$symbols" \
    -v states="$states_per_symbol" \
    -v current="$current_bits" \
    -v candidate_bits="$candidate_bits" \
    -v route="$route" \
    -v candidate="$candidate" \
    -v source="$source" \
    -v notes="$notes" '
  function ceil(x, ix) {
    ix = int(x);
    return (x == ix) ? ix : ix + 1;
  }
  function pow_int(base, exponent, i, out) {
    out = 1;
    for (i = 0; i < exponent; i++) out *= base;
    return out;
  }
  BEGIN {
    if (symbols <= 0 || states <= 0 || current < 0) {
      print "symbols, states, and current bits must be positive/non-negative" > "/dev/stderr";
      exit 2;
    }

    support = pow_int(states, symbols);
    lower = ceil(log(support) / log(2));
    current_slack = current - lower;

    if (candidate_bits == "") {
      candidate_bits = lower;
      candidate_label = "not provided; using lower bound";
    } else {
      candidate_label = candidate_bits;
    }

    candidate_slack = candidate_bits - lower;

    if (candidate_bits < lower) {
      decision = "invalid-below-entropy-bound";
      next_step = "prove smaller non-product support or abandon this local codec claim";
    } else if (current == lower) {
      decision = "local-window-entropy-tight";
      next_step = "search cross-window support or schedule overlap, not a same-window bit cut";
    } else if (current > lower) {
      decision = "local-bit-cut-possible";
      next_step = "build truth table and count Toffoli overhead before solver edit";
    } else {
      decision = "current-accounting-impossible";
      next_step = "fix current_bits or reachable support accounting";
    }
    potential_cut = 0;
    if (current > lower) potential_cut = current - lower;

    printf "Dialog codec entropy gate:\n";
    printf "- Source: %s\n", source;
    printf "- Route: %s\n", route;
    printf "- Candidate: %s\n", candidate;
    printf "- Window: symbols=%d states_per_symbol=%d support=%d\n", symbols, states, support;
    printf "- Current bits: %d slack_vs_bound=%d\n", current, current_slack;
    printf "- Entropy lower bound: %d\n", lower;
    printf "- Candidate bits: %s slack_vs_bound=%d\n", candidate_label, candidate_slack;
    printf "- Potential local cut: %d\n", potential_cut;
    printf "- Decision: %s\n", decision;
    printf "- Next: %s\n", next_step;
    if (notes != "") printf "- Notes: %s\n", notes;
  }
'
