"""
Module: handoff_contracts
Description: Data models for Phase 1 -> Phase 2 handoff contracts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Phase1Manifest:
    """
    Manifesto de entrega de Phase 1.
    Certifica la integridad y completitud del proceso de ingestión.
    """
    timestamp: str  # ISO 8601
    chunk_count: int
    integrity_hash: str  # SHA-256 del ChunkMatrix
    phase1_version: str
    document_id: str
    source_file: str
    
    # Optional metadata
    metadata: dict = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Valida la consistencia interna del manifest."""
        if self.chunk_count != 60:
            return False
        if not self.integrity_hash:
            return False
        return True
