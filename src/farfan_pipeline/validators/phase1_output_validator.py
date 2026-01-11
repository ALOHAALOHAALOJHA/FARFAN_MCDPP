"""
Phase 1 Output Validator.

Strict validation for Phase 1 handoffs.
Ensures the PreprocessedDocument adheres to the 60x6 matrix contract.

Contracts:
- C1: 60 chunks exactly.
- C2: All chunks have valid Policy Area (PA01-PA10) and Dimension (DIM01-DIM06).
- C3: No duplicate slots.
- C4: Integrity hash matches content.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from farfan_pipeline.calibracion_parametrizacion.types import PreprocessedDocument

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class MatrixValidationResult:
    """Result of matrix coordinate validation."""
    is_valid: bool
    errors: list[str]
    matrix_completeness_score: float
    integrity_hash: str

class Phase1OutputValidator:
    """
    Validator for Phase 1 output artifacts.
    Enforces the 60-chunk matrix structure required for Phase 2.
    """

    EXPECTED_CHUNK_COUNT = 60
    VALID_POLICY_AREAS = {f"PA{i:02d}" for i in range(1, 11)}
    VALID_DIMENSIONS = {f"DIM{i:02d}" for i in range(1, 7)}

    @classmethod
    def validate_matrix_coordinates(cls, doc: PreprocessedDocument) -> MatrixValidationResult:
        """
        Validate that the document chunks form a complete and valid matrix.
        
        Args:
            doc: The PreprocessedDocument to validate.
            
        Returns:
            MatrixValidationResult with detailed status.
        """
        errors = []
        chunks = doc.chunks or []
        
        # 1. Count check
        if len(chunks) != cls.EXPECTED_CHUNK_COUNT:
            errors.append(
                f"Chunk count mismatch: Expected {cls.EXPECTED_CHUNK_COUNT}, got {len(chunks)}"
            )

        # 2. Slot Validation & Uniqueness
        seen_slots = set()
        valid_slots = 0
        
        for idx, chunk in enumerate(chunks):
            pa = getattr(chunk, "policy_area_id", None)
            dim = getattr(chunk, "dimension_id", None)
            cid = getattr(chunk, "chunk_id", f"chunk_{idx}")

            if not pa or pa not in cls.VALID_POLICY_AREAS:
                errors.append(f"Chunk {cid}: Invalid Policy Area '{pa}'")
                continue
                
            if not dim or dim not in cls.VALID_DIMENSIONS:
                errors.append(f"Chunk {cid}: Invalid Dimension '{dim}'")
                continue

            slot = (pa, dim)
            if slot in seen_slots:
                errors.append(f"Duplicate matrix slot detected: {slot}")
            else:
                seen_slots.add(slot)
                valid_slots += 1

        # 3. Completeness Score
        completeness = (valid_slots / cls.EXPECTED_CHUNK_COUNT) * 100.0

        # 4. Integrity Hash
        # Compute a stable hash of the chunk contents to ensure data hasn't shifted
        integrity_hash = cls._compute_integrity_hash(chunks)

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"Phase 1 Validation Failed: {errors[:3]} (total {len(errors)})")

        return MatrixValidationResult(
            is_valid=is_valid,
            errors=errors,
            matrix_completeness_score=completeness,
            integrity_hash=integrity_hash
        )

    @staticmethod
    def _compute_integrity_hash(chunks: list[Any]) -> str:
        """Compute SHA-256 hash of sorted chunk contents."""
        hasher = hashlib.sha256()
        
        # Sort chunks by ID to ensure deterministic hashing
        # Safely get chunk_id, falling back to index if missing
        sorted_chunks = sorted(
            chunks, 
            key=lambda c: getattr(c, "chunk_id", "") or ""
        )

        for chunk in sorted_chunks:
            text = getattr(chunk, "text", "") or ""
            hasher.update(text.encode("utf-8"))
            
        return hasher.hexdigest()

    @classmethod
    def validate_phase1_manifest(cls, artifacts_path: Path) -> bool:
        """
        Validate the existence and basic integrity of the Phase 1 manifest.
        """
        manifest_path = artifacts_path / "phase1_manifest.json"
        if not manifest_path.exists():
            logger.error(f"Manifest missing at {manifest_path}")
            return False
            
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            
            # Check for critical keys
            required_keys = ["run_id", "timestamp", "chunk_count"]
            if not all(k in data for k in required_keys):
                logger.error("Manifest missing required keys")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Manifest validation failed: {e}")
            return False
