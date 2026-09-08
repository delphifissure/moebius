# Sprint 3 — the far side by the plane law: the horizon from the ground plane, the ground continued behind what stands on it (started 2026-09-08)

Inputs: S2 report §2–§5 (the foot strip, the blue triangle under the big box, sky shown behind the
trunk where the truth is a hill), R3 §2 D2 (class-aware far side), CODEMAP §20 (the reach, the
Neumann far field, the nearest-rim sky class). Everything here stays behind a flag on the rim-law
arm (`window._tearLaw = 'rim'`); no default changes.

## 1. What is wrong, stated as geometry (from the buffers, S2 report)

1. **The reach walks with one far depth.** From an unjoined edge the walk carries the far depth
   *at the edge* for the whole span. Down a box's front from its top rim that depth is the wall
   (77 texels), but the far side changes as the walk descends: wall, then the floor at each row,
   then — below the foot — the floor in front, which is the texel itself. The walk overruns the
   foot (the orange strip on every room scene) and the membrane hands the box's lower rows a
   floor-to-wall ramp that is nearer than the floor behind (the blue triangle).
2. **The sky class is decided by the nearest rim in 2D.** Behind the trunk the crown's sky rim is
   nearer than the hill rims to its left and right, so the far side is sky where the truth is a
   hill (S15 p90 depth 8.6 m; the report's "sky where truth is a hill").
3. **The far side is a harmonic membrane.** A membrane between two different surfaces is a blend;
   S2b.4 forbade the blend between sky and ground but kept it between ground and wall.

All three are one omission: the far side of an occluder is not a smooth function anchored at its
rims, it is the scene's own surfaces continued behind the occluder, and those surfaces are planes
(or locally planes) whose continuation is exact.

## 2. The law (derived; no constant that is not the source quantum)

**A plane is affine in disparity along any image line** (Hartley & Zisserman ch. 13, the plane
homography; already used by S2b.3). With the app's eye distance ze(d) = D − z(d) and disparity
1/ze, a plane's disparity along a row or a column is a + b·k in the texel index k. Consequences,
each exact for planes and needing no fitted constant:

- A **level floor is constant along a row** (a row is the intersection of a plane through the eye
  with the scene; for a horizontal surface that intersection is a line at constant depth). The
  floor behind a box at row y is the floor beside the box at row y.
- A **fronto-parallel wall is constant along both axes**; a receding wall is affine along the row.
- **Along a column the floor's disparity is affine in y and reaches zero at the horizon.** The
  horizon is therefore the *vanishing line of the ground plane*, read off the visible ground's own
  samples. With a trusted metric depth map nothing has to be estimated from image appearance
  (Workman et al.'s horizon network is what one uses *without* depth); under the user's standing
  rule (trust the depth map) the plane's zero-disparity line is the horizon, and the crossing of
  the floor's line with the sky's (disparity 0) is where the ground stops behind a full-width
  occluder. Where the far side is a wall instead of sky, the crossing of the floor's line with the
  wall's line is the wall's foot: exactly the row the foot strip needed.
- **Sky is the plane at infinity**: disparity 0, constant along every line, joined to nothing else
  (S2c).

**Runs.** Along a row (and along a column) the depth samples are cut into maximal *runs* on which
the affine prediction from the previous two samples holds within the quantisation bound
(S2b.3's test: |disp − pred| ≤ |disp(d + q) − disp(d − q)|). A run is one plane along that line;
a run ends at a jump *or a crease*. Each run carries its endpoints' disparities, so its line
(slope from the endpoints) and its length m are known.

**The far-side candidate along an axis.** For a texel i on line ℓ, walk outward from i's own run to
the first run whose line, extrapolated back to i, lies **behind** i (disparity smaller than i's by
more than the bound). That run is the candidate on that side; its distance is the number of texels
from i to its first sample (the rim), its value at i is the extrapolated line, clamped to
[0, disp(i)] (never beyond infinity, never in front of the source). A crease neighbour whose
extrapolation is nearer than i (a box's top face seen from its front face) is passed over; a
crease neighbour whose extrapolation is behind i (the floor under a box's foot, continued up the
column) is a candidate — which is the only way the ground gets behind the things standing on it.

**Two candidates on one axis (left/right or up/down):**

1. *Same plane* — the left run's line, extrapolated over the gap g to the right rim, matches the
   right rim within the bound propagated through the extrapolation,
   tol = tolAt·(½ + g / (2(m − 1))) (half a quantum at each end plus the endpoint slope's
   uncertainty, tolAt/(2(m−1)) per texel, over g texels): the far side is the one line through
   both rims (affine interpolation in disparity). Exact for a floor, a wall, a ceiling.
2. *Different planes that cross inside the gap* — the two lines meet at k*: left line up to k*,
   right line beyond. This is the floor meeting the wall's foot behind a sofa, the receding wall
   meeting the back wall behind a pillar, a hill's skyline meeting the sky behind a trunk. True
   for concave and convex junctions alike (the surfaces switch where they meet).
3. *Different planes that do not cross* — a depth step lies somewhere behind the occluder and the
   samples say nothing about where. The step is placed at the midpoint (the median of a uniform
   position prior minimises the expected misplacement); each side keeps its own line up to it.
   No blend.

**Two axes.** The axis whose nearer rim is nearer wins. This is the only prior in the sprint and it
is the same one the 2D nearest-rim rule used, moved from *value* to *axis*: surfaces are locally
coherent, and the evidence from a rim decays with its distance. It settles S15 (the trunk's row
rims are 10 texels away, the crown's sky rim is over 100) and the hedge-with-a-house case in the
other direction (the column rims are near, the row rims at the frame edge are far). A texel with no
candidate on either axis is its own far side. The 2D membrane is not used for the far field on
this arm (it remains the colour membrane, A242).

**The reach with a per-texel far side.** A texel k steps from an unjoined edge along an axis is
free iff k < |shift(farField[i]) − shift(d_edge)| (× envelope aspect vertically), with
farField[i] the texel's *own* far-side value, not the edge's; the walk stops at the first texel
that fails. Below a box's foot the far side is the texel itself, the span is zero and the strip is
not walked. The sky class is farField < skyQ (the far side is the plane at infinity), which
replaces `dSky < dGnd`.

**Constants audit.** q (the source quantum, measured from the depth image), tolAt(d) (S2b.3),
g_min (S2b, unchanged). New: none. The extrapolation bound above is derived from q and the run
length; its consequence — an extrapolation longer than the run it comes from is uncertain by more
than a quantum at its end — is logged per bake (count of candidates with g > m − 1) rather than
suppressed, so the report can say how often the rule is running on thin evidence.

## 3. What is built (`window._farRule = 'plane'`, on the rim-law arm)

- `bgFarSidePlane(dQ, pw, ph)`: row and column runs; per texel the four candidates (distance,
  value, run length); the per-axis combination (same plane / crossing / midpoint) and the axis
  choice; returns `farField`, `skyClass` (far side at infinity), `farAxis`, `farKind` (same,
  cross, mid, single, none) and the thin-evidence count. Pure function of dQ and the app's depth
  law, so the probe can dump it and the scorer can read it.
- `_plugGeoBand`: under the flag the reach uses the per-texel span; `fixedFF/valFF` come from the
  plane far field (free texels take it, everything else is its own far side); no Neumann solve,
  no nearest-rim class; `_geoSkyClass` from the field. The plate pass, the plate tear, the sky
  layer and the membrane colour are unchanged (they consume `farField` and the class).
- Logging: `[S3] far side: runs/row, runs/col, candidates by kind, horizon row (ground line's zero
  from the longest ground column run), thin extrapolations`.
- Probe: `a257_probe.js` dumps `farKind.u8` and `farAxis.u8` beside `farField.f32`.
- Truth kit, two scenes for the column rule (the row scenes already exist):
  - **S31 hedge**: a room with a low box spanning the frame width on the floor in front of the back
    wall. Behind it, per column: wall down to its foot, then floor. No row rim exists inside the
    frame; the column rule must find the wall's foot from the floor's line and the wall's.
  - **S32 hedge, open**: the same box on S15's ground with no wall and a sky. Behind it the ground
    up to the horizon (the ground line's zero) and sky above; the sky layer must be demanded
    above the horizon row and the ground below it.
  Both at 800 px, 16-bit, env45 truth on the shipped grid (thx 0…45, thy 0/15/30).

## 4. A/B protocol (a134, a196)

Arms per scene, all 16-bit, rim law, shipped envelope: (i) S2b.4 as shipped (`check_app16rim`),
(ii) + `_farRule='plane'`. Scenes: S2, S27, S12, S26, S16, S15 (with `_skyInf`), S31, S32. Read:
precision, recall, sky-reveal recall, band depth median/p90 (m), plate depth; the buffers: the
false-band mask (is the foot strip gone), the miss mask (is the blue triangle gone), farKind and
farAxis images, and S15's off-axis renders (is the hill behind the trunk). Numbers that do not move
between arms are a null result to investigate before they are quoted. Expected from §2: the room
scenes' precision rises by the foot strips (≈ 0.04–0.11) with recall held; S2's blue triangle
closes; S15's p90 falls from 8.6 m to the hill's depth; S31/S32 recall depends entirely on the
crossing rule and is the sprint's real test.

## 5. Not in this sprint (recorded so it is not lost)

- Continuation of a *hidden boundary* between two non-crossing surfaces by extending the visible
  boundary's direction (structure propagation; Sun, Yuan, Jia & Shum 2005; Criminisi's isophotes):
  the midpoint rule's principled successor when case 3 turns out to matter.
- Robustness of the run segmentation on an estimator's depth (texture noise breaks runs; the run
  length statistic will show it). The kit's depth is exact by construction.
- A segmentation sky mask for photographs (R3 D1): still required before `_skyInf` is used on a
  room-like photo.
- The observe walk under the rim law (S2 report §5).
- Anything that changes a default's geometry ships only after the user's live pass.
