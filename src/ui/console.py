from colorama import init, Fore, Style
from tqdm import tqdm
from ..utils.error_handler import ErrorHandler


class ConsoleUI:
    def __init__(self):
        init()  # Khởi tạo colorama
        self.error_handler = ErrorHandler()

    def print_welcome(self):
        """In thông điệp chào mừng"""
        print(f"{Fore.CYAN}=== YouTube Playlist Transcript Extractor ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Enter 'quit' to exit at any time{Style.RESET_ALL}\n")

    def get_playlist_url(self) -> str:
        """Lấy URL playlist từ người dùng"""
        while True:
            url = input(f"{Fore.GREEN}Enter YouTube Playlist URL: {Style.RESET_ALL}").strip()
            if url.lower() == 'quit':
                return None
            if url:
                return url
            print(f"{Fore.RED}Please enter a valid URL{Style.RESET_ALL}")

    def get_language_preference(self) -> str:
        """Lấy ngôn ngữ ưu tiên từ người dùng"""
        language = input(f"{Fore.GREEN}Choose language (default: en): {Style.RESET_ALL}").strip()
        return language if language else 'en'

    def create_progress_bar(self, total: int, desc: str = "Processing"):
        """Tạo thanh tiến trình"""
        return tqdm(total=total, desc=desc, bar_format='{l_bar}{bar:30}{r_bar}')

    def print_success(self, message: str):
        """In thông báo thành công"""
        print(f"{Fore.GREEN}[SUCCESS] {message}{Style.RESET_ALL}")
        self.error_handler.log_info(f"Success: {message}")

    def print_error(self, message: str):
        """In thông báo lỗi"""
        print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")
        self.error_handler.log_error("UI Error", message)

    def print_warning(self, message: str):
        """In thông báo cảnh báo"""
        print(f"{Fore.YELLOW}[WARNING] {message}{Style.RESET_ALL}")
        self.error_handler.log_warning(message)

    def print_info(self, message: str):
        """In thông báo thông tin"""
        print(f"{Fore.CYAN}[INFO] {message}{Style.RESET_ALL}")
        self.error_handler.log_info(message) 