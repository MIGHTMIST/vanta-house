#!/bin/bash
cd /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype
printf "%s\n" "n2 a 0 11.6667" "n2 b 11.6667 23.3333" "n2 c 23.3333 99" "crew a 0 8.6667" "crew b 8.6667 99" "build a 0 8.6667" "build b 8.6667 99" | \
  xargs -P 4 -L 1 sh -c 'VID=$0 python3 render10.py p10_$0$1.mp4 $2 $3 > p10_$0$1.log 2>&1; echo "done $0$1 rc=$?"'
echo ALLDONE
