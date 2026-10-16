---
name: game-artdirection
description: Specify a game's visual style so generated output has a deliberate look instead of the default generic one. Use when building or prompting for game visuals, 3D scenes, characters, levels, or game UI — in Godot, Unity, or an AI game generator — and whenever the user wants a specific art style, says visuals look bland or asset-flip-ish, or is starting a new game project's look.
---

# Game Art Direction

Ask for "a good-looking game" and you get the median: grey-brown PBR, soft
gradients, photoreal particles, an unreadable silhouette. A specified style
costs a paragraph and changes everything downstream. This is how to write that
paragraph.

## Name every axis, not just the style label

"Cel-shaded" is a label, not a direction. A usable spec pins down:

- **Surface treatment** — flat color blocks vs. gradients; whether outlines
  exist and how heavy; texture detail budget.
- **Silhouette rule** — how a thing reads when it is far away or small. State it
  explicitly: distant or dangerous objects read as solid silhouettes with one
  bright accent (a stripe, crest, or eye) so they are identifiable against any
  terrain. This single rule does more for game legibility than any other.
- **Particles and motion trails** — matched to the art style. Chunky flat
  illustrated dust, not photoreal smoke, if the world is illustrated.
- **Palette contrast between zones** — a warm sun-baked area against a cool
  misty one. Zones that differ in temperature are navigable from memory.
- **Sky and lighting** — usually forgotten, and it sets more of the mood than
  the models do.
- **Camera** — position, what is visible of the player, head-bob, sway on
  running or damage. Camera feel is art direction, not code detail.
- **HUD** — panel shape, accent color, what sits in which corner, and a
  legibility constraint. Say "minimal and legible" and then say what that means.

## Constrain the deliverable, not just the look

Generated games stall at the diorama stage — pretty, not playable. Say what
must actually work: the core loop, at least one of each interactive entity
class, a day/night cycle if the world implies one, and **no placeholder art**.
Naming "no placeholders" is what stops grey boxes from surviving into the demo.

## Then run a critic loop

Art direction sets the target; it does not hit it. Pair this with the
`critic-loop` skill: score silhouette readability, palette discipline, and
style consistency from several camera angles, and iterate until each clears the
bar. Specification plus scored iteration is the whole method — either alone
produces the generic result.

## Tooling notes

- **Animation from keyframes**: Nvidia MotionBricks generates animation in
  realtime from keyframes with a small local model, and has been implemented as
  a Unity third-person controller. Unity-only for now — it does not help the
  Godot projects.
- **iCity** (Blender) generates a procedural city — roads, towers, parks,
  traffic — in about 30 seconds. Aimed at driving sims, flythroughs and archviz,
  but useful anywhere you need believable urban background geometry rather than
  hand-modelling it. Style it with the axes above; procedural output defaults to
  generic exactly like everything else.
- Check the engine before recommending anything: Marble Allstars and Boxnauts
  Gauntlet are Godot; Boxnauts 2.5D and Book of Oden are Unity.
