# Publish Checklist

Use this before creating the public repo or sharing the link in Telegram.

## 1. Final Local Checks

```bash
scripts/redaction-check.sh
scripts/redaction-check.sh --history
ruby -e 'require "yaml"; YAML.load_file("CREDITS.yaml"); puts "yaml=ok"'
python3 -m json.tool dashboard/fixtures/status.json >/dev/null
```

Expected result:

- tree redaction passes,
- git-history redaction passes,
- YAML parses,
- JSON parses,
- `git status --short` is clean.

## 2. Manual Review

- README states this is not the original `ecdsa.fail` harness.
- Gautham Anant is credited for base benchmark/platform lineage.
- Gajesh Naik / Gajesh2007 is credited for early custom agent-harness
  inspiration.
- Storm is described as the public release surface for the STORM harness in
  production.
- Group-only credits are marked as group-context, not public-source claims.
- Dashboard says demo fixture only.
- No live route, raw log, endpoint, private path, key, or unreleased nonce
  appears in docs, templates, fixtures, or screenshots.

## 3. Suggested GitHub Setup

Recommended repo name:

```text
storm-ecdsa-harness
```

Recommended description:

```text
Public STORM harness for coordinating ecdsa.fail agent workflows with route packets, gates, and redaction checks.
```

Recommended topics:

```text
ecdsa-fail, agentic-science, public-benchmark, workflow, dashboard, redaction
```

## 4. First Release Boundary

Ship only:

- docs,
- templates,
- fixture dashboard,
- redaction checks,
- skills/playbooks,
- credits.

Do not add live automation, private fleet config, mailbox exports, queue state,
or active candidate data.
