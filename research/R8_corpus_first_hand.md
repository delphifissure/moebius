# R8 — The corpus read first-hand: we were reading the wrong literature, and our instruments cannot see the defect we are chasing (2026-09-22)

**Supersedes R7.** R7 was a synthesis of four subagents' reports, presented as a reading; its own errata says so. This note is
a first-hand read of every file, beginning to end. Running notes with per-paper detail:
`scratchpad/readnotes/notes.md` (858 lines).

**The pile is 20 distinct papers, not 21.** `08418.md` is PatchRefiner (2406.06679) in an ECCV rendering, and is a strict
subset — it stops at the references, while the arXiv file also carries the supplementary. Checked line by line against every
figure and number.

---

## The four findings, before the detail

1. **We were reading the wrong literature, and the survey in the pile says so in one sentence.** Amodal completion is defined
   by autonomously identifying an occluded *object* and completing *it*. We compute a mask from geometry and want background.
   By the field's own definition we are doing general inpainting. Everything R7 organised around the amodal line was aimed at
   a neighbouring problem.
2. **The right literature is Diminished Reality, and its two central papers were in the pile unread.** InpaintFusion (2020) and
   DeepDR (2023), same group at TU Graz. Between them: our return contract arrived at independently five years earlier, a
   quantified verdict on inpaint-then-redepth, and the demonstration that our measurement apparatus is blind.
3. **S51's verdict is a measurement failure, not a construction failure.** Three independent papers say our metric family
   rewards blur; a fourth shows the artefact class is invisible on still frames and separates by 4–5 points in motion. S51
   measured a 21 % cut in wall length on two stills and concluded the construction wasn't worth shipping.
4. **The return contract is the best-supported thing this project has built.** Five papers independently put depth detail in
   the gradient domain, two of them weighting the gradient term above the value term by 2× and 10×.

---

## 1. The framing error, which is the root of the rest

> **Image Amodal Completion: A Survey** (2207.02062, Ao/Ke/Ehinger, CVIU 2023), §2.2, first sentence:
> *"General image inpainting methods restore a user-selected missing area in an image to create a visually-reasonable output,
> **without concern for which object(s) the missing region belongs to**. In contrast, amodal appearance completion algorithms
> **autonomously identify** the partially-occluded objects and their hidden regions that need to be reconstructed."*

Our band mask comes from the reveal field — geometry, not object identity. We do not care which object the band belongs to. We
want plausible background. **We are doing general inpainting.** The amodal line was never addressing our problem.

This is not a quibble about taxonomy; it explains the pattern of results:

- **AmodalSynthDrive** (2309.06547) — the paper that *introduced* the amodal depth task, and the dataset our own code path is
  named after (`src.models.amodalsynthdrive.dav2`) — excludes our case by construction. §III-C1: *"We limit depth estimation
  for amorphous regions to **directly visible portions only**, as these regions **lack the structure or identifiable features
  necessary for amodal prediction**."* Amorphous = stuff = wall, terrain, vegetation, sky. The background behind an occluder
  was deliberately ruled out of the amodal depth task *on the grounds that it is not predictable*.
- **Amodal Depth Anything** (2412.02336) confirms the task is "the depth of invisible parts of objects."
- **Open-World Amodal Appearance Completion** (2411.13019) built its evaluation set by *discarding* images where "background
  elements were occluded but primary objects were not" — i.e. it filtered out our case as out of scope.

So S52's depth half did not fail because of a guide mask or a model bug. It asked a question three papers independently say
that family of model is not for. **That is now settled and should not be reopened.**

**The survey also hands us two consolations.** §2.3.2 describes our task and calls it the easier neighbour: *"For small shifts
in view, usually only a few pixels near the edges of the visible objects need to be predicted."* And §5.3 lists our far-field
rule as an open future direction — *"treating the background as multiple planes and the objects as simple volumes"* —
which `window._farRule='plane'` has been for a year. §5.1 lists our truth kit as a gap the field has.

---

## 2. The literature we should have been reading: Diminished Reality

Two papers, same group (Mori, Schmalstieg, Kalkofen, Graz), both in the pile, neither read before this week.

### InpaintFusion (IEEE TVCG 26(10), 2020)

Remove a real object from a live RGB-D view, show what is behind, joint colour **and depth**, 6-DoF, real time. It is the
closest published system to what this project is building, and it predates everything else in the pile.

**It arrived at S48's return contract independently, in 2020.** §3.7: *"Since we cannot simply copy view-dependent depth
values, we use the normal map for inpainting 3D structure... For the depth values in the ROI, we compute ∇D̂, a gradient field
[Pérez, Poisson image editing] of the sampled depth values. We minimize [...] to calculate the inpainted depth map."* Their
stated reason is ours: absolute depth is "perspective and view-dependent," gradients are not.

S48 found the pure-gradient return beat the absolute return 2.57× and wrote it up as a local discovery. It is the published
construction. (R7's errata was right that InpaintFusion's gradients are *copied from real surfaces* rather than predicted —
that distinction stands and matters. But the gradient-domain-plus-Poisson choice, and the reason for it, is theirs.)

**A concrete defect in our exporter.** They warn that copied gradients are inconsistent forward versus backward: *"a naive
horizontal gradient will usually not match the sampled depth gradient of the adjacent pixel... Therefore, we minimize [...]
where Ê is the **mean bi-directional** depth gradient sample."* Our exporter writes one-sided forward differences
(`gx[:, :-1] = d[:, 1:] - d[:, :-1]`, both in `moebius.js` and `harness/s52_depth.py`). Fixable in an afternoon.

**Multiplicative rather than additive cost combination, explicitly to avoid tunable weights** — 3 parameters down to 1
(Fig. 12). A published instance of this project's own zero-tuning principle deciding an architectural choice.

### DeepDR (2312.00532, TU Graz, 2023)

Their Table 1 is our requirements list — Color / Depth / Structure / Temporal — and they are the first to tick all four.
Their introduction states our problem: *"image space inpainting is not sufficient for DR applications — depth information
needs to be coherently inpainted as well"*, and DR *"has strict requirements in adhering to the structural boundaries of the
underlying scene. This is conflicting with the tendency towards producing blurry results at ambiguous object boundaries."*

---

## 3. Inpaint-then-redepth is settled, and against

The question has been live in this project since S52. Four papers in the pile bear on it directly.

| paper | verdict | evidence |
|---|---|---|
| Counterfactual Depth (1909.00915) | against | *"Inpainting method does not work"*; loses to direct prediction |
| **DeepDR (2312.00532)** | **against, quantified** | see below |
| Gen3R (2601.04090) | against | their 2-Stage ablation "naively connects 2D generation with 3D reconstruction, leading to accumulated errors" — 1-view PSNR 17.38 vs 20.51, CD 1.6223 vs 1.1047 |
| Pano3DComposer (2603.05908) | for | uses LaMa-then-Depth-Anywhere for the background, no ablation, no comment |

DeepDR's baselines *are* the construction in question: RGB inpainting (DeepFillV2 / PanoDR / E2FGVI) followed by a
state-of-the-art depth-completion network (InDepth / NLSPN / DM-LRN) run on the inpainted colour. Depth RMSE:

| | DeepFillV2 | PanoDR | E2FGVI | DynaFill | **DeepDR (joint)** |
|---|---|---|---|---|---|
| InteriorNet | 0.572 | 0.564 | 0.563 | — | **0.278** |
| DynaFill | 7.92 | 8.12 | 7.83 | 7.78 | **4.51** |
| ScanNet | 0.508 | 0.536 | 0.512 | — | **0.484** |

Joint inpainting roughly halves the error. Their diagnosis: *"sequential approaches suffer from the loss of detail and sharp
features in inpainted images"*, and the baseline depth completion *"fails at filling complex depth regions with sharp edges
(e.g. between floors and walls), in particular **for structures far away from the camera**."* That last clause is our band.

**Consequence.** Do not fill colour and then run a depth model on the fill. If we want depth in the band it comes from a joint
solve, or from the contract's own gradient/Poisson path — which is what S45/S48 already built. Sprint 28's depth half should
not be retried as inpaint-then-redepth; it should be retried as a return that carries both, or not at all.

One quantification worth keeping from the same paper (supplementary §7.4, Tab. 10): the same model on *visible* depth
completion scores RMSE 0.262 on ScanNet against 0.484 for the hidden-structure task. **Hidden depth is ~1.85× harder than
visible depth**, for one model, same data, same day.

---

## 4. Our instruments cannot see the thing we are chasing

This is the finding that changes what to do next, and it comes from four papers pointing the same way.

### 4a. Pixel metrics reward blur — three independent sources

**DeepDR §4.3** states it and then demonstrates it: *"these metrics only measure pixel-wise concordance and **tend to favor
blurry over perceptually similar images**, which is problematic for DR."* Their result: DeepDR comes **second** in PSNR
(41.9 vs E2FGVI's 43.2) while winning LPIPS (0.0104 vs 0.0131) and FID (0.218 vs 0.363). On ScanNet the PSNR gap widens to
46.7 vs 42.4 — *"we attribute that to its tendency to produce overly smooth results."*

**Depth Anything V2 (2406.09414), Table 2 caption**: *"Solely from the metrics, Depth Anything V2 is better than MiDaS, but
merely comparable with V1. But indeed, the focus and strengths of our V2... **cannot be correctly reflected on these
benchmarks**. Similar results (i.e. **better model but worse score**) are also observed in [7, 28]."* Figure 8: *"The noise
will cause better models instead achieve lower scores."* They responded by building a new benchmark.

**MLGS (3746027.3755176)**, single-image feed-forward 3DGS judged on disoccluded regions: their entire win is LPIPS
0.160 → 0.148 while PSNR moves 24.93 → 25.17 and SSIM does not move at all (0.833 → 0.834). They say plainly that LPIPS is the
metric that registers disocclusion quality.

**Every instrument this project has built is in the PSNR/SSIM family**: placeholder %, hole %, bounded-hole %, visible wall
length, pixels-differing, mean absolute difference. S52 reported "4.24 % of pixels differ, mean abs difference 85.1" and could
not say from those numbers whether the result was better. It cannot. Those numbers would go *up* for a worse, sharper fill and
*down* for a blurrier one.

### 4b. The artefact is invisible on stills — InpaintFusion's user study

§4.1: *"quantitative assessment in inpainting is an open research problem... **spatio-temporal consistency cannot be judged
from individual images**."* So they ran 55 subjects × 9 scenes × 3 methods = 1485 ratings, for stills **and** for video:

| | stills | video | Δ (video − stills) |
|---|---|---|---|
| Single plane | 5 | 3 | −1 |
| Multi-plane | 5 | 2 | −2 |
| **InpaintFusion** | 6 | **7** | **+1** |

**On stills the three methods are nearly indistinguishable. In motion they separate by four to five points** — the planar
proxies get *worse* in motion, only the one with correct depth improves. Their Figure 14 caption: *"static images do not
clearly show the advantages of our method. Therefore, we strongly recommend readers to watch the results in motion."*

**S51's A/B was two still frames** and concluded "the frames are indistinguishable." S52's arms were compared at fixed poses.
Our artefact is a **parallax** artefact — "streaky as hell" is a motion percept. Every "measured improvement, no visible
improvement" verdict in this project was reached in exactly the regime this paper demonstrates is blind.

### 4c. Human evaluation is the field's standard here, not a shortcut

Four of the twenty papers rest their headline claim on human raters, because the ground truth does not exist:

| paper | subjects | protocol | result |
|---|---|---|---|
| InpaintFusion | 55 | 10-pt Likert, stills and video, 9 scenes | see above |
| Open-World Amodal (2411.13019) | 180 (Prolific) | 4-way forced choice, gold-standard checks | 41.9 % vs 28.0 / 15.8 / 14.4; **Fleiss κ = 0.319, only "fair agreement"** |
| DeepDR | 64 | 7-pt, 50–200 consecutive frames, re-lit 3D meshes | median 5.3 vs 2.2 / 2.2 / 2.0; χ²(3) = 133.3, p < 0.001 |
| Infinigen Indoors | crowdsourced | ATISS protocol | preferred over four baselines |

2411.13019 §4.2: *"We **center our evaluation on human assessment**"*, and its metric table carries the footnote that the
numbers *"are provided for reference only, as the amodal appearance ground-truth is not available."* The survey (§5.5) says
the field has no consistent metrics at all.

**"The user's screen is the aesthetic authority" is not this project's idiosyncrasy. It is what the field does when there is
nothing to measure against.** But note DeepDR's gap: 5.3 vs 2.2 perceptually, against LPIPS 0.0104 vs 0.0131. The perceptual
separation is enormous next to the metric separation — which is the argument for using *both*, not for abandoning metrics.

### 4d. Zhu 2017 tells us which half is well-posed

**Semantic Amodal Segmentation** (CVPR 2017), the COCOA paper: amodal annotation is *more* consistent between annotators than
modal annotation — region consistency median F 0.723 vs 0.425, edge consistency 0.795 vs 0.728.

Set that against the Fleiss κ = 0.319 for "which completion looks best," and the split is clean, and the survey states it in
its conclusion: shape completion uses **discriminative** models "assuming only one ground truth shape"; appearance completion
uses **generative** models "allowing many possible appearances."

> **People agree on the shape of what is hidden and disagree on its appearance.** Hidden geometry is a well-posed target that
> can be scored. Hidden colour is not, and must be judged.

Our band has both halves. The return contract already treats them differently — depth solved against a Dirichlet boundary,
colour merely written on the mask. That was the right instinct and now has a reason.

---

## 5. What to measure instead — four instruments, all cheap, none requiring truth

**(i) LPIPS per frame and VFID per sweep.** The pair DeepDR uses. LPIPS catches what our area metrics cannot; VFID catches
what stills cannot. Both are off-the-shelf.

**(ii) Render the A/B in motion, not at poses.** Directly from InpaintFusion §4.1 and Fig. 14. Our sweeps already exist in the
harness; we compare frames from them.

**(iii) Ordinal depth pairs — the DA-2K protocol, and the best new instrument in the read.** DAv2 §6.2: pick two pixels, ask
which is nearer. 1K images / 2K pairs; pairs selected by disagreement between expert models, adjudicated by humans, only
popping pairs whose predicted depth ratio exceeds 3; triple-checked; organised by scenario so results are readable per class.
For us: **sample pixel pairs straddling the band and score a far-field construction on ordinal correctness.** No dense truth
needed; it is the half humans demonstrably agree on (§4d); it is cheap; and PatchRefiner found ranking supervision
*orthogonal* to scale-shift invariance (F1 26.12 alone / 26.39 alone / **26.84 together**), so it measures something our
current scores do not.

**(iv) Distribution matching as a return check.** Syn2Real-Depth (2503.20211) Eq. 12–15: compute a differentiable histogram
over a reference set and constrain predictions to match it by KL. Applied to us: **the filled band's depth distribution should
resemble the visible far field's.** This is the principled form of the hand-written median guard in `s52_depth.py` that caught
the occluder-tracking bug, and unlike that guard it generalises to any return.

Two things to *stop* doing: quoting mean-absolute-difference and pixels-differing as quality evidence (they are blur-rewarding
by construction), and drawing conclusions about a parallax artefact from still frames.

---

## 6. The return contract is right, and five papers say so

Depth detail lives in the gradients. Independently, from five directions:

| source | form | weight |
|---|---|---|
| InpaintFusion §3.7 | normal map + Poisson-integrated gradient field | — |
| DeepDR §3.4 | L1 + Sobel gradient term | **λ_grad = 100 vs λ_rec = 10** |
| Depth Anything V2 §5.2 / B.7 | L_ssi + L_gm (MiDaS gradient matching) | **1 : 2**, and only works on precise labels |
| PatchRefiner Tab. 3 | residual on a frozen coarse model beats direct prediction | RMS 0.892 vs 0.925 |
| Syn2Real-Depth Tab. 4 | distil the cost volume, not the features | 0.1809 vs 0.1911 (worse than baseline) |

The last two are the same shape as the first three: **pass the structure, not the values.** PatchRefiner's is the sharpest
analogue — when you already hold a trustworthy coarse field (our plate, the observed rim), ask the model for the *difference*.

What the literature adds that our contract does not have:

- **A ranking term.** PatchRefiner's DSD loss separates *scale error* from *boundary error* and supervises them from different
  sources — L_silog against real GT for scale, L_rank + L_ssi against a sharper teacher for detail. Crucially, naively fitting
  the teacher's absolute depth destroys scale (δ₁ 95.4 → 82.6) — **exactly the failure our per-component absolute shift had**.
  And ranking is *additive* to scale-shift invariance, so gradients are not the ceiling.
- **Bi-directional gradient averaging** (InpaintFusion, §2 above).
- **A per-texel λ from estimator disagreement.** Syn2Real-Depth Eq. 9–11: `C = exp(−β|D₁ − D₂|/D₁)`. We use one global λ in the
  screened Poisson and one uncertainty source (`_geoFarAxS`, derived inside a single law). Any second estimate of band depth
  gives a free confidence map.

---

## 7. Name the occluder explicitly — four papers, four for four

| paper | mechanism | what it buys |
|---|---|---|
| PACO (2406.07706) | Fig. 8 taxonomy; occluder mask as a strategy | the three strategies differ visibly |
| APSNet (Mohan & Valada 2022) | separate **occluder head** alongside visible and occlusion heads | M2→M3 lifts APQ_T 33.7 → 34.6, biggest gain in occluded-region coverage |
| Amodal3R (2503.13439) | occlusion-aware attention layer, separate from mask-weighted attention | **best geometry** (MMD 3.51); mask-weighting gives best appearance (FID 30.53) |
| SynergyAmodal (2504.19506) | triple mask stack **plus the background as its own channel** | — |

Amodal3R's ablation isolates *which half* it buys: the occluder channel improves **geometry**, the visibility channel improves
**appearance**. And the reason is stated plainly (Amodal3R §3.2): an invisible pixel is ambiguous between "an occluder is in
front of it" and "it is off the object entirely," and only a separate occluder mask disambiguates.

**We export `plane_object_ids` and have never used it as a distinct input.** S52's three arms differ only in whether the
occluder falls *inside* the mask. Nothing ever tells the model "this region is the occluder."

SynergyAmodal goes further and passes the visible background as its own channel (`x_background`) — a cheaper answer to PACO's
colour-leak objection than S52's harmonic continuation.

---

## 8. PACO prescribes what S52 arm A does, by name, twice

R7's errata treated the S52/PACO relationship as an argument from task mismatch. Read first-hand, it is not an inference:

> **§4.3:** *"we can seamlessly leverage recent image inpainting models such as **LAMA** to help us to deal with **occluded
> background regions**."*
> **Limitation (iv):** *"**Background deocclusion is limited by the inpainting models.** Since background inpainting has been
> extensively studied, our approach is mainly designed for object-level deocclusion, **leaving background processing to
> inpainting models like LAMA**."*

The paper whose figure was quoted as grounds for doubting S52's arms **prescribes exactly S52 arm A for exactly our half of the
problem.** Two further corrections to how PACO was read:

- Their invented-object failure is blamed on *training data*, not on inpainting: §4.4, the OE dataset exists to "avoid the
  tendency of generating novel objects based on contextual information, a common characteristic of existing inpainting
  models." LaMa's speckled patch is contingent, not a law.
- Their limitation (iii) — objects crossing the image boundary are not handled, fix is to pad — is S48's *unbounded* class, and
  2411.13019 turns it into a rule (Eq. 3: when the target touches an edge, dilate the occluder mask along that edge,
  iteratively, until stable).

---

## 9. Two rules about masks that contradict our current practice

**Masking more beats masking less, measured.** DeepDR supplementary §7.3 added the removed object's *shadow* to the mask:
*"results with masked shadows **often look better** than without. The reason for that is that our model does not need to
hallucinate the very ambiguous shadow borders."* Conversely, masks that under-cover the object cause *"artifacts and
**flickering between consecutive frames**."* Our band mask is computed to be exactly the revealed set. Dilating into the
occluder is worth an arm. (Shadows left behind by removed occluders are named as a failure by three papers: PACO,
SynergyAmodal Fig. 10, DeepDR.)

**Context for filling a disocclusion is only what lies behind it.** MLGS §3.2 defines the context mask for depth layer *m* as
the union of all *deeper* layers, and its gated convolution exists solely to suppress near-side features that "introduce
harmful artifacts." Their Table 4 says this is nearly the whole method — removing mask-guidance and gating gives back 0.008 of
their 0.012 LPIPS margin. **That is S45's far-side rim filter (worth 5.1×, 0.1776 → 0.0349) arrived at independently.**
Context rule first, architecture second.

---

## 10. Three findings that change what we would build

**(i) The band should be filled by two different tools, split on the reveal field.** SynergyAmodal Fig. 6: a regression wins
at 0–10 % occlusion; generative methods take over at 10–50 %, 50–90 %, 90–100 %. And §4.3: *"regression-based methods tend to
produce results resembling an **average** outcome. While they often achieve **decent IoU scores**, the actual shapes do not
meet the requirements."*

Our plane far-side law *is* a regression producing an average; our metrics *are* the IoU family. The trap, named. But the
split is actionable: S48 measured the reveal field at p50 0.116 screen px, p90 0.544, p99 4.641, max 45.2. **Most of the band
is a tiny disocclusion where a regression is the right tool; the heavy tail is where a generative model earns its place.** The
threshold is a field we already compute — no new parameter.

**(ii) Test-time resolution scaling is free sharpness we are leaving on the table.** DAv2 §B.8: *"we can almost freely increase
the image resolution at test time to produce more fine-grained depth maps"* — 2× and 4× of the 518 base, steadily sharper.
Our plate is 851×1023 and we run DA at short-side 518. Every streak in this project originates at a depth boundary.

**(iii) A generative prior can clean up a geometric estimator's noise.** Gen3R §4.3: *"VGGT occasionally exhibits floaters in
its predicted geometry... our generative model **corrects the errors** and produces cleaner depth"* (Co3Dv2 CD 0.9632 → 0.9625;
TartanAir 1.5957 → 1.5101; zero-shot ScanNet++ completeness 0.1162 → 0.0963). Modest, but it is the effect we want against
speckle and streaks — not "fill the hole" but "regularise the field through a learned prior."

Also worth recording: **Gen3C is our architecture and its published failure mode is our streaks.** Gen3R §4.2 — Gen3C
*"combin[es] depth-based warping and inpainting, but its quality **heavily depends on depth accuracy, leading to misaligned
boundaries when the depth estimates are inaccurate**."*

---

## 11. Calibration: how good does hidden-region work get?

The occluded half scores roughly 40 % of the visible half, across tasks, datasets and modalities:

| source | visible | hidden | ratio |
|---|---|---|---|
| APSNet APQ (thing) | 44.1 | 18.6 | 0.42 |
| APSNet APC (thing) | 62.2 | 25.8 | 0.41 |
| Amodal Cityscapes MIoU | 62.7 | 23.6 | 0.38 |
| AmodalSynthDrive (RMSE_vis vs ADErr) | 7.93 | 21.6 | 0.37 (inverted) |
| DeepDR ScanNet RMSE (visible vs hidden) | 0.262 | 0.484 | 0.54 |

And the absolute level is low: amodal instance segmentation mAP on COCOA tops out at **35.4** across the whole subfield
(survey Tab. 3); occlusion-boundary detection tops out at **ODS 0.29** (Infinigen Indoors Tab. 4). Occlusion *order*, by
contrast, is nearly solved — InstaOrderNet F1 96.0 on KINS — and we get it free from the depth map.

This is the sober prior for what any learned prior can hand our band.

---

## 12. Corrections to R7

| R7 claim | status after the first-hand read |
|---|---|
| The corpus bears on our fill stage; plan S37→S41→S49 organised around it | **Superseded.** The corpus's *amodal* half addresses a different task by the field's own definition (§1). Its *DR* half — InpaintFusion, DeepDR — addresses ours precisely and was unread. |
| "Our score is wrong, and the fix is standard" (log error, δ) | **Right diagnosis, wrong fix.** Log error and δ are still pixel metrics. The fix is LPIPS/VFID + ordinal pairs (§5). |
| InpaintFusion's central decision is gradients-not-depth | R7 errata already corrected this to "normals + Poisson on copied gradients." **Correct as amended**; the gradient-domain choice and its stated reason are genuinely theirs (§2). |
| PACO: three inpainting strategies all fail, task mismatch runs our way | **Understated.** PACO *prescribes* LaMa for background regions, by name, twice (§8). |
| Amodal-DAV2 as the learned prior for band depth (S39/S40/S43) | **Falsified three times over** (§1). Additionally: Tab. 2 of 2412.02336 shows scale-and-shift **alignment hurts** Amodal-DAV2 (3.682 → 3.878), and `amodal_probe.py` / `s52_depth.py` both apply min-max rescaling — so those runs were also in the model's degraded configuration. |
| "The corpus contains no graph cut / MRF / smoothness term" | **Confirmed, and it stands.** Sprint 27's formulation has no prior art in this pile. |
| S51: measured improvement, no visible improvement → construction not worth shipping | **Reopened as a measurement failure** (§4). Three papers on blur-rewarding metrics, one on stills-vs-motion. |

---

## 13. Per-paper ledger

Ordered by how much each bears on us. Full detail in `scratchpad/readnotes/notes.md`.

**Directly on task (Diminished Reality):**
1. **InpaintFusion** (TVCG 2020) — joint colour+depth DR, gradient-domain depth, the stills-vs-motion study.
2. **DeepDR** (2312.00532) — joint RGB-D inpainting, inpaint-then-redepth quantified, pixel-metrics-reward-blur demonstrated,
   structure conditioning, mask-generosity rule.

**Instruments and calibration:**
3. **Depth Anything V2** (2406.09414) — "better model but worse score"; the DA-2K ordinal protocol; test-time resolution scaling.
4. **MLGS** (3746027.3755176) — far-side-only context is nearly the whole method; LPIPS is where disocclusion shows.
5. **PatchRefiner** (2406.06679 = 08418) — residual beats direct; scale error and boundary error are separable; ranking is orthogonal.
6. **Syn2Real-Depth** (2503.20211) — consistency reweighting; distribution matching as a truth-free check.
7. **Semantic Amodal Segmentation** (Zhu 2017) — shape is well-posed, appearance is not; amodal segments are *simpler*
   (simplicity .718 → .834), a parameter-free prior we could use in place of wall length.

**Task boundary (why the amodal line is not ours):**
8. **Image Amodal Completion: A Survey** (2207.02062) — the definition; also names our far-field rule and our truth kit as gaps.
9. **AmodalSynthDrive** (2309.06547) — background stuff excluded from amodal depth by construction.
10. **Amodal Depth Anything** (2412.02336) — the task; alignment hurts; GT is a DAV2 prediction.
11. **PACO** (2406.07706) — prescribes LaMa for background; invented objects are a data property.
12. **Open-World Amodal** (2411.13019) — background segments as occluders; boundary-aware dilation; 180-subject study.
13. **Amodal3R** (2503.13439) — occluder channel buys geometry; one-stage beats two-stage.
14. **SynergyAmodal** (2504.19506) — regression vs generative by occlusion fraction; background as its own channel.
15. **APSNet** (Mohan & Valada 2022) — occluder head; the 40 % ratio.

**Adjacent / context:**
16. **Gen3R** (2601.04090) — Gen3C is our architecture and its failure mode is our streaks; generative priors clean geometry.
17. **Pano3DComposer** (2603.05908) — the lone voice *for* inpaint-then-redepth; oracle row as standard practice.
18. **Infinigen** (2306.09310) — truth from mesh not renderer; "real geometry" (alpha-mask trap for P1–P6); the honest
    train/test-composition negative result.
19. **Infinigen Indoors** (2406.11824) — occlusion boundaries have standard metrics (ODS/OIS/mAP); and §G.2 admits the field
    approximates them by *hand-tuned depth-gradient thresholding*, where S48's reveal field derives the threshold from the
    viewing envelope with no tuning. **One narrow point where our instrument is ahead of published practice.**
20. **Counterfactual Depth** (1909.00915) — our exact task, no weights, indoor-only, 128×160. Still the only paper whose
    prediction target is ours.

---

## 14. What to do, in order

1. **Re-measure S51 and S52 properly** before building anything: LPIPS per frame, VFID over a sweep, rendered in motion. This
   is a harness change, not a construction change, and it decides whether `window._farLabel` and S52's arms were wins we
   discarded.
2. **Fix the exporter's one-sided gradients** to bi-directional means (InpaintFusion §3.7).
3. **Build the ordinal-pair instrument** for band depth (DA-2K protocol). It measures the half humans agree on.
4. **Run DA at 2× short side** on the plate and re-bake. Free sharpness at the boundaries every streak starts from.
5. **Feed `plane_object_ids` to the inpainter as its own channel**, and add a dilated-mask arm. Four papers on the first, one
   measurement on the second.
6. Then, and only then, revisit the fill: a reveal-thresholded hybrid (regression under threshold, generative over it), with
   the threshold taken from the field we already compute.

**What not to do:** retry Sprint 28's depth half as inpaint-then-redepth (§3); quote mean-absolute-difference or
pixels-differing as quality evidence (§4a); judge a parallax artefact from stills (§4b); or reopen Amodal-DAV2 for band
depth (§1).

---

## Standing

- Every file in `scratchpad/papers/` has been read beginning to end, first-hand, this session. Per-paper notes with quotations
  and numbers are in `scratchpad/readnotes/notes.md`.
- R7 remains in the repository as the record of a second-hand synthesis and its errata. **Where R7 and R8 disagree, R8 is the
  reading.**
- Nothing in this note has been tested. §14 items 1–5 are cheap and falsifiable; they should be run before any of §10 is built.
- The blocker S33 identified — 74 % of visible streak length is the far field disagreeing with itself, a discrete labelling
  problem — still has **no prior art in this pile**. R7's errata said so and the full read confirms it. That literature
  (Boykov–Veksler–Zabih and successors) was never supplied and remains unchecked.
