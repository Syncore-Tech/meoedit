# Hướng dẫn — Quay màn hình 16:9

Video ngang 1920x1080 cho hướng dẫn phần mềm. Màn hình quay nằm trong khung bo góc trên nền vàng, dải trên có nhãn bước và một câu mô tả. Mở và kết bằng màn chữ to trên nền vàng.

## Hỏi người dùng (gộp một tin)

1. Hướng dẫn làm việc gì, cho ai xem.
2. File quay màn hình (16:9) và các mốc thời gian của từng bước, nếu họ biết.
3. Câu kết: lệnh cài, đường dẫn, hoặc lời mời dùng thử.

## Cấu trúc cảnh

| Cảnh | Nguồn | Chữ | Độ dài |
|---|---|---|---|
| mở | `color:#FFD23F`, `"shapes": []` | `lon` + `nho` | 3–4 giây |
| mỗi bước | `"srcs": ["quay.mp4"]` + `start` | `buoc` + `mo-ta` | 6–11 giây |
| kết | `color:#FFD23F`, `"shapes": []` | `lon` + `nho` + `lenh` | 4–5 giây |

Cảnh bước dùng `srcs` để màn hình nằm trong khung. Cảnh dùng `src` thì phủ kín khung hình, hợp với màn chữ hoặc một clip đã dựng sẵn.

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `buoc` | nhãn bước | `Bước 1` |
| `mo-ta` | việc làm ở bước này | ≤ 10 từ |
| `lon` | tiêu đề màn mở hoặc kết | ≤ 4 từ |
| `nho` | câu phụ dưới tiêu đề | ≤ 16 từ, được xuống dòng |
| `lenh` | lệnh hoặc đường dẫn | một dòng |

## Mẹo

- Đoạn chờ máy chạy: dùng `"speed"` (ví dụ 6 đến 10) để tua nhanh, ghi "(tua nhanh)" trong `mo-ta`.
- Quay terminal: cỡ chữ từ 24 trở lên ở 1920x1080 thì xem trên điện thoại vẫn đọc được.
- Nguồn quay phải là 16:9, khổ khác sẽ bị cắt cho vừa khung.
