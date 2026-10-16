---
name: anti-slop-design
description: Design-quality pass that strips "AI slop" from any frontend or UI work. Use this whenever building or styling a web page, landing page, dashboard, app UI, or component — even if the user just says "make it look good" or doesn't mention design at all. Also use when reviewing existing UI for polish.
---

# Anti-Slop Design

AI-generated UIs converge on a recognizable "slop" look. People bounce off it instantly because it signals low effort. This skill exists to keep output from pattern-matching to that look.

## Hard bans (the slop tells)

- No box shadows as the default depth cue. Prefer borders, background shifts, or spacing.
- No blue/purple or purple/pink gradients. If a gradient is truly needed, keep it subtle and within one hue.
- No emoji in UI chrome (headings, buttons, badges). Especially no "🟢 LIVE" style badges.
- No glassmorphism blur cards, no floating rounded-corner cards on gradient backgrounds.
- No centered hero with gradient text + two pill buttons — the default AI landing page. Pick a real layout.
- No sparkle/rocket/robot iconography to signal "AI".

## Banned copy words

AI text has a fingerprint. In UI copy, marketing text, and READMEs avoid: delve, seamless, elevate, empower, unleash, unlock, supercharge, game-changer, revolutionize, "in today's fast-paced world", vibrant, robust, cutting-edge, effortless, "look no further". Write like a person naming the concrete benefit instead.

## Positive direction

- Typography does most of the work: one good typeface, a real type scale, tight letter-spacing on headings.
- Use a restrained palette: near-black, near-white, one accent. Gray does the layering.
- Density and alignment over decoration. A tight grid reads as craft.
- Real content over placeholder energy — actual numbers, actual screenshots, actual words.

## Reference material (send to the agent or read when stuck)

- ui-skills.com — installable UI skills
- coss.com/ui — open-source UI patterns
- designsystemchecklist.com — completeness checklist for a design system
- reui.io/components — component library
- emilkowal.ski/ui — essays on motion/UI taste (e.g. "you don't need animations")

## Final pass

Before calling UI work done, reread the rendered page and ask: would someone screenshot this as an example of AI slop? If any hard-ban item survived, fix it now.
