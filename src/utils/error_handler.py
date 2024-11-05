import logging
import os
import sys
from datetime import datetime

class ErrorHandler:
    # Tạo một biến class để lưu instance duy nhất
    _instance = None
    _initialized = False
    
    def __new__(cls):
        # Singleton pattern - đảm bảo chỉ có một instance của ErrorHandler
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Chỉ khởi tạo một lần
        if not ErrorHandler._initialized:
            # Tạo thư mục logs nếu chưa tồn tại
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
                
            # Thiết lập logging với encoding UTF-8
            log_filename = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            
            # Tạo logger
            self.logger = logging.getLogger('youtube_transcript_extractor')
            self.logger.setLevel(logging.DEBUG)
            
            # Xóa handlers cũ nếu có
            if self.logger.hasHandlers():
                self.logger.handlers.clear()
            
            # Tạo file handler với encoding UTF-8
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            
            # Tạo console handler với encoding UTF-8
            console_handler = logging.StreamHandler(sys.stdout)
            
            # Định dạng log
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Thêm handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # Đảm bảo không có handlers trùng lặp
            self.logger.propagate = False
            
            ErrorHandler._initialized = True

    def log_error(self, error_type: str, error_message: str, extra_info: dict = None):
        """Ghi log lỗi với thông tin chi tiết"""
        try:
            self.logger.error(f"Error Type: {error_type}")
            self.logger.error(f"Error Message: {error_message}")
            if extra_info:
                self.logger.error(f"Additional Info: {extra_info}")
        except Exception as e:
            print(f"Logging error: {str(e)}")

    def log_warning(self, message: str):
        """Ghi log cảnh báo"""
        try:
            self.logger.warning(message)
        except Exception as e:
            print(f"Logging warning error: {str(e)}")

    def log_info(self, message: str):
        """Ghi log thông tin"""
        try:
            self.logger.info(message)
        except Exception as e:
            print(f"Logging info error: {str(e)}")

    def log_debug(self, message: str):
        """Ghi log debug"""
        try:
            self.logger.debug(message)
        except Exception as e:
            print(f"Logging debug error: {str(e)}") 