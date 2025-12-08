"""
PDT Structure Dataclass

Defines the structure for Plan de Desarrollo Territorial (PDT) document extraction.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BlockInfo:
    """Information about a structural block (CAPÍTULO, Línea estratégica, etc.)."""

    text: str
    tokens: int
    numbers_count: int


@dataclass
class HeaderInfo:
    """Information about a document header."""

    level: int
    text: str
    valid_numbering: bool


@dataclass
class SectionInfo:
    """Information about a major section (Diagnóstico, Estratégica, etc.)."""

    present: bool
    token_count: int
    keyword_matches: int
    number_count: int
    sources_found: int


@dataclass
class IndicatorRow:
    """Row from Matriz de Indicadores table."""

    tipo: str = ""
    linea_estrategica: str = ""
    programa: str = ""
    nombre_indicador: str = ""
    unidad_medida: str = ""
    linea_base: str = ""
    meta_cuatrienio: str = ""
    responsable: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "Tipo": self.tipo,
            "Línea Estratégica": self.linea_estrategica,
            "Programa": self.programa,
            "Nombre Indicador": self.nombre_indicador,
            "Unidad de Medida": self.unidad_medida,
            "Línea Base": self.linea_base,
            "Meta Cuatrienio": self.meta_cuatrienio,
            "Responsable": self.responsable,
        }


@dataclass
class PPIRow:
    """Row from Plan Plurianual de Inversiones table."""

    linea_estrategica: str = ""
    programa: str = ""
    subprograma: str = ""
    proyecto: str = ""
    costo_total: str = ""
    vigencia_2024: str = ""
    vigencia_2025: str = ""
    vigencia_2026: str = ""
    vigencia_2027: str = ""
    fuente_recursos: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "Línea Estratégica": self.linea_estrategica,
            "Programa": self.programa,
            "Subprograma": self.subprograma,
            "Proyecto": self.proyecto,
            "Costo Total": self.costo_total,
            "Vigencia 2024": self.vigencia_2024,
            "Vigencia 2025": self.vigencia_2025,
            "Vigencia 2026": self.vigencia_2026,
            "Vigencia 2027": self.vigencia_2027,
            "Fuente de Recursos": self.fuente_recursos,
        }


@dataclass
class PDTStructure:
    """
    Complete structure extracted from a PDT document.

    Includes tokenization, block detection, hierarchy validation,
    sequence verification, section analysis, and table extraction.
    """

    total_tokens: int
    full_text: str
    blocks_found: dict[str, BlockInfo] = field(default_factory=dict)
    headers: list[HeaderInfo] = field(default_factory=list)
    block_sequence: list[str] = field(default_factory=list)
    sections_found: dict[str, SectionInfo] = field(default_factory=dict)
    indicator_rows: list[IndicatorRow] = field(default_factory=list)
    ppi_rows: list[PPIRow] = field(default_factory=list)
    hierarchy_score: float = 0.0
    sequence_score: float = 0.0
