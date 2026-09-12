#!/bin/bash
# B, second pass: the forced-floor arm (window._visStep = 1) on all six pictures, after the first chain has finished.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/b_chain.log
while ! grep -q "=== B DONE" $LOG; do sleep 20; done
run() { # pic arm depthfile extraflags sky
  echo "=== probe $1 $2 $(date +%T)" >> $LOG
  IMG=harness/batchB/$1_color.png,$3 TAG=b_$1_$2 FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2$4 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
  echo "=== ui $1 $2 $(date +%T)" >> $LOG
  IMG=harness/batchB/$1_color.png,$3 TAG=ub_$1_$2 OPTS=plane,wash,picture,off,35,$5,stretched,off FLAGS=_tearLaw=rim$4 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
}
for P in bristlecone octopus room silverwarrior starwatcher vermeer; do run $P da3f harness/batchB/${P}_da3_16.png ",_visStep=1" off; done
echo "=== B2 DONE $(date +%T)" >> $LOG
