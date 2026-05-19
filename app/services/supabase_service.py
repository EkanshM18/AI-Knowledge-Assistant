from __future__ import annotations
import uuid
from supabase import create_client, Client
from app.core.config import settings

class SupabaseStorageService:
    """Service to handle file operations with Supabase Storage."""
    
    def __init__(self):
        # Use service role key to bypass RLS for ingestion purposes
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """
        Uploads a file to the enterprise-documents bucket.
        Returns the unique storage path.
        """
        unique_id = str(uuid.uuid4())
        storage_path = f"vault/{unique_id}/{filename}"
        
        self.client.storage.from_(self.bucket_name).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        return storage_path

    def get_file_bytes(self, storage_path: str) -> bytes:
        """Downloads the file content as bytes for LlamaIndex processing."""
        return self.client.storage.from_(self.bucket_name).download(storage_path)

    def delete_file(self, storage_path: str):
        """Removes the file from cloud storage."""
        self.client.storage.from_(self.bucket_name).remove([storage_path])