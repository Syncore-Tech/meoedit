# meoedit 🐱

**Biến agent AI thành editor riêng của bạn: dựng video dọc và thiết kế ảnh từ template, miễn phí, mã nguồn mở, chạy hoàn toàn trên máy bạn.**

Quay bằng điện thoại, đưa thư mục cho agent (Claude Code, Codex, Cursor, Gemini CLI...), chọn template. Agent xem clip, chọn cảnh đẹp, viết chữ, cho bạn xem bản nháp, chờ bạn duyệt rồi mới xuất video 1080x1920.

- **Miễn phí, MIT.** Không tài khoản, không đăng nhập, không trả phí theo template.
- **Riêng tư.** Ảnh, clip, giọng nói không rời khỏi máy bạn.
- **Tiếng Việt chuẩn.** Font có dấu đầy đủ (Be Vietnam Pro, Baloo 2, Dancing Script), câu hỏi và chữ mẫu bằng tiếng Việt.
- **Bạn duyệt trước.** Luôn có bản nháp + ảnh tổng quan từng cảnh trước khi xuất bản cuối.
- **Không cần Remotion hay dịch vụ ngoài.** Chỉ cần ffmpeg và Python.

## Template có sẵn

| Template | Loại | Dùng cho |
|---|---|---|
| `review-quan-cafe` | Video 9:16 | Review quán cà phê, tiệm bánh. Tông nâu kem, chữ mềm, mờ dần |
| `vlog-du-lich` | Video 9:16 | Vlog du lịch, recap chuyến đi. Cắt nhanh, chữ in hoa vàng |
| `the-san-pham` | Ảnh 4:5 | Ảnh bán hàng Facebook, Instagram, Threads, Shopee |

## Cài đặt

Cần: Python 3.9+, [ffmpeg](https://ffmpeg.org/download.html), Pillow.

```bash
# macOS
brew install ffmpeg
python3 -m pip install --user pillow

git clone https://github.com/Syncore-Tech/meoedit.git
cd meoedit
./install.sh
python3 skill/engine/cli.py doctor
```

`install.sh` cài skill vào `~/.claude/skills/meoedit` (Claude Code) và `~/.codex/skills/meoedit` (Codex) nếu có. Với Cursor, Gemini CLI hay agent khác: mở thư mục repo và bảo agent *"đọc skill/SKILL.md rồi làm theo"*.

## Dùng thế nào

Nói với agent:

> Dùng meoedit dựng video review quán cà phê từ thư mục ~/Movies/moc-chill. Nhạc ở ~/Music/lofi.mp3.

Agent sẽ:

1. Hỏi tên quán, món, giá, chấm điểm.
2. Xem nhanh từng clip (ảnh `thumbs.jpg`) để chọn đoạn đẹp.
3. Viết `plan.json`: cảnh nào, cắt từ giây mấy, chữ gì.
4. Xuất bản nháp 540x960 + ảnh tổng quan, rồi **dừng chờ bạn duyệt**.
5. Sửa theo ý bạn, xuất bản cuối 1080x1920, âm thanh chuẩn -14 LUFS.

Dùng tay không cần agent cũng được:

```bash
python3 skill/engine/cli.py templates
python3 skill/engine/cli.py thumbs clips/*.MOV -o thumbs.jpg
python3 skill/engine/cli.py video plan.json --preview
python3 skill/engine/cli.py video plan.json
python3 skill/engine/cli.py image card.json
```

Định dạng `plan.json` xem trong [skill/SKILL.md](skill/SKILL.md).

## Tự làm template

Một template là một thư mục trong `skill/templates/`:

- `style.json`: khung hình, màu chỉnh video (`grade`, bộ lọc ffmpeg), chuyển cảnh, và các kiểu chữ (`presets`: font, cỡ, màu, viền, hộp nền, vị trí, độ nghiêng).
- `TEMPLATE.md`: câu hỏi cho người dùng, cấu trúc cảnh, độ dài chữ. Agent đọc file này.

Sao chép một template có sẵn, đổi tên, sửa màu và chữ, chạy `tests/smoke.sh`. PR template mới rất được hoan nghênh: review quán ăn, outfit, unbox, bất động sản, ảnh quote...

## Lộ trình

- [ ] Giọng đọc AI tiếng Việt chạy trên máy (tuỳ chọn)
- [ ] Phụ đề tự động từ lời nói (Whisper chạy trên máy)
- [ ] Thêm template: review quán ăn, outfit, ảnh vuông 1:1, ảnh story 9:16
- [ ] Cắt theo nhịp nhạc tự động

## Giấy phép

Mã nguồn: [MIT](LICENSE). Font tải từ Google Fonts theo giấy phép SIL Open Font License. meoedit không kèm nhạc; bạn tự chịu trách nhiệm bản quyền nhạc và media đưa vào.

---

**English:** meoedit turns your AI coding agent into a video editor. Agent skills plus a small Python + ffmpeg engine that turn phone footage into vertical videos (TikTok, Reels, Shorts) and product images from templates, entirely on your machine. Vietnamese-first, MIT licensed, no account, no cloud.
