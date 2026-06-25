# Skill: Bluesky Route Salvage

Use when a route is interesting but weak, stale, underspecified, or about to be
killed before its best bounded version has been tested.

## Goal

Find the smallest falsifiable experiment that preserves upside without spending
compute on wishful thinking.

## Source Order

1. Current public benchmark state.
2. Active route packet and evidence label.
3. Recent promoted diffs and public notes.
4. Local validation or prefilter output.
5. Prior dead-lane notes, marked as historical clues.

## Questions

Ask these before Redsky kills the route:

- What would have to be true for this route to work?
- What missing measurement would unlock or kill it fastest?
- What narrower variant keeps the same upside?
- What alternative mechanism gives similar score movement?
- What cheap check can create new evidence today?

## Output

```text
Bluesky salvage:
- Route:
- Best-case mechanism:
- Missing measurement:
- Smallest useful experiment:
- Bounded alternative:
- Evidence label:
- Next gate:
- Decision: measure / narrow / hand off / park
```

## Kill Gate

Do not salvage a route by removing its validator, hiding its failure class, or
turning a `Prefilter` survivor into a clean claim.

## Credit

Derived from the public Storm audit-loop role for constructive route review.
This card includes no private chat content.
