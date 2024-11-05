# YouTube Transcript Extractor 📝

Ứng dụng web để trích xuất phụ đề từ video YouTube và playlist, được xây dựng với Streamlit và Python.

## 🌟 Tính năng

- 🔐 Xác thực người dùng với Supabase
- 🎥 Hỗ trợ trích xuất phụ đề từ video đơn lẻ
- 📑 Hỗ trợ trích xuất phụ đề từ toàn bộ playlist
- 🌍 Hỗ trợ nhiều ngôn ngữ phụ đề
- 📥 Tải xuống phụ đề dưới dạng TXT và JSON
- 📊 Hiển thị tiến trình và thống kê chi tiết
- 🔄 Tính năng thử lại cho các video lỗi
- 📁 Tổ chức file đầu ra theo cấu trúc thư mục rõ ràng

## 🚀 Cài đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/youtube_transcript_extractor.git
cd youtube_transcript_extractor
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình Supabase:
- Tạo file `.streamlit/secrets.toml`:
```toml
[supabase]
url = "your_supabase_url"
anon_key = "your_supabase_anon_key"
site_url = "your_site_url"
```

4. Chạy ứng dụng:
```bash
streamlit run streamlit_app.py
```

## 📋 Yêu cầu hệ thống

- Python 3.8+
- FFmpeg (recommended)
- Kết nối internet ổn định

## 📦 Dependencies chính

- streamlit
- youtube-transcript-api
- yt-dlp
- supabase-py
- python-dotenv

## 🎯 Cách sử dụng

1. **Đăng nhập/Đăng ký**:
   - Sử dụng email để đăng ký tài khoản
   - Xác nhận email để kích hoạt tài khoản
   - Đăng nhập để sử dụng ứng dụng

2. **Trích xuất phụ đề từ video đơn lẻ**:
   - Chọn tab "Video đơn lẻ"
   - Nhập URL video YouTube
   - Chọn ngôn ngữ phụ đề
   - Nhấn "Trích xuất phụ đề"
   - Tải xuống file phụ đề

3. **Trích xuất phụ đề từ playlist**:
   - Chọn tab "Playlist"
   - Nhập URL playlist YouTube
   - Chọn ngôn ngữ phụ đề
   - Nhấn "Bắt đầu trích xuất"
   - Theo dõi tiến trình xử lý
   - Tải xuống tất cả phụ đề

## 📂 Cấu trúc thư mục

```
youtube_transcript_extractor/
├── src/
│   ├── auth/               # Xử lý xác thực
│   ├── core/              # Logic nghiệp vụ chính
│   │   ├── transcript.py
│   │   ├── storage.py
│   │   └── playlist.py
│   ├── ui/                # Giao diện người dùng
│   │   ├── components/
│   │   └── main_app.py
│   └── utils/             # Tiện ích
├── data/                  # Thư mục lưu trữ dữ liệu
├── logs/                  # Log files
└── streamlit_app.py       # Entry point
```

## 🔧 Cấu hình

Các tùy chọn cấu hình có thể được điều chỉnh trong:
- `.streamlit/secrets.toml`: Cấu hình Supabase
- `src/core/transcript.py`: Danh sách ngôn ngữ hỗ trợ
- `src/core/storage.py`: Cấu hình lưu trữ file

## 🚨 Xử lý lỗi phổ biến

1. **Lỗi "FFmpeg not found"**:
   - Cài đặt FFmpeg theo hướng dẫn: [FFmpeg Installation](https://github.com/yt-dlp/yt-dlp#dependencies)

2. **Lỗi "No transcript found"**:
   - Kiểm tra video có phụ đề không
   - Thử ngôn ngữ khác

3. **Lỗi "Playlist not accessible"**:
   - Kiểm tra playlist có công khai không
   - Kiểm tra URL playlist

## 📝 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo branch mới
3. Commit changes
4. Tạo Pull Request

## 📧 Liên hệ

Nếu có bất kỳ câu hỏi hoặc góp ý nào, vui lòng tạo issue hoặc liên hệ qua email. 