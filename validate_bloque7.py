#!/usr/bin/env python3
"""
VALIDADOR BASADO EN BLOQUE 7 - Especificación de Enriquecimiento Epistemológico
Implementa checklist completo de § 7.1 y § 7.2
"""

import json
import sys
from pathlib import Path
from typing import Any


def validate_bloque7(enriched: dict[str, Any], filename: str) -> tuple[bool, list[str]]:
    """Valida JSON enriquecido contra especificación BLOQUE 7."""
    errors: list[str] = []

    # § 7.1 CHECKLIST DE INTEGRIDAD

    # 1. Toda clase tiene class_level
    for class_name, cls in enriched.items():
        if class_name in ['quality_metrics', '_pipeline_metadata']:
            continue

        if 'class_level' not in cls or cls['class_level'] is None:
            errors.append(f"[V7.1.1] {class_name}: Missing class_level")

        # 2. Toda clase tiene class_epistemology
        if 'class_epistemology' not in cls or cls['class_epistemology'] is None:
            errors.append(f"[V7.1.2] {class_name}: Missing class_epistemology")

        methods = cls.get('methods', {})
        for method_name, method in methods.items():
            # 3. Todo método tiene epistemological_classification
            ec = method.get('epistemological_classification')
            if ec is None:
                errors.append(f"[V7.1.3] {class_name}.{method_name}: Missing epistemological_classification")
                continue

            level = ec.get('level')

            # 4. Todo N3 tiene veto_conditions
            if level == 'N3-AUD':
                veto = ec.get('veto_conditions')
                if veto is None:
                    errors.append(f"[V7.1.4] {class_name}.{method_name}: N3-AUD without veto_conditions")

            # 5. Todo método no-INFRASTRUCTURE tiene ≥1 TYPE compatible
            if level != 'INFRASTRUCTURE':
                compat = ec.get('contract_compatibility', {})
                if not any(compat.get(k, False) for k in ['TYPE_A', 'TYPE_B', 'TYPE_C', 'TYPE_D', 'TYPE_E']):
                    errors.append(f"[V7.1.5] {class_name}.{method_name}: No contract compatibility")

            # 6. Consistencia level ↔ output_type (§ 2.5)
            output_type = ec.get('output_type')
            fusion_behavior = ec.get('fusion_behavior')
            phase_assignment = ec.get('phase_assignment')

            expected_mapping = {
                'N1-EMP': ('FACT', 'additive', 'phase_A_construction'),
                'N2-INF': ('PARAMETER', 'multiplicative', 'phase_B_computation'),
                'N3-AUD': ('CONSTRAINT', 'gate', 'phase_C_litigation'),
                'N4-SYN': ('NARRATIVE', 'terminal', 'phase_D_synthesis'),
                'INFRASTRUCTURE': ('NONE', 'none', 'none'),
            }

            if level in expected_mapping:
                expected_output, expected_fusion, expected_phase = expected_mapping[level]
                if output_type != expected_output:
                    errors.append(f"[V7.1.6a] {class_name}.{method_name}: output_type={output_type}, expected={expected_output} for {level}")
                if fusion_behavior != expected_fusion:
                    errors.append(f"[V7.1.6b] {class_name}.{method_name}: fusion_behavior={fusion_behavior}, expected={expected_fusion} for {level}")
                if phase_assignment != expected_phase:
                    errors.append(f"[V7.1.6c] {class_name}.{method_name}: phase_assignment={phase_assignment}, expected={expected_phase} for {level}")

            # 7. classification_evidence completo
            evidence = ec.get('classification_evidence', {})
            if not evidence:
                errors.append(f"[V7.1.7a] {class_name}.{method_name}: Missing classification_evidence")
            else:
                # Check decision_path (v4) o selected_rule_id (v5)
                decision_path = evidence.get('decision_path', '')
                selected_rule = evidence.get('selected_rule_id', '')
                if not decision_path and not selected_rule:
                    errors.append(f"[V7.1.7b] {class_name}.{method_name}: Missing decision_path/selected_rule_id")

    # § 7.2 MÉTRICAS DE CALIDAD
    qm = enriched.get('quality_metrics', {})
    if not qm:
        errors.append("[V7.2.1] Missing quality_metrics")
    else:
        # Métrica crítica: n3_without_veto DEBE SER 0
        n3_without_veto = qm.get('n3_without_veto', None)
        if n3_without_veto is None:
            errors.append("[V7.2.2a] quality_metrics missing n3_without_veto")
        elif n3_without_veto != 0:
            errors.append(f"[V7.2.2b] n3_without_veto={n3_without_veto}, DEBE SER 0")

        # Métrica crítica: orphan_methods DEBE SER 0
        orphan_methods = qm.get('orphan_methods', None)
        if orphan_methods is None:
            errors.append("[V7.2.3a] quality_metrics missing orphan_methods")
        elif orphan_methods != 0:
            errors.append(f"[V7.2.3b] orphan_methods={orphan_methods}, DEBE SER 0")

        # validation_errors DEBE ESTAR VACÍO
        validation_errors = qm.get('validation_errors', None)
        if validation_errors is None:
            errors.append("[V7.2.4a] quality_metrics missing validation_errors")
        elif len(validation_errors) > 0:
            errors.append(f"[V7.2.4b] validation_errors not empty: {len(validation_errors)} errors")

    passed = len(errors) == 0
    return passed, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_bloque7.py <enriched.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    print(f"Validando: {filepath}")
    print("=" * 80)

    enriched = json.loads(filepath.read_text(encoding='utf-8'))
    passed, errors = validate_bloque7(enriched, filepath.name)

    if passed:
        print("✅ VALIDACIÓN EXITOSA - Todos los checks pasaron")
        print()
        qm = enriched.get('quality_metrics', {})
        print("Métricas de calidad:")
        for k, v in qm.items():
            print(f"  {k}: {v}")
        sys.exit(0)
    else:
        print(f"❌ VALIDACIÓN FALLIDA - {len(errors)} errores encontrados")
        print()
        for error in errors:
            print(f"  {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
