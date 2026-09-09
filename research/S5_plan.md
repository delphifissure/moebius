# Decision brief after Sprint 5 — advantages and disadvantages, then the plan that follows

Everything below is on `main` behind the plane arm's flags; nothing is a default yet. Numbers are
from `research/S5_photograph_note.md` (§5–§7). Each decision lists the options, what the
evidence says, and my recommendation; the plan at the end is written for the recommended choices
and changes with yours.

## Decision A — the placeholder colour in the reveal: flat wash or mirrored far side

The plate texel behind a foreground texel needs a colour until the texture stage paints it.

**Option A1 — rim wash (current default).** The mean colour of the rim window on the far side,
blended across the reveal by a membrane (a smooth gradient between the rim colours).
- Advantages: never a foreground clone; no structure invented, so nothing false to unlearn when
  the SD stage paints over it; smooth, reads as "something is there" without drawing the eye;
  cheap (2–4 s on the photograph).
- Disadvantages: a flat grey-brown patch where the cave has texture — it reads as a patch at
  the larger poses; on the kit its colour error against the truth is 65 /255 mean (S15), worse
  than a clone would be on the crown's leaves (93 vs 20 on leaf sides).

**Option A2 — mirrored far side (`_selfSample=1`).** Each carrier takes the source colour of the
texel the same distance beyond the rim, inside the far run (mirror padding of the visible far
surface), fixed as a boundary value for the membrane.
- Advantages: the reveal shows the far surface's own texture, so it reads as continuation rather
  than a patch; on the kit the colour error halves (65 → 32 mean, 57 → 18 median), and on plain
  backgrounds it quarters (33 → 13); still never a foreground clone (it samples the far run).
- Disadvantages: mirrored one row at a time, so the fill is horizontally streaked (the sheet you
  have); a reflection is a guess that is right for repeating textures (grass, brick, cave) and
  wrong for anything with structure (a doorway would appear twice); where the far side is the sky
  or a different object it is still no better than the wash; and a textured placeholder can make
  the SD stage's job look done when it is not.

**What I do not know:** how each looks in motion on your screen; the kit says A2, the risk is
visual (streaks and doubled structure).

**Recommendation:** A2 as the default placeholder, with the streaks smoothed (mirror a small
window along the rim rather than one texel — the plane law's own rim window, no new constant),
and A1 kept as the fallback where the mirror leaves the far run. If the streaks still read as
artefacts on your screen, A1.

## Decision B — the picture's margins: plug margin 1, 2, or off

At off-axis poses the picture vacates a strip on one side (nothing follows the far content in).

**Option B0 — off.** Empty strips (the magenta in the sheets).
- Advantages: honest; nothing drawn where the picture never was.
- Disadvantages: a hard hole at the frame edge at every pose; the rim arm never had it.

**Option B1 — `_plugMargin=1` (strips across the whole window).** Four strips replicate the border
texels' depth and colour outward, drawn wherever the window is.
- Advantages: fills every margin and corner (bottom-right 1 244 → 31 undrawn); also stands behind
  interior holes as a backdrop (395 → 28 at 0.5).
- Disadvantages: a portrait picture in a landscape window gets streaked bands of border colour
  across the whole window (M = 570 texels), which is most of what you see beside the picture;
  the backdrop hides real holes from measurement and from you.

**Option B2 — `_plugMargin=2` (strips clipped to the picture's rest rectangle).**
- Advantages: fills the vacated strip and the interior holes inside the picture's own rectangle
  (left strip 1 643 → 368; interior 395 → 17 with step faces), draws nothing outside it.
- Disadvantages: the part of a vacated corner that lies outside the rest rectangle stays empty
  (bottom-right 1 244 → 632); still a backdrop behind interior holes.

**Recommendation:** B2. The window outside the picture is the app's frame, not the picture; a
wash there is more distracting than nothing. If you want the corners closed too, B1 with the
window area beside the picture masked is a small change.

## Decision C — how big the texture band should be (what the SD stage will paint)

At ±45° on a 0.06 m volume the honest band on the photograph is 47 % of the picture; carriers
55 %. Nothing in the demand is padding any more (the torn quads that used to hide it are gone).

**Option C1 — keep the envelope and volume; accept 47 %.**
- Advantages: the experience you designed (the full head range, the depth you chose) with every
  reveal covered; the band is exact to the sweep grid.
- Disadvantages: the SD stage paints half the picture; large inpaints hallucinate more and cost
  more; the atlas is big.

**Option C2 — shrink the envelope (e.g. ±30° horizontal).** Band scales roughly with the
relative slide, i.e. with tan of the half-angle: 45° → 30° is ×0.58 on the slide, so a band in
the high 20s of percent (to be measured, not assumed).
- Advantages: smaller atlas and fewer hallucinations; the poses most heads spend their time in are
  inside 30°; the fade already softens the rim.
- Disadvantages: less parallax at the extremes; the envelope was a design decision (Sprint 2a).

**Option C3 — shrink the volume (outer + inner).** The reveal width is proportional to the depth
difference across a rim; halving the volume roughly halves every reveal.
- Advantages: the biggest lever on band size; also reduces stretch on grazing surfaces.
- Disadvantages: flatter picture; the volume is the depth impression you tuned.

**Option C4 — paint less than the band: SD only the *visible* part at the working poses (e.g.
inside 25°), wash beyond.** The sweep already knows per texel at which pose it is first
uncovered (f0), so the band can be tiered.
- Advantages: the SD budget goes where the head is; the rim keeps the wash; no geometry changes.
- Disadvantages: a visible change of texture quality past the working range; needs the tiering
  built (small: it is the arrival pose the plane law already computes).

**Recommendation:** C1 for geometry (do not change the experience for the atlas) and C4 for the
texture stage when it comes: tier the band by first-uncover pose so SD paints the inner tier and
the wash covers the rest. Measure C2 once (one photograph bake at ±30°) so the trade is a number.

## Decision D — 16-bit depth for photographs

**Option D1 — re-export the estimator's output at 16 bits (`harness/depth16.py`).**
- Advantages: on the kit's 8.6 m scene the 8-bit quantum wrecked the far depth (median 3.4 m vs
  0.18 m); the app already ingests 16-bit PNG; the script exists and is tested; nothing in the
  bake changes.
- Disadvantages: needs the estimator's float output (a change in your export step, not in this
  code); the troll's depth has no float source, so it stays as it is until re-run.

**Option D2 — stay 8-bit.**
- Advantages: nothing to do.
- Disadvantages: far-field depth on every photograph is bounded by the source, and the plane
  law's rims fire on 8-bit terraces (the S1 finding, still true).

**Recommendation:** D1, as soon as the estimator can be re-run. Tell me the estimator and its
output format and I will make the script's defaults match it.

## Decision E — step faces on, and their look

**Option E1 — `_stepFaces=1` (built).** A quad across every rim between parallel lines.
- Advantages: closes box sides and return faces (S2, S16 sheets), the geometry the kit could
  not score and you named as a step; no constant.
- Disadvantages: each face is the mean of its two rim texels, so a checkerboard gives horizontal
  stripes; on the photograph most "steps" are estimator notches and the faces change little; a
  false positive (two parallel surfaces that are really separate) would draw a face between them.

**Option E2 — off.** Open jumps everywhere.
- Advantages: nothing invented. Disadvantages: the sides stay holes.

**Recommendation:** E1 with the face coloured by the rim window mean (smooth) instead of the two
texels; the same change as the A2 streak fix.

## Decision F — the Shih pre-filter for soft edges

- Rooms: it helps (S2 σ 1 precision 0.824 → 0.885, depth exact; S31 recall back to 1.000).
- Open scenes with curved far surfaces: it hurts (S15 0.184 → 0.696 m even with the corrected
  mask), because the rim law's join spares planes but not curvature.
- Options: F1 never (current); F2 a per-picture switch you set; F3 make it safe by a join that
  spares smooth curvature (a rim-law change: a second-difference rescue over a longer window,
  tested on S15's hills and the photograph's ramps).
- Recommendation: F1 now, F3 as the next rim-law item if fringes bother you on screen; F2 is a
  knob you would have to guess.

## Your decisions (recorded)

- A: build both; the placeholder (wash / mirrored far side) is an option at bake time.
- B: build both; the margin (off / picture / window) is an option at bake time.
- C: tier the band by first-uncover pose, and offer "paint it all" as the option.
- D: deferred, not forgotten — 16-bit export is important; it stays as a standing item in the
  note (§7) and in this plan until done.
- E (step faces) and F (Shih) not asked: step faces become a bake option too (on by default in
  the plane recipe, smoothed); the Shih pre-filter stays in the kit, off.

## The plan that follows your decisions

**Where options live.** The app has no settings loader; bake choices are `<select>`/`<input>`
elements in the Debug View row of `moebius.html` (L276–306: `bgModeSel`, `bgGapRuleSel`,
`bgLayerBuildBtn`, `bgSeedModeSel`…) read either in `_wireDebugSheetControls`
(moebius.js ~L19601–19691, which sets `window._*` before calling
`window._plugGeoBand({flush, observed, gateAPriori})`) or straight from the DOM at bake time
(`bgSeedModeSel` at ~L16598). No dat.GUI, no persistence beyond two localStorage keys. The
harness host `harness/scratch_moebius.html` mirrors the page and `harness/moebius.js` is a copy
of the app file, so the HTML change is mirrored there.

1. **A "Plate" option group in the Debug View row** (`moebius.html` next to `bgGapRuleSel`; the
   handler in `_wireDebugSheetControls`), one `<select>` each, applied by setting the existing
   `window._*` flags before the recipe's `_plugGeoBand` call and stamped on the HUD like
   `bgRelaxModeSel`:
   - Far side: `membrane` (S2b.4) / `plane` → `_farRule`.
   - Placeholder: `wash` / `mirrored far side` → `_selfSample`.
   - Margin: `off` / `picture` / `window` → `_plugMargin` 0 / 2 / 1.
   - Step faces: `off` / `on` → `_stepFaces`.
   - Texture band: `paint all` / `inner tier` with a degrees field (default the fade-start angle
     already in the app, so no new constant) → `_bandTierDeg`.
   - Sky at infinity: `auto` (on when the map has sky-class texels) / `off` → `_skyInf`.
   Defaults keep today's behaviour until you choose; the choices are remembered in
   `localStorage` under one key (`bgPlateOptions`), the same pattern as `bgDeviceFov`.
2. **Smoothing for A2 and E** (moebius.js): the mirrored sample and each step face take the
   mean over the rim window (`farRimW` along the rim) instead of one texel — removes the row
   streaks and the checkerboard stripes. Verify: S15 colour error table, troll and S2 sheets.
3. **Band tiering (C)**: `_plugCpuSweep` records per texel the smallest pose fraction at which its
   copy is demanded (`bandPose`, from the pose grid; poses run rim-inward so the first hit is the
   minimum); `_plugGeoBand` exports `_qbBandPose`; the texture-stage band = texels with
   `bandPose ≤ tan(tierDeg)/tan(envelopeDeg)` when a tier is chosen, else all. The probe dumps it;
   `check_app_band.py` reports band size per tier. Verify: histogram of the photograph's band by
   first-uncover angle (how much opens inside the fade-start angle).
4. **One measurement for the envelope** (informational, no change): the photograph at ±30°
   horizontal, band and undrawn pixels, appended to the note.
5. **Sheets and kit**: photograph at the four poses for each option value that changes pixels
   (wash/mirror, margin off/picture/window, steps on/off); the eight kit scenes once with the
   recipe defaults; both repos committed and pushed; `research/S5_photograph_note.md` §8.
6. **Standing item (D)**: 16-bit re-export of the photograph's depth with `harness/depth16.py`
   once the estimator's output format is known — carried in the note until done.

1. **Rim-window colour for faces and mirror** (small): step faces take the rim window mean; the
   mirrored far side samples a window along the rim (the plane law's `farRimW`) instead of one
   texel. Files: the `S5 STEP FACES` block and the self-sample block in the S3 colour code
   (moebius.js). Verify: S15 colour error (kit), the troll sheet at 0.25/0.5 without streaks.
2. **Defaults for the plane arm's recipe** — still behind `_farRule='plane'`, but the recipe sets
   `_plugMargin=2`, `_stepFaces=1`, `_selfSample=1` unless you say otherwise after the sheets.
3. **Band tiering by first-uncover pose** (C4): the sweep records per band texel the smallest pose
   fraction at which it is demanded; exported with the band (`_qbBandPose`); the texture stage
   later takes a threshold you choose. Verify: a histogram on the photograph (how much of the
   band opens inside 25°).
4. **One measurement for C2**: the photograph baked at ±30° horizontal envelope (the S2a flag),
   band and undrawn pixels, so the envelope trade is a number in the note.
5. **16-bit**: on your estimator's format, set `depth16.py` defaults; re-export the troll if the
   float output exists.
6. **Report**: `research/S5_photograph_note.md` §8 with the decisions and their evidence; CODEMAP.

Verification for each step as in Sprint 5: photograph sheets sent, kit table appended, both
repos committed and pushed.
