# Skill: Validation And Submit Gate

Use before promoting a scanner hit, calling a circuit clean, writing win
language, or preparing an `ecdsa.fail` submission.

## Goal

Keep evidence labels honest. A candidate is not clean until trusted validation
or platform promotion says it is clean.

## Evidence Labels

- `Promoted`: accepted by the public platform and present in the promoted
  source.
- `Local full run`: official local benchmark completed with score, qubits,
  Toffoli, and failure counts.
- `Partial run`: bounded local check, component test, or shortened run.
- `Prefilter`: scanner or predicate survivor only.
- `Paper score`: arithmetic estimate before trusted validation.
- `Historical clue`: older note, chat claim, or prior branch.

## Steps

1. Name the candidate source/base and exact diff.
2. Run the cheapest check that can kill the candidate.
3. If it survives, run official local validation.
4. Record qubits, average Toffoli, score, emitted ops, and
   classical / phase / ancilla counts.
5. Recheck the public frontier immediately before any submit attempt.
6. Confirm the worktree diff contains only intended editable circuit changes.
7. Write a public note with model, hypothesis, changes, result, and caveats.

## Submit Gate

Submit only when all are true:

- fresh frontier recheck,
- official local validation returns `0 / 0 / 0`,
- score beats the current public best,
- diff is legal and narrow,
- public note avoids private state,
- explicit submit decision is present.

## Output

```text
Validation gate:
- Candidate:
- Evidence label:
- Local validation:
- Score comparison:
- Diff scope:
- Public note caveats:
- Decision: submit / validate more / park / kill
```

## Kill Gate

Kill or park any route that relies on `Prefilter`, `Paper score`, or a stale
clean nonce as if it were a full clean result.

## Credit

Derived from repeated group-discussion process patterns around validation
discipline and public claim safety. This card includes no private chat content.
