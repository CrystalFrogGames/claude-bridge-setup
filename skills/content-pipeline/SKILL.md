---
name: content-pipeline
description: Playbook and tool map for short-form video and clipping operations — automated video generation, code-driven editing, viral format research, and distribution. Use whenever working on the clipper project, faceless video, TikTok/Reels/Shorts content, video automation, UGC ads, or growing views for a channel or product. Trigger on anything content-ops shaped, even casual "how do I make more clips" questions.
---

# Content Pipeline Playbook

A map of the current (mid-2026) tooling for automated short-form content, assembled from field reports. Use it to pick the right tool instead of hand-rolling a pipeline from scratch.

## Generation (topic → finished short)

- **MoneyPrinterTurbo** (github.com/harry0703/MoneyPrinterTurbo, 100k+ stars): topic/keyword in → script, stock footage, voiceover, subtitles, music, exported short out. One workflow. Best for faceless volume content; expect to rewrite hooks by hand — the auto-scripts are generic.
- **Open-source agentic editors** (e.g. the calesthio project, ~42k stars): feed it a viral video and it deconstructs script structure, pacing, and visual style, then proposes replication templates. Useful for format cloning, not original voice.

## Editing (edits as code — agent-friendly)

- **Diffusion Studio** (github.com/diffusionstudio): open-source video editor where every edit is code. This fixes the two agent-editing failure modes: lost context and unmodifiable outputs. Pair with **Remotion** (React-based programmatic video) skills for motion graphics. This is the right stack when Claude itself is the editor.
- For skeletal/character animation from text descriptions: **kimodo.cpp**.

## Format research (what to make)

- Study winning UGC formats before producing: pull the top performers in the niche, break down hook (first 1.5s), structure, and pacing, then produce variants. Format-first beats topic-first.
- Virality is engineered at the product level too: design moments that screenshot/screen-record well ("design for TikTok, not for users").

## Distribution and ads

- **TikTok for Business MCP + Agentic Hub**: official MCP server connecting agents to Ads Manager — campaign diagnostics (budget sufficiency vs 50× CPI / 20× CPA, bid health, creative fatigue, cost deterioration). Start read-only: diagnose, don't let the agent mutate campaigns until trusted.
- **Whop Content Rewards / Whop Ads**: pay-per-view clipping campaigns and cheap conversion ads — see the whop-operator skill for the full playbook.

## Working rules

- Ship volume, measure retention at 3s and completion rate, kill formats that don't hold.
- Keep every pipeline step scriptable so the whole thing can run on a schedule.
- Archive raw + project files; re-cuts of winners are the cheapest content that exists.

## Channels are assets, not identities

A creator with 5M+ subscribers across several channels makes the point bluntly:
people damage their own business by staying attached to a channel because of its
subscriber count. A channel is a distribution asset with a niche and an audience
signal attached. When the niche stops working, the subscriber number is sunk
cost — retiring or rebranding it is a normal operating decision, not a failure.

Practical version: judge each channel on whether its recent uploads are finding
an audience, not on its total subscribers. A channel whose audience signal no
longer matches what you want to post is worth relaunching into a focused niche
at a deliberate low cadence rather than continuing to post into the mismatch.

Corollary for a multi-channel operation: a viewer subscribes when they can
predict what comes next. Mixed-game, mixed-creator channels underperform focused
ones, which is why per-channel priority games exist.
