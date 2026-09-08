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

| scene | truth hidden px | app band px | precision | recall | band depth error (median abs / p90) |
|---|---|---|---|---|---|
| S27 fishtank | 4 894 | 125 332 (35 % of plate) | 0.04 | 1.00 | 0.000 / 0.079 m (scene 0.24 m) |
| S11 rounded | 36 512 | 173 436 (48 %) | 0.21 | 1.00 | 0.000 / 0.054 m (0.096 m) |
| S2 contact | 16 454 | 131 524 (37 %) | 0.13 | 1.00 | 0.001 / 0.055 m (0.128 m) |
| S9 stacked | 62 704 | 175 346 (49 %) | 0.36 | 1.00 (things 1.00, sides 0.92) | 0.000 / 0.043 m (0.112 m) |
| S10 limbs | 52 680 | 200 027 (56 %) | 0.26 | 1.00 (things 1.00, sides 1.00) | 0.000 / 0.055 m (0.096 m) |

Precision at recall 1.0 across the five scenes: 0.04–0.36, i.e. the bake fills 3–25× the true scope.

The buffers (`out/<scene>/check_app.png`) show the same anatomy on every scene: the objects are
covered exactly (green), then the whole near floor, horizontal stripes across the ceiling, and
fans that spray from the objects' bases across the wall. The stripes and the floor are 8-bit
quantisation terraces of slow gradients being read as rims (M3); the fans are hole-driven demand
propagating along the shift direction from those false rims. The mega-band we saw on the troll is
therefore not a troll property: it appears on clean synthetic rooms with exact geometry. Recall is
1.00 everywhere (the bake never misses a true reveal), depth on the true scope is right where the
far rim is the wall (median error 0) and 0.04–0.08 m too deep where the truth is a floor or a
nearer object behind the occluder.

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

`dolly.py S30` runs the family (S30: a figure at the window plane, a mid box, a fishtank behind) for
f = 18…144 mm under both conventions. Results in the next revision of this section.

## 8. Open decisions (unchanged from the plan, now with numbers behind them)

- Envelope in head units vs window angle (the sweep is 45° at the window today).
- Side aspect default (Monster Mash c; class aspects; artist override).
- SD stage: view-space-then-bake, confirmed or not.
