# Sprint 2 report — envelope, rim tear law, reach-anchored far field (2026-09-08)

Plan: `S2_sprint2_plan.md`. Inputs: S1 report §5/§5c (the fold tear is the cause of the mega-band),
CODEMAP §10–§13, §18b. All app numbers below are the quick bake on the 16-bit depth path at the
truth-kit plate (800 × 450), scored by `check_app_band.py` against the exact hidden scope at the
shipped envelope (±45° h, ±30° v; truths regridded to thy = 0, 15, 30). Everything experimental is
behind `window._tearLaw = 'rim'`; the only shipped change is the envelope (the user's spec).

## 1. What was built

**2a — envelope (shipped).** `bgViewFadeEndDegV = 30`; `bgEnvAspect() = tan 30° / tan 45° = 0.577`
replaces the window-aspect rule (0.5625) in the per-fragment pose fraction, the sweep grid and the
sweep bake; `bgFadeFrac` fades on the rectangular envelope (start at 0.700 of either rim). Truth kit:
`reveal.py` and `dolly.py` use the same aspect; env45 truths for all nine scenes regridded.

**2b — rim tear law (`window._tearLaw = 'rim'`).** Three pieces, each a measured step:

1. *Joinedness.* `bgRimLawFor(pw, ph)`: joined(a, b) iff max(ze)/min(ze) ≤ t on the app's own depth
   law, ze = D − z(d), t = 1 + (hfov/pw)/tan g_min, g_min = 2° (`window._rimGrazeDeg`). On S2 at the
   probe's D = 0.2, pw = 800: t = 1.0272. The sweep draws a foreground quad iff its four edges are
   joined; the A212 baked tear and the a160 torn footprint use the same edge test, so the rendered
   mesh and the sweep agree. The fold test is not consulted when the flag is on.
2. *Stretch net off.* The first A/B was a null result (a134: both arms produced the identical band).
   Cause: the sweep's quad fill still stopped at the cut length 1/`bgBandCutStretchFrac` = 3.33
   texels, so a joined but stretched floor cell was still read as a hole; and the baked foreground's
   band cut (`u_useBandCut`) did the same on screen. Under the rim law both are off: a joined surface
   is one surface at any stretch (compression never opens a hole; stretching is the quad's job).
   After this the arms diverged (S2 band 152 k → 49 k texels).
3. *The far field's anchor.* The a-priori far field (A244f) is the membrane whose fixed values are
   the far rims. Three anchorings were measured on S2:
   - far rims only (the A244f rule): the membrane sags under every rim-less surface (open floor:
     far field − source = −0.25 median), every hole inverted through it lands on the floor →
     precision 0.32.
   - source-anchored at every texel outside pass 1's band: precision 0.62 → 0.89 once the sweep's
     plate pass warped this field and took the landing texel as the demand; but recall fell to 0.80.
     a196 (look at the buffer): all 3 294 misses had far field == source and pass-1 class 0; they are
     the lower middle of each box front (floor behind the box, seen from the side, visibility weight
     0.19 median). Pass 1's band did not reach them, so the anchor imported pass 1's misses.
   - **the reach** (kept): a texel's far side is not itself iff an unjoined edge can slide its far
     side past it. Walk from every unjoined edge into its near side along the edge's axis for
     |shift(d_far) − shift(d_near)| texels at the envelope rim (× the envelope aspect vertically), or
     until the next unjoined edge; those texels are free (membrane), every other texel is fixed at
     its own depth. No constant: the span is the app's shift law at e_max, the joinedness is the rim
     law. On S2 the reach is 2.4 % of the plate (pass 1's band was 6.1 %).

   The sweep's plate pass then warps every texel by the far field; a cell the foreground does not
   cover is a hole, the texel that lands in it is the demand, and a landing texel whose far field
   equals its source within a quantum is self-covered (not a reveal). The observe walk (A246/A252
   lip classes) is bypassed under the flag; the band's depth is the far field.

4. *Grazing planes (S2b.3).* On S15 the ratio test tore the whole ground beyond 1.3 m (the
   distance where a 45 mm-high eye sees the ground under g_min = 2°; 46 m for a standing
   photographer) and a band ran along the horizon (precision 0.51). A plane is affine in disparity
   (1/ze) along any image line (its homography), so an edge is now joined if it passes the ratio
   test OR either side's two previous samples predict the third within the quantisation bound
   |disp(d + q) − disp(d − q)|. The crease still joins (ratio), a jump still tears (its second
   difference is the jump minus the slope), the ground joins at any grazing angle. Sky joins
   nothing but sky. S15 precision 0.51 → 0.82 at unchanged recall; S2 unchanged.

**2c — sky at infinity (`window._skyInf`).** A sky texel (source depth below half a source quantum:
the estimator's zero) and a plate texel whose far field is sky are displaced to z = −Z_sky, where
Z_sky = e_max·D·(display px per metre) is the depth whose under-move relative to infinity is one
display pixel at the rim (143 m at the probe's 572-px canvas; capped at half the camera's far plane
and logged if the cap binds). The shift LUT, the rim law and the reach carry the same rule
(`bgShiftPxAt` returns the sky shift, sky is unjoined to everything else), so the CPU sweep and the
render agree. The A245 ring's margin follows from the LUT and becomes the sky margin (1.25 W at 45°)
when the ring is on.

*Measured* (`harness/s2c_skyshot.js`; S15 rendered off-axis with a noise texture painted on the
sky so its motion can be cross-correlated; canvas 572 × 322, 3575 px/m):

| pose | e (m) | sky shift, flag on | closed form (Z_sky = 143 m) | flag off | closed form outer/(D+outer) |
|---|---|---|---|---|---|
| +0.1 rim (4.5° h) | 0.020 | −71.37 px | −71.40 | −69.90 px | −69.88 |
| −0.1 rim | −0.020 | +71.38 | +71.40 | +69.90 | +69.88 |
| +0.25 rim (11° h) | 0.050 | −178.47 | −178.50 | −174.71 | −174.71 |
| +0.1 rim vertical (3.3° v) | 0.012 | 41.19 rows | 41.31 | 40.29 | 40.38 |

The sky moves at 0.998 e with the flag (the closed form with Z_sky, to 0.1 px) and at 0.977 e
without (outer/(D + outer) exactly). On S15 the volume already spans the true 8.64 m so the two
differ by 2 %; at the app's 0.02 default the same flag takes the sky from 9 % of its rate to 100 %.
The band on S15 is unchanged by the flag (precision 0.82 either way; the reach into a hill from a
sky rim grows by the 21 px between the sky shift and the far end's).

## 2. S2 (three boxes, room), 16-bit, the arms in order

| arm | band px | precision | recall | depth median abs (m) | p90 (m) |
|---|---|---|---|---|---|
| fold law, 8-bit path (S1 §5) | 131 524 | 0.125 | 1.00 | 0.0007 | 0.055 |
| fold law, 16-bit path (S1 §5c) | 152 265 | 0.108 | 1.00 | 0.0007 | 0.057 |
| rim law, stretch net still on | 152 265 | 0.108 | 1.00 | — | — (null result, a134) |
| rim law + stretch net off, rims-only far field | 49 k | 0.33 | 1.00 | — | — |
| + source-anchored far field | — | 0.62 | 0.88 | — | — |
| + plate pass takes the far-field warp as the demand | 14 844 | 0.887 | 0.800 | 0.010 | 0.046 |
| **+ reach anchoring (kept)** | **17 937** | **0.895** | **0.976** | **0.004** | **0.043** |

Truth hidden: 16 454 px. Depth error is on true-positive band texels only, in metres against the
first hidden layer, scene depth 0.128 m. The fold-law arms' 0.7 mm median is the observed-lip
depth (A246) on a band that is 90 % wrong; the rim arm's 4 mm is the membrane's ramp on a band that
is 90 % right. Screengrabs: `out/S2/check_app16rim.png` (sent), `out/S2/miss16rim.png`.

What is left on S2 (from the buffer, not from the numbers):

- **Orange strip under each box foot** (the bulk of the 10 % false band). The vertical reach from a
  box's top rim (far side = wall) is 77 texels at the rim; the boxes are ~70 tall, so the reach runs
  over the foot onto the floor in front, which is joined to the box (a box standing on a floor is
  continuous in depth at the contact line). The membrane gives that strip a value between floor and
  wall, its warp lands in the hole beside the box and it is demanded. This is R3 D2 in miniature: the
  far side of a vertical surface below the horizon is the ground continued, and the ground is not
  behind itself. The fix is the ground class (a surface whose depth gradient says it recedes under
  the objects), which needs the horizon or the gradient — deferred to 2c's class work, not patched
  with a constant.
- **Blue triangle at the lower left of the big box** (395 missed texels, visibility weight 0.12
  median, all with far field 0.01–0.08 nearer than the truth's first layer): the membrane's
  floor-to-wall ramp is nearer than the real floor behind the box, so the warp falls short of the
  hole. Same root as the strip: the far side below the horizon is the ground plane, not a ramp.
- Depth on the band is the membrane; the observed-lip depth (0.7 mm on the old arms) is better where
  a lip exists. Re-enabling the observe walk under the rim law is a follow-up.

## 3. The other scenes (rim law, 16-bit) against the fold law

All three arms scored against the regridded (thy 0/15/30) truths; the fold arms are the S1 §5/§5c
bakes rescored, the rim arm is the serial chain of this pass. Depth median is metres on the band's
true positives.

| scene | truth px | fold 8-bit P / R | fold 16-bit P / R | rim P / R | band px (rim) | depth median (m) |
|---|---|---|---|---|---|---|
| S2 three boxes | 16 454 | 0.13 / 1.00 | 0.11 / 1.00 | 0.90 / 0.98 | 17 937 | 0.004 |
| S27 one box | 4 894 | 0.04 / 1.00 | 0.02 / 1.00 | 0.86 / 1.00 | 5 688 | 0.003 |
| S12 pole, sphere, box | 16 975 | 0.13 / 1.00 | 0.11 / 1.00 | 0.92 / 1.00 | 18 411 | 0.000 |
| S26 table, shelf (overhangs) | 25 631 | 0.15 / 1.00 | 0.17 / 1.00 | 0.77 / 1.00 | 33 068 | 0.002 |
| S16 crease / jump, as built | 14 920 | 0.07 / 0.32 | 0.04 / 0.32 | 0.54 / 0.31 | 8 606 | 0.003 |
| S16 with the ledge closed | 4 513 | 0.06 / 0.98 | 0.04 / 1.00 | 0.48 / 0.92 | 8 606 | 0.003 |
| S15 open field (sky counted), rim law before S2b.3 | 34 867 | 0.57 / 0.97 | 0.18 / 0.97 | 0.51 / 0.93 | 63 134 | 1.00 |
| S15, rim law with S2b.3 (+ sky at infinity) | 34 867 | | | 0.82 / 0.93 | 39 497 | 1.04 |

S15's sky-reveal recall (class 7) is 0.90 under the rim law and 0.95 under the fold law; the
misses are the gaps between leaves inside the crown. S15's band DEPTH is worse under the rim law
(median 1.0 m against 0.015 m for the fold-law 16-bit arm): the fold arms took the observed-lip
depth (A246) and the rim arm takes the membrane, which behind the tree ramps between the sky rims
(0) and the ground; re-enabling the observe walk under the flag is the first item of §5, and the
class-aware far side (R3 D2) is the principled fix.

The false band that remains on every room scene is the same object: a thin margin around each
silhouette and the strip under each foot (§2). On S26 the margins run round the table top and the
shelf on all sides, which is why its precision is the lowest of the four.

**S16 is two findings about the kit, not about the app** (a196: the buffers, then the scene file):

1. *An open slot.* 10 256 of the 14 920 truth texels (69 %) are back wall (depth 0.16) seen from
   the thy = −30° eyes through a gap in the scene: the crease wall (y > 0) and the jump wall (y < 0,
   0.06 W deeper) meet at y = 0 with no ledge surface between them, so every low eye looks under the
   crease wall's foot and over the jump wall's top at the back wall. No pilaster has that slot; the
   scene's own docstring says the step is a pilaster face. The far side of that seam, for the app, is
   the jump wall (reach 12 rows), and it found exactly that (the orange horizontal strip). Fix made
   in `scenes.py` (`jump_ledge`, closing the step; edge-on at rest, so the rest image and depth are
   unchanged) and the env45 truth regridded. The first regrid still left 7 492 misses of the same
   kind: the ledge is a parallelogram (the wall line offset in z), and the kit's `Quad` tested
   membership in skewed axes as if they were orthogonal, so most of the ledge was missing. `Quad`
   now solves the Gram system (identity for every existing rectangle). After that the truth is
   4 513 px and the row above is filled from it.
2. *Side faces collapse in rest-texel space.* The jump's return face is 0.06 W deep and faces +x; it
   is hidden at rest and fills 19.6 px of the window at thx = 45° (closed form), but its rest
   projection is 1.7 px wide, so the scorer holds 2 columns of truth against the app's 20-column
   band along the fold. The band is the demand the display needs; the metric counts it 90 % false.
   This is atlas v0's side-face limitation (S1 §3) showing up in the scorer, recorded here and not
   patched: a side face's demand is its window width at the rim, not its rest footprint.

Against S16's design intent the rim law does what the docstring asks: no band along the crease in
the top half (continuous), a band at the jump in the bottom half (a rim), the wall's free end at
x ≈ 671 fully covered (green).

## 4. Decisions recorded

- The fold criterion stays in the code only as the default until the user's live pass of the rim
  law; the rim law replaces it on the quick path when the flag is on. When it ships, the fold test
  and the stretch-net constants (`bgBandCutStretchFrac`, `u_bandCutAll`) leave the quick path (rule 7).
- The far field is anchored by the reach, not by any band (fixed point in one step, as A244f
  intended; the band-anchored variant is removed).
- The strip and the triangle are not tuned away; they are the ground-class item and go with 2c's
  class work.
- The rim law has one stated angle (g_min = 2°) and no longer fails on the surface that angle was
  always going to fail on (the ground); the grazing-plane rescue uses the source quantum, not a
  second constant.
- Sky at infinity is measured, not assumed: 0.998 e on the screen against the closed form.
- Two kit corrections are recorded as such (S16's open slot; `Quad` on skew axes), not as app
  results.

## 5. Next

- The observe walk (A246/A252) under the rim law: the band's depth where a lip is seen, the
  membrane elsewhere (S15's 1.0 m median is the membrane behind the tree).
- The class-aware far side (ground below the horizon, sky above): the S15 fill depth and the S2
  foot strip (R3 D2).
- The sky margin as a continuation rather than ClampToEdge replication (R3 D3) once the ring is on
  the quick path by default.
- Live-pass notes for the user: how to turn the flag on, what to look at (floors, box feet, S16's
  crease), what the fold law showed before.
