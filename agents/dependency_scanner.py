"""
Dependency Scanner — Internal Import Graph Generator
=====================================================
Scans all Python source files within this repository and maps the
*internal* import relationships between first-party modules.

The output is written to ``brain/dependency_graph.json`` and contains:

* ``nodes`` — every first-party module file found in the repository.
* ``edges`` — directed connections ``{ "from": "module_a", "to": "module_b" }``
  whenever *module_a* imports from *module_b*.
* ``adjacency`` — convenience dict keyed by source module listing all its
  direct dependencies.
* ``generated_utc`` — ISO-8601 timestamp of the scan.

Usage::

    python -m agents.dependency_scanner
    # or
    from agents.dependency_scanner import scan
    graph = scan()
"""
from __future__ import annotations

import ast
import json
import logging
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = pathlib.Path(__file__).parent.parent
OUTPUT_PATH: pathlib.Path = _REPO_ROOT / "brain" / "dependency_graph.json"

# First-party top-level packages/modules in this repository
_FIRST_PARTY: frozenset[str] = frozenset(
    {
        "agents",
        "backend",
        "brain",
        "bridge_protocol",
        "core",
        "inventory_engine",
        "nodes",
        "tasks",
        "utils",
    }
)


def _relative_module_name(py_file: pathlib.Path) -> str:
    """Return a dot-separated module name relative to *_REPO_ROOT*."""
    try:
        rel = py_file.relative_to(_REPO_ROOT)
    except ValueError:
        return str(py_file)
    parts = list(rel.with_suffix("").parts)
    # Drop __init__ suffix → represent the package itself
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _collect_internal_imports(py_file: pathlib.Path) -> set[str]:
    """
    Parse *py_file* with :mod:`ast` and return the set of first-party
    top-level packages it imports.
    """
    try:
        source = py_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError as exc:
        logger.warning("[Scanner] Syntax error in %s: %s", py_file, exc)
        return set()

    internal: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in _FIRST_PARTY:
                    internal.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                if top in _FIRST_PARTY:
                    internal.add(top)
            # Relative imports — resolve against the file's own package
            elif node.level and node.level > 0:
                parts = py_file.relative_to(_REPO_ROOT).parts
                if len(parts) > node.level:
                    top = parts[0]
                    if top in _FIRST_PARTY:
                        internal.add(top)
    return internal


def scan() -> dict[str, Any]:
    """
    Walk the repository, build the internal dependency graph, and write
    ``brain/dependency_graph.json``.

    Returns
    -------
    dict
        The full graph structure (also written to disk).
    """
    logger.info("[Scanner] Starting dependency graph scan …")

    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    adjacency: dict[str, list[str]] = {}

    for py_file in sorted(_REPO_ROOT.rglob("*.py")):
        # Skip hidden directories, virtual-envs, and dist artefacts
        if any(part.startswith(".") or part in {"__pycache__", "dist", "build", "venv", ".venv"}
               for part in py_file.parts):
            continue

        module_name = _relative_module_name(py_file)
        nodes.append({"id": module_name, "path": str(py_file.relative_to(_REPO_ROOT))})

        imports = _collect_internal_imports(py_file)
        # Exclude self-references (e.g. brain.* importing brain)
        own_top = module_name.split(".")[0]
        imports.discard(own_top)

        if imports:
            adjacency[module_name] = sorted(imports)
            for dep in sorted(imports):
                edges.append({"from": module_name, "to": dep})
                logger.debug("[Scanner] %s → %s", module_name, dep)

    graph: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges,
        "adjacency": adjacency,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2)

    logger.info(
        "[Scanner] Dependency graph written — %d node(s), %d edge(s).",
        len(nodes),
        len(edges),
    )
    return graph


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    result = scan()
    print(
        f"✅ Dependency graph complete — "
        f"{result['total_nodes']} node(s), {result['total_edges']} edge(s) → brain/dependency_graph.json"
    )
    sys.exit(0)
