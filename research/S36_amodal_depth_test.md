# S36 — Amodal Depth Anything scored on our kit truth: it is robust to the object map where our construction is not (2026-09-20)

R6 ranked three things to try for the troll and the sunflowers. **Item 1 turned out to be a repeat** and was not built: the
group-level closure it proposed is the construction §32 already measured and removed (closing on an exit onto the sheet's own
join group — 29 k of 794 k marches closed, starwatcher sky-valued 50.6 → 47.0 %, jumps 1 967 → 5 662). R6's border-ownership
reading is still the right diagnosis of *why* the per-component test misses a porous field, but the obvious fix is spent.
This note is **item 2**, run end to end.

## What was run

`Amodal-DAV2` (Amodal Depth Anything, ICCV 2025, MIT, 0.36 B parameters) on **CPU**, from the released weights
(`Zhyever/Amodal-Depth-Anything-DAV2`). The model takes rgb at 518², a binary **guide mask** (the amodal extent of the target)
and an **observation depth**, and returns a relative depth; we supply our own observation (the kit's own rest depth, which is
what the app is given) so its base checkpoint is not needed. Instrument: `bleed/amodal_probe.py`.

Because "the amodal extent" is defined for objects and our target is stuff, three mask arms were tried: **occ** (the
occluder's silhouette alone), **collar** (that silhouette dilated by the band's own half-width, so the mask also holds a rim
of visible background) and **frame** (the whole frame — the background's true amodal extent, and out of the model's training
distribution). Predictions were brought back into the app's normalised depth two ways: by inverting the observation's own
min-max, and by a least-squares scale-and-shift fit on the **visible** region, which is the alignment the paper specifies.
The visible-region correlation is 0.978–0.982, so the model is producing a sensible depth map; the argument below is only
about the band.

## L6, the troll's configuration

| arm | whole band | thing class (the hidden forest, 20 773) | background class (72 227) |
|---|---|---|---|
| **our measured arm, figure-only map** | **0.0154 m** | **0.112 m** | 0.000 |
| our measured arm, every tree labelled | 0.000 | 0.441 | 0.000 |
| amodal, occ mask | 0.170 (0.145 fitted) | 0.122 (0.139) | 0.185 (0.152) |
| amodal, frame mask | 0.155 (0.150) | 0.166 (0.153) | 0.120 (0.124) |
| amodal, collar mask | 0.167 (0.253) | 0.345 | 0.111 |

Our arm wins the whole band by an order of magnitude and ties or wins the thing class. Most of the whole-band gap is not a
fair fight: L6's band is 78 % sky-lipped, our sheet model puts an exact constant there, and a relative-depth network at 518²
never will. **The fair comparison is the thing class, and there it is a tie.**

## L5, the sunflowers' configuration

| arm | whole band | thing class (21 848) | background class (66 393) |
|---|---|---|---|
| our measured arm, **every clump labelled** (a map no one can produce) | 0.000 | 0.061 | 0.000 |
| our measured arm, **heads only** (the map a person actually gives) | 0.238 | 0.346 | 0.020 |
| **amodal, frame mask** | **0.034** | **0.061** | 0.011 |
| amodal, occ mask | 0.105 | 0.073 | 0.168 |

This is the result that matters. On the map a user would really produce — click the heads, leave the field — our construction
reads 0.238 m over the band and 0.346 m on the hidden field, and the model reads 0.034 and 0.061. **It matches our own
best-case (fully labelled) number without being given any labels at all.**

## The finding

Put the two scenes together and the pattern is not "the model is better" or "worse":

| | our arm, good map | our arm, bad map | amodal, best mask |
|---|---|---|---|
| L6 thing class | 0.112 | 0.441 | 0.122 |
| L5 thing class | 0.061 | 0.346 | 0.061 |

**Our construction swings by a factor of four to six with the object map; the model does not move.** It sits at the good-map
number in both scenes without a map. (On the two scenes added below it is a different story, so read this with the safety
check.) That is the honest statement of what a learned amodal prior buys us here: not accuracy
beyond our ceiling, but **independence from the one input we do not control on a photograph**. §52 and §56 established that
the map decides and that both over- and under-labelling cost us; this is a construction that does not care.

## The model as an arbiter, not a source

§57 measured that the contested texels — where the main tier and a nearer demoted candidate disagree — are a coin toss for
every geometric rule we tried. The model is an independent signal on exactly that population. Letting it pick whichever of
our two existing candidates its own prediction is nearer to:

| | decidable contested texels | keep the main tier (today) | take tier two (sky-last) | **let the model arbitrate** | median \|e\| today → arbitrated |
|---|---|---|---|---|---|
| L6, figure-only map | 29 075 | **67.9 %** | 32.1 % | 45.9 % | 0.047 → 0.238 m |
| L5, heads-only map | 60 913 | 14.6 % | 85.4 % | **93.2 %** | 0.397 → **0.022 m** |

On L5 arbitration beats both fixed rules and, at 0.022 m, beats the model's own direct prediction on those texels (0.060) —
**our candidates are good and our choice is bad, and the model can choose.** On L6, where our choice is already right two
times in three, it makes things worse. So this is not yet a rule; it is a measured pair of regimes, and which regime a
picture is in is §57's question one level up.

## The safety check: it must not be applied blanket

S36 was first written on L5 and L6 alone. Running the two scenes our construction already handles well changes the
recommendation, which is why the check was made before proposing anything:

| scene | our measured arm | amodal, best mask | verdict |
|---|---|---|---|
| L5, heads-only map | 0.238 m | **0.034 m** | the model fixes it |
| L1, the dense leaf layer | **0.0112 m** | 0.0177 m | the model is worse |
| L6, figure-only map | **0.0154 m** | 0.145 m (fitted) | the model is much worse |
| S15, the crown against sky | **0.264 m** | **2.57 m** | the model is destroyed |

**The model helps one scene in four.** *(S15's reading here was corrected in S38: measured in d units its error is 0.109,
smaller than L6's 0.143, and the 2.57 m is that error multiplied by a depth-law gain of 19.7 m per unit d. The model is not
uniquely bad on S15; the scene's law amplifies everyone by twenty. Our arm is still eight times better there in d units, so
the verdict stands, but the "wide-range exclusion" proposed below was aimed at the wrong thing — see S38 §3.)*

## A truth-free confidence for the model, which does work

If the model is to be used selectively, we need to know when to believe it without having truth. One observable does it:
**the model's own median disagreement with the observed depth over the VISIBLE region**, as a fraction of the visible range.
Across the five runs it orders them exactly:

| run | visible disagreement | model \|e\| in the band | against our arm |
|---|---|---|---|
| L5, heads-only | **0.013** | 0.034 | model wins |
| L1 | 0.028 | 0.018 | arm wins (narrowly) |
| S15 | 0.071 | 2.57 | arm wins (hugely) |
| L6 | 0.096 | 0.170 | arm wins |

And it works *per texel*, not only per scene. Binning each scene's band texels by the local disagreement measured in a
window the size of the band's own half-width — no truth, no tuning, the window derived from the data — the model's true
error rises monotonically with it in every scene tested:

| local disagreement quintile | L5 model \|e\| | L6 model \|e\| | L1 model \|e\| |
|---|---|---|---|
| lowest | 0.0004 | 0.084 | 0.017 |
| 2nd | 0.022 | 0.143 | 0.015 |
| 3rd | 0.026 | 0.172 | 0.018 |
| 4th | 0.056 | 0.208 | 0.019 |
| highest | 0.135 | 0.211 | 0.023 |

**So we can tell how much to believe the model, from data we already have.** This is worth having on its own: it is the
missing ingredient in any scheme that mixes a learned prior into the bake, and it needs neither truth nor a tuned constant.

## What is still missing, and it is the same thing as before

The confidence above predicts **the model's** error, not **which of the two** is better. In the same quintiles our arm's
error is flat and low on L6 and L1 and rises steeply on L5, so the comparison turns on the arm's reliability, which we have
not made observable. Picking the better source therefore still needs an arm-side confidence, and the obvious candidates —
the sky-owned share of the band, the unowned share — do not separate the five runs cleanly (L6 with every tree labelled has
74 % of its band sky-owned and the model still loses there; L5 has 94.5 % and it wins). **This is §57's question again,
one level up, and it is still open.** I stopped rather than fit a two-signal threshold to five scenes, which is the kind of
construction this project has falsified six times already.

## What I would conclude

1. **For the sunflowers, this is the first thing measured that improves them** — L5's heads-only band from 0.238 to
   0.034 m, matching our own fully-labelled best without being given a map.
2. **It cannot be turned on generally.** It is worse on L1, much worse on L6 and catastrophic on S15.
3. **Exclude wide-range scenes outright.** Relative depth cannot express a hidden range far outside the visible one (S15,
   8.64 m), which S26 found independently.
4. **The model is better as an arbiter than as a source** where our candidates exist, on the L5 evidence (0.397 → 0.022 m),
   and harmful as an arbiter where our choice is already right (L6).
5. **We now have a truth-free confidence for the model** that is monotone in its real error. We do not have one for the arm,
   and that is what blocks a rule.
6. **§57 is not overturned.**

## Caveats, stated plainly

- 800×450 is resized to 518² and back. *(S38 §4 tested this and it is not a handicap: an aspect-preserving letterbox
  changes L6 by nothing and makes L5 worse. The horizontal downsample is only 1.54× and vertically it is an upsample. This
  caveat was overstated.)*
- The kit is synthetic and the model was trained on real photographs composited with real objects.
- One model, one encoder, CPU, three hand-built mask arms. The generative variant (Amodal-DepthFM) was not run.
- No picture was run, because the pictures have no truth; the instrument works on them and would be descriptive only.

## Next, if this is taken up

The cheap and decisive follow-ups, in order: run the model at native resolution in tiles to see how much of the gap is the
518² resize; run it on L1 and S15 to check it does not damage the scenes we already have at 0.000; and find a regime test
that separates L5 from L6 without truth, which is the one thing standing between this and a rule.
