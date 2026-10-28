# Outfit — Tạp chí đen trắng

Video dọc 10–25 giây. Tiêu đề chữ có chân nghiêng kiểu tạp chí, nhãn trắng cho từng món đồ kèm giá, phụ đề chữ có chân. Màu hơi trầm, chuyển cảnh mờ nhanh.

## Hỏi người dùng (gộp một tin)

1. Chủ đề: "5 outfit đi làm", "phối đồ đi biển"...
2. Mỗi outfit gồm món gì, giá bao nhiêu (hoặc tên shop).
3. Một câu cho mỗi outfit: mặc khi nào, vì sao hợp.
4. Có muốn ghi tổng tiền hoặc mã giảm giá cuối video không.
5. Thư mục chứa clip/ảnh. Có nhạc nền không.

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Mở đầu | 2–3s | dáng đứng toàn thân đẹp nhất | `tieu-de` + `phu` |
| 2–6 | Từng outfit | 2–3s mỗi cảnh | toàn thân hoặc cận chi tiết | 1–2 `mon-do` + `caption` |
| cuối | Tổng (tuỳ chọn) | 2–3s | outfit cuối hoặc cảnh xoay người | `caption` + `tong` |

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `tieu-de` | tiêu đề nghiêng, phía trên | ≤ 6 từ |
| `phu` | dòng nhỏ dưới tiêu đề | ≤ 12 từ |
| `mon-do` | nhãn trắng tên món + giá, bên trái | `Sơ mi xanh 350k` |
| `caption` | phụ đề chữ có chân, phía dưới | ≤ 10 từ |
| `tong` | nhãn tròn trắng: tổng tiền, mã giảm giá | ≤ 6 từ |

## Mẹo

- Nhiều nhãn `mon-do` trong một cảnh: đặt mỗi nhãn một `y` khác nhau, ngang tầm món đồ (áo ~0.42, váy ~0.58).
- Người đứng lệch phải: đổi nhãn sang phải bằng `"x": 0.94, "anchor_x": "right"`.
- Nền quá sáng làm phụ đề khó đọc: chọn đoạn clip có nền tối hơn ở phần dưới.
