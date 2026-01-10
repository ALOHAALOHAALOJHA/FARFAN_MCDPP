#!/usr/bin/env python3
"""
VALIDADOR EPISTEMOLÓGICO V4 - CONTRATOS F.A.R.F.A.N
Implementa checklist completo de 450+ validaciones con cero ambigüedad.

Uso:
    python epistemological_contract_validator_v4.py <contract.json>
    python epistemological_contract_validator_v4.py <contract.json> --strict
    python epistemological_contract_validator_v4.py <contract.json> --report=detailed.md
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Niveles de severidad de fallos"""

    CRITICAL = "CRÍTICO"  # Bloquea uso del contrato
    HIGH = "ALTO"  # Degrada calidad epistemológica
    MEDIUM = "MEDIO"  # Afecta usabilidad
    LOW = "BAJO"  # Mejoras estéticas


@dataclass
class ValidationResult:
    """Resultado de una validación individual"""

    check_id: str
    passed: bool
    severity: Severity
    message: str
    section: str
    expected: Any | None = None
    actual: Any | None = None
    path: str | None = None  # JSON path al campo


@dataclass
class SectionReport:
    """Reporte de una sección completa"""

    section_id: str
    section_name: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_failures: int
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0.0

    @property
    def has_critical_failures(self) -> bool:
        return self.critical_failures > 0


class ContractValidator:
    """Validador principal de contratos epistemológicos V4"""

    # Taxonomía de tipos según PARTE I, Sección 1.1
    TYPE_DEFINITIONS = {
        "TYPE_A": {
            "name": "Semántico",
            "contracts": ["Q001", "Q013"],
            "focus_keywords": ["coherencia narrativa", "nlp", "alineación temática"],
            "n1_strategy": "semantic_corroboration",
            "n2_strategy": "dempster_shafer",
            "r2_merge": "semantic_triangulation",
            "dominant_classes": ["SemanticAnalyzer", "TextMiningEngine", "SemanticProcessor"],
        },
        "TYPE_B": {
            "name": "Bayesiano",
            "contracts": [
                "Q002",
                "Q005",
                "Q007",
                "Q011",
                "Q017",
                "Q018",
                "Q020",
                "Q023",
                "Q024",
                "Q025",
                "Q027",
                "Q029",
            ],
            "focus_keywords": ["significancia estadística", "priors", "probabilístico"],
            "n1_strategy": "concat",
            "n2_strategy": "bayesian_update",
            "r2_merge": "bayesian_update",
            "dominant_classes": [
                "BayesianNumericalAnalyzer",
                "AdaptivePriorCalculator",
                "HierarchicalGenerativeModel",
                "BayesianMechanismInference",
            ],
        },
        "TYPE_C": {
            "name": "Causal",
            "contracts": ["Q008", "Q016", "Q026", "Q030"],
            "focus_keywords": ["topología", "dags", "grafos", "causal"],
            "n1_strategy": "graph_construction",
            "n2_strategy": "topological_overlay",
            "r2_merge": "topological_overlay",
            "dominant_classes": ["CausalExtractor", "TeoriaCambio", "AdvancedDAGValidator"],
        },
        "TYPE_D": {
            "name": "Financiero",
            "contracts": ["Q003", "Q004", "Q006", "Q009", "Q012", "Q015", "Q021", "Q022"],
            "focus_keywords": ["suficiencia presupuestal", "financiero", "presupuesto"],
            "n1_strategy": "concat",
            "n2_strategy": "weighted_mean",
            "r2_merge": "weighted_mean",
            "dominant_classes": ["FinancialAuditor", "PDETMunicipalPlanAnalyzer"],
        },
        "TYPE_E": {
            "name": "Lógico",
            "contracts": ["Q005", "Q010", "Q014", "Q019", "Q028"],
            "focus_keywords": ["contradicciones", "consistencia lógica", "complementariedad"],
            "n1_strategy": "concat",
            "n2_strategy": "weighted_mean",
            "r2_merge": "weighted_mean",
            "dominant_classes": [
                "PolicyContradictionDetector",
                "IndustrialGradeValidator",
                "OperationalizationAuditor",
                "TemporalLogicVerifier",
            ],
        },
    }

    # Definiciones Semánticas para detectar clasificaciones "Contra-Natura"
    TYPE_SEMANTIC_DEFINITIONS = {
        "TYPE_A": {
            "name": "Semántico",
            "expected_keywords": [
                "text",
                "nlp",
                "semantic",
                "chunk",
                "embedding",
                "similarity",
                "meaning",
                "narrative",
                "language",
                "topic",
            ],
            "alien_keywords": [
                "budget",
                "cost",
                "financial",
                "money",
                "dollar",
                "investment",
                "dag",
                "cycle",
                "causal",
                "node",
                "edge",
            ],
        },
        "TYPE_B": {
            "name": "Bayesiano",
            "expected_keywords": [
                "probability",
                "prior",
                "posterior",
                "likelihood",
                "bayes",
                "hdi",
                "significance",
                "statistic",
                "distribution",
            ],
            "alien_keywords": ["sentiment", "parse", "literal", "budget", "graph", "cycle"],
        },
        "TYPE_C": {
            "name": "Causal",
            "expected_keywords": [
                "dag",
                "graph",
                "node",
                "edge",
                "cycle",
                "path",
                "causal",
                "topology",
                "intervention",
                "mechanism",
            ],
            "alien_keywords": [
                "sentiment",
                "embedding",
                "budgeting",
                "financial",
                "parse_text",
                "literal",
            ],
        },
        "TYPE_D": {
            "name": "Financiero",
            "expected_keywords": [
                "budget",
                "cost",
                "financial",
                "money",
                "allocation",
                "funding",
                "sufficiency",
                "investment",
                "expense",
            ],
            "alien_keywords": [
                "sentiment",
                "embedding",
                "similarity",
                "nlp",
                "text",
                "meaning",
                "dag",
                "cycle",
                "causal",
            ],
        },
        "TYPE_E": {
            "name": "Lógico",
            "expected_keywords": [
                "contradiction",
                "inconsistency",
                "logic",
                "sequence",
                "consistency",
                "complementarity",
                "valid",
            ],
            "alien_keywords": ["budget", "sentiment", "embedding", "causal"],
        },
    }

    # Patrones de nombres para clasificación de métodos
    N1_PATTERNS = ["extract_", "parse_", "mine_", "chunk_"]
    N2_PATTERNS = ["analyze_", "score_", "calculate_", "infer_", "evaluate_", "compare_"]
    N3_PATTERNS = ["validate_", "detect_", "audit_", "check_", "test_", "verify_"]

    # Vocabulario prohibido por nivel
    N1_FORBIDDEN_WORDS = ["calcula", "infiere", "evalúa", "compara", "analiza", "score"]
    N2_INFERENTIAL_REQUIRED = [
        "calcula",
        "infiere",
        "evalúa",
        "compara",
        "analiza",
        "transforma",
        "deriva",
    ]

    def __init__(self, contract: dict, strict_mode: bool = False):
        self.contract = contract
        self.strict_mode = strict_mode
        self.results: list[ValidationResult] = []
        self.sections: list[SectionReport] = []
        self.contract_type: str | None = None

    def validate_all(self) -> tuple[bool, list[SectionReport]]:
        """Ejecuta todas las validaciones"""
        print("🔍 Iniciando validación epistemológica V4...")
        print("=" * 80)

        # Sección 0: Pre-validación
        self._section_0_pre_validation()

        # Sección 1: Identity
        self._section_1_identity()

        # Sección 2: Method Binding
        self._section_2_method_binding()

        # Sección 3: Evidence Assembly
        self._section_3_evidence_assembly()

        # Sección 4: Fusion Specification
        self._section_4_fusion_specification()

        # Sección 5: Cross Layer Fusion
        self._section_5_cross_layer_fusion()

        # Sección 6: Human Answer Structure
        self._section_6_human_answer_structure()

        # Sección 7: Traceability
        self._section_7_traceability()

        # Sección 8: Validaciones Cruzadas Globales
        self._section_8_global_cross_validation()

        # Sección 9: Validaciones Específicas por Tipo
        self._section_9_type_specific()

        # Sección 10: Validaciones de Calidad Narrativa (Agregado implícito en 6)

        # Sección 11: Prohibiciones
        self._section_11_prohibitions()

        # Sección 12: Validación Matemática
        self._section_12_mathematical()

        # Sección 13: Metadatos y Compatibilidad
        self._section_13_metadata()

        # Sección 14: Coherencia Global (Auditoría Final)
        self._section_14_global_coherence()

        # Sección 15: Coherencia Semántica (Anti-Patterns de Dominio)
        self._section_15_semantic_coherence()

        # Determinar aprobación
        approved = self._determine_approval()

        return approved, self.sections

    # =========================================================================
    # SECCIÓN 0: PRE-VALIDACIÓN
    # =========================================================================

    def _section_0_pre_validation(self):
        """Validación de existencia de campos obligatorios"""
        section = SectionReport("0", "Pre-validación - Campos Obligatorios", 0, 0, 0, 0)

        required_paths = [
            ("identity.contract_type", Severity.CRITICAL),
            ("identity.base_slot", Severity.CRITICAL),
            ("method_binding.orchestration_mode", Severity.CRITICAL),
            ("method_binding.contract_type", Severity.CRITICAL),
            ("method_binding.execution_phases", Severity.CRITICAL),
            ("evidence_assembly.type_system", Severity.CRITICAL),
            ("evidence_assembly.assembly_rules", Severity.CRITICAL),
            ("fusion_specification.contract_type", Severity.CRITICAL),
            ("fusion_specification.level_strategies", Severity.CRITICAL),
            ("cross_layer_fusion", Severity.CRITICAL),
            ("human_answer_structure.sections", Severity.CRITICAL),
        ]

        for path, severity in required_paths:
            section.total_checks += 1
            exists = self._path_exists(path)

            result = ValidationResult(
                check_id=f"0.{section.total_checks}",
                passed=exists,
                severity=severity,
                message=f"Campo obligatorio {'existe' if exists else 'FALTA'}: {path}",
                section="0",
                path=path,
            )

            if exists:
                section.passed_checks += 1
            else:
                section.failed_checks += 1
                if severity == Severity.CRITICAL:
                    section.critical_failures += 1

            section.results.append(result)

        self.sections.append(section)

        # Si falta algún campo crítico, abortar
        if section.critical_failures > 0:
            print(
                f"❌ FALLO CRÍTICO en Pre-validación: {section.critical_failures} campos obligatorios faltan"
            )
            return

    # =========================================================================
    # SECCIÓN 1: IDENTITY
    # =========================================================================

    def _section_1_identity(self):
        """Validación de identity y clasificación"""
        section = SectionReport("1", "Identity - Clasificación", 0, 0, 0, 0)

        # 1.1.1: contract_type válido
        contract_type = self._get_path("identity.contract_type")
        self.contract_type = contract_type

        self._add_check(
            section,
            "1.1.1",
            Severity.CRITICAL,
            contract_type in self.TYPE_DEFINITIONS,
            "contract_type es válido (TYPE_A/B/C/D/E)",
            expected="TYPE_A|TYPE_B|TYPE_C|TYPE_D|TYPE_E",
            actual=contract_type,
            path="identity.contract_type",
        )

        # 1.1.2: contract_type_name existe
        self._add_check(
            section,
            "1.1.2",
            Severity.HIGH,
            self._path_exists("identity.contract_type_name"),
            "identity.contract_type_name existe",
            path="identity.contract_type_name",
        )

        # 1.1.3: contract_type_focus existe
        self._add_check(
            section,
            "1.1.3",
            Severity.HIGH,
            self._path_exists("identity.contract_type_focus"),
            "identity.contract_type_focus existe",
            path="identity.contract_type_focus",
        )

        # 1.1.4: contract_version es epistemológica
        version = self._get_path("identity.contract_version", "")
        self._add_check(
            section,
            "1.1.4",
            Severity.CRITICAL,
            "4.0" in version or "epistemological" in version.lower(),
            "contract_version es 4.0.0-epistemological o contiene 'epistemological'",
            expected="4.0.0-epistemological",
            actual=version,
            path="identity.contract_version",
        )

        # Validaciones 1.2.X: Correspondencia con tabla PARTE I
        if contract_type and contract_type in self.TYPE_DEFINITIONS:
            type_def = self.TYPE_DEFINITIONS[contract_type]

            # 1.2.X: Nombre correcto
            type_name = self._get_path("identity.contract_type_name", "")
            self._add_check(
                section,
                f"1.2.{contract_type}_name",
                Severity.HIGH,
                type_name == type_def["name"],
                f"contract_type_name = '{type_def['name']}' para {contract_type}",
                expected=type_def["name"],
                actual=type_name,
                path="identity.contract_type_name",
            )

            # 1.2.X: Focus contiene keywords
            focus = self._get_path("identity.contract_type_focus", "").lower()
            has_keyword = any(kw in focus for kw in type_def["focus_keywords"])
            self._add_check(
                section,
                f"1.2.{contract_type}_focus",
                Severity.HIGH,
                has_keyword,
                f"contract_type_focus contiene keyword esperado para {contract_type}",
                expected=f"Alguno de: {type_def['focus_keywords']}",
                actual=focus,
                path="identity.contract_type_focus",
            )

            # 1.2.X: representative_question_id en lista correcta
            rep_q = self._get_path("identity.representative_question_id", "")
            self._add_check(
                section,
                f"1.2.{contract_type}_contract",
                Severity.HIGH,
                rep_q in type_def["contracts"],
                f"representative_question_id pertenece a contratos de {contract_type}",
                expected=f"Uno de: {type_def['contracts']}",
                actual=rep_q,
                path="identity.representative_question_id",
            )

        self.sections.append(section)

    # =========================================================================
    # SECCIÓN 2: METHOD BINDING
    # =========================================================================

    def _section_2_method_binding(self):
        """Validación exhaustiva de method_binding"""
        section = SectionReport("2", "Method Binding - Fases Epistemológicas", 0, 0, 0, 0)

        # 2.1: Orchestration Mode
        orch_mode = self._get_path("method_binding.orchestration_mode")
        self._add_check(
            section,
            "2.1.1",
            Severity.CRITICAL,
            orch_mode == "epistemological_pipeline",
            "orchestration_mode = 'epistemological_pipeline'",
            expected="epistemological_pipeline",
            actual=orch_mode,
            path="method_binding.orchestration_mode",
        )

        self._add_check(
            section,
            "2.1.2",
            Severity.CRITICAL,
            orch_mode != "multi_method_pipeline",
            "orchestration_mode NO es 'multi_method_pipeline' (v3 prohibido)",
            actual=orch_mode,
        )

        mb_type = self._get_path("method_binding.contract_type")
        self._add_check(
            section,
            "2.1.3",
            Severity.CRITICAL,
            mb_type == self.contract_type,
            "method_binding.contract_type = identity.contract_type (IGUALDAD ESTRICTA)",
            expected=self.contract_type,
            actual=mb_type,
        )

        # 2.2: Existencia de fases
        self._add_check(
            section,
            "2.2.1",
            Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_A_construction"),
            "Existe phase_A_construction",
        )

        self._add_check(
            section,
            "2.2.2",
            Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_B_computation"),
            "Existe phase_B_computation",
        )

        self._add_check(
            section,
            "2.2.3",
            Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_C_litigation"),
            "Existe phase_C_litigation",
        )

        # 2.3-2.4: Phase A (N1-EMP)
        self._validate_phase_a(section)

        # 2.5-2.6: Phase B (N2-INF)
        self._validate_phase_b(section)

        # 2.7-2.8: Phase C (N3-AUD)
        self._validate_phase_c(section)

        # 2.9: Method Count Integrity
        self._validate_method_counts(section)

        self.sections.append(section)

    def _validate_phase_a(self, section: SectionReport):
        """Valida Phase A (N1-EMP)"""
        phase_a = self._get_path("method_binding.execution_phases.phase_A_construction", {})

        # Metadata
        self._add_check(
            section,
            "2.3.1",
            Severity.CRITICAL,
            phase_a.get("level") == "N1",
            "phase_A.level = 'N1'",
        )

        self._add_check(
            section,
            "2.3.2",
            Severity.HIGH,
            "empíric" in phase_a.get("level_name", "").lower()
            or "base empírica" in phase_a.get("level_name", "").lower(),
            "phase_A.level_name contiene 'Empírico' o 'Base Empírica'",
        )

        self._add_check(
            section,
            "2.3.3",
            Severity.HIGH,
            "empirismo positivista" in phase_a.get("epistemology", "").lower(),
            "phase_A.epistemology contiene 'Empirismo positivista'",
        )

        methods = phase_a.get("methods", [])
        self._add_check(
            section,
            "2.3.4",
            Severity.CRITICAL,
            len(methods) > 0,
            "phase_A.methods es array no vacío",
            actual=len(methods),
        )

        self._add_check(
            section,
            "2.3.5",
            Severity.CRITICAL,
            phase_a.get("dependencies") == [],
            "phase_A.dependencies = [] (array vacío - N1 no depende)",
            expected=[],
            actual=phase_a.get("dependencies"),
        )

        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n1_method(section, method, idx)

    def _validate_n1_method(self, section: SectionReport, method: dict, idx: int):
        """Valida un método individual de N1"""
        prefix = f"2.4.{idx}"

        # Campos obligatorios
        for field in [
            "class_name",
            "method_name",
            "mother_file",
            "provides",
            "description",
            "classification_rationale",
        ]:
            self._add_check(
                section,
                f"{prefix}.{field}",
                Severity.CRITICAL,
                field in method and method[field],
                f"Método N1[{idx}] tiene campo '{field}' no vacío",
            )

        # Level exacto
        self._add_check(
            section,
            f"{prefix}.level",
            Severity.CRITICAL,
            method.get("level") == "N1-EMP",
            f"Método N1[{idx}].level = 'N1-EMP' (EXACTO)",
            expected="N1-EMP",
            actual=method.get("level"),
        )

        # Output type
        self._add_check(
            section,
            f"{prefix}.output",
            Severity.CRITICAL,
            method.get("output_type") == "FACT",
            f"Método N1[{idx}].output_type = 'FACT'",
            expected="FACT",
            actual=method.get("output_type"),
        )

        # Fusion behavior
        self._add_check(
            section,
            f"{prefix}.fusion",
            Severity.CRITICAL,
            method.get("fusion_behavior") == "additive",
            f"Método N1[{idx}].fusion_behavior = 'additive'",
            expected="additive",
            actual=method.get("fusion_behavior"),
        )

        # Requires vacío
        self._add_check(
            section,
            f"{prefix}.requires",
            Severity.CRITICAL,
            method.get("requires") == [],
            f"Método N1[{idx}].requires = [] (N1 no depende)",
            expected=[],
            actual=method.get("requires"),
        )

        # Rationale referencia guía
        rationale = method.get("classification_rationale", "")
        self._add_check(
            section,
            f"{prefix}.rationale",
            Severity.HIGH,
            "PARTE II" in rationale or "Sección 2.2" in rationale,
            f"Método N1[{idx}] classification_rationale referencia 'PARTE II' o 'Sección 2.2'",
        )

        # Patrón de nombre
        method_name = method.get("method_name", "")
        has_pattern = any(pattern in method_name for pattern in self.N1_PATTERNS)
        self._add_check(
            section,
            f"{prefix}.pattern",
            Severity.HIGH,
            has_pattern,
            f"Método N1[{idx}].method_name contiene patrón N1 (extract_, parse_, mine_, chunk_)",
            actual=method_name,
        )

        # Vocabulario prohibido en description
        desc = method.get("description", "").lower()
        has_forbidden = any(word in desc for word in self.N1_FORBIDDEN_WORDS)
        self._add_check(
            section,
            f"{prefix}.vocab",
            Severity.HIGH,
            not has_forbidden,
            f"Método N1[{idx}].description NO contiene vocabulario inferencial prohibido",
            actual=desc,
        )

    def _validate_phase_b(self, section: SectionReport):
        """Valida Phase B (N2-INF)"""
        phase_b = self._get_path("method_binding.execution_phases.phase_B_computation", {})

        # Metadata
        self._add_check(
            section,
            "2.5.1",
            Severity.CRITICAL,
            phase_b.get("level") == "N2",
            "phase_B.level = 'N2'",
        )

        self._add_check(
            section,
            "2.5.3",
            Severity.HIGH,
            "bayesianismo" in phase_b.get("epistemology", "").lower()
            or "creencias actualizables" in phase_b.get("epistemology", "").lower(),
            "phase_B.epistemology contiene 'Bayesianismo' o 'creencias actualizables'",
        )

        methods = phase_b.get("methods", [])
        self._add_check(
            section,
            "2.5.4",
            Severity.CRITICAL,
            len(methods) > 0,
            "phase_B.methods es array no vacío",
        )

        deps = phase_b.get("dependencies", [])
        self._add_check(
            section,
            "2.5.5",
            Severity.CRITICAL,
            "phase_A_construction" in deps,
            "phase_B.dependencies contiene 'phase_A_construction'",
            actual=deps,
        )

        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n2_method(section, method, idx)

    def _validate_n2_method(self, section: SectionReport, method: dict, idx: int):
        """Valida un método individual de N2"""
        prefix = f"2.6.{idx}"

        # Level
        self._add_check(
            section,
            f"{prefix}.level",
            Severity.CRITICAL,
            method.get("level") == "N2-INF",
            f"Método N2[{idx}].level = 'N2-INF'",
            expected="N2-INF",
            actual=method.get("level"),
        )

        # Output type
        self._add_check(
            section,
            f"{prefix}.output",
            Severity.CRITICAL,
            method.get("output_type") == "PARAMETER",
            f"Método N2[{idx}].output_type = 'PARAMETER'",
            expected="PARAMETER",
            actual=method.get("output_type"),
        )

        # Fusion behavior
        self._add_check(
            section,
            f"{prefix}.fusion",
            Severity.CRITICAL,
            method.get("fusion_behavior") == "multiplicative",
            f"Método N2[{idx}].fusion_behavior = 'multiplicative'",
        )

        # Requires no vacío
        requires = method.get("requires", [])
        self._add_check(
            section,
            f"{prefix}.requires",
            Severity.CRITICAL,
            len(requires) > 0 and "raw_facts" in str(requires).lower(),
            f"Método N2[{idx}].requires existe y contiene 'raw_facts'",
            actual=requires,
        )

        # Modifies existe
        modifies = method.get("modifies", [])
        self._add_check(
            section,
            f"{prefix}.modifies",
            Severity.HIGH,
            len(modifies) > 0,
            f"Método N2[{idx}].modifies existe y no está vacío",
            actual=modifies,
        )

        # Vocabulario inferencial en description
        desc = method.get("description", "").lower()
        has_inferential = any(word in desc for word in self.N2_INFERENTIAL_REQUIRED)
        self._add_check(
            section,
            f"{prefix}.vocab",
            Severity.HIGH,
            has_inferential,
            f"Método N2[{idx}].description contiene vocabulario inferencial",
            actual=desc,
        )

    def _validate_phase_c(self, section: SectionReport):
        """Valida Phase C (N3-AUD)"""
        phase_c = self._get_path("method_binding.execution_phases.phase_C_litigation", {})

        # Metadata
        self._add_check(
            section,
            "2.7.1",
            Severity.CRITICAL,
            phase_c.get("level") == "N3",
            "phase_C.level = 'N3'",
        )

        self._add_check(
            section,
            "2.7.3",
            Severity.HIGH,
            "falsacionismo" in phase_c.get("epistemology", "").lower()
            or "popperiano" in phase_c.get("epistemology", "").lower(),
            "phase_C.epistemology contiene 'Falsacionismo popperiano'",
        )

        methods = phase_c.get("methods", [])
        self._add_check(
            section,
            "2.7.4",
            Severity.CRITICAL,
            len(methods) > 0,
            "phase_C.methods es array no vacío",
        )

        deps = phase_c.get("dependencies", [])
        self._add_check(
            section,
            "2.7.5",
            Severity.CRITICAL,
            "phase_A_construction" in deps and "phase_B_computation" in deps,
            "phase_C.dependencies contiene phase_A Y phase_B",
            actual=deps,
        )

        # Asimetría explícita
        asym = phase_c.get("asymmetry_principle", "")
        self._add_check(
            section,
            "2.7.6",
            Severity.CRITICAL,
            "asymmetry_principle" in phase_c,
            "phase_C tiene campo asymmetry_principle",
        )

        self._add_check(
            section,
            "2.7.7",
            Severity.CRITICAL,
            "N3 can invalidate" in asym and "CANNOT invalidate N3" in asym,
            "asymmetry_principle declara asimetría explícitamente",
            actual=asym,
        )

        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n3_method(section, method, idx)

    def _validate_n3_method(self, section: SectionReport, method: dict, idx: int):
        """Valida un método individual de N3"""
        prefix = f"2.8.{idx}"

        # Level
        self._add_check(
            section,
            f"{prefix}.level",
            Severity.CRITICAL,
            method.get("level") == "N3-AUD",
            f"Método N3[{idx}].level = 'N3-AUD'",
            expected="N3-AUD",
            actual=method.get("level"),
        )

        # Output type
        self._add_check(
            section,
            f"{prefix}.output",
            Severity.CRITICAL,
            method.get("output_type") == "CONSTRAINT",
            f"Método N3[{idx}].output_type = 'CONSTRAINT'",
            expected="CONSTRAINT",
            actual=method.get("output_type"),
        )

        # Fusion behavior
        self._add_check(
            section,
            f"{prefix}.fusion",
            Severity.CRITICAL,
            method.get("fusion_behavior") == "gate",
            f"Método N3[{idx}].fusion_behavior = 'gate'",
        )

        # Requires ambos niveles
        requires = method.get("requires", [])
        has_both = any("fact" in str(r).lower() for r in requires) and any(
            "infer" in str(r).lower() for r in requires
        )
        self._add_check(
            section,
            f"{prefix}.requires",
            Severity.CRITICAL,
            has_both,
            f"Método N3[{idx}].requires contiene raw_facts Y inferences",
        )

        # Veto conditions
        veto = method.get("veto_conditions", {})
        self._add_check(
            section,
            f"{prefix}.veto_exists",
            Severity.CRITICAL,
            len(veto) > 0,
            f"Método N3[{idx}] tiene veto_conditions no vacío",
            actual=len(veto),
        )

        # Validar al menos una condición
        if veto:
            has_valid_condition = False
            has_severe_veto = False
            for cond_name, cond in veto.items():
                if all(k in cond for k in ["trigger", "action", "scope", "confidence_multiplier"]):
                    has_valid_condition = True
                    if cond.get("confidence_multiplier", 1.0) <= 0.5:
                        has_severe_veto = True

            self._add_check(
                section,
                f"{prefix}.veto_valid",
                Severity.CRITICAL,
                has_valid_condition,
                f"Método N3[{idx}] tiene al menos UNA veto_condition completa",
            )

            self._add_check(
                section,
                f"{prefix}.veto_severe",
                Severity.HIGH,
                has_severe_veto,
                f"Método N3[{idx}] tiene al menos UNA condición severa (multiplier ≤ 0.5)",
            )

            # 2.8.15: Classification rationale
            rationale = method.get("classification_rationale", "")
            self._add_check(
                section,
                f"{prefix}.rationale",
                Severity.HIGH,
                "PARTE II" in rationale or "Sección 2.2" in rationale,
                f"Método N3[{idx}] classification_rationale referencia guía",
            )

    def _validate_method_counts(self, section: SectionReport):
        """Valida integridad de conteos"""
        phases = self._get_path("method_binding.execution_phases", {})
        phase_a_count = len(phases.get("phase_A_construction", {}).get("methods", []))
        phase_b_count = len(phases.get("phase_B_computation", {}).get("methods", []))
        phase_c_count = len(phases.get("phase_C_litigation", {}).get("methods", []))

        declared_count = self._get_path("method_binding.method_count", 0)
        actual_count = phase_a_count + phase_b_count + phase_c_count

        self._add_check(
            section,
            "2.9.1",
            Severity.CRITICAL,
            declared_count == actual_count,
            "method_count = suma de métodos en fases",
            expected=actual_count,
            actual=declared_count,
        )

        # Unicidad de provides
        all_provides = self._collect_all_provides()
        self._add_check(
            section,
            "2.9.2",
            Severity.CRITICAL,
            len(all_provides) == len(set(all_provides)),
            "Ningún 'provides' se repite entre fases (unicidad)",
            actual=f"{len(set(all_provides))} únicos de {len(all_provides)} total",
        )

        self._add_check(
            section,
            "2.9.3",
            Severity.HIGH,
            actual_count >= 3,
            "method_count ≥ 3 (al menos un método por fase)",
            actual=actual_count,
        )

    # =========================================================================
    # SECCIÓN 3: EVIDENCE ASSEMBLY
    # =========================================================================

    def _section_3_evidence_assembly(self):
        """Validación de evidence_assembly"""
        section = SectionReport("3", "Evidence Assembly - Tipología y Reglas", 0, 0, 0, 0)

        # Type system
        self._validate_type_system(section)

        # Assembly rules
        self._validate_assembly_rules(section)

        self.sections.append(section)

    def _validate_type_system(self, section: SectionReport):
        """Valida type_system completo"""
        ts = self._get_path("evidence_assembly.type_system", {})

        # Existencia de 4 tipos
        for type_name in ["FACT", "PARAMETER", "CONSTRAINT", "NARRATIVE"]:
            self._add_check(
                section,
                f"3.1.{type_name}",
                Severity.CRITICAL,
                type_name in ts,
                f"type_system.{type_name} existe",
            )

        # FACT
        fact = ts.get("FACT", {})
        self._add_check(
            section,
            "3.2.1",
            Severity.CRITICAL,
            fact.get("origin_level") == "N1",
            "FACT.origin_level = 'N1'",
        )
        self._add_check(
            section,
            "3.2.2",
            Severity.CRITICAL,
            fact.get("fusion_operation") == "graph_node_addition",
            "FACT.fusion_operation = 'graph_node_addition'",
        )
        self._add_check(
            section,
            "3.2.3",
            Severity.CRITICAL,
            fact.get("merge_behavior") == "additive",
            "FACT.merge_behavior = 'additive'",
        )
        self._add_check(
            section, "3.2.4", Severity.HIGH, fact.get("symbol") == "⊕", "FACT.symbol = '⊕'"
        )

        # PARAMETER
        param = ts.get("PARAMETER", {})
        self._add_check(
            section,
            "3.3.1",
            Severity.CRITICAL,
            param.get("origin_level") == "N2",
            "PARAMETER.origin_level = 'N2'",
        )
        self._add_check(
            section,
            "3.3.2",
            Severity.CRITICAL,
            param.get("fusion_operation") == "edge_weight_modification",
            "PARAMETER.fusion_operation = 'edge_weight_modification'",
        )
        self._add_check(
            section,
            "3.3.3",
            Severity.CRITICAL,
            param.get("merge_behavior") == "multiplicative",
            "PARAMETER.merge_behavior = 'multiplicative'",
        )

        # CONSTRAINT
        const = ts.get("CONSTRAINT", {})
        self._add_check(
            section,
            "3.4.1",
            Severity.CRITICAL,
            const.get("origin_level") == "N3",
            "CONSTRAINT.origin_level = 'N3'",
        )
        self._add_check(
            section,
            "3.4.2",
            Severity.CRITICAL,
            const.get("fusion_operation") == "branch_filtering",
            "CONSTRAINT.fusion_operation = 'branch_filtering'",
        )
        self._add_check(
            section,
            "3.4.3",
            Severity.CRITICAL,
            const.get("merge_behavior") == "gate",
            "CONSTRAINT.merge_behavior = 'gate'",
        )

        # NARRATIVE
        narr = ts.get("NARRATIVE", {})
        self._add_check(
            section,
            "3.5.1",
            Severity.CRITICAL,
            narr.get("origin_level") == "N4",
            "NARRATIVE.origin_level = 'N4'",
        )
        self._add_check(
            section,
            "3.5.2",
            Severity.CRITICAL,
            narr.get("fusion_operation") == "synthesis",
            "NARRATIVE.fusion_operation = 'synthesis'",
        )
        self._add_check(
            section,
            "3.5.3",
            Severity.CRITICAL,
            narr.get("merge_behavior") == "terminal",
            "NARRATIVE.merge_behavior = 'terminal'",
        )

    def _validate_assembly_rules(self, section: SectionReport):
        """Valida assembly_rules"""
        rules = self._get_path("evidence_assembly.assembly_rules", [])

        # Exactamente 4
        self._add_check(
            section,
            "3.6.2",
            Severity.CRITICAL,
            len(rules) == 4,
            "assembly_rules tiene EXACTAMENTE 4 reglas",
            expected=4,
            actual=len(rules),
        )

        if len(rules) != 4:
            return

        # IDs correctos
        for i in range(4):
            self._add_check(
                section,
                f"3.6.{i+3}",
                Severity.HIGH,
                rules[i].get("rule_id", "").startswith(f"R{i+1}_"),
                f"Regla [{i}].rule_id comienza con 'R{i+1}_'",
                actual=rules[i].get("rule_id"),
            )

        # R1: Empirical Basis
        self._validate_rule_r1(section, rules[0])

        # R2: Correspondencia con tipo
        self._validate_rule_r2(section, rules[1])

        # R3: Robustness Gate
        self._validate_rule_r3(section, rules[2])

        # R4: Synthesis
        self._validate_rule_r4(section, rules[3])

    def _validate_rule_r1(self, section: SectionReport, r1: dict):
        """Valida R1 específicamente"""
        self._add_check(
            section,
            "3.7.1",
            Severity.CRITICAL,
            r1.get("rule_type") == "empirical_basis",
            "R1.rule_type = 'empirical_basis'",
        )

        self._add_check(
            section,
            "3.7.5",
            Severity.CRITICAL,
            r1.get("output_type") == "FACT",
            "R1.output_type = 'FACT'",
        )

        # Cobertura 100% de Phase A
        r1_sources = set(r1.get("sources", []))
        phase_a_provides = self._get_phase_provides("A")

        self._add_check(
            section,
            "3.7.8",
            Severity.CRITICAL,
            len(r1_sources) == len(phase_a_provides),
            "R1.sources tiene mismo count que Phase A",
            expected=len(phase_a_provides),
            actual=len(r1_sources),
        )

        missing = phase_a_provides - r1_sources
        self._add_check(
            section,
            "3.7.9",
            Severity.CRITICAL,
            len(missing) == 0,
            "TODOS los provides de Phase A están en R1.sources",
            actual=f"Faltan: {missing}" if missing else "Cobertura 100%",
        )

    def _validate_rule_r2(self, section: SectionReport, r2: dict):
        """Valida R2 según tipo de contrato"""
        self._add_check(
            section,
            "3.8.3",
            Severity.CRITICAL,
            r2.get("output_type") == "PARAMETER",
            "R2.output_type = 'PARAMETER'",
        )

        # Cobertura Phase B
        r2_sources = set(r2.get("sources", []))
        phase_b_provides = self._get_phase_provides("B")

        missing = phase_b_provides - r2_sources
        self._add_check(
            section,
            "3.8.6",
            Severity.CRITICAL,
            len(missing) == 0,
            "TODOS los provides de Phase B están en R2.sources",
            actual=f"Faltan: {missing}" if missing else "Cobertura 100%",
        )

        # Validación específica por tipo
        if self.contract_type == "TYPE_A":
            self._add_check(
                section,
                "3.8.8",
                Severity.CRITICAL,
                r2.get("merge_strategy") == "semantic_triangulation",
                "R2.merge_strategy = 'semantic_triangulation' (TYPE_A)",
                expected="semantic_triangulation",
                actual=r2.get("merge_strategy"),
            )

        elif self.contract_type == "TYPE_B":
            self._add_check(
                section,
                "3.8.12",
                Severity.CRITICAL,
                r2.get("merge_strategy") == "bayesian_update",
                "R2.merge_strategy = 'bayesian_update' (TYPE_B)",
                expected="bayesian_update",
                actual=r2.get("merge_strategy"),
            )

        elif self.contract_type == "TYPE_C":
            self._add_check(
                section,
                "3.8.15",
                Severity.CRITICAL,
                r2.get("merge_strategy") == "topological_overlay",
                "R2.merge_strategy = 'topological_overlay' (TYPE_C)",
                expected="topological_overlay",
                actual=r2.get("merge_strategy"),
            )

        elif self.contract_type in ["TYPE_D", "TYPE_E"]:
            self._add_check(
                section,
                "3.8.18",
                Severity.CRITICAL,
                r2.get("merge_strategy") == "weighted_mean",
                f"R2.merge_strategy = 'weighted_mean' ({self.contract_type})",
                expected="weighted_mean",
                actual=r2.get("merge_strategy"),
            )

    def _validate_rule_r3(self, section: SectionReport, r3: dict):
        """Valida R3 - veto gate universal"""
        self._add_check(
            section,
            "3.9.2",
            Severity.CRITICAL,
            r3.get("merge_strategy") == "veto_gate",
            "R3.merge_strategy = 'veto_gate' (UNIVERSAL)",
            expected="veto_gate",
            actual=r3.get("merge_strategy"),
        )

        self._add_check(
            section,
            "3.9.3",
            Severity.CRITICAL,
            r3.get("output_type") == "CONSTRAINT",
            "R3.output_type = 'CONSTRAINT'",
        )

        # Cobertura Phase C
        r3_sources = set(r3.get("sources", []))
        phase_c_provides = self._get_phase_provides("C")

        missing = phase_c_provides - r3_sources
        self._add_check(
            section,
            "3.9.6",
            Severity.CRITICAL,
            len(missing) == 0,
            "TODOS los provides de Phase C están en R3.sources",
            actual=f"Faltan: {missing}" if missing else "Cobertura 100%",
        )

        # Gate logic
        gate_logic = r3.get("gate_logic", {})
        self._add_check(
            section, "3.9.8", Severity.CRITICAL, len(gate_logic) > 0, "R3 tiene gate_logic no vacío"
        )

        self._add_check(
            section,
            "3.9.9",
            Severity.HIGH,
            len(gate_logic) >= 2,
            "gate_logic tiene al menos 2 condiciones",
            actual=len(gate_logic),
        )

        # Al menos una condición severa
        has_severe = any(
            cond.get("confidence_multiplier", 1.0) < 0.5 for cond in gate_logic.values()
        )
        self._add_check(
            section,
            "3.9.12",
            Severity.CRITICAL,
            has_severe,
            "Al menos UNA condición tiene confidence_multiplier < 0.5",
        )

    def _validate_rule_r4(self, section: SectionReport, r4: dict):
        """Valida R4 - synthesis universal"""
        self._add_check(
            section,
            "3.10.1",
            Severity.CRITICAL,
            r4.get("rule_type") == "synthesis",
            "R4.rule_type = 'synthesis'",
        )

        self._add_check(
            section,
            "3.10.5",
            Severity.CRITICAL,
            r4.get("merge_strategy") == "carver_doctoral_synthesis",
            "R4.merge_strategy = 'carver_doctoral_synthesis'",
            expected="carver_doctoral_synthesis",
            actual=r4.get("merge_strategy"),
        )

        self._add_check(
            section,
            "3.10.6",
            Severity.CRITICAL,
            r4.get("output_type") == "NARRATIVE",
            "R4.output_type = 'NARRATIVE'",
        )

    # =========================================================================
    # SECCIÓN 4: FUSION SPECIFICATION
    # =========================================================================

    def _section_4_fusion_specification(self):
        """Validación de fusion_specification"""
        section = SectionReport("4", "Fusion Specification - Estrategias por Nivel", 0, 0, 0, 0)

        fs_type = self._get_path("fusion_specification.contract_type")
        self._add_check(
            section,
            "4.1.1",
            Severity.CRITICAL,
            fs_type == self.contract_type,
            "fusion_specification.contract_type = identity.contract_type",
            expected=self.contract_type,
            actual=fs_type,
        )

        # Level strategies
        self._validate_level_strategies(section)

        # Fusion pipeline
        self._validate_fusion_pipeline(section)

        self.sections.append(section)

    def _validate_level_strategies(self, section: SectionReport):
        """Valida level_strategies según tipo"""
        ls = self._get_path("fusion_specification.level_strategies", {})

        # Existencia
        for level in ["N1_fact_fusion", "N2_parameter_fusion", "N3_constraint_fusion"]:
            self._add_check(
                section,
                f"4.3.{level}",
                Severity.CRITICAL,
                level in ls,
                f"level_strategies.{level} existe",
            )

        # N1 strategy según tipo
        n1_strat = ls.get("N1_fact_fusion", {}).get("strategy")
        if self.contract_type and self.contract_type in self.TYPE_DEFINITIONS:
            expected_n1 = self.TYPE_DEFINITIONS[self.contract_type]["n1_strategy"]
            self._add_check(
                section,
                "4.4.2",
                Severity.CRITICAL,
                n1_strat == expected_n1,
                f"N1_fact_fusion.strategy = '{expected_n1}' para {self.contract_type}",
                expected=expected_n1,
                actual=n1_strat,
            )

        # N2 strategy según tipo
        n2_strat = ls.get("N2_parameter_fusion", {}).get("strategy")
        if self.contract_type and self.contract_type in self.TYPE_DEFINITIONS:
            expected_n2 = self.TYPE_DEFINITIONS[self.contract_type]["n2_strategy"]
            self._add_check(
                section,
                "4.5.3",
                Severity.CRITICAL,
                n2_strat == expected_n2,
                f"N2_parameter_fusion.strategy = '{expected_n2}' para {self.contract_type}",
                expected=expected_n2,
                actual=n2_strat,
            )

        # N3 strategy UNIVERSAL
        n3_strat = ls.get("N3_constraint_fusion", {}).get("strategy")
        self._add_check(
            section,
            "4.6.1",
            Severity.CRITICAL,
            n3_strat == "veto_gate",
            "N3_constraint_fusion.strategy = 'veto_gate' (UNIVERSAL)",
            expected="veto_gate",
            actual=n3_strat,
        )

        # Asimetría en N3
        n3_asym = ls.get("N3_constraint_fusion", {}).get("asymmetry_principle")
        self._add_check(
            section,
            "4.6.3",
            Severity.CRITICAL,
            n3_asym == "audit_dominates",
            "N3_constraint_fusion.asymmetry_principle = 'audit_dominates'",
            expected="audit_dominates",
            actual=n3_asym,
        )

    def _validate_fusion_pipeline(self, section: SectionReport):
        """Valida fusion_pipeline - 4 stages obligatorios"""
        pipeline = self._get_path("fusion_specification.fusion_pipeline", {})

        # Existencia de 4 stages
        for stage in [
            "stage_1_fact_accumulation",
            "stage_2_parameter_application",
            "stage_3_constraint_filtering",
            "stage_4_synthesis",
        ]:
            self._add_check(
                section,
                f"4.7.{stage}",
                Severity.HIGH,
                stage in pipeline,
                f"fusion_pipeline.{stage} existe",
            )

        # Stage 1
        s1 = pipeline.get("stage_1_fact_accumulation", {})
        self._add_check(
            section,
            "4.7.5",
            Severity.CRITICAL,
            s1.get("type_consumed") == "FACT",
            "stage_1.type_consumed = 'FACT'",
        )
        self._add_check(
            section,
            "4.7.6",
            Severity.CRITICAL,
            s1.get("behavior") == "additive",
            "stage_1.behavior = 'additive'",
        )

        # Stage 2
        s2 = pipeline.get("stage_2_parameter_application", {})
        self._add_check(
            section,
            "4.7.8",
            Severity.CRITICAL,
            s2.get("type_consumed") == "PARAMETER",
            "stage_2.type_consumed = 'PARAMETER'",
        )
        self._add_check(
            section,
            "4.7.9",
            Severity.CRITICAL,
            s2.get("behavior") == "multiplicative",
            "stage_2.behavior = 'multiplicative'",
        )

        # Stage 3
        s3 = pipeline.get("stage_3_constraint_filtering", {})
        self._add_check(
            section,
            "4.7.11",
            Severity.CRITICAL,
            s3.get("type_consumed") == "CONSTRAINT",
            "stage_3.type_consumed = 'CONSTRAINT'",
        )
        self._add_check(
            section,
            "4.7.12",
            Severity.CRITICAL,
            s3.get("behavior") == "gate",
            "stage_3.behavior = 'gate'",
        )

        # Stage 4
        s4 = pipeline.get("stage_4_synthesis", {})
        self._add_check(
            section,
            "4.7.14",
            Severity.CRITICAL,
            s4.get("type_produced") == "NARRATIVE",
            "stage_4.type_produced = 'NARRATIVE'",
        )

    # =========================================================================
    # SECCIÓN 5: CROSS LAYER FUSION
    # =========================================================================

    def _section_5_cross_layer_fusion(self):
        """Validación de cross_layer_fusion - asimetría crítica"""
        section = SectionReport("5", "Cross Layer Fusion - Asimetría N3", 0, 0, 0, 0)

        clf = self._get_path("cross_layer_fusion", {})

        # Relaciones obligatorias
        required_relations = ["N1_to_N2", "N2_to_N1", "N3_to_N1", "N3_to_N2", "all_to_N4"]
        for rel in required_relations:
            self._add_check(
                section,
                f"5.1.{rel}",
                Severity.CRITICAL,
                rel in clf,
                f"cross_layer_fusion.{rel} existe",
            )

        # N1_to_N2: Forward propagation
        n1_to_n2 = clf.get("N1_to_N2", {})
        self._add_check(
            section,
            "5.2.3",
            Severity.HIGH,
            n1_to_n2.get("data_flow") == "forward_propagation",
            "N1_to_N2.data_flow = 'forward_propagation'",
        )

        # N2_to_N1: Backpropagation
        n2_to_n1 = clf.get("N2_to_N1", {})
        self._add_check(
            section,
            "5.3.3",
            Severity.HIGH,
            n2_to_n1.get("data_flow") == "confidence_backpropagation",
            "N2_to_N1.data_flow = 'confidence_backpropagation'",
        )

        # N3_to_N1: ASIMETRÍA CRÍTICA
        n3_to_n1 = clf.get("N3_to_N1", {})
        self._add_check(
            section,
            "5.4.1",
            Severity.CRITICAL,
            "BLOCK" in n3_to_n1.get("relationship", "").upper()
            or "INVALIDATE" in n3_to_n1.get("relationship", "").upper(),
            "N3_to_N1.relationship menciona 'BLOCK' o 'INVALIDATE'",
        )

        self._add_check(
            section,
            "5.4.3",
            Severity.CRITICAL,
            n3_to_n1.get("data_flow") == "veto_propagation",
            "N3_to_N1.data_flow = 'veto_propagation'",
        )

        asym = n3_to_n1.get("asymmetry", "")
        self._add_check(
            section,
            "5.4.4",
            Severity.CRITICAL,
            "asymmetry" in n3_to_n1,
            "N3_to_N1 tiene campo asymmetry",
        )

        self._add_check(
            section,
            "5.4.5",
            Severity.CRITICAL,
            "CANNOT" in asym.upper() and "N1" in asym and "N3" in asym,
            "N3_to_N1.asymmetry contiene 'N1 CANNOT invalidate N3'",
            actual=asym,
        )

        # N3_to_N2: ASIMETRÍA CRÍTICA
        n3_to_n2 = clf.get("N3_to_N2", {})
        self._add_check(
            section,
            "5.5.4",
            Severity.CRITICAL,
            "asymmetry" in n3_to_n2,
            "N3_to_N2 tiene campo asymmetry",
        )

        asym2 = n3_to_n2.get("asymmetry", "")
        self._add_check(
            section,
            "5.5.5",
            Severity.CRITICAL,
            "CANNOT" in asym2.upper() and "N2" in asym2 and "N3" in asym2,
            "N3_to_N2.asymmetry contiene 'N2 CANNOT invalidate N3'",
            actual=asym2,
        )

        # all_to_N4
        all_n4 = clf.get("all_to_N4", {})
        self._add_check(
            section,
            "5.6.3",
            Severity.HIGH,
            all_n4.get("data_flow") == "terminal_aggregation",
            "all_to_N4.data_flow = 'terminal_aggregation'",
        )

        # Blocking propagation rules
        bpr = clf.get("blocking_propagation_rules", {})
        self._add_check(
            section,
            "5.7.1",
            Severity.HIGH,
            len(bpr) > 0,
            "blocking_propagation_rules existe y no está vacío",
        )

        self._add_check(
            section,
            "5.7.2",
            Severity.HIGH,
            len(bpr) >= 2,
            "blocking_propagation_rules tiene al menos 2 condiciones",
            actual=len(bpr),
        )

        self.sections.append(section)

    # =========================================================================
    # SECCIÓN 6: HUMAN ANSWER STRUCTURE
    # =========================================================================

    def _section_6_human_answer_structure(self):
        """Validación de human_answer_structure"""
        section = SectionReport(
            "6", "Human Answer Structure - Narrativa Epistemológica", 0, 0, 0, 0
        )

        has = self._get_path("human_answer_structure", {})

        # Metadata
        self._add_check(
            section,
            "6.1.1",
            Severity.CRITICAL,
            has.get("format") == "markdown",
            "format = 'markdown'",
        )

        self._add_check(
            section,
            "6.1.2",
            Severity.CRITICAL,
            has.get("template_mode") == "epistemological_narrative",
            "template_mode = 'epistemological_narrative'",
        )

        has_type = has.get("contract_type")
        self._add_check(
            section,
            "6.1.3",
            Severity.CRITICAL,
            has_type == self.contract_type,
            "human_answer_structure.contract_type = identity.contract_type",
            expected=self.contract_type,
            actual=has_type,
        )

        # Secciones
        sections = has.get("sections", [])
        self._add_check(
            section,
            "6.1.5",
            Severity.CRITICAL,
            len(sections) == 4,
            "sections tiene EXACTAMENTE 4 secciones",
            expected=4,
            actual=len(sections),
        )

        if len(sections) == 4:
            # Validar IDs correctos
            expected_ids = ["S1_verdict", "S2_empirical_base", "S3_robustness_audit", "S4_gaps"]
            for i, exp_id in enumerate(expected_ids):
                actual_id = sections[i].get("section_id")
                self._add_check(
                    section,
                    f"6.2.{i+1}",
                    Severity.CRITICAL,
                    actual_id == exp_id,
                    f"sections[{i}].section_id = '{exp_id}'",
                    expected=exp_id,
                    actual=actual_id,
                )

            # Validar cada sección
            self._validate_section_s1(section, sections[0])
            self._validate_section_s2(section, sections[1])
            self._validate_section_s3(section, sections[2])
            self._validate_section_s4(section, sections[3])

        # Argumentative roles
        self._validate_argumentative_roles(section, has)

        # Confidence interpretation
        self._validate_confidence_interpretation(section, has)

        self.sections.append(section)

    def _validate_section_s1(self, section: SectionReport, s1: dict):
        """Valida S1 - Veredicto"""
        self._add_check(
            section, "6.3.2", Severity.CRITICAL, s1.get("layer") == "N4", "S1.layer = 'N4'"
        )

        self._add_check(
            section,
            "6.3.4",
            Severity.HIGH,
            s1.get("narrative_style") == "declarative",
            "S1.narrative_style = 'declarative'",
        )

        self._add_check(
            section,
            "6.3.5",
            Severity.HIGH,
            s1.get("argumentative_role") == "SYNTHESIS",
            "S1.argumentative_role = 'SYNTHESIS'",
        )

        # Placeholders
        template = s1.get("template", {})
        placeholders = template.get("placeholders", {})

        required_ph = [
            "verdict_statement",
            "final_confidence_pct",
            "confidence_label",
            "method_count",
        ]
        for ph in required_ph:
            self._add_check(
                section,
                f"6.3.{ph}",
                Severity.HIGH,
                ph in placeholders,
                f"S1.template.placeholders contiene '{ph}'",
            )

    def _validate_section_s2(self, section: SectionReport, s2: dict):
        """Valida S2 - Evidencia Empírica"""
        self._add_check(
            section, "6.4.2", Severity.CRITICAL, s2.get("layer") == "N1", "S2.layer = 'N1'"
        )

        self._add_check(
            section,
            "6.4.5",
            Severity.HIGH,
            s2.get("argumentative_role") == "EMPIRICAL_BASIS",
            "S2.argumentative_role = 'EMPIRICAL_BASIS'",
        )

        # Epistemological note
        epi_note = s2.get("epistemological_note", {})
        self._add_check(
            section,
            "6.4.7",
            Severity.HIGH,
            "epistemological_note" in s2,
            "S2 tiene epistemological_note",
        )

        self._add_check(
            section,
            "6.4.8",
            Severity.HIGH,
            epi_note.get("include_in_output") == True,
            "S2.epistemological_note.include_in_output = true",
        )

    def _validate_section_s3(self, section: SectionReport, s3: dict):
        """Valida S3 - Robustez (CRÍTICA)"""
        self._add_check(
            section, "6.5.2", Severity.CRITICAL, s3.get("layer") == "N3", "S3.layer = 'N3'"
        )

        self._add_check(
            section,
            "6.5.5",
            Severity.CRITICAL,
            s3.get("argumentative_role") == "ROBUSTNESS_QUALIFIER",
            "S3.argumentative_role = 'ROBUSTNESS_QUALIFIER'",
        )

        # VETO DISPLAY (OBLIGATORIO)
        self._add_check(
            section,
            "6.5.6",
            Severity.CRITICAL,
            "veto_display" in s3,
            "S3 tiene campo veto_display (OBLIGATORIO)",
        )

        veto = s3.get("veto_display", {})
        self._add_check(
            section,
            "6.5.7",
            Severity.CRITICAL,
            "if_veto_triggered" in veto,
            "S3.veto_display.if_veto_triggered existe",
        )

        self._add_check(
            section,
            "6.5.8",
            Severity.CRITICAL,
            "if_no_veto" in veto,
            "S3.veto_display.if_no_veto existe",
        )

        # Template del veto debe ser prominente
        if_veto = veto.get("if_veto_triggered", {})
        # Manejar caso donde if_veto puede ser string en lugar de dict
        if isinstance(if_veto, dict):
            template = if_veto.get("template", "")
        elif isinstance(if_veto, str):
            template = if_veto
        else:
            template = ""

        has_emoji = "⛔" in template or "⚠️" in template
        self._add_check(
            section,
            "6.5.9",
            Severity.CRITICAL,
            has_emoji,
            "if_veto_triggered.template comienza con emoji ⛔ o ⚠️",
            actual=template[:20] if template else "",
        )

        has_alert = (
            "ALERTA" in template.upper() or "INVÁLIDO" in template.upper() if template else False
        )
        self._add_check(
            section,
            "6.5.10",
            Severity.CRITICAL,
            has_alert,
            "if_veto_triggered.template contiene 'ALERTA' o 'INVÁLIDO' (MAYÚSCULAS)",
        )

    def _validate_section_s4(self, section: SectionReport, s4: dict):
        """Valida S4 - Gaps"""
        self._add_check(
            section, "6.6.2", Severity.HIGH, s4.get("layer") == "N4-META", "S4.layer = 'N4-META'"
        )

        self._add_check(
            section,
            "6.6.5",
            Severity.HIGH,
            s4.get("argumentative_role") == "META_TRACEABILITY",
            "S4.argumentative_role = 'META_TRACEABILITY'",
        )

    def _validate_argumentative_roles(self, section: SectionReport, has: dict):
        """Valida argumentative_roles"""
        roles = has.get("argumentative_roles", {})

        for level in ["N1_roles", "N2_roles", "N3_roles", "N4_roles"]:
            self._add_check(
                section,
                f"6.7.{level}",
                Severity.HIGH,
                level in roles and len(roles.get(level, [])) > 0,
                f"argumentative_roles.{level} existe y no está vacío",
            )

        # N3 debe tener roles críticos
        n3_roles = roles.get("N3_roles", [])
        role_names = [r.get("role") for r in n3_roles]

        self._add_check(
            section,
            "6.7.7",
            Severity.HIGH,
            "ROBUSTNESS_QUALIFIER" in role_names,
            "N3_roles contiene 'ROBUSTNESS_QUALIFIER'",
        )

        self._add_check(
            section,
            "6.7.8",
            Severity.HIGH,
            "REFUTATIONAL_SIGNAL" in role_names,
            "N3_roles contiene 'REFUTATIONAL_SIGNAL'",
        )

    def _validate_confidence_interpretation(self, section: SectionReport, has: dict):
        """Valida confidence_interpretation - 4 rangos"""
        ci = has.get("confidence_interpretation", {})

        for rango in ["critical", "low", "medium", "high"]:
            self._add_check(
                section,
                f"6.9.{rango}",
                Severity.CRITICAL,
                rango in ci,
                f"confidence_interpretation.{rango} existe",
            )

        # Critical debe mencionar veto
        critical = ci.get("critical", {})
        self._add_check(
            section,
            "6.9.13",
            Severity.CRITICAL,
            critical.get("label") == "INVÁLIDO",
            "critical.label = 'INVÁLIDO' (EXACTO)",
            expected="INVÁLIDO",
            actual=critical.get("label"),
        )

        desc = critical.get("description", "").lower()
        self._add_check(
            section,
            "6.9.14",
            Severity.CRITICAL,
            "veto" in desc or "inválido" in desc or "no usar" in desc,
            "critical.description menciona 'veto' o 'inválido' o 'NO usar'",
        )

        self._add_check(
            section,
            "6.9.15",
            Severity.HIGH,
            critical.get("display") == "🔴",
            "critical.display = '🔴'",
        )

        # High debe permitir uso
        high = ci.get("high", {})
        self._add_check(
            section,
            "6.9.21",
            Severity.HIGH,
            high.get("label") == "ROBUSTO",
            "high.label = 'ROBUSTO'",
        )

        self._add_check(
            section, "6.9.22", Severity.HIGH, high.get("display") == "🟢", "high.display = '🟢'"
        )

    # =========================================================================
    # SECCIÓN 7: TRACEABILITY
    # =========================================================================

    def _section_7_traceability(self):
        """Validación de traceability"""
        section = SectionReport("7", "Traceability - Documentación", 0, 0, 0, 0)

        trace = self._get_path("traceability", {})

        # Canonical sources
        sources = trace.get("canonical_sources", {})
        self._add_check(
            section,
            "7.1.2",
            Severity.HIGH,
            "epistemological_guide" in sources,
            "canonical_sources.epistemological_guide existe",
        )

        # Generation
        gen = trace.get("generation", {})
        method = gen.get("method", "")
        self._add_check(
            section,
            "7.2.2",
            Severity.HIGH,
            "v4" in method.lower() or "epistemological" in method.lower(),
            "generation.method contiene 'v4' o 'epistemological'",
            actual=method,
        )

        # Refactoring history
        history = trace.get("refactoring_history", [])
        self._add_check(
            section,
            "7.3.1",
            Severity.HIGH,
            len(history) > 0,
            "refactoring_history existe y tiene al menos 1 entrada",
            actual=len(history),
        )

        if history:
            last = history[-1]
            to_ver = last.get("to_version", "")
            self._add_check(
                section,
                "7.3.3",
                Severity.HIGH,
                "4.0" in to_ver or "epistemological" in to_ver.lower(),
                "Última entrada.to_version contiene '4.0' o 'epistemological'",
                actual=to_ver,
            )

            # Framework epistemológico
            fw = last.get("epistemological_framework", {})
            self._add_check(
                section,
                "7.3.8",
                Severity.HIGH,
                fw.get("N1") == "Empirismo positivista",
                "epistemological_framework.N1 = 'Empirismo positivista'",
            )

            self._add_check(
                section,
                "7.3.9",
                Severity.HIGH,
                fw.get("N2") == "Bayesianismo subjetivista",
                "epistemological_framework.N2 = 'Bayesianismo subjetivista'",
            )

            self._add_check(
                section,
                "7.3.10",
                Severity.HIGH,
                fw.get("N3") == "Falsacionismo popperiano",
                "epistemological_framework.N3 = 'Falsacionismo popperiano'",
            )

        # Prohibiciones
        prohib = trace.get("prohibitions", {})
        self._add_check(
            section,
            "7.4.2",
            Severity.HIGH,
            prohib.get("v3_recovery") == "FORBIDDEN",
            "prohibitions.v3_recovery = 'FORBIDDEN'",
        )

        self.sections.append(section)

    # =========================================================================
    # SECCIÓN 8: VALIDACIONES CRUZADAS GLOBALES
    # =========================================================================

    def _section_8_global_cross_validation(self):
        """Validaciones cruzadas globales"""
        section = SectionReport("8", "Validaciones Cruzadas Globales", 0, 0, 0, 0)

        # Coherencia de contract_type en 5 lugares
        identity_type = self._get_path("identity.contract_type")
        mb_type = self._get_path("method_binding.contract_type")
        fs_type = self._get_path("fusion_specification.contract_type")
        has_type = self._get_path("human_answer_structure.contract_type")

        all_match = identity_type == mb_type == fs_type == has_type
        self._add_check(
            section,
            "8.1.5",
            Severity.CRITICAL,
            all_match,
            "TODOS los contract_type son iguales (identity, method_binding, fusion_spec, human_answer)",
            expected=identity_type,
            actual=f"identity={identity_type}, mb={mb_type}, fs={fs_type}, has={has_type}",
        )

        # Cobertura total de métodos
        all_provides = self._collect_all_provides()
        r1_sources = set(
            self._get_path("evidence_assembly.assembly_rules", [{}])[0].get("sources", [])
        )

        phase_a_provides = self._get_phase_provides("A")
        uncovered_a = phase_a_provides - r1_sources
        self._add_check(
            section,
            "8.2.1",
            Severity.CRITICAL,
            len(uncovered_a) == 0,
            "Todos los provides de phase_A aparecen en R1.sources",
            actual=f"Sin cubrir: {uncovered_a}" if uncovered_a else "100%",
        )

        # Counts matemáticos
        phases = self._get_path("method_binding.execution_phases", {})
        count_a = len(phases.get("phase_A_construction", {}).get("methods", []))
        count_b = len(phases.get("phase_B_computation", {}).get("methods", []))
        count_c = len(phases.get("phase_C_litigation", {}).get("methods", []))
        declared = self._get_path("method_binding.method_count", 0)

        self._add_check(
            section,
            "8.3.1",
            Severity.CRITICAL,
            declared == count_a + count_b + count_c,
            "method_count = |phase_A| + |phase_B| + |phase_C|",
            expected=count_a + count_b + count_c,
            actual=declared,
        )

        # No contradicciones epistemológicas
        self._validate_no_contradictions(section)

        # Correspondencia estratégica
        self._validate_strategy_correspondence(section)

        self.sections.append(section)

    def _validate_no_contradictions(self, section: SectionReport):
        """Valida que no hay contradicciones epistemológicas"""
        phases = self._get_path("method_binding.execution_phases", {})

        # N1 solo FACT
        for method in phases.get("phase_A_construction", {}).get("methods", []):
            output = method.get("output_type")
            self._add_check(
                section,
                f"8.4.1.{method.get('method_name')}",
                Severity.CRITICAL,
                output == "FACT",
                f"Método N1 '{method.get('method_name')}' tiene output_type = FACT",
                expected="FACT",
                actual=output,
            )

        # N3 todos tienen veto_conditions
        for method in phases.get("phase_C_litigation", {}).get("methods", []):
            has_veto = len(method.get("veto_conditions", {})) > 0
            self._add_check(
                section,
                f"8.4.6.{method.get('method_name')}",
                Severity.CRITICAL,
                has_veto,
                f"Método N3 '{method.get('method_name')}' tiene veto_conditions",
                actual="Sí" if has_veto else "NO - FALLA CRÍTICA",
            )

    def _validate_strategy_correspondence(self, section: SectionReport):
        """Valida correspondencia tipo → estrategias"""
        if not self.contract_type or self.contract_type not in self.TYPE_DEFINITIONS:
            return

        type_def = self.TYPE_DEFINITIONS[self.contract_type]

        # N1 strategy
        n1_actual = self._get_path("fusion_specification.level_strategies.N1_fact_fusion.strategy")
        self._add_check(
            section,
            f"8.5.{self.contract_type}_n1",
            Severity.CRITICAL,
            n1_actual == type_def["n1_strategy"],
            f"N1_strategy = '{type_def['n1_strategy']}' para {self.contract_type}",
            expected=type_def["n1_strategy"],
            actual=n1_actual,
        )

        # N2 strategy
        n2_actual = self._get_path(
            "fusion_specification.level_strategies.N2_parameter_fusion.strategy"
        )
        self._add_check(
            section,
            f"8.5.{self.contract_type}_n2",
            Severity.CRITICAL,
            n2_actual == type_def["n2_strategy"],
            f"N2_strategy = '{type_def['n2_strategy']}' para {self.contract_type}",
            expected=type_def["n2_strategy"],
            actual=n2_actual,
        )

        # R2 merge strategy
        r2_merge = (
            self._get_path("evidence_assembly.assembly_rules", [{}])[1].get("merge_strategy")
            if len(self._get_path("evidence_assembly.assembly_rules", [])) > 1
            else None
        )
        self._add_check(
            section,
            f"8.5.{self.contract_type}_r2",
            Severity.CRITICAL,
            r2_merge == type_def["r2_merge"],
            f"R2.merge_strategy = '{type_def['r2_merge']}' para {self.contract_type}",
            expected=type_def["r2_merge"],
            actual=r2_merge,
        )

        # N3 universal
        n3_actual = self._get_path(
            "fusion_specification.level_strategies.N3_constraint_fusion.strategy"
        )
        self._add_check(
            section,
            "8.5.universal_n3",
            Severity.CRITICAL,
            n3_actual == "veto_gate",
            "N3_strategy = 'veto_gate' (UNIVERSAL para todos los tipos)",
            expected="veto_gate",
            actual=n3_actual,
        )

    # =========================================================================
    # SECCIÓN 9: VALIDACIONES ESPECÍFICAS POR TIPO
    # =========================================================================

    def _section_9_type_specific(self):
        """Validaciones específicas según tipo de contrato"""
        if not self.contract_type or self.contract_type not in self.TYPE_DEFINITIONS:
            return

        section = SectionReport("9", f"Validaciones Específicas - {self.contract_type}", 0, 0, 0, 0)

        type_def = self.TYPE_DEFINITIONS[self.contract_type]

        # Validar clases dominantes
        all_methods = self._get_all_methods()
        class_counts = {}
        for method in all_methods:
            cls = method.get("class_name", "")
            class_counts[cls] = class_counts.get(cls, 0) + 1

        has_dominant = any(cls in class_counts for cls in type_def["dominant_classes"])
        self._add_check(
            section,
            f"9.{self.contract_type}.1",
            Severity.HIGH,
            has_dominant,
            f"Contrato incluye clases dominantes de {self.contract_type}",
            expected=type_def["dominant_classes"],
            actual=list(class_counts.keys()),
        )

        # Validaciones específicas por tipo
        if self.contract_type == "TYPE_C":
            self._validate_type_c_specific(section)
        elif self.contract_type == "TYPE_D":
            self._validate_type_d_specific(section)
        elif self.contract_type == "TYPE_E":
            self._validate_type_e_specific(section)

        self.sections.append(section)

    def _validate_type_c_specific(self, section: SectionReport):
        """Validaciones específicas TYPE_C (Causal)"""
        # Debe tener condición cycle_detected
        bpr = self._get_path("cross_layer_fusion.blocking_propagation_rules", {})
        has_cycle = any("cycle" in cond.lower() for cond in bpr.keys())
        self._add_check(
            section,
            "9.3.8",
            Severity.CRITICAL,
            has_cycle,
            "TYPE_C: blocking_propagation_rules tiene condición sobre 'cycle'",
            actual=list(bpr.keys()),
        )

    def _validate_type_d_specific(self, section: SectionReport):
        """Validaciones específicas TYPE_D (Financiero)"""
        # R3 debe mencionar financial
        r3 = (
            self._get_path("evidence_assembly.assembly_rules", [{}])[2]
            if len(self._get_path("evidence_assembly.assembly_rules", [])) > 2
            else {}
        )
        rule_type = r3.get("rule_type", "").lower()
        self._add_check(
            section,
            "9.4.4",
            Severity.CRITICAL,
            "financial" in rule_type,
            "TYPE_D: R3.rule_type contiene 'financial_coherence_audit'",
            actual=rule_type,
        )

        # N3_roles debe tener FINANCIAL_CONSTRAINT
        roles = self._get_path("human_answer_structure.argumentative_roles.N3_roles", [])
        role_names = [r.get("role") for r in roles]
        self._add_check(
            section,
            "9.4.9",
            Severity.HIGH,
            "FINANCIAL_CONSTRAINT" in role_names,
            "TYPE_D: N3_roles contiene 'FINANCIAL_CONSTRAINT'",
        )

    def _validate_type_e_specific(self, section: SectionReport):
        """Validaciones específicas TYPE_E (Lógico)"""
        # N3_roles debe tener LOGICAL_INCONSISTENCY
        roles = self._get_path("human_answer_structure.argumentative_roles.N3_roles", [])
        role_names = [r.get("role") for r in roles]
        self._add_check(
            section,
            "9.5.9",
            Severity.HIGH,
            "LOGICAL_INCONSISTENCY" in role_names,
            "TYPE_E: N3_roles contiene 'LOGICAL_INCONSISTENCY'",
        )

    # =========================================================================
    # SECCIÓN 11: PROHIBICIONES
    # =========================================================================

    def _section_11_prohibitions(self):
        """Validación de anti-patterns y prohibiciones"""
        section = SectionReport("11", "Prohibiciones y Anti-Patterns", 0, 0, 0, 0)

        # No existe campo "methods" plano
        self._add_check(
            section,
            "11.1.1",
            Severity.CRITICAL,
            not self._path_exists("method_binding.methods"),
            "NO existe campo 'methods' plano en method_binding (debe ser execution_phases)",
        )

        # orchestration_mode correcto
        orch = self._get_path("method_binding.orchestration_mode")
        self._add_check(
            section,
            "11.1.2",
            Severity.CRITICAL,
            orch != "multi_method_pipeline",
            "orchestration_mode NO es 'multi_method_pipeline' (v3 prohibido)",
        )

        # Version >= 4.0
        version = self._get_path("identity.contract_version", "")
        self._add_check(
            section,
            "11.1.3",
            Severity.CRITICAL,
            "4." in version or "epistemological" in version.lower(),
            "contract_version >= 4.0 o contiene 'epistemological'",
            actual=version,
        )

        # Anti-patterns de asimetría
        clf = self._get_path("cross_layer_fusion", {})
        self._add_check(
            section,
            "11.4.1",
            Severity.CRITICAL,
            "N1_to_N3" not in clf,
            "NO existe relación N1_to_N3 (prohibido - invertiría asimetría)",
        )

        self._add_check(
            section,
            "11.4.2",
            Severity.CRITICAL,
            "N2_to_N3" not in clf,
            "NO existe relación N2_to_N3 (prohibido - invertiría asimetría)",
        )

        self.sections.append(section)

    # =========================================================================
    # SECCIÓN 12: VALIDACIÓN MATEMÁTICA
    # =========================================================================

    def _section_12_mathematical(self):
        """Validaciones matemáticas y lógicas"""
        section = SectionReport("12", "Validación Matemática y Lógica", 0, 0, 0, 0)

        # Confidence multipliers en rango
        all_methods = self._get_all_methods()
        for method in all_methods:
            veto_conds = method.get("veto_conditions", {})
            for cond_name, cond in veto_conds.items():
                mult = cond.get("confidence_multiplier", 1.0)
                self._add_check(
                    section,
                    f"12.1.{method.get('method_name')}.{cond_name}",
                    Severity.HIGH,
                    0.0 <= mult <= 1.0,
                    f"confidence_multiplier en [0.0, 1.0] para {cond_name}",
                    actual=mult,
                )

        # Rangos de confidence_interpretation no se solapan
        ci = self._get_path("human_answer_structure.confidence_interpretation", {})
        if all(k in ci for k in ["critical", "low", "medium", "high"]):
            critical_range = ci["critical"].get("range", [0, 19])
            low_range = ci["low"].get("range", [20, 49])

            self._add_check(
                section,
                "12.1.5",
                Severity.HIGH,
                critical_range[1] + 1 == low_range[0],
                "critical.range[1] + 1 = low.range[0] (continuidad)",
                expected=low_range[0],
                actual=critical_range[1] + 1,
            )

        # Grafos de dependencias acíclicos
        self._validate_no_cycles(section)

        self.sections.append(section)

    def _validate_no_cycles(self, section: SectionReport):
        """Valida que no hay dependencias cíclicas"""
        phases = self._get_path("method_binding.execution_phases", {})

        a_deps = phases.get("phase_A_construction", {}).get("dependencies", [])
        b_deps = phases.get("phase_B_computation", {}).get("dependencies", [])
        c_deps = phases.get("phase_C_litigation", {}).get("dependencies", [])

        self._add_check(
            section,
            "12.2.1",
            Severity.CRITICAL,
            len(a_deps) == 0,
            "phase_A.dependencies = [] (no tiene prerrequisitos)",
        )

        self._add_check(
            section,
            "12.2.2",
            Severity.CRITICAL,
            "phase_A_construction" in b_deps,
            "phase_B.dependencies contiene phase_A",
        )

        has_both = "phase_A_construction" in c_deps and "phase_B_computation" in c_deps
        self._add_check(
            section,
            "12.2.3",
            Severity.CRITICAL,
            has_both,
            "phase_C.dependencies contiene phase_A Y phase_B",
        )

    # =========================================================================
    # SECCIÓN 13: METADATOS Y COMPATIBILIDAD
    # =========================================================================
    def _section_13_metadata(self):
        section = SectionReport("13", "Metadatos y Compatibilidad", 0, 0, 0, 0)

        # Output Contract
        out_contract = self._get_path("output_contract", {})
        schema = out_contract.get("schema", {})

        required_fields = ["base_slot", "question_id", "evidence", "score", "human_answer"]
        for field in required_fields:
            self._add_check(
                section,
                f"13.1.{field}",
                Severity.HIGH,
                field in schema.get("required", []),
                f"output_contract.schema.required contiene '{field}'",
            )

        # Epistemological trace en schema
        self._add_check(
            section,
            "13.1.7",
            Severity.HIGH,
            "epistemological_trace" in schema.get("properties", {}),
            "output_contract.schema tiene campo 'epistemological_trace'",
        )

        self.sections.append(section)

    # =========================================================================
    # SECCIÓN 14: COHERENCIA GLOBAL (AUDITORÍA FINAL)
    # =========================================================================

    def _section_14_global_coherence(self):
        """Auditoría final de coherencia global"""
        section = SectionReport("14", "Auditoría Final - Coherencia Global", 0, 0, 0, 0)

        # Triple coherencia de estrategias
        if self.contract_type and self.contract_type in self.TYPE_DEFINITIONS:
            type_def = self.TYPE_DEFINITIONS[self.contract_type]

            n1_strat = self._get_path(
                "fusion_specification.level_strategies.N1_fact_fusion.strategy"
            )
            n2_strat = self._get_path(
                "fusion_specification.level_strategies.N2_parameter_fusion.strategy"
            )
            r2_merge = (
                self._get_path("evidence_assembly.assembly_rules", [{}])[1].get("merge_strategy")
                if len(self._get_path("evidence_assembly.assembly_rules", [])) > 1
                else None
            )

            all_correct = (
                n1_strat == type_def["n1_strategy"]
                and n2_strat == type_def["n2_strategy"]
                and r2_merge == type_def["r2_merge"]
            )

            self._add_check(
                section,
                "14.1.4",
                Severity.CRITICAL,
                all_correct,
                f"Triple coherencia estratégica para {self.contract_type}",
                expected=f"N1={type_def['n1_strategy']}, N2={type_def['n2_strategy']}, R2={type_def['r2_merge']}",
                actual=f"N1={n1_strat}, N2={n2_strat}, R2={r2_merge}",
            )

        # Cuádruple declaración de type
        types = {
            "identity": self._get_path("identity.contract_type"),
            "method_binding": self._get_path("method_binding.contract_type"),
            "fusion_spec": self._get_path("fusion_specification.contract_type"),
            "human_answer": self._get_path("human_answer_structure.contract_type"),
        }

        all_same = len(set(types.values())) == 1
        self._add_check(
            section,
            "14.2.5",
            Severity.CRITICAL,
            all_same,
            "Los 4 contract_type son IDÉNTICOS",
            expected="Todos iguales",
            actual=types,
        )

        # Veto capability real
        self._validate_veto_capability(section)

        # Framework epistemológico completo
        self._validate_epistemological_framework(section)

        self.sections.append(section)

    def _validate_veto_capability(self, section: SectionReport):
        """Valida que el veto está realmente implementado"""
        all_methods = self._get_all_methods()

        has_zero_mult = False
        has_severe_action = False

        for method in all_methods:
            if method.get("level") == "N3-AUD":
                veto_conds = method.get("veto_conditions", {})
                for cond in veto_conds.values():
                    if cond.get("confidence_multiplier", 1.0) == 0.0:
                        has_zero_mult = True
                    if cond.get("action") in ["suppress_fact", "block_branch", "invalidate_graph"]:
                        has_severe_action = True

        self._add_check(
            section,
            "14.4.1",
            Severity.CRITICAL,
            has_zero_mult,
            "Existe al menos UN método N3 con confidence_multiplier = 0.0",
        )

        self._add_check(
            section,
            "14.4.2",
            Severity.CRITICAL,
            has_severe_action,
            "Existe al menos UN método N3 con action severa (suppress/block/invalidate)",
        )

    def _validate_epistemological_framework(self, section: SectionReport):
        """Valida framework epistemológico completo"""
        phases = self._get_path("method_binding.execution_phases", {})

        # N1 existe
        self._add_check(
            section,
            "14.5.1",
            Severity.CRITICAL,
            "phase_A_construction" in phases,
            "Existe representación de N1 (Empirismo positivista)",
        )

        # N2 existe
        self._add_check(
            section,
            "14.5.2",
            Severity.CRITICAL,
            "phase_B_computation" in phases,
            "Existe representación de N2 (Bayesianismo subjetivista)",
        )

        # N3 existe
        self._add_check(
            section,
            "14.5.3",
            Severity.CRITICAL,
            "phase_C_litigation" in phases,
            "Existe representación de N3 (Falsacionismo popperiano)",
        )

        # N4 existe (en human_answer_structure)
        has_s1 = len(self._get_path("human_answer_structure.sections", [])) > 0
        self._add_check(
            section,
            "14.5.4",
            Severity.CRITICAL,
            has_s1,
            "Existe representación de N4 (Reflexividad crítica)",
        )

        # Asimetría técnicamente implementada
        clf = self._get_path("cross_layer_fusion", {})
        has_asym = (
            "N3_to_N1" in clf
            and "asymmetry" in clf.get("N3_to_N1", {})
            and "N3_to_N2" in clf
            and "asymmetry" in clf.get("N3_to_N2", {})
        )
        self._add_check(
            section,
            "14.5.5",
            Severity.CRITICAL,
            has_asym,
            "Asimetría N3 está técnicamente implementada",
        )

    # =========================================================================
    # SECCIÓN 15: COHERENCIA SEMÁNTICA (NUEVA ADICIÓN)
    # =========================================================================

    def _normalize_tokens(self, text: str) -> list[str]:
        """
        Normaliza texto dividiendo camelCase, snake_case y espacios en tokens individuales.
        MODIFICACIÓN 1: Corrección léxica - tokens completos, no substrings.
        """
        # Dividir por snake_case
        parts = re.split(r"_+", text)
        # Dividir cada parte por camelCase
        tokens = []
        for part in parts:
            # Dividir camelCase: "extractText" -> ["extract", "Text"]
            camel_split = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", part)
            if camel_split:
                tokens.extend([t.lower() for t in camel_split])
            else:
                tokens.append(part.lower())
        # Dividir por espacios y filtrar vacíos
        final_tokens = []
        for token in tokens:
            final_tokens.extend([t for t in token.split() if t])
        return final_tokens

    def _get_scoring_modality(self) -> str | None:
        """
        Obtiene el scoring_modality del contrato desde question_context o questionnaire.
        MODIFICACIÓN 3: Alineación con scoring_modality.
        """
        # Intentar desde question_context
        qc = self._get_path("question_context", {})
        if qc and isinstance(qc, dict):
            scoring_modality = qc.get("scoring_modality")
            if scoring_modality:
                return scoring_modality

        # Intentar obtener desde questionnaire usando representative_question_id
        rep_q_id = self._get_path("identity.representative_question_id", "")
        if rep_q_id:
            try:
                import json
                from pathlib import Path

                questionnaire_path = Path(
                    "canonic_questionnaire_central/questionnaire_monolith.json"
                )
                if questionnaire_path.exists():
                    with open(questionnaire_path, encoding="utf-8") as f:
                        questionnaire = json.load(f)
                    # Buscar la pregunta en el questionnaire
                    questions = questionnaire.get("questions", [])
                    for q in questions:
                        if q.get("question_id") == rep_q_id:
                            scoring_modality = q.get("scoring_modality")
                            if scoring_modality:
                                return scoring_modality
            except Exception:
                # Si falla la carga del questionnaire, continuar sin scoring_modality
                pass

        return None

    def _section_15_semantic_coherence(self):
        """
        Detecta métodos cuya naturaleza semántica es ajena al tipo de contrato.
        Ejemplo: Un método 'analyze_sentiment' dentro de un contrato TYPE_D (Financiero).

        MODIFICACIONES IMPLEMENTADAS:
        1. Corrección léxica: tokens completos (normalización camelCase/snake_case)
        2. Separación por capa: métodos semánticos/lógicos/temporales permitidos en N1 de TYPE_D
        3. Alineación con scoring_modality: permite métodos TYPE_A/TYPE_E cuando scoring_modality lo indica
        """
        section = SectionReport("15", "Coherencia Semántica - Anti-Patterns de Dominio", 0, 0, 0, 0)

        if not self.contract_type or self.contract_type not in self.TYPE_SEMANTIC_DEFINITIONS:
            return

        semantics = self.TYPE_SEMANTIC_DEFINITIONS[self.contract_type]
        alien_keywords = semantics["alien_keywords"]
        type_name = semantics["name"]

        # MODIFICACIÓN 3: Obtener scoring_modality
        scoring_modality = self._get_scoring_modality()

        all_methods = self._get_all_methods()

        for method in all_methods:
            method_name = method.get("method_name", "")
            description = method.get("description", "")
            class_name = method.get("class_name", "")
            method_level = method.get("level", "")
            output_type = method.get("output_type", "")

            # MODIFICACIÓN 1: Normalizar tokens (camelCase, snake_case, espacios)
            method_tokens = self._normalize_tokens(method_name)
            desc_tokens = self._normalize_tokens(description)
            class_tokens = self._normalize_tokens(class_name)
            all_tokens = method_tokens + desc_tokens + class_tokens

            # Combinar texto a analizar (para compatibilidad con regex)
            full_text = f"{method_name.lower()} {description.lower()} {class_name.lower()}"

            # MODIFICACIÓN 1: Buscar palabras completas (tokens normalizados), no substrings
            found_aliens = []
            for kw in alien_keywords:
                kw_lower = kw.lower()
                # Verificar si el token completo está en la lista normalizada
                if kw_lower in all_tokens or re.search(
                    r"\b" + re.escape(kw_lower) + r"\b", full_text
                ):
                    found_aliens.append(kw)

            # MODIFICACIÓN 2: Separación explícita por capa
            # En contratos TYPE_D, permitir métodos semánticos/lógicos/temporales en N1-EMP
            # cuando son de extracción/estructuración, no decisiones financieras finales
            is_extraction_layer_n1 = (
                method_level == "N1-EMP"
                and self.contract_type == "TYPE_D"
                and output_type == "FACT"
            )

            # Detectar si es método semántico/lógico/temporal
            semantic_indicators = [
                "extract",
                "parse",
                "normalize",
                "entity",
                "structure",
                "detect",
                "identify",
                "match",
            ]
            logical_indicators = ["validate", "check", "verify", "consistency", "contradiction"]
            temporal_indicators = ["temporal", "sequence", "order", "chronological"]

            is_semantic_method = any(ind in full_text for ind in semantic_indicators)
            is_logical_method = any(ind in full_text for ind in logical_indicators)
            is_temporal_method = any(ind in full_text for ind in temporal_indicators)

            # MODIFICACIÓN 3: Alineación con scoring_modality
            # Si scoring_modality es TYPE_A o TYPE_E, permitir métodos acordes
            modality_allows_semantic = scoring_modality == "TYPE_A"
            modality_allows_logical = scoring_modality == "TYPE_E"

            # Permitir si:
            # 1. Es capa N1-EMP de TYPE_D y es extracción/estructuración (MODIFICACIÓN 2)
            # 2. O scoring_modality permite métodos semánticos/lógicos y el método responde directamente (MODIFICACIÓN 3)
            should_allow = False

            if is_extraction_layer_n1 and (
                is_semantic_method or is_logical_method or is_temporal_method
            ):
                # MODIFICACIÓN 2: Métodos de extracción/estructuración en N1 de TYPE_D
                should_allow = True

            elif (
                modality_allows_semantic
                and is_semantic_method
                and method_level in ["N1-EMP", "N2-INF"]
            ):
                # MODIFICACIÓN 3: scoring_modality TYPE_A permite métodos semánticos
                # Solo en N1/N2, no en N3 (que requiere lógica financiera estricta)
                should_allow = True

            elif (
                modality_allows_logical
                and is_logical_method
                and method_level in ["N1-EMP", "N2-INF"]
            ):
                # MODIFICACIÓN 3: scoring_modality TYPE_E permite métodos lógicos
                # Solo en N1/N2, no en N3 (que requiere lógica financiera estricta)
                should_allow = True

            # MODIFICACIÓN 4: Permitir evaluación de coherencia causal en TYPE_E cuando es validación lógica
            # La causalidad es un subtipo de relación lógica, válida cuando se usa para verificación de coherencia
            # y no como inferencia causal probabilística o explicación generativa
            is_causal_coherence_validation = (
                self.contract_type == "TYPE_E"
                and method_level == "N2-INF"
                and "causal" in found_aliens
                and any(
                    term in full_text
                    for term in [
                        "coherence",
                        "consistency",
                        "validation",
                        "verify",
                        "check",
                        "justification",
                        "logical",
                    ]
                )
            )

            # Verificar que el propósito es validación lógica, no inferencia predictiva
            is_predictive_inference = any(
                term in full_text
                for term in ["predict", "forecast", "estimate", "generate", "explain", "model"]
            )
            is_explanatory_generative = any(
                term in full_text
                for term in ["mechanism", "explanation", "why", "because", "dag", "intervention"]
            )

            if (
                is_causal_coherence_validation
                and not is_predictive_inference
                and not is_explanatory_generative
            ):
                should_allow = True

            # MODIFICACIÓN 5: Permitir métodos bayesianos con DAG en contratos TYPE_D cuando están en N2-INF
            # Los métodos bayesianos son herramientas válidas para inferencia financiera probabilística
            is_bayesian_financial_inference = (
                self.contract_type == "TYPE_D"
                and method_level == "N2-INF"
                and "dag" in found_aliens
                and any(
                    term in full_text
                    for term in [
                        "bayesian",
                        "posterior",
                        "probability",
                        "confidence",
                        "interval",
                        "financial",
                        "calculate",
                        "compute",
                    ]
                )
            )

            if is_bayesian_financial_inference:
                should_allow = True

            # Si debe permitirse y hay alien_keywords detectados, ignorar la alerta
            if should_allow and found_aliens:
                continue

            # Si se encontraron palabras clave de OTROS dominios en este método
            if found_aliens:
                # Determinar severidad:
                # HIGH: Si la palabra clave está en el NOMBRE del método (muy evidente).
                # MEDIUM: Si está solo en la descripción (podría ser parte de un proceso complejo).

                is_in_name = any(kw.lower() in method_tokens for kw in found_aliens)
                severity = Severity.HIGH if is_in_name else Severity.MEDIUM

                self._add_check(
                    section,
                    f"15.{method.get('method_name')}",
                    severity,
                    False,  # Passed = False porque es una alerta
                    f"Posible clasificación 'Contra-Natura' en TYPE_{type_name}: El método '{method.get('method_name')}' contiene términos ajenos: {', '.join(found_aliens)}.",
                    expected=f"Términos típicos de {type_name}",
                    actual=f"Contiene: {', '.join(found_aliens)}",
                    path=f"method_binding.execution_phases.{method.get('level', '?')}.methods.{method.get('method_name')}",
                )

        # Si no hubo fallos, agregar un check de paso
        if section.total_checks == 0:
            self._add_check(
                section,
                "15.0",
                Severity.LOW,
                True,
                "Coherencia semántica: No se detectaron términos ajenos al dominio.",
            )

        self.sections.append(section)

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    def _add_check(
        self,
        section: SectionReport,
        check_id: str,
        severity: Severity,
        passed: bool,
        message: str,
        expected: Any = None,
        actual: Any = None,
        path: str = None,
    ):
        """Agrega un check a la sección"""
        result = ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=severity,
            message=message,
            section=section.section_id,
            expected=expected,
            actual=actual,
            path=path,
        )

        section.total_checks += 1
        if passed:
            section.passed_checks += 1
        else:
            section.failed_checks += 1
            if severity == Severity.CRITICAL:
                section.critical_failures += 1

        section.results.append(result)

    def _path_exists(self, path: str) -> bool:
        """Verifica si existe un path en el contrato"""
        _SENTINEL = object()
        result = self._get_path(path, default=_SENTINEL)
        return result is not _SENTINEL

    def _get_path(self, path: str, default=None):
        """Obtiene valor de un path (dot notation)"""
        keys = path.split(".")
        value = self.contract
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _collect_all_provides(self) -> list[str]:
        """Recolecta todos los provides de todos los métodos"""
        provides = []
        phases = self._get_path("method_binding.execution_phases", {})
        for phase_key in ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]:
            methods = phases.get(phase_key, {}).get("methods", [])
            for method in methods:
                if "provides" in method:
                    provides.append(method["provides"])
        return provides

    def _get_phase_provides(self, phase: str) -> set[str]:
        """Obtiene provides de una fase específica"""
        phase_map = {
            "A": "phase_A_construction",
            "B": "phase_B_computation",
            "C": "phase_C_litigation",
        }
        phase_key = phase_map.get(phase)
        methods = self._get_path(f"method_binding.execution_phases.{phase_key}.methods", [])
        return set(m.get("provides", "") for m in methods if m.get("provides"))

    def _get_all_methods(self) -> list[dict]:
        """Obtiene todos los métodos de todas las fases"""
        methods = []
        phases = self._get_path("method_binding.execution_phases", {})
        for phase_key in ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]:
            methods.extend(phases.get(phase_key, {}).get("methods", []))
        return methods

    def _determine_approval(self) -> bool:
        """Determina si el contrato es aprobado"""
        # Criterios de aprobación según checklist:
        # - CORE (0-7): 100% (CERO fallos críticos)
        # - GLOBAL (14): 100%
        # - Resto: ≥95%

        core_sections = [
            s for s in self.sections if s.section_id in ["0", "1", "2", "3", "4", "5", "6", "7"]
        ]
        global_section = [s for s in self.sections if s.section_id == "14"]

        # Fallos críticos en core
        core_critical = sum(s.critical_failures for s in core_sections)
        if core_critical > 0:
            return False

        # Global debe estar 100%
        if global_section and global_section[0].pass_rate < 100.0:
            return False

        # Resto ≥95%
        other_sections = [
            s
            for s in self.sections
            if s.section_id not in ["0", "1", "2", "3", "4", "5", "6", "7", "14"]
        ]
        if other_sections:
            for section in other_sections:
                if section.pass_rate < 95.0:
                    return False

        return True


# =========================================================================
# REPORTE Y MAIN
# =========================================================================


def generate_report(validator: ContractValidator, report_path: str = None):
    """Genera el reporte de validación"""
    approved = any(
        s.critical_failures > 0
        for s in validator.sections
        if s.section_id in ["0", "1", "2", "3", "4", "5", "6", "7"]
    )
    approved = not approved  # Flip logic: if critical fails exist, not approved

    # Recalcular aprobación usando método interno (que es más exacto)
    approved = validator._determine_approval()

    report_lines = []

    # Resumen Ejecutivo
    report_lines.append("# 📋 REPORTE DE AUDITORÍA EPISTEMOLÓGICA V4")
    report_lines.append(f"**Resultado Global**: {'✅ APROBADO' if approved else '❌ RECHAZADO'}")
    report_lines.append("")

    # Tabla de resumen
    report_lines.append("## 📊 Resumen por Sección")
    report_lines.append("| Sección | Total | Pasados | Fallados | Críticos | % Aprobación |")
    report_lines.append("|---------|-------|---------|----------|----------|--------------|")

    total_checks = 0
    total_passed = 0
    total_critical = 0

    for section in validator.sections:
        total_checks += section.total_checks
        total_passed += section.passed_checks
        total_critical += section.critical_failures

        status_icon = (
            "🔴" if section.critical_failures > 0 else ("🟡" if section.pass_rate < 100 else "🟢")
        )
        report_lines.append(
            f"| {section.section_id} {section.section_name} | {section.total_checks} | {section.passed_checks} | {section.failed_checks} | {section.critical_failures} | {section.pass_rate:.1f}% {status_icon} |"
        )

    report_lines.append("")
    report_lines.append(
        f"**Total**: {total_checks} checks | {total_passed} passed | {total_checks - total_passed} failed"
    )
    report_lines.append("")

    # Detalles de fallos
    report_lines.append("## 🐛 Detalle de Fallos")
    has_failures = False

    for section in validator.sections:
        failures = [r for r in section.results if not r.passed]
        if failures:
            has_failures = True
            report_lines.append(f"\n### ❌ Sección {section.section_id}: {section.section_name}")

            for fail in failures:
                sev_emoji = (
                    "🛑"
                    if fail.severity == Severity.CRITICAL
                    else ("⚠️" if fail.severity == Severity.HIGH else "📝")
                )
                report_lines.append(
                    f"- **{sev_emoji} [{fail.check_id}]** ({fail.severity.value}) {fail.message}"
                )
                if fail.expected is not None or fail.actual is not None:
                    report_lines.append(f"  - Expected: `{fail.expected}`")
                    report_lines.append(f"  - Actual: `{fail.actual}`")
                if fail.path:
                    report_lines.append(f"  - Path: `{fail.path}`")

    if not has_failures:
        report_lines.append("✨ No se encontraron fallos. ¡Contrato perfecto!")

    # Output
    report_content = "\n".join(report_lines)

    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"💾 Reporte guardado en: {report_path}")

    return report_content


def main():
    parser = argparse.ArgumentParser(description="Validador de Contratos Epistemológicos V4")
    parser.add_argument("contract_file", help="Ruta al archivo JSON del contrato")
    parser.add_argument(
        "--strict", action="store_true", help="Modo estricto (falla en cualquier warning)"
    )
    parser.add_argument("--report", help="Ruta para guardar el reporte Markdown (ej: report.md)")

    args = parser.parse_args()

    # Cargar contrato
    try:
        with open(args.contract_file, encoding="utf-8") as f:
            contract_data = json.load(f)
    except Exception as e:
        print(f"❌ Error cargando contrato: {e}")
        sys.exit(1)

    # Ejecutar validación
    validator = ContractValidator(contract_data, strict_mode=args.strict)
    approved, sections = validator.validate_all()

    # Generar reporte
    report_md = generate_report(validator, args.report)

    # Imprimir resumen en consola
    print("-" * 80)
    print("RESULTADO FINAL:")
    if approved:
        print("✅ CONTRATO APROBADO: Cumple con los estándares epistemológicos v4.0")
        sys.exit(0)
    else:
        print("❌ CONTRATO RECHAZADO: No cumple con los estándares críticos v4.0")
        print("   Revise el reporte para detalles.")
        sys.exit(1)


if __name__ == "__main__":
    main()
