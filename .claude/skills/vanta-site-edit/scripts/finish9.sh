#!/bin/bash
# join each video's 3 parts frame-exact (470 + 470 + 470 = 1410 frames = 47.0 s), add its mix, run checks
H=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype
OUT=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/out
cd $H
for v in ${@:-v1 v2 v3}; do
  case $v in v1) n=VantaHouse_Site_1_THE_CREW.mp4;; v2) n=VantaHouse_Site_2_THE_BUILDING.mp4;; v3) n=VantaHouse_Site_3_THE_PHOTOS.mp4;; esac
  O=$OUT/$n
  for p in a b c; do echo "$v$p $(ffprobe -v error -select_streams v -count_frames -show_entries stream=nb_read_frames -of csv=p=0 p9_$v$p.mp4)"; done
  ffmpeg -v error -y -i p9_${v}a.mp4 -i p9_${v}b.mp4 -i p9_${v}c.mp4 -i final_mix9_$v.wav -filter_complex \
   "[0:v]trim=end_frame=470,setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=470,setpts=PTS-STARTPTS[b];[2:v]trim=end_frame=470,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]" \
   -map "[v]" -map 3:a -c:v libx264 -preset medium -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
   -c:a aac -b:a 256k -shortest -movflags +faststart $O
  echo "== $n"; ffprobe -v error -show_entries stream=codec_type,duration,nb_frames -of csv=p=0 $O
  echo "freezes: $(ffmpeg -hide_banner -i $O -vf freezedetect=n=0.002:d=0.6 -an -f null - 2>&1 | grep -cE 'freeze_start')"
  echo "black: $(ffmpeg -hide_banner -i $O -vf blackdetect=d=0.5:pix_th=0.08 -an -f null - 2>&1 | grep blackdetect | tr '\n' ' ')"
  echo "loudness: $(ffmpeg -hide_banner -nostats -i $O -af ebur128=peak=true -vn -f null - 2>&1 | grep -A14 Summary | grep -E 'I:|Peak:' | tr -s ' ' | tr '\n' ' ')"
  ls -la $O
done
