"""
Q.G.T.N.L. (0) // VAULT.PY - Archive & Ingest Logic
The Librarian's Archive Management System
Handles ingestion, archival, and tracking of the 321GB intelligence vault.
"""
import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime


# SQLite Database for tracking the 321GB vault
DB_PATH = os.path.join(os.path.dirname(__file__), "tracker.db")


def init_tracker_db():
    """Initialize the SQLite tracker database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE NOT NULL,
            file_hash TEXT,
            file_size INTEGER,
            last_modified TEXT,
            source TEXT,
            status TEXT DEFAULT 'tracked',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Tracker database initialized at {DB_PATH}")


def calculate_file_hash(filepath, chunk_size=8192):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"⚠️ Error hashing {filepath}: {e}")
        return None


def ingest_file(filepath, source="unknown"):
    """
    Ingest a file into the vault tracking system.
    
    Args:
        filepath: Path to the file to ingest
        source: Source identifier (e.g., 'GDrive', 'Oppo', 'S10', 'Laptop')
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    file_stat = os.stat(filepath)
    file_hash = calculate_file_hash(filepath)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO vault_files 
            (filepath, file_hash, file_size, last_modified, source, status)
            VALUES (?, ?, ?, ?, ?, 'tracked')
        """, (
            filepath,
            file_hash,
            file_stat.st_size,
            datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            source
        ))
        conn.commit()
        print(f"✅ Ingested: {filepath} ({file_stat.st_size} bytes)")
        return True
    except Exception as e:
        print(f"❌ Error ingesting {filepath}: {e}")
        return False
    finally:
        conn.close()


def ingest_directory(directory, source="unknown", recursive=True):
    """
    Ingest all files from a directory into the vault.
    
    Args:
        directory: Directory path to scan
        source: Source identifier
        recursive: Whether to scan subdirectories
    """
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return
    
    path = Path(directory)
    pattern = "**/*" if recursive else "*"
    
    ingested = 0
    total_size = 0
    
    for filepath in path.glob(pattern):
        if filepath.is_file():
            if ingest_file(str(filepath), source):
                ingested += 1
                total_size += filepath.stat().st_size
    
    print(f"📦 Ingested {ingested} files, total size: {total_size / (1024**3):.2f} GB")


def get_vault_stats():
    """Get statistics about the vault."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(file_size) FROM vault_files")
    count, total_size = cursor.fetchone()
    
    cursor.execute("SELECT source, COUNT(*), SUM(file_size) FROM vault_files GROUP BY source")
    by_source = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_files": count or 0,
        "total_size_gb": (total_size or 0) / (1024**3),
        "by_source": [{"source": s, "count": c, "size_gb": (sz or 0) / (1024**3)} for s, c, sz in by_source]
    }


def archive_to_json(output_path="vault_archive.json"):
    """Export the vault tracker to JSON format."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vault_files")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    data = [dict(zip(columns, row)) for row in rows]
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    conn.close()
    print(f"✅ Vault archived to {output_path}")


if __name__ == "__main__":
    import sys
    
    # Initialize database
    init_tracker_db()
    
    # Command-line interface
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            stats = get_vault_stats()
            print(f"\n📊 Vault Statistics:")
            print(f"   Total Files: {stats['total_files']}")
            print(f"   Total Size: {stats['total_size_gb']:.2f} GB")
            print(f"\n   By Source:")
            for source_stat in stats['by_source']:
                print(f"   - {source_stat['source']}: {source_stat['count']} files, {source_stat['size_gb']:.2f} GB")
        
        elif command == "ingest" and len(sys.argv) > 2:
            path = sys.argv[2]
            source = sys.argv[3] if len(sys.argv) > 3 else "unknown"
            
            if os.path.isdir(path):
                ingest_directory(path, source)
            elif os.path.isfile(path):
                ingest_file(path, source)
            else:
                print(f"❌ Invalid path: {path}")
        
        elif command == "archive":
            output = sys.argv[2] if len(sys.argv) > 2 else "vault_archive.json"
            archive_to_json(output)
        
        else:
            print("""
Usage:
    python3 Partition_01/vault.py stats           - Show vault statistics
    python3 Partition_01/vault.py ingest <path> [source] - Ingest file or directory
    python3 Partition_01/vault.py archive [output]       - Export vault to JSON
            """)
    else:
        print("✅ Vault module initialized. Use with arguments for operations.")
