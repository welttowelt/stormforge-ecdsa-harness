# Skill: Stormgate Prefilter

Use when designing, reviewing, or interpreting a prefilter, canary gate, nonce
search screen, or CPU/GPU dispatch predicate for `ecdsa.fail`.

## Goal

Separate high-volume screening from trusted validation. A prefilter can reject
bad candidates or prioritize work, but it cannot prove a score-relevant
candidate clean by itself.

## Evidence Labels

- `stage-1 reject`: deterministic prefilter reject.
- `stage-1 survivor`: prefilter passed, still not clean.
- `validator reject`: trusted replay found classical, phase, or ancilla failure.
- `full clean`: official validation completed with `0/0/0`.

## Protocol

1. Derive predicates from the current promoted source and exact op stream.
2. Require current-base canary safety before search.
3. Fail closed if canary, source, mode, or predicate config is missing.
4. Quarantine every scanner survivor as `Prefilter`.
5. Send every score-relevant survivor to trusted validation.
6. Stop on the first dirty class that invalidates the predicate.
7. Publish only aggregate, redacted outcomes.

## Output

```text
Stormgate prefilter:
- Predicate:
- Source/base:
- Canary state:
- Dirty class covered:
- Survivor label:
- Trusted validator:
- Fail-closed condition:
- Decision: reject / validate / redesign / park
```

## Kill Gate

Never print or publish prefilter-only rows as `clean`. If no current-base canary
is available, the gate fails closed.

## Credit

Derived from the public `stormgate` gate contract in this repo. This card
includes no private chat content.
