#!/bin/bash
# B: generality batch — six pictures from the repo, two depth arms each (DA3-Mono-Large 16-bit; the repo's 8-bit map), plane recipe as the panel bakes it;
# probe dumps (a257) + UI-path angle shots (ui_path); sky arm for the two pictures with sky.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/b_chain.log; : > $LOG
echo "=== prepare $(date +%T)" >> $LOG
python3 $SP/b_prepare.py 2>&1 | grep -v "INFO\|Warning" >> $LOG
run() { # pic arm depthfile extraflags
  echo "=== probe $1 $2 $(date +%T)" >> $LOG
  IMG=harness/batchB/$1_color.png,$3 TAG=b_$1_$2 FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2$4 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
  echo "=== ui $1 $2 $(date +%T)" >> $LOG
  IMG=harness/batchB/$1_color.png,$3 TAG=ub_$1_$2 OPTS=plane,wash,picture,off,35,$5,stretched,off FLAGS=_tearLaw=rim OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
}
for P in bristlecone octopus room silverwarrior starwatcher vermeer; do
  run $P da3 harness/batchB/${P}_da3_16.png "" off
  [ -f harness/batchB/${P}_repo8.png ] && run $P repo8 harness/batchB/${P}_repo8.png "" off
done
for P in bristlecone starwatcher; do run $P da3sky harness/batchB/${P}_da3_16.png ",_skyInf=1" on; done
echo "=== B DONE $(date +%T)" >> $LOG
