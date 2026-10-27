"""Render a designed image (post, product card) from a plan.json and an image template."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import templates, text


def _box(b, W, H):
    x, y, w, h = b
    return [int(x * W), int(y * H), int((x + w) * W), int((y + h) * H)]


def render(plan_path):
    plan_path = Path(plan_path).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    style = templates.load(plan["template"])
    if style["kind"] != "image":
        raise ValueError(f"Template '{plan['template']}' là template video, dùng lệnh 'video'.")

    W, H = style["size"]
    canvas = Image.new("RGBA", (W, H), text.rgba(plan.get("background", style.get("background", "#FFFFFF"))))
    d = ImageDraw.Draw(canvas)
    for s in style.get("shapes", []):
        d.rounded_rectangle(_box(s["box"], W, H), radius=s.get("radius", 0), fill=text.rgba(s["color"]))

    photos = plan.get("photos") or ([plan["photo"]] if plan.get("photo") else [])
    for slot, src in zip(style.get("photo_slots", []), photos):
        p = Path(src).expanduser()
        p = p if p.is_absolute() else base / p
        x0, y0, x1, y1 = _box(slot["box"], W, H)
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im).convert("RGBA")
            ph = ImageOps.fit(im, (x1 - x0, y1 - y0), Image.LANCZOS,
                              centering=tuple(slot.get("focus", plan.get("focus", [0.5, 0.5]))))
        mask = Image.new("L", ph.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1],
                                               radius=slot.get("radius", 0), fill=255)
        canvas.paste(ph, (x0, y0), mask)

    canvas = Image.alpha_composite(canvas, text.render_layers(style["presets"], plan.get("texts", []), W, H))

    out = Path(plan.get("output", "meoedit-image.png")).expanduser()
    out = out if out.is_absolute() else base / out
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in {".jpg", ".jpeg"}:
        canvas.convert("RGB").save(out, quality=92)
    else:
        canvas.save(out)
    return {"output": str(out), "size": f"{W}x{H}"}
