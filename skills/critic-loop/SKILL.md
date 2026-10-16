---
name: critic-loop
description: Iterate generated output against a scored rubric until it clears a threshold, using a separate critic with fresh eyes. Use when generating anything whose first draft is usually mediocre — 3D assets, game visuals, level layouts, UI, illustrations, long prose — or when the user says output looks basic, generic, sloppy, or "AI-made". Also use whenever a task has a quality bar the user cares about but hasn't defined.
---

# Critic Loop

A generator asked for one pass produces its median output, and its median is
generic. The fix is not a better prompt — it is a loop with a scorer in it, and
a critic that did not write the thing it is judging.

## The loop

1. **Define the rubric before generating.** Three to six named criteria, each
   with a description of what a 3 looks like versus a 9. Vague criteria produce
   vague scores; "silhouette readable at thumbnail size" beats "looks good".
2. **Generate.**
3. **Inspect from angles the generator did not choose.** This is the step people
   skip and it is where the value is — see below.
4. **Score each criterion 0-10 with one sentence of evidence.** The evidence is
   what makes the next iteration actionable; a bare number is not feedback.
5. **If any criterion is below threshold, fix the lowest-scoring one specifically
   and loop.** Threshold of 8 is a good default.
6. **Stop at the threshold, or after 3-4 rounds with no improvement.** A loop
   that will not converge is telling you the rubric or the approach is wrong,
   not that it needs more rounds.

## Inspect from angles the generator did not choose

Generated work is optimized for the view it was authored in and falls apart
elsewhere. What "angles" means depends on the medium:

- **3D / game assets**: screenshot from several camera positions, plus one
  silhouette-only view and one at thumbnail scale. A model that only reads from
  the hero angle is not finished.
- **UI**: narrow viewport, both themes, longest realistic string, empty state.
- **Prose**: read the opening and closing alone; skim only the headings.
- **Code**: the failure paths, not the happy one.

## Use a genuinely separate critic

The critic must not be the same pass that generated the work. In practice that
means a subagent with a fresh context that receives the rubric and the output
but not the generation reasoning. A generator grading itself rationalizes; it
already believes its choices were correct.

Give the critic explicit permission to score low. Without that it converges on
7s and 8s for everything, and a rubric that always passes measures nothing.

## Why this works

The loop replaces an unstated standard with a stated one. Most "the AI output
looks cheap" complaints are really "nobody told it what good meant, so it
produced the average of everything it has seen." A written rubric plus an
adversarial reader is how you escape the average — and it is also how you find
out that what you actually wanted was never in the prompt.

## Cost discipline

Every loop costs a full generation. Keep the rubric small, cap the rounds, and
apply this to work that will be seen many times — a hero asset, a landing page,
a character — not to throwaway output.
