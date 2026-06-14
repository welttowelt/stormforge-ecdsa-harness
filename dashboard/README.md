# Dashboard Fixture Mode

This dashboard is a static public-demo surface. It is safe to publish because it
loads only `fixtures/status.json` and does not connect to private services.

## Allowed Data

- Public benchmark examples.
- Fixture route names.
- Sanitized worker roles.
- Aggregate status counts.
- Public-demo breaking news.
- Generic fleet states such as `waiting`, `paused`, or `ready`.

## Forbidden Data

- SSH commands, IP addresses, ports, pod names, provider URLs, or account IDs.
- API keys, token parameters, credential helper output, or key filenames.
- Raw scanner logs, run logs, queue files, or mailbox history.
- Raw nonces, live route packets, private diffs, or unsubmitted candidates.
- Local paths from an operator machine.

## Replacing The Fixture

Before publishing a modified fixture, run:

```bash
scripts/redaction-check.sh
```

Use only public or demo data. If the source is group discussion rather than a
public URL, label it as group context and avoid implying public verification.
