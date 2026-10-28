# Mở hộp sản phẩm — Hồng phấn

Video dọc 15–30 giây. Câu mở đầu trong hộp trắng, tên sản phẩm viết tay, nhãn hồng cho điểm nổi bật, màn giá cuối với nút đặt hàng. Chuyển cảnh trượt lên mềm.

## Hỏi người dùng (gộp một tin)

1. Tên sản phẩm và một dòng mô tả.
2. Hai đến ba điểm nổi bật (mỗi điểm ≤ 6 từ).
3. Giá bán, giá cũ nếu đang giảm.
4. Lời kêu gọi: "Đặt ở link trong bio", "Nhắn tin để đặt"...
5. Thư mục chứa clip/ảnh. Có nhạc nền không.

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Hook | 2–3s | cầm hộp/túi hàng, sắp mở | `hook` |
| 2 | Lộ sản phẩm | 2–3s | lấy sản phẩm ra | `ten-sp` + `caption` |
| 3 | Điểm nổi bật | 2–3s | cận sản phẩm, mở nắp, thử | 2–3 `diem-nhan` |
| 4 | Chi tiết | 2s | bao bì, kết cấu | `caption` |
| 5 | Giá | 2.5–3s | `color:#FFE3EE` | `ten-sp` + `gia` + `gia-cu` + `cta` |

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `hook` | câu mở đầu trong hộp trắng, phía trên | ≤ 8 từ |
| `ten-sp` | tên sản phẩm viết tay | ≤ 3 từ |
| `diem-nhan` | nhãn hồng bên trái | ≤ 6 từ |
| `caption` | phụ đề trắng phía dưới | ≤ 10 từ |
| `gia` | giá to màu mận | `289.000đ` |
| `gia-cu` | giá gốc dưới giá mới | `Giá gốc 340.000đ` |
| `cta` | nút mận chữ trắng | ≤ 6 từ |

## Mẹo

- Màn giá nền hồng nhạt: đặt `ten-sp` lên `"y": 0.27` và đổi màu chữ `"color": "#4B1D3F", "shadow": null` cho dễ đọc.
- Nhiều nhãn `diem-nhan`: mỗi nhãn một `y`, cách nhau 0.08.
- Clip có tiếng xé hộp, mở nắp: `volume` 0.4 cho cảnh đó.
