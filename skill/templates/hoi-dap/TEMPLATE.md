# Hỏi đáp — Bong bóng tin nhắn

Video dọc 9:16, 10–25 giây. Mỗi video trả lời đúng một câu khách hay hỏi. Câu hỏi gõ dần trong bong bóng tin nhắn trắng, câu trả lời chữ to bên dưới, vài ý chính trong nhãn xanh, nút kêu gọi cuối. Tên shop nằm cố định dưới cùng.

## Hỏi người dùng (gộp một tin)

1. Câu hỏi khách hay hỏi, viết như khách nhắn ("Căn này vay được không em?").
2. Câu trả lời ngắn (≤ 8 từ) và hai đến ba ý chính kèm số cụ thể.
3. Clip minh hoạ: sản phẩm, không gian, người tư vấn.
4. Tên shop hoặc tên người tư vấn, lời kêu gọi.

## Cấu trúc cảnh

| Cảnh | Clip | Chữ | Độ dài |
|---|---|---|---|
| 1 | cảnh tổng | `nhan` + `cau-hoi` | 3,5–4 giây |
| 2 | cảnh trả lời | `tra-loi` | 3 giây |
| 3 | cảnh chi tiết | 2–3 `y-chinh` | 3–3,5 giây |
| 4 | cảnh chốt | `cta` | 2,5 giây |

Tên shop đặt ở cấp plan để hiện suốt video: `"texts": [{"preset": "ten-shop", "text": "Minh Anh · Nhà phố Thủ Đức"}]`.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `nhan` | nhãn xanh trên bong bóng | `Khách hỏi` |
| `cau-hoi` | câu hỏi gõ dần (28 ký tự/giây) | ≤ 14 từ |
| `tra-loi` | câu trả lời chữ trắng viền đen | ≤ 8 từ |
| `y-chinh` | ý chính, nhãn xanh bên trái | ≤ 7 từ |
| `cta` | nút xanh | ≤ 7 từ |
| `ten-shop` | tên shop, dưới cùng, cả video | ≤ 6 từ |

## Mẹo

- Một video, một câu hỏi. Có mười câu thì làm mười video, đăng thành chuỗi.
- Câu hỏi gõ cần thời gian: số ký tự chia 28, cộng một giây để đọc.
- Nhiều `y-chinh`: mỗi cái một `y`, cách nhau 0.08 (0.55, 0.63, 0.71). Muốn hiện lần lượt thêm `"at"`.
