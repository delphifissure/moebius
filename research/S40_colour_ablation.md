# S40 — The precursor: the amodal model does not use the colour, and blanking it makes it better (2026-09-20)

S39 closed by naming one cheap decisive test. If a depth-only model trained on our own kit is to replace the search for an
analytic gate, the first thing to know is whether the colour is carrying the work at all. The test: **feed the current model
a flat grey frame with the real depth map and see how much it loses.** It was run on all five field scenes, with a third arm
added — the observation depth replicated into three channels, which is what a depth-only model would see in place of a
photograph. Instrument: `bleed/amodal_probe.py --image rgb|grey|depth`. Nothing else changed, and the `rgb` arm reproduces
S36's and S39's numbers exactly, so the baseline is the same one.

## The answer: it loses nothing, and on two scenes it gains a lot

Thing class — the hidden field behind the figure, the class this whole line of work is about — under the **occluder mask**,
which is the one mask arm S39 found stable across scenes.

| scene | our arm | model, real colour | **model, flat grey** | model, depth as image |
|---|---|---|---|---|
| L5 clumps | 0.346 | 0.0734 | **0.0685** | 0.0656 |
| L6 forest | 0.112 | 0.1215 | **0.0960** | 0.1001 |
| L7 boulders | **0.033** | 0.0937 | **0.0405** | 0.1078 |
| L8 crowd | 0.078 | 0.0404 | **0.0391** | 0.0396 |
| L9 tufts | **0.015** | 0.0408 | **0.0387** | 0.0376 |

**Grey is better than real colour in all five.** Not equal — better, in every scene, and on L7 by a factor of 2.3. There is
no scene in the set where taking the picture away costs the model anything on the class that matters.

**So the precursor's question is answered, and in the strong direction.** Whatever the model is using to place the band, it
is not the colour. It is the observation depth and the mask, both of which we have exactly and neither of which cares
whether the source is a photograph or a painting. The main objection to training a depth-only model on our own kit — that it
would be crippled without the image — is not supported by the one model we can measure.

## Two things this also settles

**1. Showing the model the depth map as a picture is not the way.** The `depth` arm is no better than grey on four scenes
and much worse on L7 (0.108 against 0.041). The model already has the depth in its observation channel; a second copy in the
image branch competes with it. If a depth-only model is built, the depth belongs in the observation, and the image branch
should be removed rather than repurposed.

**2. S36's headline L5 number does not generalise, though its verdict does.** The 0.034 m whole-band figure came from the
`frame` mask, and that arm is **entirely a colour effect**: with the image blanked it collapses to predicting almost the
whole band at sky depth (median d 0.005 against a truth of 0.38), taking the thing class from 0.061 to 0.389. S39 had
already found `frame` catastrophic on L7 and L8; this says why it is fragile even where it wins. Under the stable occluder
mask the model still reads 0.073 on L5's thing class against our arm's 0.346, so **the sunflowers verdict stands at four to
five times, not the ten the headline implied.**

## What the colour is for

It is not useless — it is useful somewhere we do not need it. On the background class the grey arm is worse on three scenes
of five (L6 0.185 → 0.267, L8 0.195 → 0.243, L7 0.134 → 0.158), and that is what makes the whole-band medians move around.
But the background class is exactly where our own construction is already at 0.000 to 0.020 in these scenes. **The colour
helps the model on the class we do not need it for, and contributes nothing on the class we do.**

## The configuration to train from

Putting S39's mask finding and this one together gives, for the first time, a configuration with no known instability:

**occluder mask, image blanked.** Across the five field scenes its thing-class error spans 0.0387 to 0.0960, a factor of
2.5 — tighter than the model's own best-mask spread in S39 (3×) and against our arm's 23×. It beats our arm on three of the
five (L5, L6, L8) rather than two, because L6 flips: 0.096 against 0.112. It has no colour dependence, so it has no domain
gap between a photograph and a painting, and it has no mask choice left to get wrong.

It still loses to the arm on L7 and L9, so it is not a replacement and the gate question of S38 and S39 is not answered.
What has changed is what a learned model would have to be: **a function of the depth and the band mask alone**, trained on a
generator we own, with no photorealistic data required and nothing to transfer across the painting/photograph boundary.

## What I did not measure

- Whether a model *trained* without colour reaches this accuracy or better. This measures one colour-trained model's
  reliance on colour, which is the question the precursor asked, and it is evidence about where the information is, not a
  training result.
- L1 and S15, the two non-field scenes from S36's safety check. The ablation was run on the five field scenes because they
  are the ones the gate question lives on. The safety check should be repeated before any use.
- Anything on screen. That remains the gap S37 named and nothing here narrows it.

## Recommendation

Unchanged in order, sharper in content. **Phases A and B first.** If and when Phase D resumes, it now has a concrete shape
rather than an open search: train on depth and the band mask, from the kit, with the image branch deleted — and drop the
`frame` mask and the colour input from the existing instrument, since both have now been measured to be liabilities.
