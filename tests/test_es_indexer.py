from app.indexers.es_indexer import ElasticsearchIndexer

indexer = ElasticsearchIndexer()

# 1. Index a sample document
doc = {
    "file_name": "demo.txt",
    "content": "This is a sample document about Sahjad's project deadline.",
    "url": "https://drive.google.com/sample"
}

indexer.index_document(doc_id="demo123", document=doc)
print("Document indexed.")

# 2. Run a search
results = indexer.search("document")
print("Search results:")
if not results:
    print("No results found.")
else:
    for res in results:
        print(f"- {res['file_name']} → {res['content'][:50]}...")