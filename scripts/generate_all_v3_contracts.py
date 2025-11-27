#!/usr/bin/env python3
"""
Generate all 300 v3 executor contracts (D1-Q1 through D6-Q5)

Uses D1-Q1.v3.FINAL.json as template, customizes for each question.
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

# Load template
template_path = PROJECT_ROOT / "config" / "executor_contracts" / "D1-Q1.v3.FINAL.json"
with open(template_path) as f:
    template = json.load(f)

# Load methods mapping
methods_mapping_path = PROJECT_ROOT / "executor_methods_mapping.json"
with open(methods_mapping_path) as f:
    methods_mapping = json.load(f)

# Load questionnaire monolith
monolith_path = PROJECT_ROOT / "data" / "questionnaire_monolith.json"
with open(monolith_path) as f:
    monolith = json.load(f)

micro_questions = monolith["blocks"]["micro_questions"]

# Define method roles (generic mapping by method name patterns)
def get_method_role(method_name):
    """Generate semantic role for a method based on its name."""
    role_map = {
        "diagnose": "diagnosis",
        "analyze": "analysis",
        "extract": "extraction",
        "parse": "parsing",
        "process": "processing",
        "match": "matching",
        "detect": "detection",
        "validate": "validation",
        "audit": "auditing",
        "evaluate": "evaluation",
        "compare": "comparison",
        "calculate": "calculation",
        "infer": "inference",
        "construct": "construction",
        "identify": "identification",
        "generate": "generation",
        "chunk": "chunking",
        "embed": "embedding",
        "classify": "classification",
        "trace": "tracing",
        "verify": "verification",
    }

    for keyword, role in role_map.items():
        if keyword in method_name.lower():
            return f"{method_name}_{role}"

    return method_name.replace("_", "_")

# Define provides mapping (group by class namespace)
def get_provides_key(class_name, method_name):
    """Generate dot-notation provides key for a method."""
    namespace_map = {
        "TextMiningEngine": "text_mining",
        "IndustrialPolicyProcessor": "industrial_policy",
        "CausalExtractor": "causal_extraction",
        "FinancialAuditor": "financial_audit",
        "PDETMunicipalPlanAnalyzer": "pdet_analysis",
        "PolicyContradictionDetector": "contradiction_detection",
        "BayesianNumericalAnalyzer": "bayesian_analysis",
        "SemanticProcessor": "semantic_processing",
        "OperationalizationAuditor": "operationalization",
        "BayesianMechanismInference": "bayesian_mechanism",
        "BayesianCounterfactualAuditor": "bayesian_counterfactual",
        "PDFProcessor": "pdf_processing",
        "TeoriaCambio": "teoria_cambio",
        "BeachEvidentialTest": "beach_test",
        "AdvancedDAGValidator": "dag_validation",
        "BayesFactorTable": "bayes_factor",
        "HierarchicalGenerativeModel": "hierarchical_model",
        "IndustrialGradeValidator": "industrial_validator",
        "PerformanceAnalyzer": "performance",
        "SemanticAnalyzer": "semantic_analysis",
        "AdaptivePriorCalculator": "adaptive_prior",
        "PolicyAnalysisEmbedder": "policy_embedder",
        "ReportingEngine": "reporting",
        "TemporalLogicVerifier": "temporal_logic",
        "CausalInferenceSetup": "causal_setup",
        "MechanismPartExtractor": "mechanism_extraction",
        "CDAFFramework": "cdaf_framework",
        "PolicyTextProcessor": "text_processing",
        "ConfigLoader": "config_management",
    }

    namespace = namespace_map.get(class_name, class_name.lower())
    method_key = method_name.lstrip("_").replace("__", "_")

    return f"{namespace}.{method_key}"

# Generate contracts
output_dir = PROJECT_ROOT / "config" / "executor_contracts"
output_dir.mkdir(parents=True, exist_ok=True)

generated_count = 0
errors = []

for question in micro_questions:
    base_slot = question["base_slot"]
    question_id = question["question_id"]

    try:
        # Get methods for this question
        if base_slot not in methods_mapping:
            errors.append(f"{base_slot}: No methods found in mapping")
            continue

        question_methods = methods_mapping[base_slot]
        method_count = len(question_methods)

        # Create contract from template
        contract = json.loads(json.dumps(template))  # Deep copy

        # Update identity
        contract["identity"]["base_slot"] = base_slot
        contract["identity"]["question_id"] = question_id
        contract["identity"]["dimension_id"] = question.get("identity", {}).get("dimension_id", "DIM01")
        contract["identity"]["policy_area_id"] = question.get("policy_area_id", "PA01")
        contract["identity"]["created_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update executor_binding
        executor_class = base_slot.replace("-", "_") + "_Executor"
        contract["executor_binding"]["executor_class"] = executor_class

        # Build methods array
        methods_array = []
        for i, method_info in enumerate(question_methods, start=1):
            class_name = method_info["class"]
            method_name = method_info["method"]

            methods_array.append({
                "class_name": class_name,
                "method_name": method_name,
                "priority": i,
                "provides": get_provides_key(class_name, method_name),
                "role": get_method_role(method_name)
            })

        # Update method_binding
        contract["method_binding"] = {
            "orchestration_mode": "multi_method_pipeline",
            "method_count": method_count,
            "methods": methods_array,
            "note": f"All {method_count} methods extracted from {executor_class} in executors.py"
        }

        # Update question_context from monolith
        contract["question_context"]["question_text"] = question.get("question_text", "")
        contract["question_context"]["question_type"] = question.get("question_type", "micro")
        contract["question_context"]["scoring_modality"] = question.get("scoring_modality", "TYPE_A")
        contract["question_context"]["expected_output_type"] = question.get("expected_output_type", "score")
        contract["question_context"]["patterns"] = question.get("patterns", [])
        contract["question_context"]["expected_elements"] = question.get("expected_elements", [])
        contract["question_context"]["validations"] = question.get("validations", {})

        # Update output_contract schema constants
        contract["output_contract"]["schema"]["properties"]["base_slot"]["const"] = base_slot
        contract["output_contract"]["schema"]["properties"]["question_id"]["const"] = question_id
        contract["output_contract"]["schema"]["properties"]["question_global"]["const"] = question.get("question_global")
        contract["output_contract"]["schema"]["properties"]["policy_area_id"]["const"] = question.get("policy_area_id")
        contract["output_contract"]["schema"]["properties"]["dimension_id"]["const"] = question.get("identity", {}).get("dimension_id")
        contract["output_contract"]["schema"]["properties"]["cluster_id"]["const"] = question.get("identity", {}).get("cluster_id")

        # Update methodological_depth methods
        methodological_methods = []
        for i, method_info in enumerate(question_methods, start=1):
            class_name = method_info["class"]
            method_name = method_info["method"]

            # Find corresponding method from template (if exists) or use generic structure
            template_method = None
            for tm in template["output_contract"]["human_readable_output"]["methodological_depth"]["methods"]:
                if tm["class_name"] == class_name and tm["method_name"] == method_name:
                    template_method = tm
                    break

            if template_method:
                # Use existing documentation
                methodological_methods.append(template_method)
            else:
                # Create generic documentation
                methodological_methods.append({
                    "method_name": method_name,
                    "class_name": class_name,
                    "priority": i,
                    "role": get_method_role(method_name),
                    "epistemological_foundation": {
                        "paradigm": f"{class_name} analytical paradigm",
                        "ontological_basis": f"Analysis via {class_name}.{method_name}",
                        "epistemological_stance": "Empirical-analytical approach",
                        "theoretical_framework": [
                            f"Method {method_name} implements structured analysis for {base_slot}"
                        ],
                        "justification": f"This method contributes to {base_slot} analysis"
                    },
                    "technical_approach": {
                        "method_type": "analytical_processing",
                        "algorithm": f"{class_name}.{method_name} algorithm",
                        "steps": [
                            {"step": 1, "description": f"Execute {method_name}"},
                            {"step": 2, "description": "Process results"},
                            {"step": 3, "description": "Return structured output"}
                        ],
                        "assumptions": [
                            "Input data is preprocessed and valid"
                        ],
                        "limitations": [
                            "Method-specific limitations apply"
                        ],
                        "complexity": "O(n) where n=input size"
                    },
                    "output_interpretation": {
                        "output_structure": {
                            "result": f"Structured output from {method_name}"
                        },
                        "interpretation_guide": {
                            "high_confidence": "≥0.8: Strong evidence",
                            "medium_confidence": "0.5-0.79: Moderate evidence",
                            "low_confidence": "<0.5: Weak evidence"
                        },
                        "actionable_insights": [
                            f"Use {method_name} results for downstream analysis"
                        ]
                    }
                })

        contract["output_contract"]["human_readable_output"]["methodological_depth"]["methods"] = methodological_methods

        # Update human_answer_structure metadata
        contract["human_answer_structure"]["evidence_structure_schema"]["properties"]["metadata"]["properties"]["methods_executed"]["const"] = method_count
        contract["human_answer_structure"]["concrete_example"]["metadata"]["methods_executed"] = method_count

        # Update traceability
        contract["traceability"]["json_path"] = f"blocks.micro_questions[{question.get('question_global', 0) - 1}]"
        contract["traceability"]["method_source"] = f"src/saaaaaa/core/orchestrator/executors.py:{executor_class}"

        # Write contract
        output_path = output_dir / f"{base_slot}.v3.json"
        with open(output_path, 'w') as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)

        generated_count += 1
        print(f"✅ {generated_count:3d}/300 {base_slot:8s} ({method_count:2d} methods) → {output_path.name}")

    except Exception as e:
        errors.append(f"{base_slot}: {str(e)}")
        print(f"❌ {base_slot}: Error - {str(e)}")

# Summary
print("\n" + "="*80)
print(f"✅ Generated: {generated_count}/300 contracts")
if errors:
    print(f"❌ Errors: {len(errors)}")
    for error in errors[:10]:  # Show first 10 errors
        print(f"   - {error}")
else:
    print("🎉 All contracts generated successfully!")
print("="*80)

# Save generation log
log_path = PROJECT_ROOT / "docs" / "contract_generation_log.json"
with open(log_path, 'w') as f:
    json.dump({
        "timestamp": datetime.utcnow().isoformat(),
        "generated_count": generated_count,
        "total_expected": 300,
        "errors": errors,
        "template_used": str(template_path),
        "output_directory": str(output_dir)
    }, f, indent=2)

print(f"\n📄 Generation log saved: {log_path}")
