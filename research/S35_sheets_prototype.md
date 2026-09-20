# S35 — the sheet construction, offline (2026-09-16; §7–§9 added later the same day)

The user's model, built as a measurement before any app change: one continuation sheet per visible surface behind each
hole, the nearest sheet behind the texel shows, the next one is the second layer. `research/s35/sheets.py` on the app's own
dumps (source depth, band, per-line far field, depth law, join law, ground plane), scored against the kit's truth and with
the seam instrument, next to the per-line law. Envelope note: everything here is measured at the 45°/30° instrument pose;
the target is the fishtank (±90° with a sliver in view at grazing angles), which the kit truth does not yet cover.

## 1. What the prototype does (every rule the app's own, ported)

1. **Far rims.** For a band texel and each of its four line directions, the runs beyond its own run (runs = maximal chains of
   texels joined pairwise by the join law) that lie behind it by more than the join tolerance, or are sky, are its far sides
   — the app's `cand()` list. A rim may itself be a band texel (the reveal set holds one texel of the background at a
   silhouette; its far side is itself).
2. **Surfaces.** A visible surface is a connected component of the depth map under the join law through the interior (not
   only along the hole's contour: contour clustering gave the troll 643 pieces, 338 single texels, and the boundaries between
   pieces were the seams; components give 308, one of them the whole cave).
3. **Strip and sheet.** Per surface, the component texels within its reach (the longest march its rims' texels make into the
   band, +1 — the app's window rule in 2-D); a least-squares plane in disparity (affine: the plane's homography), trimmed at
   3 MAD; per axis, a slope the strip cannot support (extent shorter than the reach along that axis) is not extrapolated (the
   app's thin rule per axis); a surface whose rims are ground texels follows the fitted ground plane (the app's thin-ground
   rule); a strip under three texels supports no model and makes no sheet. Optionally the plane is pinned to the rim by a
   harmonic extension of the rim residuals (Dirichlet at the entry texels of each march, zero flux elsewhere).
4. **Domain ('stop').** The band texels a surface's rims march into along their lines. ('extend' = the whole hole: dead —
   0.5–9 % of texels reached on S15 and the wrong surface elsewhere; not reported further.)
5. **Order.** Per texel, among the sheets whose domain holds it and whose value lies behind its own depth by more than the
   tolerance (the app's candidate test), the nearest shows; the second-nearest is the second layer; none → the texel keeps
   its own depth and is counted as **unreached**.
6. **Instruments.** Truth: band depth error against the kit's first hidden layer (metres, as the kit scorer). Seams:
   *jumps* = adjacent band texels whose depths differ by more than the visible step (count and summed length in steps = the
   total length of the walls the renderer would draw at the cone rim); *kinks* = second differences beyond the step (a slant
   has none). The per-line law's own far field is scored the same way in the same run.

## 2. Kit (truth)

| scene | arm | reached | truth median (m) | p90 (m) | jumps v (len) | jumps h (len) | kinks v (len) | kinks h (len) |
|---|---|---|---|---|---|---|---|---|
| S2 boxes | per-line | — | 0.0000 | 0.0427 | 8 189 (24 426) | 35 (507) | 859 (13 000) | 55 (836) |
| | sheets, plane + pinned residual | 100 % | 0.0007 | 0.0404 | 8 190 (35 273) | 485 (22 709) | 1 126 (28 610) | 503 (23 391) |
| | sheets, local planes | 100 % | 0.0000 | 0.0533 | 6 326 (32 550) | 473 (24 521) | 1 742 (31 104) | 384 (26 435) |
| S9 cards | per-line | — | 0.0000 | 0.0640 | 1 013 (80 742) | 880 (70 762) | 2 017 (161 475) | 1 740 (141 474) |
| | plane + pinned | 100 % | 0.0006 | 0.0640 | 841 (38 459) | 915 (42 384) | 1 118 (50 809) | 1 366 (62 163) |
| | local planes | 100 % | 0.0000 | 0.0640 | 0 | 0 | 0 | 0 |
| S26 quads | per-line | — | 0.0000 | 0.0560 | 11 129 (148 302) | 465 (26 710) | 3 555 (201 600) | 840 (52 663) |
| | plane + pinned | 100 % | 0.0153 | 0.0551 | 2 908 (117 930) | 1 839 (64 423) | 3 323 (180 425) | 1 554 (71 757) |
| | plane, no residual | 100 % | 0.0161 | 0.0552 | 2 365 (36 782) | 232 (15 649) | 1 538 (53 698) | 253 (17 352) |
| | local planes | 100 % | 0.0000 | 0.0564 | 16 556 (203 966) | 3 578 (102 091) | 4 342 (312 308) | 3 131 (155 746) |
| S15 sky | per-line | — | **0.1838** | 8.566 | 8 115 (800 260) | 6 041 (978 458) | 8 743 (1 456 088) | 9 780 (1 858 057) |
| | plane + pinned | 99.7 % | **0.0133** | 6.838 | 8 413 (910 087) | 6 043 (933 650) | 10 770 (1 437 862) | 9 503 (1 526 983) |
| | plane, no residual | 98 % | 0.1871 | 5.442 | 10 650 (1 032 449) | 6 276 (1 279 221) | 9 595 (1 778 045) | 10 149 (2 222 225) |
| | local planes | 99.7 % | 0.0207 | 6.817 | 9 835 (1 006 920) | 8 006 (1 125 557) | 13 429 (1 589 989) | 11 775 (1 800 031) |

Earlier configurations along the way (contour clustering, first rim only, ground surfaces dropped) are in the run logs;
the one that mattered: with the first version of the rim rule (the texel immediately beyond the band) the trunk's hole on
S15 had no ground sheet from the sides and took the sky — median 4.9 m — because the band's own edge texel is a ground
texel; the app's rule (march past the own run) fixed it.

Reading: on exact data the sheets keep the per-line law's truth on S2 and S9, are within 1.5 cm on S26, and take S15 from
18 cm to 1.3 cm (the per-line law's median error there was the hill behind the sign; one ground sheet through the side rims
answers it as the row-axis kind-2 does, and the pinned residual follows the dome). Seams: S9 halves or vanishes, S26 falls by
half to three quarters with the bare plane, S2 is unchanged to slightly worse (its floor's slant is already the whole
signal). The kit cannot separate the three interior models; the pictures do.

## 3. Pictures (DA3-16, no truth)

| picture | arm | reached | jumps v (len) | jumps h (len) | kinks v (len) | kinks h (len) |
|---|---|---|---|---|---|---|
| troll | per-line | — | 99 203 (1 711 260) | 65 535 (1 452 445) | 91 287 (2 727 132) | 65 610 (2 488 140) |
| | plane + pinned residual | 91.5 % | 107 134 (1 910 079) | 74 266 (2 067 177) | 104 488 (3 303 182) | 79 739 (3 573 663) |
| | plane, no residual | 78.9 % | 17 444 (311 365) | 16 772 (421 282) | 18 325 (501 328) | 20 648 (682 536) |
| | local planes | 62.2 % | 120 970 (2 387 551) | 106 621 (2 948 346) | 107 671 (4 046 349) | 107 324 (5 110 597) |
| vermeer | per-line | — | 110 222 (4 151 799) | 78 795 (2 188 851) | 132 525 (7 705 370) | 66 697 (3 780 473) |
| | plane + pinned | 95.8 % | 61 528 (1 162 405) | 42 675 (1 356 066) | 76 273 (2 160 650) | 35 170 (2 513 265) |
| | plane, no residual | 68.6 % | 22 945 (311 306) | 41 184 (485 788) | 14 511 (463 194) | 18 531 (729 414) |
| room | per-line | — | 44 834 (655 195) | 44 071 (628 026) | 54 298 (1 129 550) | 53 276 (1 089 251) |
| | plane + pinned | 92.4 % | 45 482 (845 880) | 65 493 (1 382 845) | 52 534 (1 442 596) | 72 372 (2 392 241) |
| | plane, no residual | 83.6 % | 14 265 (326 013) | 13 027 (232 864) | 17 753 (575 432) | 16 025 (390 071) |

Where the seams of the sheet arms sit (kinks by owner, vertical): with the bare plane there are **no same-sheet kinks at
all** on any picture (0 on the troll, 18 on vermeer); what remains is sheet boundaries (real steps and the specks below)
and the unreached texels. With the pinned residual the same-sheet class returns at 1.6 M (troll) — the rim's own noise,
carried into the first texels of the sheet by the Dirichlet data.

Surfaces on the pictures: troll 308 components, of which 1 is the cave (5 019 rim texels), 305 are specks thin along both
axes (constant-depth sheets) and 267 of those have strips under three texels and make no sheet; vermeer 2 full, 263 thin;
room 4 full, 463 thin. DA3's silhouettes are ramps and specks; the join law makes each its own component.

## 4. What the numbers say

1. **The construction does what it was built to do.** One sheet per surface removes the within-surface hatching by
   construction (same-sheet kinks 0) and, with it, most of the wall length: bare plane −82 % (troll), −92 % (vermeer),
   −50 % (room) on vertical jumps, −71 / −78 / −63 % horizontal. On the kit the truth holds and S15 improves fourteen-fold.
2. **The cost is coverage.** A single plane per surface lands in front of 8–32 % of the band's texels (the cave is not a
   plane; extrapolated 300 texels its tilt crosses the troll's own depth) and those texels get nothing — they would keep the
   occluder's depth, a clone, which the user's rules forbid. The per-line law reaches every texel (its window is local).
3. **Following the rim brings the noise back.** Pinning the plane to each rim texel's residual (or fitting a local plane
   per rim texel) restores coverage to 92–96 % but re-imports DA3's silhouette noise as same-sheet kinks: troll +12 %/+42 %
   jumps over the per-line law, room +29 %/+120 %; vermeer still −72 %/−38 %, whose wall is flatter and cleaner.
4. **The two are one question:** what is the sheet's interior on a surface that is curved *and* whose rim is noisy. A
   rigid plane is smooth and wrong in shape; an exactly pinned surface is right at the rim and noisy. Neither choice was
   ever available to the per-line law, whose window of g + 1 samples is a local smoother along the line — which is why it
   reaches everywhere and hatches everywhere.

## 5. The next arm (proposed, not built)

**A smoothing thin-plate sheet with the noise level from the data.** Per surface, the field over strip ∪ domain that
minimises Σ_strip (u − disp)² / σ² + λ · bending, with λ set by the discrepancy principle (Morozov 1966): the strip's RMS
residual equals the strip's own noise σ, measured as S21 measured it (third differences on the source, MAD → σ). On the kit
σ = 0 and the sheet interpolates (the S25 plate, equal to the line law on truth); on DA3 σ > 0 and the sheet follows the
surface's shape at the scale the noise allows and no finer. No free constant: λ is solved for. Advantages: one model for
both regimes; coverage of the pinned version, seams of the plane version, if the theory holds. Disadvantages: a sparse solve
per surface per λ (bisection, ~10 solves; the cave's domain is 200 k unknowns — minutes offline, needs care in the app);
S21's σ estimate read 0 on three of the six pictures' maps (the σ gate), so the noise measure itself must be re-checked on
the strips rather than the whole map; the specks (305 constant sheets on the troll) remain a separate question — they are
DA3's silhouette fragments, and whether a speck is a surface is the porous class (S15's canopy wants them, the troll's
silhouette does not).

**Alternatives.** (a) Hybrid: sheets where they reach, the per-line law where they do not — keeps 100 % coverage and most of
the seam reduction, but reintroduces the per-line hatching exactly in the hardest places (the unreached texels are where the
per-line law's own answer is ~100 steps behind the texel). (b) Sheets per surface with a quadratic instead of a plane: adds
curvature with 6 coefficients and no λ, but a quadratic extrapolated 300 texels is the ill-posed case S22 named.

## 6. Files and figures

`research/s35/sheets.py` (flags `--no-residual`, `--local`, `--drop-thin2`, `--no-extend`, `--step`, `--q`, `--truth`, `--out`);
outputs under each dump's `s35/` (or `s35_base/`, `s35_nores/`): `farField_stop.f32`, `farField2_stop.f32`, `who_stop.i32`,
`summary_<tag>.json`, `surfaces_stop.png`, `far_{perline,stop}.png`, `kinks_{v,h}_stop.png`. Picture dumps from
`harness/streak_class.js` (now writes `meta.json`, `disocc.u8`, `farField.f32`, `groundCol.u8`, `groundTex.u8`). Figures in
`research/s35/`: `troll_unreached_local.png`, and the far-field pairs added below.

## 7. The deformed plane: the smoothing thin-plate sheet (`--tps`)

The user's correction: a sheet is a deformed plane, not a flat one. Built as the field u over strip ∪ domain minimising
Σ_strip (u − disp)²/σ² + λ·(u_xx² + 2u_xy² + u_yy²), σ the strip's own noise (third differences, MAD → σ, Var(Δ³) = 20σ²,
floored at the grid's quantisation noise grid/√12), λ by the discrepancy principle (Morozov 1966: the strip's RMS residual
equals σ; log-grid then bisection), free boundary in the hole. Conjugate gradients with a Jacobi preconditioner.

| scene / picture | reached | truth median (m) | p90 (m) | jumps v (len) | jumps h (len) | kinks v (len) | kinks h (len) |
|---|---|---|---|---|---|---|---|
| S2 | 100 % | 0.0000 | 0.0430 | 7 976 (21 905) | 238 (17 702) | 677 (3 251) | 238 (17 702) |
| S9 | 100 % | 0.0000 | **0.0320** | 5 038 (37 497) | 9 824 (65 099) | 1 300 (47 738) | 2 445 (78 136) |
| S26 | 100 % | **0.0000** | 0.0552 | 10 374 (67 789) | 232 (15 633) | 1 556 (75 602) | 253 (17 324) |
| S15 | 99.7 % | 0.0402 | 4.867 | 10 697 (1 096 585) | 11 524 (1 579 199) | 9 917 (1 819 391) | 11 492 (2 637 178) |
| troll | **34.6 %** | — | — | 59 066 (2 193 605) | 41 320 (2 602 197) | 26 529 (3 887 383) | 28 721 (4 805 132) |
| vermeer | **9.8 %** | — | — | 51 754 (1 691 350) | 79 562 (3 176 639) | 22 436 (3 033 846) | 28 038 (5 897 705) |
| room | **43.0 %** | — | — | 37 929 (690 665) | 30 473 (879 253) | 22 110 (1 077 254) | 23 879 (1 494 423) |

On the kit it is the best interior so far (S26 median 0 with the seams halved; S9's p90 halves) except S15 (4 cm against the
pinned plane's 1.3 cm: the dome is followed at the noise scale, not through every rim texel). On the pictures it collapses —
and the collapse pointed at the real fault, §8.

## 8. Why every sheet lands in front of the band on the pictures: the surface contains the occluder

A check added to the run: the largest surface's strip against its own rims.

| picture | strip texels of the largest surface | rims | strip texels nearer than the rims by > 20 tol | their disparity | band's own disparity |
|---|---|---|---|---|---|
| troll | 869 642 (the whole visible component) | 5 019 | 126 917 (14.6 %) | 5.00 | 4.86 |
| vermeer | 902 436 | 5 041 | 108 117 (12.0 %) | 5.83 | 4.99 |

DA3 joins the occluder to its background — at the feet, along the ramps at silhouettes (S28 §: "a quarter of the troll's band
joins no visible surface"; the troll is joined to the ground and the trees). Under the join law the cave and the troll are
ONE connected component, so "the cave's surface" was fitted to the troll's own texels too: a flat plane through both lands
in front of a fifth of the band (§4.2), and the thin plate, which follows the data closely, lands in front of two thirds.
The per-line law never met this because it works along a line, where the rim is a local discontinuity whether or not the
two surfaces touch elsewhere. So the remaining fault of the sheet model on pictures is not the interior model; it is the
**surface segmentation**: which visible texels are the background and which are the thing in front. That is the object
question (S28/S29), and the app already has the answer's source.

## 9. With object masks (SAM 2.1; the troll's S28 map, vermeer and the sunflower field clicked for this test): `--mask`

Texels of different object ids are never joined, so runs, components, strips and sheets stop at the mask. Masks:
troll picture 13 objects (S28), vermeer 9 (the woman, table, basket, jug, bowl, bread, wall basket, lantern, box;
`harness/shots/objlayers/view_vermeer/overlay_sam.png`), the "room" picture — which is a sunflower field — 9 flower heads
(porous; the mask covers 7 % of it). "Specks dropped" = a surface with no extent along either axis is not extrapolated.

| picture | arm | reached | jumps v (len) | vs per-line | jumps h (len) | vs per-line | kinks v (len) | kinks h (len) | same-sheet / boundary / own kinks v |
|---|---|---|---|---|---|---|---|---|---|
| troll | per-line law | — | 99 203 (1 711 260) | | 65 535 (1 452 445) | | 91 287 (2 727 132) | 65 610 (2 488 140) | |
| | flat plane, no mask | 78.9 % | 17 444 (311 365) | −82 % | 16 772 (421 282) | −71 % | 18 325 (501 328) | 20 648 (682 536) | 0 / 283 k / 219 k |
| | flat plane, mask | 96.7 % | 31 521 (764 975) | −55 % | 25 296 (737 403) | −49 % | 44 462 (1 367 137) | 39 900 (1 288 187) | 16 / 1 327 k / 40 k |
| | flat plane, mask, specks dropped | 94.2 % | 13 623 (335 207) | **−80 %** | 9 733 (396 736) | **−73 %** | 10 359 (577 243) | 12 788 (718 928) | 43 / 507 k / 71 k |
| | pinned, mask | 98.8 % | 86 176 (1 399 957) | −18 % | 64 073 (1 329 339) | −8 % | 93 856 (2 398 715) | 75 757 (2 249 766) | 323 k / 2 037 k / 38 k |
| | thin plate, mask | 97.8 % | 30 362 (834 444) | −51 % | 32 540 (1 158 622) | −20 % | 16 728 (1 329 796) | 21 980 (1 850 057) | 46 k / 1 057 k / 227 k |
| vermeer | per-line law | — | 110 222 (4 151 799) | | 78 795 (2 188 851) | | 132 525 (7 705 370) | 66 697 (3 780 473) | |
| | flat plane, no mask | 68.6 % | 22 945 (311 306) | −92 % | 41 184 (485 788) | −78 % | 14 511 (463 194) | 18 531 (729 414) | |
| | flat plane, mask | 99.5 % | 29 532 (1 627 705) | −61 % | 33 405 (2 051 500) | −6 % | 48 617 (3 142 430) | 57 688 (3 898 326) | 0.4 k / 3 082 k / 60 k |
| | flat plane, mask, specks dropped | 99.3 % | 7 440 (837 235) | **−80 %** | 11 634 (1 839 562) | −16 % | 10 622 (1 631 288) | 20 370 (3 602 362) | 0.5 k / 1 581 k / 49 k |
| | thin plate, mask (28 min) | 99.7 % | 69 693 (1 470 059) | −65 % | 61 307 (1 327 558) | −39 % | 28 334 (2 080 518) | 24 694 (1 883 624) | 131 k / 1 863 k / 86 k |
| sunflowers | per-line law | — | 44 834 (655 195) | | 44 071 (628 026) | | 54 298 (1 129 550) | 53 276 (1 089 251) | |
| | flat plane, no mask | 83.6 % | 14 265 (326 013) | −50 % | 13 027 (232 864) | −63 % | 17 753 (575 432) | 16 025 (390 071) | |
| | flat plane, mask | 91.3 % | 16 489 (485 405) | −26 % | 15 825 (424 706) | −32 % | 24 335 (871 583) | 23 337 (736 728) | 0 / 750 k / 122 k |
| | thin plate, mask (11 min) | 88.5 % | 26 610 (623 667) | −5 % | 26 101 (590 701) | −6 % | 16 901 (1 010 630) | 17 087 (921 993) | 43 k / 594 k / 373 k |

Reading. (a) The mask does what §8 said it would: the largest surface's strip holds 2.8 % nearer texels on vermeer (from 12 %),
coverage goes to 94–99.7 % on the two pictures whose objects can be masked. (b) The remaining wall length is almost all
**boundaries between background fragments**: vermeer's wall is 657 components under the join law, 410 of them single texels;
each fragment's constant-depth sheet marches a one-texel line across the hole (the lattice in `s35/vermeer_far_mask.png`,
second panel). Dropping surfaces with no extent along either axis removes most of it: troll −80 %/−73 %, vermeer −80 % on
the vertical walls, at 94–99 % coverage — the same rule that hurt S15's canopy, where the fragments are real leaves. (c) The
thin plate with the mask reaches the most but keeps more boundary length than the flat plane and costs 5–28 minutes per
picture in this prototype; in the app it would need a multigrid solver or the flat plane. (d) The sunflower field is the
porous class: 9 flower heads are not its objects, the field is; neither arm nor the mask changes it much.

## 10. Where this leaves the design

1. The sheet model is right where the surfaces are separable: kit truth kept or improved (S15 14×), seams halved, full
   coverage; on the pictures, with an object mask, 97 % coverage and half the wall length gone.
2. What it needs from upstream is the thing the stack was heading for anyway: an object segmentation (SAM masks, one pass —
   S30's proposal chain), so that each object's reveal is filled from the surfaces *outside* it. The per-line law hid this
   need by being one-dimensional.
3. The interior model is a second-order choice once the segmentation is right: flat plane (smoothest, wrong shape on curved
   surfaces, but the shape error is bounded by the ordering clamp and rarely visible), pinned (exact rim, DA3 noise), thin
   plate at the noise scale (best on the kit, most coverage on pictures, 5–28 min here).
4. The remaining seams are between DA3's background fragments. Dropping fragments with no extent along either axis takes
   the troll and vermeer to −80 % of the per-line law's vertical wall length at 94–99 % coverage; S15's canopy wants those
   fragments kept. Whether a fragment is a surface or noise is the porous question, and it now has a measured cost on both
   sides.
5. **Best measured configuration on pictures:** object mask + flat plane per surface + specks dropped. On the kit the same
   configuration is the "plane, no residual" row of §2 (truth kept on S2/S9, S26 1.6 cm, S15 19 cm — the dome needs the
   deformed plane, which the thin plate gives at 4 cm and the pinned plane at 1.3 cm).

## 11. Sanity check (user, 2026-09-16): the depth fields were not renders, and the flat sheets were wrong

The user pointed out that nothing shown was a render and that the fields still looked streaky. Two corrections followed.

**The flat-plane sheets had the wrong values.** Inside the troll's hole the flat sheets filled at depth 0.25 where the
per-line law puts the cave at 0.07 (own depth 0.27); vermeer's wall the same (0.43 against 0.05). A smooth wrong surface has
no seams, so the seam instrument rewarded it, and the kit truth did not catch it because the kit's scenes are planar and
small. The "−80 %" of §9 for the flat plane was the smoothness of wrong values; it is withdrawn.

**A check that needs no truth: continuity at the rim.** The fill just inside the band must match the visible far surface just
outside it. Median mismatch (depth units) over band-edge texels with a visible far neighbour:

| | per-line law | flat sheets | thin-plate sheets |
|---|---|---|---|
| troll | 0.298 | 0.211 | **0.089** |
| vermeer | 0.018 | 0.357 | **0.008** |

The deformed plane (thin plate) is the only interior that is both continuous with the visible surface and smooth; on the
troll it is more continuous than the app's own law.

**Renders through the app** (`harness/sheet_render.js`: the offline field written into the plate's depth texture after the
app's own bake; colour is the app's wash; `s35/*_render_*_pair.png`, 45°): the troll behind the woman loses most of its
horizontal streaking under the thin plate; vermeer's wall behind the woman still breaks into blocks.

## 12. Why vermeer's wall broke into blocks, and the two rules that fix it

Inside the woman's band, 75 % (vertical) and 91 % (horizontal) of the block seams were between sheet #0 (the wall, fill
0.087) and sheet #11 (1 945 rims, fill 0.42): the **floor**, whose visible strip below her is 170 rows against a reach of
600 rows upward — thin along y by the app's per-line rule — and therefore continued at **constant depth** up the whole hole,
where, being nearer, it beat the wall under the layered order. A floor continued at constant depth is a wall in front of the
wall; the app's law escapes this only because its row axis (the wall on both sides) wins the arbitration.

1. **Evidence order** (`--evidence`): a sheet extrapolated at constant depth along a thin axis is a hedge, not a measurement;
   where a fully fitted sheet also lies behind the texel, the fitted sheet shows, and hedges fill only what no fitted sheet
   reaches. Vermeer (mask, flat, specks dropped): jumps v 23 392, h 31 904 — **99 % below the per-line law**; render
   `s35/vermeer_render_evid_pair.png`: the wall behind her is one smooth surface. The floor behind her legs is then wall too
   (a trench at her feet), which is the price of demoting the floor.
2. **The 2-D thin criterion** (the app's error budget applied to a strip): the per-line rule needs g + 1 samples to hold the
   slope's error to half a quantum over g; a strip fits one slope from many lines, and the least-squares slope error falls as
   1/((extent − 1)·√lines), so the budget is met when (extent − 1)·√lines ≥ g. Vermeer's floor (170 rows × 300 columns) is
   then fitted, not hedged. Result: it competes with the wall as a plane and the blocks return (jumps v 1 316 663, render
   `s35/vermeer_render_evid2_pair.png`) — the fitted floor plane is not good enough over 600 rows on DA3's floor, or the
   floor–wall crease it implies is not where the wall's sheet is. Kit under the same flags: S2 unchanged, S26 median 0,
   S9 0.032 m (the ground now a fitted sheet that wins somewhere), S15 0.258 m (worse: no residual, hedges demoted).
   Troll (mask, evidence, 2-D thin): jumps v 534 428 (−69 %), h 558 989 (−62 %), reached 95 %.

Regional join (`--merge`: a fragment joins an adjacent surface when its texels lie within tolAt of that surface's plane)
merged **0** of vermeer's 658 fragments: they are genuine deviations beyond the tolerance, not curvature breaks — DA3 speckle.

## 13. Where this leaves it (honest)

- The construction that renders clean on vermeer is: object mask + one flat sheet per surface + specks dropped + hedges
  demoted. It is clean because the wall alone fills the hole. Where the floor should show behind her legs it shows wall.
- The thin plate is the right interior by the rim-continuity check and the kit, and is what the troll's clean render used;
  its cost (5–28 min) and its behaviour with demoted hedges are not yet measured together.
- The kit and the pictures still pull in different directions on the hedges (S15's canopy and hill want them; vermeer's
  floor must not win). One rule does not yet serve both; the object/porous split is where that line will have to be drawn.


## 14. The floor ("solve the floor")

**What §12 called the floor was not the floor.** The 0.42 surface that filled the woman's lower band (§12's #11; #415 in the
later runs, id 0, 8 192 texels, rows 603–1007, cols 61–534) is the strip of background visible **between the table and the
woman**. DA3 gives it the objects' depth: row 720 reads 0.446/0.439/0.437/0.436 across the gap against the cloth at 0.436 and
the skirt at 0.401; row 800 reads 0.422/0.402 against 0.427 and 0.405. The wall it actually shows is at 0.003. A narrow
background gap between two near objects takes the objects' depth in a monocular map — the same fusion that made the object
mask necessary (§8), seen from the background's side. The real floor, right of her skirt, is clean: the silhouette steps
0.327 → 0.238 → 0.056 in two texels (row 950), the floor is constant along a row (0.056 at row 950, 0.105 at row 1000 over
cols 660–780) and rises linearly with the row (col 850: 0.003 at row 880, 0.007 at 888, … 0.102 at 1000 — 0.0085 per 8 rows;
col 800 has a step 0.003 → 0.035 at row 856 and then the same rise). The wall–floor crease is a smooth bend at ~row 880.

**The app's ground detector cannot see this floor, and no tolerance fixes it** (`--ground-detect`, ported, then removed;
record comment in `sheets.py`). With the precision tolerance at the grid (the app), at the third-difference σ (which reads
1.0 grid on this map: the estimator sees the quantisation, not the map's deviation from planarity) or at the join quantum,
the result is identical: horizon vote at row −335 404, 0 inliers of 326–355 "horizontal" columns. Two structural reasons:
(1) under the join law the wall and the floor are **one column run** (rows 0–1007 at columns 700 and 800) because the crease
is a smooth bend, so every "rising run" is wall+floor and its line fit is meaningless; (2) in the app's flattened world (6 cm
of relief across the whole picture) a real floor's horizon lies ~10 000 rows above the frame (the floor's ze changes 1 % over
127 rows), so the shared-horizon vote has no power. The premise (grid tolerance is why 16-bit maps have no ground) is
falsified. The wall+floor is an L-bent sheet like any other and needs the bend-capable interior, not a plane law.

**Fusion test** (`--fused`). A component whose depth along its boundary to other mask ids is the neighbouring objects' own
depth is fused; its sheet is a hedge. Three versions were needed to make it a classifier, each falsified by the numbers:

| version | comparison | vermeer result |
|---|---|---|
| 1 | pair straddling the mask line, depth-joined? majority | wall 0.81, woman 0.82, table 0.99, sliver 1.00 — everything "fused" |
| 2 | boundary texel vs the nearest texel of the other id's **body** (largest depth component of that id), ratio test (rimT); majority | woman 0.08, table 0.09, sliver 0.99; **wall 0.66** (its boundary with the basket, 1.00, and the foot warmer, 1.00: one surface under rimT in the flattened world) |
| 3 | as 2, bodies exempt (fusion is a property of a fragment) | sliver FUSED (0.99 of 3 033 pairs); 350 fragments, 14 561 texels in all; every body distinct |

Version 1 failed because SAM's edge sits a few texels off DA3's depth edge, so the pair across the mask line is wall–wall
or skirt–skirt; version 2 because two bodies matched along their boundary are simply one surface under the app's law. The
distribution under version 3 for the 23 components ≥ 100 texels: matched share < 10 % for 5, 10–50 % for 3, 50–90 % for 2,
≥ 90 % for 13 — the bodies at both ends, the sliver at 0.99. The rule uses the app's ratio tolerance and the majority; no
new constant. Known limit: an object whose mask is split by a depth step into two comparable halves has a "fragment" that
can be called fused.

**Plane arm with the fusion rule** (mask, flat, specks dropped, evidence, two-sided, fused; `s35_fused`): reached 99.4 %,
hedges needed for 536 texels only; jumps v 732 (len 26 168), h 1 531 (len 35 865) against the per-line law's 110 222 /
78 795 and the previous best (§12's "wall only") 23 392 / 31 904; boundary kinks v 307 / h 319 (from 29 734 / 28 349). The
fill behind her legs is now the wall+floor sheet alone (#0 on every row) — but a **plane**, so it reads 0.098–0.117 on every
row from 640 to 1000 where the wall is 0.003 (rows < 880) and the floor rises 0.007 → 0.105 (rows 880–1000): the slab of
§12, for the known reason (§10: a plane cannot be an L). The thin-plate interior on the same configuration is the test of
the floor itself (below).

**The thin plate on the L-bent component** (`s35_fused_tps`, solver fixed). Two findings on the way. (1) The earlier thin-plate
runs had not converged: Jacobi-preconditioned CG on the 870 k-unknown biharmonic system returned the strip data and ≈ 0 on
the domain, which the discrepancy search read as rms < σ at every λ (the "0.000" fills behind the woman in `s35_mask_tps`,
§11's rim-continuity numbers included). Now algebraic multigrid (pyamg, smoothed aggregation with the affine null space as
candidates) preconditions CG and the relative residual is checked after every solve (worst 1.0e-8 on vermeer; 217 s for the
big surface). (2) Converged, the plate of the wall+floor component behind the woman's legs comes out at depth 0.67–1.0 —
nearer than the woman — and 0.000 above her: the component also holds the left side wall (a ramp 0.008 → 0.5 across the
leftmost 50 columns, DA3's receding window wall), so it is a sheet with three folds, and a biharmonic surface fitted through
them extrapolates its rim slopes across the hole. With the data tolerance raised to the visible step (the app's tolAt; λ
1.2e5) it is worse, not better (1.0 everywhere behind the legs). A single deformed plane is the wrong sheet for a folded
surface; the folds must be found first.

**Planar patches** (`--patches`). Every join-law component is split into patches that one plane fits within the visible step
(tolAt, the join tolerance: a texel within one step of a plane is that plane at every pose). Region growing in waves from the
texel deepest inside the unassigned set; the plane is refitted from all members after each wave; members the final plane no
longer fits are released and seeded again. Vermeer: 11 007 patches from 658 components in 8 s — the back wall is one patch
of 343 515 texels (rows 0–891), the floor splits into row strips (rows 927–958 at 0.047, 964–997 at 0.084: DA3's floor is
not planar to one step over its whole rise), the side wall into vertical strips. Two more rules were needed, each from the
buffer:
- **No area, no surface**: a strip whose texels are collinear along a grid line is a line, not a surface (three
  non-collinear points determine a plane). These are DA3's one-texel silhouette ramps (0.24–0.32 between skirt and floor):
  legitimate far rims under the candidate rule, nearer than the floor, and they had won the whole band behind her legs
  (fill 0.32–0.45). Dropped: 185 previously fitted line sheets.
- **2-D domain** (`--geo`): a floor strip's rims lie along the skirt's edge, so its along-line marches cover only its own
  rows; between two strips' rows the wall's column marches or a hedge showed (row striping: jumps v 21 716 / h 45 861). A
  sheet now claims the band texels within geodesic reach of its rims through the band, the reach being its own longest
  march (the reach is a property of the hole, not of a direction; no new constant). Objects under the two-sided rule keep
  only their closed marches as fitted. Computed on demand per sheet — storing 4 311 discs was 14 GB.

**Result on vermeer** (`s35_geo`: mask, fused, patches, geo, no-area, specks dropped, evidence, two-sided): reached 100 %,
hedges needed for 56 texels; behind her legs the fill is the wall (0.008) down to row 880 and then the floor at 0.024 /
0.066 / 0.105 on rows 920 / 960 / 1000 — the visible floor to her right reads 0.030 / 0.065 / 0.102 on those rows at column
850 — constant along each row (min = max). The floor also continues under the table across the whole width. Jumps v 3 333
(len 23 563), h 57 310 (len 151 825): many, but 2.6 steps each — the seams between overlapping wall patches and floor strips
whose planes differ by a step or two where they meet; per-line law 110 222 / 78 795 (4.15 M / 2.19 M). Render
`s35/vermeer_render_geo_p45_pair.png` (and `_user26_`): the wall ends at its foot and the floor recedes behind her.
Panels `s35/vermeer_floor_panels.png`.

**The other two pictures and the kit under the same flags** (jump counts (length in steps), v / h; kit: band depth error vs
the first hidden layer, median m):

| scene | flat sheets (fused rule) | patches + geo | per-line law |
|---|---|---|---|
| vermeer | 732 (26 168) / 1 531 (35 865), slab behind the legs | 3 333 (23 563) / 57 310 (151 825), floor right | 110 222 (4.15 M) / 78 795 (2.19 M) |
| troll | 6 332 (341 839) / 8 354 (446 573), reached 95.3 % | 46 683 (380 291) / 25 246 (348 877), reached 99.7 % | see §8 |
| sunflowers | 8 162 (158 263) / 8 991 (168 668), reached 90.2 % | 26 886 (447 679) / 19 975 (437 808), reached 99.3 % | see §8 |
| S2 | 0.0000 | 0.0000 | 0.0000 |
| S9 | 0.0320 | 0.0320 | 0.0000 |
| S15 | 1.0630 | **0.0691** | 0.1838 |
| S26 | 0.0000 | 0.0299 | 0.0000 |

Panels `s35/troll_panels_geo.png`, `s35/room_panels_geo.png`. Reading: the patches make every hole a mosaic of tangent
planes — right for the room's walls and floor (vermeer), a faceted approximation of the troll's cave (many small seams of a
step or two instead of few large ones; total length about equal), and wrong in the sunflower field, whose leaves are curved
and whose big flower stands against the sky: leaf and stem patches (background id, one-sided) extend upward within their
reach, and being nearer than the sky they win the sky's hole under the layered order (both arms do this; the patch arm
more, ×2.7 in length). S26 loses 3 cm: its curved ground is faceted. S15 gains (1.06 → 0.07 m) because the flat sheet over
its dome was the slab problem in another form.

**Where this leaves the floor.** Solved on vermeer by three rules that generalise (fusion by body match, no-area, planar
patches with a 2-D domain), each with the app's own tolerance and the majority rule, no new constants. Open, with numbers:
(a) a sheet's END — a background sheet that meets the sky (or a corner) should stop there; the two-sided rule does this for
objects, `--twosided-all` did it for backgrounds but broke the table-hides-wall case (§13); the sunflower field is the test
picture; (b) curved surfaces are faceted (S26 +3 cm, the troll's cave) — the deformed plane per PATCH (a thin plate whose
domain is one face, so it has no folds to extrapolate) is the natural next interior, now that the solver converges.

## 15. Where a sheet ends (item a): three rules tried, three falsified

The question: a sheet reaches into a hole; how far may it go? Under the layered order the nearest sheet that reaches a texel
shows, so a sheet that reaches too far wins ground it has no right to (the sunflower field: leaves at 0.06–0.13 filling the
big flower head's band where the sky at 0.009 is visible all around it). Each candidate rule below was implemented, measured
on the kit's truth and the three maskable pictures, and removed when the numbers refused it (rule 7). No constants were
involved in any of them; they failed on their logic, not their tuning.

**1. The exit test** (`--ends`, removed; record comment in `sheets.py`). A march that exits into a surface FARTHER than the
sheet contradicts it — the far surface is visible where the sheet would have to be — while closed, frame-edge and
nearer-surface exits do not. The four cases are exhaustive and each is the app's own comparison (the join tolerance, then
the ratio test so that a facet of the same surface does not contradict itself). **Falsified on S15**: the fill that is right
behind its trunks is the NEAR canopy (fill 0.47 against truth 0.08 m), and the canopy's marches exit into the far hill and
the sky, so the rule demoted it. 17 878 of 26 087 scored texels changed owner and their error went 0.054 → 2.264 m; the band
median went 0.069 → 1.315 m. The exit says only that the sheet must end SOMEWHERE along that march, never where, and a near
surface legitimately continues behind an occluder and comes out into the far background.

**2. The own-extent bound** (`--reach`, kept as a flag, not a default). A sheet continues into the hole no farther than the
surface itself extends outside it: reach = min(longest march, geodesic radius of its own visible patch walked from its rims).
Symmetric with the domain, so no units to convert. **Falsified by what the radius measures**: walking inward from the rims
measures the surface's THICKNESS, not its size, and a surface seen as a strip (rims along its whole length) reads ~0 — the
median own-extent was 0 on S15, S2 and S26. S15 truth 0.069 → 0.412 m, with the canopy starved like everything else.

**3. Everything is a bounded thing** (`--twosided-all` under the current stack). If the sunflowers' leaves fail because they
are things with silhouettes, treat every surface as one: only closed (two-sided) marches are measurements. **Falsified on the
picture it was for**: the big flower head's fill moved AWAY from the sky (0.067 → 0.139), because demoting every sheet to the
hedge tier leaves the same "nearest shows" order inside that tier — the tiering does not change which sheet is nearest, only
which pool it competes in. Vermeer under the same flags: jumps 59 732 / 86 015 (len 1.81 M / 3.27 M) against 3 333 / 57 310
(23 563 / 151 825). S15's truth alone improved (0.069 → 0.012 m).

**What the sunflower field actually shows.** Reading the fill rather than the rule: behind the big head DA3 has foliage at
0.06–0.13 around its base and sky at 0.009 above, and the geo arm's fill there is p10 0.019 / p50 0.067 / p90 0.131 — a
mixture of both, which is roughly what is behind it. What the render shows is not a sheet reaching too far but a band broken
into steps, and the seam counts say the same: flat sheets over whole components 8 162 (len 158 263), patches 26 886 (len
447 679). **The sunflower regression is the facet problem (b), not the end problem (a).** Item (a) is closed with a negative
result: the depth map alone does not say where a sheet ends, and none of the three tests recovers it. What does say it is the
object segmentation — a masked object's sheet is bounded by its own silhouette, which is the two-sided rule that already
works on vermeer and the troll. The sunflower field has 9 flowers masked out of a field of foliage, and its unmasked leaves
are treated as background, which is exactly what "clearly defined blobs" would fix at the segmentation stage.

## 16. The thin plate per face (item b)

With each patch fold-free by construction, the smoothing thin plate can be solved per face over the same 2-D domain
(`--patches --geo --tps`; AMG solver, converged, worst relative residual 1e-8).

| scene | flat plane per patch | thin plate per face | per-line law |
|---|---|---|---|
| S26 jumps v / h | 2 308 (114 533) / 2 105 (83 890) | **1 551 (52 264) / 744 (52 565)** | 11 129 (148 302) / 465 (26 710) |
| S26 truth median | 0.0299 m | 0.0311 m | 0.0000 m |
| S15 jumps v / h | 4 761 (778 942) / 4 063 (814 002) | 5 576 (685 744) / 4 672 (732 887) | 8 115 (800 260) / 6 041 (978 458) |
| S15 truth median | **0.0691 m** | 2.2678 m | 0.1838 m |

The plate halves S26's seam length and cuts S15's, and costs S15 2.2 m of accuracy: over a deep hole (S15's median march is
106 texels) the plate continues the face's curvature, and curvature integrated over 100 texels is metres. A plane does not.
So the interior stays a plane at long reach; the plate is worth having only where the reach is short, and "short" would need
a rule of its own. Not made the default.

**Recommended construction, unchanged from §14**: object mask, fusion by body match, planar patches, no-area rule, 2-D
geodesic domain, flat plane per patch, specks dropped, evidence order, two-sided for masked objects. It is the arm that gives
vermeer's floor and S15's best kit number (0.069 m against the per-line law's 0.184 m).

## 17. The faceting, and the thin plate per face (item b, done properly)

**The faceting is real and it was measured first.** Splitting every far-field jump by owner (sunflower field, patches arm):

| | total jump length | same sheet | facets of ONE join-law surface | different surfaces |
|---|---|---|---|---|
| vertical | 447 625 | 4 % | **96 %** | 0 % |
| horizontal | 437 596 | 1 % | **98 %** | 0 % |

**The merge** (`--smooth`). Two adjacent patches are one smooth face when the step between their planes is invisible over the
distance they span: |slope_A − slope_B| · L ≤ tolAt, with L the smaller patch's own extent √area. Slope times length is a
depth, compared against the same visible step the patches were cut with, so no constant is added; it is a crease test, not a
flatness test, so a curved surface rejoins and a wall-against-floor crease fails it by orders of magnitude. Never merges
across a join-law break. Sunflowers 19 173 → 6 853 faces, vermeer 11 007 → 4 514, S26 88 → 36, S2 56 → 24. The ownership map
is visibly consolidated (`s35/room_panels_geo.png` against the new `who`), but **the seams did not move** (v 33 067 against
27 175): a merged face is curved and a single plane cannot follow it, which is exactly what item (b) is for.

**Two more falsifications on the way** (both removed or left as non-default flags):
- *Facet-wide domains.* If the steps are domain truncation, give every facet its component's whole domain and let the order
  pick. Worse, not better: sunflowers v 41 681 (len 840 937) against 27 175 (448 944). A facet's plane extended far is also
  rejected wherever it flies in front of the occluder, so the mosaic returns with wilder values.
- *Per-texel error budget* (`--budget`, kept, not default). Shrink the fitted slope by its own predicted standard error
  against the visible step. It never fires: the patches are *selected* to be planar, so their residuals are the noise and the
  covariance says the slope is certain. Selection bias, not a tuning problem. Sunflowers: 29 373 (445 094).

**Why the plate needed a prior.** With merged faces the plate is fold-free, and on S26 it reaches **truth median 0.0000 m**,
the best possible, p90 0.0532 (best of every arm). On S15 it still gave 2.25 m, and the reason is visible in the ownership:
a face with a strip of **165 texels took 11 930 band texels** at 2.2 m error, while the same face's *plane* takes almost
none. The plate's free boundary lets a small face bulge toward the camera over the hole and win the layered order. The
face's own plane is the statement "no bending beyond what was measured", so it enters the energy as a prior on the domain at
weight 1/visible step against the strip data at weight 1/σ. Since σ is far below the step the data rules on the strip and the
prior rules where the plate would otherwise be free.

**Only merged faces need a plate**: a face still made of one patch is planar by the patch grower's own test. That takes the
solves from 6 853 to 192 (sunflowers) and 130 (vermeer), and reproduces S26 exactly (0.0253 with 7 solves against 10).

| arm | S2 | S9 | S15 (median / p90) | S26 |
|---|---|---|---|---|
| per-line law (app) | 0.0000 | 0.0000 | 0.1838 / 8.5657 | 0.0000 |
| patches + plane (§14) | 0.0000 | 0.0320 | 0.0691 / 6.7898 | 0.0299 |
| merged faces + plane | — | — | 0.0853 / 6.7289 | 0.0257 |
| merged faces + plate, no prior | — | — | 2.2540 / 6.7540 | **0.0000** |
| merged faces + plate + prior | 0.0121 | 0.0320 | 0.0795 / **4.2489** | 0.0253 |

**Net.** On the kit it is a wash on the medians and a clear gain on S15's tail (p90 4.25 against 6.79 and the per-line law's
8.57). On the pictures it changes nothing visible: vermeer stays clean (`s35/vermeer_faceting_pair.png`, jumps 3 762 /
55 543 against 3 333 / 57 310) and the sunflower field is unchanged (`s35/sunflowers_faceting_pair.png`, 27 994 against
27 175). Two findings explain that:

1. **Vermeer's remaining 55 000 horizontal "jumps" are not seams.** Their second differences are tiny — kinks 2 058 / 4 232
   against the per-line law's 132 525 / 66 697, down 97 % — so the field is a smooth steep slope that the first-difference
   instrument counts as wall length. The kink measure is the honest one for seams, as §12 said when it was introduced.
2. **The sunflower field's jumps are not faceting either.** Its join-law component fuses foliage with sky through DA3's
   ramps (component 0 spans 0.009–0.474), so the patches inside it are genuinely different surfaces and the crease test
   correctly refuses to merge them. The "96 % facets of one surface" figure is measured against the *join-law component*,
   which on this picture is a fused blob, not a surface. The staircase visible in its render is in neither arm's far field
   (both are smooth, `s35/room_panels_geo.png`) and appears in the per-line panel too: it comes from the app's own plate
   stage, not from the sheet.

**Recommendation.** Keep the §14 construction and add the merge and the primed plate: object mask, fusion by body match,
planar patches, crease-test merge, no-area rule, 2-D geodesic domain, thin plate on merged faces with the plane prior and
plane elsewhere, specks dropped, evidence order, two-sided for masked objects. It is never worse than §14 on the kit, it is
much better on S15's tail, and it leaves vermeer's floor exactly as it was. The cost is 130–190 plate solves per picture
(20–37 min offline), so the app would ship planes first and the plate as an offline refinement.

## 18. Adopted as the default, and what it costs to bake

`sheets.py` with no flags is now the §17 construction: object mask (when one is given) → fusion by body match → planar
patches → crease-test merge into faces → no-area rule → 2-D geodesic domain → thin plate with the plane prior on merged
faces and the plane elsewhere → specks dropped → evidence order → two-sided for masked objects. Every part has its own
`--no-<part>` switch and `--plain` turns the lot off for an A/B against the earlier arms. Verified by rerunning the kit with
no flags: S26 0.0252 m against the flagged run's 0.0253, S15 0.0715 m (p90 4.2489, unchanged).

**Two solver changes, neither of which touches the answer.** The multigrid hierarchy is a *preconditioner*, so conjugate
gradients converge to the same solution whichever λ it was built at; it is now rebuilt only when λ has moved more than two
decades, and the relative residual is still asserted after every solve (worst 1e-8), with an automatic rebuild-and-redo if
it is not met. The discrepancy search replaced its nine-point λ grid plus six bisections with a bracketed secant in
(log λ, log rms), which finds the same λ in about five solves instead of sixteen.

| stage | before | after |
|---|---|---|
| S26 thin plate | 21.4 s | 6.9 s |
| S15 thin plate | 109.4 s | 30.6 s |
| vermeer thin plate | 2 247.7 s | 1 410.1 s |

**The bake, measured on vermeer (896 × 1008, 370 698 band texels), offline Python on one core:**

| stage | time |
|---|---|
| patches, merge, fits | ~30 s |
| domain pass (marches + closure) | 456 s |
| thin plate, 130 faces | 1 410 s |
| layered order and output | 220 s |
| **total** | **2 109 s (35 min)** |

So the plate is two thirds of it. `--no-tps` gives the same construction with planes and costs about 12 min on the same
picture, which is what the §14 arm already cost — the merge itself is nearly free. None of this is the app's bake: the app
has no sheets in it at all yet, this is the offline prototype, single-threaded Python with per-surface loops, and the app's
own per-line bake is seconds. What the prototype's timing does say is that the plate cannot be a browser bake as written;
it belongs offline, or it needs the work below.

**Where the remaining time is, in order of size**: 130 plate solves at ~11 s each, dominated by a handful of large faces
(parallel across cores is the obvious 4×, held back here by a 10 GB peak); the domain pass, which marches every rim of
4 514 surfaces in Python including the thousands of specks that the no-area and three-texel rules drop immediately
afterwards; and the layered order, which recomputes each face's geodesic domain a second time. None of the three is
intrinsic to the method.

## 20. First principles: what the reference "Silver Warrior" GIF actually does

The user asked how someone's parallax GIF of Frazetta's Silver Warrior (`silverwarrior_anim.gif` in the app repo) is so
clean. Measured, not guessed (`s35/silverwarrior_gif_frames.png`, `s35/silverwarrior_gif_crops.png`):

| property | measured |
|---|---|
| frames, size, loop | 31 frames, 726 × 966, 3.2 s, pendulum (frame 7 ≡ frame 23 against frame 0) |
| frame timing | 100 ms per frame, 200 ms holds at the two turning points (eased reversal) |
| motion axis | horizontal only; every band's vertical shift is 0 |
| far content (sky, mountain, warrior) | −24 to −36 px at the extreme |
| near content (front bears) | +32 to +37 px at the extreme |
| zero-parallax plane | the sled and middle bears (rows 480–640 shift ≈ 0) |
| total relative parallax, nearest to farthest | 65 px = **9 % of the width**; per side ≈ 5 % |
| depth field | graded, not layered: the background band alone runs −24 → −36 → −72 across its width |

**Why it looks so good, in order of weight.**
1. **It reveals almost nothing.** The widest disocclusion any silhouette can open is the relative shift across it, at most
   65 px and at most once per silhouette; the warrior against the mountain opens about 6 px because both are far. The app's
   envelope on vermeer reveals **41 % of the picture** at some pose (370 698 of 903 168 texels); this GIF never reveals more
   than a few per cent, in strips no wider than a bear's whisker line. Everything in §1–§19 is about what fills a reveal; at
   5 % amplitude there is barely a reveal to fill.
2. **One axis.** Horizontal motion opens only vertical silhouettes; the bears' backs, the sled's rim and the horizon never
   open. The app moves on two axes and the user wants ±90° on both.
3. **The pivot sits mid-scene**, so far and near each carry half the total shift, which halves the widest reveal at any one
   silhouette. (The app pivots at the portal plane, which is the same idea.)
4. **The picture forgives.** Where the widest reveals happen — the front bears against snow and fur — the background is
   texture with no structure, so a stretch or a blur or a painted fill reads as more of the same. The one structured
   background behind a near object, the sled's ornament behind the bears' heads, opens only a few pixels because the depth
   authored there puts the heads barely in front of the sled.
5. **Motion hides seams.** The eye tracks the moving content; a strip that would be a visible artefact when held still is
   crossed in three frames at 100 ms and the turning points are eased.

**What it does not tell us.** Nothing about depth accuracy (the graded shifts are consistent with a smooth AI depth map or
a hand-painted one), nothing about the fill law (nothing is revealed wide enough to judge one), and nothing about the app's
regime: at ±45° the same picture opens strips ten times wider than anything in this GIF, and at those widths the sheet
question is unavoidable. The honest lesson is a design one: amplitude and axis count buy more cleanliness than any fill
law, and the reference effect spends 5 % of the width where the app spends its whole envelope.

## 19. The bake, made fast (plane-only path first)

Every change below leaves the far field bit-identical (vermeer, S26, S15 compared field-to-field; the only differences are
conjugate-gradient noise below 1/1000 of a visible step, with no owner changes). Measured on vermeer, 896 × 1008:

| stage | §18 | now | what changed |
|---|---|---|---|
| domain pass | 456 s | 56 s | the marches were a Python while-loop over 339 M texel steps; now four cumulative scans give each march's length and the march is a row or column slice marked at C speed. The extend-arm domain ran a full-image `isin` per surface although `--no-extend` is the default; built only when asked. Surfaces whose face is under three texels or one texel wide are dropped before any of it (1 554 of vermeer's 2 320): their strip is a subset of their face, so the three-texel and no-area rules would drop them anyway |
| layered order | 220 s (435 s after the domain fix exposed it) | 9 s | profiled, not guessed: 59.5 of 62.9 s on the sunflowers was the rim-pinned harmonic residual, a sparse Laplace solve per sheet assembled in Python. It is now off by default — §11 had already measured that following each rim's residual brings the map's noise back, the §14 recommendation ran without it, and the kit is unchanged to within solver noise (S2 0.0121, S9 0.0320, S15 0.0717, S26 0.0252). The geodesic disc is a `binary_dilation` in C for every surface without a two-sided weak set; the disc is cached between the plate stage and the order |
| thin plate, 130 faces | 1 410 s | 483 s | forked workers, three by default (`--jobs`), largest faces first; BLAS threads pinned to one per process, without which three workers were eleven times *slower* than one (S15: 29 s → 336 s → 14 s) |
| **plane-only bake** (`--no-tps`) | ~700 s | **74 s** | |
| **full bake** | 2 109 s | **556 s** | |

Where the 74 s goes now: runs, rims, components, patches and merge ~16 s; the domain pass ~40 s, of which the remaining
Python is the two-sided closure walk for masked objects; the order 9 s. Peak memory 4.5 GB (was 10 GB). The sunflower
field's plane-only bake is 27 s.

## 21. Correction to §17, and the three items (staircase, segmentation, S9)

**§17 was wrong about the sunflower staircase.** It said the steps were in neither arm's far field. They are in the adopted
arm's field, and the gamma panel hid them: beside the big head (id 1, rows 179–389, cols 313–407; the 6 287 band texels to
its right) the adopted arm fills 0.30–0.43 — leaves, extended sideways into the sky — with 56 row-to-row jumps over a step
in 210 rows, 33 of them over three steps, the largest 77 steps. The per-line law fills the same texels with 0.009, the sky,
for the upper two thirds and foliage only near the bottom, 33 jumps. The staircase in the render is the reveal width
stepping row by row with those facet depths. So on this picture the adopted sheets are *worse* than the app's law behind the
big head, and it is the §15 problem in its plainest form: unmasked leaves treated as background reach the head's hole
through its stem's band and, being nearer than the sky, win. The per-line law escapes it by its axis arbitration (the row
through the head meets sky on the far side), not by a principle. Item 2 therefore folds into item 3: the automatic
segmentation (S28's SAM pipeline, `--auto`) is the test, on the sunflowers, the troll, starwatcher and S9.

**S9's 3 cm is the same thing on the kit.** The scene is three quads at different depths before a brick wall on a checker
floor. Behind the red quad the truth is the wall; the sheets fill 26 986 texels with the middle quad's plane (0.2739,
error 0.064 m) because the quad, unmasked, is a background surface that continues. The per-line law fills the wall. The
kit has no object mask for S9, so the automatic segmentation is tried there too, where truth can score it.

## 22. Items 2–4: the things/surfaces classifier, what it fixes, where it is wrong, and what was falsified on the way

**The question behind all three items.** The adopted arm (§18) knows two kinds of visible material: masked objects (two-sided:
their sheets continue behind another object only where a march across that object exits onto the sheet's own component)
and everything else, which is background and continues one-sidedly into any hole it reaches. The staircase beside the big
sunflower head (§21), S9's 3 cm (an unmasked quad extended as background) and the "segmentation completeness" item are one
question: which visible units are bounded THINGS and which are SURFACES, when the mask is partial or absent.

**The classifier (opt-in, `--things`).** Every visible unit — a mask segment where there is one, a join-law component of the
depth map otherwise — is a thing iff, for some neighbouring unit whose shared boundary is at least the unit's median shared
boundary, the boundary pairs where this unit is nearer by more than the tolerance outnumber those where it is farther, AND
the unit's median disparity is nearer than the neighbour's by more than the larger of the two median tolerances. Things get
ids and are two-sided; surfaces become background. No constant; the tolerance is the app's `tolAt`. SAM 2.1's automatic
mode was run on every picture (`--auto --n 0`, S28's constants) and gives 12 (vermeer), 16 (troll), 32 (starwatcher),
91 (sunflowers) and 205 (S9) segments, with the sky, the ground plain and single bricks among them and 26 % of the sunflower
picture unlabelled; the classifier is what turns that into an object map.

**Results (plane-only unless noted; stop arm; jumps v (length) h (length); kit = band depth error vs the first hidden layer).**

| test | adopted §18 | + classifier | verdict from the buffer |
|---|---|---|---|
| S2 | 0.0121 m | **0.0000 m** | right |
| S9 (no mask) | 0.0320 m | **0.0000 m** | right; the auto SAM mask alone, no classifier, also gives 0.0000 |
| S26 | 0.0252 m | 0.0281 m | slightly worse |
| S15 | 0.0717 m | **8.55 m** | wrong: the tree (trunks + canopy, one unit of 240 k px) is a thing, so the canopy may not fill behind its own trunk; the sky does |
| vermeer, 9-click mask | v 3 340 (26 180) h 55 526 (153 620) | v 3 339 (26 176) h 55 526 (153 617) | identical in effect (309 things, 301 of them depth-only specks) |
| vermeer, auto mask | — | v 360 (6 901) h 508 (39 933) | **wrong: the floor is lost** — behind the legs rows 920/960/1000 read 0.008 (the wall) instead of 0.024/0.066/0.105 |
| troll, 13-click | v 46 683 (380 291) h 25 246 (348 877) | v 1 961 (36 975) h 30 565 (108 828) | **wrong: x-ray** — the band behind the troll is the deepest gap between the trees (depth ≈ 0), not the forest |
| troll, auto | — | v 5 521 (95 706) h 8 583 (101 267) | same x-ray |
| starwatcher, no mask | v 42 701 (241 932) h 3 975 (108 099) | identical | 17 things, none touching the band |
| starwatcher, auto | — | v 2 232 (48 897) h 1 161 (21 262) | right: the striped ramp behind the figure's head and lamp in the adopted arm is gone, the band is a smooth wash (`s35/star_things_p45.png`) |
| sunflowers, 9-click (geo) | v 26 886 (447 679) h 19 975 (437 808) | — | beside the big head: fill 0.28/0.40/0.42 (p10/50/90), 0 of 211 rows sky, 60 row jumps — the staircase |
| sunflowers, auto, no classifier | v 15 015 (327 626) h 14 854 (359 509) | — | 0 of 211 rows sky, 43 jumps: the unlabelled 26 % (leaves) still fills as background |
| sunflowers, auto + classifier | — | **v 1 349 (24 540) h 1 856 (15 443)** | 197 of 211 rows sky, 0 jumps; the lower band is the distant field (0.15): the plausible layering |

Renders through the app at p45 (per-line law / adopted sheets / sheets + classifier): `s35/troll_things_p45.png` (the x-ray reads clean in a still — the depth is wrong, not the wash), `s35/room_things_p45.png` and `s35/room_things2_p45.png` (the staircase gone), `s35/vermeer_things_p45.png`, `s35/star_things_p45.png`.
Buffer figures: `s35/look_vermeer_ta2.png` (vermeer auto: one wall sheet, no floor), `s35/look_troll_t13.png` (troll: the far field
inside the troll is black = the deep gap), `s35/look_room_ta.png` and `s35/look_room_nt.png` (sunflowers: sky + field vs
leaves), `s35/floor_look_ta.png`.

**Why the two failures are the same failure.** The classifier's model is "things never continue behind other things unless
the march across closes on their own component". Behind the troll the marches of every tree exit onto *another* tree
(208 of 407 depth components are things), so every tree is open, a hedge, and the only fitted sheet that reaches is the deep
background: an x-ray to the deepest surface. Behind the sunflower head the same x-ray gives the sky and the distant field,
which is right there because the sunflowers are sparse before a real background; a forest IS the background. A closure
that would tell the two apart without a constant (a tree exits onto "similar" depth, a leaf onto the sky) was not found: the
join tolerance is one visible step, which no two trees satisfy, and anything looser is a number.

**The floor vote (vermeer auto) is a flaw in the local test, recorded, not fixed.** The floor (depth component of 174 759 px,
median depth 0.167) was voted a thing by a SAM piece of the floor itself (20 605 px, 0.069): of their 470 boundary pairs, 468
are continuous, 2 have the floor nearer, 0 farther; "nearer pairs outnumber farther pairs" passes on 2 : 0. Requiring the
majority of ALL pairs would fail the milkmaid against the same floor (643 nearer of 2 282; the rest continuous at her hem,
where DA3 blends her into the floor). The honest test is the unit's plane against the neighbour's boundary texels, not
pairwise depths; not built, because the troll and S15 failures are structural and would remain.

**Falsified on the way (all removed from the code, rule 7).** All were aimed at S15's canopy behind its own trunk.
1. *Closure against the same THING instead of the same component*, *closed on ANY axis*, and *same-id demotion lifted when
   two-sided* (the three together): S15 8.5 → 3.29 m, still wrong; and — the confound only found by a clean A/B — they broke
   vermeer WITHOUT the classifier: 9-click v jumps 3 340 → 16 788 (length 26 180 → 665 559), the table's own folds filling
   behind the table (`look_vermeer_t9.png`). With the closure restored the 9-click run is bit-identical to `s35_plane`.
2. *Self-occlusion stop* (a same-id march stops at the first own-id texel behind the band texel): the milkmaid's band filled
   with her dress, the troll's with his skin (`look_vermeer_ta.png`, `look_troll_ta.png`): the foreground clone as
   background, the one thing the brief forbids.
3. *Self-occlusion band* (band texels revealed by a rim of their own thing keep the thing's own sheets, and such a march
   closes on the first own-id texel behind): S15 3.64 m; vermeer 9-click v 3 339 → 11 789 (length 1 195 418); vermeer auto
   360 → 6 364 (901 438); troll 13-click 1 961 → 18 153.
After the removals the default arm reproduces §18 exactly (S15 0.0717 m, v 5 183 (768 829) h 4 360 (823 833); vermeer
9-click bit-identical).

**App-side finding recorded here.** Starwatcher's dump was degenerate (effective quantum = grid): S10c's gate (`moebius.js`
~14572–14594) applies the visible-step floor only when the median second difference σ > 0, and on a sky-heavy DA3 map σ = 0.
`FLAGS=_visStep=1` forces the floor (`starwatcher_vs`); the gate wants a case for σ = 0 in the app. Not changed.

**Where this leaves items 2–4.**
- Item 4 (S9): solved by the object map — the automatic SAM mask alone gives 0.0000 m under the adopted arm; the classifier
  is not needed for it.
- Item 2 (staircase): needs the classifier or its principle (the unlabelled leaves must be things); the adopted arm with the
  auto mask keeps the staircase (43 jumps).
- Item 3 (completeness): the classifier is the only candidate and it is wrong in clutter (troll) and for a thing before its
  own body (S15). It stays opt-in. The decision — classifier off (troll right, sunflowers staircase), on (sunflowers right,
  troll x-ray), or a per-picture switch in the panel — is the user's; the numbers and buffers above are the case.

## 23. Where the colours come from: the bleeding and the streaks measured (user question, 2026-09-17)

**The question.** Streaking and bleeding of the foreground into the disocclusion gap; the hypothesis was that the depth does
not capture the outline exactly, so a sliver of foreground RGB counts as background and is sampled into the fill.

**How the app colours the band** (`moebius.js` 15995–16059). For every carrier texel with a far side, the colour is the mean
of the SOURCE colour over the rim window of the rim the far side came from: `winMean(j, w)` = `w` texels from the rim texel
`j` outward along the axis. `w` is the depth fit's window, `min(len, g+1)` (699): the gap plus one texel, so for the band
texels next to the silhouette `w` is 1–2. Then the band's outer ring holds those colours as Dirichlet values and the interior
is a harmonic membrane. The inner side of that ring runs along the occluder's silhouette (the ring was moved there on purpose,
16021–16024), so the whole band is bounded on one side by colours read from the one or two texels touching the silhouette.

**Measurement 1 — the rim texel** (`s35/bleed/rimcolor.py`; the app's own `farRimJ`/`farRimW` from the probe dumps, four
pictures + the troll). Of rim windows with a colour contrast between occluder and far run:

| picture | window w (median) | rim texel closer to the OCCLUDER colour than to its own run | occluder-coloured leading texels (mean / p90) | colour edge vs depth edge |
|---|---|---|---|---|
| troll | 2 | 62 % | 1.7 / 5 | on the depth edge (median); inside the far run in 35–39 % |
| vermeer | 2 | 52–58 % | 1.2 / 3–4 | median on the edge; inside in 35–42 % |
| sunflowers | 2 | 59 % | 1.5–1.9 / 5–6 | median on the edge; inside in 48–53 % |
| silverwarrior | 2 | 52 % | 1.3–1.6 / 5 | median on the edge; inside in 30–33 % |
| starwatcher | 2 | 28 % | 0.5–0.7 / 1–2 | inside in 21–24 % |

So the hypothesis is half right: the depth edge sits ON the colour edge in the median (offset −0.5 texel: the step is between
the last occluder texel and the first far texel), but the first far texel is a blend or an outline texel in more than half
of the rims, and the colour edge lies one or more texels inside the far run in a third to a half of them (soft outlines, DA3's
edge a texel inside the painted one). With a window of two texels, that texel IS the fill colour.

**Measurement 2 (SUPERSEDED by §24 — read that first)** — the fill itself (`s35/bleed/ringcontam.py`, on `plateColor.u8`): the occluder's share of the fill colour
(0 = the far surface's own colour, 1 = the occluder edge colour), on the inner ring and 6 / 15 texels into the band:

| picture | inner ring | 6 texels in | 15 texels in |
|---|---|---|---|
| troll | 0.20 | 0.31 | 0.30 |
| vermeer | 0.16 | 0.28 | 0.36 |
| sunflowers | 0.39 | 0.37 | 0.35 |
| silverwarrior | 0.05 | 0.46 | 0.55 |
| starwatcher | −0.30 | −0.06 | 0.01 |

The contamination does not fade into the band: the membrane carries the ring's blend across it. Crops
(`s35/bleed/crop_vermeer_shoulder.png`, `crop_vermeer_hip.png`, `crop_troll_arm.png`): a dotted dark or blue rim along the
silhouette (each ring texel its own line's 2-texel mean), a halo inward, then a smooth gradient between that halo and the
clean outer ring.

**Two issues, one cause each.**
- *Bleeding* = the colour window. It is the depth fit's window reused for colour; next to the silhouette it is the blended
  texel itself. Depth misregistration adds to it on a third of the rims but is not the root.
- *Streaking* = two things. Along the silhouette, the ring is a per-line quantity (neighbouring rows read different 2-texel
  means: the dotted rim in the crops), and the membrane's gradient from a noisy boundary reads as streaks. Across the band,
  the per-line geometry's row-to-row depth jumps stretch the fill along the lines (the S33/S34 seams); the sheets remove
  those, which is why the sheet renders look smoother than the per-line ones, but their colour is still the app's per-line
  fill (the harness injects only the geometry), so the halo and the surface mismatch remain in them: the per-line far side and
  the sheet's differ by more than 0.05 on 40–85 % of the band, so in the sunflower render the band behind the head is
  leaf-grey where the sheet says sky. That mismatch is the harness, not a law.
- The "cleaner washes before" are consistent with this: the code's own comment records the ring being moved onto the
  silhouette's outline texels (the box on S9 had gone floor-grey with the ring one texel further out), and the g+1 window
  came with the thin-evidence rule; both put the fill's boundary values on the blended texels.

**Remedy, previewed offline** (`s35/bleed/remedy.py`), occluder share of the boundary colour, median (mean):

| picture | app window, w = g+1 | median of the whole far run | run median after skipping the blended leading texels |
|---|---|---|---|
| troll | 0.48 (0.48) / 0.42 (0.43) | 0.03 (0.07) / 0.06 (0.11) | 0.01 (0.04) / 0.04 (0.08) |
| vermeer | 0.24 (0.32) / 0.06 (0.21) | 0.02 (0.05) / −0.01 (0.07) | 0.01 (0.03) / −0.01 (0.05) |
| sunflowers | 0.38 (0.46) / 0.38 (0.48) | 0.03 (0.10) / 0.04 (0.16) | 0.02 (0.08) / 0.02 (0.14) |
| silverwarrior | 0.28 (0.35) / 0.06 (0.26) | 0.02 (0.06) / 0.01 (0.04) | 0.01 (0.04) / 0.00 (0.02) |

(two slots = the two sides.) The blend skip is constant-free: a leading texel is skipped while it lies toward the occluder
colour and farther from the run's median than the run's own colour spread (MAD); it skips 1 texel in the median, 1.4–2.1 on
average. The run median alone takes out nine tenths of the contamination; the skip takes out most of the rest.

**Plan.**
1. In the app's fill: colour window = the far RUN, not the fit window: the run's median colour after the blend skip, as
   Dirichlet values; a run shorter than four texels has no clean colour and contributes no boundary value (the membrane
   takes the neighbours'). Measured by the tables above before/after, plus the ring's texel-to-texel colour variance along
   the silhouette (the streak number) and the kit's hidden-layer colour where the scenes have one.
2. In the sheet model: the colour of a band texel comes from the SHEET that owns it, from that sheet's own visible texels away
   from its silhouette (the same skip), as a colour field per sheet, so colour and geometry are one law and there is no
   per-line ring at all. This is item 1's atlas per sheet.
3. The render harness injects the sheets' colour with their geometry, so the screengrabs show the sheets' fill, not the
   per-line one under sheet geometry.


## 24. The colour window tested in the app and FALSIFIED as the fix (S35 §23 step 1, 2026-09-17)

§23's plan was to replace the band's colour window (the depth fit's window, the gap plus one texel) with the far run's own
colour past a blend skip. Three arms were built in `moebius.js` behind `window._colorWindow` and baked on five pictures
(troll, vermeer, sunflowers, silverwarrior, starwatcher; ten probe bakes, `harness/shots/a257probe/c_<picture>_{before,after,shift}`):

- **fit** — the law as it stands: the mean over `w = min(len, g+1)` texels from the rim texel;
- **run** — the median over the whole far run, after skipping leading texels that are blends of the occluder
  (a texel is skipped while it lies toward the occluder's edge colour and farther from the run's median than the run's own
  colour spread, the median absolute deviation scaled by 1.4826; no picture constant);
- **shift** — the same skip, then the median over the fit window's width, keeping the colour local to the texel's own part
  of the run.

**The result: the three are visually indistinguishable** (`s35/bleed/arms_vermeer_hip.png`, `s35/bleed/arms_troll_arm.png`;
colour, depth, then the three fills). The measurements say the same:

| picture | occluder share at the silhouette: fit → run | seam vs the visible far surface: fit → run → shift | streaks across the lines |
|---|---|---|---|
| troll | +0.76 → +1.00 | — | unchanged |
| vermeer | +0.25 → +0.12 | 82 → 100 → 103 | 1.49 → 1.60 → 1.60 |
| sunflowers | +0.37 → +0.32 | — | unchanged |
| silverwarrior | +0.74 → +0.67 | — | unchanged |
| starwatcher | +0.29 → +0.20 | — | unchanged |

**Why §23's diagnosis was half wrong.** The fit window is `g+1`, where `g` is the gap from the band texel to its rim. It is
short ONLY for band texels within a few texels of their rim — 2–4 % of the band. For the rest (vermeer: 22 045 of 26 000
sampled at `g > 40`) the old window already spans the whole run, so fit and run agree to 0.01 in occluder share. §23's
"occluder share 0.2–0.5 across the band" compared a fill that is legitimately a long average of the run against a LOCAL
reference eight texels past the rim: it measured non-locality, not contamination. The rim-texel measurement in §23 stands
(the first far texel is occluder-coloured in 52–62 % of rims); it simply does not drive the fill.

**What the buffer says instead** (trace of the troll's arm band, `s35/bleed/verify_impl.py` and the trace in the log):
- band texel (252,524), source colour (50,52,53): its far side is a rim **400 texels away**, run length 55, colour
  (131,130,108) — the pale wash over the arm. The colour is a faithful sample of the surface the GEOMETRY chose;
- band texel (214,491): its two rims have run lengths **1 and 2**. There is no clean colour to read at all — no window rule
  can help, because the only evidence is a blend;
- 25–29 % of rims on the troll have a run shorter than four texels.

So the bleeding the eye sees at a silhouette is the far-side CHOICE (which surface is continued, and from how far away),
and the streaks are that choice changing from line to line — the per-line law's own seams, the thing the sheets remove.
The colour stage is downstream of both and faithfully reports them.

**Removed (rule 7).** `bgRunColor`, the `_colorWindow` arms, the run-length export (`farRimL`) and an untested `_colorTrust`
rule (a rim whose blend skip cleared no texel gives no Dirichlet value and becomes a membrane unknown) are removed from
`moebius.js`; the app is byte-identical to before this test. The instruments stay in `s35/bleed/` (`score3.py` by gap,
`score4.py` at the silhouette, `crops.py`, `verify_impl.py`) and the ten probe dumps stay on disk.

**Where this leaves the colour.** Step 2 of the §23 plan is now the whole of it: the colour of a band texel comes from the
SHEET that owns it, sampled from that sheet's own visible texels away from its silhouette. That fixes both causes at once —
one surface per band region instead of a per-line choice, and no per-line ring — and it is the same construction as the
per-sheet atlas (item 1). Step 3 (the render harness injecting the sheets' colour with their geometry) stands: until it is
done, every sheet screengrab carries the per-line fill over sheet geometry.

## 25. Colour folded into the sheet model (§23 step 2 and step 3, 2026-09-17)

§24 left the colour with one cause to fix and it is upstream: the fill follows whatever far side the per-line law chose, so a
band texel can be washed with a surface 400 texels away, and neighbouring lines disagree. The answer is the same object as
the per-sheet atlas: **the colour of a band texel is its owning SHEET's own colour, continued.** Built in `sheets.py`
behind `--color`, with `--rgb` for the source image.

**The construction.**
1. The colour's unit is the **visible surface** (the join-law component), not the planar patch the depth fit uses. Colour
   does not obey planarity: a wall split into facets is one painted surface. (Grouping by patch first left 88 % of vermeer's
   band with nothing to extend from, and blotched it — `s35/bleed/` has that version's render.)
2. Each band texel belongs to the surface of the sheet that owns it (`who`), and its colour is the **harmonic extension**
   of that surface's own visible colour over the texels it owns (Perez, Gangnet & Blake 2003), solved per surface, so no two
   surfaces ever mix and there is no per-line ring anywhere.
3. The extension may not be anchored on the source's **anti-aliased fringe**: the surface's texels at a silhouette are
   mixtures of it and the occluder (§23: the first far texel is occluder-coloured in 52–62 % of rims). The fringe's width is
   **measured on the picture**, not assumed — at every step edge, the number of leading texels on the far side closer to the
   near side's colour than to the far side's own colour, median over that picture's edges. It comes out 1 texel on vermeer,
   the troll and the sunflowers, 0 on starwatcher. Those texels join the unknowns and keep their source colour in the output
   (they are visible at rest; only band texels are written).
4. Where the owning surface is **not adjacent** to the texels it owns — ownership is by depth, not adjacency, and on S9 that
   is every band texel — the extension has nothing to propagate from. Those texels take the surface's own **colour model**:
   a plane per channel over its clean visible texels, clipped to the range that surface actually shows, the same
   construction the depth uses, and still coupled to the Laplacian so the field is smoothed rather than stamped.
5. `sheet_render.js` now takes `COLORPNG=` and replaces the plate's colour map with the sheets' own (step 3). Until this,
   every sheet screengrab carried the per-line fill over sheet geometry.

**Scored against the kit's hidden-layer colour** (`scope_gt.npz` `rgb`, the first hidden layer in the band; |fill − truth|
summed over channels, median):

| scene | sheets' colour | the app's per-line fill | the source itself (a clone) |
|---|---|---|---|
| S15 (tree, sky) | **53.8** | 170.0 | 76.0 |
| S9 (quads, wall) | **146.0** | 177.0 | 237.0 |
| S2 | 91.8 | **86.0** | 150.0 |
| S26 (quads) | 91.0 | **56.0** | 101.0 |

**What that says.** The colour now follows the geometry exactly, so its error tracks the model's OWNERSHIP error. Where the
sheets' depth is much better than the per-line law, the colour is much better (S15, a third of the app's error; S9). Where
the sheet model picks the wrong surface — S9's unmasked quad (§21), S26's quads — the colour is the wrong surface's colour,
and the app's per-line read of a locally chosen run wins. The colour law adds no error of its own: it is the same evidence,
grouped by surface instead of by line.

Measured on the pictures too (`s35/bleed/score5.py`): the fill's texel-to-texel variation inside the band drops
(vermeer mean |dC| 1.54 → 1.06 vertical, sunflowers 3.96 → 3.30) — fewer streaks, as intended. The "fill within the noise of
its own source colour" count rises (vermeer 0.2 → 8.1 %, troll 7.2 → 32 %), but that instrument is not a clone detector on
a dark picture: a band correctly filled with dark forest lands within the noise of the dark occluder beside it. Recorded as
measured and not used as a verdict.

**Renders through the app at p45** (`s35/bleed/`, three panels: the per-line law, sheet geometry with the per-line colour,
sheet geometry with the sheets' colour): on **vermeer** the band behind the milkmaid becomes a smooth wall wash and the
banding at her right edge goes (`vermeer_color2_p45.png`); on the **sunflowers** colour and geometry now agree, which makes
the staircase read as foliage instead of a pale card (`room_color2_p45.png`) — the geometry is the §22 question, not the
colour's. on the **troll** the band is dark forest instead of a pale grey card (`troll_color_p45.png`); on **starwatcher** the striped
ramp behind the figure keeps its stripes under the sheets' colour, so what remains there is geometry, not colour
(`star_color_p45.png`). Buffer crops of the two fills side by side: `fillcmp_vermeer_hip.png`,
`fillcmp_vermeer_shoulder.png`.

**The sunflowers with the §22 classifier AND the sheets' colour** (`room_things_color_p45.png`) is the best result on that
picture so far: the staircase is gone (the classifier's geometry) and the band beside the big head is a smooth sky wash (the
sheets' colour), where the per-line law puts a white card and the classifier with the old per-line colour puts a cream one.
It is the first picture where both halves of the model are right at once, and it is the case for settling §22's decision
in favour of the classifier for pictures of this kind.

**Falsified on the way (removed, rule 7).** The fallback for non-adjacent owners was first the surface's **nearest clean
sample** instead of its colour model; measured against the kit it is worse (S9 146 → 181, S26 91 → 96, S15 53.8 → 53.3,
S2 unchanged), so the colour model stays.

**Open.** (i) the app itself is untouched: this is the offline prototype plus the render harness, and moving it into the app
is the atlas work (item 1); (ii) S26 and S2 say the wash still loses to a locally chosen run where ownership is wrong, which
is the §22 classifier question again; (iii) plate 2 has no sheet colour yet.

## 26. Starwatcher's streaking diagnosed: the figure has no object mask, so his own surface fills his band

The user's read of the §25 shots: "starwatcher streaking is terrible". Looking at the buffer behind the figure
(`s35/bleed/star_figure.png`: colour, depth, band, far field, owner, sheet colour), the far field INSIDE his footprint is
his own shape — a grey silhouette of the hood and the pack — sitting three to four visible steps behind his own depth
(column 300: own depth 0.337, far field 0.304–0.331). A surface a few steps behind him wins the layered order over the sky,
so the band renders as a card standing just behind him, and its facets step from row to row: the stripes.

**The cause is the segmentation, not the sheet law.** That arm ran with no object mask. The figure's feet meet the ground and
DA3 joins them, so the figure and the ground are ONE visible component; its sheet therefore continues the figure's own body
behind the figure. It is the depth twin of the foreground-clone rule we forbid for colour.

**With the figure treated as an object it goes away** (`--things` over the automatic SAM mask, which classifies him a thing):

| starwatcher, p45 | vertical jumps (length) | horizontal jumps | vertical kinks | horizontal kinks |
|---|---|---|---|---|
| the per-line law | 12 308 (199 331) | 33 531 (478 201) | 15 147 | 44 110 |
| sheets, no mask | 42 701 (241 932) | 3 975 (108 099) | 13 437 | 5 531 |
| sheets + classifier | **2 232 (48 897)** | **1 161 (21 262)** | **2 550** | **2 079** |

The render agrees (`s35/bleed/star_fix_p45.png`): the striped card behind the figure is replaced by a smooth sky wash. Note
the automatic SAM mask alone does not do it — it labels the sky and leaves the figure unlabelled — so the classifier's
reading of which units are things is what supplies the figure.

**This moves the §22 decision.** The classifier is now shown to fix three pictures (S9, the sunflowers' staircase,
starwatcher's card) and the argument against it is one picture (the troll's x-ray) plus vermeer under the automatic mask
(the floor voted a thing on two boundary pairs) and S15 (a canopy behind its own trunk). The troll's x-ray is the blocker
worth attacking next: it is one rule — a thing whose marches all exit onto OTHER things has no fitted sheet and hedges to
the deepest surface — and every failing case is of that shape.

## 27. Line work split off the foreground: segmentation-consistent depth (user request, 2026-09-17)

**The observation.** On starwatcher the staff does not come through whole: at p45 the lantern's glow and the top of the loop
stay on the background while the figure moves, and a ghost of the staff's outline is left on the plate
(`s35/bleed/star_staff_zoom.png`, first two panels). Strong line work splitting off the foreground.

**Why.** The depth map loses thin structure: the shaft above the hand and the lantern's loop sit at the SKY's depth
(`s35/bleed/star_repair.png`, "depth before"), so they belong to the plate and are revealed like sky. The segmentation
knows better: SAM's sky segment excludes the staff exactly, loop and all.

**The rule** (`s35/depth_repair.py`, a preprocessing step on the 16-bit depth, before any bake; no constant):
1. The picture's far limit is its farthest real SURFACE: among SAM segments that are the majority of the unlabelled-or-own
   material at their own depth (a surface, not a fragment such as a rock on the plain), the one with the smallest median
   depth. Only that surface can be the background a thin thing is lost against — nothing opaque can sit AT the sky's depth in
   front of the sky, whereas a loaf on a table legitimately sits at the table's depth (vermeer: 14 536 texels of bread and
   basket would otherwise have moved).
2. Its HALO first: SAM's segment stops a texel or two short of a silhouette; unlabelled texels at the surface's depth whose
   colour is closer to the surface's median than to the nearest nearer texel's colour are the surface (starwatcher: 8 468
   such texels ring the figure, with the staff's ink inside the ring).
3. Then a 4-connected component of the remaining unlabelled texels at the surface's depth whose outer boundary is MOSTLY
   that surface (enclosed by it) and which touches material nearer than it by more than the visible step is a thin part of
   that nearer thing whose depth failed. Each such texel takes the depth of the nearest nearer texel.

**What it touches.** Starwatcher 1 209 texels (the staff's shaft and loop, the lantern's glow, the crystals' edges, the
craft's edge — `star_repair_map.png`); the sunflowers 1 813 (petal tips and flower edges against the sky —
`room_repair_map.png`); vermeer 197 (against the wall); the troll 0. Three earlier versions of the rule were measured and
rejected on the way: without the enclosure test a small segment at the sky's depth made the whole sky a candidate
(312 138 texels); without the unlabelled-only restriction other segments' own texels were candidates (230 172); without the
far-limit restriction the horizon fragments repaired 26 000 plain texels and the table moved its bread.

**Result on starwatcher** (baked from the repaired depth, sheets + classifier + sheet colour; `star_staff_zoom.png`, third
panel): the lantern's glow and the loop move with the figure; the ghost outline on the plate is gone. The sheet numbers are
unchanged to within noise (vertical jumps 2 232 → 2 245, horizontal 1 161 → 1 178): this is a foreground fix, not a band one.
What remains is a pale disc on the plate where the glow was — the band behind the lantern now takes the surrounding sky's
colour, and that sky is the glow's own halo. A colour matter, small, recorded.

**Where it lives.** Offline only (a depth PNG in, a depth PNG out), nothing in the app changed, as asked. In the app it
belongs at depth import after SAM, before the bake; the segment it needs is the one the classifier already calls the
farthest surface.

**Addendum: the black outline baked into the sky.** With the thin parts repaired, a dark rim still ran along the wash
behind the figure (`s35/bleed/star_outline_zoom.png`, middle): the figure's ink OUTLINE, one to two texels wide, which
SAM excludes from the sky but the depth leaves at the sky's depth. The rule skipped it because a ring hugging the figure has
the figure on one side and fails the enclosure test by half. The contact with the nearer thing it hangs off does not count
against enclosure (it is that thing's edge); with that change the rule takes the outline too: starwatcher 1 209 → 6 097
texels (the figure's contour, the crystals' outer edges, the horizon line — `star_repair_map2.png`), sunflowers 1 813 →
2 911, vermeer 197 → 278, troll 0. The rim goes (`star_outline_zoom2.png`, middle). What was left after that is the
anti-aliased sky-side texels the ink darkened, which the colour stage already solves for as the blend fringe and then left
untouched; it now writes the surface's own colour into them as well (at rest that changes a one-texel ring of mixed texels
on the surface side of each silhouette). `star_outline_zoom2.png`, right: the rim is gone; a very faint trace of the shaft
remains in the sky where the ink's blur reached farther than the one-texel fringe. The sheet numbers stay within noise
(vertical jumps 2 245 → 2 249). Nothing in the app changed.

## 28. The troll's x-ray, five attempts (user: "go after the troll, go 5 times", 2026-09-18)

**The problem.** With the classifier the troll is a thing and his band should be the forest behind him. It is the deep gap
instead: 91.8 % of the band inside his footprint is filled below 0.05 (the sky seen between the trees), 6.4 % with forest
(0.12–0.45). The reason is the §18 closure test: the forest is hundreds of small components and things, so a forest sheet's
march across the troll never exits onto its own component — every forest sheet is a hedge, while the gap, a far surface with
no closure test, is fitted and wins. Instruments: `s35/bleed/trollfill.py` (shares of gap/forest in the troll's band),
`headfill.py` (rows of sky right of the big sunflower head, the staircase picture), the vermeer floor rows (§14), the 9-click
vermeer and automatic starwatcher vertical jumps, the kit's S15/S9/S2/S26 truth medians. All five attempts are one switch,
`--closure`, in `sheets.py`; the default (`comp`, §18) is untouched.

| arm | troll gap / forest % | sunflowers rows sky (of 211) | S15 truth m | vermeer v jumps | starwatcher v jumps |
|---|---|---|---|---|---|
| comp + classifier (baseline, same flags) | 91.8 / 6.4 | 197 (v 1 349) | 8.55 | 3 339 | 2 249 |
| 1 closed on own component OR any thing (skip what is nearer than the rim) | 2.4 / 85.6 | 0 | 8.40 | 31 598 | — |
| 2 = 1, a texel on any closed march is fitted, unreached texels weak | 32.4 / 54.4 | 4 | 8.44 | 8 923 | 5 922 |
| 3 = 1 + any-closed-fits, march counts only if its band texel is nearer than the rim, same-id lift on any closed march, reach ≤ thing's box | 1.3 / 92.6 | 0 | 3.27 | 36 754 | 15 648 |
| 4 = 3, same-id lift only where the march closed on the SAME thing | 2.3 / 85.7 | 0 | 1.009 | 35 200 | 14 921 |
| 5 = 4, box bound replaced by the EXPOSURE bound | 2.5 / 89.6 | 0 | 0.949 | 37 429 | 19 522 |
| diagnostic after 5: closed on another thing only at the sheet's own depth | 26.8 / 49.0 | 0 | 2.36 | 34 754 | 21 609 |

S9 (0.000 m), S2 (0.000) and S26 (0.028) are unchanged in every arm. Baselines re-run with the chains' exact flags
(`s35_a0`): sunflowers 197/211, starwatcher 2 249, vermeer 3 339 — the regressions are the closure and nothing else.

**What the five did.** Attempt 1 changes the occluder from "the band texel's id" to "whatever is nearer than the sheet's rim"
and closes a march that exits onto ANY thing, not only the sheet's own component: a forest wall continues behind the troll.
It fixes the troll at once and breaks the other three pictures at once. Attempts 2–4 are repairs of its side effects that
keep the troll: a texel on any closed march is fitted (2; the unreached-texels-weak part cost the troll and was dropped), a
march counts only when its band texel is nearer than the sheet's rim so a nearer plane is not continued behind a farther
object (3), and the same-id demotion (an object does not fill its own band) is lifted where the march closed on the object's
own far side (3 on any closure — the petals filled behind the petals; 4 on the same thing only), which is what brings S15's
canopy from 8.55 m to 1.0 m (the canopy beyond its own trunk, the kit's one self-occlusion). Attempt 5 replaces attempt 3's
bound "a thing's sheet reaches no farther than the thing's bounding box" by a physical one: the app's parallax scale
(`moebius.js` `bgConeSlopePerPx`, k = 400·pw/1920 texels per depth unit at the envelope's edge, the geometric derivation
gives 396) says a band texel j texels from the silhouette is uncovered for a far side at gap g only while j ≤ k·g, so a
thing's march keeps only that exposed prefix. Same units on both sides, scales with the picture. It held the troll and the
kit (S15 1.009 → 0.949 m) and did not touch the three regressions.

**Why not: the mechanism, read off the buffer** (`s35/bleed/owners.py`; figures `troll5_vermeer_a4.png`,
`troll5_vermeer_a5.png`, `troll5_star_a5.png`). Under `comp` the milkmaid's band is 92.8 % the wall (sheet 2, 0.008) and
two floor sheets; under attempt 5 the wall keeps 54.6 % and the rest goes to forty sheets of the things around and on her —
a part of her own group at 0.413 (24 %, filling at 0.353), the loaf's segment at 0.349 (4.7 %), and so on, each a THING whose
march across her exited onto some other thing (the foot-warmer, the table's objects) and so counted as closed. Starwatcher:
the horizon sheet drops from 59 % to 15 % of the figure's band and five sheets of things at 0.05–0.31 take 8–16 % each. The
sunflowers: the band right of the big head belongs to a nearer leaf (0.627); under `comp` it is sky (72 % from the two sky
sheets at 0.009), under attempt 5 it is 43 sheets of petals and leaves at 0.10–0.45 whose rims lie up to 200 rows away
(one leaf sheet with its rim at 0.097 owns 26 % of it, filled at 0.246). The exposure bound cannot stop these: their
occluders are far nearer than they are (0.627 against 0.097 is 111 exposed texels at k = 210), so the exposed prefix is
long; it only cut sheets nearly at their occluder's depth. The diagnostic variant — a march closes on another thing only
when that thing sits within the sheet's own depth spread — halves the troll's fix (the foliage it exits onto is at every
depth from 0.12 to 0.45) and leaves the three pictures where they were (a petal closes on a petal at the same depth, a part
of the dress on another part). Falsified; removed.

**The finding.** "Closed when the far side is a thing" is the only rule of the five that continues the troll's forest, and
it is the same rule that continues a petal behind a petal, a leaf behind a leaf, and the milkmaid's parts behind the
milkmaid. Neither the depth map nor the segmentation, as the closure test reads them (one exit texel per march), separates
the two: the forest is a LAYER — many things at overlapping depths that together are nine tenths of what surrounds the troll
— and it continues because the layer is large; a petal is one small thing whose continuation beyond the head is nothing.
The untested candidate is that layer notion itself: things grouped into layers by adjacency and overlapping depth range,
closure and reach decided per layer with the layer's own extent. Not attempted within the five; recorded, not started.

**Per rule 7.** The intermediate forms (attempts 1–4 as separate switches, the box bound, the any-closure lift, the
unreached-weak rule) and the depth-ordered diagnostic are removed from `sheets.py`; what remains is `--closure layer`
(attempt 5's rule, complete) beside the adopted `comp`, so the troll's fix can be re-run but is not the default. The
code was re-run after the cleanup: S15 0.9490 m under `layer` and 8.5468 m under `comp`, byte-identical jump counts.

**Options** (the user's screen decides; screengrabs `s35/bleed/troll5_renders.png`, p45):
- A. Keep `comp` (§18) and make the classifier the default. Advantages: five pictures and the kit as measured in §22–§27;
  nothing new to integrate. Disadvantages: the troll's x-ray stays (his band is the gap between the trees), and S15's canopy
  stays at 8.5 m in the kit.
- B. Adopt `layer`. Advantages: the troll (gap 91.8 → 2.5 %) and S15 (8.55 → 0.95 m). Disadvantages: vermeer, starwatcher
  and the sunflowers break through the mechanism above (vertical jumps ×11, ×9, sky rows 197 → 0).
- A per-picture switch is not an option (zero per-image tuning).
- C. The layer grouping as a bounded research item after item 1. Advantages: it is the one statement that fits all five
  cases. Disadvantages: a new construction, unmeasured; the risk of another five attempts.
Recommendation: A now, item 1 proceeds; C only if the troll's kind of background (a porous layer in front of a deep gap)
matters enough to spend another sprint on.

## 29. Item C: the layer notion tested, with four new kit scenes (user: "do C… I'm wondering if we need some more synthetic data", 2026-09-18)

**Why synthetic data first.** §28 ended with the finding that no per-march exit test separates the troll's forest from a petal
behind a petal, and with only the eye at p45 as the truth for the sunflower side of the conflict. Four kit scenes now hold the
disputed configurations with exact truth (`truthkit/scenes.py`, `layer_scenes.png`): **L1** a dense leaf layer (300 discs of
radius 0.08 W at 0.5–0.7 W, nine tenths of the frame covered) before a far wall, a figure in front — the troll; **L4** the
same with 100 discs, the layer and the gap even; **L2** thin discs on stems (the sunflowers), a big near head, two leaves per
stem chaining the plants, before a ground plane and a sky-blue wall 4 W back; **L3** a figure before a brick wall with a table
and a cluster of small things beside her — the milkmaid. Each scene gets its rest render, its env45 truth, an object-id map
from its own truth (`truth_ids.py`: the first hit's THING primitive per texel, the kit's stand-in for SAM; the forest's leaves
left unlabelled as under the troll's click mask, so they are depth components), and the app's plane bake through the a257
probe. The step passed to `sheets.py` is the visible step the probe prints, as for S15.

**A kit artefact caught on the way** (`layer_L2_squash.png`). L2 was first built like S32, ground to 300 W. The app's depth
law then puts the whole plant field and the near ground within ten tolerances of one depth (d 0.482–0.491): the app's
per-row law scored 0.0002 m there and the sheets 0.32 m, because no plane can separate a head from the ground at that
resolution. That is the law's squash of the near field under a far outer limit, not a property of the sheets; the scene was
rebuilt with the sky as a far wall at 4 W (as in the picture, where the sky is the farthest surface, d 0.009) and the app's
own score on it is median 0.000 m, p90 0.49 m.

**Layer groupings: two forms, both falsified before the kit scored them.** (1) Things adjacent with overlapping p10–p90 depth
ranges, union-find: 202 of the troll's 211 things (836 k of 870 k texels) became one layer, 393 of the sunflowers' things
another. (2) Adjacent things whose depth difference is below either one's own step down to what lies behind it: still one
layer of 179 things on the troll. With the pictures' blurred depth every clump overlaps its neighbours and the chain runs
through the troll himself; with the kit's exact leaves (ranges of one texel) nothing chains at all. A layer is not a
depth-range object. Both removed (rule 7).

**What a layer is, then: the majority of an occluder's surroundings** (`--closure surround`). The forest continues behind
the troll because nine tenths of what surrounds him is forest; the petals do not continue behind the head because six tenths
of what surrounds the head is sky. Per occluder X: the far-side texels along the rim of X's band (X's own texels excluded,
texels nearer than their band neighbour excluded — they are in front of X), their median depth m(X). A thing's sheet is
fitted behind X when it is not nearer than m(X); nearer things are minority clutter and hedges there; own-component and
own-thing closure (§18) stay as the self-occlusion case; per-texel exposure trim from §28 kept. No grouping, no threshold
beyond the median. Measured:

| arm | troll gap / forest % | sunflowers sky rows | starwatcher v | vermeer v | S15 m | S9 / S2 / S26 m | L3 m | L2 m |
|---|---|---|---|---|---|---|---|---|
| comp + classifier (baseline) | 91.8 / 6.4 | 197 | 2 249 | 3 339 | 8.55 | 0.000 / 0.000 / 0.028 | 0.000 | 0.015 |
| layer (§28) | 2.5 / 89.6 | 0 | 19 522 | 37 429 | 0.95 | same | — | — |
| surround | 3.1 / 83.6 | 0 | 12 819 | 18 170 | 1.93 | same | 0.000 | 0.083 |
| surround + reach on things | — | — | — | — | 1.91 | — | 0.000 | 0.055 |
| steps classifier + comp | 1.1 / 84.4 | 0 | 942 | 3 339 | 5.33 | 0.000 / 0.000 / 0.028 | 0.000 | — |
| steps classifier + surround | 0.8 / 84.7 | 0 | 18 307 | 16 075 | 1.22 | 0.000 / 0.000 / 0.028 | 0.000 | — |
| steps + comp + slope budget | 0.7 / 88.8 | 0 | 889 | 3 312 | 5.59 | same | 0.000 | 0.43 |
| app's per-row law (kit check) | — | — | — | — | — | — | — | 0.000 |

The troll is kept and L3 is neutral, but L2, the sunflowers, starwatcher and vermeer are all worse than `comp`. The buffers say
why, and it is the same thing every time (`layer_room_head.png`, `layer_L2.png`): once more sheets of SMALL pieces are fitted
behind an occluder, their planes run the whole hole and, being nearer than the true far side, win the layered order. Right of
the sunflower head the winners are pieces of the far field whose rims sit 200 rows below at 0.097 and whose planes read
0.245 up in the sky's rows; on L2 the tilted discs of the farther heads. Under `comp` those pieces were things whose marches
never closed, so they were hedges and the sky won — a guard by accident. Every rule that removes the accident (any-thing
closure, the surroundings' median, and the classifier change below) exposes the extrapolation.

**The classifier's part.** The buffer also showed the sunflowers' whole far field (157 k texels at 0.084) classified as a
THING: with hundreds of tiny neighbours its median shared boundary is two texels, and a three-texel fragment it stands in
front of casts the deciding vote (the §22 floor-vote flaw). Two repairs measured (`--thingrule`): a plain majority of the
whole boundary, frame included — falsified at once (SAM's part segments are bounded by their own siblings; starwatcher's
figure stopped being a thing, v 2 249 → 45 700; removed); and the vote by boundary length over STEPPED pairs only, joined
boundary abstaining (`steps`): starwatcher 2 249 → 942, vermeer 3 339 unchanged, the troll's forest becomes surfaces and his
gap 91.8 → 1.1 % under plain `comp` — and the sunflowers 197 → 0 sky rows, because the same far-field pieces, surfaces now,
are fitted everywhere and their planes run up into the sky. The slope budget (`--budget`) on top does not save it (0 rows;
L2 0.015 → 0.43 m, the ground's own slope shrunk).

**Where this leaves C.** The layer notion as a grouping is falsified; as a majority-of-surroundings rule it does what §28's
rule did — fixes the troll and S15 — and fails the same pictures for the same reason. The kit made that reason visible: the
sheet model has no rule for how far a small piece's plane may be trusted away from its own patch, and the two-sided hedge
tier has been standing in for one. That is the next item, and it is not a closure item: a reach or a slope law for small
patches (the §15 reach rule limited to things helped L2 a little, 0.083 → 0.055; the budget hurt) measured on L1–L4, where
the truth now exists. `comp` + the §22 classifier remains the best all-round arm; `steps` is a better classifier on three
counts and worse on one for the reason above, so it waits for the reach law too.

**Pending when this was written:** the L1 and L4 truths (the forest scenes were rebuilt with 300 / 100 discs after the
1 200-disc truth spent an hour in its first eye) and their scores under `comp`, `surround` and `steps`; vermeer under
`steps + surround`. Added below when they land.

## 30. The reach law, measured against the truth (user: "yes continue with reach", 2026-09-18)

**The instrument first** (`--reach-diag`, `bleed/reach_diag.py`). Per fitted sheet: its primitive (the rest render's first-hit
pid at its rims), its own visible extent E (geodesic radius of its patch from its rims), the hole reach R, and for every
texel of its disc the geodesic distance j from its entries, whether the truth's first hidden surface there IS that primitive,
and the plane's error. It asks whether the truth holds a law for how far a sheet may be trusted away from its own patch.

**Two defects the instrument exposed before it could answer.** (1) The "entries" of a sheet's disc were the whole march
footprint: `rimOf[r]` lists every band texel a rim serves along its lines (164 per rim on L2), so the geodesic distance from
the entries was 1 on every march texel. The §15 reach cap therefore only trimmed the sideways spread of a disc that was
already the full marches (L2's 3-texel leaf kept 9 217 texels with R = 3), and the §29 per-texel exposure trim never trimmed
anything. (2) A capped sheet's disc was seeded from its marches, not its entries. Both fixed: the entry per rim and
direction is the served band texel nearest the rim (a march start is not always 4-adjacent to it), and a sheet whose reach
is capped below its hole depth gets the disc of radius R about its entries. §29's conclusion stands (the majority rule fixes
the troll and fails the pictures); its trim did not exist. A third thing the instrument caught: L2's "median 0.015 m" under
`comp` sat on a knife-edge — 35 % of the band was at half a metre; the mean (−0.17 m) and the p90 told it, the median did not.

**What the truth says** (L2, L3, S15; true entries). On L2 the sheets are right on 88 % of the texels they win within their
own extent (j ≤ E), on 90 % between E and 2E, and on 2.5 % beyond 2E — 26 728 wrong texels, all beyond twice the extent.
Per sheet, J90 (the 90th percentile of j over the texels where the hidden surface is the sheet's own primitive) against E:
whole things (L2's discs, L3's jug and bowl) J90/E 0.3–1.9, median about 1; fragments of a larger surface (a 39-texel
ground component: E 2, J90 251) and pieces of a layer (S15's crown discs, one Canopy primitive: J90/E 10–29) far beyond E.
**A whole thing's hidden extent behind an occluder is of the order of its own visible extent; a fragment's is that of the
whole it belongs to.** The second half is §29's layer question; the first half is a law with no constant in it.

**The law on the kit** (`--reach`, own extent, every sheet — L2's runaway leaf is classified a surface, so things-only would
miss it). L2's buffer (`reach_L2.png`): the leaf that owned 51 % of the band (28 622 texels at 0.51 m) owns 162, all correct;
the background class goes from mean −0.228 m to −0.000 m. What remains on L2 is the other class: the hidden things (8 594
texels, 15 % of the band — heads behind the big head, leaves behind heads) are hedges under `comp` because their marches
never re-emerge, and the sky fills them (thing class 0.512 m). The truth says those slivers are real (J90 ≈ E/3 to E). Two
closures without re-emergence were tried and are falsified (rule 7, removed): `none` and `disocc` (a march whose band
texel is nearer than the rim is fitted, own-body marches keep the §18 test), each with the parallax trim (`--expo`, the §29
trim that now works): L2 things 0.51 → 0.03 m and L3 things 0.079 → 0.001 m, but L2 background −0.17 m — leaves that touch
a head's silhouette from below fill up to E behind it where the truth is the ground (their true continuation is zero: a leaf
beside a head is not behind it) — and on the pictures half the troll's and vermeer's bands go unreached (capped discs,
and with every march "closed" no hedge tier to fill behind them). No scalar of a patch separates a head that continues 13
texels behind its neighbour from a leaf that continues none; the geometry of the contact would (a convex thing hidden along
half its contour continues about its radius, one touching at a point continues nothing). That is a contour instrument, and
it is the next thing to build if the hidden-thing class matters.

**The law on the pictures: the fragment half of the statement bites at once** (`reach_pics_R.png`). Under `comp + reach`
the troll is fixed (gap 91.8 → 3.4 %, forest 84 %) for the reason the truth gave — the far-background pieces that owned his
band are fragments with tiny E, capped, and the forest hedges fill — and starwatcher's ground is destroyed for the same
reason: its band goes 19 → 92 % sky-valued, because the ground behind the figure is fragments too, capped, and the sky wins.
The sunflowers' band goes 82 → 98 % sky-valued (the field pieces capped; the "211 sky rows" beside the head are that same
loss, not a gain), vermeer 72 → 84 % with a fourfold jump length. The join-group extent (`--reach-group`: a fragment reaches
as far as the largest sheet its join law puts on one surface with it) keeps the troll (gap 6.0 %, forest 92 %), returns the
sunflowers (84 %) and vermeer (72.6 %, jumps at baseline) to their baselines, and recovers half of starwatcher (51 %
sky-valued; group extent median 4 — the ground's strips are not joined by the join law, which is the open question). Things
only (`--reach-things`) is the baseline everywhere but a few hundred jumps. On the kit `reach-group` equals `reach` (kit
surfaces are whole).

| arm | L2 bg / thing mean (m) | L2 med / p90 | L3 thing | S15 med | troll gap % | sunflowers sky-valued % (rows) | starwatcher sky-valued % | starwatcher v | vermeer v / h |
|---|---|---|---|---|---|---|---|---|---|
| comp (baseline) | −0.228 / +0.095 | 0.015 / 0.534 | 0.079 | 8.55 | 91.8 | 82 (197) | 19 | 2 249 | 3 339 / 55 526 |
| comp + reach (R) | −0.000 / +0.476 | 0.000 / 0.490 | 0.079 | 8.12 | 3.4 | 98 (211) | 92 | 1 716 | 2 747 / 32 001 |
| comp + reach-group (RG) | = R | = R | = R | = R | 6.0 | 84 (197) | 51 | 1 995 | 3 110 / 56 827 |
| comp + reach-things (RT) | = comp | = comp | = comp | = comp | 92.6 | 82 (197) | 19 | 2 136 | = comp |
| surround + reach + expo (SRE) | −0.012 / +0.451 | 0.000 / 0.490 | 0.079 | 1.99 | 19.3 (53 % unreached) | 27 (18 % unreached) | 33 (12 % unreached) | 20 113 | 25 337 / 69 984 |
| disocc + reach + expo (falsified) | −0.166 / +0.069 | 0.000 / 0.551 | 0.001 | 6.47 | 22.8 (54 % unreached) | 19 (17 % unreached) | 26 (13 % unreached) | — | — |

S2 and S9 are unchanged by every arm; S26 0.028 → 0.023 m under the closures that were falsified, unchanged otherwise.

**Where this leaves the reach.** The law is real and has no constant: a sheet is trusted no farther than the extent of the
whole it belongs to. What the sheet model lacks is the WHOLE — on the kit every surface is one, on a photograph every
background is fragments, and the join law reconstructs the whole for the sunflowers' field and vermeer's wall but not for
starwatcher's smooth ground. `reach-group` is the arm to carry (it is the first that fixes the troll without breaking the
sunflowers or vermeer); its one casualty is the instrument for the next item: why the join law does not join a smooth
ground's strips. Not adopted as default until L1 and L4 (the forest scenes, exact truth for the troll's configuration) are
scored: their truths are rendering (the 300-disc canopy fills the frame's bounding ellipsoid, ten minutes per eye, so the
grid was cut to the extreme eyes ±45° × ±29°, 15 eyes), and `kitL_after.sh` scores comp / R / RG / RT on them with the
diagnostic the moment they land.

**L1 and L4 landed** (`reach_L1.png`; the truths finished while the pictures ran — the scope log prints only every fifth eye,
so the count I was watching was wrong). L1, the dense layer (the troll): the app's own per-row law median 0.0075 m, p90
0.093; `comp` median 0.092 m, mean +0.075 — the forest not continued behind the figure, the wall fills, thing class 0.105 m:
the troll's gap in exact truth. `reach` 0.0115 m, mean −0.002, both classes 0.017 m — the app's level. `reach-group` 0.015 m
(bg 0.066 / things 0.046): worse than `reach` here, because the join law groups leaves with the wall pieces between them.
`reach-things` = `comp`. But L4, the sparse layer, says why the L1 fix is the troll's accident again: under every arm L4 is
median 0.000, thing class 0.098 m, fill 0.000 — the leaves hidden behind the figure are hedges and the wall, one whole surface
with a large extent, is never capped and wins. On L1 the wall behind the figure is fragments seen between leaves, capped, and
the leaf hedges fill. The layer's things behind the figure are filled when the background happens to be fragmented, not
because the model knows a layer. That is the same open item as §29 (a layer notion that is not a depth range), now with two
exact scenes to measure it on, and the reach law is the precondition for it: without the cap nothing but the hedge accident
kept small pieces' planes from running the hole.

| arm | L1 med / mean | L1 bg / thing | L4 med / mean | L4 thing |
|---|---|---|---|---|
| app per-row law | 0.0075 / +0.019 | — | 0.000 / +0.018 | — |
| comp | 0.092 / +0.075 | 0.000 / 0.105 | 0.000 / +0.035 | 0.099 |
| comp + reach | 0.0115 / −0.002 | 0.017 / 0.017 | 0.000 / +0.034 | 0.098 |
| comp + reach-group | 0.015 / −0.019 | 0.066 / 0.046 | 0.000 / +0.034 | 0.098 |
| comp + reach-things | 0.092 / +0.075 | 0.000 / 0.105 | 0.000 / +0.034 | 0.099 |

**Recommendation.** Carry `--reach-group` as the measured arm (troll 6 %, L1 0.015 m, sunflowers and vermeer at baseline,
L2's background exact); its casualties are starwatcher's ground (the join law not joining a smooth ground) and, shared with
every arm, the things hidden behind things (L2's slivers, L4's leaves behind the figure). The next item is the layer notion
measured on L1/L4 with the reach law in place, and the join law on a smooth ground; not another closure.

## 31. The casualty of the reach arm, traced: starwatcher's ground is a thing (2026-09-18, "ok continue")

**Where the lost texels are.** Under `comp + reach-group` starwatcher's band goes 19 → 51 % sky-valued. Every one of the
43 307 lost texels is BELOW the horizon (row 481; lost rows 555–674, columns 142–435, behind the figure's legs and to its
left), so it is a real loss, not a correction (`reach_starwatcher.png`). The baseline had filled them with one sheet — the far
plain at d 0.077 — which was itself wrong: the band there is the near plain's OWN band (a smooth receding ground has a far
side everywhere: the app's disocclusion rule fires on the gradient), and its far side is the plain a little farther up, at
0.3–0.5, not the horizon and not the sky.

**Why nothing fits it.** The near plain is a SAM segment (id 2, 131 k texels, d 0.527) and the classifier calls it a THING:
it is in front of the far plain by medians (0.53 vs 0.03) and by a depth step across the join-law break at the horizon. A
thing's own-body marches take the §18 self-closure test, they do not close (the plain runs off the frame), so its sheets are
hedges and whoever else reaches wins: the far plain under the baseline (uncapped, wrong), the sky under any reach arm (the
far plain capped to its group's extent, 173 texels). The near plain's own join group has sheets with extents up to 263; they
are hedges too.

**Three classifier rules tried against it, all constant-free, all falsified (rule 7, the code records each):**
- *Stepped vote* (§29 `steps`) + `reach-group`: starwatcher's jumps 2 249 → 794 but the plain stays a thing (51 → 53 %
  sky-valued); on the sunflowers the plants become surfaces and, given the background's group extent, fill the sky rows
  (0 of 211 sky, jumps 1 349 → 14 648) — §29's failure of `steps` was not only the reach defect. The join law puts the
  sunflowers' far field and sky in ONE group (519 k texels, extent 283): the horizon is a gradient DA3 joins.
- *Frame contact* (thing iff its stepped front boundary is longer than its contact with the frame's edges): both plains
  stay things — a ground is in front of the sky along a horizon as long as the frame's bottom.
- *Recede* (thing iff the mean disparity drop at its stepped front edge exceeds its own disparity range): both plains become
  surfaces and starwatcher's band fills (0.5 % sky-valued, fill 0.28) — and so do S2's slanted slabs (0.000 → 0.012 m), the
  milkmaid (9 → 4 labelled things) and the troll (13 → 2): their own planes fill their bands, vermeer's wall goes 72 → 6.5 %
  sky-valued, every picture's jump count rises tenfold. On the kit it gave S15 6.55 → 0.076 m median (mean −1.6: the crown
  pieces as surfaces), L4 0.000 → 0.049 m.

| arm | L1 med | L2 bg / thing mean | L4 med | S2 med | S15 med | starwatcher sky-valued % / v | sunflowers sky-valued % / v | troll gap % | vermeer sky-valued % / v |
|---|---|---|---|---|---|---|---|---|---|
| comp (baseline) | 0.092 | −0.228 / +0.095 | 0.000 | 0.000 | 8.55 | 19 / 2 249 | 82 / 1 349 | 91.8 | 72 / 3 339 |
| comp + reach-group (RG) | 0.015 | −0.000 / +0.476 | 0.000 | 0.000 | 8.12 | 51 / 1 995 | 84 / 1 029 | 6.0 | 72.6 / 3 110 |
| steps + RG | 0.015 | −0.013 / +0.386 | 0.000 | 0.000 | 6.55 | 53 / 794 | 1.8 / 14 648 | 1.1 | 72.6 / 3 110 |
| recede + RG | 0.014 | +0.000 / +0.493 | 0.049 | 0.012 | 0.076 | 0.5 / 25 272 | 1.8 / 35 141 | 17.4 | 6.5 / 20 912 |

**What separates a ground from a figure standing on it** is not in a unit's boundary lengths or depth statistics at this
level: the ground is in front of the sky along a horizon as long as the frame, and a figure's DA3 depth spans as much as its
drop to what is behind it. The property is that the ground's depth at its far edge CONTINUES into the far side (it recedes
into the horizon) while a figure's silhouette is a step of constant size — a per-edge test on the run of depths approaching
the boundary, not a per-unit statistic. That is a contour/edge instrument, the same family as the contact-geometry test §30
named for hidden things, and it is the next classifier item. Until then `comp + reach-group` stands as the measured arm with
starwatcher's near plain as its one documented casualty, and the fact that the baseline's fill there was also wrong.

## 32. The edge instrument (user: "do the edge instrument", 2026-09-18)

**The instrument.** At every boundary texel where a unit stands in front of its neighbour by a depth step, the unit's depth
along the inward grid line (up to 24 texels, at least 4) is fitted by a line and extrapolated one texel past the edge. The
unit CONTINUES there when the extrapolation lands on the far side within the tolerance; it STEPS OFF when it does not. Per
unit: the front-boundary length of each kind and the median of the extrapolation's miss over the actual step (printed with
`THINGS_DIAG`; always computed in the classifier stage, `sheets.py`).

**What it says about starwatcher's plain: it steps off.** The near plain steps off along 864 of its 917 stepped front
texels (miss/step 1.18), the far plain along 946 of 954 (1.00); every figure, jug and head on vermeer and the sunflowers
1.0–1.9. In DA3's map the near plain ends in a terrace step of 17 times its own per-row slope, not in a horizon it recedes
into. So the map presents the plain as a slab in front of another slab; the classifier is not wrong about the map, and the
baseline's fill of the plain's band with the far plain was the map's own geometry. The edge test cannot separate a
terrace from a figure, and no per-unit or per-edge depth statistic tried today can (§31: three rules; §32: this one).

**What the band behind the figure's legs actually is** (`DBG_SHEET` on the domain builder): the near plain's own
self-occlusion band — the whole plain is band, because a receding ground has a far side everywhere — and under the baseline
it was filled by a 9-rim sliver of far plain whose 923-texel column marches, dilated by their own length, reached 21 846
texels. The reach law cuts that sliver to 754 texels, correctly. The true far side is the plain itself a little farther
up, and no arm constructs it: the plain is a thing, so its own-body marches take the §18 self-closure test, and they run up
the whole plain (all band) to exit at the horizon onto the far plain — open, hedge, sky. Two constructions were tried
against this and are falsified (rule 7, both removed): closing also on an exit onto the sheet's own join group (29 k of
794 k marches closed; sky-valued 50.6 → 47.0 %, jumps 1 967 → 5 662), and the join group's AREA as the reach extent
(`--reach-area`, kept as an option: the inradius undersells a wide strip, but the strip that mattered was a sliver; kit L1
0.030 m against `reach-group`'s 0.015, every picture identical to `reach-group`).

**The construction that is missing** is the per-line law's own: what is revealed at a band texel is what lies the reveal
distance up the line, and when that is the same surface (joined all the way) the surface continues itself — a stretch,
not a far side. The sheets model has no such case: its far sides are other surfaces' planes, and a fully banded receding
surface has no rims of its own. On the kit this never shows because the kit's grounds are one visible component and one
sheet; on a photograph a smooth ground is strips. That is the next construction item, with the layer notion (L1/L4) the
one after it. The measured arm remains `comp + reach-group`; starwatcher's plain is its documented casualty, and today
established that the casualty is a missing construction, not a classifier verdict.

## 33. The self-continuation construction (user: "do the self-continuation construction", 2026-09-18)

**What it is** (`--selfcont`). A steep receding surface's band is the union of tiny per-texel gaps — starwatcher's whole plain,
41 % of vermeer — so no exit test at the far end of a march finds its far side (§32). The construction asks, per band texel
b, whether what lies BEHIND b along its rest ray is ever revealed: walk from b along each grid line while on b's own
joined surface; the walk ends at t_s onto a surface X (a frame edge is the surface continuing, an exit onto a nearer
surface says nothing); from the eye motion that direction stands for, an own texel at distance t occludes X's point behind
b iff KPAR (D_t − D_X) ≤ t; X is revealed in that direction iff the surface ends before any own texel does that. The truth
counts a reveal from any eye, so b continues itself only when NO direction reveals; the value is the surface's next depth
level behind b (its own map, one level down), and the decision is taken per join group by majority so that a footprint or
a SAM part on a plain does not leave salt-and-pepper sky behind it. It enters the layered order as a candidate like a
fitted sheet. Three earlier forms are recorded in the code and falsified by the kit: the first same-surface level behind
(filled every figure with itself), the first screen-space crossing KPAR (D_b − D_j) ≥ j (L3 0.000 → 0.083 m, S2 0.000 →
0.056 m: a curved body crosses before its silhouette), and the rest-ray test with the nearest candidate over directions
instead of no-reveal-in-any (the milkmaid's skirt 135 texels below her chest occludes the wall for a vertical eye while a
sideways one reveals it 50 texels away).

**On the kit** the final form is neutral or better everywhere: L1 0.015, L2 0.000 (bg exact), L3 0.000, L4 0.000, S2 0.000,
S9 0.000, S26 0.028, S15 8.12 → 5.10 m median. **On starwatcher** it does what was asked (`selfcont_starwatcher.png`): the
plain fills with itself within two steps of its own depth (sky-valued 51 → 1.3 %), its texture is the map's own staircase
(the jump count over four steps 1 131 → 6 270, along the terrace line and the figure's edges), and 17 % of the figure's
band leaks into self because DA3 joins the figure to the far plain's group. The troll's gap closes fully (6.0 → 0.6 %).

**On vermeer and the sunflowers it overreaches** (`selfcont_pictures.png`): 98 % of vermeer's band and 57 % of the
sunflowers' become self fills — the milkmaid and the table fill with themselves, the plants with themselves (rows of sky
beside the head 197 → 82). The numbers behind it: under the app's depth law (D 0.2, outer 0.02) the parallax reach behind
her chest is KPAR (D_chest − D_wall) = 78 texels for the full envelope, and the band across her on one row is 185 wide —
so from one side or the other the wall is revealed behind nearly all of her, and the rest-ray test should say so; it says
"occluded" because her own body has depth structure (a fold at d 0.3, 50 texels away, has 47 texels of reach against the
wall and so covers the point behind her chest for that eye motion). Whether that is a defect of the model or of the band
turns on a question this note cannot settle from the offline side: on a quantised gradient, does the app's plate tear at
every quantum step (then the band inside a figure or a plain is tiny tears and wants self) or only at the silhouette (then
the band inside her is the wall's reveal zone and wants the wall)? The band's width across her says the app marks her whole
body; the rim tear law tears at steps above the tolerance and a quantum step sits at it. That is the next thing to read in
the app, and it decides the construction's scope.

| arm | L1 | L2 bg / thing | L3 | L4 | S2 | S15 | starwatcher sky-valued % | troll gap % | sunflowers sky-valued % (rows) | vermeer sky-valued % |
|---|---|---|---|---|---|---|---|---|---|---|
| comp + reach-group (RG) | 0.015 | −0.000 / +0.476 | 0.000 | 0.000 | 0.000 | 8.12 | 51 | 6.0 | 84 (197) | 72.6 |
| RG + self-continuation (RGS) | 0.015 | −0.005 / +0.475 | 0.000 | 0.000 | 0.000 | 5.10 | 1.3 | 0.6 | 40 (82) | 1.7 |

**Standing.** `--selfcont` stays an option, not part of the measured arm: right on the kit and on starwatcher's plain, and the
one construction that filled the troll's gap to under a percent, but it claims the whole of vermeer's figure and the
sunflowers' plants, and the app's band semantics on quantised gradients must be read before that can be called right or
wrong. Instruments added this session and kept: `--reach-diag` / `bleed/reach_diag.py`, the edge instrument in the
classifier stage, `sheets_info.npz`, `bleed/owners_err.py`, `bleed/fillcheck.py`, `bleed/jumps.py`-style counts, the
`DBG_SHEET` line in the domain builder.

## 34. The tear law read, the band's semantics settled (user: "read the tear law in the app and settle it", 2026-09-18)

**The rim law** (`moebius.js` L378–461, `bgRimLawFor`). An edge between two texels is JOINED iff the ratio of their eye
distances is within t = 1 + (hfov / pw) / tan(g_min), g_min = 2°, OR the linear prediction of either from its own two
previous samples lands within the quantisation bound tolAt (the grazing-plane rescue; sky joins nothing but sky). With
starwatcher's geometry t − 1 ≈ 0.037 of the eye distance; one quantum of an 8-bit map moves it by about 0.002. **The plate
does not tear inside a quantised gradient**: it takes a step of some twenty quanta at once, or an affine prediction that
fails, to open an edge. The pre-rim fold criterion (A160, "shift span > cell extent") did tear terraces on slow gradients;
the rim law replaced it precisely because it tore nine tenths of every grazing floor (S1 §5c), and the probes run under the
rim law.

**Where the band comes from** (L8318–8660, the CPU sweep). Per pose the foreground is drawn as quads wherever all four
corners are joined, at the nearest corner's depth, as a rubber sheet however far it stretches (the stretch cut is off under
the rim law); an unjoined corner leaves only a point splat. Every in-frame cell the foreground leaves uncovered is a reveal,
inverted through the FAR FIELD's shift to the plate texel that must cover it; the union over the 17 × 5 poses, plus
pinholes and a one-texel dilation, is `disocc.u8`. So a band texel inside a figure or a plain is not a tear: it is a texel
whose far-field copy lands in a cell the near content vacated at some pose — the reveal zone of what is behind it, and it
takes the far field's depth. The app's own far field confirms the semantics on every input measured: band fill minus own
depth in steps, p50 — starwatcher's near plain −149, its figure −131, vermeer's milkmaid −217, the troll's surroundings
−117, L1 background −55, L2 things −96, L3 things −80; never within 20 steps of the texel's own depth except on L2's
3 000-texel ground band (fill = own, p50 0). The kit scores that semantics at 0.0075 m median on L1 and 0.000 on L2.

**Self-continuation is therefore falsified and removed** (rule 7; the code keeps the record). It gave a receding surface's
band its own next level where no eye motion revealed what lies behind — the opposite of what the band means. It looked
right on starwatcher only because the alternative under the reach arm was the sky; the app's answer for that band is the
FAR PLAIN, ~150 steps behind. Its overreach on vermeer (98 % of the band) had a second cause worth keeping: DA3's silhouette
ramps are joined to the figure by the rim law's affine rescue, so any walk "on the figure's own surface" runs down the ramp
to the wall's depth.

**Starwatcher's plain band, finally.** Its far side by the app's semantics is the far plain. The far plain's sheet (640
rims, 51 k texels, group 157 k) is classified a THING — it stands in front of the picture's backdrop (d 0.002) along the
horizon by a step — so its own-body marches take the self-closure test, do not close (they run down the near plain and off
the frame), and it is a hedge; the reach law rightly removed the 9-rim slivers that used to substitute for it, and the sky
(the only uncapped fitted candidate) wins. "Pairs against the sky class do not vote" was tried and removed: the app's sky
class is d < 0.5/65535 and a photograph's backdrop is not it. The item is the one §31 named: a ground in front of the
picture's farthest surface along a horizon is not thereby a thing, and no unit statistic tried separates it from a figure
in front of a wall. Two facts narrow it: the far plain's front boundary is with the FARTHEST surface of the picture only,
and it touches both frame sides; a figure's front boundary is with a surface that continues behind it on both sides. That
is a topological statement (the far side's continuation around the unit), the next thing to build, and cheap to measure on
the four pictures and L1–L4.

| arm | L1 | L3 | S2 | starwatcher sky-valued % | troll gap % | sunflowers sky-valued % (rows) | vermeer sky-valued % |
|---|---|---|---|---|---|---|---|
| comp + reach-group (RG, the measured arm) | 0.015 | 0.000 | 0.000 | 51 | 6.0 | 84 (197) | 72.6 |
| RG + sky abstains | 0.015 | 0.000 | 0.000 | 51 | — | — | — |

## 35. The topological test (user: "build the topological test", 2026-09-18)

**The rule** (`--thingrule wrap`). A thing stands in front of a surface that continues behind it, so its stepped front
boundary surrounds it: the far side lies on opposite sides of it. A ground stands in front of the picture's farthest surface
along one side only and runs to the frame elsewhere. Per unit: the directions from its centroid to every boundary texel
where it is in front of a neighbour by a step and by the two units' medians; a THING when those directions are not
contained in any half-plane, i.e. the largest angular gap between them is under a half turn. The half turn is what "on both
sides" means, not a tuned constant. Two other direction sets were tried in the same hour and are falsified, recorded in the
code: local steps alone (noise fragments wrap every background — vermeer's wall 109°, the sunflowers' field 54°), and
"surrounding neighbours" (any neighbour with at least the unit's median shared boundary that is not nearer by medians —
joined specks at a background's own depth surround it: starwatcher's sky 90°, its far plain 145°).

**Verdicts** (gap in degrees; thing under 180): L2 ground 206 → surface, big head 19, heads 52–110, leaves 3–19, stems, all
things; L3 floor 192 and ceiling/wall 360 → surfaces, milkmaid 51, table 139, jug 116, bowl 129 → things; vermeer wall 360 →
surface, milkmaid 93, table 175, jug 117, basket 195 → surface; the sunflowers' sky 360 and far field 190 → surfaces, the
heads and plants 76–159 → things; starwatcher's sky 360 and near plain 191 → surfaces, its far plain 176 → thing (the
crystals rise from its horizon), its figure a thing. This is the first classifier under which grounds, fields and skies are
surfaces and figures, heads and jugs are things on every input — the §31 casualty's cause, at last, with one borderline case
(the far plain at 176°). S2 cannot test it: its "boxes on a floor in contact" are joined to the floor by the join law and the
scene has three units, wall and two floor+box halves; the truth wants those halves treated as things (0.000 vs 0.012 m).

**What it exposes when run** (`wrap + reach-group`, kit and pictures): L1 0.015 m (unchanged), L3 0.000, L4 0.000 → 0.0039
median but its hidden leaves 0.098 → 0.038 m, S26 0.028 → 0.026, S15 8.12 → 0.076 m median (mean −1.6); starwatcher the
smoothest field yet (v jumps 1 995 → 731) with its plain band still sky (48 %: the far plain is still the thing at 176°);
the troll's gap 6.0 → 1.5 %; vermeer at baseline (v 2 819). And two collapses of one kind: **L2's background 0.000 → 0.514 m**
and **the sunflowers' band 84 → 1.5 % sky-valued, 0 of 211 sky rows, jumps 1 029 → 15 724**. In both the classifier is right
— L2's ground and the sunflowers' far field ARE surfaces — and what then shows is the defect the neighbour rule had been
hiding by mislabelling them things (hedged, so the sky won): the pieces of a big joined surface carry their OWN planes over
the group's whole extent. L2's culprits are two 860-texel ground pieces with 136 and 84 rims, own extent 8 and 15, whose
planes at d 0.36 own 47 000 texels of sky; the sunflowers' are the field pieces at 0.2–0.4 running up beside the head. The
reach law gives a fragment its group's DOMAIN (right: the ground continues behind the head) but leaves it its own PLANE
(wrong: a 900-texel strip's slope says nothing 130 texels away). That is the group-surface item: a fragment of a joined
surface should carry the group's plane, or its plate, beyond its own extent — the construction §17's faces circled.

| arm | L1 | L2 bg / thing | L3 | L4 thing | S2 | S15 med | starwatcher sky % / v | troll gap % | sunflowers sky % (rows) / v | vermeer v |
|---|---|---|---|---|---|---|---|---|---|---|
| comp + reach-group (RG, measured arm) | 0.015 | −0.000 / +0.476 | 0.000 | 0.098 | 0.000 | 8.12 | 51 / 1 995 | 6.0 | 84 (197) / 1 029 | 3 110 |
| wrap + reach-group (WG) | 0.015 | −0.421 / +0.008 | 0.000 | 0.038 | 0.012 | 0.076 | 48 / 731 | 1.5 | 1.5 (0) / 15 724 | 2 819 |

**Standing.** `wrap` is the classifier to carry, and it cannot be adopted until fragments of a joined surface stop carrying
their own planes across the group; with that construction in place `wrap + reach-group` is the arm to measure against the
kit again. The measured arm stays `comp + reach-group` today.

## 36. The group plane for fragments (user: "build the group plane for fragments", 2026-09-18)

**The construction** (`--group-strip`). A sheet's strip — the texels its plane is fitted on — is its own visible component's
texels within its reach window. A fragment of a ground therefore extrapolates its own strip's slope across the group's
domain (§35). With the flag the strip is the join group's texels in the same window together with the fragment's own: the
surface's plane, fitted on the surface's texels out to the distance the plane must be extrapolated; the thin-evidence rule
sees the larger strip too. Under `wrap + reach-group` **L2's background goes from 0.514 m to 0.000 m** (mean −0.001), the
exact answer, with the heads' slivers back in the hedge tier where the closure question leaves them (thing class 0.511,
§30). L1 0.0156 (things 0.046 → 0.024), L3 0.000, L4 0.000 (its leaves back to 0.098: §35's 0.038 was the fragments'
accident), S9 0.000, S26 0.027, S15 0.071 median; S2 0.036 (the floor+box halves, §35). Starwatcher's field the smoothest
yet (v 878), the troll's gap 0.4 % with forest 98.7 %.

**Where it breaks, and why.** Vermeer: the wall's band goes from 72 % sky-valued (the wall, right) to 0.4 % at d 0.11. The
join law joins the wall to the floor at the crease — by design, a crease is continuous in eye distance — so the group is
one continuous surface and NOT one plane, and a least-squares plane through wall and floor is neither. Starwatcher 51 → 64
% sky-valued for the same reason (its plains and their ramps), the sunflowers unchanged at the sky rows (their group is sky
+ field + ramp-joined plants, 512 k texels, 67 % sky: the join law's horizon problem, not the strip's). Two repairs measured
and falsified (rule 7, recorded in the code): growth from the fragment's own plane (inliers within three MADs, three rounds
— it never grows from a bad seed, L2 background 0.50 m again) and a sampled consensus plane over the window that carries the
fragment (L2 0.32 m, vermeer's wall band 0.30).

| arm | L1 | L2 bg / thing | L3 | L4 thing | S2 | S15 med | starwatcher sky % / v | troll gap % | sunflowers sky rows / v | vermeer sky % / v |
|---|---|---|---|---|---|---|---|---|---|---|
| comp + reach-group (RG, measured arm) | 0.015 | −0.000 / +0.476 | 0.000 | 0.098 | 0.000 | 8.12 | 51 / 1 995 | 6.0 | 197 / 1 029 | 72.6 / 3 110 |
| wrap + reach-group (WG) | 0.015 | −0.421 / +0.008 | 0.000 | 0.038 | 0.012 | 0.076 | 48 / 731 | 1.5 | 0 / 15 724 | 72.6 / 2 819 |
| wrap + reach-group + group strip (WGS) | 0.0156 | −0.001 / +0.475 | 0.000 | 0.098 | 0.036 | 0.071 | 64 / 878 | 0.4 | 0 / 25 859 | 0.4 / 2 043 |

**What the day's chain of items says together.** The reach law needs the whole a fragment belongs to (§30); the whole is the
join group (§35 makes the classifier honest about grounds and fields); a fragment then needs the whole's SURFACE for its
plane (§36) — and the join group is a continuous surface with creases and curvature, which one plane cannot carry. The
construction that carries it exists in this repo: the 2-D clamped plate per join group (§22, `sheetfield3.py`, adopted
behind a select in §32), which respects creases because it interpolates the surface rather than fitting a plane through it.
Wiring the plate as the fragment's value beyond its own extent is the next item; with it, `wrap + reach-group` can be
measured fairly on vermeer and starwatcher. The join law's horizon problem (sky joined to field on the sunflowers) is a
separate item and older. Measured arm today: still `comp + reach-group`.

## 37. The clamped plate per join group (user: "wire the clamped plate in for fragments", 2026-09-18)

**The wiring** (`--group-plate`). One thin-plate solve per join group, with the machinery of `--tps` (the §14 plate: bending
energy, data at the strip's own noise, Morozov's discrepancy for λ, algebraic multigrid): data = the group's visible texels
within reach of its sheets' discs, unknowns = data ∪ the union of those discs, no plane prior (the group's own texels pin
the plate on every side of a hole; a prior toward any plane brought back the wall+floor plane at vermeer's crease). Every
sheet of the group takes the plate's values on its disc, so fragments carry the surface — creases, curvature and all — and
share one field. Under `wrap + reach-group`:

| arm | L1 med / things | L2 bg / thing | L3 | L4 thing | S2 | S26 | S15 med | starwatcher sky % / v | troll gap % | sunflowers sky rows / v | vermeer sky % / v |
|---|---|---|---|---|---|---|---|---|---|---|---|
| comp + reach-group (RG, measured arm) | 0.015 / 0.046 | −0.000 / +0.476 | 0.000 | 0.098 | 0.000 | 0.028 | 8.12 | 51 / 1 995 | 6.0 | 197 / 1 029 | 72.6 / 3 110 |
| wrap + reach-group + group strip (WGS) | 0.0156 / 0.024 | −0.001 / +0.475 | 0.000 | 0.098 | 0.036 | 0.027 | 0.071 | 64 / 878 | 0.4 | 0 / 25 859 | 0.4 / 2 043 |
| wrap + reach-group + group plate (WGP) | **0.0101 / 0.007** | −0.000 / +0.479 | 0.000 | 0.099 | 0.0029 | 0.030 | 1.21 | 98 / 1 664 | 30.7 | 165 / 48 068 | 21 / 95 350 |

**On the kit it is the construction.** L1's hidden forest layer, the troll's configuration in exact truth, goes from 0.046 m
(RG) to **0.007 m** — the leaves behind the figure carried by their layer's plate rather than each leaf's plane or the
wall; L1's median 0.0101 m is under the app's own 0.0075 m by a third of a step (`groupplate_L1.png`). L2's background is
exact; S2 comes back to 0.003 m (the group plate carries the floor+box halves as the surface they are); S15 8.5 → 1.2 m.
The kit's join groups are surfaces, and the plate interpolates a surface.

**On the photographs it fails, and the failure is upstream of it.** Vermeer's wall band goes 72 → 21 % sky-valued at
fill 0.3 with the jump count thirty times the baseline; the troll's gap opens to 31 %; the sunflowers land between the
arms (165 of 211 sky rows, jumps 48 k). Each is the join law's grouping on a DA3 map: vermeer's wall is one group with its
floor (the crease, by design) and with the figure's silhouette ramps (the affine rescue joins a ramp as a grazing plane),
so the plate is pinned by data at three depths; the troll's forest group has 56 visible texels within reach of a 177 k
domain (the leaves' own texels are all band), so the plate is essentially free and did not converge; the sunflowers' group
is sky + field + ramp-joined plants. A plate interpolates whatever the data say is one surface, and on these maps the join
law says the wrong things are one surface. Starwatcher's plain band (98 % sky) is §34's point once more: the plain's own
plate reproduces the plain, which is not behind the plain, and the far plain that the app puts there is still the thing at
176°.

**Where the thread ends today.** The chain §30 → §35 → §36 → §37 is complete on the kit: the reach law bounded by the whole
(§30), the whole named honestly by the topological classifier (§35), the fragment carrying the whole's surface by the
plate (§37) — L1 0.0101 m, L2 background exact, L3 0.000, L4 0.000, S2 0.003, S9 0.000, S26 0.030, S15 1.21 m. What the
photographs add is one item, older than all of these and now isolated by them: the join law joins what is not one surface
on an estimator's map — creases are joined by design and should stay so for the plate, but silhouette ramps and soft
horizons are joined by the affine rescue and must not be. A ramp is a monotone run of a few texels spanning a large depth
between two surfaces that each continue beyond it; a grazing plane is not. That test on the rim law, measured on the
troll, vermeer and the sunflowers with the kit as the regression bar, is the next item. Measured arm today: still
`comp + reach-group`; the arm to measure once the join law is repaired: `wrap + reach-group + group-plate`.

## 38. The ramp test in the rim law (user: "build the ramp test in the rim law", 2026-09-18)

**The test** (`--ramp`). Along each row and column, a maximal run of joined edges each of which crosses more than the
tolerance (a distinct depth level per texel) is a candidate; its two flanks must be flat joined edges. Each flank is
extrapolated by its own affine law to the run's middle; the run is a RAMP when the two extrapolations disagree by more
than quantisation can explain over the span (L texels × tolerance) — it bridges a step between two surfaces that each
continue beyond it. A crease meets in value there and a grazing plane's near part predicts its far part, so both stay
joined. Ramp edges are unjoined and the ramp's interior texels join the band, so the march passes through them to the
surface beyond instead of taking the estimator's blur as a far rim. A first form took only runs joined by the affine
rescue and found 20 on all of vermeer: her silhouette ramps are joined by the RATIO test itself (3.3 % of eye distance per
texel under the 3.7 % that g_min = 2° allows), which is worth knowing about the rim law.

**What it does.** Vermeer: 2 426 row runs and 2 036 column runs cut, 10 804 ramp texels; the wall (375 k texels) and the
milkmaid (171 k) become separate join groups where they were one. Kit, under `wrap + reach-group + group-plate`: nothing
regresses and S26 goes 0.030 → 0.000 m — L1 0.0101 (hidden layer 0.007), L2 background exact, L3 0.000, L4 0.000, S2
0.003, S9 0.000, S26 0.000, S15 1.32 m. Seven of the kit's eight layered scenes are at or under the app's own law.

**What it does not do: rescue the plate on the photographs.** Vermeer's band behind the milkmaid fills at 0.21 (wall
0.008), the troll's gap is 30 %, starwatcher 21 % sky-valued with 18 % unreached, the sunflowers back to 211 sky rows
with jumps at 24 k. The owners behind the milkmaid say why, and it is three things, none of them the ramp: (1) the wall's
group plate itself reads 0.095 there — the wall and the floor are one group at the crease, by design, and a plate pinned
by the wall above her and the floor below her interpolates a blend where the truth is wall down to a crease; a plate
cannot make a crease inside a hole, the crease's line has to be extrapolated; (2) the table's sheet, a thing, owns 46 000
of her band texels at 0.21 as a fitted sheet — a thing's march up through her body, the §28 question again; (3) hedged
specks. The troll's forest groups have no visible texels within reach of their discs once the leaves are cut apart, so
their plates are free.

| arm | L1 / hidden layer | L2 bg | L3 | L4 thing | S2 | S26 | S15 | starwatcher sky % / v | troll gap % | sunflowers sky rows / v | vermeer sky % (wall behind her) / v |
|---|---|---|---|---|---|---|---|---|---|---|---|
| comp + reach-group (RG, measured arm) | 0.015 / 0.046 | −0.000 | 0.000 | 0.098 | 0.000 | 0.028 | 8.12 | 51 / 1 995 | 6.0 | 197 / 1 029 | 72.6 (94 %) / 3 110 |
| wrap + reach-group + group-plate (WGP) | 0.0101 / 0.007 | −0.000 | 0.000 | 0.099 | 0.003 | 0.030 | 1.21 | 98 / 1 664 | 30.7 | 165 / 48 068 | 21 / 95 350 |
| WGP + ramp (RW) | 0.0101 / 0.007 | −0.000 | 0.000 | 0.098 | 0.003 | **0.000** | 1.32 | 21 / 77 615 | 29.8 | 211 / 24 409 | 17 (27 %) / 86 749 |

**Where the day ends.** On the kit the sheet model is now complete and exact or near it: reach bounded by the whole (§30),
the whole named by the topological classifier (§35), the fragment carrying the whole's surface by the plate (§37), ramps
cut out of the join law (§38). On the photographs the same arm fails, and the failures are now three named constructions,
not a mystery: the crease inside a hole (extrapolate the crease line; the plate cannot bend there), a thing's march
through another thing (§28's question, untouched today), and data-poor groups (fall back to the plane when a group's
visible texels are few against its domain). The measured arm stays `comp + reach-group`; `wrap + reach-group +
group-plate + ramp` is the arm the kit has validated and the photographs have not. The instruments to carry: the reach
diagnostic, the edge instrument, the wrap gap, `sheets_info.npz`, the fill and owner checks.

## 39. The crease inside the hole (user: "build the crease line inside the hole", 2026-09-19)

**The construction** (`--crease`). A join group is one surface with creases (§37); its plate cannot make a crease where no
data holds it, so behind a wide occluder a wall blends into its floor. The crease is visible outside the hole: it is the
boundary between two FACES of the group (the smoothing test kept them apart because their planes differ by more than the step
over their extent) that both border the hole. Where that boundary meets the hole -- the entry -- the crease continues
straight, along the principal axis of the visible boundary within the reach window of the entry, until the line leaves the
domain; the domain edges the line crosses are HINGES. Along a hinge the plate's bending rows that straddle it keep a
thousandth of their weight (a millionth of the energy: the slope may jump) and a first difference across it is penalised at the
bending weight (the value may not). Two tests keep the hinge honest, both with the construction's own quantities: (1) a face
boundary is a crease only where the two faces' local planes MEET at the entry -- the entry must lie on the planes' intersection
line within that line's own uncertainty, the visible step over the slope jump, plus one texel of raster (a shallow crease's line
is poorly placed, a sharp one's exact; a boundary between two of an estimator's noise facets inside a field, whose planes meet
somewhere else entirely, is no crease: the sunflowers' field group had 696 such boundaries at its holes against 415 creases);
(2) the hinged plate is solved by a sparse LU (the affine-candidate multigrid does not know the fold modes and CG hit its
iteration cap: one of the sunflowers' plates ran 25 minutes unfinished), with a membrane tie-break at a millionth of the
bending energy so that a piece of the hole that no data holds -- the discrete plate's kernel on a domain of discs is larger than
the affine functions, a region joined to the data through a one-texel neck has a free tilt -- takes 'continue the value' instead
of CG's silent minimum-norm zero, and a piece no data touches at all comes back NaN (no value) instead of an exactly singular
factor. The plate fields and hinges are dumped (`group_plates.npz`); `bleed/crease_look.py` draws them, `bleed/crease_rows.py`
scores the band by truth primitive and row band.

**What the kit had to say first: the crease was not on it.** Three new scenes (`C1` a wide screen before the wall-floor crease,
`C2` a broad figure before the S1 corner, `C3` = C1 with the wall standing at 0.8 W inside a 1.5 W room). C1 and C2 were exact
or near it under the plain arm before any hinge, and the reasons are two facts about the kit worth recording: a room's back
wall sits at the scene's outer depth, d = 0, which the app's depth law and the prototype treat as sky -- so in every room scene
(L3, S2, C1, C2's back wall) the wall-floor crease is not a crease between two plates at all; and the kit's floor rides the
app's ground plane, which is exact. C3 puts a wall at a depth of its own and is the configuration of vermeer's milkmaid: a hole
across most of the frame's width, wall data above it and floor data below it, no data of either beside it at the crease rows.
There the plate blends exactly as described -- the error grows from zero at the top of the hole to 25 mm at the crease rows,
a quarter of the band over a centimetre -- and the hinge removes it entirely: median 0.0000 m, p90 0.0004 m, no texel over a
centimetre, floor and wall alike, with or without the ground plane (`crease_C3.png`).

**What C2 had to say: the classifier, again.** Under the plain arm C2's band read 0.020 m median and the hinge made it worse;
the plate's data included the figure's own texels. The figure was a SURFACE: its wrap gap was 203°, because the §22 'by
medians' gate compared it with the neighbour UNIT's median -- the room's wall and floor are one unlabelled unit whose median is
set by its near floor, so the figure standing before the far corner was 'behind' the room and its whole left silhouette did
not vote. The gate now compares the unit's median with the neighbour's depth along their SHARED BOUNDARY (where the two
actually meet): C2's figure 203° → 50°, a thing; C1, S2, S9, S26 unchanged; L1-L4 gain a few small leaf components as things;
on the pictures starwatcher is identical (35 things), vermeer 33 → 35, the troll 29 → 27, the sunflowers 142 → 150, no
background flips. The unit-median form is falsified by C2 and removed (rule 7). With it C2 is exact under the plain arm, with
and without the ground plane (0.0001 m, p90 0.005), and the hinge along its slanted wall-floor crease changes it by less than
a millimetre either way: the figure's hole is narrow and the wall's data beside it already hold the plate.

**On the kit** (medians of the band's error against truth, m; `C` = the crease scenes; things' class where it differs).
The arm `wrap + reach-group + group-plate + ramp + crease` (RWC) beside §38's arm without the hinge (RW) and the measured arm
`comp + reach-group` (RG). RWC and RG were run under the repaired classifier gate; the RW column is §38's table except C2 and
C3, which were run under the repaired gate for this section:

| scene | RG (measured arm) | RW (§38, hinge off) | RWC (hinge on) | what the hinge met |
|---|---|---|---|---|
| C3 wall at 0.8 W behind a wide screen | 0.000 (planes: no plate to blend) | 0.0016, p90 0.021; 25 % of the band over 1 cm; floor rows 0.025 | **0.0000, p90 0.0005, 0 % over 1 cm** | 2 creases, 366 hinges |
| C3 without the ground plane | -- | 0.0022, p90 0.021 | 0.0001, p90 0.0004 | the same |
| C2 broad figure before the corner | 0.005 (bg 0.000) | 0.0008 / no ground 0.0011 | 0.0013 / 0.0021 | 1 crease (the slanted floor crease), 137 hinges; a narrow hole the wall's data already hold |
| C1 wide screen, wall at outer depth (sky) | 0.000 | 0.000 | 0.000 | none: two groups, no crease between plates |
| L1 forest (hidden layer) | 0.015 / 0.046 | 0.0101 / 0.007 | 0.0105 / 0.008 | 83 creases among leaves, 57 boundaries rejected |
| L2 / L3 / L4 background | 0.000 | 0.000 | 0.000 | 0 / 2 / 4 creases |
| S2 / S9 / S26 | 0.000 / 0.000 / 0.028 | 0.003 / 0.000 / 0.000 | 0.0028 / 0.000 / 0.000 | 1 / 0 / 0 |
| S15 | 8.12 | 1.32 | 1.30 | 26 creases, 19 rejected |

Nothing on the kit regresses; C3, the one kit scene that has the milkmaid's configuration between two plates, goes from a
25 mm blend across a quarter of its band to exact. The plane arm never had this problem -- C3 is exact under RG because two
planes and the layered order make a crease by themselves; it is the price of the plate, which the kit's layers (L1) and curved
surfaces (S2) needed, and the hinge pays it back.

**On the pictures** (the standing instruments: `fillcheck` sky-valued share of the band, the troll's footprint by class,
the sunflowers' rows beside the big head, and for vermeer the wall's plate and the fill behind the milkmaid at the rows where
the truth is wall). RW = §38's arm without the hinge; RWC = with it; RG = the measured arm, all under the repaired gate.

| picture | RG (measured arm) | RW (hinge off) | RWC (hinge on) |
|---|---|---|---|
| vermeer, wall plate behind the milkmaid, wall rows: median d / within 3 cm of the wall | -- (planes) | 0.638 / 22 % (saturates to the near end across her band) | **0.022 / 66 %** |
| vermeer, FILL behind her, wall rows: median / within 3 cm of the wall / unreached | 0.008 / 99.9 % / 0 % | 0.139 / 38 % / 2.8 % | 0.022 / 66 % / 0.2 % |
| vermeer, whole band: sky-valued % / v jumps | 72.6 / 3 110 | 20.8 / 80 929 | 28.0 / 13 412 |
| starwatcher: sky-valued % / unreached % / v jumps | 50.6 / 0 / 1 995 | 20.9 / 18.3 / 77 615 | 7.3 / 10.8 / 52 464 |
| troll: gap % / forest % in his footprint | 6.0 / 92.4 | 29.8 / 44.7 | 13.0 / 56.7 |
| sunflowers: sky-valued % / sky rows beside the head of 211 / v jumps | 98.3 / 211 / 805 | 68.9 / 211 / 24 409 | 43.4 / 180 / 26 348 |

**Vermeer is the item's own case, and the hinge does there what it did on C3** (`crease_vermeer.png`). Without it the wall
group's plate over the milkmaid's band is not a blend but a runaway: pinned by the wall above her (d 0.006), by the bend and
the far floor below her (0.02-0.10), and by the receding left wall and the near floor at the band's left, it rises to the
near end of the range across her whole body (median 0.64, p90 1.0 at the wall rows). With the bend's creases continued
through her band -- they enter from her right side, where the bend's facets meet the hole, and the top one at row 857 is
not found because the wall face meets the first facet there only through three-texel specks -- the plate reads 0.022 with
p90 0.074 where the wall is 0.006: wall, not floor, over most of her band, and the fill follows (within 3 cm of the wall on
66 % of the wall rows, from 38 %; unreached 2.8 % → 0.2 %; the band's jumps 80 929 → 13 412). Not exact: the plane arm's
99.9 % is the bar, and what remains is the near-floor data at the band's left pulling the lowest rows, and the creases
the specks hide. On starwatcher the hinge cuts the sky-valued band to a third (20.9 → 7.3 %, unreached 18 → 11 %): the
plain's group has 473 creases and its plate no longer rides its own facets' gradients into the sky. The troll's gap halves
(29.8 → 13.0 %, forest 45 → 57 %) -- his forest groups' plates, with 643 creases among the leaves, bend less across them --
but stays twice the measured arm's 6 %: their problem is data, not creases. The sunflowers go the other way: the field group
(252 sheets, 213 creases kept of 722 boundaries) is DA3's noise facets, its creases are not surfaces meeting, and the band
beside the big head loses 31 of its 211 sky rows with the jumps up (12 → 30 of 211 rows): the crease test rejects 509 of
those boundaries but not all, and every one it keeps frees the plate a little more.

**What it cost.** The hinged plate cannot use the multigrid path: lambda is found on the un-hinged plate (the same data and
noise; the hinge changes how the plate bends inside the hole, not how it fits outside it) and the hinged plate is solved once
at that lambda -- by sparse LU up to 200 k unknowns (a 360 k-unknown plate factors in ten seconds and 1.5 GB on a regular
grid; an irregular 400 k one took a worker to 10 GB and the kernel killed it, which hung the pool -- the pool is now the
futures pool, which raises, and the groups still owed are solved in-process), by CG warm-started from the un-hinged plate
beyond. Pieces of a plate's unknowns that no data touches are now left out of EVERY solve, hinged or not (they came back 0 under
CG -- the far end of the range, claimed as sky -- and on the sunflowers' field the multigrid built on the singular operator
diverged); their texels are unreached instead, which is why the pictures' unreached shares move. Three forms of the hinge were tried before this one and are recorded in the code's comments: dropping the bending
rows across the hinge (singular systems), a topological guard on the pieces the hinges cut off (three data texels, then
non-collinear ones: the discrete plate's kernel on a cut region is larger than one affine function per piece, so no count
certifies it), and sixteen fold modes in the multigrid's candidates (the coarse level grew larger than the fine one).

**Where this leaves the item.** The crease inside the hole is built and measured: on the kit it takes the one scene that
has the configuration (C3) from a 25 mm blend to exact and regresses nothing; on vermeer it turns the wall plate behind the
milkmaid from a runaway into the wall. The classifier's medians gate was the day's second finding (C2) and is repaired. What
the item leaves for the pictures is now upstream of the hinge again: on vermeer the wall face meets the bend only through
specks at the milkmaid's right, so the top crease is not found, and the near floor at the band's left still leans on the
lowest rows; on the troll the forest groups' plates have no data; on the sunflowers a field of noise facets should not be hinged at all -- the crease test needs the third member of the
smoothing test's family: a crease's two faces must each be a surface of some extent, not a facet the size of the tolerance. Measured arm today:
still `comp + reach-group`; `wrap + reach-group + group-plate + ramp + crease` is the arm the kit has validated, now
including its own crease scene, and on vermeer it is the first plate arm that puts the wall behind the milkmaid.

## 40. The crease's visibility test, and the tie-break that was not one (user: "keep going", 2026-09-19)

**Two corrections to §39, both found on the sunflowers.** (1) THE VISIBILITY TEST. §39's crease test asks the two faces'
planes to meet at the entry within the line's own uncertainty, tol / slope jump; a shallow boundary therefore passes
trivially (its window is wide) and an estimator's noise facets inside a field were hinged by the hundred. The missing
condition is the smoothing test's own, with the run's length in place of the facet's extent: a crease is hinged only where
its slope jump, continued over the texels it runs through the hole, amounts to a visible step (jump x run > tol). A crease
that would not show in the plate either way is not hinged. Sunflowers: 420 → 315 creases kept, 801 boundaries rejected;
C3, L3 unchanged. (2) THE MEMBRANE WAS NOT A TIE-BREAK. §39 added a first difference over every edge of a hinged plate at a
millionth of the bending energy so that pieces the hinges cut off would take 'continue the value'. But where a plate's
continuation is affine its bending energy is exactly zero, so far from the data the millionth was the only term, and it
flattened the continuation: the sunflowers' sky plate rose from 0.000 to 0.106 over the band beside the big head, with no
hinge anywhere near it, and the band lost 31 of its 211 sky rows. The visibility test did not touch this (the rows were
lost to a plate with no creases); running the arm without the hinge under the same solver did (211 rows back), which is
what located it. The membrane is removed; the pieces no data touches are left out of every solve instead, and a factor that
is still singular falls back to CG. With both corrections the sunflowers under the crease arm equal the arm without it
(211 of 211 sky rows, one jump, sky-valued 38.8 vs 39.1 %), C3 and L3 stay exact.

**On the kit** the final form (visibility test, no membrane) is identical to §39's on every scene: C1 0.000, C2 0.0013 (bg
0.000), C3 0.0000 / p90 0.0005, L1 0.0105 / 0.008, L2 L3 L4 0.000, S2 0.0028, S9 0.000, S26 0.000, S15 1.30 m. The
visibility test rejects more of the leaves' boundaries (L1 57 creases kept of 142, S15 22 of 45) and it costs nothing there.

**On the pictures** (`fillcheck`, the troll's footprint, the sunflowers' head rows, vermeer's wall rows behind the milkmaid;
RW2 = the arm without the hinge under the same solver, the fair baseline; RWC2 = §39's form with the membrane; RWC3 = the
final form):

| picture | RG (measured arm) | RW2 (hinge off) | RWC2 (§39: hinge + membrane) | RWC3 (final: hinge, visibility test) |
|---|---|---|---|---|
| vermeer, wall rows behind the milkmaid within 3 cm of the wall (fill = wall plate) | 99.9 % | 38 % (plate median 0.64) | 66 % (0.022) | 56 % (0.029) |
| vermeer, bend rows behind her within 3 cm of the wall | 47 % | 0.7 % | 15 % | 25 % |
| vermeer, whole band sky-valued % / unreached % | 72.6 / 0.3 | 20.8 / 3.9 | 28.0 / 3.7 | 24.9 / 3.4 |
| starwatcher, sky-valued % / unreached % | 50.6 / 0 | 43.2 / 10.3 | 7.3 / 10.8 | 55.1 / 2.1 |
| troll, gap % / forest % in his footprint | 6.0 / 92.4 | 29.8 / 44.7 (RW) | 13.0 / 56.7 | 13.2 / 56.0 |
| sunflowers, sky rows beside the head of 211 / jumps | 211 / 0 | 211 / 1 | 180 / 30 | 211 / 1 |

Vermeer keeps most of §39's gain (56 % of the wall rows at the wall, from 38 %; the plate 0.64 → 0.029; 105 creases in the
wall group, from 146), the troll keeps all of it, the sunflowers are repaired. Starwatcher goes the other way, and the
comparison says why: without the hinge and without the membrane its band is 43 % sky-valued (RW2), with the hinge 55 %,
and §39's 7.3 % was the MEMBRANE's doing -- far from its data the plain's plate is an affine continuation of the plain's
disparity gradient, which runs past the far plain into the sky (d = 0), and the membrane at a millionth of the bending energy
had turned that continuation into 'affine near the data, constant beyond about a thousand texels', which is the far plain's
depth to within the instrument. That was an accident with a constant in it (the crossover length is the weight ratio's square
root), so it is not kept; but it is the same observation as vermeer's runaway plate under RW2 (0.64 where the wall is 0.006):
the plate's affine kernel over-extrapolates beyond its data, in both directions. The construction that answers it without a
constant is §17's error budget carried from the plane to the plate -- the slope trusted only as far as the fit supports it --
and it is the next item.

**Where this leaves the item.** The crease inside the hole stands as built in §39 with two corrections: a crease is hinged only
where it would show (jump x run > tol), and the membrane is gone. Kit unchanged and exact where it was; vermeer's wall behind
the milkmaid 38 → 56 % at the wall (§39's 66 % was partly the membrane); troll 30 → 13 %; sunflowers equal to the arm without
the hinge; starwatcher worse than without it (43 → 55 % sky-valued), for a reason that is not the hinge's but the plate's
far continuation, now isolated. Measured arm: still `comp + reach-group`. Next: the plate's error budget (affine only as far
as the fit supports it), measured first on starwatcher's plain and vermeer's wall under RW2, where the runaway is.

**The error budget, checked before it was built: it would not bite.** The §17 budget rests on the fitted slope's standard
error against the visible step. For a group plate the fit has hundreds of thousands of data texels: on starwatcher's plain
(403 k data, the band up to 710 texels from the data's centroid) the predicted standard error over the whole domain is at
most a tenth of the step; on vermeer's wall group (486 k data, 822 texels) at most 0.88 of it. The affine continuation is
statistically certain everywhere the plate goes; what is wrong with it is the model -- the plain is not a plane out to the
horizon, the wall group is not one plane -- and the data's residual says so (RMS 9e-3 against a noise of 2e-3 on starwatcher,
7e-2 against 4e-2 on vermeer). A budget cannot fix a certain slope. Falsified as a remedy without being wired in; the plate's
far continuation stays an open question of the model, and the reach law (§30) is the bound that exists for it.

## 41. Two remedies checked and falsified, and where vermeer's wall plate still misses (user: "continue", 2026-09-19)

**The plate's error budget** (§40's next item) was checked before it was built and would not bite: with hundreds of thousands
of data texels the fitted slope's standard error over the whole domain is at most a tenth of the visible step on starwatcher's
plain and 0.88 of it on vermeer's wall group, 800 texels out. The affine continuation is statistically certain; the model is
what is wrong (the data's residual is four to five times the noise). Falsified without being wired in.

**Speck absorption** (the bend's top crease, hidden by slivers, §39): for the crease detection a speck face took the
qualifying neighbour it touched most. C3 and L3 unchanged; on vermeer 13 more creases in the wall group, none of them the
one wanted, and the wall rows behind the milkmaid 56 → 50 % at the wall. The wall meets the bend through strips one to three
rows tall and hundreds of columns long -- facets of DA3's fillet, not specks -- whose planes cannot be placed, so no meeting
test can pass them. Removed (rule 7).

**Where the wall plate still misses** (RWC3, 44 % of the wall rows behind her off by more than 3 cm): not at the bend. The
misses sit at rows 250-450, her head and shoulders (60-65 % of those rows off, plate 0.04-0.12 where the wall is 0.006), and
at rows 750-850 (77 %). At those rows the band spans the frame from its left edge to column 657, and the wall group's data
lie to the right of it and above the head only: the plate is an affine continuation across 400-600 texels from one side,
and it drifts -- the same over-extrapolation as §40's, seen now inside the item that was meant to be about creases. The
plane arm is exact there because a face's PLANE, fitted on the whole wall, is flat; the plate, a spline through the group's
data (the receding left wall at d 0.3 among them), is not. The construction this points at is §17's plane prior, per side of
the hinge: each domain texel relaxes toward the plane of the face whose sheet reaches it, at weight 1 / visible step, which
§37 rejected for the unhinged plate because one prior plane could not serve a wall and its floor -- with the hinge, each side
has its own. That is the next item; the kit's curved surfaces (S2, L1's leaves) are its regression bar.

## 42. The group plate's plane prior, per sheet and budgeted (user: "continue", 2026-09-19)

**The construction** (`--group-prior`). §17's plane prior, brought to the group plate the way §41 pointed:
every texel of the plate's domain relaxes toward the plane of the group's sheet whose entry is nearest to it (the sheet that
reaches it), against the data at 1 / sigma. §37 had rejected one prior plane for a whole group -- a wall and its floor are not
one plane -- and with the hinge (§39) that objection is gone: each side of a crease has its own sheet and its own plane. The
weight is §17's budget: 1 / sqrt(step^2 + se^2), se the sheet's own fit's predicted standard error at the texel, which grows
with the distance from its strip. A wide flat wall therefore holds its plane far into the hole; a facet's slab, whose fit
supports its slope only a few texels out, lets the plate interpolate as before. The unweighted form (1 / step everywhere) was
tried first and is falsified on S2 (0.003 → 0.020 m: the floor+box halves are facets, and slabs came back); the budgeted form
gives S2 0.004.

**On the kit** (medians of the band's error against truth, m; RWC = §40's arm, RWCP = with the budgeted prior; RG = the
measured arm):

| scene | RG | RWC (§40) | RWCP (prior) |
|---|---|---|---|
| C1 / C2 (bg) / C3 (p90) | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.0000 (0.0005) | 0.000 / 0.000 / 0.0000 (0.0001) |
| L1 median / hidden layer | 0.015 / 0.046 | 0.0105 / 0.008 | 0.0110 / 0.010 |
| L2 / L3 / L4 background | 0.000 | 0.000 | 0.000 |
| S2 / S9 / S26 | 0.000 / 0.000 / 0.028 | 0.0028 / 0.000 / 0.000 | 0.0040 / 0.000 / 0.000 |
| S15 | 8.12 | 1.30 | **0.27** |

Nothing regresses beyond a millimetre (L1's layer 0.008 → 0.010, S2 0.003 → 0.004); S15 -- the canopy behind its own trunk,
the kit's standing casualty since §22 -- goes 1.30 → 0.27 m: the canopy's fragments hold their planes where the plate had
drifted.

**On the pictures** (RW2 = the arm without the hinge, same solver; RWC = §40; RWCP = with the prior):

| picture | RG (measured arm) | RW2 | RWC (§40) | RWCP (prior) |
|---|---|---|---|---|
| vermeer, wall rows behind the milkmaid within 3 cm of the wall (plate median) | 99.9 % | 38 % (0.64) | 56 % (0.029) | **99.0 % (0.007)** |
| vermeer, bend rows within 3 cm of the wall | 47 % | 0.7 % | 25 % | 44 % |
| vermeer, whole band sky-valued % | 72.6 | 20.8 | 24.9 | 69.7 |
| starwatcher, sky-valued % / unreached % | 50.6 / 0 | 43.2 / 10.3 | 55.1 / 2.1 | 67.9 / 2.2 |
| troll, gap % / forest % in his footprint | 6.0 / 92.4 | 29.8 / 44.7 | 13.2 / 56.0 | 21.2 / 69.0 |
| sunflowers, sky rows beside the head of 211 / jumps / band sky-valued % | 211 / 0 / 98.3 | 211 / 1 / 39.1 | 211 / 1 / 38.8 | 163 / 23 / 66.1 |

Vermeer's wall behind the milkmaid is now the plane arm's: 99.0 % of the wall rows at the wall, the plate itself 0.007 with
p90 0.009 where the wall is 0.006, the bend rows 44 % against the plane arm's 47 %, the whole band's sky-valued share 69.7
against 72.6 -- the first plate arm to match `comp + reach-group` on this picture, while keeping what the plate alone gives
the kit (L1's layer 0.010 against the planes' 0.046, S15 0.27 against 8.12). The other three pictures are mixed and say what
the prior is: it is the plane arm's behaviour brought into the plate, so where the plane arm is wrong the prior is wrong the
same way. Starwatcher's band goes further into the sky (68 % sky-valued: the plain's sheets' planes run to the horizon, as
they do under RG at 51 %), which is §34-35's far-plain question and no arm's gain; the troll's footprint gets more forest
(56 → 69 %) and more gap (13 → 21 %) as the leaves' planes take over from the interpolated layer; the sunflowers' rows beside
the big head lose 48 of 211 to the field facets' planes at d 0.08 while the band as a whole moves toward the plane arm
(39 → 66 % sky-valued, RG 98).

**Where this leaves the arm.** `wrap + reach-group + group-plate + ramp + crease + group-prior` is now exact or near it on
every kit scene including S15, and on vermeer it equals the measured arm behind the milkmaid. It is not adopted as the
measured arm: on starwatcher, the troll and the sunflowers it is between the plate and the plane arms, worse than the plane
arm on the sunflowers' head rows and than the plate on the troll's gap, and the measured arm's numbers there stand. What
separates them is the same list as before, none of it the plate any more: the far plain behind starwatcher's figure (a thing
at 176°, §35), the forest groups' data (the troll), the field's facets beside the sunflowers' head. Measured arm today: still
`comp + reach-group`. The prior's unweighted form is falsified and removed; the budgeted form is the rule behind
`--group-prior`.

## 43. Starwatcher's far plain: why 178°, and two forms of the wrap test probed (user: "keep going", 2026-09-19)

**Why the far plain is a thing at 178°** (`WRAP_DUMP=1`, `bleed/wrap_normals.py`). The unit is the far plain AND the hills
behind it, one join component (their depths grade into each other, d 0.005-0.026). Its stepped front is its silhouette against
the sky: the hills' outline above, and the plain's own horizon, a nearly straight line at rows 451-455 across 490 columns.
The unit's centroid is at row 451: half its texels are hills above the horizon, half plain below, so the horizon runs
THROUGH the centroid, and ten of its texels lie one to four rows below it. Directions from the centroid to a line through
the centroid span a half turn exactly; the ten texels make it 182°, gap 178°, a thing by two degrees. The near plain
(seg 2), whose horizon lies well above its centroid, is a surface at 191°. The rule is not wrong about its own statement; the
statement -- directions from the centroid -- is fragile when the unit's mass straddles its front.

**Form 2, outward normals** (the direction from each front texel to the far-side texel across the step, 'wrapped' when two
opposite normals exist): falsified at once. Raster normals along any sloping silhouette come in all four kinds; on
starwatcher the near plain has 8 left and 77 right normals among 921 up and becomes a thing, so does every horizon with a
bump in it (L2's ground, L3's floor). Counting cannot be made robust without a constant.

**Form 3, the turning of the front** (`bleed/wrap_turn.py`: the unit's contour traced, the tangent's signed rotation
accumulated along its front runs; wrapped when the net turning reaches a half turn). On the kit it is the right statement:
L3's figure body +224°, its head +307°, the cluster's things +180 to +307°, C2's figure +199°, L2's heads +273 to +360°, the
grounds and walls 0°. On the pictures the quick tracer is not yet the construction: it traces one outer contour per unit, so
a unit in many pieces (vermeer's seg 2, two contour points) or whose front lies on its HOLES (the troll's forest: 0 front
points on the outer contour, 664 k texels) reads nothing, and noise runs on a long horizon accumulate (starwatcher's near
plain +283° over 26 runs). What it needs is the full contour set (outer and inner, per piece) and the turning summed over
all of them, which is the discrete Gauss-Bonnet of the front: a figure's front turns +π, a disc's +2π, a horizon's 0 whatever
its bumps, and a forest's holes each −2π. That is the next form to build, and starwatcher's far plain and near plain, with
L2-L3 and C2 as the bar, are its measurement. Nothing in the classifier is changed in this section; the dump and the two
instruments are kept.

**Form 3 over all contours** (`bleed/wrap_turn2.py`, cv2's contours, outer and holes, every piece, tangent over five
texels): built and falsified as it stands. The kit's figures and discs stay right (L3 −233 to −298°, C2 −217 / −307°, L2's
heads −278 to −360°, L3's floor −114°, grounds and walls 0°), but on the pictures a ROUGH horizon turns: starwatcher's near
plain −263° over 26 front runs, its far plain −306° over 32. The reason is the run structure itself: on a rough edge the
front texels are the convex parts (the bumps that stand in front of the far side by a step) and the valleys between them
are joined or below the step, so summing the turning inside the front runs alone keeps every convex arc and drops every
concave one -- a bias, not noise, and it grows with the roughness. The corrected form must integrate the turning across
the non-front gaps between front runs as well (from the first front point to the last around each contour), where a
horizon's bumps cancel and a figure's foot-to-foot arc does not; the ends of that span carry the raster's ±90° corner turns,
which are the size of the decision, so the tangent's smoothing length at the ends is where its care goes. Left there.

**Where the arm stands.** Measured arm: `comp + reach-group`. The plate arm `wrap + reach-group + group-plate + ramp +
crease + group-prior` is exact or near it on every kit scene and equal to the measured arm on vermeer; what keeps it from
adoption is starwatcher's far plain (this section's construction), the troll's data-poor forest groups, and the sunflowers'
field facets beside the big head.

## 44. The wrap test as turning and as enclosure: both built, both falsified; the centroid form stands (user: "yes continue", 2026-09-20)

**What was built.** §43 ended with the turning form named: the front's span around each contour (from the first front texel
to the last, i.e. the contour less its largest run of non-front texels), the tangent's rotation -- smoothed over five texels
so a raster corner splits between span and gap -- summed over the span and over all of a unit's contours (outer and holes,
every piece, cv2), a thing when the sum reaches a half turn in magnitude. It went into `sheets.py` as `--thingrule turn`
and was run as the classifier alone (`CLASSIFY_ONLY=1`) on the kit and the four pictures beside the centroid form (`wrap`).

**The turning form, falsified in one pass.** On starwatcher it does what it was built for: the far plain +171°, the near
plain −95°, both surfaces, the figure +2228° a thing. On the kit's clean figures it is right (C2's figure −217°, its head
−307°; L2's heads −289 to −364°; L3's figures −233/−298/−191°; grounds and walls −90 to 0°). But the half turn is EXACTLY the
turning of a thing standing on a straight contact with vertical sides -- a box on a floor is two right-angle corners --
so every thing that widens toward its contact falls under it, and that is most of the things there are: vermeer's milkmaid
−179° (surface), the sunflowers' big head −180° (surface), the troll himself +78° and his stick −172° (surfaces), L3's two
boxes −180° each, numerically under π. The centroid form has margin on exactly these (a figure's sides run below its
centroid: milkmaid 71°, head 179°, troll 96°); the turning form has none, because its threshold sits on the common case
instead of between the cases. Removed (rule 7); the instrument `bleed/wrap_turn2.py` stays.

**The enclosure form** (`--thingrule enclose`, `bleed/wrap_enclose.py`). The same span, closed by the chord between its
ends; the unit is a thing when more of its own texels lie inside its closed spans than outside -- a figure on the ground is
everything above its contact, a disc all of itself, a horizon's slivers above its chord are not the plain. As the classifier
alone it is right everywhere the turning form was wrong and where it was right: milkmaid 86.9 %, vermeer's table 54 %,
basket 96 %; the big head 53 %, the sunflowers' labelled things 78-100 %; the troll 75 %, his stick 99.8 %; L2's heads
94-100 %, L3's figures 87-99 %, its boxes 78 / 67 %, its table 53 %, C2's figure 97 %, head 99 %; grounds, walls, floors and
skies 0-16 %. And starwatcher's far plain reads 35.6 % (the near plain 15.7 %): both surfaces, which is what the item was
after. Verdicts identical to the centroid form's on C1, C2, C3, L2, L3, S2, S9, S26; changed on L1 (9 → 5 things, all small
components), L4 (16 → 12), S15 (14 → 13), starwatcher (14 → 10), room (96 → 91), vermeer (22 → 23), troll (17 → 14), so
the plate arm (`comp + reach-group + group-plate + ramp + crease + group-prior`) was rerun under it on those seven only.

**Falsified by L4.** L4's largest far unit (144 k texels, d 0.265) is the leaf CANOPY: one connected component of leaves
before the sky wall, porous, its front on its hundreds of holes and on its outer edge. The centroid form calls it a thing
(gap 162°: from its centroid the sky is seen in every direction through the holes) and its band stays sky, exact
(background median 0.000, mean −0.002, fill d median 0.000). The enclosure form calls it a surface at 43.8 %: a hole's closed
span encloses the hole -- sky, no leaves -- so the holes count for nothing, and the outer contour, cut by the frame on both
sides, has a diagonal chord. As a surface its sheet spreads over the sky band: background median still 0.000 but mean
−0.031, fill d median 0.077, the error map red under every leaf, the band's truth median 0.000 → 0.006 m. A porous thing is a
thing precisely because the far side is seen THROUGH it, and enclosure by the unit's own mass cannot see that; the centroid
form can. L1 (the forest, its big component 70.8 %, a thing either way) and S15 are unchanged to the texel.

**On the pictures** (fillcheck / trollfill / headfill; RG2 the measured arm, RWCPb the plate arm under the centroid form,
RECPb the same arm under enclosure):

| picture | RG2 (measured arm) | RWCPb (plate arm, centroid form) | RECPb (plate arm, enclosure) |
|---|---|---|---|
| starwatcher: sky-valued % / unreached % / fill median d | 50.6 / 0.0 / 0.020 | 67.9 / 2.2 / 0.002 | **16.4 / 34.7 / 0.316** |
| troll: gap % / forest % in his footprint | 6.0 / 92.4 | 21.2 / 69.0 | **37.3 / 51.4** |
| sunflowers: sky-valued % / unreached % / sky rows beside the big head of 211 / row jumps > 1 step | 98.3 / 0.1 / 211 / 0 | 66.1 / 7.4 / 163 / 23 | **38.4 / 9.1 / 166 / 36** |
| vermeer: sky-valued % / unreached % / fill median | 72.6 / 0.3 / 0.009 | 69.7 / 3.6 / 0.009 | 69.9 / 3.7 / 0.009 |

Vermeer, whose verdicts changed only on small components, is the same arm to the decimal. The three pictures whose big units
changed all go the wrong way, and starwatcher -- the item's own case -- goes the worst: with the far plain a SURFACE its band
is not filled by the plain, it is a third unreached and near-valued where it is reached (fill median 0.316 against the plain's
0.03: the plain's group plate, now asked to serve a band the size of its own front, is held by data on one side only and runs
off, and the pieces no data touches are left out). The classifier's verdict was the item's premise -- "the far plain is a
surface, so its sheet will fill the band" -- and the measurement says the verdict alone does not do that; the measured arm
fills the same band at 50.6 % sky-valued with a different rule for things (`neighbour`) and no group plate. The troll loses
because his forest component (668 k texels, a thing by the centroid form at 143°, 0.5 % enclosed) becomes one surface whose
plate has no data in his footprint (gap 21 → 37 %); the sunflowers because their far field's holes onto the sky are the same
porous case as L4's canopy.

**Where this leaves the item.** Three statements of "the front wraps the unit" have now been measured against the centroid
form: turning within the front runs (§43: a rough horizon keeps its convex arcs), turning over the span with the half turn
(this section: the threshold sits on the standing thing), and enclosure of the unit's mass by the closed span (this section:
blind to a porous thing, L4). Each fixes starwatcher's far plain and each loses something the centroid form holds, on the kit
or on the pictures' own things. The centroid form stands as the classifier of the plate arm; starwatcher's far plain --
a unit of plain and hills whose horizon runs through its centroid -- stays its one known miss, and the record says the
remedy is not another statement of wrapping at the unit level but a unit that is not plain-and-hills in the first place
(the join law puts them together because they meet without a step). Both rules are out of the code (rule 7); the two
instruments stay. Measured arm: `comp + reach-group`, unchanged.
