# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_validator.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import logging

from .irrigation_map import IrrigationMap, IrrigationRoute
from ..vocabulary.signal_vocabulary import SignalVocabulary
from ..vocabulary.capability_vocabulary import CapabilityVocabulary
from ..core.contracts import IrrigationContract, ContractRegistry
from ..core.signal import Signal


class ValidationLevel(Enum):
    """Niveles de validación"""
    STRICT = "strict"      # Falla ante cualquier error
    LENIENT = "lenient"    # Permite warnings
    MINIMAL = "minimal"    # Solo errores críticos


@dataclass
class ValidationIssue:
    """Problema encontrado durante validación"""
    code: str
    message: str
    severity: str  # "ERROR", "WARNING", "INFO"
    context: str = ""
    suggestion: str = ""


@dataclass
class ValidationResult:
    """Resultado de la validación"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    checked_items: int = 0
    
    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "WARNING"]


class IrrigationValidator:
    """
    Validador de contratos y rutas de irrigación.
    
    Responsabilidades:
    1. Verificar integridad de contratos
    2. Detectar conflictos entre rutas
    3. Validar uso de vocabularios
    4. Asegurar cumplimiento de políticas
    """

    def __init__(
        self,
        signal_vocabulary: SignalVocabulary,
        capability_vocabulary: CapabilityVocabulary,
        contract_registry: Optional[ContractRegistry] = None
    ):
        self.signal_vocabulary = signal_vocabulary
        self.capability_vocabulary = capability_vocabulary
        self.contract_registry = contract_registry or ContractRegistry()
        self._logger = logging.getLogger("SISAS.IrrigationValidator")

    def validate_map(self, irrigation_map: IrrigationMap, level: ValidationLevel = ValidationLevel.STRICT) -> ValidationResult:
        """
        Valida un mapa de irrigación completo.
        """
        result = ValidationResult(is_valid=True)
        
        # 1. Validar rutas individuales
        for route_id, route in irrigation_map.routes.items():
            route_result = self.validate_route(route)
            result.issues.extend(route_result.issues)
            result.checked_items += 1
            if not route_result.is_valid and level == ValidationLevel.STRICT:
                result.is_valid = False

        # 2. Detectar conflictos globales
        conflict_issues = self._detect_conflicts(irrigation_map)
        result.issues.extend(conflict_issues)
        if any(i.severity == "ERROR" for i in conflict_issues):
            result.is_valid = False

        return result

    def validate_route(self, route: IrrigationRoute) -> ValidationResult:
        """
        Valida una ruta individual.
        """
        result = ValidationResult(is_valid=True)
        
        # Verificar source
        if not route.source.file_path:
            result.issues.append(ValidationIssue(
                code="MISSING_SOURCE_PATH",
                message="Route source has no file path",
                severity="ERROR",
                context=str(route.source)
            ))
            result.is_valid = False

        # Verificar targets y señales requeridas
        for target in route.targets:
            # Validar que señales requeridas existan en vocabulario
            for signal_type in target.required_signals:
                if not self.signal_vocabulary.is_valid_type(signal_type):
                    result.issues.append(ValidationIssue(
                        code="UNKNOWN_SIGNAL_TYPE",
                        message=f"Target requires unknown signal type: {signal_type}",
                        severity="ERROR",
                        context=f"Target: {target.consumer_id}",
                        suggestion="Register signal type in SignalVocabulary"
                    ))
                    result.is_valid = False

            # Validar capacidades requeridas
            for cap_id in target.required_capabilities:
                if not self.capability_vocabulary.is_valid(cap_id):
                    result.issues.append(ValidationIssue(
                        code="UNKNOWN_CAPABILITY",
                        message=f"Target requires unknown capability: {cap_id}",
                        severity="ERROR",
                        context=f"Target: {target.consumer_id}",
                        suggestion="Register capability in CapabilityVocabulary"
                    ))
                    result.is_valid = False

        return result

    def validate_contract(self, contract: IrrigationContract) -> ValidationResult:
        """
        Valida un contrato de irrigación.
        """
        result = ValidationResult(is_valid=True)
        
        # Validar campos básicos
        if not contract.contract_id:
            result.issues.append(ValidationIssue(
                code="INVALID_CONTRACT_ID",
                message="Contract ID is missing",
                severity="ERROR"
            ))
            result.is_valid = False

        # Validar señales especificadas en el contrato
        if hasattr(contract, 'signals'):
            for signal_type in contract.signals:
                if not self.signal_vocabulary.is_valid_type(signal_type):
                    result.issues.append(ValidationIssue(
                        code="UNKNOWN_CONTRACT_SIGNAL",
                        message=f"Contract specifies unknown signal type: {signal_type}",
                        severity="ERROR",
                        context=contract.contract_id
                    ))
                    result.is_valid = False

        return result

    def _detect_conflicts(self, irrigation_map: IrrigationMap) -> List[ValidationIssue]:
        """
        Detecta conflictos entre rutas.
        Ej: Dos rutas escribiendo al mismo consumidor sin coordinación.
        """
        issues = []
        consumer_sources: Dict[str, List[str]] = {}

        for route_id, route in irrigation_map.routes.items():
            for target in route.targets:
                if target.consumer_id not in consumer_sources:
                    consumer_sources[target.consumer_id] = []
                consumer_sources[target.consumer_id].append(route_id)

        # Analizar duplicados
        for consumer, routes in consumer_sources.items():
            if len(routes) > 1:
                # Esto podría ser válido (merge) o un conflicto. 
                # Por ahora lanzamos warning para revisión.
                issues.append(ValidationIssue(
                    code="MULTIPLE_SOURCES_FOR_CONSUMER",
                    message=f"Consumer {consumer} receives data from multiple routes: {len(routes)}",
                    severity="WARNING",
                    context=f"Routes: {', '.join(routes[:3])}...",
                    suggestion="Verify aggregation logic for this consumer"
                ))

        return issues

    def check_vocabulary_alignment(self, signals: List[Signal]) -> ValidationResult:
        """
        Verifica si una lista de señales cumple con el vocabulario.
        """
        result = ValidationResult(is_valid=True)
        
        for signal in signals:
            is_valid, errors = self.signal_vocabulary.validate_signal(signal)
            if not is_valid:
                result.is_valid = False
                for err in errors:
                    result.issues.append(ValidationIssue(
                        code="SIGNAL_VALIDATION_ERROR",
                        message=err,
                        severity="ERROR",
                        context=f"Signal: {signal.signal_id if hasattr(signal, 'signal_id') else 'unknown'}"
                    ))
        
        return result
