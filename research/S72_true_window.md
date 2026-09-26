# S72 — The true window: real distances, the photograph's own field of view

Date: 2026-09-26. The user, on the Lamppost:
> "Looks insanely skewed... if the displacement is done properly we should have a reasonable facsimile of decently
> accurate 3D (with certain parts of data missing), but it looks basically insane."

## 1. What caused the skew

The displacement is right: each texel moves along the ray from the reference eye through its portal point. The **depth
law** is what's wrong. It was a stylised relief, not a reconstruction (CODEMAP §0: `volumeZOffForNormDepth`):
- normalised disparity through a smoothstep pair;
- 2 cm behind the glass (`outerVolumeDepth`) to 4 cm in front (`innerVolumeDepth`);
- the portal at d = 0.5.

Measured on the Lamppost (DA3-mono 16-bit):

| | d | placed at |
|---|---|---|
| pole top | 0.63 | 0.7 cm in front of the glass |
| pole base | 0.88 | 3.4 cm in front |
| trees (about 36 m) | 0.07 | 2.0 cm behind |
| sky | 0.01 | 2.0 cm behind |

So the pole was built leaning about 17° out of the screen, in front of a flat card. MoGe-2 (metric point map) gives the
real scene:
- the pole at 6.0–6.6 m, leaning **6° away** (the camera pitched up about 6°);
- the trees at about 36 m;
- a field of view of 29.9° × 59.0°.

Three errors stack:
1. **The law.** It is a relief, not 1/disparity.
2. **The field of view.** The 59° portrait is shown in a window that spans about 25° from the 0.2 rest eye, so all depth
   relative to width is exaggerated about 2.5×.
3. **DA3's own depth along the pole.** DA3 puts the top 39% farther than the base; MoGe says 10%.

**The S69 metric law, switched on as-is**, is closer, but it breaks at wide poses: far content drops out and the up-30
view is wrong. It also leaves the field of view unmatched.

## 2. The true window, with no change to the app

The app's law is monotone behind the glass. So **any real distance can be written as a depth value the law maps back
exactly**: every part of the app sees the same true geometry, including the shader, the bake, the rim law, the shift
LUTs and the worker's private copies.

`harness/truewindow.py` (MoGe-2 → the depth file and the law's parameters):
- `D_ref = (picture half-height in portal units) / tan(vfov/2)`. At this distance the portal picture subtends the
  photograph's field of view, so the reference eye's rays ARE the camera's rays. Lamppost: 0.0796.
- The nearest content (99.9th percentile of 1/Z) sits on the glass: `z_behind = D_ref (Z/Z_near − 1)`.
- `pn = 0.999`, `outer` = the farthest finite z_behind, and `d = pn · smoothstep⁻¹(1 − z_behind/outer)`. The closed
  form is `t = ½ − sin(asin(1 − 2y)/3)`.
- MoGe's invalid pixels (sky) get d = 0, and the plate option "sky at infinity" places them on the plane at infinity.

Round trip (decode the 16-bit file against MoGe's Z, 290 603 non-sky texels): median relative error 0.018 %, p99
0.044 %.

`harness/tw_view.js` bakes and renders with those parameters:
- the eye at D_ref;
- the same pose ANGLES as before (42° left and right, up 30°);
- before painting.

**Result (Lamppost).** The pole stays upright and straight at every pose. The ground and the trees move as rigid
surfaces behind it, as through a real window.

The cost is the honest one: **larger holes**. The source-hole area goes from 60 221 to 180 648 texels, because real
parallax behind a pole 5.7 m away with trees at 36 m reveals much more. The holes are missing data, not distortion,
which is what the user asked for.

## 3. Open

- **Viewer distance.** The eye here sits at the photograph's centre of projection (8 cm for this portrait), so the rest
  view is the photograph. A true window at the viewer's real distance keeps the same geometry with the eye farther
  back: the reference eye at D_ref, the live eye wherever the head is. Both are undistorted; which one to use is a
  product choice.
- **Levelling.** The 6° camera pitch is kept, as the true camera-frame geometry. Levelling would rotate the world so
  that verticals are vertical to the window.
- **Paintings and comics.** They have no lens. MoGe's field-of-view estimate is a start; a general rule needs a test.
- **Depth source.** Compare MoGe-2 against DA3 calibrated to MoGe (DA3's edges were chosen for sharpness) on straight
  structure and on kit truth.
- **In the app.** A geometry step on the paint server (MoGe, 11–14 s on this CPU) and a "true window" plate option
  that applies the returned parameters.
- **Everything downstream** (band, painting, gallery) re-run under the true window.

## 4. UX principle: engagement is frontal (the user, 2026-09-26)

"If you're in a gallery, you approach the art you're interested in because you see it at a crappy angle, and that's
ok ... in practice it's pretty normal to see things with keystoning and still choose to engage — and once they do, they
can engage in a 6DoF way."

Consequences for the design:
- **Quality is weighted by angle.** The engaged zone (roughly ±20°, and leaning in / out) must be right: geometry,
  fill, depth. The 42° views are stress tests, not the main experience; tw_view.js now renders 20° beside 42°.
- **Wide angles may degrade gracefully** toward a keystoned flat picture (the app's view fade toward the envelope edge,
  bgViewFadeEndDeg, is the existing mechanism). Reducing depth at the extremes is a legitimate choice, where filling a
  picture-width of never-seen content is not.
- **Depth budgets are set where people look**, and may fall off with angle.
- **Approach is the engagement gesture**: z motion (leaning in, the dolly zoom) deserves as much testing as lateral motion.
