# Trước và sau — Khung vàng neon

Video dọc 9:16, 8–20 giây. Hai video chạy cùng lúc: bản gốc trong khung nhỏ bên trái, bản đã làm trong khung lớn viền vàng neon bên phải. Nền tối kẻ lưới vàng, dải ưu đãi vàng chữ đen. Khung phải lớn hơn để kết quả là thứ người xem nhìn trước. Logo và tiêu đề ở trên, câu mô tả và dải ưu đãi ở dưới.

## Hỏi người dùng (gộp một tin)

1. Tên thương hiệu (hiện thành logo chữ trên cùng).
2. Đã làm gì trong một câu ("Clip gốc thành video bán hàng").
3. Mỗi cặp clip: bản gốc và bản đã làm, cùng cảnh. Bản đã làm nên cắt đúng đoạn khớp với bản gốc.
4. Ưu đãi hoặc câu kêu gọi ở đáy.

## Cấu trúc cảnh

Mỗi cảnh là một cặp, dùng `srcs` thay cho `src`:

```json
{"srcs": ["goc.mp4", "da-dung.mp4"], "starts": [2, 0.5], "duration": 2.8,
 "texts": [{"preset": "caption", "text": "Thêm tên dự án và nhãn khu vực"}]}
```

`logo`, `tieu-de`, `nhan-truoc`, `nhan-sau`, `cta` đặt ở `texts` cấp plan để đứng yên suốt video. Mỗi cảnh chỉ đổi `caption`. Ba cặp, mỗi cặp 2,5–3 giây là vừa.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `logo` | tên thương hiệu trong viên vàng trên cùng | 1–2 từ |
| `tieu-de` | tiêu đề in hoa | ≤ 7 từ |
| `nhan-truoc` | nhãn khung trái | `Source gốc`, `Before` |
| `nhan-sau` | nhãn khung phải | `Final`, `After` |
| `caption` | điều thay đổi ở cặp này | ≤ 8 từ |
| `cta` | dải ưu đãi vàng ở đáy, in hoa, được xuống dòng | ≤ 16 từ |

## Mẹo

- Hai clip trong một cặp nên cùng góc máy, cùng nhịp. Dùng `starts` để khớp khoảnh khắc.
- Tiếng lấy từ khung phải (bản đã làm). Muốn nghe bản gốc: `"audio_panel": 0` và `"volume": 0.8`.
- Khung dọc hẹp: chọn clip có chủ thể ở giữa khung hình.
