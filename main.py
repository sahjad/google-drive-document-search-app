import os
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.services.sync_service import SyncService

CREDENTIALS_PATH = 'config/credentials.json'

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Credentials file not found at {CREDENTIALS_PATH}. Exiting app.")
        sys.exit(0)
    print("Running initial sync...")
    try:
        syncer = SyncService()
        syncer.sync()
        print("Initial sync complete.")
    except Exception as e:
        print(f"Initial sync failed: {e}")
    yield

app = FastAPI(
    title="Document Search Service",
    description="Search documents stored in Google Drive by content.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api")
