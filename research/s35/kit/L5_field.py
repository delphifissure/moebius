"""S35 §54: the L5 scene as added to moebiusv2/harness/truthkit/scenes.py (registry key 'L5'; committed there locally on main,
2026-09-20). Kept here so the moebius branch carries the definition. Rendered with make.py L5 --nx 800; truth with
scope.py L5 --nx 800 --thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/L5_env45 (the env45 grid);
object maps truth_ids.py L5 (every clump a thing) and truth_ids.py L5 --unlabelled clump (heads only); probe
IMG=harness/truthkit/out/L5/rest_rgb.png,harness/truthkit/out/L5/rest_depth16.png DEPTH_OUTER=0.64 DEPTH_INNER=0.0001
DEPTH_PN=0.5 FLAGS=_tearLaw=rim,_farRule=plane TAG=L5_16plane node a257_probe.js -- the recipe reproduces L2_16plane exactly
(band and dQ identical), so it is the one the L scenes were made with. Visible step 1.312e-3."""
import numpy as np
from tk import Quad, Sphere, Cylinder, Disc, tex_checker, tex_noise, tex_solid
STUFF, THING = 1, 2


def L5_field(W=0.16, H=0.09):
    """S35 §54: the sunflowers' FIELD, graded and clumpy. L2's plants (a big near head, smaller heads deeper, stems, leaves)
    stand in a field of small round clumps resting on the ground, from just behind the picture plane to 2.5 W back, dense
    enough that the ground shows only between them near the camera. A clump stands a little in front of the clumps behind it
    (a stepped front on all sides: a thing by the wrap test, as SAM auto's field pieces were on the picture), and the truth
    behind the big head is farther clumps, the ground between them and the sky wall -- never the sky where a clump is.
    Labelled (truth_ids: every clump a thing) it is the auto map; with --unlabelled clump it is the map a person makes by
    clicking the heads."""
    depth = 4.0 * W
    prims = []
    prims.append(Quad([0, -H / 2, -depth / 2], [1, 0, 0], [0, 0, 1], 3 * W, depth / 2 + 0.001, lambda p: tex_checker(p, scale=W * 0.3, c1=(0.45, 0.55, 0.3), c2=(0.35, 0.45, 0.25), axes=(0, 2)), STUFF, 'ground'))
    prims.append(Quad([0, 0, -depth], [1, 0, 0], [0, 1, 0], 3 * W, 3 * H, lambda p: tex_noise(p, scale=W * 0.4, base=(0.55, 0.7, 0.95), amp=0.08, axes=(0, 1)), STUFF, 'sky_wall'))
    heads = [(-0.18 * W, 0.05 * H, -0.25 * W, 0.11 * W), (-0.05 * W, 0.0, -0.55 * W, 0.07 * W), (0.12 * W, -0.05 * H, -0.5 * W, 0.075 * W),
             (0.28 * W, 0.05 * H, -0.7 * W, 0.06 * W), (0.02 * W, 0.12 * H, -1.0 * W, 0.05 * W), (0.38 * W, -0.1 * H, -0.45 * W, 0.065 * W), (-0.32 * W, -0.12 * H, -0.8 * W, 0.05 * W)]
    for k, (x, y, z, r) in enumerate(heads):
        n = np.array([0.15 * ((k % 3) - 1), 0.25, 1.0]); n /= np.linalg.norm(n)
        prims.append(Disc([x, y, z], n, r, (lambda k: (lambda p: tex_checker(p, scale=W * 0.012, c1=(0.95, 0.75, 0.15), c2=(0.35, 0.22, 0.08), axes=(0, 1))))(k), THING, f'head{k}'))
        prims.append(Cylinder([x, -H / 2, z - 0.004 * W], [x, y, z - 0.004 * W], 0.008 * W, tex_solid((0.3, 0.45, 0.2)), THING, f'stem{k}'))
    rng = np.random.RandomState(35); k = 0
    for iz in range(14):                       # rows of clumps, near to far; a row's spacing grows with its distance
        z = -0.18 * W - 0.17 * W * iz * (1 + 0.06 * iz)
        nx_ = 9 + iz; xs = np.linspace(-1.3 * W, 1.3 * W, nx_)
        for x in xs:
            r = W * (0.03 + 0.015 * rng.rand()); x_ = x + W * 0.05 * (rng.rand() - 0.5); z_ = z + W * 0.05 * (rng.rand() - 0.5)
            g = 0.42 + 0.12 * rng.rand()
            prims.append(Sphere([x_, -H / 2 + r, z_], r, (lambda g: tex_solid((0.22, g, 0.18)))(g), THING, f'clump{k}')); k += 1
    return prims, {'outer': depth, 'inner': 0.0, 'element': 'layer family: a graded clumpy field with heads in front (the sunflowers)'}

