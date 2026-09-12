#!/bin/bash
# S15 (sprint): the per-line law with its slope regularised across lines (slope) and a cross-line value median (cmed), offline vs truth and seams
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; A=/home/user/moebiusv2/harness/shots/a257probe; K=/home/user/moebiusv2/harness/truthkit/out; LOG=$SP/s15.log; : > $LOG
run() { # tag dir levels sky gt
  for M in own slope cmed; do echo "=== $1 $M $(date +%T)" >> $LOG; MODE=$M SKY=$4 python3 $SP/sheetfield3.py $2 $3 $5 >> $LOG 2>&1; done
}
run S15 $A/S15_16planesky_s12 65535 1 $K/S15_env45/scope_gt.npz
run S32 $A/S32_16planesky_s12 65535 1 $K/S32_env45/scope_gt.npz
run S2 $A/S2_16plane_s12 65535 0 $K/S2_env45/scope_gt.npz
run S26 $A/S26_16plane_s12 65535 0 $K/S26_env45/scope_gt.npz
run S16 $A/S16_16plane_s12 65535 0 $K/S16_env45/scope_gt.npz
run photo8 $A/photo_bo_da3mono 255 0 ""
run photo16 $A/photo_da3_s10d 568 0 ""
echo "=== S15 DONE $(date +%T)" >> $LOG
