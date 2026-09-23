# S61 — What the notes already said about the parallel work of 2026-09-23 (checked before continuing)

The user asked, after I queued Depth Pro without looking: "look through all the notes". Every item I had proposed as
parallel work was checked against the notes. What they hold, and what changed.

## 1. Depth Pro: already failed on these pictures. Cancelled.

`S5_photograph_note.md:1334` (the depth bake-off): Depth Pro on the troll gave "metres 4.4 … 6.0: **a flat picture** with a
top-to-bottom gradient; no figure, no cave". The user remembers the same on the paintings. The run is cancelled and its
weights deleted. The depth model is settled (DA3, S5/S8/S19); S26 (Sprint 18) tested DA3, MoGe-3 and DepthLab on kit
truth.

## 2. The silhouette ramp: found, fixed, and then silently lost on the 16-bit path

S59 §2 found the pixels next to every hole are DA3's silhouette ramp. The notes had this in full.

- **The fix exists: REVIEW's RAMP COLLAPSE (≈ line 858).** Silhouette streaks were traced to 3–10 px transition
  aprons: "every ramp pixel … binarizes to whichever side … is closer … Aprons become 1-texel cliffs". Result: "the
  streak fields at the figure edge … are gone".
- **Its cliff test is unit-bound (a107, REVIEW ≈ 5842).** `fgTearStep = 0.06` gates ground classification, the SD
  scan, seeds, the descent floor, ink adoption and ramp collapse. Yet the same nominal cliff is a 7 px reveal in one
  place and 97 px in another, within one image. S50 (line 210) kept `fgTearStep` (84 uses, most of them bake-side
  same-surface tolerances).
- **It does not run on what ships.** CODEMAP §8 and §10 (and S1 §5c): the ramp collapse lives in the live bake, which
  reads the depth at 8 bits. With a 16-bit map, the quick bake takes the raw decode and "the live bake's sharpening is
  discarded". Every map is 16-bit now, so the apron fix is off everywhere.
- **Measured today** (`harness/ramp_width.py`, 10–90% transition width across depth edges; exact kit silhouettes read
  0.8 texels):
  - the app's `dQ`: troll 3.5, vermeer 3.4, sunflowers 1.3, starwatcher 0.9;
  - the troll's raw PNG: 6.0.

  So something in the 16-bit path already narrows ramps, and `dQ` differs from the PNG by up to 0.24 at edges. That
  is the S13 despeckle and snap; which step does it is not yet traced.
- **The 2× map (S53 item 4)** reads *wider* on this instrument (7.6 against 6.0 on the raw PNGs). S53 counted "texels
  inside a transition" (1 951 → 1 463). The two measures disagree; neither is the user's screen.

**The grounded lead** is not a new depth model. It is the existing ramp collapse on the 16-bit path, with a cliff test
in units that do not vary within a picture: S48/S50's reveal field in screen px, or S35's ramp test (§38). It is a
candidate, not started.

## 3. The SD premise test: planned, never run; S52 fixes its input

- **PLAN_REVIEW §3 item 1** planned "one depth-conditioned inpaint … (FLUX Fill or SDXL inpaint with a depth
  ControlNet)". It was never run: S52 ruled diffusion out for lack of a GPU and disk, and used LaMa.
- **S52's arms (PACO's taxonomy).** The best contract was arm A: the band mask on the bundle's
  `plane_color_occluder_removed.png` (S48: every occluder footprint replaced by a harmonic continuation of the legal
  background). My first script left the occluder in the image, which is PACO's arm (a): "the model completes the
  occluder". Fixed (`4aae64c`): `bake_today.js` captures each picture's bundle, and `sd_premise.py` uses its
  occluder-removed image.
- **S47/S52: "two thirds of what reads as messy is the placeholder colour"** (ramps 3.7% of the picture at 45°,
  invented colour 10.5%). And S51's 21% wall cut "could not be seen at all underneath that wash". This is why the S59
  frames all carry one clean wash, and why the SD test matters: it shows whether depth differences survive once real
  colour is in.

## 4. The S59 wash has prior art

S52 caveat 3: the Sprint 25 occluder-removed harmonic continuation "is already better than the wash … smooth where the
wash is streaked … a better fallback than what ships". The S59 wash (a membrane pinned at the law's rims) is the same
idea on the band alone. LIVE_PASS §10 D should be read as "adopt a harmonic wash", with S52 as the earlier evidence.

## 5. Mask cleanliness and bake speed: not in the notes

- **Pinholes and specks in the SD mask.** The notes cover the depth despeckle (S13/S20: poles, lines), not the mask.
  Today's count on the dump band: 373–962 pinholes and 35–322 specks of 16 px or less per picture. It is to be
  recounted on the bundle's `plane_mask_inpaint.png`.
- **Bake speed.** Stated (S44: 66 s) and flagged unowned (S57: "A184's speed target … is in no plan"). Never profiled.
  The profile runs after the A/B renders.

## 6. The ramp collapse on the 16-bit path: first prototype, and why it is not ready (same day)

`moebiusv2/harness/ramp_collapse.py` is S35 §38's ramp test, in the rim law's own units: the visible step
1/k = 1/(D·max(outer/(D+outer), inner/(D−inner))·px-per-world), which reproduces the troll's logged 1.760e-3 and the
kit's 2.563e-3; t from the 2° grazing limit. Each ramp's interior snaps to the nearer flank's affine extrapolation. The
test ground is the kit's own blurred-edge rungs (`degrade/blur_s1/s2/s4`), scored against `exact16`. The exact map must
come through untouched.

| variant | exact16 texels changed (made worse by > 1 step) | blur rungs: error where the rung departs from truth, in steps (before → after) |
|---|---|---|
| steep runs, no join condition | S2 1 966 (1 693) · S31 1 600 (1 600) · S15 6 576 (5 408) | S31 σ1 15.2 → 1.6, S2 σ1 14.1 → 9.2, **S27 σ1 18.7 → 22.1 (worse)** |
| S35's form: only joined steep edges, joined flat flanks | S2 3 (3) · S27 0 · S31 0 · **S15 5 478 (4 514)** | S2 σ1 14.1 → 13.1, S27 ≈ unchanged, S31 only σ4 (18.2 → 11.7) |

Why each form fails:
- **Without the join condition**, a one-texel cliff beside a real two-texel slope reads as one ramp. On exact S31, a
  0 → 0.268 cliff followed by two texels of real grazing surface had those two texels snapped onto the plateau,
  9 steps wrong.
- **With the join condition**, a blurred silhouette's steepest middle edge fails the join test and splits the run in
  two. Neither half has flat flanks on both sides, so most blur is missed. S15 (the open scene, thin structures)
  still misfires on exact geometry.

**The 1-D ramp test cannot tell an estimator's blur from real geometry on this kit, in either form.** Nothing goes to
the app from this. The original collapse's 0.06 gate masked the problem by collapsing only large steps, and that gate
is the rule-2 violation.

The candidate the literature and the pictures both point to is a 2-D, colour-guided test: an estimator's ramp sits
where the IMAGE has one sharp edge but the depth spreads over several texels, and real geometry keeps its slope where
the image does too (joint / guided filtering against the colour). The kit has `rest_rgb.png` for every scene, so the
same exact-must-be-untouched test applies. Not started. It needs its own design and its own falsification, not a
tweak of this one.

## 7. The colour-guided ramp test on the kit (same day): promising, not yet trustworthy

`moebiusv2/harness/ramp_colour.py`:
- **Candidates:** steep same-sign runs with flat flanks (no join condition, so the blur is caught).
- **The colour edge:** the run edge with the largest colour change, counted only if it exceeds the flanks' colour
  change.
- **The blur signature:** texels strictly between the two surfaces on BOTH sides of that edge. A one-sided deviation
  is real geometry, like exact S31's slope beside a cliff, and is left alone.
- **The collapse:** each intermediate texel takes its own side's flank extrapolation.

It uses no constant beyond the rim law's tolerance at one visible step.

| version | exact16: texels changed / made worse | blur σ1: error where the rung departs from truth, in steps |
|---|---|---|
| v1 (as above) | S2 481 / 481 · S27 0 · S31 0 · **S15 0** | S31 15.2 → **1.6** (3 200 better, 0 worse) · S27 18.7 → **6.9** · S15 21.4 → **10.7** (ramp width 2.8 → 1.05) · S2 14.1 → 10.1 |
| v2 (+ the colour edge must be the only one in the run) | S2 85 / 85 · others 0 | S31 **no change** · S27 18.7 → 13.2 · S15 21.4 → 15.7 · S2 14.1 → 9.2 |

Findings:
- The colour image separates blur from real geometry far better than depth alone (S61 §6): S15's exact forest,
  where the depth-only test made 4 514 texels worse, is untouched.
- v1's S2 misfire is real multi-faceted geometry: a one-texel dark rim, a four-texel sloped face, a second face. v2's
  clause removes most of it and loses S31 entirely, whose blur runs cross several colour edges as well.

**Stopped here on purpose.** Each clause so far was cut to the last failure on the same four scenes. That is fitting
the test, not passing it.

The next step is held-out:
1. Freeze v1 or v2 as they stand.
2. Generate the kit's own blur rungs (`truthkit/degrade.py`) for scenes neither version has seen: C1–C3, L1–L6,
   P1–P6.
3. Test the frozen version there unchanged.

Only a version that keeps every exact map untouched and sharpens blur on unseen scenes goes to the app, and then
behind a panel option for the user's screen.
