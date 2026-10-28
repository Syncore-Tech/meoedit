"""ffmpeg / ffprobe helpers and contact sheets."""

import json
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import fonts

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".3gp"}


class FFmpegError(RuntimeError):
    pass


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        tail = "\n".join(p.stderr.strip().splitlines()[-15:])
        raise FFmpegError(f"Lệnh lỗi: {' '.join(map(str, cmd))}\n{tail}")
    return p.stdout


def is_image(path):
    return Path(path).suffix.lower() in IMAGE_EXT


def probe(path):
    path = Path(path)
    info = {"file": str(path), "name": path.name}
    if path.suffix.lower() in {".heic", ".heif"}:
        info["error"] = "HEIC chưa hỗ trợ. Trên macOS đổi sang JPG: sips -s format jpeg in.heic --out out.jpg"
        return info
    if is_image(path):
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            info.update(type="image", width=im.width, height=im.height)
        return info
    data = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    # Cover art inside an mp3/m4a shows up as a one-frame "video" stream; it is not footage.
    v = next((s for s in data["streams"] if s["codec_type"] == "video"
              and not s.get("disposition", {}).get("attached_pic")), None)
    if not v:
        if any(s["codec_type"] == "audio" for s in data["streams"]):
            info.update(type="audio", duration=round(float(data["format"].get("duration", 0)), 2))
        else:
            info["error"] = "Không có hình ảnh hay âm thanh"
        return info
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = rot or int(v.get("tags", {}).get("rotate", 0))
    if abs(rot) % 180 == 90:
        w, h = h, w
    info.update(
        type="video",
        width=w,
        height=h,
        duration=round(float(data["format"].get("duration", v.get("duration", 0))), 2),
        has_audio=any(s["codec_type"] == "audio" for s in data["streams"]),
        fps=_fps(v.get("avg_frame_rate", "0/1")),
    )
    return info


def _fps(rate):
    n, d = rate.split("/")
    return round(int(n) / int(d), 2) if int(d) else 0


def frame_at(path, t, out):
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(path),
         "-frames:v", "1", "-q:v", "3", str(out)])
    return out


def cover(im, w, h):
    return ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS)


def _label(draw, xy, text, font):
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 6, bbox[1] - 4, bbox[2] + 6, bbox[3] + 4], fill=(0, 0, 0, 200))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))


def grid(tiles, cols, tile_w, tile_h, out, title=None):
    """tiles: [(PIL.Image, label)] -> one JPG contact sheet."""
    font = fonts.load("BeVietnamPro-SemiBold", 22)
    rows = math.ceil(len(tiles) / cols)
    top = 56 if title else 0
    sheet = Image.new("RGB", (cols * tile_w + (cols + 1) * 8, top + rows * tile_h + (rows + 1) * 8), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((12, 12), title, font=fonts.load("BeVietnamPro-Bold", 28), fill=(255, 255, 255))
    for i, (im, label) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = 8 + c * (tile_w + 8), top + 8 + r * (tile_h + 8)
        if im is not None:
            sheet.paste(cover(im, tile_w, tile_h), (x, y))
        _label(d, (x + 8, y + tile_h - 40), label, font)  # bottom: top-left is where templates put tags
    sheet.save(out, quality=88)
    return out


def thumbs(files, out, per_video=4, tile_w=270, tile_h=480):
    """Contact sheet of raw media so the agent (and user) can see what each file holds."""
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(files, 1):
            info = probe(f)
            if info.get("error"):
                tiles.append((None, f"#{i} {info['name']}: {info['error']}"))
                continue
            if info["type"] == "audio":
                continue
            if info["type"] == "image":
                with Image.open(f) as im:
                    tiles.append((ImageOps.exif_transpose(im).copy(), f"#{i} {info['name']} (ảnh)"))
                continue
            dur = info["duration"]
            for k in range(per_video):
                t = dur * (k + 0.5) / per_video
                jpg = Path(tmp) / f"{i}_{k}.jpg"
                frame_at(f, t, jpg)
                with Image.open(jpg) as im:
                    tiles.append((im.copy(), f"#{i} {info['name']} @{t:.1f}s/{dur:.1f}s"))
        return grid(tiles, max(per_video, 4), tile_w, tile_h, out)
