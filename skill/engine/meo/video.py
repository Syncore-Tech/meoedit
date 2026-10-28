"""Render a vertical video from a plan.json and a video template."""

import json
import shutil
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from . import media, subtitles, templates, text


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


def _zoom(sc, w, h, dur):
    """Scene "zoom": [from, to] scales the picture over the scene (1 = fill the frame);
    "zoom_to": [x, y] picks the point it closes in on (fractions, default the centre)."""
    if not sc.get("zoom"):
        return ""
    a, b = (float(v) for v in sc["zoom"])
    if min(a, b) < 1:
        raise ValueError("zoom nhỏ nhất là 1 (vừa khung), ví dụ [1, 1.15].")
    fx, fy = sc.get("zoom_to", [0.5, 0.5])
    z = f"({a}+({b - a})*min(t/{dur},1))"
    return (f",scale=w='trunc({w}*{z}/2)*2':h='trunc({h}*{z}/2)*2':eval=frame,"
            f"crop={w}:{h}:x='(iw-{w})*{fx}':y='(ih-{h})*{fy}'")


def _source(k, src, sc, style, w, h, dur, fps, start=0.0):
    """ffmpeg inputs + filter chain that turn one source into a w x h clip of dur seconds, as stream [s{k}].
    Returns (inputs, chain, has_audio)."""
    speed = float(sc.get("speed", 1))
    if isinstance(src, str):
        color = src.split(":", 1)[1]
        return (["-f", "lavfi", "-t", f"{dur}", "-i", f"color=c={color}:s={w}x{h}:r={fps}"],
                f"[{k}:v]setsar=1,fps={fps}[s{k}]", False)
    if media.is_image(src):
        inputs = ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(src)]
        zw, zh = _even(w * 1.12), _even(h * 1.12)
        motion = "none" if sc.get("zoom") else sc.get("motion", style.get("image_motion", "pan"))
        if motion == "none":
            chain = f"[{k}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
            chain += _zoom(sc, w, h, dur)
        else:
            direction = "(iw-{w})*min(t/{d},1)" if motion == "pan" else "(iw-{w})*(1-min(t/{d},1))"
            x = direction.format(w=w, d=dur)
            chain = (f"[{k}:v]scale={zw}:{zh}:force_original_aspect_ratio=increase,crop={zw}:{zh},"
                     f"crop={w}:{h}:x='{x}':y='(ih-{h})/2',setsar=1")
        return inputs, chain + f",fps={fps}[s{k}]", False
    info = media.probe(src)
    inputs = ["-ss", f"{start}", "-t", f"{dur * speed}", "-i", str(src)]
    chain = f"[{k}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
    if speed != 1:
        chain += f",setpts=PTS/{speed}"
    chain += _zoom(sc, w, h, dur)
    chain += f",fps={fps},tpad=stop_mode=clone:stop_duration={dur}[s{k}]"
    return inputs, chain, bool(info.get("has_audio")) and speed == 1


def _overlay_input(sc, style, W, H, OW, OH, dur, fps, work, i, shapes):
    """The scene's shapes + texts as an ffmpeg input: one looped PNG, or a PNG per typing step."""
    texts = sc.get("texts", [])
    presets = style["presets"]
    shape_layer = text.render_shapes(shapes, W, H)

    def frame(t_now=None):
        im = Image.alpha_composite(shape_layer, text.render_layers(presets, texts, W, H, t_now))
        return im.resize((OW, OH), Image.LANCZOS) if (OW, OH) != (W, H) else im

    timed = [t for t in texts if text.is_timed({**presets.get(t.get("preset"), {}), **t})]
    if not timed:
        png = work / f"ov{i:02d}.png"
        frame().save(png)
        return ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(png)]
    # One frame every 1/12 s (typing, texts that appear later, countdowns); the last holds to the end.
    step = 1 / 12
    lines, n, t_now = [], 0, 0.0
    while t_now < dur:
        png = work / f"ov{i:02d}_{n:03d}.png"
        frame(t_now).save(png)
        lines += [f"file '{png}'", f"duration {min(step, dur - t_now):.4f}"]
        n, t_now = n + 1, t_now + step
    lines.append(f"file '{png}'")
    lst = work / f"ov{i:02d}.txt"
    lst.write_text("\n".join(lines) + "\n")
    return ["-f", "concat", "-safe", "0", "-i", str(lst)]


def _segment(i, sc, style, plan, W, H, OW, OH, fps, enc, work, base):
    dur = float(sc["duration"])
    grade = sc.get("grade", style.get("grade"))
    shapes = sc.get("shapes", style.get("shapes", []))
    front = [s for s in shapes if not s.get("back")]
    inputs, parts, audio = [], [], []

    srcs = sc.get("srcs")
    if srcs:
        # Split scene: background (template colour + "back" shapes), then each source in its panel.
        panels = style.get("panels") or []
        if len(srcs) > len(panels):
            raise ValueError(f"Template '{plan['template']}' có {len(panels)} khung, cảnh {i + 1} có {len(srcs)} nguồn.")
        bg = Image.new("RGBA", (W, H), text.rgba(style.get("background", "#000000")))
        bg = Image.alpha_composite(bg, text.render_shapes([s for s in shapes if s.get("back")], W, H))
        bg_png = work / f"bg{i:02d}.png"
        bg.convert("RGB").resize((OW, OH), Image.LANCZOS).save(bg_png)
        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(bg_png)]
        parts.append(f"[0:v]setsar=1,fps={fps}[b0]")
        starts = list(sc.get("starts", []))
        starts += [sc.get("start", 0)] * (len(srcs) - len(starts))
        k = 1
        for j, (src, panel) in enumerate(zip(srcs, panels)):
            px, py, pw, ph = panel["box"]
            x, y, w, h = int(px * OW), int(py * OH), _even(pw * OW), _even(ph * OH)
            ins, chain, has_a = _source(k, _resolve(base, src), sc, style, w, h, dur, fps, float(starts[j]))
            inputs += ins
            parts.append(chain)
            mask = Image.new("L", (w, h), 0)
            r = int(panel.get("radius", 0) * OW / W)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
            m_png = work / f"mask{i:02d}_{j}.png"
            mask.save(m_png)
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", str(m_png)]
            parts.append(f"[{k + 1}:v]format=gray[m{k}];[s{k}]format=rgba[c{k}];[c{k}][m{k}]alphamerge[p{k}]")
            parts.append(f"[b{j}][p{k}]overlay={x}:{y}:shortest=1[b{j + 1}]")
            if has_a:
                audio.append((k, j))
            k += 2
        last = f"[b{len(srcs)}]"
        # Sound comes from one panel only: "audio_panel" (default the last one, the edited result).
        pick = int(sc.get("audio_panel", len(srcs) - 1))
        audio = [a for a, j in audio if j == pick]
    else:
        ins, chain, has_a = _source(0, _resolve(base, sc["src"]), sc, style, OW, OH, dur, fps,
                                    float(sc.get("start", 0)))
        inputs += ins
        parts.append(chain.replace("[s0]", "[b0]"))
        last, k = "[b0]", 1
        audio = [0] if has_a else []

    base_chain = f"{last}tpad=stop_mode=clone:stop_duration={dur}" + (f",{grade}" if grade else "") + "[base]"
    parts.append(base_chain)

    ov = k
    inputs += _overlay_input(sc, style, W, H, OW, OH, dur, fps, work, i, front)
    fade_in = float(style.get("text_fade_in", 0.25))
    parts.append(f"[{ov}:v]format=rgba,fps={fps},fade=t=in:st=0.08:d={fade_in}:alpha=1[ov]" if fade_in
                 else f"[{ov}:v]format=rgba,fps={fps}[ov]")
    parts.append("[base][ov]overlay=0:0:shortest=1,format=yuv420p[v]")

    vol = float(sc.get("volume", plan.get("original_volume", style.get("original_volume", 0))))
    if audio and vol > 0:
        parts.append(f"[{audio[0]}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},"
                     f"afade=t=in:d=0.05,apad,atrim=0:{dur},afade=t=out:st={max(dur - 0.08, 0)}:d=0.08[a]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        parts.append(f"[{ov + 1}:a]anull[a]")

    out = work / f"seg{i:02d}.mp4"
    media.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
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
        extra = n  # next free input index
        if plan.get("texts"):
            # Plan-level texts (call to action, logo line) stay on screen for the whole video, over every cut.
            g = text.render_layers(style["presets"], plan["texts"], W, H)
            g = g.resize((OW, OH), Image.LANCZOS) if (OW, OH) != (W, H) else g
            g_png = work / "global.png"
            g.save(g_png)
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(g_png)]
            parts.append(f"[vx][{extra}:v]overlay=0:0:shortest=1[vg]")
            extra += 1
            vlast = "[vg]"
        else:
            vlast = "[vx]"
        cues, sub_style = subtitles.load(plan, base)
        if cues:
            # One concat input: a transparent frame between cues, the cue's text while it is on.
            blank = work / "sub_blank.png"
            Image.new("RGBA", (OW, OH), (0, 0, 0, 0)).save(blank)
            lines, t_at = [], 0.0
            for c_i, cue in enumerate(cues):
                a, b = min(cue["start"], total), min(cue["end"], total)
                if b <= a or a < t_at:
                    continue
                if a > t_at:
                    lines += [f"file '{blank}'", f"duration {a - t_at:.3f}"]
                im = text.render_layers(style["presets"], [{**sub_style, "text": cue["text"]}], W, H)
                png = work / f"sub{c_i:03d}.png"
                (im.resize((OW, OH), Image.LANCZOS) if (OW, OH) != (W, H) else im).save(png)
                lines += [f"file '{png}'", f"duration {b - a:.3f}"]
                t_at = b
            lines += [f"file '{blank}'", f"duration {max(total - t_at, 0.04):.3f}", f"file '{blank}'"]
            lst = work / "subs.txt"
            lst.write_text("\n".join(lines) + "\n")
            inputs += ["-f", "concat", "-safe", "0", "-i", str(lst)]
            parts.append(f"[{extra}:v]format=rgba,fps={fps}[subs];{vlast}[subs]overlay=0:0:eof_action=pass[vs]")
            extra += 1
            vlast = "[vs]"
        fo = float(style.get("fade_out", 0))
        parts.append(f"{vlast}fade=t=out:st={max(total - fo, 0):.3f}:d={fo}[vout]" if fo else f"{vlast}null[vout]")

        for i in range(n):
            ms = int(round(starts[i] * 1000))
            parts.append(f"[{i}:a]adelay={ms}|{ms}[d{i}]")
        parts.append("".join(f"[d{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,"
                     f"atrim=0:{total:.3f}[speech]")

        music = plan.get("music")
        has_speech = any(float(s.get("volume", plan.get("original_volume", style.get("original_volume", 0)))) > 0
                         for s in scenes)
        if music:
            mpath = _resolve(base, music)
            mi = extra
            inputs += ["-stream_loop", "-1", "-i", str(mpath)]
            mv = float(plan.get("music_volume", style.get("music_volume", 0.3)))
            parts.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},"
                         f"asetpts=PTS-STARTPTS,volume={mv},afade=t=in:d=0.4,"
                         f"afade=t=out:st={max(total - 1.5, 0):.3f}:d=1.5[m]")
            if has_speech:
                parts.append("[speech]asplit=2[sp1][sp2]")
                parts.append("[m][sp1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md]")
                parts.append("[md][sp2]amix=inputs=2:normalize=0:duration=first[aout]")
            else:
                parts.append("[m][speech]amix=inputs=2:normalize=0:duration=first[aout]")
        else:
            parts.append("[speech]anull[aout]")

        # Social apps play everything at about -14 LUFS; normalize so the video is not quieter than its neighbours.
        # A silent track (no music, original sound off) makes loudnorm output NaN, so leave it as is.
        if music or has_speech:
            parts.append("[aout]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[afinal]")
        else:
            parts.append("[aout]anull[afinal]")
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
            # Tiles keep the template's shape: 270 wide for vertical/square, 480 wide for landscape.
            tw = 480 if W > H else 270
            th = round(tw * H / W)
            media.grid(tiles, min(n, 3 if W > H else 5), tw, th, sheet,
                       title=f"{plan['template']} · {total:.1f}s · bản nháp")
            result["sheet"] = str(sheet)
        return result
    finally:
        if keep_work:
            print(f"(giữ thư mục tạm: {work})")
        else:
            shutil.rmtree(work, ignore_errors=True)
