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

## Generality: a second picture

<!--TABLE-WARRIOR-->

## The margin strips

<!--TABLE-MARGIN-->

## The decision

<!--DECISION-->

## What was retired, and what was not

<!--RETIRED-->
