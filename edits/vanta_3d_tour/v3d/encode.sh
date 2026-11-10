#!/bin/sh
# usage: ./encode.sh framedir out.mp4 [fps=30] [ext=png|jpg]  -> H.264 crf14 yuv420p (+faststart)
D=${1:?framedir}; O=${2:?out.mp4}; FPS=${3:-30}; EXT=${4:-$( ls "$D" | grep -m1 -o '\(png\|jpg\)$' )}
ffmpeg -y -loglevel error -framerate "$FPS" -i "$D/f%05d.$EXT" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$O" && echo "wrote $O"
