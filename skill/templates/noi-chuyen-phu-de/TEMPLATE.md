# Nói chuyện có phụ đề — Chữ vàng nổi

Video dọc 9:16, 20–60 giây. Một người nói thẳng vào camera. Câu mở đầu trong hộp vàng ở 3 giây đầu, phụ đề trắng viền đen bám theo lời, tên người nói ở góc trên. Cắt thẳng giữa các đoạn, tiếng gốc giữ nguyên, nhạc nền rất nhỏ.

## Hỏi người dùng (gộp một tin)

1. Clip nói (một clip dài hoặc vài đoạn), quay dọc.
2. Có sẵn file phụ đề `.srt` không. Nếu không, hỏi họ dán lời nói theo từng câu, hoặc dùng công cụ tạo phụ đề (CapCut, Whisper) rồi đưa file `.srt`.
3. Câu mở đầu (hook) ≤ 8 từ. Nếu chưa có, đề xuất từ câu hay nhất trong lời nói.
4. Tên và vai trò người nói ("Minh Anh · môi giới nhà phố").
5. Lời kêu gọi cuối.

## Cấu trúc cảnh

| Cảnh | Clip | Chữ | Độ dài |
|---|---|---|---|
| 1 | đoạn mở, câu gây tò mò | `hook` + `ten` | 3 giây |
| 2–n | các đoạn nói, bỏ chỗ ấp úng | phụ đề từ `subtitles` | tuỳ lời |
| cuối | đoạn chốt | `cta` | 2,5–3 giây |

Phụ đề đặt ở cấp plan: `"subtitles": {"file": "loi-noi.srt", "preset": "phu-de"}`. Mốc thời gian tính trên video thành phẩm: nếu cắt bớt đoạn, chỉnh lại file `.srt` cho khớp. Mỗi cảnh đặt `"volume": 1` (template đã để tiếng gốc 1).

## Kiểu chữ

| preset | Dùng cho | Gợi ý độ dài |
|---|---|---|
| `hook` | câu mở đầu trong hộp vàng | ≤ 8 từ |
| `phu-de` | phụ đề bám lời | ≤ 7 từ mỗi dòng phụ đề |
| `ten` | tên người nói, góc trên trái | ≤ 6 từ |
| `cta` | nút vàng cuối video | ≤ 6 từ |

## Mẹo

- Mỗi dòng `.srt` một ý ngắn, 1–2 giây. Câu dài thì tách đôi; phụ đề dài 3 dòng che mặt người nói.
- Muốn phụ đề cao hơn (người nói đứng thấp trong khung): thêm `"y": 0.6` vào `subtitles`. Mọi trường khác của kiểu chữ cũng ghi đè được ở đó, ví dụ `"size": 56`.
- Cảnh hook không cần phụ đề trùng lời: để trống khoảng 0–3 giây trong file `.srt`.
