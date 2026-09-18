import sys, numpy as np, json
from PIL import Image
P='/home/user/moebiusv2/harness/shots/streakclass/room_s35'; meta=json.load(open(f'{P}/meta.json')); pw,ph=meta['pw'],meta['ph']; step=2.679e-3
band=np.fromfile(f'{P}/disocc.u8',np.uint8).reshape(ph,pw)>0; dQ=np.fromfile(f'{P}/dQ.f32',np.float32).reshape(ph,pw)
oid9=np.asarray(Image.open('/home/user/moebiusv2/harness/shots/objlayers/view_sunflowers/plane_object_ids_sam.png')); oid9=oid9[...,0] if oid9.ndim==3 else oid9
ys,xs=np.nonzero(oid9==1); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
reg=np.zeros((ph,pw),bool); reg[y0:y1+1, x0:min(pw,x1+160)]=True; reg&=band&(oid9!=1)
for d in sys.argv[1:]:
    try: ff=np.fromfile(f'{P}/{d}/farField_stop.f32',np.float32).reshape(ph,pw)
    except FileNotFoundError: print(d,'missing'); continue
    rows=np.array([np.median(ff[y][reg[y]]) if reg[y].any() else np.nan for y in range(y0,y1+1)]); dd=np.abs(np.diff(rows)); ok=np.isfinite(dd)
    print(f'{d}: right of the big head, per-row fill p10/p50/p90 {np.nanpercentile(rows,[10,50,90]).round(3)}; rows filled with sky (< 0.02): {int(np.nansum(rows<0.02))} of {len(rows)}; row-to-row jumps > 1 step {int((dd[ok]>step).sum())}, > 3 steps {int((dd[ok]>3*step).sum())}, largest {np.nanmax(dd)/step:.1f}')
