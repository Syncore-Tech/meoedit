# Giới thiệu dự án BĐS — Xanh rêu ánh vàng

Video dọc 9:16, 15–30 giây cho sale bất động sản. Mở bằng tên dự án in hoa, rồi vị trí, các điểm nổi bật, màn giá "chỉ từ" chữ vàng to. Nút liên hệ nằm cố định ở đáy suốt video.

## Hỏi người dùng (gộp một tin)

1. Tên dự án, loại hình (căn hộ, nhà phố, đất nền) và khu vực.
2. Vị trí trong một câu (cách trung tâm bao xa, gần tuyến đường nào).
3. Ba điểm nổi bật (tiện ích, pháp lý, bàn giao).
4. Giá thấp nhất và câu kêu gọi liên hệ.
5. Clip flycam, nhà mẫu, tiện ích. Flycam nên để cảnh đầu.

## Cấu trúc cảnh

| Cảnh | Clip | Chữ | Độ dài |
|---|---|---|---|
| 1 | flycam toàn dự án | `nhan` + `ten-du-an` | 3 giây |
| 2 | flycam đường xá | `vi-tri` + `caption` | 2,5 giây |
| 3–4 | tiện ích, nhà mẫu | `diem` (mỗi cảnh một điểm) | 2,5 giây |
| 5 | nhà mẫu đẹp nhất | `gia-nho` + `gia` | 3 giây |

`cta` đặt ở `texts` cấp plan để hiện suốt video.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `nhan` | nhãn nhỏ trên tên dự án | `Căn hộ Thủ Đức` |
| `ten-du-an` | tên dự án in hoa | ≤ 3 từ, tự xuống dòng |
| `vi-tri` | nhãn vị trí có ghim | ≤ 6 từ |
| `diem` | một điểm nổi bật có dấu tick | ≤ 8 từ |
| `gia-nho` | dòng nhỏ trên giá | `Sở hữu chỉ từ` |
| `gia` | con số giá, chữ vàng rất to | `1,5 tỷ` |
| `caption` | câu giải thích dưới | ≤ 12 từ |
| `cta` | nút liên hệ ở đáy | ≤ 7 từ |

## Mẹo

- Giá phải là giá thật người dùng đưa. Không tự bịa con số hay pháp lý.
- `gia` chỉ nên có số và đơn vị. Chữ dài hơn sẽ bị thu nhỏ khó đọc.
- Không có flycam: mở bằng ảnh phối cảnh với `"motion": "pan"`.
