#!/bin/bash
# two-pass 1080x1920 encode sized to land just under 10 MB (Drive connector upload limit), from lossless sources
set -e
IN_V=$1; IN_A=$2; OUT=$3; VBR=$4
CM="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
VF="scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p"
cd $(dirname $OUT)
ffmpeg -v error -y -i $IN_V -map 0:v -vf "$VF" -c:v libx264 -preset slower -b:v $VBR -maxrate $(( ${VBR%k} * 3 / 2 ))k -bufsize $(( ${VBR%k} * 2 ))k -tune film -profile:v high -level 4.2 -g 30 -keyint_min 30 -r 30 $CM -pass 1 -passlogfile /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/work/x264pass -an -f null /dev/null
ffmpeg -v error -y -i $IN_V -i $IN_A -map 0:v -map 1:a -vf "$VF" -c:v libx264 -preset slower -b:v $VBR -maxrate $(( ${VBR%k} * 3 / 2 ))k -bufsize $(( ${VBR%k} * 2 ))k -tune film -profile:v high -level 4.2 -g 30 -keyint_min 30 -r 30 $CM -pass 2 -passlogfile /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/work/x264pass -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart $OUT
