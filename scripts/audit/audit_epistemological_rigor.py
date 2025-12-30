#!/usr/bin/env python3
"""
AUDITOR EPISTEMOLÓGICO CANÓNICO
Valida clasificaciones de métodos contra taxonomías de episte_refact.md y audit_v4_rigorous.py

Reglas canónicas:
- N1-EMP: Extrae hechos brutos (extract_, parse_, mine_, chunk_) → FACT
- N2-INF: Transforma en conocimiento (analyze_, score_, calculate_, infer_) → PARAMETER
- N3-AUD: Valida/refuta (validate_, detect_, audit_, check_) → CONSTRAINT
- N4-SYN: Sintetiza narrativa (generate_report, format_*) → NARRATIVE
"""

import json
import sys
from pathlib import Path
from typing import Any
from collections import defaultdict


# Taxonomía canónica de episte_refact.md § 1.2
CANONICAL_TAXONOMIES = {
    'N1-EMP': {
        'function': 'Extraer hechos brutos',
        'epistemology': 'Empirismo positivista',
        'output_type': 'FACT',
        'fusion_behavior': 'additive',
        'phase': 'phase_A_construction',
        'name_patterns': ['extract_', 'parse_', 'mine_', 'chunk_', 'split_', 'tokenize_', 'normalize_'],
        'forbidden_words': ['calcula', 'infiere', 'evalúa', 'compara', 'analiza', 'score'],
        'requires': [],  # N1 NO debe requerir inputs upstream
        'produces': ['raw_facts'],
        'description_signals': ['extrae', 'obtiene', 'lee', 'parsea', 'identifica literalmente'],
    },
    'N2-INF': {
        'function': 'Transformar datos en conocimiento probabilístico',
        'epistemology': 'Bayesianismo subjetivista',
        'output_type': 'PARAMETER',
        'fusion_behavior': 'multiplicative',
        'phase': 'phase_B_computation',
        'name_patterns': ['analyze_', 'score_', 'calculate_', 'infer_', 'evaluate_', 'compare_',
                         'compute_', 'classify_', 'estimate_', 'determine_'],
        'required_words': ['calcula', 'infiere', 'evalúa', 'compara', 'analiza', 'transforma', 'deriva'],
        'requires': ['raw_facts', 'PreprocesadoMetadata'],  # N2 DEBE consumir N1
        'produces': ['inferences', 'inferred_parameters'],
        'modifies': ['edge_weights', 'confidence_scores'],
        'description_signals': ['calcula', 'deriva', 'infiere', 'estima', 'genera score'],
    },
    'N3-AUD': {
        'function': 'Cuestionar, validar o refutar',
        'epistemology': 'Falsacionismo popperiano',
        'output_type': 'CONSTRAINT',
        'fusion_behavior': 'gate',
        'phase': 'phase_C_litigation',
        'name_patterns': ['validate_', 'detect_', 'audit_', 'check_', 'test_', 'verify_'],
        'requires': ['raw_facts', 'inferences'],  # N3 DEBE consumir N1 Y N2
        'produces': ['validated_constraints'],
        'modulates': ['raw_facts.confidence', 'inferences.confidence'],
        'veto_required': True,  # § 5.3
        'description_signals': ['valida', 'verifica', 'detecta contradicción', 'audita', 'refuta'],
    },
    'N4-SYN': {
        'function': 'Analizar el propio proceso analítico / Síntesis narrativa',
        'epistemology': 'Reflexividad crítica',
        'output_type': 'NARRATIVE',
        'fusion_behavior': 'terminal',
        'phase': 'phase_D_synthesis',
        'name_patterns': ['generate_report', 'generate_summary', 'format_', '_format_',
                         'compose_', 'synthesize_', 'render_'],
        'requires': ['raw_facts', 'inferences', 'validated_constraints'],  # N4 consume todo
        'produces': ['narrative'],
        'description_signals': ['genera reporte', 'sintetiza', 'formatea respuesta', 'narrativa'],
    },
    'INFRASTRUCTURE': {
        'function': 'Soporte técnico sin juicio epistemológico',
        'epistemology': 'Instrumentalismo',
        'output_type': 'NONE',
        'fusion_behavior': 'none',
        'phase': 'none',
        'name_patterns': ['__init__', '__repr__', '__str__', '__hash__', '__eq__'],
        'requires': [],
        'produces': [],
    }
}


# Clases típicas de N1 (episte_refact.md líneas 126-133)
TYPICAL_N1_CLASSES = {
    'TextMiningEngine', 'IndustrialPolicyProcessor', 'CausalExtractor',
    'PDETMunicipalPlanAnalyzer', 'SemanticProcessor', 'PolicyContradictionDetector',
    'AdvancedSemanticChunker', 'MechanismPartExtractor'
}

# Clases típicas de N2 (episte_refact.md líneas 163-171)
TYPICAL_N2_CLASSES = {
    'BayesianNumericalAnalyzer', 'AdaptivePriorCalculator', 'HierarchicalGenerativeModel',
    'BayesianMechanismInference', 'TeoriaCambio', 'SemanticProcessor',
    'IndustrialPolicyProcessor', 'PolicyAnalysisEmbedder', 'EmbeddingPolicy'
}

# Clases típicas de N3 (episte_refact.md líneas 211-218)
TYPICAL_N3_CLASSES = {
    'PolicyContradictionDetector', 'FinancialAuditor', 'IndustrialGradeValidator',
    'AdvancedDAGValidator', 'BayesianCounterfactualAuditor', 'OperationalizationAuditor',
    'TemporalLogicVerifier'
}


class EpistemologicalIssue:
    """Registro de inconsistencia epistemológica."""

    def __init__(self, severity: str, issue_id: str, class_name: str, method_name: str,
                 current_level: str, expected_level: str, reason: str, evidence: dict):
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.issue_id = issue_id
        self.class_name = class_name
        self.method_name = method_name
        self.current_level = current_level
        self.expected_level = expected_level
        self.reason = reason
        self.evidence = evidence

    def __repr__(self):
        return (f"[{self.severity}] {self.issue_id}: {self.class_name}.{self.method_name} "
                f"classified as {self.current_level}, should be {self.expected_level}")


class EpistemologicalAuditor:
    """Auditor que valida clasificaciones contra taxonomía canónica."""

    def __init__(self, enriched_data: dict):
        self.data = enriched_data
        self.issues: list[EpistemologicalIssue] = []
        self.stats = defaultdict(int)

    def audit_all(self) -> tuple[list[EpistemologicalIssue], dict]:
        """Ejecuta auditoría completa."""
        print("🔍 Iniciando auditoría epistemológica contra taxonomía canónica...")
        print("=" * 80)

        for class_name, cls in self.data.items():
            if class_name in ['quality_metrics', '_pipeline_metadata']:
                continue

            methods = cls.get('methods', {})
            for method_name, method in methods.items():
                self.audit_method(class_name, method_name, method)

        return self.issues, dict(self.stats)

    def audit_method(self, class_name: str, method_name: str, method: dict):
        """Audita un método individual."""
        ec = method.get('epistemological_classification', {})
        level = ec.get('level', 'UNKNOWN')
        output_type = ec.get('output_type')
        fusion_behavior = ec.get('fusion_behavior')
        phase_assignment = ec.get('phase_assignment')

        self.stats[f'total_{level}'] += 1

        # Skip INFRASTRUCTURE
        if level == 'INFRASTRUCTURE':
            return

        # Check 1: level ↔ output_type consistency
        if level in CANONICAL_TAXONOMIES:
            expected = CANONICAL_TAXONOMIES[level]

            if output_type != expected['output_type']:
                self.issues.append(EpistemologicalIssue(
                    severity='CRITICAL',
                    issue_id='OUTPUT_TYPE_MISMATCH',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=level,
                    reason=f"output_type='{output_type}', esperado '{expected['output_type']}'",
                    evidence={'current': output_type, 'expected': expected['output_type']}
                ))

            if fusion_behavior != expected['fusion_behavior']:
                self.issues.append(EpistemologicalIssue(
                    severity='CRITICAL',
                    issue_id='FUSION_BEHAVIOR_MISMATCH',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=level,
                    reason=f"fusion_behavior='{fusion_behavior}', esperado '{expected['fusion_behavior']}'",
                    evidence={'current': fusion_behavior, 'expected': expected['fusion_behavior']}
                ))

            if phase_assignment != expected['phase']:
                self.issues.append(EpistemologicalIssue(
                    severity='HIGH',
                    issue_id='PHASE_ASSIGNMENT_MISMATCH',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=level,
                    reason=f"phase='{phase_assignment}', esperado '{expected['phase']}'",
                    evidence={'current': phase_assignment, 'expected': expected['phase']}
                ))

        # Check 2: Name pattern vs level
        self.check_name_pattern_consistency(class_name, method_name, level, ec)

        # Check 3: Dependencies (requires/produces)
        self.check_dependencies(class_name, method_name, level, ec)

        # Check 4: N3 veto conditions
        if level == 'N3-AUD':
            self.check_n3_veto_conditions(class_name, method_name, ec)

        # Check 5: Class membership consistency
        self.check_class_membership(class_name, method_name, level)

    def check_name_pattern_consistency(self, class_name: str, method_name: str,
                                      level: str, ec: dict):
        """Verifica que el patrón de nombre sea consistente con el nivel."""
        if level not in CANONICAL_TAXONOMIES:
            return

        expected_patterns = CANONICAL_TAXONOMIES[level].get('name_patterns', [])

        # Check if method name matches expected patterns
        matches_expected = any(method_name.startswith(p.rstrip('_')) or p in method_name
                              for p in expected_patterns)

        # Check if method name matches OTHER level patterns
        for other_level, taxonomy in CANONICAL_TAXONOMIES.items():
            if other_level == level or other_level == 'INFRASTRUCTURE':
                continue

            other_patterns = taxonomy.get('name_patterns', [])
            matches_other = any(method_name.startswith(p.rstrip('_')) or p in method_name
                               for p in other_patterns)

            if matches_other and not matches_expected:
                self.issues.append(EpistemologicalIssue(
                    severity='HIGH',
                    issue_id='NAME_PATTERN_MISMATCH',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=other_level,
                    reason=f"Nombre '{method_name}' sugiere {other_level} (patrones: {other_patterns}), pero está clasificado como {level}",
                    evidence={'method_name': method_name, 'expected_patterns': other_patterns}
                ))
                self.stats['name_pattern_mismatches'] += 1

    def check_dependencies(self, class_name: str, method_name: str, level: str, ec: dict):
        """Verifica que las dependencias sean correctas según nivel."""
        if level not in CANONICAL_TAXONOMIES:
            return

        expected = CANONICAL_TAXONOMIES[level]
        deps = ec.get('dependencies', {})
        requires = set(deps.get('requires', []))
        produces = set(deps.get('produces', []))

        expected_requires = set(expected.get('requires', []))
        expected_produces = set(expected.get('produces', []))

        # N1 NO debe requerir inputs
        if level == 'N1-EMP' and len(requires) > 0:
            self.issues.append(EpistemologicalIssue(
                severity='CRITICAL',
                issue_id='N1_WITH_REQUIREMENTS',
                class_name=class_name,
                method_name=method_name,
                current_level=level,
                expected_level=level,
                reason=f"N1-EMP NO debe requerir inputs, pero tiene requires={list(requires)}",
                evidence={'requires': list(requires)}
            ))

        # N2 DEBE consumir raw_facts o PreprocesadoMetadata
        if level == 'N2-INF':
            if not (requires & {'raw_facts', 'PreprocesadoMetadata'}):
                self.issues.append(EpistemologicalIssue(
                    severity='CRITICAL',
                    issue_id='N2_WITHOUT_RAW_FACTS',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=level,
                    reason=f"N2-INF DEBE consumir raw_facts o PreprocesadoMetadata, tiene requires={list(requires)}",
                    evidence={'requires': list(requires)}
                ))

        # N3 DEBE consumir raw_facts Y inferences
        if level == 'N3-AUD':
            if not ({'raw_facts', 'inferences'}.issubset(requires)):
                self.issues.append(EpistemologicalIssue(
                    severity='CRITICAL',
                    issue_id='N3_INCOMPLETE_REQUIREMENTS',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level=level,
                    reason=f"N3-AUD DEBE consumir raw_facts Y inferences, tiene requires={list(requires)}",
                    evidence={'requires': list(requires)}
                ))

        # Check produces
        if level != 'INFRASTRUCTURE' and len(produces) == 0:
            self.issues.append(EpistemologicalIssue(
                severity='HIGH',
                issue_id='NO_OUTPUT_DECLARED',
                class_name=class_name,
                method_name=method_name,
                current_level=level,
                expected_level=level,
                reason=f"Método {level} debe producir algo, pero produces está vacío",
                evidence={'produces': list(produces)}
            ))

        # N4 DEBE producir narrative
        if level == 'N4-SYN' and 'narrative' not in produces:
            self.issues.append(EpistemologicalIssue(
                severity='CRITICAL',
                issue_id='N4_WITHOUT_NARRATIVE',
                class_name=class_name,
                method_name=method_name,
                current_level=level,
                expected_level=level,
                reason=f"N4-SYN DEBE producir 'narrative', tiene produces={list(produces)}",
                evidence={'produces': list(produces)}
            ))

    def check_n3_veto_conditions(self, class_name: str, method_name: str, ec: dict):
        """Verifica que N3 tenga veto_conditions (§ 5.3)."""
        veto = ec.get('veto_conditions')

        if veto is None or (isinstance(veto, dict) and len(veto) == 0):
            self.issues.append(EpistemologicalIssue(
                severity='CRITICAL',
                issue_id='N3_WITHOUT_VETO',
                class_name=class_name,
                method_name=method_name,
                current_level='N3-AUD',
                expected_level='N3-AUD',
                reason="N3-AUD DEBE tener veto_conditions (§ 5.3)",
                evidence={'veto_conditions': veto}
            ))

    def check_class_membership(self, class_name: str, method_name: str, level: str):
        """Verifica consistencia de clase con métodos típicos."""
        # Check if class is in typical N1 but method is not N1
        if class_name in TYPICAL_N1_CLASSES and level not in ['N1-EMP', 'INFRASTRUCTURE']:
            if not method_name.startswith('_'):  # Allow private helpers
                self.issues.append(EpistemologicalIssue(
                    severity='MEDIUM',
                    issue_id='CLASS_LEVEL_INCONSISTENCY',
                    class_name=class_name,
                    method_name=method_name,
                    current_level=level,
                    expected_level='N1-EMP',
                    reason=f"Clase {class_name} es típicamente N1-EMP (extractora), pero método está en {level}",
                    evidence={'class': class_name, 'typical_level': 'N1-EMP'}
                ))


def main():
    if len(sys.argv) < 2:
        print("Uso: python audit_epistemological_rigor.py <enriched.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"ERROR: Archivo no encontrado: {filepath}")
        sys.exit(1)

    print(f"Auditando: {filepath}")
    print("=" * 80)

    enriched = json.loads(filepath.read_text(encoding='utf-8'))
    auditor = EpistemologicalAuditor(enriched)
    issues, stats = auditor.audit_all()

    # Agrupar por severidad
    by_severity = defaultdict(list)
    for issue in issues:
        by_severity[issue.severity].append(issue)

    print("\n" + "=" * 80)
    print("RESULTADOS DE AUDITORÍA")
    print("=" * 80)

    print(f"\nTotal de issues encontrados: {len(issues)}")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = len(by_severity[severity])
        if count > 0:
            print(f"  {severity}: {count}")

    # Mostrar issues críticos
    if by_severity['CRITICAL']:
        print("\n" + "🔴" * 40)
        print("ISSUES CRÍTICOS (primeros 20)")
        print("🔴" * 40)
        for i, issue in enumerate(by_severity['CRITICAL'][:20], 1):
            print(f"\n{i}. {issue}")
            print(f"   Razón: {issue.reason}")
            if issue.evidence:
                print(f"   Evidencia: {issue.evidence}")

    # Mostrar issues de alta severidad
    if by_severity['HIGH']:
        print("\n" + "🟡" * 40)
        print("ISSUES DE ALTA SEVERIDAD (primeros 20)")
        print("🟡" * 40)
        for i, issue in enumerate(by_severity['HIGH'][:20], 1):
            print(f"\n{i}. {issue}")
            print(f"   Razón: {issue.reason}")

    # Estadísticas
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS")
    print("=" * 80)
    for key, value in sorted(stats.items()):
        print(f"  {key}: {value}")

    # Exit code
    if by_severity['CRITICAL']:
        print("\n❌ AUDITORÍA FALLIDA: Issues críticos encontrados")
        sys.exit(1)
    elif by_severity['HIGH']:
        print("\n⚠️  AUDITORÍA CON ADVERTENCIAS: Issues de alta severidad encontrados")
        sys.exit(0)
    else:
        print("\n✅ AUDITORÍA EXITOSA: No se encontraron issues críticos o de alta severidad")
        sys.exit(0)


if __name__ == '__main__':
    main()
