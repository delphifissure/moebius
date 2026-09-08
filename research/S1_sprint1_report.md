# Sprint 1 report — truth kit, scope instrument, atlas v0

Status: Sprint 1a–1c delivered as instruments and first measurements. No app defaults changed. All
code in the app repo under `harness/truthkit/` (commits 5f1fc70, 2dcd647); outputs under
`harness/truthkit/out/` (gitignored) and `harness/shots/a257probe/<scene>/`. Bakes this sprint:
six (the troll and five synthetic scenes), about a minute each.

Not done in this sprint: the cleanliness metric for the app's fills (needs the fill RGB, which the
probe does not dump) and any 2-D (diagonal-pose) term in the closed-form instrument; both noted in
§7.

## 1. What was built

**tk.py — exact ground truth.** An analytic multi-hit ray-caster with the portal's own camera: window
rect W×H in z = 0, eye at (x, y, D), K surfaces per pixel front to back (quads, boxes, spheres,
cylinders, ellipsoids, discs, a 900-disc canopy), procedural textures, Lambert shading. Labels: sky /
stuff / thing. The app's depth mapping (`viewSpaceDisplacement`: smoothstep law with pn, outer,
inner) is reproduced (`app_z_of_d`) and inverted, so the exact depth is exported as the 8/16-bit
normalised map the app actually reads.

**scenes.py — R1 §4 scenes.** S27 fishtank (room deeper than wide, one box), S28 the same room at
0.25/0.75/2.0 W, S11 rounded bodies, S1 corner, S2 contact / S3 floating, S5 poles 0.5–3 px, S9
stacked cards, S10 crossing limbs, S7 canopy, S4 pop-out figure.

**scope.py — envelope ground truth.** Two exact products, no tolerances:
- Rest-atlas GT: for every rest-canvas sample (pixel, layer k) and every envelope eye, whether that
  sample is seen *through the window* (window-pass test + shadow ray). Classes: photographed /
  outpaint / bg disocclusion / thing disocclusion / own side / own interior / sky. Weights:
  `w_disp` = fraction of eyes that see it; `w_ret` = the same with each eye weighted by the window's
  retinal solid angle, cos³θ for a viewer on the plane z = D (R1 §1.4 corrected from cos²θ).
- Display GT per eye: what the viewer sees, classified per display pixel, with per-eye fractions.

**degrade.py — 17 estimator-defect rungs** (M1–M6): 8-bit quantisation, disparity law, blur σ 1/2/4,
halo dilate/erode, affine, gamma, thin loss, pixel noise, low-frequency bias.

**reveal.py — closed-form reveal instrument.** From a depth map alone: the app's shift law
(`bgShiftLUTFor`, with its layer-width rule), its 17×5 sweep grid, per-scanline forward warp,
rims by the Depth Pro ratio test on metric eye distance (t = 1.05; a ratio is invariant to scale),
per-rim gap attribution (the gap shows the far side's continuation, whose rest position is under
the near texel beside the rim), visibility weights, outpaint strip widths; comparison against the
app's dumped band.

**atlas.py — gap atlas v0** (R2): one npz+json container, charts A0 (photographed), H_k (hidden
layers: depth, RGB placeholder, class, w_disp, w_ret, provenance), O (outpaint beyond the frame),
written from the truth kit and from the app's probe dump, plus an artist sheet.

**check_reveal.py / check_app_band.py** — score the instrument and the app's baked band against
the exact hidden scope at the *same envelope* (the app's 45° sweep).

## 2. The window model checked against exact truth

S27, back wall at d = 0.24 m, W 0.16, D 0.2. Photographed fraction of the back wall visible through
the window, measured by the truth kit vs the closed form `f = 1 − e·d/(W(D+d))`:

| θ | measured | closed form, unbounded plane | closed form, room-bounded |
|---|---|---|---|
| 11° | 0.851 | 0.864 | 0.864 |
| 22° | 0.775 | 0.725 | 0.799 |
| 32° | 0.729 | 0.581 | 0.762 |
| 45° | 0.622 | 0.318 | 0.636 |

The unbounded-plane form (R1 §1.4 item 1) is wrong as soon as the room's side wall enters the
visible strip; the room-bounded form (visible strip clipped to the room) matches to 2–3 %, the
residual being the box's occlusion. The R1 statement stands with that clip added. At ≥ 60° no back
wall is visible at all in this room: the side wall fills the window (display GT: 77 % outpaint at
60°, 96 % at 85°).

## 3. Instrument vs exact truth (S27, app's 45° envelope)

| depth given to the instrument | band px | precision | recall |
|---|---|---|---|
| exact (16-bit) | 5 698 | 0.86 | 1.00 |
| 8-bit linear | 5 575 | 0.88 | 1.00 |
| 8-bit disparity law | 8 241 | 0.59 | 1.00 |
| blur σ 1 (edge-localised) | 4 654 | 0.98 | 0.93 |
| blur σ 2 (edge-localised) | 3 513 | 0.98 | 0.71 |
| blur σ 4 (edge-localised) | 0 | – | 0.00 |
| blur σ 2, whole map (control) | 3 513 | 0.98 | 0.71 |
| halo dilate 2 / 4 px | 6 068 / 6 439 | 0.81 / 0.76 | 1.00 |
| blur σ 2 + dilate 2 | 3 664 | 0.89 | 0.66 |
| thin loss r2 | 5 686 | 0.86 | 1.00 |
| pixel noise 0.02 / 0.05 | 36 036 / 175 073 | 0.13 / 0.03 | 1.00 |
| low-frequency bias 0.05 | 5 561 | 0.88 | 1.00 |
| affine 0.8 d + 0.1 | 7 373 | 0.66 | 1.00 |
| gamma 1.5 | 4 538 | 0.97 | 0.90 |

Truth hidden scope: 4 894 px (bg) + 338 (own side) of a 360 000 px plate. Read:
- On exact or quantised depth the closed form is right: everything the envelope reveals is in the
  band; the 14 % excess is the 8 bottom rows of the box, where the instrument assumes the revealed
  content sits at the far rim's depth (the wall) while the truth is the floor behind the box, which
  the envelope never reaches. A depth-only instrument cannot know that; the atlas can.
- **Soft edges kill the per-pixel ratio test** (σ 2: recall 0.71; σ 4: nothing found). Ramp
  handling (R1 §2.2: boundary-layer / ramp snapping) is not optional; it is Sprint 2's first item.
  The blur rungs were rebuilt to ramp only within 3σ of the exact rims (an estimator smooths across
  occlusion boundaries, not along plane gradients); for this instrument the numbers did not move at
  all against the whole-map blur (a null result, recorded: the ratio test never fires on plane
  gradients either way). The two versions will differ for the app, which reads terraces as rims.
- **Pixel noise floods it** (0.02 of range → 7× over-band). The rim test must be scale-aware
  (multi-pixel support), not a two-pixel ratio.
- The disparity law and affine offsets change the *geometry* (the app maps the given numbers with
  its own law), not the instrument: they over-band because the mapped depths are wrong.

## 4. Instrument vs the app's band on the troll (45°, 851×1023, app mapping outer 0.02 inner 0.04)

| | px | % of plate |
|---|---|---|
| app band (`_qbDisocc`) | 422 147 | 48.4 |
| instrument band, ratio rims | 89 825 | 10.3 |
| overlap | 89 512 | precision 1.00 / recall 0.21 against the app |

Everything the instrument finds, the app also fills; the app fills 4.7× more. On the troll neither
can be adjudicated directly (no truth), and §3 says the instrument under-detects the troll's soft
8-bit edges. The adjudication comes from §5.

## 5. The app's band vs exact truth (synthetic scenes, app's own 45° sweep, app given the scene's
8-bit depth and its exact mapping)

Path note (from the code read, CODEMAP §10/§19): every probe in this section fed the app the
8-bit depth PNG, which is the path where the quick bake consumes the live-baked (sharpened)
depth. A 16-bit PNG takes a different path in which the quick bake reads the raw decode and the
live bake's sharpening is discarded. The 16-bit reruns of all nine scenes are in §5c; they also
test the terrace claim below directly, since a 16-bit source has no 1/255 terraces.

| scene | truth hidden px | app band px | precision | recall | band depth error (median abs / p90) |
|---|---|---|---|---|---|
| S27 fishtank | 4 894 | 125 332 (35 % of plate) | 0.04 | 1.00 | 0.000 / 0.079 m (scene 0.24 m) |
| S11 rounded | 36 512 | 173 436 (48 %) | 0.21 | 1.00 | 0.000 / 0.054 m (0.096 m) |
| S2 contact | 16 454 | 131 524 (37 %) | 0.13 | 1.00 | 0.001 / 0.055 m (0.128 m) |
| S9 stacked | 62 704 | 175 346 (49 %) | 0.36 | 1.00 (things 1.00, sides 0.92) | 0.000 / 0.043 m (0.112 m) |
| S10 limbs | 52 680 | 200 027 (56 %) | 0.26 | 1.00 (things 1.00, sides 1.00) | 0.000 / 0.055 m (0.096 m) |
| S12 frame-cut | 16 975 | 135 075 (38 %) | 0.13 | 1.00 (things 1.00, sides 1.00) | 0.000 / 0.076 m (0.128 m) |
| S15 open (sky, hills, tree) | 26 133 → **34 867 with sky reveals (R3)** | 59 796 (17 %) | 0.43 → **0.57** | 0.99 (bg 0.99, things 1.00, sides 1.00, interior 1.00) → **0.97 (sky reveal 0.95)** | 3.07 / 8.57 m (8.64 m) |
| S16 ridge vs jump | 15 114 | 72 415 (20 %) | 0.07 | **0.32** (bg 0.32) | 0.000 / 0.003 m (0.16 m) |
| S26 overhangs | 25 631 | 166 255 (46 %) | 0.15 | 1.00 (things 1.00, sides 1.00) | 0.011 / 0.055 m (0.112 m) |

Precision at recall 1.0 across the first five scenes: 0.04–0.36, i.e. the bake fills 3–25× the
true scope. The four scenes added afterwards (bakes run after the sufficiency review) change the
picture in two places:

- **S16 is the first recall failure.** The scene has a grazing wall whose top half continues as a
  crease (a ridge, no reveal) and whose bottom half steps 0.06 W back (a jump, a wide reveal of
  the far wall). The app's band covers the jump's near lip (green) but misses most of the far-wall
  strip the jump reveals (blue in `out/S16/check_app.png`): recall 0.32. The reveal is a wide,
  low-contrast strip on a wall that is itself at a grazing angle, so the rims the far field is
  anchored to are weak and the demand propagates only a few texels past the lip. Meanwhile the
  band still sprays the usual fans and terraces over the near wall (precision 0.07). This is the
  case the sufficiency review predicted: a ridge-vs-jump scene separates "there is a depth step"
  from "there is a reveal", and the band gets both halves wrong in opposite directions.
- **S15 exposes the depth of the band, not its footprint.** Recall is 0.99 and the footprint is
  the tightest of the nine (precision 0.43: the tree canopy, trunk and signpost are covered
  almost exactly, with fans only on the ground). But the band's plate depth is wrong by a median
  3.1 m on an 8.6 m scene: behind the tree and the post the truth is the hills and the ground,
  and the far field (a membrane anchored at the far rims, which on an open scene are the sky)
  puts the band at sky depth. On a room scene the far rim IS the back wall, so this error never
  showed. For an open scene the fill would parallax as sky where the viewer expects ground.
- S12 and S26 repeat the room anatomy: objects exact (the frame-cut box, the pole, the ball; the
  table with its legs, the shelf and the beam), recall 1.00, precision 0.13–0.15 from ceiling
  terraces, the floor and fans.

The buffers (`out/<scene>/check_app.png`) show the same anatomy on every scene: the objects are
covered exactly (green), then the whole near floor, horizontal stripes across the ceiling, and
fans that spray from the objects' bases across the wall. The mega-band we saw on the troll is
therefore not a troll property: it appears on clean synthetic rooms with exact geometry. Recall is
1.00 on the room scenes (the bake never misses a true reveal there), depth on the true scope is
right where the far rim is the wall (median error 0) and 0.04–0.08 m too deep where the truth is
a floor or a nearer object behind the occluder.

**Correction (after the code read and the 16-bit reruns, §5c).** An earlier draft of this section
said the stripes and the floor were 8-bit terraces read as rims (M3). That was a guess and the
16-bit reruns falsified it: with a continuous depth source the stripes and fans disappear and the
ceiling and floor become SOLID band (S2 precision 0.13 → 0.11). The cause is the tear rule, not the
quantisation. The CPU sweep does not draw texels the bake has torn (`_plugCpuSweep`, L7845), and
the bake tears every cell whose rim shift span exceeds its own extent (A160 at L13975, A212 at
L15623). On S2 that is 92 % of ceiling cells and 86–88 % of floor cells in BOTH depth formats
(measured on the dumped `dQ.f32` with the app's own shift law; the horizontal-pose-only fold rate
is 0–2 %, i.e. the test is directionless and tears the ceiling for poses that cannot fold it). A
grazing plane compresses under one head direction and stretches under the other; compression
never opens a hole and the sweep's quad fill already covers stretching up to the cut length. So the
tear removes exactly the geometry that was covering the screen, the sweep counts the gap it
opened as a reveal, and the far-field inversion lays a streak of demand along that pose's shift
direction — one streak per pose, 85 poses, hence the fans from every object base. With 8-bit
depth the A212 quantum gate (depth span > 1/255) exempted the one-level treads and left only the
risers tearing, which is what made stripes; at 16 bits every cell passes the gate and the whole
plane tears. The terraces modulated the pattern; they did not cause it.

Two further readings of the colour key. In S15 the hill rims against the sky are orange because
the truth kit files sky as class 6 and does not count it as hidden content; a sky reveal behind a
hill is genuine, so that orange is a kit convention, not an app error. Blue (truth only) on S16 is
the far-wall strip behind the jump; its wedge shape is the reveal width growing with the depth gap
along the jump, and the two lobes are the envelope's two vertical pose rows.

### 5c. The same nine bakes with 16-bit depth (the A99 float path)

Same scenes, same flags, same env45 truth; the only change is `rest_depth16.png` instead of
`rest_depth8.png`. Per CODEMAP §10 this also bypasses the live bake's sharpening (irrelevant on
exact synthetic depth, which has nothing to sharpen). Buffers: `out/<scene>/check_app16.png`.

| scene | 8-bit: precision (band % of plate) | 16-bit: precision (band %) | recall 8 / 16 | band depth median abs, 8 / 16 |
|---|---|---|---|---|
| S27 fishtank | 0.04 (35 %) | 0.02 (56 %) | 1.00 / 1.00 | 0.000 / 0.000 m |
| S11 rounded | 0.21 (48 %) | 0.23 (45 %) | 1.00 / 1.00 | 0.000 / 0.000 |
| S2 contact | 0.13 (37 %) | 0.11 (42 %) | 1.00 / 1.00 | 0.001 / 0.001 |
| S9 stacked | 0.36 (49 %) | 0.32 (55 %) | 1.00 / 1.00 | 0.000 / 0.000 |
| S10 limbs | 0.26 (56 %) | 0.31 (48 %) | 1.00 / 1.00 | 0.000 / 0.000 |
| S12 frame-cut | 0.13 (38 %) | 0.11 (44 %) | 1.00 / 1.00 | 0.000 / 0.000 |
| S15 open | 0.43 (17 %) | 0.14 (53 %) | 0.99 / 1.00 | 3.07 / 0.015 m (p90 8.6 / 6.8 m) |
| S15 open, sky reveals counted (R3 §4) | 0.57 (17 %) | 0.18 (53 %) | 0.97 / 0.97 (sky reveal 0.95 / 0.95) | unchanged (sky has no metric depth) |

**Sky accounting (R3, user decision).** With the sky behind the hills and above the tree counted as
revealed content, S15's truth grows from 26 133 to 34 867 texels (17 566 sky-reveal texels, 95 % of
which the app's band covers: the hill rims that were orange in the first pass are green in
`out/S15/check_app.png`, with a thin blue line on the far side of each hill where the band stops a
few texels short). The definitional change also moves S15's full-envelope fractions: sky that the
photograph shows in the same direction is 0.018 of the display on average, sky the photograph did not
show 0.002, and 0.69 is outpaint — at the shipped cone every off-axis sky pixel is a direction the
photograph never saw (closed form in R3 §2), so sky outpaint, not sky reveal, is the open scene's
main demand.
| S16 ridge vs jump | 0.07 (20 %) | 0.04 (30 %) | **0.32 / 0.33** | 0.000 / 0.000 |
| S26 overhangs | 0.15 (46 %) | 0.17 (42 %) | 1.00 / 1.00 | 0.011 / 0.014 |

Reading:

1. **A better depth source does not shrink the band; on six of nine scenes it grows it.** The
   room scenes go from stripes-plus-fans to solid ceiling and floor (S2, S12, S27; S27's band is
   now 56 % of the plate for a truth of 1.4 %). S15's open ground, which the 8-bit bake left
   mostly alone (precision 0.43, the best row in §5), becomes solid band at 16 bits (0.14). This is
   the fold-tear mechanism of the §5 correction acting without the quantum gate's accidental
   protection: any grazing plane whose parallax gradient exceeds one texel per texel at the rim
   is torn and rebuilt as band.
2. **Recall is unchanged everywhere**, S16's miss included (0.32 → 0.33): the far-wall strip
   behind the jump is not a quantisation casualty either. It is a demand-propagation limit at a
   low-contrast rim on a grazing wall, and it needs its own fix.
3. **S15's depth column is not a like-for-like improvement.** The median fell from 3.07 m to
   0.015 m because the band is now dominated by ground texels whose far field is the ground
   itself; on the tree's and post's true reveal the far field is still the sky (p90 6.8 m of 8.6 m).
4. The depth of the band on the room scenes is identical in both formats (median 0, p90 0.03–0.09
   m): the far field is a membrane anchored at far rims and does not care about the source's
   quantum.

Decision recorded (rule 7 candidate for the app, not applied here): the tear criterion "rim
shift span > cell extent" is not a disocclusion test. It fires on compression, which opens
nothing, and it ignores the direction of head motion relative to the depth gradient. A reveal
opens only where a surface STRETCHES beyond the mesh's cut length or where two surfaces are not
joined (a step); the instrument of §3 uses exactly that test and has precision 0.86 on the same
scene where the app has 0.02–0.04. Changing the app's tear is a geometry change and needs the
user's live pass before it ships (standing constraint); the measurement that would justify it
is now on file.

### 5b. The full envelope (39 eyes to 85°, ±25° vertical): what each scene asks for

Display GT, mean over the 39 eyes (retinal cos³ mean in brackets); atlas = ever-visible rest
samples in the frame, and in the 0.5 W canvas margin.

| scene | photographed | outpaint | bg disocc | thing disocc | own side | own interior | atlas bg / thing / side / interior px | outpaint px |
|---|---|---|---|---|---|---|---|---|
| S27 fishtank 1.5 W | 0.49 [0.78] | 0.51 [0.21] | 0.003 | 0 | 0.001 | 0 | 2 635 / 0 / 126 / 0 | 200 584 |
| S28 room 0.25 W | 0.63 [0.89] | 0.36 [0.10] | 0.002 | 0 | 0.014 | 0 | 2 799 / 0 / 625 / 0 | 200 552 |
| S28 room 0.75 W | 0.52 [0.81] | 0.47 [0.18] | 0.005 | 0 | 0.003 | 0 | 4 060 / 0 / 310 / 0 | 200 984 |
| S28 room 2.0 W | 0.49 [0.77] | 0.51 [0.22] | 0.003 | 0 | 0 | 0 | 2 146 / 0 / 113 / 0 | 200 592 |
| S1 corner | 0.68 [0.82] | 0.25 [0.18] | 0 | 0 | 0 | 0 | 34 / 0 / 0 / 0 | 205 543 |
| S2 contact | 0.51 [0.80] | 0.47 [0.18] | 0.013 | 0 | 0.002 | 0 | 9 214 / 0 / 1 553 / 0 | 200 564 |
| S3 floating | 0.51 [0.80] | 0.47 [0.18] | 0.011 | 0 | 0.003 | 0 | 10 618 / 0 / 1 728 / 0 | 200 564 |
| S4 pop-out figure | 0.55 [0.78] | 0.30 [0.15] | 0.042 | 0.005 | 0.099 | 0 | 18 088 / 150 / 17 038 / 0 | 196 284 |
| S5 poles | 0.56 [0.85] | 0.44 [0.15] | 0.002 | 0 | 0.001 | 0 | 906 / 0 / 906 / 0 | 200 552 |
| S7 canopy | 0.47 [0.74] | 0.49 [0.20] | 0.019 | 0 | 0.010 | 0.010 | 19 918 / 279 / 12 299 / 10 634 | 200 584 |
| S9 stacked cards | 0.51 [0.77] | 0.45 [0.17] | 0.019 | 0.021 | 0 | 0 | 31 872 / 15 046 / 370 / 0 | 200 556 |
| S10 limbs | 0.51 [0.76] | 0.43 [0.16] | 0.041 | 0.008 | 0.004 | 0.001 | 29 443 / 3 950 / 6 468 / 0 | 200 552 |
| S11 rounded | 0.52 [0.79] | 0.45 [0.16] | 0.028 | 0.001 | 0.005 | 0 | 20 422 / 0 / 5 880 / 0 | 200 552 |

Read: over the gallery envelope the display is, on average, half photograph and half content
beside the frame; disocclusions of any kind are 0.3–5 % of the display (10 % for the pop-out figure,
whose own sides dominate). Retinal weighting moves the split to roughly 80/20 because the extreme
eyes see the window as a sliver. The outpaint region beyond the frame is the same ~200 k samples for
every room (it is a property of the room walls and the envelope, not of the objects). A canvas
margin of 0.5 W per side holds 92–94 % of the retinal-weighted outpaint display area across these
scenes (`scope_summary.json: outpaint_on_canvas_retinal`); the remainder is what the extreme eyes
see beyond it, and the display GT keeps it.

## 6. Atlas v0 numbers, S27 truth (`out/S27/atlas_truth.json`)

| chart | ever-visible samples | Σ w_disp | Σ w_ret |
|---|---|---|---|
| H (hidden, in frame) | 5 232 | 1 682 | 1 872 |
| O (outpaint, margin 0.5 W) | 270 048 | 46 604 | 41 817 |

At the 45° envelope the outpaint scope outweighs the in-frame hidden scope by 28× in
visibility-weighted samples for this room: for a fishtank the generation budget is beside the
frame, not behind the box. (The canvas margin of 0.5 W holds only part of it; the display GT
carries the rest.)

## 7. What this decides

1. Scope precision is the app's failure mode, not recall: the bake reveals everything that must be
   revealed and 25× more. The fix is a rim detector that is quantisation- and ramp-aware, scored on
   S27/S11/S2/S9/S10 by precision at recall 1.0 — that is Sprint 2's acceptance number.
2. The closed-form instrument is the reference for hard-edged depth and a floor for soft depth; the
   truth kit is the reference for both. Every Sprint 2 producer is scored against `scope_gt.npz`.
3. cos³θ, not cos²θ, is the retinal weight; R1 corrected.
4. Still owed by the instruments: a cleanliness score (dump the fill colour in the probe and compare
   against the hidden RGB placeholder on the true scope), and a check of the instrument's axis-only
   pose set against the full 17×5 grid (corners of objects; second order, unmeasured).

## 9. The dolly family is one parameter, and it is measured

The app's off-axis dolly zoom keeps the window W×H, moves the camera to D(f) = (W/2)·(f/18 mm)
(A208) and pins the subject plane at the window, so the focal object keeps its frame position and
size across a cut. In the truth kit D is already a free parameter, so "testing with the dolly zoom"
is the same scene photographed from each D(f) through the same window, with the subject at z = 0.
It needs no new geometry and no new instrument:

- every pixel quantity is a function of z/D and of the eye's window angle θ = atan(e/D): the shift
  is e·z/(D − z)·px/m = tanθ · (z/D)/(1 − z/D) · px/m, hole widths are differences of it, the
  visible strip at depth d is W(1 + d/D), the photographed reach is d* = W·D/(e − W);
- scaling W, D, z and e together changes no pixel, so the family is fully described by D/W, i.e.
  by f; and the *photograph itself* changes with f exactly as a real lens change would (the
  background compresses behind the pinned subject: the dolly-zoom stretch).

What is *not* a pure function of f is the envelope convention, which is the open decision:

  (a) window angle fixed (θ_max = 45° at every f): the eye travels e = D tan45°, further for a
      longer lens;
  (b) the app's head units today: e = deviation · camOff · scalar · lensGain with lensGain =
      tan(hfov/2) = W/(2D) under the dolly, so e ∝ 1/D and θ_max = atan(e_ref·D_ref/D²) — the (18/f)²
      law of R1 §1.4.

`dolly.py S30` runs the family (S30: a figure at the window plane, a mid box, a fishtank 1.5 W deep
behind) for f = 18…144 mm under both conventions. The extreme horizontal eye of each envelope, 480 px
plate (`out/dolly/S30/dolly_table.json`, `dolly_sheet.png`):

Three conventions: (a) window angle fixed at 45°; (b) head displacement scaled by the A65 lens gain
with the dolly distance matched to the same lens (e ∝ tan(hfov/2) ∝ 1/D); (c) head motion constant
in metres, e = 0.2 m at every f — "head motion in focal-plane frame widths" literally, since under
the dolly the frame width at the focal plane is W.

**Correction (after re-reading the code, not memory).** The dolly and the lens gain are two
independent controls in the app. The dolly (`dollyDistForFocal`, `updateCameraAndProjection`)
moves only `camera.position.z`; the head offset is `deviation · camOff · scalar · lensGain` with
`lensGain = tan(contentLensFovDeg/2)`, and `contentLensFovDeg` is set only by `window.setLensFov`
per cut (default 90°, gain 1). So **the dolly as implemented is convention (c)**: the head
displacement stays constant in metres while D moves. Convention (b) arises only when a cut calls
`setLensFov` with the new lens *and* the dolly is set to the matching distance; a cut that calls
`setLensFov` without dollying is A65's fixed-D law (e ∝ tan(hfov/2), D unchanged), which this table
does not cover. An earlier draft of this section, and the "correction after reading the code" in R1
§1.4, treated (b) as the implementation; both were wrong on that point and are amended.

| f | D | hfov | (a) θ 45°: phot / outp / disocc, shift | (b) app head units: θ, phot / outp / disocc, shift | (c) const e: θ, phot / outp / disocc, shift |
|---|---|---|---|---|---|
| 18 mm | 0.080 | 90° | 0.70 / 0.21 / 0.10, 180 px | 80.9°, 0.50 / 0.33 / 0.17, 1 125 px | 68.2°, 0.56 / 0.36 / 0.08, 450 px |
| 25 | 0.111 | 72° | 0.66 / 0.24 / 0.10, 228 | 72.8°, 0.39 / 0.52 / 0.09, 738 | 60.9°, 0.53 / 0.41 / 0.07, 410 |
| 35 | 0.156 | 54° | 0.59 / 0.32 / 0.08, 283 | 58.8°, 0.41 / 0.54 / 0.05, 468 | 52.1°, 0.53 / 0.41 / 0.05, 364 |
| 45 | 0.200 | 44° | 0.56 / 0.40 / 0.04, 327 | 45.0°, 0.56 / 0.40 / 0.04, 327 | 45.0°, 0.56 / 0.40 / 0.04, 327 |
| 65 | 0.289 | 31° | 0.44 / 0.53 / 0.03, 393 | 25.6°, 0.65 / 0.26 / 0.09, 188 | 34.7°, 0.56 / 0.36 / 0.09, 272 |
| 90 | 0.400 | 23° | 0.32 / 0.65 / 0.03, 450 | 14.0°, 0.72 / 0.19 / 0.09, 112 | 26.6°, 0.61 / 0.31 / 0.09, 225 |
| 144 | 0.640 | 14° | 0.21 / 0.76 / 0.02, 524 | 5.6°, 0.82 / 0.09 / 0.09, 51 | 17.4°, 0.62 / 0.29 / 0.09, 164 |

Read:
- **(c) constant head motion in metres is the lens-invariant one.** Photographed share 0.53–0.62 and
  outpaint 0.29–0.41 across the whole 18–144 mm range, shift 164–450 px: the generated budget for a
  given head move barely depends on the lens. This is what A65's own text asks for ("head motion
  measured in focal-plane frame widths is lens-invariant"); the tan(hfov/2) gain it implemented was
  derived with D fixed, and the dolly makes 2D·tan(hfov/2) = W constant, so under the dolly the
  right gain is 1.0 and the implemented gain adds a 1/D factor (b).
- **(a) fixed window angle.** The trend is smooth and follows the closed form: with the eye at
  45° from a camera position D, the visible strip at the back wall slides by e·d/D = d·tan45° =
  0.24 m at every f while its width W(1 + d/D) shrinks with the longer lens, so the photographed
  share falls from 0.70 to 0.21 and the far wall's shift grows toward its orthographic limit (z·px/m
  = 720 px). Content at a given metric depth behind the pinned subject moves the same number of
  pixels per head angle at every lens (shift → tanθ·z for z ≪ D): the "everything feels the expected
  size" property extends to the parallax.
- **(b) the app's head units today.** θ at the edge of head travel runs from 81° at 18 mm to 5.6°
  at 144 mm. At the wide end the same head move puts the eye 0.5 m to the side of an 8 cm-distant
  window: half the display is generated, the far wall slides 1 125 px on a 480 px plate. At the long
  end almost nothing moves (51 px). The generated scope varies by ~20× across the lens range for the
  same physical head motion.
- The in-frame band of the instrument is 12–14 k px in every cell: the subject's and the box's
  footprints saturate (their relative shift exceeds their width) in all cases, so the in-frame scope
  is set by the objects, and the lens moves the outpaint and the depth budget.

Which convention is right is the open decision, now with numbers. (a) is the physical-screen model
(same head position → same view angle through the window at every lens; scope then varies with the
lens, 0.70 → 0.21 photographed). (c) keeps the generated budget lens-invariant, is what A65 says it
wanted, and is what the dolly does today. (b) is what happens if a cut both dollies to the new lens
and applies the A65 gain for it: 81° at 18 mm and 5.6° at 144 mm for the same head move, a ~20×
swing in generated content. The practical point is that the two controls must not both be applied
for one lens change; which single law to keep (a or c) is the user's live pass. Nothing was changed.

## 8. Open decisions (unchanged from the plan, now with numbers behind them)

- Envelope in head units vs window angle (the sweep is 45° at the window today).
- Side aspect default (Monster Mash c; class aspects; artist override).
- SD stage: view-space-then-bake, confirmed or not.
