from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs
from ..utils.error_handler import ErrorHandler


class PlaylistHandler:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True
        }

    def validate_playlist_url(self, url: str) -> bool:
        """Kiểm tra tính hợp lệ của URL playlist"""
        try:
            self.error_handler.log_info(f"Đang kiểm tra URL playlist: {url}")
            
            # Kiểm tra định dạng URL cơ bản
            parsed_url = urlparse(url)
            if 'youtube.com' not in parsed_url.netloc:
                self.error_handler.log_error("Invalid URL", "URL không phải từ YouTube")
                return False
            
            query_params = parse_qs(parsed_url.query)
            if 'list' not in query_params:
                self.error_handler.log_error("Invalid URL", "Không tìm thấy ID playlist")
                return False
                
            playlist_id = query_params['list'][0]
            
            # Thử tải thông tin cơ bản của playlist
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'no_warnings': False
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    self.error_handler.log_info("Đang thử tải thông tin playlist...")
                    info = ydl.extract_info(url, download=False, process=False)
                    
                    if not info:
                        self.error_handler.log_error("Playlist Access Error", "Không thể truy cập playlist")
                        return False
                        
                    if info.get('_type') != 'playlist':
                        self.error_handler.log_error("Invalid Content Type", "URL không phải là playlist")
                        return False
                        
                    self.error_handler.log_info(f"Playlist hợp lệ: {info.get('title', 'Unknown')}")
                    return True
                    
                except Exception as e:
                    self.error_handler.log_error("Playlist Access Error", 
                        f"Lỗi khi truy cập playlist: {str(e)}", 
                        {"playlist_id": playlist_id}
                    )
                    return False
                    
        except Exception as e:
            self.error_handler.log_error("URL Validation Error", str(e), {"url": url})
            return False

    def get_playlist_info(self, url: str) -> dict:
        """Lấy thông tin playlist bao gồm ID, tên và channel"""
        try:
            self.error_handler.log_info("Bắt đầu lấy thông tin playlist...")
            with YoutubeDL(self.ydl_opts) as ydl:
                self.error_handler.log_info("Đang tải thông tin từ YouTube...")
                playlist_dict = ydl.extract_info(url, download=False)
                
                if not playlist_dict:
                    self.error_handler.log_error("Empty playlist dict", "Không lấy được thông tin playlist")
                    return None
                    
                self.error_handler.log_info(f"Đã lấy được thông tin: {playlist_dict.get('title', 'Unknown')}")
                
                result = {
                    'id': playlist_dict.get('id'),
                    'title': playlist_dict.get('title'),
                    'channel': playlist_dict.get('channel', playlist_dict.get('uploader', '')),
                    'channel_id': playlist_dict.get('channel_id', playlist_dict.get('uploader_id', ''))
                }
                self.error_handler.log_info(f"Đã xử lý xong thông tin playlist: {result}")
                return result
                
        except Exception as e:
            self.error_handler.log_error("Playlist Info Extraction Error", str(e), {
                "url": url,
                "error_type": type(e).__name__,
                "error_details": str(e)
            })
            return None

    def extract_playlist_id(self, url: str) -> str:
        """Trích xuất ID của playlist từ URL"""
        try:
            parsed_url = urlparse(url)
            playlist_id = parse_qs(parsed_url.query)['list'][0]
            self.error_handler.log_info(f"Extracted playlist ID: {playlist_id}")
            return playlist_id
        except Exception as e:
            self.error_handler.log_error("Playlist ID Extraction Error", str(e), {"url": url})
            return None

    def get_playlist_videos(self, url: str) -> list:
        """Lấy danh sách các video từ playlist"""
        try:
            self.error_handler.log_info(f"Bắt đầu tải thông tin playlist: {url}")
            
            # Cấu hình chi tiết cho yt-dlp
            ydl_opts = {
                'quiet': False,  # Hiện output để debug
                'extract_flat': True,
                'force_generic_extractor': False,  # Thử dùng extractor mặc định trước
                'ignoreerrors': True,  # Bỏ qua video lỗi
                'no_warnings': False,
                'verbose': True
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    self.error_handler.log_info("Đang trích xuất thông tin playlist...")
                    playlist_dict = ydl.extract_info(url, download=False)
                    
                    if not playlist_dict:
                        self.error_handler.log_error("Playlist Info Error", "Không thể tải thông tin playlist")
                        return []
                    
                    self.error_handler.log_info(f"Đã tải thông tin playlist: {playlist_dict.get('title', 'Unknown')}")
                    
                    if 'entries' not in playlist_dict:
                        self.error_handler.log_error("Playlist Structure Error", 
                            f"Không tìm thấy danh sách video. Keys có sẵn: {list(playlist_dict.keys())}")
                        return []
                    
                    videos = []
                    entries = playlist_dict['entries']
                    
                    if not entries:
                        self.error_handler.log_error("Empty Playlist", "Playlist không có video nào")
                        return []
                    
                    for entry in entries:
                        if entry:
                            video_data = {
                                'video_id': entry.get('id'),
                                'title': entry.get('title'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'duration': entry.get('duration'),
                                'download_date': None,
                                'status': 'pending'
                            }
                            self.error_handler.log_info(f"Đã tìm thấy video: {video_data['title']}")
                            videos.append(video_data)
                        else:
                            self.error_handler.log_warning("Bỏ qua entry rỗng trong playlist")
                    
                    self.error_handler.log_info(f"Tổng cộng: {len(videos)} video trong playlist")
                    return videos
                    
                except Exception as e:
                    self.error_handler.log_error("YouTube-DL Error", 
                        f"Lỗi khi xử lý playlist: {str(e)}", 
                        {"url": url, "error_type": type(e).__name__}
                    )
                    return []
                    
        except Exception as e:
            self.error_handler.log_error("Playlist Video Extraction Error", str(e), {
                "url": url,
                "error_type": type(e).__name__,
                "error_details": str(e)
            })
            return []

    def extract_video_id(self, url: str) -> str:
        """Trích xuất video ID từ URL"""
        try:
            # Xử lý các dạng URL khác nhau
            if 'youtu.be' in url:
                return url.split('/')[-1].split('?')[0]
            elif 'youtube.com/watch' in url:
                parsed_url = urlparse(url)
                return parse_qs(parsed_url.query)['v'][0]
            else:
                self.error_handler.log_error("Invalid URL", "URL không phải là video YouTube")
                return None
        except Exception as e:
            self.error_handler.log_error("Video ID Extraction Error", str(e), {"url": url})
            return None

    def get_video_info(self, url: str) -> dict:
        """Lấy thông tin của video đơn lẻ"""
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                video_dict = ydl.extract_info(url, download=False)
                if not video_dict:
                    return None
                    
                return {
                    'id': video_dict.get('id'),
                    'title': video_dict.get('title'),
                    'channel': video_dict.get('channel', video_dict.get('uploader', '')),
                    'duration': video_dict.get('duration')
                }
        except Exception as e:
            self.error_handler.log_error("Video Info Extraction Error", str(e), {"url": url})
            return None