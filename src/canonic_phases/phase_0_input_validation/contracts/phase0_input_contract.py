"""Phase 0 Input Contract

Validates input file hashing and integrity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputContract:
    """Contract for Phase 0 input validation.
    
    Ensures that input files (PDF and questionnaire) have been properly hashed
    and meet integrity requirements.
    """
    
    def validate_hashes(self, pdf_sha256: str, questionnaire_sha256: str) -> None:
        """Validate input file hashes.
        
        Args:
            pdf_sha256: SHA-256 hash of the input PDF
            questionnaire_sha256: SHA-256 hash of the questionnaire
            
        Raises:
            AssertionError: If hash validation fails
        """
        assert len(pdf_sha256) == 64, f"Invalid PDF SHA-256 length: {len(pdf_sha256)}"
        assert all(c in "0123456789abcdef" for c in pdf_sha256.lower()), \
            "Invalid PDF SHA-256 format"
        
        assert len(questionnaire_sha256) == 64, \
            f"Invalid questionnaire SHA-256 length: {len(questionnaire_sha256)}"
        assert all(c in "0123456789abcdef" for c in questionnaire_sha256.lower()), \
            "Invalid questionnaire SHA-256 format"
