"""S39: the L9 scene as added to moebiusv2/harness/truthkit/scenes.py (registry key 'L9'). Kept here so the moebius
branch carries the definition, as L5 and L6 are. Rendered with make.py L9 --nx 800; truth with scope.py L9 --nx 800
--thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/L9_env45 (the env45 grid); object maps
truth_ids.py L9 (every piece a thing) and truth_ids.py L9 --unlabelled tuft (the click map, figure only); probe
IMG=harness/truthkit/out/L9/rest_rgb.png,harness/truthkit/out/L9/rest_depth16.png DEPTH_OUTER=0.64 DEPTH_INNER=0.0001
DEPTH_PN=0.5 FLAGS=_tearLaw=rim,_farRule=plane TAG=L9_16plane node a257_probe.js."""
import numpy as np
from tk import Quad, Sphere, Cylinder, Ellipsoid, tex_checker, tex_noise, tex_solid, tex_stripes
STUFF, THING = 1, 2

# _figure is the shared helper in scenes.py; _ground_and_sky was added with these three scenes.


def _ground_and_sky(W, H, depth):
    prims = []
    prims.append(Quad([0, -H / 2, -depth / 2], [1, 0, 0], [0, 0, 1], 3 * W, depth / 2 + 0.001, lambda p: tex_checker(p, scale=W * 0.25, c1=(0.40, 0.46, 0.28), c2=(0.30, 0.38, 0.22), axes=(0, 2)), STUFF, 'ground'))
    prims.append(Quad([0, 0, -depth], [1, 0, 0], [0, 1, 0], 3 * W, 3 * H, lambda p: tex_noise(p, scale=W * 0.4, base=(0.55, 0.7, 0.95), amp=0.08, axes=(0, 1)), STUFF, 'sky_wall'))
    return prims


def L9_tufts(W=0.16, H=0.09):
    """S38/S39, the L5 regime at its extreme: a dense low field of small tufts sitting ON the ground, receding, with a figure
    in front. The finest contact case -- hundreds of small pieces every one of which touches the ground, so nothing survives
    as its own component under a click-the-heads map. Field named tuft* for `truth_ids.py L9 --unlabelled tuft`."""
    depth = 4.0 * W
    prims = _ground_and_sky(W, H, depth)
    _figure(prims, W, H, -0.10 * W, -0.30 * W, W * 0.080, 'figure')
    rng = np.random.RandomState(90); k = 0
    for rank in range(16):
        z = -(0.30 + 0.17 * rank * (1 + 0.07 * rank)) * W
        sc = 1.0 / (1.0 + 0.40 * rank)
        n = 10 + rank
        for j in range(n):
            x = (-1.25 + 2.5 * (j + 0.5 + 0.8 * (rng.rand() - 0.5)) / n) * W
            r = W * (0.028 + 0.016 * rng.rand()) * sc
            g = 0.40 + 0.18 * rng.rand()
            prims.append(Ellipsoid([x, -H / 2 + r * 0.9, z + W * 0.05 * (rng.rand() - 0.5)], [r * 0.8, r * 1.5, r * 0.8],
                                   tex_solid((0.22, g, 0.18)), THING, f'tuft{k}')); k += 1
    return prims, {'outer': depth, 'inner': 0.0, 'element': 'L5 regime, extreme: a dense low field of tufts on the ground, figure in front'}
