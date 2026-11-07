#!/bin/bash
# small copy under 2.9 MB for the Drive connector: 2-pass, bitrate from duration
IN=$1; OUT=$2; W=${3:-540}; H=${4:-960}
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $IN)
VB=$(python3 -c "print(max(120,int(2.85*8e6/$D/1000-56)))")
cd /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/work
ffmpeg -v error -y -i $IN -vf scale=$W:$H:flags=lanczos -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile ds_$$ -an -f null /dev/null
ffmpeg -v error -y -i $IN -vf scale=$W:$H:flags=lanczos -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile ds_$$ -c:a aac -b:a 48k -ac 1 -movflags +faststart $OUT
ls -l $OUT | awk '{print $5}'; sha256sum $OUT | cut -c1-64
