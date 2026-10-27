"""Render a vertical video from a plan.json and a video template."""

import json
import shutil
import tempfile
from pathlib import Path

from PIL import Image

from . import media, templates, text


def _even(n):
    return int(n) // 2 * 2


def _resolve(base, src):
    if src.startswith("color:"):
        return src
    p = Path(src).expanduser()
    p = p if p.is_absolute() else base / p
    if not p.exists():
        raise FileNotFoundError(f"Không thấy file: {p}")
    return p


def _segment(i, sc, style, plan, W, H, OW, OH, fps, enc, work, base):
    dur = float(sc["duration"])
    src = _resolve(base, sc["src"])
    speed = float(sc.get("speed", 1))
    grade = sc.get("grade", style.get("grade"))

    overlay = text.render_layers(style["presets"], sc.get("texts", []), W, H)
    if (OW, OH) != (W, H):
        overlay = overlay.resize((OW, OH), Image.LANCZOS)
    ov_png = work / f"ov{i:02d}.png"
    overlay.save(ov_png)

    has_audio = False
    if isinstance(src, str):
        color = src.split(":", 1)[1]
        inputs = ["-f", "lavfi", "-t", f"{dur}", "-i", f"color=c={color}:s={OW}x{OH}:r={fps}"]
        vchain = "[0:v]setsar=1"
    elif media.is_image(src):
        inputs = ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(src)]
        zw, zh = _even(OW * 1.12), _even(OH * 1.12)
        motion = sc.get("motion", style.get("image_motion", "pan"))
        if motion == "none":
            vchain = f"[0:v]scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},setsar=1"
        else:
            direction = "(iw-{w})*min(t/{d},1)" if motion == "pan" else "(iw-{w})*(1-min(t/{d},1))"
            x = direction.format(w=OW, d=dur)
            vchain = (f"[0:v]scale={zw}:{zh}:force_original_aspect_ratio=increase,crop={zw}:{zh},"
                      f"crop={OW}:{OH}:x='{x}':y='(ih-{OH})/2',setsar=1")
    else:
        info = media.probe(src)
        start = float(sc.get("start", 0))
        inputs = ["-ss", f"{start}", "-t", f"{dur * speed}", "-i", str(src)]
        vchain = f"[0:v]scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},setsar=1"
        if speed != 1:
            vchain += f",setpts=PTS/{speed}"
        has_audio = info.get("has_audio") and speed == 1

    vchain += f",fps={fps},tpad=stop_mode=clone:stop_duration={dur}"
    if grade:
        vchain += f",{grade}"
    vchain += "[base]"

    inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(ov_png)]
    fade_in = float(style.get("text_fade_in", 0.25))
    ochain = f"[1:v]format=rgba,fade=t=in:st=0.08:d={fade_in}:alpha=1[ov]" if fade_in else "[1:v]format=rgba[ov]"

    vol = float(sc.get("volume", plan.get("original_volume", style.get("original_volume", 0))))
    if has_audio and vol > 0:
        achain = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},"
                  f"afade=t=in:d=0.05,apad,atrim=0:{dur},afade=t=out:st={max(dur - 0.08, 0)}:d=0.08[a]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        achain = "[2:a]anull[a]"

    fc = ";".join([vchain, ochain, "[base][ov]overlay=0:0:shortest=1,format=yuv420p[v]", achain])
    out = work / f"seg{i:02d}.mp4"
    media.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-t", f"{dur}", "-r", str(fps), *enc, "-c:a", "aac", "-b:a", "160k", str(out)])
    return out, dur


def render(plan_path, preview=False, keep_work=False):
    plan_path = Path(plan_path).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    style = templates.load(plan["template"])
    if style["kind"] != "video":
        raise ValueError(f"Template '{plan['template']}' là template ảnh, dùng lệnh 'image'.")
    scenes = plan["scenes"]
    if not scenes:
        raise ValueError("Plan chưa có cảnh nào.")

    W, H = style["size"]
    fps = int(style.get("fps", 30))
    if preview:
        OW, OH = _even(W / 2), _even(H / 2)
        enc = ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-pix_fmt", "yuv420p"]
    else:
        OW, OH = W, H
        enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p"]

    out = Path(plan.get("output", "meoedit-video.mp4")).expanduser()
    out = out if out.is_absolute() else base / out
    if preview:
        out = out.with_name(out.stem + ".preview.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    trans = {**style.get("transition", {}), **plan.get("transition", {})}
    work = Path(tempfile.mkdtemp(prefix="meoedit-"))
    try:
        segs = [_segment(i, sc, style, plan, W, H, OW, OH, fps, enc, work, base) for i, sc in enumerate(scenes)]
        durs = [d for _, d in segs]
        n = len(segs)
        cut = trans.get("type", "fade") == "cut" or n == 1
        t = 0.0 if cut else min(float(trans.get("duration", 0.3)), min(durs) / 2.5)
        starts = [sum(durs[:i]) - i * t for i in range(n)]
        total = sum(durs) - (n - 1) * t

        inputs = []
        for p, _ in segs:
            inputs += ["-i", str(p)]
        parts = []
        if cut:
            parts.append("".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vx]")
        else:
            prev = "[0:v]"
            for k in range(1, n):
                # Per-scene override picks another xfade type; the overlap length stays the same.
                kind = scenes[k].get("transition", trans.get("type", "fade"))
                label = "[vx]" if k == n - 1 else f"[x{k}]"
                parts.append(f"{prev}[{k}:v]xfade=transition={kind}:duration={t:.3f}:offset={starts[k]:.3f}{label}")
                prev = label
        fo = float(style.get("fade_out", 0))
        parts.append(f"[vx]fade=t=out:st={max(total - fo, 0):.3f}:d={fo}[vout]" if fo else "[vx]null[vout]")

        for i in range(n):
            ms = int(round(starts[i] * 1000))
            parts.append(f"[{i}:a]adelay={ms}|{ms}[d{i}]")
        parts.append("".join(f"[d{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,"
                     f"atrim=0:{total:.3f}[speech]")

        music = plan.get("music")
        if music:
            mpath = _resolve(base, music)
            mi = n
            inputs += ["-stream_loop", "-1", "-i", str(mpath)]
            mv = float(plan.get("music_volume", style.get("music_volume", 0.3)))
            parts.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},"
                         f"asetpts=PTS-STARTPTS,volume={mv},afade=t=in:d=0.4,"
                         f"afade=t=out:st={max(total - 1.5, 0):.3f}:d=1.5[m]")
            if any(float(s.get("volume", plan.get("original_volume", style.get("original_volume", 0)))) > 0
                   for s in scenes):
                parts.append("[speech]asplit=2[sp1][sp2]")
                parts.append("[m][sp1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md]")
                parts.append("[md][sp2]amix=inputs=2:normalize=0:duration=first[aout]")
            else:
                parts.append("[m][speech]amix=inputs=2:normalize=0:duration=first[aout]")
        else:
            parts.append("[speech]anull[aout]")

        # Social apps play everything at about -14 LUFS; normalize so the video is not quieter than its neighbours.
        parts.append("[aout]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[afinal]")
        media.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts),
                   "-map", "[vout]", "-map", "[afinal]", *enc, "-c:a", "aac", "-b:a", "192k",
                   "-movflags", "+faststart", "-t", f"{total:.3f}", str(out)])

        result = {"output": str(out), "duration": round(total, 2), "scenes": n,
                  "size": f"{OW}x{OH}", "preview": preview}
        if preview:
            sheet = out.with_suffix(".jpg")
            tiles = []
            for i in range(n):
                tmid = starts[i] + durs[i] / 2
                jpg = work / f"mid{i:02d}.jpg"
                media.frame_at(out, tmid, jpg)
                with Image.open(jpg) as im:
                    tiles.append((im.copy(), f"Cảnh {i + 1} @{tmid:.1f}s"))
            media.grid(tiles, min(n, 5), 270, 480, sheet, title=f"{plan['template']} · {total:.1f}s · bản nháp")
            result["sheet"] = str(sheet)
        return result
    finally:
        if keep_work:
            print(f"(giữ thư mục tạm: {work})")
        else:
            shutil.rmtree(work, ignore_errors=True)
