# S44 — Sprint 24, the live pass: the input contract closed, two arms consolidated, and the envelope measured for the first time (2026-09-21)

S41's second sprint, and the one S37 named as the single most valuable action eleven sprints ago. Four of its six items are
done in code and verified headlessly; one turned out to have nothing to do; one needs the user's screen and now has the
shots to do it with.

---

## 1. The depth-map input contract — the last correctness gap, closed

S19 §3.3 has been open since 2026-09-12: a user can load an ordinary depth PNG and nothing checks it. The app's convention
is **normalised disparity, 1 = near, 0 = far**, and roughly half the depth estimators in circulation write the opposite. An
inverted map does not fail loudly. It parallaxes backwards, which a person reads as "the 3D is broken" rather than "my input
is upside down".

`bgDepthContract()` now runs on every load, on the 16-bit data when the float ingest succeeded and on the 8-bit element read
back through a canvas otherwise. It reports in the console under `[S44]` and, when something is off, in an amber banner over
the picture. **It never changes the map and never refuses it.** Five tests, each stating its assumption:

| test | what fires it | the assumption it states |
|---|---|---|
| polarity | the top decile of rows reads more than 0.10 nearer than the bottom | in an ordinary picture the bottom is nearer than the top; a view looking down, or a ceiling, breaks this honestly |
| flatness | range below 8 quanta or 0.02 | — |
| range used | range below half of [0, 1] | — |
| clipping | more than 25% at d = 1, or 45% at d = 0 | the second is only a fault if it is not sky |
| levels vs the fold limit | one level exceeds the per-texel fold limit at this width | a133 |

**Verified headlessly on five deliberately broken maps** (`harness/s44_contract.js`, seconds, no bake). The last row is worth
recording because the first version of the test was wrong and the contract was right: at **851 px** one 8-bit level is
**0.69×** the fold limit and must NOT warn; at **1920 px** it is **1.55×** and must. a133's ~1250 px threshold is real and
the contract tracks it rather than assuming eight bits is always bad.

## 2. Two arms consolidated into the defaults

`rules` now ships as **ceiling cut + line despeckle**. The bar S41 set was a measured win and no measured cost:

- **Ceiling cut (S23):** S7 precision 0.65 → 0.86, S26 beams 0.46 → 0.82, P6 grille 0.50 → 0.69, and **byte-identical** on
  every scene and picture where no ceiling plane is found — the majority test simply does not fire, which is why the
  vermeer's ceiling is untouched.
- **Line despeckle (S20):** S5 one-texel poles recall 0.51 → 0.98, so wires, thin branches and railings survive. On the
  troll and the six pictures it kept 270–1 070 texels each with no visible change and no clone. S5's precision falls only
  because a one-texel pole's band is a few texels wide against a truth of one, which is the truth being thin.

The storage key moved to `bgPlateOptions.v3` and the old set is **not** read, because a panel saved under the previous
default would otherwise shadow the change exactly once for everyone who has ever touched it. Both the default and the
non-shadowing are asserted in the harness.

**Not promoted, with reasons.** `seams = all` closes the far-pose rim holes (silverwarrior 1 635 → 2 px) at the price of a
skin between every silhouette and its background; the margin modes are clamp-extended edge colour standing in for an
outpaint, and are off at the user's instruction. Both are trades only a screen can price, which is what §5 below is for.

## 3. Nothing was stripped, and that is the finding

S37 asked to strip the dead arms from the bake panel. **There are none.** The falsified work left the file at a169 — "the
falsified work is out of the file, not behind a flag" — and took eight window flags with it. A mechanical scan finds 65 of
the 293 `window._` flags written but never read inside the app, and they are almost all the `_geo*` and `_qb*` arrays the
probe harness reads, so the scan is not evidence of death. Going through the panel option by option against the record, each
remaining arm has a measured for and a measured against, recorded in LIVE_PASS §3. Removing a working option on the grounds
that it is not the default would be the opposite of this project's discipline, so none was removed.

## 4. The rest-versus-envelope difference — a new instrument, and the axis we have never measured

R7 read twenty papers looking for an evaluation built for a viewer like ours and found one. InpaintFusion collected three
numbers: a still rating, a motion rating, and their difference; their planar baselines rated acceptably as stills and
collapsed in motion, and **a static score alone would have ranked the methods almost identically and missed the effect.**
Every instrument this project owns scores the bake or the rest frame.

`harness/s44_envelope.js` bakes with whatever the panel ships — not an arm, the defaults a new user gets — and reports, per
pose, the share of the picture whose colour the bake **invented** (read off the S17 check view) and the share that has gone
**dark**, each against rest.

**Everything is measured inside the rest-pose content rectangle.** The letterbox is 47% of this canvas and the check view
recolours it; the first version of this instrument reported 53% placeholder at rest and was measuring the frame around the
picture rather than the picture. The rect is printed with every run so the correction stays visible.

**The troll, at the shipped defaults** (bake 66 s, zero clones, depth contract clean):

| pose | h° | placeholder % | vs rest | dark % | vs rest |
|---|---|---|---|---|---|
| rest | 0 | **0.168** | — | 0.001 | — |
| half right | 26.6 | 4.901 | +4.73 | 1.409 | +1.41 |
| full right | 45 | 8.900 | +8.73 | 2.005 | +2.00 |
| full up | 0 | 2.279 | +2.11 | 0.043 | +0.04 |
| up-right corner | 45 | 9.141 | +8.97 | 1.498 | +1.50 |
| **down-left corner** | 45 | **27.744** | **+27.58** | **21.254** | **+21.25** |

Two readings.

**Rest at 0.17% is the sanity check passing.** At rest the viewer is looking at the picture and essentially none of what
they see was invented. That has been assumed for the whole project and never measured.

**The envelope is not symmetrical, and the asymmetry is large.** The down-left corner is three times the up-right corner on
placeholder and fourteen times on dark. Part of that is structural — the troll's content touches the top of the canvas at
rest, so there is no margin above it and moving the eye down exposes the open frame edge, which is exactly what the margin
modes exist for and they are off. But a factor of fourteen is worth a look before it is explained away, and it is precisely
the kind of thing the instrument was built to surface.

## 5. What still needs eyes, and now has the shots

Three decisions cannot be made from numbers, and the frames for all three are now on disk:

1. **The down-left corner** (`harness/shots/s44_env/troll/*_m1_m1.png`). The worst place in the envelope by a wide margin.
2. **`seams = all`** at 52° and 56° on silverwarrior: the rim holes close, a skin appears. Which is worse to look at.
3. **S7's ceiling over-claim and the sky option's uncovered frame edge from 0.2 m**, both open since S18 and S19.

## 6. Re-baseline

The defaults change is recorded as the new baseline for the troll in `harness/shots/s44_env/troll/envelope.json`: plane far
side, wash, no margin, tier 35°, ceiling cut and line despeckle armed, zero clones, depth contract clean. The kit
instruments are unaffected — they pass their arms as explicit flags rather than through the panel — so nothing there needed
re-running, which is worth stating rather than leaving implied.

---

**Where this leaves S41.** Sprint 23 and Sprint 24 are done. Sprint 25, the end-to-end loop with the contract R7 settled, is
next, and it is the first time a photograph will go out of the app and come back. The three items above are the user's, and
they gate nothing.
