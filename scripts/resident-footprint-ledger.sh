#!/usr/bin/env bash
set -euo pipefail

trace=""
frontier=""
q=""
target_q=""
route=""

usage() {
  cat <<'USAGE'
usage: resident-footprint-ledger.sh --trace PATH --frontier SCORE --q Q [options]

Options:
  --target-q Q       target peak qubit tier; defaults to Q-1
  --route NAME       route label for the ledger
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trace) trace="${2:-}"; shift 2 ;;
    --frontier) frontier="${2:-}"; shift 2 ;;
    --q) q="${2:-}"; shift 2 ;;
    --target-q) target_q="${2:-}"; shift 2 ;;
    --route) route="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown_arg=%s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$trace" ] || [ -z "$frontier" ] || [ -z "$q" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$trace" ]; then
  printf 'resident_footprint_gate=fail missing_trace=%s\n' "$trace" >&2
  exit 1
fi

if [ -z "$target_q" ]; then
  target_q=$((q - 1))
fi

max_avg=$(( (frontier - 1) / q ))
target_max_avg=$(( (frontier - 1) / target_q ))

awk -v route="${route:-unknown}" \
    -v frontier="$frontier" \
    -v q="$q" \
    -v target_q="$target_q" \
    -v max_avg="$max_avg" \
    -v target_max_avg="$target_max_avg" '
  /^TLM_FFG / {
    call = phase = g = entry = peak = ops = "";
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^call=/) { split($i, a, "="); call = a[2]; }
      if ($i ~ /^phase=/) { split($i, a, "="); phase = a[2]; }
      if ($i ~ /^g=/) { split($i, a, "="); g = a[2] + 0; }
      if ($i ~ /^entry_active=/) { split($i, a, "="); entry = a[2] + 0; }
      if ($i ~ /^local_peak=/) { split($i, a, "="); peak = a[2] + 0; }
      if ($i ~ /^ops=/) { split($i, a, "="); ops = a[2]; }
    }
    if (peak > max_peak) max_peak = peak;
    if (entry > max_entry) max_entry = entry;
    if (peak > target_q) {
      need = peak - target_q;
      if (need > max_need) max_need = need;
      rows++;
      over_calls[call] = 1;
      line = sprintf("call=%s phase=%s g=%d entry_active=%d local_peak=%d need=%d ops=%s",
        call, phase, g, entry, peak, need, ops);
      if (rows <= 80) {
        detail[rows] = line;
      }
    }
  }
  END {
    for (c in over_calls) calls++;
    decision = rows > 0 ? "resident-footprint-cut-required" : "target-already-satisfied";
    printf "Resident footprint gate:\n";
    printf "- Route: %s\n", route;
    printf "- Frontier/q/max avgT: %s/%s/%s\n", frontier, q, max_avg;
    printf "- Target q/max avgT: %s/%s\n", target_q, target_max_avg;
    printf "- Observed max local peak: %s\n", max_peak ? max_peak : "unknown";
    printf "- Observed max entry active: %s\n", max_entry ? max_entry : "unknown";
    printf "- Calls above target: %d\n", calls;
    printf "- Rows above target: %d\n", rows;
    printf "- Required uniform peak reduction: %d\n", max_need;
    printf "- Decision: %s\n", decision;
    if (rows > 0) {
      printf "- Above-target rows:\n";
      for (i = 1; i <= rows && i <= 80; i++) {
        printf "  %s\n", detail[i];
      }
      if (rows > 80) printf "  ... truncated rows=%d\n", rows;
    }
  }
  ' "$trace"
