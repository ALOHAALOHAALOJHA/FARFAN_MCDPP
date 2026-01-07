"""
Quantitative Triplet Extractor (MC01) - Empirically Calibrated.

Extracts quantitative data triplets: línea_base (baseline value), año (year),
fuente (source citation).

This extractor implements MC01 (Quantitative Triplet) - the highest-priority
signal type with empirical_availability: 0.78–0.94 across slots.

Empirical Calibration:
- Triplets completos per plan: mean=78, min=25, max=155
- Porcentajes per plan: mean=485, std=195
- Montos per plan: mean=285, std=98
- Confidence threshold: 0.66 (at least 2/3 components)
- Pattern match quality weight: 0.3

Innovation Features:
- Proximity-based component linking (año within 50 chars, fuente within 200)
- Multiple value formats (percentages, currency, integers, decimals)
- Year validation (1990-2030 range)
- Source citation normalization
- Completeness scoring

Author: CQC Extractor Excellence Framework
Version: 1.0.0
Date: 2026-01-07
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from collections import defaultdict

from .empirical_extractor_base import (
    PatternBasedExtractor,
    ExtractionResult
)

logger = logging.getLogger(__name__)


@dataclass
class QuantitativeTriplet:
    """Represents a detected quantitative triplet."""
    linea_base: Optional[str]  # Baseline value
    linea_base_normalized: Optional[float]  # Normalized numeric value
    value_type: str  # percentage, currency, integer, decimal
    ano: Optional[int]  # Year
    fuente: Optional[str]  # Source citation
    completeness: float  # 0.0 - 1.0 (count of non-null / 3)
    confidence: float
    text_span: Tuple[int, int]
    context: str


class QuantitativeTripletExtractor(PatternBasedExtractor):
    """
    Extractor for quantitative triplets: baseline value + year + source.
    
    Highest-priority signal type per integration_map with:
    - 94 questions mapped (coverage: 0.31)
    - Dimensions primary: DIM01_INS, DIM03_PRO, DIM04_RES
    - Scoring modality: TYPE_A
    """

    # Proximity thresholds (in characters)
    YEAR_PROXIMITY = 50  # año within 50 chars of línea_base
    SOURCE_PROXIMITY = 200  # fuente within 200 chars
    
    # Year validation range
    YEAR_MIN = 1990
    YEAR_MAX = 2030

    def __init__(self, calibration_file: Optional[Path] = None):
        super().__init__(
            signal_type="QUANTITATIVE_TRIPLET",  # Must match integration_map key
            calibration_file=calibration_file,
            auto_validate=True
        )
        
        # Build extraction patterns
        self._build_patterns()
        
        logger.info("QuantitativeTripletExtractor initialized")

    def _build_patterns(self):
        """Build regex patterns for triplet extraction."""
        
        # Value patterns (línea_base)
        self.value_patterns = {
            'percentage': [
                # Standard percentage: 45.5%, 45,5%
                r'(\d{1,3}(?:[.,]\d{1,2})?)\s*%',
                # Percentage with text: el 45% de la población
                r'(?:el\s+)?(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:de\s+(?:la\s+)?(?:población|hogares|familias|niños|mujeres))?',
            ],
            'currency': [
                # Colombian pesos: $1.500.000, $1,500,000
                r'\$\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)',
                # Millions/billions: 1.500 millones, 2.5 billones
                r'(\d{1,3}(?:[.,]\d{1,3})?)\s*(?:millones?|billones?)',
                # Currency codes: COP 1.500.000
                r'(?:COP|USD)\s*(\d{1,3}(?:[.,]\d{3})*)',
            ],
            'integer': [
                # Large integers with separators: 1.500.000
                r'(\d{1,3}(?:\.\d{3})+)(?!\s*%)',
                # Plain integers: 15000 (followed by unit word)
                r'(\d{4,})(?=\s+(?:personas|habitantes|familias|hogares|niños|mujeres|hombres|viviendas|hectáreas|kilómetros|metros))',
            ],
            'decimal': [
                # Decimal values: 0.45, 0,45
                r'(\d+[.,]\d+)(?!\s*%)',
                # Rates: tasa de 0.12
                r'(?:tasa|índice|razón)\s+(?:de\s+)?(\d+[.,]\d+)',
            ],
        }
        
        # Year patterns
        self.year_patterns = [
            # Explicit year: año 2023, 2023
            r'(?:año\s+)?(\b20[0-3]\d\b|\b19[9]\d\b)',
            # Year ranges: 2020-2023 (extract end year)
            r'\b20[0-3]\d\s*[-–—]\s*(20[0-3]\d)\b',
            # Period references: vigencia 2023
            r'(?:vigencia|período|periodo)\s+(\b20[0-3]\d\b)',
            # Date formats: 15/03/2023, marzo de 2023
            r'(?:\d{1,2}/\d{1,2}/|(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?)(\b20[0-3]\d\b)',
        ]
        
        # Source patterns (fuente)
        self.source_patterns = [
            # Explicit source: Fuente: DANE
            r'[Ff]uente[:\s]+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s,\-]{2,50})',
            # According to: Según el DANE
            r'[Ss]egún\s+(?:el\s+)?([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{2,30})',
            # Parenthetical source: (DANE, 2023)
            r'\(([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{2,20}),?\s*\d{4}\)',
            # Institutional acronyms: DANE, DNP, ICBF
            r'\b(DANE|DNP|ICBF|CONPES|SISBEN|ANSPE|DPS|MinSalud|MinEducación|MinAmbiente|IDEAM|IGAC|Planeación\s+Nacional)\b',
            # Census/Survey references
            r'(?:Censo|Encuesta|Estudio)\s+(?:de\s+)?([A-Za-záéíóúñ\s]{2,40})',
        ]
        
        # Compile all patterns
        self._compiled_value_patterns = {
            vtype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for vtype, patterns in self.value_patterns.items()
        }
        self._compiled_year_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.year_patterns
        ]
        self._compiled_source_patterns = [
            re.compile(p) for p in self.source_patterns
        ]

    def extract(self, text: str, context: Optional[Dict] = None) -> ExtractionResult:
        """
        Extract quantitative triplets from text.
        
        A triplet consists of:
        - línea_base: A quantitative value (percentage, currency, number)
        - año: A reference year
        - fuente: A source citation
        
        Components are linked by proximity.
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # Step 1: Extract all values
        values = self._extract_values(text)
        
        # Step 2: Extract all years
        years = self._extract_years(text)
        
        # Step 3: Extract all sources
        sources = self._extract_sources(text)
        
        # Step 4: Link components by proximity to form triplets
        triplets = self._link_components(text, values, years, sources)
        
        # Step 5: Build matches
        matches = []
        total_completeness = 0.0
        
        for triplet in triplets:
            match = {
                "linea_base": triplet.linea_base,
                "linea_base_normalized": triplet.linea_base_normalized,
                "value_type": triplet.value_type,
                "ano": triplet.ano,
                "fuente": triplet.fuente,
                "completeness": triplet.completeness,
                "confidence": triplet.confidence,
                "span_start": triplet.text_span[0],
                "span_end": triplet.text_span[1],
                "context": triplet.context,
            }
            matches.append(match)
            total_completeness += triplet.completeness
        
        # Calculate overall confidence
        # Formula: 0.7 * avg_completeness + 0.3 * pattern_match_quality
        avg_completeness = total_completeness / len(triplets) if triplets else 0.0
        pattern_quality = min(1.0, len(triplets) / 10)  # Normalize by expected count
        overall_confidence = 0.7 * avg_completeness + 0.3 * pattern_quality
        
        # Build metadata
        by_type = defaultdict(int)
        for m in matches:
            by_type[m["value_type"]] += 1
        
        complete_triplets = sum(1 for m in matches if m["completeness"] >= 0.66)
        
        result = ExtractionResult(
            extractor_id="QuantitativeTripletExtractor",
            signal_type="QUANTITATIVE_TRIPLET",
            matches=matches,
            confidence=overall_confidence,
            metadata={
                "total_triplets": len(matches),
                "complete_triplets": complete_triplets,
                "by_value_type": dict(by_type),
                "avg_completeness": round(avg_completeness, 3),
                "values_found": len(values),
                "years_found": len(years),
                "sources_found": len(sources),
            }
        )
        
        # Validate
        if self.auto_validate:
            validation = self._validate_extraction(result)
            result.metadata["validation"] = validation
        
        return result

    def _extract_values(self, text: str) -> List[Dict]:
        """Extract all quantitative values from text."""
        values = []
        
        for value_type, patterns in self._compiled_value_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    raw_value = match.group(1)
                    normalized = self._normalize_value(raw_value, value_type)
                    
                    values.append({
                        "raw": raw_value,
                        "normalized": normalized,
                        "type": value_type,
                        "start": match.start(),
                        "end": match.end(),
                        "full_match": match.group(0),
                    })
        
        # Deduplicate by position
        values = self._deduplicate_by_position(values)
        return values

    def _extract_years(self, text: str) -> List[Dict]:
        """Extract all years from text."""
        years = []
        
        for pattern in self._compiled_year_patterns:
            for match in pattern.finditer(text):
                year_str = match.group(1)
                try:
                    year = int(year_str)
                    if self.YEAR_MIN <= year <= self.YEAR_MAX:
                        years.append({
                            "year": year,
                            "start": match.start(),
                            "end": match.end(),
                        })
                except ValueError:
                    continue
        
        # Deduplicate by year value
        seen = set()
        unique_years = []
        for y in years:
            key = (y["year"], y["start"])
            if key not in seen:
                seen.add(key)
                unique_years.append(y)
        
        return unique_years

    def _extract_sources(self, text: str) -> List[Dict]:
        """Extract all source citations from text."""
        sources = []
        
        for pattern in self._compiled_source_patterns:
            for match in pattern.finditer(text):
                source = match.group(1).strip() if match.groups() else match.group(0)
                # Clean source
                source = re.sub(r'\s+', ' ', source).strip()
                
                sources.append({
                    "source": source,
                    "start": match.start(),
                    "end": match.end(),
                })
        
        # Deduplicate by position
        sources = self._deduplicate_by_position(sources)
        return sources

    def _link_components(
        self, 
        text: str, 
        values: List[Dict], 
        years: List[Dict], 
        sources: List[Dict]
    ) -> List[QuantitativeTriplet]:
        """Link components by proximity to form triplets."""
        triplets = []
        used_values = set()
        
        for val in values:
            if val["start"] in used_values:
                continue
            
            # Find nearest year within proximity
            nearest_year = self._find_nearest(val, years, self.YEAR_PROXIMITY)
            
            # Find nearest source within proximity
            nearest_source = self._find_nearest(val, sources, self.SOURCE_PROXIMITY)
            
            # Calculate completeness
            components = 1  # value is always present
            if nearest_year:
                components += 1
            if nearest_source:
                components += 1
            completeness = components / 3
            
            # Only include if meets minimum completeness
            if completeness >= 0.33:  # At least value present
                # Calculate confidence
                pattern_quality = 0.9 if val["type"] == "percentage" else 0.8
                confidence = 0.7 * completeness + 0.3 * pattern_quality
                
                # Get context window
                ctx_start = max(0, val["start"] - 50)
                ctx_end = min(len(text), val["end"] + 50)
                context = text[ctx_start:ctx_end]
                
                triplet = QuantitativeTriplet(
                    linea_base=val["raw"],
                    linea_base_normalized=val["normalized"],
                    value_type=val["type"],
                    ano=nearest_year["year"] if nearest_year else None,
                    fuente=nearest_source["source"] if nearest_source else None,
                    completeness=completeness,
                    confidence=confidence,
                    text_span=(val["start"], val["end"]),
                    context=context.strip(),
                )
                triplets.append(triplet)
                used_values.add(val["start"])
        
        return triplets

    def _find_nearest(
        self, 
        value: Dict, 
        candidates: List[Dict], 
        max_distance: int
    ) -> Optional[Dict]:
        """Find the nearest candidate within max_distance."""
        val_center = (value["start"] + value["end"]) / 2
        
        nearest = None
        min_dist = float('inf')
        
        for cand in candidates:
            cand_center = (cand["start"] + cand["end"]) / 2
            dist = abs(val_center - cand_center)
            
            if dist < min_dist and dist <= max_distance:
                min_dist = dist
                nearest = cand
        
        return nearest

    def _normalize_value(self, raw: str, value_type: str) -> Optional[float]:
        """Normalize a raw value to a float."""
        try:
            # Remove thousands separators and normalize decimal point
            cleaned = raw.replace('.', '').replace(',', '.')
            return float(cleaned)
        except ValueError:
            return None

    def _deduplicate_by_position(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items that overlap in position."""
        if not items:
            return items
        
        # Sort by start position
        sorted_items = sorted(items, key=lambda x: x["start"])
        
        # Keep non-overlapping items (prefer longer matches)
        result = []
        for item in sorted_items:
            overlaps = False
            for existing in result:
                if (item["start"] < existing["end"] and item["end"] > existing["start"]):
                    overlaps = True
                    # Keep the longer match
                    if (item["end"] - item["start"]) > (existing["end"] - existing["start"]):
                        result.remove(existing)
                        result.append(item)
                    break
            if not overlaps:
                result.append(item)
        
        return result

    def _validate_extraction(self, result: ExtractionResult) -> Dict:
        """Validate extraction against calibration thresholds."""
        # From integration_map: completeness_threshold: 0.8, triplets_completos mean: 78
        complete_ratio = result.metadata.get("complete_triplets", 0) / max(1, result.metadata.get("total_triplets", 1))
        
        return {
            "passes_completeness": result.metadata.get("avg_completeness", 0) >= 0.66,
            "complete_triplet_ratio": round(complete_ratio, 3),
            "confidence_adequate": result.confidence >= 0.6,
            "triplet_count_reasonable": 1 <= result.metadata.get("total_triplets", 0) <= 200,
        }

    def _empty_result(self) -> ExtractionResult:
        """Return an empty result for invalid input."""
        return ExtractionResult(
            extractor_id="QuantitativeTripletExtractor",
            signal_type="QUANTITATIVE_TRIPLET",
            matches=[],
            confidence=0.0,
            metadata={
                "total_triplets": 0,
                "complete_triplets": 0,
                "by_value_type": {},
                "avg_completeness": 0.0,
                "values_found": 0,
                "years_found": 0,
                "sources_found": 0,
            }
        )
