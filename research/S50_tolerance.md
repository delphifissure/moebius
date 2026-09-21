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

<!--TABLE-TROLL-->

## Generality: a second picture

<!--TABLE-WARRIOR-->

## The margin strips

<!--TABLE-MARGIN-->

## The decision

<!--DECISION-->

## What was retired, and what was not

<!--RETIRED-->
