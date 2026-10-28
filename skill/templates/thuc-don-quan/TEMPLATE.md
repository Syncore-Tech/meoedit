# Thực đơn quán — Bảng gỗ ấm

Video dọc 9:16, 15–35 giây. Cảnh mở có tên quán kiểu bảng hiệu. Mỗi món một cảnh: tên món chữ tròn to, giá vàng, một dòng mô tả. Nhãn combo nghiêng góc phải. Địa chỉ và giờ mở cửa nằm cố định dưới cùng suốt video. Tông ấm, chuyển mờ.

## Hỏi người dùng (gộp một tin)

1. Tên quán và một câu giới thiệu ("Thực đơn trưa tuần này").
2. Ba đến năm món: tên, giá, một dòng mô tả.
3. Combo hoặc khuyến mãi nếu có.
4. Địa chỉ ngắn và giờ mở cửa.
5. Clip/ảnh cho từng món, cảnh mặt tiền hoặc bếp cho cảnh mở.

## Cấu trúc cảnh

| Cảnh | Clip | Chữ | Độ dài |
|---|---|---|---|
| 1 | mặt tiền, bếp, quầy | `ten-quan` + `phu` | 3 giây |
| 2–n | mỗi món | `mon` + `gia` + `mo-ta` | 2,5–3 giây |
| cuối | combo hoặc món bán chạy | `combo` + `mon` + `gia` | 3 giây |

Địa chỉ đặt ở cấp plan: `"texts": [{"preset": "dia-chi", "text": "12 Trần Quang Khải, Q1 · Mở 10:00–22:00"}]`.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `ten-quan` | tên quán kiểu bảng hiệu | ≤ 4 từ |
| `phu` | câu dưới tên quán | ≤ 8 từ |
| `mon` | tên món | ≤ 5 từ |
| `gia` | giá vàng | `45k` |
| `mo-ta` | mô tả món | ≤ 8 từ |
| `combo` | nhãn vàng nghiêng | ≤ 5 từ |
| `dia-chi` | địa chỉ + giờ, dưới cùng, cả video | ≤ 10 từ |

## Mẹo

- Viết giá ngắn (`45k`) cho dễ đọc lướt.
- Mô tả nói điều khác biệt ("nước dùng ninh 8 tiếng"), không nói "ngon tuyệt".
- Món chụp từ trên xuống thì đặt `mon` cao hơn: `"y": 0.62` để không che món.
