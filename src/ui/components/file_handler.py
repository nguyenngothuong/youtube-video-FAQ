import os
import zipfile
import io
import re

class FileHandler:
    def __init__(self, data_storage):
        self.data_storage = data_storage

    def create_zip_file(self, playlist_id: str) -> bytes:
        """Tạo file ZIP từ các file transcript"""
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            playlist_path = os.path.join(self.data_storage.base_path, 'playlists', playlist_id)
            
            for folder in ['json', 'txt']:
                folder_path = os.path.join(playlist_path, folder)
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, file)
                        arcname = os.path.join(folder, file)
                        zf.write(file_path, arcname)
                
            metadata_path = os.path.join(playlist_path, 'metadata.json')
            if os.path.exists(metadata_path):
                zf.write(metadata_path, 'metadata.json')
        
        memory_file.seek(0)
        return memory_file.getvalue()

    def generate_filename(self, channel_name: str, playlist_title: str, playlist_id: str) -> str:
        """Tạo tên file ZIP"""
        def clean_text(text):
            text = re.sub(r'[\\/*?:"<>|]', "-", text)
            text = re.sub(r'\s+', "_", text)
            text = re.sub(r'[^\w\-_]', "", text)
            return text.strip()
        
        channel_name = clean_text(channel_name)
        playlist_title = clean_text(playlist_title)
        playlist_id = clean_text(playlist_id)
        
        if channel_name:
            return f"{channel_name}_{playlist_title}_{playlist_id}.zip"
        return f"{playlist_title}_{playlist_id}.zip" 