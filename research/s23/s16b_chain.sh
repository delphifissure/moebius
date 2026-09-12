#!/bin/bash
# Sprint 16b: the ceiling cut (window._ceilCut=1) on the porous scenes with truth, the kit, the troll and two pictures; then the porous probe chain resumes
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s16b.log; : > $LOG
: > $SP/kit_ceil.log; TAGSUF=_ceil EXTRA=,_ceilCut=1 bash $SP/kit_s7b3_chain.sh P6 S7 P5 S26 S2 S16 S31 S11 S15 S32
echo "=== probe troll 8bit ceil $(date +%T)" >> $LOG
IMG=defaultImgColor.png,defaultImgDepth.png TAG=photo_8bit_ceil FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2,_ceilCut=1 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
echo "=== ui troll 8bit ceil $(date +%T)" >> $LOG
IMG=defaultImgColor.png,defaultImgDepth.png TAG=ui_8bit_ceil OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim,_ceilCut=1 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
for P in vermeer room silverwarrior; do
  echo "=== probe $P ceil $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=b_${P}_da3ceil FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2,_ceilCut=1 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
done
echo "=== S16B DONE $(date +%T)" >> $LOG
setsid nohup bash $SP/p_probe_chain.sh > /dev/null 2>&1 &
