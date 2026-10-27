# Vlog du lịch — Nhật ký đi

Video dọc 15–40 giây. Cắt thẳng theo nhịp nhanh (1.2–2 giây mỗi cảnh), chữ in hoa vàng viền đen, phụ đề nền đen từng dòng. Màu video tươi hơn một chút.

## Hỏi người dùng (gộp một tin)

1. Đi đâu, mấy ngày, đi với ai.
2. Tổng chi phí (nếu muốn khoe), hoặc một con số ấn tượng.
3. 3–5 khoảnh khắc nhớ nhất, mỗi cái một câu (ăn gì, ở đâu, làm gì, mấy giờ).
4. Muốn một video cho cả chuyến hay mỗi ngày một video.
5. Thư mục chứa ảnh/clip. Có nhạc nền không (nhạc nhanh hợp hơn).

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Mở | 1.5–2s | cảnh rộng, đẹp nhất của chuyến | `ngay` + `dia-diem` + `phu` |
| 2…n-1 | Khoảnh khắc | 1.2–2s mỗi cảnh | mỗi khoảnh khắc 1–2 cảnh | `tag` (giờ hoặc tên chỗ) + `caption` |
| n | Kết | 1.5–2s | cảnh đi xa, hoàng hôn, vẫy tay | `caption` ("Hẹn gặp lại…") |

Tổng 10–20 cảnh. Clip đi đường dài: dùng `"speed": 2` hoặc `3` để tua.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `ngay` | "Ngày 1", "Cuối tuần", in hoa vàng, nghiêng | ≤ 3 từ |
| `dia-diem` | tên nơi đến rất to giữa màn hình | ≤ 2 từ |
| `phu` | dòng phụ dưới tên nơi, nền vàng | ≤ 8 từ |
| `tag` | giờ hoặc tên chỗ, góc trên trái | ≤ 4 từ |
| `caption` | phụ đề nền đen từng dòng | ≤ 12 từ |

## Mẹo

- Nhịp quan trọng hơn số cảnh: cảnh sau ngắn hơn hoặc bằng cảnh trước cho đến cuối.
- Khi có nhạc, chọn `duration` là bội của một nhịp nhạc (ví dụ nhạc 120 BPM: 1 nhịp = 0.5s, dùng 1.5s / 2s).
- Giữ tiếng gốc (`volume` 0.6–1) cho cảnh có tiếng sóng, tiếng chợ, hoặc người nói.
