"""One anonymous ping per installed version, so we know roughly how many people use meoedit.

Sends only the version, the OS family and the command name to https://meoedit.com/ping, once per
version (a marker file in ~/.meoedit remembers it). No file names, no content, no id. The server
keeps a daily count per version, OS and country and never stores the IP.
Turn it off with MEOEDIT_NO_PING=1 or DO_NOT_TRACK=1.
"""

import os
import sys
import urllib.parse
import urllib.request

from . import __version__
from .fonts import HOME

URL = "https://meoedit.com/ping"


def disabled():
    return any(os.environ.get(k, "") not in ("", "0") for k in ("MEOEDIT_NO_PING", "DO_NOT_TRACK"))


def once(cmd):
    if disabled():
        return
    marker = HOME / f"pinged-{__version__}"
    try:
        if marker.exists():
            return
        HOME.mkdir(parents=True, exist_ok=True)
        marker.touch()
        osname = {"darwin": "mac", "win32": "windows"}.get(sys.platform, "linux" if sys.platform.startswith("linux") else "other")
        q = urllib.parse.urlencode({"v": __version__, "os": osname, "cmd": cmd})
        req = urllib.request.Request(f"{URL}?{q}", headers={"User-Agent": f"meoedit/{__version__}"})
        urllib.request.urlopen(req, timeout=2).close()
    except Exception:  # offline, firewall, read-only home: never get in the way
        pass
