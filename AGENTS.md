# meoedit

If the user asks you to edit a video or design an image with meoedit, read `skill/SKILL.md` and follow it. In that file `$MEO` means the `skill/` folder of this repository.

Working on meoedit itself: the engine is `skill/engine/` (Python 3.9+, Pillow, ffmpeg on PATH), templates are `skill/templates/<name>/{style.json,TEMPLATE.md}`. Run `tests/smoke.sh` after any change; it renders every template from synthetic media.

Claude Code plugin: `.claude-plugin/marketplace.json` (repo root) lists one plugin whose source is `./skill`; `skill/.claude-plugin/plugin.json` is its manifest. Bump `version` there and `__version__` in `skill/engine/meo/__init__.py` together on every release, or users stay on the old version. Check with `claude plugin validate ./skill && claude plugin validate .`.

Landing page: `site/` (one HTML file; `site/docs` links to `docs/`). Deploy to Cloudflare (Workers static assets, https://meoedit.gaupoit.workers.dev):

```bash
rsync -aL --delete --exclude .DS_Store site/ _site/ && npx wrangler deploy
```
