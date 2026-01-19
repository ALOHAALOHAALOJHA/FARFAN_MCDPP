# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/harmonization/harmonization_validator.py

"""
PILAR 4: ARMONIZACIÓN - Coherencia global del sistema

Este módulo implementa el cuarto pilar de SISAS: la armonización.

AXIOMA: Todas las partes del sistema deben estar sincronizadas y ser coherentes.
          NINGÚN componente debe estar desactualizado o inconsistente.
"""

from __future__ import annotations
import ast
import fnmatch
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Importaciones SISAS
from ..validators.depuration import DepurationValidator
from ..wiring.wiring_config import WiringConfiguration
from ..vocabulary.signal_vocabulary import SignalVocabulary
from ..vocabulary.capability_vocabulary import CapabilityVocabulary
from ..vehicles import BaseVehicle
from ..consumers import BaseConsumer
from ..core.contracts import ContractRegistry


# =============================================================================
# RESULT TYPES
# =============================================================================

class DimensionStatus(Enum):
    """Estado de validación de una dimensión"""
    HARMONIZED = "HARMONIZED"
    PARTIAL = "PARTIAL"
    MISALIGNED = "MISALIGNED"
    UNKNOWN = "UNKNOWN"


@dataclass
class HarmonizationIssue:
    """Issue de armonización encontrado"""
    dimension: str  # "VOCAB_CODE", "CODE_METADATA", etc.
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    type: str  # "MISSING_SIGNAL", "ORPHAN_CONTRACT", etc.
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "severity": self.severity,
            "type": self.type,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion
        }


@dataclass
class DimensionValidation:
    """
    Resultado de validación de una dimensión.

    Cada dimensión tiene su propia validación.
    """
    dimension_name: str
    status: DimensionStatus
    issues: List[HarmonizationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def critical_issues(self) -> List[HarmonizationIssue]:
        return [i for i in self.issues if i.severity == "CRITICAL"]

    @property
    def high_issues(self) -> List[HarmonizationIssue]:
        return [i for i in self.issues if i.severity == "HIGH"]

    @property
    def blocking_issues(self) -> List[HarmonizationIssue]:
        """Issues que bloquean la armonización"""
        return [i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]]

    @property
    def issue_count(self) -> Dict[str, int]:
        """Conteo de issues por severidad"""
        counts = {}
        for issue in self.issues:
            sev = issue.severity
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension_name": self.dimension_name,
            "status": self.status.value,
            "total_issues": len(self.issues),
            "blocking_issues": len(self.blocking_issues),
            "issue_count": self.issue_count,
            "metadata": self.metadata
        }


@dataclass
class HarmonizationReport:
    """
    Reporte completo de armonización del sistema.

    Contiene la validación de las 6 dimensiones y el estado final.
    """
    harmonized: bool = False
    dimensions: Dict[str, DimensionValidation] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        return sum(len(d.issues) for d in self.dimensions.values())

    @property
    def blocking_issues(self) -> List[HarmonizationIssue]:
        """Todos los issues bloqueantes de todas las dimensiones"""
        blocking = []
        for dim in self.dimensions.values():
            blocking.extend(dim.blocking_issues)
        return blocking

    @property
    def dimensions_harmonized(self) -> int:
        return sum(1 for d in self.dimensions.values() if d.status == DimensionStatus.HARMONIZED)

    @property
    def dimensions_partial(self) -> int:
        return sum(1 for d in self.dimensions.values() if d.status == DimensionStatus.PARTIAL)

    @property
    def dimensions_misaligned(self) -> int:
        return sum(1 for d in self.dimensions.values() if d.status == DimensionStatus.MISALIZED)

    def add_dimension(self, validation: DimensionValidation):
        """Añade una validación de dimensión"""
        self.dimensions[validation.dimension_name] = validation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "harmonized": self.harmonized,
            "total_dimensions": len(self.dimensions),
            "dimensions_harmonized": self.dimensions_harmonized,
            "dimensions_partial": self.dimensions_partial,
            "dimensions_misaligned": self.dimensions_misaligned,
            "total_issues": self.total_issues,
            "blocking_issues": len(self.blocking_issues),
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


# =============================================================================
# MAIN HARMONIZATION VALIDATOR
# =============================================================================

class HarmonizationValidator:
    """
    Validador de armonización del sistema SISAS.

    Responsabilidad: Validar que TODAS las partes del sistema están sincronizadas.

    Este es el PILAR 4 de SISAS: ARMONIZACIÓN.

    Dimensiones validadas:
        1. VOCABULARIO ↔ CÓDIGO
        2. CÓDIGO ↔ METADATOS
        3. METADATOS ↔ DATOS
        4. WIRING ↔ CÓDIGO
        5. SCHEMAS ↔ DATOS
        6. DEPENDENCIES ↔ ORQUESTACIÓN

    Uso:
        validator = HarmonizationValidator(
            base_path="canonic_questionnaire_central",
            code_path="src/farfan_pipeline"
        )

        report = validator.validate_full_harmonization()

        if not report.harmonized:
            for issue in report.blocking_issues:
                print(f"BLOCKING [{issue.dimension}]: {issue.message}")
    """

    def __init__(
        self,
        base_path: str = "canonic_questionnaire_central",
        code_path: str = "src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS",
        wiring_config: Optional[WiringConfiguration] = None
    ):
        """
        Inicializa el validador de armonización.

        Args:
            base_path: Path al questionnaire canónico
            code_path: Path al código SISAS
            wiring_config: Configuración de wiring (opcional)
        """
        self.base_path = base_path
        self.code_path = code_path
        self.wiring_config = wiring_config or WiringConfiguration.from_defaults()

        # Cargar vocabularios
        self.signal_vocabulary = SignalVocabulary()
        self.capability_vocabulary = CapabilityVocabulary()

    # =========================================================================
    # MAIN API
    # =========================================================================

    def validate_full_harmonization(self) -> HarmonizationReport:
        """
        Valida la armonización completa del sistema en 6 dimensiones.

        Returns:
            HarmonizationReport con el resultado de todas las validaciones
        """
        report = HarmonizationReport()

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 1: VOCABULARIO ↔ CÓDIGO
        # ═══════════════════════════════════════════════════════
        dim1 = self._validate_vocab_code()
        report.add_dimension(dim1)

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 2: CÓDIGO ↔ METADATOS
        # ═══════════════════════════════════════════════════════
        dim2 = self._validate_code_metadata()
        report.add_dimension(dim2)

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 3: METADATOS ↔ DATOS
        # ═══════════════════════════════════════════════════════
        dim3 = self._validate_metadata_data()
        report.add_dimension(dim3)

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 4: WIRING ↔ CÓDIGO
        # ═══════════════════════════════════════════════════════
        dim4 = self._validate_wiring_code()
        report.add_dimension(dim4)

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 5: SCHEMAS ↔ DATOS
        # ═══════════════════════════════════════════════════════
        dim5 = self._validate_schemas_data()
        report.add_dimension(dim5)

        # ═══════════════════════════════════════════════════════
        # DIMENSIÓN 6: DEPENDENCIES ↔ ORQUESTACIÓN
        # ═══════════════════════════════════════════════════════
        dim6 = self._validate_dependencies_orchestration()
        report.add_dimension(dim6)

        # ═══════════════════════════════════════════════════════
        # RESULTADO FINAL
        # ═══════════════════════════════════════════════════════
        report.harmonized = (
            len(report.blocking_issues) == 0 and
            report.dimensions_harmonized >= 4  # Al menos 4 de 6 dimensiones armonizadas
        )

        return report

    # =========================================================================
    # DIMENSIÓN 1: VOCABULARIO ↔ CÓDIGO
    # =========================================================================

    def _validate_vocab_code(self) -> DimensionValidation:
        """
        Valida que las señales usadas en código están en vocabulario.

        Checks:
        - Señales en vehículos están en SignalVocabulary
        - Señales en consumers están en SignalVocabulary
        - No hay señales en vocabulario que nunca se usan
        """
        dim = DimensionValidation(dimension_name="VOCABULARIO_CODE")

        # Obtener señales en vocabulario
        vocab_signals = set(self.signal_vocabulary.definitions.keys())

        # Obtener señales usadas en código
        code_signals = self._extract_signals_from_code()

        # Señales en código pero no en vocabulario
        missing_in_vocab = code_signals - vocab_signals
        for signal_type in missing_in_vocab:
            if signal_type not in ["*", "all"]:
                dim.issues.append(HarmonizationIssue(
                    dimension="VOCABULARIO_CODE",
                    severity="HIGH",
                    type="SIGNAL_NOT_IN_VOCAB",
                    message=f"Signal '{signal_type}' used in code but not in SignalVocabulary",
                    details={"signal_type": signal_type},
                    suggestion=f"Add '{signal_type}' to SignalVocabulary"
                ))

        # Señales en vocabulario pero no usadas
        unused_in_vocab = vocab_signals - code_signals
        if unused_in_vocab:
            dim.metadata["unused_signals"] = list(unused_in_vocab)
            for signal_type in unused_in_vocab:
                if signal_type not in ["*", "all"]:
                    dim.issues.append(HarmonizationIssue(
                        dimension="VOCABULARIO_CODE",
                        severity="LOW",
                        type="SIGNAL_UNUSED",
                        message=f"Signal '{signal_type}' in vocabulary but never used",
                        details={"signal_type": signal_type}
                    ))

        # Determinar estado
        if len(missing_in_vocab) == 0:
            dim.status = DimensionStatus.HARMONIZED
        elif len(missing_in_vocab) < 3:
            dim.status = DimensionStatus.PARTIAL
        else:
            dim.status = DimensionStatus.MISALIGNED

        dim.metadata["vocab_signal_count"] = len(vocab_signals)
        dim.metadata["code_signal_count"] = len(code_signals)
        dim.metadata["missing_in_vocab"] = len(missing_in_vocab)

        return dim

    def _extract_signals_from_code(self) -> Set[str]:
        """Extrae tipos de señal usados en el código"""
        signals = set()

        # Añadir señales de vehículos
        from ..vehicles import signal_registry, signal_context_scoper, signal_quality_metrics
        vehicles = [
            signal_registry.SignalRegistryVehicle,
            signal_context_scoper.SignalContextScoperVehicle,
            signal_quality_metrics.SignalQualityMetricsVehicle
        ]

        for vehicle_cls in vehicles:
            # Obtener signal_types_produced
            if hasattr(vehicle_cls, '__dataclass_fields__'):
                capabilities_field = getattr(vehicle_cls, 'capabilities', None)
                if capabilities_field:
                    signal_types = capabilities_field.signal_types_produced
                    signals.update(signal_types)

        # Añadir señales de vocabulario
        signals.update(self.signal_vocabulary.definitions.keys())

        return signals

    # =========================================================================
    # DIMENSIÓN 2: CÓDIGO ↔ METADATOS
    # =========================================================================

    def _validate_code_metadata(self) -> DimensionValidation:
        """
        Valida que los metadatos (SISAS_IRRIGATION_SPEC) reflejan el código.

        Checks:
        - Contratos en spec existen en código
        - Vehículos en spec existen en código
        - Archivos en spec existen
        """
        dim = DimensionValidation(dimension_name="CODE_METADATA")

        # Cargar spec
        spec_path = os.path.join(self.base_path, "_registry/SISAS_IRRIGATION_SPEC.json")
        if not os.path.exists(spec_path):
            dim.issues.append(HarmonizationIssue(
                dimension="CODE_METADATA",
                severity="HIGH",
                type="SPEC_NOT_FOUND",
                message=f"SISAS_IRRIGATION_SPEC.json not found",
                details={"expected_path": spec_path}
            ))
            dim.status = DimensionStatus.MISALIGNED
            return dim

        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)
        except Exception as e:
            dim.issues.append(HarmonizationIssue(
                dimension="CODE_METADATA",
                severity="HIGH",
                type="SPEC_READ_ERROR",
                message=f"Error reading SISAS_IRRIGATION_SPEC: {str(e)}",
                details={"error": str(e)}
            ))
            dim.status = DimensionStatus.MISALIGNED
            return dim

        # Validar que los vehículos en spec existen
        spec_vehicles = set()
        for unit_id, unit_data in spec.get("units", {}).items():
            for vehicle in unit_data.get("vehicles", []):
                spec_vehicles.add(vehicle)

        # Vehículos en código (desde wiring)
        code_vehicles = set(self.wiring_config.vehicle_contracts.keys())

        # Vehículos en spec pero no en código
        orphan_vehicles = spec_vehicles - code_vehicles
        for vehicle in orphan_vehicles:
            dim.issues.append(HarmonizationIssue(
                dimension="CODE_METADATA",
                severity="MEDIUM",
                type="VEHICLE_IN_SPEC_NOT_CODE",
                message=f"Vehicle '{vehicle}' in spec but not in code",
                details={"vehicle": vehicle}
            ))

        # Vehículos en código pero no en spec
        undocumented_vehicles = code_vehicles - spec_vehicles
        if undocumented_vehicles:
            dim.metadata["undocumented_vehicles"] = list(undocumented_vehicles)
            for vehicle in undocumented_vehicles:
                dim.issues.append(HarmonizationIssue(
                    dimension="CODE_METADATA",
                    severity="LOW",
                    type="VEHICLE_NOT_IN_SPEC",
                    message=f"Vehicle '{vehicle}' in code but not in spec",
                    details={"vehicle": vehicle}
                ))

        # Determinar estado
        if not orphan_vehicles and not undocumented_vehicles:
            dim.status = DimensionStatus.HARMONIZED
        elif not orphan_vehicles:
            dim.status = DimensionStatus.PARTIAL
        else:
            dim.status = DimensionStatus.MISALIGNED

        return dim

    # =========================================================================
    # DIMENSIÓN 3: METADATOS ↔ DATOS
    # =========================================================================

    def _validate_metadata_data(self) -> DimensionValidation:
        """
        Valida que los archivos en spec existen en disco.

        Checks:
        - Archivos listados en SISAS_IRRIGATION_SPEC existen
        - Conteos de archivos son correctos
        """
        dim = DimensionValidation(dimension_name="METADATA_DATA")

        # Cargar spec
        spec_path = os.path.join(self.base_path, "_registry/SISAS_IRRIGATION_SPEC.json")
        if not os.path.exists(spec_path):
            dim.status = DimensionStatus.UNKNOWN
            return dim

        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)
        except Exception:
            dim.status = DimensionStatus.UNKNOWN
            return dim

        # Verificar archivos listados en spec
        total_spec_files = 0
        missing_files = []

        for unit_id, unit_data in spec.get("units", {}).items():
            source_files = unit_data.get("source_files", [])
            total_spec_files += len(source_files)

            for file_path in source_files:
                full_path = os.path.join(self.base_path, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)

        for file_path in missing_files:
            dim.issues.append(HarmonizationIssue(
                dimension="METADATA_DATA",
                severity="HIGH",
                type="FILE_IN_SPEC_NOT_FOUND",
                message=f"File in spec not found: {file_path}",
                details={"file_path": file_path}
            ))

        # Comparar con archivos actuales
        actual_file_count = self._count_actual_files()

        dim.metadata["spec_file_count"] = total_spec_files
        dim.metadata["actual_file_count"] = actual_file_count
        dim.metadata["missing_files"] = len(missing_files)

        if missing_files:
            dim.status = DimensionStatus.MISALIGNED
        elif total_spec_files != actual_file_count:
            dim.status = DimensionStatus.PARTIAL
        else:
            dim.status = DimensionStatus.HARMONIZED

        return dim

    def _count_actual_files(self) -> int:
        """Cuenta archivos JSON actuales"""
        count = 0
        for root, dirs, files in os.walk(self.base_path):
            count += len([f for f in files if f.endswith(".json")])
        return count

    # =========================================================================
    # DIMENSIÓN 4: WIRING ↔ CÓDIGO
    # =========================================================================

    def _validate_wiring_code(self) -> DimensionValidation:
        """
        Valida que wiring configuration es consistente con el código.

        Checks:
        - Vehículos en wiring existen
        - Consumers en wiring existen
        - Buses en wiring existen
        """
        dim = DimensionValidation(dimension_name="WIRING_CODE")

        # Usar wiring_config para validar
        wiring_report = self.wiring_config.validate_wiring()

        for issue in wiring_report.issues:
            dim.issues.append(HarmonizationIssue(
                dimension="WIRING_CODE",
                severity=issue.severity.upper(),
                type=issue.type,
                message=issue.message,
                details=issue.details
            ))

        if wiring_report.is_valid:
            dim.status = DimensionStatus.HARMONIZED
        elif len(wiring_report.blocking_issues) == 0:
            dim.status = DimensionStatus.PARTIAL
        else:
            dim.status = DimensionStatus.MISALIGNED

        return dim

    # =========================================================================
    # DIMENSIÓN 5: SCHEMAS ↔ DATOS
    # =========================================================================

    def _validate_schemas_data(self) -> DimensionValidation:
        """
        Valida que los datos cumplen sus schemas.

        Checks:
        - Archivos metadata.json cumplen schema
        - Archivos questions.json cumplen schema
        """
        dim = DimensionValidation(dimension_name="SCHEMAS_DATA")

        # Usar DepurationValidator para check de schema
        depuration_validator = DepurationValidator(base_path=self.base_path)

        # Validar muestra de archivos
        test_files = [
            "_registry/SISAS_IRRIGATION_SPEC.json",
            "dimensions/DIM01_INSUMOS/metadata.json",
            "policy_areas/PA01_MUJERES_GENERO/metadata.json"
        ]

        schema_violations = 0
        for file_path in test_files:
            result = depuration_validator.depurate(file_path)

            # Contar violaciones de schema
            for error in result.errors:
                if error.type == "SCHEMA_VIOLATION":
                    schema_violations += 1
                    dim.issues.append(HarmonizationIssue(
                        dimension="SCHEMAS_DATA",
                        severity="MEDIUM",
                        type="SCHEMA_VIOLATION",
                        message=f"Schema violation in {file_path}: {error.message}",
                        details={"file": file_path, "error": error.message}
                    ))

        dim.metadata["schema_violations"] = schema_violations

        if schema_violations == 0:
            dim.status = DimensionStatus.HARMONIZED
        elif schema_violations < 3:
            dim.status = DimensionStatus.PARTIAL
        else:
            dim.status = DimensionStatus.MISALIGNED

        return dim

    # =========================================================================
    # DIMENSIÓN 6: DEPENDENCIES ↔ ORQUESTACIÓN
    # =========================================================================

    def _validate_dependencies_orchestration(self) -> DimensionValidation:
        """
        Valida que el orden de fases respeta dependencias.

        Checks:
        - El orden de ejecución respeta dependencias
        - No hay fases que dependen de fases posteriores
        """
        dim = DimensionValidation(dimension_name="DEPENDENCIES_ORCHESTRATION")

        # Configuración de dependencias correcta
        correct_deps = {
            "phase_00": [],
            "phase_01": ["phase_00"],
            "phase_02": ["phase_01"],
            "phase_03": ["phase_01", "phase_02"],
            "phase_07": ["phase_02"],
            "phase_08": ["phase_03"],
        }

        # Detectar violaciones
        violations = []

        # Verificar que no hay dependencias circulares
        for phase_id, deps in correct_deps.items():
            for dep in deps:
                # Verificar que dep no depende de phase_id
                if dep in correct_deps and phase_id in correct_deps[dep]:
                    violations.append({
                        "phase": phase_id,
                        "dependency": dep,
                        "issue": f"Circular dependency: {phase_id} ↔ {dep}"
                    })
                    dim.issues.append(HarmonizationIssue(
                        dimension="DEPENDENCIES_ORCHESTRATION",
                        severity="CRITICAL",
                        type="CIRCULAR_DEPENDENCY",
                        message=f"Circular dependency: {phase_id} ↔ {dep}",
                        details={"phase": phase_id, "dependency": dep},
                        suggestion="Remove circular dependency"
                    ))

        # Verificar orden topológico
        phases = list(correct_deps.keys())
        for i, phase in enumerate(phases):
            for dep in correct_deps[phase]:
                dep_index = phases.index(dep) if dep in phases else -1
                if dep_index > i:
                    violations.append({
                        "phase": phase,
                        "dependency": dep,
                        "issue": f"{phase} depends on {dep} but comes before"
                    })
                    dim.issues.append(HarmonizationIssue(
                        dimension="DEPENDENCIES_ORCHESTRATION",
                        severity="CRITICAL",
                        type="DEPENDENCY_VIOLATION",
                        message=f"{phase} depends on {dep} but comes before in order",
                        details={"phase": phase, "dependency": dep},
                        suggestion=f"Move {phase} after {dep}"
                    ))

        dim.metadata["violations"] = len(violations)

        if len(violations) == 0:
            dim.status = DimensionStatus.HARMONIZED
        else:
            dim.status = DimensionStatus.MISALIGNED

        return dim


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def validate_harmonization(
    base_path: str = "canonic_questionnaire_central",
    code_path: str = "src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS",
    output_path: Optional[str] = None
) -> HarmonizationReport:
    """
    Función de conveniencia para validar armonización completa.

    Args:
        base_path: Path al questionnaire canónico
        code_path: Path al código SISAS
        output_path: Path donde guardar el reporte (opcional)

    Returns:
        HarmonizationReport con el resultado
    """
    validator = HarmonizationValidator(
        base_path=base_path,
        code_path=code_path
    )

    report = validator.validate_full_harmonization()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False, default=str)

    return report
