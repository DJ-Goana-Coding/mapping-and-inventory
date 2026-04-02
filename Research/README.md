# Research Cargo Bays

This directory contains synced data from multiple sources:

## Structure

- **GDrive/** - Data synced from Google Drive GENESIS_VAULT
- **Oppo/** - Data from Oppo Librarian Node (OPPO_CARGO)
- **S10/** - Data from S10 Field Uplink (S10_CARGO)
- **Laptop/** - Data from Laptop nodes (LAPTOP_CARGO)

## Sync Source

All directories are populated by the `TIA_CITADEL_DEEP_SCAN` GitHub Actions workflow, which pulls data from:
- Google Drive remote: `gdrive:GENESIS_VAULT/`

## Usage

These directories are gitignored to avoid committing large data files. They are populated during:
1. GitHub Actions workflow runs
2. Local rclone syncs on device nodes
3. Manual sync operations via the Streamlit UI

## Path Convention

All scripts must use **relative paths** from the repository root:
```
./Research/GDrive/
./Research/Oppo/
./Research/S10/
./Research/Laptop/
```

Never use absolute paths like `/data/` to ensure cross-platform compatibility.
