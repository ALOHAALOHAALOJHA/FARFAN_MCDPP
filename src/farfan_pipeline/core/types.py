"""
Core type definitions for F.A.R.F.A.N pipeline.
This is a stub module providing minimal types for test execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class ChunkData:
    """Represents a chunk of processed document data."""
    chunk_id: str
    content: str
    start_offset: int = 0
    end_offset: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class PreprocessedDocument:
    """Represents a preprocessed document ready for analysis."""
    doc_id: str
    chunks: list[ChunkData] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    
__all__ = ["ChunkData", "PreprocessedDocument"]
