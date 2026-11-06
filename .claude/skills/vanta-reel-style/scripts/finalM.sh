#!/bin/bash
# composite video M: crossfade plates, MyEdit_B grade (curves/teal-warm balance/vignette/grain), titles overlay, ambient score
set -e
S=/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad; M=$S/M; DUR=11.9
ffmpeg -v error -y -i $M/m1.mkv -i $M/m2.mkv -i $M/m3.mkv -i $M/ov.mkv -i $M/score_raw.wav -filter_complex "
 [0:v]format=gbrp,settb=AVTB[a];[1:v]format=gbrp,settb=AVTB[b];[2:v]format=gbrp,settb=AVTB[c];
 [a][b]xfade=transition=fade:duration=0.5:offset=3.8[ab];[ab][c]xfade=transition=fade:duration=0.5:offset=7.6,format=rgb24,
   curves=all='0/0 0.25/0.23 0.5/0.49 0.8/0.80 1/0.95',
   eq=contrast=1.06:saturation=1.10,
   colorbalance=rs=-0.04:gs=0.0:bs=0.05:rm=0.01:gm=-0.025:rh=0.05:gh=-0.005:bh=-0.04,
   vignette=angle=PI/5,unsharp=5:5:0.4[g];
 [3:v]format=rgba[ov];
 [g][ov]overlay=0:0:format=rgb,noise=alls=4:allf=t,fade=t=in:st=0:d=0.35,fade=t=out:st=11.45:d=0.45,format=yuv444p[v];
 [4:a]lowpass=f=2400,highpass=f=35,aecho=0.8:0.55:70|140:0.28|0.18,afade=t=in:d=0.5,afade=t=out:st=11.0:d=0.9,
   alimiter=limit=0.8,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,atrim=0:$DUR[aout]
" -map "[v]" -map "[aout]" -c:v libx264 -preset veryfast -qp 0 -r 30 -c:a pcm_s24le -t $DUR $M/M_lossless.mkv
CM="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
O=$S/out/VantaHouse_M_slowglide_1080x1920_HQ.mp4
ffmpeg -v error -y -i $M/M_lossless.mkv -vf "scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -maxrate 45M -bufsize 90M -tune film -profile:v high -level 4.2 -g 30 -keyint_min 30 -r 30 $CM -af volume=-1.1dB -c:a aac -b:a 320k -ar 48000 -movflags +faststart $O
ffmpeg -v error -y -i $O -vf scale=720:1280:flags=lanczos -c:v libx264 -crf 23 -maxrate 1600k -bufsize 3200k -preset slow -c:a aac -b:a 128k -movflags +faststart $S/out/VantaHouse_M_slowglide_WhatsApp_720.mp4
