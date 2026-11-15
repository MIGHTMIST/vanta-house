#!/bin/bash
# render the 3 videos in 9 parts, 3 at a time
cd /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype
printf "%s\n" "v1 a 0 15.6667" "v1 b 15.6667 31.3333" "v1 c 31.3333 47" "v2 a 0 15.6667" "v2 b 15.6667 31.3333" "v2 c 31.3333 47" "v3 a 0 15.6667" "v3 b 15.6667 31.3333" "v3 c 31.3333 47" | \
  xargs -P 3 -L 1 sh -c 'VID=$0 NOAUDIO=1 python3 render9.py p9_$0$1.mp4 $2 $3 > p9_$0$1.log 2>&1; echo "done $0$1 rc=$?"'
echo ALLDONE
