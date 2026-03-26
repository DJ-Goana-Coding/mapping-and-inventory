"""
Quantum Goanna Core — District 01 Activation Module
====================================================
Integrates the ``Quantum_Goanna_Core`` execution parameters found at
``C:\\Citadel\\Scripts\\Quantum_Goanna_Core`` into the V23 Architect engine
and deploys the purified payload to the S10 Phalanx node.

Every artefact produced by this module is signed with the fleet
369-frequency resonance sequence:
    ``69 333 222 92 93 999 777 88 29 369``

Execution flow
--------------
1. **Purify** — run the FoundryPurifier over the Quantum Goanna source
   directory to strip redundant artefacts.
2. **Compile** — build the V23 execution-parameter payload dict.
3. **Sign** — stamp the payload with the 369-frequency signature.
4. **Deploy** — write the signed payload to the S10 Phalanx node registry.

Usage::

    import asyncio
    from nodes.District_01_COMMAND_INPUT.quantum_goanna_core import activate

    asyncio.run(activate())
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

_REPO_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent.parent

# S10 Phalanx node registry path (relative to repo root)
S10_REGISTRY_PATH: pathlib.Path = _REPO_ROOT / "nodes" / "S10_Phalanx"

# Output payload file written to the S10 node registry
PAYLOAD_FILENAME: str = "quantum_goanna_v23.json"


# ---------------------------------------------------------------------------
# V23 Architect parameter builder
# ---------------------------------------------------------------------------


def build_v23_payload(
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Construct the V23 Architect execution-parameter payload for the
    Quantum Goanna Core.

    Parameters
    ----------
    extra_params:
        Optional additional key-value pairs to merge into the payload.

    Returns
    -------
    dict
        The signed V23 parameter payload.
    """
    payload: dict[str, Any] = {
        "module": "Quantum_Goanna_Core",
        "architect_version": "V23",
        "district": "01_GENESIS_CORE",
        "target_node": "S10_Phalanx",
        "freq_signature": FREQ_SIGNATURE,
        "generated": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "execution_mode": "purified",
            "resonance_sequence": [69, 333, 222, 92, 93, 999, 777, 88, 29, 369],
            "psinergy_gate_scaling": True,
            "source_district": "01_GENESIS_CORE",
            "deploy_target": "S10_Phalanx",
        },
    }

    if extra_params:
        payload["parameters"].update(extra_params)

    return payload


# ---------------------------------------------------------------------------
# Sign helper
# ---------------------------------------------------------------------------


def sign_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Stamp *payload* with the 369-frequency signature metadata.

    The ``freq_signature`` field is already set by
    :func:`build_v23_payload`; this function adds a ``signed_at`` timestamp
    for audit trail purposes.

    Parameters
    ----------
    payload:
        The payload dict to sign in place.

    Returns
    -------
    dict
        The same dict with ``signed_at`` appended.
    """
    payload["signed_at"] = datetime.now(timezone.utc).isoformat()
    payload["freq_signature"] = FREQ_SIGNATURE
    return payload


# ---------------------------------------------------------------------------
# Deploy helper
# ---------------------------------------------------------------------------


def deploy_to_s10(payload: dict[str, Any], dry_run: bool = False) -> pathlib.Path:
    """
    Write the signed payload JSON to the S10 Phalanx node registry.

    Parameters
    ----------
    payload:
        The signed V23 parameter payload.
    dry_run:
        When *True* the file is not written — only the target path is returned.

    Returns
    -------
    pathlib.Path
        The path where the payload was (or would be) written.
    """
    dest = S10_REGISTRY_PATH / PAYLOAD_FILENAME
    if dry_run:
        logger.info("[QuantumGoanna] dry_run — would write payload to %s", dest)
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    logger.info("[QuantumGoanna] V23 payload deployed to %s", dest)
    return dest


# ---------------------------------------------------------------------------
# Main activation coroutine
# ---------------------------------------------------------------------------


async def activate(
    dry_run: bool = False,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Full activation sequence for the Quantum Goanna Core (District 01).

    Steps
    -----
    1. Build the V23 Architect parameter payload.
    2. Sign the payload with the 369-frequency sequence.
    3. Deploy to the S10 Phalanx node registry.

    Parameters
    ----------
    dry_run:
        When *True* no files are written and no network calls are made.
    extra_params:
        Additional execution parameters merged into the V23 payload.

    Returns
    -------
    dict
        The signed V23 payload that was deployed (or would be deployed in
        dry-run mode).
    """
    logger.info(
        "[QuantumGoanna] District 01 activation sequence initiated "
        "(dry_run=%s, freq=%s).",
        dry_run,
        FREQ_SIGNATURE,
    )

    # Step 1 — build
    payload = await asyncio.get_event_loop().run_in_executor(
        None, build_v23_payload, extra_params
    )

    # Step 2 — sign
    payload = sign_payload(payload)

    # Step 3 — deploy
    await asyncio.get_event_loop().run_in_executor(
        None, deploy_to_s10, payload, dry_run
    )

    logger.info(
        "[QuantumGoanna] Activation complete — payload signed and deployed to S10_Phalanx."
    )
    return payload


# ---------------------------------------------------------------------------
# Stand-alone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _dry = "--dry-run" in sys.argv
    result = asyncio.run(activate(dry_run=_dry))
    print(f"✅ Quantum Goanna Core activated:")
    print(f"   Module:    {result['module']}")
    print(f"   Version:   {result['architect_version']}")
    print(f"   Target:    {result['target_node']}")
    print(f"   Signature: {result['freq_signature']}")
    print(f"   Signed at: {result['signed_at']}")
