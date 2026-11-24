#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
/usr/bin/python3 _Code/captions.py
for section in '0 35' '35 75' '75 140' '140 200' '200 270' '270 300'; do
    /usr/bin/python3 _Code/animate.py $section
done
for clip in 000 035 075 140 200 270; do echo "file '$clip.mp4'"; done > build/parts.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/parts.txt -i Assets/Naman_Narration.flac -vf "drawbox=x=0:y=0:w=iw:h=101:color=0x0a1423:t=fill,ass=build/top.ass" -map 0:v -map 1:a -c:v libx264 -preset veryfast -crf 18 -threads 6 -c:a aac -b:a 128k -movflags +faststart -t 300 How_Matrices_Transform_Vectors_Video.mp4
