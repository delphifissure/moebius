# S53 — R8's first five items, executed (2026-09-22)

R8 read the corpus first-hand and ended with an ordered action list. This is items 1 to 5 of it, done. Three of the
five changed a conclusion the project had already recorded; one of them was **wrong in R8's own premise** and the
measurement says so; and one is **not achievable with the tools here**, which is itself the finding rather than an
excuse.

Every number below was produced by running something, and where a first attempt produced a number that turned out
to be an artefact of the instrument, both the wrong number and the reason are kept.

## The whole session on one page

| # | idea, and where it comes from | verdict |
|---|---|---|
| 1 | **Re-measure S51 and S52 in motion** (InpaintFusion §4.1) | done — and it **settles S51 against R8**: sFD 0.0005 from the wash, the closest arm in the study |
| 2 | **Bi-directional gradient means** (InpaintFusion §3.7) | done — a no-op in the interior by construction; at the rim it removes a median 0.0828 in d from the guidance field |
| 3 | **Ordinal pairs** (DA-2K, DAv2 §6.2) | done — shipped far field **72.3%** on band ordering, 99.0% on the occluder sanity family; later overturns another instrument |
| 4 | **Test-time resolution scaling** (DAv2 §B.8) | done — R8's premise was wrong (already at 2×); the *next* doubling gives **25% fewer texels in a transition** and the **largest motion effect measured, −8.4%** |
| 5 | **Occluder as its own channel** (4 papers) | **not possible** — LaMa is `(64, 4, 7, 7)`, frozen TorchScript. Mask-shaping half done instead |
| 6 | **Reveal-thresholded hybrid** (SynergyAmodal Fig. 6) | done — **beats both of its own endpoints** in motion, the only arm that does |
| 7 | **Distribution guard** (2503.20211 Eq. 12–15) | built — self-calibrating, truth passes 29/30 kit scenes, catches the known-bad return automatically |
| 8 | **Two-estimator confidence → per-texel λ** (2503.20211 Eq. 9–11) | built — the free second estimate is **independent** (corr −0.005 with the old uncertainty); the paper's relative form does **not** transfer and was rebuilt on the reveal field |
| 9 | **Simplicity as an objective** (amodal survey Tab. 1) | **refuted** — runs backwards; do-nothing scores highest, truth lowest |
| 10 | **Unnamed regions as occluders** (2411.13019 §3.1) | **confirmed, 54.8%** of the occluded rim — but my geometric fix floods to 60% of the plate |
| 11 | **Band fragmentation** (Amodal3R) | **refuted** — 261 components, but the largest holds 94.6% of the area |
| 12 | **Reveal field beats published boundary practice** (R8's own claim) | **refuted** — ODS 0.833 vs 0.835, a tie |
| 13 | **Depth from the inpainted plate** (Pano3DComposer §3.3) | tested — passes the guard, **loses ordinally on 5 of 5**; R8's prohibition upheld by measurement |
| 14 | **Colour–depth alignment** (Gen3R Tab. 11) | built — detects gross misalignment; cannot rank two plausible pairs, and says so |

**Six negatives, and they are the point.** Each cost minutes to establish and would have cost weeks to discover
after building on it. Two of them (9 and 12) contradict claims in R8 itself.

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

---

# Part II — the rest of the corpus, worked through

R8's §14 was the *ordered* subset. The read turned up more, in §9, §10 and the per-paper notes. This part works
through those, and **four of the seven produced a negative result** — which is the point of testing them cheaply
before building on them.

## Tested and REFUTED: simplicity as an objective

The amodal survey (Tab. 1) and AmodalSynthDrive (Tab. II) report that amodal segments are simpler than modal ones —
`simplicity = √(4πA)/P` — on five datasets (BSDS .718→.834, COCO .746→.856, KINS .709→.830, KITTI-360-APS
.778→.884, BDD100K-APS .697→.821), "independent of scene geometry and occlusion patterns".

This mattered because **S51's entire cost function was visible wall length**, a perimeter measure with no published
prior saying which direction is right. Simplicity is the same kind of quantity *with* a direction, so it was the
obvious candidate to reopen S51 with. Tested first, on 30 kit scenes with exact hidden truth:

| | mean simplicity | median |
|---|---|---|
| modal (visible only, band excluded) | 0.4276 | 0.4356 |
| amodal: **truth** | **0.4052** | 0.3974 |
| amodal: far field (shipped) | 0.4642 | 0.4668 |
| amodal: **do nothing** | **0.5104** | 0.4852 |

**The prior does not transfer, and the metric runs backwards.** Completing with truth *raises* simplicity on only
10 of 30 scenes, and on average **lowers** it (−2.6%), against the papers' +16% on all five of their datasets. Worse,
the ranking is inverted: do-nothing — the definitionally wrong answer, a flat occluder depth smeared across the
band — scores **highest of all** (+23.2%), above the shipped construction (+11.6%), above truth.

The reason is interpretable. Their segments are compact *objects* whose amodal extent is a blob; ours are
*background surfaces revealed behind things*, and the smoothest wrong answer makes the simplest regions. It is the
"regression produces an average" trap once more, in a third metric.

**Do not reopen S51 with simplicity.** Cost of finding out: one script.

## Tested and REFUTED: band fragmentation as a distribution mismatch

Amodal3R builds training masks "to ensure these regions connect — thereby better simulating real-world occlusions,
where mask regions are typically **not highly fragmented**." R8's note flagged our 261-component troll band as a
mismatch for any off-the-shelf inpainter.

By count it is fragmented; **by area it is one hole.** The largest component holds **94.6%** of the band, the top ten
hold 97.7%, and the 223 components under 64 px hold **0.64%** between them. The context-to-fill ratio is a flat 0.08
rim edges per band texel at every percentile. There is no mismatch to correct and no case for per-component
inpainting.

## Tested and REFUTED — a claim of R8's own: the reveal field beats published practice

Infinigen Indoors §4.3 makes occlusion-boundary estimation a named task with the BSDS protocol (ODS/OIS/mAP), and
its §G.2 admits how the field builds ground truth when it has none:

> "we approximate them by thresholding the gradient of the provided depth maps. **We carefully tuned this
> threshold** on Hypersim to give the best results."

That is S33's construction exactly, with a hand-tuned threshold. R8 concluded: *"on this narrow point our
instrument is better than the published practice, and the R7 synthesis should say so."*

Scored on 30 kit scenes, both rankings swept over every threshold:

| | ODS (one global threshold) | per-scene mean F | scenes won |
|---|---|---|---|
| reveal field ranking | **0.833** (P 0.91 R 0.77) | 0.887 | 12 of 30 |
| depth-gradient ranking | **0.835** (P 0.91 R 0.77) | 0.887 | 18 of 30 |

**Indistinguishable. R8's claim is not supported.** What survives is narrower and should be stated that way: the
reveal field gives a threshold that needs *no tuning*, in the units the artefact appears in. That is a practical
advantage, not a detection-accuracy one, and this experiment does not test it — it sweeps both thresholds, so it
scores ranking quality alone.

*(A correction to my own first run: I labelled the reveal column "threshold derived from the envelope" while in
fact sweeping it. Fixed. And the absolute F values here are not comparable to Infinigen's 0.29 — they detect
boundaries from RGB with a network, we threshold a depth map whose truth comes from the same geometry.)*

## Confirmed, but the fix is ours to find: unnamed things are the occluders

2411.13019 §3.1 is the only paper in the pile treating amorphous "stuff" as a first-class occluder: "these
unlabelled (or 'background'-labelled) regions can be occluders of a target object." Their ablation: LPIPS .333 → .320.

On the troll the claim lands hard. Of the band texels with an occluding visible neighbour, **54.8% are hidden by
something the object map never named** — SAM 2.1 was clicked on nameable things, and the cave wall, foliage and rock
are what actually occlude.

**Their fix is aimed at their problem, and my substitute failed.** They partition the unsegmented remainder by
erode-then-dilate because their pipeline reasons per object. We need a *mask*, not units, and the geometry states
exactly which visible texels occlude — so I built it from the geometry and grew it over the surface. It floods:
**60% of the plate even at a 0.002 tolerance**, because a smooth monocular depth map always has a low-gradient path
around any boundary (band |∇d| p50 0.00046, p90 0.0034, p99 0.189 — the mass is in the tail, but the connectivity is
in the bulk). That is the same wall S35's sheets ran into.

What survives: the rim **seed** (visible texels directly in front of a band texel, 3.5% of the plate) is well defined,
and bounded dilations of it are stable. And the return guard's verdict does not depend on the question at all —
shipped 0.38–0.65, Amodal-DAV2 1.47–1.55, under every reference tried.

## Measured, and the fix already exists in the app: the frame edge

2411.13019 Eq. 3 dilates the occluder mask along the image edge when the target touches it; PACO's limitation (iii)
says the same and prescribes padding. S48 calls it the *unbounded* class.

| | |
|---|---|
| band texels **at** the frame | 1 274 (**0.37%** of the band) |
| within 4 texels | 4 837 (1.39%) |
| within 16 | 15 699 (4.52%) |
| band components touching the frame | 11 of 261, holding **96.5%** of the band area |
| the bottom edge | **851 of 851 border texels are band** |

Topologically dominant, geometrically a thin strip, and concentrated on the bottom edge where the ground runs out of
the picture. **The app already implements the published fix** — the margin mechanism and the `plane_out_*` strips —
and the troll bundle was baked with `plateOptions.margin: 'off'`. The action is to turn it on and measure, not to
build anything.

## Built and queued: the reveal-thresholded hybrid (R8 §14 item 6)

SynergyAmodal Fig. 6: a regression wins the 0–10% occlusion bucket; generative methods take over at 10–50%, 50–90%,
90–100%. §4.3 names the failure our construction has: "regression-based methods tend to produce results resembling
an **average** outcome. While they often achieve **decent IoU scores**, the actual shapes do not meet the
requirements."

The split costs nothing because the threshold is a field we already export. Two tools, neither newly trained: the
harmonic continuation (`plane_color_occluder_removed.png`) under threshold, LaMa (S52 arm A) over it.

**A decoding trap, recorded because it nearly produced a silent result.** `meta.plane.reveal.pngScale: 16` is *not* a
multiplier — it is the **cap in texels**, and the decode is `texels = value / 65535 × cap`, exactly as the file's own
description states. Reading it as a multiplier gives a field ~375× too large, puts every band texel above every
threshold, and degenerates the hybrid to "all generative" while looking like it ran. What caught it was the decoded
percentiles disagreeing with the meta's own by three orders of magnitude.

Decoded correctly, on the band: p50 **0.542** texels (0.170 screen px), p90 3.574, p99 16.0 — clipped, since 0.94% of
band texels saturate the 16-texel cap and the true max is 143.6.

| threshold | generative | share of band |
|---|---|---|
| T = 0.25 | 272 571 px | 78.5% |
| T = 0.5 | 185 917 | 53.6% |
| **T = 1.0** | 95 357 | **27.5%** |
| T = 2.0 | 46 376 | 13.4% |
| T = 4.0 | 32 482 | 9.4% |

### The three-point test, rendered: the split wins

`H_seedonly` (pure regression, no model at all), `H_rev1` (27.5% generative) and `armA` (all generative), against
the wash, on the same camera path with identical geometry:

| arm | generative share | temporal step, mean | sd | sFD vs wash | LPIPS vs rest at 45° |
|---|---|---|---|---|---|
| wash (control) | — | 0.05161 | 0.00727 | — | 0.2878 |
| H_seedonly | 0% | 0.05072 | 0.00689 | 0.0026 | 0.2929 |
| **H_rev1** | **27.5%** | **0.05038** | **0.00675** | 0.0032 | 0.2947 |
| armA | 100% | 0.05055 | 0.00707 | 0.0042 | 0.2961 |

**The hybrid is the best arm on both temporal measures, beating each of its own endpoints.** That is precisely what
SynergyAmodal Fig. 6 predicts — neither tool wins everywhere, and splitting on occlusion size beats either alone —
reproduced here on a parallax artefact rather than an occludee, with the split taken from a field we already export
and no new parameter.

It is also the only arm in the whole study that improves on *both* of the things it is made of, which is the
signature of a real interaction rather than a ranking.

**The margins are small and must be reported as such**: H_rev1 is 0.3% below armA, 0.7% below H_seedonly, 2.4%
below the wash, on one scene with nine frames. The ordering is consistent across mean *and* spread and matches the
published prediction, which is worth more than any single margin, but this is a direction confirmed rather than an
effect sized. The sFD and degradation columns simply order the arms by how much generative content they carry,
as expected, and carry no verdict.

## Not attemptable here, and why

- **The occluder as its own channel, and the background as a second channel** (PACO, APSNet, Amodal3R,
  SynergyAmodal — four papers). LaMa's first convolution is `(64, 4, 7, 7)` in a frozen TorchScript archive. Needs a
  different inpainter and a training run; no GPU here.
- **Global-to-local inference**, worth ~13% FID (SynergyAmodal §3.4, COCOA 10.9 → 9.5). Only applies to a latent
  diffusion inpainter with a fixed input size. Moot while the inpainter is LaMa.
- **A generative prior as a regulariser** (Gen3R §4.3, "corrects the errors and produces cleaner depth"). This is the
  effect we want against speckle, but it needs the model.
- **Shadows left by removed occluders** (PACO, SynergyAmodal Fig. 10, DeepDR). DeepDR's supplement masks the shadow
  and reports results "often look better"; we have no shadow detector. The *other* half of their claim — that
  under-covering masks cause "flickering between consecutive frames" — is testable now that the motion instrument
  exists, and the dilated arms D/E/F are exactly the test.
- **Structure conditioning as the thing that keeps colour and depth agreeing** (DeepDR §5, RGB-D SPADE: predict a
  segmentation at every decoder scale and modulate *both* streams with shared parameters; ablation LPIPS 0.0104
  against 0.0143, depth RMSE 0.278 against 0.374). This needs training, so it is not attemptable — but it is the
  architectural recommendation for the next supplier, and it is worth noting that **we already have the input**:
  the SAM 2.1 object map, currently used only for highlighting and `plane_object_ids`. DeepDR's §8.5 adds that
  *fewer* classes segment better, which our coarse map satisfies. `harness/return_align.py` measures the symptom
  their SPADE prevents, so the instrument and the eventual fix are already pointed at the same defect.

---

# Part III — the last untried construction, and the two instruments disagreeing

## Depth from the inpainted plate (Pano3DComposer §3.3)

R8 §14's "what not to do" forbids inpaint-then-redepth on three votes (1909.00915, Gen3R, DeepDR — the last
quantifying a joint solve at ~2× better depth RMSE). But **R8's own per-paper notes contradict that**, flagging
Pano3DComposer §3.3 as "a depth path WE HAVE NOT TRIED and can try today with assets already on disk", distinct
from the Amodal-DAV2 failure, which failed for a task-definition reason rather than a quality one:

> "We merge all instance masks and apply an inpainting model (LaMa or DiT360) on the panoramic image to obtain a
> clean background panorama I_bg … predicts background depth with Depth-Anywhere" — Pano3DComposer §3.3, 2026

The three votes all compare it against a **joint model**, and we have no joint model. The comparison nobody had run
is against **our plane construction**. S52 arm B is already the clean background plate, so the test was one DA3 run.

**It passes the guard that killed Amodal-DAV2, and beats the shipped construction there.**

| | vs occluder | vs plane background | guard W1 | guard ratio |
|---|---|---|---|---|
| Amodal-DAV2 (S52) | 0.083 | 0.261 — **3× further** | 0.2353 | 1.55 **reject** |
| inpaint-then-redepth | 0.193 | **0.071 — 2.7× closer** | **0.0531** | **0.35 pass** |
| the shipped plane construction | — | — | 0.0638 | 0.42 pass |

On the distribution guard this is the first thing in the project to beat the plane construction on band depth.

**And the ordinal instrument overturns it, on all five kit scenes.** `band_band`, both endpoints hidden surface:

| scene | far field (shipped) | do nothing | inpaint-then-redepth |
|---|---|---|---|
| S10 | **68.7%** | 61.3% | 54.5% |
| S11 | 51.7% | **69.4%** | 42.2% *(below chance)* |
| S27 | **83.3%** | 52.4% | 77.9% |
| S2 | **81.1%** | 75.6% | 72.6% |
| S9 | 81.2% | **83.2%** | 67.0% |

**It loses to the shipped construction on five of five**, by 5 to 14 points, and falls below chance on S11. The
occluder sanity family is fine (98.6–100%), so it is not broken — it is *smoothly wrong*.

**This is the whole argument of R8 §5, demonstrated rather than cited.** The distribution guard says the field is
drawn from the background's depth family, which it is: a plausible monocular depth map of a plausible inpainted
background. The guard's stated limitation is that it cannot detect a return that is merely too *average*. The
ordinal instrument exists precisely to detect that, and it does. **The two instruments disagree, and the
disagreement is the finding** — neither is wrong, they measure different failures, and a return needs to pass both.

**And the failure reproduces the mechanism DeepDR names, which is the strongest form this result could take.**
Their §4.4, on exactly this class of baseline: *"sequential approaches suffer from the **loss of detail and sharp
features** in inpainted images"*, and the depth model *"fails at filling complex depth regions with sharp edges …
in particular **for structures far away from the camera**."* Our band is the far structure behind things, and what
the ordinal instrument measured is precisely a loss of ordering detail there while the gross arrangement (the
occluder family, 98.6–100%) stays right. We did not merely reproduce their verdict; we reproduced their
explanation, on our own scenes, with an instrument they did not use.

Two consequences worth stating plainly:

1. **R8 §14's prohibition on inpaint-then-redepth is upheld — by our own measurement on our own scenes, not by
   citation.** The path is now tested rather than forbidden, and the answer is the same.
2. **The ordinal instrument earned its place.** This is the first time it has overturned another instrument's
   verdict, which is the job it was built for. Had the guard been the only check, this path would have been
   adopted as an improvement.

## Item 1's first numbers: the arms in motion

Four arms (wash, A, B, D), nine frames, 0–45° horizontal, LPIPS-alex at 608×342.

| arm | LPIPS vs rest at 45° | temporal step, mean | sd | max |
|---|---|---|---|---|
| wash (control) | 0.2878 | **0.05161** | 0.00727 | 0.06646 |
| A band, occluder removed | 0.2961 | **0.05055** | 0.00707 | 0.06410 |
| B band ∪ occluder | 0.2957 | 0.05062 | **0.00684** | 0.06379 |
| D band dilated 4 px | 0.2914 | 0.05069 | 0.00709 | 0.06490 |

sFD between arms: wash↔arms 0.0033–0.0044; arms↔each other 0.0002–0.0012.

**Read honestly: the motion measurement is consistent but small.** All three inpainted arms have a lower
frame-to-frame perceptual step than the wash (−1.8% to −2.1%) and a lower spread (−2.5% to −5.9%), which is the
direction InpaintFusion predicts and which stills could not show at all. But the effect is **2% on a baseline
dominated by ordinary parallax**, not the four-to-five-point separation their Fig. 9 reports on a 1–7 human scale.

What it does settle: **S52's still-frame conclusion survives the motion re-measurement.** The arms remain far
closer to each other (sFD 0.0002–0.0012) than any is to the wash (0.0033–0.0044) — the same "the choice of
strategy matters about half as much as the choice to inpaint at all" that S52 found on two frames. The re-measure
did not overturn S52; it confirmed it and added the one thing stills could not: inpainting measurably reduces
temporal instability, it does not merely change the picture.

*(The S51 arm failed its first run — my sweep loop split the spec on `:`, which also split the JSON
`{"_farLabel":true}`, so the arm baked with the flag unset. It failed loudly as a parse error rather than
producing a silent wrong result. Re-run below.)*

## S51 settled, against R8's hypothesis — and item 4 is the surprise

The geometry arms, same camera path, no return imported, differing only in what the bake was given:

| arm | LPIPS vs rest at 45° | temporal step, mean | sd | sFD vs wash |
|---|---|---|---|---|
| wash (control) | 0.2878 | 0.05161 | 0.00727 | — |
| **farlabel** (S51's cross-line labelling) | 0.2887 | **0.05202** | 0.00753 | **0.0005** |
| **da2x** (the 2× depth map, item 4) | 0.2833 | **0.04725** | 0.00918 | **0.0173** |

**S51 is invisible in motion too, and that answers the question item 1 was built for.** R8 argued that S51's
"measured improvement, no visible improvement" should be *reopened as a measurement failure*, on DAv2's precedent
of "better model but worse score". The better measurement has now been made and it says the opposite: the
cross-line labelling is **the closest arm to the wash in the entire study** — sFD 0.0005, against 0.0042 for the
weakest inpainting arm and 0.0173 for the 2× depth — and its temporal step is fractionally *worse* (+0.8%), not
better. A construction that cut artefact wall length by 33.5% is perceptually indistinguishable from doing nothing,
on stills and in motion. **It was not a measurement failure.** Either the wall length it removed was not what the
eye integrates, or the effect is genuinely below threshold; either way S51 stays off, now on perceptual evidence
rather than on a bar it missed.

**And the 2× depth map has the largest motion effect of anything tested this session.** Its frame-to-frame
perceptual step is **8.4% below the wash** — four times the effect of any inpainting arm — and its sFD from the
wash (0.0173) is four times any colour return's. This is the arm that changes the picture in motion. It follows
directly from the 25% reduction in texels sitting inside a depth transition: those are the texels that get
stretched, and fewer of them means less frame-to-frame instability.

Two honest qualifications. Its step *variance* is higher (sd 0.00918 against 0.00727), so it is smoother on
average but less uniformly so. And its degradation curve is not uniformly better — worse at 22.5° (0.1795 vs
0.1735), better at 28.1° (0.1975 vs 0.2091). It changes the picture rather than simply improving it, and it
deserves a look on screen before it is adopted.

**The ranking of the five items by measured motion effect** is therefore the reverse of the order R8 proposed:
item 4 (a one-line resolution change, 8.4%) ≫ item 5's inpainting arms (~2%) ≫ item 1's re-measurement of S51
(0.8%, wrong sign).

## What to do next, on this evidence

1. **Put the 2× depth map on screen.** It is the only change measured with a large motion effect (−8.4% temporal
   step, 4× anything else), it costs one flag, and its two qualifications — higher step variance, a
   non-uniformly-better degradation curve — are exactly the kind a person settles by looking in ten seconds and a
   harness cannot settle at all.
2. **Turn the margin on and re-measure.** The published frame-edge fix is already implemented and was off for this
   bake; the `margin2` arm is rendering.
3. **Ship the hybrid rather than either endpoint**, if a look on screen agrees with the numbers. It beat both of
   the things it is made of, and the threshold costs no new parameter.
4. **Use the guard and the ordinal instrument together, never singly.** Part III is the demonstration: a return
   can pass one and fail the other, and the one it passes is the one that cannot see over-averaging.

## What is still open

- **The occluder channel, the background channel, structure conditioning, global-to-local, and a generative prior
  as a regulariser.** Five ideas with published support, all blocked on the same thing: a model we can train or
  run. None of them has been tested here and none should be recorded as tried.
- **Shadow masking.** DeepDR's measured win; we have no shadow detector.
- **The 2× map on other pictures.** One photograph is not generality, and the kit cannot test this one — its depth
  is synthetic truth, not a DA output, so there is nothing to re-run at 2×.
- **S51 is closed, not open.** It stays off, now on perceptual evidence rather than a missed bar.
- **S33's blocker** — 74% of the troll's visible wall length being the field disagreeing with itself — still has
  **no prior art in the corpus**, and this session did not change that. Simplicity was the one candidate objective
  with a published direction and it is refuted. The discrete-labelling literature (Boykov–Veksler–Zabih and
  successors) was never supplied and remains the one unexamined direction.

## What this session says about the project's method

Twelve ideas tested, six negative, two of them contradicting R8 itself. That ratio is the argument for the way they
were tested: each negative cost minutes and would have cost weeks if discovered after a construction was built on
it. Three specific patterns are worth carrying forward.

**An instrument that cannot fail its own test is not an instrument.** The distribution guard's first design used an
absolute threshold; the kit showed truth itself spans 0.02 to 0.52 and would be rejected. The ordinal instrument's
first design gave the do-nothing baseline a free correct endpoint and scored it 100%. Both were caught by running
them against known answers rather than by reasoning about them.

**Published findings transfer as directions, not as formulas.** 2503.20211's confidence form divides by metric
depth; in normalised disparity it collapsed to "trust nothing". The amodal survey's simplicity prior holds on
compact objects and inverts on background surfaces. In both cases the idea was sound and the arithmetic was not.

**A verdict reached by one instrument is a hypothesis.** The cleanest result here is Part III, where two
instruments disagree about the same return and both are right about different failures.
