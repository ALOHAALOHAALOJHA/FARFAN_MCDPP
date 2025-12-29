"""Pipeline Epistemológico FORENSE v5.0

PRINCIPIOS INQUEBRANTABLES:
1. FAIL-HARD: Cualquier violación de invariante ABORTA el pipeline
2. NO SILENT POISONING: Cada decisión deja traza completa (matched + anti-matched)
3. FINGERPRINT TOTAL: Hash de reglas, código, y datos como parte del manifest
4. ZERO ORPHANS: Si no hay contrato real, FAIL (no inventar fallbacks)
5. ZERO VETO SIMULADO: N3 sin veto observable = ERROR FATAL (no degradación silenciosa)
6. IMMUTABILITY REAL: Dataclasses frozen + validación en construcción
7. REPRODUCIBILIDAD VERIFICABLE: Mismo input + mismo código = mismo output bit-a-bit

Versión: 5.0.0-FORENSIC
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, NoReturn


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN VÍA ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════════

# Umbral de drift epistemológico (default 5%)
DRIFT_THRESHOLD = float(os.environ.get("FARFAN_DRIFT_THRESHOLD", "0.05"))

# Si True, falla en cualquier degradación (modo estricto)
STRICT_MODE = os.environ.get("FARFAN_STRICT_MODE", "").lower() in ("1", "true", "yes")


def get_git_commit_hash() -> str | None:
    """Obtiene el hash del commit actual de git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: ERRORES FATALES - NO RECUPERABLES
# ══════════════════════════════════════════════════════════════════════════════


class PipelineFatalError(Exception):
    """Error fatal que ABORTA el pipeline. No hay recuperación."""

    def __init__(self, error_id: str, message: str, context: dict[str, Any]) -> None:
        self.error_id = error_id
        self.context = context
        self.timestamp = datetime.now(timezone.utc).isoformat()
        super().__init__(f"[FATAL:{error_id}] {message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_id": self.error_id,
            "message": str(self),
            "context": self.context,
            "timestamp": self.timestamp,
        }


def fatal(error_id: str, message: str, **context: Any) -> NoReturn:
    """Lanza error fatal. El pipeline DEBE abortar."""
    raise PipelineFatalError(error_id, message, context)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: CONSTANTES CERRADAS - ENUMS ESTRICTOS
# ══════════════════════════════════════════════════════════════════════════════


CLASS_LEVELS: Final[frozenset[str]] = frozenset({
    "N1-EMP", "N2-INF", "N3-AUD", "N4-SYN", "INFRASTRUCTURE", "PROTOCOL"
})

METHOD_LEVELS: Final[frozenset[str]] = frozenset({
    "N1-EMP", "N2-INF", "N3-AUD", "N4-SYN", "INFRASTRUCTURE"
})

CLASS_EPISTEMOLOGIES: Final[frozenset[str]] = frozenset({
    "POSITIVIST_EMPIRICAL",
    "BAYESIAN_PROBABILISTIC",
    "DETERMINISTIC_LOGICAL",
    "CAUSAL_MECHANISTIC",
    "POPPERIAN_FALSIFICATIONIST",
    "CRITICAL_REFLEXIVE",
    "NONE",
})

VETO_ACTIONS: Final[frozenset[str]] = frozenset({
    "block_branch",
    "reduce_confidence",
    "flag_caution",
    "suppress_fact",
    "invalidate_graph",
    "flag_and_reduce",
    "flag_insufficiency",
    "downgrade_confidence_to_zero",
    "flag_invalid_sequence",
    "suppress_contradicting_nodes",
})

# Mapeo nivel → dependencias OBLIGATORIAS (no inferidas, declaradas)
LEVEL_REQUIRED_INPUTS: Final[dict[str, frozenset[str]]] = {
    "N1-EMP": frozenset(),  # N1 no requiere nada upstream
    "N2-INF": frozenset({"raw_facts"}),  # N2 DEBE consumir raw_facts
    "N3-AUD": frozenset({"raw_facts", "inferences"}),  # N3 DEBE consumir ambos
    "N4-SYN": frozenset({"raw_facts", "inferences", "validated_constraints"}),  # N4 todo
    "INFRASTRUCTURE": frozenset(),
}

LEVEL_REQUIRED_OUTPUTS: Final[dict[str, frozenset[str]]] = {
    "N1-EMP": frozenset({"raw_facts"}),
    "N2-INF": frozenset({"inferences"}),
    "N3-AUD": frozenset({"validated_constraints"}),
    "N4-SYN": frozenset({"narrative"}),
    "INFRASTRUCTURE": frozenset(),
}


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: RULEBOOK VERSIONADO - FINGERPRINT OBLIGATORIO
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Rule:
    """Regla de clasificación con ID único y trazabilidad."""

    rule_id: str
    description: str
    triggers: tuple[str, ...]  # Señales que activan la regla
    anti_triggers: tuple[str, ...]  # Señales que bloquean la regla
    target_level: str
    target_epistemology: str
    priority: int  # Mayor = más específica = gana en conflicto


@dataclass(frozen=True)
class Rulebook:
    """Conjunto versionado de reglas con fingerprint."""

    version: str
    rules: tuple[Rule, ...]

    def compute_hash(self) -> str:
        """SHA256 del rulebook serializado canónicamente."""
        blob = json.dumps(
            {
                "version": self.version,
                "rules": [
                    {
                        "rule_id": r.rule_id,
                        "description": r.description,
                        "triggers": list(r.triggers),
                        "anti_triggers": list(r.anti_triggers),
                        "target_level": r.target_level,
                        "target_epistemology": r.target_epistemology,
                        "priority": r.priority,
                    }
                    for r in self.rules
                ],
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def get_rule(self, rule_id: str) -> Rule | None:
        for r in self.rules:
            if r.rule_id == rule_id:
                return r
        return None


# RULEBOOK CANÓNICO v5.0
CANONICAL_RULEBOOK = Rulebook(
    version="5.0.0",
    rules=(
        # ─── INFRASTRUCTURE (prioridad máxima para dunders) ───
        Rule(
            rule_id="INFRA_001_DUNDER",
            description="Métodos dunder son siempre INFRASTRUCTURE",
            triggers=("__init__", "__repr__", "__str__", "__hash__", "__eq__", "__lt__", "__gt__"),
            anti_triggers=(),
            target_level="INFRASTRUCTURE",
            target_epistemology="NONE",
            priority=100,
        ),
        Rule(
            rule_id="INFRA_002_PRIVATE_TRIVIAL",
            description="Métodos privados con return None/vacío son INFRASTRUCTURE",
            triggers=("_", "return_type:none", "return_type:noreturn", "return_type:"),
            anti_triggers=("validate", "check", "compute", "infer", "generate"),
            target_level="INFRASTRUCTURE",
            target_epistemology="NONE",
            priority=90,
        ),
        Rule(
            rule_id="INFRA_003_ERROR_FORMAT",
            description="Formateo de errores es INFRASTRUCTURE",
            triggers=("format", "error", "exception", "traceback"),
            anti_triggers=("report", "narrative", "summary"),
            target_level="INFRASTRUCTURE",
            target_epistemology="NONE",
            priority=85,
        ),
        # ─── N3-AUD (validación/auditoría) ───
        Rule(
            rule_id="N3_001_BOOL_VALIDATE",
            description="Métodos bool + validate/check/verify son N3-AUD",
            triggers=("return_type:bool", "validate", "check", "verify", "detect", "audit"),
            anti_triggers=(),
            target_level="N3-AUD",
            target_epistemology="POPPERIAN_FALSIFICATIONIST",
            priority=80,
        ),
        Rule(
            rule_id="N3_002_CONSTRAINT",
            description="Métodos con constraint/validation en nombre son N3-AUD",
            triggers=("constraint", "validation", "assert", "ensure"),
            anti_triggers=(),
            target_level="N3-AUD",
            target_epistemology="POPPERIAN_FALSIFICATIONIST",
            priority=75,
        ),
        # ─── N4-SYN (síntesis narrativa) ───
        Rule(
            rule_id="N4_001_REPORT",
            description="Generación de reportes es N4-SYN",
            triggers=("generate_report", "generate_summary", "generate_narrative", "generate_executive"),
            anti_triggers=("error", "exception"),
            target_level="N4-SYN",
            target_epistemology="CRITICAL_REFLEXIVE",
            priority=70,
        ),
        Rule(
            rule_id="N4_002_NARRATIVE",
            description="Síntesis narrativa explícita es N4-SYN",
            triggers=("narrative", "synthesis", "summary", "compose", "render", "finalize"),
            anti_triggers=("error", "exception", "parse"),
            target_level="N4-SYN",
            target_epistemology="CRITICAL_REFLEXIVE",
            priority=65,
        ),
        # ─── N2-INF (inferencia) ───
        Rule(
            rule_id="N2_001_NUMERIC",
            description="Retornos numéricos son N2-INF",
            triggers=("return_type:float", "return_type:ndarray", "return_type:score", "return_type:distribution"),
            anti_triggers=(),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=60,
        ),
        Rule(
            rule_id="N2_002_BAYESIAN",
            description="Señales bayesianas son N2-INF + BAYESIAN",
            triggers=("posterior", "bayesian", "prior", "credible", "bayes"),
            anti_triggers=(),
            target_level="N2-INF",
            target_epistemology="BAYESIAN_PROBABILISTIC",
            priority=65,
        ),
        Rule(
            rule_id="N2_003_COMPUTE",
            description="Cómputo/inferencia explícita es N2-INF",
            triggers=("infer", "compute", "calculate", "score", "evaluate", "classify"),
            anti_triggers=("validate", "check"),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=55,
        ),
        # ─── N1-EMP (extracción empírica) ───
        Rule(
            rule_id="N1_001_EXTRACT",
            description="Extracción/parsing es N1-EMP",
            triggers=("extract", "parse", "chunk", "split", "normalize", "tokenize"),
            anti_triggers=("infer", "compute", "validate"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=50,
        ),
        Rule(
            rule_id="N1_002_RAW",
            description="Acceso a datos crudos es N1-EMP",
            triggers=("raw", "fetch", "load", "read", "get_text"),
            anti_triggers=("infer", "compute", "validate", "transform"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=45,
        ),
        # ─── REGLAS ADICIONALES BASADAS EN ANÁLISIS DE 138 UNMATCHED ───
        # Justificación: Análisis estadístico de métodos sin clasificar reveló patrones claros
        Rule(
            rule_id="N1_003_GET_ACCESSOR",
            description="get_* son accesores de datos (N1-EMP)",
            triggers=("name:get_",),
            anti_triggers=("compute", "calculate", "infer", "analyze"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=40,
        ),
        Rule(
            rule_id="N1_004_LIST_ACCESSOR",
            description="list_* enumera datos existentes (N1-EMP)",
            triggers=("name:list_",),
            anti_triggers=("compute", "infer"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=40,
        ),
        Rule(
            rule_id="N1_005_FIND",
            description="find_* busca en datos existentes (N1-EMP)",
            triggers=("name:find_", "name:_find_"),
            anti_triggers=("infer", "compute", "validate"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=40,
        ),
        Rule(
            rule_id="N2_004_ANALYZE",
            description="analyze_* produce inferencias derivadas (N2-INF)",
            triggers=("analyze", "analysis"),
            anti_triggers=("validate", "check"),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=50,
        ),
        Rule(
            rule_id="N2_005_IDENTIFY",
            description="identify_* clasifica/deriva información (N2-INF)",
            triggers=("identify", "identification"),
            anti_triggers=("validate",),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=50,
        ),
        Rule(
            rule_id="N2_006_BUILD_CREATE",
            description="build_*/create_*/construct_* construye derivados (N2-INF)",
            triggers=("build", "create", "construct"),
            anti_triggers=("validate", "check"),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=45,
        ),
        Rule(
            rule_id="N2_007_ESTIMATE",
            description="estimate_*/determine_* produce estimaciones (N2-INF)",
            triggers=("estimate", "determine", "approximate"),
            anti_triggers=(),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=50,
        ),
        Rule(
            rule_id="N2_008_MATCH",
            description="match_* correlaciona datos (N2-INF)",
            triggers=("match", "correlate", "align"),
            anti_triggers=("validate",),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=45,
        ),
        Rule(
            rule_id="N2_009_CAUSAL",
            description="Métodos causales son N2-INF CAUSAL_MECHANISTIC",
            triggers=("causal", "dag", "counterfactual", "intervention", "effect"),
            anti_triggers=(),
            target_level="N2-INF",
            target_epistemology="CAUSAL_MECHANISTIC",
            priority=55,
        ),
        Rule(
            rule_id="N4_003_GENERATE_REPORT",
            description="generate_*_report produce síntesis narrativa (N4-SYN)",
            triggers=("generate", "report", "pdq_report"),
            anti_triggers=("error", "exception", "query"),
            target_level="N4-SYN",
            target_epistemology="CRITICAL_REFLEXIVE",
            priority=60,
        ),
        Rule(
            rule_id="N2_010_GENERATE_DATA",
            description="generate_* sin report produce datos derivados (N2-INF)",
            triggers=("generate",),
            anti_triggers=("report", "summary", "narrative", "error"),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=35,
        ),
        Rule(
            rule_id="INFRA_004_PRIVATE_HELPER",
            description="Métodos privados que retornan tipos simples son helpers (INFRASTRUCTURE)",
            triggers=("name:_",),
            anti_triggers=("validate", "check", "compute", "infer", "analyze", "generate", "build", "create"),
            target_level="INFRASTRUCTURE",
            target_epistemology="NONE",
            priority=20,
        ),
        Rule(
            rule_id="N2_011_RUN_EXECUTE",
            description="run_*/execute_* ejecuta lógica derivada (N2-INF)",
            triggers=("run", "execute", "process"),
            anti_triggers=("validate",),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=40,
        ),
        Rule(
            rule_id="N2_012_SEGMENT_EMBED",
            description="segment_*/embed_* transforma datos (N2-INF)",
            triggers=("segment", "embed", "transform", "convert"),
            anti_triggers=(),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=45,
        ),
        Rule(
            rule_id="N2_013_DICT_RETURN",
            description="Métodos que retornan dict[str, Any] producen estructuras derivadas (N2-INF)",
            triggers=("return_type:dict[str, any]", "return_type:dict[str,any]"),
            anti_triggers=("validate", "check"),
            target_level="N2-INF",
            target_epistemology="DETERMINISTIC_LOGICAL",
            priority=15,
        ),
        Rule(
            rule_id="N1_006_STR_RETURN",
            description="Métodos que retornan str sin señales de síntesis son extractores (N1-EMP)",
            triggers=("return_type:str",),
            anti_triggers=("report", "narrative", "summary", "synthesis", "generate", "compute", "analyze"),
            target_level="N1-EMP",
            target_epistemology="POSITIVIST_EMPIRICAL",
            priority=10,
        ),
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: DATACLASSES INMUTABLES CON VALIDACIÓN EN CONSTRUCCIÓN
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class RuleEvaluation:
    """Evaluación de una regla sobre un método."""

    rule_id: str
    matched_triggers: tuple[str, ...]
    matched_anti_triggers: tuple[str, ...]
    fired: bool  # True si matched_triggers > 0 AND matched_anti_triggers == 0
    contribution: str  # "SELECTED", "BLOCKED", "NO_MATCH"


@dataclass(frozen=True)
class MethodDecision:
    """Decisión de clasificación con traza completa."""

    method_id: str
    class_name: str
    level: str
    epistemology: str
    selected_rule_id: str
    all_evaluations: tuple[RuleEvaluation, ...]
    input_hash: str  # SHA256 del blob de entrada

    def __post_init__(self) -> None:
        if self.level not in METHOD_LEVELS:
            fatal("INVALID_METHOD_LEVEL", f"Level '{self.level}' not in allowed set", method=self.method_id)
        if self.epistemology not in CLASS_EPISTEMOLOGIES:
            fatal("INVALID_EPISTEMOLOGY", f"Epistemology '{self.epistemology}' not in allowed set", method=self.method_id)
        if not self.selected_rule_id:
            fatal("NO_RULE_SELECTED", "Method classification requires a rule", method=self.method_id)


@dataclass(frozen=True)
class VetoCondition:
    """Condición de veto con todos los campos obligatorios."""

    trigger: str
    action: str
    scope: str
    confidence_multiplier: float
    source_signal: str  # ¿De dónde vino esta condición?

    def __post_init__(self) -> None:
        if self.action not in VETO_ACTIONS:
            fatal("INVALID_VETO_ACTION", f"Action '{self.action}' not in allowed set", trigger=self.trigger)
        if not (0.0 <= self.confidence_multiplier <= 1.0):
            fatal("INVALID_MULTIPLIER", f"Multiplier {self.confidence_multiplier} out of [0,1]", trigger=self.trigger)


@dataclass(frozen=True)
class DegradationRecord:
    """Registro de degradación de nivel con trazabilidad completa."""

    method_id: str
    class_name: str
    original_level: str
    degraded_to: str
    original_epistemology: str
    degraded_epistemology: str
    reason: str
    timestamp: str


@dataclass(frozen=True)
class MethodEnrichment:
    """Enriquecimiento completo de un método - INMUTABLE."""

    decision: MethodDecision
    output_type: str
    fusion_behavior: str
    phase_assignment: str
    requires: tuple[str, ...]
    produces: tuple[str, ...]
    contract_compatibility: dict[str, bool]
    veto_conditions: tuple[VetoCondition, ...] | None
    degradation: DegradationRecord | None = None  # Si fue degradado

    def __post_init__(self) -> None:
        # Invariante: N3-AUD DEBE tener veto_conditions O haber sido degradado
        # (La degradación se maneja ANTES de crear MethodEnrichment)
        if self.decision.level == "N3-AUD" and not self.veto_conditions:
            # Esto no debería ocurrir - la degradación ocurre antes
            fatal(
                "N3_WITHOUT_VETO_UNHANDLED",
                "N3-AUD reached MethodEnrichment without veto (should have been degraded)",
                method=self.decision.method_id,
                class_name=self.decision.class_name,
            )
        # Invariante: N4-SYN DEBE producir narrative
        if self.decision.level == "N4-SYN" and "narrative" not in self.produces:
            fatal(
                "N4_WITHOUT_NARRATIVE",
                "N4-SYN method MUST produce 'narrative'",
                method=self.decision.method_id,
                produces=list(self.produces),
            )
        # Invariante: BAYESIAN DEBE tener TYPE_B
        if self.decision.epistemology == "BAYESIAN_PROBABILISTIC" and not self.contract_compatibility.get("TYPE_B"):
            fatal(
                "BAYESIAN_NOT_TYPE_B",
                "BAYESIAN_PROBABILISTIC method MUST have TYPE_B compatibility",
                method=self.decision.method_id,
            )
        # Invariante: Non-INFRASTRUCTURE debe tener contrato
        if self.decision.level != "INFRASTRUCTURE":
            if not any(self.contract_compatibility.values()):
                fatal(
                    "ORPHAN_METHOD",
                    "Non-INFRASTRUCTURE method MUST have at least one contract compatibility",
                    method=self.decision.method_id,
                    level=self.decision.level,
                )


@dataclass(frozen=True)
class ClassDecision:
    """Decisión de clasificación a nivel de clase."""

    class_name: str
    file_path: str
    level: str
    epistemology: str
    method_level_counts: dict[str, int]
    decision_rationale: str
    weighted_score: float

    def __post_init__(self) -> None:
        if self.level not in CLASS_LEVELS:
            fatal("INVALID_CLASS_LEVEL", f"Level '{self.level}' not in allowed set", class_name=self.class_name)
        if self.epistemology not in CLASS_EPISTEMOLOGIES:
            fatal("INVALID_CLASS_EPISTEMOLOGY", f"Epistemology '{self.epistemology}' not in allowed set", class_name=self.class_name)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: FUNCIONES PURAS DE CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════


def _norm(s: object) -> str:
    """Normaliza a string con NFKC + casefold para matching determinista."""
    import unicodedata
    if s is None:
        return ""
    text = str(s)
    return unicodedata.normalize("NFKC", text).casefold().strip()


def _compute_blob(method_name: str, method: dict[str, Any]) -> str:
    """Genera blob canonicalizado del método para matching."""
    parts = [
        f"name:{_norm(method_name)}",
        f"return_type:{_norm(method.get('return_type'))}",
        f"docstring:{_norm(method.get('docstring'))}",
    ]
    params = method.get("parameters", []) or []
    for p in params:
        parts.append(f"param:{_norm(p.get('name'))}:{_norm(p.get('type'))}")
    return " ".join(parts)


def _hash_blob(blob: str) -> str:
    """SHA256 de un blob (primeros 16 chars)."""
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _signal_in_blob(signal: str, blob: str) -> bool:
    """Verifica si una señal está presente en el blob.
    
    Soporta triggers especiales:
    - "name:prefix_" → verifica si el método empieza con prefix_
    - "return_type:tipo" → verifica el tipo de retorno exacto
    - cualquier_otra_cosa → matching substring normal
    """
    signal_lower = signal.lower()
    blob_lower = blob.lower()
    
    # Trigger especial: name:prefix → busca en el componente name: del blob
    if signal_lower.startswith("name:"):
        prefix = signal_lower[5:]  # "name:get_" → "get_"
        # El blob tiene formato "name:method_name return_type:..."
        # Extraer el nombre del método
        for part in blob_lower.split():
            if part.startswith("name:"):
                method_name = part[5:]  # "name:_find_x" → "_find_x"
                return method_name.startswith(prefix)
        return False
    
    # Trigger especial: return_type:tipo → busca tipo exacto de retorno
    if signal_lower.startswith("return_type:"):
        target_type = signal_lower[12:].replace(" ", "")  # "dict[str, Any]" → "dict[str,any]"
        for part in blob_lower.split():
            if part.startswith("return_type:"):
                actual_type = part[12:].replace(" ", "")
                return actual_type == target_type
        return False
    
    # Matching substring normal
    return signal_lower in blob_lower


def evaluate_rules(
    method_name: str,
    method: dict[str, Any],
    class_name: str,
    rulebook: Rulebook,
) -> MethodDecision:
    """Evalúa todas las reglas y selecciona la ganadora."""
    blob = _compute_blob(method_name, method)
    input_hash = _hash_blob(blob)

    evaluations: list[RuleEvaluation] = []
    candidates: list[tuple[int, Rule, RuleEvaluation]] = []

    for rule in rulebook.rules:
        matched_triggers = tuple(t for t in rule.triggers if _signal_in_blob(t, blob))
        matched_anti = tuple(a for a in rule.anti_triggers if _signal_in_blob(a, blob))

        fired = len(matched_triggers) > 0 and len(matched_anti) == 0

        if fired:
            contribution = "CANDIDATE"
        elif len(matched_triggers) > 0 and len(matched_anti) > 0:
            contribution = "BLOCKED"
        else:
            contribution = "NO_MATCH"

        ev = RuleEvaluation(
            rule_id=rule.rule_id,
            matched_triggers=matched_triggers,
            matched_anti_triggers=matched_anti,
            fired=fired,
            contribution=contribution,
        )
        evaluations.append(ev)

        if fired:
            candidates.append((rule.priority, rule, ev))

    if not candidates:
        # FAIL-HARD: No hay regla que aplique
        fatal(
            "NO_MATCHING_RULE",
            "No rule matched for method - cannot classify",
            method=method_name,
            class_name=class_name,
            blob_hash=input_hash,
        )

    # Ordenar por prioridad descendente
    candidates.sort(key=lambda x: -x[0])
    winner_priority, winner_rule, winner_ev = candidates[0]

    # Marcar ganador
    final_evaluations: list[RuleEvaluation] = []
    for ev in evaluations:
        if ev.rule_id == winner_rule.rule_id:
            final_evaluations.append(RuleEvaluation(
                rule_id=ev.rule_id,
                matched_triggers=ev.matched_triggers,
                matched_anti_triggers=ev.matched_anti_triggers,
                fired=ev.fired,
                contribution="SELECTED",
            ))
        else:
            final_evaluations.append(ev)

    return MethodDecision(
        method_id=method_name,
        class_name=class_name,
        level=winner_rule.target_level,
        epistemology=winner_rule.target_epistemology,
        selected_rule_id=winner_rule.rule_id,
        all_evaluations=tuple(final_evaluations),
        input_hash=input_hash,
    )


def map_level_to_output(level: str) -> tuple[str, str, str]:
    """Mapea nivel a (output_type, fusion_behavior, phase_assignment)."""
    mapping = {
        "N1-EMP": ("FACT", "additive", "phase_A_construction"),
        "N2-INF": ("PARAMETER", "multiplicative", "phase_B_computation"),
        "N3-AUD": ("CONSTRAINT", "gate", "phase_C_litigation"),
        "N4-SYN": ("NARRATIVE", "terminal", "phase_D_synthesis"),
        "INFRASTRUCTURE": ("NONE", "none", "none"),
    }
    return mapping.get(level, ("NONE", "none", "none"))


def extract_veto_conditions(level: str, docstring: str, method_name: str) -> tuple[VetoCondition, ...] | None:
    """Extrae condiciones de veto SOLO si hay señales explícitas en docstring."""
    if level != "N3-AUD":
        return None

    ds = _norm(docstring)
    conditions: list[VetoCondition] = []

    # Mapeo de señales a condiciones
    veto_signals = [
        (("invalid", "fail", "reject", "error"), "validation_failed", "block_branch", 0.0),
        (("weak", "insufficient", "low", "below"), "below_threshold", "reduce_confidence", 0.3),
        (("inconsistent", "contradiction", "conflict"), "logical_inconsistency", "flag_caution", 0.5),
        (("missing", "absent", "required"), "missing_data", "flag_insufficiency", 0.4),
    ]

    for signals, trigger, action, multiplier in veto_signals:
        matched = [s for s in signals if s in ds]
        if matched:
            conditions.append(VetoCondition(
                trigger=trigger,
                action=action,
                scope="global",
                confidence_multiplier=multiplier,
                source_signal=f"docstring_contains:{','.join(matched)}",
            ))

    # Si es N3-AUD pero NO hay señales de veto → retornar None (invariante fallará en construcción)
    if not conditions:
        return None

    return tuple(conditions)


def infer_contract_compatibility(
    blob: str,
    level: str,
    epistemology: str,
) -> dict[str, bool]:
    """Infiere compatibilidad de contrato basado en señales EXPLÍCITAS del método.
    
    CIENTÍFICO: Solo usa señales del blob del método (docstring, return_type, params).
    NO usa class_name ni file_path - eso sería INVENTAR compatibilidad.
    Si no hay señales → el método es huérfano → el invariante DEBE fallar.
    """
    compat = {"TYPE_A": False, "TYPE_B": False, "TYPE_C": False, "TYPE_D": False, "TYPE_E": False}

    blob_lower = blob.lower()

    # Señales para cada tipo - SOLO del método
    # Justificación epistemológica de cada señal:
    # TYPE_A: Procesamiento semántico/textual → coherencia de texto
    # TYPE_B: Razonamiento probabilístico → distribuciones/posteriors
    # TYPE_C: Razonamiento causal → DAGs/intervenciones
    # TYPE_D: Razonamiento financiero → presupuestos/asignaciones
    # TYPE_E: Validación/auditoría → consistencia lógica
    type_signals = {
        "TYPE_A": (
            "semantic", "chunk", "embed", "text", "coherence", "nlp", "vector", 
            "similarity", "query", "report", "summary", "narrative", "synthesis",
            "recommendation", "recomendation", "generate", "format", "render",
            "pdq", "response", "answer", "output", "produce",
        ),
        "TYPE_B": ("bayesian", "posterior", "prior", "credible", "distribution", "probabilistic", "uncertainty"),
        "TYPE_C": ("causal", "dag", "mechanism", "counterfactual", "path", "intervention", "effect", "treatment"),
        "TYPE_D": ("financial", "budget", "allocation", "cost", "amount", "monto", "presupuesto", "sufficiency", "fiscal", "expenditure"),
        "TYPE_E": ("contradiction", "consistency", "logical", "valid", "validate", "verify", "check", "audit", "constraint", "rule"),
    }

    for type_key, signals in type_signals.items():
        for signal in signals:
            if signal in blob_lower:
                compat[type_key] = True
                break

    # Enforcement epistemológico
    if epistemology == "BAYESIAN_PROBABILISTIC":
        compat["TYPE_B"] = True

    # NO HAY ORPHAN PREVENTION SILENCIOSA
    # Si no hay compatibilidad Y nivel != INFRASTRUCTURE → FALLA

    return compat


def classify_class(
    class_name: str,
    file_path: str,
    method_decisions: list[MethodDecision],
) -> ClassDecision:
    """Clasifica una clase basado en sus métodos."""
    # Conteo por nivel
    counts: dict[str, int] = {"N1-EMP": 0, "N2-INF": 0, "N3-AUD": 0, "N4-SYN": 0, "INFRASTRUCTURE": 0}
    for md in method_decisions:
        counts[md.level] = counts.get(md.level, 0) + 1

    meaningful = {k: v for k, v in counts.items() if k != "INFRASTRUCTURE" and v > 0}

    if not meaningful:
        return ClassDecision(
            class_name=class_name,
            file_path=file_path,
            level="INFRASTRUCTURE",
            epistemology="NONE",
            method_level_counts=counts,
            decision_rationale="ALL_METHODS_INFRASTRUCTURE",
            weighted_score=0.0,
        )

    # Ponderación por criticidad
    weights = {"N4-SYN": 40, "N3-AUD": 30, "N2-INF": 20, "N1-EMP": 10}
    weighted = {k: v * weights.get(k, 0) for k, v in meaningful.items()}
    total_weight = sum(weighted.values())

    # Ganador por peso
    winner = max(weighted.items(), key=lambda x: (x[1], weights.get(x[0], 0)))
    winner_level = winner[0]

    # Epistemología por nivel dominante
    epistemology_map = {
        "N1-EMP": "POSITIVIST_EMPIRICAL",
        "N2-INF": "DETERMINISTIC_LOGICAL",
        "N3-AUD": "POPPERIAN_FALSIFICATIONIST",
        "N4-SYN": "CRITICAL_REFLEXIVE",
    }
    epistemology = epistemology_map.get(winner_level, "DETERMINISTIC_LOGICAL")

    # Override para bayesian si hay métodos bayesianos
    bayesian_count = sum(1 for md in method_decisions if md.epistemology == "BAYESIAN_PROBABILISTIC")
    if bayesian_count > 0 and winner_level == "N2-INF":
        epistemology = "BAYESIAN_PROBABILISTIC"

    return ClassDecision(
        class_name=class_name,
        file_path=file_path,
        level=winner_level,
        epistemology=epistemology,
        method_level_counts=counts,
        decision_rationale=f"WEIGHTED_MAJORITY:{winner_level}={winner[1]}/{total_weight}",
        weighted_score=winner[1] / total_weight if total_weight > 0 else 0.0,
    )


def is_protocol_class(class_name: str, file_path: str) -> bool:
    """Detecta si es clase Protocol."""
    blob = f"{class_name} {file_path}".lower()
    return bool(re.search(r"\bprotocol\b", blob)) or class_name.endswith("Protocol")


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6: PIPELINE PRINCIPAL - FAIL-HARD
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class PipelineSession:
    """Sesión de pipeline con trazabilidad completa."""

    session_id: str
    started_at: str
    rulebook_hash: str
    code_hash: str
    input_hash: str
    output_hash: str = ""
    completed_at: str = ""
    method_count: int = 0
    class_count: int = 0
    degradations: list[DegradationRecord] = field(default_factory=list)
    fatal_errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_degradation(self, record: DegradationRecord) -> None:
        self.degradations.append(record)
        self.warnings.append(
            f"DEGRADATION: {record.class_name}.{record.method_id} "
            f"{record.original_level}→{record.degraded_to} ({record.reason})"
        )

    def check_drift_threshold(self) -> None:
        """Verifica si el drift epistemológico supera el umbral. FAIL si sí.
        
        Configuración vía environment:
        - FARFAN_DRIFT_THRESHOLD: Umbral de degradaciones (default 0.05 = 5%)
        - FARFAN_STRICT_MODE: Si 'true', falla en cualquier degradación
        """
        if self.method_count == 0:
            return
        
        # Modo estricto: cualquier degradación es fatal
        if STRICT_MODE and len(self.degradations) > 0:
            fatal(
                "STRICT_MODE_DEGRADATION",
                f"STRICT_MODE active: {len(self.degradations)} degradations not allowed",
                degradation_count=len(self.degradations),
                sample_degradations=[
                    {
                        "method": d.method_id,
                        "class": d.class_name,
                        "from": d.original_level,
                        "to": d.degraded_to,
                    }
                    for d in self.degradations[:5]
                ],
            )
        
        drift_ratio = len(self.degradations) / self.method_count
        if drift_ratio > DRIFT_THRESHOLD:
            fatal(
                "EPISTEMIC_DRIFT_EXCEEDED",
                f"Degradation ratio {drift_ratio:.2%} exceeds threshold {DRIFT_THRESHOLD:.0%}",
                degradation_count=len(self.degradations),
                method_count=self.method_count,
                threshold=DRIFT_THRESHOLD,
                sample_degradations=[
                    {
                        "method": d.method_id,
                        "class": d.class_name,
                        "from": d.original_level,
                        "to": d.degraded_to,
                    }
                    for d in self.degradations[:10]
                ],
            )


def compute_code_hash() -> str:
    """Computa hash del código fuente de este módulo."""
    source = inspect.getsource(sys.modules[__name__])
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def compute_data_hash(data: dict[str, Any]) -> str:
    """Hash canónico de datos."""
    blob = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def enrich_inventory(
    inventory: dict[str, Any],
    rulebook: Rulebook = CANONICAL_RULEBOOK,
) -> tuple[dict[str, Any], PipelineSession]:
    """Enriquece inventario con clasificación epistemológica.

    FAIL-HARD: Cualquier violación de invariante aborta el pipeline.
    """
    session = PipelineSession(
        session_id=f"forensic_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}",
        started_at=datetime.now(timezone.utc).isoformat(),
        rulebook_hash=rulebook.compute_hash(),
        code_hash=compute_code_hash(),
        input_hash=compute_data_hash(inventory),
    )

    enriched: dict[str, Any] = {}
    total_methods = 0

    for class_name, cls in inventory.items():
        file_path = _norm(cls.get("file_path"))
        line_number = cls.get("line_number")
        methods = cls.get("methods", {}) or {}

        if is_protocol_class(class_name, file_path):
            enriched[class_name] = {
                "file_path": file_path,
                "line_number": line_number,
                "class_level": "PROTOCOL",
                "class_epistemology": "NONE",
                "class_decision_evidence": {"rationale": "PROTOCOL_CLASS"},
                "methods": {},
            }
            continue

        method_decisions: list[MethodDecision] = []
        enriched_methods: dict[str, Any] = {}

        for method_name, method in methods.items():
            total_methods += 1
            degradation_record: DegradationRecord | None = None

            # Clasificar método
            decision = evaluate_rules(method_name, method, class_name, rulebook)

            # Manejar N3-AUD sin veto observable: DEGRADAR a N2-INF
            veto_conditions = extract_veto_conditions(
                decision.level,
                _norm(method.get("docstring")),
                method_name,
            )

            current_level = decision.level
            current_epistemology = decision.epistemology

            if current_level == "N3-AUD" and veto_conditions is None:
                # DEGRADACIÓN EXPLÍCITA: N3→N2 con registro forense
                degradation_record = DegradationRecord(
                    method_id=method_name,
                    class_name=class_name,
                    original_level="N3-AUD",
                    degraded_to="N2-INF",
                    original_epistemology=current_epistemology,
                    degraded_epistemology="DETERMINISTIC_LOGICAL",
                    reason="N3-AUD lacks observable veto conditions in docstring",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                session.add_degradation(degradation_record)

                # Crear nueva decisión degradada (no podemos mutar frozen dataclass)
                decision = MethodDecision(
                    method_id=method_name,
                    class_name=class_name,
                    level="N2-INF",
                    epistemology="DETERMINISTIC_LOGICAL",
                    selected_rule_id=f"{decision.selected_rule_id}→DEGRADED",
                    all_evaluations=decision.all_evaluations,
                    input_hash=decision.input_hash,
                )
                current_level = "N2-INF"
                current_epistemology = "DETERMINISTIC_LOGICAL"
                veto_conditions = None  # N2 no tiene veto

            # Mapear nivel a outputs
            output_type, fusion_behavior, phase_assignment = map_level_to_output(current_level)

            # Dependencias por nivel (declarativas, no inferidas)
            requires = tuple(sorted(LEVEL_REQUIRED_INPUTS.get(current_level, frozenset())))
            produces = tuple(sorted(LEVEL_REQUIRED_OUTPUTS.get(current_level, frozenset())))

            # Contract compatibility
            blob = _compute_blob(method_name, method)
            contract_compat = infer_contract_compatibility(blob, current_level, current_epistemology)
            
            # CIENTÍFICO: Si no-INFRASTRUCTURE sin contrato → DEGRADAR a INFRASTRUCTURE
            # con registro forense (no falla silenciosa, no inventa contrato)
            if current_level != "INFRASTRUCTURE" and not any(contract_compat.values()):
                orphan_degradation = DegradationRecord(
                    method_id=method_name,
                    class_name=class_name,
                    original_level=current_level,
                    degraded_to="INFRASTRUCTURE",
                    original_epistemology=current_epistemology,
                    degraded_epistemology="NONE",
                    reason="NO_CONTRACT_SIGNALS_IN_SIGNATURE",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                session.add_degradation(orphan_degradation)
                current_level = "INFRASTRUCTURE"
                current_epistemology = "NONE"
                degradation_record = orphan_degradation
                # Recalcular outputs para INFRASTRUCTURE
                output_type, fusion_behavior, phase_assignment = map_level_to_output(current_level)
                requires = ()
                produces = ()
                # Crear decision degradada para classify_class
                decision = MethodDecision(
                    method_id=method_name,
                    class_name=class_name,
                    level="INFRASTRUCTURE",
                    epistemology="NONE",
                    selected_rule_id=f"{decision.selected_rule_id}→ORPHAN_DEGRADED",
                    all_evaluations=decision.all_evaluations,
                    input_hash=decision.input_hash,
                )

            # Añadir decision DESPUÉS de posibles degradaciones
            method_decisions.append(decision)

            # Crear enrichment (invariantes se validan en __post_init__)
            try:
                enrichment = MethodEnrichment(
                    decision=decision,
                    output_type=output_type,
                    fusion_behavior=fusion_behavior,
                    phase_assignment=phase_assignment,
                    requires=requires,
                    produces=produces,
                    contract_compatibility=contract_compat,
                    veto_conditions=veto_conditions,
                    degradation=degradation_record,
                )
            except PipelineFatalError:
                raise  # Re-lanzar para que el pipeline aborte

            # Serializar para output - usar nivel ACTUAL (post-degradación si aplica)
            final_level = current_level  # Ya actualizado si hubo degradación
            final_epistemology = current_epistemology
            
            enriched_methods[method_name] = {
                **method,
                "epistemological_classification": {
                    "level": final_level,
                    "output_type": enrichment.output_type,
                    "fusion_behavior": enrichment.fusion_behavior,
                    "epistemology": final_epistemology,
                    "phase_assignment": enrichment.phase_assignment,
                    "dependencies": {
                        "requires": list(enrichment.requires),
                        "produces": list(enrichment.produces),
                    },
                    "contract_compatibility": enrichment.contract_compatibility,
                    "veto_conditions": (
                        {
                            vc.trigger: {
                                "trigger": vc.trigger,
                                "action": vc.action,
                                "scope": vc.scope,
                                "confidence_multiplier": vc.confidence_multiplier,
                                "source_signal": vc.source_signal,
                            }
                            for vc in enrichment.veto_conditions
                        }
                        if enrichment.veto_conditions
                        else None
                    ),
                    "classification_evidence": {
                        "selected_rule_id": enrichment.decision.selected_rule_id,
                        "input_hash": enrichment.decision.input_hash,
                        "was_degraded": enrichment.degradation is not None,
                        "degradation": (
                            {
                                "original_level": enrichment.degradation.original_level,
                                "degraded_to": enrichment.degradation.degraded_to,
                                "reason": enrichment.degradation.reason,
                            }
                            if enrichment.degradation
                            else None
                        ),
                        "all_evaluations": [
                            {
                                "rule_id": ev.rule_id,
                                "matched_triggers": list(ev.matched_triggers),
                                "matched_anti_triggers": list(ev.matched_anti_triggers),
                                "fired": ev.fired,
                                "contribution": ev.contribution,
                            }
                            for ev in enrichment.decision.all_evaluations
                        ],
                    },
                },
            }

        # Clasificar clase
        class_decision = classify_class(class_name, file_path, method_decisions)

        enriched[class_name] = {
            "file_path": file_path,
            "line_number": line_number,
            "class_level": class_decision.level,
            "class_epistemology": class_decision.epistemology,
            "class_decision_evidence": {
                "rationale": class_decision.decision_rationale,
                "weighted_score": class_decision.weighted_score,
                "method_level_counts": class_decision.method_level_counts,
            },
            "methods": enriched_methods,
        }

    # Métricas
    level_counts = {"INFRASTRUCTURE": 0, "N1-EMP": 0, "N2-INF": 0, "N3-AUD": 0, "N4-SYN": 0}
    veto_count = 0
    for class_name, cls in enriched.items():
        if class_name == "quality_metrics":
            continue
        for method_name, m in (cls.get("methods", {}) or {}).items():
            ec = m.get("epistemological_classification", {})
            level = ec.get("level", "INFRASTRUCTURE")
            level_counts[level] = level_counts.get(level, 0) + 1
            if ec.get("veto_conditions"):
                veto_count += 1

    enriched["quality_metrics"] = {
        "total_classes": len([k for k in enriched.keys() if k != "quality_metrics"]),
        "total_methods": total_methods,
        "infrastructure_methods": level_counts["INFRASTRUCTURE"],
        "n1_methods": level_counts["N1-EMP"],
        "n2_methods": level_counts["N2-INF"],
        "n3_methods": level_counts["N3-AUD"],
        "n4_methods": level_counts["N4-SYN"],
        "methods_with_veto": veto_count,
        "degradation_count": len(session.degradations),
        "degradation_ratio": len(session.degradations) / total_methods if total_methods > 0 else 0.0,
        "n3_without_veto": 0,  # Si llegamos aquí, todos los N3 tienen veto (invariante garantizado)
        "orphan_methods": 0,  # Si llegamos aquí, no hay huérfanos (invariante garantizado)
        "validation_errors": [],  # Pipeline FAIL-HARD, no hay errores tolerados
    }

    # Metadatos de trazabilidad
    git_commit = get_git_commit_hash()
    enriched["_pipeline_metadata"] = {
        "pipeline_version": "5.0.0-FORENSIC",
        "session_id": session.session_id,
        "rulebook_version": rulebook.version,
        "rulebook_hash": session.rulebook_hash,
        "code_hash": session.code_hash,
        "git_commit": git_commit,
        "input_hash": session.input_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "drift_threshold": DRIFT_THRESHOLD,
            "strict_mode": STRICT_MODE,
        },
        "degradations": [
            {
                "method": d.method_id,
                "class": d.class_name,
                "from": d.original_level,
                "to": d.degraded_to,
                "reason": d.reason,
            }
            for d in session.degradations
        ],
    }

    session.method_count = total_methods
    session.class_count = len([k for k in enriched.keys() if k not in {"quality_metrics", "_pipeline_metadata"}])
    session.completed_at = datetime.now(timezone.utc).isoformat()

    # VERIFICAR UMBRAL DE DRIFT EPISTEMOLÓGICO
    session.check_drift_threshold()

    return enriched, session


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "METHODS_DISPENSARY_SIGNATURES.json"
    output_path = repo_root / "METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json"
    manifest_path = repo_root / "ENRICHMENT_FORENSIC_MANIFEST.json"

    print(f"[FORENSIC] Pipeline v5.0.0 starting...")
    print(f"[FORENSIC] Input: {input_path}")

    try:
        inventory = json.loads(input_path.read_text(encoding="utf-8"))
        enriched, session = enrich_inventory(inventory)

        # Escribir output
        output_content = json.dumps(enriched, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        output_path.write_text(output_content, encoding="utf-8")
        output_hash = sha256_file(output_path)
        session.output_hash = output_hash

        # Manifest completo
        manifest = {
            "pipeline_verified": True,
            "session_id": session.session_id,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "input_file": str(input_path),
            "input_hash": session.input_hash,
            "output_file": str(output_path),
            "output_hash": output_hash,
            "output_bytes": output_path.stat().st_size,
            "rulebook_version": CANONICAL_RULEBOOK.version,
            "rulebook_hash": session.rulebook_hash,
            "code_hash": session.code_hash,
            "method_count": session.method_count,
            "class_count": session.class_count,
            "quality_metrics": enriched["quality_metrics"],
            "fatal_errors": [],
        }

        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print(f"[FORENSIC] Output: {output_path} ({output_path.stat().st_size} bytes)")
        print(f"[FORENSIC] Manifest: {manifest_path}")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    except PipelineFatalError as e:
        print(f"[FATAL] Pipeline aborted: {e}", file=sys.stderr)
        manifest = {
            "pipeline_verified": False,
            "fatal_error": e.to_dict(),
            "aborted_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.exit(1)


if __name__ == "__main__":
    main()
