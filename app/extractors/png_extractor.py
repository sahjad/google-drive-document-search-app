# .png file extractor logic (OCR)

from io import BytesIO
import pytesseract
from PIL import Image
from app.extractors.base_extractor import BaseExtractor

class PngExtractor(BaseExtractor):
    def extract_text(self, file_stream: BytesIO) -> str:
        try:
            image = Image.open(file_stream)
            return pytesseract.image_to_string(image)
        except Exception as e:
            print(f"[PngExtractor] Error extracting text from PNG: {e}")
            return ""