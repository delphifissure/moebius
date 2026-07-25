# Estimating depth in disoccluded regions
## Background disocclusion, self-occlusion, and contact — what works, what is open, and what it costs

Companion to `RESEARCH-LDI-MPI-DISOCCLUSION.md` (history/licences) and
`REVIEW.md` (measurements). This one is only about **depth in regions the
camera cannot see**, which is the harder and less-published half.

Same constraints: permissive licence, performant, training-free preferred, must
hold up on photographs, paintings and ink art.

---

## 0. Summary

**The taxonomy matters more than the algorithm.** Three problems get conflated
under "disocclusion depth" and they have different correct answers:

| | who owns the hidden pixels | correct hidden depth | solvable classically? |
|---|---|---|---|
| **A. Inter-object disocclusion** | the background surface | continuation of the background, monotonically behind the occluder | **yes, well** |
| **B. Self-occlusion** (arm over torso, cloak fold, staff across body) | the *same* object | just behind the occluding part — **not** background depth | **no** — needs amodal reasoning |
| **C. Contact / support** (figure meets ground) | shared | continuous with the supporting surface | yes, but needs the contact detected |

Filling B with a background rule punches a hole through the figure. That is the
doppelgänger / hole-in-figure / "seated figures must STAND" / troll-arm family,
and `REVIEW.md` Addendum 47 already names it correctly as the overlap class.

**Five results worth acting on:**

1. **The accuracy requirement on hidden depth is `1/k`.** An error ε in
   inpainted depth misplaces that content by `ε·k` px at the cone rim. At
   `k = 775`, one 8-bit level of hidden-depth error = **3 px of misplacement**;
   at `k = 30` it is 0.12 px. Hidden depth only has to be *good* in proportion
   to the cone. Same number as everything else.
2. **First-order smoothness is the wrong prior and it is what most fills use.**
   Harmonic/Laplace/diffusion inpainting (and pull–push, and Telea, and
   Navier–Stokes) are biased toward **fronto-parallel plateaus**. A second-order
   (biharmonic / thin-plate) prior continues the *gradient*, so a slanted ground
   continues as a slanted ground. This is the mathematical statement of
   Addendum 63b's "gradient-true fill values", and it is a solver change, not a
   heuristic.
3. **The ordering constraint is free accuracy and it replaces the backstop
   sweep.** `d_hidden ≥ d_occluder + ε`, clamped after the solve. Cheap,
   always correct, and it structurally removes the class where the plug wins the
   z-test (D1), the protrusion hunts, the 60 s backstop sweep, and the 0.004
   fudge offset.
4. **Ownership is a segmentation question, asked before any depth is filled.**
   T-junctions are the classical, training-free signal — and they are *more*
   reliable on drawn art than on photographs, because illustrators draw them
   deliberately. This is the rigorous form of "the ink was the segmentation
   all along."
5. **Self-occlusion does not need the true shape.** It needs three properties:
   hidden depth stays with its *owning surface*, sits behind the occluder, and
   is smooth. Get those and self-occlusion stops producing artifacts even
   though the geometry is objectively wrong. That is one segmentation and one
   boundary-condition change, not a shape model.

**One trap to avoid:** "inpaint the colour, then re-run the depth estimator on
the result, then scale-shift align." Every text-to-3D-scene pipeline tried it
and the literature is explicit that it breaks at the seam. §6.

---

## 1. Why depth is the harder half

Two asymmetries make hidden *depth* error worse than hidden *colour* error.

**Colour error is static; depth error is dynamic.** A wrong colour in a
disocclusion is wrong at rest and stays equally wrong as the camera moves. A
wrong depth makes that content *move at the wrong rate*. Human motion-parallax
sensitivity is far sharper than texture-plausibility sensitivity — which is why
`REVIEW.md`'s "the wash reads as smeary" complaint survived every improvement to
the wash's *appearance*. The complaint is about rate, not pixels.

**Depth error is a re-projection error with gain `k`.** Content placed at
`d + ε` instead of `d` lands `ε·k` px from where it should. So:

```
hidden-depth precision required  =  (tolerable misplacement in px) / k
```

At the tolerable misplacement of ~1 px:

| k | required hidden-depth precision | in 8-bit levels |
|---|---|---|
| 775 (851 px asset, current cone) | 0.0013 | **0.33 of a level — unachievable from 8-bit input** |
| 1279 (3000 px asset) | 0.0008 | 0.20 of a level |
| 60 | 0.017 | 4.3 levels |
| 30 | 0.033 | 8.5 levels |

This is the same conclusion as the fold limit, reached from the other end: at
the current cone, *even a perfect depth inpainter cannot be represented*. At a
sane cone, a crude one suffices. Before investing in a better fill, the cone
decision has to be made, or the investment is unrecoverable.

---

## 2. The three problems

### A. Inter-object disocclusion

Foreground object in front of a background surface. The hidden region belongs
unambiguously to the background, and it is **monotone** — every hidden point
must be at least as far as the occluder's silhouette. Nearly the entire
published literature is about this case, and it is essentially solved (§4).

### B. Self-occlusion

An object occludes part of itself: an arm across a torso, a leg behind a leg,
a cloak fold, a staff crossing a body, hair over a shoulder. Two things go wrong
if you treat it as case A:

- **Depth**: the hidden torso is placed at *sky* depth instead of *body* depth.
  Under parallax it then slides at the background rate, and the figure appears
  to have a hole punched through it that fills with distant scenery.
- **Ordering**: the monotone constraint is still satisfied (the torso *is*
  behind the arm), so no depth-side check catches it. It is an **ownership**
  error, invisible to every depth-domain test.

`REVIEW.md` has a lot of this class under other names: the black-blob
doppelgänger (A9), the wash doppelganger (A69b/70), "the party is the
estimator's error" (A55), "seated figures must STAND" (A57b), the footing rule
(A46), rise-debt (A76), the troll arm, arm-over-torso. Several of those were
correctly root-caused to the estimator; but the *renderer-side* half of each is
"which surface owns this hidden strip", and that is answerable.

### C. Contact / support

Where an object meets its supporting surface, the "disocclusion" is a thin
wedge and its depth must be continuous with *both* surfaces. Get it wrong in
one direction and the figure floats; wrong in the other and it sinks into the
ground. This is what the footing rule and the standing-content mask are for.
The clean formulation: at a contact boundary the two surfaces' depth fields
should be *tied*, not independently extrapolated — a Dirichlet condition shared
between layers rather than two free extrapolations that happen to disagree.

---

## 3. Ownership comes first

**You cannot fill hidden depth until you know which visible surface the hidden
pixels belong to.** Every method below is a way of answering that.

### 3.1 Classical, training-free, and unusually good on art

- **T-junctions.** Where a contour terminates against another contour, the
  continuing contour is in front. Palou & Salembier's *Monocular Depth Ordering
  Using T-Junctions and Convexity Occlusion Cues*, and *Exploiting T-junctions
  for depth segregation in single images*, build a global depth order from these
  alone. **This is worth more on moebius's asset class than on photographs**:
  a photograph's T-junctions are noisy and often ambiguous; a painter or inker
  *draws* the occlusion explicitly, with a deliberate stroke that terminates at
  the occluding edge. The ink that has been fighting the depth estimator for
  fifteen addenda is a high-quality, hand-authored occlusion-order annotation.
- **Convexity / closure / good continuation.** The Gestalt cues, used alongside
  T-junctions in the same literature, for boundaries with no junction.
- **Figure/ground via CRF over boundary fragments** — enforces *global*
  consistency, which is what turns local cues into a usable layer order.

Cost: cheap, deterministic, no weights, no domain assumption. Accuracy from the
classical literature is roughly 60–70% on local figural assignment alone —
useful as a prior and as a tie-breaker, not as a sole source.

### 3.2 Learned ownership

| method | what it gives | licence |
|---|---|---|
| **Self-Supervised Scene De-occlusion (PCNet)**, CVPR 2020 | occlusion **order** + amodal masks, trained **without amodal annotations** | Apache-2.0 (verify) |
| **InstaOrder / InstaFormer** (CVPR 2022 / 2025) | pairwise and holistic **occlusion order and depth order** from RGB in one pass | verify |
| **Object-level Scene Deocclusion (PACO)**, SIGGRAPH 2024 | amodal completion at object level, self-supervised, 500k samples | verify |
| pix2gestalt / Open-World Amodal Appearance Completion (CVPR 2025) | amodal RGBA for a queried object; training-free framework over pretrained models | verify |
| **SAM 2** | region boundaries (not order) — pair with any of the above | **Apache-2.0** |

### 3.3 The one built for this asset class

**Illustrator's Depth: Monocular Layer Index Prediction for Image
Decomposition** (Maruani et al., Nov 2025) predicts, per pixel, a **discrete
layer index** rather than a continuous depth — a globally consistent ordering
producing piecewise-flat regions, trained on layered vector graphics, and
explicitly designed to handle *flat elements that have no real-world depth*:
shadows, textures, drawn marks. Stated to apply to illustrations, paintings,
and some realistic images.

That is a remarkably close match to what moebius actually needs. Continuous
monocular depth on a painting is being asked a question the painting does not
answer ("how far away is this brushstroke?"); layer index is the question the
image was authored to answer ("what is in front of what?"). Worth an
evaluation on the four assets before more depth-estimator surgery. Licence and
code availability need verifying — project page `nissmar.github.io`.

---

## 4. Class A: filling background disocclusion depth

### 4.1 The prior dominates the algorithm

Ranked worst to best, with the failure mode of each:

1. **Constant / nearest-value fill.** Creates a fronto-parallel plateau. Slides
   at a single rate while the surface it continues does not. The
   `MOEBIUS_DISOCCLUSION_SPEC.md` "Law 3" objection ("the matte moves at a
   different rate than the floor it continues") is exactly this failure, and
   Addendum 3 is right that a depth-matched plate does not have it.
2. **Harmonic / Laplace / homogeneous diffusion** — minimises `∫|∇d|²`. Still
   biased toward fronto-parallel: the harmonic extension of a slanted boundary
   flattens toward the boundary mean, and it produces singularities at mask
   points. **Telea (fast marching) and Navier–Stokes inpainting — the two in
   OpenCV — are in this class and are the wrong tool for depth.**
   Pull–push is also first-order in effect: smooth, and flat.
3. **Biharmonic / thin-plate** — minimises `∫|Δd|²`. Continues the *gradient*
   across the boundary, so a slanted ground extends as a slanted ground. No
   fronto-parallel bias, no boundary singularity. Correct default. One caveat:
   biharmonic has no maximum principle, so it over/undershoots — clamp the
   result (which you want to do anyway, §4.3).
4. **Second-order smoothness with colour-guided anisotropy.** Herrera, Kannala
   et al., *Depth Map Inpainting under a Second-Order Smoothness Prior* — the
   stated goal is to *"encourage flat surfaces without favouring
   fronto-parallel planes"*, with the colour image guiding the fill so depth
   edges align with colour edges; solved efficiently with graph cuts. This is
   the best-in-class classical answer and it is directly implementable.
5. **Normal-guided propagation.** IronDepth (BMVC 2022) propagates depth to a
   query pixel *along the predicted surface normal*, formulating refinement as
   choosing which neighbour to propagate from. This is plane continuation with a
   learned normal field, and it is what Text2Room reached for instead of
   re-estimating depth. Same principle as (3)/(4); higher ceiling; needs a
   normal predictor (MoGe gives normals for free, MIT).

**Recommended concrete formulation for moebius** — fits the existing pyramid
and the existing solver, and is strictly better than pull–push on depth:

```
Solve   ∇²d = ∇·g            inside the hole Ω
with    d = d_bg              on the BACKGROUND part of ∂Ω     (Dirichlet)
        ∂d/∂n free            on the FOREGROUND part of ∂Ω     (Neumann)
where   g = the background rim's depth gradient, extended into Ω
```

This is a Poisson solve with a guidance field, i.e. gradient-domain
extrapolation. It gives slope continuation exactly, sources only from the
background side by construction (no "rind exclusion" heuristic needed), and is
O(N) with multigrid on the pyramid that is already built. It is the same solver
shape as the Jacobi sweeps already in the code — `REVIEW.md` Addendum 3 already
identified multigrid on the existing pyramid as a 10–20× win.

Getting `g` right is most of the quality. Simplest version that works: fit a
local plane to the background rim in a small window and take its gradient;
extend it into the hole constant along the direction away from the occluder.

### 4.2 Directionality

Disocclusion is directional — content is revealed on the side opposite the
camera motion, which is why classical DIBR fills along the epipolar direction
(Jantet & Guillemot's Joint Projection Filling). moebius's cone is 2D, so the
fill must be valid in all directions, but the *source* for any given direction
is still the background rim on the correct side. Weight the guidance field by
direction rather than filling isotropically; this is what the existing
directional plug was reaching for, at the right layer of the stack.

### 4.3 The ordering constraint: free accuracy, and it deletes a sweep

The hidden surface **must** be behind the occluder:

```
d_hidden(x) ≥ d_occluder_silhouette(x) + ε        (hard clamp, after the solve)
```

Enforced in the field, this is unconditional and costs one pass. It structurally
removes:

- **D1** — the plug winning the z-test at rest at silhouettes. It cannot, if the
  field is clamped behind the occluder everywhere.
- **the 0.004-unit fudge offset** — replaced by a constraint that is correct by
  construction rather than by tuning.
- **the backstop sweep** (60 s, 65% of the v1 bake) and the protrusion hunts
  (A21, A41, A43, A112) — these all search *rendered poses* for the failure that
  the clamp forbids at bake time. Searching for violations of an invariant is
  strictly worse than enforcing the invariant.
- **cap cards** (a111e / A114) — introduced to paint where the fold-torn mesh
  left nothing; unnecessary once the field is complete and clamped.

This is the highest ratio of deleted code to added code in this document.

### 4.4 What not to do

- **Do not run a colour inpainter on a depth map.** Depth has structure, not
  texture; a texture model invents detail that becomes visible geometry.
- **Do not smooth the depth to avoid holes.** That is Fehn 2004, and a86 is the
  same trade: `REVIEW.md`:5788 measured it going the *wrong* way on 2 of 4
  assets ("a86 trades banding for folding"). Not resolvable at that layer.
- **Do not derive hidden depth from the colour pull–push pyramid.** First-order,
  fronto-parallel biased — the plateau problem above.
- **Do not fill across an occluder.** Neumann on the foreground boundary, not
  Dirichlet. Any fill that reads foreground depth values inherits them.

---

## 5. Class B: self-occlusion — the honest state of the art

**Nothing training-free solves this**, and no method solves it *correctly*,
because what is behind an object's own arm is not determined by anything
visible. Options in increasing cost:

### 5.1 Continue the owning surface (do this first)

Once §3 says the hidden strip belongs to the torso rather than to the sky, run
the **same second-order solve of §4.1**, but with the Dirichlet boundary taken
from the *torso's* rim rather than the background rim, still clamped behind the
arm.

This is nearly free — one segmentation and one change of which boundary you
read — and it is right in the only sense that matters at moderate parallax:
the hidden surface stays with the body, moves at the body's rate, and never
opens a hole into the background. The reconstructed geometry is wrong (a real
torso is not a smooth continuation of its own silhouette) and it does not
matter, because the error is `ε·k` px and both terms are small.

**This is the single highest-value change on the depth side**, and it is the
mechanism behind the "MPI layering is the endgame for overlap-class errors"
note in Addendum 47 — layering fixes it not because layers are magic but
because a layer boundary encodes ownership.

### 5.2 Amodal mask + amodal depth (the modern drop-in)

- **Amodal mask**: PCNet / Self-Supervised Scene De-occlusion (no amodal
  annotations needed), PACO, pix2gestalt.
- **Amodal depth**: **Amodal Depth Anything** (Li et al., ICCV 2025) —
  takes **image + amodal mask**, predicts **relative depth of the occluded
  portion**. Two variants: Amodal-DAV2 (deterministic) and Amodal-DepthFM
  (generative flow matching). Trained on **ADIW**, a large dataset built by
  *compositing* existing segmentation datasets — no multi-view capture, which is
  why it scales. Reports ~50.7% RMSE improvement over prior SOTA.
  **Repository licence: MIT.**

  **Licence caveat, important:** Amodal-DAV2 is built on a Depth-Anything-V2
  backbone, and DAv2 Base/Large/Giant weights are **CC-BY-NC-4.0**. An MIT
  licence on the wrapper does not launder the backbone. If this route is taken
  commercially, it needs to be rebuilt on the Apache-2.0 backbone
  (DAv2-Small, or a DA3 Apache variant). The *method* is unencumbered; a
  specific checkpoint may not be.

  Second caveat: trained on natural images. Generalisation to painted and inked
  art is unverified. The relative-depth formulation was chosen specifically to
  improve generalisation, which is encouraging but not evidence.

### 5.3 Predict hidden geometry directly (research-grade)

- **Peeking Behind Objects** (Dhamo et al., 2018) — regresses a two-layer LDI
  from one RGB image: depth + foreground mask, then a GAN hallucinates colour
  and depth behind. The first direct attack on exactly this problem.
- **Behind the Scenes** (Wimbauer et al., CVPR 2023) — predicts an implicit
  **density field over the whole camera frustum** from one image, self-supervised
  from video only, and explicitly "predicts meaningful geometry for regions
  occluded in the input". Interesting because it sidesteps layer decisions
  entirely; trained on driving video, so domain transfer to painted art is a
  real question.
- **Amodal3R / DeOcc-1-to-3 / human body priors** (2025) — full 3D shape priors.
  Heavy, object-centric, photo- and human-biased. Not appropriate here.

### 5.4 What "good enough" means

For a layered renderer at moderate parallax, hidden depth must satisfy three
properties and nothing more:

1. **Ownership** — it belongs to the right surface.
2. **Ordering** — it is behind its occluder.
3. **Smoothness** — second-order continuous with the surface it belongs to.

None of these requires knowing the true amodal shape. All three are enforceable.
The shape only starts to matter when `ε·k` grows past a pixel — which is,
again, a cone decision.

---

## 6. The "re-estimate depth on the inpainted image" trap

Widely used in the text-to-3D-scene pipelines (Text2Room, LucidDreamer,
WonderJourney, PanoDreamer, Text2Immersion): inpaint the colour, re-run the
monocular estimator on the completed image, then scale-shift align the new
prediction to the known region.

**Why it looks ideal:** no depth model to train, reuses the estimator already in
the pipeline, and it handles self-occlusion "for free" because the estimator
sees a plausible complete object.

**Why it fails.** Monocular estimators are affine-invariant *globally*, not
locally. A single scale+shift cannot make a fresh prediction agree with the old
one at the seam. The literature is unusually blunt about this: the approach
"often results in depth discontinuities within the inpainted regions, leading to
misalignment with the scene's original depth", and global or region-specific
linear transforms "often result in broken structure and misalignment,
particularly near complex boundaries". It is why Text2Room reached for a
dedicated depth-*inpainting* model (IronDepth) rather than re-estimation,
why LucidDreamer needs an extra interpolation step at the seams, why
WonderJourney needs a multi-stage fusion (align → group at similar disparity →
sky refinement), and why **Invisible Stitch** (Engstler et al., 3DV 2025) is an
entire paper arguing that depth inpainting should replace estimate-then-align.

**Verdict:** usable as a *coarse prior* fed into the §4 solve as a soft data
term; never as the final field, and never with a global alignment. If used,
align **locally in an annulus around each hole**, and let the second-order
solve own the seam.

There is a specific version of this that is more defensible and worth trying
on moebius's assets: run the estimator on the *deoccluded object* (amodal RGBA
from §3.2) in isolation, which gives a self-consistent depth for that object
including its self-occluded parts, then fit it into the scene by aligning to
that object's *visible* pixels only. That is a per-object alignment against a
much better-conditioned problem than a whole-scene one.

---

## 7. Recommended order of work

Each step is independently shippable and independently measurable with the
existing harness.

1. **Print `k` and derive the hidden-depth precision budget** (`1/k` px). One
   line. It decides whether any of the rest is worth doing at the current cone.
   *(Same first step as the other document; it gates both.)*
2. **Add the ordering clamp** `d_hidden ≥ d_occluder + ε` to the existing plug
   field. Cheap, cannot regress correctness, and it should let the backstop
   sweep and the protrusion machinery be switched off behind a flag and
   measured. Expect a large bake-time win and no quality loss.
3. **Replace the depth fill's first-order smoothing with a second-order
   (Poisson-with-guidance) solve**, background-side Dirichlet + foreground-side
   Neumann, multigrid on the existing pyramid. This is Addendum 63b's intent
   with the correct operator, and it retires the directional reflect/smooth
   fill, the rind exclusion, and the wash's flatness.
4. **Introduce ownership.** Start classical and free: T-junction + convexity
   depth ordering over the existing edge/ink maps, which on these assets is a
   hand-authored signal. Use it to choose *which rim* seeds each hole's
   Dirichlet condition. This is the self-occlusion fix (§5.1) and it should
   visibly kill the doppelgänger/hole-in-figure class.
5. **Evaluate `Illustrator's Depth` and SAM 2** as the learned ownership layer
   on the four assets. If layer-index prediction holds up on Frazetta and the
   troll, it is a better primitive than continuous depth for this asset class
   and would retire a large amount of estimator-repair code.
6. **Only then** consider amodal depth (Amodal Depth Anything, on an
   Apache-licensed backbone) as a Tier-2 offline refinement for the
   self-occlusion class.

---

## 8. Depth-side licence table

| component | role | licence | note |
|---|---|---|---|
| Poisson / biharmonic solve, T-junction ordering, Gestalt cues | fill + ownership | **none — classical** | training-free, style-agnostic, the recommended core |
| **SAM 2** | region boundaries | **Apache-2.0** | zero-shot to unseen domains |
| **MoGe / MoGe-2** | depth + **normals** + FOV | **MIT** | normals feed normal-guided propagation |
| **Self-Supervised Scene De-occlusion (PCNet)** | occlusion order + amodal masks | Apache-2.0 *(verify)* | no amodal annotations needed |
| **Amodal Depth Anything** | amodal depth from image+mask | **MIT repo** | **backbone caveat**: DAv2 Base/Large are CC-BY-NC. Rebuild on an Apache backbone |
| InstaOrder / InstaFormer | occlusion + depth order | verify | holistic order in one pass |
| Illustrator's Depth | **layer index** for illustration/painting | verify | best conceptual match to this asset class |
| IronDepth | normal-guided depth refinement/propagation | verify | what Text2Room used instead of re-estimation |
| Behind the Scenes | frustum density field incl. occluded | verify | research-grade; driving-video trained |
| Layered Depth Refinement w/ Mask Guidance (MaskDepth) | mask-guided depth inpaint/outpaint | verify | published fix for the stroke-depth family |
| Depth-Anything-V2 Base/Large/Giant, DA3 Large/Giant | depth | **CC-BY-NC — excluded** | Small/Base(DA3)/DA3MONO-LARGE are Apache-2.0 |

---

## 9. How to test hidden depth without ground truth

The review's measurement discipline is its strongest asset, and hidden depth
currently has no number attached to it. Two tests give it one, and neither needs
new data.

**9.1 Hold-out occlusion test (gives real ground truth).** Take a region of an
asset that is *not* occluded. Composite a mask over it shaped like a real
occluder from the same asset. Run the full ownership + completion pipeline.
Compare the completed depth to the depth that was there. Report RMSE in
**pixels of misplacement at the cone rim** (`ε·k`), not in depth units — that is
the number that matters and it is directly comparable to the fold limit and the
tear threshold.

This is exactly how the ADIW dataset was constructed (compositing over
segmentation data) and how SLIDE trains its inpainter (a *training background
occlusion* mask rather than a disocclusion mask, so ground truth exists). It
costs a harness script and it turns the whole hidden-depth question from
argument into measurement.

**9.2 Cross-pose consistency.** Content revealed at pose A and at pose B must
land on the same *source* texels. Any hidden-depth error shows up as a
disagreement that grows with pose separation, and it catches rate errors that no
single-frame comparison can. Cheap: two renders and a reprojection.

Both tests can be run per class (A / B / C) by masking with background-adjacent
vs self-occluding vs contact-adjacent shapes, which would for the first time
separate the three failure modes numerically instead of by eye.

---

## Sources

Depth inpainting priors and classical methods
- [Depth Map Inpainting under a Second-Order Smoothness Prior (Herrera, Kannala et al., SCIA 2013)](https://link.springer.com/chapter/10.1007/978-3-642-38886-6_52) — "flat surfaces without favouring fronto-parallel planes"
- [Discrete Green's Functions for Harmonic and Biharmonic Inpainting](https://www.mia.uni-saarland.de/Publications/hoffmann-emmcvpr15.pdf) — harmonic vs biharmonic behaviour at mask points
- [Fourth-Order Anisotropic Diffusion for Inpainting](https://arxiv.org/abs/2006.10406)
- [Depth-guided disocclusion inpainting of synthesized RGB-D images (HAL)](https://hal.science/hal-01391065/file/article_revised.pdf)
- [Joint Projection Filling for occlusion handling in DIBR (Jantet, Guillemot et al., 2011)](https://inria.hal.science/hal-00628019/en) — depth first, epipolar direction, full-Z depth-aided inpaint
- [Depth-Aided Exemplar-Based Disocclusion Filling for DIBR](https://web.stanford.edu/class/ee368/Project_Autumn_1516/Reports/Burke.pdf)
- [Review and Preview: Disocclusion by Inpainting for Image-based Rendering](https://scispace.com/pdf/review-and-preview-disocclusion-by-inpainting-for-image-263099rxfc.pdf)

Ownership / occlusion ordering
- [Monocular Depth Ordering Using T-Junctions and Convexity Occlusion Cues (Palou & Salembier)](https://www.semanticscholar.org/paper/Monocular-Depth-Ordering-Using-T-Junctions-and-Cues-Palou-Salembier/5a5c5770bfcf3ee68d0ee42ca2bd5a21434a8ecf)
- [Exploiting T-junctions for depth segregation in single images](https://researchgate.net/publication/220735209_Exploiting_T-junctions_for_depth_segregation_in_single_images)
- [Occlusion Boundary Detection and Figure/Ground Assignment (Maire et al., CVPR 2011)](https://people.cs.uchicago.edu/~mmaire/papers/pdf/sbmam_cvpr2011.pdf)
- [Self-Supervised Scene De-occlusion (Zhan et al., CVPR 2020)](https://openaccess.thecvf.com/content_CVPR_2020/papers/Zhan_Self-Supervised_Scene_De-Occlusion_CVPR_2020_paper.pdf) · [code](https://github.com/XiaohangZhan/deocclusion)
- [Instance-wise Occlusion and Depth Orders in Natural Scenes (InstaOrder, CVPR 2022)](https://openaccess.thecvf.com/content/CVPR2022/papers/Lee_Instance-Wise_Occlusion_and_Depth_Orders_in_Natural_Scenes_CVPR_2022_paper.pdf) · [Holistic Order Prediction / InstaFormer](https://arxiv.org/pdf/2510.01704) · [code](https://github.com/SNU-VGILab/InstaOrder)
- [Object-level Scene Deocclusion (PACO, SIGGRAPH 2024)](https://liuzhengzhe.github.io/Deocclude-Any-Object.github.io/)
- [Open-World Amodal Appearance Completion (CVPR 2025)](https://arxiv.org/pdf/2411.13019)
- [**Illustrator's Depth: Monocular Layer Index Prediction for Image Decomposition** (Maruani et al., 2025)](https://arxiv.org/abs/2511.17454) · [project](https://nissmar.github.io/projects/illustrators_depth/)

Amodal / hidden geometry
- [**Amodal Depth Anything: Amodal Depth Estimation in the Wild** (ICCV 2025)](https://openaccess.thecvf.com/content/ICCV2025/papers/Li_Amodal_Depth_Anything_Amodal_Depth_Estimation_in_the_Wild_ICCV_2025_paper.pdf) · [code (MIT)](https://github.com/zhyever/Amodal-Depth-Anything) · [project](https://zhyever.github.io/Amodal-Depth-Anything/)
- [Peeking Behind Objects: Layered Depth Prediction from a Single Image (Dhamo et al., 2018)](https://arxiv.org/pdf/1807.08776)
- [Behind the Scenes: Density Fields for Single View Reconstruction (CVPR 2023)](https://openaccess.thecvf.com/content/CVPR2023/papers/Wimbauer_Behind_the_Scenes_Density_Fields_for_Single_View_Reconstruction_CVPR_2023_paper.pdf) · [code](https://github.com/Brummi/BehindTheScenes)
- [Amodal3R: Amodal 3D Reconstruction from Occluded 2D Images](https://arxiv.org/pdf/2503.13439)
- [DeOcc-1-to-3: 3D De-Occlusion from a Single Image](https://arxiv.org/pdf/2506.21544)

Depth completion in generative 3D pipelines (the alignment trap)
- [Invisible Stitch: Generating Smooth 3D Scenes with Depth Inpainting (3DV 2025)](https://arxiv.org/pdf/2404.19758)
- [IronDepth: Iterative Refinement of Single-View Depth using Surface Normal and its Uncertainty (BMVC 2022)](https://arxiv.org/abs/2210.03676) · [project](https://baegwangbin.github.io/IronDepth/)
- [Text2Room](https://github.com/lukashoel/text2room) · [InFusion: depth completion from a diffusion prior](https://arxiv.org/html/2404.11613v1) · [AuraFusion360](https://arxiv.org/html/2502.05176) · [SplatFill](https://arxiv.org/html/2509.07809v1)

Layered systems whose depth handling is the reference
- [3D Photography using Context-aware Layered Depth Inpainting (CVPR 2020) — MIT](https://openaccess.thecvf.com/content_CVPR_2020/papers/Shih_3D_Photography_Using_Context-Aware_Layered_Depth_Inpainting_CVPR_2020_paper.pdf) · [code](https://github.com/vt-vl-lab/3d-photo-inpainting)
- [SLIDE (ICCV 2021)](https://openaccess.thecvf.com/content/ICCV2021/papers/Jampani_SLIDE_Single_Image_3D_Photography_With_Soft_Layering_and_Depth-Aware_ICCV_2021_paper.pdf) — trains the inpainter with an *occlusion* mask so ground truth exists
- [Layered Depth Refinement with Mask Guidance (CVPR 2022)](https://openaccess.thecvf.com/content/CVPR2022/papers/Kim_Layered_Depth_Refinement_With_Mask_Guidance_CVPR_2022_paper.pdf)
