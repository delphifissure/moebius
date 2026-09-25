# S70 — One click to paint, faces as scale references, a robust scale fit, and the seen test without sampled poses

Date: 2026-09-25. The user's go on the four "while it renders" items: (1) the one-click flow, (2) detected faces as Set
Scale references with per-shot storage, (3) outlier rejection in the scale fit, (4) an exact formulation for the hidden
band in place of pose sampling. App changes on the worker branch (`moebius.js`, `moebius.html`, `server.js`), each
checked headlessly.

## 1. Paint holes: one click from the picture to the painted plate

**What the user does:** start the paint server once (`python3 harness/paint_server.py`), then press **🖌 Paint holes**
(the row above Debug View). The row has the painter (SD / wash + SD / LaMa + SD / LaMa only), the mask SD is shown
(as is / blob), depth on or off, and an optional server address.

**What happens:**
1. The server is asked first (`/health`). With none, the button says how to start it and nothing is baked: a bake is
   minutes, and there is no point without a painter.
2. If there is no plate yet, the Build button's own path bakes one (the panel's plate options, source hole by default).
3. The SD bundle is written exactly as the SD Bundle button writes it (`exportSDBundle({ returnBytes: true })` returns
   the zip instead of downloading it; nothing else in the export changed).
4. It is POSTed to the server, which runs `sd_return.py` on it as a subprocess with the chosen flags, one job at a time
   (two SD jobs at once were OOM-killed on this 15 GB machine; it happened again today to a label-prompt run beside
   the kit probes). The status line shows the painter's last log line and the elapsed time.
5. The returned `return_band*.png` files go through `_importPlaneReturnFiles`, the path Import plane return uses.

**Serving:** the app's `server.js` forwards `/paint/*` to the paint server (`PAINT_URL`, default `127.0.0.1:8765`), so
the page reaches it same-origin, over http on the Mac and over https from the iPad (a direct http call from an https page
is blocked as mixed content). A full URL in the box points it anywhere else (a GPU machine), with CORS open.

**Check** (`harness/paint_oneclick_check.js`, the default picture with its DA3 16-bit depth, LaMa, no depth return):

| step | result |
|---|---|
| no server | refused before any bake: "no paint server at … run python3 harness/paint_server.py" |
| unknown painter | server answers 400, "painter must be one of sd, lama, lama+sd, wash+sd" |
| one click, nothing baked | baking → bundle 27.3 MB (26 files) → LaMa → import |
| import | 172 264 band texels painted, plate 2: 55 690 texels painted, none dropped |
| `server.js` forwarding | 502 with the start command when the server is down; `/paint/health`, a non-zip body (400), an unknown job (404) all pass through |

Wall time here was 25 min, almost all of it SwiftShader (the bake and the import render on the CPU) and a painter
sharing four cores with the background queue; the painting itself was 146 s of LaMa. On a GPU the bake is the
seconds-to-minutes the user already sees.

## 2. Faces as size references

**Find faces** (Set Scale panel) searches the picture with the same face mesh the webcam tracker uses (MediaPipe, iris
landmarks on), whole and in tiles of a half and a quarter of the short side, because the mesh's detector only finds
faces that fill a good part of its input. Each face becomes a reference, used unless unticked:
- the size is the 3-D span between the iris centres (the head-Z measure, which a turned head does not shorten) against
  the adult interpupillary distance, 63 mm;
- its class spread is the SD 3.5 mm (5.6 %), both the Dodgson (2004) values the code already cites at `IPD_M` (not
  re-read here);
- its depth is the median disparity over a disc of half the eye span at the eyes.

The webcam detector is swapped out while the picture is searched and rebuilt after (two detectors of this runtime at
once were not tested).

**References are per shot.** A shot is the depth map it was baked from, keyed by a hash of 4 096 samples of it. The
references are kept in the browser under that key and come back when the same picture is baked again. The metric depth
law is used only when the references belong to the shot on screen (before this, a new picture kept the last picture's
scale).

**Check** (`harness/face_scale_check.js`; the real tracker, served locally from the vendored packages). One face (the
Milkmaid's) is drawn three times on a synthetic picture with a sky strip and thirds at disparity 0.8 / 0.55 / 0.3:
- left, at 0.8, eyes 60 px apart;
- right, at 0.3, eyes 22.5 px apart (the true scale, 0.3/0.8 of the left);
- a "poster" in the middle, at 0.55, eyes 60 px apart (1.45× too large for its depth).

| | result |
|---|---|
| faces found | 3 of 3, each at its region's depth |
| the poster | left out: 31 % off the line (its 2σ is about 12 %) |
| the far end | β/α = −4·10⁻⁶: the sky is at infinity, as drawn |
| left/right size ratio | 2.70 against 2.67 true (1.4 %, landmark precision) |

The first run, with the right face's eyes 15 px apart, found only two faces. That face was below the detector's range:
about 1/50 of the short side is the floor even with the quarter tiles. The run also exposed item 3's tie problem.

## 3. The fit: outliers, conflicts, ties

Each reference has a 1σ in its size:
- **Presets:** the preset's stated range read as ±2σ (person 1.5–1.9 m, head 0.21–0.25, door 1.95–2.1, car 3.5–5.5,
  step 0.15–0.20). These ranges are typical values for the user to edit, not citations.
- **Typed length:** exact.
- **Click / landmark precision:** √2 px over the measured length, for every reference.
- **Depth precision:** the map's quantum, times α.

The sky enters as the point (d = 0, q = 0), with the sky threshold as its depth precision.

- **Robust fit:** with three or more points, every pair proposes a line. The largest set within 2σ of it (the two-sided
  95 % band) is refitted by weighted least squares, and the rest are named as OFF THE LINE in the list. They are left
  out, not averaged in.
- **Ambiguous:** two or more equally large sets that each agree internally mean the data cannot choose. Sky + two
  disagreeing faces is the case: either face can be the odd one, or the sky can. The fit now says AMBIGUOUS, names the
  disputed references, and fits all of them together. Before this fix it picked one silently: the first face run kept
  the poster and threw out the true face.
- **Conflicts and assumptions** are reported as before (S69).
- **The list:** each reference has a tick box (use / don't use), a remove button, and its residual.

**Check** (`harness/scale_check.js`, extended; the synthetic line α = 0.2, β = 0.02):
- Two references: exact (residuals 10⁻¹⁶).
- Three true + one at 3× (a poster): the poster is flagged (residual +132 %) and α, β are exact. Unticking it gives the
  same line with no note.
- The person preset's σ: 0.0588 = 0.1/1.7.
- A conflicting pair is still reported.
- Per shot: a second depth map gets a different key, no references, and the law off. Returning to the first brings
  both references back from storage, with the law on.
- The face-tracking slider is untouched.

## 4. The seen test without sampled poses: what closes and what does not

**Where the sampling sits now.** In source mode (the default hole) the band is not a pose sweep. It is:
1. a reach walk from each rim through the object (a distance, continuous in direction);
2. a SEEN filter that keeps a candidate only if the source mesh leaves its screen place open at one of 32 poses
   (8 directions × 4 magnitudes);
3. a majority smoothing.

The poses are in step 2.

**Measured** (`harness/seen_check.js`: one bake, then the hole re-solved on the bake's own inputs). The default
picture, 248 175 candidates. Recall is against 4 096 poses (256 directions × 16 magnitudes, uniform in angle):

| arm | seen | recall of the 4 096-pose set | hole after smoothing | its recall | time (this CPU) |
|---|---|---|---|---|---|
| 32 poses (the app today; re-solve = the bake's own hole exactly) | 175 975 | 88.6 % | 172 264 | 89.9 % | 9 s |
| 1 024 poses | 193 432 | — | 185 548 | — | 184 s |
| 4 096 poses (reference) | 198 729 | 100 % | 189 612 | 100 % | 734 s |
| 32 poses + emergence test | 186 935 | 93.5 % (+1 026 beyond) | 179 435 | 94.3 % | 9 + 43 s |

- **The dense set is not converged either:** 1 024 → 4 096 poses still adds 2.7 %. As in S67 §3, sampling finer costs
  linearly and closes slowly.
- **The misses sit at the outer edge of each reveal**, in fans between sampled directions. These are texels seen only
  near the rim of the head-motion range, and only from some directions.

**The closed form, and exactly what it covers.** Every texel moves by its shift s times the pose h, with E the envelope
rectangle (|hx| ≤ 1, |hy| ≤ env). A hidden plate texel v (shift σ) is crossed by the source mesh's torn edge u (shift
s_u > σ) at the pose

    h = (x_v − x_u) / (s_u − σ),  which lies in E exactly when  dE(x_v − x_u) ≤ s_u − σ,
    dE(dx, dy) = max(|dx|, |dy| / env)   (the rectangle's own gauge).

So v can leave its occluder within the envelope iff σ ≤ W(x_v), where W(x) = max over edge texels u of [s_u − dE(x − x_u)].
This is a max-plus distance transform. It is computed exactly at every breakpoint of the gauge by growing a rectangle
one texel at a time (per quadrant of the offset). No pose is sampled.

**What it does not give.** This is a necessary condition, not a sufficient one: another surface can cover v at that
pose. Of the 63 440 candidates the 32 poses did not see, 62 077 pass it. Sufficiency needs a visibility test at a pose.
The emergence test does that per texel: it tries 12 poses (4 quadrants × just past the crossing, halfway, and the rim),
each with a point test against the mesh as drawn, within one texel as the renderer's test is.

**What that buys.** 10 960 texels are added, every one verified open at a stated pose, so none of them is a false
positive of the test. 1 026 of them are beyond even the 4 096-pose set. Recall goes from 88.6 % to 93.5 % for 43 s more
(in the worker). It does not reach the dense set: 6.5 % of what some dense pose sees is seen at none of each texel's 12
poses.

**Status.** The emergence test is in the app as an instrument (`bgSourceHole` o.seenMode = 'exact'), off by default, and
not in the panel. An exact replacement for the pose sampling is therefore not achieved: the reveal *condition* is closed
form, and its *visibility* is still sampled, only better aimed (per texel instead of per picture). Starwatcher and the
Milkmaid run on the same instrument:

| picture | candidates | 32 poses: recall of 4 096 | emergence test: recall | added (verified) | beyond 4 096 |
|---|---|---|---|---|---|
| default (troll) | 248 175 | 88.6 % | 93.5 % | 10 960 | 1 026 |
| Starwatcher | 87 222 | 99.3 % | 99.9 % | 507 | 4 |
| Milkmaid | (rerunning after the 13:06 container restart) | | | | |

On Starwatcher the 32 poses already see nearly everything (its reveals are narrow). The troll, with wide reveals at
the outer reach, is where the sampling loses texels.

## 5. Depth first or colour first? The kit answer, light arms (`harness/depth_order_eval.py`)

This is from the previous round's item 3. The kit probes were re-dumped under the current law (19 scenes, 07:46–08:12), then the
light arms ran. Two classes of hidden texel are scored against the kit's exact hidden depth:
- **bg:** the background behind an object;
- **own:** the object's own hidden back.

Two arms:
- **rule:** the plane law the app uses, depth first;
- **colour:** paint first, then DA3 on the painted picture, fitted to the visible depth and clamped behind the front.

The colour arm here uses the truth's own colour, i.e. a perfect painter. It is an upper bound, and the LaMa and SD
painter arms have not run.

Median over scenes, in metres:

| class | scenes | rule: median error | rule: p90 | colour (perfect painter): median | colour: p90 | rule's p90 better in |
|---|---|---|---|---|---|---|
| bg | 19 | 0.0000 | 0.0000 | 0.0011 | 0.0043 | 13 of 19 |
| own | 17 | 0.0571 | 0.1364 | 0.0107 | 0.0460 | 1 of 17 |

- **Behind an object, depth first is right.** The rule is exact in most scenes. The kit's backgrounds are planes, which
  flatters a plane law, so on real pictures this is an upper bound too. Colour first adds DA3's own millimetres, and on
  S5, S9 and S10 it adds new depth steps at the hole's seam (6–13 % of seam pairs).
- **An object's own hidden side needs the colour first**, if the painter is good. The rule continues the far side, 6 cm
  median off, while depth read from a correctly painted picture is 1 cm off. The rule wins only where the back is a flat
  continuation (S9, S11, S12 are ties).
- **Where both fail:** S15 (sky and far hills: both arms metres off, the rule's own class 3.8 m median) and S32 (an
  open hedge whose truth has almost no rule coverage: band cover 0.86 / 0.00).
- **What this means for the order of passes:** the per-layer SD depth pass the user asked about earlier belongs
  to the object layers, not to the background plate. The background keeps the rule's depth, and an object's own
  back takes the depth read off its painted colour. Whether a real painter keeps enough of the perfect painter's
  advantage is what the LaMa / SD arms (not yet run) must show.
