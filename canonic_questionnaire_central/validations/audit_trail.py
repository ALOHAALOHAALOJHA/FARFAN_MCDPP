"""
Immutable Audit Trail for Enrichment Operations

Provides verifiable, tamper-proof logging of all enrichment
operations for compliance and debugging.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Single immutable audit entry."""
    
    entry_id: str
    timestamp: str
    operation: str
    consumer_id: str
    request_data: Dict[str, Any]
    result_data: Dict[str, Any]
    gate_status: Dict[str, bool]
    violations: List[str]
    success: bool
    execution_time: float
    previous_hash: str
    entry_hash: str = field(init=False)
    
    def __post_init__(self):
        """Compute entry hash after initialization."""
        self.entry_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of entry (excluding entry_hash itself)."""
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "consumer_id": self.consumer_id,
            "request_data": self.request_data,
            "result_data": self.result_data,
            "gate_status": self.gate_status,
            "violations": self.violations,
            "success": self.success,
            "execution_time": self.execution_time,
            "previous_hash": self.previous_hash
        }
        
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify entry hasn't been tampered with."""
        expected_hash = self._compute_hash()
        return expected_hash == self.entry_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AuditTrail:
    """
    Immutable audit trail with blockchain-like chaining.
    
    Each entry contains hash of previous entry, making tampering detectable.
    """
    
    def __init__(
        self,
        trail_id: str,
        max_memory_entries: int = 1000,
        persist_path: Optional[Path] = None
    ):
        self._trail_id = trail_id
        self._max_memory_entries = max_memory_entries
        self._persist_path = persist_path
        self._entries: deque[AuditEntry] = deque(maxlen=max_memory_entries)
        self._entry_count = 0
        self._genesis_hash = self._create_genesis_hash()
        self._last_hash = self._genesis_hash
        
        # Load existing trail if persist_path exists
        if persist_path and persist_path.exists():
            self._load_from_disk()
    
    def _create_genesis_hash(self) -> str:
        """Create genesis (first) hash for the trail."""
        genesis_data = {
            "trail_id": self._trail_id,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        json_str = json.dumps(genesis_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def append(
        self,
        operation: str,
        consumer_id: str,
        request_data: Dict[str, Any],
        result_data: Dict[str, Any],
        gate_status: Dict[str, bool],
        violations: List[str],
        success: bool,
        execution_time: float
    ) -> AuditEntry:
        """
        Append new entry to audit trail.
        
        Args:
            operation: Operation type (e.g., "enrichment", "validation")
            consumer_id: Consumer identifier
            request_data: Request parameters
            result_data: Result data
            gate_status: Status of validation gates
            violations: List of violations
            success: Whether operation succeeded
            execution_time: Execution time in seconds
            
        Returns:
            Created AuditEntry
        """
        entry_id = f"{self._trail_id}:{self._entry_count:08d}"
        timestamp = datetime.now().isoformat()
        
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            operation=operation,
            consumer_id=consumer_id,
            request_data=request_data,
            result_data=result_data,
            gate_status=gate_status,
            violations=violations,
            success=success,
            execution_time=execution_time,
            previous_hash=self._last_hash
        )
        
        self._entries.append(entry)
        self._last_hash = entry.entry_hash
        self._entry_count += 1
        
        # Persist if configured
        if self._persist_path:
            self._persist_entry(entry)
        
        return entry
    
    def verify_chain(self) -> bool:
        """
        Verify integrity of entire audit trail.
        
        Returns:
            True if trail is valid and unmodified
        """
        if not self._entries:
            return True
        
        # Verify each entry's integrity
        for entry in self._entries:
            if not entry.verify_integrity():
                logger.error(f"Entry {entry.entry_id} failed integrity check")
                return False
        
        # Verify chain linkage
        prev_hash = self._genesis_hash
        for entry in self._entries:
            if entry.previous_hash != prev_hash:
                logger.error(
                    f"Chain broken at {entry.entry_id}: "
                    f"expected previous_hash {prev_hash}, got {entry.previous_hash}"
                )
                return False
            prev_hash = entry.entry_hash
        
        return True
    
    def get_entries(
        self,
        consumer_id: Optional[str] = None,
        operation: Optional[str] = None,
        success_only: bool = False,
        limit: Optional[int] = None
    ) -> List[AuditEntry]:
        """
        Query audit entries with filters.
        
        Args:
            consumer_id: Filter by consumer ID
            operation: Filter by operation type
            success_only: Only return successful operations
            limit: Maximum number of entries to return
            
        Returns:
            List of matching AuditEntry objects
        """
        filtered = list(self._entries)
        
        if consumer_id:
            filtered = [e for e in filtered if e.consumer_id == consumer_id]
        
        if operation:
            filtered = [e for e in filtered if e.operation == operation]
        
        if success_only:
            filtered = [e for e in filtered if e.success]
        
        if limit:
            filtered = filtered[-limit:]
        
        return filtered
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics."""
        if not self._entries:
            return {
                "total_entries": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0
            }
        
        total = len(self._entries)
        successful = sum(1 for e in self._entries if e.success)
        exec_times = [e.execution_time for e in self._entries]
        
        # Group by operation
        by_operation = {}
        for entry in self._entries:
            op = entry.operation
            if op not in by_operation:
                by_operation[op] = {"count": 0, "success": 0}
            by_operation[op]["count"] += 1
            if entry.success:
                by_operation[op]["success"] += 1
        
        # Group by consumer
        by_consumer = {}
        for entry in self._entries:
            cid = entry.consumer_id
            if cid not in by_consumer:
                by_consumer[cid] = {"count": 0, "success": 0}
            by_consumer[cid]["count"] += 1
            if entry.success:
                by_consumer[cid]["success"] += 1
        
        return {
            "trail_id": self._trail_id,
            "total_entries": total,
            "successful_entries": successful,
            "failed_entries": total - successful,
            "success_rate": successful / total,
            "avg_execution_time": sum(exec_times) / len(exec_times),
            "min_execution_time": min(exec_times),
            "max_execution_time": max(exec_times),
            "by_operation": by_operation,
            "by_consumer": by_consumer,
            "chain_verified": self.verify_chain()
        }
    
    def export_to_file(self, output_path: Path, format: str = "json") -> None:
        """
        Export audit trail to file.
        
        Args:
            output_path: Output file path
            format: Export format ('json' or 'csv')
        """
        if format == "json":
            data = {
                "trail_id": self._trail_id,
                "genesis_hash": self._genesis_hash,
                "entry_count": self._entry_count,
                "entries": [e.to_dict() for e in self._entries],
                "chain_verified": self.verify_chain()
            }
            
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        
        elif format == "csv":
            import csv
            
            with open(output_path, "w", newline="") as f:
                if not self._entries:
                    return
                
                fieldnames = [
                    "entry_id", "timestamp", "operation", "consumer_id",
                    "success", "execution_time", "entry_hash", "previous_hash"
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in self._entries:
                    writer.writerow({
                        "entry_id": entry.entry_id,
                        "timestamp": entry.timestamp,
                        "operation": entry.operation,
                        "consumer_id": entry.consumer_id,
                        "success": entry.success,
                        "execution_time": entry.execution_time,
                        "entry_hash": entry.entry_hash,
                        "previous_hash": entry.previous_hash
                    })
        
        logger.info(f"Exported {len(self._entries)} entries to {output_path}")
    
    def _persist_entry(self, entry: AuditEntry) -> None:
        """Persist single entry to disk."""
        if not self._persist_path:
            return
        
        # Append to JSONL file
        with open(self._persist_path, "a") as f:
            json.dump(entry.to_dict(), f, default=str)
            f.write("\n")
    
    def _load_from_disk(self) -> None:
        """Load entries from persisted file."""
        if not self._persist_path or not self._persist_path.exists():
            return
        
        try:
            with open(self._persist_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = AuditEntry(**data)
                        self._entries.append(entry)
                        self._last_hash = entry.entry_hash
                        self._entry_count += 1
            
            logger.info(f"Loaded {len(self._entries)} entries from {self._persist_path}")
        except Exception as e:
            logger.error(f"Failed to load audit trail from {self._persist_path}: {e}")


class AuditTrailManager:
    """Manages multiple audit trails."""
    
    def __init__(self, base_path: Optional[Path] = None):
        self._base_path = base_path
        self._trails: Dict[str, AuditTrail] = {}
    
    def get_or_create_trail(
        self,
        trail_id: str,
        max_memory_entries: int = 1000
    ) -> AuditTrail:
        """Get existing trail or create new one."""
        if trail_id in self._trails:
            return self._trails[trail_id]
        
        persist_path = None
        if self._base_path:
            self._base_path.mkdir(parents=True, exist_ok=True)
            persist_path = self._base_path / f"{trail_id}.jsonl"
        
        trail = AuditTrail(
            trail_id=trail_id,
            max_memory_entries=max_memory_entries,
            persist_path=persist_path
        )
        
        self._trails[trail_id] = trail
        return trail
    
    def get_trail(self, trail_id: str) -> Optional[AuditTrail]:
        """Get existing trail."""
        return self._trails.get(trail_id)
    
    def list_trails(self) -> List[str]:
        """List all trail IDs."""
        return list(self._trails.keys())


# Global audit trail manager
_audit_manager: Optional[AuditTrailManager] = None


def get_audit_manager(base_path: Optional[Path] = None) -> AuditTrailManager:
    """Get or create global audit trail manager."""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditTrailManager(base_path)
    return _audit_manager
