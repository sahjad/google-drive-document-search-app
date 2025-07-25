# .txt file extractor logic

from io import BytesIO
from app.extractors.base_extractor import BaseExtractor

class TxtExtractor(BaseExtractor):
    def extract_text(self, file_stream: BytesIO) -> str:
        try:
            return file_stream.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[TxtExtractor] Error reading TXT content: {e}")
            return ""