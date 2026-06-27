# Single-CCX Fanout Throughput Patch

Use this when the live route is the q1152 `SINGLE_CCX_FANOUT` count-edge
nonce-retune search and the bottleneck is per-nonce `build_circuit` time.

## What This Is

`patches/fanout-no-clone-d44.patch` is a source-preserving build-time patch for
the d44 fanout route. It changes `rewrite_first_target_fanout` from taking an
owned `Vec<Op>` to borrowing `&[Op]`, so the outer fanout loop no longer clones
the full opstream before every rewrite scan.

It does not change the circuit claim, nonce predicate, correctness status,
score, or submit gate.

## Verified Effect

On a clean detached d44 worktree with fanout enabled:

- baseline build time: `real 69.50s`
- patched build time: `real 63.79s`
- build-time delta: about `8.2%` faster
- fanout summary unchanged: `passes=318`, `input_ops=10221377`,
  `output_ops=10221059`
- opstream hash unchanged:
  `de23210078367b3d641606047afaa225b25995f2485bf30e4f148aa7a7cf5e85`
- trusted eval status unchanged: dirty, not clean

This is a throughput helper only. It is not a winner and not a score proof.

## Apply Gate

Apply only in a disposable or deliberately claimed challenge worktree:

```bash
git apply /path/to/storm-ecdsa-harness/patches/fanout-no-clone-d44.patch
```

Do not apply in a dirty live checkout unless the owner has acknowledged the
patch and the current source matches d44 fanout files closely enough for
`git apply --check`.

## Verification Gate

After applying:

```bash
cargo build --release --locked --offline --bin build_circuit --bin eval_circuit
env SINGLE_CCX_FANOUT_DISABLE=0 ./target/release/build_circuit
python3 /path/to/storm-ecdsa-harness/scripts/storm-single-ccx-fanout-ledger.py \
  --build-stdout build.out \
  --build-stderr build.err
```

For any claimed nonce shard, still run official `build_circuit -> eval_circuit`
and report exact `classical/phase/ancilla` counts. Only a 9024-shot clean eval
can move the route to official benchmark.

## Rejected Follow-Up

A stronger cached-wire-count variant was tested and rejected. It preserved the
idea of avoiding repeated full-stream metadata scans, but did not finish the
build within the observed window and produced no fanout summary or hash. Do not
ship that variant without a fresh same-hash timing run.
