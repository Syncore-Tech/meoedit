# Review quán cà phê — Nâu kem chill

Video dọc 20–35 giây. Tông nâu kem ấm, chữ mềm, chuyển cảnh mờ dần 0.35 giây. Màu video được làm ấm nhẹ.

## Hỏi người dùng (gộp một tin)

1. Tên quán và khu vực (ví dụ "Mộc Chill, Quận 3").
2. Đã gọi món gì, giá bao nhiêu.
3. Điều thích nhất và điều chưa thích (một câu mỗi ý).
4. Chấm mấy điểm trên 10.
5. Thư mục chứa ảnh/clip. Có nhạc nền không.

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Hook | 2–3s | cảnh đẹp nhất: mặt tiền, góc nắng, ly nước cầm tay | `dia-diem` + `hook` |
| 2 | Tên quán | 2–3s | toàn cảnh không gian | `ten-quan` (+ `caption` tuỳ chọn) |
| 3–4 | Không gian | 2–2.5s mỗi cảnh | góc ngồi, cây, ánh sáng | `caption` |
| 5–6 | Đồ uống/món | 2–2.5s mỗi cảnh | cận ly, rót, khuấy | `gia` + `caption` |
| 7 | Chấm điểm | 2.5–3s | `color:#3B2A20` | `diem` + `nho` (một câu kết luận) |

Tổng 7–10 cảnh. Có thể bỏ bớt cảnh không gian nếu ít media.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `hook` | câu mở đầu, hộp kem chữ nâu, phía trên | ≤ 8 từ |
| `ten-quan` | tên quán, chữ viết tay, giữa màn hình | ≤ 3 từ |
| `dia-diem` | nhãn khu vực góc trên trái | ≤ 5 từ |
| `caption` | phụ đề trắng viền nâu, phía dưới | ≤ 12 từ |
| `gia` | nhãn giá nghiêng, bên phải | `45k` |
| `diem` | số điểm rất to | `8.5` |
| `nho` | dòng nhỏ dưới điểm số | ≤ 14 từ |

## Mẹo

- Không có clip mặt tiền thì dùng ảnh ly nước làm hook.
- `volume` 0.3–0.5 ở cảnh có tiếng máy pha, tiếng mưa để video có không khí.
- Cảnh có người ngồi chính giữa: dời `caption` lên bằng `"y": 0.7` nếu che mặt.
