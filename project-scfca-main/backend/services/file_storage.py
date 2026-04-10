"""Filesystem-backed file storage for SCFCA documents.

Stores PDF bytes on local disk at a configurable base path.
Interface is designed to be swappable for S3/GCS in production.

NFR-4: Long-term data retention.
SR-16: Integrity verification reads bytes from this store.
"""

from __future__ import annotations

from pathlib import Path


class FileStorage:
    """Store and retrieve file bytes on the local filesystem."""

    def __init__(self, base_path: str = "data/documents") -> None:
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)

    def _path_for(self, doc_id: str) -> Path:
        return self._base / f"{doc_id}.pdf"

    def save(self, doc_id: str, content: bytes) -> Path:
        """Write file bytes to disk. Returns the full path."""
        path = self._path_for(doc_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def load(self, doc_id: str) -> bytes | None:
        """Read file bytes from disk. Returns None if not found."""
        path = self._path_for(doc_id)
        if not path.exists():
            return None
        return path.read_bytes()

    def exists(self, doc_id: str) -> bool:
        return self._path_for(doc_id).exists()

    def delete(self, doc_id: str) -> bool:
        """Remove file from disk. Returns True if deleted."""
        path = self._path_for(doc_id)
        if path.exists():
            path.unlink()
            return True
        return False


# Module-level singleton. Tests can override with a temp directory.
FILE_STORAGE = FileStorage()
