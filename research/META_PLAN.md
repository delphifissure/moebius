# Meta-plan (updated 2026-09-12, after C, D and B)

## Where we are

- **Geometry (the plate).** Rim law, plane far side per line, carriers, plate 2 from the arrival order, sky at infinity as an
  option, 16-bit sources with a σ-gated visible-step floor. On the eight kit scenes and the three rescored ones the band is
  the size of the truth at recall ≈ 1 (precision 0.94–0.96 where Sprint 1 had 0.21–0.36); depth error median 0. Nine
  designs tried and removed with numbers; seams accepted as the price of locality and handled at the plate.
- **Depth.** DA3-Mono-Large chosen by bake-off; on six repo pictures it beats every stored map (S19).
- **Hand-off.** The SD-regions view shows the true placeholder set by class; the bundle after a plane bake is the plane
  bake (native res, 16-bit, plate 2, masks, conventions meta). No reimport of that bundle exists.
- **Known gaps, measured:** thin lines erased by the despeckle (S5: 1-texel poles, S18 §2); holes at far poses on
  silverwarrior / vermeer / room (S19 §3.1); S7's ceiling over-claim (S18 §2b); the σ gate reads 0 on sky-heavy maps and the
  floor does not clearly help (S19 §3.4); the sky option leaves the frame edge uncovered from 0.2 m (S19 §3.5); no polarity
  / range check on incoming depth maps (S19 §3.3).

## Principles (unchanged)

Zero per-image tuning; every constant cited or derived from the window's own extent; trust the depth map; everything filled,
wash never clone; falsified premises removed from code and recorded; arms must diverge before numbers are read; the user's
screen is the aesthetic authority; defaults change only in the live pass.

## Order of work

1. **Sprint 13 (now).** (a) **Thin-line despeckle**: the fleck test keeps a texel through which a 1-texel line of the 5×5
   window's own length passes (all 4 along-direction neighbours within tolerance, any of 4 directions); behind
   `window._despeckleLines`; measured on S5 (recall), the troll's striation combs (the rule's reason to exist; shots), the
   kit (identity expected), the six pictures (clones, holes). (b) **Far-pose holes**: diagnose with the sweep class maps on
   silverwarrior / vermeer / room at 45°, 52°, 56°; name the class of every hole (never demanded / demanded but torn /
   beyond the envelope / beyond the frame); the fix follows the class, not before.
2. **Live pass (A), with the user.** Defaults consolidated from the option arms (plane far side, tier, seams, margin, sky),
   dead arms stripped, re-baseline of all instruments; the input contract: polarity and range check on a loaded depth map
   with a visible warning; decide the S7 ceiling blob and the sky-margin gap on screen.
3. **Reimport** of the plane bundle (plate 1 colour, plate 2, sky, margin) onto the live plate; round-trip test with the
   bundle checker.
4. **SD integration test**: one real inpaint of the bundle (any model), reimported, viewed; the first end-to-end picture.
5. **After Sprint 13, in this order (user's instruction, 2026-09-12):**
   - **Per-region noise estimate for the σ gate** (S19 §3.4): σ per region rather than one global median, so a flat sky
     cannot declare a noisy foreground exact; gate the floor where the region is noisy. Measure: the four sky-heavy DA3 maps,
     the troll (must be unchanged: σ > 0 everywhere that matters), the kit (must stay byte-identical: σ = 0 on planes).
   - **Consistent far field across lines** (§16 closed the per-sheet thin-plate and local variants against truth and by
     seams; reopening means a different construction — the closure's numbers are the bar: S15 band depth 0.18 m, the
     photograph's same-sheet seams must fall, not rise).
   - **Persistent-departure segmentation** (§15 closed at step 0: 99.6 % of DA3-16's breaks are already supported by an
     adjacent line; reopening means either a different criterion or a different source where unsupported breaks exist).
   - **S7-class porous silhouettes**: a scene set of its own (canopy density, leaf size, single vs layered crowns, a fence, a
     grille) with env45 truth, then the ceiling over-claim and the between-leaf demand scored per class.
6. **Live pass (A) and reimport / SD test** follow, as in items 2–4.

## Status after item 5 (2026-09-13)

All four queue items are measured and closed (S20–S23). Built and kept as option arms for the live pass: the line-aware
despeckle (`_despeckleLines`, S20), the untorn plate seams value (S20), the **ceiling cut** (`_ceilCut`, S23 — S7 P 0.65 → 0.86,
P6 0.50 → 0.69, S26 0.46 → 0.82, inert elsewhere). Built, measured and removed: the regional noise gate (S21). Closed
offline without building: cross-line regularisation of the law (S22), persistent departure along the line (S23). The porous
set P1–P6 has env45 truth; its residual is the one-texel silhouette ring, ordered by perimeter ÷ area. Next: the live pass
(item 2) with these defaults on the table.

## Status after the horizon scan and the depth-stage test (2026-09-13, later)

S24 (horizon scan), R4 (mathematics of the plug), S25 (Sprint 17: rules select, 60° bake, fold-alpha plate, clamped plate /
AMLE offline — the field family closed a fourth time), R5 (the layered stack: RevealLayer, RLD, Amodal SAM, SAMEO, Lift3Dreamer,
DepthLab, MoGe-3 read; the stack proposed with trades) and **S26 (Sprint 18: the depth stage scored on truth)**. S26's
result fixes the shape of the stack's depth stage: **background layers → the plane law** (beats DA3 / MoGe-3 / DepthLab on
19 of 19 scenes, exact on continued surfaces, and the models cannot be normalised where the hidden range is outside the
visible one); **the object's own far side → a depth model on the completed object layer + the ordering clamp** (beats the
plane law on 17 of 17 scenes by 5–400×; thin objects excepted). DepthLab is a learned continuation of known depth: strong on
non-planar anchored backgrounds, the plane law's equal on self-occlusion. Then **S26 §3b** removed the depth model from the object path (the zero-thickness rule ties or beats it) and **S27 (Sprint 19)**
wired the object-layer path into the bundle as objects: `plane_object_ids` + `meta.plane_objects` out (A253 rule + continuity,
ranked by band demand), `Import object layers` in (visible texels keep the source depth, hidden ones continue the object's
front or an aligned depth, clamped behind what is visible). On the kit it does what it can: where an object hides another
(S9's cards) the changed pixels' error against the truth view falls 71–76 → 7–17; where nothing is hidden behind anything
(S2's boxes, S15's crown, P2's canopy as a first-hit layer) it changes almost nothing, and an object's own sides cannot live
in a texel layer at all. Queue: the live pass; RevealLayer / RLD on the six pictures when a GPU exists (60 GB) — their layers
now have a place to land; per-leaf (K-hit) layers for porous objects; labelling of the far-side choice scored by magenta area
(S25 §4); hole class X (S25 §2).

## Status after Sprint 20 (2026-09-14, later)

**S28**: SAM 2.1 visible masks replace the depth-only footprints on photographs (offline script, clicks / boxes / automatic;
`Import object masks`), and the live **standpoint highlight** reads, per band texel, its occluder and the surface its plate
depth continues (`_bandContinuation`, seeds gated so the occluder cannot seed its own band): red = hidden by another surface,
orange = a surface hiding itself at a step inside the picture, blue = visible. On the troll one click is the torso; four
clicks are the troll (speckled left arm); the woman needs two. What orange cannot mean: sides and back faces beyond a
silhouette — not in the picture, a 3D prior per object (Amodal3R) is the only source. Queue: SAM 2.1 in the browser for live
clicks (ONNX Runtime Web); amodal masks (pix2gestalt / a SAMEO reproduction) when a GPU exists; then the live pass.

## Status after Sprint 21 (2026-09-14, later)

**S29**: SAM 2.1 runs in the page (onnxruntime-web, WebGPU or WASM; the onnx-community export of hiera-small fetched once
from Hugging Face and cached). Click objects at the rest pose, Tab through SAM's three candidates, Alt-click to exclude,
Enter to keep — the kept objects are the object map and the S28 highlight comes on per object. Headless replay of the S28
clicks reproduces the offline masks (troll IoU 0.993; the woman 0.89 by SAM's own near-tie between two candidates); the
screen ↔ source mapping is exact at rest (colour check). Queue unchanged otherwise: amodal masks (pix2gestalt / SAMEO
reproduction) and per-object 3D priors when a GPU exists; the live pass.

**Video (user, 2026-09-14).** The object masks must work for video in time. SAM 2 / 2.1 is that model: the image path wired
in S29 is its per-frame half; the video half (memory encoder + memory attention + object pointers, propagating a click on
one frame through the clip) is the same weights family and exists as ONNX exports (onnx-community publishes `Sam2Video`
configs; a `sam2.1-memory-attention` export is on the Hub). When the app's video layer needs per-frame object maps, the
plan is: encode frames with the same encoder, run the memory attention graph per frame, and hand each frame's ids to the
same `_setObjectIds` path — one prompt per object per clip, not per frame. Not started; it needs a video bake first.

**Plan review (2026-09-15).** `PLAN_REVIEW.md` restates the goal and ranks the weaknesses: the diffusion loop never closed
(no inpaint run, no plane-bundle reimport), cardboard objects at wide angles, no real-scene truth, beyond-frame content,
one-pass and video not designed, the live pass not held, the untested fork to novel-view generation. It reorders the GPU
work: close the loop first, real truth second, the fork third, objects fourth, video fifth; the live pass alongside.

**Defaults set (2026-09-15).** The measured panel set is now the app's start-up default (CODEMAP §38); margin off at the
user's word. The four trades (seams, margin, fold-alpha, tier) stay panel choices until seen in motion.

**S32 (2026-09-15).** The user's sheets: the frame-edge streaks with margin off were A245's rest-footprint clip switched off
together with the strips; the clip is back by default (`_edgeTear = 1` is the fold-law alternative outside the footprint).
The 2-D clamped plate per run cluster, ported into the app behind the join select, equals the plane law on the kit and adds
to the row structure on the troll and vermeer (clusters follow the run segmentation; rows are solved apart) — falsified as a
cure, due for removal by rule 7 after the user's look. Next: the diffusion loop (plane-bundle reimport, one inpaint on a GPU).

**S33 (2026-09-15).** The user asked why the plate streaks at all. Measured on six pictures: 57–77 % of the plate's visible
bends (42–74 % of the wall length) are the far-side construction disagreeing with itself — rows of one surface given two
depths (short walls, the hatching) and the row/column arbitration flipping between neighbours (long walls); 26–58 % of the
wall length are real steps between two background surfaces drawn as rubber where the user's model wants a tear with a sheet
behind. Options ranked: the axis decided per piece (A), tear + second layer behind internal cliffs (C), the tangent-plane
carry (B). Nothing built; the user decides.

**S34 (2026-09-15).** Step A (the layered order between the row and column candidates) built, measured and removed: the
kit does not rank it and on the six pictures the wall length moved −39…+20 % with the seam count rising — the candidate
fields themselves jump, so no per-texel arbitration can be seamless. C and B in their S33 form withdrawn for the same
reason. The design the measurements point at: one continuation sheet per visible surface (rim-contour clusters by the join
law; plane + harmonic rim-residual extension; nearest sheet shows; ends are tears with the next sheet behind). Next: offline
prototype on the dumps, scored by the S33 instrument and the kit, before any app change. The S32 plate arm is removed.

**S35 (2026-09-16).** The sheet construction built offline (`s35/sheets.py`): surfaces = joined components of the visible
depth; one sheet per surface (plane in disparity, per-axis thin rule, ground plane for ground surfaces; optional rim-pinned
residual or local planes); far sides by the app's run scan; nearest sheet behind the texel shows. Kit: truth kept (S2, S9),
S26 within 1.5 cm, S15 0.184 → 0.013 m; seams halved on S9/S26. Pictures: the bare plane removes 50–92 % of the wall length
with zero within-sheet kinks but reaches only 69–84 % of the band; pinning to the rim restores 92–96 % coverage and brings
DA3's rim noise back (troll +12 %, room +29 %, vermeer −72 %). Next arm proposed: the smoothing thin-plate sheet with λ from
the discrepancy principle at the strip's own noise. Envelope corrected by the user: the target is ±90° (fishtank), the
instruments run at 45°/30°.

**S35 continued (2026-09-16).** The deformed-plane sheet (smoothing thin plate at the strip's own noise, λ by discrepancy)
is the best interior on the kit (S26 median 0, S9 p90 halved) and collapsed on the pictures — which exposed the real fault:
under the join law DA3 fuses the occluder with its background (12–18 % of the "background" strip is the occluder), so every
sheet is fitted partly to the thing in front. With S28's SAM object mask separating them, the bare-plane sheets reach 97 %
of the troll's band and cut the wall length by half. The sheet model needs the object segmentation; the interior model is
second-order. Next: thin plate + mask (running); the mask path for the other pictures; then the app.

**S35 closed (2026-09-16).** With SAM masks (troll's S28 map; vermeer and the sunflower field clicked for the test) the sheet
construction reaches 94–99.7 % of the band on the two maskable pictures and, with fragment specks dropped, cuts the per-line
law's vertical wall length by 80 % (troll, vermeer). Remaining seams: boundaries between DA3 background fragments (the
porous question, now with a measured cost both ways). Thin plate: best on the kit, 5–28 min per picture offline. Decision
for the user: take sheets (mask + flat plane per surface + specks dropped) into the app behind the far-side select, with the
thin plate as the interior once a fast solver exists.


**S35 §14, the floor (2026-09-16).** The 0.42 surface that filled the woman's lower band was not the floor but the strip of
wall seen between table and woman, which DA3 gives the objects' depth; the app's ground detector cannot fit DA3's floor for
structural reasons (wall+floor are one run; the horizon lies 10 000 rows out in the flattened world) and was removed from
the prototype. Three rules solve the floor on vermeer with no new constants: fusion by body match (a fragment whose boundary
depth is the neighbouring object's own is a hedge), no area no surface (one-texel silhouette ramps are not sheets), planar
patches with a 2-D geodesic domain (the folded wall+floor+side-wall component is split into faces; the thin plate over the
whole fold overshoot to depth 1.0 even after the solver was fixed with AMG). Behind her legs: wall to row 880, then the
floor at the visible floor's depths. Troll: faceted cave, equal seam length in smaller pieces; sunflowers worse (leaves are
curved, and one-sided background sheets win the sky's hole — the "where does a sheet end" question, now with a test picture);
kit S2/S9 unchanged, S15 0.18 → 0.07 m, S26 0 → 0.03 m. Next: the sheet's end (sky/corners), then the thin plate per face.

**S35 §17, faceting and the plate per face (2026-09-16).** 96–98 % of the far field's jump length is between facets of one
join-law component, so the patches were rejoined by a crease test (slope difference times the smaller facet's extent against
the visible step; no new constant): 19 173 → 6 853 faces on the sunflowers, 11 007 → 4 514 on vermeer. Merging alone changes
nothing because a merged face is curved; with the thin plate on merged faces S26 reaches truth 0.0000 m. The plate needed one
fix: its free boundary let a 165-texel face bulge and take 11 930 band texels on S15 (2.25 m), cured by entering the face's
own plane as a prior on the domain at weight 1/visible step (S15 0.0795 m, p90 4.25, the best tail measured). Only merged
faces need a plate, which cuts the solves to 130–190 per picture. Net: kit a wash on medians, better on S15's tail, pictures
visually unchanged. Two negatives recorded: facet-wide domains (worse) and the per-texel error budget (never fires, because
patches are selected to be planar). Vermeer's remaining "jumps" are legitimate slope (kinks down 97 %), and the sunflower
field's are real structure inside a fused foliage-sky component, not faceting.

**S35 §19–§20, speed and the reference GIF (2026-09-17).** Vermeer's plane-only bake 12 min → 74 s and the full bake with
the plate 35 min → 9.3 min, bit-identical fields: marches as C-speed slices, specks dropped before the domain pass, the
never-read extend domain no longer built, the rim-pinned residual off by default (it was the whole ordering cost and §11 had
already shown it adds noise), geodesic discs by C dilation, three forked plate workers with BLAS pinned. The Silver Warrior
GIF was measured: a horizontal pendulum of ±5 % of the width with the pivot mid-scene, so it never reveals more than a few
per cent of the picture where the app's envelope reveals 41 %; its cleanliness is amplitude and one axis, not a fill law.

**S35 §21–§22, the three items and the things/surfaces classifier (2026-09-17).** §17 was wrong: the sunflower staircase IS in
the adopted arm (unlabelled leaves extended into the sky beside the big head, 60 row jumps), the same failure as S9's 3 cm
(an unmasked quad extended). A things/surfaces classifier over every visible unit (SAM segment or depth component; a thing
iff nearer than a neighbour along their boundary and by medians, no constant) fixes S9 and S2 to 0.0000 m and the sunflowers
(197 of 211 rows sky, 0 jumps), leaves vermeer 9-click unchanged, and is wrong on the troll (x-ray: every tree is a thing,
none closes, the deep gap fills the whole band), on vermeer with the auto mask (the floor voted a thing on 2 of 470 boundary
pairs) and on S15 (8.55 m: the canopy may not fill behind its own trunk). Four closure variants aimed at S15 were falsified
and removed; one clean A/B showed three of them had broken vermeer without the classifier (v jumps 3 340 → 16 788). Default
arm restored bit-identically; classifier opt-in (`--things`). S9 alone is also fixed by the auto SAM mask under the adopted
arm. Decision for the user: classifier on/off/per picture. App-side: S10c's σ = 0 gate leaves sky-heavy maps at quantum = grid
(starwatcher; `_visStep=1` forces the floor).

**S35 §23, where the colours come from (2026-09-17).** The band's fill colour is the mean of the source colour over the depth
fit's window from the rim texel, and that window is the gap plus one texel, so next to the silhouette it is the one or two
texels straddling the edge; the membrane then carries that across the band. Measured on five pictures: the first far texel is
occluder-coloured in 52–62 % of rims (starwatcher 28 %), the colour edge lies inside the far run in a third to a half of them,
and the occluder's share of the fill is 0.2–0.5 across the band. Remedy previewed offline: the far run's median colour after a
constant-free blend skip brings the share to 0.00–0.04. The streaks are the per-line ring plus the per-line geometry; the sheet
renders still carried the per-line colour (harness). Plan: run-median colour in the app; per-sheet colour fields in the
prototype; the harness to inject colour with geometry.

**S35 §24, the colour window falsified (2026-09-17).** The §23 remedy was built in the app behind `_colorWindow` (three arms:
the fit window, the run median past a blend skip, the fit window past the blend) and baked on five pictures. The arms are
visually indistinguishable and the seam against the visible far surface gets worse (vermeer 82 → 100). The fit window is short
only for the 2–4 % of band texels within a few texels of their rim; elsewhere it already spans the whole run. §23's
"contamination across the band" measured non-locality against a local reference, not contamination, and is corrected. The
buffer shows the real cause: the far side chosen can be a different surface 400 texels away (the troll's pale arm wash), and
25–29 % of rims have runs under four texels where no clean colour exists. All of it removed from the app (rule 7); the fix is
per-sheet colour (§23 step 2), which is the same construction as the per-sheet atlas.

**S35 §25, colour folded into the sheet model (2026-09-17).** A band texel's colour is now its owning sheet's own colour,
continued: grouped by visible surface (not planar patch), harmonic extension per surface, the source's anti-aliased fringe
measured per picture (1 texel on three pictures, 0 on starwatcher) and left unanchored, and a per-surface colour plane where
the owner is not adjacent to what it owns. `sheet_render.js` injects it with the geometry, so screengrabs finally show the
sheets' own fill. Against the kit's hidden-layer colour the sheets beat the app where their depth is better (S15 54 vs 170,
S9 146 vs 177) and lose where ownership is wrong (S26 91 vs 56, S2 92 vs 86): the colour adds no error of its own, it
reports the model's ownership. Streaks inside the band drop (vermeer |dC| 1.54 → 1.06). Nearest-clean-sample fallback tried
and rejected (S9 146 → 181). The app is untouched; moving this in is item 1.

**S35 §26, starwatcher's streaking diagnosed (2026-09-17).** The band behind the figure was filled with his own body three to
four steps behind himself — without an object mask his feet join the ground, so his own surface is the one that continues
behind him, and the layered order prefers it to the sky. The classifier over the automatic SAM mask supplies the figure as a
thing and the card goes: vertical jumps 42 701 → 2 232, horizontal 3 975 → 1 161, both far under the per-line law's 12 308 /
33 531. Three pictures now need the classifier (S9, the sunflower staircase, starwatcher) against the troll's x-ray, which is
the one rule left to fix before it can be the default.

**S35 §27, line work split off the foreground (2026-09-17).** Starwatcher's staff loop and lantern glow sit at the sky's
depth in the map and stay on the plate while the figure moves. A segmentation-consistent depth repair (`depth_repair.py`,
offline, no constant): the farthest real surface, its halo absorbed, then unlabelled components at its depth enclosed by it
and touching nearer material take the nearer depth. Starwatcher 1 209 texels, sunflowers 1 813 (petal tips), vermeer 197,
troll 0; three looser versions rejected by their counts. Baked from the repaired depth the glow and loop move with the
figure and the ghost is gone; the band numbers are unchanged. The figure's ink outline was next (a ring hugging the figure failed the enclosure test by half; the nearer thing's contact no longer counts): starwatcher 6 097 texels, and the colour stage now repaints the one-texel blend fringe too, so the black outline baked into the sky goes. App untouched.

**S35 §28, the troll's x-ray, five attempts (2026-09-18).** The one rule that continues the troll's forest behind him
(a thing's march closes when it exits onto ANY thing, not only its own component) fixes the troll (gap 91.8 → 2.5 %,
forest 6 → 90 %) and S15 (8.55 → 0.95 m with the same-thing lift) and breaks vermeer, starwatcher and the sunflowers by
the same mechanism: things' sheets closed on unrelated things become fitted and, nearer than the true far surface, win
(vertical jumps 3 339 → 37 429, 2 249 → 19 522, sky rows 197 → 0). Four repairs (any-closed-fits, rim-behind-band,
same-thing lift, the exposure bound from the app's own parallax scale) and a depth-ordered diagnostic did not separate
them; the forest is a layer of many things and a petal is one small thing, which no per-march exit test sees. Falsified
forms removed; `--closure layer` kept beside the adopted `comp`. Recommendation: `comp` + classifier as the default with
the troll's x-ray recorded as the known exception; the layer grouping (things → layers by adjacency and overlapping depth)
is the untested candidate, a bounded item after item 1 if wanted.

**S35 §29, item C: the layer notion tested against four new kit scenes (2026-09-18).** Scenes L1/L4 (a leaf layer before a gap,
dense and sparse, figure in front), L2 (thin discs before a far sky wall), L3 (figure with a cluster beside her), each with
env45 truth, a truth-derived id map and the app's probe. Layer GROUPING falsified twice (range overlap and step-relative
chaining both swallow the picture). The majority-of-surroundings rule (`--closure surround`) keeps the troll (gap 3.1 %) and
S15 (1.93 m) and is neutral on L3, but loses L2 (0.015 → 0.083 m), the sunflowers, starwatcher and vermeer — the buffers
show the same mechanism every time: once small pieces' sheets are fitted behind an occluder, their planes run the whole hole
and beat the true far side; `comp`'s hedge tier had been guarding against that by accident. A stepped-boundary vote for the
classifier (`--thingrule steps`) fixes starwatcher (2 249 → 942) and the troll under plain comp (gap 1.1 %) and breaks the
sunflowers the same way. Next item is therefore a reach / slope-trust law for small patches, measured on L1–L4; not a closure
item. L1/L4 scores pending.

**S35 §30, the reach law against the truth (2026-09-18).** Instrument: per sheet and disc texel, geodesic distance from the
entries vs own extent vs whether the truth's hidden surface is that sheet's primitive. Two defects found on the way: the disc
"entries" were the whole march footprint (so the §15 reach and the §29 exposure trim never acted), and capped discs were
seeded from the marches; both fixed. The truth's law: a whole thing continues about its own extent (J90/E ≈ 1 on L2/L3), a
fragment as far as its whole (ground pieces, S15's crown). `--reach` (own extent) makes L2's background exact and fixes the
troll (gap 3.4 %) but destroys every fragmented background on the photographs (starwatcher 19 → 92 % sky-valued); the
join-group extent (`--reach-group`) keeps the troll (6 %), holds the sunflowers and vermeer at baseline, half-loses
starwatcher (the join law does not join its smooth ground — the next question). Hidden things behind things (L2's 15 %)
remain hedged; two closures without re-emergence were falsified and removed. L1 (dense layer): comp 0.092 m, reach 0.0115 m (the app's level), reach-group 0.015 m; L4 (sparse layer): every arm 0.000
median but the leaves behind the figure 0.098 m under all of them — the layer's things are filled only when the background
happens to be fragmented (the troll's accident). Carry `--reach-group`; next: the layer notion on L1/L4 with the reach in
place, and why the join law does not join a smooth ground.

**S35 §31 (2026-09-18).** The reach arm's one casualty traced: starwatcher's near plain is a SAM segment the classifier calls a
thing (in front of the far plain across a join-law break at the horizon), so its own band — a receding ground has a far side
everywhere — is never fitted and the sky wins once the far plain is capped. Three constant-free classifier rules tried
(stepped vote + group reach, frame contact, recede): each fixes or misses the plain and breaks the sunflowers, or S2, the
milkmaid and the troll. What separates a ground from a figure is how its depth approaches its far edge (continuing vs a step),
an edge instrument, not a unit statistic — the next classifier item. `comp + reach-group` stands as the measured arm.

**S35 §32 (2026-09-18).** Edge instrument built (continue vs step-off along the inward line at every stepped front texel).
Verdict: starwatcher's near plain steps off (864 of 917 texels) — a terrace in DA3's map, not a horizon; no per-unit or
per-edge depth statistic separates it from a figure. The band behind the legs is the plain's own self-occlusion; the reach
law rightly removed the far-plain sliver that filled it; the missing piece is the per-line law's self-continuation (what is
revealed is the same surface farther up), a construction the sheets model lacks. Two attempts falsified and removed
(join-group closure; join-group area as extent kept as an option). Next: the self-continuation construction; then L1/L4.

**S35 §33 (2026-09-18).** Self-continuation built behind `--selfcont`: per band texel, whether what lies behind it along its
rest ray is revealed from any eye motion (walk on its own joined surface; an own texel at t occludes the exit surface X iff
KPAR (D_t − D_X) ≤ t); if no direction reveals, the surface continues itself one depth level down, decided per join group
by majority. Kit neutral or better (S15 8.1 → 5.1 m), starwatcher's plain fixed (sky 51 → 1.3 %), troll gap 6.0 → 0.6 %;
but 98 % of vermeer's band and 57 % of the sunflowers' become self (the milkmaid fills with herself). Whether that is wrong
depends on whether the app's plate tears at quantum steps inside a gradient (band = tiny tears, wants self) or only at
silhouettes (band = reveal zone, wants the wall): the next thing to read in the app. Measured arm unchanged (`comp +
reach-group`).

**S35 §34 (2026-09-18).** Tear law read: under the rim law the plate tears only at unjoined edges (eye-distance ratio > 3.7 %
or a failed affine prediction); a quantum step is joined; the band is the area the near content vacates over the envelope,
inverted through the far field, and takes the far field's depth — the app's own far field is 100–250 steps behind the
texel's own depth on every band measured. Self-continuation (§33) contradicts that and is removed. Starwatcher's plain band
wants the far plain, whose sheet is a thing (in front of the backdrop along the horizon) and hedged; the classifier item
stands, now stated topologically: a thing's far side continues behind it on both sides, a ground's front boundary is with
the picture's farthest surface only. Measured arm unchanged: `comp + reach-group`.

**S35 §35 (2026-09-18).** Topological classifier `--thingrule wrap`: a thing's stepped front boundary (by step and medians)
surrounds it — directions from its centroid not contained in a half-plane. First classifier under which grounds, fields and
skies are surfaces and figures, heads, jugs are things on every input (starwatcher's far plain borderline at 176°). Run with
the group reach it exposes the defect the old rule hid: pieces of a joined surface carry their own planes over the group's
extent (L2 background 0 → 0.51 m, the sunflowers' band filled to the sky rows). Next construction: the group's plane or plate
for fragments beyond their own extent; then `wrap + reach-group` measured again. Two alternative direction sets falsified.

**S35 §36 (2026-09-18).** Group strip for fragments (`--group-strip`): the plane fitted on the join group's texels in the reach
window. L2's background 0.514 → 0.000 m under the wrap classifier (exact); breaks at vermeer's wall-floor crease (a join group
is a continuous surface, not a plane; wall band 0.008 → 0.11). Growth and consensus repairs falsified. Next: the §32 clamped
plate per join group as the fragment's value beyond its own extent; then wrap + reach-group re-measured. The sunflowers' sky
joined to its field by the rim law's affine rescue is a separate, older item.

**S35 §37 (2026-09-18).** Clamped plate per join group as every fragment's value (`--group-plate`). Kit: L1 0.0101 m with the
hidden layer at 0.007 m, L2 background exact, S2 0.003, S15 1.2 m — the §30–§37 chain closed on the kit. Photographs fail
for one upstream reason: the join law joins silhouette ramps and soft horizons (the affine rescue) so groups are not
surfaces (vermeer's wall band 21 % sky-valued, troll gap 31 %). Next: a ramp test in the rim law (a few-texel monotone run
spanning a large depth between two surfaces that continue beyond it is not a grazing plane), kit as the regression bar.
Measured arm unchanged; the arm to measure after the repair is `wrap + reach-group + group-plate`.

**S35 §38 (2026-09-18).** Ramp test in the rim law (`--ramp`): a steep joined run whose flat flanks, extrapolated to its
middle, disagree by more than quantisation over the span is unjoined and its texels join the band. Vermeer's wall and
milkmaid separate (2 426 + 2 036 runs cut); kit nothing regresses, S26 0.030 → 0.000. The kit chain is complete: L1 0.0101
(hidden layer 0.007), L2 exact, L3/L4/S9/S26 0.000, S2 0.003, S15 1.3 m. Photographs still fail under the validated arm for
three named reasons: the crease inside a hole (a plate cannot bend there), a thing's march through another thing (§28), and
data-poor groups (need a plane fallback). Measured arm unchanged.

**S35 §39 (2026-09-19).** The crease inside the hole (`--crease`): a join group's visible creases -- boundaries between two of
its faces that border the hole, kept only where the faces' planes meet at the entry -- are continued straight through the
hole and the group plate is hinged along them (slope free, value continuous). Kit: three crease scenes added (C1-C3); in the
room scenes the far wall is at the outer depth and counts as sky, so only C3 (a wall at 0.8 W in a 1.5 W room, wide screen)
has the configuration; there the plate's 25 mm blend over a quarter of the band goes to exact (p90 0.4 mm), nothing else
regresses (L1 0.0105 / 0.008, L2-L4 0, S2 0.003, S9/S26 0, S15 1.30). C2 exposed the classifier's medians gate (a figure before
a corner was a surface): the gate now compares against the neighbour's depth along the shared boundary; the unit-median form
is falsified and removed. Pictures: vermeer's wall plate behind the milkmaid 0.64 → 0.022 (66 % of the wall rows within 3 cm
of the wall, from 38 %), starwatcher sky-valued 21 → 7 %, troll gap 30 → 13 %, the sunflowers worse (noise facets hinged).
Solver: hinged plates by sparse LU at the un-hinged plate's lambda, warm CG beyond 200 k unknowns, data-free pieces left out.
Measured arm unchanged (`comp + reach-group`, which is exact behind the milkmaid by planes alone).

**S35 §40 (2026-09-19).** Two corrections to the crease (§39), both from the sunflowers: a crease is hinged only where its slope
jump over its run through the hole amounts to a visible step (jump x run > tol, the smoothing test's own criterion), and the
membrane tie-break is removed (at a millionth of the bending energy it was the only term where the continuation is affine and
flattened the sky plate far from data). Kit unchanged; sunflowers repaired (211 of 211 sky rows); vermeer's wall behind the
milkmaid 38 → 56 % at the wall (plate 0.64 → 0.029); troll 30 → 13 %; starwatcher worse with the hinge (43 → 55 % sky-valued)
because the plain's plate over-extrapolates affinely past the far plain -- §39's 7 % was the membrane's accidental 'constant
beyond a thousand texels'. Next: the plate's error budget (§17's rule carried from planes to the plate). Measured arm unchanged.

**S35 §41 (2026-09-19).** Two remedies falsified before adoption: the plate's error budget (the fitted slope's standard error
never reaches the visible step on the pictures' group plates -- the over-extrapolation is a model error) and speck absorption
for the crease detection (DA3's bend is a fillet of 1-3-row strips, not specks; vermeer 56 → 50 %, removed). Vermeer's
remaining misses located: rows 250-450 and 750-850 behind the milkmaid, where the wall group's data lie on one side of a
400-600-texel band and the plate's affine continuation drifts to 0.04-0.12. Next: §17's plane prior per side of the hinge.

**S35 §42 (2026-09-19).** The group plate's plane prior per sheet, budgeted (`--group-prior`): each domain texel relaxes toward
the plane of the sheet whose entry is nearest, at weight 1/sqrt(step² + se²) with se the sheet's own fit's standard error
there (§17's budget); the unweighted form is falsified on S2 and removed. Kit: nothing regresses beyond a millimetre, S15
1.30 → 0.27 m, C2/C3 exact. Vermeer's wall behind the milkmaid 56 → 99 % at the wall (plate 0.007), the plane arm's level.
Starwatcher, troll and sunflowers mixed (the prior brings the plane arm's behaviour, right and wrong, into the plate).
Measured arm unchanged; the plate arm now matches it on vermeer and beats it on the kit.

**S35 §43 (2026-09-19).** Starwatcher's far plain explained: its unit is plain + hills, its horizon runs through its centroid,
ten texels below it make the wrap gap 178°. Two other forms of the wrap test probed: outward normals (falsified, noise flips
every horizon) and the front's net turning along the contour (right on the kit: figures +180 to +307°, backgrounds 0°; not yet
a construction on the pictures -- needs all contours, holes and pieces: the discrete Gauss-Bonnet of the front). Next: build
that form. Classifier unchanged; instruments kept (`WRAP_DUMP`, `bleed/wrap_normals.py`, `bleed/wrap_turn.py`).

**S35 §44 (2026-09-20).** The wrap test built two more ways and both falsified against the centroid form: the front's TURNING
over its span (a thing at a half turn -- which is exactly the turning of a thing standing on a straight contact, so the
milkmaid −179°, the big sunflower head −180°, the troll +78° became surfaces) and ENCLOSURE of the unit's mass by the closed
span (right on every figure and on starwatcher's plains, but blind to a porous thing: L4's leaf canopy 44 % → surface, its
sheet over the sky band, bg mean −0.002 → −0.031 m; on the pictures starwatcher unreached 2 → 35 %, troll gap 21 → 37 %,
sunflowers sky-valued 66 → 38 %). Both removed (rule 7), instruments kept (`bleed/wrap_turn2.py`, `bleed/wrap_enclose.py`).
The centroid form stands; starwatcher's far plain stays its known miss, and making it a surface does not fill its band anyway.
Measured arm unchanged. Next: the troll's data-poor forest groups (when a group plate should yield to the hedge tier), then
the sunflowers' field facets beside the big head.

**S35 §45 (2026-09-20).** The troll's "data-poor forest groups" measured: the forest plate has 522 k data, a well-posed
lambda, data 8-69 texels from his footprint, and DA3's forest beside him is a smooth ramp (no step above 0.7 quantum) -- the
plate continues it behind him. The old troll instrument read the troll's own depth as "forest" and the forest's continuation
as "gap": the measured arm fills 70 % of his footprint at his own depth (his own sheets in the hedge tier), the crease arm
without the prior 54 % within the forest's range beside him, 1 % beyond. New instrument `bleed/trollfill2.py`; every earlier
troll column is to be read accordingly. The §42 prior's below-range values located (facet planes near the far end; not
zero-residual strips, not over-extrapolation); the plane's reach measured on the group's data built and falsified (vermeer:
the crease reads as model error; a curved field's facets are creases too). Prior stands as §42; measured arm unchanged.
Next: the sunflowers' field facets beside the big head (the same plane-versus-field question, from the plate's side).

**S35 §46 (2026-09-20).** The sunflowers' "48 lost sky rows beside the big head" were the instrument's: the visible texels
beside the lowest sixty rows are the field at d 0.14, not sky, and the prior arm's 0.088 there is the continuation (26 steps
short) where the measured arm's 0.009 is the x-ray (50 short). New instrument `bleed/headfill2.py` (fill against the ring
beside the band). The layered order's prior (nearest plane among the group's sheets reaching a texel, with and without the
order's tiers) built and falsified: a maximum over hundreds of facet planes is biased toward the viewer -- vermeer's lower
band 55.6 → 3.5 % sky-valued, the troll 77 % at his own depth. The §42 nearest-entry prior stands. Both picture instruments
that held the measured arm (troll, head rows) are retired; next: the plate arm against the data-relative instruments on all
pictures with the kit as the bar, and the arm decision.

**S35 §47 (2026-09-20).** One generic instrument for the pictures (`bleed/ringfill.py`: the fill against the hole's own
line lips), calibrated on the kit: where the hidden surface is the lip's continuation it orders the arms as the truth does,
and on S15 it inverts (continuation texels carry 6.7–8.6 m of error; the arm with the lowest continuation share is nearest
the truth). No picture instrument is a bar; the kit alone is. Found on the way: "unreached" has meant unowned, and an unowned
band texel keeps the occluder's depth (a clone by construction; L1 48 % of the band, the troll 17 %). Decision: the plate arm
`wrap + reach-group + group-plate + ramp + crease + group-prior` is the measured arm (kit: equal or better everywhere but S2
+0.004 m; S15 0.275 m against 8.12). Next: the unowned texel's fall-back = the far lip, not the occluder; S2's sky-side pull;
the sunflowers' 7 % surface clone.

**S35 §48 (2026-09-20).** The unowned texel's fall-back: `--lip-fallback` (the far line lip) and an offline neighbour
fall-back against the occluder's depth. L1 truth: the lip is right for the hidden background (0.093 → 0.009 m) and wrong for
the occluder's own body behind itself (0.007 → 0.02–0.06 m), whole band 0.0110 → 0.0118; the neighbour is the occluder again.
On the troll the lip removes the clones (21 → 4.5 %). Not in the measured arm; the question (background or the occluder's own
body) is the object layer's, not the far field's. Next: S2's sky-side pull under the prior; the sunflowers' 7 % surface clone.

**S35 §49 (2026-09-20).** S2's sky-side pull came from a hedge's plane as the prior (52 rims, one constant); hedges and fused
surfaces now give no prior (rule 1). Kit: S2 0.004 → 0.000, S15 0.275 → 0.264, L1 flat, the rest 0; vermeer's wall 67 → 71 %
continued, starwatcher and the troll flat. The sunflowers' partial field beside the big head (§46) was a two-texel hedge's
tilted plane and is gone; the rows read as the measured arm's. Measured arm: the plate arm with the hedge-free prior (RWCPh).
Next: the sunflowers' 7 % surface clone, by owner.

**S35 §50 (2026-09-20).** The sunflowers' 7 % surface clone by owner: 71 % is the unowned fall-back (§48, the near flowers'
band at the frame's foot), the rest the flowers' own small fragments (1.9 %, sheets of 23–80 rims). Not an item. Open in
order: the unowned fall-back as the object layer's question; the field beside the big head as a reach question; 16-bit.

**S35 §51 (2026-09-20).** The sunflowers' x-ray traced (TRACE_TEXEL): the field piece beside the big head is a candidate at
d 0.141 but WEAK — SAM auto's segment is a thing by the wrap test and its march behind the head is open (the §18 two-sided
rule), so the sky wins; 46 % of the band is the sky over a nearer tier-two candidate (skylast.py on TIER_DUMP=1). Sky-last
measured offline and falsified: L4 changed texels 0.000 → 0.064 m (background 0 → 0.092, things 0.09 → 0.01; wrong two to
one), L1 the same split. The curated nine-object map fails the other way (unowned 28 %, the head's band at the head's depth:
the group plate spans the near flowers). The sunflowers need a person's object map and a background group that excludes the
near flowers; not an item for the far field.

**S35 §52 (2026-09-20).** The object map measured on the kit: L2 (the sunflowers' twin) reads 0.000 m with its truth map,
0.180 m with three near heads unlabelled (an unlabelled head is the ground's own surface, its plane wins behind the big head),
0.000 m with the ground over-segmented (flat cells do not wrap). On the sunflowers a click stand-in (curated heads + near auto
segments) behaves like the curated map: the near flowers are not auto segments; without the field patches' labels DA3's ramps
join them to the field. Both picture failures are one dependence on labels the maps do not provide. Measured arm unchanged;
the sunflowers recorded as out of the far field's reach; an L5 graded field would hold the auto-map failure in the kit.

**S35 §53 (2026-09-20).** Where S35 stands: the measured arm (wrap + reach-group + group-plate + ramp + crease + hedge-free
group-prior) against the old one on the kit (S15 8.12 → 0.264 m, S26 0.028 → 0, L4 0.031 → 0.002, L1 0.015 → 0.011, the rest
0) and the pictures described by ringfill. Open and assigned: the unowned fall-back to the object layer's bundle import; the
sunflowers to labels upstream; an L5 graded-field kit scene. The "16-bit standing item" was Sprint 6's finished work, not open.

**S35 §54 (2026-09-20).** L5, a graded clumpy field with heads in front, added to the kit with env45 truth (renderer made
memory-safe; probe recipe verified on L2). Measured arm: 0.000 m with every clump labelled (background exact, things behind
heads 0.061 m short — the picture's x-ray with the ground standing in for the sky), 0.238 m with heads only (clumps merge into
the ground, the sky wall fills 94 %; the old arm 0.274). Sky-last is wrong on the full map and right on the poor one: the map
decides, no far-field rule can. Kit changes committed locally in moebiusv2 (not pushed: out of scope).

**S35 §55 (2026-09-20).** Checking §52's near-flower claim (it stands) turned up an unmeasured property: most far rims are
BAND texels, not visible ones — 40 % sunflowers, 54 % troll, 78 % vermeer, 87–97 % on the kit — sitting a median of 1–11 texels
inside the band, so most sheets are founded on the app's plate stretch. The clone hypothesis is refuted (such sheets own 0–5.7 %
of the band except the troll's 37 %, and on L5's poor map they are the better sheets). Requiring a visible rim (SHEETS_VISRIM)
is falsified: S15 0.264 → 3.26 m, everything else flat. New instrument bleed/bandrims.py. Open: a troll-like kit scene to judge
the troll's 37 %.

**S35 §56 (2026-09-20).** L6, a figure before a forest receding continuously (the troll's configuration), added to the kit
with env45 truth and two maps. The thing class (the hidden forest, 20 773 texels): measured arm with the figure-only map
0.112 m, every other arm/map 0.441-0.445. The map lesson reverses L5's — labelling every tree is WRONG (the two-sided rule
demotes the trees that ARE the far side and sky fills), labelling every clump was right. §55 answered: the no-visible-rim
sheets own 16.3 % of L6's band under the click map and are the whole of the 0.112-vs-0.441 gap, so the troll's 37 % is
evidence, not clones. Sky-last falsified on a fourth scene. The open problem: the two-sided rule cannot tell an occluder from
the far side, and the wrap test is right about both.

**S35 §57 (2026-09-20).** Can the far field tell an occluder from the far side? The contested population (main tier vs a
nearer demoted candidate) is a coin toss on every kit scene: tier two helps 32-48 %, hurts 51-68 %. Two discriminators
measured and refuted — the hole's far lip (on L6's hidden forest the lip itself is 0.450 m, no better than the arm, because
the forest is porous and the lines escape to sky) and the number of agreeing demoted candidates (help and hurt distributions
overlap 36-77 %). With sky-last (§51) that is three constructions against the same question. The far field's part is finished;
the answer must come from the object layer, which §48, §52 and §56 all ask for. Colour is the one untested avenue and belongs
to the plate.

**S35 §58 (2026-09-20).** Standing summary, second edition (supersedes §53). The measured arm is the plate arm with the
hedge-free prior; the kit reads 0.000 on ten scenes, L1 0.0112, S15 0.264, and L5/L6 carry the object-map question with both
answers. Four of the seven photographs are scored; the other three lack a map, a truth and a recorded step, and are named as
not scored rather than guessed. S35 as a depth-field prototype is finished: the one open question (occluder or far side)
belongs to the object layer, and colour belongs to the plate.

**R6 (2026-09-20).** Targeted literature review for the troll and the sunflowers (`research/R6_troll_sunflowers.md`), after
S35 §57 closed the far field's own part of the question. Six families read (abstracts and repository pages only; arXiv, CVF
and the project pages are blocked). The finds: (a) *counterfactual / amodal depth* states our problem exactly — image +
observed depth + amodal mask → depth behind the occluder, scale-and-shift aligned to the observed map — and Amodal Depth
Anything (ICCV 2025) ships MIT weights and an infer script; (b) *diminished reality* says to inpaint colour and depth in one
pass with asymmetric masks, which is a change to our hole contract rather than a new construction, and the reimport sprint is
already queued; (c) *border ownership* is the perceptual name for our two-sided rule, and T-junction context is the cue —
which diagnoses our failure as applying the test per COMPONENT when no single crown wraps a figure though the forest does;
(d) the amodal literature is object-centric and explicitly leaves stuff visible-only, so transfer to a forest or a field is
untested and is exactly what L5/L6 can measure. Recommended order: group-level two-sided rule (cheap, ours, no dependency),
then Amodal Depth Anything scored on the kit, then depth in the inpainting contract.

**S36 (2026-09-20).** R6's item 2 run end to end (`research/S36_amodal_depth_test.md`, `bleed/amodal_probe.py`): Amodal
Depth Anything (0.36 B, MIT) on CPU against L5 and L6 truth. R6's item 1 was dropped on inspection as a repeat of §32's
falsified group closure. The result: our construction swings 0.061 → 0.346 (L5) and 0.112 → 0.441 (L6) on the hidden-thing
class depending on the object map, while the model sits at 0.061 and 0.122 with no map at all. On the map a person can
actually produce, it fixes the sunflowers' configuration (L5 heads-only band 0.238 → 0.034 m) and it should be kept away from
the troll's, where our arm is better and arbitration degrades it (L6 contested texels 67.9 % correct today → 45.9 %). As an
ARBITER between our two existing candidates it is the best of all on L5 (93.2 % correct, |e| 0.397 → 0.022 m), better than its
own direct prediction. §57 is not overturned. **Safety check added the same day: the model helps one scene in four** — it is worse on L1 (0.0112 →
0.0177), much worse on L6 (0.0154 → 0.145) and destroyed on S15 (0.264 → 2.57 m, a relative prediction cannot carry a hidden
range 8.64 m outside the visible one, which is S26's finding again). So it cannot be turned on generally. What the test did
establish is a **truth-free confidence for the model**: its median disagreement with the observed depth over the visible
region orders all five runs by whether to trust it, and per texel (in windows of the band's own half-width) the model's true
error rises monotonically with it in every scene. What is still missing is the same confidence for the ARM, which is what
would let either be chosen; that is §57's question one level up.

**S37 plan (2026-09-20).** `research/S37_plan.md`. Item 0, urgent: three commits (L5, L6, the renderer top-K fix) are
unpushed on moebiusv2 and the rendered truth is gitignored, so ~90 minutes of ray-casting and S36's reproducibility die with
the container; push to moebiusv2 or vendor into moebius. Then: **Phase A the live pass** (consolidate the measured arms as
defaults, strip dead arms, the depth-map polarity/range check, S7's ceiling and the sky margin on screen) -- recommended as
the single next sprint, because eleven sprints of measurement have passed since anything changed on screen; **Phase B** the
reimport plus one real inpaint round trip, taking R6's contract change (ask for depth back as well as colour, asymmetric
masks); **Phase C** decide the sheet model's port by an on-screen A/B on four pictures, one day to decide a weeks-long port;
**Phase D** the amodal prior for the sunflowers only, blocked on an arm-side confidence and gated behind A and B.

**S38 (2026-09-20).** Phase D run (`research/S38_phase_d.md`, `bleed/armconf.py`). **Delivered:** an arm-side confidence.
`reach` -- the texel's distance from its owning sheet's own visible patch over that sheet's extent E, the ratio §30 uses as a
gate, here as a degree -- is monotone in the arm's error in both scenes (L5 0.000 → 0.549, L6 0.000 → 0.091), needs no truth
and no constant. **Not delivered:** a rule. The crossing against the model sits in a different place per scene (L5 swaps from
the second quintile, L6 never), so choosing needs a scene-level gate, and that would be two thresholds fitted to five scenes
with one positive example; stopped rather than fit it. **Two corrections to S36:** S15's 2.57 m is the depth law amplifying a
normal error (0.109 in d units, smaller than L6's 0.143, times a gain of 19.7), not a distinctive model failure -- which also
means the kit's METRE score varies twenty-fold in amplification across scenes and a score in d units or visible steps would
compare them on equal terms; and the 518² resize is not a handicap (aspect-preserving letterbox: L6 unchanged, L5 worse).
Next for Phase D, if resumed: three or four more L5-regime scenes (~20 min of truth each) to turn the scene gate into a
measurement. Phases A and B still come first.

**S39 (2026-09-20).** S38's "three or four more L5-regime scenes" built and scored (`research/S39_l5_regime_scenes.md`;
`truthkit/scenes.py` L7 boulders, L8 crowd, L9 tufts, mirrored in `s35/kit/`). The prediction written down before scoring --
that all three would be L5-regime positives -- was wrong: only L8 was (thing class, arm vs model: L5 0.346/0.061 model,
L6 0.112/0.122 arm, L7 0.033/0.094 arm, L8 0.078/0.040 model, L9 0.015/0.041 arm). **Two falsifications.** (a) The regime is
not ground contact: L7 and L9 contact the ground exactly as L5's clumps do and the arm wins both, on L9 by twenty times, and
L9 merges into a SINGLE component -- the most extreme collapse in the kit -- yet reads 0.015 m, because its tufts hide almost
nothing (2 402 band thing texels against L5's 21 848). A field can merge completely and still not matter if it does not
occlude. (b) **S38's gate candidate is dead**: the model's visible-region disagreement is 0.091 on L8 (model wins) against
0.096 on L6 (arm wins). Sky-owned share and surviving-component count do not separate either; the unowned share happens to
separate all five but a meaningless signal does that by luck one time in five, so it is noted and not claimed. **What
strengthens** is S36's stability finding, now on five scenes: the model's thing-class error spans 0.040-0.122 (3x), the arm's
0.015-0.346 (23x) -- the construction is sometimes far better and sometimes far worse, the model is always mediocre, the
choice is worth about a factor of five, and nothing observable says which case you are in. Practical caveat: the mask arm is
unstable (`frame` best on L5, catastrophic on L7/L8 where it puts the band at sky depth). **Conclusion: the gate is not a
function of the quantities we have been looking at, and a sixth scene will not change that.** If Phase D is resumed the next
step is to let the gate be learned rather than found -- the kit is a generator, and a model trained on DEPTH AND THE BAND
MASK ALONE has almost no domain gap for this project's pictures, which are paintings; the cheap decisive precursor is to feed
the current model a flat grey image with the real depth and see how much it loses. Phases A and B still come first.

**S40 (2026-09-20).** S39's precursor run (`research/S40_colour_ablation.md`; `bleed/amodal_probe.py --image rgb|grey|depth`).
The question was whether the colour is carrying the amodal model's work, because if it is not, a depth-only model trained on
our own kit has no domain gap for this project's pictures, which are paintings. **It is not.** On the hidden-thing class
under the occluder mask -- the one mask arm S39 found stable -- a flat grey frame beats the real picture in ALL FIVE field
scenes: L5 0.0734 -> 0.0685, L6 0.1215 -> 0.0960, L7 0.0937 -> 0.0405, L8 0.0404 -> 0.0391, L9 0.0408 -> 0.0387. The `rgb`
arm reproduces S36/S39 exactly, so the baseline is the same one. Three consequences. (a) **The information the model uses to
place the band is the observation depth and the mask, not the image**, which is the strong answer to the precursor and
removes the main objection to a depth-only model. (b) **Showing the depth map as a picture is not the way**: the `depth` arm
is no better than grey anywhere and much worse on L7 (0.108 vs 0.041) -- the model already has the depth in its observation
channel and a second copy competes with it, so a depth-only model should delete the image branch rather than repurpose it.
(c) **S36's headline L5 number (0.034 whole band) is a colour effect of the `frame` mask** and collapses to sky depth when
the image is blanked (thing 0.061 -> 0.389); under the stable occluder mask L5 reads 0.073 against our arm's 0.346, so the
sunflowers verdict stands at four to five times rather than ten. Where the colour DOES help is the background class (L6
0.185 -> 0.267 without it), which is exactly the class our own construction already has at 0.000-0.020. **The configuration
to train from is therefore: occluder mask, image blanked** -- thing-class spread 0.0387-0.0960 across the five scenes (2.5x,
against the arm's 23x), no colour dependence, no mask choice left to get wrong, and it beats the arm on three of five rather
than two, because L6 flips (0.096 vs 0.112). It still loses on L7 and L9, so the gate question is not answered. Not
measured: a model actually trained without colour, L1 and S15 from S36's safety check, and anything on screen. Phases A and
B still come first.
