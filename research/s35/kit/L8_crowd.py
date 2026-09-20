"""S39: the L8 scene as added to moebiusv2/harness/truthkit/scenes.py (registry key 'L8'). Kept here so the moebius
branch carries the definition, as L5 and L6 are. Rendered with make.py L8 --nx 800; truth with scope.py L8 --nx 800
--thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/L8_env45 (the env45 grid); object maps
truth_ids.py L8 (every piece a thing) and truth_ids.py L8 --unlabelled crowd (the click map, figure only); probe
IMG=harness/truthkit/out/L8/rest_rgb.png,harness/truthkit/out/L8/rest_depth16.png DEPTH_OUTER=0.64 DEPTH_INNER=0.0001
DEPTH_PN=0.5 FLAGS=_tearLaw=rim,_farRule=plane TAG=L8_16plane node a257_probe.js."""
import numpy as np
from tk import Quad, Sphere, Cylinder, Ellipsoid, tex_checker, tex_noise, tex_solid, tex_stripes
STUFF, THING = 1, 2

# _figure is the shared helper in scenes.py; _ground_and_sky was added with these three scenes.


def _ground_and_sky(W, H, depth):
    prims = []
    prims.append(Quad([0, -H / 2, -depth / 2], [1, 0, 0], [0, 0, 1], 3 * W, depth / 2 + 0.001, lambda p: tex_checker(p, scale=W * 0.25, c1=(0.40, 0.46, 0.28), c2=(0.30, 0.38, 0.22), axes=(0, 2)), STUFF, 'ground'))
    prims.append(Quad([0, 0, -depth], [1, 0, 0], [0, 1, 0], 3 * W, 3 * H, lambda p: tex_noise(p, scale=W * 0.4, base=(0.55, 0.7, 0.95), amp=0.08, axes=(0, 1)), STUFF, 'sky_wall'))
    return prims


def L8_crowd(W=0.16, H=0.09):
    """S38/S39, the L5 regime with upright pieces: a CROWD of standing figures at graded depths on a ground, a larger figure
    in front. Every one of them meets the ground, as L5's clumps do, but they are tall and narrow rather than round, so the
    silhouette statistics are the opposite of L5's while the contact structure is the same. Field named crowd* for
    `truth_ids.py L8 --unlabelled crowd`."""
    depth = 4.0 * W
    prims = _ground_and_sky(W, H, depth)
    _figure(prims, W, H, -0.15 * W, -0.28 * W, W * 0.080, 'figure')
    rng = np.random.RandomState(80); k = 0
    for rank in range(9):
        z = -(0.55 + 0.30 * rank * (1 + 0.09 * rank)) * W
        sc = 1.0 / (1.0 + 0.30 * rank)
        for j in range(3 + rank // 2):
            n = 3 + rank // 2
            x = (-1.15 + 2.3 * (j + 0.5 + 0.7 * (rng.rand() - 0.5)) / n) * W
            r = W * (0.045 + 0.018 * rng.rand()) * sc
            z_ = z + W * 0.10 * (rng.rand() - 0.5)
            c1 = (0.35 + 0.45 * rng.rand(), 0.30 + 0.40 * rng.rand(), 0.35 + 0.40 * rng.rand())
            prims.append(Cylinder([x, -H / 2, z_], [x, -H / 2 + H * (0.34 + 0.10 * rng.rand()) * sc, z_], r,
                                  (lambda c: (lambda p: tex_stripes(p, scale=W * 0.02, c1=c, c2=(c[0] * 0.6, c[1] * 0.6, c[2] * 0.6), axis=1)))(c1), THING, f'crowd{k}_body'))
            prims.append(Sphere([x, -H / 2 + H * (0.34 + 0.10 * rng.rand()) * sc + 0.9 * r, z_], 0.9 * r,
                                tex_solid((0.80, 0.62, 0.50)), THING, f'crowd{k}_head')); k += 1
    return prims, {'outer': depth, 'inner': 0.0, 'element': 'L5 regime, upright: a crowd of standing figures, larger figure in front'}
