"""Write a plan as a CapCut draft, so the user can keep editing in CapCut.

The draft format is CapCut's own JSON (draft_content.json). Field shapes follow drafts that CapCut 9.5 opened
and re-saved; pyJianYingDraft (Apache 2.0) documents the same format for Jianying.
What maps 1:1: clips and their cut points, images, colour scenes, split panels, texts with their template
font, size, colour, box and position, plan-level texts, SRT subtitles, music, volume, speed, zoom.
Mapped to CapCut's own effects (ids in TRANSITIONS / TEXT_INTROS / RECT_MASK): transitions between scenes,
typewriter and fade-in on scene texts, rounded panel corners (rectangle mask).
What does not (yet): colour grade. Shapes from the template (frames, gradients, glow) come over as
transparent PNG layers.
"""

import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from PIL import Image

from . import fonts, media, subtitles, templates, text

US = 1_000_000  # CapCut times are microseconds
PLATFORM = {"app_id": 359289, "app_source": "cc", "app_version": "6.7.0", "os": "windows"}
MATERIAL_KINDS = [
    "ai_translates", "audio_balances", "audio_effects", "audio_fades", "audio_track_indexes", "audios", "beats",
    "canvases", "chromas", "common_mask", "color_curves", "digital_humans", "drafts", "effects", "flowers",
    "green_screens", "handwrites", "hsl", "images", "log_color_wheels", "loudnesses", "manual_deformations", "masks",
    "material_animations", "material_colors", "multi_language_refs", "placeholders", "plugin_effects",
    "primary_color_wheels", "realtime_denoises", "shapes", "smart_crops", "smart_relights",
    "sound_channel_mappings", "speeds", "stickers", "tail_leaders", "text_templates", "texts", "time_marks",
    "transitions", "video_effects", "video_trackings", "videos", "vocal_beautifys", "vocal_separations"]

# CapCut effects are referenced by resource id (effect_id is the same number). Names and ids read from a
# sample draft that pyCapCut 0.0.4 wrote (its names are the Jianying ones); only what meoedit needs.
# ffmpeg xfade name -> (CapCut name, id). Anything else falls back to "fade".
TRANSITIONS = {
    "fade": ("叠化", "6724845717472416269"),
    "fadeblack": ("闪黑", "6724239388189921806"),
    "fadewhite": ("闪白", "6724845376098013708"),
    "slideleft": ("向左", "6724227717195108867"),
    "slideright": ("向右", "6724227599616184836"),
    "slideup": ("向上", "6724227090872275463"),
    "slidedown": ("向下", "6724227330190873100"),
    "wipeleft": ("向左擦除", "6724849999336706573"),
    "wiperight": ("向右擦除", "6724849898857959950"),
    "wipeup": ("向上擦除", "6724849456891564557"),
    "wipedown": ("向下擦除", "6724849752921346573"),
    "circleopen": ("圆形遮罩", "6725767129519362573"),
    "zoomin": ("推近", "6724226861666144779"),
}
for _a, _b in (("dissolve", "fade"), ("fadefast", "fade"), ("fadeslow", "fade"), ("smoothleft", "slideleft"),
               ("smoothright", "slideright"), ("smoothup", "slideup"), ("smoothdown", "slidedown"),
               ("circleclose", "circleopen"), ("circlecrop", "circleopen")):
    TRANSITIONS[_a] = TRANSITIONS[_b]
TEXT_INTROS = {"typewriter": ("打字机", "7210980292243231233"), "fade": ("渐显", "6724916044072227332")}
RECT_MASK = ("矩形", "6791700809454195207")


def default_drafts_dir():
    if sys.platform == "darwin":
        return Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut/User Data/Projects/com.lveditor.draft"
    return Path.home() / "CapCut Drafts"


def _id():
    return uuid.uuid4().hex


def _us(seconds):
    return int(round(float(seconds) * US))


def _rgb(color):
    r, g, b, _ = text.rgba(color)
    return [r / 255, g / 255, b / 255]


def _alpha(color):
    return text.rgba(color)[3] / 255


class Draft:
    def __init__(self, folder, W, H, fps):
        self.folder, self.W, self.H, self.fps = folder, W, H, fps
        self.materials = {k: [] for k in MATERIAL_KINDS}
        self.tracks = []  # [{"type", "name", "segments"}]
        self.copied = {}  # source path -> path inside the draft
        # CapCut text size 1 is about 5.6 px on a 1080 px short side (measured on CapCut 9.5).
        self.px_per_size = 5.6 * min(W, H) / 1080

    # --- files: CapCut on macOS is sandboxed to ~/Movies, so everything it reads lives inside the draft.
    def copy_in(self, src, sub="media"):
        src = Path(src).resolve()
        if src in self.copied:
            return self.copied[src]
        d = self.folder / sub
        d.mkdir(parents=True, exist_ok=True)
        dst = d / src.name
        n = 1
        while dst.exists():
            n += 1
            dst = d / f"{src.stem}-{n}{src.suffix}"
        shutil.copy2(src, dst)
        self.copied[src] = dst
        return dst

    def png(self, im, name):
        d = self.folder / "media"
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        im.save(p)
        return p

    # --- tracks: one segment per time slot; a new track opens when segments would overlap.
    def place(self, kind, seg, layer=None):
        start, dur = seg["target_timerange"]["start"], seg["target_timerange"]["duration"]
        for tr in self.tracks:
            if tr["type"] != kind or (layer is not None and tr.get("layer") != layer):
                continue
            if all(start >= s["target_timerange"]["start"] + s["target_timerange"]["duration"]
                   or start + dur <= s["target_timerange"]["start"] for s in tr["segments"]):
                tr["segments"].append(seg)
                return
        n = sum(1 for t in self.tracks if t["type"] == kind)
        self.tracks.append({"type": kind, "name": f"{kind}{n}", "layer": layer, "segments": [seg]})

    # --- segments
    def _seg(self, material_id, start, dur, *, source=None, speed=1.0, volume=1.0, clip=None, refs=(),
             keyframes=None, render_index=0):
        seg = {
            "enable_adjust": True, "enable_color_correct_adjust": False, "enable_color_curves": True,
            "enable_color_match_adjust": False, "enable_color_wheels": True, "enable_lut": True,
            "enable_smart_color_adjust": False, "last_nonzero_volume": 1.0, "reverse": False,
            "track_attribute": 0, "track_render_index": 0, "visible": True,
            "id": _id(), "material_id": material_id,
            # end - start in microseconds, so clips that touch in seconds also touch after rounding
            "target_timerange": {"start": _us(start), "duration": _us(start + dur) - _us(start)},
            "common_keyframes": keyframes or [], "keyframe_refs": [],
            "source_timerange": source, "speed": speed, "volume": volume,
            "extra_material_refs": list(refs), "is_tone_modify": False,
            "clip": None, "hdr_settings": None, "render_index": render_index,
        }
        if clip is not None:
            seg["clip"] = {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
                           "rotation": clip.get("rotation", 0.0),
                           "scale": {"x": clip.get("scale", 1.0), "y": clip.get("scale", 1.0)},
                           "transform": {"x": clip.get("x", 0.0), "y": clip.get("y", 0.0)}}
            seg["uniform_scale"] = {"on": True, "value": 1.0}
        return seg

    def _speed(self, speed):
        m = {"curve_speed": None, "id": _id(), "mode": 0, "speed": speed, "type": "speed"}
        self.materials["speeds"].append(m)
        return m["id"]

    def visual(self, path, start, dur, *, src_start=0.0, speed=1.0, volume=0.0, box=None, zoom=None,
               pan=None, layer=0, radius=0, transition=None):
        """A video or image on the timeline, filling `box` ([x, y, w, h] fractions, default the frame)
        the way ffmpeg's cover crop does. radius = rounded corners in template px (rectangle mask);
        transition = (xfade name, seconds) into the next clip on the same track."""
        path = self.copy_in(path) if not str(path).startswith(str(self.folder)) else Path(path)
        info = media.probe(path)
        is_photo = info["type"] == "image"
        vw, vh = info["width"], info["height"]
        bx, by, bw, bh = box or (0, 0, 1, 1)
        tw, th = bw * self.W, bh * self.H
        # Crop the source to the box's aspect (centred), so scale 1 = exactly the box.
        if vw / vh > tw / th:
            cw, ch = vh * tw / th, vh
        else:
            cw, ch = vw, vw * th / tw
        cx0, cy0 = (vw - cw) / 2 / vw, (vh - ch) / 2 / vh
        cx1, cy1 = 1 - cx0, 1 - cy0
        mat = {
            "audio_fade": None, "category_id": "", "category_name": "local", "check_flag": 63487,
            "crop": {"upper_left_x": cx0, "upper_left_y": cy0, "upper_right_x": cx1, "upper_right_y": cy0,
                     "lower_left_x": cx0, "lower_left_y": cy1, "lower_right_x": cx1, "lower_right_y": cy1},
            "crop_ratio": "free", "crop_scale": 1.0,
            "duration": _us(10800) if is_photo else _us(info["duration"]),
            "height": vh, "id": _id(), "local_material_id": "", "material_id": "",
            "material_name": path.name, "media_path": "", "path": str(path),
            "type": "photo" if is_photo else "video", "width": vw,
        }
        mat["material_id"] = mat["id"]
        self.materials["videos"].append(mat)
        # CapCut fits the (cropped) picture inside the frame; scale it to the box.
        fit = min(self.W / cw, self.H / ch)
        scale = tw / (cw * fit)
        x, y = (bx + bw / 2) * 2 - 1, 1 - (by + bh / 2) * 2
        kfs = []
        if zoom:
            a, b = (float(v) for v in zoom)
            kfs.append(_keyframes("KFTypeScaleX", dur, scale * a, scale * b))
            scale *= a
        elif pan:
            # Images drift sideways inside a 12% larger frame, like the MP4 render.
            scale *= 1.12
            shift = 0.12 * bw
            a, b = (shift, -shift) if pan == "pan" else (-shift, shift)
            kfs.append(_keyframes("KFTypePositionX", dur, x + a, x + b))
        source = None if is_photo else {"start": _us(src_start), "duration": _us(dur * speed)}
        refs = [self._speed(speed)]
        if radius:
            refs.append(self._mask(radius / (min(tw, th) / 2)))
        seg = self._seg(mat["id"], start, dur, source=source, speed=speed, volume=volume,
                        clip={"scale": scale, "x": x, "y": y}, refs=refs, keyframes=kfs,
                        render_index=layer)
        if transition:
            seg["_transition"] = transition  # becomes a material in save(), if the next clip is adjacent
        self.place("video", seg, layer)

    def _mask(self, corner):
        """Rectangle mask over the whole (cropped) picture; corner = radius / half the shorter side."""
        name, rid = RECT_MASK
        config = {"aspectRatio": 1.0, "centerX": 0.0, "centerY": 0.0, "feather": 0.0, "height": 1.0,
                  "invert": False, "rotation": 0.0, "roundCorner": min(corner, 1.0), "width": 1.0}
        m = {"config": config, "id": _id(), "name": name, "platform": "all", "position_info": "",
             "resource_type": "rectangle", "resource_id": rid, "type": "mask"}
        self.materials["masks"].append(m)
        # Newer CapCut keeps the same mask (same id) in common_mask too.
        self.materials["common_mask"].append({**m, "config": {**config, "expansion": 0.0}, "category": "video",
                                              "category_id": "", "category_name": "", "panel": "",
                                              "source_platform": 0})
        return m["id"]

    def _transition(self, kind, seconds):
        name, rid = TRANSITIONS.get(kind, TRANSITIONS["fade"])
        m = {"category_id": "", "category_name": "", "duration": _us(seconds), "effect_id": rid, "id": _id(),
             "is_overlap": True, "name": name, "platform": "all", "resource_id": rid, "type": "transition"}
        self.materials["transitions"].append(m)
        return m["id"]

    def _intro(self, kind, seconds):
        """Text intro animation (typewriter / fade-in), from the start of the text segment."""
        name, rid = TEXT_INTROS[kind]
        m = {"id": _id(), "type": "sticker_animation", "multi_language_current": "none",
             "animations": [{"anim_adjust_params": None, "platform": "all", "panel": "", "material_type": "sticker",
                             "name": name, "id": rid, "type": "in", "resource_id": rid, "start": 0,
                             "duration": _us(seconds)}]}
        self.materials["material_animations"].append(m)
        return m["id"]

    def image_layer(self, im, name, start, dur, layer):
        """A full-frame transparent PNG (template shapes) on its own video track above the clips."""
        p = self.png(im, name)
        self.visual(p, start, dur, layer=layer)

    def text(self, presets, t, start, dur, fade_in=None):
        """fade_in = None: no intro (plan texts, subtitles), like the MP4. Otherwise a "typewriter" preset
        types in at its chars per second, any other text fades in over fade_in seconds (0 = none)."""
        lay = text.layout(presets, t, self.W, self.H)
        p = lay["preset"]
        body = "\n".join(lay["lines"])
        size = p.get("size", 64) / self.px_per_size
        font = p.get("font", "BeVietnamPro-Bold")
        font_path = str(self.copy_in(fonts.path(font), "fonts"))
        style = {
            "fill": {"alpha": 1.0, "content": {"render_type": "solid",
                                               "solid": {"alpha": 1.0, "color": _rgb(p.get("color", "#FFFFFF"))}}},
            "range": [0, len(body)], "size": size, "bold": False, "italic": False, "underline": False,
            "strokes": [], "font": {"id": "", "path": font_path},
        }
        flag = 7
        stroke = p.get("stroke") or {}
        if stroke.get("width"):
            # CapCut stroke width is relative to the glyph size.
            style["strokes"] = [{"content": {"solid": {"alpha": 1.0, "color": _rgb(stroke.get("color", "#000000"))}},
                                 "width": min(float(stroke["width"]) / p.get("size", 64) * 0.6, 0.2)}]
            flag |= 8
        shadow = p.get("shadow")
        if shadow:
            ox, oy = shadow.get("offset", [0, 6])
            style["shadows"] = [{"diffuse": min(shadow.get("blur", 10) / 100 / 6, 1 / 6),
                                 "alpha": _alpha(shadow.get("color", "#00000099")),
                                 "distance": min((ox ** 2 + oy ** 2) ** 0.5, 100),
                                 "content": {"solid": {"color": _rgb(shadow.get("color", "#000000"))}},
                                 "angle": -90.0}]
            flag |= 32
        mat = {
            "id": _id(), "content": json.dumps({"styles": [style], "text": body}, ensure_ascii=False),
            "typesetting": 0, "alignment": {"left": 0, "right": 2}.get(p.get("align"), 1),
            "letter_spacing": 0.0, "line_spacing": 0.02 + (float(p.get("line_spacing", 1.12)) - 1.12) * 0.5,
            "line_feed": 1, "line_max_width": float(p.get("max_width", 0.86)),
            "force_apply_line_max_width": False, "type": "text", "global_alpha": 1.0,
            "font_path": font_path, "font_name": font,
        }
        box = p.get("box")
        if box:
            pad_y, pad_x = box.get("pad", [16, 28])
            fs = p.get("size", 64)
            mat.update({"background_style": 1, "background_color": box["color"][:7],
                        "background_alpha": _alpha(box["color"]),
                        "background_round_radius": min(box.get("radius", 24) / fs, 1.0),
                        "background_height": pad_y / fs, "background_width": pad_x / fs,
                        "background_horizontal_offset": 0.0, "background_vertical_offset": 0.0})
            flag |= 16
        mat["check_flag"] = flag
        self.materials["texts"].append(mat)
        refs = []
        if fade_in is not None and p.get("typewriter"):
            # Nothing shows before typewriter_delay, then the whole text types in.
            delay = min(float(p.get("typewriter_delay", 0)), dur * 0.5)
            start, dur = start + delay, dur - delay
            refs.append(self._intro("typewriter", min(len(t["text"]) / float(p["typewriter"]), dur)))
        elif fade_in:
            refs.append(self._intro("fade", min(fade_in, dur)))
        cx, cy = lay["center"]
        seg = self._seg(mat["id"], start, dur, clip={"x": cx / self.W * 2 - 1, "y": 1 - cy / self.H * 2,
                                                       "rotation": -float(p.get("rotate", 0))},
                        refs=refs, render_index=15000)
        self.place("text", seg)

    def audio(self, path, start, dur, volume):
        path = self.copy_in(path)
        info = media.probe(path)
        mat = {"app_id": 0, "category_id": "", "category_name": "local", "check_flag": 3,
               "copyright_limit_type": "none", "duration": _us(info["duration"]), "effect_id": "", "formula_id": "",
               "id": _id(), "local_material_id": "", "music_id": "", "name": path.name, "path": str(path),
               "source_platform": 0, "type": "extract_music", "wave_points": []}
        self.materials["audios"].append(mat)
        # Music shorter than the video loops, one segment per pass.
        mlen, t = float(info["duration"]), 0.0
        while t < dur - 0.01:
            d = min(mlen, dur - t)
            seg = self._seg(mat["id"], start + t, d, source={"start": 0, "duration": _us(d)}, volume=volume,
                            refs=[self._speed(1.0)])
            self.place("audio", seg)
            t += d

    def save(self, duration):
        order = {"video": 0, "audio": 1, "text": 2}
        for tr in self.tracks:
            segs = sorted(tr["segments"], key=lambda s: s["target_timerange"]["start"])
            for a, b in zip(segs, segs[1:] + [None]):
                tran = a.pop("_transition", None)
                # A transition sits on the clip before the cut; only between two clips that touch.
                if tran and b and a["target_timerange"]["start"] + a["target_timerange"]["duration"] \
                        == b["target_timerange"]["start"]:
                    a["extra_material_refs"].append(self._transition(*tran))
        tracks = []
        for tr in sorted(self.tracks, key=lambda t: (order[t["type"]], t.get("layer") or 0)):
            tracks.append({"attribute": 0, "flag": 0, "id": _id(), "is_default_name": False,
                           "name": tr["name"], "type": tr["type"],
                           "segments": sorted(tr["segments"], key=lambda s: s["target_timerange"]["start"])})
        now = int(time.time())
        content = {
            "canvas_config": {"width": self.W, "height": self.H, "ratio": "original"},
            "color_space": 0,
            "config": {"adjust_max_index": 1, "attachment_info": [], "combination_max_index": 1,
                       "export_range": None, "extract_audio_last_index": 1, "lyrics_recognition_id": "",
                       "lyrics_sync": True, "lyrics_taskinfo": [], "maintrack_adsorb": True,
                       "material_save_mode": 0, "multi_language_current": "none", "multi_language_list": [],
                       "multi_language_main": "none", "multi_language_mode": "none",
                       "original_sound_last_index": 1, "record_audio_last_index": 1, "sticker_max_index": 1,
                       "subtitle_keywords_config": None, "subtitle_recognition_id": "", "subtitle_sync": True,
                       "subtitle_taskinfo": [], "system_font_list": [], "use_float_render": False,
                       "video_mute": False, "zoom_info_params": None},
            "cover": None, "create_time": 0, "duration": _us(duration), "extra_info": None, "fps": self.fps,
            "free_render_index_mode_on": False, "group_container": None, "id": str(uuid.uuid4()).upper(),
            "is_drop_frame_timecode": False, "keyframe_graph_list": [],
            "keyframes": {k: [] for k in ("adjusts", "audios", "effects", "filters", "handwrites", "stickers",
                                          "texts", "videos")},
            "last_modified_platform": PLATFORM, "lyrics_effects": [], "materials": self.materials,
            "mutable_config": None, "name": "", "new_version": "140.0.0", "path": "", "platform": PLATFORM,
            "relationships": [], "render_index_track_mode_on": False, "retouch_cover": None, "source": "default",
            "static_cover_image_path": "", "time_marks": None, "tracks": tracks, "update_time": 0,
            "version": 360000,
        }
        raw = json.dumps(content, ensure_ascii=False)
        # CapCut for Windows reads draft_content.json, CapCut for macOS draft_info.json.
        for name in ("draft_content.json", "draft_info.json"):
            (self.folder / name).write_text(raw, encoding="utf-8")
        meta = {
            "draft_cover": "", "draft_fold_path": str(self.folder), "draft_id": str(uuid.uuid4()).upper(),
            "draft_is_invisible": False,
            "draft_materials": [{"type": k, "value": []} for k in (0, 1, 2, 3, 6, 7, 8)],
            "draft_name": self.folder.name, "draft_root_path": str(self.folder.parent),
            "draft_timeline_materials_size_": 0, "tm_draft_create": now * US, "tm_draft_modified": now * US,
            "tm_duration": _us(duration),
        }
        (self.folder / "draft_meta_info.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")


def _keyframes(prop, dur, a, b):
    def kf(t, v):
        return {"curveType": "Line", "graphID": "", "left_control": {"x": 0.0, "y": 0.0},
                "right_control": {"x": 0.0, "y": 0.0}, "id": _id(), "time_offset": _us(t), "values": [v]}
    return {"id": _id(), "keyframe_list": [kf(0, a), kf(dur, b)], "material_id": "", "property_type": prop}


def _resolve(base, src):
    p = Path(src).expanduser()
    p = p if p.is_absolute() else base / p
    if not p.exists():
        raise FileNotFoundError(f"Không thấy file: {p}")
    return p


def export(plan_path, name=None, drafts_dir=None):
    plan_path = Path(plan_path).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    style = templates.load(plan["template"])
    if style["kind"] != "video":
        raise ValueError(f"Template '{plan['template']}' là template ảnh, CapCut chỉ nhận video.")
    scenes = plan["scenes"]
    if not scenes:
        raise ValueError("Plan chưa có cảnh nào.")
    W, H = style["size"]
    presets = style["presets"]

    root = Path(drafts_dir).expanduser() if drafts_dir else default_drafts_dir()
    if not root.exists():
        raise FileNotFoundError(f"Không thấy thư mục draft của CapCut: {root}. Mở CapCut một lần, "
                                "hoặc chỉ thư mục bằng --drafts.")
    name = name or Path(plan.get("output", "meoedit")).stem
    folder = root / name
    n = 1
    while folder.exists():  # never overwrite a draft the user may have edited
        n += 1
        folder = root / f"{name}-{n}"
    folder.mkdir(parents=True)

    try:
        d = Draft(folder, W, H, int(style.get("fps", 30)))
        # Same overlap as the MP4 (video.render): scene k starts x seconds before scene k-1 ends, so the
        # total length, and with it the subtitle timing, match. CapCut draws a transition across the cut,
        # so each cut sits in the middle of the MP4's xfade and every scene loses x/2 at each joined side.
        trans = {**style.get("transition", {}), **plan.get("transition", {})}
        durs = [float(sc["duration"]) for sc in scenes]
        n = len(scenes)
        x = 0.0 if trans.get("type", "fade") == "cut" or n == 1 else \
            min(float(trans.get("duration", 0.3)), min(durs) / 2.5)
        cuts = [0.0] + [sum(durs[:k]) - k * x + x / 2 for k in range(1, n)] + [sum(durs) - (n - 1) * x]
        fade_in = float(style.get("text_fade_in", 0.25))
        for i, sc in enumerate(scenes):
            t, dur = cuts[i], cuts[i + 1] - cuts[i]
            speed = float(sc.get("speed", 1))
            lead = (x / 2 if i else 0.0) * speed  # source seconds hidden under the incoming transition
            # Transition into the next scene, on the main track (layer 0) only.
            kind = scenes[i + 1].get("transition", trans.get("type", "fade")) if x and i < n - 1 else "cut"
            tran = None if kind == "cut" else (kind, x)
            vol = float(sc.get("volume", plan.get("original_volume", style.get("original_volume", 0))))
            shapes = sc.get("shapes", style.get("shapes", []))
            srcs = sc.get("srcs")
            if srcs:
                panels = style.get("panels") or []
                if len(srcs) > len(panels):
                    raise ValueError(f"Template '{plan['template']}' có {len(panels)} khung, "
                                     f"cảnh {i + 1} có {len(srcs)} nguồn.")
                bg = Image.new("RGBA", (W, H), text.rgba(style.get("background", "#000000")))
                bg = Image.alpha_composite(bg, text.render_shapes([s for s in shapes if s.get("back")], W, H))
                d.visual(d.png(bg.convert("RGB"), f"bg{i:02d}.png"), t, dur, layer=0, transition=tran)
                starts = list(sc.get("starts", [])) + [sc.get("start", 0)] * len(srcs)
                pick = int(sc.get("audio_panel", len(srcs) - 1))
                for j, (src, panel) in enumerate(zip(srcs, panels)):
                    d.visual(_resolve(base, src), t, dur, src_start=float(starts[j]) + lead, speed=speed,
                             volume=vol if j == pick else 0.0, box=panel["box"], zoom=sc.get("zoom"),
                             layer=1 + j, radius=panel.get("radius", 0))
            else:
                src = sc["src"]
                if src.startswith("color:"):
                    p = d.png(Image.new("RGB", (W, H), text.rgba(src.split(":", 1)[1])[:3]), f"color{i:02d}.png")
                    d.visual(p, t, dur, layer=0, transition=tran)
                else:
                    p = _resolve(base, src)
                    pan = None
                    if media.is_image(p) and not sc.get("zoom"):
                        motion = sc.get("motion", style.get("image_motion", "pan"))
                        pan = None if motion == "none" else motion
                    d.visual(p, t, dur, src_start=float(sc.get("start", 0)) + lead, speed=speed, volume=vol,
                             zoom=sc.get("zoom"), pan=pan, layer=0, transition=tran)
            front = [s for s in shapes if not s.get("back")]
            if front:
                d.image_layer(text.render_shapes(front, W, H), f"shapes{i:02d}.png", t, dur, layer=10)
            for tx in sc.get("texts", []):
                p = {**presets.get(tx.get("preset"), {}), **tx}
                at = min(float(p.get("at", 0)), dur - 0.1)
                if p.get("countdown"):
                    # CapCut has no running clock: one text per second, each showing that second's face.
                    total_s, k = float(p["countdown"]), 0
                    while k < total_s and at + k < dur:
                        d.text(presets, {**tx, "countdown": 0, "at": 0, "text": text.clock(total_s - k)},
                               t + at + k, min(1.0, dur - at - k))
                        k += 1
                    if at + k < dur:  # the MP4 holds 0:00 until the scene ends
                        d.text(presets, {**tx, "countdown": 0, "at": 0, "text": text.clock(0)},
                               t + at + k, dur - at - k)
                elif tx.get("text"):
                    d.text(presets, {**tx, "at": 0}, t + at, dur - at, fade_in)
        total = cuts[-1]

        for tx in plan.get("texts", []):
            if tx.get("text"):
                d.text(presets, tx, 0, total)
        cues, sub_style = subtitles.load(plan, base)
        for cue in cues:
            if cue["start"] < total:
                d.text(presets, {**sub_style, "text": cue["text"]}, cue["start"],
                       min(cue["end"], total) - cue["start"])
        if plan.get("music"):
            d.audio(_resolve(base, plan["music"]), 0, total,
                    float(plan.get("music_volume", style.get("music_volume", 0.3))))
        d.save(total)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return {"draft": folder.name, "folder": str(folder), "duration": round(total, 2), "scenes": len(scenes),
            "note": "Mở CapCut (thoát hẳn rồi mở lại nếu đang chạy), chọn project này. "
                    "Chỉnh màu chưa sang được, thêm trong CapCut nếu cần."}
