# .pdf file extractor logic

from io import BytesIO
from PyPDF2 import PdfReader
from app.extractors.base_extractor import BaseExtractor

class PdfExtractor(BaseExtractor):
    def extract_text(self, file_stream: BytesIO) -> str:
        try:
            reader = PdfReader(file_stream)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        except Exception as e:
            print(f"[PdfExtractor] Error reading PDF: {e}")
            return ""