"""Render text layers (from template presets) onto a transparent canvas."""

from PIL import Image, ImageDraw, ImageFilter

from . import fonts


def rgba(color):
    c = color.lstrip("#")
    if len(c) == 6:
        c += "FF"
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4, 6))


def place(base, layer, x, y):
    """Alpha-composite layer onto base at (x, y); parts outside base are clipped."""
    tmp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tmp.paste(layer, (x, y))
    return Image.alpha_composite(base, tmp)


def wrap(text, font, max_w, stroke=0):
    """Greedy wrap, then narrow the width as far as the line count allows so lines come out even
    (no one-word orphan on the last line)."""
    lines = _greedy(text, font, max_w, stroke)
    if len(lines) < 2:
        return lines
    lo, hi = max_w / len(lines), max_w
    while hi - lo > 4:
        mid = (lo + hi) / 2
        if len(_greedy(text, font, mid, stroke)) == len(lines):
            hi = mid
        else:
            lo = mid
    return _greedy(text, font, hi, stroke)


def _greedy(text, font, max_w, stroke):
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for w in words[1:]:
            trial = line + " " + w
            if font.getlength(trial) + 2 * stroke <= max_w:
                line = trial
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def _block(preset, text, W, reveal=None):
    """Draw one text block on its own tight RGBA tile. reveal = how many characters to show (typewriter);
    the layout is that of the full text so lines do not move while typing."""
    size = preset.get("size", 64)
    font = fonts.load(preset.get("font", "BeVietnamPro-Bold"), size, preset.get("variation"))
    if preset.get("uppercase"):
        text = text.upper()
    stroke = preset.get("stroke") or {}
    sw = int(stroke.get("width", 0))
    box = preset.get("box")
    pad_y, pad_x = (box.get("pad", [16, 28]) if box else [0, 0])
    line_mode = bool(box) and preset.get("box_mode") == "line"

    max_w = preset.get("max_width", 0.86) * W - (2 * pad_x)
    lines = wrap(text, font, max_w, sw)
    ascent, descent = font.getmetrics()
    lh = int((ascent + descent) * preset.get("line_spacing", 1.12))
    widths = [font.getlength(l) + 2 * sw for l in lines]
    block_w = int(max(widths))
    block_h = lh * (len(lines) - 1) + ascent + descent + 2 * sw
    gap = int(preset.get("line_gap", 10)) if line_mode else 0
    if line_mode:
        block_h += gap * (len(lines) - 1)

    margin = 40  # room for shadow blur
    tw, th = block_w + 2 * pad_x + 2 * margin, block_h + 2 * pad_y + 2 * margin
    tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    align = preset.get("align", "center")

    def line_x(w):
        if align == "left":
            return margin + pad_x
        if align == "right":
            return margin + pad_x + block_w - w
        return margin + pad_x + (block_w - w) / 2

    if box and not line_mode:
        d.rounded_rectangle([margin, margin, tw - margin, th - margin],
                            radius=box.get("radius", 24), fill=rgba(box["color"]))

    text_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    y = margin + pad_y
    left = len(text) if reveal is None else int(reveal)
    for line, w in zip(lines, widths):
        x = line_x(w)
        line, left = line[:max(left, 0)], left - len(line) - 1
        if not line:
            y += lh + gap
            continue
        if line_mode:
            d.rounded_rectangle([x - pad_x, y - pad_y, x + w + pad_x, y + ascent + descent + 2 * sw + pad_y],
                                radius=box.get("radius", 16), fill=rgba(box["color"]))
        td.text((x + sw, y + sw), line, font=font, fill=rgba(preset.get("color", "#FFFFFF")),
                stroke_width=sw, stroke_fill=rgba(stroke.get("color", "#000000")) if sw else None,
                anchor="la")
        y += lh + gap

    shadow = preset.get("shadow")
    if shadow:
        alpha = text_layer.getchannel("A")
        sh = Image.new("RGBA", (tw, th), rgba(shadow.get("color", "#00000099")))
        sh.putalpha(alpha.point(lambda a: a * rgba(shadow.get("color", "#00000099"))[3] // 255))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow.get("blur", 10)))
        ox, oy = shadow.get("offset", [0, 6])
        tile = place(tile, sh, int(ox), int(oy))
    tile.alpha_composite(text_layer)

    if preset.get("rotate"):
        tile = tile.rotate(preset["rotate"], expand=True, resample=Image.BICUBIC)
    return tile, margin, lines


def render_shapes(shapes, W, H):
    """Shapes from a template, box = [x, y, w, h] as fractions:
    {"box", "color", "radius"}: filled rectangle
    {"type": "gradient", "box", "from", "to"}: top-to-bottom gradient
    {"type": "frame", "box", "color", "width", "radius", "glow": blur px}: outline, optionally glowing
    {"type": "grid", "box", "color", "step": px, "width": px}: grid lines"""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for s in shapes:
        x, y, w, h = s["box"]
        x0, y0, x1, y1 = int(x * W), int(y * H), int((x + w) * W), int((y + h) * H)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if s.get("type") == "gradient":
            c0, c1 = rgba(s["from"]), rgba(s["to"])
            band = Image.new("RGBA", (1, max(y1 - y0, 1)))
            n = band.height
            for i in range(n):
                t = i / max(n - 1, 1)
                band.putpixel((0, i), tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(4)))
            layer.paste(band.resize((x1 - x0, n)), (x0, y0))
        elif s.get("type") == "frame":
            lw = int(s.get("width", 6))
            box = [x0, y0, x1 - 1, y1 - 1]
            if s.get("glow"):
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(g).rounded_rectangle(box, radius=s.get("radius", 0), outline=rgba(s["color"]),
                                                    width=lw * 3)
                g = g.filter(ImageFilter.GaussianBlur(s["glow"]))
                layer = Image.alpha_composite(layer, g)
                layer = Image.alpha_composite(layer, g)
            ImageDraw.Draw(layer).rounded_rectangle(box, radius=s.get("radius", 0), outline=rgba(s["color"]),
                                                    width=lw)
        elif s.get("type") == "grid":
            d = ImageDraw.Draw(layer)
            step, lw, c = int(s.get("step", 60)), int(s.get("width", 1)), rgba(s["color"])
            for gx in range(x0, x1, step):
                d.line([(gx, y0), (gx, y1)], fill=c, width=lw)
            for gy in range(y0, y1, step):
                d.line([(x0, gy), (x1, gy)], fill=c, width=lw)
        else:
            ImageDraw.Draw(layer).rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=s.get("radius", 0),
                                                    fill=rgba(s["color"]))
        canvas = Image.alpha_composite(canvas, layer)
    return canvas


def _preset(presets, t):
    if t.get("preset") not in presets:
        raise ValueError(f"Template không có kiểu chữ '{t.get('preset')}'. Có: {', '.join(presets)}")
    return {**presets[t["preset"]], **{k: v for k, v in t.items() if k not in ("preset", "text")}}


def _top_left(preset, tile, margin, W, H):
    tw, th = tile.size
    cx, cy = preset.get("x", 0.5) * W, preset.get("y", 0.5) * H
    ax = preset.get("anchor_x", "center")
    x = cx - margin if ax == "left" else cx - tw + margin if ax == "right" else cx - tw / 2
    ay = preset.get("anchor", "center")
    y = cy - margin if ay == "top" else cy - th + margin if ay == "bottom" else cy - th / 2
    return x, y


def layout(presets, t, W, H):
    """Where one text lands, for writers that draw text themselves (CapCut export):
    the merged preset, the wrapped lines and the block centre in pixels."""
    preset = _preset(presets, t)
    body = clock(float(preset["countdown"])) if preset.get("countdown") else t["text"]
    tile, margin, lines = _block(preset, body, W)
    x, y = _top_left(preset, tile, margin, W, H)
    return {"preset": preset, "lines": lines,
            "center": (x + tile.width / 2, y + tile.height / 2)}


def clock(seconds):
    """Countdown face: 75 -> "1:15"."""
    s = max(int(-(-seconds // 1)), 0)  # round up, so 0:00 shows only at the very end
    return f"{s // 60}:{s % 60:02d}"


def is_timed(preset):
    """Text that changes during the scene and needs a frame per step."""
    return bool(preset.get("typewriter") or preset.get("at") or preset.get("countdown"))


def render_layers(presets, texts, W, H, t_now=None):
    """texts: [{"preset": name, "text": "...", ...overrides}] -> RGBA canvas W x H.
    t_now = seconds into the scene; texts with "typewriter": chars per second show only what is typed by then,
    texts with "at": seconds stay hidden until then, "countdown": seconds replaces the text with a running clock."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for t in texts:
        if not t.get("text") and not t.get("countdown"):
            continue
        preset = _preset(presets, t)
        at = float(preset.get("at", 0))
        if t_now is not None and t_now < at:
            continue
        body = t.get("text", "")
        if preset.get("countdown"):
            left = float(preset["countdown"]) - (t_now - at if t_now is not None else 0)
            body = clock(left)
        reveal = None
        if preset.get("typewriter") and t_now is not None:
            reveal = max(t_now - at - float(preset.get("typewriter_delay", 0)), 0) * float(preset["typewriter"])
        tile, margin, _ = _block(preset, body, W, reveal)
        x, y = _top_left(preset, tile, margin, W, H)
        canvas = place(canvas, tile, int(round(x)), int(round(y)))
    return canvas
