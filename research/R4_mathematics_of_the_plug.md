# R4 — The mathematics of the plug: what the heavier constructions compute, with our boundary conditions (2026-09-13)

Asked (S24 §6, "where heavier math earns its place — yes, dig deep into this"). This note states each construction as an
energy or an equation, gives the boundary conditions that our setting imposes, says what the construction would compute on
our grid, and how it would be tested. The references are the classical ones; none needs a network.

## 0. The setting, once

On one layer (plate 1, plate 2), a hidden region Ω: the texels under an occluder that have something behind them. Its
boundary has two parts with different physics:

- **Γ_f, the far rim**: where the hidden surface meets the *visible* background. Here we know the surface — its value
  (disparity) and, from the run along the line, its slope. Cauchy data.
- **Γ_o, the occluder's rim**: the silhouette. The hidden surface passes *under* it and continues; the occluder is in
  front and carries no information about the surface behind. No data: a **free** boundary in the plate sense, and a
  **jump** in the depth field between the two layers.

Constraints: the hidden surface cannot pass through another surface it would be seen against — the ground, the
ceiling, a wall (the **obstacles**). Everything below is one of: an energy over Ω with these boundaries, or a
continuation law along contours. The per-line plane law of the app is, in these terms: Cauchy data on Γ_f from the run,
zero-bending (linear) continuation along one axis, free end, obstacle cut — a one-dimensional discretisation of §3 + §6.

## 1. Layers and hidden contours: the 2.1D sketch and Euler's elastica

**Nitzberg–Mumford–Shiota (1993, *Filtering, Segmentation and Depth*, LNCS 662)** formalise "a picture is a stack of
overlapping regions". They minimise, over regions R_i with an occlusion order, E = Σ_i [ α·length(∂R_i) + ∫_{∂R_i ∩ hidden}
(β + γ κ²) ds ] + fidelity: the *visible* boundary is paid by length, the *hidden* continuation of each boundary by
**Euler's elastica** ∫(β + γκ²) ds — the curve of least bending that joins the two ends of a silhouette where it disappears
behind an occluder (the two T-junctions), tangent-continuous at both. Mumford (1994, *Elastica and computer vision*) gives
the probabilistic reading (elastica = mode of a random-walk-with-curvature prior); Horn (1983, *The curve of least energy*)
the classical solution; Kimia–Frankel–Popescu (IJCV 2003) the **Euler spiral** (curvature linear in arclength) as the
minimum-variation-of-curvature completion, which is what the eye draws (Kanizsa); Williams–Jacobs (1997, *Stochastic
completion fields*) the same as a field of completion probabilities.

*What it computes for us.* Not the far side's depth but **the shape of what is hidden**: when a hidden object on plate 2 (the
chair behind the person, the second leaf layer) shows two ends at the occluder's silhouette, the elastica between its two
T-junction tangents is the cited completion of its outline; inside that outline the layer belongs to the object (its own
depth), outside to the background. The occlusion order is what our arrival order already computes.

*Discretisation.* Per pair of matched T-junctions (same layer, same sheet, tangents pointing at each other): the elastica
between two points with prescribed tangents has no closed form but a two-parameter family of solutions; the Euler spiral
(Kimia) is found by a 1-D root find on its two parameters (total turning and its rate); a cubic Hermite is the crude
stand-in. Constants: β and γ have units (1/length and length); the ratio γ/β is a length scale — **that is a genuine
constant to be cited or measured**, and the Euler-spiral variant has none (it is scale-free by construction), which is why it
is the one to use.

*Test.* The kit's env45 truth labels hidden texels as background (class 2) or thing (class 3): S4 figure pop-out, S9 cards,
S11 bodies, S7/P canopies. For each occluder with a hidden object behind it, the IoU of the elastica-completed outline
against the class-3 region; the baseline is plate 2's arrival-order footprint.

## 2. Curvature-based inpainting of the field itself (why the classical inpainters are two-sided)

**Masnou–Morel (1998)** join the level lines of the known image across the hole by geodesics / elastica; **Chan–Kang–Shen
(2002, *Euler's elastica and curvature-based inpainting*)** minimise ∫_Ω (a + b κ²)|∇u| with κ = ∇·(∇u/|∇u|), which
continues level lines smoothly; **Ballester–Bertalmío–Caselles–Sapiro–Verdera (2001)** interpolate the gradient direction
field θ and the grey level u jointly (∫ |∇·θ|^p (a + b|∇k∗u|) + ∫ |∇u| − θ·∇u); **Bertalmío et al. (2000)** transport
isophotes inward; **TV inpainting** (Chan–Shen 2001) minimises ∫|∇u|. All of them take the data on the **whole** boundary of
the hole and interpolate across it. For a depth field that is exactly the mistake §6 of S24 named: they connect the
occluder's depth to the background's across Γ_o — the spaghetti in the field. They become right only when Γ_o is removed
from the data, and then TV and harmonic extensions are ill-posed or flat (harmonic extension of value data through a free
edge does not carry slope), which leaves the slope-carrying constructions of §3–§4. Their proper place in our pipeline is
**the colour placeholder, not the depth** (§5).

## 3. The clamped plate: the biharmonic problem with the right boundaries

**Energy.** E[u] = ∫_Ω (u_xx² + 2u_xy² + u_yy²) dx — the bending energy of a thin plate (Kirchhoff–Love; Duchon 1977 for the
thin-plate spline, which is the same energy with scattered data). Minimisers satisfy Δ²u = 0.

**Boundary conditions in our setting.** On Γ_f: **clamped** — u = g (the rim's disparity) and ∂u/∂n = h (the run's slope
along the axis, projected on the normal), the Cauchy data the plane law already extracts. On Γ_o: **free edge** — the
natural conditions of the energy, zero bending moment and zero Kirchhoff shear (Timoshenko–Woinowsky-Krieger, *Theory of
Plates and Shells*, ch. 2): the plate ends there without being held. Properties that matter: (i) affine data is
reproduced exactly (an affine function has zero bending energy and satisfies the clamped data) — so on a planar wall or
floor the plate returns the plane, as the per-line law does; (ii) the energy has **no parameter** and is invariant to scaling
u, so nothing is tuned; (iii) across lines the solution is one surface — the seams between adjacent lines' extrapolations
vanish inside a plate by construction; (iv) with curved data (a hill) the curvature decays away from Γ_f rather than being
carried — the safe extrapolation.

**Why §16 (Sprint 12) does not settle this.** That test used a thin-plate spline *through scattered rim samples of a join-law
sheet* — scattered-data interpolation, not a boundary-value problem: no slope data, no free edge, and a domain (the
sheet) that crossed the fold between S15's ground and hill so that one surface was asked to be both. The construction
above differs on all three points. It is untested.

**Discretisation on our grid.** Minimise the discrete bending energy Σ over Ω of (δ_xx u)² + 2(δ_xy u)² + (δ_yy u)² with the
Cauchy strip fixed — the rim texel and the run's next texels along the axis (the run's own window w), whose values are the
line fit's — and *nothing else fixed*. A least-squares problem with a sparse matrix (each row a second difference); every
boundary that is not fixed is automatically **natural**, which is the discrete free edge — no special stencil. Solve per
component with a sparse Cholesky or conjugate gradients; a 1 500 × 1 000 plate has ~40 % hidden texels, i.e. ~600 k
unknowns, seconds in numpy/scipy offline, and the app's version would be the same normal equations solved by multigrid.
**Domain.** Per **run cluster**: adjacent lines whose rim runs are joined (the join law between the runs' rim texels) form
one cluster; each cluster is one plate. That is the fold segmentation the runs already carry, so the ground and the hill
are separate plates. Per texel, several plates may reach (one per side/axis, as the candidates now); the arrival order and
the layering rules stay exactly as they are — the plate replaces the per-line *value* of a candidate, nothing else.

**Test.** Offline in `sheetfield3.py` (MODE=plate): S15, S2, S26, S16, S32 depth against env45 truth; seams on the troll's
DA3 16-bit and 8-bit. The S22 bar: S15's median within 0.01 m of 0.184, p90 within 10 %; same-sheet seams halved. One day.

## 4. AMLE — the infinity Laplacian

**Equation.** Δ_∞u = Σ_{ij} u_{x_i} u_{x_j} u_{x_i x_j} = 0 (Aronsson 1967, *Extension of functions satisfying Lipschitz
conditions*). **Meaning.** Among all extensions of boundary data, the AMLE is the one whose Lipschitz constant is minimal on
every sub-domain — it extends "as linearly as possible along its own gradient lines", creates no spurious maxima or
minima, and is the unique interpolant satisfying **Caselles–Morel–Sbert's axioms** (IEEE TIP 1998, *An axiomatic approach to
image interpolation*: comparison principle, regularity, stability under affine changes of the grey level and of the
domain). Cones and affine functions are ∞-harmonic. **Discretisation.** Oberman (Math. Comp. 2005): a convergent, monotone
scheme — u(x) ← ½(max_{y∈B(x,r)} u(y) + min_{y∈B(x,r)} u(y)) iterated to a fixed point; a few lines of code, no parameter
beyond the neighbourhood (the 8-neighbourhood, or a small ball).

**In our setting.** AMLE takes *values* on the data set, not slopes. Give it the same Cauchy strip as the plate (the rim
texel and the run's window along the axis, with their fitted values) as fixed data, and let Ω's other boundary be
natural (the scheme simply has no data there). On a planar strip AMLE continues the plane (affine functions are
∞-harmonic and the strip's data are affine); on curved data it continues linearly along the gradient — a cone-like
extension, the "safe" behaviour again. It has the same seam-free property inside a domain as the plate, is simpler to
solve, and carries a *comparison principle* the plate lacks (it never overshoots its data), which is a real advantage
against obstacles: max(u, ψ) with an obstacle ψ keeps the solution ∞-harmonic off the contact set.

**Test.** Same as §3, MODE=amle; same bar.

## 5. Coherence transport — the one-sided fast inpainter, and the placeholder colour

**Bornemann–März (JMIV 2007, *Fast image inpainting based on coherence transport*).** The hole is filled inward in order of
distance from the known data; each new pixel is a weighted average of the *already known* pixels in its neighbourhood, the
weights concentrated along the local **coherence direction** (the dominant orientation of the structure tensor of the known
side), so lines and edges are transported straight into the hole. It is explicitly one-sided (it fills from the boundary
in), takes milliseconds, and is what the classical inpainters converge to at large scale. In our setting: (i) for *depth*
it transports values — a flat continuation — so it is not a competitor to §3/§4 unless the transported quantity is the local
affine model (value + gradient), which is the plane law generalised to arbitrary directions; (ii) for the **colour
placeholder** it is the right tool today: the current wash is a rim-window mean (flat); coherence transport from the far
rim would continue the floor's tiles, the wall's stripes and the hedge's texture direction into the band — a placeholder
that already looks like the surface it stands for, still never a clone of the foreground (the transport is from the far
side only; the occluder's texels are not in the known set). That is "plausible wash" made structural, at no model cost.
**Test.** Troll, room, vermeer: clone count 0; the SD stage's fill against a flat wash vs a coherence wash (the inpainter's
context is better where the placeholder already has the surface's orientation); the user's eye on the band at 27° and 45°.

## 6. The obstacle problem — the cuts as a constraint

**Problem.** min E[u] subject to u ≥ ψ on Ω (in disparity, "not behind the ground / ceiling / wall along the rest ray"),
ψ = max over the obstacle planes. Solutions have a **contact set** where u = ψ and a free boundary where they separate;
regularity is C^{1,1} (Caffarelli, J. Fourier Anal. Appl. 1998, *The obstacle problem revisited*): the surface meets the
obstacle tangentially, not with a kink. For our plug the contact set is exactly the ground the wall stands on behind the
hedge (S32), the ceiling the wall meets behind the grille (P6), the floor a table leg meets. **Discretisation.** Projected
Gauss–Seidel / projected multigrid (Brandt–Cryer 1983) for the plate or AMLE energy: iterate the solver and clamp u to ψ
each sweep; converges monotonically. For AMLE, max(u, ψ) inside Oberman's iteration is the whole implementation. **What
it changes against the cuts.** The per-line cut replaces a candidate that passes the ground by the ground's value at that
texel and continues; several planes are handled in sequence and can disagree at their intersection. The constrained
solve handles them at once and puts the crease where the planes meet — the room's corner behind a cupboard.

## 7. Mumford–Shah with a known jump set

Mumford–Shah (CPAM 1989): min ∫_{Ω∖K} |∇u|² + λ ∫ (u − f)² + ν·length(K) over u and the discontinuity set K. In our setting the
jump set on plate 1 is *known* — it is the occluder's silhouette — and Mumford–Shah reduces to smooth pieces per region,
i.e. to §3/§4 with the layers separated. It becomes new only where the jump set inside the hidden region is unknown: the
outline of a hidden object, which is §1. So there are two mathematics, not three: **contours (§1)** and **surfaces with
one-sided Cauchy data and obstacles (§3, §4, §6)**; §5 is the colour's transport.

## 8. Where each enters the three problems of the plug (S24 §6)

| problem | tool | status |
|---|---|---|
| coverage (no hole at any pose) | geometry: the reveal at the envelope's extreme pose, carriers to the reach (S24 §5); the fold-alpha on stretched plate cells (Sprint 17a) | building |
| depth of the plug | one-sided Cauchy continuation with obstacles: the per-line law (1-D, in the app); the clamped plate and AMLE (2-D, §3–§4), constrained solve (§6) | offline test next |
| colour of the plug | coherence transport from the far rim as the placeholder (§5); the diffusion stage for content (S24 §5) | proposal |
| hidden contours (plate 2 shapes) | Euler spiral / elastica between T-junction tangents (§1); the amodal models as the learned alternative | proposal |

## 9. Order and cost

1. §3 + §4 offline against the S22 bar (one day; `sheetfield3.py` MODE=plate | amle, domain = run cluster, Cauchy strip,
   obstacles = ground and ceiling planes from the probe meta). Decides whether the 2-D field enters the app at all.
2. §5 coherence-transport wash on the troll, room, vermeer (one day; a bake-time CPU pass over the band; clone count 0).
3. §1 Euler-spiral completion on the kit's class-3 truth (two days).
4. §6 folds into 1 when the plate or AMLE is adopted; otherwise the plane cut of S24 I2 stays as sequential cuts.
