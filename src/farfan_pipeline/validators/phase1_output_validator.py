"""
Module: phase1_output_validator
PHASE_LABEL: Phase 2
Sequence: V
Description: Phase 1 Output Validator (CP-0.1, CP-0.2)

Strictly validates the output of Phase 1 (Ingestion) before allowing Phase 2 to proceed.
Enforces the 60-chunk invariant (10 Policy Areas x 6 Dimensions).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from farfan_pipeline.core.types import PreprocessedDocument
from farfan_pipeline.phases.Phase_two.phase2_40_00_synchronization import ChunkMatrix

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    matrix_completeness_score: float
    integrity_hash: Optional[str] = None
    manifest_validated: bool = False

class Phase1OutputValidator:
    """
    Validates the handoff contract between Phase 1 and Phase 2.
    """

    EXPECTED_CHUNK_COUNT = 60
    EXPECTED_POLICY_AREAS = [f"PA{i:02d}" for i in range(1, 11)]  # PA01-PA10
    EXPECTED_DIMENSIONS = [f"DIM{i:02d}" for i in range(1, 7)]    # DIM01-DIM06

    @classmethod
    def validate_matrix_coordinates(cls, doc: PreprocessedDocument) -> ValidationResult:
        """
        CP-0.1: Validación fuerte de la matriz 10x6.
        """
        errors = []
        warnings = []
        
        # Check basic document structure
        if not doc.chunks:
            return ValidationResult(False, ["No chunks found in document"], [], 0.0)

        # 1. Verify 60 chunks invariant using ChunkMatrix (Phase 2 synchronization logic)
        try:
            matrix = ChunkMatrix(doc)
            chunk_matrix = matrix.chunk_matrix
            
            # Check for exactly 60 chunks
            if len(chunk_matrix) != cls.EXPECTED_CHUNK_COUNT:
                errors.append(f"Expected {cls.EXPECTED_CHUNK_COUNT} chunks, found {len(chunk_matrix)}")

            # Check for missing coordinates
            existing_coords = set(chunk_matrix.keys())
            expected_coords = {
                (pa, dim) for pa in cls.EXPECTED_POLICY_AREAS for dim in cls.EXPECTED_DIMENSIONS
            }
            missing = expected_coords - existing_coords
            if missing:
                errors.append(f"Missing coordinates: {sorted(missing)}")
            
            # 2. Integrity Check & 3. Empty Content Check & 4. Encoding
            valid_chunks = 0
            for coord, chunk in chunk_matrix.items():
                # Content Hash is already calculated by SmartPolicyChunk in ChunkMatrix
                if not chunk.content_hash:
                     errors.append(f"Chunk {chunk.chunk_id} missing content_hash")

                # Empty content check (already done in ChunkMatrix, but double check)
                if not chunk.text or not chunk.text.strip():
                     errors.append(f"Chunk {chunk.chunk_id} is empty")
                
                # Encoding check (UTF-8) - already implicit in string handling but making it explicit check
                try:
                    chunk.text.encode('utf-8')
                except UnicodeError:
                    errors.append(f"Chunk {chunk.chunk_id} has invalid UTF-8 encoding")
                
                valid_chunks += 1
            
            completeness_score = (valid_chunks / cls.EXPECTED_CHUNK_COUNT) * 100
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                matrix_completeness_score=completeness_score,
                integrity_hash=matrix.integrity_hash
            )

        except Exception as e:
            logger.error("Validation failed with exception", exc_info=True)
            return ValidationResult(False, [f"Validation exception: {str(e)}"], [], 0.0)

    @classmethod
    def validate_phase1_manifest(cls, artifacts_dir: Path) -> bool:
        """
        CP-0.2: Valida la existencia y contenido del manifest de Phase 1.
        """
        manifest_path = artifacts_dir / "phase1_manifest.json"
        
        if not manifest_path.exists():
            logger.error(f"Phase 1 manifest missing at {manifest_path}")
            return False
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_fields = ["timestamp", "chunk_count", "integrity_hash", "phase1_version"]
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                logger.error(f"Manifest missing fields: {missing_fields}")
                return False
                
            if manifest["chunk_count"] != cls.EXPECTED_CHUNK_COUNT:
                 logger.error(f"Manifest reports {manifest['chunk_count']} chunks, expected {cls.EXPECTED_CHUNK_COUNT}")
                 return False
                 
            return True
            
        except json.JSONDecodeError:
            logger.error("Phase 1 manifest is not valid JSON")
            return False
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return False
