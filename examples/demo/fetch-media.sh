#!/usr/bin/env bash
# Tải media cho bản demo (Pexels License + nhạc CC BY 4.0 của Kevin MacLeod) vào examples/demo/media.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p media
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
get() { [ -s "media/$1" ] || curl -fL -A "$UA" --progress-bar -o "media/$1" "$2"; }
for id in 8426100 30846352 13737099 13736673 34164108 40047468 13736675; do get "cafe-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 32117880 34081853 33887925 34081907 29684375 35840531; do get "vlog-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
get candle-6798396.jpg "https://images.pexels.com/photos/6798396/pexels-photo-6798396.jpeg?w=2000"
for id in 40420097 37266179 32017237 9888677 6645806 30320645; do get "food-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 18156289 34057218 34733102 35132253 35132257; do get "ootd-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 7308296 7316363 7316364 7316370 7316374; do get "unbox-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 12837556 12837558 34711974 35733990 37848045 37848046; do get "cook-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
for id in 32116008 8534373 40529241; do get "photo-$id.jpg" "https://images.pexels.com/photos/$id/pexels-photo-$id.jpeg?w=2000"; done
# Ảnh túi cho story khuyến mãi: một khung hình từ clip ootd-34733102.
[ -s media/photo-bag-34733102.jpg ] || ffmpeg -v error -y -ss 1.5 -i media/ootd-34733102.mp4 -frames:v 1 -q:v 2 media/photo-bag-34733102.jpg
for id in 32953540 36371120 36796001 37674124 38410480 39204540 40187590 40397792 40398038 7646600 7646763 7817246 8293132; do get "bds-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
get talk-8814493.mp4 "https://www.pexels.com/download/video/8814493/"
for id in 10145272 19162466 6612202; do get "gadget-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
get phone-6624858.mp4 "https://www.pexels.com/download/video/6624858/"
for id in 26540715 34491185 35075300 35585591 37281098; do get "gym-$id.mp4" "https://www.pexels.com/download/video/$id/"; done
get music-Lobby-Time.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lobby%20Time.mp3"
get music-Life-of-Riley.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Life%20of%20Riley.mp3"
get music-Happy-Alley.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Alley.mp3"
get music-Local-Forecast---Elevator.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Local%20Forecast%20-%20Elevator.mp3"
echo "Xong. Chạy: python3 ../../skill/engine/cli.py video cafe.plan.json --preview"
echo "truoc-sau-video.plan.json dùng out/vuon-may-residence.mp4: render du-an.plan.json trước."
