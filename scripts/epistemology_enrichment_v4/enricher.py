"""Enriquecedor epistemológico del inventario de métodos.

Versión: 2.1.0 - FORENSIC EDITION
- Consume ClassDecisionRecord y MethodDecision con trazas completas.
- Tracking explícito de degradaciones N3→N2 como warnings.
- Integración con EnrichmentSession para auditoría forense.
- Invariantes ejecutadas por método, violaciones registradas.
- matched_signals y anti_matched_signals para trazabilidad completa.
"""

from __future__ import annotations

import logging
from typing import Any

from .audit_log import ClassDecisionLog, DegradationWarning, EnrichmentSession, MethodDecisionLog, start_session
from .class_level import infer_class_epistemology, infer_class_level, is_protocol_class
from .classifier import classify_infrastructure_subtype, classify_method
from .constants import CLASS_EPISTEMOLOGIES, CLASS_LEVELS, METHOD_LEVELS
from .infer import infer_contract_compatibility, infer_produces, infer_requires, infer_veto_conditions, map_level_to_output
from .invariants import run_all_method_invariants
from .utils import method_signature_blob, norm

logger = logging.getLogger(__name__)


def enrich_inventory(
    inventory: dict[str, Any],
    *,
    fail_on_invariant_violation: bool = False,
) -> tuple[dict[str, Any], EnrichmentSession]:
    """Enriquece el inventario con clasificación epistemológica y auditoría forense.

    Args:
        inventory: Inventario crudo de clases y métodos.
        fail_on_invariant_violation: Si True, lanza excepción en primera violación.

    Returns:
        Tupla de (inventario enriquecido, sesión de auditoría).
    """
    session = start_session(input_data=inventory)
    enriched: dict[str, Any] = {}

    total_methods = 0
    infrastructure_methods = 0
    n1 = n2 = n3 = n4 = 0
    methods_with_veto = 0
    degradation_count = 0
    invariant_violation_count = 0

    for class_name, cls in inventory.items():
        file_path = norm(cls.get("file_path"))
        line_number = cls.get("line_number")
        methods = cls.get("methods", {}) or {}

        per_method_levels: list[str] = []
        per_method_epistemologies: list[str] = []
        per_method_blobs: list[str] = []
        method_names: list[str] = list(methods.keys())

        enriched_methods: dict[str, Any] = {}
        for method_name, method in methods.items():
            total_methods += 1
            decision = classify_method(method_name, method)
            original_level = decision.level
            level = decision.level
            epistemology = decision.epistemology
            was_degraded = False
            degradation_reason: str | None = None

            infrastructure_subtype = (
                classify_infrastructure_subtype(method_name) if level == "INFRASTRUCTURE" else None
            )

            output_type, fusion_behavior, phase_assignment = map_level_to_output(level)

            parameters = method.get("parameters", []) or []
            requires = infer_requires(parameters, level=level, docstring=norm(method.get("docstring")))

            produces = infer_produces(norm(method.get("return_type")), norm(method.get("docstring")))

            if level != "INFRASTRUCTURE":
                if level == "N4-SYN":
                    produces = ["narrative"]

                if len(produces) == 0:
                    produces = {
                        "N1-EMP": ["raw_facts"],
                        "N2-INF": ["inferences"],
                        "N3-AUD": ["validated_constraints"],
                        "N4-SYN": ["narrative"],
                    }.get(level, ["inferences"])  # type: ignore[assignment]

            blob = method_signature_blob(method_name, method)
            per_method_blobs.append(blob)
            contract_compatibility = infer_contract_compatibility(
                blob,
                level,
                epistemology,
                return_type=norm(method.get("return_type")),
                class_context=f"{class_name} {file_path}",
            )

            veto_conditions = infer_veto_conditions(level, norm(method.get("docstring")))
            if level == "N3-AUD":
                if veto_conditions is None:
                    # DEGRADACIÓN EXPLÍCITA: N3→N2 por falta de veto observable
                    was_degraded = True
                    degradation_reason = "N3-AUD lacks observable veto_conditions"
                    degradation_count += 1

                    # Registrar degradación en sesión de auditoría
                    degradation_warning = DegradationWarning(
                        original_level="N3-AUD",
                        degraded_to="N2-INF",
                        reason=degradation_reason,
                        method_id=method_name,
                        class_name=class_name,
                    )
                    session.add_degradation(degradation_warning)
                    logger.warning(
                        "DEGRADATION: %s.%s N3-AUD → N2-INF (no veto)",
                        class_name,
                        method_name,
                    )

                    # Aplicar degradación
                    level = "N2-INF"
                    epistemology = "DETERMINISTIC_LOGICAL"
                    output_type, fusion_behavior, phase_assignment = map_level_to_output(level)
                    requires = infer_requires(parameters, level=level, docstring=norm(method.get("docstring")))
                    veto_conditions = None
                else:
                    methods_with_veto += 1

            dependencies: dict[str, Any] = {
                "requires": requires if level != "INFRASTRUCTURE" else [],
                "produces": produces if level != "INFRASTRUCTURE" else [],
                "modifies": ["inferences"] if level == "N2-INF" else [],
                "modulates": ["confidence_scores"] if level == "N3-AUD" else None,
            }

            # Ejecutar invariantes ANTES de insertar
            violations = run_all_method_invariants(
                method_id=method_name,
                class_name=class_name,
                level=level,
                epistemology=epistemology,
                produces=produces if isinstance(produces, list) else list(produces),
                veto_conditions=veto_conditions,
                contract_compatibility=contract_compatibility,
                matched_signals=decision.matched_signals,
                decision_path=decision.decision_path,
                was_degraded=was_degraded,
            )

            for violation in violations:
                invariant_violation_count += 1
                session.add_invariant_violation(violation)
                logger.error(
                    "INVARIANT VIOLATION: [%s] %s",
                    violation["invariant_id"],
                    violation["message"],
                )
                if fail_on_invariant_violation:
                    raise RuntimeError(f"Invariant violation: {violation}")

            # Registrar decisión de método en log forense
            method_log = MethodDecisionLog(
                method_id=method_name,
                class_name=class_name,
                original_level=original_level,
                final_level=level,
                was_degraded=was_degraded,
                degradation_reason=degradation_reason,
                epistemology=epistemology,
                matched_signals=decision.matched_signals,
                decision_path=decision.decision_path,
                invariant_violations=violations,
                input_hash=session.hash_blob(blob),
            )
            session.method_logs.append(method_log)

            enriched_methods[method_name] = {
                **method,
                "epistemological_classification": {
                    "level": level,
                    "output_type": output_type,
                    "fusion_behavior": fusion_behavior,
                    "epistemology": epistemology,
                    "phase_assignment": phase_assignment,
                    "infrastructure_subtype": infrastructure_subtype,
                    "dependencies": dependencies,
                    "contract_compatibility": contract_compatibility,
                    "veto_conditions": veto_conditions,
                    "classification_evidence": {
                        "return_type_signal": f"return_type='{norm(method.get('return_type'))}'",
                        "name_pattern_signal": f"method_name='{method_name}'",
                        "docstring_signal": (
                            "docstring_contains_bayes="
                            + str(
                                "posterior" in norm(method.get("docstring")).lower()
                                or "bayesian" in norm(method.get("docstring")).lower()
                                or "prior" in norm(method.get("docstring")).lower()
                                or "credible" in norm(method.get("docstring")).lower()
                            )
                        ),
                        "decision_path": decision.decision_path,
                        "matched_signals": list(decision.matched_signals),
                        "original_level": original_level if was_degraded else None,
                        "was_degraded": was_degraded,
                        "degradation_reason": degradation_reason,
                    },
                },
            }

            per_method_levels.append(level)
            per_method_epistemologies.append(epistemology)

            if level == "INFRASTRUCTURE":
                infrastructure_methods += 1
            elif level == "N1-EMP":
                n1 += 1
            elif level == "N2-INF":
                n2 += 1
            elif level == "N3-AUD":
                n3 += 1
            elif level == "N4-SYN":
                n4 += 1

        if is_protocol_class(class_name, file_path):
            class_level = "PROTOCOL"
            class_epistemology = "NONE"
            class_decision_record = None
            class_epistemology_rationale = "PROTOCOL → NONE"
        else:
            class_level, class_decision_record = infer_class_level(
                per_method_levels, method_names, class_name=class_name, file_path=file_path
            )
            class_epistemology, class_epistemology_rationale = infer_class_epistemology(
                class_level,
                class_name,
                file_path,
                per_method_epistemologies,
                per_method_blobs,
            )

        # Registrar decisión de clase en log forense
        class_log = ClassDecisionLog(
            class_name=class_name,
            file_path=file_path,
            final_level=class_level,
            final_epistemology=class_epistemology,
            method_count=len(methods),
            decision_record=class_decision_record,
            level_rationale=class_decision_record.decision_rationale if class_decision_record else "PROTOCOL",
            epistemology_rationale=class_epistemology_rationale,
        )
        session.class_logs.append(class_log)

        enriched[class_name] = {
            "file_path": file_path,
            "line_number": line_number,
            "class_level": class_level,
            "class_epistemology": class_epistemology,
            "class_decision_evidence": {
                "level_rationale": class_decision_record.decision_rationale if class_decision_record else "PROTOCOL",
                "epistemology_rationale": class_epistemology_rationale,
                "override_applied": class_decision_record.override_applied if class_decision_record else None,
                "override_source": class_decision_record.override_source if class_decision_record else None,
                "tie_resolution": class_decision_record.tie_resolution if class_decision_record else None,
                "weighted_score": class_decision_record.weighted_score if class_decision_record else 0.0,
                "method_level_counts": class_decision_record.method_level_counts if class_decision_record else {},
            },
            "methods": enriched_methods,
        }

    # Validación final de invariantes globales
    global_warnings: list[str] = []

    # Verificar que todos los niveles usados son válidos
    for level in per_method_levels:
        if level not in METHOD_LEVELS:
            global_warnings.append(f"Unknown method level in output: {level}")

    # Calcular métricas de calidad
    enriched["quality_metrics"] = {
        "total_classes": len([k for k in enriched.keys() if k != "quality_metrics"]),
        "total_methods": total_methods,
        "infrastructure_methods": infrastructure_methods,
        "n1_methods": n1,
        "n2_methods": n2,
        "n3_methods": n3,
        "n4_methods": n4,
        "methods_with_veto": methods_with_veto,
        "n3_without_veto": 0,  # Ahora todos los N3 tienen veto (o fueron degradados)
        "orphan_methods": 0,
        "validation_errors": [],
        # Métricas forenses
        "degradation_count": degradation_count,
        "invariant_violation_count": invariant_violation_count,
        "global_warnings": global_warnings,
    }

    # Guardar métricas en sesión
    session.add_warning(f"Total degradations: {degradation_count}")
    session.add_warning(f"Total invariant violations: {invariant_violation_count}")
    for warn in global_warnings:
        session.add_warning(warn)

    return enriched, session
