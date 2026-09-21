# S41 — The plan after R7 (2026-09-21). Supersedes S37.

S37 set four phases and said Phase A was the single most valuable next action. That judgement is unchanged. What R7 changed is
(a) it added one cheap prerequisite that everything else is scored against, (b) it settled Phase B's contract, which was an open
design question, (c) it gave Phase D a concrete shape instead of an open search, and (d) it added one small experiment that may
dissolve our hardest failure rather than gate around it.

**The order below is by dependency, not by appeal.** Sprint 23 first because every later A/B is currently scored with a metric
that varies twenty-fold in amplification for reasons unrelated to quality. Then Phase A, because eleven sprints of measurement
have passed since anything changed on screen.

---

## Sprint 23 — The measurement fix (half a sprint; do first, it unblocks everything)

S38 found the metre score amplifies a fixed relative error by a gain varying 20× across the kit. R7 found the fix is standard:
every depth paper in the corpus reports at least one ratio metric alongside RMSE, and both usual ones are exactly gain-invariant.

1. **log₁₀ error and δ at 1.25^i alongside RMSE** in the kit scorer. Gain-free, and it makes our numbers comparable with the
   literature for the first time.
2. **Interior / exterior / whole split** on every metric. We score the hidden class only; the exterior column catches a method
   that improves the band while corrupting the visible plate, which nothing in the harness would currently notice.
3. **A do-nothing baseline column** — predict the visible depth, ignore the band. We have never reported how much of any score
   is the band at all.
4. **Accuracy and completeness reported separately**, not one aggregate. These are our two failure modes, bleeding the occluder
   in versus leaving a hole, and a single number lets either hide behind the other.
5. **Error binned by depth range**, plotted against the scene's depth histogram, so it is visible which band dominates a scalar.
6. **Re-baseline**: restate the tables in S35, S36, S38, S39 and S40 under the new scorer.

**Done means** no ranking in the project rests on a metre score again, and every future A/B is scored in units that compare
across scenes.

---

## Sprint 24 — Phase A, the live pass (1 sprint). Still the most valuable thing we can do.

Unchanged from S37 except for one addition. Everything here is already measured; none of it is research.

1. **Consolidate the measured defaults**: the line-aware despeckle, the untorn plate seams value, the ceiling cut. Decide each
   on screen, then make it the default.
2. **Strip the dead arms** from the bake panel. The notes are the record.
3. **The input contract**: a polarity and range check on a loaded depth map, with a visible warning. The one outstanding
   correctness gap a user can trip over.
4. **Two things that need eyes**: S7's ceiling over-claim and the sky option's uncovered frame edge.
5. **NEW, from R7.** Ship the **rest-versus-envelope difference** as a first-class instrument: score at rest, score at the
   envelope corners, report the delta. InpaintFusion's user study is the only evaluation in twenty papers built for a viewer
   like ours, and its planar baselines rated acceptably as stills and collapsed in motion — a static score would have ranked
   the methods almost identically and missed the whole effect. We have never measured this axis.
6. **Re-baseline** every instrument against the new defaults.

---

## Sprint 25 — Phase B, end to end (1 sprint). The contract is now settled by the literature.

S37 planned to change the hand-off so depth comes back as well as colour. R7 says how.

1. **Reimport the plane bundle** onto the live plate and round-trip it through the bundle checker. No reimport exists today.
2. **Joint colour and depth, not a cascade.** Gen3R's same-architecture ablation is the cleanest evidence (Chamfer 1.62 → 1.10,
   LPIPS 0.34 → 0.23); DeepDR's sequential baselines agree (0.563 → 0.278 depth RMSE); **Pano3DComposer's background path is
   literally our current cascade and appears in their own failure figure**; and Amodal Depth Anything found inpaint-then-redepth
   leaves ghosting even with a ground-truth mask.
3. **Ask for the depth GRADIENT, not the depth**, and integrate it Poisson-wise against the observed depth at the band
   boundary. This is InpaintFusion's central decision and it solves three problems at once: the seam is exact by construction
   because the observed depth is the boundary condition, the representation is scale-free, and the solve is a sparse Laplacian
   on a thin band — 97 ms for their whole reconstruction at 640×480 on a 2016 dual-core CPU.
4. **Pass the arrival-order contextual mask** as the legal source region: only texels strictly behind the occluder. This is the
   no-clone rule written as a constraint rather than a hope, and our arrival order is a strictly better layer index than the
   depth clustering the literature uses.
5. **Replace the occluder's pixels with a clean background before inpainting** — not left in, and not flat grey, because PACO
   tested grey and the fill colour leaks.
6. **Asymmetric masks** for colour and depth, channel-concatenated through a zero-initialised convolution.
7. **One real inpaint, reimported, viewed.** Whatever it looks like is the finding.

**Carry this warning into the design review.** PACO tried three inpainter contracts *with the ground-truth amodal mask* and all
three failed: inpainting the hole alone makes the model complete the occluder; greying it leaks the grey; extending the mask
invents new objects. A hole does not tell a model whose surface it is. Our contract must carry ownership and depth, not a region.

---

## Sprint 26 — Phase C, the sheet A/B (1 day, decides a weeks-long port)

Bake four pictures both ways offline, render each through the envelope at the same poses, and put them side by side. Now also
scored with the rest-versus-envelope delta from Sprints 23 and 24, which is the axis the kit cannot see. If the sheet model is
visibly better, port it; if it is a wash, shelve it with the numbers and keep the per-line law. A documented decision either way.

---

## Sprint 27 — The gate (size depends on the collar test, running now)

R7's first item. Three outcomes, each with a different sprint:

- **Lands per texel and per scene** → build the gate, and use it to arbitrate between the construction and the learned prior.
  Arbitration already beat direct prediction on L5 (0.022 against 0.060 m), so the gate is the missing piece, not the mechanism.
- **Lands per texel only** → a per-texel confidence, which is a blend rather than a gate, and probably a fold-alpha style
  degradation rather than a switch.
- **Fails** → the gate is not a function of any observable we can construct, Phase D closes as a research line, and that gets
  recorded as clearly as the six constructions before it.

Two cheap companions, hours rather than days, to run regardless:

- **Cross-pose disagreement.** Derive the guide mask from several head positions in the envelope, run the model at each, measure
  per-texel disagreement. Amodal3R showed independently completed views disagree and that the disagreement is harmful; nobody
  turns it into a confidence signal and we already have the envelope.
- **DAV2 depth as the observation.** The model has only ever seen a Depth Anything V2 prediction normalised to [0,1] as its
  observation channel, and S40 showed that channel carries all the work. We feed it exact ray-traced depth. Run the scene's
  colour through DAV2 and feed that instead. Ten minutes, and either result is informative.

---

## Sprint 28 — The meadow, reframed (small, and it may dissolve the problem)

We have framed L5 as a labelling problem: the user cannot click every clump, so the field merges into the ground and the
construction collapses. Counterfactual Depth's formulation does not require separating anything. It takes **one mask covering any
number of objects** and predicts *the surface behind*, and it reports the hidden region is the **easier** region — interior error
0.310 against 0.425 for the whole image — because what sits behind clutter is usually floor and wall.

Behind a field of tufts is terrain. **Test: one mask over the whole merged field, ask the construction and the model for the
ground behind it, score on L5 and L9 where the click map is what breaks us.** If this works it is worth more than the gate,
because it removes the regime rather than detecting it. Honest caveat: their "number of nearby objects" factor tops out at two,
so nobody has tested fifty tufts.

---

## Sprint 29 — Kit diversity, then a training pilot (gated on Sprints 27 and 28)

Only if the gate fails and the reframing does not dissolve the problem. R7 supports this more strongly than S40 did, because
PatchRefiner shows the synthetic-to-real gap in depth is a **scale** gap and our band lives in an already-normalised space.

1. **A degrees-of-freedom audit of the kit**, counted Infinigen's way. Depth Anything V2's ablation says diversity of sources
   cannot be bought with more epochs on one source, so **this number, not the scene count, is the binding constraint.** The axes
   that matter are the ones that change what is behind things: occluder-to-background distance, background orientation relative
   to the ray, number of stacked layers, silhouette complexity, ground-plane versus vertical-plane mix.
2. **Expand the generator** on whichever axes the audit says are thin.
3. **A 200-scene pilot** before committing to 1,000–3,000: a **residual off the frozen sheet model** (so the analytic work
   becomes the base predictor rather than waste), scale-and-shift-invariant plus ranking losses (masking a conventional loss to
   the region is the one thing tried and failed), an **analytic** surface-normal loss (worth 15–27% and free for us because our
   geometry is exact), supervision over band **plus collar**, mask dropout, and **family-level holdout** — a random split over
   one generator will lie to us.

**The risk, recorded now so it is not a surprise later.** Every synthetic-to-real mechanism in the corpus depends on a
real-domain signal our task does not have: no band truth on a painting, no second viewpoint, no competent teacher. Depth Anything
V2 fixed scene-prior overfitting with 62 million pseudo-labelled real images and we cannot. The defence is entirely front-loaded
into generator diversity, which is why item 1 comes before any training loop.

---

## Order and size

| | sprint | size | gate |
|---|---|---|---|
| 1 | **23 — the measurement fix** | half | none; do first |
| 2 | **24 — Phase A, the live pass** | 1 | none |
| 3 | **25 — Phase B, end to end** | 1 | 24 |
| 4 | **26 — Phase C, the sheet A/B** | 1 day | 23, 24 |
| 5 | **28 — the meadow reframed** | small | none; can run any time |
| 6 | **27 — the gate** | varies | the collar test |
| 7 | **29 — diversity audit, then a pilot** | open | 27 and 28 both negative |

**The single most valuable next action is still Phase A**, and the reason is still not technical: the fastest way to learn
something genuinely new is to look at a picture. Sprint 23 is half a sprint and makes everything after it trustworthy, so it goes
first. Sprints 27 and 28 are research and stay behind the two that put the thing in front of a person.

## Not recommended, and why

- **Hunting for a confidence mechanism to adopt.** Twenty papers, none has one; the 2023 survey lists it as future work.
- **Revisiting the visible-region residual or occlusion fraction as gates.** The first we falsified; the second is nearly flat
  on the model we use, by its own authors' table (RMSE 3.324 easy → 3.476 hard).
- **Adopting any of the literature's layer orderings.** Ours is exact; theirs is estimated depth compared across boundaries at
  90% pairwise accuracy, or histogram clustering.
- **Building a layered generative model for plate 2.** Multi-Layer Gaussian Splatting's entire occlusion apparatus buys 0.009
  LPIPS over the same network without it, and never scores depth.
- **Planning around obtainable weights.** None of the five RGB-D papers states a release with a licence, and the deocclusion
  models are all GPU-bound. What transfers is contracts, masking schemes, losses and data recipes.
