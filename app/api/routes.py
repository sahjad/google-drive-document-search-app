# API routes for document search application

from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.services.sync_service import SyncService
from app.indexers.es_indexer import ElasticsearchIndexer
from app.api.drive_webhook import router as webhook_router

router = APIRouter()
router.include_router(webhook_router)


@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/sync")
def trigger_sync():
    try:
        syncer = SyncService()
        syncer.sync()
        return {"status": "Sync completed"}
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        raise HTTPException(status_code=500, detail="Sync failed due to server error.")

@router.get("/search", response_model=List[str])
def search_documents(q: str = Query(..., min_length=1)):    
    try:
        indexer = ElasticsearchIndexer()
        results = indexer.search(q)
        file_names = []
        for doc in results:
            file_names.append(doc["file_name"])
        return file_names
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed due to server error.")