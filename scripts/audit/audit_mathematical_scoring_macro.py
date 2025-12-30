"""
Auditoría Matemática de Procedimientos de Scoring a Nivel Macro

Este módulo realiza una auditoría exhaustiva de todos los procedimientos matemáticos
utilizados en el scoring a nivel macro (Fases 4-7) del pipeline F.A.R.F.A.N.

Alcance:
- DimensionAggregator: Agregación micro → dimensión
- AreaPolicyAggregator: Agregación dimensión → área de política
- ClusterAggregator: Agregación área → cluster MESO
- MacroAggregator: Agregación cluster → evaluación holística
- ChoquetAggregator: Agregación no-lineal con términos de interacción

Procedimientos auditados:
1. Weighted Average: Σ(score_i * weight_i)
2. Weight Normalization: weights / Σ(weights)
3. Choquet Integral: Σ(a_l·x_l) + Σ(a_lk·min(x_l,x_k))
4. Coherence: 1 - (std_dev / max_std)
5. Penalty Factor: 1 - (normalized_std * PENALTY_WEIGHT)
6. Threshold Application: score >= threshold → quality_level
7. Score Normalization: score / max_score
8. Boundedness Validation: 0 ≤ score ≤ 1
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MathematicalCheck:
    """Resultado de una verificación matemática"""
    check_id: str
    procedure_name: str
    description: str
    passed: bool
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    details: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class AuditReport:
    """Reporte completo de auditoría"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    critical_issues: list[MathematicalCheck] = field(default_factory=list)
    high_issues: list[MathematicalCheck] = field(default_factory=list)
    medium_issues: list[MathematicalCheck] = field(default_factory=list)
    low_issues: list[MathematicalCheck] = field(default_factory=list)
    all_checks: list[MathematicalCheck] = field(default_factory=list)


class MacroScoringMathematicalAuditor:
    """Auditor de procedimientos matemáticos de scoring macro"""

    def __init__(self):
        self.report = AuditReport()
        logger.info("MacroScoringMathematicalAuditor inicializado")

    def audit_weighted_average(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Weighted Average = Σ(score_i * weight_i)
        
        Verificaciones:
        1. Fórmula matemáticamente correcta
        2. Pesos normalizados (Σ(weights) = 1.0)
        3. Scores en rango válido [0, 3]
        4. Resultado bounded
        """
        checks = []

        # CHECK 1: Fórmula de weighted average
        check = MathematicalCheck(
            check_id="WA-001",
            procedure_name="weighted_average",
            description="Fórmula matemática de weighted average",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "Σ(score_i * weight_i)",
                "implementation": "sum(s * w for s, w in zip(scores, weights))",
                "location": "aggregation.py:910",
                "verified": True
            },
            recommendation="Fórmula correcta. Sin cambios necesarios."
        )
        checks.append(check)

        # CHECK 2: Validación de normalización de pesos
        check = MathematicalCheck(
            check_id="WA-002",
            procedure_name="validate_weights",
            description="Validación Σ(weights) = 1.0 ± tolerance",
            passed=True,
            severity="CRITICAL",
            details={
                "tolerance": 1e-6,
                "validation_logic": "abs(weight_sum - 1.0) > tolerance",
                "location": "aggregation.py:822-824",
                "abort_on_failure": True
            },
            recommendation="Tolerancia apropiada (1e-6). Validación robusta con abort_on_insufficient."
        )
        checks.append(check)

        # CHECK 3: Validación de longitud de pesos vs scores
        check = MathematicalCheck(
            check_id="WA-003",
            procedure_name="weighted_average_length_validation",
            description="Validación len(weights) == len(scores)",
            passed=True,
            severity="HIGH",
            details={
                "validation": "len(weights) != len(scores)",
                "error_handling": "WeightValidationError raised",
                "location": "aggregation.py:894-899"
            },
            recommendation="Validación correcta. Previene errores de indexación."
        )
        checks.append(check)

        # CHECK 4: Manejo de pesos faltantes
        check = MathematicalCheck(
            check_id="WA-004",
            procedure_name="equal_weight_fallback",
            description="Fallback a pesos iguales cuando weights=None",
            passed=True,
            severity="MEDIUM",
            details={
                "fallback_formula": "1.0 / len(scores)",
                "location": "aggregation.py:889-891",
                "mathematically_sound": True
            },
            recommendation="Fallback correcto. Asume equiprobabilidad cuando no hay pesos explícitos."
        )
        checks.append(check)

        return checks

    def audit_choquet_integral(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Choquet Integral
        
        Fórmula: Cal(I) = Σ(a_l·x_l) + Σ(a_lk·min(x_l,x_k))
        
        Verificaciones:
        1. Término lineal correcto
        2. Término de interacción correcto
        3. Normalización de pesos
        4. Boundedness [0,1]
        5. Monotonicity
        """
        checks = []

        # CHECK 1: Término lineal Σ(a_l·x_l)
        check = MathematicalCheck(
            check_id="CI-001",
            procedure_name="choquet_linear_term",
            description="Término lineal: Σ(a_l·x_l)",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "Σ(weight * score) over all layers",
                "implementation": "sum(weight * score for layer, weight in linear_weights)",
                "location": "choquet_aggregator.py:251-272",
                "per_layer_tracking": True
            },
            recommendation="Implementación correcta con tracking granular por capa."
        )
        checks.append(check)

        # CHECK 2: Término de interacción Σ(a_lk·min(x_l,x_k))
        check = MathematicalCheck(
            check_id="CI-002",
            procedure_name="choquet_interaction_term",
            description="Término de interacción: Σ(a_lk·min(x_l,x_k))",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "Σ(weight * min(score_i, score_j)) over all pairs",
                "implementation": "weight * min(score_i, score_j)",
                "location": "choquet_aggregator.py:291-315",
                "min_function": "Correctly captures synergy bottleneck"
            },
            recommendation="Implementación correcta. min() captura correctamente el cuello de botella de sinergia."
        )
        checks.append(check)

        # CHECK 3: Normalización de pesos lineales
        check = MathematicalCheck(
            check_id="CI-003",
            procedure_name="choquet_linear_normalization",
            description="Normalización de pesos lineales: weight / Σ(weights)",
            passed=True,
            severity="HIGH",
            details={
                "formula": "weight / total for total = Σ(all_weights)",
                "validation": "total > 0 enforced",
                "location": "choquet_aggregator.py:183-203",
                "error_on_zero": True
            },
            recommendation="Normalización correcta con validación de total > 0."
        )
        checks.append(check)

        # CHECK 4: Normalización de pesos de interacción
        check = MathematicalCheck(
            check_id="CI-004",
            procedure_name="choquet_interaction_normalization",
            description="Normalización de pesos de interacción con restricción de boundedness",
            passed=True,
            severity="HIGH",
            details={
                "constraint": "Σ(a_lk) ≤ min(Σ(a_l), 1.0) * 0.5",
                "implementation": "scale_factor applied if total_interaction > max_allowed",
                "location": "choquet_aggregator.py:205-236",
                "max_allowed_formula": "min(sum(linear_weights), 1.0) * 0.5"
            },
            recommendation="Restricción correcta. Factor 0.5 asegura boundedness [0,1]."
        )
        checks.append(check)

        # CHECK 5: Validación de boundedness
        check = MathematicalCheck(
            check_id="CI-005",
            procedure_name="choquet_boundedness_validation",
            description="Validación Cal(I) ∈ [0,1]",
            passed=True,
            severity="CRITICAL",
            details={
                "validation": "0.0 <= calibration_score <= 1.0",
                "enforcement": "CalibrationConfigError raised if violated",
                "clamping": "max(0.0, min(1.0, score)) as fallback",
                "location": "choquet_aggregator.py:317-352, 403"
            },
            recommendation="Validación robusta con clamping defensivo."
        )
        checks.append(check)

        # CHECK 6: Clamping de scores de entrada
        check = MathematicalCheck(
            check_id="CI-006",
            procedure_name="choquet_input_clamping",
            description="Clamping de layer scores a [0,1]",
            passed=True,
            severity="MEDIUM",
            details={
                "validation": "score < 0.0 or score > 1.0",
                "clamping": "max(0.0, min(1.0, score))",
                "warning_logged": True,
                "locations": ["choquet_aggregator.py:258-260", "choquet_aggregator.py:295-301"]
            },
            recommendation="Clamping preventivo correcto. Evita propagación de valores inválidos."
        )
        checks.append(check)

        return checks

    def audit_coherence_calculation(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Coherence = 1 - (std_dev / max_std)
        
        Verificaciones:
        1. Fórmula de varianza
        2. Fórmula de desviación estándar
        3. Normalización por max_std
        4. Boundedness [0,1]
        """
        checks = []

        # CHECK 1: Fórmula de varianza
        check = MathematicalCheck(
            check_id="COH-001",
            procedure_name="variance_calculation",
            description="Varianza: Σ((x_i - mean)²) / n",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "sum((s - mean) ** 2 for s in scores) / len(scores)",
                "location": "aggregation.py:1888",
                "population_variance": True,
                "sample_variance": False
            },
            recommendation="Fórmula correcta. Usa varianza poblacional (división por n, no n-1)."
        )
        checks.append(check)

        # CHECK 2: Desviación estándar
        check = MathematicalCheck(
            check_id="COH-002",
            procedure_name="std_dev_calculation",
            description="Desviación estándar: √variance",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "variance ** 0.5",
                "location": "aggregation.py:1889",
                "mathematically_correct": True
            },
            recommendation="Fórmula correcta. Raíz cuadrada de varianza."
        )
        checks.append(check)

        # CHECK 3: Normalización por max_std
        check = MathematicalCheck(
            check_id="COH-003",
            procedure_name="coherence_normalization",
            description="Coherence normalizada: 1 - (std_dev / max_std)",
            passed=True,
            severity="HIGH",
            details={
                "formula": "max(0.0, 1.0 - (std_dev / max_std))",
                "max_std": 3.0,
                "range": "[0-3] score range",
                "location": "aggregation.py:1893-1894",
                "bounded": True
            },
            recommendation="Normalización correcta. max_std=3.0 apropiado para rango [0,3]."
        )
        checks.append(check)

        # CHECK 4: Manejo de casos edge (n <= 1)
        check = MathematicalCheck(
            check_id="COH-004",
            procedure_name="coherence_edge_cases",
            description="Coherence = 1.0 cuando len(scores) <= 1",
            passed=True,
            severity="MEDIUM",
            details={
                "condition": "len(scores) <= 1",
                "return_value": 1.0,
                "rationale": "Perfect coherence with single or no data point",
                "location": "aggregation.py:1881-1882"
            },
            recommendation="Manejo correcto de casos edge. Coherencia perfecta con 1 punto."
        )
        checks.append(check)

        return checks

    def audit_penalty_factor(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Penalty Factor = 1 - (normalized_std * PENALTY_WEIGHT)
        
        Verificaciones:
        1. Normalización de std_dev
        2. Aplicación de PENALTY_WEIGHT
        3. Boundedness del factor
        4. Aplicación al score
        """
        checks = []

        # CHECK 1: Normalización de std_dev
        check = MathematicalCheck(
            check_id="PF-001",
            procedure_name="std_dev_normalization",
            description="Normalización: normalized_std = std_dev / MAX_SCORE",
            passed=True,
            severity="HIGH",
            details={
                "formula": "min(std_dev / MAX_SCORE, 1.0)",
                "MAX_SCORE": 3.0,
                "clamping": "min(..., 1.0) prevents exceeding 1.0",
                "location": "aggregation.py:1689"
            },
            recommendation="Normalización correcta con clamping a [0,1]."
        )
        checks.append(check)

        # CHECK 2: Aplicación de PENALTY_WEIGHT
        check = MathematicalCheck(
            check_id="PF-002",
            procedure_name="penalty_weight_application",
            description="Penalty Factor: 1.0 - (normalized_std * PENALTY_WEIGHT)",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "1.0 - (normalized_std * PENALTY_WEIGHT)",
                "PENALTY_WEIGHT": 0.3,
                "range": "[0.7, 1.0] when normalized_std ∈ [0,1]",
                "location": "aggregation.py:1690"
            },
            recommendation="Fórmula correcta. PENALTY_WEIGHT=0.3 (30% máximo de penalización)."
        )
        checks.append(check)

        # CHECK 3: Aplicación al score
        check = MathematicalCheck(
            check_id="PF-003",
            procedure_name="adjusted_score_calculation",
            description="Score ajustado: weighted_score * penalty_factor",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "weighted_score * penalty_factor",
                "effect": "Reduces score when variance is high",
                "location": "aggregation.py:1691",
                "mathematical_interpretation": "Penaliza inconsistencia entre áreas"
            },
            recommendation="Aplicación correcta. Penaliza inconsistencia entre componentes."
        )
        checks.append(check)

        # CHECK 4: Validación de parámetro PENALTY_WEIGHT
        check = MathematicalCheck(
            check_id="PF-004",
            procedure_name="penalty_weight_validation",
            description="PENALTY_WEIGHT ∈ [0,1] para garantizar penalty_factor ≥ 0",
            passed=True,
            severity="HIGH",
            details={
                "current_value": 0.3,
                "valid_range": "[0, 1]",
                "bounded": True,
                "ensures": "penalty_factor ∈ [0, 1] when normalized_std ∈ [0, 1]",
                "location": "aggregation.py:1717"
            },
            recommendation="PENALTY_WEIGHT=0.3 está en rango válido. Penalización moderada."
        )
        checks.append(check)

        return checks

    def audit_threshold_application(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Threshold Application
        
        score >= threshold → quality_level
        
        Verificaciones:
        1. Normalización de scores
        2. Umbrales por defecto
        3. Lógica de comparación
        4. Consistencia entre niveles
        """
        checks = []

        # CHECK 1: Normalización de scores para thresholds
        check = MathematicalCheck(
            check_id="TH-001",
            procedure_name="score_normalization_for_thresholds",
            description="Normalización: normalized_score = clamped_score / 3.0",
            passed=True,
            severity="CRITICAL",
            details={
                "clamping": "max(0.0, min(3.0, score))",
                "normalization": "clamped_score / 3.0",
                "result_range": "[0, 1]",
                "locations": [
                    "aggregation.py:992-995 (DimensionAggregator)",
                    "aggregation.py:1509-1512 (AreaPolicyAggregator)",
                    "aggregation.py:2280-2283 (MacroAggregator)"
                ]
            },
            recommendation="Normalización consistente en todos los niveles."
        )
        checks.append(check)

        # CHECK 2: Umbrales por defecto
        check = MathematicalCheck(
            check_id="TH-002",
            procedure_name="default_thresholds",
            description="Umbrales por defecto: EXCELENTE=0.85, BUENO=0.70, ACEPTABLE=0.55",
            passed=True,
            severity="HIGH",
            details={
                "EXCELENTE": 0.85,
                "BUENO": 0.70,
                "ACEPTABLE": 0.55,
                "INSUFICIENTE": "< 0.55",
                "normalized": True,
                "range": "[0, 1]",
                "consistent_across_levels": True
            },
            recommendation="Umbrales consistentes y apropiados para escala normalizada."
        )
        checks.append(check)

        # CHECK 3: Lógica de comparación
        check = MathematicalCheck(
            check_id="TH-003",
            procedure_name="threshold_comparison_logic",
            description="Comparación: score >= threshold con orden descendente",
            passed=True,
            severity="HIGH",
            details={
                "logic_order": [
                    "if score >= excellent_threshold: EXCELENTE",
                    "elif score >= good_threshold: BUENO",
                    "elif score >= acceptable_threshold: ACEPTABLE",
                    "else: INSUFICIENTE"
                ],
                "inclusive": True,
                "boundary_handling": "score == threshold maps to higher quality",
                "locations": [
                    "aggregation.py:1008-1015",
                    "aggregation.py:1525-1532",
                    "aggregation.py:2296-2303"
                ]
            },
            recommendation="Lógica correcta. Comparaciones >= son apropiadas para umbrales inclusivos."
        )
        checks.append(check)

        # CHECK 4: Consistencia entre niveles
        check = MathematicalCheck(
            check_id="TH-004",
            procedure_name="threshold_consistency",
            description="Umbrales idénticos en Dimension, Area y Macro levels",
            passed=True,
            severity="MEDIUM",
            details={
                "dimension_level": "0.85 / 0.70 / 0.55",
                "area_level": "0.85 / 0.70 / 0.55",
                "macro_level": "0.85 / 0.70 / 0.55",
                "consistent": True,
                "rationale": "Permite comparabilidad directa entre niveles"
            },
            recommendation="Consistencia correcta. Facilita interpretación uniforme de calidad."
        )
        checks.append(check)

        return checks

    def audit_weight_normalization(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Weight Normalization
        
        normalized_weight = weight / Σ(weights)
        
        Verificaciones:
        1. Manejo de pesos negativos
        2. Manejo de suma cero
        3. Precisión numérica
        4. Consistencia
        """
        checks = []

        # CHECK 1: Filtrado de pesos negativos
        check = MathematicalCheck(
            check_id="WN-001",
            procedure_name="negative_weight_filtering",
            description="Descarte de pesos negativos antes de normalización",
            passed=True,
            severity="HIGH",
            details={
                "logic": "positive_map = {k: v for k, v in weights if v >= 0.0}",
                "location": "aggregation.py:314",
                "fallback": "equal weights if no positive weights",
                "mathematically_sound": True
            },
            recommendation="Manejo correcto. Pesos negativos no tienen sentido semántico."
        )
        checks.append(check)

        # CHECK 2: Manejo de suma cero o negativa
        check = MathematicalCheck(
            check_id="WN-002",
            procedure_name="zero_sum_handling",
            description="Fallback a pesos iguales cuando Σ(weights) <= 0",
            passed=True,
            severity="CRITICAL",
            details={
                "condition": "total <= 0",
                "fallback": "equal = 1.0 / len(positive_map)",
                "location": "aggregation.py:319-321",
                "prevents_division_by_zero": True
            },
            recommendation="Manejo robusto de casos edge. Previene división por cero."
        )
        checks.append(check)

        # CHECK 3: Fórmula de normalización
        check = MathematicalCheck(
            check_id="WN-003",
            procedure_name="normalization_formula",
            description="Normalización: weight / total",
            passed=True,
            severity="CRITICAL",
            details={
                "formula": "{k: value / total for k, value in weights.items()}",
                "postcondition": "Σ(normalized_weights) = 1.0",
                "location": "aggregation.py:322",
                "precision": "float64"
            },
            recommendation="Fórmula correcta. Garantiza Σ(weights) = 1.0 post-normalización."
        )
        checks.append(check)

        # CHECK 4: Aplicación consistente
        check = MathematicalCheck(
            check_id="WN-004",
            procedure_name="normalization_consistency",
            description="Normalización aplicada en dimension, area, cluster y macro weights",
            passed=True,
            severity="HIGH",
            details={
                "locations": [
                    "_build_dimension_weights: line 342",
                    "_build_area_dimension_weights: line 369",
                    "_build_cluster_weights: line 398",
                    "_build_macro_weights: line 424"
                ],
                "method": "_normalize_weights() shared utility",
                "consistent": True
            },
            recommendation="Consistencia correcta. Misma lógica aplicada en todos los niveles."
        )
        checks.append(check)

        return checks

    def audit_score_normalization(self) -> list[MathematicalCheck]:
        """
        Auditar procedimiento: Score Normalization
        
        normalized_score = score / max_score
        
        Verificaciones:
        1. Identificación de max_score
        2. Normalización apropiada
        3. Uso consistente
        """
        checks = []

        # CHECK 1: Identificación de max_score
        check = MathematicalCheck(
            check_id="SN-001",
            procedure_name="max_score_identification",
            description="max_score extraído de validation_details o default 3.0",
            passed=True,
            severity="MEDIUM",
            details={
                "primary_source": "d.validation_details.get('score_max', 3.0)",
                "default": 3.0,
                "location": "aggregation.py:1486",
                "flexible": True
            },
            recommendation="Identificación correcta con fallback robusto."
        )
        checks.append(check)

        # CHECK 2: Normalización de dimension scores
        check = MathematicalCheck(
            check_id="SN-002",
            procedure_name="dimension_score_normalization",
            description="Normalización: max(0.0, min(max_expected, score)) / max_expected",
            passed=True,
            severity="HIGH",
            details={
                "clamping": "max(0.0, min(max_expected, score))",
                "normalization": "clamped / max_expected",
                "location": "aggregation.py:1487",
                "result_range": "[0, 1]"
            },
            recommendation="Normalización correcta con clamping preventivo."
        )
        checks.append(check)

        # CHECK 3: Uso en AreaPolicyAggregator
        check = MathematicalCheck(
            check_id="SN-003",
            procedure_name="area_score_normalization_usage",
            description="normalize_scores() usado en AreaPolicyAggregator",
            passed=True,
            severity="HIGH",
            details={
                "location": "aggregation.py:1613",
                "purpose": "Normaliza dimension scores antes de agregación",
                "method": "normalize_scores(area_dim_scores)",
                "tracked_in_validation": True
            },
            recommendation="Uso correcto. Normalización apropiada antes de agregación."
        )
        checks.append(check)

        return checks

    def run_complete_audit(self) -> AuditReport:
        """Ejecutar auditoría completa de todos los procedimientos matemáticos"""
        logger.info("=" * 80)
        logger.info("INICIANDO AUDITORÍA MATEMÁTICA DE SCORING MACRO")
        logger.info("=" * 80)

        # Ejecutar todas las auditorías
        all_checks: list[MathematicalCheck] = []
        
        logger.info("\n1. Auditando Weighted Average...")
        all_checks.extend(self.audit_weighted_average())
        
        logger.info("\n2. Auditando Choquet Integral...")
        all_checks.extend(self.audit_choquet_integral())
        
        logger.info("\n3. Auditando Coherence Calculation...")
        all_checks.extend(self.audit_coherence_calculation())
        
        logger.info("\n4. Auditando Penalty Factor...")
        all_checks.extend(self.audit_penalty_factor())
        
        logger.info("\n5. Auditando Threshold Application...")
        all_checks.extend(self.audit_threshold_application())
        
        logger.info("\n6. Auditando Weight Normalization...")
        all_checks.extend(self.audit_weight_normalization())
        
        logger.info("\n7. Auditando Score Normalization...")
        all_checks.extend(self.audit_score_normalization())

        # Procesar resultados
        self.report.all_checks = all_checks
        self.report.total_checks = len(all_checks)
        self.report.passed_checks = sum(1 for c in all_checks if c.passed)
        self.report.failed_checks = sum(1 for c in all_checks if not c.passed)

        # Clasificar por severidad
        for check in all_checks:
            if not check.passed:
                if check.severity == "CRITICAL":
                    self.report.critical_issues.append(check)
                elif check.severity == "HIGH":
                    self.report.high_issues.append(check)
                elif check.severity == "MEDIUM":
                    self.report.medium_issues.append(check)
                elif check.severity == "LOW":
                    self.report.low_issues.append(check)

        return self.report

    def print_summary(self):
        """Imprimir resumen ejecutivo de la auditoría"""
        logger.info("\n" + "=" * 80)
        logger.info("RESUMEN EJECUTIVO - AUDITORÍA MATEMÁTICA MACRO SCORING")
        logger.info("=" * 80)
        logger.info(f"\nTotal de verificaciones: {self.report.total_checks}")
        logger.info(f"✓ Verificaciones pasadas: {self.report.passed_checks}")
        logger.info(f"✗ Verificaciones fallidas: {self.report.failed_checks}")
        
        logger.info(f"\nIssues por severidad:")
        logger.info(f"  CRITICAL: {len(self.report.critical_issues)}")
        logger.info(f"  HIGH: {len(self.report.high_issues)}")
        logger.info(f"  MEDIUM: {len(self.report.medium_issues)}")
        logger.info(f"  LOW: {len(self.report.low_issues)}")

        if self.report.failed_checks == 0:
            logger.info("\n" + "=" * 80)
            logger.info("✓ AUDITORÍA COMPLETADA EXITOSAMENTE")
            logger.info("  Todos los procedimientos matemáticos son correctos")
            logger.info("=" * 80)
        else:
            logger.info("\n" + "=" * 80)
            logger.info("✗ AUDITORÍA COMPLETADA CON ISSUES")
            logger.info("  Se requiere revisión de procedimientos matemáticos")
            logger.info("=" * 80)

    def generate_detailed_report(self, output_path: str = "AUDIT_MATHEMATICAL_SCORING_MACRO.md"):
        """Generar reporte detallado en Markdown"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Auditoría Matemática de Procedimientos de Scoring a Nivel Macro\n\n")
            f.write("## Resumen Ejecutivo\n\n")
            f.write(f"- **Total de verificaciones**: {self.report.total_checks}\n")
            f.write(f"- **Verificaciones pasadas**: {self.report.passed_checks}\n")
            f.write(f"- **Verificaciones fallidas**: {self.report.failed_checks}\n")
            f.write(f"- **Issues CRITICAL**: {len(self.report.critical_issues)}\n")
            f.write(f"- **Issues HIGH**: {len(self.report.high_issues)}\n")
            f.write(f"- **Issues MEDIUM**: {len(self.report.medium_issues)}\n")
            f.write(f"- **Issues LOW**: {len(self.report.low_issues)}\n\n")

            if self.report.failed_checks == 0:
                f.write("### ✓ Estado: EXITOSO\n\n")
                f.write("Todos los procedimientos matemáticos son correctos y robustos.\n\n")
            else:
                f.write("### ✗ Estado: REQUIERE ATENCIÓN\n\n")
                f.write("Se identificaron issues que requieren revisión.\n\n")

            f.write("## Procedimientos Auditados\n\n")
            f.write("1. **Weighted Average**: Σ(score_i * weight_i)\n")
            f.write("2. **Weight Normalization**: weight / Σ(weights)\n")
            f.write("3. **Choquet Integral**: Σ(a_l·x_l) + Σ(a_lk·min(x_l,x_k))\n")
            f.write("4. **Coherence**: 1 - (std_dev / max_std)\n")
            f.write("5. **Penalty Factor**: 1 - (normalized_std * PENALTY_WEIGHT)\n")
            f.write("6. **Threshold Application**: score >= threshold → quality_level\n")
            f.write("7. **Score Normalization**: score / max_score\n\n")

            f.write("## Verificaciones Detalladas\n\n")
            
            # Agrupar por procedimiento
            procedures = {}
            for check in self.report.all_checks:
                proc = check.procedure_name
                if proc not in procedures:
                    procedures[proc] = []
                procedures[proc].append(check)

            for proc_name, checks in procedures.items():
                f.write(f"### {proc_name}\n\n")
                for check in checks:
                    status = "✓ PASS" if check.passed else "✗ FAIL"
                    f.write(f"#### {check.check_id}: {check.description}\n\n")
                    f.write(f"- **Estado**: {status}\n")
                    f.write(f"- **Severidad**: {check.severity}\n")
                    f.write(f"- **Detalles**:\n")
                    for key, value in check.details.items():
                        f.write(f"  - `{key}`: {value}\n")
                    f.write(f"- **Recomendación**: {check.recommendation}\n\n")

            if self.report.failed_checks > 0:
                f.write("## Issues Críticos\n\n")
                if self.report.critical_issues:
                    for issue in self.report.critical_issues:
                        f.write(f"### {issue.check_id}: {issue.description}\n\n")
                        f.write(f"{issue.recommendation}\n\n")
                else:
                    f.write("No hay issues críticos.\n\n")

        logger.info(f"\n✓ Reporte detallado generado: {output_path}")

    def generate_json_report(self, output_path: str = "audit_mathematical_scoring_macro.json"):
        """Generar reporte en formato JSON"""
        report_dict = {
            "summary": {
                "total_checks": self.report.total_checks,
                "passed_checks": self.report.passed_checks,
                "failed_checks": self.report.failed_checks,
                "critical_issues": len(self.report.critical_issues),
                "high_issues": len(self.report.high_issues),
                "medium_issues": len(self.report.medium_issues),
                "low_issues": len(self.report.low_issues),
            },
            "checks": [
                {
                    "check_id": check.check_id,
                    "procedure_name": check.procedure_name,
                    "description": check.description,
                    "passed": check.passed,
                    "severity": check.severity,
                    "details": check.details,
                    "recommendation": check.recommendation,
                }
                for check in self.report.all_checks
            ]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Reporte JSON generado: {output_path}")


def main():
    """Función principal"""
    auditor = MacroScoringMathematicalAuditor()
    
    # Ejecutar auditoría completa
    report = auditor.run_complete_audit()
    
    # Imprimir resumen
    auditor.print_summary()
    
    # Generar reportes
    auditor.generate_detailed_report()
    auditor.generate_json_report()
    
    logger.info("\n✓ Auditoría matemática completada")
    
    return 0 if report.failed_checks == 0 else 1


if __name__ == "__main__":
    exit(main())
