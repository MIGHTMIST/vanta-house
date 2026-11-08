#!/bin/bash
# run a render script, then peak-fix every HQ file it printed
S=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad; cd $S/scripts
LOG=$1; shift
python3 "$@" > $S/IV/$LOG.log 2>&1
for f in $(grep -E "_HQ\.mp4$" $S/IV/$LOG.log); do echo -n "$(basename $f): "; bash $S/scripts/fixtp.sh $f ${f%.mp4}_tp.mp4 && mv ${f%.mp4}_tp.mp4 $f; done
