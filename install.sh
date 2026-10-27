#!/usr/bin/env bash
# Cài meoedit thành skill cho Claude Code và Codex.
#   ./install.sh          sao chép skill
#   ./install.sh --link   tạo symlink (cho người phát triển meoedit)
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skill"
MODE="${1:-copy}"
installed=0

put() {
  local dest="$1/meoedit"
  mkdir -p "$1"
  rm -rf "$dest"
  if [ "$MODE" = "--link" ]; then ln -s "$SRC" "$dest"; else cp -R "$SRC" "$dest"; fi
  echo "✓ $dest"
  installed=1
}

[ -d "$HOME/.claude" ] && put "$HOME/.claude/skills"
[ -d "$HOME/.codex" ] && put "$HOME/.codex/skills"
if [ "$installed" = 0 ]; then
  echo "Không thấy ~/.claude hay ~/.codex. Với agent khác, bảo agent đọc: $SRC/SKILL.md"
fi

command -v ffmpeg >/dev/null || echo "! Cần cài ffmpeg (macOS: brew install ffmpeg, Ubuntu: sudo apt install ffmpeg)"
python3 -c "import PIL" 2>/dev/null || echo "! Cần Pillow: python3 -m pip install --user pillow"
echo "Xong. Mở agent và nói: \"dùng meoedit dựng video review quán cà phê từ thư mục ~/Movies/cafe\""
