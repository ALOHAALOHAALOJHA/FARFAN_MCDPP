#!/usr/bin/env python3
"""
Phase 2 Class Instantiation and Method Signature Validation
===========================================================

This script validates the remaining variables for 100% method call certainty:
- Class instantiation requirements (no-arg constructor vs special rules)
- Method signature validation
- Parameter type analysis
- Return type analysis

NO FALLBACKS - Every class must be instantiable with documented requirements.

Author: GitHub Copilot
Date: 2026-01-18
"""

import ast
import importlib
import inspect
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, get_type_hints

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.append(str(Path(__file__).resolve().parent.parent))


@dataclass
class InstantiationRequirement:
    """Requirements for class instantiation."""
    
    class_name: str
    file_name: str
    
    # Constructor analysis
    has_no_arg_constructor: bool = False
    constructor_params: list[dict[str, Any]] = field(default_factory=list)
    required_params: list[str] = field(default_factory=list)
    optional_params: list[str] = field(default_factory=list)
    
    # Special instantiation needs
    requires_special_rule: bool = False
    special_rule_type: str = ""  # "config_file", "model_path", "no_init", etc.
    special_rule_description: str = ""
    
    # Instantiation test result
    instantiation_tested: bool = False
    instantiation_success: bool = False
    instantiation_error: str = ""
    
    # Risk assessment
    instantiation_risk: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, CRITICAL
    certainty_level: float = 0.0  # 0.0 to 1.0


@dataclass
class MethodSignatureValidation:
    """Method signature validation result."""
    
    method_id: str
    class_name: str
    method_name: str
    file_name: str
    
    # Signature analysis
    signature_valid: bool = False
    signature_str: str = ""
    parameters: list[dict[str, Any]] = field(default_factory=list)
    return_type: str = "Any"
    
    # Parameter validation
    requires_self: bool = True
    requires_additional_params: bool = False
    has_default_values: bool = False
    has_var_args: bool = False
    has_var_kwargs: bool = False
    
    # Call requirements
    min_required_args: int = 0
    max_args: int = 0
    
    # Risk assessment
    call_risk: str = "UNKNOWN"
    certainty_level: float = 0.0


class InstantiationValidator:
    """Validator for class instantiation requirements."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_root = repo_root / "src"
        self.methods_dir = self.src_root / "farfan_pipeline" / "methods"
        
        # Load methods mapping
        mapping_file = (
            repo_root / "canonic_questionnaire_central" / "governance" / 
            "METHODS_TO_QUESTIONS_AND_FILES.json"
        )
        
        if mapping_file.exists():
            with open(mapping_file) as f:
                data = json.load(f)
                self.methods_mapping = data.get("methods", {})
        else:
            self.methods_mapping = {}
        
        # Cache for loaded classes
        self.loaded_classes = {}
        
        # Special instantiation patterns detected from code inspection
        self.known_special_patterns = {
            "PDFProcessor": "requires config_path parameter",
            "ConfigLoader": "requires config_path parameter",
            "ReportingEngine": "requires output_dir parameter",
            "PolicyAnalysisEmbedder": "requires model_name parameter",
            "AdvancedSemanticChunker": "requires model configuration",
        }
    
    def get_unique_classes(self) -> dict[str, list[str]]:
        """Get unique classes and their methods."""
        classes = {}
        
        for method_id, method_data in self.methods_mapping.items():
            class_name = method_data.get("class_name", "")
            file_name = method_data.get("file", "")
            
            if class_name and file_name:
                if class_name not in classes:
                    classes[class_name] = {"file": file_name, "methods": []}
                classes[class_name]["methods"].append(method_data.get("method_name", ""))
        
        return classes
    
    def validate_class_instantiation(
        self, class_name: str, file_name: str
    ) -> InstantiationRequirement:
        """Validate instantiation requirements for a class."""
        
        req = InstantiationRequirement(
            class_name=class_name,
            file_name=file_name,
        )
        
        # Try to load the class
        module_name = file_name.replace(".py", "")
        module_path = f"farfan_pipeline.methods.{module_name}"
        
        try:
            if class_name not in self.loaded_classes:
                module = importlib.import_module(module_path)
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    if inspect.isclass(cls):
                        self.loaded_classes[class_name] = cls
                    else:
                        req.instantiation_error = f"{class_name} is not a class"
                        req.instantiation_risk = "CRITICAL"
                        return req
                else:
                    req.instantiation_error = f"{class_name} not found in {module_name}"
                    req.instantiation_risk = "CRITICAL"
                    return req
            
            cls = self.loaded_classes[class_name]
            
            # Analyze __init__ signature
            try:
                init_sig = inspect.signature(cls.__init__)
                params = list(init_sig.parameters.values())
                
                # Filter out 'self'
                params = [p for p in params if p.name != "self"]
                
                # Analyze each parameter
                for param in params:
                    param_info = {
                        "name": param.name,
                        "kind": str(param.kind),
                        "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                        "annotation": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    }
                    req.constructor_params.append(param_info)
                    
                    if param.default == inspect.Parameter.empty and param.kind not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    ):
                        req.required_params.append(param.name)
                    else:
                        req.optional_params.append(param.name)
                
                # Determine if no-arg constructor
                if len(req.required_params) == 0:
                    req.has_no_arg_constructor = True
                    req.instantiation_risk = "LOW"
                    req.certainty_level = 1.0
                else:
                    req.requires_special_rule = True
                    req.instantiation_risk = "MEDIUM"
                    req.certainty_level = 0.5
                    
                    # Check for known patterns
                    if class_name in self.known_special_patterns:
                        req.special_rule_description = self.known_special_patterns[class_name]
                        req.special_rule_type = "known_pattern"
                    else:
                        req.special_rule_description = f"Requires {len(req.required_params)} parameters: {', '.join(req.required_params)}"
                        req.special_rule_type = "custom_params"
                
                # Try to instantiate (only if no-arg constructor)
                if req.has_no_arg_constructor:
                    try:
                        instance = cls()
                        req.instantiation_tested = True
                        req.instantiation_success = True
                        req.certainty_level = 1.0
                    except Exception as e:
                        req.instantiation_tested = True
                        req.instantiation_success = False
                        req.instantiation_error = f"Instantiation failed: {str(e)[:100]}"
                        req.instantiation_risk = "HIGH"
                        req.certainty_level = 0.3
            
            except (ValueError, TypeError) as e:
                req.instantiation_error = f"Cannot inspect __init__: {e}"
                req.requires_special_rule = True
                req.instantiation_risk = "HIGH"
                req.certainty_level = 0.2
        
        except ImportError as e:
            req.instantiation_error = f"Import error: {e}"
            req.instantiation_risk = "CRITICAL"
            req.certainty_level = 0.0
        except Exception as e:
            req.instantiation_error = f"Unexpected error: {e}"
            req.instantiation_risk = "CRITICAL"
            req.certainty_level = 0.0
        
        return req
    
    def validate_method_signature(
        self, method_id: str, method_data: dict[str, Any]
    ) -> MethodSignatureValidation:
        """Validate method signature."""
        
        validation = MethodSignatureValidation(
            method_id=method_id,
            class_name=method_data.get("class_name", ""),
            method_name=method_data.get("method_name", ""),
            file_name=method_data.get("file", ""),
        )
        
        class_name = validation.class_name
        method_name = validation.method_name
        
        # Get the class
        if class_name in self.loaded_classes:
            cls = self.loaded_classes[class_name]
            
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                
                if callable(method):
                    try:
                        sig = inspect.signature(method)
                        validation.signature_str = str(sig)
                        validation.signature_valid = True
                        
                        params = list(sig.parameters.values())
                        
                        # Analyze parameters
                        for param in params:
                            if param.name == "self":
                                validation.requires_self = True
                                continue
                            
                            param_info = {
                                "name": param.name,
                                "kind": str(param.kind),
                                "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                                "annotation": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                            }
                            validation.parameters.append(param_info)
                            
                            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                                validation.has_var_args = True
                            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                                validation.has_var_kwargs = True
                            elif param.default != inspect.Parameter.empty:
                                validation.has_default_values = True
                            else:
                                validation.min_required_args += 1
                        
                        # Calculate max args (inf if *args present)
                        if validation.has_var_args:
                            validation.max_args = -1  # Infinite
                        else:
                            validation.max_args = len(validation.parameters)
                        
                        # Get return type
                        if sig.return_annotation != inspect.Signature.empty:
                            validation.return_type = str(sig.return_annotation)
                        
                        # Assess risk
                        if validation.min_required_args == 0:
                            validation.call_risk = "LOW"
                            validation.certainty_level = 1.0
                        elif validation.min_required_args <= 2:
                            validation.call_risk = "MEDIUM"
                            validation.certainty_level = 0.7
                        else:
                            validation.call_risk = "HIGH"
                            validation.certainty_level = 0.5
                    
                    except (ValueError, TypeError) as e:
                        validation.signature_valid = False
                        validation.call_risk = "HIGH"
                        validation.certainty_level = 0.3
        
        return validation
    
    def generate_special_instantiation_rules(
        self, requirements: dict[str, InstantiationRequirement]
    ) -> str:
        """Generate Python code for special instantiation rules."""
        
        code_lines = [
            "# Special Instantiation Rules",
            "# Generated from class instantiation validation",
            "",
            "def setup_special_instantiation_rules(registry: MethodRegistry) -> None:",
            '    """Register special instantiation rules for classes requiring parameters."""',
            "",
        ]
        
        for class_name, req in requirements.items():
            if req.requires_special_rule and req.required_params:
                code_lines.append(f"    # {class_name}: {req.special_rule_description}")
                code_lines.append(f"    registry.register_instantiation_rule(")
                code_lines.append(f'        "{class_name}",')
                code_lines.append(f"        lambda cls: cls(...),  # TODO: Provide required parameters")
                code_lines.append(f"    )")
                code_lines.append("")
        
        return "\n".join(code_lines)


def main():
    """Run instantiation and signature validation."""
    
    repo_root = Path(__file__).resolve().parent.parent
    validator = InstantiationValidator(repo_root)
    
    print("=" * 80)
    print("PHASE 2 INSTANTIATION & SIGNATURE VALIDATION")
    print("=" * 80)
    print()
    
    # Get unique classes
    unique_classes = validator.get_unique_classes()
    print(f"Total unique classes: {len(unique_classes)}")
    print()
    
    # Validate instantiation for each class
    print("Validating class instantiation requirements...")
    instantiation_reqs = {}
    
    for class_name, class_info in unique_classes.items():
        req = validator.validate_class_instantiation(class_name, class_info["file"])
        instantiation_reqs[class_name] = req
    
    # Generate summary
    no_arg_count = sum(1 for r in instantiation_reqs.values() if r.has_no_arg_constructor)
    special_rule_count = sum(1 for r in instantiation_reqs.values() if r.requires_special_rule)
    tested_count = sum(1 for r in instantiation_reqs.values() if r.instantiation_tested)
    success_count = sum(1 for r in instantiation_reqs.values() if r.instantiation_success)
    
    print()
    print("=" * 80)
    print("INSTANTIATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Total classes analyzed: {len(instantiation_reqs)}")
    print(f"No-arg constructor: {no_arg_count} ({no_arg_count/len(instantiation_reqs)*100:.1f}%)")
    print(f"Requires special rule: {special_rule_count} ({special_rule_count/len(instantiation_reqs)*100:.1f}%)")
    print(f"Instantiation tested: {tested_count}")
    print(f"Instantiation successful: {success_count}")
    print()
    
    # Risk breakdown
    risk_levels = {}
    for req in instantiation_reqs.values():
        risk = req.instantiation_risk
        if risk not in risk_levels:
            risk_levels[risk] = 0
        risk_levels[risk] += 1
    
    print("Risk Level Distribution:")
    for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]:
        if level in risk_levels:
            count = risk_levels[level]
            print(f"  {level}: {count} classes ({count/len(instantiation_reqs)*100:.1f}%)")
    print()
    
    # Show classes requiring special rules
    special_rule_classes = [
        (name, req) for name, req in instantiation_reqs.items() 
        if req.requires_special_rule
    ]
    
    if special_rule_classes:
        print("=" * 80)
        print(f"CLASSES REQUIRING SPECIAL INSTANTIATION RULES ({len(special_rule_classes)})")
        print("=" * 80)
        print()
        
        for class_name, req in special_rule_classes[:20]:  # Show first 20
            print(f"Class: {class_name}")
            print(f"  File: {req.file_name}")
            print(f"  Required params: {', '.join(req.required_params)}")
            print(f"  Description: {req.special_rule_description}")
            print(f"  Risk: {req.instantiation_risk}")
            print()
    
    # Validate method signatures
    print("=" * 80)
    print("VALIDATING METHOD SIGNATURES")
    print("=" * 80)
    print()
    
    method_validations = {}
    for method_id, method_data in validator.methods_mapping.items():
        validation = validator.validate_method_signature(method_id, method_data)
        method_validations[method_id] = validation
    
    # Method signature summary
    valid_sigs = sum(1 for v in method_validations.values() if v.signature_valid)
    no_req_args = sum(1 for v in method_validations.values() if v.min_required_args == 0)
    
    print(f"Total methods analyzed: {len(method_validations)}")
    print(f"Valid signatures: {valid_sigs} ({valid_sigs/len(method_validations)*100:.1f}%)")
    print(f"No required args (besides self): {no_req_args} ({no_req_args/len(method_validations)*100:.1f}%)")
    print()
    
    # Save results
    output_file = repo_root / "artifacts" / "reports" / "audit" / "PHASE_2_INSTANTIATION_VALIDATION.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "summary": {
            "total_classes": len(instantiation_reqs),
            "no_arg_constructor": no_arg_count,
            "requires_special_rule": special_rule_count,
            "instantiation_tested": tested_count,
            "instantiation_successful": success_count,
            "risk_levels": risk_levels,
            "total_methods": len(method_validations),
            "valid_signatures": valid_sigs,
            "no_required_args": no_req_args,
        },
        "classes": {
            class_name: {
                "class_name": req.class_name,
                "file_name": req.file_name,
                "has_no_arg_constructor": req.has_no_arg_constructor,
                "required_params": req.required_params,
                "optional_params": req.optional_params,
                "requires_special_rule": req.requires_special_rule,
                "special_rule_type": req.special_rule_type,
                "special_rule_description": req.special_rule_description,
                "instantiation_tested": req.instantiation_tested,
                "instantiation_success": req.instantiation_success,
                "instantiation_error": req.instantiation_error,
                "instantiation_risk": req.instantiation_risk,
                "certainty_level": req.certainty_level,
            }
            for class_name, req in instantiation_reqs.items()
        },
        "methods": {
            method_id: {
                "method_id": v.method_id,
                "class_name": v.class_name,
                "method_name": v.method_name,
                "signature_valid": v.signature_valid,
                "signature_str": v.signature_str,
                "min_required_args": v.min_required_args,
                "max_args": v.max_args,
                "has_var_args": v.has_var_args,
                "has_var_kwargs": v.has_var_kwargs,
                "return_type": v.return_type,
                "call_risk": v.call_risk,
                "certainty_level": v.certainty_level,
            }
            for method_id, v in method_validations.items()
        },
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    print()
    
    # Generate special instantiation rules code
    rules_code = validator.generate_special_instantiation_rules(instantiation_reqs)
    rules_file = repo_root / "artifacts" / "reports" / "audit" / "PHASE_2_SPECIAL_INSTANTIATION_RULES.py"
    
    with open(rules_file, "w") as f:
        f.write(rules_code)
    
    print(f"Special instantiation rules code saved to: {rules_file}")
    print()
    
    # Final assessment
    overall_certainty = sum(r.certainty_level for r in instantiation_reqs.values()) / len(instantiation_reqs)
    
    print("=" * 80)
    print("OVERALL ASSESSMENT")
    print("=" * 80)
    print()
    print(f"Instantiation Certainty: {overall_certainty:.1%}")
    
    if overall_certainty >= 0.9:
        print("Status: ✅ HIGH CERTAINTY - Most classes can be instantiated")
        return 0
    elif overall_certainty >= 0.7:
        print("Status: ⚠️ MEDIUM CERTAINTY - Some classes need special rules")
        return 0
    else:
        print("Status: 🔴 LOW CERTAINTY - Many classes require special instantiation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
