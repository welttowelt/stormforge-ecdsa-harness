# Contributing

Storm is a sanitized operator-layer template for public `ecdsa.fail`
coordination. Contributions should improve process clarity, safety, attribution,
or demo usability without adding private hunt state.

## Good Contributions

- Cleaner templates for route packets, operator cards, or compute requests.
- Better redaction checks.
- Fixture-only dashboard improvements.
- Credit corrections with a public source or clear group-context note.
- Documentation that helps new solvers run a safer agent workflow.

## Do Not Add

- Private endpoints, account details, pod names, provider URLs, or machine
  commands.
- API keys, credential helper output, key filenames, or local private paths.
- Raw logs, private mailbox history, unreleased nonces, active route packets, or
  unsubmitted diffs.
- Claims about a person's contribution that are not public or clearly labeled
  as group context.

## Before Opening A Pull Request

Run:

```bash
scripts/redaction-check.sh
scripts/redaction-check.sh --history
```

Also review `docs/release-redaction-checklist.md`.

## Credit Corrections

Open an issue or pull request if:

- a credit is missing,
- a credit overstates direct use,
- a source should be public instead of group-context,
- a name, handle, or URL is wrong.

Use `inspired by` for process ideas, `uses` for actual code/tool dependencies,
and `based on` only for direct foundations.
