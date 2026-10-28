# Gym — Bài tập và đồng hồ đếm

Video dọc 9:16, 20–45 giây. Cảnh mở có tiêu đề chữ đậm in hoa. Mỗi bài một cảnh: tên bài góc trên, nhãn đỏ số hiệp và số lần, đồng hồ đếm ngược góc dưới phải, một mẹo tư thế. Cắt thẳng theo nhịp nhạc, màu hơi gắt.

## Hỏi người dùng (gộp một tin)

1. Chủ đề buổi tập ("Chân mông 20 phút tại phòng").
2. Ba đến năm bài: tên bài, số hiệp × số lần (hoặc số giây giữ), một mẹo tư thế.
3. Clip từng bài, quay đủ một lượt động tác.
4. Câu kết hoặc lời mời ("Lưu lại tập tối nay", "Inbox để có lịch tập riêng").

## Cấu trúc cảnh

| Cảnh | Clip | Chữ | Độ dài |
|---|---|---|---|
| 1 | cảnh đẹp nhất | `tieu-de` + `phu` | 2,5 giây |
| 2–n | mỗi bài | `ten-bai` + `hiep` + `dong-ho` + `meo` | 4–6 giây |
| cuối | cảnh nghỉ, cười | `ket` | 2,5 giây |

Đồng hồ đếm ngược không cần chữ, chỉ cần số giây:

```json
{"preset": "dong-ho", "countdown": 5}
```

Đồng hồ chạy từ `0:05` về `0:00` rồi đứng yên tới hết cảnh. Muốn bắt đầu muộn hơn: thêm `"at": 1`.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `tieu-de` | tiêu đề in hoa | ≤ 6 từ |
| `phu` | nhãn đỏ dưới tiêu đề | ≤ 6 từ |
| `ten-bai` | tên bài in hoa, góc trên trái | ≤ 4 từ |
| `hiep` | nhãn đỏ | `4 hiệp × 12 lần` |
| `dong-ho` | đồng hồ đếm ngược | `"countdown": 5` |
| `meo` | mẹo tư thế, nhãn tối | ≤ 9 từ |
| `ket` | câu kết in hoa | ≤ 6 từ |

## Mẹo

- Video demo không cần đếm đủ 60 giây; đếm vừa độ dài cảnh (4–6 giây) cho người xem thấy nhịp.
- Mẹo tư thế nói cụ thể: "Gối không vượt mũi chân", không phải "Giữ đúng tư thế".
- Cảnh xuất sang CapCut: đồng hồ thành một dòng chữ mỗi giây, sửa được từng số.
