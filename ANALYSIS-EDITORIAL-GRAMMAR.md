# On the 6DoF editorial grammar paper, and whether the fill work is a rabbit hole

## 0. The convergence

The paper's §6.2 and this project's `k` analysis are the same result reached
from opposite directions, and neither knew about the other.

**Paper:** maximum disocclusion area is a computable function of presentation
scale *s*, the cone half-angle of **V**, and scene depth range. Because *s* is
authored and **V** is declared, the fill budget is known at authoring time.

**This project:** `k` = screen shift across the depth range at the cone rim,
`k = tan(θ_half) × relief`, disocclusion extent `= Δδ·k`, and every open defect
family is `k` in a different hat.

`s` **is** the relief term. **V**'s half-angle **is** the tan term. Same product,
same bound, same conclusion: **if the product is authored, fill is a finishing
pass; if it is inherited, fill is the ceiling on the medium.**

Two independent analyses landing on one inequality is the strongest evidence
either of them is right.

## 1. So is the fill work wasted?

No — but it is being done at the wrong point on a curve that was never chosen.

The paper's claim is conditional: *if* demanded parallax is held inside what the
data supports, fill degrades to a garnish. **moebius does not currently meet that
precondition.** Measured: `k = 568` at the 45° cone on the troll — 67% of image
width. The sim-viewer HUD puts the reveal at the rim at **634 source px against
63 px of machinery**, a 16× shortfall.

That is precisely the regime §1.1 predicts for naive coupling: *"a 20% baseline
in a close-up demands hole regions no single-viewpoint capture contains. Naive
coupling makes fill quality the bottleneck of the entire medium."*

So the paper is not saying the inpainting work was worthless. It is saying **you
are paying for a parallax budget nobody chose.** Bring the product down and the
fill machinery you already have becomes adequate.

## 2. A correction to my own earlier advice

In `CONE-DECISION.md` §2 I wrote: *"Cone is free. Relief is not. Turn the free
knob first, all the way to the physical bound. Only touch relief if `k` is still
too large after that."*

**That was wrong for this asset class, and the paper is right.**

My reasoning treated relief as fidelity — reduce it and you flatten the scene
away from its true depth. That holds for a photograph. **It is meaningless for a
painting.** There is no true relief for a Frazetta; the depth map is an
estimator's invention over an artefact that never had a third dimension. So
relief is not a fidelity budget being spent. It is **pure authorship**, and the
paper's framing — *s* as a first-class authored dial, set per shot — is the
correct one.

That inverts the ordering. Relief should be the **first** thing authored, not the
last resort. And once `s` is authored, `k` is bounded by construction and the
whole downstream defect stream — fold limit, tear threshold, plane count, band
width, hidden-depth precision — is bounded with it.

## 3. The actual rabbit hole

Here is the sharper version, and it is not about inpainting.

**The paper's contribution is what happens at the cut.** §2.3 says the
normalization law is textbook (Kooima's CAVE formulation, and view-camera
movements before it). §10 says view synthesis *"is a crowded, well-served field,
and this work contributes nothing to it."* The claim rests entirely on §3 — the
editorial algebra, anchor-locked transitions, the cut graph, cycle consistency.

**moebius has one image and no cuts.** As currently built it cannot demonstrate
the paper's actual contribution at all. It demonstrates the base effect, which
§8 correctly says the framework *"claims nothing about."*

So the rabbit hole is not "too much inpainting." It is:

> **You are perfecting single-image disocclusion fill in service of a thesis
> about transitions, in a build that has no transitions.**

Another month of fill work tests nothing the paper asserts. **Two assets and one
anchor-locked cut between them tests the whole thing** — and that is days, not
months, in a renderer that already handles a single asset well.

## 4. The cheapest experiment that would settle it

The paper hands you the protocol in §6.2 and does not seem to notice it is a
week's work rather than a program:

> *"A well-constructed demonstration should therefore use **deliberately crude**
> fill — flat regions or edge smears, clearly labelled — because the editorial
> point must survive ugly fill, and showing that it does is itself the argument."*

Run exactly that:

1. **Author `s` down** until `k` lands somewhere the existing machinery serves —
   say `k ≈ 40–60 px`, which is 0.05–0.07 of image width instead of 0.67.
2. **Turn the fill machinery off.** Pull–push only, or flat background colour.
   No plate, no plug, no band, no SD.
3. **Two assets, one cut, anchor-locked.** Both anchors mapping to the same
   display region for every viewpoint in the cone.
4. **Look at it.**

Three outcomes, all informative:

- **It reads.** Then the paper's central claim holds, fill is confirmed as
  garnish, and the last several months of fill work were a solution to a
  self-inflicted problem. Set `s` per asset and move to the editorial layer.
- **It reads but looks cheap.** Then fill is a quality dial rather than a
  correctness one, which is still a complete reframing of the work.
- **It does not read even at small `k`.** Then the paper's precondition is
  insufficient and that is a genuinely important negative result — arguably the
  most valuable thing this project could produce, and it would need saying before
  any provisional is filed.

Note what this experiment costs: **one authored constant and a second asset.**
Not an architecture.

## 5. Honest read on the paper

**Strong.** §1.1 is the best thing in it: working distance `D = f·h/H`, the
observation that parallax gain and lens rhetoric are *both* functions of `D`
alone, the 600:1 spread between an ECU and a landscape establishing shot, and —
the sharp bit — *"the effect is invisible to a centred viewer and grows with
off-axis offset, so it cannot be caught by authoring on-axis."* The numbers check
out. That section would stand on its own.

The `s`/`ρ` decoupling is a real capability claim: physical optics cannot
separate depth compression from parallax gain because both are `D`, and a
renderer can. The dolly zoom reducing to *"animate ρ with the anchor locked"* is
the kind of one-line special case that suggests a formalism is describing
something real. The ∀-**e** quantifier is a clean distinction from
computational-zoom prior art. And §6's scope test — *"would a competitor who
rejects this entire approach still need it?"* — is a genuinely good discipline
that directly answers the question you asked me.

**Risks, stated plainly.**

- **The law is textbook and the paper says so.** Everything rests on §3, which
  is the shortest technical section. Anchor-locked transition reduces to "both
  anchors map to the same display region" — reasonable, but not much once you
  have the invariance. The cut graph and cycle consistency are the substantial
  part and get half a page.
- **Editors already hold subjects across cuts.** Match cuts and graphic matches
  are exactly this. §8's *"medium precedent"* is honest about it. The novelty is
  the viewpoint-invariant version, which is narrower than the framing implies.
- **It is a grammar for a medium whose playback does not work yet.** This is the
  inversion. §9 lists notation and the inverse problem as open, and both are
  research programs. Meanwhile the reference implementation produces speckle and
  smears at 45° because `k` was never authored — a problem the paper's own §6.2
  solves in a sentence.
- **The disclosure gate is creating the inversion.** Filing pressure rewards
  writing the claim before building the demo. That is a legitimate strategy, but
  the demo is *days* away and would materially strengthen the filing, because
  the strongest form of any of these claims is "and here it is, working, with
  crude fill."

## 6. What I would actually do

1. **Author `s`.** Today. One constant, printed alongside `k`. This is the same
   action as the cone fix arriving from the other side, and between them they
   bound everything.
2. **Run §4's experiment.** Small `s`, crude fill, two assets, one cut. Days.
3. **Keep the depth-provider work.** It is about depth *quality* — boundaries,
   ink, the troll's arm — which `s` does not touch. Orthogonal, still worth it.
4. **Stop escalating fill sophistication** pending the experiment's outcome. Not
   "delete it" — freeze it and let the measurement decide.
5. **If the experiment reads, put the fill effort into the editorial layer
   instead**, because that is where both the paper's claim and any defensible
   contribution actually live.

The one-sentence version: **the paper is right that fill should be a garnish, and
it is not a garnish here only because nobody ever chose `s`.**
