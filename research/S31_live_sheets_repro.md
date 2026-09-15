# S31 — The user's live sheets of 2026-09-15, reproduced headlessly (`harness/live_repro.js`)

Two debug contact sheets from the user's screen (build v3.13.63-a232; poses cam = (0.220, 0.043, 0.200) = 45.2°, 4.2° outside
the 45° cone with fade off, and (−0.097, 0.023, 0.200) = 26.5°; plate = plane/wash/off/off/35/off/stretched/off/cur; the
realtime contract's inpaint on, method pull-push). Reproduced with the app's start-up defaults, the Build button, the same
poses, once with the repo's 8-bit `defaultImgDepth.png` (the file the user's copy auto-loads: quantum 1/255, 2 clones) and once
with `depth_da3mono16.png` (quantum 1/65535, effective 1/568, 0 clones). Shots in `s31/`.

**Reading the sheets.** "gap mask (white = hole)", "scene color (pre-inpaint)" and "FG only (holes = plug demand)" are the
*demand* of the realtime contract — where the foreground is absent behind a silhouette at that pose and the plate must
supply — not black on the screen; the white side bands are the landscape canvas beyond the portrait picture. What the
viewer sees is the "live canvas" / "POSE …: live composite" panels. In the reproduction the live canvas has **no black
inside the picture** at either pose with either depth map. What it does show, and what the user's sheets show too:

1. **The frame edge stretched** at 26.5°: with margin off (today's default, at the user's word) the picture's border column
   is not torn open but drawn stretched across the gap the margin strips used to fill — horizontal streaks off the left edge
   (both depth maps; wider with the 8-bit map). A gap in the "off" mode: the border should tear like a rim (fold-alpha,
   the a165 ratio) or be covered; it should not stretch.
2. **The wash strips** behind the woman and the troll at 45°: the placeholder that awaits the diffusion model, with the
   per-line far field's row structure visible in it ("BG plug only": horizontal streaks). Not holes — content the pipeline
   has not yet painted, drawn on a depth field that disagrees row to row.
3. **Skins at silhouettes** (seams = stretched): the S20 trade, chosen for silverwarrior's holes; on the troll they read as
   foreground stretched to background.
4. The 45.2° pose is outside the envelope the band was built for; with fade off the app itself labels it "viewer sees BLACK".

**Depth file.** The user's copy auto-loaded the repo's 8-bit map. `defaultImgDepth.png` is now the DA3 16-bit map
(app `4aa6898`); the 8-bit one is `depth_8bit_repo.png`.

**Consequences (see the reply of 2026-09-15):** tear the frame edge under the fold rule when margin is off; offer the 2-D
clamped plate (S25 §4: equal to the per-line law on truth, streak-free by construction) as the far-field construction for
the eye; seams torn + fold-alpha as the alternative to the skins — all judged on the live canvas.
