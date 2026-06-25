# Skill: Route And Compute Gate

Use before asking for CPU/GPU time, launching a nonce hunt, assigning ranges, or
turning a route idea into a worker task.

## Goal

Spend compute only on falsifiable routes with an owner, predicate, validator,
budget, and stop condition.

## Route Packet Minimum

Every route needs:

- current source/base,
- expected score movement,
- evidence label,
- predicate or proof target,
- cheap falsifier,
- full validator,
- owner,
- maximum budget,
- non-overlap rule for sharded work,
- kill condition,
- public-credit policy.

## Steps

1. Refresh the frontier.
2. Write or update the route packet.
3. Try to kill the route before assigning compute.
4. Run a cheap local/source check first.
5. Dispatch CPU/GPU only if the route has a validator and kill gate.
6. Label all scanner survivors as `Prefilter`.
7. Send every score-relevant survivor to trusted validation.
8. Record negative evidence so dead lanes stay dead.

## Output

```text
Compute gate:
- Route ID:
- Predicate:
- Validator:
- Owner:
- Budget:
- Stop condition:
- Sharding/non-overlap:
- Result label:
- Decision: dispatch / measure / park / kill
```

## Kill Gate

No paid compute when the route lacks a measurable predicate, validator, owner,
budget, or stop condition.

## Credit

Derived from repeated group-discussion process patterns around GPU/CPU dispatch,
nonce search, and route gating. This card includes no private chat content.
