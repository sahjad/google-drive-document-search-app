from app.connectors.drive_connector import GoogleDriveConnector
from app.extractors.txt_extractor import TxtExtractor
from app.extractors.csv_extractor import CsvExtractor
from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.png_extractor import PngExtractor

def run_extraction_tests():
    drive = GoogleDriveConnector()
    files = drive.list_supported_files()

    for file in files:
        file_id = file['id']
        name = file['name']
        mime = file['mimeType']
        print(f"\nTesting: {name} ({mime})")

        stream = drive.download_file(file_id)

        if mime == "text/plain":
            extractor = TxtExtractor()
        elif mime == "text/csv":
            extractor = CsvExtractor()
        elif mime == "application/pdf":
            extractor = PdfExtractor()
        elif mime == "image/png":
            extractor = PngExtractor()
        else:
            print("Unsupported type - skipping")
            continue

        try:
            content = extractor.extract_text(stream)
            print(f"Extracted Content (first 300 chars):\n{content[:300]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_extraction_tests()