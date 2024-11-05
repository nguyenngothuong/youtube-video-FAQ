import streamlit as st
from ...core.transcript import TranscriptExtractor
from ...core.storage import DataStorage
from ...core.playlist import PlaylistHandler
from ...utils.error_handler import ErrorHandler

class VideoProcessor:
    def __init__(self, transcript_extractor, data_storage, error_handler, playlist_handler):
        self.transcript_extractor = transcript_extractor
        self.data_storage = data_storage
        self.error_handler = error_handler
        self.playlist_handler = playlist_handler
        
    def process_video(self, video, playlist_id, language, video_status_container):
        """Xử lý một video riêng lẻ"""
        try:
            transcript_data = self.transcript_extractor.download_transcript(
                video['video_id'],
                video['title'],
                language
            )
            
            if transcript_data:
                if self.data_storage.save_transcript(
                    playlist_id,
                    video['video_id'],
                    video['title'],
                    transcript_data
                ):
                    video['status'] = 'success'
                    return True
            
            return False
                
        except Exception as e:
            st.session_state.results['error_logs'].append({
                'video_id': video['video_id'],
                'title': video['title'],
                'error': str(e),
                'is_retry': False
            })
            video['status'] = 'failed'
            return False

    def process_playlist(self, playlist_url: str, language: str, retry_videos=None):
        """Xử lý toàn bộ playlist"""
        try:
            self.error_handler.log_info("Bắt đầu xử lý playlist...")
            
            # Nếu là retry thì dùng videos đã có
            if retry_videos:
                videos = retry_videos
                playlist_id = st.session_state.results['playlist_id']
            else:
                # Lấy thông tin playlist
                playlist_info = self.playlist_handler.get_playlist_info(playlist_url)
                if not playlist_info:
                    st.error("Không thể lấy thông tin playlist")
                    return
                    
                playlist_id = playlist_info['id']
                videos = self.playlist_handler.get_playlist_videos(playlist_url)
                
                # Cập nhật session state
                st.session_state.results.update({
                    'playlist_id': playlist_id,
                    'playlist_title': playlist_info['title'],
                    'playlist_uploader': playlist_info['channel']
                })
            
            total_videos = len(videos)
            self.error_handler.log_info(f"Tìm thấy {total_videos} video")
            
            # Tạo container cho progress bar và status
            progress_container = st.container()
            with progress_container:
                progress_text = st.empty()
                progress_bar = st.progress(0)
                current_video_container = st.empty()  # Container cho tên video hiện tại
                stats_container = st.empty()  # Container cho thống kê
            
            success_count = 0
            failed_count = 0
            
            # Xử lý từng video
            for i, video in enumerate(videos):
                current = i + 1
                progress = current / total_videos
                
                # Cập nhật progress bar và text
                progress_bar.progress(progress)
                progress_text.write(f"⏳ Đang xử lý: {current}/{total_videos} videos ({int(progress * 100)}%)")
                
                # Hiển thị tên video đang xử lý
                current_video_container.info(f"🎥 Video hiện tại: {video['title']}")
                
                # Xử lý video và cập nhật thống kê
                if self.process_video(video, playlist_id, language, None):  # Truyền None cho video_status_container
                    success_count += 1
                else:
                    failed_count += 1
                    st.session_state.results['failed_videos'].append(video)
                
                # Cập nhật số liệu trong một dòng
                stats_container.info(f"✅ Thành công: {success_count}/{total_videos} | ❌ Thất bại: {failed_count}/{total_videos}")
            
            # Xóa container tên video sau khi hoàn thành
            current_video_container.empty()
            
            # Cập nhật kết quả cuối cùng
            st.session_state.results.update({
                'success_count': success_count,
                'failed_count': failed_count,
                'videos': videos,
                'total_videos': total_videos
            })
            st.session_state.processing_complete = True
            st.session_state.show_retry = failed_count > 0
            
            # Hiển thị thông báo hoàn thành
            if success_count == total_videos:
                st.success(f"✨ Hoàn thành! Đã tải thành công {success_count}/{total_videos} transcripts")
            else:
                st.warning(f"⚠️ Đã hoàn thành với {success_count}/{total_videos} transcripts thành công")
                
            self.error_handler.log_info("Đã hoàn thành xử lý playlist")
            
        except Exception as e:
            self.error_handler.log_error("Playlist Processing Error", str(e))
            st.error(f"Lỗi khi xử lý playlist: {str(e)}")

    def retry_failed_videos(self):
        """Thử lại các video bị lỗi"""
        st.session_state.show_retry = False
        prev_success = st.session_state.results['success_count']
        prev_failed = st.session_state.results['failed_count']
        
        self.process_playlist(None, None, st.session_state.results['failed_videos'])
        
        if 'success_count' in st.session_state.results:
            st.session_state.results['success_count'] = prev_success + st.session_state.results['success_count']
            st.session_state.results['failed_count'] = prev_failed - st.session_state.results['success_count'] 