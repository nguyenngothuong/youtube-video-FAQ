from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from ..utils.error_handler import ErrorHandler
from datetime import datetime

class TranscriptExtractor:
    def __init__(self):
        self.error_handler = ErrorHandler()
        # Định nghĩa các ngôn ngữ phổ biến
        self.common_languages = {
            'en': 'English',
            'vi': 'Vietnamese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh-Hans': 'Chinese (Simplified)',
            'zh-Hant': 'Chinese (Traditional)',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'ru': 'Russian'
        }

    def download_transcript(self, video_id: str, title: str, language_code: str = 'en') -> dict:
        """
        Tải transcript cho video
        Args:
            video_id: ID của video
            title: Tiêu đề video
            language_code: Mã ngôn ngữ cần tải
        """
        try:
            # Thử tải transcript với ngôn ngữ được chọn
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
            except NoTranscriptFound:
                # Nếu không tìm thấy, thử tải bản tiếng Anh và dịch
                if language_code != 'en':
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        transcript = transcript_list.find_transcript(['en']).translate(language_code).fetch()
                        self.error_handler.log_info(f"Đã dịch transcript từ tiếng Anh sang {language_code}")
                    except:
                        self.error_handler.log_warning(f"Không thể dịch transcript sang {language_code}")
                        raise
                else:
                    raise
            
            transcript_data = {
                "video_id": video_id,
                "title": title,
                "transcript": transcript,
                "metadata": {
                    "language": language_code,
                    "language_name": self.common_languages.get(language_code, language_code),
                    "download_date": datetime.now().isoformat()
                }
            }
            
            self.error_handler.log_info(f"Đã tải transcript cho video {video_id} - {title}")
            return transcript_data

        except NoTranscriptFound:
            self.error_handler.log_warning(f"Không tìm thấy phụ đề {language_code} cho video {title}")
            return None
        except TranscriptsDisabled:
            self.error_handler.log_warning(f"Video {title} đã tắt phụ đề")
            return None
        except Exception as e:
            self.error_handler.log_error("Lỗi tải transcript", str(e), {
                "video_id": video_id,
                "title": title,
                "language": language_code
            })
            return None