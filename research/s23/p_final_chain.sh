#!/bin/bash
# after the ceiling re-runs: resume the porous probe chain (current law, _c), then the ceiling arm on the canopies once all six are probed
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad
while ! grep -q "=== S16C DONE" $SP/s16b.log; do sleep 20; done
bash $SP/p_probe_chain.sh
cd /home/user/moebiusv2 && TAGSUF=_ceil EXTRA=,_ceilCut=1 bash $SP/kit_s7b3_chain.sh P1 P2 P3 P4 >> $SP/p_probe.log 2>&1
echo "=== P CEIL DONE $(date +%T)" >> $SP/p_probe.log
