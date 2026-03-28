"""
ark_engine.py — ARK_CORE Triple-Sync Orchestrator
Architect: Chance | OPPO_FORGE Origin

Orchestrates the full sync cycle:
  1. Regenerates the file manifest (manifest_generator.py)
  2. Stages and commits the updated inventory
  3. Force-pushes to all configured remotes (inventory, ark, space)
"""

import subprocess
import sys


# Remote targets to push to (must be configured via `git remote add`)
_REMOTES: list[str] = ['inventory', 'ark', 'space']
_BRANCH = 'main'
_COMMIT_MSG = '[LIBRARIAN-WELD] Mapping & Inventory Sync - Architect: Chance'


def run_sync() -> None:
    """Run the full manifest → commit → push sync cycle."""
    print('[ARK] INITIALIZING TRIPLE-SYNC...')

    # Step 1: Regenerate the manifest
    result = subprocess.run(
        [sys.executable, 'services/manifest_generator.py'],
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    if result.returncode != 0:
        print(f'[ERROR] Manifest generation failed:\n{result.stderr}')
        sys.exit(1)
    print(result.stdout.strip())

    # Step 2: Stage all changes
    subprocess.run(['git', 'add', '.'], check=True)

    # Step 3: Commit (allow empty commits in case nothing changed)
    commit_result = subprocess.run(
        ['git', 'commit', '-m', _COMMIT_MSG, '--allow-empty'],
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    if commit_result.returncode != 0:
        print(f'[WARN] Commit step returned non-zero:\n{commit_result.stderr}')

    # Step 4: Force-push to each remote
    all_ok = True
    for remote in _REMOTES:
        print(f'[!] PUSHING TO {remote.upper()}...')
        push_result = subprocess.run(
            ['git', 'push', remote, _BRANCH, '--force'],
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        if push_result.returncode != 0:
            print(f'[ERROR] {remote.upper()} FAILED:\n{push_result.stderr.strip()}')
            all_ok = False
        else:
            print(f'[V] {remote.upper()} SYNCHRONIZED.')

    if all_ok:
        print('[FINALISED] THE ARK IS STAINLESS.')
    else:
        print('[WARN] One or more remotes failed. Check logs above.')
        sys.exit(1)


if __name__ == '__main__':
    run_sync()