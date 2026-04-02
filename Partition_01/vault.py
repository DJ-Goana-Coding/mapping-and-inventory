"""
ARK_CORE // PARTITION_01 // VAULT.PY
The Librarian's Archive & Ingest Logic
Handles archival and ingestion of the 321GB Empire data.
"""
import os
import json
import sqlite3
from datetime import datetime


class VaultArchive:
    """Archive and catalog manager for ARK_CORE assets."""
    
    def __init__(self, db_path="./Partition_01/tracker.db"):
        """Initialize vault with SQLite tracker database."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tracker database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archive_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                source_device TEXT,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def ingest_file(self, file_path, source_device="OPPO", metadata=None):
        """
        Ingest a file into the vault archive.
        
        Args:
            file_path: Relative path to the file
            source_device: Source device (OPPO, S10, LAPTOP)
            metadata: Optional JSON metadata
        """
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}
        
        file_size = os.path.getsize(file_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO archive_ledger (file_path, file_size, source_device, metadata)
            VALUES (?, ?, ?, ?)
        """, (file_path, file_size, source_device, json.dumps(metadata) if metadata else None))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success",
            "record_id": record_id,
            "file_path": file_path,
            "file_size": file_size,
            "source_device": source_device
        }
    
    def query_archive(self, source_device=None, limit=100):
        """Query archive ledger with optional filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if source_device:
            cursor.execute("""
                SELECT * FROM archive_ledger 
                WHERE source_device = ?
                ORDER BY archived_at DESC
                LIMIT ?
            """, (source_device, limit))
        else:
            cursor.execute("""
                SELECT * FROM archive_ledger 
                ORDER BY archived_at DESC
                LIMIT ?
            """, (limit,))
        
        records = cursor.fetchall()
        conn.close()
        
        return records
    
    def get_stats(self):
        """Get vault statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(file_size) FROM archive_ledger")
        total_files, total_size = cursor.fetchone()
        
        cursor.execute("SELECT source_device, COUNT(*) FROM archive_ledger GROUP BY source_device")
        by_device = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_files": total_files or 0,
            "total_size_bytes": total_size or 0,
            "total_size_gb": round((total_size or 0) / (1024**3), 2),
            "by_device": by_device
        }


def main():
    """Main vault CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ARK_CORE Vault Archive Manager")
    parser.add_argument("--ingest", help="Ingest a file into the vault")
    parser.add_argument("--device", default="OPPO", help="Source device (OPPO, S10, LAPTOP)")
    parser.add_argument("--stats", action="store_true", help="Show vault statistics")
    parser.add_argument("--query", action="store_true", help="Query archive ledger")
    
    args = parser.parse_args()
    
    vault = VaultArchive()
    
    if args.stats:
        stats = vault.get_stats()
        print("\n🏛️ VAULT ARCHIVE STATISTICS")
        print(f"Total Files: {stats['total_files']}")
        print(f"Total Size: {stats['total_size_gb']} GB ({stats['total_size_bytes']:,} bytes)")
        print(f"\nBy Device:")
        for device, count in stats['by_device'].items():
            print(f"  {device}: {count} files")
    
    elif args.ingest:
        result = vault.ingest_file(args.ingest, source_device=args.device)
        if result["status"] == "success":
            print(f"✅ Ingested: {result['file_path']} ({result['file_size']:,} bytes)")
        else:
            print(f"❌ Error: {result['message']}")
    
    elif args.query:
        records = vault.query_archive(limit=20)
        print(f"\n📚 ARCHIVE LEDGER (Last 20 entries)")
        for record in records:
            print(f"  [{record[0]}] {record[1]} - {record[4]} ({record[2]:,} bytes)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
