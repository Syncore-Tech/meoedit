"""SRT subtitles: parse a file into cues on the final video timeline."""

import re
from pathlib import Path

_TIME = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})")


def _seconds(stamp):
    m = _TIME.fullmatch(stamp.strip())
    if not m:
        raise ValueError(f"Mốc thời gian SRT sai: '{stamp}' (cần dạng 00:00:01,500)")
    h, mi, s, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def parse(path):
    """-> [{"start": s, "end": s, "text": "..."}], sorted by start. Blocks without a time line are skipped."""
    raw = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = block.strip().split("\n")
        i = next((k for k, l in enumerate(lines) if "-->" in l), None)
        if i is None:
            continue
        a, b = lines[i].split("-->")
        text = "\n".join(l.strip() for l in lines[i + 1:] if l.strip())
        start, end = _seconds(a), _seconds(b.split()[0])
        if text and end > start:
            cues.append({"start": start, "end": end, "text": text})
    return sorted(cues, key=lambda c: c["start"])


def load(plan, base):
    """Plan field "subtitles": {"file": "x.srt", "preset": "caption", "y": 0.6} (or just the file name).
    -> (cues, text style: {"preset": name, ...overrides}) or ([], None)."""
    sub = plan.get("subtitles")
    if not sub:
        return [], None
    if isinstance(sub, str):
        sub = {"file": sub}
    p = Path(sub["file"]).expanduser()
    p = p if p.is_absolute() else base / p
    if not p.exists():
        raise FileNotFoundError(f"Không thấy file phụ đề: {p}")
    style = {k: v for k, v in sub.items() if k != "file"}
    style.setdefault("preset", "caption")
    return parse(p), style
