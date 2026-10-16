---
name: simple-code
description: Complexity-budget discipline for writing and refactoring code. Use whenever writing new functions, reviewing code, refactoring, or when the user complains code is convoluted, over-engineered, or "slop". Apply it even when the user doesn't mention complexity — it should shape how code gets written by default.
---

# Simple Code (Cyclomatic Complexity Budget)

Telling a model "write clean code" does little. Giving it a hard, measurable gate works: code must pass a cyclomatic-complexity lint. Real-world result: a function dropped from 91 decision paths to 12 just by imposing the gate.

## The rule

Write every function as if a linter will reject anything with cyclomatic complexity over 10. When editing existing code, leave functions simpler than you found them.

## How to actually get under budget

- One job per function. If a function's name needs "and", split it.
- Replace nested if/else ladders with early returns (guard clauses).
- Replace switch/if chains that map values with lookup tables or dictionaries.
- Hoist repeated conditions — compute a boolean once, name it, reuse it.
- Push per-case logic into small dedicated functions; the parent becomes a dispatcher.
- Delete speculative branches for situations that can't occur. Handling imaginary cases is complexity with no payoff.

## When tooling exists, use it

If the project has a linter, turn on its complexity rule and run it:
- JS/TS (eslint): `"complexity": ["error", 10]`
- Python: `ruff check --select C901` (mccabe), or `radon cc -s -n C .` to survey
- Go: `gocyclo -over 10 ./...`

If the lint fails, refactor until it passes — do not raise the threshold to make the error go away.

## Sanity check

Simplicity is the goal, not fragmentation. Twenty two-line functions with cute names can be worse than one clear ten-line function. Split along real seams (validation, transformation, IO), not arbitrarily to game the number.
