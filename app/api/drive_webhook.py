from fastapi import APIRouter, Request, HTTPException
from app.services.sync_service import SyncService

router = APIRouter()

@router.post("/drive-webhook")
async def drive_webhook(request: Request):
    try:
        headers = request.headers
        print("Google Drive Notification Received")
        print("X-Goog-Resource-State:", headers.get("X-Goog-Resource-State"))
        print("X-Goog-Changed:", headers.get("X-Goog-Changed"))

        # Trigger sync
        SyncService().sync()

        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook sync failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error during sync.")

# Google’s webhook validation
@router.get("/drive-webhook")
async def validate_webhook():
    try:
        return {"message": "Webhook endpoint is active."}
    except Exception as e:
        print(f"Webhook validation failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook validation error.")