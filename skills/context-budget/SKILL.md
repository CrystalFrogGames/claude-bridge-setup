---
name: context-budget
description: Audit and slim the always-loaded context — CLAUDE.md, AGENTS.md, skill descriptions, and memory indexes — when sessions burn tokens fast, skills mis-trigger, or instruction files have grown by accretion. Use when the user mentions token consumption, context bloat, skills firing when they shouldn't, or asks to clean up / consolidate their agent setup. Also worth running after adding several skills at once.
---

# Context Budget

Every session pays for the always-loaded layer before it does any work: project
instruction files, every skill's name and description, the memory index. That
layer grows by accretion — a rule added here, a skill added there — and nobody
ever removes anything. The cost is paid on every single turn, forever.

This is an audit, not a rewrite. The goal is a smaller always-loaded layer that
loses no capability.

## Inventory before reading

Read the entry points and sizes first, not the full bodies. Loading everything
to decide what to trim defeats the purpose.

- Project instructions: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules`, and any file
  the harness auto-loads. Note byte counts.
- Skills: just the `name` + `description` frontmatter of each. That pair is what
  actually sits in context; the body is only paid for when the skill fires.
- Memory: the index file, not every memory.

Then read bodies only where the inventory suggests a problem.

## What to cut

**Duplicated rules.** The same instruction in `CLAUDE.md` and `AGENTS.md` and a
skill is paid for three times. Keep it in the most specific place that always
applies, and delete the copies. When two harnesses need the same rule, prefer one
file that both read over two that drift apart.

**Descriptions that ramble.** A skill description exists to answer one question:
should this fire for the current task? Trigger conditions belong there; the
method belongs in the body. A description explaining *how* the skill works is
paying context rent for something only needed after it fires.

**Long examples and templates inline.** Move them to `references/` with a
pointer saying when to read them. A worked example is valuable and almost never
needed on every turn.

**Rules that never fire.** Instructions about a framework you no longer use or a
mistake made once a year cost as much as the ones that matter daily. Cut them.

## What to protect

The pressure to shrink will quietly cost you capability if you let it. Do not
remove:

- Permission boundaries and anything about what must never happen.
- Acceptance criteria and stop-on-failure conditions.
- Explicit output quantities the user asked for.
- Hard-won incident knowledge — the "we learned this the painful way" notes are
  the highest value per byte in any instruction file.

If a cut would trade quality for tokens, it is not a cut. Say so and leave it.

## Fixing mis-triggering

Over-broad descriptions are the usual cause, and the fix is to name the negative
cases. A description saying when the skill should *not* fire disambiguates far
better than more adjectives about when it should. When two skills compete for
the same tasks, either give each an explicit boundary or merge them — two skills
that fire on the same prompts are one skill with extra overhead.

## Verify, then report honestly

After editing: confirm the files still parse, every `references/` pointer
resolves, and nothing in the protected list above went missing.

Report the change list, before/after byte counts, and what you deliberately left
alone. **Do not convert a byte reduction into a claimed token or cost saving** —
the always-loaded layer is only part of a session's usage, and without a real
before/after measurement any percentage is invented.

## Back up first

Instruction files are hand-tuned and often unversioned. Copy before editing, and
say where the backup is.
