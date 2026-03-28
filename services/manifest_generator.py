"""
manifest_generator.py — ARK_CORE File Inventory Builder
Architect: Chance | OPPO_FORGE Origin

Walks the project root and indexes all relevant source files into
Partition_01/master_inventory.json, recording each file's relative
path, size in bytes, and last-modification timestamp.
"""

import datetime
import json
import os

# File extensions included in the inventory scan
_TRACKED_EXTENSIONS: tuple[str, ...] = ('.py', '.sh', '.json', '.csv', '.log')
_EXCLUDED_DIRS: set[str] = {'.git'}
_OUTPUT_SUBDIR = 'Partition_01'
_OUTPUT_FILE = 'master_inventory.json'


def generate_manifest() -> None:
    """Walk the repository root and write a fresh master_inventory.json."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    now = datetime.datetime.now()

    manifest: dict = {
        'timestamp': now.isoformat(),
        'origin': 'OPPO_FORGE',
        'architect': 'Chance',
        'inventory': [],
    }

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in-place so os.walk skips them entirely
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIRS]

        for filename in filenames:
            if filename.endswith(_TRACKED_EXTENSIONS):
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, root)
                stat = os.stat(abs_path)
                manifest['inventory'].append({
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

    manifest['total_files'] = len(manifest['inventory'])

    output_dir = os.path.join(root, _OUTPUT_SUBDIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, _OUTPUT_FILE)

    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=4)

    print(f'[V] ARK_CORE INDEXED: {manifest["total_files"]} FILES SECURED → {output_path}')


if __name__ == '__main__':
    generate_manifest()