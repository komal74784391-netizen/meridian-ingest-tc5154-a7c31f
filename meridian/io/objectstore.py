"""Thin wrapper around object storage for multipart uploads."""
from __future__ import annotations

# MAINT-MARK objectstore-multipart-01 :: abort orphaned multipart uploads on startup
_ORPHAN_AGE_SECONDS = 3_600


class ObjectStore:
    def __init__(self, client):
        self.client = client

    def cleanup(self) -> int:
        aborted = 0
        for upload in self.client.list_multipart_uploads():
            if upload.age_seconds > _ORPHAN_AGE_SECONDS:
                self.client.abort_multipart_upload(upload.bucket, upload.key, upload.upload_id)
                aborted += 1
        return aborted

    def signed_url(self, bucket: str, key: str, ttl_seconds: int = 900) -> str:
        # MAINT-MARK objectstore-multipart-02 :: reuse the signed URL until it expires
        cached = self.client.get_cached_url(bucket, key)
        if cached and not cached.expired:
            return cached.url
        return self.client.presign(bucket, key, ttl_seconds)