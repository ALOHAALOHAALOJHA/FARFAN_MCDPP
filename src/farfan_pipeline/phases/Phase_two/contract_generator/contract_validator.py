"""
Módulo: contract_validator.py
Propósito: Validar contratos generados antes de emisión
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ValidationSeverity(Enum):
    """Severidad de validación"""
    CRITICAL = "CRITICAL"  # Bloquea emisión
    HIGH = "HIGH"  # Degrada calidad
    MEDIUM = "MEDIUM"  # Afecta usabilidad
    LOW = "LOW"  # Mejora sugerida


@dataclass
class ValidationResult:
    """Resultado de una validación individual"""
    check_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    section: str
    expected: Any = None
    actual: Any = None


@dataclass
class ValidationReport:
    """Reporte completo de validación"""
    contract_id: str
    question_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_failures: int
    results: list[ValidationResult]
    is_valid: bool

    @property
    def pass_rate(self) -> float:
        return self.passed_checks / self.total_checks if self.total_checks > 0 else 0.0


class ContractValidator:
    """
    Validador de contratos generados.

    CAPAS DE VALIDACIÓN:
    1. Estructural: Campos requeridos presentes
    2. Epistémica: Coherencia entre niveles
    3. Temporal: Validez declarada
    4. Referencial: Cross-references válidas
    """

    # Campos requeridos por sección
    REQUIRED_FIELDS = {
        "identity": [
            "base_slot", "representative_question_id", "contract_type",
            "contract_version", "created_at", "generator_version",
        ],
        "executor_binding": ["executor_class", "executor_module"],
        "method_binding": [
            "orchestration_mode", "contract_type", "method_count",
            "execution_phases", "efficiency_score",
        ],
        "question_context": ["monolith_ref", "pregunta_completa"],
        "evidence_assembly": ["engine", "type_system", "assembly_rules"],
        "fusion_specification": [
            "contract_type", "primary_strategy", "level_strategies",
        ],
        "cross_layer_fusion": ["N1_to_N2", "N2_to_N1", "N3_to_N1", "N3_to_N2"],
        "human_answer_structure": [
            "format", "template_mode", "sections", "confidence_interpretation",
        ],
        "audit_annotations": [
            "generation_metadata", "source_references", "composition_trace",
        ],
    }

    # Fases requeridas en method_binding
    REQUIRED_PHASES = ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]

    # Reglas requeridas en evidence_assembly
    REQUIRED_RULES = ["R1_empirical_extraction", "R2_inferential_processing",
                      "R3_audit_gate", "R4_narrative_synthesis"]

    def validate_contract(
        self, contract: "GeneratedContract"
    ) -> ValidationReport:
        """
        Valida un contrato generado.

        Returns:
            ValidationReport con resultados detallados
        """
        results: list[ValidationResult] = []

        # Layer 1: Validación estructural
        results.extend(self._validate_structure(contract))

        # Layer 2: Validación epistémica
        results.extend(self._validate_epistemic_coherence(contract))

        # Layer 3: Validación temporal
        results.extend(self._validate_temporal(contract))

        # Layer 4: Validación referencial
        results.extend(self._validate_cross_references(contract))

        # Calcular estadísticas
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical = sum(
            1 for r in results
            if not r.passed and r.severity == ValidationSeverity.CRITICAL
        )

        return ValidationReport(
            contract_id=contract.identity.get("representative_question_id", "UNKNOWN"),
            question_id=contract.identity.get("base_slot", "UNKNOWN"),
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            critical_failures=critical,
            results=results,
            is_valid=(critical == 0),
        )

    def _validate_structure(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación estructural: campos requeridos"""
        results = []
        contract_dict = contract.to_dict()

        for section, fields in self.REQUIRED_FIELDS.items():
            section_data = contract_dict.get(section, {})

            for field in fields:
                check_id = f"STRUCT_{section}_{field}"
                passed = field in section_data and section_data[field] is not None

                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required field '{field}' in section '{section}'",
                    section=section,
                    expected=f"Field '{field}' present and not None",
                    actual=f"{'Present' if passed else 'Missing or None'}",
                ))

        # Validar fases en method_binding
        phases = contract.method_binding.get("execution_phases", {})
        for phase in self.REQUIRED_PHASES:
            check_id = f"STRUCT_method_binding_phase_{phase}"
            passed = phase in phases

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required phase '{phase}' in execution_phases",
                section="method_binding",
                expected=f"Phase '{phase}' present",
                actual=f"{'Present' if passed else 'Missing'}",
            ))

        # Validar reglas en evidence_assembly
        rules = contract.evidence_assembly.get("assembly_rules", [])
        rule_ids = {r.get("rule_id") for r in rules}

        for rule_id in self.REQUIRED_RULES:
            check_id = f"STRUCT_evidence_assembly_rule_{rule_id}"
            passed = rule_id in rule_ids

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required rule '{rule_id}' in assembly_rules",
                section="evidence_assembly",
                expected=f"Rule '{rule_id}' present",
                actual=f"{'Present' if passed else 'Missing'}",
            ))

        return results

    def _validate_epistemic_coherence(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación epistémica: coherencia entre niveles"""
        results = []

        # Verificar que hay métodos en cada nivel
        phases = contract.method_binding.get("execution_phases", {})

        for phase_name, expected_level in [
            ("phase_A_construction", "N1"),
            ("phase_B_computation", "N2"),
            ("phase_C_litigation", "N3"),
        ]:
            phase_data = phases.get(phase_name, {})
            methods = phase_data.get("methods", [])

            # Check: fase tiene métodos
            check_id = f"EPIST_{phase_name}_has_methods"
            passed = len(methods) > 0

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Phase '{phase_name}' must have at least one method",
                section="method_binding",
                expected="At least 1 method",
                actual=f"{len(methods)} methods",
            ))

            # Check: métodos tienen nivel correcto
            for i, method in enumerate(methods):
                method_level = method.get("level", "")
                check_id = f"EPIST_{phase_name}_method_{i}_level"
                passed = method_level.startswith(expected_level)

                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.HIGH,
                    message=f"Method in '{phase_name}' should be level {expected_level}",
                    section="method_binding",
                    expected=f"Level starting with '{expected_level}'",
                    actual=method_level,
                ))

        # Verificar asimetría N3
        cross_layer = contract.cross_layer_fusion
        n3_to_n1 = cross_layer.get("N3_to_N1", {})
        n3_to_n2 = cross_layer.get("N3_to_N2", {})

        check_id = "EPIST_asymmetry_N3_to_N1"
        passed = n3_to_n1.get("asymmetry") == "N1 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="N3→N1 asymmetry must be declared (VETO GATE - CRITICAL)",
            section="cross_layer_fusion",
            expected="asymmetry: 'N1 CANNOT invalidate N3'",
            actual=n3_to_n1.get("asymmetry", "NOT DECLARED"),
        ))

        check_id = "EPIST_asymmetry_N3_to_N2"
        passed = n3_to_n2.get("asymmetry") == "N2 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="N3→N2 asymmetry must be declared (VETO GATE - CRITICAL)",
            section="cross_layer_fusion",
            expected="asymmetry: 'N2 CANNOT invalidate N3'",
            actual=n3_to_n2.get("asymmetry", "NOT DECLARED"),
        ))

        # Verificar TYPE consistencia
        identity_type = contract.identity.get("contract_type")
        method_binding_type = contract.method_binding.get("contract_type")
        fusion_type = contract.fusion_specification.get("contract_type")

        check_id = "EPIST_type_consistency"
        passed = (identity_type == method_binding_type == fusion_type)
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL,
            message="Contract TYPE must be consistent across sections",
            section="global",
            expected=f"All sections: {identity_type}",
            actual=f"identity: {identity_type}, method_binding: {method_binding_type}, fusion: {fusion_type}",
        ))

        return results

    def _validate_temporal(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación temporal: timestamps y validez"""
        results = []

        # Check: created_at presente
        created_at = contract.identity.get("created_at")
        check_id = "TEMP_created_at_present"
        passed = created_at is not None and len(created_at) > 0

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="created_at timestamp must be present",
            section="identity",
            expected="ISO timestamp",
            actual=created_at or "MISSING",
        ))

        # Check: validity_conditions presentes
        validity = contract.audit_annotations.get("validity_conditions", {})
        check_id = "TEMP_validity_conditions"
        passed = (
            "temporal_validity" in validity and
            "review_trigger" in validity
        )

        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.MEDIUM,
            message="Validity conditions should be declared",
            section="audit_annotations",
            expected="temporal_validity and review_trigger present",
            actual=f"Keys: {list(validity.keys())}",
        ))

        return results

    def _validate_cross_references(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación referencial: cross-references válidas"""
        results = []

        # Verificar que sources en assembly_rules matchean provides en methods
        phases = contract.method_binding.get("execution_phases", {})
        all_provides = set()

        for phase_data in phases.values():
            for method in phase_data.get("methods", []):
                provides = method.get("provides")
                if provides:
                    all_provides.add(provides)

        rules = contract.evidence_assembly.get("assembly_rules", [])
        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            sources = rule.get("sources", [])

            # Verificar que al menos algunos sources existen
            # (sources puede ser un subset de provides)
            matching_sources = [s for s in sources if s in all_provides]

            check_id = f"XREF_rule_{rule_id}_sources"
            # Para R4 (synthesis), sources puede estar vacío
            if rule_id == "R4_narrative_synthesis":
                passed = True
            else:
                passed = len(matching_sources) > 0 or len(sources) == 0

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.MEDIUM,
                message=f"Rule '{rule_id}' sources should reference method provides",
                section="evidence_assembly",
                expected="Sources matching method provides",
                actual=f"{len(matching_sources)}/{len(sources)} sources match",
            ))

        # Verificar input_hashes presentes
        hashes = contract.audit_annotations.get("generation_metadata", {}).get("input_hashes", {})
        required_hashes = ["classified_methods", "contratos_clasificados", "method_sets"]

        for hash_name in required_hashes:
            check_id = f"XREF_input_hash_{hash_name}"
            passed = hash_name in hashes and len(hashes[hash_name]) > 0

            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.MEDIUM,
                message=f"Input hash '{hash_name}' should be present for traceability",
                section="audit_annotations",
                expected="Non-empty hash string",
                actual=hashes.get(hash_name, "MISSING"),
            ))

        return results
