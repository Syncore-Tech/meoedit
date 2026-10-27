import json
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


def load(name):
    p = TEMPLATES_DIR / name / "style.json"
    if not p.exists():
        raise ValueError(f"Không có template '{name}'. Có: {', '.join(t['name'] for t in all_templates())}")
    return json.loads(p.read_text(encoding="utf-8"))


def all_templates():
    out = []
    for p in sorted(TEMPLATES_DIR.glob("*/style.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        out.append({
            "name": s["name"],
            "kind": s["kind"],
            "title": s["title"],
            "description": s.get("description", ""),
            "guide": str(p.parent / "TEMPLATE.md"),
            "text_styles": sorted(s["presets"]),
        })
    return out
