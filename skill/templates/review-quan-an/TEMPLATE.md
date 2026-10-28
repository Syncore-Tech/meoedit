# Review quán ăn — Đường phố đỏ vàng

Video dọc 15–30 giây. Câu mở đầu in hoa trên hộp đỏ, tên món viết tay vàng, nhãn giá vàng nghiêng, chuyển cảnh trượt ngang 0.25 giây. Màu video được làm rực hơn một chút.

## Hỏi người dùng (gộp một tin)

1. Tên quán (nếu muốn ghi) và khu vực, ví dụ "Phố cổ Hà Nội".
2. Các món đã ăn và giá từng món.
3. Một câu cho từng món: ngon ở đâu.
4. Chấm mấy điểm trên 10, một câu kết luận (ví dụ tổng tiền cho mấy người).
5. Thư mục chứa ảnh/clip. Có nhạc nền không.

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Hook | 2–3s | món đẹp nhất, cảnh múc/rót đang chuyển động | `dia-chi` + `hook` |
| 2–3 | Không khí quán | 2s mỗi cảnh | người bán, bàn ghế, mặt tiền | `caption` |
| 4–6 | Từng món | 2–2.5s mỗi cảnh | cận món, gắp, chấm | `mon` + `gia` (+ `caption`) |
| 7 | Chấm điểm | 2.5–3s | `color:#D62828` | `diem` + `ket-luan` |

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `hook` | câu mở đầu, in hoa trên hộp đỏ, phía trên | ≤ 7 từ |
| `dia-chi` | nhãn khu vực góc trên trái | ≤ 5 từ |
| `mon` | tên món, chữ viết tay vàng, giữa màn hình | ≤ 3 từ |
| `gia` | nhãn giá vàng nghiêng, cạnh tên món | `45k` |
| `caption` | phụ đề trắng, phía dưới | ≤ 12 từ |
| `diem` | số điểm rất to | `9/10` |
| `ket-luan` | câu dưới số điểm | ≤ 14 từ |

## Mẹo

- Cảnh hook có chuyển động (múc nước dùng, gắp) giữ người xem tốt hơn ảnh tĩnh.
- `volume` 0.3–0.4 ở cảnh có tiếng xèo xèo, tiếng quán để video có không khí.
- Món nằm phía dưới khung hình: dời `mon` lên bằng `"y": 0.35`.
