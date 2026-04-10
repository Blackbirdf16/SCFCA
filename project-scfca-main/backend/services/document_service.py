"""Document handling service.

SR-12 / SR-18: Evidence handling with integrity.
- PDF-only uploads.
- Server computes SHA-256 and stores metadata.
- Integrity verification recomputes hash from stored bytes.

PoC uses in-memory storage; replace with durable object store in production.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


def _utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    content_type: str
    sha256_hex: str
    created_at: str
    ticket_id: str | None
    case_id: str | None
    uploader: str


class DocumentStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._docs: dict[str, Document] = {}
        self._bytes: dict[str, bytes] = {}

    def _next_id(self) -> str:
        return f"DOC-{100 + len(self._docs) + 1}"

    def create(
        self,
        *,
        filename: str,
        content_type: str,
        content: bytes,
        uploader: str,
        case_id: str | None,
        ticket_id: str | None,
    ) -> Document:
        digest = sha256(content).hexdigest()
        with self._lock:
            doc_id = self._next_id()
            doc = Document(
                id=doc_id,
                filename=filename,
                content_type=content_type,
                sha256_hex=digest,
                created_at=_utc_date(),
                ticket_id=ticket_id,
                case_id=case_id,
                uploader=uploader,
            )
            self._docs[doc_id] = doc
            self._bytes[doc_id] = content
            return doc

    def list(self) -> list[Document]:
        with self._lock:
            # newest first (by insertion id order is ok for PoC)
            return list(reversed(list(self._docs.values())))

    def get(self, doc_id: str) -> Document | None:
        key = (doc_id or "").strip()
        with self._lock:
            return self._docs.get(key)

    def verify(self, doc_id: str) -> dict[str, Any]:
        with self._lock:
            doc = self._docs.get(doc_id)
            content = self._bytes.get(doc_id)
        if not doc or content is None:
            return {"ok": False, "reason": "not_found"}

        recomputed = sha256(content).hexdigest()
        ok = recomputed == doc.sha256_hex
        return {
            "ok": ok,
            "documentId": doc.id,
            "expected": doc.sha256_hex,
            "actual": recomputed,
        }


DOCUMENT_STORE = DocumentStore()
