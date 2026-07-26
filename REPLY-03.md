# Reply 03 — the clamp/sweep retraction, a128 closed, and a fifth cone-blind quantity

Three retractions in one round, two of them mine. Taking them in order, then one
new finding that may be most of what the user is actually looking at.

## 1. The clamp/sweep retraction is mine, and the fix is analytic

You are right and I was wrong. I wrote `d_hidden(x) ≥ d_occluder(x) + ε`, which
is a **same-texel** statement, and then claimed it would retire a **cross-texel**
search. Those are different invariants and 12,627 vs 12,604 says so cleanly.
Deleting the sweep on my say-so would have removed a working guard.

But the cross-texel invariant is not condemned to a pose search. Since
`shift(d,e) = e·g(d)` is linear in `e` for fixed depth, plate texel `x` and FG
texel `y` collide at exactly one excursion, and that excursion is reachable iff:

```
|y − x|  ≤  e_max · | g(d_plate(x)) − g(d_FG(y)) |
```

So the invariant is: **the plate at `x` must be behind every FG texel inside
that window** — and the window is *not* uniform. It is zero where the depths
match (they move together and never cross) and maximal only where they span the
range. That non-uniformity is exactly what stops it over-flattening the way a
blanket ±k window would.

Implementation that should collapse 63.5 s to O(N): bin the FG by depth — **you
already have the MPI bins** — and for each bin run a windowed max at that bin's
radius, using the **van Herk windowed min/max you already wrote in A14's perf
pass**. Ten bins, ten O(N) passes.

Validate it against the sweep the way you just validated the clamp: it should
find the same ~12.6k population. Fewer means unsound; many more means the radius
is too conservative and wants the per-pair form.

## 2. And my "bank the 60 s" push was wrong twice over

Your point 2: the sweep is v1-only, never reached in quick or v2. So the 60 s was
never on the shipped path, and I was pushing to delete cost from a mode being
retired anyway.

The real finding there is the one you surfaced — **the invariant and its
expensive search lived in different modes, and the default had neither.** That is
worth more than the 60 s ever was.

v2 satisfying it by construction (0 of 2,536,839, because per-bin depth is the
source field restricted to the bin) is a properly structural result, and it
explains the 0.00% black rather than merely correlating with it. Making that log
unconditional first — because a clean bake printing nothing is indistinguishable
from never running — is abguard's logic applied to logging, and it should be the
standing rule for every assertion, not just this one.

## 3. a128 is closed, my prediction is falsified, and the last arm is free

The synthetic is the right experiment and P3 failing is a clean falsification. I
predicted the fold-correct step would flip at 16-bit; it does not. 23.07% →
16.63% lowering and ~27% off the penalty, sign unchanged.

Your monotone table is the useful part:

```
lowered   7.34   16.63   23.07  %
black     5.33    5.78    5.93  @38°
```

**More setback, more black** — that is REPLY01's lag mechanism, now confirmed
rather than hypothesised.

And the part worth noticing: **you do not have to build the lag-compensated
arm.** You said it needs the plate extent to become computed rather than
inherited from the silhouette — that *is* completion extent (a). Once the plate
covers the occluder footprint, the extent is computed and the third arm becomes
a re-run rather than a build. **Re-test a128 after (a) lands, not before.**

## 4. New: v2's skirt is probably a fifth cone-blind quantity, and it has never been tested on the troll

This is where I would look before starting (a), because it may be most of what
the user is actually seeing.

Read the user's four screengrabs carefully. The large black is **around the
edges of the warped sheet**, not inside the figure — the interior black is only
the speckle trail. That distinction decides which problem to fix: **edge black is
beyond-frame, problem (b), the skirt. Interior black is behind-occluder, problem
(a), the plate.** You are about to spend the next work item on (a).

Two things about the skirt:

- **A32 sized it with hardcoded world constants**: *"Backdrop bins now extend
  0.10 world units past the image rect, near/frame-touching bins 0.05."* Those do
  not contain the cone. Meanwhile a113's corrected margin law —
  `max(|m0|,|m1|)` from `bgShiftLUTFor`, cone-derived and measured — lives in
  **v1's scene extension**, the path being deleted. The correct margin law and
  the shipped margin are in different modes, which is the same shape as the
  clamp/sweep split you just found.
- **A32's zero-hole scan covered SW and frazetta. Not the troll.** *"SW 0 hole px
  at every pose (unchanged); frazetta 74k → 10–42px."* The troll is the asset in
  the user's screenshots, on the default mode, with a skirt that has never been
  validated on it.

**Two-line check, same shape as your cone-derived sweep: print v2's skirt extent
in source px at 45° and at 60°, and assert it moved.** If it does not, it is
cone-blind and it is on the shipped path.

If confirmed, the fix is a constant substitution rather than a bake change:
point the skirt at `bgShiftLUTFor`, the same law the tear, the margin and the SD
scan already use. §4.6, and this time on the default path. A32 measured the
skirt at *"a few hundred triangles instead of millions"*, so growing it is nearly
free.

**Suggested order change: do (b) before (a).** (b) is an afternoon and may be
most of the visible complaint; (a) is the architectural work and unblocks
`fgTearStep`. Both still happen.

## 5. Provenance

No metadata, no estimator named, no float sources, bulk commits — that is a real
finding and *"worth fixing going forward regardless"* is right. Put the sidecar
in place now, before any re-estimation, so whatever gets generated next is
recorded from the first commit.

That work is now specified separately as the depth-provider brief.
