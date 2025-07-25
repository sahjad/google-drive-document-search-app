from app.services.sync_service import SyncService

if __name__ == "__main__":
    syncer = SyncService()
    syncer.sync()