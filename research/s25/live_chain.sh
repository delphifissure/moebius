#!/bin/bash
# Live-pass preview on the photographs: the panel's plane recipe as the user builds it (arm cur) against the recommended
# defaults (arm cand: ceiling cut + line-aware despeckle), UI path shots at the five poses; a third arm (trade) on the two
# pictures whose far-pose holes were plate tears / clipped margin: cand + seams "all" + margin window.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/live_chain.log; : > $LOG
run() { # pic arm img sky opts-margin opts-seams extraflags
  echo "=== ui $1 $2 $(date +%T)" >> $LOG
  IMG=$3 TAG=ul_$1_$2 OPTS=plane,wash,$5,off,35,$4,$6,off FLAGS=_tearLaw=rim$7 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
}
for P in troll bristlecone octopus room silverwarrior starwatcher vermeer; do
  if [ "$P" = troll ]; then IMG=defaultImgColor.png,depth_da3mono16.png; else IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png; fi
  SKY=off; case $P in bristlecone|starwatcher) SKY=on;; esac
  run $P cur  $IMG $SKY picture stretched ""
  run $P cand $IMG $SKY picture stretched ",_ceilCut=1,_despeckleLines=1"
done
for P in silverwarrior vermeer; do
  run $P trade harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png off window all ",_ceilCut=1,_despeckleLines=1"
done
echo "=== LIVE DONE $(date +%T)" >> $LOG
