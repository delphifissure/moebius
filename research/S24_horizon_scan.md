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

## 5. Implications for the inpainting stage, and the hole contract (added after the user's reply, 2026-09-13)

**Does the atlas survive the new methods?** Yes; each family consumes or produces its parts.

- *2D layer decomposition / amodal completion* (RevealLayer, Referring Layer Decomposition, Amodal SAM) returns RGBA layers
  and no depth. They map onto plate 2 and onto per-object hidden layers; the depth of what they return is ours to assign
  (the plane law for background continuation, the arrival order or a learned prior for a hidden object). They need from us
  the occluder's mask and the picture; they give back a completed background layer that is exactly the band's content.
- *3D-aware inpainters* (3D-Consistent Inpainting, Geometry-Aware Multiview Inpainting, Lift3Dreamer) consume colour +
  depth + mask (+ camera): the bundle as written — `plane_plate_color`, `plane_plate_depth16`, `plane_mask_inpaint`, the
  envelope in `meta.plane`. Lift3Dreamer's training signal is a visibility mask lifted from monocular depth, i.e. the band.
- *Camera-controlled video models* (GEN3C, Stable Virtual Camera, ViewCrafter) consume renders along a path; the completed
  frames are back-projected into the atlas's band texels. The atlas stays the store; the model is a filler.

**What the inpainting stage needs from us, whichever filler is used.**

1. **The context image is the background layer with the foreground absent.** The plate is already that: where the
   foreground stands at rest, the plate texel is the far side. An inpainter that never sees the foreground cannot bleed it
   into the fill — that is the mechanism against spill, not mask feathering. The foreground layer is exported separately
   and never enters the fill's context.
2. **Masks are exact and clean.** Union-of-reveals sets are blobby by construction (they are swept regions), but speckle
   from the despeckle and one-texel islands must not reach the mask; the ring (§0) is not in it. A mask edge that is a
   surface's true silhouette lets the fill end where the object ends.
3. **The fill is depth-conditioned by our plate depth** (ControlNet-depth or the model's own depth input). A flat plate depth
   conditions a flat continuation; the fill continues the wall or the floor instead of inventing a chair at the wall's
   depth. A generated object painted on the plate is a billboard that parallaxes as the wall — acceptable far away,
   wrong close behind. Near hidden objects belong on plate 2 with their own depth (I4, LaRI/DepthLab), not in the plate's
   texture. Prompting follows: "continuation of the visible surfaces; no new objects" for plate 1.
4. **Depth stays ours after the paint.** Re-estimating depth on painted texels with a monocular network re-introduces the
   noise the plane law removed; if a depth model is consulted for the fill, its output is snapped to the plate's planes
   (or accepted only on plate 2). The atlas's depth is piecewise smooth by construction, which is what "the world is made
   of discrete objects" asks of it.
5. **Routing by class** (S17): class 2 (tier) → paint; class 1 (band outside the tier) → paint or keep the wash, the
   artist's call; class 3 (carrier-only) → never seen, no paint; plate 2 → amodal / hidden-layer models; margin strips →
   outpainting with the strips' own depth (`plane_out_*`).

**The perception rank, clarified.** "Stretching" in §2 G means content whose screen motion is not the parallax its depth
predicts — a triangle drawn from a foreground rim to a distant background (spaghetti), a seam that opens and closes, a plate
parallaxing at the wrong depth. Spaghetti is the worst instance, agreed. The plate's *internal* "seams stretched" option
spans two background depths (a skin between carriers); the S20 "rim stretched" value spans from a carrier at far depth to
the plate under the occluder — that is the spaghetti class on the plate, visible only where the foreground has moved away,
and the hole contract below removes the need for it.

**The hole contract.** The far-pose holes (S20) had two causes with one root: the band was built for the 45° / 30° envelope
and the shots at 52°/24° and 56°/19° lie outside it, so the foreground moves further than the carriers reach and the rim
tear opens onto nothing; and content beyond the frame (vermeer's edge). The mathematics is closed-form and already in the
bake: the reveal behind a rim at the envelope's extreme pose is k · (shift(d_near) − shift(d_far)) texels (the a104 law;
Thatte & Girod's statistic is the same quantity), and the band is the union of those reveals over the sweep grid. So the
contract is:

- **the band is built for the envelope the viewer can reach**, not for the fade's rim: every texel inside the extreme
  reveal of every rim gets a carrier at the far side's depth *before* any pose is rendered; then no tear can open onto
  nothing inside the envelope, and the fill has an exact region to paint;
- **the acceptance test is zero interior alpha-0 at every pose up to that envelope** (the b_holes counter, already in the
  harness), on the kit and the pictures;
- **the cost is band area ∝ tan θ**: against 45°, a 50° envelope is 1.19× the band width, 55° 1.43×, 60° 1.73×, 70° 2.75×;
  the tier tells the inpainter which part is seen first, so a wider guarantee costs placeholder area, not correctness.

The harness already bakes to a wider envelope (`ENV=60`); the test running now bakes silverwarrior, vermeer and room to
60° and counts holes at the same five poses as the live chain — if the contract holds, the 52°/56° holes go to the frame
edge only (vermeer's margin class), and the "rim stretched" option can be dropped rather than defaulted. The decision
that is yours: the guaranteed angle (the fade can stay a design choice at 45°; the band can be built wider than the fade).

## 6. "Is there not some complex math membrane for the perfect plug?" (user, 2026-09-13)

**What a membrane bought before, and why it was dropped — measured.** The shipped quick bake's far side *was* a membrane:
a harmonic (Laplace) surface between fixed values (Sprint 2 A244f, then "the reach" chose which texels are free). It
never has holes because it never tears — it stretches the plate from the near rim to the far rim (S5 §7: "no holes at any
angle because it never tears"), which in depth is the spaghetti of §5, and it sags under every rim-less surface (open floor
−0.25 median, precision 0.32, Sprint 2). The plane law replaced it in Sprint 3 because it was exact on every planar far
side and the only arm that put the ground behind a full-width occluder up to the horizon (S15: 0.009 m against the
membrane's 0.031 / 1.1 m). A second membrane, the thin-plate spline per join-law sheet (Sprint 12, §16), scored 1.23 m on
S15 against the law's 0.18 m: a sheet joined the ground and the hill across their fold and one smooth surface through both
is neither; and a thin plate extended from a rim arc over a wide reveal is a poor extrapolator.

**Why a membrane is the wrong object, not just a losing one.** A membrane is one continuous height field over the hole,
determined by the values *around* it. The hidden far side is not that: it is the **continuation of one surface** — the
far one — past the occluder, with a **jump** at the occluder's rim (the occluder is in front; nothing connects them), bounded
below and above by the surfaces it must not pass through (ground, ceiling, walls). The correct mathematical object is
therefore *layered, one-sided and piecewise-smooth with a free discontinuity*: Nitzberg–Mumford–Shiota's 2.1D sketch
(1993; layers with occlusion ordering, occluded contours continued by Euler's elastica), Mumford–Shah with the rim as the
discontinuity set, and each layer continued as a clamped plate — Cauchy data (value **and slope**) on the far rim, a *free*
edge under the occluder, and the other planes as **obstacles**. The per-line plane law with its ground and ceiling cuts is
exactly the one-dimensional finite-difference form of this: Cauchy data from the run, linear (zero-bending) continuation,
free end, obstacle cuts. That is why it beat every membrane: it has the right boundary conditions.

**What the two-dimensional version could add, and what it costs.** Its only promised gain is cross-line consistency — the
seams — because a plate solved over a region continues its Cauchy data as one surface, where the per-line law continues
each line on its own. §16 tested it on the wrong domain (the join-law sheet, which crosses folds); the untested form is
the plate solved per **run cluster** (the same fold segmentation the runs already use, so ground and hill are separate
plates), with a free edge, obstacles, and no constants (the clamped biharmonic energy has none and is invariant to depth
scaling). *For:* seams vanish by construction within a cluster; the arrival order and layering are untouched; the offline
reproduction with truth (`sheetfield3.py`) exists, so it is a one-day test against the S22 bar. *Against:* the family
"replace the per-line choice by a field" has been closed three times (§10b, §16, S22); an affine continuation is already
what a clamped plate returns on planar data, so the only scenes that can move are curved ones, where §16's extrapolation
weakness applies; and the perception result (§2 G) says the seams themselves are cheap once the plate hides them — what
is expensive is content that slides, which the hole contract (§5) addresses without a field.

**The plug itself is three problems, each with its own right tool, and only one of them is a surface.**

1. *Coverage* (no hole at any pose): closed-form geometry — the reveal of every rim at the envelope's extreme pose, carriers
   to that reach (§5, the contract). No membrane needed; a membrane's hole-freeness was stretching.
2. *Depth of the plug*: one-sided extrapolation of the far surface with obstacles — the plane law now; the clamped plate per
   run cluster is the one two-dimensional refinement not yet tested.
3. *Colour of the plug*: the inpainting stage, depth-conditioned (§5).

**Where "complex math" does earn its place beyond the plate equation.** (a) *Hidden contours*: the silhouette of an occluded
object continued behind the occluder — Euler's elastica / Euler-spiral completion is the classical amodal-completion core
(Kanizsa; Nitzberg–Mumford–Shiota; Chan–Kang–Shen elastica inpainting) and is what plate 2's hidden shapes and the amodal
models' outputs should be checked against. (b) *The obstacle problem*: a surface continued under an occluder cannot pass
through the ground, the ceiling or a wall — the variational form handles several intersecting planes in one solve, where
the cuts handle them one at a time (this is the plane cut I2 stated as a constraint rather than a rule). (c) *AMLE* (the
infinity-Laplacian; Caselles–Morel–Sbert 1998, the only interpolant satisfying their axioms): extends "as linearly as
possible" and creates no spurious extrema — the property the truth liked in §16 — but takes values only, not slopes, so it
needs the Cauchy data supplied as a boundary strip; a candidate for the same one-day test as the plate.

Recommendation: keep the plane law as the estimator; run the one-day offline test of the clamped plate per run cluster
(and AMLE) against the S22 bar only if the live pass shows seams the plate does not hide; solve coverage by the contract
first, because that is where the holes are.

## 7. "The band should be as wide as possible — if content is always inside the portal, ±90° horizontal and vertical?" (user, 2026-09-13)

**Geometrically yes, and it diverges.** With the content behind the window plane, an eye at angle θ and distance D sees
behind an occluder a strip whose width is the shift difference between the occluder's depth and the far side's, and
every shift is proportional to e = D·tan θ (the a104 law). So the band behind every rim, the outpaint margin beyond the
frame (the far plane's visible footprint shifts by tan θ × box depth) and the plate step all scale with tan θ:

| envelope | 45° | 50° | 55° | 60° | 70° | 80° | 85° | 89° | 90° |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| band width, margin, k (× the 45° value) | 1 | 1.19 | 1.43 | 1.73 | 2.75 | 5.67 | 11.4 | 57 | ∞ |

At 90° the eye lies in the window plane and sees, through it, the far wall infinitely far to the side: there is no finite
band. "As wide as possible" therefore has to mean *as wide as a viewer can ever be tracked and can see the screen*, which
is a measured number per installation, not a limit of the geometry.

**Where the physical cap comes from.** (1) *The tracker*: beyond the camera's half field of view there is no head position
and nothing to render; a143–a145 measured the observed loss boundary of the face tracker on the user's own camera and
anchored the fade there (onset 24°, black by ~27° on that laptop camera); a gallery with wide or multiple cameras moves
this to 60–70°, not to 90°. (2) *The display*: at θ the window subtends cos θ of its width (60°: half; 80°: 17 %; 85°: 9 %)
and its luminance and contrast fall with the panel's viewing-angle curve; past ~75° the screen is a sliver. (3) *Precision*:
k grows with tan θ, so the visible step 1/k shrinks — at 85° the plate needs 11× the depth precision it needs at 45°; on an
8-bit map that is already past the fold limit, on 16-bit it holds to ~80°. (4) *Evidence*: at 85° the plane law continues a
run for eleven times its 45° reach, and the inpainter invents the whole far wall; plausibility falls with distance from
any pixel that was photographed.

**What changes in the bake at wide angles — not only the width.** At 60° and beyond the dominant reveal behind a person is
no longer the wall but the *person's own side* (R1 E4: at gallery angles a closed side to the equator is most of what is
seen); the layers that matter shift from plate 1 to plate 2 and the object's thickness (R1 A8, 0.71 × width in world
units) — the metric frame of I7 becomes a requirement, not a refinement. The vertical envelope (30° now, `bgViewFadeEndDegV`)
behaves the same way with the floor and the ceiling: at steep look-down the floor behind every object is the reveal, at
look-up the ceiling — which is what the ground and ceiling cuts already bound.

**Recommendation.** Three envelopes, decoupled and each a first-class parameter of the bake and the bundle (`meta.plane.envelope`
already carries the angles): (a) the **bake envelope** — band, carriers, plate 2 and margins — set to the installation's
tracking limit plus its measured jitter margin (the a143 quantity), or to a chosen gallery figure (60–70°); (b) the
**fade**, a design choice, at or inside the bake envelope; (c) the **texture tier**, what the inpainter must paint first,
from the head-motion distribution the recorder measures. Bake wider than you fade — never the reverse — and show the
cost table at the panel. The 60° bake running now on silverwarrior, vermeer and room gives the first real numbers for
that trade (band %, bake time, holes at 52°/56°); 70° and 80° arms follow if you want the curve.
