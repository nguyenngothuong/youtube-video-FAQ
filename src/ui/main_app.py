import streamlit as st
from ..core.playlist import PlaylistHandler
from ..core.transcript import TranscriptExtractor
from ..core.storage import DataStorage
from ..utils.error_handler import ErrorHandler
from .components import video_processor, file_handler

class MainApp:
    def __init__(self):
        # Khởi tạo các components
        self.playlist_handler = PlaylistHandler()
        self.transcript_extractor = TranscriptExtractor()
        self.data_storage = DataStorage()
        self.error_handler = ErrorHandler()
        self.video_processor = video_processor.VideoProcessor(
            self.transcript_extractor,
            self.data_storage,
            self.error_handler,
            self.playlist_handler
        )
        self.file_handler = file_handler.FileHandler(self.data_storage)
        
        # Khởi tạo session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Khởi tạo các session state cần thiết"""
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
            
        if 'results' not in st.session_state:
            st.session_state.results = {
                'success_count': 0,
                'failed_count': 0,
                'videos': [],
                'playlist_id': None,
                'playlist_title': '',
                'playlist_uploader': '',
                'error_logs': [],
                'failed_videos': [],
                'total_videos': 0
            }
            
        if 'show_retry' not in st.session_state:
            st.session_state.show_retry = False

    def render(self):
        """Hiển thị giao diện chính của ứng dụng"""
        st.title("📝 YouTube Transcript Extractor")
        st.markdown("Trích xuất phụ đề từ video hoặc playlist YouTube")

        # Tab cho video đơn lẻ và playlist
        tab1, tab2 = st.tabs(["🎥 Video đơn lẻ", "📑 Playlist"])
        
        with tab1:
            # Form cho nhập liệu
            with st.form("single_video_form"):
                video_url = st.text_input(
                    "Nhập URL video YouTube",
                    placeholder="https://www.youtube.com/watch?v=..."
                )
                
                language = st.text_input(
                    "Chọn ngôn ngữ phụ đề",
                    value="en",
                    help="Nhập mã ngôn ngữ (vd: en=Tiếng Anh, vi=Tiếng Việt, ja=Tiếng Nhật, ko=Tiếng Hàn...)"
                )
                
                submitted = st.form_submit_button("Trích xuất phụ đề")
            
            # Xử lý và hiển thị kết quả bên ngoài form
            if submitted:
                self._handle_single_video(video_url, language)
        
        with tab2:
            with st.form("playlist_form"):
                playlist_url = st.text_input(
                    "Nhập URL playlist YouTube",
                    placeholder="https://www.youtube.com/playlist?list=..."
                )
                
                language = st.text_input(
                    "Chọn ngôn ngữ phụ đề",
                    value="en",
                    help="Nhập mã ngôn ngữ (vd: en=Tiếng Anh, vi=Tiếng Việt, ja=Tiếng Nhật, ko=Tiếng Hàn...)"
                )
                
                submitted = st.form_submit_button("Bắt đầu trích xuất")
                
                if submitted:
                    self._handle_submission(playlist_url, language)

        if st.session_state.processing_complete:
            self._show_results()

    def _handle_submission(self, playlist_url: str, language: str):
        """Xử lý khi form được submit"""
        try:
            if not playlist_url:
                st.error("Vui lòng nhập URL playlist!")
                return
                
            self.error_handler.log_info(f"Bắt đầu xử lý URL: {playlist_url}")
                
            if not self.playlist_handler.validate_playlist_url(playlist_url):
                st.error("URL playlist không hợp lệ!")
                return
                
            # Lấy thông tin playlist
            playlist_info = self.playlist_handler.get_playlist_info(playlist_url)
            if not playlist_info:
                st.error("Không thể lấy thông tin playlist. Vui lòng kiểm tra URL và thử lại.")
                return
                
            self.error_handler.log_info(f"Đã lấy thông tin playlist: {playlist_info}")
            st.info(f"🎵 Đang xử lý playlist: {playlist_info['title']}")
            
            # Lấy danh sách video
            videos = self.playlist_handler.get_playlist_videos(playlist_url)
            if not videos:
                st.error("""
                ❌ Không thể tải danh sách video. Có thể do:
                - Playlist không tồn tại hoặc đã bị xóa
                - Playlist ở chế độ riêng tư
                - Có vấn đề với kết nối mạng
                """)
                return
                
            # Bắt đầu xử lý video
            self.video_processor.process_playlist(playlist_url, language)
            
        except Exception as e:
            self.error_handler.log_error("Submission Error", str(e))
            st.error(f"Có lỗi xảy ra: {str(e)}")

    def _show_results(self):
        """Hiển thị kết quả xử lý"""
        results = st.session_state.results
        
        # Hiển thị thông tin playlist
        if results.get('playlist_title'):
            st.subheader(f"Playlist: {results['playlist_title']}")
            if results.get('playlist_uploader'):
                st.markdown(f"*Uploader: {results['playlist_uploader']}*")
        
        # Hiển thị thống kê tổng quan
        total = results.get('total_videos', 0)
        st.write(f"### Tổng quan")
        
        # Tạo columns cho thống kê
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tổng số video", f"{total}")
        with col2:
            st.metric("Thành công", f"{results['success_count']}/{total}", 
                     delta=f"{int(results['success_count']/total*100)}%" if total > 0 else "0%")
        with col3:
            if results['failed_count'] > 0:
                st.metric("Thất bại", f"{results['failed_count']}/{total}", 
                         delta=f"-{int(results['failed_count']/total*100)}%", 
                         delta_color="inverse")
        
        # Nút retry và tải xuống
        self._show_action_buttons(results)
        
        # Hiển thị chi tiết
        self._show_details(results)

    def _show_action_buttons(self, results):
        """Hiển thị các nút hành động"""
        # Nút retry
        if st.session_state.show_retry and results.get('failed_videos'):
            if st.button("🔄 Thử lại các video lỗi"):
                self.video_processor.retry_failed_videos()
        
        # Nút tải xuống
        if results['success_count'] > 0:
            zip_data = self.file_handler.create_zip_file(results['playlist_id'])
            filename = self.file_handler.generate_filename(
                results.get('playlist_uploader', ''),
                results.get('playlist_title', ''),
                results.get('playlist_id', '')
            )
            
            st.download_button(
                label="📥 Tải xuống tất cả transcript",
                data=zip_data,
                file_name=filename,
                mime="application/zip"
            )

    def _show_details(self, results):
        """Hiển thị chi tiết video và log lỗi"""
        if results.get('videos'):
            with st.expander("Xem chi tiết từng video"):
                for video in results['videos']:
                    status_color = "🟢" if video.get('status') == 'success' else "🔴"
                    st.markdown(f"{status_color} **{video.get('title', 'Unknown Title')}**")
        
        if results.get('error_logs'):
            with st.expander("Xem log lỗi chi tiết"):
                for log in results['error_logs']:
                    retry_status = "Lần thử lại" if log.get('is_retry') else "Lần đầu"
                    st.markdown(f"""
                        **Video:** {log.get('title', 'Unknown Title')}  
                        **Error:** {log.get('error', 'Unknown Error')}  
                        **Trạng thái:** {retry_status}  
                        ---
                    """) 

    def process_url(self):
        """Xử lý URL được nhập vào"""
        url = st.session_state.url.strip()
        
        # Kiểm tra URL
        if not self.playlist_handler.validate_playlist_url(url):
            st.error("❌ URL không hợp lệ. Vui lòng nhập URL playlist YouTube hợp lệ.")
            return
            
        try:
            # Lấy thông tin playlist
            playlist_info = self.playlist_handler.get_playlist_info(url)
            if not playlist_info:
                st.error("❌ Không thể tải thông tin playlist. Vui lòng kiểm tra URL và thử lại.")
                return
                
            st.info(f"🎵 Đang xử lý playlist: {playlist_info['title']}")
            
            # Lấy danh sách video
            videos = self.playlist_handler.get_playlist_videos(url)
            if not videos:
                st.error("""
                ❌ Không thể tải danh sách video. Có thể do:
                - Playlist không tồn tại hoặc đã bị xóa
                - Playlist ở chế độ riêng tư
                - Có vấn đề với kết nối mạng
                - YouTube đã thay đổi API
                
                Vui lòng kiểm tra và thử lại.
                """)
                return
                
            # Tiếp tục xử lý...
            
        except Exception as e:
            st.error(f"❌ Có lỗi xảy ra: {str(e)}")
            self.error_handler.log_error("Processing Error", str(e))

    def _handle_single_video(self, video_url: str, language: str):
        """Xử lý video đơn lẻ"""
        try:
            if not video_url:
                st.error("Vui lòng nhập URL video!")
                return
                
            # Kiểm tra và lấy video ID
            video_id = self.playlist_handler.extract_video_id(video_url)
            if not video_id:
                st.error("URL video không hợp lệ!")
                return
                
            # Lấy thông tin video
            video_info = self.playlist_handler.get_video_info(video_url)
            if not video_info:
                st.error("Không thể lấy thông tin video. Vui lòng kiểm tra URL và thử lại.")
                return
                
            st.info(f"🎥 Đang xử lý video: {video_info['title']}")
            
            # Tạo container cho status
            status_container = st.empty()
            
            # Tạo video object
            video = {
                'video_id': video_id,
                'title': video_info['title'],
                'url': video_url,
                'status': 'pending'
            }
            
            # Xử lý video
            success = self.video_processor.process_video(
                video,
                'single_videos',  # Thư mục đặc biệt cho video đơn lẻ
                language,
                status_container
            )
            
            # Hiển thị kết quả và nút download bên ngoài form
            if success:
                st.success(f"✅ Đã tải thành công transcript cho video: {video_info['title']}")
                
                # Tạo nút download
                transcript_data = self.transcript_extractor.download_transcript(video_id, video_info['title'], language)
                if transcript_data:
                    txt_content = self.data_storage._create_text_content(transcript_data)
                    # Nút download được đặt bên ngoài form
                    st.download_button(
                        label="📥 Tải transcript",
                        data=txt_content,
                        file_name=f"{self.data_storage._sanitize_filename(video_info['title'])}_{video_id}.txt",
                        mime="text/plain"
                    )
            else:
                st.error(f"❌ Không thể tải transcript cho video: {video_info['title']}")
                
        except Exception as e:
            self.error_handler.log_error("Single Video Processing Error", str(e))
            st.error(f"Có lỗi xảy ra: {str(e)}")