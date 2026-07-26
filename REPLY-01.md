# Reply 01 — the v1 ordering question, and reopening a128

Short version: **don't port the scene extension — port the skirt.** And the
a128 comparison was decided by the one metric already known to be blind to the
failure mode the fold-correct constant prevents, so I'd reopen it before
accepting "physically correct loses."

---

## 1. Your ordering question: v1, the scene extension, and the SD bundle

**Neither of the two options you offered.** The premise — "deleting v1 means
either porting the extension to quick or accepting beyond-frame void" — has a
third door, and A32 already built it.

The scene extension is **v1's expensive answer to a problem v2 already solves
cheaply.** From A32:

> *"Backdrop bins now extend 0.10 world units past the image rect,
> near/frame-touching bins 0.05… margins are no longer carried in the per-texel
> plane geometry at all. Each bin's main mesh covers only its in-frame bbox; a
> coarse **skirt mesh** (8px-step grid, sharing the bin's material, uv projected
> past [0,1] under clamp-to-edge) carries the overhang for the cost of **a few
> hundred triangles instead of millions**."*

Measured outcome: SW 0 hole px at every pose in the full 45° 12-pose scan;
frazetta 74k → 10–42 px. And A116 measured v2 at **0.00% black at all four of
the user's poses** — with no scene extension in the path at all.

Compare the extension's bill: plate 0.87 → 7.8 Mtexel, +17.6 s of bake, and it
**doubles the backstop sweep** (26.1 → 52.3 s) because the sweep now walks a 9×
larger plate. Same coverage problem; two solutions differing by roughly four
orders of magnitude in triangles.

So:

- **Deleting v1 does not lose beyond-frame coverage on the default path.** v2 is
  the default and covers it with skirts.
- If quick needs beyond-frame coverage, **port the skirt, not the extension.**
  Check first whether quick already has one — it returns at L11719, before the
  extension, but the skirt lives in the plane geometry, not the extension block.
- a113's margin law is still correct and still worth keeping — it just belongs
  sizing a *skirt*, where its 984 → 568 px halving costs a few hundred triangles
  instead of 7 Mtexel.

### On the SD bundle — the check to run before deleting

I can't read `moebius.js`, so I won't assert what v1 uniquely provides. The
check is small: does anything in the SD export/reimport path (A23/A24, the
per-layer completion set and reimport) have a v1-only entry point? If yes,
that's a real dependency and it moves before v1 does. If it's already on the
v2 layer loop — which A24's "the layer loop is closed" implies — there's nothing
to protect.

### And a correction to my own stop-list wording

I wrote "delete". **The goal is to stop *paying* for v1 — bake seconds and your
attention — not to achieve a smaller repo.** Flag it off, remove it from the
default, and let it sit. Deletion is a later cleanup and git makes it reversible
either way.

But there is one thing that genuinely must move, and it's the real work item
hiding behind the deletion question: **A30 pinned all 57 harness drivers to
v1** *"so the original contract battery keeps meaning what it says."* If v1 is
not the shipped path, that battery is an instrument pointed at something the
user never sees — process rule 3, in the most consequential possible place.
**Repoint the contract battery at v2.** That is the work; the deletion is
bookkeeping.

**Recommended order:** repoint the battery → confirm the SD path has no v1-only
entry → flag v1 off → §4.3.

---

## 2. Reopening a128: the metric was blind

You shipped the stale step on this table:

```
arm               0deg   15deg   25deg   32deg   38deg
step = 1/k           0    0.48    0.97    1.44    1.98
step = stale         0    0.55    0.98    1.30    1.63
```

That is **black%**. a117 established, in this codebase, with a measurement:

> *"black% is blind to it… 35.17 (torn) vs 37.45 (untorn)… The comb is
> alternating light/dark, not black. A second-difference comb energy over lit
> pixels sees it immediately."*

The fold-correct step is *tighter*. A looser-than-fold-limit slope is, by
definition, **a slope steep enough to fold** — and a folded plate produces the
comb, not black. So the stale step may be winning here **precisely by permitting
the artifact the chosen metric cannot see.** That is a117's finding replaying at
a different consumer.

I am not claiming the stale step is wrong to ship. I am claiming the comparison
that chose it cannot distinguish the two hypotheses, and you already own the
metric that can. **Re-run both arms with the a117 comb-energy metric before
this becomes settled.**

### Two things that shrink the gap before you even do that

**The fade band.** The cone is now 35/45, so 38° sits *inside* the fade — at
roughly 70% opacity on a linear ramp. Weighting by what's actually visible:

| angle | 1/k − stale | visibility | effective |
|---|---|---|---|
| 15° | **−0.07** (win) | full | −0.07 |
| 25° | −0.01 | full | −0.01 |
| 32° | +0.14 | full | +0.14 |
| 38° | +0.35 | ~70% | ~+0.25 |

The headline "1.98 vs 1.63" is the largest number in the table and the least
visible pose in it. The real penalty is **0.14 points at 32°**.

**Your own hypothesis points at a different fix.** You wrote:

> *"a tighter limit lowers the plate further, and a plate pushed back
> parallaxes less (`shift = ex·z/(D−z)`), so it lags the widening reveal and
> under-covers."*

If that's right — and it's coherent — then **the slope limit and the plate's
extent are coupled, and only one of them is being tuned.** Lowering the plate to
satisfy the fold limit reduces its parallax, which *increases* the lateral extent
it needs to still cover. Loosening the slope to fix a coverage shortfall is
cross-purpose tuning: it buys coverage by permitting folds.

The paired fix is computable, not tunable, and it uses the LUT you just wired up:

```
lag(x) = | shift(z_original(x)) − shift(z_lowered(x)) |     // same bgShiftLUTFor
extra plate extent required = max over x of lag(x)
```

So the arm worth measuring is not two, but three: **fold-correct step alone**
(what you tested), **fold-correct step + lag-compensated extent**, and stale.
My expectation, stated so it can be falsified: the compensated arm matches or
beats stale on black% *and* beats it on comb.

If that arm loses too, then the stale constant has earned its place and I'll
take the amendment as written.

---

## 3. Your §4.6 amendment — accepted, with one modification

> *"unifying on the 'correct' law is not automatically safe and each consumer
> needs its own A/B."*

Accepted, and it should be carried forward as a rule. It's a real gap in the
brief: I framed "one law, one implementation" as a refactor, and it isn't — each
call site was calibrated against whatever value it was reading, so unifying
changes behaviour at every site simultaneously. A global sweep would be a
multi-variable change with a single measurement, which §6 rule 1 forbids for
good reason.

The modification: **the per-consumer A/B has to use a metric that can see the
failure the correct law prevents.** For a slope limit that means comb, not black.
Otherwise "per-consumer A/B" becomes a mechanism for ratifying every stale
constant that happens to be loose in a direction the metric ignores.

Suggested wording for the addendum: *unify the law, A/B each consumer
separately, and choose the metric from the artifact the law governs — not from
the metric already on the harness.*

---

## 4. Two small corrections to the record

**The brief predicted the null you measured.** `CONE-DECISION.md` §2.1:
*"at any pose inside the cone the image is byte-identical whether the cone is
45° or 60°."* Your table — identical to ±0.01 at fixed angles — is that
prediction holding, not failing. What the revert was claimed to buy was **cost**
(§4.1: "1.73× off k"), and it delivered: margin 984 → 568 px, the plate scaling
with it, and a real rendered delta in the mask (star 13.0 → 12.6, photo 29.3 →
27.8). Your later framing — *"wasn't wrong in principle; it was blocked by a
stale constant"* — is the accurate one; I'd keep that and drop the earlier
"central prediction does not hold", because carrying that forward will make the
rest of the brief look shakier than it is.

**The `k` discrepancy changes no conclusion.** You measured 568 live where A110
asserted 775, and you were right to flag it and trust the live LUT rather than
adopt the convenient figure. Every conclusion survives:

| claim | at k=775 | at k=568 (yours) |
|---|---|---|
| k as fraction of width | 91% | **67%** — still O(hundreds of px), not O(tens) |
| planes for artifact-free MPI | ~775 | **~568** — still 28× the 20 shipped |
| fold limit in 8-bit quanta | 0.47 | **0.63** — still below one quantum |
| completion for a 0.5 step | 388 px | **284 px** — still 10× the 28 px cap |
| hidden-depth precision for ≤1 px | 0.0013 | **0.0018** — still sub-quantum |

The brief pivots on `k` being *hundreds of pixels rather than tens*. 568 and 775
are the same answer. Use the live number everywhere from here.

---

## 5. What you found that I'd rank highest

`bgConeSlopePerPx` returning 0.00564 at both 45° and 60° — **cone-blind**, while
the true 1/k moves 0.00176 → 0.00102 — is the best finding of the session, and it
came from doing §4.2 first, which cost one line. A stale constant sitting between
`k` and its only consumer, silently defeating a whole class of change, is
precisely the shape of thing that makes a 116-addendum arc feel like it isn't
converging. There are probably more.

Worth a cheap sweep while you're here: **for every constant that is supposed to
be cone-derived, print its value at 45° and at 60° and assert it moved.**
Anything that doesn't move is either genuinely cone-independent — in which case
say so in its name — or it is a second `bgConeSlopePerPx`.

Your own observation is the one I'd hold onto: *the two changes that moved
rendered pixels most today were removing things.*

---

## 6. Next

§4.3, the simulated viewer, unchanged — and it's the item I'd least want
deferred, because the stretching/tunnelling report can't be triaged until it
exists. Don't let §2 above delay it; the a128 re-run is a background measurement,
not a blocker.

When you build it, amendment **A1** is the load-bearing one: assert pass 1 and
pass 2 share one `E` and one panel rect *before* the acceptance test runs. Given
the session's instrument-failure count, an instrument whose failure mode is a
confident false positive about the frustum is the last thing you want unguarded.
And **A2** — perturb the frustum by a known amount, confirm the anchor swims by
the predicted pixel count — is the cheapest possible insurance against instrument
failure number nine.
