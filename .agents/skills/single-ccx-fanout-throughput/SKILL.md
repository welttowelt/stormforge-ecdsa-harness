---
name: single-ccx-fanout-throughput
description: Apply and verify the source-preserving no-clone throughput patch for the d44 q1152 SINGLE_CCX_FANOUT nonce-retune route.
---

# Single-CCX Fanout Throughput

Use this when a worker is sharding the q1152 `SINGLE_CCX_FANOUT` route and
`build_circuit` time is the bottleneck.

Read `skills/single-ccx-fanout-throughput.md` first. The public patch is:

```text
patches/fanout-no-clone-d44.patch
```

Rules:

- Apply only in a disposable or explicitly claimed challenge worktree.
- Run `git apply --check` before applying.
- Verify same fanout summary and same opstream hash before using the patched
  build for nonce work.
- Treat the patch as throughput-only. It does not make a dirty nonce clean.
- Keep raw nonce shards out of public repo artifacts.
