# Skill: Multi-Agent Handoff

Use when handing work between Codex-, Claude-, DeepSeek-, Kimi-, OpenRouter-, or
human workers.

## Goal

Make worker coordination explicit enough that claims, objections, and next
actions survive model changes and async chat.

## Roles

- Research lead: refreshes frontier, ranks routes, writes packets, kills stale
  lanes.
- Engineering specialist: receives narrow tasks with validator and kill gate.
- Deep researcher: answers proof or architecture questions.
- Skeptic: tries to falsify route, claim, or public note.
- External pressure-test worker: returns one objection, one question, one
  bounded alternative, and a falsifiable decision.

## Handoff Contract

Every directed handoff should include:

- sender and recipient,
- current target,
- active route,
- evidence label,
- exact task,
- validator,
- kill gate,
- allowed and forbidden inputs,
- expected output format,
- read receipt request.

## Steps

1. Convert chat input into source-labeled evidence before it affects routing.
2. Ask for ACK or correction from the receiving worker.
3. Keep private logs, endpoints, and nonces outside public handoffs.
4. Route objections back into the route packet.
5. Close the loop with what changed, what failed, and who owns the next action.

## Output

```text
Handoff:
- From / to:
- Current target:
- Route:
- Evidence label:
- Task:
- Validator:
- Kill gate:
- ACK requested from:
- Next owner:
```

## Kill Gate

Do not accept a worker completion claim without a validator output, source
citation, or explicit blocker.

## Credit

Derived from repeated group-discussion process patterns around multi-agent
coordination. This card includes no private chat content.
