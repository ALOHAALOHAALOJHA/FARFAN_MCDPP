"""Phase 2 frozen constants - no runtime monolith reads.

Constitutional invariants for Phase 2 micro-answer execution:
- 60 chunks (from Phase 1: 10 PA × 6 DIM)
- 30 base questions (Q001-Q030)
- 10 policy areas (PA01-PA10)
- 300 micro-answers total (30 questions × 10 PA)
- Cardinality: 60→300 transformation
"""

from __future__ import annotations

from enum import Enum
from typing import Final

NUM_CHUNKS: Final[int] = 60
NUM_BASE_QUESTIONS: Final[int] = 30
NUM_POLICY_AREAS: Final[int] = 10
NUM_DIMENSIONS: Final[int] = 6
NUM_MICRO_ANSWERS: Final[int] = 300

CHUNKS_PER_PA: Final[int] = 6
QUESTIONS_PER_PA: Final[int] = 30
EXPECTED_OUTPUTS_PER_QUESTION: Final[int] = 10

PHASE_2_CARDINALITY_INVARIANT: Final[str] = "60 chunks → 300 micro-answers"


class Dimension(Enum):
    """Six causal dimensions from logical framework."""
    D1_INSUMOS = "DIM01"
    D2_ACTIVIDADES = "DIM02"
    D3_PRODUCTOS = "DIM03"
    D4_RESULTADOS = "DIM04"
    D5_IMPACTOS = "DIM05"
    D6_SOSTENIBILIDAD = "DIM06"


class PolicyArea(Enum):
    """Ten policy areas covering territorial development."""
    PA01_ECONOMIC = "PA01"
    PA02_SOCIAL = "PA02"
    PA03_ENVIRONMENTAL = "PA03"
    PA04_INSTITUTIONAL = "PA04"
    PA05_INFRASTRUCTURE = "PA05"
    PA06_EDUCATION = "PA06"
    PA07_HEALTH = "PA07"
    PA08_SECURITY = "PA08"
    PA09_CULTURE = "PA09"
    PA10_TERRITORIAL = "PA10"


POLICY_AREA_IDS: Final[list[str]] = [pa.value for pa in PolicyArea]
DIMENSION_IDS: Final[list[str]] = [dim.value for dim in Dimension]

BASE_QUESTION_IDS: Final[list[str]] = [f"Q{i:03d}" for i in range(1, NUM_BASE_QUESTIONS + 1)]

EXPECTED_TASK_COUNT: Final[int] = NUM_CHUNKS * 5
RETRY_BACKOFF_BASE: Final[float] = 0.5
MAX_RETRIES: Final[int] = 3

DEFAULT_HIGH_EXECUTION_TIME_MS: Final[int] = 1000
DEFAULT_HIGH_MEMORY_MB: Final[int] = 100
DEFAULT_HIGH_SERIALIZATION_MS: Final[int] = 100

MAX_QUESTION_GLOBAL: Final[int] = 999

assert NUM_MICRO_ANSWERS == NUM_BASE_QUESTIONS * NUM_POLICY_AREAS, \
    f"Cardinality check failed: {NUM_MICRO_ANSWERS} != {NUM_BASE_QUESTIONS} × {NUM_POLICY_AREAS}"

assert NUM_CHUNKS == NUM_POLICY_AREAS * NUM_DIMENSIONS, \
    f"Chunk count check failed: {NUM_CHUNKS} != {NUM_POLICY_AREAS} × {NUM_DIMENSIONS}"

__all__ = [
    "NUM_CHUNKS",
    "NUM_BASE_QUESTIONS",
    "NUM_POLICY_AREAS",
    "NUM_DIMENSIONS",
    "NUM_MICRO_ANSWERS",
    "CHUNKS_PER_PA",
    "QUESTIONS_PER_PA",
    "EXPECTED_OUTPUTS_PER_QUESTION",
    "PHASE_2_CARDINALITY_INVARIANT",
    "Dimension",
    "PolicyArea",
    "POLICY_AREA_IDS",
    "DIMENSION_IDS",
    "BASE_QUESTION_IDS",
    "EXPECTED_TASK_COUNT",
    "RETRY_BACKOFF_BASE",
    "MAX_RETRIES",
    "DEFAULT_HIGH_EXECUTION_TIME_MS",
    "DEFAULT_HIGH_MEMORY_MB",
    "DEFAULT_HIGH_SERIALIZATION_MS",
    "MAX_QUESTION_GLOBAL",
]
