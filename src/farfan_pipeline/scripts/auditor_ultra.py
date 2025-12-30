#!/usr/bin/env python3
"""
VALIDADOR EPISTEMOLÓGICO V4 - CONTRATOS F.A.R.F.A.N
Implementa checklist completo de 450+ validaciones con cero ambigüedad.

Uso:
    python epistemological_contract_validator_v4.py <contract.json>
    python epistemological_contract_validator_v4.py <contract.json> --strict
    python epistemological_contract_validator_v4.py <contract.json> --report=detailed.md
"""

import json
import sys
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Niveles de severidad de fallos"""
    CRITICAL = "CRÍTICO"      # Bloquea uso del contrato
    HIGH = "ALTO"             # Degrada calidad epistemológica
    MEDIUM = "MEDIO"          # Afecta usabilidad
    LOW = "BAJO"              # Mejoras estéticas


@dataclass
class ValidationResult:
    """Resultado de una validación individual"""
    check_id: str
    passed: bool
    severity: Severity
    message: str
    section: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    path: Optional[str] = None  # JSON path al campo


@dataclass
class SectionReport:
    """Reporte de una sección completa"""
    section_id: str
    section_name: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_failures: int
    results: List[ValidationResult] = field(default_factory=list)
    
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
        'TYPE_A': {
            'name': 'Semántico',
            'contracts': ['Q001', 'Q013'],
            'focus_keywords': ['coherencia narrativa', 'nlp', 'alineación temática'],
            'n1_strategy': 'semantic_corroboration',
            'n2_strategy': 'dempster_shafer',
            'r2_merge': 'semantic_triangulation',
            'dominant_classes': ['SemanticAnalyzer', 'TextMiningEngine', 'SemanticProcessor']
        },
        'TYPE_B': {
            'name': 'Bayesiano',
            'contracts': ['Q002', 'Q005', 'Q007', 'Q011', 'Q017', 'Q018', 
                         'Q020', 'Q023', 'Q024', 'Q025', 'Q027', 'Q029'],
            'focus_keywords': ['significancia estadística', 'priors', 'probabilístico'],
            'n1_strategy': 'concat',
            'n2_strategy': 'bayesian_update',
            'r2_merge': 'bayesian_update',
            'dominant_classes': ['BayesianNumericalAnalyzer', 'AdaptivePriorCalculator', 
                               'HierarchicalGenerativeModel', 'BayesianMechanismInference']
        },
        'TYPE_C': {
            'name': 'Causal',
            'contracts': ['Q008', 'Q016', 'Q026', 'Q030'],
            'focus_keywords': ['topología', 'dags', 'grafos', 'causal'],
            'n1_strategy': 'graph_construction',
            'n2_strategy': 'topological_overlay',
            'r2_merge': 'topological_overlay',
            'dominant_classes': ['CausalExtractor', 'TeoriaCambio', 'AdvancedDAGValidator']
        },
        'TYPE_D': {
            'name': 'Financiero',
            'contracts': ['Q003', 'Q004', 'Q006', 'Q009', 'Q012', 
                         'Q015', 'Q021', 'Q022'],
            'focus_keywords': ['suficiencia presupuestal', 'financiero', 'presupuesto'],
            'n1_strategy': 'concat',
            'n2_strategy': 'weighted_mean',
            'r2_merge': 'weighted_mean',
            'dominant_classes': ['FinancialAuditor', 'PDETMunicipalPlanAnalyzer']
        },
        'TYPE_E': {
            'name': 'Lógico',
            'contracts': ['Q010', 'Q014', 'Q019', 'Q028'],
            'focus_keywords': ['contradicciones', 'consistencia lógica', 'complementariedad'],
            'n1_strategy': 'concat',
            'n2_strategy': 'weighted_mean',
            'r2_merge': 'weighted_mean',
            'dominant_classes': ['PolicyContradictionDetector', 'IndustrialGradeValidator', 
                               'OperationalizationAuditor']
        }
    }
    
    # Patrones de nombres para clasificación de métodos
    N1_PATTERNS = ['extract_', 'parse_', 'mine_', 'chunk_']
    N2_PATTERNS = ['analyze_', 'score_', 'calculate_', 'infer_', 'evaluate_', 'compare_']
    N3_PATTERNS = ['validate_', 'detect_', 'audit_', 'check_', 'test_', 'verify_']
    
    # Vocabulario prohibido por nivel
    N1_FORBIDDEN_WORDS = ['calcula', 'infiere', 'evalúa', 'compara', 'analiza', 'score']
    N2_INFERENTIAL_REQUIRED = ['calcula', 'infiere', 'evalúa', 'compara', 'analiza', 'transforma', 'deriva']
    
    def __init__(self, contract: Dict, strict_mode: bool = False):
        self.contract = contract
        self.strict_mode = strict_mode
        self.results: List[ValidationResult] = []
        self.sections: List[SectionReport] = []
        self.contract_type: Optional[str] = None
        
    def validate_all(self) -> Tuple[bool, List[SectionReport]]:
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
        
        # Sección 11: Prohibiciones
        self._section_11_prohibitions()
        
        # Sección 12: Validación Matemática
        self._section_12_mathematical()
        
        # Sección 14: Coherencia Global (Auditoría Final)
        self._section_14_global_coherence()
        
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
                path=path
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
            print(f"❌ FALLO CRÍTICO en Pre-validación: {section.critical_failures} campos obligatorios faltan")
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
            section, "1.1.1", Severity.CRITICAL,
            contract_type in self.TYPE_DEFINITIONS,
            f"contract_type es válido (TYPE_A/B/C/D/E)",
            expected="TYPE_A|TYPE_B|TYPE_C|TYPE_D|TYPE_E",
            actual=contract_type,
            path="identity.contract_type"
        )
        
        # 1.1.2: contract_type_name existe
        self._add_check(
            section, "1.1.2", Severity.HIGH,
            self._path_exists("identity.contract_type_name"),
            "identity.contract_type_name existe",
            path="identity.contract_type_name"
        )
        
        # 1.1.3: contract_type_focus existe
        self._add_check(
            section, "1.1.3", Severity.HIGH,
            self._path_exists("identity.contract_type_focus"),
            "identity.contract_type_focus existe",
            path="identity.contract_type_focus"
        )
        
        # 1.1.4: contract_version es epistemológica
        version = self._get_path("identity.contract_version", "")
        self._add_check(
            section, "1.1.4", Severity.CRITICAL,
            "4.0" in version or "epistemological" in version.lower(),
            "contract_version es 4.0.0-epistemological o contiene 'epistemological'",
            expected="4.0.0-epistemological",
            actual=version,
            path="identity.contract_version"
        )
        
        # Validaciones 1.2.X: Correspondencia con tabla PARTE I
        if contract_type and contract_type in self.TYPE_DEFINITIONS:
            type_def = self.TYPE_DEFINITIONS[contract_type]
            
            # 1.2.X: Nombre correcto
            type_name = self._get_path("identity.contract_type_name", "")
            self._add_check(
                section, f"1.2.{contract_type}_name", Severity.HIGH,
                type_name == type_def['name'],
                f"contract_type_name = '{type_def['name']}' para {contract_type}",
                expected=type_def['name'],
                actual=type_name,
                path="identity.contract_type_name"
            )
            
            # 1.2.X: Focus contiene keywords
            focus = self._get_path("identity.contract_type_focus", "").lower()
            has_keyword = any(kw in focus for kw in type_def['focus_keywords'])
            self._add_check(
                section, f"1.2.{contract_type}_focus", Severity.HIGH,
                has_keyword,
                f"contract_type_focus contiene keyword esperado para {contract_type}",
                expected=f"Alguno de: {type_def['focus_keywords']}",
                actual=focus,
                path="identity.contract_type_focus"
            )
            
            # 1.2.X: representative_question_id en lista correcta
            rep_q = self._get_path("identity.representative_question_id", "")
            self._add_check(
                section, f"1.2.{contract_type}_contract", Severity.HIGH,
                rep_q in type_def['contracts'],
                f"representative_question_id pertenece a contratos de {contract_type}",
                expected=f"Uno de: {type_def['contracts']}",
                actual=rep_q,
                path="identity.representative_question_id"
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
            section, "2.1.1", Severity.CRITICAL,
            orch_mode == "epistemological_pipeline",
            "orchestration_mode = 'epistemological_pipeline'",
            expected="epistemological_pipeline",
            actual=orch_mode,
            path="method_binding.orchestration_mode"
        )
        
        self._add_check(
            section, "2.1.2", Severity.CRITICAL,
            orch_mode != "multi_method_pipeline",
            "orchestration_mode NO es 'multi_method_pipeline' (v3 prohibido)",
            actual=orch_mode
        )
        
        mb_type = self._get_path("method_binding.contract_type")
        self._add_check(
            section, "2.1.3", Severity.CRITICAL,
            mb_type == self.contract_type,
            "method_binding.contract_type = identity.contract_type (IGUALDAD ESTRICTA)",
            expected=self.contract_type,
            actual=mb_type
        )
        
        # 2.2: Existencia de fases
        self._add_check(
            section, "2.2.1", Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_A_construction"),
            "Existe phase_A_construction"
        )
        
        self._add_check(
            section, "2.2.2", Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_B_computation"),
            "Existe phase_B_computation"
        )
        
        self._add_check(
            section, "2.2.3", Severity.CRITICAL,
            self._path_exists("method_binding.execution_phases.phase_C_litigation"),
            "Existe phase_C_litigation"
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
        self._add_check(section, "2.3.1", Severity.CRITICAL,
                       phase_a.get("level") == "N1",
                       "phase_A.level = 'N1'")
        
        self._add_check(section, "2.3.2", Severity.HIGH,
                       "empíric" in phase_a.get("level_name", "").lower() or 
                       "base empírica" in phase_a.get("level_name", "").lower(),
                       "phase_A.level_name contiene 'Empírico' o 'Base Empírica'")
        
        self._add_check(section, "2.3.3", Severity.HIGH,
                       "empirismo positivista" in phase_a.get("epistemology", "").lower(),
                       "phase_A.epistemology contiene 'Empirismo positivista'")
        
        methods = phase_a.get("methods", [])
        self._add_check(section, "2.3.4", Severity.CRITICAL,
                       len(methods) > 0,
                       "phase_A.methods es array no vacío",
                       actual=len(methods))
        
        self._add_check(section, "2.3.5", Severity.CRITICAL,
                       phase_a.get("dependencies") == [],
                       "phase_A.dependencies = [] (array vacío - N1 no depende)",
                       expected=[],
                       actual=phase_a.get("dependencies"))
        
        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n1_method(section, method, idx)
    
    def _validate_n1_method(self, section: SectionReport, method: Dict, idx: int):
        """Valida un método individual de N1"""
        prefix = f"2.4.{idx}"
        
        # Campos obligatorios
        for field in ["class_name", "method_name", "mother_file", "provides", 
                     "description", "classification_rationale"]:
            self._add_check(section, f"{prefix}.{field}", Severity.CRITICAL,
                           field in method and method[field],
                           f"Método N1[{idx}] tiene campo '{field}' no vacío")
        
        # Level exacto
        self._add_check(section, f"{prefix}.level", Severity.CRITICAL,
                       method.get("level") == "N1-EMP",
                       f"Método N1[{idx}].level = 'N1-EMP' (EXACTO)",
                       expected="N1-EMP", actual=method.get("level"))
        
        # Output type
        self._add_check(section, f"{prefix}.output", Severity.CRITICAL,
                       method.get("output_type") == "FACT",
                       f"Método N1[{idx}].output_type = 'FACT'",
                       expected="FACT", actual=method.get("output_type"))
        
        # Fusion behavior
        self._add_check(section, f"{prefix}.fusion", Severity.CRITICAL,
                       method.get("fusion_behavior") == "additive",
                       f"Método N1[{idx}].fusion_behavior = 'additive'",
                       expected="additive", actual=method.get("fusion_behavior"))
        
        # Requires vacío
        self._add_check(section, f"{prefix}.requires", Severity.CRITICAL,
                       method.get("requires") == [],
                       f"Método N1[{idx}].requires = [] (N1 no depende)",
                       expected=[], actual=method.get("requires"))
        
        # Rationale referencia guía
        rationale = method.get("classification_rationale", "")
        self._add_check(section, f"{prefix}.rationale", Severity.HIGH,
                       "PARTE II" in rationale or "Sección 2.2" in rationale,
                       f"Método N1[{idx}] classification_rationale referencia 'PARTE II' o 'Sección 2.2'")
        
        # Patrón de nombre
        method_name = method.get("method_name", "")
        has_pattern = any(pattern in method_name for pattern in self.N1_PATTERNS)
        self._add_check(section, f"{prefix}.pattern", Severity.HIGH,
                       has_pattern,
                       f"Método N1[{idx}].method_name contiene patrón N1 (extract_, parse_, mine_, chunk_)",
                       actual=method_name)
        
        # Vocabulario prohibido en description
        desc = method.get("description", "").lower()
        has_forbidden = any(word in desc for word in self.N1_FORBIDDEN_WORDS)
        self._add_check(section, f"{prefix}.vocab", Severity.HIGH,
                       not has_forbidden,
                       f"Método N1[{idx}].description NO contiene vocabulario inferencial prohibido",
                       actual=desc)
    
    def _validate_phase_b(self, section: SectionReport):
        """Valida Phase B (N2-INF)"""
        phase_b = self._get_path("method_binding.execution_phases.phase_B_computation", {})
        
        # Metadata
        self._add_check(section, "2.5.1", Severity.CRITICAL,
                       phase_b.get("level") == "N2",
                       "phase_B.level = 'N2'")
        
        self._add_check(section, "2.5.3", Severity.HIGH,
                       "bayesianismo" in phase_b.get("epistemology", "").lower() or
                       "creencias actualizables" in phase_b.get("epistemology", "").lower(),
                       "phase_B.epistemology contiene 'Bayesianismo' o 'creencias actualizables'")
        
        methods = phase_b.get("methods", [])
        self._add_check(section, "2.5.4", Severity.CRITICAL,
                       len(methods) > 0,
                       "phase_B.methods es array no vacío")
        
        deps = phase_b.get("dependencies", [])
        self._add_check(section, "2.5.5", Severity.CRITICAL,
                       "phase_A_construction" in deps,
                       "phase_B.dependencies contiene 'phase_A_construction'",
                       actual=deps)
        
        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n2_method(section, method, idx)
    
    def _validate_n2_method(self, section: SectionReport, method: Dict, idx: int):
        """Valida un método individual de N2"""
        prefix = f"2.6.{idx}"
        
        # Level
        self._add_check(section, f"{prefix}.level", Severity.CRITICAL,
                       method.get("level") == "N2-INF",
                       f"Método N2[{idx}].level = 'N2-INF'",
                       expected="N2-INF", actual=method.get("level"))
        
        # Output type
        self._add_check(section, f"{prefix}.output", Severity.CRITICAL,
                       method.get("output_type") == "PARAMETER",
                       f"Método N2[{idx}].output_type = 'PARAMETER'",
                       expected="PARAMETER", actual=method.get("output_type"))
        
        # Fusion behavior
        self._add_check(section, f"{prefix}.fusion", Severity.CRITICAL,
                       method.get("fusion_behavior") == "multiplicative",
                       f"Método N2[{idx}].fusion_behavior = 'multiplicative'")
        
        # Requires no vacío
        requires = method.get("requires", [])
        self._add_check(section, f"{prefix}.requires", Severity.CRITICAL,
                       len(requires) > 0 and "raw_facts" in str(requires).lower(),
                       f"Método N2[{idx}].requires existe y contiene 'raw_facts'",
                       actual=requires)
        
        # Modifies existe
        modifies = method.get("modifies", [])
        self._add_check(section, f"{prefix}.modifies", Severity.HIGH,
                       len(modifies) > 0,
                       f"Método N2[{idx}].modifies existe y no está vacío",
                       actual=modifies)
        
        # Vocabulario inferencial en description
        desc = method.get("description", "").lower()
        has_inferential = any(word in desc for word in self.N2_INFERENTIAL_REQUIRED)
        self._add_check(section, f"{prefix}.vocab", Severity.HIGH,
                       has_inferential,
                       f"Método N2[{idx}].description contiene vocabulario inferencial",
                       actual=desc)
    
    def _validate_phase_c(self, section: SectionReport):
        """Valida Phase C (N3-AUD)"""
        phase_c = self._get_path("method_binding.execution_phases.phase_C_litigation", {})
        
        # Metadata
        self._add_check(section, "2.7.1", Severity.CRITICAL,
                       phase_c.get("level") == "N3",
                       "phase_C.level = 'N3'")
        
        self._add_check(section, "2.7.3", Severity.HIGH,
                       "falsacionismo" in phase_c.get("epistemology", "").lower() or
                       "popperiano" in phase_c.get("epistemology", "").lower(),
                       "phase_C.epistemology contiene 'Falsacionismo popperiano'")
        
        methods = phase_c.get("methods", [])
        self._add_check(section, "2.7.4", Severity.CRITICAL,
                       len(methods) > 0,
                       "phase_C.methods es array no vacío")
        
        deps = phase_c.get("dependencies", [])
        self._add_check(section, "2.7.5", Severity.CRITICAL,
                       "phase_A_construction" in deps and "phase_B_computation" in deps,
                       "phase_C.dependencies contiene phase_A Y phase_B",
                       actual=deps)
        
        # Asimetría explícita
        asym = phase_c.get("asymmetry_principle", "")
        self._add_check(section, "2.7.6", Severity.CRITICAL,
                       "asymmetry_principle" in phase_c,
                       "phase_C tiene campo asymmetry_principle")
        
        self._add_check(section, "2.7.7", Severity.CRITICAL,
                       "N3 can invalidate" in asym and "CANNOT invalidate N3" in asym,
                       "asymmetry_principle declara asimetría explícitamente",
                       actual=asym)
        
        # Validar cada método
        for idx, method in enumerate(methods):
            self._validate_n3_method(section, method, idx)
    
    def _validate_n3_method(self, section: SectionReport, method: Dict, idx: int):
        """Valida un método individual de N3"""
        prefix = f"2.8.{idx}"
        
        # Level
        self._add_check(section, f"{prefix}.level", Severity.CRITICAL,
                       method.get("level") == "N3-AUD",
                       f"Método N3[{idx}].level = 'N3-AUD'",
                       expected="N3-AUD", actual=method.get("level"))
        
        # Output type
        self._add_check(section, f"{prefix}.output", Severity.CRITICAL,
                       method.get("output_type") == "CONSTRAINT",
                       f"Método N3[{idx}].output_type = 'CONSTRAINT'",
                       expected="CONSTRAINT", actual=method.get("output_type"))
        
        # Fusion behavior
        self._add_check(section, f"{prefix}.fusion", Severity.CRITICAL,
                       method.get("fusion_behavior") == "gate",
                       f"Método N3[{idx}].fusion_behavior = 'gate'")
        
        # Requires ambos niveles
        requires = method.get("requires", [])
        has_both = any("fact" in str(r).lower() for r in requires) and \
                   any("infer" in str(r).lower() for r in requires)
        self._add_check(section, f"{prefix}.requires", Severity.CRITICAL,
                       has_both,
                       f"Método N3[{idx}].requires contiene raw_facts Y inferences")
        
        # Veto conditions
        veto = method.get("veto_conditions", {})
        self._add_check(section, f"{prefix}.veto_exists", Severity.CRITICAL,
                       len(veto) > 0,
                       f"Método N3[{idx}] tiene veto_conditions no vacío",
                       actual=len(veto))
        
        # Validar al menos una condición
        if veto:
            has_valid_condition = False
            has_severe_veto = False
            for cond_name, cond in veto.items():
                if all(k in cond for k in ["trigger", "action", "scope", "confidence_multiplier"]):
                    has_valid_condition = True
                    if cond.get("confidence_multiplier", 1.0) <= 0.5:
                        has_severe_veto = True
            
            self._add_check(section, f"{prefix}.veto_valid", Severity.CRITICAL,
                           has_valid_condition,
                           f"Método N3[{idx}] tiene al menos UNA veto_condition completa")
            
            self._add_check(section, f"{prefix}.veto_severe", Severity.HIGH,
                           has_severe_veto,
                           f"Método N3[{idx}] tiene al menos UNA condición severa (multiplier ≤ 0.5)")
    
    def _validate_method_counts(self, section: SectionReport):
        """Valida integridad de conteos"""
        phases = self._get_path("method_binding.execution_phases", {})
        phase_a_count = len(phases.get("phase_A_construction", {}).get("methods", []))
        phase_b_count = len(phases.get("phase_B_computation", {}).get("methods", []))
        phase_c_count = len(phases.get("phase_C_litigation", {}).get("methods", []))
        
        declared_count = self._get_path("method_binding.method_count", 0)
        actual_count = phase_a_count + phase_b_count + phase_c_count
        
        self._add_check(section, "2.9.1", Severity.CRITICAL,
                       declared_count == actual_count,
                       f"method_count = suma de métodos en fases",
                       expected=actual_count,
                       actual=declared_count)
        
        # Unicidad de provides
        all_provides = self._collect_all_provides()
        self._add_check(section, "2.9.2", Severity.CRITICAL,
                       len(all_provides) == len(set(all_provides)),
                       "Ningún 'provides' se repite entre fases (unicidad)",
                       actual=f"{len(set(all_provides))} únicos de {len(all_provides)} total")
        
        self._add_check(section, "2.9.3", Severity.HIGH,
                       actual_count >= 3,
                       "method_count ≥ 3 (al menos un método por fase)",
                       actual=actual_count)
    
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
            self._add_check(section, f"3.1.{type_name}", Severity.CRITICAL,
                           type_name in ts,
                           f"type_system.{type_name} existe")
        
        # FACT
        fact = ts.get("FACT", {})
        self._add_check(section, "3.2.1", Severity.CRITICAL,
                       fact.get("origin_level") == "N1",
                       "FACT.origin_level = 'N1'")
        self._add_check(section, "3.2.2", Severity.CRITICAL,
                       fact.get("fusion_operation") == "graph_node_addition",
                       "FACT.fusion_operation = 'graph_node_addition'")
        self._add_check(section, "3.2.3", Severity.CRITICAL,
                       fact.get("merge_behavior") == "additive",
                       "FACT.merge_behavior = 'additive'")
        self._add_check(section, "3.2.4", Severity.HIGH,
                       fact.get("symbol") == "⊕",
                       "FACT.symbol = '⊕'")
        
        # PARAMETER
        param = ts.get("PARAMETER", {})
        self._add_check(section, "3.3.1", Severity.CRITICAL,
                       param.get("origin_level") == "N2",
                       "PARAMETER.origin_level = 'N2'")
        self._add_check(section, "3.3.2", Severity.CRITICAL,
                       param.get("fusion_operation") == "edge_weight_modification",
                       "PARAMETER.fusion_operation = 'edge_weight_modification'")
        self._add_check(section, "3.3.3", Severity.CRITICAL,
                       param.get("merge_behavior") == "multiplicative",
                       "PARAMETER.merge_behavior = 'multiplicative'")
        
        # CONSTRAINT
        const = ts.get("CONSTRAINT", {})
        self._add_check(section, "3.4.1", Severity.CRITICAL,
                       const.get("origin_level") == "N3",
                       "CONSTRAINT.origin_level = 'N3'")
        self._add_check(section, "3.4.2", Severity.CRITICAL,
                       const.get("fusion_operation") == "branch_filtering",
                       "CONSTRAINT.fusion_operation = 'branch_filtering'")
        self._add_check(section, "3.4.3", Severity.CRITICAL,
                       const.get("merge_behavior") == "gate",
                       "CONSTRAINT.merge_behavior = 'gate'")
        
        # NARRATIVE
        narr = ts.get("NARRATIVE", {})
        self._add_check(section, "3.5.1", Severity.CRITICAL,
                       narr.get("origin_level") == "N4",
                       "NARRATIVE.origin_level = 'N4'")
        self._add_check(section, "3.5.2", Severity.CRITICAL,
                       narr.get("fusion_operation") == "synthesis",
                       "NARRATIVE.fusion_operation = 'synthesis'")
        self._add_check(section, "3.5.3", Severity.CRITICAL,
                       narr.get("merge_behavior") == "terminal",
                       "NARRATIVE.merge_behavior = 'terminal'")
    
    def _validate_assembly_rules(self, section: SectionReport):
        """Valida assembly_rules"""
        rules = self._get_path("evidence_assembly.assembly_rules", [])
        
        # Exactamente 4
        self._add_check(section, "3.6.2", Severity.CRITICAL,
                       len(rules) == 4,
                       "assembly_rules tiene EXACTAMENTE 4 reglas",
                       expected=4, actual=len(rules))
        
        if len(rules) != 4:
            return
        
        # IDs correctos
        for i in range(4):
            self._add_check(section, f"3.6.{i+3}", Severity.HIGH,
                           rules[i].get("rule_id", "").startswith(f"R{i+1}_"),
                           f"Regla [{i}].rule_id comienza con 'R{i+1}_'",
                           actual=rules[i].get("rule_id"))
        
        # R1: Empirical Basis
        self._validate_rule_r1(section, rules[0])
        
        # R2: Correspondencia con tipo
        self._validate_rule_r2(section, rules[1])
        
        # R3: Robustness Gate
        self._validate_rule_r3(section, rules[2])
        
        # R4: Synthesis
        self._validate_rule_r4(section, rules[3])
    
    def _validate_rule_r1(self, section: SectionReport, r1: Dict):
        """Valida R1 específicamente"""
        self._add_check(section, "3.7.1", Severity.CRITICAL,
                       r1.get("rule_type") == "empirical_basis",
                       "R1.rule_type = 'empirical_basis'")
        
        self._add_check(section, "3.7.5", Severity.CRITICAL,
                       r1.get("output_type") == "FACT",
                       "R1.output_type = 'FACT'")
        
        # Cobertura 100% de Phase A
        r1_sources = set(r1.get("sources", []))
        phase_a_provides = self._get_phase_provides("A")
        
        self._add_check(section, "3.7.8", Severity.CRITICAL,
                       len(r1_sources) == len(phase_a_provides),
                       "R1.sources tiene mismo count que Phase A",
                       expected=len(phase_a_provides),
                       actual=len(r1_sources))
        
        missing = phase_a_provides - r1_sources
        self._add_check(section, "3.7.9", Severity.CRITICAL,
                       len(missing) == 0,
                       "TODOS los provides de Phase A están en R1.sources",
                       actual=f"Faltan: {missing}" if missing else "Cobertura 100%")
    
    def _validate_rule_r2(self, section: SectionReport, r2: Dict):
        """Valida R2 según tipo de contrato"""
        self._add_check(section, "3.8.3", Severity.CRITICAL,
                       r2.get("output_type") == "PARAMETER",
                       "R2.output_type = 'PARAMETER'")
        
        # Cobertura Phase B
        r2_sources = set(r2.get("sources", []))
        phase_b_provides = self._get_phase_provides("B")
        
        missing = phase_b_provides - r2_sources
        self._add_check(section, "3.8.6", Severity.CRITICAL,
                       len(missing) == 0,
                       "TODOS los provides de Phase B están en R2.sources",
                       actual=f"Faltan: {missing}" if missing else "Cobertura 100%")
        
        # Validación específica por tipo
        if self.contract_type == "TYPE_A":
            self._add_check(section, "3.8.8", Severity.CRITICAL,
                           r2.get("merge_strategy") == "semantic_triangulation",
                           "R2.merge_strategy = 'semantic_triangulation' (TYPE_A)",
                           expected="semantic_triangulation",
                           actual=r2.get("merge_strategy"))
        
        elif self.contract_type == "TYPE_B":
            self._add_check(section, "3.8.12", Severity.CRITICAL,
                           r2.get("merge_strategy") == "bayesian_update",
                           "R2.merge_strategy = 'bayesian_update' (TYPE_B)",
                           expected="bayesian_update",
                           actual=r2.get("merge_strategy"))
        
        elif self.contract_type == "TYPE_C":
            self._add_check(section, "3.8.15", Severity.CRITICAL,
                           r2.get("merge_strategy") == "topological_overlay",
                           "R2.merge_strategy = 'topological_overlay' (TYPE_C)",
                           expected="topological_overlay",
                           actual=r2.get("merge_strategy"))
        
        elif self.contract_type in ["TYPE_D", "TYPE_E"]:
            self._add_check(section, "3.8.18", Severity.CRITICAL,
                           r2.get("merge_strategy") == "weighted_mean",
                           f"R2.merge_strategy = 'weighted_mean' ({self.contract_type})",
                           expected="weighted_mean",
                           actual=r2.get("merge_strategy"))
    
    def _validate_rule_r3(self, section: SectionReport, r3: Dict):
        """Valida R3 - veto gate universal"""
        self._add_check(section, "3.9.2", Severity.CRITICAL,
                       r3.get("merge_strategy") == "veto_gate",
                       "R3.merge_strategy = 'veto_gate' (UNIVERSAL)",
                       expected="veto_gate",
                       actual=r3.get("merge_strategy"))
        
        self._add_check(section, "3.9.3", Severity.CRITICAL,
                       r3.get("output_type") == "CONSTRAINT",
                       "R3.output_type = 'CONSTRAINT'")
        
        # Cobertura Phase C
        r3_sources = set(r3.get("sources", []))
        phase_c_provides = self._get_phase_provides("C")
        
        missing = phase_c_provides - r3_sources
        self._add_check(section, "3.9.6", Severity.CRITICAL,
                       len(missing) == 0,
                       "TODOS los provides de Phase C están en R3.sources",
                       actual=f"Faltan: {missing}" if missing else "Cobertura 100%")
        
        # Gate logic
        gate_logic = r3.get("gate_logic", {})
        self._add_check(section, "3.9.8", Severity.CRITICAL,
                       len(gate_logic) > 0,
                       "R3 tiene gate_logic no vacío")
        
        self._add_check(section, "3.9.9", Severity.HIGH,
                       len(gate_logic) >= 2,
                       "gate_logic tiene al menos 2 condiciones",
                       actual=len(gate_logic))
        
        # Al menos una condición severa
        has_severe = any(
            cond.get("confidence_multiplier", 1.0) < 0.5 
            for cond in gate_logic.values()
        )
        self._add_check(section, "3.9.12", Severity.CRITICAL,
                       has_severe,
                       "Al menos UNA condición tiene confidence_multiplier < 0.5")
    
    def _validate_rule_r4(self, section: SectionReport, r4: Dict):
        """Valida R4 - synthesis universal"""
        self._add_check(section, "3.10.1", Severity.CRITICAL,
                       r4.get("rule_type") == "synthesis",
                       "R4.rule_type = 'synthesis'")
        
        self._add_check(section, "3.10.5", Severity.CRITICAL,
                       r4.get("merge_strategy") == "carver_doctoral_synthesis",
                       "R4.merge_strategy = 'carver_doctoral_synthesis'",
                       expected="carver_doctoral_synthesis",
                       actual=r4.get("merge_strategy"))
        
        self._add_check(section, "3.10.6", Severity.CRITICAL,
                       r4.get("output_type") == "NARRATIVE",
                       "R4.output_type = 'NARRATIVE'")
    
    # =========================================================================
    # SECCIÓN 4: FUSION SPECIFICATION
    # =========================================================================
    
    def _section_4_fusion_specification(self):
        """Validación de fusion_specification"""
        section = SectionReport("4", "Fusion Specification - Estrategias por Nivel", 0, 0, 0, 0)
        
        fs_type = self._get_path("fusion_specification.contract_type")
        self._add_check(section, "4.1.1", Severity.CRITICAL,
                       fs_type == self.contract_type,
                       "fusion_specification.contract_type = identity.contract_type",
                       expected=self.contract_type,
                       actual=fs_type)
        
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
            self._add_check(section, f"4.3.{level}", Severity.CRITICAL,
                           level in ls,
                           f"level_strategies.{level} existe")
        
        # N1 strategy según tipo
        n1_strat = ls.get("N1_fact_fusion", {}).get("strategy")
        if self.contract_type and self.contract_type in self.TYPE_DEFINITIONS:
            expected_n1 = self.TYPE_DEFINITIONS[self.contract_type]['n1_strategy']
            self._add_check(section, "4.4.2", Severity.CRITICAL,
                           n1_strat == expected_n1,
                           f"N1_fact_fusion.strategy = '{expected_n1}' para {self.contract_type}",
                           expected=expected_n1,
                           actual=n1_strat)
        
        # N2 strategy según tipo
        n2_strat = ls.get("N2_parameter_fusion", {}).get("strategy")
        if self.contract_type and self.contract_type in self.TYPE_DEFINITIONS:
            expected_n2 = self.TYPE_DEFINITIONS[self.contract_type]['n2_strategy']
            self._add_check(section, "4.5.3", Severity.CRITICAL,
                           n2_strat == expected_n2,
                           f"N2_parameter_fusion.strategy = '{expected_n2}' para {self.contract_type}",
                           expected=expected_n2,
                           actual=n2_strat)
        
        # N3 strategy UNIVERSAL
        n3_strat = ls.get("N3_constraint_fusion", {}).get("strategy")
        self._add_check(section, "4.6.1", Severity.CRITICAL,
                       n3_strat == "veto_gate",
                       "N3_constraint_fusion.strategy = 'veto_gate' (UNIVERSAL)",
                       expected="veto_gate",