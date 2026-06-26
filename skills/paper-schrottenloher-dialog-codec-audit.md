# Skill: Paper - Schrottenloher Dialog Codec Audit

Use when a lower-Q route proposes to reduce the resident TrailMix/Ludicrous
GCD dialog tape, codec windows, or transcript bits using the 2026
Schrottenloher point-addition paper.

## Source

- Andre Schrottenloher, "Optimized Point Addition Circuits for Elliptic Curve
  Discrete Logarithms", arXiv:2606.02235.

## Why We Keep It

The paper makes one codec lesson very concrete: if each Euclidean step emits a
pair of bits with only three reachable states, then three successive pairs have
only 27 reachable values and can be packed into five bits. That is useful, but
it is also a trap. The live TrailMix dialog symbol is not the paper's two-bit
alphabet; the current codec uses richer symbols and already packs three
five-state symbols into seven bits, which is entropy-tight for a local
three-symbol window.

This skill exists to stop false "just port Figure 1" routes and to focus the
team on the only codec cuts that can still matter: cross-window support,
tail-support restrictions, earlier decode/recompression timing, or a proven
smaller alphabet on the exact live route.

## Apply To

- `src/point_add/trailmix_ludicrous/codec.rs`
- `src/point_add/trailmix_ludicrous/gcd.rs`
- `DialogCodec::{Pair, Triple, Step0, Tail4Top32}`
- any proposal to remove resident tape/code bits, remap dialog windows, or
  claim a lower-Q route from transcript compression.

## Required Invariant

State the reachable alphabet and the window support before editing code:

```text
symbol=<name> states=<count/list> window=<k>
current_bits=<b> entropy_lower_bound=ceil(log2(states^k))
cut_claim=<bits removed> proof=<truth table / trace / source argument>
```

A codec cut is invalid if the claimed bit count is below the entropy lower
bound for the reachable support. A local window cut is exhausted if
`current_bits == entropy_lower_bound`; further work must prove additional
non-product support restrictions or change the schedule so fewer bits are
resident at the peak.

## Procedure

1. Run the entropy ledger before touching the solver:

```bash
scripts/dialog-codec-entropy-ledger.sh \
  --route <tree-or-branch> \
  --candidate <codec-name> \
  --symbols <k> \
  --states-per-symbol <n> \
  --current-bits <b> \
  --candidate-bits <claimed-bits>
```

2. For the paper's three-pair gadget, use `states=3`, `symbols=3`,
   `current_bits=6`, `candidate_bits=5`. This should pass and documents the
   source idea.
3. For the live all-triple TrailMix codec, use `states=5`, `symbols=3`,
   `current_bits=7`, `candidate_bits=6`. This should fail the six-bit claim
   and mark the seven-bit codec as local-entropy-tight.
4. Only implement a solver edit after one of these is true:
   - a trace or source proof shows the live route has fewer reachable symbols
     than the generic five-state alphabet at the peak;
   - a larger window has non-product support small enough to save at least one
     resident bit after Toffoli overhead;
   - decode/recompress timing reduces peak overlap without changing the codec
     truth table.
5. After any solver edit, run the normal gates: toy truth table, count, partial
   residual, full 9024 residual/eval, then benchmark. Regenerate dead-drop
   indexes if the op stream changes.

## Output

```text
Dialog codec entropy gate:
- Source:
- Route:
- Candidate:
- Window:
- Current bits:
- Entropy lower bound:
- Candidate bits:
- Potential local cut:
- Decision:
- Next:
```

## Kill Gate

Do not dispatch compute from a codec paper claim. Do not implement a direct
three-pair to five-bit port into TrailMix unless the live symbol alphabet is
actually the same three-state alphabet. Do not claim q1152/q1147 progress from
a codec count until trusted local evaluation is 0/0/0 and the official score is
below the refreshed frontier.
