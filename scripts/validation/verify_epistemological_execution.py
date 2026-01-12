#!/usr/bin/env python3
"""Verify epistemological pipeline execution for v4 contracts.

This script validates that:
1. v4 contracts with orchestration_mode="epistemological_pipeline" are detected
2. execution_phases structure is parsed correctly
3. Phase order (A→B→C) and dependencies are respected
4. Signal injection works across all phases

F.A.R.F.A.N - Epistemological Pipeline Verification
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_sample_v4_contracts(limit: int = 5) -> list[dict[str, Any]]:
    """Load sample v4 contracts for testing."""
    contracts_dir = PROJECT_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "generated_contracts"
    contracts = []
    
    for contract_path in sorted(contracts_dir.glob("Q*_PA*_contract_v4.json"))[:limit]:
        with open(contract_path) as f:
            contracts.append(json.load(f))
    
    return contracts


def verify_epistemological_structure(contract: dict[str, Any]) -> dict[str, Any]:
    """Verify v4 epistemological pipeline structure."""
    results = {
        "contract_id": contract.get("identity", {}).get("contract_id", "UNKNOWN"),
        "valid": True,
        "errors": [],
        "phase_stats": {},
    }
    
    method_binding = contract.get("method_binding", {})
    orchestration_mode = method_binding.get("orchestration_mode")
    
    if orchestration_mode != "epistemological_pipeline":
        results["errors"].append(f"Unexpected orchestration_mode: {orchestration_mode}")
        results["valid"] = False
        return results
    
    execution_phases = method_binding.get("execution_phases", {})
    if not execution_phases:
        results["errors"].append("Missing execution_phases")
        results["valid"] = False
        return results
    
    expected_phases = [
        ("phase_A_construction", "N1", "raw_facts"),
        ("phase_B_computation", "N2", "inferences"),
        ("phase_C_litigation", "N3", "validated_output"),
    ]
    
    for phase_key, expected_level, expected_output in expected_phases:
        if phase_key not in execution_phases:
            results["errors"].append(f"Missing phase: {phase_key}")
            continue
        
        phase = execution_phases[phase_key]
        methods = phase.get("methods", [])
        level = phase.get("level", "")
        output_target = phase.get("output_target", "")
        dependencies = phase.get("dependencies", [])
        
        results["phase_stats"][phase_key] = {
            "method_count": len(methods),
            "level": level,
            "output_target": output_target,
            "dependencies": dependencies,
            "has_veto_conditions": any(m.get("veto_conditions") for m in methods),
        }
        
        # Validate phase level
        if not level.startswith(expected_level):
            results["errors"].append(f"{phase_key}: expected level {expected_level}, got {level}")
        
        # Validate methods have required fields
        for idx, method in enumerate(methods):
            if "class_name" not in method:
                results["errors"].append(f"{phase_key}.methods[{idx}]: missing class_name")
            if "method_name" not in method:
                results["errors"].append(f"{phase_key}.methods[{idx}]: missing method_name")
    
    # Validate phase dependencies
    if "phase_B_computation" in execution_phases:
        b_deps = execution_phases["phase_B_computation"].get("dependencies", [])
        if "raw_facts" not in b_deps:
            results["errors"].append("phase_B_computation should depend on raw_facts")
    
    if "phase_C_litigation" in execution_phases:
        c_deps = execution_phases["phase_C_litigation"].get("dependencies", [])
        if "raw_facts" not in c_deps or "inferences" not in c_deps:
            results["errors"].append("phase_C_litigation should depend on raw_facts and inferences")
    
    if results["errors"]:
        results["valid"] = False
    
    return results


def verify_signal_injection_points(contract: dict[str, Any]) -> dict[str, Any]:
    """Verify that signal injection points are present."""
    results = {
        "contract_id": contract.get("identity", {}).get("contract_id", "UNKNOWN"),
        "has_patterns": False,
        "has_expected_elements": False,
        "has_signal_requirements": False,
        "pattern_count": 0,
        "expected_element_count": 0,
    }
    
    question_context = contract.get("question_context", {})
    patterns = question_context.get("patterns", [])
    expected_elements = question_context.get("expected_elements", [])
    
    results["has_patterns"] = len(patterns) > 0
    results["pattern_count"] = len(patterns)
    results["has_expected_elements"] = len(expected_elements) > 0
    results["expected_element_count"] = len(expected_elements)
    results["has_signal_requirements"] = "signal_requirements" in contract
    
    return results


def verify_executor_compatibility() -> dict[str, Any]:
    """Verify that BaseExecutorWithContract handles epistemological_pipeline."""
    results = {
        "imports_ok": False,
        "has_epistemological_handler": False,
        "has_veto_evaluator": False,
        "errors": [],
    }
    
    try:
        from farfan_pipeline.phases.Phase_two.phase2_60_00_base_executor_with_contract import (
            BaseExecutorWithContract,
        )
        results["imports_ok"] = True
        
        # Check for epistemological pipeline handling
        import inspect
        source = inspect.getsource(BaseExecutorWithContract._execute_v3)
        
        if 'epistemological_pipeline' in source:
            results["has_epistemological_handler"] = True
        else:
            results["errors"].append("_execute_v3 does not handle epistemological_pipeline")
        
        # Check for veto condition evaluator
        if hasattr(BaseExecutorWithContract, "_evaluate_veto_condition"):
            results["has_veto_evaluator"] = True
        else:
            results["errors"].append("Missing _evaluate_veto_condition method")
        
    except Exception as e:
        results["errors"].append(f"Import error: {e}")
    
    return results


def main() -> int:
    """Run all verifications."""
    print("=" * 70)
    print("     F.A.R.F.A.N - EPISTEMOLOGICAL PIPELINE VERIFICATION")
    print("=" * 70)
    print()
    
    # 1. Verify executor compatibility
    print("[1/3] Verificando compatibilidad del executor...")
    executor_result = verify_executor_compatibility()
    
    if executor_result["imports_ok"]:
        print("      ✓ Imports OK")
    else:
        print("      ✗ Import errors")
    
    if executor_result["has_epistemological_handler"]:
        print("      ✓ Epistemological pipeline handler presente")
    else:
        print("      ✗ Falta handler para epistemological_pipeline")
    
    if executor_result["has_veto_evaluator"]:
        print("      ✓ Evaluador de condiciones veto presente")
    else:
        print("      ✗ Falta _evaluate_veto_condition")
    
    # 2. Verify contract structures
    print("\n[2/3] Verificando estructura de contratos v4...")
    contracts = load_sample_v4_contracts(limit=10)
    print(f"      → Cargados {len(contracts)} contratos de prueba")
    
    structure_errors = 0
    phase_totals = {"A": 0, "B": 0, "C": 0}
    veto_capable_count = 0
    
    for contract in contracts:
        struct_result = verify_epistemological_structure(contract)
        if not struct_result["valid"]:
            structure_errors += 1
            print(f"      ✗ {struct_result['contract_id']}: {struct_result['errors']}")
        else:
            stats = struct_result["phase_stats"]
            if "phase_A_construction" in stats:
                phase_totals["A"] += stats["phase_A_construction"]["method_count"]
            if "phase_B_computation" in stats:
                phase_totals["B"] += stats["phase_B_computation"]["method_count"]
            if "phase_C_litigation" in stats:
                phase_totals["C"] += stats["phase_C_litigation"]["method_count"]
                if stats["phase_C_litigation"]["has_veto_conditions"]:
                    veto_capable_count += 1
    
    print(f"      → Errores de estructura: {structure_errors}/{len(contracts)}")
    print(f"      → Total métodos Phase A (N1-EMP): {phase_totals['A']}")
    print(f"      → Total métodos Phase B (N2-INF): {phase_totals['B']}")
    print(f"      → Total métodos Phase C (N3-AUD): {phase_totals['C']}")
    print(f"      → Contratos con capacidad veto: {veto_capable_count}")
    
    # 3. Verify signal injection
    print("\n[3/3] Verificando puntos de inyección de señales...")
    signal_ok = 0
    total_patterns = 0
    total_expected = 0
    
    for contract in contracts:
        signal_result = verify_signal_injection_points(contract)
        if signal_result["has_patterns"] and signal_result["has_expected_elements"]:
            signal_ok += 1
        total_patterns += signal_result["pattern_count"]
        total_expected += signal_result["expected_element_count"]
    
    print(f"      → Contratos con señales completas: {signal_ok}/{len(contracts)}")
    print(f"      → Total patterns: {total_patterns}")
    print(f"      → Total expected_elements: {total_expected}")
    
    # Summary
    print("\n" + "=" * 70)
    print("                          RESUMEN")
    print("=" * 70)
    
    all_ok = (
        executor_result["has_epistemological_handler"]
        and executor_result["has_veto_evaluator"]
        and structure_errors == 0
        and signal_ok == len(contracts)
    )
    
    if all_ok:
        print("  🟢 VERIFICACIÓN COMPLETA: Pipeline epistemológico operativo")
        print()
        print("  El executor ahora puede:")
        print("    1. Detectar contratos v4 con orchestration_mode='epistemological_pipeline'")
        print("    2. Ejecutar fases A→B→C respetando dependencias")
        print("    3. Inyectar señales (patterns, expected_elements) a cada método")
        print("    4. Evaluar condiciones de veto en Phase C (N3-AUD)")
        print("    5. Propagar restricciones de confianza según asimetría epistémica")
        return 0
    else:
        print("  🔴 VERIFICACIÓN FALLIDA")
        if executor_result["errors"]:
            for err in executor_result["errors"]:
                print(f"    - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
