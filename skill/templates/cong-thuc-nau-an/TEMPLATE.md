# Công thức nấu ăn — Bếp nhà

Video dọc 20–45 giây. Tên món chữ tròn màu kem viền xanh, màn nguyên liệu nền xanh lá, nhãn Bước 1, 2, 3 vàng mù tạt, mô tả trong hộp xanh.

## Hỏi người dùng (gộp một tin)

1. Tên món, số người ăn, thời gian nấu.
2. Danh sách nguyên liệu (mỗi dòng một thứ).
3. Các bước, mỗi bước một câu ngắn.
4. Thư mục chứa clip (mỗi bước nên có một clip). Có nhạc nền không.

## Cấu trúc cảnh

| # | Cảnh | Thời lượng | Media nên chọn | Chữ |
|---|---|---|---|---|
| 1 | Món hoàn thành | 2–3s | món đã xong, gắp lên | `ten-mon` + `thong-tin` |
| 2 | Nguyên liệu | 3–4s | `color:#1F4D3A` hoặc ảnh bày nguyên liệu | `tieu-de` + `nguyen-lieu` |
| 3–n | Từng bước | 2–3s mỗi bước | clip đúng thao tác | `buoc` + `mo-ta` |
| cuối | Bày đĩa | 2–3s | món trên đĩa | `buoc` ("Xong") + `mo-ta` |

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `ten-mon` | tên món to, phía trên | ≤ 5 từ |
| `thong-tin` | nhãn kem: số người, thời gian | ≤ 8 từ |
| `tieu-de` | tiêu đề màn nguyên liệu | `Nguyên liệu` |
| `nguyen-lieu` | danh sách, mỗi dòng cách bằng `\n` | ≤ 7 dòng |
| `buoc` | nhãn vàng "Bước 1" | ≤ 2 từ |
| `mo-ta` | hộp xanh mô tả bước | ≤ 12 từ |

## Mẹo

- Một clip dài có nhiều bước: dùng cùng `src` với `start` khác nhau cho từng bước.
- Bước cần thời gian (luộc, ninh): thêm `"speed": 2` để tua nhanh.
- Danh sách quá 7 dòng: tách thành hai cảnh nguyên liệu.
