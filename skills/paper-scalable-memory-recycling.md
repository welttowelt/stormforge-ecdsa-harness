# Skill: Paper - Scalable Memory Recycling

Use when a lower-Q route changes qubit allocation or free-list timing and may
silently perturb a dynamic schedule, headroom query, or downstream carry split.

## Source

- Israel Reichental, Ravid Alon, Lior Preminger, Matan Vax, and Amir Naveh,
  "Scalable Memory Recycling for Large Quantum Programs", arXiv:2503.00822.
- Guido Meuli, Mathias Soeken, Martin Roetteler, Nikolaj Bjorner, and Giovanni
  De Micheli, "Reversible Pebbling Game for Quantum Memory Management",
  arXiv:1904.02121.
- Anouk Paradis, Benjamin Bichsel, and Martin Vechev, "Reqomp:
  Space-constrained Uncomputation for Quantum Circuits", Quantum 8:1258 (2024).

## Why We Keep It

The paper family treats qubit reduction as a scheduling and memory-reuse
problem, not only as a local circuit-rewrite problem. This directly maps to
the q1152 Gidney-adder integration failure mode: a replacement primitive can
be value, phase, and ancilla clean in isolation while still changing
`active_qubits`, free-list reuse, or dynamic headroom timing in the full
circuit. If a later schedule decision reads that timing, the full route can
become value-dirty even though the primitive selftest passes.

This skill exists to prevent that failure class.

## Apply To

- `src/point_add/trailmix_ludicrous/arith.rs`
- `add_f_window`
- `add_f_window_hybrid`
- `const_chunk_add_clean`
- `controlled_add_const_chunked_graduated_off`
- `target_qubit_headroom`
- any `TLM_FFG_CALL_G`, `TLM_TARGET_FFG_*`, carry/cout, codec, or fold route
  that changes allocation timing before a dynamic schedule decision

## Required Invariant

A local replacement must either:

1. preserve the baseline semantic schedule at every downstream headroom query,
   or
2. explicitly rebake the schedule and then prove the rebaked route is value,
   phase, and ancilla clean.

Count-only q reductions are not evidence if the candidate changes the
schedule that selects `g`, carry width, cout layout, tape decode timing, or
dead-drop identity.

## Procedure

1. Capture a baseline schedule ledger before the edit:
   - call index;
   - phase/function;
   - active qubits before and after the local primitive;
   - free-list size or active peak if available;
   - chosen `g`, carry width, or schedule knob;
   - operation index around the headroom query.
2. Apply the candidate with a frozen baseline schedule:
   - force the previous per-call `g` or equivalent schedule table;
   - run a no-drop build/eval gate before any dead-drop or nonce work.
3. Diff allocator timing separately from semantic scheduling:
   - the active-qubit timeline may improve;
   - the downstream schedule decisions must not drift in frozen-schedule mode.
4. If the candidate needs a new schedule, create a rebaked-schedule branch:
   - derive the full per-call table under the edited primitive;
   - record exactly which downstream calls changed;
   - run no-drop residual before any current-stream dead-drop regeneration.
5. Only after no-drop value/phase/ancilla is clean, proceed to count,
   2048 residual, 9024 residual, official benchmark, and submit gates.

## Gidney q1152 Gate

For a Gidney 3-clean or constant-workspace suffix route:

```text
Gate A: primitive selftest passes value/phase/ancilla.
Gate B: full build with baseline FFG schedule forced is 0/0/0 no-drop.
Gate C: active timeline shows a real peak cut and records any local transient
        scratch increase.
Gate D: if schedule is rebaked, every changed call index is listed and the
        rebaked route is 9024-clean before score work.
```

If Gate A passes but Gate B fails, debug integration or qubit-lifetime
coupling. If Gate B passes but rebaked mode fails, debug the schedule table,
not the adder.

### Production q1152 update from 2026-06-25

Codex-Vector applied this gate to a 4cd1b2f production-adjacent Gidney
no-drop checkout with the production Gidney switch:

```bash
TLM_GIDNEY_3CLEAN_SUFFIX=1 \
DROP_DEAD_ROBUST_DISABLE=1 \
DROP_DEAD_ROBUST_SECOND=0 \
TRACE_TLM_PROFILE=1 \
TRACE_TLM_FFG_SCHEDULE=1 \
PROFILE_ACTIVE_TIMELINE=1 \
TRACE_PHASE_ACTIVE=1 \
./target/release/build_circuit
```

Result:

```text
baseline raw/no-drop: peak=1153 emitted_ops=10220962
gidney raw/no-drop:   peak=1152 emitted_ops=10247575
schedule rows:        601 baseline / 601 gidney
final_g_diffs:        0
headroom_diffs:       0
phase_diffs:          0
trusted eval:         12 cls / 12 pha / 0 anc over 9024 shots, first shot=948
```

Decision for this exact tree: the Gidney q1152 failure is **not** an FFG
schedule-rebake problem. The schedule decisions are identical; only local
active pressure drops. Do not spend scanner/pod time on this route as a
"rebake the FFG table" task. Move to first-divergence plus lifetime/free-pool
A/B on the Gidney transient family, or park the Fig-5 suffix.

## Output

```text
Memory recycling / schedule-coupling:
- Source paper:
- Candidate primitive:
- Baseline schedule ledger:
- Frozen-schedule result:
- Active-timeline delta:
- Rebaked schedule changes:
- Residual class:
- Decision: freeze / rebake / lifetime-debug / park
```

## Kill Gate

Park the route before compute if:

- any downstream headroom-derived schedule decision changes without an explicit
  rebaked table;
- no-drop full eval is value-dirty;
- phase or ancilla dirt appears after a primitive selftest passed but before a
  schedule ledger identifies the changed region;
- the route relies on stale dead-drop indexes after an op-stream edit.
