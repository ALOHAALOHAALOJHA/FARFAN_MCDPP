"""
Módulo: contract_validator.py
Propósito: Validar contratos generados antes de emisión

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/contract_validator.py

RESPONSABILIDADES:
1. Validación estructural: campos requeridos presentes
2. Validación epistémica: coherencia entre niveles
3. Validación temporal: timestamps y validez declarada
4. Validación referencial: cross-references válidas
5. Validación de sector: sector embebido correctamente

CAPAS DE VALIDACIÓN (en orden):
- Layer 1: Estructural (campos requeridos)
- Layer 2: Epistémica (coherencia N1→N2→N3)
- Layer 3: Temporal (timestamps, validez)
- Layer 4: Referencial (sources, provides)
- Layer 5: Sector (PA01-PA10)

PRINCIPIO:  Fail-loud - cualquier CRITICAL failure bloquea emisión

Versión:  4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . contract_assembler import GeneratedContract

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

VALIDATOR_VERSION = "4.0.0-granular"

# Sectores válidos (PA01-PA10)
VALID_SECTOR_IDS = {f"PA{i:02d}" for i in range(1, 11)}

# Contract types válidos
VALID_CONTRACT_TYPES = {"TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"}

# Levels válidos por fase
VALID_PHASE_LEVELS = {
    "phase_A_construction": "N1",
    "phase_B_computation": "N2",
    "phase_C_litigation": "N3",
}


# ══════════════════════════════════════════════════════════════════════════════
# ENUMS Y DATACLASSES
# ══════════════════════════════════════════════════════════════════════════════


class ValidationSeverity(Enum):
    """
    Severidad de validación. 

    CRITICAL: Bloquea emisión del contrato
    HIGH: Degrada calidad epistemológica
    MEDIUM:  Afecta usabilidad
    LOW: Mejora sugerida (informativo)
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class ValidationResult:
    """
    Resultado de una validación individual.

    Inmutable para garantizar integridad del reporte.
    """
    check_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    section: str
    expected: Any = None
    actual: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "section": self.section,
            "expected": str(self.expected) if self.expected else None,
            "actual": str(self.actual) if self.actual else None,
        }


@dataclass
class ValidationReport:
    """
    Reporte completo de validación de un contrato. 
    """
    contract_id:  str
    question_id: str
    sector_id: str
    contract_number: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    results:  list[ValidationResult] = field(default_factory=list)
    is_valid: bool = True
    validation_timestamp: str = ""
    validator_version: str = VALIDATOR_VERSION

    @property
    def pass_rate(self) -> float:
        """Tasa de checks pasados."""
        return self.passed_checks / self.total_checks if self.total_checks > 0 else 0.0

    @property
    def has_critical_failures(self) -> bool:
        """Indica si hay fallos críticos."""
        return self.critical_failures > 0

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return {
            "contract_id": self.contract_id,
            "question_id":  self.question_id,
            "sector_id": self.sector_id,
            "contract_number": self.contract_number,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "pass_rate": round(self.pass_rate, 4),
            "critical_failures":  self.critical_failures,
            "high_failures": self.high_failures,
            "medium_failures": self.medium_failures,
            "low_failures": self.low_failures,
            "is_valid": self.is_valid,
            "validation_timestamp":  self.validation_timestamp,
            "validator_version": self.validator_version,
            "results": [r.to_dict() for r in self.results],
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL - VALIDADOR
# ══════════════════════════════════════════════════════════════════════════════


class ContractValidator:
    """
    Validador de contratos generados. 

    CAPAS DE VALIDACIÓN:
    1. Estructural: Campos requeridos presentes
    2. Epistémica: Coherencia entre niveles N1→N2→N3
    3. Temporal: Validez declarada
    4. Referencial: Cross-references válidas
    5. Sector: Sector embebido correctamente

    PRINCIPIO: 
    - Un contrato es válido solo si tiene 0 CRITICAL failures
    - Fail-loud: en strict_mode, HIGH failures también bloquean

    USO:
        validator = ContractValidator(strict_mode=True)
        report = validator.validate_contract(contract)
        if report.is_valid:
            emitter.emit(contract)
    """

    # ══════════════════════════════════════════════════════════════════════════
    # CAMPOS REQUERIDOS POR SECCIÓN
    # ══════════════════════════════════════════════════════════════════════════

    REQUIRED_FIELDS:  dict[str, list[str]] = {
        "identity": [
            "contract_id",
            "contract_number",
            "base_contract_id",
            "base_slot",
            "sector_id",
            "sector_name",
            "dimension_id",
            "contract_type",
            "contract_type_name",
            "contract_version",
            "created_at",
            "generator_version",
        ],
        "executor_binding": [
            "executor_class",
            "executor_module",
        ],
        "method_binding":  [
            "orchestration_mode",
            "contract_type",
            "method_count",
            "execution_phases",
            "efficiency_score",
            "mathematical_evidence",
            "doctoral_justification",
        ],
        "question_context": [
            "monolith_ref",
            "pregunta_completa",
            "sector_id",
            "sector_name",
        ],
        "signal_requirements": [
            "derivation_source",
            "derivation_rules",
            "signal_aggregation",
        ],
        "evidence_assembly": [
            "engine",
            "module",
            "type_system",
            "assembly_rules",
        ],
        "fusion_specification": [
            "contract_type",
            "primary_strategy",
            "level_strategies",
        ],
        "cross_layer_fusion": [
            "N1_to_N2",
            "N2_to_N1",
            "N3_to_N1",
            "N3_to_N2",
            "all_to_N4",
        ],
        "human_answer_structure": [
            "sections",
            "confidence_interpretation",
        ],
        "traceability":  [
            "input_files",
            "generation_metadata",
            "contract_lineage",
            "method_count",
        ],
        "output_contract":  [
            "schema_version",
            "required_fields",
        ],
        "audit_annotations":  [
            "generation_metadata",  # Was generation_audit - aligned with assembler output
            "quality_flags",
            "validation_status",
            "sector_specific",
        ],
    }

    # Fases requeridas en method_binding
    REQUIRED_PHASES = [
        "phase_A_construction",
        "phase_B_computation",
        "phase_C_litigation",
    ]

    # Campos requeridos por método expandido
    REQUIRED_METHOD_FIELDS = [
        "class_name",
        "method_name",
        "mother_file",
        "provides",
        "method_id",
        "level",
        "level_name",
        "epistemology",
        "output_type",
        "fusion_behavior",
        "fusion_symbol",
        "classification_rationale",
        "confidence_score",
        "contract_affinities",
        "evidence_requirements",
        "output_claims",
        "constraints_and_limits",
        "failure_modes",
        "description",
    ]

    # Reglas requeridas en evidence_assembly
    REQUIRED_RULES = [
        "R1_empirical_extraction",
        "R2_inferential_processing",
        "R3_audit_gate",
        "R4_narrative_synthesis",
    ]

    # ══════════════════════════════════════════════════════════════════════════
    # INICIALIZACIÓN
    # ══════════════════════════════════════════════════════════════════════════

    def __init__(self, strict_mode: bool = True):
        """
        Inicializa el validador.

        Args:
            strict_mode:  Si True, HIGH failures también bloquean emisión
        """
        self. strict_mode = strict_mode
        self._validation_count = 0

        logger.info(f"ContractValidator initialized, version {VALIDATOR_VERSION}")
        logger.info(f"  Strict mode: {strict_mode}")

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODO PRINCIPAL
    # ══════════════════════════════════════════════════════════════════════════

    def validate_contract(self, contract: "GeneratedContract") -> ValidationReport: 
        """
        Valida un contrato generado.

        SECUENCIA:
        1. Layer 1: Validación estructural
        2. Layer 2: Validación epistémica
        3. Layer 3: Validación temporal
        4. Layer 4: Validación referencial
        5. Layer 5: Validación de sector
        6.  Calcular estadísticas y determinar validez

        Args: 
            contract: GeneratedContract a validar

        Returns:
            ValidationReport con resultados detallados
        """
        from datetime import datetime, timezone

        results:  list[ValidationResult] = []

        # ══════════════════════════════════════════════════════════════════
        # LAYER 1: VALIDACIÓN ESTRUCTURAL
        # ══════════════════════════════════════════════════════════════════
        results.extend(self._validate_structure(contract))

        # ══════════════════════════════════════════════════════════════════
        # LAYER 2: VALIDACIÓN EPISTÉMICA
        # ══════════════════════════════════════════════════════════════════
        results.extend(self._validate_epistemic_coherence(contract))

        # ══════════════════════════════════════════════════════════════════
        # LAYER 3: VALIDACIÓN TEMPORAL
        # ══════════════════════════════════════════════════════════════════
        results.extend(self._validate_temporal(contract))

        # ══════════════════════════════════════════════════════════════════
        # LAYER 4: VALIDACIÓN REFERENCIAL
        # ══════════════════════════════════════════════════════════════════
        results.extend(self._validate_cross_references(contract))

        # ══════════════════════════════════════════════════════════════════
        # LAYER 5: VALIDACIÓN DE SECTOR
        # ══════════════════════════════════════════════════════════════════
        results.extend(self._validate_sector(contract))

        # ══════════════════════════════════════════════════════════════════
        # CALCULAR ESTADÍSTICAS
        # ══════════════════════════════════════════════════════════════════
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        critical = sum(
            1 for r in results
            if not r.passed and r.severity == ValidationSeverity.CRITICAL
        )
        high = sum(
            1 for r in results
            if not r.passed and r.severity == ValidationSeverity.HIGH
        )
        medium = sum(
            1 for r in results
            if not r.passed and r.severity == ValidationSeverity.MEDIUM
        )
        low = sum(
            1 for r in results
            if not r.passed and r.severity == ValidationSeverity.LOW
        )

        # Determinar validez
        if self.strict_mode:
            is_valid = (critical == 0) and (high == 0)
        else:
            is_valid = (critical == 0)

        # Extraer IDs
        contract_id = contract.identity.get("contract_id", "UNKNOWN")
        question_id = contract.identity.get("base_slot", "UNKNOWN")
        sector_id = contract.identity.get("sector_id", "UNKNOWN")
        contract_number = contract.identity.get("contract_number", 0)

        self._validation_count += 1

        return ValidationReport(
            contract_id=contract_id,
            question_id=question_id,
            sector_id=sector_id,
            contract_number=contract_number,
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            critical_failures=critical,
            high_failures=high,
            medium_failures=medium,
            low_failures=low,
            results=results,
            is_valid=is_valid,
            validation_timestamp=datetime.now(timezone.utc).isoformat(),
            validator_version=VALIDATOR_VERSION,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 1: VALIDACIÓN ESTRUCTURAL
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_structure(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """
        Validación estructural:  campos requeridos. 

        Verifica: 
        - Todas las secciones presentes
        - Campos requeridos en cada sección
        - Fases requeridas en method_binding
        - Reglas requeridas en evidence_assembly
        - Campos requeridos en métodos expandidos
        """
        results: list[ValidationResult] = []
        contract_dict = contract.to_dict()

        # ─────────────────────────────────────────────────────────────────
        # Verificar campos requeridos por sección
        # ─────────────────────────────────────────────────────────────────
        for section, fields in self.REQUIRED_FIELDS.items():
            section_data = contract_dict.get(section, {})

            # Verificar que la sección existe
            if section_data is None or not isinstance(section_data, dict):
                results.append(ValidationResult(
                    check_id=f"STRUCT_section_{section}_exists",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Section '{section}' must exist and be a dict",
                    section=section,
                    expected="dict",
                    actual=type(section_data).__name__,
                ))
                continue

            # Verificar cada campo requerido
            for field_name in fields:
                check_id = f"STRUCT_{section}_{field_name}"
                value = section_data.get(field_name)
                passed = value is not None

                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required field '{field_name}' in section '{section}'",
                    section=section,
                    expected=f"Field '{field_name}' present and not None",
                    actual="Present" if passed else "Missing or None",
                ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar fases en method_binding
        # ─────────────────────────────────────────────────────────────────
        phases = contract.method_binding.get("execution_phases", {})

        for phase_name in self.REQUIRED_PHASES: 
            check_id = f"STRUCT_phase_{phase_name}"
            passed = phase_name in phases and isinstance(phases. get(phase_name), dict)

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required phase '{phase_name}' in execution_phases",
                section="method_binding",
                expected=f"Phase '{phase_name}' present as dict",
                actual="Present" if passed else "Missing",
            ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar métodos tienen campos requeridos
        # ─────────────────────────────────────────────────────────────────
        for phase_name, phase_data in phases.items():
            methods = phase_data.get("methods", [])
            for i, method in enumerate(methods):
                for field_name in self.REQUIRED_METHOD_FIELDS:
                    check_id = f"STRUCT_{phase_name}_method_{i}_{field_name}"
                    passed = field_name in method and method[field_name] is not None

                    # Solo severity HIGH para campos de método (no bloquea)
                    results.append(ValidationResult(
                        check_id=check_id,
                        passed=passed,
                        severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.LOW,
                        message=f"Method field '{field_name}' in {phase_name}[{i}]",
                        section="method_binding",
                        expected=f"Field '{field_name}' present",
                        actual="Present" if passed else "Missing",
                    ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar reglas en evidence_assembly
        # ─────────────────────────────────────────────────────────────────
        rules = contract. evidence_assembly.get("assembly_rules", [])
        rule_ids = {r. get("rule_id") for r in rules if isinstance(r, dict)}

        for rule_id in self.REQUIRED_RULES: 
            check_id = f"STRUCT_rule_{rule_id}"
            passed = rule_id in rule_ids

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required rule '{rule_id}' in assembly_rules",
                section="evidence_assembly",
                expected=f"Rule '{rule_id}' present",
                actual="Present" if passed else "Missing",
            ))

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 2: VALIDACIÓN EPISTÉMICA
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_epistemic_coherence(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]: 
        """
        Validación epistémica: coherencia entre niveles.

        Verifica:
        - Cada fase tiene métodos
        - Métodos están en el nivel correcto (N1 en phase_A, etc.)
        - Asimetría N3 declarada
        - TYPE consistente en todas las secciones
        - Veto conditions en métodos N3
        """
        results:  list[ValidationResult] = []
        phases = contract.method_binding.get("execution_phases", {})

        # ─────────────────────────────────────────────────────────────────
        # Verificar métodos por fase
        # ─────────────────────────────────────────────────────────────────
        for phase_name, expected_level in VALID_PHASE_LEVELS.items():
            phase_data = phases.get(phase_name, {})
            methods = phase_data.get("methods", [])

            # Check:  fase tiene métodos
            check_id = f"EPIST_{phase_name}_has_methods"
            passed = len(methods) > 0

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity. CRITICAL,
                message=f"Phase '{phase_name}' must have at least one method",
                section="method_binding",
                expected="At least 1 method",
                actual=f"{len(methods)} methods",
            ))

            # Check: métodos tienen nivel correcto
            for i, method in enumerate(methods):
                method_level = method.get("level", "")
                method_id = method.get("method_id", f"method_{i}")
                check_id = f"EPIST_{phase_name}_{method_id}_level"
                passed = method_level. startswith(expected_level)

                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Method '{method_id}' in '{phase_name}' must be level {expected_level}",
                    section="method_binding",
                    expected=f"Level starting with '{expected_level}'",
                    actual=method_level,
                ))

            # Check:  métodos N3 tienen veto_conditions
            if expected_level == "N3": 
                for i, method in enumerate(methods):
                    method_id = method.get("method_id", f"method_{i}")
                    veto_conditions = method.get("veto_conditions", {})
                    check_id = f"EPIST_{phase_name}_{method_id}_veto"
                    passed = isinstance(veto_conditions, dict) and len(veto_conditions) > 0

                    results.append(ValidationResult(
                        check_id=check_id,
                        passed=passed,
                        severity=ValidationSeverity.HIGH,
                        message=f"N3 method '{method_id}' should have veto_conditions",
                        section="method_binding",
                        expected="Non-empty veto_conditions dict",
                        actual=f"{len(veto_conditions)} conditions",
                    ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar asimetría N3
        # ─────────────────────────────────────────────────────────────────
        cross_layer = contract.cross_layer_fusion

        n3_to_n1 = cross_layer.get("N3_to_N1", {})
        check_id = "EPIST_asymmetry_N3_to_N1"
        passed = n3_to_n1.get("asymmetry") == "N1 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="N3→N1 asymmetry must be declared",
            section="cross_layer_fusion",
            expected="asymmetry: 'N1 CANNOT invalidate N3'",
            actual=n3_to_n1.get("asymmetry", "NOT DECLARED"),
        ))

        n3_to_n2 = cross_layer.get("N3_to_N2", {})
        check_id = "EPIST_asymmetry_N3_to_N2"
        passed = n3_to_n2.get("asymmetry") == "N2 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. HIGH,
            message="N3→N2 asymmetry must be declared",
            section="cross_layer_fusion",
            expected="asymmetry: 'N2 CANNOT invalidate N3'",
            actual=n3_to_n2.get("asymmetry", "NOT DECLARED"),
        ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar TYPE consistente
        # ─────────────────────────────────────────────────────────────────
        identity_type = contract.identity.get("contract_type")
        method_binding_type = contract.method_binding.get("contract_type")
        fusion_type = contract.fusion_specification.get("contract_type")

        check_id = "EPIST_type_consistency"
        passed = (identity_type == method_binding_type == fusion_type)
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. CRITICAL,
            message="Contract TYPE must be consistent across sections",
            section="global",
            expected=f"All sections:  {identity_type}",
            actual=f"identity:{identity_type}, method_binding:{method_binding_type}, fusion:{fusion_type}",
        ))

        # Verificar TYPE es válido
        check_id = "EPIST_type_valid"
        passed = identity_type in VALID_CONTRACT_TYPES
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="Contract TYPE must be valid",
            section="identity",
            expected=f"One of {VALID_CONTRACT_TYPES}",
            actual=identity_type,
        ))

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 3: VALIDACIÓN TEMPORAL
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_temporal(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """
        Validación temporal: timestamps y validez.

        Verifica:
        - created_at presente y formato ISO
        - generator_version presente
        - Timestamps consistentes
        """
        results: list[ValidationResult] = []

        # ─────────────────────────────────────────────────────────────────
        # created_at
        # ─────────────────────────────────────────────────────────────────
        created_at = contract.identity.get("created_at", "")
        check_id = "TEMP_created_at_present"
        passed = bool(created_at) and len(created_at) > 10

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="created_at timestamp must be present",
            section="identity",
            expected="ISO timestamp (e.g., 2026-01-03T... )",
            actual=created_at[: 30] if created_at else "MISSING",
        ))

        # Verificar formato ISO
        if created_at:
            check_id = "TEMP_created_at_format"
            # Patrón básico ISO: YYYY-MM-DDTHH:MM:SS
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
            passed = bool(re.match(iso_pattern, created_at))

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity. MEDIUM,
                message="created_at should be ISO format",
                section="identity",
                expected="YYYY-MM-DDTHH:MM:SS.. .",
                actual=created_at[: 25],
            ))

        # ─────────────────────────────────────────────────────────────────
        # generator_version
        # ─────────────────────────────────────────────────────────────────
        generator_version = contract.identity.get("generator_version", "")
        check_id = "TEMP_generator_version"
        passed = bool(generator_version)

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. MEDIUM,
            message="generator_version must be present",
            section="identity",
            expected="Version string (e.g., 4.0.0-granular)",
            actual=generator_version or "MISSING",
        ))

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 4: VALIDACIÓN REFERENCIAL
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_cross_references(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """
        Validación referencial:  cross-references válidas.

        Verifica:
        - Sources en assembly_rules referencian provides válidos
        - Input hashes presentes en traceability
        - method_count consistente
        """
        results:  list[ValidationResult] = []

        # ─────────────────────────────────────────────────────────────────
        # Recolectar todos los 'provides' de métodos
        # ─────────────────────────────────────────────────────────────────
        phases = contract.method_binding.get("execution_phases", {})
        all_provides:  set[str] = set()

        for phase_data in phases.values():
            for method in phase_data.get("methods", []):
                provides = method.get("provides")
                if provides:
                    all_provides.add(provides)

        # ─────────────────────────────────────────────────────────────────
        # Verificar sources en assembly_rules
        # ─────────────────────────────────────────────────────────────────
        rules = contract.evidence_assembly.get("assembly_rules", [])

        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            sources = rule.get("sources", [])

            # R4 (synthesis) puede tener sources vacío
            if rule_id == "R4_narrative_synthesis":
                continue

            if sources:
                matching = sum(1 for s in sources if s in all_provides)
                check_id = f"XREF_rule_{rule_id}_sources"
                passed = matching > 0

                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity. MEDIUM,
                    message=f"Rule '{rule_id}' sources should reference method provides",
                    section="evidence_assembly",
                    expected="At least one source matching provides",
                    actual=f"{matching}/{len(sources)} sources match",
                ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar input hashes en traceability
        # ─────────────────────────────────────────────────────────────────
        input_files = contract.traceability.get("input_files", {})
        required_inputs = ["classified_methods", "contratos_clasificados", "method_sets"]

        for input_name in required_inputs:
            input_data = input_files.get(input_name, {})
            hash_value = input_data.get("hash", "")

            check_id = f"XREF_input_hash_{input_name}"
            passed = bool(hash_value) and len(hash_value) >= 8

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.MEDIUM,
                message=f"Input hash '{input_name}' should be present",
                section="traceability",
                expected="Hash string >= 8 chars",
                actual=hash_value[: 16] if hash_value else "MISSING",
            ))

        # ─────────────────────────────────────────────────────────────────
        # Verificar method_count consistente
        # ─────────────────────────────────────────────────────────────────
        declared_count = contract.method_binding.get("method_count", 0)
        actual_count = sum(
            len(phase_data.get("methods", []))
            for phase_data in phases.values()
        )

        check_id = "XREF_method_count_consistent"
        passed = declared_count == actual_count

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="method_count must match actual method count",
            section="method_binding",
            expected=f"Declared:  {declared_count}",
            actual=f"Actual: {actual_count}",
        ))

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 5: VALIDACIÓN DE SECTOR
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_sector(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """
        Validación de sector: sector embebido correctamente.

        Verifica:
        - sector_id presente y válido (PA01-PA10)
        - sector_name presente
        - sector_id consistente entre secciones
        - contract_id tiene formato correcto (Qxxx_PAxx)
        """
        results: list[ValidationResult] = []

        # ─────────────────────────────────────────────────────────────────
        # sector_id válido
        # ─────────────────────────────────────────────────────────────────
        sector_id = contract.identity.get("sector_id", "")

        check_id = "SECTOR_id_present"
        passed = bool(sector_id)
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. CRITICAL,
            message="sector_id must be present in identity",
            section="identity",
            expected="Non-empty sector_id",
            actual=sector_id or "MISSING",
        ))

        check_id = "SECTOR_id_valid"
        passed = sector_id in VALID_SECTOR_IDS
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="sector_id must be valid (PA01-PA10)",
            section="identity",
            expected=f"One of {sorted(VALID_SECTOR_IDS)}",
            actual=sector_id,
        ))

        # ─────────────────────────────────────────────────────────────────
        # sector_name presente
        # ─────────────────────────────────────────────────────────────────
        sector_name = contract.identity.get("sector_name", "")

        check_id = "SECTOR_name_present"
        passed = bool(sector_name) and len(sector_name) > 5
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="sector_name must be present and meaningful",
            section="identity",
            expected="Non-empty sector name",
            actual=sector_name[: 50] if sector_name else "MISSING",
        ))

        # ─────────────────────────────────────────────────────────────────
        # sector_id consistente
        # ─────────────────────────────────────────────────────────────────
        question_context_sector = contract.question_context.get("sector_id", "")
        audit_sector = contract.audit_annotations.get("sector_specific", {}).get("sector_id", "")

        check_id = "SECTOR_id_consistent"
        passed = (sector_id == question_context_sector == audit_sector)
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="sector_id must be consistent across sections",
            section="global",
            expected=f"All:  {sector_id}",
            actual=f"identity:{sector_id}, question_context:{question_context_sector}, audit:{audit_sector}",
        ))

        # ─────────────────────────────────────────────────────────────────
        # contract_id formato correcto
        # ─────────────────────────────────────────────────────────────────
        contract_id = contract.identity. get("contract_id", "")

        check_id = "SECTOR_contract_id_format"
        # Formato esperado: Q001_PA01, Q030_PA10, etc.
        pattern = r'^Q\d{3}_PA\d{2}$'
        passed = bool(re.match(pattern, contract_id))

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="contract_id must have format Qxxx_PAxx",
            section="identity",
            expected="Format: Q001_PA01, Q030_PA10, etc.",
            actual=contract_id,
        ))

        # Verificar que sector_id en contract_id coincide
        if passed:
            extracted_sector = contract_id.split("_")[1] if "_" in contract_id else ""
            check_id = "SECTOR_contract_id_matches"
            passed = extracted_sector == sector_id

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message="sector_id in contract_id must match identity. sector_id",
                section="identity",
                expected=f"Extracted: {sector_id}",
                actual=f"In contract_id: {extracted_sector}",
            ))

        return results

    # ══════════════════════════════════════════════════════════════════════════
    # PROPIEDADES PÚBLICAS
    # ══════════════════════════════════════════════════════════════════════════

    @property
    def validation_count(self) -> int:
        """Número de contratos validados por esta instancia."""
        return self._validation_count

    @property
    def version(self) -> str:
        """Versión del validador."""
        return VALIDATOR_VERSION