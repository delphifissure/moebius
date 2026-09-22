# S56 — the margin default banked on four pictures, and an instrument found leaning on its own rim (2026-09-22)

Two results from the same afternoon, unrelated in subject and related in kind: both are cases where a number
that looked settled turned out to be measuring something other than what it named.

---

## Part I — Sprint 29: the margin default generalises, and the mechanism is the frame edge

S53 measured `_plugMargin=2` on the troll at **−4.8% temporal step**, the only arm in that study that was
uniformly better than wash on every sub-measure. The open question was whether one picture's win was the
picture's or the law's. Three more pictures, margin off against margin on, identical camera path, nine frames
over 0–45°.

### The numbers

Temporal step (LPIPS frame-to-frame), mean over the sweep:

| picture | margin off | margin on | change | sd off → on |
|---|---|---|---|---|
| vermeer | 0.08353 | 0.08250 | **−1.2%** | 0.00795 → 0.00788 |
| room | 0.07969 | 0.07022 | **−11.9%** | 0.00682 → 0.01014 |
| silverwarrior | 0.14038 | 0.08574 | **−38.9%** | 0.02087 → 0.01865 |
| troll (S53) | 0.05161 | 0.04914 | −4.8% | — |

Degradation at 45° (LPIPS from rest): vermeer 0.4568 → 0.4574 (unchanged), room 0.4110 → **0.3733**,
silverwarrior 0.5392 → **0.3897**.

sFD between the off and on arms of each picture: vermeer **0.0005**, room 0.0238, silverwarrior 0.0356 — the
size of the change tracks the size of the benefit, which is the consistency check one wants.

**Margin helps on 4/4 pictures and hurts on none.** The margin default is banked.

### What it is actually fixing, which is not the band

The sheets say so plainly. On silverwarrior at 45°, the margin-off arm **tears the left frame edge open to
black**; margin-on fills it with continued content. The difference image is a single vertical strip at that
edge — **5.29% of pixels at 22°, 10.47% at 45%**, and essentially nothing anywhere else. Room is the same
mechanism at smaller scale (4.40% / 8.33%, left edge with some spill into the lower left).

So the margin win is the **frame edge**, not the disocclusion band, and it is the artefact Sprint 22 built the
fold rule for. That explains the spread: the benefit scales with how much the frame edge has to reveal, which is
a property of the **composition** — silverwarrior's subject runs to the left edge, vermeer's does not. Vermeer's
−1.2% and sFD of 0.0005 are not a weak result; they are the correct result for a picture with little to reveal
at its edge.

**Stated as a rule:** margin is worth between nothing and a great deal depending on the picture, it is never
negative, and the amount is predictable from the frame edge rather than from the band. Default it on.

### One honest wrinkle

**Room's sd rises** (0.00682 → 0.01014) while its mean falls 11.9%. Replacing a growing black tear with filled
content trades a large smooth error for a smaller structured one; the strip's own horizontal streaking then
changes frame to frame. The mean is the right summary here — a black wedge opening in the frame is worse to look
at than streaked continuation, and the sheet makes that obvious — but the roughness measure noticing is correct
behaviour, and it is the kind of trade that would be invisible in a mean-only report.

---

## Part II — task #62: `return_align` was scoring its own rim

This came directly out of Bornemann & März §5 (S55 note 21), read the same day:

> *"in general, this makes ∂Ω(x) **a spurious edge, aligning the coherence flow tangentially to it** … we would
> basically end up with Telea's algorithm once again."*

Their point is that **any** filter run near a fill front without normalising by the validity mask treats the
unfilled side as content and manufactures an edge at the boundary. That is a bug class, so I went looking for it
in our band-adjacent tooling.

### `harness/return_grad.py` — clean, and already doing the right thing

It takes source labels and never forms a cross-source difference, which is Bornemann's normalised convolution by
another route. It also already **measured** its own fix: on the 42 586 rim-crossing edges the naive difference
has median |g| 0.0828 in *d* and the bi-directional mean has 0.0004. Nothing to do.

### `harness/return_align.py` — defective, and the defect was load-bearing

`sobel()` is a central difference over the whole plate. At a band texel one pixel inside the rim its support
reaches onto the plate and carries the rim step — the same 0.0828 that `return_grad` had already quantified. The
colour has an edge at the same place (the occluder silhouette). So both fields shared a large, correlated,
spurious edge on a one-texel ring, and the NCC was reading it as alignment.

Scoring on the band eroded by *k* texels, troll bundle, band 39.9%:

| k | band px | NCC | |
|---|---|---|---|
| **0 (as shipped)** | 347 177 | **0.4006** | sobel support reaches the plate |
| 1 | 314 093 | **0.1454** | −63.7% |
| 2 | 293 071 | 0.1324 | −66.9% |
| 3 | 278 041 | 0.1322 | −67.0% |
| 5 | 253 910 | 0.1294 | −67.7% |

**A 64% fall at k=1 and flat thereafter** — the exact signature of a one-texel ring, which is **9.5% of the
band** and carries depth edges **5.9× stronger** than the interior (mean 0.1433 against 0.0243).

And the verdict was resting on it:

| mask | score | shifted control | margin |
|---|---|---|---|
| as shipped | 0.4006 | 0.1828 | **+0.2178** |
| rim ring excluded | 0.1454 | 0.1434 | **+0.0020** |

A factor of 109. Against the calibration line the script already printed — the same measurement on the **visible
plate**, where colour and depth are both observed and therefore aligned by construction, at ratio **2.70×** — the
band now reads **1.01×**.

**So on the band proper, the pair is not distinguishable from a displaced copy of itself.** That is precisely
what the shifted control exists to detect, and the rim was masking it. Note the band's *raw* NCC (0.1454) is
higher than the visible plate's (0.0774) while its margin is 24× smaller — the signature of "both maps are busy
in the same region" rather than "the edges coincide", which is the failure the control was written for.

### What this does and does not overturn

**Nothing is retracted.** `return_align` is cited once, descriptively, in S53 ("measures the symptom their SPADE
prevents"); no numeric conclusion rested on it. And the run above uses the shipped plate depth and the wash
colour, so it is a reading on *our own* band fill, not a verdict on any supplier's return — a wash has few edges
for depth edges to coincide with, so a low score there is expected rather than alarming.

What changes is that the instrument now has **a calibration (2.70× on observed data) and a reading (1.01× on the
band)**, and the gap between them is the room the return path has to improve in. That is a far more useful
instrument than one reading 0.4006 and looking like a pass.

Fixed in `harness/return_align.py` (moebiusv2 `86a725b`): the band is eroded by one texel before scoring, and
**both numbers are printed** — the honest one and the old one — so the size of the defect stays visible instead
of being quietly corrected away.

### The general lesson, and where to look next

Three mechanisms are now known to produce **rim-parallel** structure in this project:

1. **per-line independence** — S33 class 1, our far-side law solving each line alone;
2. **uniform-speed filling** — Criminisi's skeleton, Bornemann's `n·∇u = 0`; the fill follows the band's medial
   axis, which for a long thin band is rim-parallel (task #61, unmeasured);
3. **the hole read as content** — this one; the band's own boundary becomes an edge and everything aligns to it.

The third is available to **LaMa** wherever its effective context straddles the rim, which is the sharpest
argument yet for task #59's connectivity-limited context — and it gives that task something specific to look for
in the output rather than a general principle to apply.
