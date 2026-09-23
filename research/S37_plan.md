# S37 — Plan (2026-09-20)

Written after S35 closed as a prototype (§58), R6 reviewed the literature for the two named failures, and S36 measured the
one candidate it turned up. The state is: **a lot of measurement has accumulated ahead of anything a person can see.** The
app still runs the per-line plane law; the sheet model that beats it on the kit is offline Python; the last thing shown on
screen was the live pass of 2026-09-13. This plan is ordered to fix that first.

---

## 0. Now, before anything else: preserve work that will be lost (30 minutes)

Three commits sit **unpushed** on `moebiusv2` `main` — the L5 scene, the L6 scene and the renderer fix (a running top-K of
hits; without it L5 exhausts memory). The session's GitHub scope covers `delphifissure/moebius` only, so they have never
left this container.

Worse, the **rendered truth is gitignored**: `out/L5`, `out/L5_env45`, `out/L6`, `out/L6_env45`, about 18 MB, are the product
of roughly ninety minutes of ray-casting (L5 22 min, L6 71 min). When the container is reclaimed they go, and every number in
S36 becomes unreproducible without re-rendering.

**Done means:** either the three commits are pushed to `moebiusv2` (needs that repository added to the session with push
access), or the scenes and their truth are vendored into `moebius` under `research/s35/kit/`. The scene *definitions* are
already mirrored there as source; the renderer fix and the rendered truth are not.

**Recommendation:** push to `moebiusv2`. It is where the kit belongs and the mirror was only ever a stopgap.

---

## Phase A — The live pass (the next real sprint)

This has been item 2 on the queue since 2026-09-12 and has been passed over five times. Everything in it is already measured;
none of it is research.

1. **Consolidate defaults from the option arms.** The arms carrying measured wins and no known cost: the line-aware
   despeckle (`_despeckleLines`, S20), the untorn plate seams value (S20), the ceiling cut (`_ceilCut`, S23: S7 precision
   0.65 → 0.86, P6 0.50 → 0.69, S26 0.46 → 0.82, inert elsewhere). Decide each on screen, then make it the default.
2. **Strip the dead arms.** Everything falsified and recorded is still selectable in the bake panel. Remove it; the notes
   are the record.
3. **The input contract** (S19 §3.3, still open): a polarity and range check on a loaded depth map, with a visible warning.
   This is the one outstanding *correctness* gap that a user can trip over by loading an ordinary depth PNG.
4. **Two things that need eyes, not numbers:** S7's ceiling over-claim (S18 §2b) and the sky option's uncovered frame edge
   from 0.2 m (S19 §3.5).
5. **Re-baseline every instrument** against the new defaults so later work compares against what ships.

**Done means:** defaults are what a new user gets, the panel has only live arms, a bad depth map is refused with a message,
and `LIVE_PASS.md` records the decisions and the shots they were made from.

---

## Phase B — Close the loop, end to end (the first whole picture)

Queue items 3 and 4, plus the one contract change R6 turned up.

1. **Reimport the plane bundle** onto the live plate (plate 1 colour, plate 2, sky, margin) and round-trip it through the
   bundle checker. No reimport exists today, so the hand-off has never been proved in both directions.
2. **Ask for depth back, not only colour.** Every paper in R6's diminished-reality family inpaints colour and depth in one
   pass and conditions each on the other; the joint-RGBD line supports **asymmetric masks** for the two channels, which
   matches us, since we trust the plate's colour and its geometry differently by class. We are changing the contract anyway
   for the reimport, so change it once.
3. **One real inpaint, any model, reimported and viewed.** This is the first end-to-end picture and the first honest look at
   whether the whole idea holds up.

**Done means:** a photograph goes out as a bundle, comes back inpainted in colour and depth, loads onto the plate, and is
viewed through the envelope. Whatever it looks like is the finding.

---

## Phase C — Decide the sheet model's fate (a decision, then possibly a port)

S35's arm beats the app's per-line law substantially on the kit: S15 8.12 → 0.264 m, S26 0.028 → 0, L4 0.031 → 0.002, ten
scenes at 0.000. None of it is in the app, and porting an offline Python construction (surfaces, groups, clamped plates per
group, a layered order) into the live JS/WebGL bake is a large piece of work — larger than any single sprint so far.

**It should not be ported on kit numbers alone.** This project's own principle is that the user's screen is the aesthetic
authority, and the kit does not measure what a seam looks like when a head moves.

**The cheap decision procedure:** bake the same four pictures both ways offline, render each through the envelope at the
same poses, and put them side by side on screen. One day of work to get the answer, against weeks to port blind.

### The stopping rule (fixed 2026-09-23, before any A/B frame was rendered)

This rule was written before the test ran, so a result cannot change it. It ends the geometry loop either way.

**What is compared.**
- Arm A is the per-line law with the app's start-up defaults.
- Arm B is S35's measured arm (§58: `--closure comp --thingrule wrap --reach-group --group-plate --ramp --crease
  --group-prior`). Its band depth goes into the app through the Sprint 25 return path.
- Where the sheet model owns no texel, arm B uses the per-line law's depth. It does not use the occluder's own depth,
  which would be a clone by construction (S35 §47) and would break rule 4.
- The two arms differ only where the sheets supply a surface, and neither arm contains a clone.
- Both arms get the same band colour (the hybrid inpaint), the same depth map and the same poses.
- The arm B construction is frozen as written. No flag is changed after the first frame has been seen.

**The pictures.** Troll, vermeer, sunflowers and starwatcher: the four that have object maps (S35 §58). This set is fixed.
If the result is close, no fifth picture is added (rule 6).

**Who judges, and how.**
- The user judges, on their screen (rule 8). I do not decide.
- Each picture is shown as a pair at yaw 45°, with 22.5° and a vertical 45° as context. Each pair is labelled only L/R.
  Which arm is on which side is randomised per picture and recorded in a sealed file. It is revealed only after all four
  verdicts are in.
- For each picture the user answers **L better**, **R better**, or **no clear difference**. The question is which one
  looks better overall at 45°, so any new artefact the sheets bring (seams between sheets, jumps at the fall-back edge)
  counts against them.
- Metrics (wall length, S33 classes, coverage) are reported only after the verdicts, as context. They cannot overturn a
  verdict (A126).

**The decision.**
- **The sheets are preferred on at least 3 of the 4 pictures: port them.** The sheet model becomes the far field, with the
  per-line law as its fall-back.
  - After that, geometry work means only the port: matching the offline frames, then bake speed (66 s now, ~2 s target).
  - The S55 material (capped join cost, gated median, connectivity for class 2) is input to the port, not a separate
    sprint.
  - Defaults change in the live pass after the port, not before (A126).
- **Any other outcome (2 of 4 or fewer, "no clear difference" included): stop geometry research.**
  - Ship the per-line law with the hybrid inpaint band.
  - Close Sprints 30 and 31 and the join-cost work on the per-line law.
  - Record the remaining combing as the known limit of one photograph.
  - Geometry reopens only for *new information*, not for a new idea on the same data. Examples: a new depth model, truth
    from the phone pans, or a failure on a new photograph that the current limit does not explain.
- A "no clear difference" verdict counts against the port, because a port of several weeks needs a visible reason.

**What does not count as a result.**
- A frame broken by a bug is not a result: for example, a mismatched pose, missing colour, or an empty band. Fix the bug,
  re-render that pair, and log it in the write-up.
- Changing arm B because a frame looked wrong is not a bug fix. It would be a new test, and this rule does not allow one.

**Done means:** a documented decision under this rule, with the frames, the sealed side assignment and the user's verdicts.

---

## Phase D — The sunflowers, and only the sunflowers (research, gated)

S36 measured the learned amodal prior honestly: it helps **one kit scene in four**. It fixes the sunflowers' configuration
(L5 heads-only, 0.238 → 0.034 m, matching our own fully-labelled best with no map at all) and it is worse on L1, much worse
on L6 and destroyed on S15. So this is not a default and not a general mechanism.

What would make it usable, in order of what blocks what:

1. **An arm-side confidence.** We have a truth-free confidence for the *model* (its median disagreement with the observed
   depth over the visible region orders all five runs, and per texel its error rises monotonically with it). We have none
   for the *arm*, so we cannot choose between them. This is the blocker, and it is §57's question one level up. If it
   resists two honest attempts, stop: the pattern of this project is that such questions are answered upstream, not here.
2. **The wide-range exclusion**, which is free: S15 failed because a relative prediction cannot carry a hidden range 8.64 m
   outside the visible one, exactly as S26 found. Any use must exclude that case, and the scene's own depth extent says so.
3. **Native resolution.** Everything in S36 went through a 518² resize, which costs precisely the texel-scale detail the
   band is measured at. Tiling would say how much of the gap that was.
4. **Then, if all three land:** the prior as a bake-time option for field-like pictures, arbitrating between our existing
   candidates rather than replacing them, since arbitration beat direct prediction on L5 (0.022 against 0.060 m).

**Recommendation: do not start Phase D until Phases A and B have shipped.** It improves one picture conditionally; they put
the whole thing in front of a person.

---

## Not recommended, and why

- **Porting the sheet model before the on-screen A/B** (Phase C decides it).
- **Turning the amodal prior on generally.** One scene in four.
- **Re-opening the group-level closure.** §32 measured and removed it; R6 proposed it again from the border-ownership
  reading, and the check found the repeat before anything was built.
- **Scoring silverwarrior, bristlecone and octopus** as they are. They have depth bakes but no object map, no truth and no
  recorded visible step; scoring them means inventing two of the three. If the picture set must be seven, give them probes
  properly in Phase A, or leave the set at four and say so.

---

## Order, with rough sizes

| | phase | size | why now |
|---|---|---|---|
| 0 | preserve the kit work | 30 min | it is lost when the container goes |
| 1 | Phase A, the live pass | 1 sprint | measured work no one has seen |
| 2 | Phase B, end to end | 1 sprint | proves the hand-off in both directions |
| 3 | Phase C, the sheet A/B | 1 day | decides a weeks-long port for the cost of a day |
| 4 | Phase D, the sunflowers | open-ended | blocked on an arm-side confidence |

**The single most valuable next action is Phase A**, and the reason is not technical. Eleven sprints of measurement have
gone by since anything changed on screen, the research has settled into questions the far field cannot answer by itself, and
the fastest way to learn something genuinely new now is to look at a picture.
