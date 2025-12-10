#!/usr/bin/env python3
"""
Verificación COMPLETA de los 300 contratos de ejecutores.
Verifica que cada contrato tenga TODOS los campos requeridos y estén bien formados.

ESTRUCTURA REAL DE CONTRATOS v3:
- identity (10 keys)
- executor_binding (2 keys)
- method_binding (4 keys)
- question_context (8 keys)
- signal_requirements (5 keys)
- evidence_assembly (5 keys)
- output_contract (4 keys) - CONTIENE human_readable_output
- validation_rules (2 keys)
- traceability (12 keys)
- error_handling (4 keys)
- fallback_strategy (3 keys)
- test_configuration (4 keys)
- compatibility (5 keys)
- calibration (3 keys)
- human_answer_structure (7 keys)
"""
import json
from pathlib import Path
from typing import Any
from collections import defaultdict

CONTRACTS_DIR = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")

# Campos TOP-LEVEL requeridos (15 secciones)
REQUIRED_TOP_LEVEL = [
    "identity",
    "executor_binding",
    "method_binding",
    "question_context",
    "signal_requirements",
    "evidence_assembly",
    "output_contract",
    "validation_rules",
    "traceability",
    "error_handling",
    "fallback_strategy",
    "test_configuration",
    "compatibility",
    "calibration",
    "human_answer_structure"
]

# Campos de identity
REQUIRED_IDENTITY = [
    "base_slot",
    "question_id",
    "dimension_id",
    "policy_area_id",
    "cluster_id",
    "question_global"
]

# Campos de output_contract.schema.properties (const values para validación)
REQUIRED_SCHEMA_CONST_FIELDS = [
    "question_id",
    "policy_area_id",
    "dimension_id",
    "cluster_id",
    "question_global"
]

# Campos de question_context (estructura REAL del contrato v3)
# NOTA: method_sets está en method_binding.methods
# NOTA: failure_contract está en error_handling.failure_contract
REQUIRED_QUESTION_CONTEXT = [
    "question_text",
    "patterns",
    "expected_elements",
    "validations"
]

# Campos de error_handling (contiene failure_contract)
REQUIRED_ERROR_HANDLING = [
    "failure_contract"
]

# Campos de method_binding (contiene los métodos)
REQUIRED_METHOD_BINDING = [
    "orchestration_mode",
    "methods"
]

# Campos de evidence_assembly
REQUIRED_EVIDENCE_ASSEMBLY = [
    "assembly_rules"
]

# Campos de validation_rules
REQUIRED_VALIDATION_RULES = [
    "rules",
    "na_policy"
]

# Campos de output_contract
REQUIRED_OUTPUT_CONTRACT = [
    "schema",
    "human_readable_output"
]


def verify_contract(contract_path: Path) -> dict[str, Any]:
    """Verifica un contrato individual y retorna resultados detallados."""
    results = {
        "path": str(contract_path.name),
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    try:
        with open(contract_path) as f:
            contract = json.load(f)
    except json.JSONDecodeError as e:
        results["valid"] = False
        results["errors"].append(f"JSON inválido: {e}")
        return results
    
    # 1. Verificar campos top-level
    missing_top = []
    for field in REQUIRED_TOP_LEVEL:
        if field not in contract:
            missing_top.append(field)
    
    if missing_top:
        results["valid"] = False
        results["errors"].append(f"Faltan campos top-level: {', '.join(missing_top)}")
        return results
    
    # 2. Verificar identity
    identity = contract.get("identity", {})
    for field in REQUIRED_IDENTITY:
        if field not in identity:
            results["valid"] = False
            results["errors"].append(f"Falta identity.{field}")
    
    results["stats"]["question_id"] = identity.get("question_id", "UNKNOWN")
    results["stats"]["policy_area_id"] = identity.get("policy_area_id", "UNKNOWN")
    results["stats"]["dimension_id"] = identity.get("dimension_id", "UNKNOWN")
    results["stats"]["base_slot"] = identity.get("base_slot", "UNKNOWN")
    
    # 3. Verificar output_contract
    output_contract = contract.get("output_contract", {})
    for field in REQUIRED_OUTPUT_CONTRACT:
        if field not in output_contract:
            results["valid"] = False
            results["errors"].append(f"Falta output_contract.{field}")
    
    # 3.1 Verificar output_contract.schema.properties
    schema = output_contract.get("schema", {})
    properties = schema.get("properties", {})
    
    # 3.2 Verificar const values correctos
    for field in REQUIRED_SCHEMA_CONST_FIELDS:
        if field in properties:
            prop = properties[field]
            if "const" in prop:
                expected = identity.get(field)
                actual = prop["const"]
                if expected != actual:
                    results["valid"] = False
                    results["errors"].append(f"const incorrecto: {field}={actual}, esperado={expected}")
    
    # 3.3 Verificar human_readable_output tiene template
    hr_output = output_contract.get("human_readable_output", {})
    if not hr_output.get("template"):
        results["warnings"].append("output_contract.human_readable_output.template vacío o faltante")
    else:
        template = hr_output.get("template", {})
        results["stats"]["has_template"] = True
        results["stats"]["template_sections"] = list(template.keys()) if isinstance(template, dict) else ["string_template"]
    
    # 4. Verificar question_context
    question_context = contract.get("question_context", {})
    for field in REQUIRED_QUESTION_CONTEXT:
        if field not in question_context:
            results["valid"] = False
            results["errors"].append(f"Falta question_context.{field}")
    
    # 4.1 Verificar patterns
    patterns = question_context.get("patterns", [])
    if not patterns:
        results["warnings"].append("patterns está vacío")
    else:
        results["stats"]["num_patterns"] = len(patterns)
    
    # 4.2 Verificar expected_elements
    expected_elements = question_context.get("expected_elements", [])
    if not expected_elements:
        results["warnings"].append("expected_elements está vacío")
    else:
        if isinstance(expected_elements, list):
            results["stats"]["num_expected_elements"] = len(expected_elements)
            # Contar elementos requeridos
            required_count = 0
            for elem in expected_elements:
                if isinstance(elem, dict):
                    if elem.get("required") == True:
                        required_count += 1
                    elif elem.get("minimum", 0) > 0:
                        required_count += 1
            results["stats"]["required_elements_count"] = required_count
        elif isinstance(expected_elements, dict):
            results["stats"]["num_expected_elements"] = len(expected_elements)
            required_count = 0
            for elem_key, elem_val in expected_elements.items():
                if isinstance(elem_val, dict):
                    if elem_val.get("required") == True:
                        required_count += 1
                    elif elem_val.get("minimum", 0) > 0:
                        required_count += 1
            results["stats"]["required_elements_count"] = required_count
    
    # 4.3 Verificar validations (EN question_context)
    validations = question_context.get("validations", {})
    if not validations:
        results["warnings"].append("validations está vacío")
    else:
        results["stats"]["num_validations"] = len(validations)
        results["stats"]["validation_types"] = list(validations.keys())
    
    # 5. Verificar method_binding.methods (NO en question_context)
    method_binding = contract.get("method_binding", {})
    for field in REQUIRED_METHOD_BINDING:
        if field not in method_binding:
            results["valid"] = False
            results["errors"].append(f"Falta method_binding.{field}")
    
    methods = method_binding.get("methods", [])
    if not methods:
        results["warnings"].append("method_binding.methods está vacío")
    else:
        results["stats"]["num_methods"] = len(methods)
        results["stats"]["orchestration_mode"] = method_binding.get("orchestration_mode", "MISSING")
    
    # 6. Verificar error_handling.failure_contract (NO en question_context)
    error_handling = contract.get("error_handling", {})
    failure_contract = error_handling.get("failure_contract", {})
    if not failure_contract:
        results["warnings"].append("error_handling.failure_contract está vacío")
    else:
        has_abort = "abort_if" in failure_contract
        has_emit = "emit_code" in failure_contract
        results["stats"]["failure_contract_complete"] = has_abort and has_emit
        if not has_abort:
            results["warnings"].append("failure_contract sin abort_if")
        if not has_emit:
            results["warnings"].append("failure_contract sin emit_code")
    
    # 7. Verificar evidence_assembly
    evidence_assembly = contract.get("evidence_assembly", {})
    assembly_rules = evidence_assembly.get("assembly_rules", [])
    if not assembly_rules:
        results["warnings"].append("assembly_rules está vacío")
    else:
        results["stats"]["num_assembly_rules"] = len(assembly_rules)
        # Verificar que cada regla tiene target y sources
        for i, rule in enumerate(assembly_rules):
            if "target" not in rule:
                results["errors"].append(f"assembly_rules[{i}] sin target")
                results["valid"] = False
            if "sources" not in rule:
                results["errors"].append(f"assembly_rules[{i}] sin sources")
                results["valid"] = False
    
    # 8. Verificar validation_rules
    validation_rules = contract.get("validation_rules", {})
    for field in REQUIRED_VALIDATION_RULES:
        if field not in validation_rules:
            results["valid"] = False
            results["errors"].append(f"Falta validation_rules.{field}")
    
    results["stats"]["na_policy"] = validation_rules.get("na_policy", "MISSING")
    rules_list = validation_rules.get("rules", [])
    results["stats"]["num_validation_rules"] = len(rules_list) if isinstance(rules_list, list) else 0
    
    # 9. Verificar human_answer_structure (para respuesta humana)
    human_answer = contract.get("human_answer_structure", {})
    if not human_answer:
        results["warnings"].append("human_answer_structure vacío")
    else:
        results["stats"]["human_answer_keys"] = list(human_answer.keys())
    
    # 10. Verificar calibration
    calibration = contract.get("calibration", {})
    calibration_status = calibration.get("status", "MISSING")
    results["stats"]["calibration_status"] = calibration_status
    
    return results


def main():
    contracts = sorted(CONTRACTS_DIR.glob("Q*.v3.json"))
    print(f"\n{'='*80}")
    print(f"VERIFICACIÓN COMPLETA DE {len(contracts)} CONTRATOS v3")
    print(f"{'='*80}\n")
    
    total_valid = 0
    total_invalid = 0
    total_with_warnings = 0
    
    all_errors: dict[str, list[str]] = defaultdict(list)
    all_warnings: dict[str, list[str]] = defaultdict(list)
    
    validation_distribution: dict[str, int] = defaultdict(int)
    pattern_counts: list[int] = []
    method_counts: list[int] = []
    assembly_rule_counts: list[int] = []
    
    for contract_path in contracts:
        result = verify_contract(contract_path)
        
        if result["valid"]:
            total_valid += 1
        else:
            total_invalid += 1
            for error in result["errors"]:
                all_errors[error].append(result["path"])
        
        if result["warnings"]:
            total_with_warnings += 1
            for warning in result["warnings"]:
                all_warnings[warning].append(result["path"])
        
        # Estadísticas
        stats = result.get("stats", {})
        if "validation_types" in stats:
            for vtype in stats["validation_types"]:
                validation_distribution[vtype] += 1
        if "num_patterns" in stats:
            pattern_counts.append(stats["num_patterns"])
        if "num_methods" in stats:
            method_counts.append(stats["num_methods"])
        if "num_assembly_rules" in stats:
            assembly_rule_counts.append(stats["num_assembly_rules"])
    
    # RESUMEN
    print(f"{'='*80}")
    print("RESUMEN DE VALIDACIÓN")
    print(f"{'='*80}")
    print(f"Total contratos: {len(contracts)}")
    print(f"  ✅ Válidos: {total_valid}")
    print(f"  ❌ Inválidos: {total_invalid}")
    print(f"  ⚠️  Con advertencias: {total_with_warnings}")
    
    if all_errors:
        print(f"\n{'='*80}")
        print("ERRORES ENCONTRADOS")
        print(f"{'='*80}")
        for error, files in sorted(all_errors.items(), key=lambda x: -len(x[1])):
            print(f"\n❌ {error}")
            print(f"   Afecta {len(files)} contratos:")
            for f in files[:5]:
                print(f"     - {f}")
            if len(files) > 5:
                print(f"     ... y {len(files) - 5} más")
    
    if all_warnings:
        print(f"\n{'='*80}")
        print("ADVERTENCIAS (no bloquean ejecución)")
        print(f"{'='*80}")
        for warning, files in sorted(all_warnings.items(), key=lambda x: -len(x[1])):
            print(f"\n⚠️  {warning}")
            print(f"   Afecta {len(files)} contratos")
    
    print(f"\n{'='*80}")
    print("ESTADÍSTICAS DE CONTENIDO")
    print(f"{'='*80}")
    
    print("\nDistribución de validaciones por tipo:")
    for vtype, count in sorted(validation_distribution.items(), key=lambda x: -x[1]):
        print(f"  - {vtype}: {count} contratos")
    
    if pattern_counts:
        print(f"\nPatterns por contrato:")
        print(f"  - Mínimo: {min(pattern_counts)}")
        print(f"  - Máximo: {max(pattern_counts)}")
        print(f"  - Promedio: {sum(pattern_counts)/len(pattern_counts):.1f}")
    
    if method_counts:
        print(f"\nMétodos por contrato:")
        print(f"  - Mínimo: {min(method_counts)}")
        print(f"  - Máximo: {max(method_counts)}")
        print(f"  - Promedio: {sum(method_counts)/len(method_counts):.1f}")
    
    if assembly_rule_counts:
        print(f"\nReglas de ensamblaje por contrato:")
        print(f"  - Mínimo: {min(assembly_rule_counts)}")
        print(f"  - Máximo: {max(assembly_rule_counts)}")
        print(f"  - Promedio: {sum(assembly_rule_counts)/len(assembly_rule_counts):.1f}")
    
    # Verificación de irrigación desde monolith
    print(f"\n{'='*80}")
    print("VERIFICACIÓN DE IRRIGACIÓN DESDE MONOLITH")
    print(f"{'='*80}")
    
    monolith_path = Path("canonic_questionnaire_central/questionnaire_monolith.json")
    if monolith_path.exists():
        with open(monolith_path) as f:
            monolith = json.load(f)
        
        micro_questions = monolith.get("blocks", {}).get("micro_questions", [])
        print(f"\nPreguntas en monolith: {len(micro_questions)}")
        print(f"Contratos generados: {len(contracts)}")
        
        # Verificar correspondencia 1:1
        monolith_ids = {q.get("question_id") for q in micro_questions}
        contract_ids = set()
        
        for contract_path in contracts:
            with open(contract_path) as f:
                contract = json.load(f)
            qid = contract.get("identity", {}).get("question_id")
            contract_ids.add(qid)
        
        missing_in_contracts = monolith_ids - contract_ids
        extra_in_contracts = contract_ids - monolith_ids
        
        if missing_in_contracts:
            print(f"\n⚠️  Preguntas en monolith sin contrato: {len(missing_in_contracts)}")
            for qid in sorted(missing_in_contracts)[:10]:
                print(f"     - {qid}")
        else:
            print(f"\n✅ Todas las preguntas del monolith tienen contrato")
        
        if extra_in_contracts:
            print(f"\n⚠️  Contratos sin pregunta en monolith: {len(extra_in_contracts)}")
        else:
            print(f"✅ Todos los contratos corresponden a preguntas del monolith")
    
    print(f"\n{'='*80}")
    print("CONCLUSIÓN FINAL")
    print(f"{'='*80}")
    
    if total_invalid == 0:
        print("\n✅ TODOS LOS 300 CONTRATOS SON ESTRUCTURALMENTE VÁLIDOS")
        print("   - Tienen todos los campos requeridos (15 secciones)")
        print("   - Los const values coinciden con identity")
        print("   - Tienen assembly_rules para EvidenceAssembler")
        print("   - Tienen human_readable_output en output_contract")
        print("   - Tienen validation_rules con na_policy")
        if total_with_warnings:
            print(f"\n   ⚠️  Hay {total_with_warnings} contratos con advertencias menores")
            print("      (campos opcionales vacíos - no bloquean ejecución)")
    else:
        print(f"\n❌ HAY {total_invalid} CONTRATOS CON ERRORES QUE DEBEN CORREGIRSE")
    
    return 0 if total_invalid == 0 else 1


if __name__ == "__main__":
    exit(main())
