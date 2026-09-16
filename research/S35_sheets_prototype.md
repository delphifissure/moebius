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
