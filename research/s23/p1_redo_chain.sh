#!/bin/bash
# P1's env45 truth was truncated by ENOSPC (archive lacks depth/label); rebuild it, then probe (_c) and score
cd /home/user/moebiusv2/harness/truthkit || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/p1_redo.log; : > $LOG
rm -rf out/P1_env45
echo "=== scope P1 $(date +%T)" >> $LOG
python3 scope.py P1 --nx 800 --thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/P1_env45 >> $LOG 2>&1
echo "=== P1 TRUTH DONE $(date +%T)" >> $LOG
