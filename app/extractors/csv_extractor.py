# .csv file extractor logic

import pandas as pd
from io import BytesIO
from app.extractors.base_extractor import BaseExtractor

class CsvExtractor(BaseExtractor):
    def extract_text(self, file_stream: BytesIO) -> str:
        try:
            df = pd.read_csv(file_stream)
            return df.to_string(index=False)
        except Exception as e:
            print(f"[CSVExtractor] Error reading CSV content: {e}")
            return ""