# S25 — Sprint 17: stretched plate pixels made transparent, the 60° bake, the far-pose holes re-classed; the clamped plate and AMLE against truth (2026-09-13)

Three of the user's questions from S24 answered by measurement: (4) "why aren't we making over-the-top stretched pixels
transparent?", (3) "dig into the 2-D membrane and AMLE", and the coverage contract of §5 ("bake wider"). Plus the live
pass's panel select for the two recommended rules. Scripts, logs and sheets in `s25/`.

## 1. The rules select (live pass)

`bgPlateRulesSel` in the bake panel: **rules: current | + ceiling cut | + ceiling cut + line despeckle**, driving
`_ceilCut` / `_despeckleLines` from the panel like every other option. Verified: the panel path with "new" is
**byte-identical** to the flag-driven arm on silverwarrior at all five poses and differs from the current arm (a134). The
seven-picture preview (`s25/live_*_sheet.png`, rows: current / recommended / trade) shows the two rules change nothing
visible on these pictures — interior holes per pose equal within a few pixels everywhere — which is what S20 and S23
predicted (no accepted ceiling plane; a few hundred line texels kept). They earn their place on the kit and cost nothing
here.

## 2. The 60° bake does not close the far-pose holes

The coverage contract of S24 §5 said the holes at 52°/24° and 56°/19° were reveals outside the 45° envelope the band was
built for. Baked to 60° (band 14.9 → 16.2 % on silverwarrior, 41.2 → 41.8 % vermeer, 21.3 → 22.0 % room):

| picture | pose | holes, 45° bake | holes, 60° bake |
|---|---|---:|---:|
| silverwarrior | 52°/24° · 56°/19° | 1 308 · 1 636 | 1 223 · 1 460 |
| vermeer | 52°/24° · 56°/19° | 1 334 · 328 | 1 311 · 309 |
| room | 27° · 52°/24° | 347 · 610 | 347 · 612 |

**Falsified for these holes.** Where they are (`p_holewhere.py`): silverwarrior's largest (1 066–1 113 px) sits 41–49 px
from the picture's right edge, 13–17 px from the bottom (the bear); vermeer's (830 + 236 px) 5–9 px from the right edge
(the milkmaid); the room's 5–15 px from its right edge and at its bottom-left corner. For the vermeer and the room the
far side these need lies **beyond the photograph** (a near object at the frame's edge moves inward by more than its
distance to the edge; the margin window covers most of them, S20). For silverwarrior the first reading was the same, and
§5 shows it is wrong: the hole sits inside the bear's own footprint with a complete far side under it. In both cases no
band width creates the missing cover, and "seams + rim stretched" hid it by stretching — the spaghetti of §3.

What can supply beyond-frame content: the margin strips (A245: the plate clamp-extended outward by the border's largest
rim shift, at the border texel's own depth) or, in the 90° box model, the box's side walls, with outpainted content. The
margin-window arm with the stretched seams and the magenta check view (§3) is measured below (§5).

## 3. Stretched plate pixels transparent — the fold-alpha (`window._plateFoldAlpha`)

The A241 per-fragment stretch law existed for the foreground and the object-back layer; the plate was exempt (a126: "the
plate is the backstop, a hole in it has nothing behind it"). Armed on the plate: a fragment whose cell is stretched past
the fold — shift span > cell extent, i.e. stretch > 2 relative to rest (A212/a102; not a tuned constant) — or back-facing
is discarded in the colour pass and the depth pre-pass (value 1), or painted **magenta** (value 2) so the spaghetti pixels
of any arm can be counted. Panel options as the live pass, 45° and 60° bakes, five poses (`s25/s17a_fold_sheet.png`):

| picture | arm | holes 14° · 27° · 45° · 52°/24° · 56°/19° | magenta (spaghetti drawn) 45° · 52°/24° · 56°/19° |
|---|---|---|---|
| silverwarrior | current (stretched) | 6 · 217 · 489 · 1 308 · 1 636 | 1.2 % · 3.7 % · 3.6 % of the picture |
| silverwarrior | fold-alpha, 45° bake | 10 · 250 · 544 · **390** · **633** | — |
| silverwarrior | fold-alpha, 60° bake | 10 · 225 · 689 · **264** · **411** | (60° bake: 1.6 · 3.7 · 3.7 %) |
| vermeer | current (stretched) | 4 · 12 · 6 · 1 334 · 328 | 2.4 % · **8.1 %** · **8.6 %** |
| vermeer | fold-alpha, 45° bake | 13 · 151 · 840 · 3 003 · 1 168 | — |
| vermeer | fold-alpha, 60° bake | 11 · 132 · 839 · 2 757 · 838 | (60° bake: 2.7 · 8.6 · 9.0 %) |

Three findings.

1. **The current default draws spaghetti over 4–9 % of the picture at the far poses** (3.6 % silverwarrior, 8.6 % vermeer
   at 56°), and the 60° bake does not reduce it: it is not envelope-limited. On the vermeer it is the whole region behind
   the milkmaid (the sheet): rows of the plate at different far values stretched into a skin — the per-line far field's
   disagreements, made visible as area.
2. **Making it transparent closes holes on silverwarrior** (52°: 1 308 → 390 → 264 with the 60° bake; 56°: 1 636 → 633 →
   411). Folded plate cells were not only drawing skins: in the depth pre-pass they occluded the valid plate behind them
   (a folded cell spans the depth range between its vertices and wins the depth test wherever it is drawn), so removing
   them from both passes lets the plate that exists show. The remaining holes are the beyond-frame class of §2.
3. **On the vermeer it opens holes** (52°: 1 334 → 3 003): behind the milkmaid there is nothing at the far depth to show
   once the skin is gone. The skin was covering a region where the far field never carried the wall's depth consistently
   across rows. The honest state of the plate there is a hole; the honest fix is the far side, not the stretch.

Also visible in the sheet: with the fold-alpha the sky region left of the warrior shows one-texel horizontal black lines at
the far poses — rows whose far value differs from their neighbours' by more than the fold allows; under the stretched
default these were one-texel skins. Same class as (1), at a smaller scale.

**Where this leaves the option.** Fold-alpha is the correct replacement for "seams stretched" *once the far field is
consistent enough that skins are rare*, because it never shows a stretched pixel and it lets valid plate through where a
folded cell used to occlude it. Today it trades spaghetti for holes on pictures whose far field is row-inconsistent
(vermeer) and is a net gain where it is not (silverwarrior). It stays a flag until the far field's consistency is fixed;
the magenta view is the instrument for that fix (it counts the spaghetti any arm draws, at any pose, on any picture —
the concomitant-motion metric of S24 §2 G in its simplest form).

## 4. The clamped plate per run cluster, and AMLE, against truth and seams (R4 §3–§4, §6)

`s25/sheetfield4.py`, MODE=plate | amle: domain = **run cluster** (rim texels connected through the *same run* along the
axis that joins them, so the run segmentation's creases separate clusters — a wall and its floor are two plates although
their depth is continuous; the first attempt with the join law as adjacency merged them and reproduced §16's failure);
Cauchy data = each rim's run window (the per-line law's own window, raw disparity) fixed; every other boundary natural
(the discrete free edge); the ground as an obstacle (texels that come out behind it fixed at it, re-solved, ≤ 4 rounds);
AMLE by Oberman's scheme from the same strip, obstacle by max. Per-texel arrival and layering unchanged; only a
non-thin, non-ground candidate's *value* is replaced.

| scene | measure | app per-line | plate per cluster | AMLE |
|---|---|---|---|---|
| S2 contact (planar) | truth median / p90 m; seams | 0.000 / 0.043; 4 | **0.000 / 0.043; 3** | 0.000 / 0.044; **302** |
| S15 hill + tree (truth) | band depth median m | 0.184 | **0.188** | 0.375 |
| S15 | seams total (same sheet) | 11 478 (2 413) | 12 264 (**3 709**) | 12 361 (3 612) |
| S26 beams | truth median / p90; seams | 0.000 / 0.056; 3 461 | 0.000 / 0.056; 3 447 | 0.005 / 0.055; 3 500 |
| S16 two walls | truth p90; seams | 0.000; 1 847 | 0.000; **1 662** | 0.001; 2 135 |
| S32 open hedge | (all ground-cut) | 800 | 800 | — |
| photograph DA3 8-bit | seams total (same sheet) | 33 239 (30 542) | 50 928 (**35 503**, +16 %) | timed out (50 min) |
| photograph DA3 16-bit | seams total (same sheet) | 38 078 (24 766) | 44 984 (**30 295**, +22 %) | — |

**The clamped plate with the right boundary conditions reproduces the per-line law where the law is right** (S2, S26, S16,
S32: identical truth; seams −25 % on S2, −10 % on S16, −0.4 % on S26) **and passes the depth bar on S15** (0.188 vs 0.184,
within 0.01 m) — the two things §16's thin-plate could not do. **It fails the seams bar**: S15 same-sheet seams +54 %,
photograph +16 % (8-bit) / +22 % (16-bit). The reason is structural and the same as S22's: the seams are choice
disagreements — adjacent lines served by *different clusters or different sides* — and a field that is smooth inside a
cluster makes the boundary between clusters sharper, not smoother. **AMLE** is worse everywhere it differs (S15 0.375 m;
S2 +298 seams): the discrete infinity-Laplacian with value-only data does not carry a sloped plane exactly, and its
cone-like extension adds edges.

**Closed on the S22 bar; the plate is recorded as the correct 2-D form of the law** (no parameter, exact on planes,
truth-neutral on curved scenes) whose only promised gain — seams — it does not deliver, because the seams are not
within-sheet noise. Nothing built in the app. Together with S22 and §16 this closes the field family on its third,
best-posed attempt.

## 5. The margin-window arm, and where the silverwarrior hole really is

Margin = window with the seams stretched (not "all"), recommended rules, 45° bake; the magenta check view beside it
(`s25/s17a2_margin_sheet.png`):

| picture | arm | holes 14° · 27° · 45° · 52°/24° · 56°/19° | magenta 45° · 52°/24° · 56°/19° |
|---|---|---|---|
| silverwarrior | margin window | 6 · 0 · 475 · 1 336 · **1 686** | 1.4 % · 4.4 % · 4.2 % |
| room | margin window | 149 · 382 · 185 · 598 · 253 | 3.4 % · **11.1 %** · 10.8 % |

**The margin does not close silverwarrior's hole either**, and its position is the same (picture-x 240–296, 78–80 % across,
90 % down). So §2's beyond-frame reading is wrong for this hole: it lies inside the frame, 41 px from the right edge but
well inside the bear's own rest footprint. The buffers under it: the region is the bear (dQ 0.35–0.6, close to the window
plane) beside a 100-texel strip of the far plane (dQ 0.003) and a second near piece to its right; **every bear texel has a
far side** (4 345 of 4 345 carriers, far side = the far plane, 0.003), so it is not a missing far side; the plate under it
is at the far plane everywhere. The CPU sweep at 45° already marks these cells "no owner" (`s20/s13_silverwarrior_classmap_45deg.png`,
the red blobs at the bottom right): in the sweep's own model no source texel, at its own depth or its far depth, lands
there. What closes it: "seams + rim stretched" (a stretch across it); what reduces it by 60–75 %: the fold-alpha (§3),
which means part of it was a folded cell occluding valid plate. **Its mechanism is not yet named** — the candidate is
that a near piece close to the window plane and its far copy at the far plane separate by more than the piece's own
width at 52–56°, so that the far copy slides out from under it and the strip between is owed to source columns that are
themselves a different near object — and it is the first item of the next sprint, with the sweep's owner map at 56° as
the instrument (which texel *would* own each red cell, and whether it exists). Recorded as **hole class X**: inside the
frame, not band width, not margin, predicted by the sweep, closed only by stretching.

The room's 11 % magenta at 52° is the sunflower field's per-line far field stretched between rows (the smears in the
sheets); with the fold-alpha they would be holes. The vermeer's 8 % is the same class. Both say the same thing as §4:
the per-line far field's cross-line disagreement is the largest visible defect at the far poses, and it is a *choice*
problem.

## 6. Where the effect stands after Sprint 17

- The **spaghetti** the user named is measured: 4–9 % of the picture at the far poses under the current default, none of
  it envelope-limited; a check view counts it on any picture at any pose.
- The **far-pose holes** are not band width (60° bake) and, on silverwarrior, not the margin either (§5): vermeer's and the
  room's sit at the frame edge (the margin window covers most of them, S20), silverwarrior's is hole class X inside the
  frame, mechanism to be named with the sweep's owner map.
- **Fold-alpha** is the right mechanism against spaghetti and already a net gain on silverwarrior; it needs a consistent
  far field to be a net gain everywhere.
- The **far field's cross-line consistency** is the open item under all of this (the streaks behind the milkmaid, the
  one-texel lines in the sky, vermeer's 8 %). Four field constructions have failed the seams bar (§10b, §16, S22, this
  plate); the seams are choice disagreements between candidates, so the remaining construction is the **labelling** of
  S24 I3 — a consistent *choice*, not a smoother *value* — with the magenta area, not the seam count, as its bar.
