# Skill: q1152 Structural Core

Use when a worker tries to turn a lower-qubit or structural `ecdsa.fail`
insight into a fleet route, especially q1152 fold, square, register, dirty-host,
borrowed-host, comparator, or GCD static-trim work.

## Goal

Convert structural ideas into reusable evidence. Kill local-only relief before
it burns fleet time, and promote only routes that move a global score wall and
survive trusted validation.

## Core Lesson

The best converter is the wall-gated count/eval loop:

1. Prove the mechanism locally.
2. Check whether it covers every global q wall.
3. Check the score product, not just width or op count.
4. Treat a count edge as `Prefilter` until trusted eval returns clean.
5. Record NACKs with enough detail that the fleet does not repeat them.

Local peak relief is not a candidate. A route must lower the scored qubit tier,
reduce emitted/average Toffoli at the same tier, or produce a clean residual
that beats the refreshed frontier.

## Protocol

1. Refresh the frontier and source base. Record score, qubits, Toffoli, source
   id, and the q-tier threshold being attacked.
2. Name the route family and non-overlap rule. Examples: dirty fold suffix,
   tape-host borrowing, square static trim, GCD exact skip, register wall.
3. Announce CPU or pod use to the coordinator before dispatch. Do not ask for
   approval when CPU use is already authorized, but state the route, validator,
   budget, stop condition, and any protected fleet lane.
4. Run a baseline canary from a clean default environment. Record emitted ops,
   qubits, Toffoli/CCX count, `ops.bin` hash, and the exact command.
5. Locate wall coverage. List every co-peak or q1152 wall: fold, register,
   square/body, clean carry floor, allocator watermark, or exact static family.
   A route that relieves only one below-score shelf is a NACK unless it also
   lowers the official count or score.
6. For dirty-host or borrowed-host ideas, run proof before source hooks:
   candidate id, width, call family, dirty hosts required, clean hosts saved,
   extra CCX estimate, `restore_proof`, `phase_proof`, and `ancilla_proof`.
7. Run source/trace census before a hook. Report available qids, whether the
   host is read during the protected fold, required host width, predicted clean
   host savings, extra CCX, and expected wall movement.
8. Screen count with a default-off knob. Parse emitted ops, qubits, static
   Toffoli/CCX, and peak location. Do not run trusted eval for count-neutral or
   count-worse variants unless the evaluator is the falsifier.
9. If a q-tier or same-tier count edge exists, run trusted eval. Record
   classical, phase, and ancilla failures plus a short failure sample shape.
10. Restore the baseline artifact before leaving the worktree. Post the result
    as ACK, PARTIAL, NACK, or CANDIDATE with artifact names and no private raw
    logs.

## High-Converting Failure Signatures

- Fold-only relief: a dirty suffix can lower a local fold shelf while global
  q1152 remains at register, clean, square, or body walls. If emitted ops
  worsen, park it.
- Proof-only dirty host: a theorem and host census can pass while economics
  fail. If clean hosts saved are below the extra CCX or another q wall remains,
  do not write the source hook.
- Count-positive but dirty: a static skip that saves emitted ops or CCX is still
  `Prefilter` until trusted eval is clean. Broad classical mismatches or phase
  batches make it a NACK, not a near-win.
- Repeated parameter sweeps: if variants share one failed assumption, stop and
  invert the assumption instead of widening the grid.

Recent production pattern to preserve: dirty fold suffix work lowered local
fold pressure but stayed q1152 and count-worse; tape-host census proved host
supply but not a score edge; one GCD top-zero static skip saved count but failed
trusted eval. The reusable result is the gate, not those knobs.

## Output

```text
q1152 structural core:
- Frontier/source:
- Route family:
- Baseline canary:
- Claimed mechanism:
- Wall coverage:
- Proof gate:
- Host/source census:
- Count screen:
- Trusted eval:
- Score economics:
- Evidence label:
- Decision: candidate / validate-more / partial-proof / park / NACK
- Baseline restored:
- Coordinator note:
```

## Kill Gates

Kill or park the route if any of these are true:

- No refreshed frontier or baseline canary.
- The claimed improvement is local-only and another q wall remains.
- Dirty-host proof lacks `restore_proof=1` and `phase_proof=1`.
- Host census lacks enough untouched qids for the required width.
- Extra CCX exceeds the expected score gain.
- Count is neutral or worse at the same q tier.
- Trusted eval has any classical, phase, or ancilla failures.
- The worktree is left on a non-baseline `ops.bin` after a failed variant.

## Public Boundary

Do not put private mailbox history, endpoints, account data, keys, raw logs,
live candidate diffs, unreleased nonces, or submit authority into public route
cards. Redact to source id, command class, artifact label, metric deltas, and
evidence label.

## Companion Cards

Use with:

- `frontier-lock` before any route decision.
- `redsky-frontier-audit` before compute or public claims.
- `route-compute-gate` before CPU/GPU dispatch.
- `exact-support-miner` for value-exact static-skip packets.
- `validation-submit-gate` before clean, win, or submit language.
