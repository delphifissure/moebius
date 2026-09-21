# S50 — Sprint 26: the cliff tolerance in screen pixels, and what the assertion says about it (2026-09-21)

S46 built the plate's near-extent rule and swept its tolerance in source quanta on the troll at 45°. Hole area came out
2.19 / 2.33 / 2.52 / 2.76 per cent at sixteen / eight / four / two quanta and the note recorded the honest conclusion
available at the time: *"monotone with no knee, so the tolerance is a dial between smear and stipple and the screen has
to choose."* A dial with no knee has no defensible default, and the rule has been off ever since.

This sprint reopens it with two things S46 did not have.

1. **The tolerance is now in screen pixels at the rim** (S48, `window._plateNearOnlyPx`). A quantum is a property of the
   depth file; a pixel of reveal is a property of what the viewer sees, and the two differ by the relief. A sweep in
   quanta cannot transfer between pictures. A sweep in pixels can.
2. **The assertion gives the dial a cost function** (S48). Hole area alone cannot separate the two things tightening
   does — it removes fake surface (good: the ramp was never a surface) and it opens cracks between texels that really
   are adjacent (bad: a spanning rule of that reach should have covered them). A **leak is the rule's own mistake**, and
   it is now countable.

Instrument: `moebiusv2/harness/s50_tolsweep.js`. Nothing in the bake depends on the tolerance — it is a fragment test
evaluated every frame — so the arms are re-armed live and a sweep costs one bake and N renders rather than N bakes.

## An arm that did not diverge, and the guard that now catches it

The first sweep's `fold` arm — discard every ramp, the pre-existing all-or-nothing answer this whole sprint is measured
against — returned numbers **identical to `off` at all three poses**: 15 px bounded at 45°, 30 leaks at the corner, byte
for byte. That is not a result; it is an inert arm. The plate's fold path is gated on `u_fragTear > 0.5` and needs the
rest of the A241 stretch law with it — the app arms four uniforms together at bake time — and the harness set one.

Nothing in the numbers looked wrong. They were plausible, they were monotone, and they would have supported a
conclusion. This codebase already carries the lesson, from a134: **an A/B arm must diverge downstream of the flag before
its numbers are read.** So the harness now enforces it rather than relying on me noticing: every non-`off` arm is
compared against `off`'s frame at the same pose and mode, and an identical render is reported loudly instead of
tabulated quietly.

The `fold` rows in the first run's `sweep.json` are void. They are superseded below.

## A defect found on the way in

The S5 **step faces clone the plate's material**, so they inherit whatever near-extent tolerance the plate was armed
with — and the rule would delete every one of them. A step face is *intended* geometry spanning a depth step, so by
construction its whole quad sits far behind its own near end. Nobody had seen it because `_plateNearOnly` defaults to 0
and the faces option ships off. Both the quantum and the pixel tolerance are now explicitly cleared on the step
material.

## Predictions, recorded before the table was read

From the exported reveal field on the troll, converted to screen pixels by the law's own 0.3145 screen px per plate
texel. **Reveal in screen pixels: p50 0.116, p90 0.544, p99 4.641, max 45.2.** Share of texels whose own reveal exceeds
T: **10.83 / 7.03 / 3.35 / 1.06 / 0.75 %** at T = 0.5 / 1 / 2 / 4 / 8.

- **P1. Hole area falls monotonically as T rises.** (Reproduce S46's monotone finding in transferable units.)
- **P2. A knee near T = 4.** The share the rule bites collapses 10.83 → 7.03 → 3.35 → 1.06 and then barely moves to 0.75
  at T = 8. Past four screen pixels there is almost nothing left to bite.
- **P3. Leaks should not be monotone in T.** The rule keeps a ramp within T px of its near end and discards the rest, so
  it removes (reveal − T) px of streak from every ramp exceeding T. Small T removes most of a ramp → the gap left is
  *wide* → genuine. Large T shaves a sliver off the ramps that only just exceed T → *narrow* → leak. Both extremes
  should therefore produce few leaks and the peak should be somewhere in between. I deliberately did not predict where.
- **P4. The quantum arms should not line up with any pixel arm, and should line up differently on a second picture.**
  A quantum is a property of the depth file; the d-to-pixel conversion is the law's nonlinearity, which spreads 40× across
  this one picture (p50 0.116 px against p99 4.641 px). This is the whole argument for changing units, and it is
  falsifiable.
- **P5. Self-consistency of the two S47 takeaways.** The field predicts which cells open a gap wider than T; the
  assertion measures which gaps we failed to close. If the rule produces a bounded-genuine class far exceeding the
  field's over-T share, the two are measuring different things and at least one is wrong.

**P3 was wrong, and the sweep says why.** Leaks fall monotonically with T on this picture (322 → 208 → 123 → 56 at
45° horizontal). The sliver-shaving effect is real but it is swamped by the collapse in *how many ramps are bitten at
all* — 10.83 % of texels at T = 0.5 against 1.06 % at T = 4. I had the mechanism right and its magnitude wrong.

**One thing I worried about in advance and was also wrong about.** The rule evaluates reveal at the envelope *rim*, not
at the current pose, so I expected it to open cracks even at rest. It does not: at rest two adjacent texels project one
texel apart, the ramp quad spans no gap, and removing it removes nothing. **Every arm including `fold` costs exactly one
unpainted pixel at rest, the same as shipping.** This is the same fact from the other side as S46's "the defect only
appears in motion" — so does the cost of fixing it.

## The sweep

### The cost curve (troll, rest-pose rectangle, three poses)

The first run, `off` through `px4` and `q8` — the `fold` rows from it are void, see above. Every figure is a share of
the **rest-pose** content rectangle (86 296 px); leak counts are pixels.

| arm | rest bounded | 45° h bounded | 45° h leak T=1 | leak share | corner bounded | corner leak |
|---|---|---|---|---|---|---|
| off (shipped) | 1 px | 15 px | 15 | — | 825 px | 30 |
| px0.5 | 2 px | 607 px | 322 | 53 % | 2 182 px | 234 |
| px1 | 2 px | 423 px | 208 | 49 % | 2 003 px | 191 |
| px2 | 2 px | 280 px | 123 | 44 % | 1 739 px | 218 |
| **px4** | 1 px | **154 px** | **56** | **36 %** | **1 423 px** | 148 |
| q8 (S46) | 2 px | 298 px | 147 | 49 % | 1 736 px | 256 |

**P1 and P2 hold.** Hole area is monotone in T, and the knee is at T = 4 where the field predicted it — past four screen
pixels only 1.06 % of texels still exceed the tolerance, falling to 0.75 % at T = 8, so there is almost nothing left to
bite. **Rest costs nothing**: one unpainted pixel, every arm, same as shipping.

**The leak share is strongly pose-dependent and the mechanism is plain.** At 45° horizontal it is 36–53 %; at the corner
it is 8–13 %. At the corner both axes sit at the rim so the removed ramp tails are wide and land in *genuine*; at 45°
horizontal only the horizontal axis is at the rim (the vertical envelope is 30°), so the tails are narrow slivers and
land in *leak*. **The rule is at its worst in the pose that happens most**, since pure horizontal head movement is the
dominant motion. This is the single strongest argument against a tight tolerance, and no instrument before the assertion
could have stated it.

### The trade (troll, 45°, all five arms, one rectangle)

Streak removal needs the placeholder column, which needs the SD check view, so this is a second pass at the 45° pose
only — **its rectangle is that pose's bbox (141 358 px), not the rest pose's, so these absolutes are not comparable with
the table above.** Internally they are one measurement, which is what the comparison needs. All five arms diverged.

| arm | placeholder | bounded hole | leak | streak removed | hole added | **removed per added** | leaks added |
|---|---|---|---|---|---|---|---|
| off | 34.882 % | 0.0113 % | 16 | — | — | — | — |
| px2 | 34.582 % | 0.1988 % | 124 | 0.300 | 0.1875 | 1.60 | +108 |
| **px4** | 34.705 % | **0.1097 %** | **57** | 0.177 | **0.0984** | **1.80** | **+41** |
| q8 | 34.674 % | 0.2115 % | 148 | 0.208 | 0.2002 | 1.04 | +132 |
| fold | 34.553 % | 0.5079 % | 291 | 0.329 | 0.4966 | **0.66** | +275 |

**The middle path beats both extremes.** `fold` removes 1.9× as much streak as `px4` but pays 5× the hole and 6.7× the
leaks — a ratio of 0.66 against 1.80. Keeping every ramp (`off`) is free of holes but keeps the whole streak.

**The pixel form dominates the quantum form.** `px2` beats `q8` on every column at once: more streak removed (0.300
against 0.208), less hole (0.199 against 0.212), fewer leaks (124 against 148). That is the evidence for retiring
`u_plateNearOnly` rather than an argument from units.

### A caveat that changes what the benefit is

`fold` discards **every** ramp and reduces placeholder by only 0.329 points. S46 measured the ramps at 3.7 % of the
picture at 45°. The gap is not a contradiction — plate 2 exists on this bake, so discarding a ramp frequently reveals
**plate 2, which is also placeholder-tinted**. Removing ramps therefore does not mostly reduce invented colour; it
replaces one invention with a better one. The benefit is qualitative — a second-surface estimate instead of a rubber
band that tunnels between foreground and background, which was the user's original report — and the cost, hole and
leaks, is the part that is quantitative.

## Generality: a second picture, and P4 holds

Silverwarrior at 45°, its own pose rectangle (127 190 px). The `fold` arm was killed before it finished — it had run
over an hour on a single render and was blocking Sprint 27; the four arms below are complete.

| arm | placeholder | bounded hole | leak T=1 |
|---|---|---|---|
| off | 29.117 % | 0.8751 % (1 113 px) | 292 |
| px1 | 29.554 % | 1.7596 % (2 238 px) | 466 |
| px4 | 29.506 % | 1.6990 % (2 161 px) | 430 |
| q8 | 29.799 % | 1.7942 % (2 282 px) | 495 |

**On this picture the rule removes no streak at all — it is pure cost.** Placeholder *rises* under every arm (29.117 →
29.5–29.8), because the discarded ramp tails reveal plate 2 and other placeholder classes behind them rather than real
content. The troll's modest benefit does not generalise even to a second photograph, which is a stronger version of the
sprint's conclusion than the troll alone supports.

**P4 holds, and it is the case for the change of units.** S46's quantum tolerance does not keep its place between
pictures:

| | troll | silverwarrior |
|---|---|---|
| where `q8` sits | between `px1` and `px2` (bounded 298 px against 423 and 280) | **worse than both** `px1` and `px4` (2 282 against 2 238 and 2 161) |

A threshold in source quanta is a statement about the depth *file*; the same number means a different visible gap on the
next picture. On both pictures the pixel form also **dominates** the quantum form outright — `px4` beats `q8` on every
column here as `px2` did on the troll — so if the near-extent rule is ever turned on, the quantum form goes.

## The margin strips

<!--TABLE-MARGIN-->

## The decision: none of these, and the sprint's real finding is why

The contact sheet went to the user. Their verdict was *"they are all streaky as hell — why in the world are we not
getting clean outlines."* That is the correct reading and it is the most valuable result of the sprint, so the rest of
this section is the measurement that explains it rather than a defence of the arms.

**Decomposing the 45° frame by placeholder class** (content rect 439 × 322 = 141 358 px):

| | off | px4 | fold |
|---|---|---|---|
| real source colour | 30.59 % | 30.76 % | 30.90 % |
| **cyan — band, must paint** | **5.19 %** | 4.89 % | **4.36 %** |
| blue — band outside tier | 0.62 % | 0.67 % | 0.69 % |
| magenta — plate 2 | 0.11 % | 0.14 % | 0.16 % |
| orange — beyond the frame | 28.96 % | 28.99 % | 29.19 % |
| dark — hole / letterbox | 34.53 % | 34.53 % | 34.55 % |

**About 16 % of the actual picture at 45° is invented colour, and the ramps this sprint tuned are ~0.8 points of it.**
Discarding *every* ramp moves the band from 5.19 % to 4.36 %. Every arm looks streaky because every arm leaves the band
untouched.

**And at magnification the band's texture is horizontal tongues with a ragged edge against the figure** — which is not
the colour fill's doing but the *geometry's*. S33 measured this on 2026-09-15 and the numbers are unambiguous. On the
troll, 99 205 visible bends (40.5 % of all vertical band edges), classified by what the two texels continue from:

| class | count | wall length (what the eye integrates) |
|---|---|---|
| **1 — same surface, the law disagrees with itself** | **77.2 %** | 38.8 % |
| 2 — a real step between two background surfaces | 10.4 % | 26.1 % |
| **3 — axis change: row/column arbitration flipping between neighbours** | 12.3 % | **35.1 %** |

**74 % of the troll's streak length is the construction disagreeing with itself.** Class 1 draws short walls (median
3.3 px) — the fine horizontal hatching that fills the band. Class 3 draws long ones (median 25 px) — two adjacent texels,
one continued along its row and one along its column, landing a hundred pixels of parallax apart.

**So the cliff tolerance is choosing how to draw a wall that should not exist.** Keep it, shave it, or discard it: the
wall is an artefact of the far field's per-line construction either way. That is why the sweep's arms differ by tenths
of a point and all of them look the same to the eye.

**Therefore: the rule stays off, which is what ships today.** Not because a tolerance could not be chosen — `px4` is
clearly the best of them — but because the choice is worth 0.8 points against a 5.8-point problem, and the person whose
screen is the authority looked at all five and rejected them. Turning on a rule that trades smear for stipple, for that,
would be motion without progress.

## What was retired, and what was not

**`fgTearStep` was not retired, and S49's item was written too broadly.** It has 84 uses and most are not the renderer's
cliff criterion: they are bake-side "are these two lips the same surface" tolerances — component segmentation in
`_planeObjects`, band continuation, the v1 directional plate, object detection (A253). Those are pose-independent
statements about the depth map's structure. As the *tear* criterion it is already only a fallback behind
`window._noFoldTear`, since a160/a177 replaced it with the fold-plus-quantum law.

**`window._noFoldTear` was not retired.** It restores the falsified a117 criterion and is still used as a deliberate
control by `posesweep.js` and `restblack.js`. This project keeps such controls on purpose.

**`u_plateNearOnly` (S46's quantum form) was not retired either, and the reason is worth recording.** The evidence to
retire it is there — `px2` beats `q8` on every column at once, more streak removed, less hole, fewer leaks — and it is
the right call *if the rule ever ships*. But the rule does not ship, so retiring one of two dormant dials is churn
against a plan item rather than work. **The evidence is recorded here so that if the near-extent rule is ever turned on,
the quantum form goes without re-measuring.**

The genuine deliverables of this sprint are three, and none of them is a tolerance:

1. **`harness/s50_tolsweep.js`** — the cliff dial swept in transferable units and scored by the assertion rather than by
   hole area.
2. **The inert-arm guard.** The `fold` arm rendered identically to `off` at every pose and its plausible, monotone rows
   would have supported a conclusion. Every arm is now compared against `off`'s own frame and a match is reported
   loudly (a134).
3. **The diagnosis above**, which redirects the plan: the streak is 74 % self-disagreement in the far field, and that is
   upstream of every rule this sprint measured.
