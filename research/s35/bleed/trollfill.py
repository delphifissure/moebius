"""What fills the band inside the troll's footprint? Far field of each arm over band texels the 13-click mask assigns to the
troll's body: depth distribution and the shares that are the deep gap (< 0.05), forest (0.12..0.45) or nearer."""
import sys, json, numpy as np
from PIL import Image
P='/home/user/moebiusv2/harness/shots/streakclass/troll_s35'; meta=json.load(open(f'{P}/meta.json')); pw,ph=meta['pw'],meta['ph']
band=np.fromfile(f'{P}/disocc.u8',np.uint8).reshape(ph,pw)>0; dQ=np.fromfile(f'{P}/dQ.f32',np.float32).reshape(ph,pw)
m13=np.asarray(Image.open('/home/user/moebiusv2/harness/shots/objlayers/view_troll_v2/plane_object_ids_sam.png')); m13=m13[...,0] if m13.ndim==3 else m13
if m13.shape!=(ph,pw): m13=np.asarray(Image.fromarray(m13).resize((pw,ph),Image.NEAREST))
ids,cnt=np.unique(m13[m13>0],return_counts=True); troll=int(ids[np.argmax(cnt)])
sel=band&(m13==troll)
print(f'troll id {troll}: {sel.sum()} band texels in his footprint; his own depth median {np.median(dQ[sel]):.3f}; visible forest beside him (non-band, non-mask, rows 100..600) median {np.median(dQ[100:600][(~band&(m13==0))[100:600]]):.3f}')
for d in sys.argv[1:]:
    try: ff=np.fromfile(f'{P}/{d}/farField_stop.f32',np.float32).reshape(ph,pw)
    except FileNotFoundError: print(d,'missing'); continue
    v=ff[sel]; print(f'  {d:12s}: far field p10 {np.percentile(v,10):.3f} p50 {np.median(v):.3f} p90 {np.percentile(v,90):.3f}; gap (<0.05) {100*(v<0.05).mean():.1f} %  forest (0.12..0.45) {100*((v>=0.12)&(v<=0.45)).mean():.1f} %  own/near (>0.45) {100*(v>0.45).mean():.1f} %')
