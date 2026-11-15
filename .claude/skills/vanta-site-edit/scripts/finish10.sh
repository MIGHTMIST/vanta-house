#!/bin/bash
# join parts frame-exact, add the mix, checks + a beat check (every cut vs the beat grid)
H=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype
OUT=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/out
cd $H
for v in ${@:-n2 crew build}; do
  case $v in offplan) n=VantaHouse_Site_R4_4_OFFPLAN_loop.mp4; parts="a b c";; n2) n=VantaHouse_Site_R4_1_CINEMATIC.mp4; parts="a1 a2 b c1 c2";; crew) n=VantaHouse_Site_R4_2_CREW_loop.mp4; parts="a b";; build) n=VantaHouse_Site_R4_3_BUILDING_loop.mp4; parts="a b";; esac
  O=$OUT/$n; ins=""; fc=""; i=0; lab=""
  for p in $parts; do ins="$ins -i p10_$v$p.mp4"; fc="$fc[$i:v]setpts=PTS-STARTPTS[v$i];"; lab="$lab[v$i]"; i=$((i+1)); done
  ffmpeg -v error -y $ins -i final_mix10_$v.wav -filter_complex "$fc${lab}concat=n=$i:v=1:a=0[v]" \
   -map "[v]" -map $i:a -c:v libx264 -preset medium -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
   -c:a aac -b:a 256k -shortest -movflags +faststart $O
  echo "== $n"; ffprobe -v error -show_entries stream=codec_type,duration,nb_frames -of csv=p=0 $O
  echo "loudness: $(ffmpeg -hide_banner -nostats -i $O -af ebur128=peak=true -vn -f null - 2>&1 | grep -A14 Summary | grep -E 'I:' | tr -s ' ')"
  VID=$v python3 beatcheck.py $O
done
