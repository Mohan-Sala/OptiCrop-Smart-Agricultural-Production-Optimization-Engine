import anyio
from app.storage.supabase import get_storage_client
from app.core.config import settings


class StorageService:
    """Wraps Supabase Object Storage operations inside async thread pool executions."""

    def __init__(self, bucket_name: str = "datasets"):
        # Resolves dynamic bucket override config from settings
        self.bucket_name = settings.STORAGE_BUCKET or bucket_name

    async def upload_file(self, storage_path: str, file_path: str, content_type: str = "text/csv") -> str:
        """Pushes a local file binary up to the Supabase storage bucket."""
        storage_client = get_storage_client()
        
        def _upload():
            with open(file_path, "rb") as f:
                options = {"content-type": content_type, "x-upsert": "false"}
                storage_client.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=f,
                    file_options=options
                )
            return storage_path

        return await anyio.to_thread.run_sync(_upload)

    async def download_file(self, storage_path: str) -> bytes:
        """Retrieves raw file bytes from Supabase storage."""
        storage_client = get_storage_client()
        
        def _download():
            return storage_client.from_(self.bucket_name).download(storage_path)

        return await anyio.to_thread.run_sync(_download)

    async def delete_file(self, storage_path: str) -> None:
        """Removes an object from the Supabase storage bucket."""
        storage_client = get_storage_client()
        
        def _delete():
            storage_client.from_(self.bucket_name).remove(storage_path)

        await anyio.to_thread.run_sync(_delete)
