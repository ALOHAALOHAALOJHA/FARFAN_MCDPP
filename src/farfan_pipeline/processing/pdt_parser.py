"""
PDT Parser

Parses Plan de Desarrollo Territorial (PDT) documents and extracts structured information.
Implements tokenization, block detection, hierarchy validation, sequence verification,
section analysis, and table extraction.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

from farfan_pipeline.processing.pdt_structure import (
    BlockInfo,
    HeaderInfo,
    IndicatorRow,
    PDTStructure,
    PPIRow,
    SectionInfo,
)

logger = logging.getLogger(__name__)


class PDTParser:
    """Parser for Plan de Desarrollo Territorial documents."""

    BLOCK_PATTERNS = [
        (r"CAPÍTULO\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)", "CAPÍTULO"),
        (r"Línea\s+estratégica\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)", "Línea estratégica"),
        (r"Eje\s+estratégico\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)", "Eje estratégico"),
        (r"PROGRAMA\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)", "PROGRAMA"),
    ]

    SECTION_KEYWORDS = {
        "Diagnóstico": [
            "diagnóstico",
            "situación actual",
            "problemática",
            "análisis de contexto",
        ],
        "Estratégica": [
            "estratégica",
            "estrategia",
            "visión",
            "objetivos estratégicos",
            "líneas estratégicas",
        ],
        "PPI": ["plan plurianual", "inversiones", "presupuesto", "financiación"],
        "Seguimiento": [
            "seguimiento",
            "evaluación",
            "indicadores",
            "monitoreo",
            "medición",
        ],
    }

    NUMBERING_PATTERN = re.compile(
        r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?\s+(.+?)$", re.MULTILINE
    )

    MIN_BLOCK_TOKENS = 10
    MIN_BLOCK_NUMBERS = 1

    def __init__(self) -> None:
        """Initialize the PDT parser."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_pdf(self, pdf_path: str | Path) -> PDTStructure:
        """
        Parse a PDF file and extract PDT structure.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDTStructure with extracted information
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        full_text = self._extract_text_from_pdf(pdf_path)

        return self.parse_text(full_text)

    def parse_text(self, text: str) -> PDTStructure:
        """
        Parse text and extract PDT structure.

        Args:
            text: Full document text

        Returns:
            PDTStructure with extracted information
        """
        tokens = self._tokenize(text)
        total_tokens = len(tokens)

        blocks_found = self._detect_blocks(text)
        headers = self._extract_headers(text)
        hierarchy_score = self._validate_hierarchy(headers)

        block_sequence = list(blocks_found.keys())
        sequence_score = self._verify_sequence(block_sequence)

        sections_found = self._analyze_sections(text)

        indicator_rows = self._extract_indicator_matrix(text)
        ppi_rows = self._extract_ppi_matrix(text)

        return PDTStructure(
            total_tokens=total_tokens,
            full_text=text,
            blocks_found=blocks_found,
            headers=headers,
            block_sequence=block_sequence,
            sections_found=sections_found,
            indicator_rows=indicator_rows,
            ppi_rows=ppi_rows,
            hierarchy_score=hierarchy_score,
            sequence_score=sequence_score,
        )

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        text_parts = []

        try:
            doc = pymupdf.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_parts.append(page.get_text())
            doc.close()
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            raise

        return "\n".join(text_parts)

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize text by splitting on whitespace.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        return text.split()

    def _detect_blocks(self, text: str) -> dict[str, BlockInfo]:
        """
        Detect structural blocks (CAPÍTULO, Línea estratégica, etc.).

        Args:
            text: Input text

        Returns:
            Dictionary mapping block names to BlockInfo
        """
        blocks = {}

        for pattern, block_type in self.BLOCK_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                block_num = match.group(1)
                match.group(2).strip() if len(match.groups()) > 1 else ""
                block_name = f"{block_type} {block_num}"

                start_pos = match.end()
                end_pos = self._find_block_end(text, start_pos, pattern)

                block_text = text[start_pos:end_pos]

                tokens = self._tokenize(block_text)
                token_count = len(tokens)
                numbers_count = len(re.findall(r"\d+", block_text))

                if (
                    token_count >= self.MIN_BLOCK_TOKENS
                    and numbers_count >= self.MIN_BLOCK_NUMBERS
                ):
                    blocks[block_name] = BlockInfo(
                        text=block_text[:500],
                        tokens=token_count,
                        numbers_count=numbers_count,
                    )

        return blocks

    def _find_block_end(self, text: str, start_pos: int, current_pattern: str) -> int:
        """
        Find the end position of a block by looking for the next block header.

        Args:
            text: Full text
            start_pos: Start position of current block
            current_pattern: Pattern of current block type

        Returns:
            End position of block
        """
        next_pos = len(text)

        for pattern, _ in self.BLOCK_PATTERNS:
            match = re.search(pattern, text[start_pos:], re.IGNORECASE)
            if match:
                candidate_pos = start_pos + match.start()
                next_pos = min(candidate_pos, next_pos)

        return next_pos

    def _extract_headers(self, text: str) -> list[HeaderInfo]:
        """
        Extract headers with hierarchical numbering.

        Args:
            text: Input text

        Returns:
            List of HeaderInfo objects
        """
        headers = []

        for match in self.NUMBERING_PATTERN.finditer(text):
            groups = match.groups()
            level = sum(1 for g in groups[:4] if g is not None)
            header_text = groups[4].strip() if len(groups) > 4 else ""

            numbering_parts = [g for g in groups[:4] if g is not None]
            valid_numbering = self._is_valid_numbering(numbering_parts)

            if header_text and len(header_text) > 5:
                headers.append(
                    HeaderInfo(
                        level=level,
                        text=header_text[:200],
                        valid_numbering=valid_numbering,
                    )
                )

        return headers

    def _is_valid_numbering(self, numbering_parts: list[str]) -> bool:
        """
        Check if numbering follows valid hierarchical pattern.

        Args:
            numbering_parts: List of numbering components (e.g., ['1', '2', '3'])

        Returns:
            True if valid, False otherwise
        """
        try:
            for i, part in enumerate(numbering_parts):
                num = int(part)
                if num < 1:
                    return False
                if i == 0 and num > 100:
                    return False
            return True
        except (ValueError, TypeError):
            return False

    def _validate_hierarchy(self, headers: list[HeaderInfo]) -> float:
        """
        Validate header numbering hierarchy and return score.

        Args:
            headers: List of headers

        Returns:
            Score: 1.0 if ≥80% valid, 0.5 if ≥50% valid, 0.0 otherwise
        """
        if not headers:
            return 0.0

        valid_count = sum(1 for h in headers if h.valid_numbering)
        validity_ratio = valid_count / len(headers)

        if validity_ratio >= 0.8:
            return 1.0
        elif validity_ratio >= 0.5:
            return 0.5
        else:
            return 0.0

    def _verify_sequence(self, block_sequence: list[str]) -> float:
        """
        Verify block sequence order and return score.

        Args:
            block_sequence: List of block names in order

        Returns:
            Score: 1.0 if 0 inversions, 0.5 if 1 inversion, 0.0 if ≥2 inversions
        """
        if len(block_sequence) < 2:
            return 1.0

        expected_order = [
            "CAPÍTULO",
            "Eje estratégico",
            "Línea estratégica",
            "PROGRAMA",
        ]

        inversions = 0

        for i in range(len(block_sequence) - 1):
            current_type = self._get_block_type(block_sequence[i])
            next_type = self._get_block_type(block_sequence[i + 1])

            if current_type in expected_order and next_type in expected_order:
                current_idx = expected_order.index(current_type)
                next_idx = expected_order.index(next_type)

                if current_idx > next_idx:
                    inversions += 1

        if inversions == 0:
            return 1.0
        elif inversions == 1:
            return 0.5
        else:
            return 0.0

    def _get_block_type(self, block_name: str) -> str:
        """
        Extract block type from block name.

        Args:
            block_name: Full block name (e.g., "CAPÍTULO 1")

        Returns:
            Block type (e.g., "CAPÍTULO")
        """
        for _, block_type in self.BLOCK_PATTERNS:
            if block_name.startswith(block_type):
                return block_type
        return ""

    def _analyze_sections(self, text: str) -> dict[str, SectionInfo]:
        """
        Analyze major sections (Diagnóstico, Estratégica, PPI, Seguimiento).

        Args:
            text: Full text

        Returns:
            Dictionary mapping section names to SectionInfo
        """
        sections = {}
        text_lower = text.lower()

        for section_name, keywords in self.SECTION_KEYWORDS.items():
            section_info = self._extract_section_info(
                text, text_lower, section_name, keywords
            )
            sections[section_name] = section_info

        return sections

    def _extract_section_info(
        self, text: str, text_lower: str, section_name: str, keywords: list[str]
    ) -> SectionInfo:
        """
        Extract information about a specific section.

        Args:
            text: Full text
            text_lower: Lowercase version of text
            section_name: Name of section
            keywords: Keywords to search for

        Returns:
            SectionInfo object
        """
        keyword_matches = sum(text_lower.count(kw) for kw in keywords)
        present = keyword_matches > 0

        if not present:
            return SectionInfo(
                present=False,
                token_count=0,
                keyword_matches=0,
                number_count=0,
                sources_found=0,
            )

        section_start, section_end = self._find_section_boundaries(text_lower, keywords)

        section_text = text if section_start == -1 else text[section_start:section_end]

        tokens = self._tokenize(section_text)
        token_count = len(tokens)
        number_count = len(re.findall(r"\d+", section_text))
        sources_found = len(
            re.findall(
                r"\[(\d+)\]|referencias?|fuentes?|bibliografía",
                section_text,
                re.IGNORECASE,
            )
        )

        return SectionInfo(
            present=present,
            token_count=token_count,
            keyword_matches=keyword_matches,
            number_count=number_count,
            sources_found=sources_found,
        )

    def _find_section_boundaries(
        self, text_lower: str, keywords: list[str]
    ) -> tuple[int, int]:
        """
        Find start and end positions of a section.

        Args:
            text_lower: Lowercase text
            keywords: Section keywords

        Returns:
            Tuple of (start_pos, end_pos)
        """
        start_pos = -1

        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1 and (start_pos == -1 or pos < start_pos):
                start_pos = pos

        if start_pos == -1:
            return (-1, -1)

        end_pos = len(text_lower)

        for other_keywords in self.SECTION_KEYWORDS.values():
            if other_keywords == keywords:
                continue
            for keyword in other_keywords:
                pos = text_lower.find(keyword, start_pos + 1)
                if pos != -1 and pos < end_pos:
                    end_pos = pos

        return (start_pos, end_pos)

    def _extract_indicator_matrix(self, text: str) -> list[IndicatorRow]:
        """
        Extract Matriz de Indicadores table rows.

        Args:
            text: Full text

        Returns:
            List of IndicatorRow objects
        """
        rows: list[IndicatorRow] = []

        matrix_pattern = r"Matriz\s+de\s+Indicadores"
        match = re.search(matrix_pattern, text, re.IGNORECASE)

        if not match:
            return rows

        start_pos = match.end()
        section_text = text[start_pos : start_pos + 10000]

        table_rows = self._parse_table_rows(section_text)

        for row_data in table_rows:
            row = IndicatorRow(
                tipo=row_data.get("tipo", ""),
                linea_estrategica=row_data.get("linea_estrategica", ""),
                programa=row_data.get("programa", ""),
                nombre_indicador=row_data.get("nombre_indicador", ""),
                unidad_medida=row_data.get("unidad_medida", ""),
                linea_base=row_data.get("linea_base", ""),
                meta_cuatrienio=row_data.get("meta_cuatrienio", ""),
                responsable=row_data.get("responsable", ""),
            )
            rows.append(row)

        return rows

    def _extract_ppi_matrix(self, text: str) -> list[PPIRow]:
        """
        Extract Plan Plurianual de Inversiones table rows.

        Args:
            text: Full text

        Returns:
            List of PPIRow objects
        """
        rows: list[PPIRow] = []

        matrix_pattern = r"Plan\s+Plurianual\s+de\s+Inversiones"
        match = re.search(matrix_pattern, text, re.IGNORECASE)

        if not match:
            return rows

        start_pos = match.end()
        section_text = text[start_pos : start_pos + 20000]

        table_rows = self._parse_table_rows(section_text)

        for row_data in table_rows:
            row = PPIRow(
                linea_estrategica=row_data.get("linea_estrategica", ""),
                programa=row_data.get("programa", ""),
                subprograma=row_data.get("subprograma", ""),
                proyecto=row_data.get("proyecto", ""),
                costo_total=row_data.get("costo_total", ""),
                vigencia_2024=row_data.get("vigencia_2024", ""),
                vigencia_2025=row_data.get("vigencia_2025", ""),
                vigencia_2026=row_data.get("vigencia_2026", ""),
                vigencia_2027=row_data.get("vigencia_2027", ""),
                fuente_recursos=row_data.get("fuente_recursos", ""),
            )
            rows.append(row)

        return rows

    def _parse_table_rows(self, section_text: str) -> list[dict[str, str]]:
        """
        Parse table rows from section text using simple pattern matching.

        Args:
            section_text: Text containing table

        Returns:
            List of dictionaries with row data
        """
        rows: list[dict[str, str]] = []

        lines = section_text.split("\n")

        for line in lines[:100]:
            line = line.strip()

            if not line or len(line) < 10:
                continue

            parts = re.split(r"\s{2,}|\t|\|", line)
            parts = [p.strip() for p in parts if p.strip()]

            if len(parts) >= 3:
                row_data = {}

                if len(parts) >= 8:
                    row_data = {
                        "tipo": parts[0] if len(parts) > 0 else "",
                        "linea_estrategica": parts[1] if len(parts) > 1 else "",
                        "programa": parts[2] if len(parts) > 2 else "",
                        "nombre_indicador": parts[3] if len(parts) > 3 else "",
                        "unidad_medida": parts[4] if len(parts) > 4 else "",
                        "linea_base": parts[5] if len(parts) > 5 else "",
                        "meta_cuatrienio": parts[6] if len(parts) > 6 else "",
                        "responsable": parts[7] if len(parts) > 7 else "",
                    }
                elif len(parts) >= 5:
                    row_data = {
                        "linea_estrategica": parts[0] if len(parts) > 0 else "",
                        "programa": parts[1] if len(parts) > 1 else "",
                        "subprograma": parts[2] if len(parts) > 2 else "",
                        "proyecto": parts[3] if len(parts) > 3 else "",
                        "costo_total": parts[4] if len(parts) > 4 else "",
                        "vigencia_2024": parts[5] if len(parts) > 5 else "",
                        "vigencia_2025": parts[6] if len(parts) > 6 else "",
                        "vigencia_2026": parts[7] if len(parts) > 7 else "",
                        "vigencia_2027": parts[8] if len(parts) > 8 else "",
                        "fuente_recursos": parts[9] if len(parts) > 9 else "",
                    }

                if row_data and any(row_data.values()):
                    rows.append(row_data)

        return rows
