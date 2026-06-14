# Audit Card Example

## Identity

- Audit ID: demo-audit-route-before-compute
- Auditor: RCI_Worker
- Audit type: RCI/Tony plus Bluesky/Redsky
- Target artifact: examples/route-packet.example.md
- Evidence label: Source fact plus Inference

## Scope

- Decision being audited: should demo-route-current-target-first receive compute?
- What is allowed to change: route packet wording and missing gates
- What is out of scope: paid compute, private logs, submit decisions

## Findings

### Finding 1

- Problem: compute is blocked until the route names a measurable predicate
- Evidence: the route says expected edge is unknown
- Effect: workers could spend time without knowing what output rejects the idea
- Source or implementation check: template requires validator, predicate, and stop condition
- Smallest useful fix: add the exact metric and dirty class before requesting compute
- Gate: do not dispatch until the route predicts a measurable clean class

## Bluesky Pass

- Best case if the route is real: it prevents wasted compute by routing only testable ideas
- Smallest measurement that could unlock it: one cheap local check that classifies failure
- Bounded alternative: park compute and ask for a stronger route packet

## Redsky Pass

- Strongest objection: no score-moving claim exists yet
- Fastest falsifier: check whether the packet names a validator and stop condition
- Failure class: process failure, not circuit failure
- Stop condition: no predicate means no compute

## Decision

- Proceed, park, or kill: park
- Owner: ResearchLead_Worker
- Exact next action: revise route packet with predicate, validator, and kill gate
- Read receipt requested from: ResearchLead_Worker
