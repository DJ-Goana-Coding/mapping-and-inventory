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

# Binary MIME types that are ingested as *metadata-only* (no content download)
# to prevent repository / vault bloat while still preserving asset discoverability.
_BINARY_MIME_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "application/octet-stream",
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }
)

# File extensions that are treated as binary / large model assets.
# Content download is skipped; only file path + metadata is ingested.
_BINARY_EXTENSIONS: frozenset[str] = frozenset(
    {".bin", ".safetensors", ".pt", ".pth", ".ckpt", ".onnx", ".gguf", ".pkl", ".pdf"}
)

# Name of the top-level Districts folder to search for
DISTRICTS_FOLDER_NAME: str = os.getenv("DISTRICTS_FOLDER_NAME", "12 Districts")

# Task 3: Primary Citadel folder — "A1 - The Citadel and 12 Dimensional Districts"
CITADEL_FOLDER_NAME: str = os.getenv(
    "CITADEL_FOLDER_NAME", "A1 - The Citadel and 12 Dimensional Districts"
)


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


def _list_files_recursive(
    service,
    folder_id: str,
    folder_path: str = "",
    *,
    _depth: int = 0,
    _max_depth: int = 20,
) -> Generator[dict[str, Any], None, None]:
    """
    Recursively yield every non-trashed file under *folder_id*.

    Each yielded item is the Drive file metadata dict with an additional
    ``"folder_path"`` key indicating the virtual path within the Citadel.

    Sub-folders are traversed in-place; folder nodes themselves are *not*
    yielded (only their file children are).

    Parameters
    ----------
    service:
        Authenticated Drive v3 service object.
    folder_id:
        ID of the root folder to crawl.
    folder_path:
        Human-readable path prefix accumulated during recursion.
    _depth / _max_depth:
        Guard against infinite recursion in unusual Drive layouts.
    """
    if _depth > _max_depth:
        logger.warning("Nexus: max recursion depth reached at '%s'.", folder_path)
        return

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
        items: list[dict[str, Any]] = result.get("files", [])

        for item in items:
            child_path = "/".join([folder_path, item["name"]]) if folder_path else item["name"]
            if item.get("mimeType") == "application/vnd.google-apps.folder":
                # Recurse into sub-folder
                yield from _list_files_recursive(
                    service,
                    item["id"],
                    child_path,
                    _depth=_depth + 1,
                    _max_depth=_max_depth,
                )
            else:
                item["folder_path"] = child_path
                yield item

        page_token = result.get("nextPageToken")
        if not page_token:
            break


def _is_binary(file_meta: dict[str, Any]) -> bool:
    """
    Return *True* if the file should be treated as a large binary asset.
    Binary assets are ingested as metadata-only records to prevent vault bloat.
    """
    mime = file_meta.get("mimeType", "")
    name = file_meta.get("name", "")
    ext = os.path.splitext(name)[1].lower()
    return mime in _BINARY_MIME_TYPES or ext in _BINARY_EXTENSIONS


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


# ---------------------------------------------------------------------------
# Task 3: Citadel Recursive Vacuum
# ---------------------------------------------------------------------------

def stream_citadel(
    service=None,
    folder_name: str = CITADEL_FOLDER_NAME,
) -> Generator[dict[str, Any], None, None]:
    """
    Task 3 — '1TB Rack' Recursive Vacuum.

    Locate the Citadel folder ("A1 - The Citadel and 12 Dimensional Districts")
    in Drive, recursively traverse every sub-folder, and yield one record per
    file found.

    Each record contains:
        ``file_id``, ``name``, ``mime_type``, ``modified_time``,
        ``folder_path``, ``content``, ``metadata_only``

    * ``content`` is a plain-text string for code / doc / config files.
    * For large binaries (``.bin``, ``.safetensors``, ``.pdf``, media) only
      the file path and Drive metadata are captured (``metadata_only=True``,
      ``content=None``) to prevent vault bloat.

    Parameters
    ----------
    service:
        Authenticated Drive v3 service object.  Built automatically if omitted.
    folder_name:
        Top-level Citadel folder name (default ``CITADEL_FOLDER_NAME``).
    """
    if service is None:
        service = build_drive_service()

    folder_id = _find_folder(service, folder_name)
    if folder_id is None:
        logger.warning(
            "Nexus: Citadel folder '%s' not found in Drive. Nothing streamed.", folder_name
        )
        return

    logger.info(
        "Nexus: found Citadel folder '%s' (%s). Starting recursive vacuum…",
        folder_name,
        folder_id,
    )

    for file_meta in _list_files_recursive(service, folder_id, folder_name):
        is_binary = _is_binary(file_meta)
        content: str | None = None

        if not is_binary:
            content = _read_file_content(service, file_meta)

        yield {
            "file_id": file_meta["id"],
            "name": file_meta["name"],
            "mime_type": file_meta.get("mimeType", ""),
            "modified_time": file_meta.get("modifiedTime", ""),
            "size": file_meta.get("size"),
            "folder_path": file_meta.get("folder_path", file_meta["name"]),
            "content": content,
            "metadata_only": is_binary or content is None,
        }


def ingest_citadel(service=None, folder_name: str = CITADEL_FOLDER_NAME) -> int:
    """
    Task 3 — Recursively vacuum the Citadel Drive folder into the brain vault.

    * Text files (``.py``, ``.sh``, ``.md``, ``.txt``, ``.json``, ``.yaml``,
      ``.requirements``) — full content ingested.
    * Large binaries (``.bin``, ``.safetensors``, ``.pdf``, media) — only file
      path and Drive metadata ingested (``metadata_only`` flag set in record).

    Returns the total number of chunks committed to the vault.
    """
    from brain.indexer import get_collection, index_text  # local import to avoid circular

    collection = get_collection()
    total_chunks = 0

    for record in stream_citadel(service=service, folder_name=folder_name):
        source_label = f"citadel::{record['file_id']}::{record['folder_path']}"
        extra: dict[str, Any] = {
            "drive_file_id": record["file_id"],
            "drive_name": record["name"],
            "mime_type": record["mime_type"],
            "modified_time": record["modified_time"],
            "folder_path": record["folder_path"],
            "metadata_only": str(record["metadata_only"]),
        }
        if record["size"] is not None:
            extra["file_size_bytes"] = str(record["size"])

        if record["metadata_only"]:
            # Ingest a synthetic metadata summary so the file is discoverable
            # in the vault without bloating it with binary data.
            meta_text = (
                f"[BINARY ASSET — METADATA ONLY]\n"
                f"Name: {record['name']}\n"
                f"Path: {record['folder_path']}\n"
                f"MIME: {record['mime_type']}\n"
                f"Modified: {record['modified_time']}\n"
                f"Size: {record.get('size', 'unknown')} bytes\n"
                f"Drive ID: {record['file_id']}\n"
            )
            chunks = index_text(collection, meta_text, source_label, extra)
        else:
            content = record["content"] or ""
            if not content.strip():
                logger.debug("Nexus: empty content for '%s', skipping.", record["name"])
                continue
            chunks = index_text(collection, content, source_label, extra)

        total_chunks += chunks

    logger.info(
        "Nexus: Citadel recursive vacuum complete — %d chunks committed to brain.",
        total_chunks,
    )
    return total_chunks
