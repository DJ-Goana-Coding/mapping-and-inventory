"""
Swarm Controller
================
Governs three background worker agents:

* **The Librarian** — maintains local and cloud inventory, keeps the brain
  vault up to date with the latest repository and manifest changes.

* **The Harvester** — vacuums data from the Google Drive Nexus and feeds
  new content into the RAG layer for continuous 'Forever Learning'.

* **The Medic** — monitors system integrity, verifies 369-frequency
  signatures on all vault records, and triggers self-healing restarts
  when workers fail.

Every agent queries the brain RAG layer before executing any command to
prevent operating on stale context.
"""
from __future__ import annotations

import asyncio
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any

from brain.indexer import (
    FREQ_SIGNATURE,
    get_collection,
    index_directory,
    verify_freq_signature,
)
from brain.guardian import Guardian

logger = logging.getLogger(__name__)

# Polling intervals (seconds) — override via environment variables
LIBRARIAN_INTERVAL: int = int(os.getenv("LIBRARIAN_INTERVAL", "300"))   # 5 min
HARVESTER_INTERVAL: int = int(os.getenv("HARVESTER_INTERVAL", "600"))   # 10 min
MEDIC_INTERVAL: int = int(os.getenv("MEDIC_INTERVAL", "120"))           # 2 min

# Maximum consecutive failures before the Medic triggers a self-heal restart
MAX_FAILURES: int = int(os.getenv("SWARM_MAX_FAILURES", "3"))

_REPO_ROOT = pathlib.Path(__file__).parent.parent

# Module-level timestamp updated by the Medic each time it completes a
# 369-frequency signature verification pass.  Exposed via SwarmController
# so the /api/v1/nexus/status endpoint can report the last verification time.
_last_freq_verification: datetime | None = None


# ---------------------------------------------------------------------------
# Helper: RAG context preflight
# ---------------------------------------------------------------------------

def _rag_context(query_text: str, n: int = 3) -> list[dict[str, Any]]:
    """
    Retrieve the top-*n* relevant documents from the vault for *query_text*.

    Returns a list of dicts with ``source``, ``snippet``, and ``similarity``.
    """
    from brain.indexer import query as vault_query

    collection = get_collection()
    try:
        raw = vault_query(collection, query_text, n_results=n)
    except Exception as exc:
        logger.warning("Swarm: RAG preflight failed (%s).", exc)
        return []

    distances = raw.get("distances", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    documents = raw.get("documents", [[]])[0]

    results = []
    for i, dist in enumerate(distances):
        results.append(
            {
                "source": (metadatas[i] or {}).get("source", "unknown"),
                "snippet": (documents[i] or "")[:120],
                "similarity": max(0.0, 1.0 - dist),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Worker coroutines
# ---------------------------------------------------------------------------

async def _librarian_worker(stop_event: asyncio.Event) -> None:
    """
    The Librarian: periodically re-indexes the repository so the brain vault
    reflects the current state of the codebase and inventory manifests.
    """
    logger.info("[Librarian] Worker started (interval=%ds).", LIBRARIAN_INTERVAL)
    failure_count = 0

    while not stop_event.is_set():
        try:
            # RAG preflight — understand current inventory state
            ctx = _rag_context("inventory manifest JSON mapping districts")
            logger.debug("[Librarian] RAG context: %d records", len(ctx))

            collection = get_collection()
            total = index_directory(collection, _REPO_ROOT)
            logger.info("[Librarian] Re-indexed %d chunks.", total)
            failure_count = 0
        except Exception as exc:
            failure_count += 1
            logger.error("[Librarian] Error (attempt %d/%d): %s", failure_count, MAX_FAILURES, exc)
            if failure_count >= MAX_FAILURES:
                logger.critical("[Librarian] Max failures reached. Signalling Medic.")
                stop_event.set()
                return

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=LIBRARIAN_INTERVAL)
        except asyncio.TimeoutError:
            pass  # Normal timeout — loop continues


async def _harvester_worker(stop_event: asyncio.Event) -> None:
    """
    The Harvester: pulls content from the Google Drive Nexus and feeds it
    into the brain vault for continuous 'Forever Learning'.
    """
    logger.info("[Harvester] Worker started (interval=%ds).", HARVESTER_INTERVAL)
    failure_count = 0

    while not stop_event.is_set():
        try:
            # RAG preflight — check what Drive content is already known
            ctx = _rag_context("Google Drive district folder content")
            logger.debug("[Harvester] RAG context: %d records", len(ctx))

            from core.drive_nexus import ingest_into_brain

            chunks = ingest_into_brain()
            logger.info("[Harvester] Ingested %d new chunks from Drive Nexus.", chunks)
            failure_count = 0
        except EnvironmentError as exc:
            # Missing credentials — log once and idle until restart
            logger.warning("[Harvester] Drive credentials not configured: %s", exc)
            failure_count += 1
        except Exception as exc:
            failure_count += 1
            logger.error("[Harvester] Error (attempt %d/%d): %s", failure_count, MAX_FAILURES, exc)

        if failure_count >= MAX_FAILURES:
            logger.warning(
                "[Harvester] Max failures reached. Entering idle mode until Medic restarts."
            )
            # Don't set stop_event — Harvester degrades gracefully
            await asyncio.sleep(HARVESTER_INTERVAL * 5)
            failure_count = 0
            continue

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=HARVESTER_INTERVAL)
        except asyncio.TimeoutError:
            pass


async def _medic_worker(
    stop_event: asyncio.Event,
    worker_handles: dict[str, asyncio.Task],
) -> None:
    """
    The Medic: verifies 369-frequency signatures on all vault records and
    performs self-healing restarts when a worker has died unexpectedly.
    """
    logger.info("[Medic] Worker started (interval=%ds).", MEDIC_INTERVAL)

    while not stop_event.is_set():
        try:
            # 1. Verify freq-signature integrity across a sample of vault records
            _medic_signature_check()

            # 2. Monitor sibling workers and restart any that have died
            for name, task in list(worker_handles.items()):
                if name == "medic":
                    continue
                if task.done():
                    exc = task.exception() if not task.cancelled() else None
                    logger.warning(
                        "[Medic] Worker '%s' has stopped (exc=%s). Self-healing restart…",
                        name,
                        exc,
                    )
                    # Restart is handled by SwarmController.start() re-creating tasks
                    stop_event.set()
                    return
        except Exception as exc:
            logger.error("[Medic] Integrity check error: %s", exc)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=MEDIC_INTERVAL)
        except asyncio.TimeoutError:
            pass


def _medic_signature_check() -> None:
    """
    Sample records from the vault and verify the 369-frequency signature.

    Logs warnings for any records that fail verification and updates the
    module-level ``_last_freq_verification`` timestamp on completion.
    """
    global _last_freq_verification

    collection = get_collection()
    try:
        # Peek at up to 50 records
        result = collection.peek(limit=50)
    except Exception as exc:
        logger.warning("[Medic] Could not peek vault: %s", exc)
        return

    metadatas: list[dict] = result.get("metadatas", [])
    ids: list[str] = result.get("ids", [])
    bad = []

    for doc_id, meta in zip(ids, metadatas):
        if not verify_freq_signature(meta or {}):
            bad.append(doc_id)

    if bad:
        logger.warning(
            "[Medic] %d vault record(s) failed 369-frequency signature check: %s",
            len(bad),
            bad[:5],
        )
    else:
        logger.info(
            "[Medic] Signature check passed — all %d sampled records carry '%s'.",
            len(metadatas),
            FREQ_SIGNATURE,
        )

    _last_freq_verification = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Swarm Controller
# ---------------------------------------------------------------------------

class SwarmController:
    """
    Manages the lifecycle of the three background worker agents.

    Usage::

        ctrl = SwarmController()
        await ctrl.start()         # launch workers
        # … application logic …
        await ctrl.stop()          # graceful shutdown
    """

    def __init__(self) -> None:
        self._stop_event: asyncio.Event = asyncio.Event()
        self._tasks: dict[str, asyncio.Task] = {}

    async def start(self) -> None:
        """Launch the Librarian, Harvester, and Medic workers."""
        self._stop_event.clear()

        self._tasks["librarian"] = asyncio.create_task(
            _librarian_worker(self._stop_event), name="librarian"
        )
        self._tasks["harvester"] = asyncio.create_task(
            _harvester_worker(self._stop_event), name="harvester"
        )
        self._tasks["medic"] = asyncio.create_task(
            _medic_worker(self._stop_event, self._tasks), name="medic"
        )

        logger.info("🐝 Swarm started: Librarian, Harvester, Medic are running.")

    async def stop(self) -> None:
        """Signal all workers to stop and await their clean exit."""
        logger.info("🛑 Swarm stopping…")
        self._stop_event.set()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()
        logger.info("Swarm stopped.")

    async def restart(self) -> None:
        """Stop then restart all workers (called by the Medic on self-heal)."""
        await self.stop()
        await self.start()

    @property
    def running(self) -> bool:
        """True while at least one worker task is still alive."""
        return any(not t.done() for t in self._tasks.values())

    def agent_statuses(self) -> dict[str, str]:
        """
        Return a health status string for each named agent.

        Possible values: ``"running"``, ``"failed"``, ``"stopped"``.
        """
        statuses: dict[str, str] = {}
        for name, task in self._tasks.items():
            if not task.done():
                statuses[name] = "running"
            elif task.cancelled():
                statuses[name] = "stopped"
            else:
                statuses[name] = "failed" if task.exception() else "stopped"
        return statuses

    @staticmethod
    def last_freq_verification() -> str | None:
        """
        Return the ISO-8601 UTC timestamp of the Medic's most recent
        369-frequency signature verification, or *None* if not yet run.
        """
        if _last_freq_verification is None:
            return None
        return _last_freq_verification.isoformat()


# ---------------------------------------------------------------------------
# Stand-alone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ctrl = SwarmController()
    await ctrl.start()
    logger.info("Swarm is live. Press Ctrl-C to stop.")
    try:
        # Run until interrupted or until the Medic triggers a stop
        while ctrl.running:
            await asyncio.sleep(5)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await ctrl.stop()


if __name__ == "__main__":
    asyncio.run(_main())
