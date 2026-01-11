"""
Generador Granular de Contratos Ejecutores F.A.R.F.A.N v4.0.0

Este módulo implementa la generación granular de contratos ejecutores siguiendo
estrictamente la especificación técnica del guide.md.

INVARIANTES DE DISEÑO:
- I-1: Autoridad Epistémica Inmutable
- I-2: Composición Bottom-Up
- I-3: Sin Templates por TYPE
- I-4: Determinismo Total
- I-5: Fail-Loud

Arquitectura en capas:
- Layer 0: InputRegistry (carga y validación de insumos)
- Layer 1: MethodExpander (expansión de métodos)
- Layer 2: ChainComposer (composición de cadenas)
- Layer 3: ContractAssembler (ensamblaje de contratos)
- Layer 4: ContractValidator + JSONEmitter (validación y emisión)
"""

from .chain_composer import (
    ChainComposer,
    EpistemicChain,
)
from .contract_assembler import (
    ContractAssembler,
    GeneratedContract,
)
from .contract_generator import (
    ContractGenerator,
    main,
)
from .contract_validator import (
    ContractValidator,
    ValidationReport,
    ValidationResult,
    ValidationSeverity,
)
from .input_registry import (
    ContractClassification,
    InputLoader,
    InputRegistry,
    MethodAssignment,
    MethodDefinition,
    QuestionMethodSet,
)
from .json_emitter import (
    JSONEmitter,
)
from .method_expander import (
    ExpandedMethodUnit,
    MethodExpander,
)

__all__ = [
    # Layer 0
    "InputLoader",
    "InputRegistry",
    "MethodDefinition",
    "ContractClassification",
    "MethodAssignment",
    "QuestionMethodSet",
    # Layer 1
    "MethodExpander",
    "ExpandedMethodUnit",
    # Layer 2
    "ChainComposer",
    "EpistemicChain",
    # Layer 3
    "ContractAssembler",
    "GeneratedContract",
    # Layer 4
    "ContractValidator",
    "ValidationReport",
    "ValidationResult",
    "ValidationSeverity",
    "JSONEmitter",
    # Orchestrator
    "ContractGenerator",
    "main",
]

__version__ = "4.0.0-granular"
