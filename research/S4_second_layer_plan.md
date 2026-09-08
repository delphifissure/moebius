# Sprint 4 plan (draft) — the second layer: one rest texel, two far sides

Written 2026-09-08 at the end of Sprint 3, before its last numbers landed. Not started.

## 1. Why one depth per texel is not enough (from the Sprint 3 buffers)

- **S15's sign.** Behind the sign board the row rims are hills 76 texels wide; at the envelope rim
  the board slides ~800 texels against the sky. The hill is what shows when the reveal opens and for
  the first 15 % of the envelope; the sky covers the remaining 85 %. With one depth, the
  first-arriving choice (the hill) is right at the onset and leaves an empty reveal later; the
  pose-coverage choice (the sky) is right later and shows sky where the hill should be at the
  poses the head spends its time in. Both rules are implemented (`window._farPick`); neither is
  complete.
- **S15's crown.** In sparse parts the far side is sky or hill; in dense parts the next leaf,
  2 cm back, moves with the crown and never passes. The kit's first hidden layer is a leaf on
  40 % of the crown's band texels and hill or sky on the rest; a single plate holds one.
- **S2's boxes.** Exact already: one surface behind (the floor at that row, or the wall) and it
  never passes.

The plane law already produces, per texel and side, the ordered list of arriving runs with the
pose interval each one covers — a layered depth image (Shade, Gortler, He & Szeliski 1998) read
off the geometry rather than inpainted (Shih et al. 2020 build theirs by inpainting at depth
edges). What is missing is a place to put the second entry.

## 2. What would be built

- **Plate 2.** A second plate mesh on the same grid, carrying per texel the second-arriving run
  where one exists with non-zero pose coverage after the first has passed (the coverage arithmetic
  in `cand` gives it directly: the first's interval, then the next run's uncovered share). Torn
  at its own rims, coloured from its own rims (the S3 colour rule), depth-tested against plate 1
  and the foreground: at small poses plate 1's texel covers it, once plate 1's texel has slid away
  plate 2's shows. No blending, no alpha: two opaque surfaces at their own depths, the LDI's own
  rendering.
- **Demand.** The sweep's plate pass names a hole's texel by warping one far field; with two,
  a hole cell is covered if either layer's warp lands on it, and the band is the union. Plate 2's
  texels are demanded only where plate 1's have passed.
- **Truth kit.** `check_app_band` scores depth against the first hidden layer; add the second
  layer (the kit already stores K = 6 layers per rest texel with per-eye visibility) and a
  two-layer error: for each true-positive texel, the app's two depths against the kit's first two
  ever-visible layers, matched by order.
- **Not this sprint.** Edge-on surfaces (S16's ledge and return face, the sides of boxes): they
  have no rest texels and no arriving run; they need synthesis from the step prior (a jump inside
  one continuous wall is a return face; a jump to a much farther surface is open), which is a
  taxonomy call for the user first.

## 3. Constants audit

None new. The second layer uses the same runs, bounds and coverage arithmetic as the first; the
only choice is which run is first and which second, and the pose interval decides both.

## 4. A/B

S15 (sign, trunk, crown) and S2 as the control (nothing should change: one surface behind each
box). Read: band precision/recall as before, the two-layer depth error, the S15 shots at 0.1,
0.25 and 0.5 of the rim (the sign's far side must read hill then sky as the head moves), the
crown crop.

## 5. First pass (built the same evening; `moebius.js` on main, flag arm)

Built as planned: `bgFarSidePlane` records per texel the run seen once the first-arriving run has
passed (the nearest run covering its exit pose, else the next to arrive inside the envelope; none
if the first never passes); `_plugGeoBand` exports it (`_geoFarField2`, `_geoFarRim2`); the quick
bake builds plate 2 on the source grid (only triangles whose three texels carry a second layer and
are one surface on it; nearest-filtered depth; colour = the rim window's mean along its axis;
`matQ.clone()`; `bgLayerMesh.userData.plate2`, added, hidden and disposed with the plate); the
probe dumps `farField2`, `plateF2`, `plateColor2`; `check_app_band` reports `layer2`
(app/kit/both counts, layer 2 against the kit's second visible layer, best-of-two against the
kit's first); `HIDE=plate2` in the shot harness.

Two defects on the way (a196): the second layer admitted runs that never arrive inside the
envelope (a crown leaf at head fraction 21) — restricted to f0 < 1; and plate 2 rendered at the
app's *default* depth volume (its sign-shaped patch moved 56 display px per unit head fraction
where the hill it carried moves ~700) because the per-frame depth-law uniform sync (`_syncBG`)
knew only plate 1 — plate 2 is now synced. (The A257 object-back mesh is not in that sync
either; noted, not touched.)

Numbers (S15, 16-bit, plane arm): 11 236 band texels carry a second layer (of 39 260); band
P/R unchanged at 0.83 / 0.94 (plate 2 does not change the band); best of the two layers against
the kit's first hidden layer: median 0.0525 m (layer 1 alone 0.0624), p90 unchanged 8.57 m; the
app's layer 2 against the kit's *second* visible layer: median 3.4 m on the 3 410 texels where
both exist — the kit orders layers along the rest ray, the app in pose order, so that comparison
is not the right one and is recorded only as such. S2 (control): 1 089 texels get a second layer
(floor behind a box's top rows after the wall's line passes), band and depth unchanged.

Screen (`sheet_S15_s4.png`, sent): plate 2 alone shows the sign's silhouette carried at the
second hill's depth and the crown's second leaves, moving with the parallax of what they are;
combined with plate 1 the sign's reveal keeps content across 0.1–0.5 of the rim where plate 1's
own torn patches leave holes; the visible difference is small on this scene. The layer exists and
renders right; whether it earns its cost is a screen call on real pictures.
