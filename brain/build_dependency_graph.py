"""
build_dependency_graph.py — Phase 23 Omniscient Sync
======================================================
Scans all Python files in the mapping-and-inventory Hub and produces
``brain/dependency_graph.json``, mapping every internal import relationship.

Re-run any time after code changes to keep the graph current::

    python brain/build_dependency_graph.py

sovereignty_layer : Phase 23 — Lattice Purification & Omniscient Sync
last_purified_date: 2026-03-26
"""
from __future__ import annotations

import ast
import json
import pathlib
from datetime import UTC, datetime

REPO_ROOT = pathlib.Path(__file__).parent.parent
INTERNAL_PACKAGES = frozenset(
    {"agents", "brain", "core", "nodes", "tasks", "utils", "backend"}
)
OUTPUT_PATH = pathlib.Path(__file__).parent / "dependency_graph.json"


def _extract_imports(filepath: pathlib.Path) -> list[str]:
    """Return deduplicated first-party module dotted-paths imported in *filepath*."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []
    refs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in INTERNAL_PACKAGES:
                    refs.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in INTERNAL_PACKAGES:
                    refs.add(node.module)
    return sorted(refs)


def _build_module_map() -> dict[str, pathlib.Path]:
    """Return {dotted_module_id: filepath} for every .py file in the repo."""
    module_map: dict[str, pathlib.Path] = {}
    for py_file in sorted(REPO_ROOT.rglob("*.py")):
        rel = py_file.relative_to(REPO_ROOT)
        parts = list(rel.parts)
        mod = ".".join(p.replace(".py", "") for p in parts)
        if mod.endswith(".__init__"):
            mod = mod[: -len(".__init__")]
        module_map[mod] = py_file
    return module_map


def build_graph() -> dict:
    """Scan the repository and return a dependency-graph dict."""
    module_map = _build_module_map()

    nodes = []
    edges: list[dict] = []
    seen_edges: set[tuple[str, str]] = set()

    for mod_id, filepath in sorted(module_map.items()):
        rel = str(filepath.relative_to(REPO_ROOT))
        pkg = rel.split("/")[0] if "/" in rel else "root"
        nodes.append({"id": mod_id, "file": rel, "package": pkg})

        for imp in _extract_imports(filepath):
            target = imp if imp in module_map else imp.split(".")[0]
            if target in module_map and target != mod_id:
                key = (mod_id, target)
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges.append({"from": mod_id, "to": target, "type": "import"})

    return {
        "schema_version": "1.0.0",
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "Phase 23 — Lattice Purification & Omniscient Sync",
        "description": (
            "Internal import-dependency graph for the mapping-and-inventory Hub. "
            "Edges represent 'module A imports from module B' relationships "
            "discovered by static AST analysis. Re-generate with: "
            "python brain/build_dependency_graph.py"
        ),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)

    graph = build_graph()
    OUTPUT_PATH.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    log.info(
        "[DependencyGraph] Written to %s — %d nodes, %d edges.",
        OUTPUT_PATH,
        graph["node_count"],
        graph["edge_count"],
    )
