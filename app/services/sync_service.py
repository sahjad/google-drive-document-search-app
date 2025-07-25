# This module handles synchronization between Google Drive and Elasticsearch index.
# It checks for new, modified, or deleted files and updates the index accordingly.

from app.connectors.drive_connector import GoogleDriveConnector
from app.extractors.txt_extractor import TxtExtractor
from app.extractors.csv_extractor import CsvExtractor
from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.png_extractor import PngExtractor
from app.indexers.es_indexer import ElasticsearchIndexer

MIME_TYPE_TO_EXTRACTOR = {
    "text/plain": TxtExtractor(),
    "text/csv": CsvExtractor(),
    "application/pdf": PdfExtractor(),
    "image/png": PngExtractor()
}

class SyncService:
    def __init__(self):
        self.drive = GoogleDriveConnector()
        self.indexer = ElasticsearchIndexer()
  
    def sync(self):
        try:
            files = self.drive.list_supported_files()
        except Exception as e:
            print(f"[sync_service] Failed to list files: {e}")
            return

        # Get current metadata from Google Drive
        current_dict = {
            file["id"]: file["modifiedTime"]
            for file in files
        }

        # Get all indexed metadata
        indexed_dict = self.indexer.get_indexed_metadata()
        indexed_ids = set(indexed_dict.keys())

        # If completely unchanged, skip sync
        if current_dict == indexed_dict:
            return

        # Handle deleted files
        if len(indexed_dict) > len(current_dict):
            deleted_ids = indexed_ids - set(current_dict.keys())
            for file_id in deleted_ids:
                self.indexer.delete_document(file_id)
            return

        # Handle new or modified files
        for file in files:
            file_id = file["id"]
            mime = file["mimeType"]
            modified = file["modifiedTime"]

            if file_id in indexed_dict and indexed_dict[file_id] == modified:
                continue

            try:
                stream = self.drive.download_file(file_id)
                extractor = MIME_TYPE_TO_EXTRACTOR.get(mime)
                if not extractor:
                    print(f"[sync_service] No extractor found for MIME type {mime}")
                    continue

                content = extractor.extract_text(stream)

                document = {
                    "file_name": f"{file.get('folder_name', '')}/{file['name']}".strip("/"),
                    "url": f"https://drive.google.com/file/d/{file_id}",
                    "content": content,
                    "modified": modified
                }

                self.indexer.index_document(file_id, document)
            except Exception as e:
                print(f"[sync_service] Failed to index {file.get('name', file_id)}: {e}")