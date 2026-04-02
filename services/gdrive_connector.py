"""
Q.G.T.N.L. (0) // GDRIVE CONNECTOR
Handles Google Drive and rclone-based cloud sync operations.
Supports: GENESIS_VAULT, LAPTOP_CARGO, S10 pulls.
"""
import os
import subprocess


RCLONE_REMOTE = "gdrive"

# Known GDrive targets
GDRIVE_TARGETS = {
    "GENESIS_VAULT": {
        "label": "Genesis Vault (Oppo 23GB)",
        "remote": f"{RCLONE_REMOTE}:GENESIS_VAULT",
        "local": "./Research/Genesis",
    },
    "LAPTOP_CARGO": {
        "label": "Laptop Cargo (321GB)",
        "remote": f"{RCLONE_REMOTE}:GENESIS_VAULT/LAPTOP_CARGO",
        "local": "./Research/Laptop",
    },
    "S10_VAULT": {
        "label": "S10 Vault",
        "remote": f"{RCLONE_REMOTE}:S10_VAULT",
        "local": "./Research/S10",
    },
}


def setup_rclone_config():
    """Write rclone config from RCLONE_CONFIG_DATA env var if present."""
    conf_data = os.getenv("RCLONE_CONFIG_DATA")
    if not conf_data:
        return False, "RCLONE_CONFIG_DATA not set."
    config_path = os.path.expanduser("~/.config/rclone/rclone.conf")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        f.write(conf_data)
    return True, f"rclone config written to {config_path}"


def check_rclone_available():
    """Check if rclone is installed."""
    try:
        subprocess.run(["rclone", "version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def list_gdrive(remote_path=None, max_depth=2):
    """List files/folders on GDrive remote."""
    path = remote_path or f"{RCLONE_REMOTE}:GENESIS_VAULT"
    try:
        out = subprocess.check_output(
            ["rclone", "lsjson", path, "--max-depth", str(max_depth)],
            stderr=subprocess.DEVNULL,
            timeout=30,
        ).decode()
        import json
        return json.loads(out)
    except Exception:
        return []


def sync_from_gdrive(target_key, dry_run=True):
    """
    Sync a known GDrive target to local storage.
    Returns (success, output_lines).
    """
    target = GDRIVE_TARGETS.get(target_key)
    if not target:
        return False, [f"Unknown target: {target_key}"]

    local_path = target["local"]
    os.makedirs(local_path, exist_ok=True)

    cmd = ["rclone", "sync", target["remote"], local_path, "--progress", "--stats-one-line"]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        lines = (result.stdout + result.stderr).splitlines()
        return result.returncode == 0, lines
    except subprocess.TimeoutExpired:
        return False, ["Sync timed out after 5 minutes."]
    except FileNotFoundError:
        return False, ["rclone not found. Is it installed?"]
    except Exception as e:
        return False, [str(e)]


def get_gdrive_status():
    """Quick status check of rclone / gdrive config."""
    rclone_ok = check_rclone_available()
    config_path = os.path.expanduser("~/.config/rclone/rclone.conf")
    config_exists = os.path.exists(config_path)
    env_key = bool(os.getenv("RCLONE_CONFIG_DATA"))
    return {
        "rclone_installed": rclone_ok,
        "config_file_exists": config_exists,
        "env_key_present": env_key,
        "targets": list(GDRIVE_TARGETS.keys()),
    }
