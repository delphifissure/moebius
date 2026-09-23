# S59 — The sheet A/B, run under a stopping rule fixed in advance (2026-09-23, DRAFT: results pending)

**Question.** The per-line law fills each row of a hole on its own, and its holes comb (S33 class 1; four attempts to
fix that inside the per-line law, S22/S32/S51/S58, moved numbers but not the picture). Should the S35 sheet model
replace it? Or, if not, what ships? This is S37 Phase C, planned three times and never run (S57 §2).

**The standard (the user, 2026-09-23).** This stage exists to hand diffusion **clean holes**: plausible but clean
depth, a plausible wash for the colour, SD doing the texture later. **A noisy atlas is the failure.** The bar is clean
and plausible, not accurate.

**The rule** is S37 Phase C, second edition. It was fixed and committed before any frame was rendered: `271b42d`, then
the pre-render amendment below.
- Three arms, one wash, blind L/M/R.
- The user is asked one question per picture: "which is cleanest?"
- If the sheets win on at least 3 of 4, port them. Otherwise geometry research stops and the cleaner of per-line and
  plain fill ships.

## 1. Arms, inputs, poses

| | band depth | notes |
|---|---|---|
| A | the per-line law, the app's own plate | start-up defaults, no flags |
| B | S35's measured arm RWCPh (`--no-tps --things --closure comp --thingrule wrap --reach-group --group-plate --ramp --crease --group-prior`) where a sheet owns the texel; C elsewhere | `research/s35/sheets.py`, unchanged |
| C | a membrane per band component, pinned at the background edge to arm A's value there, free elsewhere | `harness/sheet_ab_fields.py` |

The wash is identical on all three arms. It is the same membrane per RGB channel, pinned at the same edge texels to the
colour of the per-line law's own far rim (`farRimJ`/`farRimW`). Plate 2 is hidden on all three.

**Inputs.** All four pictures use their own DA3-16 maps with no repair: the troll's default map, and `batchB/*_da3_16.png`
for the others. Starwatcher's S35 arms ran on a depth-repaired map (`starwatcher_fix2`); this test does not use it
(rule 3). `--step`/`--q` is each picture's visible step 1/k from the app's `[S10]` line.

**Object maps.** Arm B uses the maps S35 measured with:

| picture | map | prompts |
|---|---|---|
| troll | `view_troll_v2` | hand clicks (six points) plus automatic |
| vermeer | `view_vermeer` | hand clicks (fifteen points) |
| sunflowers | `view_sunflowers_auto` | fully automatic |
| starwatcher | `view_starwatcher_auto` | fully automatic |

So on two of the four pictures arm B had human segmentation input that arms A and C did not have (see §6).

**Poses.** The camera sits at z = 0.2.
- Decision: yaw ±42° (x = ±0.180, y = 0.008; the "p45" of every S35/S53 frame, inside the 35–45° fade).
- Context: yaw 22.5° and pitch +30°.
- The decision sheet also shows the hole's depth itself as a relief: the atlas.

**Pipeline** (the app repo's harness, commit `c1cf899`):
- `streak_class.js` → dump;
- `sheets.py` → arm B;
- `sheet_ab.js PHASE=rims` → the law's rims;
- `sheet_ab_fields.py` → B, C and the wash;
- `sheet_ab.js` → frames, with guards: the bake band equals the dump band, and the plate equals the dump's far field;
- `sheet_ab_compose.py` → blind sheets and the key.
- `sheet_ab_review.py` → the same frames as a page to flip through (L/M/R only, side by side or in place, every pose
  and the relief). It runs only after compose has recorded the key's hash, and its verdict buttons build the line
  `sheet_ab_decide.py` takes.

## 2. Found before any frame: the plain fill's first specification pinned to the silhouette ramp

As first written, C was pinned to the *non-band* texels next to the hole that lie behind the occluder by two steps (S35
§47's lip test). The builder's guard counts fills that are not behind their occluder. On the troll (the S35-era dump,
before any render) it found **56 246 texels, 22% of the band, in front of their occluder**: a near clone.

The cause is DA3's silhouettes, which are ramps a few texels wide. Measured on the 3 357 ring texels:
- their median is **3.2 steps** behind the occluder;
- they are **37 steps** nearer than the per-line law's value next to them (p90: 280);
- **88%** of them are still descending three texels further out.

The ring was the ramp, not the background.

Two repairs that keep the ring were measured and rejected before the one adopted:
- *Pin only to texels behind every occluder of the component* (so that the maximum principle guarantees behind-ness).
  The troll's largest component loses all its pins, because the band holds ramp texels at d 0.014. Only 102 k of 259 k
  texels stay pinned.
- *Cut components where the occluder's depth jumps.* The ramps shatter into 9 385 sub-regions and only 36% are pinned.

**Adopted** (committed to the rule as a dated amendment before any frame): pin at the band texels on the background side,
to the per-line law's own value there, where the law has just left its far rim past the ramp. Texels still not behind
their occluder, and components with no pin, keep arm A; both are counted. The same repair applies to the wash. The
ring's colour is the ramp's fringe, so the wash takes the colour of the law's rim texel instead.

On the old troll dump this form leaves 4 021 texels (1.6%) to fall back, 17 114 texels in pin-less specks, and cuts the
summed depth jump inside the band from 3.20 M to 0.30 M steps against arm A. That number was taken before the test and is
advisory; it does not enter the decision.

## 2b. Run log: bugs fixed during the run (the rule's "a frame broken by a bug is not a result")

- **Troll, first render attempt, 01:14.** The render guard stopped the run before any frame: the bake's band differed
  from the dump's band by 7 098 texels.
  - The cause was the harness, not the app. `streak_class.js` writes as its band `_qbDisocc ∩ (far field < source
    depth − grid)`. The texels it leaves out keep their own depth: nothing is revealed there.
  - Fix (`1a8c29c`): inject depth and wash on the dump's band, and require the dump band to be a subset of the app's
    band.
  - Re-run guard: subset holds, 7 098 app-band texels outside the dump band (identical on all three arms), plate
    against the dump's far field max |Δ| = 0.
  - No construction changed, and no frame had been seen.

## 3. Frames and the key

All four pictures rendered (troll 02:17, vermeer 03:26, sunflowers 04:28, starwatcher 05:23). Every render guard held:
the bake band matches the dump band (mismatch 0; app-band texels outside the dump band, identical on all arms: troll
7 098, vermeer 1 606, sunflowers 1 636, starwatcher 7 600), and the plate matches the dump's far field exactly (max |Δ| 0).

**The key** (`shots/sheet_ab/key.json`, drawn by `sheet_ab_compose.py` from `os.urandom`, 2026-09-23 after the last
render, before anyone saw a sheet):

    SHA-256 8abe1c3a94441201ef47a45a43788f8d335375e18456dcfca29e441c45d8a82c

**Rule 7 (the arms diverge), checked before sending.** Measured per arm pair, with no side named:
- Band depth: 75–95% of band texels differ by more than one visible step, per picture and pair.
- The frames: at the decision poses, 0.3–3.6% of each frame's pixels differ by more than 8 levels, and the largest
  difference is 104–215 levels.
- Starwatcher's differences are the smallest (0.3–0.9% of pixels), because less of its hole is in view. Its band still
  differs on 86–91% of texels.

No injection missed its band.

## 4. The user's verdicts

*Pending.* One line per picture: L / M / R / no clear difference.

## 5. The decision

*Pending.* It is applied mechanically from §4 and the key.

## 6. What each outcome costs (written before the result)

- **B (port the sheets).**
  - `sheets.py` is 2 020 lines of offline Python: join components, planar patches, the things rule, the layered order,
    per-group clamped plates with creases and a prior.
  - The full bake takes ~9 min offline (S35 §19), against the app's ~66 s bake and a ~2 s target.
  - It needs an object map for every picture. Two of the four test maps used hand clicks, so a port means either the
    in-app SAM click step (Sprint 21, exists) as part of every bake, or automatic maps. S35 §52 measured that choice as
    material on the kit.
  - Weeks.
  - **Measured while waiting (arm B against itself, so nothing is unblinded):** the frozen arm re-run with automatic
    object maps (`view_troll_auto`, `view_vermeer_auto`) in place of the clicked ones.

    | picture | band owned by sheets, clicked / automatic | median difference where both own | band differing by > 10 steps |
    |---|---|---|---|
    | troll | 82% / 64% | 24 steps | 36% |
    | vermeer | 97% / 99% | 0.6 steps | 28% |

    About a third of the hole's depth changes with the map. If B wins, the port must carry the click step (Sprint 21's
    in-app SAM) into every bake, or it ships something materially different from what was judged.
- **C (ship the plain fill).**
  - About 100 lines in the bake: find the background-side edge texels (the existing lip test), take the per-line law's
    values there (the law still runs, as the pin source), and solve a masked membrane.
  - The existing `_screenedPoissonBand` (the return path's solver) pins *every* non-band neighbour, so it needs a
    variant that pins only the background edge. With red-black SOR at 600 iterations, a 400-texel-wide hole will not
    converge, so it needs conjugate gradients or a multigrid.
  - Then the not-behind fall-back, and the wash membrane on the law's rim colours.
  - The bundle already exports the plate depth and colour, so the SD hand-off needs no change.
  - Days.
- **A (keep the per-line law).**
  - Nothing to port.
  - It ships the atlas that combs, which is the failure the user named. If A is chosen, the write-up must say that
    plainly rather than call the geometry done.

## 7. Known biases and limits of the test

- **The mesh's tears are the per-line bake's.** B and C replace the band depth after the bake, as S35's renders and
  Sprint 25's return path both do. Each arm reports how many rim-law join decisions its field would change
  (`render.json`, `retear`). This favours A.
- **The band is the per-line bake's** (`_qbDisocc`), and it is the same for all three arms.
- **C and B both lean on A.** C is pinned to A's values at the background edge, and B falls back to C.
  - C and A therefore agree at the hole's background edge by construction, and differ inside.
  - B inherits C's pins wherever no sheet reaches.
- **Plate 2 is hidden** on all three arms. It is the per-line law's second layer, and the test is about plate 1's band.
- **The wash is the law's rim colour, diffused.** It is not what ships today (the app's own wash is continued per line).
  All three arms carry it, so it doesn't favour any arm, but it also means none of the frames shows today's colour.

## 7b. Queued for after the verdicts (user, 2026-09-23)

- **Fill the pinhole depth spikes in the bake's own band** (S61 §10–§11). The same rule as the bundle mask: an enclosed
  hole at its surrounding band's depth joins the band. It is applied at bake time, so those texels take the winning
  arm's fill and the wash. It changes the band the arms are frozen on, so it runs after the decision and is measured
  before/after, with frames for the user's screen.

## 8. Metrics (advisory, reported only after the verdicts)

`harness/sheet_ab_metrics.py`, per arm, on the plate as rendered, in visible steps:
- band bends over one step and their length;
- **edge cliffs** at the hole's background edge, which answers task #60 ("does the filled band create new cliffs?");
- texels not behind their occluder;
- C's fall-backs and B's owned share;
- the re-tear count.

*Sealed until §4 is filled.*
