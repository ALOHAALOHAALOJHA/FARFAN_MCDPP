"""
SISAS Extractors Package

Real signal-emitting extractors that replace the passive data loading pattern.
Each extractor:
1. Analyzes text/documents
2. Creates Signal objects
3. Dispatches through SDO

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from .financial_chain_extractor import FinancialChainExtractor
from .causal_verb_extractor import CausalVerbExtractor
from .institutional_ner_extractor import InstitutionalNERExtractor
from .base_extractor import BaseSignalExtractor, ExtractionContext, ExtractionResult

__all__ = [
    "BaseSignalExtractor",
    "ExtractionContext",
    "ExtractionResult",
    "FinancialChainExtractor",
    "CausalVerbExtractor",
    "InstitutionalNERExtractor",
]
