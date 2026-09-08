# Research note R1 — what a single-image parallax portal must accommodate, and what the literature offers

Status: second draft — seven literature passes folded in (full reports in `research/R1_passes/`), revised for the gallery envelope (§1.4) and for the stated purpose, an inpainting scope for the artist and SD (§0b). Passes: (DIBR hole
filling; single-image 3D photography and layered representations; depth edges, thin structures,
foliage and matting; amodal completion and back-surface priors; interiors, layout and background
completion; benchmarks and synthetic scene generation; depth-estimator artefacts and scale).
Section 1 is written from our own failures and from what any photograph, painting or render can
contain. Nothing here is code; nothing here changes a default.

## 0. Why this note exists

Addenda 173–190 attacked disocclusion one mechanism at a time (band outline, membrane colour,
per-fragment tear, geometric band, observed hidden layer, lip instrument, object rule, object backs).
Each fixed the scene it was measured on and met a new failure on the next scene: the troll's
interior steps, the woman's true disocclusion, the bristlecone's porous silhouette, the cave wall
mis-segmented by a sagging membrane. The pattern is that we never wrote down the space of scene
elements the system has to handle, so every rule was general in intent and local in test. This note
does that first, then asks the literature which mechanisms cover which elements, then designs a
synthetic suite that isolates each element with ground truth for what lies behind it.

## 0b. The purpose, restated: a scope map for the artist and Stable Diffusion

The stable, semi-plausible depth and RGB we build for the gaps are not the product. They exist to
**show the artist the scope of what has to be generated** — highlighted, clean regions of depth and
RGB — and to give Stable Diffusion a depth to condition on and a mask to fill. That fixes the
success criteria, in this order:

1. **Scope correctness.** Every texel that some eye position in the gallery envelope sees through
   the aperture and that was never photographed must be in the scope, with its class (disocclusion
   behind a thing, object side, outpaint beyond the frame, porous holes, boundary matte), and no
   photographed texel may be in it. The window model of §1.4 gives this set in closed form per
   depth layer; the synthetic suite gives it exactly as ground truth. This is a precision/recall
   problem, and it is measurable.
2. **Stability.** The scope, its depth and its placeholder RGB are computed once per image and live
   in a static layered atlas; nothing is per pose, so nothing can flicker along a walk. A fill that
   swims is worse than a fill that is wrong, because the artist cannot paint into it and SD cannot
   condition on it.
3. **Depth plausibility inside the scope.** SD is conditioned on depth (ControlNet-depth / SD2-depth);
   the generated texture lands in 3D where the depth says. A plane-continued wall, a ground plane
   bounded by gravity, a closed object side at 0.71 × width, a second LDI sample behind a first —
   these are what make the generated pixels sit still when the viewer moves. Depth error inside the
   scope against the peeled ground truth is the second measurable.
4. **Cleanliness of the placeholder.** The placeholder RGB must read as "unpainted": a smooth wash
   in the rim's colours, no clones (the artist reads a clone as finished), no streaks or skirts (they
   pollute the mask and the conditioning), a visible highlight of the scope in the artist's view.
   This is why the membrane/wash was the right choice from Addendum 179 on, and why every stretched
   texel of Addendum 190 was a defect even where coverage was perfect.
5. **RGB fidelity of the fill is not a criterion.** That is SD's job and the artist's. The placeholder
   is judged on 1–4 only.

Consequences for the representation and the tooling:

- **A static layered atlas is the deliverable** (Addendum 184's "static atlas for SD", Kopf 2020's
  chart atlas): per layer — foreground, boundary matte, k hidden layers, object sides, outpaint at
  depth — a 2-D chart with depth, placeholder RGB, scope mask, class label and a confidence
  (distance to the nearest photographed texel; visibility weight over the envelope). Charts must be
  low-distortion for a 2-D inpainter: Kopf's flat charts by seed-and-grow, or **plane-rectified
  charts** for stuff surfaces (rectify the back wall, floor or ceiling into its own frame, outpaint
  there so perspective texture is consistent, re-project) — the natural home of V1's outpaint.
- **A visibility-weighted scope.** Each scope texel carries the fraction of the envelope that sees it
  (weighted toward central poses if the product wants): the artist sees what matters first, and the
  suite scores recall by visibility, not by texel count.
- **SD runs per chart with the chart's own depth and mask**, outpainting for V1 and inpainting for
  disocclusions and sides, with fattened-foreground masks so it borrows only from the far side
  (SLIDE's training discipline as a prompt-time rule); cross-chart consistency by overlap and
  iterative order (Text2Room, NeRFiller's tiling prior); the boundary matte's alpha is carried
  through as the layer's alpha. Depth for the residue can itself be completed by an
  InFusion-class model conditioned on the generated colour, then re-fed.
- **The artist's view**: the rest image with the scope highlighted per class, a turntable at three
  envelope positions with the placeholder in place, and the per-chart atlas for painting — nothing
  else in the UI needs to change for the purpose.

## 1. Scene elements to accommodate

The system's inputs are one RGB image and one monocular depth map. Every element below is a
situation those two inputs can present. For each: what the eye expects to see when it moves, what
the two inputs actually tell us, and what our current pipeline does.

### 1.1 Occlusion structure (what opens when the eye moves)

| # | element | the eye expects | the inputs tell us | current pipeline |
|---|---|---|---|---|
| E1 | **true disocclusion**: a free-standing object in front of a distant background (the woman, the star watcher's figure) | background continues behind the object; the object's own side is thin | far lip depth and colour at the rim; nothing about the object's back | far-rim membrane + observed hidden layer: correct in depth, colour a wash |
| E2 | **interior self-occlusion, solid body**: a nearer part of one object in front of a farther part (calf over thigh, cape over body, tentacle over tentacle) | the farther PART of the same object, at its depth | both lips belong to one silhouette; far lip depth is the far part | A253 interior step: far lip depth, floor against a162 sinking — works (troll knee, octopus bands) |
| E3 | **glancing self-occlusion of a continuous surface**: a receding wall or floor seen at a grazing angle (the troll's left cave wall) | the surface continues; no gap at all | slopes on both sides of the gap extrapolate to meet | A253 continuous class by slope — works on the wall |
| E4 | **object's own side (limb turn-out)**: the band between an object's silhouette and the background at large eye offsets | the object's flank, textured like the object, then the background | silhouette width and the front's bulge; nothing else | A257 backs: measured-scale inflation gives a thin flank; beyond it the background — the physics of the data, disputed by the user's principle |
| E5 | **stacked occluders**: three or more depth layers overlapping (figure in front of a tree in front of a wall) | the middle layer's continuation first, the far one only where the middle layer ends | the sweep sees both at different poses; one plug texel gets two hidden layers | single-layer plug: the median wins; recorded as the two-layer conflict (80 k texels on the troll); needs k layers |
| E6 | **porous / see-through silhouettes**: foliage, fences, nets, lace, hair masses, scaffolding (the bristlecone) | the background through the holes, moving differently from the branches | the mask is one component with thousands of holes; both lips of a hole are "the same object" | A253 misfires: holes filled at branch depth (the orange bars) — the open failure of Addendum 190 |
| E7 | **thin features**: poles, wires, stems, staffs, railings, antennas | the feature stays thin and rigid; background passes behind it | often missing or merged in the depth map; a 1–3 px feature is narrower than the depth blur | tear feather keeps some; many drag background or vanish |
| E8 | **soft edges**: fur, hair, motion blur, defocus, smoke, translucent cloth | a soft transition that moves with the object, background visible through the fringe | depth edge is a ramp; colour is a mixture | hard tear at one depth; the fringe is either object or background, never both |
| E9 | **object touching its support**: feet on the floor, a vase on a table, a tree trunk in the ground | no gap at the contact line at any pose | depth is continuous across the contact; silhouette components merge with the ground | the rest-silhouette mask merges objects with the floor (troll + floor + walls = one component) |
| E10 | **object cut by the frame edge** | outpaint demand, not disocclusion | nothing | the A214 contract: transparent beyond frame, marked orange for the SD stage |

### 1.2 Background structure (what the hidden layer should look like)

| # | element | the eye expects | current pipeline |
|---|---|---|---|
| B1 | **planar walls, floors, ceilings** (interiors, streets) | planes continue behind objects with their perspective gradient | a membrane anchored at hole rims: right near rims, sags under large rim-less surfaces (cave wall), no notion of a plane |
| B2 | **ground plane with objects standing on it** | the floor continues under and behind the object, foreshortened | as B1; plus the contact-merge of E9 |
| B3 | **sky / infinite backdrop** | infinite depth, no parallax | the depth map's far value; sky texels sometimes treated as a surface (mis-segmented objects over sky in the bristlecone) |
| B4 | **distant terrain / mountains / horizon** | small parallax, smooth | works when the depth map is smooth |
| B5 | **cluttered mid-ground** (shelves, crowds, undergrowth) | many small disocclusions, each a different layer | the median-per-texel plug; stacked case E5 |
| B6 | **repetitive texture** (tiles, bricks, fences) | the pattern continues in phase | the wash loses the pattern; a clone would keep it; the SD stage's job |
| B7 | **text, signs, line drawings** | strokes continue or end cleanly | wash smears strokes into grey |
| B8 | **strong lighting structure** (cast shadows, light beams, reflections on the floor) | shadows stay attached to the ground; beams are volumetric | shadows are depth-map texture; beams and god-rays are painted as surfaces |

### 1.3 Surface and material cases the depth map gets wrong

| # | element | typical depth-map behaviour | consequence |
|---|---|---|---|
| M1 | **glass, windows, transparent water** | depth of the glass plane or of what is behind it, inconsistently | tears and plugs in the wrong place |
| M2 | **mirrors and strong reflections** | the reflected scene's depth or a flat plane | a "hole" into the mirror or a flat card |
| M3 | **specular highlights, wet surfaces** | small pits or bumps | flying pixels, false cliffs |
| M4 | **dark / low-texture regions (night, shadows)** | smooth guesses, wrong absolute depth | false continuity across true edges |
| M5 | **painted / illustrated images** (the troll, the warrior) | plausible but relief-like; scale unknown | thin bodies; the z-vs-x ratio we had to fit |
| M6 | **depth-edge blur ramps** | 2–8 px ramps at every edge, wider at low resolution | skirts unless torn; the ramp's own texels belong to neither side |
| M7 | **8-bit quantisation** | 1/255 terraces on slow gradients | staircases in the plug, false micro-cliffs |
| M8 | **halos** | a band of intermediate depth around objects | a false thin layer at every silhouette |
| M9 | **relative vs metric scale** | affine-invariant disparity; no world scale | thickness, parallax budget and eye-offset limits are all guesses |

### 1.4 The viewing envelope (revised: the fishtank / gallery target)

The target is not a ±45° cone. It is the full half-space in front of the window: a viewer walking
past a picture in a gallery, or looking into a fishtank from any point short of the wall's own
plane (never crossing 180°), with the frame keystoning and occluding more of the scene as the
offset grows. Reflections, specularity and transparency (M1–M3) are deferred by decision. This
section fixes the geometry, because it decides what the pipeline must be.

**Window model.** Eye at lateral offset e and perpendicular distance D from a window of width W
in the plane z = 0; scene content at depth d behind the window; θ = atan(e/D). Three effects, all in
closed form:

1. **The strip slides.** Through the window the eye sees, at depth d, an interval of width
   W·(D + d)/D centred at x = −e·d/D. The photograph is the same interval centred at 0, so the
   photographed fraction of what is visible at depth d is
   `f(d, e) = 1 − e·d / (W·(D + d))`, clamped at 0. The rest is content beside the photographed
   frustum: a strip of width e·d/D per side at that depth.
2. **The window shrinks on screen.** Everything is seen through the window's projected solid angle.
   For a viewer walking a line parallel to the wall (constant D) the distance to the window is
   D/cosθ and the flat window foreshortens by cosθ, so Ω = W·H·cosθ/(D/cosθ)² ∝ **cos³θ**: 0.65 at
   30°, 0.35 at 45°, 0.125 at 60°, 0.017 at 75°, 0.00066 at 85°, 0.000005 at 89°. (An earlier draft
   of this note said cos²θ; it counted the distance once instead of squared. For a viewer on a
   sphere of radius D around the window the law is cosθ.) At 89° the whole scene is a sliver. The
   truth kit's retinal weight uses cos³θ and states it.
3. **The photographed depth reach collapses.** Rays through the window stay inside the photographed
   frustum only to depth `d* = W·D / (e − W)` for e > W; deeper than that they have exited its side.
   Our diorama (W 0.16, D 0.2): d* = 0.80 m at 45°, 0.17 m at 60°, 0.055 m at 75°, 0.015 m at 85°,
   2.8 mm at 89°. A metric room (W 0.5, D 0.5): unbounded at 45° (e = W), 0.68 m at 60°, 0.18 m at
   75°, 0.048 m at 85°.

Consequences:
- **The outpaint scope is bounded**, not dominant: per side and per depth layer it is a strip of
  width e_max·d/D beside the frame, and its visibility weight over the envelope falls as cos³θ, so
  the weighted scope concentrates within roughly half a window width of the frame edge at the
  scene's depths. The extreme angles add regions almost no pixel ever lands on; the artist's
  highlight ranking and the generation budget should follow the weight, not the union.
- **Parallax of near content** relative to the window plane is e·d/(D + d), bounded by e as long as
  the content is behind the glass; pop-out content (allowed by decision) diverges as it approaches
  the eye and is clipped by the frame, so its scope is bounded by the aperture.
- **Sides.** At offset θ the eye sees an object's flank up to θ from the front; at 60–85° the flank
  is seen nearly frontally, but through an aperture that has shrunk by cos³θ. The side is a surface
  that must exist, closed to the equator; how much of it is ever seen in pixels is again the weight.
- Numbers for the diorama at sheet1 (42°): the deepest layer is 81 % photographed — the 19 % is
  today's orange A214 mark — through a window at 55 % of its head-on area.

**Correction after reading the code (A65, A208, `updateCameraAndProjection`).** The claim made in
conversation that "a longer lens gives more generated content at the same head angle" assumed the
envelope is specified as an angle at the window with the eye's lateral offset e independent of the
lens. That is not how the app normalises across cuts. Two things scale with the lens together:
the dolly distance D = (W/2)·(f/18 mm) (A208: doubling the focal length doubles the camera's
travel), and the lateral eye offset per unit of head motion, e = k·tan(hfov/2) (A65: head motion
measured in focal-plane frame widths; 90° is identity). The portal rect stays fixed and the
subject plane is pinned by the lateral gain g = (e − q)/(e0 − q) plus the A208 corner adjustment
(rect scaled by k = h(h0 − z)/(h0(h − z)), centre moved by e·(1 − a)(1 − k)); measured 0.000 px
drift of portal-plane points across the dolly sweep at offsets 0 / 0.1 / 0.2. Under that
normalisation, with tan(hfov/2) = 18/f for a 36 mm frame, e/D ∝ (18/f)², so the slide of the
visible strip at depth d, e·d/D, falls with the SQUARE of the focal length for the same head
motion, and the photographed fraction rises: a telephoto cut has a far smaller world envelope and
far less scope than a wide cut, not more. With the shipped head gain (camOff 0.2, scalar 1, face
deviation ±0.5 → e_max = 0.1 m × tan(hfov/2)) and W = 0.16 m, the window angle reached at the edge
of head travel is about 51° for a 90° lens, 12° for a 45° lens, and 2° for an 18° lens. The
gallery envelope of this section is therefore reachable only for wide content unless the
head-tracking scalar is raised per cut; whether the envelope is specified in head units (world
angle lens-dependent, scope small on long lenses) or in window angle (head gain varies per cut) is
the decision to make. Within a dolly the far background breathes by design (89–214 px measured
behind the portal) while the subject plane holds; across cuts nothing moves at rest.

**Second correction (Sprint 1, after re-reading the code rather than recalling it).** "Two things
scale with the lens together" above is wrong as a description of the app. They are two independent
controls: the dolly (`dollyDistForFocal`, `updateCameraAndProjection`) moves only `camera.position.z`,
and the A65 gain `tan(contentLensFovDeg/2)` is applied to head motion only when `window.setLensFov`
is called per cut (default 90°, gain 1). So during a dolly the head displacement is constant in
metres and the window angle at the edge of head travel falls as 1/D, not 1/D²; the (18/f)² law and
the 51° / 12° / 2° figures describe a cut that both dollies to the new lens and applies the A65 gain
for it. The measured table for all three conventions (fixed window angle; constant head motion,
which is the dolly as implemented; both controls applied) is in `S1_sprint1_report.md` §9; the
constant-head-motion convention is the one whose generated scope barely depends on the lens.

| # | element | consequence at gallery angles |
|---|---|---|
| V0 | **the envelope**: e up to ~85°, D from a hand's length to a room's width | every rule must be measured at 60–85°, not 10–45°; nothing published operates there (§2.7) |
| V1 | **outpaint beside the frame at depth**: a strip of width e_max·d/D per side per layer, visibility-weighted by cos³θ | a background model defined beyond the frame (planes, ground, sky) and a generative texture stage are first-class; the scope is bounded and concentrates near the frame edge |
| V2 | **vertical offsets** (crouching, standing, looking down into the tank) | floor and ceiling planes carry the same load as walls; the sweep is 2-D |
| V3 | **the rest pose must stay pixel-faithful** | unchanged |
| V4 | **temporal coherence along a walk** | plug, sides and outpaint must be pose-independent assets; per-pose fills would swim over a metre of travel |
| V5 | **real-time budget** | the shader still gets three rules; everything else is a bake — but the bake now produces a small scene, not a fringe |
| V6 | **the diorama depth is a design lever** | the fraction photographed at the back is 1 − e·d/(W(D + d)); a shallower diorama keeps more of the gallery walk photographed at the cost of flatter parallax; a metric-scale scene makes the walk mostly generated content |

## 2. What the literature offers per element

Each pass below is condensed; the full agent reports are kept in `research/R1_passes/`. Citations are
those the passes verified (author, venue, year, link); anything they could not verify is marked.

### 2.1 DIBR / 3DTV hole filling (2004–2020) and its learned successors

The 3DTV corpus is our problem with a small horizontal baseline instead of a 45° head. Its history is
a sequence of the same failures we have re-found.

- **Depth pre-smoothing** (Fehn, SPIE 2004; Zhang & Tam, IEEE Trans. Broadcasting 2005, asymmetric
  vertical smoothing) shrank holes by turning cliffs into ramps: background edges bow, objects look
  glued to the background. That is exactly the mechanism of our skirts (M6, E8). Lesson inverted:
  never ramp a cliff, tear it.
- **Fill only from the far rim, depth before colour** (Vazquez, Tam & Speranza SPIE 2006 comparison;
  Ndjiki-Nya et al. IEEE TMM 2011 and Köppel et al. ICIP 2010: depth hole first, then a background
  sprite, then Laplacian membrane, texture synthesis only as a last resort; Gautier, Le Meur &
  Guillemot 3DTV-CON 2011 one-sided structure-tensor fill; Buyssens et al. IEEE TIP 2017 depth first
  then colour candidates restricted to that depth). Our membrane/wash is their Laplace fill; the
  comparison papers are the evidence that a smooth fill beats a clone for a moving viewer. What we
  never did: **fit the far rim's depth field as a plane (or linear continuation) per hole** and use
  that as the plug depth — derivable, no constant, and the answer to both "too deep" (E2) and
  "tunnelling" (E1) when the rim is the background.
- **Unreliable boundary layer** (Müller et al. EURASIP JIVP 2008: main layer + foreground boundary
  layer + background boundary layer a few px either side of each depth edge, warped separately, the
  far boundary layer dropped where anything else lands; VSRS boundary-noise removal, Tanimoto et al.
  MPEG 2008, Lee & Ho APSIPA 2009; Zinger, Do & de With JVCIR 2010: pixels at strong depth
  discontinuities are not warped at all, every pixel carries a reliability weight = distance to a
  depth edge). Our blurred ramp (M6) is their untrusted layer: **assign each ramp texel to the near
  or far plateau explicitly, exclude ramp texels from geometry and from wash seeding.** One derived
  width (the ramp's own measured profile), no threshold.
- **Depth-weighted push–pull** (Solh & AlRegib, IEEE JSTSP 2012: Gaussian pyramid ignoring hole
  pixels, expand back down, far pixels weighted up): a GPU membrane whose only parameter is
  log2(max hole width). A real-time replacement for our multigrid wash.
- **Reliability channel** (Zinger 2010; Ahn & Kim IEEE Trans. Broadcasting 2013: tensor priority +
  confidence near foreground boundaries + background-only candidates): distance-to-cliff and local
  depth variance per texel, used for seeding weights and silhouette alpha. Cheap in a fragment
  shader.
- **Analytic hole geometry** (Zhu & Li, IEEE Trans. Broadcasting 2016): hole width = baseline ×
  (disparity_near − disparity_far). Sizes the sweep and plug extent from the maximum eye offset
  rather than any dilation constant (we do this implicitly with the sweep; the closed form is the
  check).
- **Depth-guided exemplar inpainting** (Criminisi et al. TIP 2004 → Daribo & Pesquet-Popescu MMSP
  2010 with a level-regularity priority and depth-SSD; Oh, Yea & Ho PCS 2009 background priority):
  seconds per frame, clones texture, empirical weights. Not for us as an algorithm; three rules
  transfer (depth first; far rim only; rank rim texels by low depth variance / distance from the
  cliff).
- **Layered depth images** (Shade, Gortler, He & Szeliski, SIGGRAPH 1998; Hedman et al. Casual 3D
  Photography SIGGRAPH Asia 2017; Hedman & Kopf Instant 3D Photography SIGGRAPH 2018 — a two-layer
  front/back panorama mesh with the back layer extended behind silhouettes). Our plug is a two-layer
  LDI whose back layer comes from a synthetic pose sweep instead of real views. The k-layer case
  (E5) is the LDI's native form; we have one layer.
- **Learned successors** (Tulsiani, Tucker & Snavely ECCV 2018 two-layer LDI from one image; Niklaus
  et al. 3D Ken Burns SIGGRAPH Asia 2019; Shih et al. CVPR 2020 — verified defaults: disparity edge
  threshold 0.04, edge dilation 10/5 px, background thickness 70, context thickness 140, edge
  segments < 10 px dropped, synthesis region dilated 5 px "to compensate for imperfect depth", 2–3
  min per image; Kopf et al. One Shot 3D Photography SIGGRAPH 2020; SynSin CVPR 2020 soft z-buffer
  splats; SLIDE ICCV 2021 soft two-layer split via matting; Worldsheet 2021; DIBR CNNs Cai et al.
  JEI 2020, CFFHNet IEEE TIP 2023). None runs per frame in WebGL, all hallucinate texture, all carry
  empirical thresholds. Their structural choices transfer: connectivity-torn LDI, depth-then-colour,
  a soft alpha layer for porous silhouettes.

**Never solved in this corpus:** interior self-occlusion of one object (every method fills with
background — our "too deep" is the standard failure, E2); porous and thin structures (E6, E7 —
acknowledged failure cases from Fehn to Shih, SLIDE the one attempt); floor-meets-wall vs object
(B1/B2/E9 — "far = background" is assumed throughout); zero-tuning constants (VSRS and Shih expose
empirical thresholds); 2-D parallax at 45° (V1/V2 — the corpus assumes small horizontal baselines,
so vertical disocclusion and top/bottom rims are untreated); real-time single-image quality (fast
methods are washes, good methods are minutes per frame).


### 2.2 Single-image 3D photography and layered representations

- **The LDI is the representation** (Shade, Gortler, He & Szeliski SIGGRAPH 1998): hidden content is
  stored per lattice position, zero-to-many samples, composited by McMillan ordering. Kopf et al.
  (One Shot 3D Photography, SIGGRAPH 2020) is the closest production analogue of our pipeline — LDI,
  inpainting on the LDI by connectivity traversal, chart atlas, mesh, seconds on a phone — and it is
  "not limited to at most two layers": interior self-occlusion (E2) and stacked occluders (E5) are
  native to a multi-layer LDI and impossible for a single plug. Kopf also **continues the depth EDGE
  into the disoccluded region** under constraints, so the fill's depth profile is shaped rather than
  flat.
- **Shih et al. CVPR 2020, at code level**: MiDaS disparity rescaled to [0, 3]; discontinuity
  |Δ(1/depth)| > 0.04; five passes of sparse bilateral weighted median (windows 7,7,5,5,5, σ_s 4 px,
  σ_r 0.5) with the range kernel zeroed across discontinuities; per edge component a flood on the
  FAR side to 70 px (synthesis) and 140 px (context) at a 960-px long side, i.e. ~7 % / 15 % of the
  image; edges cleaned (dangling, redundant, dilate 10 then 5). Region size is a fixed fraction of
  the image; for us it should be the analytic hole width from the known eye offset.
- **SLIDE (Jampani et al. ICCV 2021, read in full) is the single most reusable paper.** Two layers,
  both meshes, one forward pass (0.07 s; 0.35 s with matting). (i) **Soft visibility** A =
  exp(−β‖∇D‖²): the cliff becomes transparent instead of torn, so skirts cannot form and a porous
  silhouette shows the plug through its gaps. (ii) **Geometry-derived disocclusion extent**: a pixel
  can be disoccluded if some scanline neighbour at pixel distance K has D(x,y) − D(neighbour) > ρ·K;
  with our eye offset bounded, ρ = 1/(g·b_max) with g the parallax gain and b_max the maximum offset
  — no free constant, and the plug's depth never needs to exceed the depth that satisfies it, which
  bounds both "too deep" and "tunnelling" analytically. (iii) MiDaS is Gaussian-blurred then
  **max-pooled by the blur radius** so mixed boundary pixels land on the foreground layer — ramp
  ownership by construction. (iv) Matting only inside the thin band M̄ − M around cliffs (U2Net →
  FBA), never leaked into the background. (v) Its inpainter is trained with fattened-foreground
  occlusion masks so it learns to borrow only from farther pixels. β, ρ, γ are not stated in the
  paper or supplement (a public re-implementation uses β = 3); the derivations above replace them.
- **Niklaus et al. 3D Ken Burns SIGGRAPH Asia 2019, at code level**: points are dropped where
  |Laplacian(normalised disparity)| ≥ 0.03 (`tenValid`) — a second cheap skirt filter; the
  disocclusion fill scans 16 directions and takes the endpoint with GREATER depth (far rim only);
  **semantic ground anchoring**: person/vehicle/animal instances get their disparity replaced by the
  max disparity of their bottom 3 % rows, so the object stands on its contact instead of leaning
  (E9); render from 1.1× the maximum shift to find the holes.
- **Single-view MPIs** (Tucker & Snavely CVPR 2020: 32 planes, colour per plane blends the input
  with ONE predicted global background image, which is low-frequency — validating the membrane;
  without it "blurriness and repeated edge artefacts at depth boundaries"; MINE ICCV 2021; AdaMPI
  SIGGRAPH 2022, warp-back training, "inpainting fails under large viewpoint change"; **TMPI ICCV
  2023**: 12.5 %-width tiles, per tile a confidence-weighted 3-cluster k-means on disparity places
  four planes — a tuning-free local rule for plug depth (the farthest local mode) that never asks
  whether a texel is object or wall; SinMPI SIGGRAPH Asia 2023). Soft alpha spreads a cliff over
  2–3 planes; all trained at RealEstate10K baselines.
- **Worldsheet ICCV 2021** states our design's necessity from the other side: a single sheet
  connecting foreground to background "causes artifacts near object boundaries"; the fix is multiple
  alpha-textured sheets. **SynSin CVPR 2020**: soft z-buffer splats (radius 4 px, K = 128) plus a
  refinement GAN; not an asset.
- **Generative NVS 2023–2026** (ZeroNVS, GenWarp, ViewCrafter, Stable Virtual Camera — whose v1.0
  shipped "foreground objects detached from the background" —, WonderJourney, LucidDreamer, Invisible
  Stitch, Flash3D, Splatt3R, DepthSplat): none yields a per-pixel layered asset for a browser in real
  time. Two ideas transfer: Flash3D (3DV 2025) predicts **two Gaussians per pixel with the second
  parametrised as a positive depth increment behind the first** — the constraint form for a second
  plug sample; Invisible Stitch's depth completion conditioned on image + partial depth + mask is the
  bake-stage plug depth. Their inpainters, prompted with fattened-foreground masks, are the texture
  stage.
- **Open in this corpus**: no single-image method recovers hidden-surface depth; every pipeline is
  designed and evaluated at RealEstate10K baselines, so 45° off-axis is outside all published
  regimes; porous silhouettes only via mattes, which fail where depth fails; edge/colour misalignment
  and quantised depth remain hand-thresholded heuristics; scale/parallax ambiguity is fixed by one
  arbitrary gain in every method.

### 2.3 Depth edges, soft boundaries, thin structures, foliage

- **Every ramp pixel is a flying pixel** (Sabov & Krüger SCCG 2008 on ToF mixed pixels; the
  practitioner "depth discontinuity filter"): sensor practice discards them, never keeps them as
  geometry. The mesh tear is the right default; the missing safety net is a **threshold-free,
  view-dependent test in the shader — a triangle whose normal is near-perpendicular to the view ray
  is a skirt** whatever the depth step, and that test stays valid at 45° where any fixed step does
  not (M6, and the A257e/f/g skirts).
- **Resample, don't smooth** (Displacement Fields, Ramamonjisoa, Du & Lepetit CVPR 2020: a
  displacement field collapses the ramp onto one side; SharpNet ICCV-W 2019; Koch et al. iBims-1
  ECCV-W 2018 as the evidence that CNN depth is systematically over-smoothed at edges). The
  training-free equivalent with published constants is Shih 2020's discontinuity-aware weighted
  median (five passes, windows 7,7,5,5,5, weights zeroed across the discontinuity mask): the ramp
  snaps to a plateau. Means (guided filter, bilateral solver) re-blur and follow RGB texture edges;
  if used, only with confidence zero inside the ramp band.
- **Ramp ownership = far side, snapped to the RGB edge** (Hoiem, Efros & Hebert IJCV 2011 figure/
  ground; DOC/DOOBNet orientation, P2ORM ECCV 2020 pairwise occlusion; DepthCut SGP 2017 layering
  by the discontinuity graph): the colour edge marks the owner's silhouette, so ramp texels belong to
  the far plateau unless the RGB edge says otherwise. Jump edges vs crease edges are told apart by
  local plane-fit residuals, not gradients — gradient tests fire on creases and steep floors, which
  matters at grazing views (E3).
- **Zitnick et al. SIGGRAPH 2004 is our design with the missing piece.** Verified from the paper:
  discontinuity = disparity jump > 4 px; within a 4-px band Bayesian matting gives foreground colour,
  alpha and alpha-weighted depth; that band becomes a sparse foreground **boundary layer** (~1/64 of
  the data) while the background stays in the main layer; the matte is dilated 1 px inward; triangles
  spanning a discontinuity are erased; rendering blends and normalises by alpha. Main mesh + plug +
  an alpha-matted foreground strip — the strip is what we lack for E8 (hair, fur, blur).
  Hasinoff, Kang & Szeliski CVIU 2006 states fuzzy boundaries as the limitation of sharp mattes;
  Soft 3D (Penner & Zhang SIGGRAPH Asia 2017) keeps a per-pixel depth distribution — the ramp is a
  crude version of that signal, and "near plateau with alpha from ramp position, far plateau
  behind" is its single-image analogue. SLIDE ICCV 2021 (soft visibility from disparity
  discontinuities × an optional matte; users preferred it on hair) and the 2026 HairGuard / αDepth
  preprints are the learned forms.
- **A better depth model will not fix porosity.** Depth Pro's boundary metric scores recall against
  the alpha = 0.1 contour of matting datasets, i.e. the OUTERMOST extent of hair and foliage, so a
  model that scores well assigns foreground depth to the whole silhouette including its gaps —
  exactly the bristlecone's map (E6). Porosity must come from the image.
- **Porous vs solid, without a hand threshold**, from forestry: gap fraction (gap pixels over the
  crown envelope, Otsu-binarised), the Euler number of the binarised silhouette (components minus
  holes; strongly negative for crowns), the box-counting dimension difference between silhouette and
  outline (≈ 0 for a solid blob), lacunarity. Recipe for image + depth: envelope from the
  discontinuity graph; inside it classify texels foliage vs background by colour (two-cluster / Otsu
  against the plug's rim colour) or matting alpha; porous when the Euler number is strongly negative
  AND gap fraction is non-trivial AND RGB shows edges where depth shows none — the blur radius sets
  the smallest gap depth can register, so any RGB hole below that size is diagnostic. Every constant
  is data-derived or inherited (alpha 0.1; t ∈ [1.05, 1.25]; the 4-px band).
- **What to render for foliage**: single-image tree modelling (Tan et al. SIGGRAPH 2008; Tree-D
  Fusion ECCV 2024) fills a crown envelope with stochastic porosity, never per-gap depth; volumetric
  methods (NeRF, 3DGS) use per-sample alpha. The single-image answer: the crown is a near layer with
  alpha coverage inside its envelope and the plug shows through the holes — not an interior-step
  fill at branch depth.
- **Thin structures** (E7): a structure of width w under a blur of width b > w never reaches its own
  depth (amplitude ≈ w/b), so it vanishes or sits mid-ramp and drags background. Detect ridges in
  disparity (top-hat / ridge filter, width ≤ 2b), restore their disparity by the max within the ridge,
  tear both sides; a thin structure is a pair of opposite-ownership occlusion edges within b pixels
  — threshold-free given b. Miangoleh et al. CVPR 2021: thin detail appears only when inference
  resolution fits the edge density (R0/R20), so run the estimator at higher resolution on patches when
  thin features are detected. CurveFusion 2021 fails for wires near a wall for lack of depth
  resolution — the 8-bit case.

### 2.4 The geometry behind a silhouette: backs, thickness, amodal priors

- **Nobody in the literature fills a self-occlusion at the object's own depth, and nobody leaves it
  to the background either: the consensus picture is side first, then background.** Layered
  methods (Dhamo et al., Pattern Recognition Letters 2019; Tulsiani, Tucker & Snavely ECCV 2018;
  Shih CVPR 2020; SLIDE ICCV 2021) inpaint the reveal as background at background depth and
  leave the object a zero-thickness card. Inflation and body methods (Teddy SIGGRAPH 1999;
  Monster Mash SIGGRAPH Asia 2020; Photo Wake-Up CVPR 2019; ECON CVPR 2023) give the object a
  closed side of thickness proportional to its width and let the background appear beyond it.
  The user's principle ("a gap inside the head-on silhouette must never show the distant
  background") is therefore stronger than the literature supports; whether the background shows
  depends only on thickness × parallax, and at an eye offset ≈ portal distance the revealed band
  ≈ thickness, so a side 0.7 × width deep covers most of the reveal for compact objects and,
  correctly, not for thin ones. Our tunnelling violated both rules; our thin band came from an
  underestimated thickness, not from the approach (E4).
- **Monster Mash's Poisson inflation is the best-justified zero-tuning thickness rule.** Verified
  from `src/reconstruction.cpp` (google/monster-mash): Δz = −c inside the region, z = 0 on the
  outline, z ← sgn(z)·√|z|, front and back solved separately with ±c, `defaultInflationAmount = 2`.
  For a disc of radius R the solution is c(R² − r²)/4, so after the square root the profile is a
  hemi-ellipsoid of peak height R·√c/2 = 0.71 R per side: **thickness ≈ 0.71 × local width**,
  self-scaling, resolution-independent, smooth (no crease at the spine, unlike our medial-ball
  envelope). Overlapping parts are pushed apart in z (ARAP-L), which is the treatment of internal
  self-occlusion (E2): separate layers per part, never a tunnel. Photo Wake-Up does the same with
  body-part labels; a torso is ~0.25–0.35 of shoulder width thick in SMPL terms.
- **Our A257d scale fit was the wrong instrument.** The pass's judgement, which I accept: a
  normalised, blurred 8-bit depth map cannot resolve a bulge of a few centimetres inside a scene
  spanning metres, so a scale fitted to the front bulge comes out near zero. Thickness must be
  expressed in world units through the image's focal length: a silhouette w px wide at metric depth
  Z is Z·w/f wide in the world (Depth Pro ICLR 2025 predicts f and metric Z; MoGe/MoGe-2 CVPR 2025 /
  NeurIPS 2025 recover FOV; UniDepth v2 predicts intrinsics). With metric depth the ratio
  thickness / scene depth range is scale-free and survives the diorama's slider compression. This
  is the answer to M9 and to the "isotropic vs 0.64" confusion of Addendum 190.
- **Ground contact** ("Floating No More", 2024; pixel-height maps, Sheng et al. 2022): the inflated
  side must terminate on the ground plane at the silhouette's lower edge; shadow footprint is the
  only image cue to depth extent and needs a light direction. The cheap justified bound for E9.
- **Per-pixel entry/exit depth** (Shin, Ren, Sudderth & Fowlkes ICCV 2019 — the only scene-level
  predictor of an object's back surface; synthetic indoor; weights apparently never released) is the
  right target representation for any thickness field we build, whatever produces it.
- **Amodal completion** (Zhu et al. CVPR 2017; Zhan et al. CVPR 2020; pix2gestalt CVPR 2024;
  Amodal3R ICCV 2025; Amodal Depth Anything ICCV 2025) completes a silhouette hidden by ANOTHER
  object. Ours is complete and needs depth extent; only the ordering cue transfers and the depth map
  already gives it. Applicable to E5 (stacked occluders) later, not to E2/E4.
- **Single-image object generators** (TripoSR < 0.5 s; Hunyuan3D-2 10–25 s; TRELLIS ~16 s; Wonder3D
  2–3 min; all need a segmented centred object, all hallucinate the back, Janus failures documented):
  at most an offline per-object pre-pass for a low-frequency thickness field, never texture; at 45°
  one sees the side, never the back. **Symmetry priors** (unsup3d CVPR 2020 and successors) say
  nothing about depth extent in a head-on view.

### 2.5 Structured backgrounds: planes, ground, sky, semantics

- **The membrane is the wrong background model under rim-less surfaces (B1, B2, E9).** The 2024–25
  single-image-to-3D literature (Gen3DSR 3DV 2025; LayerPano3D 2024; Scene4U 2025; Generative
  Omnimatte 2025) converged on one rule: **background = the union of panoptic "stuff" classes
  (wall, floor, ceiling, ground, road, sky, water, vegetation mass), represented as a surface fitted
  to their depth; "things" are the separable layers.** Only things may tear; stuff is background even
  when it has no holes. This is the decision our rest-silhouette mask lacks, and the reason the cave
  wall and the floor became "objects".
- **Planes as the background continuation.** Learned plane nets (PlaneRCNN CVPR 2019; PlaneAE CVPR
  2019, 30 fps; PlaneTR ICCV 2021; PlaneRecTR ICCV 2023; PlaneSAM 2024) collapse outdoors; the
  MonoPlane recipe (2024: GC-RANSAC + normal consistency on monocular depth + normals) works
  wherever the depth is roughly right. A plane (n, d) is defined at every pixel, so the occluded
  region behind a thing in front of it is the plane evaluated there: it cannot sag because it has no
  free interior. Fit a few large planes to our own depth on stuff pixels in the bake; zero real-time
  cost (a dot product per vertex).
- **Gravity, horizon, focal** (GeoCalib ECCV 2024; Perspective Fields CVPR 2023; GroundNet ACM MM
  2019): with gravity g and focal f the ground plane has normal g and one scalar (camera height)
  fitted to depth below the horizon; every pixel below the horizon then has a lower bound on its
  background depth, and the floor's own depth equals the bound, so it can never be foreground. The
  two physical constants the pipeline is missing.
- **Sky as a hard class** (Liba et al. CVPRW 2020 sky segmentation, < 0.5 s on a phone; MoGe's
  validity mask; "Modeling Depth Ambiguity" 2026 sky mixture component): depth = far plane, never a
  rim or anchor for the membrane; in an 8-bit map sky is clamped at 255 anyway and the segmentation
  says which 255s are sky (B3, and the bristlecone's sky "objects").
- **Room layout** (HorizonNet CVPR 2019; LED²-Net CVPR 2021 — layout AS a renderable depth map;
  uLayout 2025 for perspective images; Total3DUnderstanding CVPR 2020; Structured3D ECCV 2020 for
  training data): indoor only, cuboid-biased; the cheapest usable output is a per-column floor
  boundary row, ~W numbers per image, giving the floor's extent behind every object.
- **Hidden-background depth from diffusion** (InFusion 2024 — a Marigold-derived depth-completion
  diffusion model on (inpainted RGB, incomplete depth, mask); Invisible Stitch 2024; SPIn-NeRF CVPR
  2023 inpaints disparity with LaMa; NeRFiller CVPR 2024; Text2Room ICCV 2023): the hidden depth is a
  smooth interpolant of the rim in all of them, floors bulge into the hole, seconds to minutes. Bake
  stage only, after planes; colour-conditioned depth completion beats geometry-only extrapolation
  because colour says whether the hole is floor or wall. ControlNet-depth and SD2-depth consume
  depth, they do not produce it (texture stage only).
- **The unanimous classical rule** (Shih 2020, verified from `argument.yml`: disparity difference
  > 0.04 after five passes of discontinuity-aware weighted median, context 140 px grown only on the
  background side, synthesis 70 px, nets in the order edge → colour → depth so a wall–floor crease
  continues behind the object; Kopf 2020 grows background pixels into the occluded region with
  smoothly continued background depth; AdaMPI 2022 and SinMPI 2023 use an edge → depth → image
  inpainter): **extrapolate depth from the far side only, edges first.** We have the far-side rule;
  we lack the edge-first structural continuation and any bound on how far extrapolated depth may run.

### 2.6 Evaluation and synthetic ground truth

- **The field's default metric hides our problem.** Tucker & Snavely CVPR 2020, Shih 2020, MINE
  ICCV 2021, SLIDE, AdaMPI all score held-out video frames with whole-frame PSNR/SSIM/LPIPS, where
  disocclusions are < 5 % of pixels. The precedents for scoring the hidden region alone are SynSin's
  Vis / InVis split (CVPR 2020) and amodal mIoU_occ; FID/KID on patches where there is no single
  truth (Infinite Nature 2020); Lai et al. ECCV 2018 warping error with flow and occlusion masks for
  temporal coherence. Spring (Mehl et al. CVPR 2023) ships evaluation maps for sky, detail (thin
  structures) and unmatched (disocclusion) regions — the region-map design to copy.
- **Ground truth for what lies behind an occluder** exists in three grades: hidden-occluder
  re-render (Dhamo 2019 on SceneNet: hide the instance, re-render RGB + depth — colour AND correct
  illumination; the only route that is right for glass/mirror/water), multi-hit ray casting (Shin
  2019), depth peeling (pass k with z > z_{k−1}). None of the 3D-photo papers render the same scene
  from an offset eye, which is our gold standard: an off-axis sheared frustum at ±45°
  (Blender shift_x/shift_y).
- **Generators**: BlenderProc 2 (depth, distance, normals, instance, flow, stereo, arbitrary poses;
  a few lines per element scene) as the backbone; Infinigen (BSD-3) for foliage, hair and terrain
  that are true geometry so k-layer peeling is exact; Kubric (Apache-2.0, GSO objects) runner-up;
  Unity/Habitat fast but rasterised, no hidden-layer shading or glass physics; Habitat + Replica once
  as a realism check with annotated mirrors (`glass.sur`). Existing datasets with occlusion truth:
  MPI-Sintel (occlusion masks, blur, defocus, fog), Middlebury 2014 (nonocc/all), Spring, Hypersim
  (461 scenes, trajectories), TartanAir (flow with occlusion masks), LayeredDepth-Syn (multi-layer
  depth for transparent objects).
- **No 3D-photo paper documents a depth-corruption protocol**; AdaMPI's warp-back uses raw DPT depth.
  The degradation ladder has to be ours (§4).

### 2.7 The depth estimator is part of the system

- **Output spaces differ and our pipeline ignores it.** MiDaS/DPT, Depth Anything V2, Video Depth
  Anything and DepthCrafter are affine in DISPARITY; Marigold is affine in depth; ZoeDepth,
  Metric3D (needs a focal, else guesses among nine), UniDepth (predicts intrinsics), Depth Pro
  (metric + focal, 1536² native, 0.3 s) and MoGe-2 (metric, FOV, sky validity mask) are metric. A
  step Δ in normalised disparity is Δ·Z² in depth, so any fixed threshold in normalised units is far
  more permissive far away — which is why our tear step and lip tolerances behave differently across
  scenes. Depth Pro's boundary code uses a scale-free ratio test instead: an occluding contour exists
  where Z_far/Z_near > t, t swept 1.05–1.25 (verified in `eval/boundary_metrics.py`).
- **Storage.** No research pipeline stores 8-bit depth as its working format (MiDaS/Marigold/
  Boosting/ZoeDepth 16-bit PNG, Depth Pro/VDA/DepthCrafter float npz/EXR, Shih log-depth .npy);
  the one shipping 8-bit format (iPhone Portrait JPEG) is disparity-encoded. Our M7 terraces are a
  self-inflicted artefact; 16-bit inverse or log depth ends them.
- **Edge ramps** are roughly constant in network-input pixels and scale with (image width / network
  input width) after upsampling (Miangoleh et al. CVPR 2021 R0/R20 argument); our 4 px at 1200 px
  matches a 1–2 px ramp at 384–518 px input. Shih's discontinuity-aware weighted median (five passes,
  edge pixels excluded from the support) shrinks the ramp before tearing; UniDepthV2's edge-guided
  loss and the "sharp boundary" losses target the same thing at training time. The ramp is also the
  origin of flying pixels (M6, M8).
- **Scale and parallax.** Shih invents intrinsics (f = max(H, W), ~53° FOV) and moves the camera
  ±1.5 % of the frame; Google Cinematic Photos solve the parallax amplitude per photo against a
  "stretchiness" loss; Apple spatial photos limit the baseline to one IPD and warn that 2–3 % of
  width of convergence offset "dramatically alters depth perception". **No published single-image
  method operates anywhere near 45°, and the gallery envelope of §1.4 runs to 85°; we are one to two
  orders of magnitude beyond the literature's parallax budget.** That is not a reason to stop, but it
  is the reason every artefact is magnified, why the synthetic suite must sweep eye offset to 85°, and
  why the far half of the envelope is a generation problem (V1) before it is a disocclusion problem.

## 3. Techniques to combine

The literature does not contain our system, but it contains every piece of it. Read together, the
seven passes describe one pipeline. Everything heavy runs once per image in the bake; the real-time
part is a shader with three rules.

### 3.1 The bake, in order

| step | technique | source | replaces / adds in our pipeline | elements served |
|---|---|---|---|---|
| A1 depth | metric depth + focal length (Depth Pro; MoGe-2 as second opinion; DA-V2 relative for speed); float/16-bit inverse-depth storage; diorama sliders applied in disparity space | §2.7 | 8-bit linear PNG; unknown x/z scale; the fitted 0.64 | M7, M9, M5 |
| A2 calibration | gravity, horizon, focal (GeoCalib / Perspective Fields); ground plane = normal g, camera height fitted to depth below the horizon | §2.5 | nothing today | B2, E9, B1 |
| A3 semantics | panoptic stuff/things + a sky class (any current panoptic model; Liba-style sky net); only things may tear, stuff is background even without holes, sky is at infinity and never an anchor | §2.5 | the rest-silhouette mask (`dQ − farField > TOLB`) that made the cave wall and floor objects | B1–B3, E9, the bristlecone's sky objects |
| A4 edges | jump edges by the scale-free ratio test (Z_far/Z_near > t, t ∈ [1.05, 1.25]) on the thing/stuff boundary and inside things; measured ramp width b; five-pass discontinuity-aware weighted median to snap the ramp, then max-pool by b so mixed pixels land on the front layer (SLIDE); ramp ownership = far side snapped to the RGB edge; jump vs crease by plane-fit residual | §2.2, §2.3, §2.7 | fgTearStep in normalised units; RWD as a cited constant; the ramp rendered as geometry | M6, M8, E3 |
| A5 thin structures | ridge detection in disparity (width ≤ 2b), disparity restored to the ridge max, both sides torn; optional higher-resolution patch inference where ridges are found | §2.3 | the tear feather alone | E7 |
| A6 porosity | per thing: Euler number, gap fraction over the envelope, RGB-edges-without-depth-edges; porous → alpha-coverage crown layer over the plug; solid → object back | §2.3 | the interior-step rule applied to everything | E6 vs E2 |
| A7 background | planes fitted to stuff depth (RANSAC + normal consistency, few large planes), bounded by the ground plane; sky at infinity; membrane only where no plane; hidden depth behind a thing = nearest supporting plane along the ray; later: colour-conditioned depth completion (InFusion / Invisible Stitch class) for the residue | §2.5 | the far-rim membrane as the whole background model | B1, B2, B4, E1 |
| A8 object backs | Poisson inflation with c = 2 (Monster Mash): thickness 0.71 × local width, in world units through the focal; per-part layers at internal cliffs (Photo Wake-Up / ARAP-L); side terminates on the ground plane at the silhouette's lower edge | §2.4 | the medial-ball envelope and the bulge-fitted scale | E4, E2, E9 |
| A9 boundary layer | Zitnick's 4-px matte strip (alpha, foreground colour, alpha-weighted depth) as a sparse foreground layer; the discontinuity mask dilated by b is the free trimap | §2.3 | the hard tear at one depth | E8 |
| A10 plug | k-layer LDI (2–3 layers) from the pose sweep, extent bounded by SLIDE's analytic disocclusion condition at b_max; depth = plane / far-rim continuation with Kopf's edge continuation into the hole, or TMPI's farthest local disparity mode where no plane exists, never the near depth, never below the deeper lip of a solid interior step, second sample as a positive increment behind the first (Flash3D); colour = depth-weighted push–pull wash from the far rim; texture later by depth-conditioned diffusion prompted with fattened-foreground masks | §2.1, §2.2, §2.5 | the single-layer median plug | E1, E2, E5, B5–B7 |

### 3.1b What the gallery envelope changes in the bake

- **A7 grows from "background behind things" to "the scene beside the frame".** Planes, the ground
  plane and the sky are the only background models defined outside the photographed frustum; they
  are the geometry of the outpaint, extended by e_max·d/D per side per depth. The membrane cannot
  extrapolate that far; a plane is defined there by construction.
- **A8 must close the object to its equator**, textured on the side: Monster Mash's inflation already
  produces a closed front-and-back surface; the texture of the flank is generated (a wash is
  acceptable geometry, not acceptable appearance at 75°).
- **A10 becomes a small layered scene**: k-layer LDI for hidden layers between things AND an
  outpaint layer at depth for V1, both with pose-independent texture, sized by f(d, e) over the
  envelope instead of by the sweep's per-pose reveals.
- **The demand region is the envelope integral**: for each plate texel and depth, the set of eye
  positions on the gallery envelope that see it through the aperture; the frame's keystoning
  removes near-side content and adds far-side content. This replaces the 85-pose cone sweep with a
  closed-form visibility footprint per depth layer (the window model above is linear in e).
- **The texture stage moves forward.** Depth-conditioned diffusion inpainting/outpainting (§2.5,
  §2.2: ControlNet-depth / SD2-depth with fattened-foreground masks for the plug, Invisible-Stitch-
  class depth completion for its depth) is the only known way to produce the far half of the
  envelope. It runs once per image in the bake and its output is an asset, so V4 holds.

### 3.2 The real-time part

Three shader rules, all view-dependent, none with a scene constant: (1) soft visibility α = exp(−β‖∇D‖²) at cliffs (SLIDE), β set so the smallest step already treated as a cliff spread over the measured ramp width gives α ≈ 0 — a transparent cliff instead of a torn one, which also lets a porous crown show the plug through its gaps; (2) discard any triangle whose normal is near-perpendicular to the
view ray (the flying-triangle / skirt kill — this alone would have removed the A257e slab and the
bristlecone bars without A257f/g); (3) composite layers front to back with the boundary layer's alpha
and the crown layer's coverage. A per-texel reliability channel (distance to the nearest jump edge,
local depth variance) rides along for seeding weights and silhouette alpha.

### 3.3 Element coverage, and what stays open

| element | covered by | open |
|---|---|---|
| E1 true disocclusion | A7 planes + A10 far-rim plug | texture (SD stage) |
| E2 interior step, solid | A6 solid + A8 per-part backs + A10 deeper-lip floor | thickness of the far part when it is itself thin |
| E3 glancing continuous surface | A4 crease vs jump + A3 stuff never tears | — |
| E4 object side | A8 inflation at 0.71 × width in world units | the user's principle vs "side first, then background" — a decision, not a technique |
| E5 stacked occluders | A10 k-layer LDI | k > 3; ordering when the sweep sees layers at different poses |
| E6 porous silhouettes | A6 porosity + crown alpha layer | per-gap depth is not recoverable from one image; the crown is an envelope |
| E7 thin features | A5 ridges + double tear | features narrower than one network pixel are gone before we see them |
| E8 soft edges | A9 boundary layer | motion blur and defocus where the depth edge and the image edge genuinely disagree |
| E9 contact with support | A2 ground plane + A3 stuff/things + A8 ground clamp | objects on non-planar supports |
| E10 frame edge | A214 contract (outpaint) | — |
| B1–B4 planes, ground, sky, distance | A2, A3, A7 | curved backgrounds (the cave) fall back to the membrane |
| B5–B8 clutter, repetition, text, lighting | A10 layers; texture stage | shadows detach from objects unless treated as stuff |
| M1–M4 glass, mirror, specular, dark | none | documented failure classes for every single-image method; detect and flag (LayeredDepth-Syn shows the ambiguity) |
| M5–M9 estimator artefacts | A1, A4 | the ramp width b is measured per image, not assumed |
| V1–V5 viewer | A10 sweep sized by the analytic hole width; rest pose untouched by construction | no published comfort bound at our offsets |


## 4. Synthetic test suite

### 4.1 Principles
- One element per scene, ground truth for what lies behind every occluder, and the SAME scene
  rendered from the offset eye through the portal's own sheared frustum — the gold standard none of
  the 3D-photo papers use.
- Two axes crossed with every scene: eye offset {15°, 30°, 45°, 60°, 75°, 85°} × {horizontal,
  vertical, diagonal}, at viewing distances {0.5, 1, 2} × window width, through the portal's own
  sheared frustum with the frame's aperture applied (so keystoning is in the truth); and a depth-degradation ladder that reproduces the estimators (§2.7): 16-bit vs 8-bit
  (linear and disparity), edge blur σ ∈ {0, 1, 2, 4} px scaled by image/network width, edge erosion/
  dilation ±1–3 px (halos), affine scale/shift in disparity, ±20–30 % focal error, low-frequency
  floor/sky bowing, thin-structure erasure below 1–2 network pixels, and finally a real estimator
  (Depth Pro, DA-V2, Marigold) run on the render.
- Ground truth per scene: RGB + float depth from the portal camera; depth-peeled layers 2–3;
  hidden-occluder re-render (RGB + depth, correct illumination); instance and stuff/things masks;
  offset-eye renders; GT flow portal → eye with occlusion mask, so the disocclusion mask is exact.
- Generator: BlenderProc 2 for authoring and rendering (a few lines per scene, depth/normals/
  instance/flow/stereo built in, hidden-occluder re-render and depth peeling trivial, Cycles
  illumination for hidden regions); Infinigen assets for foliage, hair and terrain because they are
  true geometry; Kubric for object-on-table variants; one Habitat + Replica pass for real scanned
  interiors with annotated mirrors.

### 4.2 The scenes (26; our existing four in brackets; S17–S20 deferred with the material classes)

| # | scene | isolates | GT needed beyond the standard set |
|---|---|---|---|
| S1 | room corner: two walls + floor, textured | plane continuation (B1), 8-bit terraces on slow gradients (M7) | — |
| S2 | boxes on a textured floor | contact line (E9), floor under and behind objects (B2) | — |
| S3 | the same boxes floating | touching vs detached (E9 control) | — |
| S4 | a standing figure against a far wall [figure] | true disocclusion (E1) | — |
| S5 | thin pole 0.5–3 px in front of a textured wall [pole] | thin features (E7), ramp vs width | layer 2 only |
| S6 | wire / fence grid | sub-pixel occluders, sheet formation (E7) | — |
| S7 | porous canopy (Infinigen tree) against sky | porosity (E6), sky (B3) | k = 3 peeling |
| S8 | hair / fur (particle hair converted to mesh) | soft edges (E8) | alpha matte GT from the hair render |
| S9 | three cards at three depths, overlapping | stacked occluders (E5) | k = 3 |
| S10 | posed humanoid, thigh over calf, arm over torso [fold, generalised] | interior step (E2), per-part backs | entry/exit depth per pixel |
| S11 | rounded solid (sphere, cylinder, torso) against a wall at several distances | object side thickness (E4): does 0.71 × width match the render? | entry/exit depth |
| S12 | object cut by the frame edge | outpaint contract (E10) | wider-FOV render |
| S13 | brick / tile wall behind an occluder | repetition (B6): plausible-but-misaligned plugs | — |
| S14 | text and signage behind an occluder | strokes (B7), hallucination penalty | — |
| S15 | sky + far mountains + a near occluder | infinity handling, near-zero parallax (B3, B4) | — |
| S16 | receding wall at a grazing angle with a ridge [screen / fold wall] | glancing continuity (E3), jump vs crease | — |
| S17 | glass pane in front of an object — DEFERRED | M1 | both truths |
| S18 | mirror on a wall — DEFERRED | M2 | virtual-depth flag |
| S19 | water surface with a submerged object — DEFERRED | M1 | both truths |
| S20 | strong specular on curved metal — DEFERRED | M3 | — |
| S21 | night scene, point lights, bloom | M4 low-SNR edges | — |
| S22 | motion blur and defocus (Cycles) | E8 where depth edge and image edge disagree | — |
| S23 | toon-shaded versions of S1, S5, S9 | M5 illustration style (estimator behaviour) | real-estimator ladder only |
| S24 | cluttered shelf | B5 many small disocclusions | k = 3 |
| S25 | figure standing on the floor with a cast shadow and a floor reflection | B8 shadows and reflections attached to the ground | hidden-occluder render without the object's shadow |
| S26 | a vertical-offset set: overhang, table edge, ceiling beam | V2 vertical reveals | vertical eye offsets emphasised |
| S27 | a room deeper than the window is wide (fishtank): back wall, side walls, floor, one object | V1 outpaint at depth: f(d, e) per layer; how much of the walk is photographed | wider-FOV source render (the truth beyond the frame) |
| S28 | the same room at three diorama depths (V6) | parallax realism vs photographed fraction | as S27 |
| S29 | gallery walk: a continuous eye path from −85° to +85° at two distances | V4 coherence of plug, sides and outpaint along a walk | GT video along the path |

### 4.3 Metrics
The purpose of §0b orders them. Primary, per layer and per class, against the synthetic truth:
- **scope precision and recall**, visibility-weighted over the envelope (the set of unphotographed
  texels visible from anywhere in the envelope is exact in the synthetic renders);
- **depth error inside the scope** against the peeled / hidden-occluder truth (median and bad-pixel
  rate) — what decides whether SD's texture will sit still;
- **stability**: change of scope mask, depth and placeholder RGB along the gallery walk (zero by
  construction for a static atlas; measured to catch anything per-pose that leaks in);
- **placeholder cleanliness**: clone index against the near lip (the ghost index of Addendum 180),
  streak/stretch count (grazing-triangle and edge-band tests), highlight legibility;
- **end-to-end**: SD inpainting on the atlas with the chart depth and mask, rendered through the
  envelope, scored on the exact scope region with masked LPIPS/DISTS and the disocclusion bad-pixel
  rate against the offset-eye truth — the only metric that says whether the scope and depth were
  good enough for the purpose.
Secondary, on the offset-eye render per eye offset, reported for the full frame, the exact
disocclusion region and a ±2 px depth-edge band (Spring's region maps):
1. masked LPIPS and DISTS on the disocclusion region — appearance of the fill (SynSin InVis precedent);
2. disocclusion bad-pixel rate: rendered depth vs the peeled layer-2 depth beyond δ (Middlebury bad2
   analogue) — "did the plug land at the right depth", which a head-tracked viewer sees as swimming;
3. temporal warping error along the head path with GT flow and occlusion mask (Lai et al. 2018) —
   popping and flicker;
4. edge-band PSNR/LPIPS — halos, skirts, stretched skin;
5. Depth Pro's boundary F1 and matting recall (port `boundary_metrics.py`) on our snapped depth;
6. degradation sensitivity — the slope of 1–3 against the ladder; a robust rule has a flat slope;
7. FID/KID on pooled disocclusion patches for the hallucination-only scenes (S12, S14);
8. the photographed fraction f(d, e) per layer reported alongside every score, so a fill is judged as disocclusion or as outpaint, never mixed;
9. (deferred with S17–S20) failure flags for the material classes.
Whole-frame PSNR is kept only as a sanity check. No perceptual study exists for head-tracked
disocclusion tolerance at our offsets; a small paired-comparison study on five scenes is the only
validation of the metric ranking.

### 4.4 Order of construction
S27 and S11 first — the two facts the gallery envelope turns on (how much of a walk is
photographed at all; how large an object's side really is at 75°) — then S1, S2, S5, S7, S10 (the
elements that failed this year: planes, contact, thin, porous, interior step). Then S9, S16, S26,
S29 (layers, viewing geometry, the walk). S21–S23 after; S17–S20 deferred with the material classes.


## 5. What the current pipeline is missing, in one list

0. **The deliverable as an object.** There is no static layered atlas with per-texel scope, class,
   depth, placeholder and visibility weight; the scope exists only implicitly as "where the plug
   draws" plus the orange outpaint mark, per pose, in the renderer. (§0b)
1. **A metric frame.** No focal length, no metric depth, so no x/z ratio, no thickness in world
   units, no analytic hole width; every constant in normalised depth units means something different
   in every image. (A1, A2)
2. **A semantic background.** Background membership is decided by a sagging membrane; the literature
   decides it by stuff/things and sky, then fits planes. (A3, A7)
3. **Planes and a ground plane.** Nothing in the pipeline knows a wall or a floor continues. (A7, A2)
4. **A scale-free edge test and a snapped ramp.** fgTearStep is a normalised threshold; the ramp is
   rendered as geometry and then patched by tears, floors and margins. (A4)
5. **Ownership of the ramp.** Ramp texels are assigned by depth midpoint, not to the far side at the
   RGB edge. (A4)
6. **A porosity decision.** The interior-step rule treats a tree crown as a torso. (A6)
7. **A boundary (matte) layer.** Hair, fur, blur and defocus have no representation. (A9)
8. **Object thickness with a justification.** The medial-ball envelope at a bulge-fitted scale
   underestimates by construction; Poisson inflation at 0.71 × width in world units is the cited
   rule, per part, terminating on the ground. (A8)
9. **More than one hidden layer.** The plug is one depth per texel; 80 k troll texels and 47 % of the
   silver warrior's band carry two. (A10)
10. **A view-dependent skirt kill.** A grazing-angle triangle test would have removed every skirt of
    Addendum 190 without an index or a stretch factor. (3.2)
11. **An analytic fill extent.** The sweep finds reveals empirically per pose; SLIDE's condition gives the same set in closed form from b_max and the parallax gain, and bounds the plug depth with it. (A10)
12. **Ground truth.** Four synthetic scenes and six photographs; no offset-eye truth, no hidden-layer
    truth for real elements, no degradation ladder, whole-frame metrics. (§4)
13. **The envelope itself.** No budget in the pipeline is derived from the gallery envelope: the
    sweep cone, the margin, the outpaint demand and the layer count are all per-pose or constant.
    The window model of §1.4 gives every one of them in closed form from (W, D, e, d); the suite must
    measure at 60–85°, where the far half of the envelope is generated content by construction.

Decided by the user on reading the first draft: the envelope is the gallery half-space to ~85°
(§1.4), and the material classes M1–M3 are deferred. Still the user's: whether E4 follows the
literature ("side first, then background", thickness 0.71 × width) or the stronger principle — at
gallery angles the two converge, because a closed side to the equator IS most of what is seen; and
the diorama-depth lever V6, which sets how much of the walk is photograph and how much is generated.
