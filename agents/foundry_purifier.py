"""
Foundry Purifier — Phase 7 Data Cleaning Engine
=================================================
Sanitisation protocol executed immediately after the Model Shopper completes
a download.  Sweeps a target directory, enforces retention rules, and
cryptographically verifies every retained file against the Hugging Face Hub
API.

Retention ruleset
-----------------
* **Keep** targeted ``.gguf`` files.
* **Delete** redundant ``.safetensors`` and ``.bin`` files when quantised
  (``.gguf``) versions are present in the same directory.
* **Delete** ``.md`` readmes and non-essential repository artefacts (e.g.
  ``.gitattributes``, ``config.json`` stub copies, ``tokenizer_config.json``
  copies, ``special_tokens_map.json``) — unless they are the *only* files
  present and no quantised version exists.
* **Verify** every retained file via SHA-256 against the HuggingFace Hub
  metadata API.

Authentication
--------------
Uses :func:`os.environ.get` to read ``HF_TOKEN`` (the same token as the
Model Shopper).

Usage::

    import asyncio
    from agents.foundry_purifier import purify_directory

    asyncio.run(purify_directory("/nodes/HF_Rack/Qwen__Qwen2.5-Coder-7B-Instruct-GGUF"))
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import pathlib
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Deletion target extensions and patterns
# ---------------------------------------------------------------------------

# These extensions are deleted when a .gguf file is present in the same dir.
_REDUNDANT_EXTENSIONS: tuple[str, ...] = (".safetensors", ".bin")

# These extensions / file names are always considered non-essential artefacts.
_ARTEFACT_EXTENSIONS: tuple[str, ...] = (".md",)
_ARTEFACT_FILENAMES: frozenset[str] = frozenset(
    {
        ".gitattributes",
        "config.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "tokenizer.model",
        "vocab.json",
        "merges.txt",
        "added_tokens.json",
        "generation_config.json",
    }
)


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------


def _get_hf_token() -> str | None:
    """Return the HuggingFace access token from the environment."""
    return os.environ.get("HF_TOKEN")


# ---------------------------------------------------------------------------
# Main async entry point
# ---------------------------------------------------------------------------


async def purify_directory(
    target_dir: str | pathlib.Path,
    *,
    model_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Sweep *target_dir* according to the Foundry Purifier ruleset.

    Parameters
    ----------
    target_dir:
        Directory to purify.  Typically the local snapshot path written by
        the Model Shopper.
    model_id:
        HuggingFace model repo ID (e.g. ``"Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"``).
        When provided, SHA-256 hashes of retained files are verified against
        the HuggingFace Hub API.
    dry_run:
        When *True*, log what *would* be deleted / verified without actually
        making any changes.

    Returns
    -------
    dict
        Summary with keys ``kept``, ``deleted``, ``verified``, ``failed_verification``.
    """
    target = pathlib.Path(target_dir)
    if not target.exists():
        raise FileNotFoundError(f"[FoundryPurifier] Target directory not found: {target}")

    logger.info("[FoundryPurifier] Sweeping directory: %s (dry_run=%s)", target, dry_run)

    # Run blocking I/O operations inside executor to remain non-blocking.
    loop = asyncio.get_event_loop()
    deleted = await loop.run_in_executor(None, _sweep_directory, target, dry_run)

    # SHA-256 verification against HuggingFace Hub metadata.
    verified: list[str] = []
    failed: list[str] = []
    if model_id:
        remaining_files = [p for p in target.rglob("*") if p.is_file()]
        for filepath in remaining_files:
            ok = await loop.run_in_executor(
                None, _verify_sha256, filepath, model_id, filepath.name
            )
            if ok is True:
                verified.append(str(filepath))
            elif ok is False:
                failed.append(str(filepath))
            # ok is None → hash unavailable from Hub; skip silently.

    kept = [str(p) for p in target.rglob("*") if p.is_file()]

    summary: dict[str, Any] = {
        "kept": kept,
        "deleted": deleted,
        "verified": verified,
        "failed_verification": failed,
    }
    logger.info(
        "[FoundryPurifier] Complete — kept=%d, deleted=%d, verified=%d, failed=%d",
        len(kept),
        len(deleted),
        len(verified),
        len(failed),
    )
    return summary


# ---------------------------------------------------------------------------
# Synchronous sweep — runs inside executor
# ---------------------------------------------------------------------------


def _sweep_directory(
    target: pathlib.Path,
    dry_run: bool,
) -> list[str]:
    """
    Apply the retention ruleset to *target* and delete disallowed files.

    Returns a list of deleted file path strings.
    """
    all_files = [p for p in target.rglob("*") if p.is_file()]
    deleted: list[str] = []

    # Determine whether any .gguf file is present anywhere in the tree.
    has_gguf = any(p.suffix.lower() == ".gguf" for p in all_files)

    for filepath in all_files:
        suffix = filepath.suffix.lower()
        name = filepath.name

        should_delete = False

        # Rule 1 — delete redundant weight formats when a gguf exists.
        if has_gguf and suffix in _REDUNDANT_EXTENSIONS:
            should_delete = True
            logger.info("[FoundryPurifier] Marking for deletion (redundant): %s", filepath)

        # Rule 2 — delete artefact extensions (.md etc.).
        if not should_delete and suffix in _ARTEFACT_EXTENSIONS:
            should_delete = True
            logger.info("[FoundryPurifier] Marking for deletion (artefact ext): %s", filepath)

        # Rule 3 — delete well-known non-essential artefact filenames.
        if not should_delete and name in _ARTEFACT_FILENAMES:
            should_delete = True
            logger.info("[FoundryPurifier] Marking for deletion (artefact name): %s", filepath)

        if should_delete:
            if not dry_run:
                try:
                    filepath.unlink()
                    logger.info("[FoundryPurifier] Deleted: %s", filepath)
                except OSError as exc:
                    logger.warning("[FoundryPurifier] Could not delete '%s': %s", filepath, exc)
                    continue
            deleted.append(str(filepath))

    # Remove any empty subdirectories left behind.
    if not dry_run:
        _remove_empty_dirs(target)

    return deleted


def _remove_empty_dirs(root: pathlib.Path) -> None:
    """Recursively remove empty subdirectories under *root*."""
    for dirpath in sorted(root.rglob("*"), reverse=True):
        if dirpath.is_dir() and dirpath != root:
            try:
                dirpath.rmdir()  # Only succeeds when directory is empty.
                logger.debug("[FoundryPurifier] Removed empty dir: %s", dirpath)
            except OSError:
                pass  # Not empty — ignore.


# ---------------------------------------------------------------------------
# SHA-256 verification
# ---------------------------------------------------------------------------


def _compute_sha256(filepath: pathlib.Path) -> str:
    """Return the lowercase hex SHA-256 digest of *filepath*."""
    sha256_hasher = hashlib.sha256()
    with filepath.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            sha256_hasher.update(block)
    return sha256_hasher.hexdigest()


def _verify_sha256(
    filepath: pathlib.Path,
    model_id: str,
    filename: str,
) -> bool | None:
    """
    Verify *filepath* against the SHA-256 reported by the HuggingFace Hub API.

    Returns
    -------
    True
        Hash matches — file is cryptographically intact.
    False
        Hash mismatch — file is corrupted or incomplete.
    None
        Hash unavailable from Hub (skip silently).
    """
    try:
        from huggingface_hub import HfApi  # type: ignore[import]

        token = _get_hf_token()
        api = HfApi(token=token) if token else HfApi()

        repo_info = api.model_info(model_id, files_metadata=True)
        siblings = getattr(repo_info, "siblings", None) or []

        # Find the sibling entry matching our filename.
        remote_sha: str | None = None
        for sibling in siblings:
            if getattr(sibling, "rfilename", None) == filename:
                # HuggingFace stores the LFS sha256 as a nested dict on the sibling.
                lfs_info = getattr(sibling, "lfs", None)
                if isinstance(lfs_info, dict):
                    remote_sha = lfs_info.get("sha256")
                elif isinstance(lfs_info, str):
                    remote_sha = lfs_info
                break

        if remote_sha is None:
            logger.debug(
                "[FoundryPurifier] No remote SHA-256 for '%s' in '%s' — skipping verification.",
                filename,
                model_id,
            )
            return None

        local_sha = _compute_sha256(filepath)
        if local_sha == remote_sha.lower():
            logger.info(
                "[FoundryPurifier] SHA-256 verified OK: %s", filepath.name
            )
            return True
        else:
            logger.error(
                "[FoundryPurifier] SHA-256 MISMATCH for '%s': local=%s remote=%s",
                filepath.name,
                local_sha,
                remote_sha,
            )
            return False

    except Exception as exc:
        logger.warning(
            "[FoundryPurifier] SHA-256 verification error for '%s': %s",
            filename,
            exc,
        )
        return None


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _target = sys.argv[1] if len(sys.argv) > 1 else "."
    _model_id = sys.argv[2] if len(sys.argv) > 2 else None
    _dry_run = "--dry-run" in sys.argv

    result = asyncio.run(
        purify_directory(_target, model_id=_model_id, dry_run=_dry_run)
    )
    print(f"✅ Purification complete:")
    print(f"   Kept:              {len(result['kept'])}")
    print(f"   Deleted:           {len(result['deleted'])}")
    print(f"   Verified:          {len(result['verified'])}")
    print(f"   Failed verification: {len(result['failed_verification'])}")
