---
name: agent-harness
description: How to build self-improving agent systems instead of writing one-off prompts — graphs, loops, subagent fan-out, and durable context. Use whenever a task is big, repetitive, or will be run more than once; when the user wants agents that remember, self-correct, or improve each run; or when they mention workflows, multi-agent, orchestration, or automating a process rather than doing it once.
---

# Agent Harness

The shift (per Anthropic's own Claude Code team): stop prompting agents, start building graphs and loops so agents build the agents. A prompt is a single run. A harness is a process that gets better every run.

## The four durable layers

Anything worth doing twice should be captured in one of these, in this order:

1. **Memory** — facts about the user, the project, the constraints. Written once, read every session.
2. **Project context** (`CLAUDE.md`, project instructions) — what the project is, what good output looks like, the constraints, and what to never do. That last item does the most work.
3. **Skills** — a repeatable *method*. Context lives in a project; method lives in a skill.
4. **Schedules / loops** — the boring recurring work, running whether or not the laptop is on.

## Writing skills from real runs, not imagination

Do the task manually twice, get the output right, *then* ask for the skill to be written from what just happened. Skills written from imagination are guesses about your own process.

A good skill names five things: when to use it, what it needs as input, the steps, what the output looks like, and what it must never do. Missing the last two is why most skills produce something almost right.

## Graphs and loops (the actual harness)

- **Fan out** with subagents when a task decomposes into independent pieces; each gets its own clean context window.
- **Pipeline, don't barrier.** Let each item flow through all stages independently; only synchronize when a stage genuinely needs every prior result at once.
- **Adversarially verify.** Have separate agents try to *refute* each finding. Majority-refuted findings get dropped. This is what stops plausible-but-wrong output.
- **Loop until dry.** For unknown-size discovery (bugs, edge cases), keep running finders until N consecutive rounds surface nothing new. Fixed counts miss the tail.
- **Isolate writes.** When parallel agents modify files, give each a worktree.

In Claude Code, `Workflow` implements all of this; `/loop` handles interval-based repetition; `.claude/agents/*.md` defines reusable subagent roles.

## Self-correction

An agent system improves when failures get written back into the harness. When the same mistake happens twice, do not correct it in chat a third time — add the rule to the skill or project instructions. That single habit is most of what "self-improving" means in practice.

## Multi-agent implementation pattern

For large specs, the proven shape (see github.com/mattpocock/skills → `implement-spec`):
research the codebase in a subagent → implement each ticket in parallel subagents in worktrees → review the merged result against the spec → clean up worktrees.

## Feeding agents good sources

Agents ship wrong code mostly from stale knowledge. Point them at primary sources: official docs, the actual repo, open issues. Firecrawl's Developer Index (firecrawl.dev/developer-index) indexes 70M+ repos/docs/issues specifically for this.
