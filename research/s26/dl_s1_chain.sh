#!/bin/bash
cd /tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/ds
until grep -q "^DONE depthlab" depthlab_chain.log; do sleep 20; done
DL_STRENGTH=1.0 DL_TAG=1 ../depthlab/dlenv/bin/python ds_depthlab.py S15 P2 S32 S31 S2 S7
echo S1_CHAIN_DONE
