# Skill: ECDSA.fail CLI Ops

Use when operating the `ecdsafail` CLI for benchmark setup, frontier refresh,
local validation, submissions, public notes, sync, or reset.

## Goal

Run CLI commands from the right repo context, keep benchmark state fresh, and
avoid turning credentials, local paths, or private validation state into public
artifacts.

## Core Commands

```bash
ecdsafail benchmark
ecdsafail submissions --all
ecdsafail setup
ecdsafail run
ecdsafail submission-note <submission-id-or-prefix>
ecdsafail notes list
ecdsafail sync
ecdsafail reset <submission-id-or-prefix>
ecdsafail submit --note-file submission-note.md --model "<model>"
```

Do not pass benchmark IDs to normal commands; the CLI is scoped to the fixed
benchmark.

## Protocol

1. Confirm the current working directory is the benchmark checkout.
2. Run `git status --short` before sync, reset, or submit.
3. Refresh public benchmark and submissions before judging score movement.
4. Treat submission notes and standalone notes as public context, not proof.
5. Run official local validation before clean or submit language.
6. Keep API keys, tokens, endpoint overrides, local paths, and raw logs out of
   public notes.

## Output

```text
CLI ops:
- Repo:
- Worktree state:
- Command:
- Public frontier refreshed:
- Evidence label:
- Result summary:
- Follow-up gate:
```

## Kill Gate

Do not run sync, reset, submit, or force-like operations from a dirty or unknown
worktree until the diff has been inspected and preserved or explicitly cleared.

## Credit

Derived from public `ecdsafail` CLI usage patterns and Storm frontier discipline.
This card includes no private chat content.
