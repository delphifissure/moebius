#!/bin/bash
# Sprint 16: porous-silhouette scenes — rest render + env45 truth, two streams in parallel (product A skipped: closed rooms, no sky; check_app_band guards it)
cd /home/user/moebiusv2/harness/truthkit || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad
stream() { LOG=$SP/p_truth_$1.log; : > $LOG; shift
  for S in "$@"; do
    echo "=== make $S $(date +%T)" >> $LOG; python3 make.py $S --nx 800 >> $LOG 2>&1
    echo "=== scope $S $(date +%T)" >> $LOG; python3 scope.py $S --nx 800 --thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --no-atlas --out out/${S}_env45 >> $LOG 2>&1
  done; echo "=== STREAM DONE $(date +%T)" >> $LOG; }
stream A P5 P6 P1 P3 &
stream B P2 P4 &
wait; echo "=== P TRUTH DONE $(date +%T)" >> $SP/p_truth_A.log
