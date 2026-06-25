# Skill: Submission Forensics

Use when doing a deep public audit of another solver's `ecdsa.fail`
submission, promoted commit, rejected row, public note, or adjacent frontier
move.

## Goal

Understand what a public submission actually changed, what evidence supports
it, what mechanism likely moved the score, and what can be learned without
overclaiming, copying blindly, or exposing private state.

## Public Boundary

Use only public benchmark state, public submission rows, public notes, promoted
Git commits, local legal checkouts, and local validation output. Do not request
or expose private messages, private endpoints, account details, raw logs,
unreleased nonces, live ranges, or non-public candidate diffs.

Do not frame this as an attribution dispute, provenance question, or integrity
claim unless the user has supplied a specific public claim and the evidence is
public. Default to mechanism analysis and credit-safe learning.

## Source Order

1. Current public frontier and submission table.
2. Submission row: status, score, qubits, Toffoli, commit, timestamp, solver.
3. Public submission note.
4. Promoted commit diff against the adjacent promoted base.
5. Local benchmark or targeted reproduction in a clean checkout.
6. Nearby rejected/failed submissions only as clues, not proof.

## Steps

1. Lock the current frontier before analyzing old rows.
2. Identify the exact submission and adjacent base commit.
3. Read the public note and extract only source-checkable claims.
4. Diff editable circuit paths first; ignore harness/scoring changes unless the
   task is legality review.
5. Classify the mechanism:
   - peak-qubit move,
   - average-Toffoli move,
   - nonce/island move,
   - dead-op/drop-list move,
   - schedule/lifetime move,
   - validator or evidence-label move,
   - public-note or credit move.
6. Separate fact from inference. Mark conjectures explicitly.
7. If reproducing, use a clean separate checkout and preserve any dirty local
   work elsewhere.
8. Run the smallest validation needed to verify the claim under review.
9. Produce a dossier with reusable lessons and credit requirements.

## Output

```text
Submission forensics:
- Target submission:
- Status / score / metrics:
- Adjacent base:
- Public note claims:
- Diff mechanism:
- Evidence label:
- Reproduction performed:
- Facts:
- Inferences:
- Risks or proof gaps:
- Reusable lesson:
- Credit note:
- Decision: learn / reproduce / route candidate / ignore / request human review
```

## Kill Gate

Stop or downgrade the analysis if any of these are true:

- the target submission cannot be uniquely identified,
- the adjacent base commit is unknown,
- the claimed mechanism is not visible in public code or public notes,
- local reproduction would overwrite dirty work,
- the conclusion would require private logs, private chat, or unreleased data.

## Credit

Inspired by public frontier-review habits from the `ecdsa.fail` community:
promoted-diff discipline, source-checkable notes, validation-first claims,
current-frontier refresh, and credit-safe mechanism learning. This card includes
no private chat content.
