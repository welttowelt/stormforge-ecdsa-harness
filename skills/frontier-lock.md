# Skill: Frontier Lock

Use before judging a route, writing a public note, dispatching compute, or
submitting an `ecdsa.fail` candidate.

## Goal

Force every decision to start from the current public benchmark state, not from
memory, screenshots, stale chat, or a previous clean nonce.

## Public Boundary

Use public benchmark state, public submissions, local repo commits, and local
validation output. Do not request or expose private endpoints, account details,
raw logs, private mailbox history, live ranges, or unreleased nonces.

## Steps

1. Run the current benchmark/frontier query.
2. Record the current best submission ID, solver, score, qubits, Toffoli,
   promoted commit, and timestamp.
3. Confirm the local source commit matches the public promoted source.
4. Inspect recent promoted diffs before proposing edits.
5. Treat old notes and chat memory as `Historical clue` until rechecked.
6. If the frontier moved, rebase the route analysis onto the new promoted diff.
7. Park any route whose expected edge no longer beats the current score.

## Output

Return a frontier lock block:

```text
Frontier lock:
- Current best:
- Promoted commit:
- Local commit:
- Local worktree state:
- Recent promoted diffs read:
- Stale assumptions killed:
- Route decision:
```

## Kill Gate

Do not proceed if the current best, promoted commit, or local worktree state is
unknown.

## Credit

Derived from repeated group-discussion process patterns around stale frontier
avoidance. This card includes no private chat content.
