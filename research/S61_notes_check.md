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

## 8. The held-out test: both versions frozen, 15 unseen kit scenes (same day)

v1 and v2 exactly as committed in §7, with no change after seeing any held-out result. The scenes are C1–C3, L1–L6 and
P1–P6, each with the kit's own blur rungs (`truthkit/degrade.py`, σ = 1, 2, 4 px, within 3σ of the exact rims) and its
own depth law. The script is `moebiusv2/harness/ramp_colour_heldout.py`; the result is in
`shots/sheet_ab/ramp_colour_heldout.json`.

| | v1 | v2 |
|---|---|---|
| exact16 untouched | 7 of 15. Misfires: L1 290, L4 267, P3 25, P6 15, L6 10, P4 10, P2 6, L5 2 texels (worst 0.08% of a map) | **13 of 15.** L1 2, P4 2 texels |
| blur σ1: error where the rung departs, in steps | C1 20.5 → 1.2 · C2 12.9 → 3.3 · C3 12.3 → 0.9 · L1 13.5 → 5.3 · L2 27.8 → 8.3 · L3 17.4 → 6.4 · L4 17.9 → 4.3 · L5 16.0 → 6.8 · L6 38.6 → 21.8 · P1 24.4 → 12.5 · P2 14.3 → 8.4 · P3 20.7 → 17.7 · P4 15.2 → 9.3 · P5 24.2 → 2.3 · P6 25.3 → 8.7 | roughly a third of v1's gain (C1 → 11.2, L4 → 9.8, P5 → 10.5) |
| texels made better : worse | 10:1 to over 100:1, except **L3 about 2:1** at σ1/σ2 | similar, except **L3 net worse** at σ1/σ2 (1 716 : 2 073) |

What it says:
- The colour-guided test generalises: on unseen scenes it sharpens blurred silhouettes a lot and rarely touches real
  geometry.
- Neither version meets the strict bar set before the test ("every exact map untouched"). v2 misses by 4 texels in
  5.4 M; v1 by up to 290 in one map.
- The trade is plain: v1 gives about three times the sharpening for small misfires on half the scenes. v2 is almost
  perfectly safe for a third of the gain.
- L3 is the case both handle worst, and it is where real structure and blur look most alike.

This is a choice for the user, not a result to tune further.
- If v2: it goes into the app on the 16-bit path, behind a panel option, as a candidate for the live pass.
- If v1: the same, with the misfire counts stated beside it.
- Either way, the app version must reproduce this Python to the texel before any frame is judged.

## 9. Both versions ported, behind one panel select (user: "both, as two options")

- **The code.** `bgRampColourCollapse` is in `moebius.js` (branch `rule5-pass`, not yet merged), and it is called on
  the 16-bit path right after the raw decode. The panel select is **ramps: as estimated (default) / collapse (safe = v2)
  / collapse (strong = v1)**, and it sets `window._rampColour`. The step and the law come from the app itself
  (`bgShiftLUTFor`, the volume depths, the portal plane), and the colour is the source drawn at the plate grid.
- **Bit-exact to the Python.** `harness/ramp_colour_verify.js` extracts the function's source from `moebius.js` and runs
  it on the four pictures' raw maps. In both modes it matches `ramp_colour.py` with **0 texels differing** and identical
  run statistics, in 90–240 ms.

| picture | texels changed, strong / safe |
|---|---|
| troll | 21 606 / 1 562 |
| vermeer | 9 829 / 982 |
| sunflowers | 5 491 / 1 058 |
| starwatcher | 6 508 / 1 209 |

- **Still to do before merge** (queued after the SD tests, since the browser port is shared):
  - default frames byte-identical between main and the branch;
  - the troll baked with safe and strong in the live app, with frames for the user's screen.

## 10. Two parallel findings (same day)

**The SD-mask pinholes are artefacts of the band definition, not content.** Each enclosed hole in the dump band was
classified by comparing its median source depth with that of the band texels around it (within two visible steps,
S35 §47's lip criterion).

| picture | pinholes | same depth as the surrounding band | nearer | farther |
|---|---|---|---|---|
| troll | 962 (20 867 texels) | 928 (10 530 texels) | 14 | 20 |
| vermeer | 606 | 588 | 8 | 10 |
| sunflowers | 373 | 352 | 8 | 13 |
| starwatcher | 449 | 432 | 5 | 12 |

About 95% are specks of the occluder where the per-line law returned the occluder's own depth, so they drop out of the
band (`streak_class.js`'s band keeps only texels whose fill lies behind the source). In an SD inpaint each is an island
of source pixels left unpainted inside a hole.

The rule, with no size constant: an enclosed hole at the depth of its surrounding band belongs to the band. Holes
nearer or farther than their surroundings are real content and stay out. The rule is proposed, not applied: it would
change the band, and the S59 arms are frozen on it. It is for after the A/B, and before the SD test is repeated on the
chosen arm.

**The colour-guided ramp test and the literature.** Colour-guided depth refinement has one documented failure, texture
copying: "copying of texture-information into smooth depth areas", caused by "the inconsistency between depth edges and
corresponding color edges" ([Robust Guided Image Filtering, arXiv 1703.09379](https://arxiv.org/pdf/1703.09379);
[non-convex JBU](https://link.springer.com/article/10.1007/s11042-017-5131-x)).

The standard remedy is to use the colour only where the depth has an edge, with distinct handling for edge and smooth
pixels ([edge-guided joint trilateral upsampling](https://www.researchgate.net/publication/349180447_Depth_map_super-resolution_based_on_edge-guided_joint_trilateral_upsampling);
[Chan et al., noise-aware filter, ECCV 2008](https://people.mpi-inf.mpg.de/~theobalt/eccv08.pdf)). Our test already
does this, since only steep depth runs are candidates, and v2's refusal when a run holds more than one colour edge is
the same principle pushed to abstention. S2's and L3's residue (real faceted geometry with several colour edges) is
the documented limit of the method, not a missed technique.

## 11. The pinhole rule applied to the bundle masks (user: "apply the pinhole rule to the bundle masks")

- **The code.** `bgPinholeFilledMask` is in `moebius.js` (branch `rule5-pass`). It is pure and takes no size constant:
  an enclosed hole in the placeholder set joins it when its median source depth is within two visible steps of the
  median over the mask texels bordering it, each texel counted once. The step is the app's 1/k.
- **Export.** The export writes `plane_mask_inpaint.png` with the rule applied and `plane_mask_inpaint_raw.png`
  without it, and records the counts in `window._qbPinholes`.
- **Return.** The return path (`_importPlaneReturn`) applies the same rule, so colour SD paints into a pinhole comes
  back rather than being dropped.
- **Verified** (`harness/pinhole_verify.js`, source extracted from `moebius.js`). It reproduces the offline
  classification exactly: troll 928 of 962 holes joined (10 530 texels), vermeer 588 of 606 (8 416), sunflowers 352 of
  373 (1 619), starwatcher 432 of 449 (15 643), in 44–152 ms. A first cut counted a bordering texel once per adjacent
  hole texel, which skewed the median and gave 925 and 585. That was fixed before commit.
- **Not done:** the pinholes are also depth spikes. The plate keeps the occluder's own depth there, standing up
  inside the filled band. The mask rule fixes the colour. A depth return that covers the mask now fills them on
  reimport, but the bake's own band still leaves them, and fixing that changes the band that the S59 arms are frozen
  on. That is for after the verdicts.
- **Queued:** a live bundle exported from the branch (the troll), with the pinholes counted in both masks.

## 12. Built ahead of the verdicts, default off (user: "build all speculative stuff you can")

Everything is on branch `rule5-pass`. Each new panel select defaults to today's behaviour.

- **Arm C as an app option: "hole depth: per-line | plain fill".**
  - `bgPlainFill` is `harness/plainfill.js` copied verbatim.
  - The solver was rebuilt, because plain conjugate gradients took 2 730 iterations and 60 s on the troll. The
    replacement is CG preconditioned by an aggregation-multigrid V-cycle: 2×2 blocks, Galerkin coarse operators,
    symmetric Gauss–Seidel.

| stopping rule | iterations | error against the exact fill |
|---|---|---|
| relative residual 1e-10 | 144 | 0.00003 visible steps |
| **1e-8 (adopted)** | 107 | 0.0004 steps |
| 1e-6 | 73 | **81 steps** |

  - The cutoff is chosen on measured error. The 1e-6 row is why: this problem is badly conditioned, and a loose
    residual hides a large error.
  - Timing: 13 s with the CPU shared with SwiftShader renders; an idle machine should manage a few seconds. A
    warm start from a coarse solve alone gave only 2 730 → 2 566 iterations: warm starts do not fix conditioning.
- **The membrane wash as an app option:** `fill: wash | mirrored far side | membrane wash (S59)` (LIVE_PASS §10 D).
- **The pinhole spike fill: "pinholes: as baked | filled".** The S61 §10 rule is applied to the bake's own band, so
  joined pinholes take the hole's fill and the wash. The user asked for this after the verdicts: it is built, off, and
  gets switched on then.
- **How they apply:** `bgPostBakeFill` runs right after `_bgQuickBaked = true`. It works on the A/B's band
  definition and writes exactly as `sheet_ab.js` injected the arms, so the options show what was judged. It also
  updates `_qbPlateF` and `_qbPlateColor`, so the SD bundle carries what is on screen.
- **Verified** (`harness/plainfill_verify.js`, source extracted from `moebius.js`): the troll matches the Python arm C
  to 0.0004 steps, and the wash within one colour level, with every count identical.
- **One difference from the A/B:** the A/B hid plate 2 on every arm; the options leave plate 2 as the panel has it.
- **Queued in the live app:** the troll with hole=plain, wash=membrane and pinholes=filled, after the branch check.

## 13. Two more tools built while waiting

- **`moebiusv2/harness/atlas_lint.py`.** It counts a bundle's noise before SD sees it:
  - mask specks and pinholes;
  - depth spikes standing in pinholes, and clones in the mask;
  - walls in visible steps;
  - wash streak anisotropy.

  It takes the step from the bundle's own `meta.plane.depth.visibleStep`. A first cut counted spikes inside the mask,
  where by construction there are none; spikes stand in the pinholes around the mask, and that was fixed before use.
  An older troll bundle (S45) reads: 494 pinholes with 41 304 spike texels, 0 clones in the mask, 581 depth walls per
  1 000 hole texels, and wash anisotropy 1.11. The linter is advisory (A126).
- **`moebiusv2/harness/sd_return.py`: the SD stage as a tool.**
  - **In:** an exported bundle, using S52's contract: `plane_color_occluder_removed.png`, the pinhole-ruled
    `plane_mask_inpaint.png`, and the atlas's own `plane_plate_depth16.png` through a depth ControlNet.
  - **Out:** Sprint 25's return files, `return_band_color.png` plus, with `--depth`, depth back. The plumbing is
    smoke-tested at 2 steps and 256 px.
  - **What depth back found:** DA3 run on the completed picture does not come back in the app's frame by any global
    fit. Fitted on the legal background (`plane_mask_context`), in whichever affine form fits better, the median
    residual is still 0.059, about 33 visible steps. A first fit over all visible texels was worse (0.067), because
    the completed picture has the occluder removed while the source depth has it.
  - **So the tool also writes the gradient return** (`return_band_gradx16/grady16`, (g + 0.5) · 65535). The app's
    screened Poisson solve integrates it from the hole's own rim, which is the Sprint 25/S48 design for exactly this
    offset-free case.

  Nothing from the tool is judged yet. The first real run belongs to the chosen arm's bundle, after the verdicts.

## 14. Run log after the renders (2026-09-23, morning)

**The branch's browser checks ran main's code, and are being re-run.**
- What happened: a scratch server started from main at 01:11, orphaned by the failed first troll run, held port 8099
  all night. Every later browser run from the `rule5-pass` worktree started its own server, which failed to bind
  without saying so, and the page loaded main's `moebius.js`.
- What this voided: the branch identity check (it compared main with main), the ramp safe/strong bakes, the three fill
  options and the live pinhole bundle. The give-away was the bake line: it had no `ramps=`, `hole=` or `pinholes=`
  fields, and `_qbRampColour` / `_qbPostFill` were null.
- What it did not touch:
  - the S59 frames, which are main's by design;
  - the verifications in §9–§12, which read the branch's source file directly;
  - the end-to-end smoke test below, which is a valid test of main.
- Fix (both trees): `scratch_server.js` answers `/__root` with the folder it serves and exits on a bind error.
  `bake_today.js`, `e2e.js` and `branch_check.js` abort unless `/__root` is their own harness folder. It was tested
  against the orphan before the orphan was stopped (it aborted with the served-tree message). Nothing had been
  recorded from the void runs.

**End-to-end smoke test on main (the troll; plumbing only: 4 SD steps at 320×384, not a quality run).**
- The steps: bake (121 s), bundle (13 MB), lint, SD with depth back, then the app's own *Import plane return*
  function, and frames before and after. Every step completed.
- Lint of main's bundle:
  - 347 177 mask texels in 261 components (106 specks of ≤ 4 texels);
  - 497 pinholes, holding 41 304 spike texels;
  - 0 clones;
  - 581 walls per 1 000 mask texels;
  - wash anisotropy 1.11.
- The import: 155 solver iterations (1.7 s), the rim seam exact (max |Δ| 0), and 37 643 rim-law join decisions that a
  rebake would change.
- **A finding for the first real run.** The import moved the hole's depth by 0.078 on average (max 0.65), about 44
  visible steps.
  - DA3's absolute depth fitted this completed picture to a median residual of 0.095 (54 steps), and the import used
    it together with the gradients (form "screened (both)").
  - So the absolute part is likely dragging the result. When the absolute fit is that poor, the import should take
    the gradients alone, which is the case §13's gradient return was added for.
  - This is not changed yet. It is a design point for the chosen arm's first real run.
