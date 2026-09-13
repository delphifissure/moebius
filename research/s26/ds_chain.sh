#!/bin/bash
cd /tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/ds
SC="S2 S15 S26 S16 S11 S27 S12 S31 S32 S5 S7 S9 S10 P1 P2 P3 P4 P5 P6"
python3 ds_run.py da3 $SC
python3 ds_run.py moge3 $SC
echo CHAIN_DONE
