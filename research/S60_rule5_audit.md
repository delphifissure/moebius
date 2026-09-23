# S60 — Rule-5 audit of every behaviour switch in moebius.js (2026-09-23, read-only; nothing removed yet)

> **Status.** Nothing has been removed. The removals are applied only after the S59 A/B renders finish, because every bake reads the live `moebius.js`. The guard is byte-identical default frames plus the a134 served-identity check.
>
> Three verdict quotes were re-checked verbatim against REVIEW.md: 5401–5403, 10078–10081 and 3972.
>
> **Bug to fix** (§ "Side finding"): the gap-rule select leaks `_plugMembrane`, `_plugGuided` and `_fragTear` into every later bake in the session. Confirmed at `moebius.js` 21530/21533/21606.


The audit reads `/home/user/moebiusv2/moebius.js` (29 839 lines) and the notes. Nothing was edited or run.

**Abbreviations.** `R:` = `/home/user/moebius/REVIEW.md`. `S50:219` = `/home/user/moebius/research/S50_tolerance.md` line 219 (the other S-notes follow the same pattern). `LP` = `research/LIVE_PASS.md`, `CM` = `research/CODEMAP.md`, `MP` = `research/META_PLAN.md`. A bare number in the "default" or "delete sites" column is a line in `moebius.js`.

**Method.**
- Grepped all 313 distinct `window._*` names.
- Kept the names that are read as a switch or a tunable: 111 of them.
- Excluded pure captures and outputs: every `_qb*`, the `_geo*` arrays, `_a249*`, `_srDbg`, `_fpData`/`_fpSeed`, `_carveDbg`, `_dbgFill`, `_p2Dbg`, `_mpiDebug`, `_objHL*`, `_bgQuickBaked`, `_bgUserBuiltOnce`, `_bsRefs`, the face/eye/dolly state and the exported functions.
- A separate list at the end covers 8 names that now exist only in comments.
- Harness users in the risk column exclude `harness/moebius_hist.js`, which is an old 23k-line snapshot of the app, not a driver.
- "Panel" means the S6 plate panel at 21549–21616. Its `applyPlateOptions()` runs at load (21597), so panel flags are always set.

## Summary count (111 switches)

| verdict | n |
|---|---|
| ADOPTED-AS-DEFAULT | 35 |
| FALSIFIED | 16 |
| OPEN-TRADE | 18 |
| HARNESS-ONLY | 18 |
| UNKNOWN | 24 |

In addition:
- 8 comment-only residues: the flag is gone but a comment still names it.
- About 12 config/UI names that are not research switches (end of file).

## Panel and selects → switches (the map)

| control | values (default **bold**) | switches it sets |
|---|---|---|
| `bgPlateFarSel` far | membrane / **plane** | `_tearLaw='rim'`, `_farRule='plane'` (21583); `plane` also routes Build to `bakePlate` → `_plateFlushExempt=true` + `_plugGeoBand({flush,observed,gateAPriori})` (21606–21610) |
| `bgPlateFillSel` fill | **wash** / mirror | `_selfSample` (21585) |
| `bgPlateMarginSel` margin | **off** / picture / window | `_plugMargin` 0/2/1 (21586) |
| `bgPlateFacesSel` faces | **off** / on | `_stepFaces` (21587) |
| `bgPlateBandSel` band | all / **35** / 25 / 15 | `_bandTierDeg` (21588) |
| `bgPlateSkySel` sky | **off** / on | `_skyInf` (21584) |
| `bgPlateSeamSel` seams | torn / **stretched** / all | `_plateStretchInner`, `_plateKeepAll` (21589–21590) |
| `bgPlateJoinSel` join | **off** / on | `_farJoin` (21591) |
| `bgPlateRulesSel` rules | cur / ceil / **new** | `_ceilCut`, `_despeckleLines` (21593–21594). The HTML marks `cur` selected (`moebius.html:313`), but the JS default overwrites it at 21578. |
| `bgGapRuleSel` gaps | **default** / far / skirt / side / back | `_plugObjectRule`, `_plugExtent`, `_geoLipSeed`, `_plugBack`, plus `_plateFlushExempt`, `_plugMembrane=1`, `_plugGuided=1`, `_fragTear=2`, `_plugMargin=1` (21530–21533) |
| `bgModeSel` mode | quick / v2 / v1 (disabled) | JS globals `bgQuickBake`/`bgMPIMode`/`bgMPIFullPlanes`, not `window._` (21504–21508). v1 is greyed out but kept reachable (A129, 21498–21503); no rule-5 verdict in the notes. |

`_bgPlateOptions` (21595) and `_bgGapRule` (21529) only stamp the choice for the debug sheet and export. They switch nothing.

## Table

The "delete sites" column is filled only for FALSIFIED and ADOPTED-AS-DEFAULT rows. "Risk" names what else reads the flag, or the harnesses that set it.

### FALSIFIED (16)

| flag | default (set) | what it changes | introduced | verdict | evidence | delete sites · risk |
|---|---|---|---|---|---|---|
| `_fillBandLimit` | unset → off | band-limits the field the fill's gradient estimator reads (a100) | a100, R:5380ff | FALSIFIED | R:5401–5403 "a100's premise … was FALSE. Defaulted off, kept behind window._fillBandLimit"; S57:227 | 14483–14533 (the A100 comment block and `if` block; `dSm = dQ` stays) · no reader besides `dSm`; no live harness |
| `_nearestAnchorWins` | unset → off | restores the a63b nearest-anchor claim law | a63b; A78 made farther-value-wins the default | FALSIFIED | R:3972 "nearest-anchor Voronoi steps ARE the gloop"; R:4013–4014 (the hatch); S57:228 | 14751, 14754–14762 · `harness/ab_valwins.js` sets it |
| `_plateRowColor` | unset → off | a70 depth-consistent per-row reveal colours | a70 / a72b | FALSIFIED | R:10078–10087 "Enabling the opt-in row-colour pass is refuted, measured … ghost streak +92.7% … a hard clone"; S57:229 | 16600–16715 (`plateColorTex` must still be declared as `null`) · `a213_ab.js`, `a213_rowcolor.js` |
| `_plateMembrane` | unset → off | a69 row-flank membrane on the directional plate | a69 / a72b | FALSIFIED | R:4270 "MEMBRANE: NOT the cure"; R:4141–4144 "stay OPT-IN indefinitely … re-landing … CANCELLED"; S57:233 | 14842–14882 · `a88_membrane.js`, `regress.js` name it; check that regress.js does not assert on it |
| `_strokeAdopt` | unset → off (`_adoptOff` true) | a51 ink-adoption depth writes | a51 (A61b turned it off) | FALSIFIED | R:3300–3306 "stroke-adopt depth OFF … Not load-bearing anywhere measured"; S57:230 | 12736–12744 (comment and flag), the flood 12745–12816, the write loop 12823–12827, the branch at 12987 · `adopt` also feeds the `_srCapture` dump (12817, harness `p2probe`/`hline_probe`); `adoptedM` stays (GC/P2 set it) · `verify_a61b.js`, `dirplate_*`, `diag_mask.js` |
| `_inkSeat` | unset → false (13181) | a56 ink-island seat | a56 (A61 turned it off) | FALSIFIED | R:3292–3298 "The seat's founding premise … is false on the shipped map … Opt-in window._inkSeat"; S57:230 | 13161–13288 (the A56 comment block and the `if (_inkSeatOn…)` block) · takes `_seatFloorFlat` and `_seatDbg` with it · `dirplate_*`, `depthaudit.js`, `diag_mask.js` |
| `_seatFloorFlat` | unset → off | a56 floor-decal form of the seat | a57b | FALSIFIED (it lives inside `_inkSeat`) | R:3080 "available as an A/B opt-in"; the parent premise is R:3292 | 13278–13279 (inside the `_inkSeat` block) |
| `_farLabel` | unset → off | S51 cross-line ICM axis labelling of the far field | S51:111 | FALSIFIED (disputed, see below) | S53:600–603 "perceptually indistinguishable from doing nothing … S51 stays off, now on perceptual evidence"; S57:231. But S57:235–236 calls it "arguable", and S58:55–58 defers to the sheet A/B. | 9046–9089 · `s53_sweep.js` |
| `_plateNearOnly` | unset → 0 | S46 near-extent rule, tolerance in source quanta | S46 (via S48:98) | FALSIFIED | S50:219–222 "The evidence to retire it is there — px2 beats q8 on every column"; S57:232 | 17176–17186; `u_plateNearOnly` at 3045, 3125, the `else` at 3279; 18185 · shares the shader block with `_plateNearOnlyPx` · `s50_tolsweep.js` |
| `_plateNearOnlyPx` | unset → 0 | the same rule, tolerance in screen px at the rim | S48:109 | FALSIFIED ("not adopted") | S50:202–205 "the rule stays off … the person whose screen is the authority looked at all five and rejected them". S50:216–222 chose not to retire it; S57 §4 does not list it. | 10745–10759 (`_setPlateNearOnlyPx`); 10768–10772 (T in `_armRevealLaw`); 17187–17190; shader 3048, 3128, 3262–3284; the `liveRule` string at 11324 · keep `_revealLaw`, `_revealZofD` and `_revealPxField`: S53 confidence (9069, 9134) and the export (11308) use them · `s50_tolsweep.js` |
| `_plugBackTex` | unset → off | the A257 back layer keeps raw texels instead of the membrane wash | A257d | FALSIFIED | R:14202–14203 "Removed this arc (rule 7): … the raw-texel side colour (kept behind `_plugBackTex`)" | 9318, 9320 (drop `&& !window._plugBackTex`) · no harness |
| `_envelopePlateStep` | unset → off | a126 slope limit uses the fold-correct 1/k instead of the shipped step | a128 | FALSIFIED (on 8-bit data) | R:6748 "a128 REOPENED, AND THE REOPENING FAILS"; R:6774–6777 "falsified on the metric chosen to see that artifact"; R:6895–6899 (REPLY02: on 8-bit "can never win") | 17659–17663 (use `bgConeSlopePerPx(pw)`) · already dead on the default path: the loop is skipped under the rim law (17670 `if (!_rimA126)`) · the maps are now 16-bit, so the REPLY02 caveat may apply · `combstep.js`, `synth128.js` |
| `_vpScan` | unset → off | A80 all-viewpoint scan pruning the SD mask | A80 (R:4150ff); a121 turned it off | FALSIFIED (measured inert) | R:6527 "a121 viewpoint scan off — pruned 0px on ALL FOUR suite assets"; R:11142 "it pruned 0 px"; code 15844–15855 | 15828–15933 (block and log) · takes `_noVpScan`, `_scanRange` and `_legacyScanWarp` with it · `a228_carve.js`, `a229_plug*.js` set it = true: those arms stop diverging, so apply the a134 guard |
| `_noVpScan` | unset | forces the scan off (the default since a121) | A83 R:4165 | FALSIFIED (redundant) | code 15856–15857 "still forces it off for older harnesses" | 15858 · 21 old `a8x`/`a9x` harnesses set it; the assignment becomes a no-op, which is harmless |
| `_scanRange` | unset → 1.0 | scales the vpScan sweep | A83 | FALSIFIED (only inside the dead scan) | R:5731 "window._scanRange stops being a tuned number" | 15866–15870 (inside the vpScan block) |
| `_plugCarve` | unset → off (reset at 8390, 8855) | a217/a229 carve: drop plate triangles outside demand; A232 region carve | a217 (R:10514) | FALSIFIED (demand form), disputed | R:11229–11232 "The carve is not a general plug"; but R:12886 keeps "the carve as an optimisation" (plan item 7), and `_plugSweepBake` sets it (8438) | 17862–17992 (takes `_collarSameTexel` and `plateFPreCross` 16025 with it) · `_plugSweepBake`/`_plugRegion` pipeline (8377–8440), `a228_*`, `a229_*`, `a231_visible.js`, `a242_ghost.js` · **not a clean delete** |

### ADOPTED-AS-DEFAULT (35)

The flag is now redundant and the legacy branch it restores is dead by default. Deleting one means removing the hatch and its legacy branch.

| flag | default (set) | what it changes | introduced | verdict | evidence | delete sites · risk |
|---|---|---|---|---|---|---|
| `_tearLaw` | `'rim'` (panel 21583) | rim tear law vs the fold law | S2b (S2_sprint2_report:16) | ADOPTED | LP:17 "far side = plane (rim law)"; code 21552–21553 "made the defaults on 2026-09-15 at the user's word" | 461 `bgRimLawOn` and every `bgRimLawOn()` branch · **still backs the live `membrane` option**; S44:52–66 kept every panel option; `objl_*.js`, `s2c_skyshot.js` · needs a call before removal |
| `_farRule` | `'plane'` (21583) | plane far side | S3 (S3_sprint3_plan:100) | ADOPTED | the same as `_tearLaw` | 521 `bgFarRuleOn` · the same caveat: removal drops the `membrane` option |
| `_ceilCut` | 1 (21593, rules=new) | S16 ceiling cut in `bgFarSidePlane` | S23:57 | ADOPTED | S44:35–48 "`rules` now ships as ceiling cut + line despeckle"; LP:207 "B. Two arms became defaults" | 632 (make it unconditional), 880 (log); 21593; the rules select `moebius.html:313` · `s44_envelope.js`/`s44_contract.js` assert the rules default and must be updated |
| `_despeckleLines` | 1 (21594) | S13 line-aware despeckle | S20:8 | ADOPTED | S44:47–48; LP:207–209 | 15474–15483, 15491–15492 (drop the flag test); 21594 · the same harnesses |
| `_plateFlushExempt` | `true` on every plane Build (21606) and gap select (21533); unset on the membrane path | A233: a162 does not push back texels at source depth | A233, R:11265 | ADOPTED (on the default path) | S3_sprint3_report:216 (recipe `flush:true`); `_plugGeoBand` sets it (8859); LP:17 plane is the default | 17557–17568 (drop the test); 8391, 8859, 21533, 21606 · makes it on for the `membrane` far side too, which changes those frames (not the default) · 30 harness files set it |
| `_plugMembrane` | unset, but `bgRimLawOn()` gives the same branch (16857, 16981) | A242 Laplace-membrane band colour | A242, R:11931 | ADOPTED (under the rim law) | S2_sprint2_report:77 "band's colour is the membrane" (S2b.4); code 16854–16856 | 16857/16981/17157: fold into `bgRimLawOn()` · the gap select sets it (21533); it still selects the membrane on the non-rim path · `a242_ghost.js`, `a257_diag.js`, `p0_depthviews.js` |
| `_dirPlate` | unset → on (15572, 19558) | a62 directional rising plate | a62 | ADOPTED | R:3309 "a62 — directional rising-plate (quick-bake), DEFAULT ON" | 15572, 19558 (drop the test; the legacy plate branch goes) · `dirplate_*`, `legs_probe.js`, `v2seam_ab.js` |
| `_noSmearSnap` | unset | reverts the A79 smear snap | A79 | ADOPTED | R:4021 header "A72 smear-fringe snap LANDED"; R:4039 | 15605–15606 · none live |
| `_noPromBound` | unset | reverts the A81 prominence bound | A81 | ADOPTED | R:4098 "prominence bound LANDED"; R:4101 | 14782, 14788 · none |
| `_noConeFill` | unset | restores a84 (no cone fill) | A92 | ADOPTED | R:4515 "Hatch: window._noConeFill restores a84 exactly" | 14710–14711 · `bufexport_a84.js` |
| `_noDescFloor` | unset | drops the a63b descent floor | a63b | ADOPTED | R:3978 "DESCENT FLOOR EXONERATED" | 14731–14732 (ternary) · `fold_probe.js` |
| `_noDequant` | unset | reverts the a86 dequantiser | A93 | ADOPTED | R:4526 header; R:4560 "Hatch: window._noDequant" | 15237, 15390 (drop the term) · `a112_small.js`, `a113_tiny.js`, `a114_ptear.js` |
| `_legacyPlateTear` | unset | restores the a87 plate tear instead of the a126 slope limit | a126 | ADOPTED | CM:355 "a126 slope limit (default; `_legacyPlateTear` reverts to the a87 tear)"; R:11817 | 17610–17611 plus the `else` branch 17753–17788 · `combstep.js`, `holes.js` |
| `_noPlateTear` | unset | inside the legacy branch: a87 → a50 | A94 | ADOPTED (superseded twice) | R:4622 "Hatch: window._noPlateTear" | 17377 comment, 17753 (goes with the branch above) |
| `_sConeFixed` | unset | a88 per-width cone slope → fixed 0.0025 | A95 | ADOPTED | R:4672 "FIX (a88 …) … Hatch: window._sConeFixed" | 15535–15536 |
| `_noPerPixelCone` | unset | reverts the a101 per-pixel cone to the scalar | A109 | ADOPTED | R:5503 "`window._noPerPixelCone` restores the scalar" | 259–261, 16483 · `a109_dolly.js` (history) |
| `_noExactCone` | unset | reverts the a102 exact envelope (fill, tear, scan) | a102 | ADOPTED | R:5948–5950 (hatch; a106 split out) | 14315, 15547, 15891, 16415 plus the LUT-null fallbacks (e.g. 14729–14730) · `teartest.js`, `a109_dolly.js` |
| `_legacyScanWarp` | unset | reverts the a106 scan warp | a106 | ADOPTED (inside the dead vpScan) | R:5906–5908 "Hatch _legacyScanWarp"; R:5950 | 15887–15891 · `a106_ab.js`, `regress.js` |
| `_legacyPlugLUT` | unset | restores bgDirectionalPlug's private LUT | a104 | ADOPTED | R:5901–5904 "Three private copies retired … Hatches _legacyPlugLUT, _legacyV2Budget" | 12269–12275 |
| `_legacyV2Budget` | unset | restores v2's second cone slope | a104 | ADOPTED | R:5904 | 13518–13520 |
| `_scanPoses` | unset → 4 | backstop sweep pose count (8 = the diagonals back) | a105 | ADOPTED | R:5906; R:5924 "window._scanPoses = 8 restores them" | 14087–14092 |
| `_scanLegacyPoses` | unset | hard-coded backstop poses | a105 | ADOPTED | R:5906 | 14089–14098 · `a105_ab.js`, `a105_poses.js` |
| `_winFloorLegacy` | unset | old window floors (3/16/2/4 texels) | a93 | ADOPTED | R:5075 "Window floors = 1 texel (a93)" | 14331, 14388, 14538, 14557 |
| `_noSeedReveal` | unset | reverts the a95 reveal-width seed threshold | a95 | ADOPTED | R:5148–5152 "REJECTION OVERTURNED (a92 -> a95) … the form is reinstated" | 14579 (ternary) |
| `_noOrderClamp` | unset | reverts the a135 same-texel ordering clamp | a135 | ADOPTED | R:6975; R:7013 "`window._noOrderClamp` reverts" | 17450, 20490 · `orderclamp.js`, `sweepvsclamp.js` |
| `_noContactCut` | unset | disables the A84 contact-ramp cut uniform | A91 | ADOPTED | R:4446 "Hatch: window._noContactCut" | 17296, 19843, 21214 |
| `_noV2PairValid` | unset | reverts v2 pair validation | A66 | ADOPTED | R:3533 header; R:3562 "Opt-out window._noV2PairValid" | 13583–13584 · `war_ab.js` |
| `_noBgIslands` | unset | v1 hole-only islands → full clone | a58d/A59 | ADOPTED | R:3123 "Gated behind `window._noBgIslands` (reverts to the full clone)" | 21138–21139 · `a90_islands.js`, `a59v1_probe.js`, `islandtest_probe.js` |
| `_plugZBias` | unset | restores the −0.004 plug bias | a59f | ADOPTED | R:3226–3227 "drop the −0.004 plug bias (obsolete…) `window._plugZBias` restores it" | 17213–17214 |
| `_plugConeDepth` | unset | old (too-far) cone floor for the plug | a58c/a59d | ADOPTED | R:3151 "Flush-to-background (a58c) is correct"; code 16036 "reverts to the old (too-far) cone floor" | 16054–16055 (keep the `_plugGroundUp` / else chain) · `flushtest_probe.js` |
| `_legacyGapPass` | unset | SD gap buffer from the edge detector, not coverage | a120 | ADOPTED | R:6525 "a120 gap mask from coverage" | 11157–11158, 25611 · `fgmask.js` |
| `_noFloatDepth` | unset | disables the a99 16-bit float ingest | a99 | ADOPTED | R:5337 (Addendum 106 "float depth ingest (a99)"); LP:10 (16-bit maps shipped) | 4571 · none |
| `_legacyExtMargin` | unset | v1 scene-extension margin law before a113 | a113 | ADOPTED | R:6378–6386 (the A/B: a113 black 0.00% vs legacy 9.72%) | 20970–20990 · `modeprofile.js`, `platecover2.js` |
| `_noRampCollapse` | unset | disables ramp collapse in the edge bake | a52–a61b | ADOPTED | R:3306 "Ramp-collapse: secondary … — kept" | 12594, 12609 · `diag_mask.js`, `depthaudit.js` |
| `_noThinLift` | unset | disables the A63 thin-lift | A63 | ADOPTED | R:3439 "thin-lift: the ribbon class, solved" | 13056–13057 · `a79b_lift.js`, `a79c_liftoff.js` |

### OPEN-TRADE (18): the user decides; do not remove

| flag | default (set) | what | introduced | verdict | evidence |
|---|---|---|---|---|---|
| `_plugMargin` | 0 (21586) | A245 margin strips: 1 window, 2 picture | A245 | OPEN-TRADE | LP:250–255 (§10A "Keep / drop?"); code 21569–21571 |
| `_plateStretchInner` | true (seams=stretched, 21589) | internal plate seams drawn stretched | S5:857 | OPEN-TRADE | code 21557 "remaining trades (seams, margin, fold-alpha, tier)"; S5:1103 "stays as the hole fix" |
| `_plateKeepAll` | false (21590) | no plate tear at all (seams=all) | S20:84 | OPEN-TRADE | S44:55–61; LP:62–64 |
| `_plateFoldAlpha` | unset → 0 | the plate obeys the A241 stretch law (1 transparent, 2 magenta) | S25:40 | OPEN-TRADE | LP:25–27; MP:109 "four trades (seams, margin, fold-alpha, tier)" |
| `_bandTierDeg` | 35 (21588) | texture band by first-uncover angle | S5_plan:174 | OPEN-TRADE | LP:72–74; MP:109 |
| `_skyInf` | 0 (21584) | sky layer at infinity | S2c (S2_sprint2_plan:38) | OPEN-TRADE (per picture) | LP:67–70; code 21553–21554 |
| `_selfSample` | false (21585) | mirrored far side as the placeholder | S5:534 | OPEN-TRADE | S5:566 "the screen call; both stay available"; S5:636 |
| `_stepFaces` | false (21587) | S5 step-face quads | S5:392 | OPEN-TRADE | S5:762–764 "a bake option … off by default for 8-bit photographs until the 16-bit re-export" (the maps are now 16-bit) |
| `_farJoin` | 0 (21591) | far field made t-Lipschitz across lines | S5:955 | OPEN-TRADE (kept as an option) | S5:1103 "the join stays as an option" |
| `_edgeTear` | unset → off | fold law outside the rest footprint instead of the clip | S32:35 | OPEN-TRADE | LP:183–186 "Which one reads better in motion is yours to say" |
| `_plugObjectRule` | false (reset 21530/21606) | A253 rest-silhouette object rule | A253 | OPEN-TRADE (gap select) | R:14205–14207 "Open, for the user: … (3) the live pass on the select" |
| `_plugExtent` | null | object-rule extent: far / skirt / side | A253 | OPEN-TRADE (gap select) | R:14205–14207 |
| `_geoLipSeed` | false | A255 two-sided seeds for continuous texels | A255 | OPEN-TRADE (gap select) | R:13908; R:14205–14207 |
| `_plugBack` | false | A257 object-back second layer | A257 | OPEN-TRADE (gap select "back") | R:13963; R:14205–14207 |
| `_plugGuided` | unset (gap select sets 1) | A249 guided membrane (mirrored detail) | A249b | OPEN-TRADE (gap-select recipe) | R:13473 "kept, flagged"; R:13737–13739 "its live pass is the recipe"; R:14206 |
| `_fragTear` | unset (gap select sets 2) | A241 per-fragment tear, modes 1/2 | A241 | OPEN-TRADE (gap-select recipe) | R:11765 "flagged … not default"; R:14205–14207 |
| `_bandFillBlend` | unset → off | A215 Shepard blend band fill | A215 | OPEN-TRADE per S57, **conflicting** | S57:236–237 "user-priced trades, not falsified premises". But R:10501–10506 records the user's verdict: "go back to the wash … re-enables it for A/B only". |
| `_enableRigidify` | unset → off | a54 rigidify small standing components | a54 | OPEN-TRADE | R:4195 "(default flip = user call)"; S57:237 |

### HARNESS-ONLY (18)

| flag | default | what | evidence |
|---|---|---|---|
| `_visStep` | unset | forces or disables the S10 visible-step floor | S19:97 "`window._visStep = 1` is a harness flag"; S35:707 |
| `_noFoldTear` | unset | restores the fixed 0.06 tear (a117) | S50:216–217 "still used as a deliberate control by posesweep.js and restblack.js. This project keeps such controls on purpose." |
| `_noCrossTexelOrder` | unset | disables the a162 cross-texel clamp | R:7909–7910 "Deliberately kept … (the A/B `harness/depthorder.js` runs against a162)" |
| `_noFishtank` | unset | drops the fishtank volume and aperture | R:7909 (deliberately kept); R:8979 |
| `_rayReproject` | unset; the UI deletes it (21769) | A/B override of `bgRayReproject` | R:3262 "a `window._rayReproject` boolean override" (152 harness files) |
| `_srCapture` | unset | stroke-repair capture dumps | R:2133 |
| `_srNoGC`, `_srNoP2`, `_srNoCont` | unset | bisect kill-flags for the stroke repair | R:2148–2150 "left in as gated debug affordances with a driver (`protrude_ab.js`)" |
| `_bsNoSweep`, `_bsVerbose` | unset | skip or log the v1 backstop sweep | R:2321 "Debug affordances" |
| `_foldProbe` | unset | claim-record probe arrays | R:4014–4015 "instrumentation stays (gated, zero-cost off)" |
| `_plugSweepCapture` | unset (`_plugSweepBake` sets it, 8390) | captures dQ/plateF/torn for the CPU sweep | CM:135, CM:301 |
| `_dbgFillCapture` | unset | fill debug capture | code 20519 (22 probes read it; no note) |
| `_seatDbg` | unset | seat debug log (dies with `_inkSeat`) | code 13280 (no note) |
| `_depthContractUI` | unset | suppresses the S44 banner | LP:205 "Console flag … suppresses the banner" |
| `_rawPass` | unset | bypasses bake sharpening | code 12527 "A55 DIAGNOSTIC"; CM:214 (no verdict) |
| `_foldFactor` | unset → √2 | overrides the per-cell fold factor | code 219 "overrides for A/B"; the constant is kept at R:5158–5165 |

### UNKNOWN (24): the notes do not settle these

| flag | default | what | what the record says |
|---|---|---|---|
| `_farPick` | unset → first arrival | 'coverage' picks the most-seen run | S4_second_layer_plan:12 "Both rules are implemented; neither is complete". No later verdict. |
| `_rimGrazeDeg` | 2° | g_min of the rim law | S2_sprint2_plan:18 defines it; no verdict on the override |
| `_confTolPx` | 1.0 px | S53 far-side confidence T | no note hit; code 9128–9133 |
| `_collarSameTexel` | off | A231b collar against the pre-a162 plate | code 17948 "Measured arm, not default"; no REVIEW entry; dies with `_plugCarve` |
| `_plugWashGated` | off | A247 gated pull-push band fill | R:13454 "stays as a flagged, measured arm; nothing default changed" |
| `_foldClaimPx` | off | A239 fold-front claim law | R:11670–11672 "it stays flagged (it fixed the one scene, bristlecone…)" |
| `_seedRevealPx` | 24 | a95 seed width in px (A239 uses √2) | R:11575; tied to the A239 arm |
| `_fragTearFactor` | 2.0 | A241/A212 stretch factor | S48:99 (units only) |
| `_fragTearMode` | unset | alias for `_fragTear===2` (18325) | no note |
| `_fragTearUngated` | unset | ungates the A241 tear | no note |
| `_a212Ungated` | unset | A212 fold scan outside the band | CM:382 only |
| `_geoLipFloor` | unset | A253c lip floor without the object rule (2 = observed classes) | CM:304, CM:358; no verdict |
| `_geoLipBound` | never set | A253 lip bound without the object rule | no note |
| `_geoDepth` | never set (`!== false`) | `false` stops the band depth taking the far field | CM:310 only |
| `_pocketProm` | off | pocket promotion in the ground flood | code 14423 "measured 576k over-promotion on the warrior"; no note |
| `_plugGroundUp` | off | A59e ground-up plug depth | R:5199 "opt-in path, NOT fixed" |
| `_bgPlugBand` | off | v1/plate bud band instead of the tight silhouette | CM:314, CM:435 only |
| `_bgIslandDilate` | −1 | a fixed px island band | CM:314 only |
| `_coneSlopeDerived`, `_coneSlopePh` | off / pw | derived cone-slope form | R:5043 "NOT SETTLED … awaiting an on-device measurement of k" (k was later measured and made a field, A109; no verdict on this flag) |
| `_noV2Anamorphic` | unset | v2 backdrop → full-frame clone | code 13510 only |
| `_noGroundStop` | unset | skips the ground flood | no note |
| `_grdEdge` | 0.10 | ground-flood luma edge | R:4734 lists "luma edge 0.10"; no verdict |
| `_srNoScale` | unset | disables A42 stroke-scale | code 12660 only |

### Comment-only residues (8): the flag is gone, the comment still offers it

| name | comment line | what to do |
|---|---|---|
| `_bandFillLegacyWash` | 16817, 16838 | Remove the comment. It still advertises a revert that no longer exists. `harness/a213_ab.js` and `a215_ab_fresh.js` set it, so those A/Bs are now inert (the a134 hazard). ROADMAP:116 is also stale. |
| `_coneWide` | 133, 135 | Stale comment (R:6961, the dead-flag lesson). `abguard.js` still names it. |
| `_noFillBandLimit` | 14506 | Stale (only `_fillBandLimit` exists). |
| `_noSeatFloor` | 13161 | Stale (the seat is now opt-in via `_inkSeat`). |
| `_plugPullPush` | 16039 | Stale. |
| `_noiseTol` | 15275 | Stale. |
| `_geoObsMode` | 9375, 9412 | Arm removed (R:13895); the comment remains. |
| `_foldWindow` | 18348 | Records its own removal (R:12969); fine. |

Two notes are also stale: LP:186 and CM:1159 still describe `window._farPlate2D`, and S21:35 describes `_noiseTiles`. Neither exists in the code any more.

## Safe to remove now

These are FALSIFIED or ADOPTED and do not touch a live user choice. Default-path frames should stay byte-identical; use the a134 served-identity guard and regress.js to check.

- **FALSIFIED:** `_fillBandLimit`, `_nearestAnchorWins`, `_plateRowColor`, `_plateMembrane`, `_strokeAdopt`, `_inkSeat` (with `_seatFloorFlat` and `_seatDbg`), `_plugBackTex`, `_envelopePlateStep`, `_plateNearOnly`, `_vpScan` (with `_noVpScan`, `_scanRange` and `_legacyScanWarp`).
- **ADOPTED revert hatches:** `_dirPlate`, `_noSmearSnap`, `_noPromBound`, `_noConeFill`, `_noDescFloor`, `_noDequant`, `_legacyPlateTear` + `_noPlateTear`, `_sConeFixed`, `_noPerPixelCone`, `_noExactCone`, `_legacyPlugLUT`, `_legacyV2Budget`, `_scanPoses`, `_scanLegacyPoses`, `_winFloorLegacy`, `_noSeedReveal`, `_noOrderClamp`, `_noContactCut`, `_noV2PairValid`, `_noBgIslands`, `_plugZBias`, `_plugConeDepth`, `_legacyGapPass`, `_noFloatDepth`, `_legacyExtMargin`, `_noRampCollapse`, `_noThinLift`.
  - Caveat: many old `aNN_*` harnesses set these. After removal those arms silently stop diverging, so retire or update those drivers in the same change (A127's practice).
  - Several hatches (`_noBgIslands`, `_legacyExtMargin`, `_noV2PairValid`, `_legacyV2Budget`) sit on the v1/v2 paths. The panel default never exercises those paths, so byte-identical default frames do not cover them.
- **ADOPTED panel rules:** `_ceilCut` and `_despeckleLines`. Make both unconditional, drop the `rules` select, and update `s44_envelope.js`/`s44_contract.js`.
- **Comment residues:** the 8 above.

## Needs the user's live-pass call

- **The four named trades:** `_plugMargin` (LP §10A), seams (`_plateStretchInner`/`_plateKeepAll`), `_plateFoldAlpha`, `_bandTierDeg`.
- **Other kept screen choices:** `_skyInf`, `_selfSample`, `_stepFaces`, `_farJoin`, `_edgeTear`, `_enableRigidify`.
- **The gap-rule select arms:** `_plugObjectRule`, `_plugExtent`, `_geoLipSeed`, `_plugBack`, `_plugGuided`, `_fragTear`. R:14205–14207 leaves the live pass on this select open.
- **`_bandFillBlend`:** S57 calls it a user-priced trade, but A162 already records the user saying "go back to the wash". Ask whether that verdict counts as the final one.

## Needs an owner decision: the notes conflict or defer

- **`_farLabel`:** falsified per S53. S57 calls it "arguable" and S58 defers it to the sheet A/B. Remove it after the sheet A/B, or now if S53 stands.
- **`_plateNearOnlyPx`:** the user rejected the rule (S50). S50 kept it deliberately, and S57 does not list it.
- **`_plugCarve`** (and `_collarSameTexel`): the demand carve is falsified (A172), but the region carve shares the flag and "the carve as an optimisation" is a plan item (R:12886).
- **`_tearLaw` / `_farRule` / `_plugMembrane` / `_plateFlushExempt`:** adopted on the default path, but they still back the panel's `membrane` far-side option. Removing them means dropping that option. S44 §3 kept every panel option.
- **The 24 UNKNOWN switches:** each needs a verdict written down before rule 5 can apply.

## Side finding (not a removal)

The gap-rule select leaks state into later bakes:
- Any object-rule arm sets `_plugMembrane=1`, `_plugGuided=1` and `_fragTear=2` (21533).
- Neither the `default` branch of the gap select (21530) nor `bakePlate` (21606) resets them.
- So after one gap-rule bake, every later plate bake in that session silently carries the guided membrane and the per-fragment tear. `_plugMargin` is re-set by `applyPlateOptions`, so it does not leak.
