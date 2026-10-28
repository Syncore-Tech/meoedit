"""Font registry. Fonts are Google Fonts (SIL Open Font License), downloaded on first use."""

import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from PIL import ImageFont

HOME = Path(os.environ.get("MEOEDIT_HOME", Path.home() / ".meoedit"))
FONT_DIR = HOME / "fonts"
BASE_URL = "https://github.com/google/fonts/raw/main/ofl/"

# name -> path inside github.com/google/fonts/ofl. Every font here covers Vietnamese.
FONTS = {
    "BeVietnamPro-Medium": "bevietnampro/BeVietnamPro-Medium.ttf",
    "BeVietnamPro-SemiBold": "bevietnampro/BeVietnamPro-SemiBold.ttf",
    "BeVietnamPro-Bold": "bevietnampro/BeVietnamPro-Bold.ttf",
    "BeVietnamPro-ExtraBold": "bevietnampro/BeVietnamPro-ExtraBold.ttf",
    "BeVietnamPro-Black": "bevietnampro/BeVietnamPro-Black.ttf",
    "DancingScript": "dancingscript/DancingScript%5Bwght%5D.ttf",
    "Baloo2": "baloo2/Baloo2%5Bwght%5D.ttf",
    "PlayfairDisplay": "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "PlayfairDisplay-Italic": "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf",
    "Oswald": "oswald/Oswald%5Bwght%5D.ttf",
    "Lobster": "lobster/Lobster-Regular.ttf",
}


def _download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=dest.name, suffix=".part")
    os.close(fd)
    try:
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
        except Exception:
            # Some Python builds lack CA certificates; curl usually has them.
            subprocess.run(["curl", "-fsSL", "-o", tmp, url], check=True)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def path(name):
    """Return a local path for a registered font name, or a font file path given directly."""
    if name not in FONTS:
        p = Path(name).expanduser()
        if p.is_file():
            return p
        raise ValueError(f"Không có font '{name}'. Font có sẵn: {', '.join(FONTS)}")
    dest = FONT_DIR / (name + ".ttf")
    if not dest.exists():
        _download(BASE_URL + FONTS[name], dest)
    return dest


def load(name, size, variation=None):
    font = ImageFont.truetype(str(path(name)), int(size))
    if variation:
        font.set_variation_by_name(variation)
    return font


def fetch_all():
    return [path(n) for n in FONTS]
