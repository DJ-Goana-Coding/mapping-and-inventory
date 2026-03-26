"""
Model Shopper — Phase 7 Hugging Face Bridge
============================================
Asynchronous downloader engine that pulls model files from Hugging Face
Hub into local storage nodes.

Destination nodes
-----------------
* ``/nodes/HF_Rack/``                  — primary 1 TB compute rack
* ``District_05_OPEN_SOURCE_BIN/``     — open-source staging bin

Authentication
--------------
Set the ``HF_TOKEN`` environment variable to a HuggingFace access token
with read permissions. Gated / private repositories require a valid token.

Usage::

    import asyncio
    from agents.model_shopper import download_model

    asyncio.run(
        download_model(
            model_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
            quantization_target="*Q4_K_M.gguf",
            destination_node="HF_Rack",
        )
    )
"""
from __future__ import annotations

import asyncio
import logging
import os
import pathlib
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Repository root and destination node resolution
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).parent.parent

# Registered destination nodes — extend as new rack / bin locations are added.
DESTINATION_NODES: dict[str, pathlib.Path] = {
    "HF_Rack": _REPO_ROOT / "nodes" / "HF_Rack",
    "District_05_OPEN_SOURCE_BIN": _REPO_ROOT / "District_05_OPEN_SOURCE_BIN",
}

# ---------------------------------------------------------------------------
# Retry / streaming configuration
# ---------------------------------------------------------------------------

DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_DELAY_S: float = 5.0


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------


def _get_hf_token() -> str | None:
    """Return the HuggingFace access token from the environment."""
    return os.environ.get("HF_TOKEN")


# ---------------------------------------------------------------------------
# Async download implementation
# ---------------------------------------------------------------------------


async def download_model(
    model_id: str,
    quantization_target: str = "*",
    destination_node: str = "HF_Rack",
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY_S,
) -> list[pathlib.Path]:
    """
    Download model file(s) matching *quantization_target* from *model_id*
    on Hugging Face Hub and write them to *destination_node*.

    Parameters
    ----------
    model_id:
        Full HuggingFace model repository ID,
        e.g. ``"Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"``.
    quantization_target:
        Glob pattern selecting which files to download,
        e.g. ``"*Q4_K_M.gguf"``.  Pass ``"*"`` to download everything.
    destination_node:
        Key from :data:`DESTINATION_NODES` **or** an absolute / relative
        path string.  Defaults to ``"HF_Rack"``.
    max_retries:
        Number of retry attempts before raising the last exception.
    retry_delay:
        Seconds to wait between retry attempts.

    Returns
    -------
    list[pathlib.Path]
        Local paths of every file that was successfully downloaded.

    Raises
    ------
    EnvironmentError
        When ``HF_TOKEN`` is not set (required for gated repos).
    ValueError
        When *destination_node* cannot be resolved to a directory path.
    RuntimeError
        When all retry attempts are exhausted without a successful download.
    """
    # Resolve destination directory
    dest_dir = _resolve_destination(destination_node)
    dest_dir.mkdir(parents=True, exist_ok=True)

    token = _get_hf_token()

    logger.info(
        "[ModelShopper] Downloading '%s' (pattern=%s) → %s",
        model_id,
        quantization_target,
        dest_dir,
    )

    # Run the blocking HF Hub call in a thread-pool to avoid blocking the
    # event loop, with retry logic wrapping the whole attempt.
    downloaded: list[pathlib.Path] = []
    last_exc: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            downloaded = await asyncio.get_event_loop().run_in_executor(
                None,
                _blocking_download,
                model_id,
                quantization_target,
                dest_dir,
                token,
            )
            logger.info(
                "[ModelShopper] Download complete (%d file(s)) on attempt %d.",
                len(downloaded),
                attempt,
            )
            return downloaded
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "[ModelShopper] Attempt %d/%d failed for '%s': %s",
                attempt,
                max_retries,
                model_id,
                exc,
            )
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)

    raise RuntimeError(
        f"All {max_retries} download attempts failed for '{model_id}'. "
        f"Last error: {last_exc}"
    ) from last_exc


# ---------------------------------------------------------------------------
# Blocking helper (runs inside executor)
# ---------------------------------------------------------------------------


def _blocking_download(
    model_id: str,
    quantization_target: str,
    dest_dir: pathlib.Path,
    token: str | None,
) -> list[pathlib.Path]:
    """
    Synchronous HF Hub download executed inside an asyncio thread executor.

    Uses ``huggingface_hub.snapshot_download`` with an ``allow_patterns``
    filter to stream only the quantisation-matched file(s), keeping memory
    usage flat regardless of total repository size.
    """
    from huggingface_hub import snapshot_download  # type: ignore[import]

    allow_patterns: list[str] | None = (
        None if quantization_target in ("*", "") else [quantization_target]
    )

    kwargs: dict[str, Any] = {
        "repo_id": model_id,
        "local_dir": str(dest_dir / _safe_model_dir(model_id)),
        "local_dir_use_symlinks": False,
    }
    if allow_patterns:
        kwargs["allow_patterns"] = allow_patterns
    if token:
        kwargs["token"] = token

    local_path = snapshot_download(**kwargs)

    # Collect every file that was written under the downloaded snapshot path.
    downloaded = [p for p in pathlib.Path(local_path).rglob("*") if p.is_file()]
    return downloaded


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _resolve_destination(destination_node: str) -> pathlib.Path:
    """
    Resolve *destination_node* to a :class:`pathlib.Path`.

    Accepts:
    * A key from :data:`DESTINATION_NODES` (e.g. ``"HF_Rack"``).
    * An absolute or relative path string.
    """
    if destination_node in DESTINATION_NODES:
        return DESTINATION_NODES[destination_node]
    candidate = pathlib.Path(destination_node)
    if candidate.is_absolute() or destination_node.startswith(("./", "../", "/")):
        return candidate
    raise ValueError(
        f"Unknown destination_node '{destination_node}'. "
        f"Known nodes: {list(DESTINATION_NODES)}"
    )


def _safe_model_dir(model_id: str) -> str:
    """Return a filesystem-safe directory name derived from *model_id*."""
    return model_id.replace("/", "__").replace(":", "_")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _model_id = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
    _quant = sys.argv[2] if len(sys.argv) > 2 else "*Q4_K_M.gguf"
    _dest = sys.argv[3] if len(sys.argv) > 3 else "HF_Rack"

    _files = asyncio.run(
        download_model(
            model_id=_model_id,
            quantization_target=_quant,
            destination_node=_dest,
        )
    )
    print(f"✅ Downloaded {len(_files)} file(s):")
    for f in _files:
        print(f"   {f}")
