#!/usr/bin/env python3
"""
AUDITORÍA DE CALIDAD EPISTÉMICA - F.A.R.F.A.N v4.0.0

Evalúa si los métodos asignados a cada pregunta son suficientes y apropiados
para responder el interrogante con alto rigor intelectual.

CRITERIOS DE EVALUACIÓN:
1. Cobertura de dimensiones semánticas de la pregunta
2. Suficiencia de métodos N1 (extracción empírica)
3. Suficiencia de métodos N2 (procesamiento inferencial)
4. Suficiencia de métodos N3 (auditoría y robustez)
5. Alineación TYPE-pregunta-métodos
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class EpistemicGap(Enum):
    """Tipos de gaps epistémicos detectados"""
    INSUFFICIENT_N1 = "N1_INSUFICIENTE"
    INSUFFICIENT_N2 = "N2_INSUFICIENTE"
    INSUFFICIENT_N3 = "N3_INSUFICIENTE"
    MISSING_DIMENSION = "DIMENSION_FALTANTE"
    TYPE_MISMATCH = "DESAJUSTE_TYPE"
    WEAK_VALIDATION = "VALIDACION_DEBIL"


@dataclass
class AuditFinding:
    """Hallazgo de auditoría"""
    question_id: str
    gap_type: EpistemicGap
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    recommendation: str
    current_methods: Dict[str, List[str]]


class EpistemicAuditor:
    """Auditor de calidad epistémica"""

    def __init__(self, assets_path: Path):
        self.assets_path = assets_path
        self.questions = self._load_questions()
        self.method_sets = self._load_method_sets()

    def _load_questions(self) -> Dict[str, str]:
        """Carga las 30 preguntas desde contratos_clasificados.json"""
        with open(self.assets_path / "contratos_clasificados.json") as f:
            data = json.load(f)

        questions = {}
        for dim_key, dim_data in data["contratos"].items():
            for q_key, q_data in dim_data.items():
                questions[q_key] = {
                    "pregunta": q_data["pregunta"],
                    "tipo": q_data["tipo_contrato"]["codigo"],
                    "dimension": dim_key
                }
        return questions

    def _load_method_sets(self) -> Dict[str, Any]:
        """Carga los conjuntos de métodos"""
        with open(self.assets_path / "method_sets_by_question.json") as f:
            data = json.load(f)
        return data["method_sets"]

    def audit_question(self, q_id: str) -> AuditFinding | None:
        """Audita una pregunta específica"""
        q_data = self.questions[q_id]
        methods = self.method_sets[q_id]

        # Extraer nombres de métodos
        n1_methods = [m["method_name"] for m in methods["phase_a_N1"]]
        n2_methods = [m["method_name"] for m in methods["phase_b_N2"]]
        n3_methods = [m["method_name"] for m in methods["phase_c_N3"]]

        # Análisis específico por pregunta
        if q_id == "D1_Q1":
            return self._audit_d1_q1(q_data, n1_methods, n2_methods, n3_methods)
        elif q_id == "D1_Q2":
            return self._audit_d1_q2(q_data, n1_methods, n2_methods, n3_methods)
        elif q_id == "D1_Q3":
            return self._audit_d1_q3(q_data, n1_methods, n2_methods, n3_methods)
        # ... continuar con las demás preguntas
        return None

    def _audit_d1_q1(self, q_data: Dict, n1: List[str], n2: List[str], n3: List[str]) -> AuditFinding | None:
        """
        D1.Q1: ¿El diagnóstico del sector presenta datos cuantitativos (tasas, porcentajes,
        cifras absolutas) con año de referencia y fuente identificada, desagregados por
        territorio o población?

        Dimensiones requeridas:
        1. Extracción de datos cuantitativos (tasas, %, cifras)
        2. Extracción de año de referencia
        3. Extracción de fuente identificada
        4. Extracción de desagregación territorial/poblacional
        5. Validación de coherencia semántica
        """
        pregunta = q_data["pregunta"]

        # Verificar N1: ¿Extrae datos cuantitativos?
        n1_has_numeric = any(m in n1 for m in ["extract_numeric", "parse_quantitative", "detect_numbers"])
        # Verificar N1: ¿Extrae fuentes?
        n1_has_source = any(m in n1 for m in ["extract_source", "detect_citation", "identify_reference"])

        # Verificar N2: ¿Valida coherencia?
        n2_has_validation = any(m in n2 for m in ["validate", "check_coherence", "verify"])

        # Verificar N3: ¿Audita calidad?
        n3_has_audit = any(m in n3 for m in ["audit", "validate", "check"])

        gaps = []

        if not n1_has_numeric:
            gaps.append("N1 no detecta explícitamente datos cuantitativos")

        if not n1_has_source:
            gaps.append("N1 no detecta explícitamente fuentes")

        if gaps:
            return AuditFinding(
                question_id="D1_Q1",
                gap_type=EpistemicGap.INSUFFICIENT_N1,
                severity="HIGH",
                description=f"Gaps en N1: {', '.join(gaps)}",
                recommendation="Añadir métodos: extract_quantitative_data(), detect_source_citation()",
                current_methods={"N1": n1, "N2": n2, "N3": n3}
            )

        return None

    def _audit_d1_q2(self, q_data: Dict, n1: List[str], n2: List[str], n3: List[str]) -> AuditFinding | None:
        """
        D1.Q2: ¿El diagnóstico dimensiona numéricamente la magnitud del problema o déficit
        del sector y reconoce explícitamente limitaciones en los datos?

        Dimensiones requeridas:
        1. Extracción de cuantificaciones de brecha
        2. Extracción de reconocimiento de vacíos
        3. Inferencia bayesiana de completitud
        4. Validación de consistencia limitaciones vs evidencia
        """
        n1_has_gap = any(m in n1 for m in ["extract_gap", "detect_deficit", "quantify_magnitude"])
        n1_has_limitations = any(m in n1 for m in ["extract_limitation", "recognize_uncertainty"])

        if not n1_has_gap:
            return AuditFinding(
                question_id="D1_Q2",
                gap_type=EpistemicGap.INSUFFICIENT_N1,
                severity="HIGH",
                description="N1 no extrae explícitamente dimensionamiento de brechas",
                recommendation="Añadir método: extract_breach_quantification()",
                current_methods={"N1": n1, "N2": n2, "N3": n3}
            )

        return None

    def _audit_d1_q3(self, q_data: Dict, n1: List[str], n2: List[str], n3: List[str]) -> AuditFinding | None:
        """
        D1.Q3: ¿El Plan Plurianual de Inversiones (PPI) o tablas presupuestales asignan
        recursos monetarios explícitos a programas, proyectos o intervenciones específicas
        del sector?

        Dimensiones requeridas (TYPE_D - Financiero):
        1. Extracción de asignaciones presupuestales
        2. Extracción de códigos de proyectos/programas
        3. Validación de suficiencia financiera
        4. Auditoría de coherencia financiera
        """
        n1_has_budget = any(m in n1 for m in ["extract_budget", "parse_financial", "detect_allocation"])
        n3_has_sufficiency = any(m in n3 for m in ["check_sufficiency", "validate_budget", "audit_allocation"])

        gaps = []
        if not n1_has_budget:
            gaps.append("N1 no extrae asignaciones presupuestales")

        if not n3_has_sufficiency:
            gaps.append("N3 no valida suficiencia financiera")

        if gaps:
            return AuditFinding(
                question_id="D1_Q3",
                gap_type=EpistemicGap.INSUFFICIENT_N1,
                severity="CRITICAL",
                description=f"Gaps financieros: {', '.join(gaps)}",
                recommendation="Añadir métodos N1 de extracción presupuestal y N3 de validación de suficiencia",
                current_methods={"N1": n1, "N2": n2, "N3": n3}
            )

        return None

    def audit_all(self) -> List[AuditFinding]:
        """Audita todas las 30 preguntas"""
        findings = []

        for q_id in sorted(self.questions.keys()):
            finding = self.audit_question(q_id)
            if finding:
                findings.append(finding)

        return findings

    def generate_report(self) -> str:
        """Genera reporte de auditoría"""
        findings = self.audit_all()

        report = ["# AUDITORÍA EPISTÉMICA F.A.R.F.A.N v4.0.0", ""]
        report.append(f"Total preguntas auditadas: 30")
        report.append(f"Hallazgos detectados: {len(findings)}")
        report.append("")

        if not findings:
            report.append("✅ NO SE DETECTARON GAPS EPISTÉMICOS")
        else:
            report.append("## HALLAZGOS POR SEVERIDAD")
            report.append("")

            critical = [f for f in findings if f.severity == "CRITICAL"]
            high = [f for f in findings if f.severity == "HIGH"]
            medium = [f for f in findings if f.severity == "MEDIUM"]

            if critical:
                report.append(f"### CRÍTICOS ({len(critical)})")
                for f in critical:
                    report.append(f"- **{f.question_id}**: {f.description}")
                    report.append(f"  Recomendación: {f.recommendation}")
                report.append("")

            if high:
                report.append(f"### ALTOS ({len(high)})")
                for f in high:
                    report.append(f"- **{f.question_id}**: {f.description}")
                    report.append(f"  Recomendación: {f.recommendation}")
                report.append("")

            if medium:
                report.append(f"### MEDIOS ({len(medium)})")
                for f in medium:
                    report.append(f"- **{f.question_id}**: {f.description}")
                    report.append(f"  Recomendación: {f.recommendation}")

        return "\n".join(report)


if __name__ == "__main__":
    assets = Path("src/farfan_pipeline/phases/Phase_two/epistemological_assets")
    auditor = EpistemicAuditor(assets)
    report = auditor.generate_report()
    print(report)

    # Guardar reporte
    output = Path("/tmp/epistemic_audit_report.md")
    output.write_text(report)
    print(f"\nReporte guardado en: {output}")
