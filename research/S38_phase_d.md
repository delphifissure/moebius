# S38 — Phase D: an arm-side confidence, and two corrections to S36 (2026-09-20)

Phase D of the S37 plan, in the order the plan set: (1) the arm-side confidence that blocks any rule, (2) the wide-range
exclusion, (3) the resolution ablation. Items 2 and 3 both came back differently from how S36 framed them, so they are
corrections rather than confirmations.

---

## 1. The arm-side confidence: found

S36 gave a truth-free confidence for the model. The arm had none, so the two could not be compared. Four observables the
construction already implies were tested (`bleed/armconf.py`), binned into quintiles and scored against truth:

**`reach` — the texel's distance from its owning sheet's own visible patch, divided by that sheet's own extent E.** How far
beyond its own evidence the sheet is reaching. This is the ratio the reach law of §30 uses as a *gate*; here it is used as a
*degree*. It is monotone in the arm's error in both scenes:

| reach quintile | L5 heads-only, arm \|e\| | L6 figure-only, arm \|e\| |
|---|---|---|
| lowest | 0.0000 | 0.0000 |
| 2nd | 0.0708 | 0.0000 |
| 3rd | 0.3011 | 0.0000 |
| 4th | 0.4214 | 0.0754 |
| highest | **0.5487** | **0.0913** |

**`lipsp` — the spread of the hole's far lips at the texel**, in visible steps. Also monotone on L5 (0.000 → 0.120 → 0.238 →
0.425 → 0.547) and weakly so on L6. **`owner is sky`** separates strongly on L5 (sky-owned 0.252, otherwise 0.012) and not at
all on L6 (sky-owned 0.000).

**So the blocker is lifted: the arm can say where it is unreliable, from its own construction, with no truth and no tuned
constant.** `reach` is the one to keep — it is monotone in both scenes, it is already computed, and it has a meaning rather
than being a correlate.

## 2. But it does not yet give a rule, and I stopped rather than fit one

Having both confidences is not the same as being able to choose. The crossing against the model happens in a different place
in each scene: on L5 the model wins from the second reach quintile onward, on L6 the arm wins in **every** quintile including
the highest (0.091 against the model's 0.153). The arm's error at high reach differs six-fold between the two scenes, so no
single reach threshold serves both.

What does separate them is the model's own scene-level confidence — 0.013 on L5 against 0.096 on L6. A rule would therefore
be: gate on the model's visible-region disagreement for the scene, then use `reach` to place the swap within it. **That is
two thresholds fitted to five scenes with exactly one positive example.** This project has falsified six constructions that
looked better supported than that, so I am not proposing it. What is needed is more scenes in the L5 regime, not more
cleverness on these.

A ceiling worth knowing: on L5 a reach-placed hybrid gains little over simply using the model everywhere (0.034), because the
arm is only better in its lowest quintile, where both are near zero. **The decision is effectively per scene, not per
texel**, which makes the missing piece a scene classifier and not a blending rule.

---

## 3. Correction to S36: S15's collapse is the depth law, not the model

S36 said a relative prediction "cannot carry a hidden range that far outside the visible one". Measuring the error in the
model's own units instead of metres says otherwise:

| scene | scene depth (outer) | model \|e\| in d units | model \|e\| in metres | the law's gain dm/dd where it fills |
|---|---|---|---|---|
| L1 | 0.19 m | 0.031 | 0.018 | 0.57 |
| L5 | 0.64 | **0.022** | 0.034 | 1.79 |
| L6 | 0.64 | 0.143 | 0.170 | 1.69 |
| S15 | 8.64 | **0.109** | **2.57** | **19.72** |

S15's error in d units (0.109) is *smaller* than L6's (0.143). The 2.57 m is 0.109 multiplied by a law gain of 19.7 m per
unit d. **The model is not uniquely bad on S15; the scene's depth law amplifies everyone's error by twenty.** Our own arm on
S15 is 0.264 m, which is 0.013 in d units — still eight times better than the model, so the verdict does not change, but the
reason does, and the proposed "wide-range exclusion" was aimed at the wrong thing.

**The methodological consequence is larger than the finding.** Our kit scorer reports metres, and metres are amplified by a
factor that varies twenty-fold across the kit for reasons that have nothing to do with a construction's quality. The app's
own working space is d, and parallax at the window follows d, not metres. **A score in d units, or in visible steps, would
compare scenes on equal terms; the metre score over-penalises wide scenes and flatters near ones.** That affects every table
in S35, not just this note. It does not change any ranking measured *within* a scene, which is how the arm decisions were
made, so nothing already decided is at risk.

## 4. Correction to S36: the 518² resize was not handicapping the model

S36 closed with "every number above handicaps the model", citing the resize of 800×450 into 518². Tested by running an
aspect-preserving letterbox against the squash:

| | L6 whole band | L5 whole band |
|---|---|---|
| squash (what S36 did) | 0.1702 m | **0.0343 m** |
| aspect-preserved letterbox | 0.1719 | 0.2874 |

No difference on L6, and much worse on L5 — though that is an artefact of the padding (black borders and a fabricated far
region inside the target mask) rather than of resolution, so it does not prove the squash is *optimal*. What it does show is
that **the squash is not the explanation for the gap**, and S36's caveat overstated the case. The horizontal downsample is
only 1.54×, and vertically 450 → 518 is an upsample, so there was less resolution loss to begin with than the caveat implied.

---

## 5. Where Phase D leaves the sunflowers

- **Delivered:** an arm-side confidence (`reach`) that is monotone in the arm's error and costs nothing to compute.
- **Not delivered:** a rule for choosing. It needs a scene-level classifier for "is this the L5 regime", and one positive
  example is not enough to build one.
- **Corrected:** S15 is a units artefact, not a model failure; the resize is not a handicap.
- **Unchanged:** the model still helps one kit scene in four, and the sunflowers are still the one it helps.

**Recommendation.** Phase D has gone as far as five scenes allow. The next thing that would move it is not more analysis but
**more scenes in the L5 regime** — fields whose pieces merge into the ground and cannot be labelled by clicking — which the
L5 recipe makes cheap to build, at about twenty minutes of truth each. Three or four of those would turn the scene gate from
a guess into a measurement. That is a contained piece of work, but it is still research, and the S37 plan's judgement
stands: **Phases A and B should come first.**
