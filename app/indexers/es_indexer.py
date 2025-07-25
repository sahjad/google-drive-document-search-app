# Elasticsearch indexer 
# This module provides functionality to index, delete, and search documents in an Elasticsearch index.

from elasticsearch import Elasticsearch, helpers
import os

import warnings
from elasticsearch import ElasticsearchWarning
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

class ElasticsearchIndexer:
    def __init__(self, index_name="documents"):
        self.index_name = index_name
        try:
            self.client = Elasticsearch("http://localhost:9200")
            self._ensure_index_exists()
        except Exception as e:
            print(f"[es_indexer] Initialization failed: {e}")
            raise

    def _ensure_index_exists(self):
        try:
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(index=self.index_name)
        except Exception as e:
            print(f"[es_indexer] Failed to ensure index exists: {e}")
            raise

    def index_document(self, doc_id: str, document: dict):
        try:
            self.client.index(index=self.index_name, id=doc_id, document=document)
        except Exception as e:
            print(f"[es_indexer] Failed to index document {doc_id}: {e}")

    def delete_document(self, doc_id: str):
        try:
            self.client.delete(index=self.index_name, id=doc_id, ignore=[404])
        except Exception as e:
            print(f"[es_indexer] Failed to delete document {doc_id}: {e}")

    def search(self, query: str):
        try:
            response = self.client.search(
                index=self.index_name,
                query={
                    "match": {
                        "content": query
                    }
                },
                size=10000
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            print(f"[es_indexer] Search failed for query '{query}': {e}")
            return []
    
    def get_indexed_metadata(self):
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "query": {"match_all": {}},
                    "_source": ["modified"]
                },
                size=10000
            )
            return {
                hit["_id"]: hit["_source"].get("modified")
                for hit in response["hits"]["hits"]
            }
        except Exception as e:
            print(f"[es_indexer] Failed to fetch indexed metadata: {e}")
            return {}
