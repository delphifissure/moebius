# S57 — direction review: are we on the right track? (2026-09-22, working notes)

Requested by the user: "please read everything and make sure we're on the right track". This file is written
incrementally while reading, so conclusions survive context compaction. Corpus: `ROADMAP.md` (183 lines),
`REVIEW.md` (14 215 lines, Addenda 1–176+), `research/` (~20 500 lines, 100 files), the app repo's harness.

Method: read the documents that state the GOAL and the RULES first, then the history in order, and hold every
recent decision against them. A decision can be well-evidenced and still off-track.

---

## 0. The yardstick — from `ROADMAP.md` (state 2026-08-05, v3.13.44)

**The product.** One image + one depth map → a head-tracked 2.5D portal, "a window, not a fishtank".
Disocclusions are filled by a baked background plate, "the plug". An SD inpaint/outpaint stage will
eventually supply real texture; "everything current is the geometry and placeholder-texture layer underneath".

**The user's prime rules, recorded as non-negotiable:**

1. Generalise to ANY image with ZERO per-image tuning.
2. Every magic number cited or DERIVED; "a constant is only safe if its units are invariant to the thing you're
   about to vary."
3. Trust the depth map. SD inpainting is a LATER texture stage.
4. The background is a PLUG: fills disocclusions only. No cloning.
5. Falsified premises get REMOVED from the code and recorded — never left behind flags.
6. Never widen a failing test range to make it green.
7. When two statistics contradict, look at the buffer. A/B arms must diverge downstream of the flag.
8. **The user's screen is the final authority on aesthetic trades.** Metrics cannot price a semantic artefact
   against a texture artefact.
9. Numbered plain-language summaries + test shots; never over-claim.

Plus: "Frames are the evidence; metrics are advisory."

### First-pass concerns raised by the rules alone (to be confirmed or cleared by the reading)

- **C1 — Rule 2 vs my Sprint 30 plan.** As I specified it today, Sprint 30 SWEEPS α, γ, floor and cap and
  "tunes on the noisiest picture". That is fitting constants, which rule 2 forbids unless cited or derived — and
  Banz's values are cited for SGM matching costs, not for our problem. The rule-compliant version exists and I
  half-noted it: the **cap** is already derived (the S50 cliff tolerance in screen px); the **floor** can be
  derived from the per-tile effective quantum (Sprint 14); the **contrast scale** can be self-calibrating, as in
  Szeliski et al. §4.3, β = (2⟨‖Δx‖²⟩)⁻¹ from the image's own statistics. The sweep should survive only as a
  sensitivity check on derived values, never as the way to choose them. **Likely correction.**
- **C2 — Rule 5 vs flag accumulation.** The recent arc carries many window flags (`_farLabel`, `_plugMargin`,
  `_bandTierDeg`, `_tearLaw`, `_farRule`, `_skyInf`, `_despeckleLines`, `_noiseTiles`, `_plateStretchInner`,
  lam:'auto', …). Any whose premise was falsified (S51's farlabel: settled AGAINST in S53) must be removed, not
  left behind a flag. **To audit in the code.**
- **C3 — Rule 8 vs metric-driven decisions.** Today I wrote "the margin default is banked" on LPIPS + my own
  reading of sheets. By rule 8 that is the user's call on their screen; my job is to put the frames in front of
  them and say what I think, not to bank it. Same for the 2× depth and hybrid decisions in Sprint 29.
- **C4 — Rule 3 vs scope drift toward the texture stage.** The roadmap puts SD/texture in the MID term and says
  "once SD supplies band content, the wash-vs-fill debate dissolves; the geometry stays authoritative." A large
  share of recent work (return path, LaMa, hybrid, occluder-informed inpaint arms, task #59) is texture-stage
  work. May be user-directed after 08-05 — **to check against META_PLAN and the later notes.**

---

## 1. `META_PLAN.md` (716 lines, 2026-09-12 → 09-21) — read in full

### C4 cleared: the texture-stage work was directed, not drift

`PLAN_REVIEW.md` (2026-09-15) restated the goal and ranked "the diffusion loop never closed" as weakness #1, and
reordered the work "close the loop first". S37 and S41 then put Phase B (reimport + one real inpaint) second only
to the live pass. The return path, LaMa and one real inpaint were the plan. **C4 withdrawn.**

### Two goal facts I had wrong or incomplete

- **The envelope target is ±90° (fishtank)**, corrected by the user on 2026-09-16 (S35 entry: "the target is ±90°
  (fishtank), the instruments run at 45°/30°"). The ROADMAP's "window more than a fishtank" is superseded on this
  point. Every argument I made from "our envelope is ±45°/±30°" (e.g. against Zhang & Tam) holds a fortiori.
- **Margin was set OFF by the user's word** (2026-09-15: "margin off at the user's word. The four trades (seams,
  margin, fold-alpha, tier) stay panel choices until seen in motion"), and S44 kept it unpromoted: "trades only a
  screen can price". Principle restated in META_PLAN: **"defaults change only in the live pass."**

### C3 CONFIRMED — S56 overstepped on margin

I wrote in S56 "the margin default is banked … Default it on". That is on the wrong side of an explicit user
decision and of the principle above. The evidence is good (4/4 pictures, a black frame-edge tear on the sheet) and
is exactly the "seen in motion" evidence the user asked for — but what it earns is a **recommendation put in front
of the user's screen**, not a banked default. **Correction required to S56 wording; check the code default was not
flipped.**

### C5 — THE CENTRAL QUESTION THIS REVIEW HAS SURFACED: is Sprint 30/31 re-solving what S35 already solved?

S35 (§1–§58, 2026-09-16 → 09-20, the largest single effort in the project) built offline **one continuation sheet
per visible surface**. That construction removes S33's class 1 *structurally*: if a surface has one sheet, its rows
cannot be given two depths. Measured: the bare plane removes **50–92 % of the wall length**; with SAM masks it
**cuts the per-line law's vertical wall length by 80 %** (troll, vermeer). S37/S41 planned **Phase C: "decide the
sheet model's port by an on-screen A/B on four pictures, one day to decide a weeks-long port."**

My S54 → S55 line (read 23 stereo/DIBR papers; specify Sprint 30 = a better join cost for the PER-LINE law, Sprint
31 = a gated median post-filter on the per-line law's output) attacks class 1 by **patching the per-line law**.
If the sheet model already removes class 1 by construction, then Sprints 30/31 are polishing the construction the
project had already decided to replace, and the one-day on-screen A/B that decides the port is the higher-value
item. **Must establish: did Phase C ever happen, and what did it decide?** (Sprint numbering in the task list
diverged from S41's; S51 "cross-line labelling" may have been the path taken instead of sheets.)

### C6 — the placeholder, not the geometry, is two thirds of the mess

S47's standing conclusion: "at 45 deg the ramps are 3.7 % of the picture against 10.5 % invented colour, so **two
thirds of what reads as messy is the placeholder, which no representation reaches.**" S33's class 1/2/3 are
GEOMETRY. If the visible mess is dominated by placeholder colour, the highest-value work is the texture stage
(Phase B, which S53 was advancing), not more geometry — unless the user's complaint (S33: "why does the plate streak
at all") is specifically about geometry streaks. **To weigh against S53's motion results.**

---

## 2. The plans and the recent notes (S37, S41, S44, LIVE_PASS, S49–S54) — read in full

### C5 SETTLED: the sheet A/B was planned three times and never run

- **S37 (09-20)** Phase C: "bake the same four pictures both ways offline, render each through the envelope at the
  same poses, and put them side by side on screen … One day of work to get the answer, against weeks to port blind."
  Listed under "Not recommended": "Porting the sheet model before the on-screen A/B".
- **S41 (09-21)** kept it as Sprint 26 (1 day, gated on 23 and 24).
- **S49** kept it as "Sprint 29 — the sheet A/B".
- **What happened instead.** Sprint 26 became the cliff tolerance (S50), 27 the cross-line labelling (S51), 28 one
  real inpaint (S52), then R8's list (S53), then my S54/S55 literature line. The task list's "Sprint 29" became
  "bank three measured wins". **No note records the sheet A/B being run or deliberately dropped.** It drifted out.

### What the recent notes themselves concluded, which my S54/S55 plan did not follow

- **S50** (the user's own verdict on the tolerance arms: *"they are all streaky as hell — why in the world are we not
  getting clean outlines"*) located the streak in the far field's **per-line construction**: "74 % of the troll's
  streak length is the construction disagreeing with itself."
- **S51** built the cross-line labelling on the per-line law and found it **invisible** (1.39 % of pixels differ,
  nothing the eye can find). Its closing line: *"the next attempt must change what the candidates ARE — that is,
  stop extrapolating per line — which is what S33 said a week before this sprint."* That is the sheet model.
- **S51** also said: *"a geometry fix cannot be judged on screen while the band is a wash … class 1 will shear
  visibly once there is real texture on that surface, and the fix becomes judgeable then."* → **content first.**
- **S53** then measured S51 in motion: sFD 0.0005 from the wash, temporal step +0.8 % (worse). Closed.

### C5 CONFIRMED — Sprints 30/31 as specified are off-track

My S54 → S55 plan (Sprint 30: cap and reshape S51's join cost; Sprint 31: gated median on the per-line law's output)
**improves the energy of a construction measured invisible on stills and in motion, and patches the per-line law that
S33, S50 and S51 all concluded must be replaced.** S54's prediction ("capping keeps the class-3 halving while removing
the 11 % real-step damage") is falsifiable, but even if it lands, it moves a wall-length number that S51/S53 showed
the eye does not see under the wash. The reading (S55) was not wasted — the clamped two-sided join cost, the gated
median, Criminisi/Bornemann normalised convolution and Shih's explicit connectivity all transfer to the SHEET model
(which also has joins between sheets and a band to fill) — but they are **inputs to the sheet port, not a sprint on
the per-line law.**

### The condition S51 set for judging geometry is now met

S51 said geometry becomes judgeable once the band carries real texture. **S52/S53 put real texture in it** (LaMa arm
A, and the reveal-thresholded hybrid H_rev1, which beat both endpoints in motion). So the one-day sheet A/B should now
be run **with the inpainted band**, not the wash: per-line + hybrid vs sheets + hybrid, same poses, on screen. That is
the first time the comparison can show what S33 measured.

### C3 compounded: S53 and S56 both lean toward defaults the user set

S44 kept margin off "at the user's instruction (the clamp-extended strips are the outpaint placeholder you did not
want)". S53 "What to do next 1. Turn the margin on" and my S56 "banked / default it on" both argue past that. The
motion numbers are real and are exactly the "seen in motion" evidence META_PLAN asked for — **so they go to the
user's screen as a recommendation with frames, and the default stays off until the user says otherwise.** Same for
da2x (S53 already says "needs a person to look at it") and the hybrid ("if a look on screen agrees").

### A pattern worth naming: the live pass keeps being displaced

S37: "Eleven sprints of measurement have gone by since anything changed on screen … the fastest way to learn
something genuinely new now is to look at a picture." S44 did the live pass's code half and listed three things that
"need eyes". Since S44 there have been six more measurement sessions (S47–S56) and the user's only recorded on-screen
verdict is S50's "streaky as hell". Every S53 recommendation ends with "put it on screen". **The bottleneck is not
measurement; it is getting frames in front of the user in a form they can judge in minutes.**

---

## 3. `REVIEW.md` Addenda 1–149 (lines 1–10 000) — the lessons the recent notes have not carried forward

### C7 (NEW, serious) — the S53 motion metric is the kind of metric Addendum 126 banned from gating

Addendum 126 (a117 bisect): a triangle stretched across a reveal "is *smooth*, so it lowers comb. It *covers*, so
it lowers black. The arm that produced the taffy scored best on both." Its standing rule: **"A metric that answers
'is this pixel painted' or 'is this neighbourhood smooth' will always prefer the smear. Neither may gate a change
again. The acceptance test is the picture: a side-by-side at the user's controls, plus rest fidelity against the
source."** Addendum 125 adds: black% read 0.00 while the crystal mountain collapsed flat; Addendum 137: a
self-referential metric (each arm against its own rest) is blind to a constant defect.

S53's **temporal step** (mean LPIPS between consecutive frames of a sweep) is a smoothness-over-time metric of
exactly that family. An arm that covers a tearing frame edge with a smooth clamp-extended strip, or fills a band
with smooth low-frequency colour, changes less between frames and scores better **whether or not it looks right**.
Concretely:

- **margin2 (−4.8 %)** covers the frame-edge tear with clamp-extended edge colour — the very strips the user
  rejected as "the outpaint placeholder you did not want" (LIVE_PASS §1). The metric rewards covering; it cannot
  say whether the cover is acceptable. S56's "the mechanism is the frame edge tear" is consistent with that.
- **LaMa / hybrid arms (−2 %)**: LaMa "is blur-prone. The fill is smooth rather than detailed" (S52). Smooth fill
  → smaller frame-to-frame change. Part of the gain may be blur, not correctness.
- **da2x (−8.4 %)** is the least exposed: its mechanism (25 % fewer texels inside a depth transition → fewer
  stretched texels) is a geometric count, not a smoothness preference. But S53 already found it worse at 22.5° with
  higher variance — it needs eyes too.

This does not make the S53 numbers wrong; it makes them **unable to gate** by the project's own rule. It also
means S56's "4 of 4 pictures agree" is 4 of 4 readings of a metric that prefers the cover, not 4 of 4 pictures that
look better. **The frames are the evidence; the frames must go to the user.**

### Other standing lessons that bear on the current plan

- **Harness-green, screen-red, repeatedly** (A45, A47, A73, A85, A114, A125, A126): "the user's live pass caught
  what five green batteries did not". The rollback of a61–a72b (A74) and a219 (A162) were on the user's live
  verdict. Every time the project went several sprints without the user's screen, it drifted.
- **"Eyes on the grid beat thumbnails, again"** (A85, A86), **verification renders must match the user's canvas
  scale** (A47). S53 rendered at 608×342 for cost; fine for ordering, not for a look.
- **A108/A110: k varies 19× across depth**; one-number constants are wrong almost everywhere. Relevant to C1: the
  Sprint 30 constants would have been exactly this kind of number.
- **A82 (user decision)**: "figure-against-sky reveals KEEP THE WASH … the SD inpaint pass is responsible for
  painting the reveal correctly." The user has twice placed band *content* on the texture stage — consistent with
  S51's "content first" and with C6.
- **A116/A117 (user, verbatim)**: "the goal right now is to build a working, cheap quick bake (like near instant)
  so people can see a preview with correct depth inpainting before handing it to SD … not spilling over into a
  bunch of places where there are no disocclusions, and exportable for SD." That is still the clearest statement
  of what the geometry layer is FOR: a correct preview and a correct hand-off, not a finished image.

---

## 4. The code, against rule 5 (`moebiusv2/moebius.js`, read 2026-09-22)

**Margin default: not flipped.** `bgPlateOptions` still ships `margin: 'off'` (line ~21572). C3 was wording only;
S56 is corrected.

**C2 CONFIRMED — falsified premises still behind flags.** S44 §3 concluded "nothing was stripped, and that is the
finding" after going through the *panel*. The window flags were not audited the same way, and several of them
restore behaviour whose premise the record itself calls false:

| flag | what it restores | the record |
|---|---|---|
| `_fillBandLimit` | the a100 band-limit | A107: "a100's premise … was FALSE. Defaulted off, kept behind" the flag |
| `_nearestAnchorWins` | the a63b nearest-anchor law | A78: convicted as the troll "gloop" mechanism |
| `_plateRowColor` | a70 row colour | A151: refuted by its own A/B (ghost +92.7 %, hard clone on misses) |
| `_strokeAdopt`, `_inkSeat` | a51 ink adoption, a56 seat | A61/A61b: founding premise false on the shipped map |
| `_farLabel` | S51 cross-line labelling | S53: closed on perceptual evidence ("stays off") |
| `_plateNearOnly` (quantum form) | S46 tolerance in quanta | S50: the pixel form dominates it on every column on both pictures |
| `_plateMembrane` | the a69 membrane on the plate | A86: "NOT the cure", no other role recorded |

Rule 5 says these leave the code and the notes keep the record. Some are arguable (`_farLabel` was parked "until the
band carries content", which is now true, and the sheet A/B below is the place to settle it; `_bandFillBlend` and
`_enableRigidify` are user-priced trades, not falsified premises, and are not in the table). **Recommendation: one
hygiene pass, flag by flag, each removal citing its addendum, with the a134 guard that the default path's frames stay
byte-identical.** Not done in this review: removing code is a change, and a review should not ship one.

## 5. Task 61, run: the band's error does NOT follow its medial axis

`harness/truthkit/medial_axis.py` (the fixed version: bad-pixel rate at |err| > 0.02 instead of the median, and the
isophote only where the full stencil is valid), 11 kit scenes, the app's far field against the first ever-visible
hidden layer:

- **Conditional test (fixed distance from the rim, ridge vs basin):** 39 (scene, distance) cells. The ridge is
  *better* in 22, worse in 12; weighted mean difference **−0.050** (ridge minus basin), median −0.008. Only S2 and
  S27 show the predicted excess on the ridge. The prediction — error concentrates where characteristics from different
  rim points meet — is **not supported**.
- **Bornemann's angle test (error rising as structure runs along the band):** present on S2, S10 and S12 (S10:
  0.75 → 0.37 bad rate from "along" to "across"), reversed on S9 and S16, flat on S7 and S11. Pooled medians
  0.48 / 0.58 / 0.56 / 0.51 / 0.29 — no monotone law.

Reading: our far field is a per-line extrapolation, not a distance-ordered fill, so the Criminisi/Bornemann mechanism
was an analogy and the data do not back it. **Fill order is not a lever here; that line closes.** (The distance
confound is visible in the marginal rows, which is why the conditional test was built; it is the conditional test that
says no.)

---

## 6. Verdict

**On track:**
- Closing the diffusion loop (S52/S53) was the plan (PLAN_REVIEW W1, S37 Phase B) and it worked: export → inpaint →
  reimport → render, colour on the mask and nowhere else. It produced the first visible change in three sprints.
- The paper reading the user supplied was done first-hand and is sound; its prior art is real.
- Instrument hygiene is good and improving (rim confound, inert-arm guard, identity checks).

**Off track, in order of cost:**
1. **Sprints 30/31 patch the per-line law that S33, S50 and S51 all said must be replaced**, and the one-day
   sheet A/B that decides the replacement was planned three times (S37, S41, S49) and never run (C5).
2. **Defaults were argued from a smoothness-over-time metric** (S53 temporal step, S56) against an explicit user
   decision and against A126's rule that such metrics may not gate a change (C3, C7).
3. **The user's screen has been starved again.** Since S44 the only on-screen verdict recorded is S50's "streaky as
   hell". Every S53 recommendation ends "put it on screen"; none has been.
4. **Rule-5 residue in the code** (§4).
5. **Two cheap PLAN_REVIEW items never started**: real truth from phone pans (W3, "cheap, and I recommend it first")
   and the novel-view fork (W10). And A184's speed target (a bake under ~2 s; the troll bakes in 66 s) is in no plan.

## 7. Recommended course

1. **Frames to the user, one sheet, three decisions** — no default changes until they answer: margin on/off
   (silverwarrior and room at 45°), the 2× depth map against 1× (troll at 22.5° and 45°, where the metric disagreed
   with itself), and the hybrid band against the wash. Each with the metric beside it, labelled as advisory.
2. **Run the sheet A/B (S37 Phase C), now with content in the band.** Per-line law vs S35's sheet model on four
   pictures, both carrying the same hybrid inpaint, same poses, on screen. S51's condition for judging geometry
   (real texture in the band) is met, and the Sprint 25 return path (`return_band_depth16.png`, absolute depth on the band) can carry
   the sheet model's band depth into the app without a port — the band is where the two constructions differ. This decides whether the port happens.
3. **Only then the geometry sprint, under the stopping rule in S37 Phase C** (second edition, 2026-09-23, fixed before
   any frame was rendered).
   - Three arms: the per-line law, the sheets, and a plain membrane fill. All three carry one clean wash, and the user
     judges them blind on "which is cleanest?".
   - If the sheets are chosen on at least 3 of 4 pictures, the port follows, with the S55 material as design input.
   - Otherwise geometry research stops and the cleaner of per-line and plain fill ships.
   - *Superseded:* this item once read "if it is a wash, a join-cost sprint on the per-line law", which would have kept
     the loop running.
4. **The rule-5 hygiene pass** (§4), byte-identical default frames as the guard.
5. **Ask the user for 3–5 sideways phone pans** (W3). It is the only route to truth on real hidden content.
6. **Task list:** #54 and #55 are superseded by item 2; #53 becomes item 1 (recommendations, not banked wins); #56
   and #57 fold into the port or the join-cost sprint; #59 and #60 wait for item 2; #61 is done (§5).
