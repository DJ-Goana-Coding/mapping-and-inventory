#!/usr/bin/env python3
"""
📦 SYNC QUEUE MANAGER
Mobile Citadel Command Center - Offline/Online Sync Queue

Manages queued operations for batch execution when connectivity is available.
Implements priority-based sync with deferred operations for offline periods.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class SyncPriority(Enum):
    """Sync operation priority levels"""
    CRITICAL = 1    # Security updates, emergency commits
    HIGH = 2        # Code changes, bug fixes
    NORMAL = 3      # Features, documentation
    LOW = 4         # Discovery data, logs
    BULK = 5        # Large datasets, models

class SyncOperation(Enum):
    """Types of sync operations"""
    GIT_PULL = "git_pull"
    GIT_PUSH = "git_push"
    HF_PULL = "hf_pull"
    HF_PUSH = "hf_push"
    GDRIVE_SYNC = "gdrive_sync"
    MODEL_DOWNLOAD = "model_download"
    DATASET_SYNC = "dataset_sync"
    MANIFEST_UPDATE = "manifest_update"

@dataclass
class QueuedOperation:
    """Represents a queued sync operation"""
    id: str
    operation: str
    priority: int
    created_at: str
    repo: Optional[str] = None
    branch: Optional[str] = None
    files: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    size_estimate_mb: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "queued"  # queued, in_progress, completed, failed

class SyncQueueManager:
    """Manages sync queue for offline/online operations"""
    
    def __init__(self, queue_dir: str = "/tmp/mobile_citadel/sync_queue"):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.queue_dir / "queue.json"
        self.history_file = self.queue_dir / "history.json"
        self.load_queue()
    
    def load_queue(self) -> List[QueuedOperation]:
        """Load queue from disk"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.queue = [QueuedOperation(**op) for op in data]
                    return self.queue
            except (json.JSONDecodeError, IOError):
                pass
        self.queue = []
        return self.queue
    
    def save_queue(self):
        """Save queue to disk"""
        with open(self.queue_file, 'w') as f:
            json.dump([asdict(op) for op in self.queue], f, indent=2)
    
    def add_operation(
        self,
        operation: SyncOperation,
        priority: SyncPriority,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        files: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        size_estimate_mb: Optional[float] = None
    ) -> str:
        """Add operation to queue"""
        # Generate unique ID
        op_data = f"{operation.value}_{repo}_{branch}_{datetime.utcnow().isoformat()}"
        op_id = hashlib.md5(op_data.encode()).hexdigest()[:12]
        
        queued_op = QueuedOperation(
            id=op_id,
            operation=operation.value,
            priority=priority.value,
            created_at=datetime.utcnow().isoformat(),
            repo=repo,
            branch=branch,
            files=files,
            metadata=metadata or {},
            size_estimate_mb=size_estimate_mb
        )
        
        self.queue.append(queued_op)
        self.save_queue()
        
        return op_id
    
    def get_prioritized_queue(self) -> List[QueuedOperation]:
        """Get queue sorted by priority"""
        return sorted(
            [op for op in self.queue if op.status == "queued"],
            key=lambda x: (x.priority, x.created_at)
        )
    
    def get_operation(self, op_id: str) -> Optional[QueuedOperation]:
        """Get operation by ID"""
        for op in self.queue:
            if op.id == op_id:
                return op
        return None
    
    def update_status(self, op_id: str, status: str):
        """Update operation status"""
        for op in self.queue:
            if op.id == op_id:
                op.status = status
                self.save_queue()
                break
    
    def mark_completed(self, op_id: str):
        """Mark operation as completed and archive"""
        op = self.get_operation(op_id)
        if op:
            op.status = "completed"
            self.save_queue()
            self._archive_operation(op)
    
    def mark_failed(self, op_id: str, error: str = None):
        """Mark operation as failed and retry if possible"""
        op = self.get_operation(op_id)
        if op:
            op.retry_count += 1
            if op.retry_count >= op.max_retries:
                op.status = "failed"
                if error:
                    op.metadata["last_error"] = error
            else:
                op.status = "queued"  # Retry
            self.save_queue()
    
    def _archive_operation(self, op: QueuedOperation):
        """Archive completed operation to history"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        history.append(asdict(op))
        
        with open(self.history_file, 'w') as f:
            json.dump(history[-1000:], f, indent=2)  # Keep last 1000
    
    def clear_completed(self):
        """Remove completed operations from queue"""
        self.queue = [op for op in self.queue if op.status != "completed"]
        self.save_queue()
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        stats = {
            "total_queued": len([op for op in self.queue if op.status == "queued"]),
            "in_progress": len([op for op in self.queue if op.status == "in_progress"]),
            "completed": len([op for op in self.queue if op.status == "completed"]),
            "failed": len([op for op in self.queue if op.status == "failed"]),
            "by_priority": {},
            "by_operation": {},
            "total_size_mb": 0
        }
        
        for op in self.queue:
            if op.status == "queued":
                # By priority
                priority_name = SyncPriority(op.priority).name
                stats["by_priority"][priority_name] = stats["by_priority"].get(priority_name, 0) + 1
                
                # By operation
                stats["by_operation"][op.operation] = stats["by_operation"].get(op.operation, 0) + 1
                
                # Total size
                if op.size_estimate_mb:
                    stats["total_size_mb"] += op.size_estimate_mb
        
        return stats
    
    def get_next_batch(self, max_operations: int = 10, max_size_mb: float = 100.0) -> List[QueuedOperation]:
        """
        Get next batch of operations to execute.
        Respects max count and total size limits.
        """
        batch = []
        total_size = 0.0
        
        for op in self.get_prioritized_queue():
            if len(batch) >= max_operations:
                break
            
            op_size = op.size_estimate_mb or 0
            if total_size + op_size > max_size_mb and len(batch) > 0:
                break
            
            batch.append(op)
            total_size += op_size
        
        return batch
    
    def generate_sync_report(self) -> str:
        """Generate human-readable sync queue report"""
        stats = self.get_queue_stats()
        prioritized = self.get_prioritized_queue()
        
        report = []
        report.append("=" * 60)
        report.append("📦 SYNC QUEUE REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.utcnow().isoformat()}")
        report.append(f"\nQueue Status:")
        report.append(f"  Queued: {stats['total_queued']}")
        report.append(f"  In Progress: {stats['in_progress']}")
        report.append(f"  Completed: {stats['completed']}")
        report.append(f"  Failed: {stats['failed']}")
        
        if stats['by_priority']:
            report.append(f"\nBy Priority:")
            for priority, count in sorted(stats['by_priority'].items()):
                report.append(f"  {priority}: {count}")
        
        if stats['by_operation']:
            report.append(f"\nBy Operation:")
            for operation, count in sorted(stats['by_operation'].items()):
                report.append(f"  {operation}: {count}")
        
        report.append(f"\nEstimated Total Size: {stats['total_size_mb']:.1f} MB")
        
        if prioritized:
            report.append(f"\nNext Operations (Top 5):")
            for i, op in enumerate(prioritized[:5], 1):
                report.append(f"  {i}. [{SyncPriority(op.priority).name}] {op.operation}")
                if op.repo:
                    report.append(f"     Repo: {op.repo}")
                if op.size_estimate_mb:
                    report.append(f"     Size: {op.size_estimate_mb:.1f} MB")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Main execution - manage sync queue"""
    import sys
    
    manager = SyncQueueManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "add":
            # Example: add git_push HIGH mapping-and-inventory main
            if len(sys.argv) >= 5:
                operation = SyncOperation[sys.argv[2].upper()]
                priority = SyncPriority[sys.argv[3].upper()]
                repo = sys.argv[4] if len(sys.argv) > 4 else None
                branch = sys.argv[5] if len(sys.argv) > 5 else None
                
                op_id = manager.add_operation(operation, priority, repo=repo, branch=branch)
                print(f"✅ Operation queued: {op_id}")
            else:
                print("Usage: sync_queue_manager.py add <operation> <priority> [repo] [branch]")
        
        elif command == "stats":
            print(manager.generate_sync_report())
        
        elif command == "next":
            batch = manager.get_next_batch()
            print(f"Next batch ({len(batch)} operations):")
            for op in batch:
                print(f"  • [{SyncPriority(op.priority).name}] {op.operation} - {op.repo or 'N/A'}")
        
        elif command == "clear":
            manager.clear_completed()
            print("✅ Cleared completed operations")
        
        else:
            print(f"Unknown command: {command}")
    else:
        # Default: show stats
        print(manager.generate_sync_report())


if __name__ == "__main__":
    main()
