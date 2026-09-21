# S42 — The collar test: the named failure is real and one-sided, the gate falsifies a fifth time, and the question turns out to be class-level (2026-09-21)

R7's first item, run. Counterfactual Depth names the condition under which a geometric continuation fails — *"one side of the
background is closer than the other"* — and reports that a smoothing baseline's error is poorly explained by scene attributes
because *"more important is the pool of depths around the object"*. Every gate this project has falsified is scene-level or
model-level, so the collar family was untested. Instrument: `bleed/collar.py`. Six scenes, the five field scenes plus L1 as a
control where the construction is excellent.

## The statistic

Per band texel, the **opposition**: the difference between the far lip on one side of the hole and the far lip on the other,
per axis, in visible steps. A far lip is the nearest visible texel along the axis whose depth is behind the occluder's. This is
the named failure directly. S38's `lipsp` took a maximum minus a minimum over all four directions at once, which conflates the
axes and does not isolate opposition. Per band component, two more: the largest gap in the sorted far-collar depths, and the
residual of a plane fit to that collar. The collar is the component's own visible rim, which is parameter-free. (A first
version dilated by the band's own half-width, as §47 does for a per-texel window; on L7 that is 59 texels, a neighbourhood
rather than a collar, and it drags in surfaces the hole never touches.)

## 1. The named failure is real, and it is strong

Arm error over the whole band, split by whether the two opposing far lips agree to within one visible step:

| scene | lips agree | lips disagree | ratio |
|---|---|---|---|
| **L5** clumps | **0.0027 m** | **0.4402 m** | **162×** |
| **L6** forest | **0.0000** | **0.0492** | unbounded |
| **L9** tufts | **0.0000** | **0.0023** | unbounded |
| L1 leaves | 0.0121 | 0.0105 | 0.9× |
| L7 boulders | 0.0667 | 0.0589 | 0.9× |
| L8 crowd | 0.0947 | 0.0902 | 1.0× |

On three scenes of six the construction is **exactly right wherever the collar does not oppose**, and wrong wherever it does.
That is the paper's claim reproduced on our data, and it is the first time any observable has separated our error by two orders
of magnitude.

## 2. But it is sufficient, not necessary, and that is what kills it

On L1, L7 and L8 the split does nothing, because **the construction is already wrong where the collar agrees** — 0.012, 0.067
and 0.095 m in the agreeing region. A second failure mode dominates those scenes and opposition cannot see it. So the signal
has good recall of one failure and no purchase on the other.

## 3. No scene-level aggregate orders the scenes. That is the fifth falsification.

Six scenes, ranked by the construction's thing-class error, against every aggregate the collar offers:

| aggregate | vs thing class | vs whole band |
|---|---|---|
| fraction of band where lips disagree | ρ −0.43, p 0.40 | ρ +0.03, p 0.96 |
| mean opposition | ρ −0.60, p 0.21 | **ρ −0.77, p 0.07** |
| 90th percentile opposition | ρ −0.54, p 0.27 | ρ −0.43, p 0.40 |
| mean lip spread | ρ −0.66, p 0.16 | ρ −0.66, p 0.16 |
| mean reach | ρ −0.03, p 0.96 | ρ −0.14, p 0.79 |

Nothing reaches significance, and **every correlation is negative, which is the wrong direction** — more opposition goes with
*lower* error across scenes. The nearest thing to a signal, mean opposition against the whole-band error at ρ −0.77, says a
scene whose collars oppose more is a scene the construction handles better. That is not a gate; it is an artefact of scenes with
more opposition also being scenes with more visible structure to continue from.

**Also falsified: S38's per-texel monotonicity does not survive the new scenes.** Reach is monotone on 2 of 6, lip spread on 2
of 6, opposition on 2 of 6. S38 saw L5 and L6 only.

## 4. The hybrid: a real improvement over the construction that still loses to the model

Switching per texel — keep the construction where the lips agree, take the learned model where they disagree — on the thing
class, with the model in S40's stable configuration (occluder mask, image blanked):

| scene | arm | model | hybrid |
|---|---|---|---|
| L5 | 0.3456 | **0.0685** | 0.1793 |
| L6 | 0.1119 | **0.0960** | 0.1147 |
| L7 | **0.0331** | 0.0405 | 0.0378 |
| L8 | 0.0777 | **0.0391** | 0.0392 |
| L9 | **0.0149** | 0.0387 | 0.0205 |
| **mean** | 0.1166 | **0.0566** | 0.0783 |
| **worst** | 0.3456 | **0.0960** | 0.1793 |
| **spread** | 23.1× | **2.5×** | 8.8× |

The gate **halves the construction's worst case and cuts its spread from 23× to 8.8×**, which is a genuine result. It also
beats the construction on only 2 scenes of 5 and the model on only 2 of 5, and it is worse than simply using the model
everywhere on both mean and worst case. The cost is precision: on L7 and L9 opposition fires on 45% and 32% of the band where
the construction was fine, and the swap makes those scenes worse.

**And no threshold rescues it.** Sweeping the opposition threshold from 1 to 128 visible steps moves the mean by less than
0.0005 m and leaves the tally at 2 of 5 against each rival at every value. The magnitude of the opposition carries no
information beyond the fact that it is non-zero, so there is no tuned version to be tempted by.

## 5. What the two tables together say, which is new

S39 and S40 scored the thing class. Putting the whole band beside it changes the conclusion:

| whole band | L5 | L6 | L7 | L8 | L9 |
|---|---|---|---|---|---|
| our construction | 0.2383 | **0.0154** | **0.0614** | **0.0921** | **0.0005** |
| the model (occ, grey) | **0.0976** | 0.2052 | 0.0791 | 0.1412 | 0.0763 |

**The construction wins the whole band on four scenes of five, and loses the thing class on three of five.** The model's
advantage is confined to the hidden-thing class; on the background class our construction is exact and the model is nowhere
near it. So "use the model everywhere", which the thing-class table appears to recommend, would wreck the class we already get
right — on L9 by a factor of 150.

**The decision is therefore not per scene and not per texel. It is per class.** S38 concluded the missing piece was a scene
classifier; S42 says the missing piece is a *class* discriminator — is this band texel backed by a thing or by background —
and that is precisely what the object map determines, which §52 and §56 already established is the input that decides
everything. The gate we have been hunting for four notes may be the object map wearing a different hat.

## 6. A concrete demonstration of R7's scoring item

L1's whole band reads **0.0112 m / 0.0198 d**; L6's reads **0.0154 m / 0.0106 d**. In metres L1 looks better than L6; in the
app's own normalised depth L6 looks better than L1. **The metre score reverses a ranking between two real scenes.** That is
S38's warning observed rather than argued, and it is the case for doing Sprint 23 before any further comparison.

## What I would conclude

- **Delivered:** the first observable that separates the construction's error by two orders of magnitude, where it applies.
  Opposition is a sound one-sided per-texel confidence — when the collar opposes, do not trust the sheet.
- **Not delivered:** a gate. Five attempts now (§57, S36, S38, S39, S42) and no observable orders the scenes.
- **Falsified:** the scene-level collar aggregate, in the wrong direction; the tunable opposition threshold; and S38's
  per-texel monotonicity as a general property rather than a two-scene one.
- **New:** the contest is class-level, not scene-level. That reframes Sprint 27 and connects it to the object layer of S27.

**Recommendation.** Do not spend another note on a scene gate. The next thing that would move this is Sprint 28, the meadow
reframing — one mask over the whole merged field, ask for the surface behind — because it attacks the input that S42 now
identifies as decisive rather than trying to detect its consequences. Phases A and B still come first.
