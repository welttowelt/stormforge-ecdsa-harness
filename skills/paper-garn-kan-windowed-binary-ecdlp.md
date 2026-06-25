# Skill: Paper - Garn Kan Windowed Binary ECDLP

Use when a route or public note needs exact exceptional-case and windowed
point-addition discipline from binary-field ECDLP resource estimates.

## Source

- Michael Garn and Angus Kan, "Quantum resource estimates for computing binary
  elliptic curve discrete logarithms", arXiv:2503.02984.

## Why We Keep It

The paper is not directly a secp256k1 prime-field circuit, but it is useful
because it emphasizes exact point-addition implementation, exceptional cases,
windowed point additions, table lookups, and exact logical gate/qubit counts.

## Apply To

- architecture reviews that propose table/window changes;
- public notes comparing binary-field and prime-field ECDLP costs;
- validation reminders around exceptional cases;
- rejecting unsafe direct ports into secp256k1 TLM code.

## Required Invariant

A binary-field idea must be translated into a prime-field TLM invariant before
it can become a route.

## Procedure

1. Label the idea as binary-field until translated.
2. Identify whether the value is exceptional-case handling, windowing, or table
   lookup discipline.
3. State a local prime-field invariant or park it.
4. Never claim a direct secp256k1 improvement without local count/residual.

## Output

```text
Garn/Kan windowed binary ECDLP:
- Binary-field idea:
- Local prime-field analogue:
- Exceptional-case impact:
- Window/table impact:
- Decision: cite / translate / park
```

## Kill Gate

No direct field-porting. Binary-field resource movement is not secp256k1
evidence until the local harness validates it.

