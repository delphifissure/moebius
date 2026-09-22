# S53 — R8's first five items, executed (2026-09-22)

R8 read the corpus first-hand and ended with an ordered action list. This is items 1 to 5 of it, done. Three of the
five changed a conclusion the project had already recorded; one of them was **wrong in R8's own premise** and the
measurement says so; and one is **not achievable with the tools here**, which is itself the finding rather than an
excuse.

Every number below was produced by running something, and where a first attempt produced a number that turned out
to be an artefact of the instrument, both the wrong number and the reason are kept.

---

## Item 2 — the exporter's one-sided gradients (`harness/return_grad.py`)

**R8's claim was half wrong and the half that was right is bigger than it looked.**

R8 said the defect was in "moebius.js and `harness/s52_depth.py`". It is not in `moebius.js`: that file only
*consumes* gradients (`_screenedPoissonBand`, ~10740), and its divergence `gx[i] − gx[i−1]` is the correct staggered
Poisson form for an edge-centred gradient. The only producer was `s52_depth.py`.

InpaintFusion §3.7, in their words:

> "directly sampling pixels from f\* will introduce inconsistencies: Consider a pixel at u and its right neighbor at
> u+v. A naive horizontal gradient will usually not match the sampled depth gradient of the adjacent pixel,
> d(f\*(u+v)) − d(f\*(u+v) − v). Therefore, we minimize […] where Ê is the mean bi-directional depth gradient sample."

**On a dense field this is a no-op, and that had to be established before anything else.** Their f\* is an exemplar
shift map, so two adjacent target pixels can be copied from unrelated places. Ours is a dense prediction, and for an
edge with both endpoints in the same field the forward difference *is* the within-source estimate. The self-test in
the module asserts this identity, so only one thing can move.

**What moves is the rim, and the rim is a composite of two sources**: observed plate depth outside the band, model
prediction inside. Every edge straddling it was a cross-source difference — the literal case the paper says to
avoid, at the one place in the picture where a wrong gradient does the most damage.

Measured on the troll bundle (851×1023, band 39.9 %):

| | naive forward difference | bi-directional mean |
|---|---|---|
| median \|g\| on the 42 586 crossing edges | **0.0828** in d | **0.0004** |
| divergence over the band, mean \|·\| | 0.0491 | 0.0317 |
| divergence over the band, p99 | 0.5682 | 0.3347 |

The crossing edges are 2.45 % of all edges. The whole rim step was entering the guidance field, and a Poisson solve
then reproduces it one texel inside the band.

**Is the step real geometry being erased? No — checked rather than assumed.** Split by which side is nearer:

| | count | share | \|step\| median |
|---|---|---|---|
| outside nearer than the band (an occluder cliff) | 39 723 | 93.3 % | 0.0907 |
| outside within 0.01 of the band (same surface) | 2 725 | 6.4 % | 0.0056 |
| outside farther than the band | 138 | 0.3 % | 0.0151 |

70.7 % of the crossing edges step more than 0.05 in d. The correction removes cliff; on the 6.4 % that are genuine
same-surface continuity the two estimates agree to 0.006 either way, so continuity across the far-side rim survives.

**The app already applies this rule to the other half of the return.** `_shiftBandComponents` takes the rim law's
far-side neighbours only, because — the comment's own words — "anchoring on it makes the shift absorb the cliff".
The gradient guidance had no such protection. This is that rule, applied to the gradient half.

---

## Item 3 — the ordinal-pair instrument (`harness/truthkit/ordinal_pairs.py`)

Built on DA-2K's protocol (DAv2 §6.2, C.3): sparse pixel pairs, "which is nearer", a ratio rule that keeps only
unambiguous pairs, results split by scenario rather than pooled. R8 called it "the most concrete new instrument in
the whole read" and it is the one that produced the most.

**Two design errors were caught by running it, not by reasoning about it.** Both are recorded in the module because
both would have produced a plausible, publishable, wrong table.

1. *Candidates must be composited with the observed depth outside the band.* `farField.f32` is only defined on the
   band's free texels, and `dQ` **is** the truth outside the band by construction. Scoring the raw arrays gave the
   do-nothing baseline a free correct endpoint: it scored **100.0 % on `visible` and 99.4 % on `rim`**, which
   measures nothing at all. Composited, every candidate agrees outside the band and each family isolates the
   construction.
2. *Rim pairs must be adjacent texels.* A random visible neighbour within 6 px mixes the occluder side of the
   silhouette with the background side — two opposite geometries — and the ratio filter then keeps a biased subset
   of whichever dominates. That family scored **4.0 % on one scene and 31.2 % on another** for reasons entirely
   about the sampling.

**A third finding came out of fixing the second.** With adjacent pairs, DA-2K's ratio rule leaves the rim almost
empty — 72, 74 and 1 surviving pairs on three scenes. Adjacent texels across a disocclusion rim almost never differ
by 1.5× in depth. That is not a bug: **it says the rim question is genuinely ambiguous at the pixel level**, and an
instrument that keeps only pairs humans would agree on must decline to answer it. The families that do answer are
`band_band` (both endpoints hidden surface — the construction isolated) and `occluder` (sanity).

### The table: 29 kit scenes with `env45` truth

`band_band`, both endpoints hidden surface; `occluder`, the sanity family. Chance is 50 %.

| | far field (shipped) | do nothing |
|---|---|---|
| **band_band** mean | **72.3 %** | 57.4 % |
| band_band median | 71.7 % | 60.3 % |
| band_band min | 42.8 % (S15) | 5.2 % (S5) |
| below chance | 1 of 29 scenes | — |
| **occluder** mean | **99.0 %** | — |
| occluder min | 92.3 % | — |

Per scene, the shipped far field beats do-nothing on **18 of 29** and loses on **10**. Scenes where it is at or
below chance: S15 42.8 %, S11 51.5 %, S26 53.1 %, S5 57.5 %.

**What this says, stated carefully.** The shipped construction is *reliably right about what is in front of what* —
99.0 % on the occluder family, and it never confuses the hidden surface with the thing hiding it. Its **ordering
within the hidden surface is 72 %**, and for scale DA-2K's own Table 3 puts Marigold at 86.8, DAv1 at 88.5 and
DAv2-G at 97.4 on their benchmark. "Beats do-nothing on 18 of 29" is also a low bar: do-nothing puts the whole band
at the occluder's depth, so on band-internal pairs its ordering is close to arbitrary (5.2 % on S5). The number to
carry forward is **72 %, not the win-loss record**.

This is the first instrument in the project that scores band depth on something other than a magnitude, and it
ranks constructions that the metre-error tables rank as equal.

---

## Item 4 — DA at 2× (`depth_da3mono16_2x.png`)

**R8's premise was wrong and the run log says so.** R8's list reads "Our plate is 851×1023 and we run DA at its
native short side 518." The shipped troll map was made by DA3-Mono-Large at `process_res=1008`, which is already
twice DA3's own default of 504 — `scratchpad/bakeoff/out/log.json` records it verbatim: *"process_res=1008 (default
504)"*. So the test that was actually open is the **next** doubling.

DAv2 §B.8, the claim being tested:

> "we surprisingly find that our model has the property of 'test-time resolution scaling up' … we can almost freely
> increase the image resolution at test time to produce more fine-grained depth maps."

Run on CPU: 1008 in 36 s, 2016 in 262 s.

| on the plate grid | shipped (1008) | rerun 1008 | rerun 2016 |
|---|---|---|---|
| gradient p50 | 0.00058 | 0.00059 | 0.00071 |
| gradient p99 | 0.01132 | 0.01132 | 0.00648 |
| gradient p99.9 | 0.11761 | 0.11761 | **0.13387** |
| strong edges (step > 0.02) | 891 | 891 | 586 |
| **texels inside a transition** | **1 951** | 1 951 | **1 463** |

**The rerun at 1008 reproduces the shipped map exactly**, which is the check that the resample path is the same one
the shipped map took; without it none of the 2016 column would mean anything.

**The quantity that matters is the last row, and it falls 25 %.** A depth boundary spanning several texels produces
texels whose depth is a blend of two surfaces. Those texels belong to neither, and when the viewer moves they are
stretched between the two — that *is* the streak. 1 951 → 1 463 is 25 % fewer texels available to be stretched.

The distribution moved coherently rather than just scaling: p50 up (more genuine fine texture), p99 down (fewer
mid-scale ramps), p99.9 up 14 % (true silhouettes steeper). Median transition width is unchanged at 2.00 texels, so
the gain is in *how many* boundaries are soft, not in the typical boundary getting thinner.

**Not yet done: the re-bake.** The map is written and ready; the bake and its band/streak rescore are the remaining
half of this item.

---

## Item 5 — the occluder channel, which cannot be done here

R8 asked for `plane_object_ids` to be fed to the inpainter **as its own channel**, on four papers' evidence. It is
not possible with LaMa, and this is checked rather than assumed:

```
torch.jit.load('big-lama.pt') -> first parameter
model.generator.model.1.ffc.convl2l.weight   (64, 4, 7, 7)
```

**Four input channels: RGB plus the mask.** The checkpoint is a frozen TorchScript archive, so the first convolution
cannot be widened in place, let alone trained. A fifth channel needs a different inpainter and a training run, and
there is no GPU here. **The channel is not tested, and nothing in this section should be read as testing it.**

What a fixed 4-channel model *can* be given is a better-shaped mask. Arm B is already occluder-informed in the only
way the interface allows. The new arms vary how much of the rim is withheld as context, since the band's outer rim
is the streakiest part of the wash and LaMa's context is exactly the pixels just outside the mask:

| arm | mask | mean \|Δ\| inside | px changed outside the mask |
|---|---|---|---|
| A band, occluder removed | band | 23.2 | **0** |
| B band ∪ occluder (PACO c) | band ∪ occ | 27.3 | **0** |
| C band on the raw wash (PACO a) | band | 82.8 | **0** |
| **D band dilated 4 px** | band ⊕ 4 | **20.0** | **0** |
| **E band dilated 12 px** | band ⊕ 12 | 25.4 | **0** |
| **F (band ∪ occ) dilated 4 px** | (band ∪ occ) ⊕ 4 | 41.5 | **0** |

All six respect the mask exactly, so the return contract's "colour on the mask and nowhere else" holds without the
app enforcing it — now verified across six masks rather than three.

---

## Item 1 — the arms rendered in motion

*(Rendering; this section is completed below when the sweeps land.)*

The instrument is `harness/s53_sweep.js` (a continuous path through the envelope, identical for every arm) and
`harness/s53_metrics.py` (LPIPS per frame, frame-to-frame temporal step, and a Fréchet distance between arms'
sweeps). The reason it exists is InpaintFusion §4.1:

> "As inpainting has no ground truth … quantitative assessment in inpainting is an open research problem … In
> addition, **spatio-temporal consistency cannot be judged from individual images.**"

and their Fig. 9, where three methods scoring 6/5/5 on stills separate by four to five points in motion, the planar
proxies getting *worse* and only the one with correct depth getting better. Fig. 14's caption: *"static images do
not clearly show the advantages of our method."*

**VFID is not computed and the substitute is not called VFID.** I3D weights are unobtainable in this environment
(three sources tried: 404, unreachable, 403) and there is no ground-truth video to compare against in any case. What
is computed is a Fréchet distance between two arms' per-frame AlexNet feature distributions — named **sFD** — and it
is weak: 1152 feature dimensions against ~9 frames, so the covariance is shrunk to be invertible at all and what
survives is closer to a mean-and-variance distance. It is a coarse ordering between arms, never a calibrated number.

Two honest limits on the render itself: the LPIPS backbone is **alex** (the vgg weights fail their hash through this
environment's proxy; alex is LPIPS's own recommended "best forward" configuration, so this is the standard choice
rather than a fallback), and the viewport is **608×342** rather than 912×513 because a frame at the envelope edge
costs minutes under SwiftShader on four cores. Every arm renders at the same size and the metrics are comparisons
between arms, so this costs resolution in the absolute numbers and nothing in the ordering.

---

## What is still open

- **The re-bake for item 4.** The 2× map exists; the bake and rescore do not.
- **Item 6, deliberately deferred by R8's ordering**: the reveal-thresholded hybrid fill (regression under the
  threshold, generative over it).
- **The occluder channel** needs an inpainter that accepts one. Nothing here tested the idea, only the interface.
- **S33's blocker** — 74 % of the troll's visible wall length being the field disagreeing with itself — still has no
  prior art in the corpus.
