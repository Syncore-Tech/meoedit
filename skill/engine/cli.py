#!/usr/bin/env python3
"""meoedit CLI.

  python3 cli.py doctor                      kiểm tra máy (ffmpeg, Pillow, font)
  python3 cli.py templates                   liệt kê template
  python3 cli.py probe FILE...               thông tin media (JSON)
  python3 cli.py thumbs FILE... -o sheet.jpg ảnh xem nhanh các file gốc
  python3 cli.py video plan.json --preview   bản nháp 540x960 + ảnh tổng quan
  python3 cli.py video plan.json             bản cuối 1080x1920
  python3 cli.py image plan.json             thiết kế ảnh
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from meo import __version__, fonts, image, media, templates, video  # noqa: E402


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def doctor(_):
    ok = True
    for tool in ("ffmpeg", "ffprobe"):
        found = shutil.which(tool)
        print(f"{'✓' if found else '✗'} {tool}: {found or 'chưa cài (macOS: brew install ffmpeg)'}")
        ok &= bool(found)
    import PIL
    print(f"✓ Pillow {PIL.__version__}")
    try:
        fonts.fetch_all()
        print(f"✓ font: {len(fonts.FONTS)} font trong {fonts.FONT_DIR}")
    except Exception as e:  # network or disk
        ok = False
        print(f"✗ tải font lỗi: {e}")
    print(f"meoedit {__version__}: {'sẵn sàng' if ok else 'cần sửa các mục ✗ ở trên'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(prog="meoedit", description="Dựng video và thiết kế ảnh từ template.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("templates")
    p = sub.add_parser("probe")
    p.add_argument("files", nargs="+")
    p = sub.add_parser("thumbs")
    p.add_argument("files", nargs="+")
    p.add_argument("-o", "--out", default="meoedit-thumbs.jpg")
    p.add_argument("--per-video", type=int, default=4)
    p = sub.add_parser("video")
    p.add_argument("plan")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--keep-work", action="store_true")
    p = sub.add_parser("image")
    p.add_argument("plan")
    a = ap.parse_args()

    try:
        if a.cmd == "doctor":
            return doctor(a)
        if a.cmd == "templates":
            emit(templates.all_templates())
        elif a.cmd == "probe":
            emit([media.probe(f) for f in a.files])
        elif a.cmd == "thumbs":
            emit({"sheet": str(media.thumbs(a.files, a.out, a.per_video))})
        elif a.cmd == "video":
            emit(video.render(a.plan, preview=a.preview, keep_work=a.keep_work))
        elif a.cmd == "image":
            emit(image.render(a.plan))
    except (ValueError, FileNotFoundError, media.FFmpegError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
