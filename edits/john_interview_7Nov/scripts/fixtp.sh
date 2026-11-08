#!/bin/bash
# keep picture, re-make the AAC with a soft true-peak limiter so the delivered file is <= -1.5 dBTP (target about -2)
IN=$1; OUT=$2
ffmpeg -nostdin -v error -y -i "$IN" -map 0:v -map 0:a -c:v copy -af "aresample=192000,alimiter=limit=0.77:attack=2:release=60:level=false:asc=1,aresample=48000" -c:a aac -b:a 320k -movflags +faststart "$OUT"
ffmpeg -nostdin -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^ +I:|^ +Peak:" | tail -2 | tr -s ' ' | tr '\n' ' '; echo
