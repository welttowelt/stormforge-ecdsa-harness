# Release Redaction Checklist

Run this checklist before publishing a public repo, release, screenshot, or
dashboard.

## Automated Check

```bash
scripts/redaction-check.sh
scripts/redaction-check.sh --history
```

## Manual Check

- No secrets, tokens, API keys, or credential helper output.
- No remote machine commands, hosts, ports, account names, or provider-specific
  endpoints.
- No private local paths.
- No live mailbox content.
- No private chat exports.
- No run logs, scanner logs, or raw candidate logs.
- No unreleased candidate diffs.
- No unreleased nonces.
- No current private route state.
- All dashboard data is fixture or public data.
- Every borrowed idea or tool has a credit entry.
- Every group-only source is labeled `group discussion`.
- Every group-only credit is marked `group_context_unverified_publicly` or
  equivalent.
- GitHub Actions redaction checks are present and passing.

## Allowed

- Public benchmark links.
- Public GitHub repo links.
- Fixture data.
- Public leaderboard examples.
- Generic templates.
- Sanitized process docs.

## Required Framing

Every public release should state:

> This is a public benchmark coordination harness for resource-estimation
> research. It does not include private compute access, attack workflows,
> unreleased nonces, or live candidate diffs.
