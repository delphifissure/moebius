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
