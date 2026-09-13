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
