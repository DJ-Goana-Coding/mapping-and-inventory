"""
HuggingFace Garage Sync — Task 4: '20GB Garage' Model Sync
============================================================
Crawls the ``DJ-Goana`` HuggingFace profile and maps all Models, Datasets,
and Spaces.  Missing assets are *appended* to ``Master_Garage_Inventory.json``
without overwriting any existing entries.

Authentication
--------------
Set the ``HUGGINGFACE_TOKEN`` environment variable (or the legacy ``HF_TOKEN``
fallback) to a HuggingFace access token with read permissions.
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# HuggingFace user / organisation to crawl
HF_USER: str = os.getenv("HF_USER", "DJ-Goana")

# Path to the garage inventory relative to the repo root
_REPO_ROOT = pathlib.Path(__file__).parent.parent
GARAGE_INVENTORY_PATH: pathlib.Path = _REPO_ROOT / "Master_Garage_Inventory.json"


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _get_hf_token() -> str | None:
    """Return the HuggingFace access token from the environment."""
    return os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")


def _build_api():
    """Return an authenticated HfApi instance."""
    from huggingface_hub import HfApi  # type: ignore[import]

    token = _get_hf_token()
    if not token:
        raise EnvironmentError(
            "HUGGINGFACE_TOKEN (or HF_TOKEN) environment variable is not set. "
            "Provide a HuggingFace read-access token."
        )
    return HfApi(token=token)


# ---------------------------------------------------------------------------
# Profile crawl helpers
# ---------------------------------------------------------------------------

def _list_models(api, user: str) -> list[dict[str, Any]]:
    """Return a list of model asset dicts for *user*."""
    try:
        models = list(api.list_models(author=user))
    except Exception as exc:
        logger.warning("HF Garage: could not list models for '%s': %s", user, exc)
        return []

    results = []
    for m in models:
        results.append(
            {
                "asset_type": "model",
                "id": getattr(m, "id", ""),
                "name": getattr(m, "modelId", None) or getattr(m, "id", ""),
                "private": getattr(m, "private", False),
                "pipeline_tag": getattr(m, "pipeline_tag", None),
                "tags": list(getattr(m, "tags", []) or []),
                "last_modified": str(getattr(m, "lastModified", "") or ""),
                "downloads": getattr(m, "downloads", 0),
                "likes": getattr(m, "likes", 0),
                "sha": getattr(m, "sha", None),
            }
        )
    return results


def _list_datasets(api, user: str) -> list[dict[str, Any]]:
    """Return a list of dataset asset dicts for *user*."""
    try:
        datasets = list(api.list_datasets(author=user))
    except Exception as exc:
        logger.warning("HF Garage: could not list datasets for '%s': %s", user, exc)
        return []

    results = []
    for d in datasets:
        results.append(
            {
                "asset_type": "dataset",
                "id": getattr(d, "id", ""),
                "name": getattr(d, "id", ""),
                "private": getattr(d, "private", False),
                "tags": list(getattr(d, "tags", []) or []),
                "last_modified": str(getattr(d, "lastModified", "") or ""),
                "downloads": getattr(d, "downloads", 0),
                "likes": getattr(d, "likes", 0),
            }
        )
    return results


def _list_spaces(api, user: str) -> list[dict[str, Any]]:
    """Return a list of Space asset dicts for *user*."""
    try:
        spaces = list(api.list_spaces(author=user))
    except Exception as exc:
        logger.warning("HF Garage: could not list spaces for '%s': %s", user, exc)
        return []

    results = []
    for s in spaces:
        results.append(
            {
                "asset_type": "space",
                "id": getattr(s, "id", ""),
                "name": getattr(s, "id", ""),
                "private": getattr(s, "private", False),
                "sdk": getattr(s, "sdk", None),
                "tags": list(getattr(s, "tags", []) or []),
                "last_modified": str(getattr(s, "lastModified", "") or ""),
                "likes": getattr(s, "likes", 0),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Inventory read / write helpers
# ---------------------------------------------------------------------------

def _load_inventory() -> dict[str, Any]:
    """Load the existing garage inventory JSON, or return an empty scaffold."""
    if GARAGE_INVENTORY_PATH.exists():
        try:
            with GARAGE_INVENTORY_PATH.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "HF Garage: could not parse existing inventory (%s). "
                "Will treat as empty.",
                exc,
            )
    return {"assets": [], "last_synced": None, "hf_user": HF_USER}


def _save_inventory(inventory: dict[str, Any]) -> None:
    """Persist the inventory dict to ``GARAGE_INVENTORY_PATH``."""
    GARAGE_INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with GARAGE_INVENTORY_PATH.open("w", encoding="utf-8") as fh:
        json.dump(inventory, fh, indent=2, default=str)
    logger.info("HF Garage: inventory saved to %s.", GARAGE_INVENTORY_PATH)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sync_garage(user: str = HF_USER) -> int:
    """
    Task 4 — Crawl the HuggingFace profile for *user* and append any missing
    assets to ``Master_Garage_Inventory.json``.

    Existing entries are **never overwritten** — only new assets (identified
    by their ``id`` field) are appended.

    Returns the number of new assets appended.
    """
    api = _build_api()

    logger.info("HF Garage: crawling profile '%s' (models, datasets, spaces)…", user)

    all_remote: list[dict[str, Any]] = (
        _list_models(api, user)
        + _list_datasets(api, user)
        + _list_spaces(api, user)
    )

    logger.info("HF Garage: found %d total assets on HuggingFace.", len(all_remote))

    inventory = _load_inventory()
    existing_assets: list[dict[str, Any]] = inventory.get("assets", [])

    # Build a set of existing asset IDs to detect duplicates efficiently.
    existing_ids: set[str] = {a.get("id", "") for a in existing_assets}

    new_assets: list[dict[str, Any]] = [
        asset for asset in all_remote if asset.get("id", "") not in existing_ids
    ]

    if new_assets:
        existing_assets.extend(new_assets)
        inventory["assets"] = existing_assets
        logger.info(
            "HF Garage: appending %d new assets (%d already present).",
            len(new_assets),
            len(existing_ids),
        )
    else:
        logger.info(
            "HF Garage: no new assets found — inventory is already up to date (%d entries).",
            len(existing_ids),
        )

    inventory["last_synced"] = datetime.now(timezone.utc).isoformat()
    inventory["hf_user"] = user
    inventory["total_assets"] = len(existing_assets)

    _save_inventory(inventory)

    # Also index the updated inventory into the brain vault (Task 5 cross-ref)
    try:
        from brain.indexer import get_collection, index_json_manifest

        col = get_collection()
        index_json_manifest(
            col,
            GARAGE_INVENTORY_PATH,
            source_label="hf_garage::Master_Garage_Inventory.json",
        )
        logger.info("HF Garage: inventory indexed into brain vault.")
    except Exception as exc:
        logger.warning("HF Garage: could not index inventory into brain vault: %s", exc)

    return len(new_assets)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    added = sync_garage()
    print(f"✅ HF Garage sync complete — {added} new assets appended.")
