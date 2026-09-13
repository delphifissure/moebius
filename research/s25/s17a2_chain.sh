#!/bin/bash
# beyond-the-frame class: margin window with seams STRETCHED (not "all") and the magenta check view, 45-degree bake, silverwarrior + room
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s17a2_chain.log
while ! grep -q "=== S17A DONE" $SP/s17a_chain.log 2>/dev/null; do sleep 30; done
: > $LOG
for P in silverwarrior room; do
  echo "=== ui $P winfold2 $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=ul_${P}_winfold2 OPTS=plane,wash,window,off,35,off,stretched,off,new FLAGS=_tearLaw=rim,_plateFoldAlpha=2 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
  echo "=== ui $P win $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=ul_${P}_win OPTS=plane,wash,window,off,35,off,stretched,off,new FLAGS=_tearLaw=rim OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
done
echo "=== S17A2 DONE $(date +%T)" >> $LOG
