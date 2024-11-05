import json
import os
import re
from datetime import datetime
from ..utils.error_handler import ErrorHandler



class DataStorage:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        self._ensure_directories()

    def _ensure_directories(self):
        """Đảm bảo các thư mục cần thiết tồn tại"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            self.error_handler.log_info(f"Created data directory at {self.base_path}")

    def _sanitize_filename(self, filename: str, max_length: int = 70) -> str:
        """
        Xử lý tên file để tránh các ký tự không hợp lệ và giới hạn độ dài
        Args:
            filename: Tên file gốc
            max_length: Độ dài tối đa cho phép (mặc định 50 ký tự)
        """
        # Loại bỏ các ký tự không hợp lệ
        filename = re.sub(r'[\\/*?:"<>|]', "-", filename)
        
        # Loại bỏ khoảng trắng thừa
        filename = " ".join(filename.split())
        
        # Nếu tên quá dài, cắt bớt và thêm dấu ...
        if len(filename) > max_length:
            name_part = filename[:(max_length-3)]
            # Đảm bảo không cắt giữa từ
            last_space = name_part.rfind(" ")
            if last_space > 0:
                name_part = name_part[:last_space]
            filename = f"{name_part}..."
        
        return filename

    def create_playlist_directory(self, playlist_id: str) -> tuple:
        """Tạo thư mục cho playlist và các thư mục con"""
        # Tạo thư mục gốc cho playlist
        playlist_path = os.path.join(self.base_path, 'playlists', playlist_id)
        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)
            
        # Tạo thư mục con cho JSON
        json_path = os.path.join(playlist_path, 'json')
        if not os.path.exists(json_path):
            os.makedirs(json_path)
            
        # Tạo thư mục con cho TXT
        txt_path = os.path.join(playlist_path, 'txt')
        if not os.path.exists(txt_path):
            os.makedirs(txt_path)
            
        self.error_handler.log_info(f"Created directory structure at {playlist_path}")
        return playlist_path, json_path, txt_path

    def _create_text_content(self, transcript_data: dict) -> str:
        """Tạo nội dung cho file text từ transcript data"""
        text_content = []
        
        # Thêm metadata
        text_content.append(f"Video ID: {transcript_data['video_id']}")
        text_content.append(f"Title: {transcript_data['title']}")
        text_content.append(f"Language: {transcript_data['metadata']['language']}")
        text_content.append(f"Language Name: {transcript_data['metadata']['language_name']}")
        text_content.append(f"Download Date: {transcript_data['metadata']['download_date']}")
        text_content.append("\nTranscript:\n")
        
        # Thêm transcript
        for entry in transcript_data['transcript']:
            timestamp = f"[{int(entry['start']//60):02d}:{int(entry['start']%60):02d}]"
            text_content.append(f"{timestamp} {entry['text']}")
        
        return '\n'.join(text_content)

    def save_transcript(self, playlist_id: str, video_id: str, video_title: str, transcript_data: dict):
        """Lưu transcript vào cả file JSON và TXT"""
        try:
            # Tạo các thư mục cần thiết
            _, json_path, txt_path = self.create_playlist_directory(playlist_id)
            
            # Tạo tên file cơ bản
            base_filename = f"{self._sanitize_filename(video_title, 30)}_{video_id}"
            
            # Đảm bảo transcript_data có đầy đủ thông tin
            if 'title' not in transcript_data:
                transcript_data['title'] = video_title
            
            # Lưu file JSON với đầy đủ thông tin
            json_file_path = os.path.join(json_path, f"{base_filename}.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            # Tạo và lưu file TXT với đầy đủ thông tin
            txt_content = self._create_text_content(transcript_data)
            txt_file_path = os.path.join(txt_path, f"{base_filename}.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            
            self.error_handler.log_info(f"Saved transcript for video {video_id} - {video_title} in both JSON and TXT formats")
            return True
        except Exception as e:
            self.error_handler.log_error("Storage Error", str(e), {
                "playlist_id": playlist_id,
                "video_id": video_id,
                "video_title": video_title
            })
            return False

    def save_metadata(self, playlist_id: str, metadata: dict):
        """Lưu metadata của playlist"""
        try:
            playlist_path, _, _ = self.create_playlist_directory(playlist_id)
            file_path = os.path.join(playlist_path, "metadata.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.error_handler.log_info(f"Saved metadata for playlist {playlist_id}")
            return True
        except Exception as e:
            self.error_handler.log_error("Metadata Storage Error", str(e), {
                "playlist_id": playlist_id
            })
            return False