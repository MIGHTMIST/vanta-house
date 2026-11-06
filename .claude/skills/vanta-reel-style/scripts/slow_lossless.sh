#!/bin/bash
S=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad
ffmpeg -v error -y -i $S/src/433A6916.MOV -map 0:v:0 -an \
 -vf "scale=in_range=pc:out_range=tv,format=yuv420p,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=2.0*PTS,fps=30" \
 -c:v libx264 -qp 0 -preset veryfast $S/work/slow_lossless.mkv && echo SLOWDONE > $S/work/slow.status
