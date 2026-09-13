#!/bin/bash
# Sprint 17c: the clamped plate per run cluster and AMLE, offline against truth and seams (R4 §3, §4; the S22 bar)
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; A=/home/user/moebiusv2/harness/shots/a257probe; K=/home/user/moebiusv2/harness/truthkit/out; LOG=$SP/s17c.log; : > $LOG
cd $SP
run() { # tag dir levels sky gt modes...
  tag=$1; dir=$2; lv=$3; sk=$4; gt=$5; shift 5
  for M in "$@"; do echo "=== $tag $M $(date +%T)" >> $LOG; MODE=$M SKY=$sk timeout 3000 python3 sheetfield4.py $dir $lv $gt >> $LOG 2>&1; echo "--- exit $? $(date +%T)" >> $LOG; done
}
run S15 $A/S15_16planesky_s12 65535 1 $K/S15_env45/scope_gt.npz own plate amle
run S26 $A/S26_16plane_s12 65535 0 $K/S26_env45/scope_gt.npz plate amle
run S16 $A/S16_16plane_s12 65535 0 $K/S16_env45/scope_gt.npz plate amle
run S32 $A/S32_16planesky_s12 65535 1 $K/S32_env45/scope_gt.npz plate
run photo8 $A/photo_bo_da3mono 255 0 "" plate
run photo16 $A/photo_da3_s10d 568 0 "" plate
run photo8 $A/photo_bo_da3mono 255 0 "" amle
echo "=== S17C DONE $(date +%T)" >> $LOG
