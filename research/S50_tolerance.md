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

<!--PREDICTIONS-->

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
