#!/bin/bash
# Vertical (9:16) social edit of blackstone footage 433A6916.MOV, made with ffmpeg only.
# Usage: ./make_edit.sh /path/to/433A6916.MOV /path/to/output.mp4
# Steps: 0.5x slow motion with motion interpolation -> eased pan from listener to speaker
# with slow push-in -> grade (soft highlights, teal/warm split, vignette, grain)
# -> text hook -> sound bed (stretched room tone + synth pad + pan whoosh), -14 LUFS.
set -e
SRC=$1; OUT=$2
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -an \
 -vf "scale=in_range=pc:out_range=tv,format=yuv420p,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=2.0*PTS,fps=30" \
 -c:v libx264 -crf 8 -preset fast "$TMP/slow.mp4"
T=4.0667
FB=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
FM=/usr/share/fonts/opentype/inter/Inter-Medium.otf
# eased pan progress p(t): hold 0.35s, glide 3.0s, settle
U="clip((t-0.35)/3.0\,0\,1)"
P="($U*$U*(3-2*$U))"
ffmpeg -v error -y \
 -i "$TMP/slow.mp4" \
 -i "$SRC" \
 -f lavfi -i "color=c=black:s=1080x1920:d=$T,format=rgba,geq=r=0:g=0:b=0:a='if(lt(Y\,980)\,0\,215*pow((Y-980)/940\,0.9))'" \
 -f lavfi -i "color=c=0x2EC4B6:s=96x6:d=$T:r=30,format=rgba" \
 -f lavfi -i "aevalsrc='0.06*(sin(2*PI*110*t)+sin(2*PI*110.35*t)+0.8*sin(2*PI*164.81*t)+0.8*sin(2*PI*165.2*t)+0.6*sin(2*PI*220*t)+0.45*sin(2*PI*261.63*t)+0.35*sin(2*PI*329.63*t)+0.2*sin(2*PI*493.88*t))*(0.8+0.2*sin(2*PI*0.4*t))|0.06*(sin(2*PI*109.7*t)+sin(2*PI*110.15*t)+0.8*sin(2*PI*164.6*t)+0.8*sin(2*PI*165.0*t)+0.6*sin(2*PI*220.3*t)+0.45*sin(2*PI*261.9*t)+0.35*sin(2*PI*329.3*t)+0.2*sin(2*PI*494.3*t))*(0.8+0.2*sin(2*PI*0.4*t+1))':s=48000:d=$T" \
 -f lavfi -i "anoisesrc=c=pink:a=0.5:d=$T:r=48000" \
 -filter_complex "
 [0:v]scale=w='trunc(1920*(1+0.08*t/$T)/2)*2':h=-2:eval=frame:flags=bicubic,
      crop=608:1080:x='clip((1616+(470-1616)*$P)*(iw/1920)-304\,0\,iw-608)':y='(ih-1080)*0.3',
      scale=1080:1920:flags=lanczos,setsar=1,
      curves=all='0/0 0.25/0.23 0.5/0.49 0.8/0.80 1/0.95',
      eq=contrast=1.06:saturation=1.10,
      colorbalance=rs=-0.04:gs=0.0:bs=0.05:rh=0.05:gh=0.01:bh=-0.04,
      vignette=angle=PI/5,
      unsharp=5:5:0.5,
      noise=alls=4:allf=t,format=yuv420p[base];
 [2:v]format=rgba[grad];
 [3:v]fade=t=in:st=0.95:d=0.4:alpha=1[bar];
 [base][grad]overlay=0:0:format=auto[g1];
 [g1][bar]overlay=x=(W-w)/2:y=1262:format=auto,
   drawtext=fontfile=$FB:text='EVERY BIG DEAL':fontsize=94:fontcolor=white:
     x=(w-text_w)/2:y='1290+26*pow(1-clip((t-0.95)/0.5\,0\,1)\,2)':
     alpha='clip((t-0.95)/0.5\,0\,1)':shadowcolor=black@0.35:shadowx=0:shadowy=3,
   drawtext=fontfile=$FM:text='STARTS WITH A CONVERSATION':fontsize=46:fontcolor=white@0.92:
     x=(w-text_w)/2:y='1412+22*pow(1-clip((t-1.2)/0.5\,0\,1)\,2)':
     alpha='clip((t-1.2)/0.5\,0\,1)':shadowcolor=black@0.35:shadowx=0:shadowy=2,
   fade=t=out:st=3.72:d=0.34,format=yuv420p[v];
 [1:a]atempo=0.5,lowpass=f=750,highpass=f=80,volume=0.55,atrim=0:$T[room];
 [4:a]lowpass=f=2200,aecho=0.8:0.6:70|140:0.3|0.2,afade=t=in:d=0.6,afade=t=out:st=3.3:d=0.75,volume=0.9[pad];
 [5:a]aformat=channel_layouts=stereo,bandpass=f=900:width_type=o:w=2,volume=eval=frame:volume='0.35*pow(sin(PI*clip((t-0.35)/3.0\,0\,1))\,2)'[wh];
 [room][pad][wh]amix=inputs=3:normalize=0,alimiter=limit=0.8,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,atrim=0:$T[a]
 " -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 -movflags +faststart \
 -c:a aac -b:a 192k -ar 48000 -t $T "$OUT"
