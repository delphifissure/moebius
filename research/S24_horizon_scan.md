# S24 — Horizon scan: the ring answered, the literature 2024–2026 by problem, our own next constructions, a priority (2026-09-13)

Asked: "should we not do the texel ring first? … be exhaustive, using every technique we can find in the literature and
through our own innovation … another literature search … ways to improve the overall effect … other areas to explore."
R1 (2026-09-07) mapped the literature to 2024 and listed what the pipeline lacked (R1 §5). This note is the second pass:
what the last two years added, measured against where we now stand, and what we could build that nobody has. Direct
page fetches are blocked by this environment's network policy; every paper below was reached through search summaries
and is cited by its arXiv / venue link so the claim can be checked on your side.

## 0. The ring, answered with the buffers first

The porous residual (S23 §2.4) is the one-texel ring around every silhouette that the band includes but the truth does
not. Before deciding to chase it: is it a placeholder — does anyone ever see it?

| scene | ring texels in the band | plate depth moved off its own depth (> 2 q) | synthesised colour | in the SD paint mask |
|---|---:|---:|---:|---:|
| P6 grille (ceiling cut) | 11 731 | 83 | 83 (0.7 %) | 83 |
| P5 fence | 6 177 | 26 | 26 (0.4 %) | 26 |
| S11 rounded bodies | 1 398 | 66 | 66 (5 %) | 66 |
| P1 sparse canopy (ceiling cut) | 5 033 | 388 | 388 (8 %) | 388 |
| S7 canopy (ceiling cut) | 3 614 | 697 | 697 (19 %) | 697 |
| S2 contact | 681 | 13 | — | — |

On 92–99.6 % of the ring the plate keeps its own depth and its own source colour: the texel is *in the band* (the sweep
marks it as uncovered from some pose — it is the first far-side texel beside the rim, and the sweep's cell is a texel wide)
but nothing was synthesised there, nothing is painted there, and at rest and in motion it is the photograph. The few per
cent that are synthesised (S7's 697, P1's 388) sit between leaves where the far side truly differs, i.e. they are real
band. So the ring is a **scoring definition** (band membership) and not a defect of the plate or of the hand-off.
**Recommendation: not first.** One line in the checker — score precision on the synthesised set as well as on the band — and
the porous scenes read P 0.86–0.99 for what the viewer and the inpainter actually get. Removing the ring texel from the band
would change nothing visible and would touch the carrier contract for no gain. Done below as the checker's second column
when the live pass re-baselines.

## 1. What limits the effect now (measured, in order of what a viewer meets)

1. **The placeholder is a wash.** Every synthesised texel is a wash until the diffusion stage exists (bundle ready, S17; no
   reimport). This is the largest gap in the experience by construction, not by failure.
2. **Hidden-layer depth where the far side is not a plane.** Canopies and rounded bodies: band depth p90 0.13–0.14 m
   (thing behind thing); plate 2 from the arrival order carries part of it (S4); the truth's layer-2 demand is 6–34 k texels
   per canopy (S23).
3. **Seams and the skin.** Adjacent lines choose different candidates (27 k same-sheet seams on the troll's DA3-16, S22);
   handled at the plate by stretching (a skin) or tearing (a hole) — the trade the live pass decides.
4. **The depth model's edges.** Boundaries arrive as ramps and thin structures are gone before we see them (S5 poles 0.25
   texel absent; the line rule recovers the one-texel ones). DA3-Mono-Large was chosen in the S8 bake-off; MoGe-2/3 and
   Depth Pro claim sharper boundaries (§2 D).
5. **Noise on 16-bit sources.** The join tolerance's value (1/k) on a noisy 16-bit map is the open item of S10/S21: the
   8-bit quantisation was the better denoiser on the troll.
6. **The frame.** Margin strips are clamp-extended source (a placeholder for the outpaint); the sky layer leaves the frame
   edge uncovered from 0.2 m (S19).
7. **Room's far-pose holes** are unclassified (S20).
8. **No score on a photograph** beyond holes, clones and seams; every precision/recall number is the kit's.
9. **No perceptual budget**: nothing says how large a depth error or a placeholder the viewer tolerates in motion.

## 2. The literature since R1, by problem

**A. Hidden-layer colour — the placeholder becomes content.**

- *2D layer decomposition and amodal completion have matured into foundation-model tools.* RevealLayer (May 2026) decomposes
  an RGB image into multiple RGBA layers with a FLUX-based transformer and a 100 k-image layered dataset, recovering occluded
  content and the background behind it ([arXiv 2605.11818](https://arxiv.org/abs/2605.11818)); Referring Layer
  Decomposition (ICLR 2026) does the same for a referred object ([arXiv 2602.19358](https://arxiv.org/pdf/2602.19358));
  Object-level Scene Deocclusion (SIGGRAPH 2024, [arXiv 2406.07706](https://arxiv.org/pdf/2406.07706)); Open-World Amodal
  Appearance Completion (CVPR 2025, training-free, RGBA output, [arXiv 2411.13019](https://arxiv.org/pdf/2411.13019));
  pix2gestalt ([arXiv 2401.14398](https://arxiv.org/pdf/2401.14398)); SynergyAmodal ([arXiv 2504.19506](https://arxiv.org/pdf/2504.19506));
  amodal masks zero-shot: SAMEO "Segment Anything, Even Occluded" (CVPR 2025, [arXiv 2503.06261](https://arxiv.org/abs/2503.06261)),
  Amodal SAM (2026, [arXiv 2604.20748](https://arxiv.org/pdf/2604.20748)), tuning-free amodal segmentation from the
  occlusion-free bias of inpainters ([arXiv 2503.18947](https://arxiv.org/pdf/2503.18947)). *What it gives us:* a per-object
  answer to "is what is behind this rim the same object or the background?" — the user's self-sampling rule (mirror fill only
  for self-occlusion) becomes decidable per instance instead of a global option; and a completed background layer that is
  exactly our band's content, at the price of a second model with no depth of its own.
- *Inpainting that knows it is 3D.* 3D-Consistent Image Inpainting with Diffusion Models ([arXiv 2412.05881](https://arxiv.org/pdf/2412.05881)),
  Geometry-Aware Diffusion Models for Multiview Scene Inpainting ([arXiv 2502.13335](https://arxiv.org/pdf/2502.13335)),
  DiGA3D ([arXiv 2507.00429](https://arxiv.org/pdf/2507.00429)), Perspective-aware 3D Gaussian Inpainting (Oct 2025,
  [arXiv 2510.10993](https://arxiv.org/pdf/2510.10993)), ObjFiller-3D with video diffusion ([arXiv 2508.18271](https://arxiv.org/pdf/2508.18271)),
  and **Lift3Dreamer** (March 2026, [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2667325826000324)):
  a 2D inpainter fine-tuned with *visibility masks obtained by lifting monocular depth into 3D and simulating novel views* —
  which is, word for word, our band. *What it gives us:* the bundle (plate depth 16-bit + `plane_mask_inpaint` + colour) is
  the input these models expect; Lift3Dreamer's training signal says our mask is the right thing to hand over.
- *Generative novel-view models as the filler at bake time.* ViewCrafter (TPAMI 2025, point-cloud renders condition a
  video diffusion model, [arXiv 2409.02048](https://arxiv.org/html/2409.02048.pdf), [code](https://github.com/Drexubery/ViewCrafter));
  GEN3C (CVPR 2025, a depth-based 3D cache rendered along the camera path conditions the video model, [arXiv 2503.03751](https://arxiv.org/pdf/2503.03751));
  Stable Virtual Camera (2025, 1.3 B generalist NVS diffusion; v1.1 fixed foregrounds detaching from backgrounds,
  [arXiv 2503.14489](https://arxiv.org/pdf/2503.14489), [weights](https://huggingface.co/stabilityai/stable-virtual-camera));
  PostCam ([arXiv 2511.17185](https://arxiv.org/pdf/2511.17185)); splatting-guided diffusion (SIGGRAPH 2025,
  [ACM](https://dl.acm.org/doi/10.1145/3721238.3730669)); Look Beyond (panorama + video, [arXiv 2509.00843](https://arxiv.org/html/2509.00843)).
  *What it gives us:* an alternative to inpainting the atlas — render our plate at the envelope's rim poses, let a
  camera-controlled model complete the view, back-project into the texels the band marks. The model owns the cross-pose
  consistency; we still own the mask and the depth. Heavy on GPU; the models are known to move foregrounds.

**B. Hidden-layer depth.** DepthLab (Dec 2024): RGB-conditioned depth inpainting that keeps the known depth's scale, used
for 3D scene inpainting ([arXiv 2412.18153](https://arxiv.org/abs/2412.18153)); Marigold-DC ([arXiv 2412.13389](https://arxiv.org/pdf/2412.13389));
Invisible Stitch's depth inpainter for scene generation ([arXiv 2404.19758](https://arxiv.org/pdf/2404.19758)); InFusion for
Gaussian scenes ([2404.11613](https://www.emergentmind.com/papers/2404.11613)); **LaRI** — layered ray intersections, the
hidden layers predicted directly as an LDI from one image (Apr 2025, [arXiv 2504.18424](https://arxiv.org/html/2504.18424));
zero-shot novel-*depth* synthesis from 3D foundation-model tokens (Sep 2026, [arXiv 2609.04174](https://arxiv.org/html/2609.04174v1));
PanoDreamer's four-layer LDI by disparity clustering ([arXiv 2412.04827](https://arxiv.org/html/2412.04827)). *What it gives
us:* our plane law is a depth inpainter with a cited premise; where the premise fails (thing behind thing, curved backs) a
learned depth prior is the candidate for plate 2, and the env45 truth already contains the hidden-layer depth to score it.

**C. Layered representations.** Multi-Layer Gaussian Splatting (ACM MM 2025): shallow base layers for the visible content
plus occlusion layers dedicated to what is hidden, from one image ([ACM](https://dl.acm.org/doi/10.1145/3746027.3755176));
Complete Gaussian Splats from a Single Image with denoising diffusion, occluded parts included (Aug 2025,
[arXiv 2508.21542](https://arxiv.org/abs/2508.21542)); Flash3D (3DV 2025); WonderWorld's foreground / background / sky
layers in under 10 s (CVPR 2025, [arXiv 2406.09394](https://arxiv.org/abs/2406.09394)) and WonderTurbo
([arXiv 2504.02261](https://arxiv.org/pdf/2504.02261)); GEN3D (Nov 2025); and the industrial reference for the deliverable
shape, Broxton et al. 2020's layered mesh — a small fixed number of RGBA + depth layers in texture atlases, rendered in a
browser ([ACM TOG](https://dl.acm.org/doi/10.1145/3386569.3392485)). *What it gives us:* confirmation that plate + plate 2 +
sky is the layer count the field converged on (3–4), and a target format for the reimport.

**D. Depth models and their edges.** MoGe-2 (Jul 2025): metric point map, normals and **camera FOV** in one pass, boundary
sharpness comparable to Depth Pro with better geometry ([arXiv 2507.02546](https://arxiv.org/pdf/2507.02546),
[code](https://github.com/microsoft/moge)); **MoGe-3** (Jul 2026): self-guided sparse volumetric refinement, thin structures
and sharp disparity boundaries at lower resolution ([arXiv 2607.17967](https://arxiv.org/html/2607.17967),
[page](https://qft-333.github.io/moge3page/)); Depth Pro's thin-structure recall ([arXiv 2410.02073](https://arxiv.org/html/2410.02073v1));
PointDiT pixel-space diffusion for geometry (Jul 2026, [arXiv 2607.02515](https://arxiv.org/pdf/2607.02515)); occlusion
boundary and depth as one task (May 2025, [arXiv 2505.21231](https://arxiv.org/pdf/2505.21231)); the displacement-field
boundary sharpener ([Ramamonjisoa 2020](https://arxiv.org/pdf/2002.12730)). *What it gives us:* the S8 bake-off predates
MoGe-3; a metric point map with FOV is the metric frame R1 §5.1 asked for (thickness in metres, the envelope in metres,
planes fitted in world units), and sharper edges remove ramp and despeckle work at the source.

**E. Planes and layout.** PlaneRecTR / PlaneRecTR++ single-view plane recovery ([arXiv 2307.13756](https://arxiv.org/pdf/2307.13756)),
PlaneSAM ([arXiv 2410.16545](https://arxiv.org/pdf/2410.16545)), in-the-wild single-image plane reconstruction (Jun 2025,
[arXiv 2506.02493](https://arxiv.org/pdf/2506.02493)), AlphaTablets ([arXiv 2411.19950](https://arxiv.org/html/2411.19950v1));
room layout: PixCuboid (Aug 2025, [arXiv 2508.04659](https://arxiv.org/html/2508.04659)), PolyLayout ([arXiv 2608.03323](https://arxiv.org/pdf/2608.03323)),
GeoLayout from depth-map planes ([arXiv 2008.06286](https://arxiv.org/pdf/2008.06286)); the classical machinery — plane
candidates + MRF labelling by graph cuts (Sinha 2009, [PDF](https://snsinha.github.io/pdfs/SinhaICCV2009.pdf)) and depth
completion with a piecewise-planar model ([arXiv 2012.03195](https://arxiv.org/abs/2012.03195)). *What it gives us:* the
ground and ceiling cuts are two instances of one rule — *an extrapolated surface stops at the first nearer plane on the rest
ray*; walls, tables and shelves are the rest of it. Planes can come from the depth map itself (robust multi-plane fitting
with the same majority acceptance), keeping "trust the depth map" and adding no model.

**F. Scoring without ground truth.** Test-time depth refinement by self-supervision (Re-Depth Anything,
[arXiv 2512.17908](https://arxiv.org/html/2512.17908v2)); 3D-consistency scoring with density fields and pseudo-truth depth
from a baseline model ([NVS with diffusion, 2210.04628](https://arxiv.org/pdf/2210.04628)); DIBR synthesized-view quality
metrics overview ([arXiv 1911.07036](https://arxiv.org/pdf/1911.07036)); Thatte & Girod's statistical model of disocclusions
([PDF](https://web.stanford.edu/~bgirod/pdfs/ThatteVCIP2019.pdf)) — the closed-form cousin of our scope instrument. *What it
gives us:* a photograph scorecard (§3, I6).

**G. Perception — what the viewer actually notices.** Fish-tank VR (Ware et al.: head-coupling beat stereo; error 22 % →
3.2 % from head-coupling alone, [PDF](https://www.researchgate.net/publication/221517266_Fish_tank_virtual_reality));
motion parallax from head movement: between the depth threshold and the concomitant-motion threshold *depth is seen with no
perceived motion*, and a slower head needs more parallax for the same depth ([Ono & Ujike 2005](https://pubmed.ncbi.nlm.nih.gov/15943054/));
viewers tolerate mild depth distortion off the centre of projection (cognitive correction; viewpoint-tolerant depth on
wall-sized displays, Aug 2025, [arXiv 2508.06889](https://arxiv.org/pdf/2508.06889)); perceptual requirements for
eye-tracked distortion correction (SIGGRAPH 2022, [ACM](https://dl.acm.org/doi/fullHtml/10.1145/3528233.3530699));
scene-motion and latency thresholds for head-mounted displays ([Jerald 2010](https://www.cs.unc.edu/techreports/10-013.pdf));
in DIBR studies background inpainting beats stretching in subjective quality ([overview](https://arxiv.org/pdf/1911.07036)).
*What it gives us:* a ranking of our own defects. A far side at the wrong depth that stays *still* relative to the world is
tolerated (depth distortion is forgiven); content that *slides with the head* — a stretched skin, a seam that opens and
closes, a plate that parallaxes at the foreground's depth — is concomitant motion, the thing the visual system flags. The
stretched-seams skin is therefore the more expensive artefact, and a wrong-but-far wash the cheaper one; that is the user's
rule ("wash is much better than a clone") in the literature's terms.

**H. The frame.** Outpainting with geometric consistency: Look Beyond (2025), Unboxed (Disney 2025, geometrically and
temporally consistent video outpainting, [PDF](https://studios.disneyresearch.com/app/uploads/2025/05/Unboxed-Geometrically-and-Temporally-Consistent-Video-Outpainting_Paper.pdf)),
NeRF-enhanced outpainting for FOV extrapolation ([arXiv 2309.13240](https://arxiv.org/pdf/2309.13240)), positional-query
one-step outpainting ([arXiv 2401.15652](https://arxiv.org/pdf/2401.15652)). *What it gives us:* the margin strips
(`plane_out_*` in the bundle) are an outpaint job with a known geometry (the window model's shift envelope); the strips'
depth is already decided by us, only the colour is missing.

## 3. Our own next constructions — for, against, and how each would be measured

**I1. Amodal-gated self-sampling.** Per rim, an amodal instance mask (SAMEO / Amodal SAM) decides whether the far side
belongs to the same object; mirror fill only there, wash elsewhere. *For:* the user's rule made per instance; the other side
of a face is sampled, the wall behind the head is not. *Against:* a second model at bake; amodal masks on porous and
thin objects are weak. *Measure:* the kit's class 3 (thing disocclusion) vs class 2 (background) already labels this: the
gate's precision/recall per texel on S4, S11, S9, S7; clone count must stay 0.

**I2. The general plane cut.** Robust multi-plane fitting on the depth map (RANSAC / J-linkage in disparity space, inlier
tolerance = the law's own tol, majority acceptance per run as with the ground), then the one rule: an extrapolation is cut
at the first nearer plane on the rest ray — ground, ceiling, walls, table tops. *For:* the two cuts that worked (ground,
ceiling) generalised; no network; rooms are mostly planes. *Against:* false planes on curved content (the majority test is
the guard, as with S15's 800 falling runs and 0 planes); order of cuts when planes intersect. *Measure:* S16 two walls, S31,
S26, the room and vermeer pictures (holes at the far poses), byte-identity on troll and open scenes.

**I3. Choice consistency as a labelling with costs in tolerance units.** The S22 closure said a labelling needs a weight
nothing in the scene supplies; the tolerance does: data cost = the candidate's arrival rank × tol, pairwise cost =
|far value difference| / tol between neighbouring lines' choices (Potts above one tol), solved by α-expansion per sheet.
Units-invariant by construction (both terms are in tol). *For:* the seams are exactly choice disagreements (S22 §3);
this is the field's standard tool (Sinha 2009). *Against:* closed twice in other forms; solver cost at 1.5 M texels; risk of
smoothing true creases. *Measure:* the S22 bar — same-sheet seams on the troll DA3-16 must halve, S15 depth not worse.

**I4. A learned depth prior for plate 2.** Where the plane law's far side is another thing (canopies, bodies), ask
DepthLab / LaRI for the hidden-layer depth on the band and score it against the env45 layer-2 truth; adopt per texel only
where the plane law is outside tol of its own evidence. *For:* the truth to score it exists; plate 2 is the layer with the
weakest law. *Against:* GPU, model download, scale drift (DepthLab claims scale preservation). *Measure:* layer-2 depth
median/p90 on P1–P4, S7, S11 vs the arrival-order plate 2.

**I5. Pose-space completion with a camera-controlled video model** (GEN3C / Stable Virtual Camera / ViewCrafter): render
the plate along the envelope's rim, let the model complete, back-project only into band texels. *For:* the model sees the
whole picture and keeps its own cross-pose consistency; handles thing-behind-thing; the same GPU job as the SD stage.
*Against:* heavy; foregrounds may be moved (the SEVA v1.0 defect); our depth must stay the authority. *Measure:* clone
count 0; the I6 scorecard; the user's eye.

**I6. A photograph scorecard without truth.** (a) *Cycle depth:* run the depth model on our rendered rim-pose views and
compare to the depth we rendered — disagreement marks a far side the picture does not support. (b) *Concomitant motion:*
optical flow of the rendered sequence along the head path against the flow the plate's depth predicts; any residual is
content sliding with the head (seams opening, skins stretching, a plate at the wrong depth) — the perceptual literature's
own criterion (§2 G) made measurable. (c) LPIPS of the band against neighbouring source patches, per class. *For:* every
option of the live pass becomes a number on any picture; cheap (the renderer and the depth model exist). *Against:* DA3
is biased on wash; flow is noisy on textureless wash. *Measure:* calibrate on the kit where truth exists (does the scorecard
rank arms the way env45 does?), then run the six pictures.

**I7. Second depth bake-off, with a metric frame.** MoGe-3, MoGe-2, DA3 (mono and any-view), Depth Pro on the kit's
renders (sharp truth) and the six pictures, scored in our terms: ramp width at edges, thin-structure recall (S5-style),
noise σ₃ against the grid, and the plane law's P/R downstream. MoGe's FOV and metric depth give the metric frame R1 asked
for (envelope in metres, thickness 0.71 × width in world units, planes in world units). *For:* boundary and thin-structure
gains arrive at the source, ahead of every rule we wrote to repair them. *Against:* weights must be fetched (DA3 came
through the cache in-session; each model is 1–3 GB); a day of compute. *Measure:* the S8 tables re-run plus the metric
frame's effect on I2.

**I8. The perceptual budget in the bake.** Adopt "no concomitant motion inside the envelope" as the acceptance criterion
(I6 b) and set the texture tier from the recorded head-motion distribution (the a130 recorder exists) rather than 35°.
*For:* the constants become measured. *Against:* needs sessions of real head data. *Measure:* the recorder.

**I9. The frame as an outpaint job.** Sky-layer margin fixed; the margin strips (`plane_out_*`) inpainted by the diffusion
stage with the strips' own depth. Engineering; measured by the edge-uncovered count already in the B tables.

**I10. Reimport in the layered-mesh shape** (Broxton 2020): plate 1 colour, plate 2, sky, margins as RGBA + depth layers;
round-trip through the bundle checker. Engineering; prerequisite for the first end-to-end picture.

**I11. Room's holes** classified (S20 left them); **I12. the matte layer** for hair/fur (R1 A9), now with the amodal
models' alpha and Depth Pro / MoGe-3's thin recall as sources.

## 4. Priority (my recommendation; the trades are above)

1. **Live pass** — unchanged, first: it fixes the defaults every instrument re-baselines against, and it is your screen.
2. **I6 scorecard** — cheapest, and it turns every later decision on photographs into a number (calibrated on the kit).
3. **I2 general plane cut** — the direct extension of the two rules that worked, no new model, measurable on the kit today.
4. **I7 depth bake-off + metric frame** — one experiment, many downstream wins; MoGe-3 did not exist at S8.
5. **SD stage**: I10 reimport → atlas inpaint (Lift3Dreamer-style mask semantics) with I5 as the alternative arm and I4 as
   the plate-2 depth candidate → the first end-to-end picture.
6. **I1 amodal gating** — the self-sampling rule per instance, once the SD stage shows where clones would tempt.
7. **I3 labelling** — last: the highest risk and the smallest visible gain (seams are already hidden by the stretch, and
   §2 G says the stretch's motion, not the seam, is what the eye flags — which I6 b will measure directly).

The ring: a checker column, not a sprint (§0).
