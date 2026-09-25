import io
import logging
from typing import Optional
import anyio
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from app.database.mongodb import get_motor_database
from app.core.config import settings

logger = logging.getLogger("app.storage.gridfs")

# Configured GridFS bucket collections
BUCKETS = {
    "datasets": "datasets",
    "trained_models": "trained_models",
    "plots": "plots",
    "exports": "exports",
}


def get_gridfs_bucket(bucket_name: str = "fs") -> AsyncIOMotorGridFSBucket:
    """Returns an AsyncIOMotorGridFSBucket for the specified bucket namespace."""
    db = get_motor_database()
    return AsyncIOMotorGridFSBucket(db, bucket_name=bucket_name)


async def check_gridfs_connection() -> bool:
    """Verifies that MongoDB GridFS bucket storage is operational."""
    try:
        db = get_motor_database()
        # Ping the database to verify operational connectivity
        await db.command("ping")
        bucket = get_gridfs_bucket(settings.GRIDFS_DATASETS_BUCKET)
        # Attempt listing on bucket
        cursor = bucket.find({}).limit(1)
        await cursor.to_list(length=1)
        logger.debug("MongoDB GridFS health check succeeded.")
        return True
    except Exception as e:
        logger.error("MongoDB GridFS health check failed: %s", str(e))
        return False


class GridFSStorageService:
    """MongoDB GridFS storage service for object and binary storage."""

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or settings.GRIDFS_DATASETS_BUCKET or "fs"

    def _get_bucket(self) -> AsyncIOMotorGridFSBucket:
        return get_gridfs_bucket(self.bucket_name)

    async def upload_file(self, storage_path: str, file_path: str, content_type: str = "text/csv") -> str:
        """Uploads a local file into MongoDB GridFS under the given storage path / filename."""
        bucket = self._get_bucket()

        # Delete any existing file with the same filename to enforce upsert semantics
        await self.delete_file(storage_path)

        def _read_file():
            with open(file_path, "rb") as f:
                return f.read()

        file_bytes = await anyio.to_thread.run_sync(_read_file)
        
        # Upload bytes stream to GridFS
        file_stream = io.BytesIO(file_bytes)
        await bucket.upload_from_stream(
            filename=storage_path,
            source=file_stream,
            metadata={"contentType": content_type},
        )
        return storage_path

    async def upload_bytes(self, storage_path: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Uploads raw bytes directly into MongoDB GridFS."""
        bucket = self._get_bucket()
        await self.delete_file(storage_path)
        file_stream = io.BytesIO(data)
        await bucket.upload_from_stream(
            filename=storage_path,
            source=file_stream,
            metadata={"contentType": content_type},
        )
        return storage_path

    async def download_file(self, storage_path: str) -> bytes:
        """Retrieves raw file bytes from MongoDB GridFS by storage path / filename."""
        bucket = self._get_bucket()
        grid_out = await bucket.open_download_stream_by_name(storage_path)
        data = await grid_out.read()
        return data

    async def download_bytes(self, storage_path: str) -> bytes:
        """Alias for download_file returning raw bytes."""
        return await self.download_file(storage_path)

    async def delete_file(self, storage_path: str) -> None:
        """Removes all revisions of the specified file from MongoDB GridFS."""
        bucket = self._get_bucket()
        cursor = bucket.find({"filename": storage_path})
        async for grid_file in cursor:
            await bucket.delete(grid_file._id)
