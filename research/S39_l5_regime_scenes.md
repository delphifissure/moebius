# S39 — Three more field scenes: the regime hypothesis and S38's gate are both falsified (2026-09-20)

S38 ended by saying the scene gate needed "more scenes in the L5 regime, three or four, about twenty minutes of truth each".
Three were built, rendered, mapped, probed, run through the measured arm and scored against the amodal model. The prediction
written down before scoring was that **all three would be L5-regime positives**. One was. Both the hypothesis behind the
prediction and S38's gate candidate are falsified by the result.

## The scenes

All three are ground-contacting clutter behind a figure, which was the structure I believed defined the L5 regime, and they
span it deliberately rather than repeating it. Mirrored in `s35/kit/` with L5 and L6; definitions in `truthkit/scenes.py`.

| scene | the field | pieces surviving the join law under a click map | band |
|---|---|---|---|
| **L7** | boulders, large and sparse, ground visible between them | 7 | 24.9 % |
| **L8** | a crowd of standing figures, tall and narrow | 12 | 17.1 % |
| **L9** | hundreds of small tufts, the extreme contact case | **1** | 16.2 % |

## The result, on the thing class (the hidden field behind the figure)

| scene | arm | model | winner |
|---|---|---|---|
| L5, clumps, heads-only map | **0.346** | **0.061** | model |
| L6, forest crowns in the air | 0.112 | 0.122 | arm |
| L7, boulders | **0.033** | 0.094 | arm |
| L8, crowd | 0.078 | **0.040** | model |
| L9, tufts | **0.015** | 0.041 | arm |

**Two positives out of five, not four.** L8 joined L5; L7 and L9 did not.

## What this falsifies

**1. The regime is not ground contact.** L7 and L9 rest on the ground exactly as L5's clumps do, and the arm wins both —
on L9 by twenty times. So the structural story in §54 and S38, that contact merges the field into the ground and the
construction collapses, does not survive contact with three more scenes. L9 is the sharpest counter-example: its field
merges into a *single* component, the most extreme collapse in the kit, and the arm reads 0.015 m.

The reason is visible in the truth: L9's tufts are low, so they hide almost nothing. Its band carries only 2 402 thing
texels against L5's 21 848. A field can merge completely and still not matter, if it does not occlude.

**2. S38's gate candidate is dead.** The model's median disagreement with the observed depth over the visible region ordered
all five earlier runs correctly. On the five field scenes it does not:

| | L5 | L8 | L6 | L9 | L7 |
|---|---|---|---|---|---|
| model vs observed depth, visible region | 0.013 | **0.091** | 0.096 | 0.084 | 0.082 |
| winner | model | **model** | arm | arm | arm |

L8 sits at 0.091, indistinguishable from L6's 0.096 where the arm wins, and the model wins on L8. One scene was enough to
break it, which is what S38 was afraid of when it refused to fit a threshold to one positive example.

**3. The other candidates do not separate either.** The sky-owned share of the band is 94.5 % and 16.7 % for the two
model wins, and 22–53 % for the three arm wins. The number of surviving components is 1 for an arm win and 12 for a model
win. The only column that happens to separate all five is the unowned share (0.8 and 3.6 % for the model, 4.4 to 9.3 % for
the arm) — but with five points and a two-three split, a signal with no meaning does that by luck one time in five, and the
direction is backwards on its face, so it is noted and not claimed.

## What strengthens

**The stability finding from S36, now on five scenes instead of two.** Across the five field scenes the model's thing-class
error spans 0.040 to 0.122, a factor of three. The arm's spans 0.015 to 0.346, a factor of twenty-three.

| | best | worst | spread |
|---|---|---|---|
| our arm | 0.015 | 0.346 | **23×** |
| the model | 0.040 | 0.122 | 3× |

That is the durable result of this whole line: **the construction is sometimes far better and sometimes far worse; the model
is always mediocre.** Where the arm is good it is better than the model by three to five times, and where it collapses it is
worse by five. Choosing between them is worth roughly a factor of five on the hardest class, and nothing observable that has
been tried tells you which case you are in.

## A practical caveat for anyone using this model

The mask arm is unstable and matters more than expected. `frame` was much the best on L5 (0.034 whole band) and
catastrophic on L7 and L8, where it predicted almost the entire band at sky depth (d 0.006 and 0.012 against a truth of
0.40). `occ` is the safer default but was the worse arm on L5. There is no mask construction here that is safe everywhere,
which is itself evidence that the model is being used outside the distribution it was trained on.

## Where this leaves Phase D

Phase D has now had its extra scenes and the gate did not survive them. Four of the observables the construction offers, plus
the model's own self-consistency, have been measured against five field scenes and none separates the two regimes. I do not
think a sixth scene changes that; I think the gate is not a function of the quantities we have been looking at.

**What I would do instead, in order of cost.**

1. **Stop looking for the gate analytically and let it be learned.** The kit is a generator, not just a scorer. A model
   trained on our own scenes to predict band depth from *depth and the band mask alone* would absorb the regime question
   rather than answering it, and — the point that matters for this project's pictures, which are paintings and
   illustrations rather than photographs — a depth-only model has almost no domain gap, because the depth map is already an
   estimate normalised into the app's own space. A cheap decisive precursor exists: feed the current model a flat grey image
   with the real depth map and see how much it loses. If little, the colour is not carrying the work and a depth-only model
   trained on the kit is viable without any photorealistic data at all.
2. **Or settle it on screen.** A factor of five on the thing class may or may not be visible once the colour plate is over
   it. Nobody has looked. This is the S37 Phase A and B argument again, and it applies with more force now: we are
   optimising a proxy whose relation to what a viewer notices has never been measured.

**Recommendation unchanged, and now better supported: Phases A and B before any more of this.**
