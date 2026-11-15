#!/bin/bash
# Version B: join the three parts frame-exact (390 + 390 + 366 frames), add the Version A sound mix (same cuts), run checks
set -e
H=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype
O=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/out/VantaHouse_Site_AI_CameraMoves_B1.mp4
cd $H
for p in p8a p8b p8c; do echo "$p $(ffprobe -v error -select_streams v -count_frames -show_entries stream=nb_read_frames -of csv=p=0 $p.mp4)"; done
ffmpeg -v error -y -i p8a.mp4 -i p8b.mp4 -i p8c.mp4 -i final_mix7.wav -filter_complex \
 "[0:v]trim=end_frame=390,setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=390,setpts=PTS-STARTPTS[b];[2:v]trim=end_frame=366,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]" \
 -map "[v]" -map 3:a -c:v libx264 -preset medium -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -c:a aac -b:a 256k -shortest -movflags +faststart $O
echo "== streams"; ffprobe -v error -show_entries stream=codec_type,duration,nb_frames -of csv=p=0 $O
echo "== freezes"; ffmpeg -hide_banner -i $O -vf freezedetect=n=0.002:d=0.6 -an -f null - 2>&1 | grep -E "freeze_start|freeze_dur" | head -8 || true
echo "== black"; ffmpeg -hide_banner -i $O -vf blackdetect=d=0.3:pix_th=0.08 -an -f null - 2>&1 | grep blackdetect | head -5 || true
echo "== loudness"; ffmpeg -hide_banner -i $O -af ebur128=peak=true -vn -f null - 2>&1 | grep -E " I:| Peak:" | tail -2
ls -la $O
