#!/bin/bash
# P2 and P3 env45 truths, rerun after the OOM kill (tk.py Canopy.hits now keeps a running top-k); two in parallel
cd /home/user/moebiusv2/harness/truthkit || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad
one() { S=$1; LOG=$SP/p23_$S.log; : > $LOG; rm -rf out/${S}_env45
  echo "=== scope $S $(date +%T)" >> $LOG
  python3 scope.py $S --nx 800 --thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/${S}_env45 >> $LOG 2>&1
  echo "=== $S exit $? $(date +%T)" >> $LOG; }
one P2 & one P3 & wait
echo "=== P23 TRUTH DONE $(date +%T)" >> $SP/p23_P2.log
