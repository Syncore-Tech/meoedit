#!/usr/bin/env bash
# Smoke test: makes synthetic media with ffmpeg, then renders every template.
# Usage: tests/smoke.sh [out_dir]   (default: a new temp dir)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/skill/engine/cli.py"
OUT="${1:-$(mktemp -d -t meoedit-smoke)}"
mkdir -p "$OUT"
cd "$OUT"

ff() { ffmpeg -y -v error "$@"; }
ff -f lavfi -i "testsrc2=s=1080x1920:r=30:d=6" -f lavfi -i "sine=f=440:d=6" -shortest -c:v libx264 -pix_fmt yuv420p doc.mp4
ff -f lavfi -i "testsrc2=s=1920x1080:r=30:d=6" -c:v libx264 -pix_fmt yuv420p ngang.mp4
ff -f lavfi -i "mandelbrot=s=1600x1200" -frames:v 1 anh.jpg
ff -f lavfi -i "sine=f=220:d=40" -f lavfi -i "sine=f=330:d=40" -filter_complex amix=inputs=2 nhac.m4a

python3 "$CLI" probe doc.mp4 ngang.mp4 anh.jpg > /dev/null
python3 "$CLI" thumbs doc.mp4 ngang.mp4 anh.jpg -o thumbs.jpg > /dev/null

cat > cafe.plan.json <<'JSON'
{
  "template": "review-quan-cafe",
  "output": "cafe.mp4",
  "music": "nhac.m4a",
  "scenes": [
    {"src": "doc.mp4", "start": 0.5, "duration": 2.5, "volume": 0.8, "texts": [
      {"preset": "dia-diem", "text": "Quận 3, Sài Gòn"},
      {"preset": "hook", "text": "Quán cà phê yên tĩnh nhất mình từng ngồi"}]},
    {"src": "ngang.mp4", "start": 1, "duration": 2.5, "volume": 0.8, "texts": [
      {"preset": "ten-quan", "text": "Mộc Chill"},
      {"preset": "caption", "text": "Không gian gỗ, nhiều cây, nhạc lofi nhỏ"}]},
    {"src": "anh.jpg", "duration": 2.5, "texts": [
      {"preset": "gia", "text": "45k"},
      {"preset": "caption", "text": "Bạc xỉu muối béo mà không gắt"}]},
    {"src": "color:#3B2A20", "duration": 2.5, "texts": [
      {"preset": "diem", "text": "8.5"},
      {"preset": "nho", "text": "Điểm của mình. Hợp ngồi làm việc cả buổi chiều."}]}
  ]
}
JSON

cat > vlog.plan.json <<'JSON'
{
  "template": "vlog-du-lich",
  "output": "vlog.mp4",
  "music": "nhac.m4a",
  "scenes": [
    {"src": "doc.mp4", "duration": 1.6, "texts": [
      {"preset": "ngay", "text": "Ngày 1"},
      {"preset": "dia-diem", "text": "Đà Lạt"},
      {"preset": "phu", "text": "3 ngày 2 đêm, 2 triệu rưỡi"}]},
    {"src": "ngang.mp4", "start": 2, "duration": 1.4, "texts": [
      {"preset": "tag", "text": "06:30 sáng"},
      {"preset": "caption", "text": "Săn mây ở đồi chè Cầu Đất, lạnh run nhưng đáng"}]},
    {"src": "anh.jpg", "duration": 1.4, "motion": "pan-back", "texts": [
      {"preset": "caption", "text": "Bánh căn 25k một đĩa"}]},
    {"src": "doc.mp4", "start": 3, "duration": 1.5, "speed": 2, "texts": [
      {"preset": "caption", "text": "Hẹn gặp lại nha"}]}
  ]
}
JSON

cat > card.plan.json <<'JSON'
{
  "template": "the-san-pham",
  "output": "card.png",
  "photo": "anh.jpg",
  "texts": [
    {"preset": "nhan", "text": "-20%"},
    {"preset": "ten", "text": "Nến thơm gỗ đàn hương"},
    {"preset": "mo-ta", "text": "Sáp đậu nành, cháy 40 giờ, hương ấm dịu"},
    {"preset": "gia", "text": "159.000đ"},
    {"preset": "shop", "text": "Tiệm Nhà Mèo · Giao toàn quốc"}
  ]
}
JSON

python3 "$CLI" video cafe.plan.json --preview
python3 "$CLI" video vlog.plan.json --preview
python3 "$CLI" video cafe.plan.json
python3 "$CLI" image card.plan.json

# Every template, every text style: one sample plan per template from its own preset list.
python3 - "$CLI" <<'PY'
import json, subprocess, sys
cli = sys.argv[1]
for t in json.loads(subprocess.check_output([sys.executable, cli, "templates"])):
    texts = [{"preset": p, "text": "Chữ mẫu " + p} for p in t["text_styles"]]
    if t["kind"] == "video":
        plan = {"template": t["name"], "output": f"all-{t['name']}.mp4", "scenes": [
            {"src": "doc.mp4", "duration": 1.2, "texts": texts},
            {"src": "anh.jpg", "duration": 1.0, "texts": texts[:1]}]}
        cmd = "video"
    else:
        plan = {"template": t["name"], "output": f"all-{t['name']}.png", "photos": ["anh.jpg", "anh.jpg"], "texts": texts}
        cmd = "image"
    path = f"all-{t['name']}.plan.json"
    json.dump(plan, open(path, "w"), ensure_ascii=False)
    subprocess.run([sys.executable, cli, cmd, path] + (["--preview"] if cmd == "video" else []),
                   check=True, stdout=subprocess.DEVNULL)
    print("ok", t["name"])
PY

for f in cafe.preview.mp4 cafe.preview.jpg vlog.preview.mp4 vlog.preview.jpg cafe.mp4 card.png thumbs.jpg; do
  test -s "$f" || { echo "THIẾU $f"; exit 1; }
done
ffprobe -v error -show_entries stream=codec_type,width,height:format=duration -of compact cafe.mp4
echo "OK: $OUT"
