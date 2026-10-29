# So sánh A với B — Hai khung, bảng điểm

Video dọc 9:16, 15–30 giây. Hai sản phẩm chạy song song trong khung cam (A) và khung xanh (B). Bên dưới, từng tiêu chí hiện lần lượt: tên tiêu chí ở giữa, điểm của A bên trái, của B bên phải. Cuối cảnh có nhãn vàng chốt bên thắng.

## Hỏi người dùng (gộp một tin)

1. Hai sản phẩm so sánh, tên ngắn (≤ 3 từ mỗi bên).
2. Clip hoặc ảnh của từng sản phẩm, cùng góc quay nếu được.
3. Ba đến bốn tiêu chí và kết quả của mỗi bên ("Pin: 1 ngày / 2 ngày").
4. Kết luận: bên nào hợp với ai.

## Cấu trúc cảnh

| Cảnh | Nguồn | Chữ | Độ dài |
|---|---|---|---|
| 1 | `srcs`: [A, B] | `tieu-de` + `ten-a` + `ten-b` | 2,5 giây |
| 2 | `srcs`: [A, B] | `ten-a` + `ten-b` + 3–4 hàng tiêu chí hiện lần lượt + `thang` | 6–8 giây |
| 3 | `src`: một clip hoặc `color:#111216`, kèm `"shapes": []` để bỏ hai khung | `ket` | 2,5 giây |

Một hàng tiêu chí gồm ba chữ cùng `y` và cùng `at`:

```json
{"preset": "tieu-chi", "text": "Pin", "y": 0.68, "at": 0.5},
{"preset": "diem-a", "text": "1 ngày", "y": 0.68, "at": 0.5},
{"preset": "diem-b", "text": "2 ngày", "y": 0.68, "at": 0.5}
```

Hàng sau: `y` cộng 0.06 (0.74, 0.80, 0.86), `at` cộng 1,2 giây. Nhãn `thang` hiện sau hàng cuối (`"at"` lớn hơn hàng cuối 1 giây).

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `tieu-de` | câu hỏi so sánh, trên cùng | ≤ 8 từ |
| `ten-a`, `ten-b` | tên hai bên dưới khung | ≤ 3 từ |
| `tieu-chi` | tên tiêu chí ở giữa | ≤ 2 từ |
| `diem-a`, `diem-b` | kết quả từng bên | ≤ 3 từ |
| `thang` | nhãn vàng chốt | ≤ 8 từ |
| `ket` | câu kết cảnh cuối | ≤ 12 từ |

## Mẹo

- Công bằng: nói rõ bên thua hơn ở đâu, người xem tin hơn.
- Cảnh 2 cần đủ dài: số hàng nhân 1,2 giây, cộng 2 giây để đọc nhãn chốt.
- `at` là giây tính từ đầu cảnh, dùng được cho mọi kiểu chữ ở mọi template.
