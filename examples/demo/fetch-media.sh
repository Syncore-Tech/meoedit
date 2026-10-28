#!/usr/bin/env bash
# Tải media cho bản demo (Pexels License + nhạc CC BY 4.0 của Kevin MacLeod) vào examples/demo/media.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p media
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
get() { [ -s "media/$1" ] || curl -fL -A "$UA" --progress-bar -o "media/$1" "$2"; }
for id in 8426100 30846352 13737099 13736673 34164108 40047468 13736675; do get "cafe-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 32117880 34081853 33887925 34081907 29684375 35840531; do get "vlog-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
get candle-6798396.jpg "https://images.pexels.com/photos/6798396/pexels-photo-6798396.jpeg?w=2000"
get music-Lobby-Time.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lobby%20Time.mp3"
get music-Life-of-Riley.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Life%20of%20Riley.mp3"
echo "Xong. Chạy: python3 ../../skill/engine/cli.py video cafe.plan.json --preview"
