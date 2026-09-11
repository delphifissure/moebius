#!/usr/bin/env python3
"""Kit: v11 vs S10 (visible-step floor)."""
import json, os
O = '/home/user/moebiusv2/harness/truthkit/out'
print('| scene | band v11 → S10 | P v11 → S10 | R v11 → S10 | depth median (m) | depth p90 (m) | layer-2 px |'); print('|---|---|---|---|---|---|---|')
for S in ['S2', 'S27', 'S12', 'S26', 'S16', 'S31', 'S15', 'S32']:
    suf = 'planesky' if S in ('S15', 'S32') else 'plane'
    a = f'{O}/{S}/check_app16{suf}.json'; b = f'{O}/{S}/check_app16{suf}_s10d.json'
    if not os.path.exists(b): print(f'| {S} | (not run) |'); continue
    ja, jb = json.load(open(a)), json.load(open(b)); da, db = ja.get('band_depth_err_m', {}), jb.get('band_depth_err_m', {})
    f = lambda x, y, fmt: (fmt % x) if (fmt % x) == (fmt % y) else (fmt % x) + ' → ' + (fmt % y)
    print(f"| {S} | {f(ja['app_band_px'], jb['app_band_px'], '%d')} | {f(ja['precision'], jb['precision'], '%.3f')} | {f(ja['recall'], jb['recall'], '%.3f')} | {f(da.get('median_abs', 0), db.get('median_abs', 0), '%.3f')} | {f(da.get('p90_abs', 0), db.get('p90_abs', 0), '%.3f')} | {f(ja.get('layer2', {}).get('app_px', 0), jb.get('layer2', {}).get('app_px', 0), '%d')} |")
