# meoedit

If the user asks you to edit a video or design an image with meoedit, read `skill/SKILL.md` and follow it. In that file `$MEO` means the `skill/` folder of this repository.

Working on meoedit itself: the engine is `skill/engine/` (Python 3.9+, Pillow, ffmpeg on PATH), templates are `skill/templates/<name>/{style.json,TEMPLATE.md}`. Run `tests/smoke.sh` after any change; it renders every template from synthetic media.
