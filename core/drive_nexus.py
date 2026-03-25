"""
Google Drive Nexus Bridge
==========================
Mounts the '12 Districts' folder structure from Google Drive and streams
file metadata and content directly into the brain RAG layer.

Authentication
--------------
Set the ``DRIVE_SERVICE_KEY`` environment variable to the **base64-encoded**
JSON of a Google service-account key that has read access to the Drive.
Alternatively set ``GOOGLE_CREDENTIALS_B64`` (legacy name) as a fallback.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import os
from typing import Any, Generator

logger = logging.getLogger(__name__)

# MIME types that can be streamed as plain text
_TEXT_MIME_TYPES: frozenset[str] = frozenset(
    {
        "text/plain",
        "application/json",
        "text/csv",
        "text/markdown",
        "application/x-python",
        "text/x-python",
    }
)

# Google Workspace mime types that can be exported as plain text
_EXPORT_MIME_MAP: dict[str, str] = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
}

# Name of the top-level Districts folder to search for
DISTRICTS_FOLDER_NAME: str = os.getenv("DISTRICTS_FOLDER_NAME", "12 Districts")


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _get_credentials():
    """
    Build a ``google.oauth2.service_account.Credentials`` object from the
    base64-encoded service-account JSON stored in ``DRIVE_SERVICE_KEY``
    (or the legacy ``GOOGLE_CREDENTIALS_B64`` fallback).

    Raises
    ------
    EnvironmentError
        If neither environment variable is set.
    """
    from google.oauth2 import service_account  # type: ignore[import]

    raw_b64 = os.getenv("DRIVE_SERVICE_KEY") or os.getenv("GOOGLE_CREDENTIALS_B64")
    if not raw_b64:
        raise EnvironmentError(
            "DRIVE_SERVICE_KEY (or GOOGLE_CREDENTIALS_B64) environment variable is not set. "
            "Provide a base64-encoded Google service-account JSON key."
        )

    creds_json = base64.b64decode(raw_b64).decode("utf-8")
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    return service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)


# ---------------------------------------------------------------------------
# Drive helpers
# ---------------------------------------------------------------------------

def build_drive_service():
    """Return an authenticated Google Drive v3 service object."""
    from googleapiclient.discovery import build  # type: ignore[import]

    creds = _get_credentials()
    return build("drive", "v3", credentials=creds)


def _find_folder(service, name: str, parent_id: str | None = None) -> str | None:
    """
    Return the Drive ID of the first folder named *name*.
    Optionally restrict the search to *parent_id*.
    """
    query_parts = [
        f"name='{name}'",
        "mimeType='application/vnd.google-apps.folder'",
        "trashed=false",
    ]
    if parent_id:
        query_parts.append(f"'{parent_id}' in parents")

    result = (
        service.files()
        .list(q=" and ".join(query_parts), fields="files(id, name)", pageSize=5)
        .execute()
    )
    files = result.get("files", [])
    if files:
        return files[0]["id"]
    return None


def _list_files(service, folder_id: str) -> list[dict[str, Any]]:
    """Return all non-trashed files directly inside *folder_id*."""
    items: list[dict[str, Any]] = []
    page_token: str | None = None

    while True:
        kwargs: dict[str, Any] = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "nextPageToken, files(id, name, mimeType, size, modifiedTime)",
            "pageSize": 100,
        }
        if page_token:
            kwargs["pageToken"] = page_token

        result = service.files().list(**kwargs).execute()
        items.extend(result.get("files", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return items


def _read_file_content(service, file_meta: dict[str, Any]) -> str | None:
    """
    Download or export a Drive file and return its content as a string.
    Returns *None* for binary or unsupported file types.
    """
    from googleapiclient.http import MediaIoBaseDownload  # type: ignore[import]

    mime = file_meta.get("mimeType", "")

    # Google Workspace docs need to be exported
    if mime in _EXPORT_MIME_MAP:
        export_mime = _EXPORT_MIME_MAP[mime]
        fh = io.BytesIO()
        request = service.files().export_media(
            fileId=file_meta["id"], mimeType=export_mime
        )
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return fh.getvalue().decode("utf-8", errors="replace")

    # Plain text / JSON files can be downloaded directly
    if mime in _TEXT_MIME_TYPES or mime.startswith("text/"):
        fh = io.BytesIO()
        request = service.files().get_media(fileId=file_meta["id"])
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return fh.getvalue().decode("utf-8", errors="replace")

    return None  # Binary / unsupported


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def stream_districts(
    service=None,
    folder_name: str = DISTRICTS_FOLDER_NAME,
) -> Generator[dict[str, Any], None, None]:
    """
    Locate the '12 Districts' folder and yield one record per file found.

    Each record is a dict with keys:
        ``file_id``, ``name``, ``mime_type``, ``modified_time``, ``content``

    *content* is a plain-text string when available, or ``None`` for binary
    files that cannot be streamed as text.

    Parameters
    ----------
    service:
        An authenticated Drive service object.  Constructed automatically
        when omitted.
    folder_name:
        Name of the top-level folder to search for (default ``"12 Districts"``
        or value of ``DISTRICTS_FOLDER_NAME`` env var).
    """
    if service is None:
        service = build_drive_service()

    folder_id = _find_folder(service, folder_name)
    if folder_id is None:
        logger.warning(
            "Nexus: folder '%s' not found in Drive. Nothing streamed.", folder_name
        )
        return

    logger.info("Nexus: found folder '%s' (%s). Streaming files…", folder_name, folder_id)
    files = _list_files(service, folder_id)
    logger.info("Nexus: %d files to process.", len(files))

    for file_meta in files:
        content = _read_file_content(service, file_meta)
        yield {
            "file_id": file_meta["id"],
            "name": file_meta["name"],
            "mime_type": file_meta.get("mimeType", ""),
            "modified_time": file_meta.get("modifiedTime", ""),
            "content": content,
        }


def ingest_into_brain(service=None, folder_name: str = DISTRICTS_FOLDER_NAME) -> int:
    """
    Stream all readable files from the Districts folder into the brain vault.

    Returns the total number of text chunks indexed.
    """
    from brain.indexer import get_collection, index_text  # local import to avoid circular

    collection = get_collection()
    total_chunks = 0

    for record in stream_districts(service=service, folder_name=folder_name):
        if record["content"] is None:
            logger.debug("Nexus: skipping binary file '%s'", record["name"])
            continue

        source_label = f"drive::{record['file_id']}::{record['name']}"
        extra = {
            "drive_file_id": record["file_id"],
            "drive_name": record["name"],
            "mime_type": record["mime_type"],
            "modified_time": record["modified_time"],
        }
        chunks = index_text(collection, record["content"], source_label, extra)
        total_chunks += chunks

    logger.info("Nexus: ingestion complete — %d chunks committed to brain.", total_chunks)
    return total_chunks
