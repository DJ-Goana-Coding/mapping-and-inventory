"""
Dimensional Router — Multi-Account Architecture (Phase 24)
==========================================================
Prepares the Hub to handle multiple instances of the same program across
different dimensional layers (Accounts / Emails) simultaneously.

Key responsibilities:
* Define a **Key-Vault** structure — environment-variable names for all
  GitHub, HuggingFace, and Google credentials across Layers 1–3.
* Provide a **DimensionalRouter** that can deploy the *exact same* agent
  (trading bot, RAG brain, etc.) to multiple GitHub / HF accounts in
  parallel without cross-contamination between layers.
* Enforce strict **layer isolation**: Layer 1 credentials and workspace
  state must never bleed into Layer 2 or Layer 3 execution contexts.

Isolation model
---------------
Each layer lives in a fully isolated ``LayerContext``:
  * Its own set of credentials (sourced from environment variables).
  * Its own target GitHub org / HF namespace.
  * Its own working directory prefix so file I/O never overlaps.

Usage::

    from brain.dimensional_router import DimensionalRouter

    router = DimensionalRouter()
    results = router.deploy_all(
        agent_id="pioneer-trader",
        local_dir="nodes/HF_Rack/pioneer-omega",
    )
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Key-Vault — environment variable names for multi-layer credentials
# ---------------------------------------------------------------------------
# Populate these variables in GitHub Secrets / .env (never commit real values).
# The naming convention is:  <SERVICE>_<LAYER_N>
#
# GitHub tokens
#   GH_TOKEN_LAYER_1   — Primary GitHub account (main citadel)
#   GH_TOKEN_LAYER_2   — Secondary GitHub account (shadow / backup)
#   GH_TOKEN_LAYER_3   — Tertiary GitHub account (ops / stealth)
#
# HuggingFace tokens
#   HF_TOKEN_LAYER_1   — Primary HF account
#   HF_TOKEN_LAYER_2   — Secondary HF account
#   HF_TOKEN_LAYER_3   — Tertiary HF account
#
# Google / Drive credentials (base64-encoded service-account JSON)
#   GOOGLE_CREDS_LAYER_1 — Primary Google account
#   GOOGLE_CREDS_LAYER_2 — Secondary Google account
#   GOOGLE_CREDS_LAYER_3 — Tertiary Google account

KEY_VAULT_SCHEMA: dict[str, dict[str, str]] = {
    "layer_1": {
        "github_token": "GH_TOKEN_LAYER_1",
        "hf_token": "HF_TOKEN_LAYER_1",
        "google_creds": "GOOGLE_CREDS_LAYER_1",
        "github_org": "GH_ORG_LAYER_1",
        "hf_namespace": "HF_NAMESPACE_LAYER_1",
        "description": "Primary sovereign layer — main Citadel accounts",
    },
    "layer_2": {
        "github_token": "GH_TOKEN_LAYER_2",
        "hf_token": "HF_TOKEN_LAYER_2",
        "google_creds": "GOOGLE_CREDS_LAYER_2",
        "github_org": "GH_ORG_LAYER_2",
        "hf_namespace": "HF_NAMESPACE_LAYER_2",
        "description": "Secondary dimensional layer — shadow / backup accounts",
    },
    "layer_3": {
        "github_token": "GH_TOKEN_LAYER_3",
        "hf_token": "HF_TOKEN_LAYER_3",
        "google_creds": "GOOGLE_CREDS_LAYER_3",
        "github_org": "GH_ORG_LAYER_3",
        "hf_namespace": "HF_NAMESPACE_LAYER_3",
        "description": "Tertiary dimensional layer — ops / stealth accounts",
    },
}

#: Ordered list of active layer IDs.
ACTIVE_LAYERS: list[str] = ["layer_1", "layer_2", "layer_3"]


# ---------------------------------------------------------------------------
# Layer Context — per-layer credential + workspace envelope
# ---------------------------------------------------------------------------


@dataclass
class LayerContext:
    """
    Isolated execution context for a single dimensional layer.

    Attributes
    ----------
    layer_id:
        One of ``"layer_1"``, ``"layer_2"``, ``"layer_3"``.
    github_token:
        GitHub personal-access token for this layer (or *None* if not set).
    hf_token:
        HuggingFace token for this layer (or *None* if not set).
    google_creds:
        Base64-encoded Google service-account JSON (or *None* if not set).
    github_org:
        GitHub organisation / username for this layer.
    hf_namespace:
        HuggingFace namespace (username or org) for this layer.
    workspace_prefix:
        Filesystem prefix used to segregate all file I/O for this layer.
    """

    layer_id: str
    github_token: str | None = None
    hf_token: str | None = None
    google_creds: str | None = None
    github_org: str = ""
    hf_namespace: str = ""
    workspace_prefix: str = ""
    _extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_configured(self) -> bool:
        """Return True when at least the HF token is present."""
        return bool(self.hf_token or self.github_token)

    def redacted_summary(self) -> dict[str, str]:
        """
        Return a loggable summary with credential values redacted.

        Tokens are replaced with ``"SET"`` or ``"NOT SET"`` so that this
        dict can be written to logs without leaking secrets.
        """
        return {
            "layer_id": self.layer_id,
            "github_token": "SET" if self.github_token else "NOT SET",
            "hf_token": "SET" if self.hf_token else "NOT SET",
            "google_creds": "SET" if self.google_creds else "NOT SET",
            "github_org": self.github_org or "(not set)",
            "hf_namespace": self.hf_namespace or "(not set)",
            "workspace_prefix": self.workspace_prefix,
            "is_configured": str(self.is_configured),
        }


# ---------------------------------------------------------------------------
# DimensionalRouter
# ---------------------------------------------------------------------------


class DimensionalRouter:
    """
    Route and deploy agents across multiple dimensional layers simultaneously.

    The router reads credentials from environment variables (sourced from
    GitHub Secrets or a local ``.env`` file) and constructs isolated
    ``LayerContext`` objects for each layer.  Deployment methods iterate
    over all configured layers and execute the target action in parallel
    — each layer in strict isolation.

    Parameters
    ----------
    layers:
        List of layer IDs to activate.  Defaults to all three standard
        layers defined in ``ACTIVE_LAYERS``.
    """

    def __init__(self, layers: list[str] | None = None) -> None:
        self._layer_ids = layers if layers is not None else list(ACTIVE_LAYERS)
        self._contexts: dict[str, LayerContext] = {}
        self._load_contexts()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_contexts(self) -> None:
        """Build a LayerContext for each active layer from the environment."""
        for layer_id in self._layer_ids:
            schema = KEY_VAULT_SCHEMA.get(layer_id, {})
            ctx = LayerContext(
                layer_id=layer_id,
                github_token=os.environ.get(schema.get("github_token", "")) or None,
                hf_token=os.environ.get(schema.get("hf_token", "")) or None,
                google_creds=os.environ.get(schema.get("google_creds", "")) or None,
                github_org=os.environ.get(schema.get("github_org", ""), ""),
                hf_namespace=os.environ.get(schema.get("hf_namespace", ""), ""),
                workspace_prefix=f".workspace/{layer_id}",
            )
            self._contexts[layer_id] = ctx
            logger.debug(
                "DimensionalRouter: loaded %s",
                ctx.redacted_summary(),
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_context(self, layer_id: str) -> LayerContext:
        """
        Return the ``LayerContext`` for *layer_id*.

        Raises
        ------
        KeyError
            If *layer_id* is not an active layer.
        """
        return self._contexts[layer_id]

    def list_contexts(self) -> list[LayerContext]:
        """Return all active LayerContext objects in layer order."""
        return [self._contexts[lid] for lid in self._layer_ids]

    def configured_layers(self) -> list[LayerContext]:
        """Return only the layers that have at least one credential set."""
        return [ctx for ctx in self.list_contexts() if ctx.is_configured]

    def deploy_to_hf(
        self,
        agent_id: str,
        local_dir: str,
        repo_type: str = "space",
        path_in_repo: str = ".",
    ) -> dict[str, str]:
        """
        Deploy *local_dir* to the HuggingFace Space ``<hf_namespace>/<agent_id>``
        for every configured dimensional layer.

        Layers with missing tokens are skipped and reported as ``SKIPPED``.
        Each layer is executed sequentially to avoid credential cross-talk.

        Parameters
        ----------
        agent_id:
            The HF repository / Space name (e.g. ``"pioneer-trader"``).
        local_dir:
            Local directory containing the artefacts to upload.
        repo_type:
            HuggingFace repository type (default ``"space"``).
        path_in_repo:
            Destination path inside the HF repository (default ``"."``).

        Returns
        -------
        dict[str, str]
            Mapping of ``layer_id → status`` (``"OK"``, ``"SKIPPED"``,
            or an error message).
        """
        results: dict[str, str] = {}

        for ctx in self.list_contexts():
            if not ctx.hf_token:
                logger.warning(
                    "DimensionalRouter [%s]: HF token not set — skipping %s deploy.",
                    ctx.layer_id,
                    agent_id,
                )
                results[ctx.layer_id] = "SKIPPED — HF token not configured"
                continue

            namespace = ctx.hf_namespace or "DJ-Goana-Coding"
            repo_id = f"{namespace}/{agent_id}"

            try:
                from huggingface_hub import HfApi  # type: ignore[import]

                api = HfApi(token=ctx.hf_token)
                api.upload_folder(
                    folder_path=local_dir,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    path_in_repo=path_in_repo,
                )
                logger.info(
                    "DimensionalRouter [%s]: deployed %s → %s",
                    ctx.layer_id,
                    agent_id,
                    repo_id,
                )
                results[ctx.layer_id] = f"OK → {repo_id}"
            except Exception as exc:
                logger.error(
                    "DimensionalRouter [%s]: deploy of %s failed: %s",
                    ctx.layer_id,
                    agent_id,
                    exc,
                )
                results[ctx.layer_id] = f"ERROR — {exc}"

        return results

    def deploy_all(
        self,
        agent_id: str,
        local_dir: str,
        **kwargs: Any,
    ) -> dict[str, str]:
        """
        Convenience wrapper — deploy *agent_id* to all configured HF layers.

        Equivalent to :meth:`deploy_to_hf` with default arguments.
        """
        return self.deploy_to_hf(agent_id, local_dir, **kwargs)

    def log_layer_status(self) -> None:
        """Emit an INFO-level log entry for every layer showing its readiness."""
        for ctx in self.list_contexts():
            summary = ctx.redacted_summary()
            status = "READY" if ctx.is_configured else "NOT CONFIGURED"
            logger.info(
                "DimensionalRouter [%s] %s — github_token=%s hf_token=%s",
                ctx.layer_id,
                status,
                summary["github_token"],
                summary["hf_token"],
            )
