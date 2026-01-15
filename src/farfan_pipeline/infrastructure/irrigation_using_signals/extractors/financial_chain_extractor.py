"""
Financial Chain Extractor (MC05)

Extracts financial/budgetary information from text and emits MC05 signals.

Patterns extracted:
- Currency amounts (pesos, millones, billones)
- Budget allocations
- Investment figures
- Financial projections

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import re
from typing import Any, Dict, List, Optional, Tuple
import logging

from .base_extractor import BaseSignalExtractor, ExtractionContext

from canonic_questionnaire_central.core.signal import Signal, SignalType

logger = logging.getLogger(__name__)


class FinancialChainExtractor(BaseSignalExtractor):
    """
    Extracts financial chains and emits MC05 signals.
    
    Calibrated empirical availability: 0.85 (from MC05_financial_chains.json)
    """
    
    SIGNAL_TYPE = SignalType.MC05_FINANCIAL
    CAPABILITIES_REQUIRED = ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS", "CURRENCY_NORMALIZATION"]
    EMPIRICAL_AVAILABILITY = 0.85
    DEFAULT_PHASE = "phase_1"
    DEFAULT_SLOT = "D1-Q1"  # Financial inputs dimension
    
    # Colombian peso patterns
    PATTERNS = [
        # $X millones/billones
        (r'\$\s*([0-9.,]+)\s*(millones?|billones?)', "currency_with_unit"),
        # X millones/billones de pesos
        (r'([0-9.,]+)\s*(millones?|billones?)\s+de\s+pesos', "amount_de_pesos"),
        # presupuesto de $X or presupuesto de X
        (r'presupuesto\s+de\s+\$?\s*([0-9.,]+)(?:\s*(millones?|billones?))?', "presupuesto"),
        # inversión de/por $X
        (r'inversi[oó]n\s+(?:de|por)\s+\$?\s*([0-9.,]+)(?:\s*(millones?|billones?))?', "inversion"),
        # asignación de $X
        (r'asignaci[oó]n\s+de\s+\$?\s*([0-9.,]+)(?:\s*(millones?|billones?))?', "asignacion"),
        # recursos por $X
        (r'recursos\s+(?:de|por)\s+\$?\s*([0-9.,]+)(?:\s*(millones?|billones?))?', "recursos"),
        # X COP
        (r'([0-9.,]+)\s*COP', "cop_explicit"),
        # Generic large number with context
        (r'(?:monto|valor|costo)\s+(?:de|por|total)?\s*\$?\s*([0-9.,]+)', "monto_generico"),
    ]
    
    UNIT_MULTIPLIERS = {
        "millon": 1_000_000,
        "millón": 1_000_000,
        "millones": 1_000_000,
        "billon": 1_000_000_000,
        "billón": 1_000_000_000,
        "billones": 1_000_000_000,
    }
    
    def __init__(self, sdo):
        super().__init__(sdo)
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), name) 
            for pattern, name in self.PATTERNS
        ]
    
    def extract(self, text: str, context: ExtractionContext) -> List[Signal]:
        """
        Extract financial amounts from text.
        
        Returns list of MC05 signals with normalized financial data.
        """
        signals = []
        seen_amounts = set()  # Dedup within same text
        
        for compiled_pattern, pattern_name in self._compiled_patterns:
            for match in compiled_pattern.finditer(text):
                try:
                    amount, unit, raw_match = self._parse_match(match, pattern_name)
                    
                    if amount is None:
                        continue
                    
                    # Normalize to base COP
                    normalized_amount = self._normalize_amount(amount, unit)
                    
                    # Dedup check
                    amount_key = f"{normalized_amount:.0f}"
                    if amount_key in seen_amounts:
                        continue
                    seen_amounts.add(amount_key)
                    
                    # Create payload
                    payload = {
                        "amount": normalized_amount,
                        "amount_raw": amount,
                        "currency": "COP",
                        "unit": unit or "pesos",
                        "unit_multiplier": self.UNIT_MULTIPLIERS.get(unit.lower(), 1) if unit else 1,
                        "context_snippet": self._get_context_window(text, match),
                        "pattern_matched": pattern_name,
                        "confidence": self._calculate_confidence(match, pattern_name)
                    }
                    
                    # Determine slot based on context
                    slot = self._determine_slot(text, match)
                    
                    signal = self.create_signal(
                        payload=payload,
                        context=context,
                        slot=slot,
                        extraction_pattern=pattern_name,
                        enrichment=True
                    )
                    
                    signals.append(signal)
                    
                except Exception as e:
                    logger.warning(f"Error parsing financial match: {e}")
                    continue
        
        logger.debug(f"Extracted {len(signals)} financial signals from text")
        return signals
    
    def _parse_match(self, match: re.Match, pattern_name: str) -> Tuple[Optional[float], Optional[str], str]:
        """Parse a regex match into (amount, unit, raw_string)."""
        raw_match = match.group(0)
        
        try:
            # Extract amount string
            amount_str = match.group(1).replace(',', '').replace('.', '')
            
            # Handle decimal points
            if ',' in match.group(1) or '.' in match.group(1):
                # Could be thousands separator or decimal
                parts = re.split(r'[,.]', match.group(1))
                if len(parts[-1]) == 2:  # Likely decimal
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    amount_str = ''.join(parts)
            
            amount = float(amount_str)
            
            # Extract unit if present
            unit = None
            if len(match.groups()) > 1 and match.group(2):
                unit = match.group(2)
            
            return amount, unit, raw_match
            
        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse match '{raw_match}': {e}")
            return None, None, raw_match
    
    def _normalize_amount(self, amount: float, unit: Optional[str]) -> float:
        """Normalize amount to base COP."""
        if unit is None:
            return amount
        
        unit_lower = unit.lower()
        multiplier = self.UNIT_MULTIPLIERS.get(unit_lower, 1)
        return amount * multiplier
    
    def _get_context_window(self, text: str, match: re.Match, window: int = 100) -> str:
        """Get surrounding context for the match."""
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        return text[start:end].strip()
    
    def _calculate_confidence(self, match: re.Match, pattern_name: str) -> float:
        """Calculate confidence score for the extraction."""
        base_confidence = 0.7
        
        # Higher confidence for explicit patterns
        if pattern_name in ["currency_with_unit", "amount_de_pesos", "cop_explicit"]:
            base_confidence = 0.9
        elif pattern_name in ["presupuesto", "inversion", "asignacion"]:
            base_confidence = 0.85
        elif pattern_name == "monto_generico":
            base_confidence = 0.6
        
        return base_confidence
    
    def _determine_slot(self, text: str, match: re.Match) -> str:
        """Determine the appropriate question slot based on context."""
        context = text[max(0, match.start()-200):match.end()+200].lower()
        
        # Check for specific indicators
        if any(kw in context for kw in ["presupuesto", "asignación", "recursos"]):
            return "D1-Q1"  # Input resources
        elif any(kw in context for kw in ["inversión", "gasto", "ejecución"]):
            return "D1-Q2"  # Financial execution
        elif any(kw in context for kw in ["meta", "proyección", "estimado"]):
            return "D1-Q3"  # Financial planning
        
        return self.DEFAULT_SLOT
