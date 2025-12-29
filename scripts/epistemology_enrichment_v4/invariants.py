"""Invariantes y aserciones que deben cumplirse durante enriquecimiento.

Si una aserción falla, el pipeline DEBE abortar ruidosamente.

Versión: 2.0.0
"""

from __future__ import annotations

from typing import Any

from .constants import CLASS_EPISTEMOLOGIES, CLASS_LEVELS, METHOD_LEVELS


class InvariantViolationError(Exception):
    """Error crítico: invariante violado durante enriquecimiento."""

    def __init__(self, invariant_id: str, message: str, context: dict[str, Any]) -> None:
        self.invariant_id = invariant_id
        self.context = context
        super().__init__(f"[{invariant_id}] {message} | Context: {context}")


def assert_valid_method_level(level: str, method_id: str, class_name: str) -> None:
    if level not in METHOD_LEVELS:
        raise InvariantViolationError(
            "INV_001_INVALID_METHOD_LEVEL",
            f"Level '{level}' not in allowed set",
            {"method_id": method_id, "class_name": class_name, "allowed": list(METHOD_LEVELS)},
        )


def assert_valid_class_level(level: str, class_name: str) -> None:
    if level not in CLASS_LEVELS:
        raise InvariantViolationError(
            "INV_002_INVALID_CLASS_LEVEL",
            f"Level '{level}' not in allowed set",
            {"class_name": class_name, "allowed": list(CLASS_LEVELS)},
        )


def assert_valid_epistemology(epistemology: str, entity_id: str) -> None:
    if epistemology not in CLASS_EPISTEMOLOGIES:
        raise InvariantViolationError(
            "INV_003_INVALID_EPISTEMOLOGY",
            f"Epistemology '{epistemology}' not in allowed set",
            {"entity_id": entity_id, "allowed": list(CLASS_EPISTEMOLOGIES)},
        )


def assert_n3_has_veto_or_degraded(
    level: str,
    veto_conditions: dict[str, Any] | None,
    was_degraded: bool,
    method_id: str,
    class_name: str,
) -> None:
    """N3-AUD debe tener veto observable, o haber sido degradado a N2."""
    if level == "N3-AUD" and veto_conditions is None and not was_degraded:
        raise InvariantViolationError(
            "INV_004_N3_WITHOUT_VETO",
            "N3-AUD method has no veto_conditions and was not degraded",
            {"method_id": method_id, "class_name": class_name},
        )


def assert_n4_produces_narrative(
    level: str,
    produces: list[str],
    method_id: str,
    class_name: str,
) -> None:
    """N4-SYN debe producir 'narrative'."""
    if level == "N4-SYN" and "narrative" not in produces:
        raise InvariantViolationError(
            "INV_005_N4_WITHOUT_NARRATIVE",
            "N4-SYN method does not produce 'narrative'",
            {"method_id": method_id, "class_name": class_name, "produces": produces},
        )


def assert_bayesian_has_type_b(
    epistemology: str,
    contract_compatibility: dict[str, bool],
    method_id: str,
    class_name: str,
) -> None:
    """BAYESIAN_PROBABILISTIC debe tener TYPE_B=True."""
    if epistemology == "BAYESIAN_PROBABILISTIC" and not contract_compatibility.get("TYPE_B"):
        raise InvariantViolationError(
            "INV_006_BAYESIAN_NOT_TYPE_B",
            "BAYESIAN_PROBABILISTIC method does not have TYPE_B compatibility",
            {"method_id": method_id, "class_name": class_name, "compat": contract_compatibility},
        )


def assert_non_infrastructure_has_contract(
    level: str,
    contract_compatibility: dict[str, bool],
    method_id: str,
    class_name: str,
) -> None:
    """Métodos no-INFRASTRUCTURE deben tener al menos un TYPE_* = True."""
    if level != "INFRASTRUCTURE":
        if not any(contract_compatibility.get(k) for k in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]):
            raise InvariantViolationError(
                "INV_007_ORPHAN_METHOD",
                "Non-INFRASTRUCTURE method has no contract compatibility",
                {"method_id": method_id, "class_name": class_name, "compat": contract_compatibility},
            )


def assert_matched_signals_not_empty(
    level: str,
    matched_signals: tuple[str, ...] | list[str],
    method_id: str,
    class_name: str,
) -> None:
    """Todo método clasificado debe tener al menos una señal matched."""
    if not matched_signals:
        raise InvariantViolationError(
            "INV_008_NO_MATCHED_SIGNALS",
            "Method has no matched_signals (untraceable decision)",
            {"method_id": method_id, "class_name": class_name, "level": level},
        )


def assert_decision_path_not_empty(
    decision_path: str,
    method_id: str,
    class_name: str,
) -> None:
    """Toda decisión debe tener un decision_path no vacío."""
    if not decision_path or not decision_path.strip():
        raise InvariantViolationError(
            "INV_009_EMPTY_DECISION_PATH",
            "Method has empty decision_path (untraceable)",
            {"method_id": method_id, "class_name": class_name},
        )


def run_all_method_invariants(
    method_id: str,
    class_name: str,
    level: str,
    epistemology: str,
    produces: list[str],
    veto_conditions: dict[str, Any] | None,
    contract_compatibility: dict[str, bool],
    matched_signals: tuple[str, ...] | list[str],
    decision_path: str,
    was_degraded: bool,
) -> list[dict[str, Any]]:
    """Ejecuta todas las invariantes de método. Retorna lista de violaciones (vacía si OK)."""

    violations: list[dict[str, Any]] = []

    checks = [
        (assert_valid_method_level, (level, method_id, class_name)),
        (assert_valid_epistemology, (epistemology, f"{class_name}.{method_id}")),
        (assert_n3_has_veto_or_degraded, (level, veto_conditions, was_degraded, method_id, class_name)),
        (assert_n4_produces_narrative, (level, produces, method_id, class_name)),
        (assert_bayesian_has_type_b, (epistemology, contract_compatibility, method_id, class_name)),
        (assert_non_infrastructure_has_contract, (level, contract_compatibility, method_id, class_name)),
        (assert_matched_signals_not_empty, (level, matched_signals, method_id, class_name)),
        (assert_decision_path_not_empty, (decision_path, method_id, class_name)),
    ]

    for check_fn, args in checks:
        try:
            check_fn(*args)  # type: ignore[arg-type]
        except InvariantViolationError as e:
            violations.append({
                "invariant_id": e.invariant_id,
                "message": str(e),
                "context": e.context,
            })

    return violations
