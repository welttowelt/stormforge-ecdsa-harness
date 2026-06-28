# Bluesky/Redsky Source-Family Exhaustion - 2026-06-28

## Context

The latest source-family sweep found seven fresh-looking CCX/CCZ rows, then
closed all seven with counterexamples. The family summary was exhausted:
summary_ccx_ccz_total=71 and open_after_all_jsonl_plus_fresh7=0. That is a
NACK, not a new source packet.

## Loop 1

Bluesky audit:
- Route or idea: Turn exhausted family summaries into machine-readable NACKs.
- Best case: workers stop reopening a family after every open row has a
  counterexample.
- Smallest useful experiment: parse open_after_all_jsonl_plus_fresh7=0.

Redsky audit:
- Strongest objection: open_after=0 can be buried in prose while the route name
  still sounds fresh.
- Fastest falsifier: empty open digest or zero open rows after closure.
- Decision: add source_family_exhausted failure.

## Loop 2

Bluesky audit:
- Route or idea: Require candidate index/diff hash on source packets.
- Best case: a proposed source row can be reproduced and joined to later proof
  output.
- Smallest useful experiment: pass fixtures carry candidate_index_hash.

Redsky audit:
- Strongest objection: source hash alone identifies the code, not the proposed
  candidate row or diff.
- Fastest falsifier: missing candidate hash holds the packet.
- Decision: add missing_candidate_index_or_diff_hash hold.

## Loop 3

Bluesky audit:
- Route or idea: Preserve source-packet novelty as proof admission only.
- Best case: a good packet enters one bounded source proof, not compute.
- Smallest useful experiment: pass output remains
  admit-one-bounded-source-proof-no-compute.

Redsky audit:
- Strongest objection: novelty gates can be mistaken for run authorization.
- Fastest falsifier: compute or submit language still fails through existing
  checks.
- Decision: no compute, pod, alert, or submit authority.

## Loop 4

Bluesky audit:
- Route or idea: Keep exhausted-family evidence public-safe.
- Best case: redacted mailbox rows can be pasted into the gate without private
  paths or raw artifacts.
- Smallest useful experiment: source-packet-novelty-family-exhausted fixture.

Redsky audit:
- Strongest objection: source-family artifact paths can leak local worker
  state.
- Fastest falsifier: redaction check over the public harness tree.
- Decision: add only redacted fixture fields.

## Loop 5

Bluesky audit:
- Route or idea: Wire parser behavior into the public harness.
- Best case: future source-family closures cannot regress quietly.
- Smallest useful experiment: check-public-harness asserts
  source_family_exhausted=true, summary_total=71, open_after=0, and empty open
  digest.

Redsky audit:
- Strongest objection: docs without fixtures drift.
- Fastest falsifier: missing manifest entry.
- Decision: fixture, manifest, skill, bridge, and README updates.

## Result

Implemented process-control hardening only:

- source-packet novelty pass packets now require candidate index/diff hash.
- exhausted source-family summaries fail with source_family_exhausted.
- public harness covers the fresh7-style exhausted-family NACK.

No candidate, no official clean run, no compute unlock, no pod, no alert, and
no submit authority.
