# R7 — Twenty papers read against our open questions: the gate has an untried family, depth-only training is supported, and our score is the wrong one (2026-09-21)

Twenty papers supplied as markdown and read in full, in four groups: amodal depth (Amodal Depth Anything, Counterfactual Depth,
Amodal Panoptic Segmentation, the Image Amodal Completion survey, Semantic Amodal Segmentation), deocclusion (PACO/Object-level
Scene Deocclusion, SynergyAmodal, Open-World Amodal Appearance Completion, Amodal3R), synthetic data (Infinigen, Infinigen
Indoors, AmodalSynthDrive, PatchRefiner, Syn2Real-Depth, Depth Anything V2) and RGB-D inpainting (DeepDR, InpaintFusion,
Multi-Layer Gaussian Splatting, Gen3R, Pano3DComposer). This note records only what bears on a decision we actually face.

**The four things that change what we do**, before the detail:

1. **The gate has an untried family, and we already have two members of it.** The one paper that studied *when a geometric
   continuation fails* found the answer is not a scene property but the depth distribution in the collar around the hole.
   Every predictor we falsified in §57, S38 and S39 is scene-level or model-level. `reach` and `lipsp` from S38 are collar
   statistics and both were monotone in our error. We stopped at the wrong moment.
2. **Our metre score is not just incomparable, it is non-standard.** Every depth paper here reports log error and δ alongside
   RMSE, and both are exactly gain-invariant. S38's complaint has an off-the-shelf fix that costs nothing.
3. **Depth-only training is better supported than S40 claimed**, and the supporting result is a decomposition nobody in this
   project had seen: the synthetic-to-real gap in depth is a *scale* gap, not a *structure* gap.
4. **The meadow may be self-inflicted.** The one paper whose target is the surface behind, rather than the completed object,
   takes a single mask covering any number of objects and reports that hidden surfaces are *easier* than visible ones,
   because what is behind clutter is usually floor and wall.

---

## 1. The gate: we were looking in the wrong place, and our own instruments already point at the right one

**Counterfactual Depth (Issaranon, Zou and Forsyth, 2019) is the only paper in the corpus that treats "which pictures are
hard?" as a research question**, and it is also the only one whose prediction target is ours — the depth of the scene with a
masked region removed, not the completed shape of an object.

They built a factorial evaluation set: five factors (object shape complexity, shape rarity, number of nearby objects, what is
behind, camera distance) at 2×2×3×3×2 = 72 real captures with depth measured before and after the object was physically
removed. Then they regressed error against the attributes, with main effects *and all ten pairwise interactions*, and fitted
it separately per method:

| method | adjusted R² of error against scene attributes |
|---|---|
| their learned model | **0.882** |
| image inpainting | 0.633 |
| **Poisson smoothing** (their geometric baseline) | **0.632** |

Their own comment on the geometric baseline is the sentence this project needed three sprints ago: the attributes have *"only
mild effect on whether smoothing is likely to be successful (more important is the pool of depths around the object)."*

**That is an independent reproduction of our asymmetry.** A learned prior's error is well explained by scene properties; a
geometric construction's error is not, and the reason is that what governs a continuation rule is local — the collar of
observed depth around the hole. We falsified four predictors in §57, S38 and S39: the model's visible-region disagreement, the
sky-owned share, the surviving-component count, the unowned share. **All four are scene-level or model-level. None is a collar
statistic.**

And they name the failure condition exactly: Poisson smoothing *"fails in the obvious way when one side of the background is
closer than the other."*

**We are closer to this than the note above implies.** S38 measured `lipsp`, the spread of the hole's far lips at a texel, and
found it monotone in the arm's error on both scenes (L5 0.000 → 0.120 → 0.238 → 0.425 → 0.547). `reach` was monotone too. Both
are collar statistics. We set them aside because the *crossing against the model* moved between scenes — but the crossing is a
different question from the gate, and what S39 then failed to find was a *scene-level* gate. We never aggregated a collar
statistic to the scene, and we never measured the specific thing the literature names: **opposing-side disagreement of the
collar, per band component.**

**The concrete proposal**, cheap and using instruments we already have: for each band component, sample the observed depth in
a collar ring, split it by side, and compute (a) the disagreement between opposing sides, (b) the bimodality of the collar
distribution, (c) the residual of a single-plane fit to the collar. Then aggregate per scene and test against the five field
scenes' known outcome. This is orthogonal to everything ruled out so far.

**A second, independent lead, from the deocclusion group.** Amodal3R's headline negative result is that independently
completed views *disagree*, and that the disagreement is harmful: on GSO, four separately completed views scored FID 65.69
against 58.82 for a single view, and on Toys4K 46.34 against 43.05. Their reading is that *"inconsistent 2D completion does
confuse reconstruction models to the point that using a single view is preferable."* Nobody turns this into a confidence
signal. **We can.** We have the envelope; we can derive the amodal mask from several head positions inside it, run the model
at each, and measure per-texel disagreement. That is truth-free, it is not on our falsified list, and the machinery exists.

**A third, nearly free.** Amodal Depth Anything's Figure 8 establishes that the model's output is strongly mask-dependent, and
presents it as a feature. It is also a test-time consistency probe: perturb the guide mask by dilating, eroding or splitting
it, and measure output variance.

**What the literature does NOT have.** No confidence head, no calibration, no ensemble, no regime classifier, in any of the
twenty papers. The 2023 survey says so directly: handling uncertainty in amodal completion is listed under *future work*. If
we need a gate we are building it, not adopting it. That is worth knowing — it means the absence we have been struggling with
is the field's absence too, not our incompetence.

**Do not revisit two things.** First, the model-versus-observed-depth residual: Amodal Depth Anything computes exactly that
fit and uses it only as a correction, with inconsistent effect across models. Our falsification stands. Second, occlusion
fraction as a difficulty axis — it is the field's default and it is nearly flat for the model we ran: Amodal-DAV2-L moves from
RMSE 3.324 on the easy tercile to 3.476 on the hard one, and δ from 94.4 to 93.3 **across the entire range**. That is the
model's own authors confirming, on their own validation set, our finding that the model is uniformly mediocre.

---

## 2. Why the model is always mediocre, explained

**Amodal-DAV2's ground truth is not geometry.** Its supervision target for the occluded region is Depth Anything V2 (ViT-G)
run on the *un-occluded background image*, then scale-and-shift aligned to the observation over the visible region. The
observation channel is likewise a DAV2 prediction normalised to [0,1], not a sensor or a renderer. The model is distilling
DAV2's opinion about un-occluded objects.

So its ceiling is DAV2's accuracy and its bias is DAV2's bias, and **it has never seen an exact surface in training.** That is
a sufficient explanation for the 2.5× to 3× band we measured in S39 and S40, and it means our kit is scoring it against a
standard it was never trained toward. It also reframes S36's verdict: the model is not a rival construction, it is a
regulariser with a known ceiling.

**A risk we have not tested.** The model has only ever seen an observation depth that is DAV2-ViT-G output on a photograph,
linearly renormalised. We feed it exact ray-traced depth. Given S40's finding that the observation channel carries all the
work, **an off-distribution observation is now the highest-leverage untested variable.** The check is cheap: run the scene's
colour through DAV2-ViT-G and feed that as the observation instead of the kit's exact depth, then compare. Either outcome is
informative.

**One correction to how S40 should be read.** Feeding a flat grey frame does not remove the colour path; the guidance
convolution is summed into the patch-token stream, so a constant image becomes a constant token bias. S40 measured that
*colour variation is actively harmful on our inputs*, which is a stronger and more specific claim than "the colour path is
unused". For paintings that is the result one would predict, since the stem carries a photographic prior. The conclusion for a
depth-only model is unchanged and arguably strengthened.

---

## 3. Our score is wrong, and the fix is standard

S38 found that the metre score amplifies a fixed relative error by a gain varying twenty-fold across the kit, and proposed
scoring in d units. The literature has already settled this and we should simply adopt its convention.

**Every depth paper here reports at least one ratio metric alongside RMSE**, and both of the usual ones are exactly
gain-invariant: log₁₀ error, the mean absolute difference of log depths, and δ, the fraction of pixels within a ratio of
1.25^i. They are Amodal Depth Anything's primary metrics. A fixed relative error costs the same at two metres and at two
hundred.

Four further changes to the harness, each cheap and each catching something we currently cannot see.

**Report interior, exterior and whole separately.** Counterfactual Depth reports every metric three times: inside the mask,
outside it, and overall. We score the hidden class only. The exterior column catches a method that improves the band while
corrupting the visible plate, which nothing in our harness would currently notice.

**Split accuracy from completeness.** Gen3R aligns point clouds with a Umeyama similarity transform and then reports accuracy
and completeness separately, and the split is revealing: pure reconstruction has 2.5× to 4.5× better accuracy and 4.2× to 6.5×
worse completeness than generation. Accuracy asks whether what you put there is right; completeness asks whether you put
anything there. **These are exactly our two failure modes — bleeding the occluder in, versus leaving a hole — and one
aggregate number lets either hide.**

**Score at rest and across the envelope, and report the difference.** InpaintFusion's user study collected three numbers: a
still rating, a motion rating, and their difference. Their planar baselines rated 5 out of 10 as stills and 2 to 3 in motion;
their own method rated 6 and 7. **The static score alone would have ranked the methods almost identically and missed the whole
effect.** This is the only evaluation idea in twenty papers built for a viewer like ours, and we do not have it. S37's Phase A
and C both want it.

**Add a do-nothing baseline.** Counterfactual Depth reports one: predict the visible depth, ignore the band. On their real set
it scores 0.600 interior RMSE against their model's 0.310. We have never reported what fraction of our score is the band at
all.

One more borrowed diagnostic: bin the error by ground-truth depth range and plot it against the depth histogram, so it is
visible which band dominates a scalar. And one design pattern from Amodal Panoptic Segmentation: report a pair of metrics
differing only in how they weight the confound, and read the *ratio of the gains* to learn which regime moved.

---

## 4. Training a depth-only model: supported, with a named risk and a concrete scale

S40 argued for training on depth and the band mask alone. The literature supports it more strongly than S40 claimed, from
three independent directions.

**PatchRefiner decomposes the synthetic-to-real gap, and it is a scale gap.** A model trained purely on synthetic data,
applied zero-shot to real photographs, collapses on scale and simultaneously produces the best boundary structure in the
table:

| | δ1 % ↑ | REL ↓ | boundary F1 ↑ |
|---|---|---|---|
| real-trained baseline | 94.5 | 0.070 | 19.3 |
| **synthetic-only, zero-shot** | **5.7** | **0.399** | **36.3** |

**The part that does not transfer is absolute metric scale. Our band prediction lives in an already-normalised space where
scale is not at stake.** We would be asking a network to do the part that transfers.

**Syn2Real-Depth corroborates from the other side.** Distilling across a domain gap in *raw feature* space made results worse
than not distilling at all (AbsRel 0.1911 against a 0.1865 baseline); doing it in the geometrically filtered cost-volume space
helped (0.1809). Their reasoning — that the filtered space retains motion and structure while discarding appearance — is S40's
argument, arrived at independently by people with no reason to be thinking about us.

**Infinigen Indoors gives the scale.** A U-Net trained from scratch on **1,464 domain-matched images** with exact geometric
ground truth beat one trained on Hypersim, which is 461 professionally built scenes and about 77,000 images, on zero-shot
occlusion-boundary detection. Their competitor's labels had to be approximated by thresholding depth gradients; theirs were
exact. That is our ray-caster's advantage exactly.

**How much data.** Nobody publishes a scaling curve. The working points that exist are 1,464 images and 2,000 pairs for narrow
tasks trained from scratch, and 16K pairs or 20,627 assets for fine-tunes on a pretrained prior. **Target one to three
thousand scenes, not thirty-one and not thirty thousand.** At our 20 to 70 minutes per scene that is on the order of 750 CPU
hours, a day on 32 cores.

**But spend the budget on variety, not volume.** Depth Anything V2's ablation is decisive: training on one 11M-image source
for the same iterations as eight sources totalling 62M lost 2.3 points of δ1, and their conclusion is that *"data diversity
cannot be bridged by simply iterating a single dataset for more cycles."* Their per-source table shows each synthetic source
buying a *distinct geometric capability*. Infinigen counts its interpretable degrees of freedom as a diversity audit and
reports 1,070 across 182 generators. **Running that count over our quads, spheres, ellipsoids, cylinders and discs would tell
us concretely where we are thin**, and the axes that matter for band depth are the ones that change what is behind things:
occluder-to-background distance, background orientation relative to the ray, number of stacked layers, silhouette complexity,
and the ground-plane versus vertical-plane mix.

**Four design decisions the literature settles.**

- **Predict a residual, not an absolute value.** PatchRefiner's residual formulation beats direct prediction (RMS 0.892
  against 0.925), and even a single feature level beats the prior state of the art. **Our sheet model becomes the frozen
  coarse predictor and the network learns the correction.** The analytic work is not thrown away; it is reframed as the base.
  Multi-Layer Gaussian Splatting independently does the same thing, predicting residuals off a layer-boundary prior, and our
  arrival-order plate is a far better prior than their depth-histogram boundary.
- **Do not simply mask a conventional depth loss to the band.** That is the one thing tried and failed: PatchRefiner's
  masked variant scored δ1 81.4 against 95.4 for the invariant losses, with RMS *worse* than unmasked. **Change the loss form,
  not its support** — scale-and-shift-invariant and ranking losses.
- **Supervise the band plus a visible collar, never the band alone.** Amodal Depth Anything loses measurably when supervised
  on the invisible region only: 3.682 → 3.845 for one framework, 4.645 → 5.636 for the other, the latter 21% worse. But not
  the whole frame either.
- **Use a surface-normal loss, and skip the machinery.** Counterfactual Depth's normal loss is worth 15% to 27% on interior
  error. Their elaborate 16×4-bin quantisation of ground-truth normals exists *only* because sensor noise makes normals
  unusable; we have exact geometry and can take normals analytically. Depth Anything V2 agrees from the other end: its
  gradient-matching term, weighted twice the depth term, *"fails to bring evident improvement"* on real labels and improves
  steadily on synthetic ones. **The gradient losses only pay off when labels are exact and dense, which is precisely our
  situation and precisely not anyone else's.**

**The risk, stated plainly.** Scene-prior overfitting, and unlike everyone in this literature we have no escape hatch. Depth
Anything V2's stated limitation is ours exactly: synthetic sets have restricted scene coverage, and their concrete failures
were sky and human heads, absent from training. Our version is a model that learns hidden surfaces are quads and ellipsoids
and confidently continues a painted cathedral as a cylinder. **They fixed this with 62 million pseudo-labelled real images. We
cannot.** Pseudo-labelling needs a teacher plus real inputs on which the target is defined; we have real depth maps from
paintings but no band truth, no second viewpoint and no competent teacher. PatchRefiner's transfer scheme needs real ground
truth for the scale term; Syn2Real's needs real image pairs. **Every synthetic-to-real mechanism in the corpus depends on a
real-domain signal our task does not have.** The defence is entirely front-loaded into generator diversity, which is what
makes the degrees-of-freedom audit the highest-leverage thing to do before writing a training loop.

Two further cautions. **Mask dropout** (flip 10% of mask pixels, exclude them from the loss) does nothing in-distribution and
prevents collapse out of it — 0.425 against 0.762 on the real set. It is a domain-generalisation device and our situation is
exactly the one it is for. And **hold out scene families, not random scenes**: Infinigen validated on 400 scenes sharing no
assets with training, AmodalSynthDrive split geographically. A random split over one generator will lie to us.

**Two adverse data points that belong in the decision.** Semantic Amodal Segmentation A/B'd synthetically composited amodal
training against real annotation and synthetic lost, 0.395 against 0.434 average recall. And AmodalSynthDrive, the only paper
that formalises amodal *depth*, explicitly excludes occluded background from prediction *"as these regions lack the structure
or identifiable features necessary for amodal prediction."* That is a large fraction of our band, declined by the people
closest to our task. Their assertion is unargued and I think it is probably wrong — continuing a floor behind a figure is
easier than hallucinating the back of a car, not harder — but it should be tested early rather than assumed away. Their
headline difficulty number is also worth internalising: amodal depth error ran 2.4 to 2.7 times the visible depth error.

---

## 5. The meadow: the reframing, and the field's refusal

**The field has defined our hardest case out of scope, repeatedly and explicitly.** PACO excludes stuff by fiat, *"such as the
crowd, ice"*, and delegates background to an off-the-shelf inpainter. Open-World's evaluation filter deletes images where
*"background elements were occluded but primary objects were not"*. Amodal Panoptic Segmentation gives stuff no amodal extent
at all, and classifies vegetation and terrain as stuff. AmodalSynthDrive excludes amorphous regions. PACO's own layer-wise
quality degrades precisely on *"more challenging cases, such as with the zebras"*, which is many similar adjacent instances.
The survey names the mechanism: when an object is occluded by another of its own class, *"features of this category are
present in multiple places"* and the boundary becomes ambiguous.

Two leads survive that.

**The reframing, and it is the important one.** Counterfactual Depth's formulation does not require separating instances. It
takes one mask covering any number of objects — their Figure 7 shows seven combinations of three objects handled by one
network — and predicts *the surface behind*. And it reports that the hidden region is the **easy** region: interior RMSE 0.310
against 0.425 for the whole image, with the explanation that *"it's uncommon that objects mask other clutter, so the masked
scene tends to be walls, floors, etc., where depth has simpler statistics and is easier to predict."*

**Behind a meadow of tufts is terrain.** Our L5 problem has been stated as "the user cannot click every clump, so the field
merges into the ground and the construction collapses". The alternative statement is: do not click the clumps. Take one mask
over the whole merged field and ask for the ground behind it. **That is this paper's native mode, not a degenerate case.** The
honest caveat is that their "number of nearby objects" factor tops out at two; nobody has tested fifty tufts.

**The mechanism for identity-free masks.** Open-World is the only paper that treats regions with no object label as
first-class, partitioning the unsegmented residual by erosion and dilation into connected components. They point it at
occluders; pointed at targets it is a handle on a field that cannot be clicked apart. Their own ablation only shows the
components are useful as occluders, so this is a lead, not a result.

One encouraging note against the field's pessimism. The survey is dismissive of geometric completion — Euler spirals, Bézier
curves, *"extremely difficult to make assumptions that apply to different real-world objects in highly cluttered natural
scenes"* — but that pessimism is about **object silhouettes**, not background depth, and Counterfactual Depth's finding cuts
the other way for depth specifically. The same survey then lists as an open direction *"treating the background as multiple
planes and the objects as simple volumes"*, which is our continuation-sheet construction named as a line the field flagged and
did not pursue. Our option (a) is not a hack we fell into.

---

## 6. The hand-off contract for Phase B

S37's Phase B plans to change the inpainting contract so depth comes back as well as colour. The corpus is unanimous that this
is right, and supplies the formulation.

**Joint, not cascade.** Gen3R's ablation is the cleanest evidence because it is the same architecture both ways: generating
colour and then reconstructing geometry from it scores Chamfer 1.6223 against 1.1047 for joint, LPIPS 0.3412 against 0.2281.
Their diagnosis is accumulated error. DeepDR's sequential baselines tell the same story, 0.563 against 0.278 depth RMSE
indoors. **And Pano3DComposer's background path is literally our current cascade — inpaint, then run monocular depth on the
result — and appears in their own failure figure.** Amodal Depth Anything closes the route independently: even with a
ground-truth amodal mask, inpaint-then-redepth leaves *"ghosting artifacts in the predicted depth map"*. A further argument:
the cascade's quality depends on a depth-completion model choice that does not transfer across domains.

**Ask for the depth gradient, not the depth, and integrate against the observed depth at the band boundary.** This is
InpaintFusion's central design decision and it is the most actionable single item in the corpus. They never copy depth,
because depth is view-dependent; they fill colour and normals by patch search and recover depth by Poisson integration of a
gradient field. Three of our problems fall out at once: **the seam is exact by construction**, because the observed depth is
the boundary condition, so there is nothing to align back; the representation is **scale-free**, which is the comparability
S38 asked for; and the solve is a **sparse Laplacian on a thin band**, 97 milliseconds for their whole depth reconstruction at
640×480 on a 2016 dual-core laptop. DeepDR corroborates by weighting its Sobel gradient loss at 100 against 10 for
reconstruction — the gradient structure of depth weighted an order of magnitude above the values.

**Asymmetric masks have two published patterns.** The cheap one is SynergyAmodal's: channel-concatenate the distinct masks and
push them through a **zero-initialised convolution**, so training starts from the pretrained inpainter's behaviour and
degrades nothing. The elegant one is Amodal3R's: one mask as a multiplicative log-bias on attention, the other through its own
cross-attention layer, with the ablation showing mask-weighting buys appearance and the occlusion-aware layer buys geometry.
SynergyAmodal also decodes colour and an amodal mask from **one shared latent with two decoder heads**, which is the shape our
depth head wants.

**Four anti-clone mechanisms, all cheap.**

- **Pass the legal source region explicitly.** Multi-Layer Gaussian Splatting's contextual mask is the union of all layers
  strictly behind the current one, and their gated convolutions exist solely to enforce it, because *"features derived from
  areas outside the contextual mask introduce harmful artifacts"*. **We compute arrival order, which is a strictly better
  layer index than their depth clustering.** This is the no-clone rule written as a constraint rather than a hope.
- **Gate patch similarity multiplicatively by normal agreement**, as InpaintFusion's cost function does. Their claim is that
  it *"provides a geometrical labeling that limits pixel search to geometrically similar surfaces, overcoming the need for
  manual labeling used in previous work"*. Caveat: it constrains against the current target estimate, so it prevents cloning
  only if that estimate is trustworthy. Ours would be the geometric plate.
- **Query with the mask, never the visible colour.** PACO found that an appearance-carrying query makes the decoder copy.
- **Replace the occluder's pixels before inpainting, and do not use flat grey.** Open-World substitutes a clean background;
  PACO tested grey and found the fill colour leaks into the result.

**And a warning about the contract as we would naturally write it.** PACO tried three ways of using a diffusion inpainter for
deocclusion, **all with the ground-truth amodal mask**, and all three failed: inpainting the occluded region alone makes the
model complete the *occluder*; greying the occluder leaks the grey; extending the mask over the whole occluder invents new
objects. **Handing an inpainter a hole does not tell it whose surface the hole belongs to, and a perfect mask does not fix
that.** Our contract must carry the depth and the ownership, not just the region.

**One counter-intuitive result worth testing.** DeepDR found that adding the object's cast shadow to the mask makes results
*better*, because the model then does not have to hallucinate ambiguous shadow borders. Our band may benefit from being
dilated past the exact geometric disocclusion for the same reason: the seam is where the ambiguity concentrates.

**Do not build a layered generative model for plate 2.** Multi-Layer Gaussian Splatting's entire occlusion apparatus — seven
extra layers, depth clustering, contextual masks, gated convolutions, a dedicated loss — buys LPIPS 0.157 → 0.148 and PSNR
24.91 → 25.17 over the same network without it, and never scores depth at all. Its layer ordering is depth-histogram
clustering, which is strictly weaker than arrival order and is why it needs two full-scene base layers to paper over its own
fragmentation. Separately, their source-view comparison is an argument *for* our representation: dense MPI-style methods beat
Gaussian-splat methods badly at reconstructing the source view (LPIPS 0.008 against 0.032), and for a painting the nominal
view must be exact.

---

## 7. What to do, in order

Everything below is cheap and none of it is a new sprint. Phases A and B still come first; items 1 and 2 are small enough to
run alongside.

1. **Collar statistics as the gate.** Per band component: opposing-side depth disagreement, collar bimodality, single-plane
   residual. Aggregate per scene, test against the five field scenes. Our `lipsp` and `reach` are the same family and were
   already monotone. *Highest expected value of anything in this note.*
2. **Switch the kit scorer to log error and δ, keeping RMSE alongside.** Add the interior/exterior/whole split, a do-nothing
   baseline, and error binned by depth range. Closes S38 §3.
3. **Cross-pose disagreement as a second confidence signal.** Derive the guide mask from several head positions in the
   envelope, run the model at each, measure per-texel disagreement.
4. **Feed the model a DAV2 depth instead of the kit's exact depth.** Tests whether the observation channel, which S40 showed
   carries all the work, is off-distribution. Ten minutes.
5. **A degrees-of-freedom audit of the kit**, counted Infinigen's way. This, not the scene count, is the binding constraint on
   any training plan.
6. **Score at rest and at the envelope corners, and report the difference.** The only parallax-specific metric in twenty
   papers, and it belongs in Phase A regardless of what happens to Phase D.
7. **If Phase D resumes as training:** residual off the frozen sheet model, scale-and-shift-invariant plus ranking losses,
   analytic normal loss, supervision over band plus collar, mask dropout, family-level holdout, one to three thousand scenes.
8. **For Phase B:** joint colour and depth, depth returned as a gradient field integrated against the observed depth at the
   band boundary, asymmetric masks through a zero-init convolution, the arrival-order contextual mask passed as the legal
   source region.

## 8. What not to do

- **Do not look for a confidence mechanism to adopt.** Twenty papers, none has one, and the survey lists it as future work.
- **Do not revisit the model-versus-observation residual** or **occlusion fraction** as gates. The first we falsified and the
  literature gives no reason to reopen it; the second is nearly flat on the model we use, by its authors' own table.
- **Do not adopt anything from the literature's layer ordering.** Ours is exact; theirs is estimated depth compared across
  boundaries at 90% pairwise accuracy, or histogram clustering.
- **Do not use the visible-part-versus-completion similarity metrics** that Open-World reports. They score "looks like the
  occluder" as success, which is precisely our failure.
- **Do not expect to obtain any of this as software.** None of the five RGB-D papers states a code or weights release with a
  licence; the deocclusion models are all GPU-bound, one carrying a 13-billion-parameter language model. What transfers is
  contracts, masking schemes, losses and data recipes. **The one exception is InpaintFusion, which needs no weights at all and
  whose inpainting core ran at 4.4 seconds per keyframe on a 2016 dual-core CPU** — which is why a six-year-old paper with no
  neural network in it is the most actionable item in the pile.

---

# ERRATA (2026-09-21) — how this note was produced, and what it does not cover

**This note was not written from a reading.** The 21 papers were read by four subagents in parallel and this note is a
synthesis of their reports. It was presented as a reading and it was not one. Recorded here because the note has been
load-bearing: S37, S41 and S49 were all organised around it.

## 1. What the second-hand reading got wrong

**InpaintFusion.** R7 §Phase B item 3 says the paper's "central decision" is to *ask for the depth gradient rather than
the depth* and integrate it Poisson-wise. Read first-hand, that is not what the paper does. Its depth method is
patch-based: *"since we cannot simply copy view-dependent depth values, we use the **normal map** for inpainting 3D
structure"*, the depth gradient enters as a **cost term modulating texture similarity** so that copied patches agree
geometrically, and the Poisson step (Pérez, Gangnet & Blake) integrates the gradients of the **sampled/copied** patches.

The distinction matters for the reason the adaptation works at all. InpaintFusion's gradient field is integrable and
locally consistent *because it was copied off a real surface in the same scene*. A gradient field returned by a
generative model carries independent per-texel noise and has neither property.

In fairness: the adapted recommendation was the **best-performing arm** on the photograph (S48: pure gradient 0.0118
against a raw return of 0.0304, 2.57× better). What failed in the round trip was the per-component shift, which came
from S45's kit measurement and my implementation, not from this paper. So the misreading cost a correct attribution,
not a sprint.

## 2. What the corpus does not contain, which matters more

Counted across all 21 papers:

| term | papers containing it |
|---|---|
| graph cut / graph-cut | **0** |
| belief propagation | **0** |
| alpha expansion | **0** |
| smoothness term | **0** |
| scanline / scan-line | **0** |
| Markov random field / MRF | 1 (a passing related-work citation in Counterfactual Depth, listing MRF as an *early* monocular-depth approach) |

**The corpus is about the fill stage** — amodal completion, deocclusion, RGB-D inpainting, and the synthetic data to
train them. Our blocking defect, localised in S33 and confirmed in S50, is upstream of the fill: **74 % of the troll's
visible streak length is the far field giving adjacent rows of one surface two different depths.** That is a discrete
labelling / surface-reconstruction problem, and **this literature does not address it.**

This is the substantive cost of the second-hand reading. Not a misquoted number — a plan (S37 → S41 → S49) organised
around the stage the corpus covers, while the dominant visible defect was in the stage it does not.

## 3. Standing

- The synthesis's *factual* claims about the fill stage have not been re-verified first-hand and should be treated as
  second-hand until they are. The papers that drive Sprint 28's contract — PACO / Object-level Scene Deocclusion,
  Amodal Depth Anything, DeepDR, Pano3DComposer, Gen3R, SynergyAmodal, Open-World Amodal Appearance Completion — are to
  be read first-hand **before** that sprint, not summarised.
- The literature for the actual blocker is the stereo / discrete-labelling line (Boykov–Veksler–Zabih and successors),
  which is not in what was sent. Sprint 27's formulation does not depend on it — a binary MRF with a submodularity
  check is standard — but the prior art should be checked before anything is shipped.

## 4. First-hand check: PACO (2406.07706, Object-level Scene Deocclusion)

Checked because R7's PACO claims are **already built into shipped code** — they are the stated justification for
`plane_color_occluder_removed.png` and `plane_mask_context.png` in the Sprint 25 bundle.

**The three claims are accurate.** §5.3 and Fig. 8: (a) inpainting the occluded region alone "leads to ambiguity,
regarding which object the missing area belongs to"; (b) replacing the occluder with uniform grey — "the inpainting
process is **partly influenced by the replacement color**"; (c) extending the mask over the whole occluder — "may
create unexpected new objects". All three with the ground-truth amodal mask.

**Two things the synthesis missed, both of which matter for Sprint 28.**

1. **PACO's own preferred baseline is strategy (c).** Supplementary, §"additional qualitative comparisons": *"For these
   tests, we employed the third inpainting strategy indicated in Figure 8 (c) in the main paper, as our empirical
   findings indicated its **superiority over the other two strategies in most scenarios**."* R7 presented the three as
   equally failed. They are not; (c) is the one the authors use.
2. **Their task is not ours, and the difference runs the favourable way.** Every PACO failure is about completing the
   *occludee* — the album behind the teddy bear, the front bear's hand. **Our band is the background behind the
   occluder.** Strategy (c) — remove the occluder, fill what is behind it — *is our task*, and the authors' objection to
   it ("creates unexpected new objects") is an objection from wanting the album completed. For a background band,
   plausible new background is the goal, not the failure.

**Consequence for the Sprint 25 export, recorded now rather than discovered later.** What was built is a hybrid: the
occluder footprint is replaced by a harmonic continuation (better than PACO's grey, which is the right call and is
supported), but `plane_mask_inpaint.png` covers only the placeholder classes and **does not extend over the occluder
footprint**. PACO's own evidence favours extending it. `plane_mask_context.png` already carries the occluder footprint,
so the (c) variant is a mask union away and should be an arm in Sprint 28 rather than a decision taken by default.

**Standing correction to R7's framing.** "A hole does not tell a model whose surface it is" is true and is the useful
lesson. "All three failed, therefore our contract must carry ownership and depth" overstated it into a prohibition on
the strategy the authors themselves prefer.
