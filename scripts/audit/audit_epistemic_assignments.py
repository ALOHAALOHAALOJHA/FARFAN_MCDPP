#!/usr/bin/env python3
"""
AUDITOR DE ASIGNACIONES EPISTEMOLÓGICAS Q001-Q030
Valida EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json contra episte_refact.md

Autor: AI Agent (PythonGod Trinity Mode)
Fecha: 2025-12-31
Versión: 1.0.0

Uso:
    python audit_epistemic_assignments.py <assignments.json>
    python audit_epistemic_assignments.py --generate-report
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum


class Severity(Enum):
    CRITICAL = "🔴 CRÍTICO"
    HIGH = "🟠 ALTO"
    MEDIUM = "🟡 MEDIO"
    LOW = "🟢 BAJO"


@dataclass
class Issue:
    question_id: str
    severity: Severity
    category: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class AuditReport:
    total_questions: int = 0
    questions_audited: int = 0
    issues: List[Issue] = field(default_factory=list)
    passed_checks: int = 0
    failed_checks: int = 0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.MEDIUM)
    
    @property
    def compliance_percent(self) -> float:
        total = self.passed_checks + self.failed_checks
        return (self.passed_checks / total * 100) if total > 0 else 0.0


class EpistemicAssignmentAuditor:
    """Auditor principal para asignaciones epistemológicas"""
    
    # TYPE definitions from episte_refact.md Section 2.2
    MANDATORY_METHODS = {
        'TYPE_A': {
            'N2': ['DempsterShaferCombinator'],
            'N3': ['ContradictionDominator']
        },
        'TYPE_B': {
            'N2': ['BayesianUpdater'],
            'N3': ['StatisticalGateAuditor']
        },
        'TYPE_C': {
            'N2': ['DAGCycleDetector'],
            'N3': ['DAGCycleDetector.veto_on_cycle']
        },
        'TYPE_D': {
            'N2': ['FinancialAggregator.normalize'],
            'N3': ['FiscalSustainabilityValidator']
        },
        'TYPE_E': {
            'N2': ['LogicalConsistencyChecker'],  # with MIN
            'N3': ['ContradictionDominator']
        }
    }
    
    EXPECTED_TYPES = {
        'Q001': 'TYPE_A', 'Q013': 'TYPE_A',
        'Q002': 'TYPE_B', 'Q005': 'TYPE_B', 'Q007': 'TYPE_B', 'Q011': 'TYPE_B',
        'Q017': 'TYPE_B', 'Q018': 'TYPE_B', 'Q020': 'TYPE_B', 'Q023': 'TYPE_B',
        'Q024': 'TYPE_B', 'Q025': 'TYPE_B', 'Q027': 'TYPE_B', 'Q029': 'TYPE_B',
        'Q008': 'TYPE_C', 'Q016': 'TYPE_C', 'Q026': 'TYPE_C', 'Q030': 'TYPE_C',
        'Q003': 'TYPE_D', 'Q004': 'TYPE_D', 'Q006': 'TYPE_D', 'Q009': 'TYPE_D',
        'Q012': 'TYPE_D', 'Q015': 'TYPE_D', 'Q021': 'TYPE_D', 'Q022': 'TYPE_D',
        'Q010': 'TYPE_E', 'Q014': 'TYPE_E', 'Q019': 'TYPE_E', 'Q028': 'TYPE_E'
    }
    
    def __init__(self, assignments_data: Dict):
        self.data = assignments_data
        self.report = AuditReport()
    
    def audit_all(self) -> AuditReport:
        """Ejecuta auditoría completa"""
        print("🔍 Iniciando auditoría de asignaciones epistemológicas...")
        print("=" * 80)
        
        assignments = self.data.get('assignments', {})
        self.report.total_questions = len(assignments)
        
        for question_id, question_data in assignments.items():
            print(f"📋 Auditando {question_id}...")
            self.audit_question(question_id, question_data)
            self.report.questions_audited += 1
        
        # Validaciones globales
        self.audit_global_consistency()
        
        return self.report
    
    def audit_question(self, question_id: str, data: Dict):
        """Audita una pregunta específica"""
        # 1. Verificar clasificación TYPE
        self._check_type_classification(question_id, data)
        
        # 2. Verificar métodos N1
        self._check_n1_methods(question_id, data)
        
        # 3. Verificar métodos N2
        self._check_n2_methods(question_id, data)
        
        # 4. Verificar métodos N3
        self._check_n3_methods(question_id, data)
        
        # 5. Verificar estrategias de fusión
        self._check_fusion_strategies(question_id, data)
        
        # 6. Verificar justificación epistemológica
        self._check_overall_justification(question_id, data)
    
    def _check_type_classification(self, qid: str, data: Dict):
        """Verifica clasificación TYPE correcta"""
        actual_type = data.get('type')
        expected_type = self.EXPECTED_TYPES.get(qid)
        
        if not actual_type:
            self.report.issues.append(Issue(
                qid, Severity.CRITICAL, "TYPE_CLASSIFICATION",
                "Falta campo 'type'"))
            self.report.failed_checks += 1
            return
        
        if actual_type != expected_type:
            self.report.issues.append(Issue(
                qid, Severity.CRITICAL, "TYPE_CLASSIFICATION",
                f"Clasificación TYPE incorrecta",
                expected=expected_type,
                actual=actual_type))
            self.report.failed_checks += 1
        else:
            self.report.passed_checks += 1
    
    def _check_n1_methods(self, qid: str, data: Dict):
        """Verifica métodos N1-EMP"""
        methods = data.get('selected_methods', {}).get('N1-EMP', [])
        
        if not methods:
            self.report.issues.append(Issue(
                qid, Severity.CRITICAL, "N1_METHODS",
                "Faltan métodos N1-EMP (debe haber al menos 1)"))
            self.report.failed_checks += 1
            return
        
        for i, method in enumerate(methods):
            # Verificar output_type = FACT
            output_type = method.get('output_type')
            if output_type != 'FACT':
                self.report.issues.append(Issue(
                    qid, Severity.CRITICAL, "N1_OUTPUT_TYPE",
                    f"Método N1[{i}] '{method.get('method_id')}' debe tener output_type='FACT'",
                    expected='FACT',
                    actual=output_type))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
            
            # Verificar fusion_behavior = concat
            fusion = method.get('fusion_behavior')
            if fusion != 'concat':
                self.report.issues.append(Issue(
                    qid, Severity.HIGH, "N1_FUSION_BEHAVIOR",
                    f"Método N1[{i}] '{method.get('method_id')}' debe tener fusion_behavior='concat'",
                    expected='concat',
                    actual=fusion))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
            
            # Verificar justification presente
            justification = method.get('justification')
            if not justification:
                self.report.issues.append(Issue(
                    qid, Severity.MEDIUM, "N1_JUSTIFICATION",
                    f"Método N1[{i}] '{method.get('method_id')}' falta justification"))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
    
    def _check_n2_methods(self, qid: str, data: Dict):
        """Verifica métodos N2-INF"""
        methods = data.get('selected_methods', {}).get('N2-INF', [])
        question_type = data.get('type')
        
        if not methods:
            self.report.issues.append(Issue(
                qid, Severity.CRITICAL, "N2_METHODS",
                "Faltan métodos N2-INF (debe haber al menos 1)"))
            self.report.failed_checks += 1
            return
        
        # Verificar métodos mandatorios según TYPE
        if question_type in self.MANDATORY_METHODS:
            mandatory = self.MANDATORY_METHODS[question_type]['N2']
            method_ids = [m.get('method_id', '') for m in methods]
            
            for required_method in mandatory:
                found = any(required_method in mid for mid in method_ids)
                if not found:
                    self.report.issues.append(Issue(
                        qid, Severity.CRITICAL, "N2_MANDATORY_METHOD",
                        f"Falta método mandatorio N2 para {question_type}: {required_method}",
                        expected=required_method,
                        actual=', '.join(method_ids)))
                    self.report.failed_checks += 1
                else:
                    self.report.passed_checks += 1
        
        for i, method in enumerate(methods):
            # Verificar output_type = PARAMETER
            output_type = method.get('output_type')
            if output_type != 'PARAMETER':
                self.report.issues.append(Issue(
                    qid, Severity.CRITICAL, "N2_OUTPUT_TYPE",
                    f"Método N2[{i}] '{method.get('method_id')}' debe tener output_type='PARAMETER'",
                    expected='PARAMETER',
                    actual=output_type))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
            
            # Verificar epistemic_necessity para métodos mandatorios
            if 'forced_inclusion' in method.get('epistemic_necessity', ''):
                method_id = method.get('method_id', '')
                if question_type in self.MANDATORY_METHODS:
                    mandatory = self.MANDATORY_METHODS[question_type]['N2']
                    is_mandatory = any(req in method_id for req in mandatory)
                    if is_mandatory:
                        self.report.passed_checks += 1
                    else:
                        self.report.issues.append(Issue(
                            qid, Severity.HIGH, "N2_EPISTEMIC_NECESSITY",
                            f"Método N2[{i}] '{method_id}' tiene forced_inclusion pero no es mandatorio para {question_type}"))
                        self.report.failed_checks += 1
    
    def _check_n3_methods(self, qid: str, data: Dict):
        """Verifica métodos N3-AUD"""
        methods = data.get('selected_methods', {}).get('N3-AUD', [])
        question_type = data.get('type')
        
        if not methods:
            self.report.issues.append(Issue(
                qid, Severity.CRITICAL, "N3_METHODS",
                "Faltan métodos N3-AUD (debe haber al menos 1)"))
            self.report.failed_checks += 1
            return
        
        # Verificar métodos mandatorios según TYPE
        if question_type in self.MANDATORY_METHODS:
            mandatory = self.MANDATORY_METHODS[question_type]['N3']
            method_ids = [m.get('method_id', '') for m in methods]
            
            for required_method in mandatory:
                found = any(required_method in mid for mid in method_ids)
                if not found:
                    self.report.issues.append(Issue(
                        qid, Severity.CRITICAL, "N3_MANDATORY_METHOD",
                        f"Falta método mandatorio N3 para {question_type}: {required_method}",
                        expected=required_method,
                        actual=', '.join(method_ids)))
                    self.report.failed_checks += 1
                else:
                    self.report.passed_checks += 1
        
        for i, method in enumerate(methods):
            # Verificar output_type = CONSTRAINT
            output_type = method.get('output_type')
            if output_type != 'CONSTRAINT':
                self.report.issues.append(Issue(
                    qid, Severity.CRITICAL, "N3_OUTPUT_TYPE",
                    f"Método N3[{i}] '{method.get('method_id')}' debe tener output_type='CONSTRAINT'",
                    expected='CONSTRAINT',
                    actual=output_type))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
            
            # Verificar fusion_behavior = veto_gate
            fusion = method.get('fusion_behavior', '')
            if fusion and ('veto' in fusion.lower() or 'gate' in fusion.lower()):
                self.report.passed_checks += 1
            else:
                self.report.issues.append(Issue(
                    qid, Severity.HIGH, "N3_FUSION_BEHAVIOR",
                    f"Método N3[{i}] '{method.get('method_id')}' debe tener fusion_behavior con 'veto_gate'",
                    expected='veto_gate',
                    actual=fusion))
                self.report.failed_checks += 1
    
    def _check_fusion_strategies(self, qid: str, data: Dict):
        """Verifica estrategias de fusión según TYPE"""
        fusion_strategy = data.get('fusion_strategy', {})
        question_type = data.get('type')
        
        expected_strategies = {
            'TYPE_A': {
                'R1': 'semantic_bundling',
                'R2': 'semantic_triangulation',
                'R3': 'contradiction_veto'
            },
            'TYPE_B': {
                'R1': 'concat',
                'R2': 'bayesian_update',
                'R3': 'statistical_gate'
            },
            'TYPE_C': {
                'R1': 'graph_construction',
                'R2': 'topological_overlay',
                'R3': 'cycle_detection_veto'
            },
            'TYPE_D': {
                'R1': 'financial_aggregation',
                'R2': 'weighted_mean',
                'R3': 'sufficiency_gate'
            },
            'TYPE_E': {
                'R1': 'fact_collation',
                'R2': 'min_consistency',
                'R3': 'contradiction_veto'
            }
        }
        
        if question_type not in expected_strategies:
            return
        
        expected = expected_strategies[question_type]
        
        for rule, expected_strat in expected.items():
            actual_strat = fusion_strategy.get(rule)
            if actual_strat != expected_strat:
                self.report.issues.append(Issue(
                    qid, Severity.HIGH, "FUSION_STRATEGY",
                    f"Estrategia {rule} incorrecta para {question_type}",
                    expected=expected_strat,
                    actual=actual_strat))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
    
    def _check_overall_justification(self, qid: str, data: Dict):
        """Verifica justificación epistemológica general"""
        justification = data.get('overall_justification')
        
        if not justification:
            self.report.issues.append(Issue(
                qid, Severity.MEDIUM, "OVERALL_JUSTIFICATION",
                "Falta overall_justification"))
            self.report.failed_checks += 1
        else:
            # Verificar que menciona el tipo y la estrategia
            question_type = data.get('type')
            if question_type and question_type not in justification:
                self.report.issues.append(Issue(
                    qid, Severity.LOW, "JUSTIFICATION_QUALITY",
                    f"overall_justification no menciona {question_type}"))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1
    
    def audit_global_consistency(self):
        """Validaciones globales de consistencia"""
        assignments = self.data.get('assignments', {})
        
        # Verificar que hay exactamente 30 preguntas
        if len(assignments) != 30:
            self.report.issues.append(Issue(
                'GLOBAL', Severity.CRITICAL, "QUESTION_COUNT",
                "Debe haber exactamente 30 preguntas",
                expected='30',
                actual=str(len(assignments))))
            self.report.failed_checks += 1
        else:
            self.report.passed_checks += 1
        
        # Verificar distribución de tipos
        type_counts = {}
        for qid, data in assignments.items():
            qtype = data.get('type')
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        expected_distribution = {
            'TYPE_A': 2,
            'TYPE_B': 12,
            'TYPE_C': 4,
            'TYPE_D': 8,
            'TYPE_E': 4
        }
        
        for qtype, expected_count in expected_distribution.items():
            actual_count = type_counts.get(qtype, 0)
            if actual_count != expected_count:
                self.report.issues.append(Issue(
                    'GLOBAL', Severity.HIGH, "TYPE_DISTRIBUTION",
                    f"Distribución incorrecta de {qtype}",
                    expected=str(expected_count),
                    actual=str(actual_count)))
                self.report.failed_checks += 1
            else:
                self.report.passed_checks += 1


def generate_markdown_report(report: AuditReport, output_path: Path):
    """Genera reporte Markdown"""
    lines = []
    
    lines.append("# 📊 EPISTEMIC ASSIGNMENT AUDIT REPORT")
    lines.append(f"**Fecha**: 2025-12-31")
    lines.append(f"**Archivo**: EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json")
    lines.append("")
    
    # Resumen ejecutivo
    lines.append("## 📈 Resumen Ejecutivo")
    lines.append("")
    lines.append(f"- **Preguntas auditadas**: {report.questions_audited}/{report.total_questions}")
    lines.append(f"- **Checks totales**: {report.passed_checks + report.failed_checks}")
    lines.append(f"- **Checks pasados**: {report.passed_checks} ✅")
    lines.append(f"- **Checks fallados**: {report.failed_checks} ❌")
    lines.append(f"- **Cumplimiento**: {report.compliance_percent:.1f}%")
    lines.append("")
    
    # Severidad de issues
    lines.append("## 🚨 Issues por Severidad")
    lines.append("")
    lines.append(f"- 🔴 **Críticos**: {report.critical_count}")
    lines.append(f"- 🟠 **Altos**: {report.high_count}")
    lines.append(f"- 🟡 **Medios**: {report.medium_count}")
    lines.append(f"- 🟢 **Bajos**: {len(report.issues) - report.critical_count - report.high_count - report.medium_count}")
    lines.append("")
    
    # Estado global
    if report.critical_count == 0 and report.compliance_percent >= 95:
        lines.append("## ✅ ESTADO: APROBADO")
        lines.append("")
        lines.append("El archivo cumple con los requisitos epistemológicos mínimos.")
    else:
        lines.append("## ❌ ESTADO: REQUIERE CORRECCIONES")
        lines.append("")
        lines.append("Se encontraron issues críticos que deben ser resueltos.")
    lines.append("")
    
    # Detalles de issues
    if report.issues:
        lines.append("## 🐛 Issues Detectados")
        lines.append("")
        
        # Agrupar por severidad
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            issues_of_severity = [i for i in report.issues if i.severity == severity]
            if issues_of_severity:
                lines.append(f"### {severity.value}")
                lines.append("")
                for issue in issues_of_severity:
                    lines.append(f"**{issue.question_id}** - {issue.category}")
                    lines.append(f"- {issue.message}")
                    if issue.expected:
                        lines.append(f"  - Esperado: `{issue.expected}`")
                    if issue.actual:
                        lines.append(f"  - Actual: `{issue.actual}`")
                    lines.append("")
    else:
        lines.append("## ✨ Sin Issues")
        lines.append("")
        lines.append("No se detectaron problemas. ¡Excelente trabajo!")
        lines.append("")
    
    # Recomendaciones
    if report.critical_count > 0:
        lines.append("## 💡 Recomendaciones")
        lines.append("")
        lines.append("1. **Prioridad Alta**: Resolver todos los issues críticos (🔴)")
        lines.append("2. Verificar que los métodos mandatorios están presentes según episte_refact.md Section 2.2")
        lines.append("3. Asegurar que output_types son correctos: N1=FACT, N2=PARAMETER, N3=CONSTRAINT")
        lines.append("4. Validar estrategias de fusión según TYPE")
        lines.append("")
    
    # Escribir
    output_path.write_text("\n".join(lines), encoding='utf-8')
    print(f"✅ Reporte guardado en: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python audit_epistemic_assignments.py <assignments.json>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"❌ Archivo no encontrado: {input_file}")
        sys.exit(1)
    
    # Cargar datos
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Auditar
    auditor = EpistemicAssignmentAuditor(data)
    report = auditor.audit_all()
    
    # Generar reporte
    repo_root = Path(__file__).resolve().parent.parent.parent
    output_path = repo_root / "artifacts" / "data" / "reports" / "EPISTEMIC_AUDIT_REPORT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_markdown_report(report, output_path)
    
    # Imprimir resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE AUDITORÍA")
    print("=" * 80)
    print(f"Preguntas auditadas: {report.questions_audited}/{report.total_questions}")
    print(f"Cumplimiento: {report.compliance_percent:.1f}%")
    print(f"Issues críticos: {report.critical_count}")
    print(f"Issues altos: {report.high_count}")
    print("")
    
    if report.critical_count == 0 and report.compliance_percent >= 95:
        print("✅ RESULTADO: APROBADO")
        sys.exit(0)
    else:
        print("❌ RESULTADO: REQUIERE CORRECCIONES")
        sys.exit(1)


if __name__ == "__main__":
    main()
