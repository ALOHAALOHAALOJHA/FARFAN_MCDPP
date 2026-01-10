"""
Structural Marker Extractor (MC03) - Empirically Calibrated.

Detects structural elements: PPI tables, budget matrices, indicator grids,
section headers, and document structure markers.

This extractor implements MC03 (Structural Marker) with:
- 87 questions mapped (coverage: 0.29)
- Critical for PPI table detection
- Table and section structure analysis

Empirical Calibration:
- PPI tables per plan: mean=12, std=5
- Budget matrices per plan: mean=4, std=2
- Section headers per plan: mean=45, std=20
- Table detection confidence: from_table=0.95

Innovation Features:
- Heuristic row/column detection
- Table type classification (PPI, budget, indicator)
- Section hierarchy extraction
- Document structure mapping

Author: CQC Extractor Excellence Framework
Version: 1.0.0
Date: 2026-01-07
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import logging
from collections import defaultdict
from enum import Enum

from .empirical_extractor_base import PatternBasedExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class StructureType(Enum):
    """Types of structural elements."""

    PPI_TABLE = "ppi_table"
    BUDGET_TABLE = "budget_table"
    INDICATOR_TABLE = "indicator_table"
    GENERIC_TABLE = "generic_table"
    SECTION_HEADER = "section_header"
    SUBSECTION_HEADER = "subsection_header"
    LIST_STRUCTURE = "list_structure"
    MATRIX = "matrix"


@dataclass
class StructuralMarker:
    """Represents a detected structural element."""

    structure_type: StructureType
    content_preview: str  # First N chars of content
    row_count: Optional[int]  # For tables
    column_count: Optional[int]  # For tables
    header_level: Optional[int]  # For section headers
    has_numeric_data: bool
    has_percentage_data: bool
    confidence: float
    text_span: Tuple[int, int]
    metadata: Dict[str, Any]


class StructuralMarkerExtractor(PatternBasedExtractor):
    """
    Extractor for document structural elements.

    Detects:
    1. PPI tables (Plan Plurianual de Inversiones)
    2. Budget allocation matrices
    3. Indicator tables
    4. Section headers at various levels
    5. List structures
    """

    # PPI table detection keywords
    PPI_KEYWORDS = [
        "plan plurianual",
        "plan de inversiones",
        "plurianual de inversiones",
        "programas y proyectos",
        "asignación presupuestal",
        "vigencia",
        "metas",
        "indicadores",
    ]

    # Budget table keywords
    BUDGET_KEYWORDS = [
        "presupuesto",
        "apropiación",
        "recursos",
        "fuente de financiación",
        "sgp",
        "recursos propios",
        "regalías",
    ]

    # Indicator table keywords
    INDICATOR_KEYWORDS = [
        "línea base",
        "meta",
        "indicador",
        "unidad de medida",
        "responsable",
        "fuente de verificación",
    ]

    def __init__(self, calibration_file: Optional[Path] = None):
        super().__init__(
            signal_type="STRUCTURAL_MARKER",  # Must match integration_map key
            calibration_file=calibration_file,
            auto_validate=True,
        )

        # Build detection patterns
        self._build_patterns()

        logger.info("StructuralMarkerExtractor initialized")

    def _build_patterns(self):
        """Build regex patterns for structure detection."""

        # Table detection patterns
        self.table_patterns = [
            # Markdown-style tables
            r"\|[^|\n]+\|(?:\s*\n\|[-:| ]+\|)?(?:\s*\n\|[^|\n]+\|)+",
            # Tab-separated rows (3+ columns)
            r"(?:[^\t\n]+\t){2,}[^\t\n]+(?:\n(?:[^\t\n]+\t){2,}[^\t\n]+)+",
            # Pipe-separated values
            r"(?:[^|\n]+\|){2,}[^|\n]+(?:\n(?:[^|\n]+\|){2,}[^|\n]+)+",
        ]

        # Table indicator patterns (text that suggests a table nearby)
        self.table_indicator_patterns = [
            r"(?:Tabla|Cuadro|Matriz)\s*(?:N[°º]?|No\.?)?\s*\d+",
            r"(?:Ver|Véase)\s+(?:tabla|cuadro|matriz)",
            r"(?:A\s+continuación|Siguiente)\s+(?:tabla|cuadro)",
        ]

        # Section header patterns
        self.header_patterns = [
            # Numbered sections: 1. TITULO, 1.1 Subtitulo
            (r"^(\d+)\.\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{3,80})$", 1),
            (r"^(\d+\.\d+)\s+([A-Za-záéíóúñ][A-Za-záéíóúñ\s]{3,80})$", 2),
            (r"^(\d+\.\d+\.\d+)\s+([A-Za-záéíóúñ][A-Za-záéíóúñ\s]{3,80})$", 3),
            # Roman numeral sections
            (r"^([IVXLC]+)\.\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{3,80})$", 1),
            # ALL CAPS headers
            (r"^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{5,50})$", 1),
            # Article/Chapter
            (r"^(?:ARTÍCULO|CAPÍTULO|SECCIÓN)\s+([IVXLC\d]+)[.:]\s+(.+)$", 1),
        ]

        # List patterns
        self.list_patterns = [
            # Bulleted lists
            r"(?:^|\n)[•\-\*]\s+[A-Za-záéíóúñ]",
            # Numbered lists
            r"(?:^|\n)\d+[.)\-]\s+[A-Za-záéíóúñ]",
            # Letter lists
            r"(?:^|\n)[a-zA-Z][.)\-]\s+[A-Za-záéíóúñ]",
        ]

        # Compile patterns
        self._compiled_table_patterns = [re.compile(p, re.MULTILINE) for p in self.table_patterns]
        self._compiled_table_indicators = [
            re.compile(p, re.IGNORECASE) for p in self.table_indicator_patterns
        ]
        self._compiled_header_patterns = [
            (re.compile(p, re.MULTILINE), level) for p, level in self.header_patterns
        ]
        self._compiled_list_patterns = [re.compile(p, re.MULTILINE) for p in self.list_patterns]

    def extract(self, text: str, context: Optional[Dict] = None) -> ExtractionResult:
        """
        Extract structural markers from text.
        """
        if not text or not text.strip():
            return self._empty_result()

        markers: List[StructuralMarker] = []

        # Detect tables
        table_markers = self._detect_tables(text)
        markers.extend(table_markers)

        # Detect section headers
        header_markers = self._detect_headers(text)
        markers.extend(header_markers)

        # Detect list structures
        list_markers = self._detect_lists(text)
        markers.extend(list_markers)

        # Sort by position
        markers.sort(key=lambda m: m.text_span[0])

        # Build matches
        matches = []
        for marker in markers:
            match = {
                "structure_type": marker.structure_type.value,
                "content_preview": marker.content_preview[:100],
                "row_count": marker.row_count,
                "column_count": marker.column_count,
                "header_level": marker.header_level,
                "has_numeric_data": marker.has_numeric_data,
                "has_percentage_data": marker.has_percentage_data,
                "confidence": marker.confidence,
                "span_start": marker.text_span[0],
                "span_end": marker.text_span[1],
                "metadata": marker.metadata,
            }
            matches.append(match)

        # Calculate overall confidence
        avg_confidence = sum(m["confidence"] for m in matches) / len(matches) if matches else 0.0

        # Build metadata
        by_type = defaultdict(int)
        for m in matches:
            by_type[m["structure_type"]] += 1

        ppi_tables = sum(1 for m in matches if m["structure_type"] == "ppi_table")

        result = ExtractionResult(
            extractor_id="StructuralMarkerExtractor",
            signal_type="STRUCTURAL_MARKER",
            matches=matches,
            confidence=avg_confidence,
            metadata={
                "total_structures": len(matches),
                "by_type": dict(by_type),
                "ppi_tables_detected": ppi_tables,
                "tables_with_numeric": sum(1 for m in matches if m.get("has_numeric_data")),
                "section_headers": by_type.get("section_header", 0)
                + by_type.get("subsection_header", 0),
            },
        )

        # Validate
        if self.auto_validate:
            validation = self._validate_extraction(result)
            result.metadata["validation"] = validation

        return result

    def _detect_tables(self, text: str) -> List[StructuralMarker]:
        """Detect tables in text."""
        markers = []

        # First, find explicit table patterns
        for pattern in self._compiled_table_patterns:
            for match in pattern.finditer(text):
                table_text = match.group(0)
                table_type, confidence = self._classify_table(table_text)
                rows, cols = self._count_table_dimensions(table_text)

                marker = StructuralMarker(
                    structure_type=table_type,
                    content_preview=table_text,
                    row_count=rows,
                    column_count=cols,
                    header_level=None,
                    has_numeric_data=self._has_numeric_data(table_text),
                    has_percentage_data=self._has_percentage_data(table_text),
                    confidence=confidence,
                    text_span=(match.start(), match.end()),
                    metadata={"detection_method": "pattern_match"},
                )
                markers.append(marker)

        # Also look for table indicators (implicit tables)
        for pattern in self._compiled_table_indicators:
            for match in pattern.finditer(text):
                # Check if we already have a table at this position
                pos = match.start()
                if any(m.text_span[0] <= pos <= m.text_span[1] for m in markers):
                    continue

                marker = StructuralMarker(
                    structure_type=StructureType.GENERIC_TABLE,
                    content_preview=match.group(0),
                    row_count=None,
                    column_count=None,
                    header_level=None,
                    has_numeric_data=False,
                    has_percentage_data=False,
                    confidence=0.6,  # Lower confidence for indicators
                    text_span=(match.start(), match.end()),
                    metadata={"detection_method": "indicator"},
                )
                markers.append(marker)

        return markers

    def _classify_table(self, table_text: str) -> Tuple[StructureType, float]:
        """Classify a table by its content."""
        text_lower = table_text.lower()

        # Check for PPI table
        ppi_score = sum(1 for kw in self.PPI_KEYWORDS if kw in text_lower)
        if ppi_score >= 2:
            return StructureType.PPI_TABLE, min(0.95, 0.7 + 0.1 * ppi_score)

        # Check for budget table
        budget_score = sum(1 for kw in self.BUDGET_KEYWORDS if kw in text_lower)
        if budget_score >= 2:
            return StructureType.BUDGET_TABLE, min(0.90, 0.65 + 0.1 * budget_score)

        # Check for indicator table
        indicator_score = sum(1 for kw in self.INDICATOR_KEYWORDS if kw in text_lower)
        if indicator_score >= 2:
            return StructureType.INDICATOR_TABLE, min(0.90, 0.65 + 0.1 * indicator_score)

        return StructureType.GENERIC_TABLE, 0.7

    def _count_table_dimensions(self, table_text: str) -> Tuple[Optional[int], Optional[int]]:
        """Count rows and columns in a table."""
        lines = table_text.strip().split("\n")
        rows = len(lines)

        # Estimate columns from first non-empty row
        cols = None
        for line in lines:
            if "|" in line:
                cols = line.count("|") + 1
                break
            elif "\t" in line:
                cols = line.count("\t") + 1
                break

        return rows if rows > 0 else None, cols

    def _detect_headers(self, text: str) -> List[StructuralMarker]:
        """Detect section headers."""
        markers = []

        for pattern, level in self._compiled_header_patterns:
            for match in pattern.finditer(text):
                header_text = match.group(0)

                # Skip if too short or looks like table content
                if len(header_text) < 5 or "|" in header_text:
                    continue

                structure_type = (
                    StructureType.SECTION_HEADER if level == 1 else StructureType.SUBSECTION_HEADER
                )

                marker = StructuralMarker(
                    structure_type=structure_type,
                    content_preview=header_text,
                    row_count=None,
                    column_count=None,
                    header_level=level,
                    has_numeric_data=False,
                    has_percentage_data=False,
                    confidence=0.85,
                    text_span=(match.start(), match.end()),
                    metadata={"level": level},
                )
                markers.append(marker)

        return markers

    def _detect_lists(self, text: str) -> List[StructuralMarker]:
        """Detect list structures."""
        markers = []

        for pattern in self._compiled_list_patterns:
            matches = list(pattern.finditer(text))

            # Group consecutive matches into list structures
            if len(matches) >= 2:
                # Find clusters of list items
                clusters = []
                current_cluster = [matches[0]]

                for i in range(1, len(matches)):
                    # If matches are within 500 chars, same list
                    if matches[i].start() - matches[i - 1].end() < 500:
                        current_cluster.append(matches[i])
                    else:
                        if len(current_cluster) >= 2:
                            clusters.append(current_cluster)
                        current_cluster = [matches[i]]

                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)

                # Create markers for each cluster
                for cluster in clusters:
                    start = cluster[0].start()
                    end = cluster[-1].end()
                    list_text = text[start:end]

                    marker = StructuralMarker(
                        structure_type=StructureType.LIST_STRUCTURE,
                        content_preview=list_text,
                        row_count=len(cluster),
                        column_count=None,
                        header_level=None,
                        has_numeric_data=self._has_numeric_data(list_text),
                        has_percentage_data=self._has_percentage_data(list_text),
                        confidence=0.75,
                        text_span=(start, end),
                        metadata={"item_count": len(cluster)},
                    )
                    markers.append(marker)

        return markers

    def _has_numeric_data(self, text: str) -> bool:
        """Check if text contains significant numeric data."""
        # Look for numbers that aren't just years
        numeric_pattern = r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b"
        matches = re.findall(numeric_pattern, text)
        # Filter out likely years
        non_year = [m for m in matches if not re.match(r"^(19|20)\d{2}$", m)]
        return len(non_year) >= 2

    def _has_percentage_data(self, text: str) -> bool:
        """Check if text contains percentage data."""
        return bool(re.search(r"\d+[.,]?\d*\s*%", text))

    def _validate_extraction(self, result: ExtractionResult) -> Dict:
        """Validate extraction."""
        return {
            "ppi_detection_adequate": result.metadata.get("ppi_tables_detected", 0) >= 1,
            "has_structure": result.metadata.get("total_structures", 0) > 0,
            "confidence_adequate": result.confidence >= 0.6,
        }

    def _empty_result(self) -> ExtractionResult:
        """Return an empty result for invalid input."""
        return ExtractionResult(
            extractor_id="StructuralMarkerExtractor",
            signal_type="STRUCTURAL_MARKER",
            matches=[],
            confidence=0.0,
            metadata={
                "total_structures": 0,
                "by_type": {},
                "ppi_tables_detected": 0,
                "tables_with_numeric": 0,
                "section_headers": 0,
            },
        )
