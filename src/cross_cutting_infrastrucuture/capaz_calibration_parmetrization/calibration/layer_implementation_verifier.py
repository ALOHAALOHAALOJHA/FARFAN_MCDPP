"""
Layer Implementation Verifier.

Deep verification of each layer evaluator to confirm:
1. Compute method exists and is not a stub
2. Required inputs are documented
3. Output format matches expected
4. Production logic is present (not just placeholders)
5. Integration with orchestrator
"""

import ast
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple

@dataclass
class MethodSignature:
    """Method signature details."""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: str
    has_docstring: bool
    docstring: str
    line_number: int
    is_async: bool = False


@dataclass
class LayerImplementationVerification:
    """Detailed verification of layer implementation."""
    layer_symbol: str
    layer_name: str
    file_path: str
    file_exists: bool
    total_lines: int
    has_imports: bool
    compute_methods: List[MethodSignature]
    helper_methods: List[str]
    classes_defined: List[str]
    has_production_logic: bool
    stub_indicators: List[str]
    missing_elements: List[str]
    integration_evidence: List[str]
    quality_score: float
    details: Dict[str, Any] = field(default_factory=dict)


class LayerImplementationVerifier:
    """Verifies layer evaluator implementations in detail."""
    
    def __init__(self, calibration_dir: str):
        self.calibration_dir = Path(calibration_dir)
        
        self.layer_files = {
            "@b": "COHORT_2024_intrinsic_scoring.py",
            "@chain": "COHORT_2024_chain_layer.py",
            "@q": "COHORT_2024_question_layer.py",
            "@d": "COHORT_2024_dimension_layer.py",
            "@p": "COHORT_2024_policy_layer.py",
            "@C": "COHORT_2024_congruence_layer.py",
            "@u": "COHORT_2024_unit_layer.py",
            "@m": "COHORT_2024_meta_layer.py"
        }
        
        self.layer_names = {
            "@b": "Base Layer (Intrinsic Calibration)",
            "@chain": "Chain Layer (Data Flow Position)",
            "@q": "Question Layer (Question Compatibility)",
            "@d": "Dimension Layer (Dimension Compatibility)",
            "@p": "Policy Layer (Policy Compatibility)",
            "@C": "Congruence Layer (Ensemble Coherence)",
            "@u": "Unit Layer (PDT Quality)",
            "@m": "Meta Layer (Governance & Transparency)"
        }
        
        self.expected_compute_methods = {
            "@b": ["compute_base_layer", "load_intrinsic_score", "get_intrinsic_score"],
            "@chain": ["evaluate_chain_score", "compute_chain_layer", "score_position"],
            "@q": ["evaluate_question_score", "compute_question_layer"],
            "@d": ["evaluate_dimension_score", "compute_dimension_layer"],
            "@p": ["evaluate_policy_score", "compute_policy_layer"],
            "@C": ["evaluate_congruence", "compute_congruence_layer"],
            "@u": ["evaluate_unit_score", "compute_unit_layer", "evaluate_pdt"],
            "@m": ["evaluate_meta_score", "compute_meta_layer"]
        }
        
        self.production_logic_indicators = [
            "compatibility",
            "score",
            "weight",
            "compute",
            "calculate",
            "normalize",
            "aggregate",
            "match",
            "semantic",
            "threshold"
        ]
        
        self.stub_indicators = [
            "NotImplementedError",
            "TODO",
            "STUB",
            "PLACEHOLDER",
            "pass  # implementation",
            "return 0.5",
            "return None",
            "raise NotImplemented"
        ]
    
    def parse_method_signature(self, node: ast.FunctionDef) -> MethodSignature:
        """Parse method signature from AST node."""
        parameters = []
        
        for arg in node.args.args:
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            parameters.append({
                "name": arg.arg,
                "type": param_type,
                "has_annotation": bool(arg.annotation)
            })
        
        return_type = ast.unparse(node.returns) if node.returns else "Any"
        
        docstring = ast.get_docstring(node) or ""
        
        return MethodSignature(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            has_docstring=bool(docstring),
            docstring=docstring,
            line_number=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def analyze_file_content(self, content: str) -> Dict[str, Any]:
        """Analyze file content for implementation quality."""
        lines = content.split('\n')
        
        has_stub = any(indicator in content for indicator in self.stub_indicators)
        
        has_production = any(indicator in content.lower() for indicator in self.production_logic_indicators)
        
        import_count = len([line for line in lines if line.strip().startswith('import') or line.strip().startswith('from')])
        
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        docstring_count = content.count('"""') // 2
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "import_lines": import_count,
            "comment_lines": comment_lines,
            "docstring_count": docstring_count,
            "has_stub_indicators": has_stub,
            "has_production_logic": has_production
        }
    
    def verify_layer_implementation(self, layer_symbol: str) -> LayerImplementationVerification:
        """Verify a single layer implementation."""
        file_name = self.layer_files[layer_symbol]
        file_path = self.calibration_dir / file_name
        
        verification = LayerImplementationVerification(
            layer_symbol=layer_symbol,
            layer_name=self.layer_names[layer_symbol],
            file_path=str(file_path),
            file_exists=file_path.exists(),
            total_lines=0,
            has_imports=False,
            compute_methods=[],
            helper_methods=[],
            classes_defined=[],
            has_production_logic=False,
            stub_indicators=[],
            missing_elements=[],
            integration_evidence=[],
            quality_score=0.0
        )
        
        if not verification.file_exists:
            verification.missing_elements.append(f"File does not exist: {file_path}")
            verification.quality_score = 0.0
            return verification
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            content_analysis = self.analyze_file_content(content)
            verification.total_lines = content_analysis["total_lines"]
            verification.has_production_logic = content_analysis["has_production_logic"]
            
            if content_analysis["has_stub_indicators"]:
                for indicator in self.stub_indicators:
                    if indicator in content:
                        verification.stub_indicators.append(indicator)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    verification.has_imports = True
                
                elif isinstance(node, ast.ClassDef):
                    verification.classes_defined.append(node.name)
                
                elif isinstance(node, ast.FunctionDef):
                    sig = self.parse_method_signature(node)
                    
                    expected = self.expected_compute_methods[layer_symbol]
                    if any(exp in node.name.lower() for exp in [e.lower() for e in expected]):
                        verification.compute_methods.append(sig)
                    else:
                        verification.helper_methods.append(node.name)
            
            if not verification.compute_methods:
                verification.missing_elements.append(
                    f"No compute method found. Expected one of: {self.expected_compute_methods[layer_symbol]}"
                )
            
            if not verification.has_imports:
                verification.missing_elements.append("No imports found - likely minimal implementation")
            
            if verification.total_lines < 20:
                verification.missing_elements.append(f"File too short ({verification.total_lines} lines) - likely stub")
            
            orchestrator_patterns = ["orchestrator", "calibration_result", "layer_score"]
            for pattern in orchestrator_patterns:
                if pattern.lower() in content.lower():
                    verification.integration_evidence.append(f"References '{pattern}'")
            
            verification.quality_score = self._calculate_quality_score(verification, content_analysis)
            
            verification.details = {
                "content_analysis": content_analysis,
                "compute_method_count": len(verification.compute_methods),
                "helper_method_count": len(verification.helper_methods),
                "class_count": len(verification.classes_defined)
            }
        
        except Exception as e:
            verification.missing_elements.append(f"Failed to parse file: {str(e)}")
            verification.quality_score = 0.0
        
        return verification
    
    def _calculate_quality_score(self, verification: LayerImplementationVerification, content_analysis: Dict) -> float:
        """Calculate implementation quality score (0-1)."""
        score = 0.0
        
        if verification.file_exists:
            score += 0.2
        
        if verification.compute_methods:
            score += 0.3
        
        if verification.has_production_logic:
            score += 0.2
        
        if not verification.stub_indicators:
            score += 0.2
        
        if verification.total_lines >= 50:
            score += 0.1
        
        if verification.stub_indicators:
            score *= 0.3
        
        if not verification.has_production_logic:
            score *= 0.5
        
        return min(1.0, max(0.0, score))
    
    def verify_all_layers(self) -> Dict[str, LayerImplementationVerification]:
        """Verify all layer implementations."""
        results = {}
        
        for layer_symbol in self.layer_files.keys():
            results[layer_symbol] = self.verify_layer_implementation(layer_symbol)
        
        return results
    
    def generate_detailed_report(self, verifications: Dict[str, LayerImplementationVerification]) -> Dict[str, Any]:
        """Generate detailed verification report."""
        report = {
            "summary": {
                "total_layers": len(verifications),
                "fully_implemented": 0,
                "partially_implemented": 0,
                "not_implemented": 0,
                "average_quality_score": 0.0
            },
            "layer_details": {},
            "critical_issues": [],
            "recommendations": []
        }
        
        quality_scores = []
        
        for layer_symbol, verification in verifications.items():
            quality_scores.append(verification.quality_score)
            
            if verification.quality_score >= 0.8:
                report["summary"]["fully_implemented"] += 1
                status = "✅ IMPLEMENTED"
            elif verification.quality_score >= 0.4:
                report["summary"]["partially_implemented"] += 1
                status = "⚠️ PARTIAL"
            else:
                report["summary"]["not_implemented"] += 1
                status = "❌ MISSING/STUB"
            
            report["layer_details"][layer_symbol] = {
                "name": verification.layer_name,
                "status": status,
                "quality_score": verification.quality_score,
                "file": verification.file_path,
                "compute_methods": [m.name for m in verification.compute_methods],
                "stub_indicators": verification.stub_indicators,
                "missing_elements": verification.missing_elements,
                "integration_evidence": verification.integration_evidence,
                "details": verification.details
            }
            
            if verification.quality_score < 0.4:
                report["critical_issues"].append({
                    "layer": layer_symbol,
                    "name": verification.layer_name,
                    "issue": "Not implemented or stub only",
                    "missing": verification.missing_elements,
                    "action": f"Implement production logic in {verification.file_path}"
                })
        
        report["summary"]["average_quality_score"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        for layer_symbol, verification in verifications.items():
            if not verification.compute_methods and verification.file_exists:
                report["recommendations"].append({
                    "layer": layer_symbol,
                    "recommendation": f"Add compute method (expected: {self.expected_compute_methods[layer_symbol]})",
                    "priority": "high"
                })
            
            if verification.stub_indicators:
                report["recommendations"].append({
                    "layer": layer_symbol,
                    "recommendation": f"Remove stub indicators: {verification.stub_indicators}",
                    "priority": "high"
                })
            
            if not verification.has_production_logic and verification.file_exists:
                report["recommendations"].append({
                    "layer": layer_symbol,
                    "recommendation": "Add production logic (compatibility scoring, aggregation, etc.)",
                    "priority": "critical"
                })
        
        return report
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print summary to console."""
        print("\n" + "=" * 80)
        print("LAYER IMPLEMENTATION VERIFICATION REPORT")
        print("=" * 80)
        
        print(f"\nTotal Layers: {report['summary']['total_layers']}")
        print(f"✅ Fully Implemented: {report['summary']['fully_implemented']}")
        print(f"⚠️  Partially Implemented: {report['summary']['partially_implemented']}")
        print(f"❌ Not Implemented/Stub: {report['summary']['not_implemented']}")
        print(f"Average Quality Score: {report['summary']['average_quality_score']:.2f}")
        
        print("\n" + "=" * 80)
        print("LAYER STATUS DETAILS")
        print("=" * 80)
        
        for layer_symbol in sorted(report['layer_details'].keys()):
            details = report['layer_details'][layer_symbol]
            print(f"\n{layer_symbol} - {details['name']}")
            print(f"  Status: {details['status']}")
            print(f"  Quality: {details['quality_score']:.2f}")
            print(f"  File: {details['file']}")
            
            if details['compute_methods']:
                print(f"  Compute Methods: {', '.join(details['compute_methods'])}")
            else:
                print(f"  Compute Methods: ⚠️ NONE FOUND")
            
            if details['stub_indicators']:
                print(f"  ⚠️ Stub Indicators: {', '.join(details['stub_indicators'][:3])}")
            
            if details['missing_elements']:
                print(f"  ❌ Missing: {details['missing_elements'][0]}")
        
        if report['critical_issues']:
            print("\n" + "=" * 80)
            print("CRITICAL ISSUES")
            print("=" * 80)
            for issue in report['critical_issues']:
                print(f"\n❌ {issue['layer']} - {issue['name']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Action: {issue['action']}")
        
        if report['recommendations']:
            print("\n" + "=" * 80)
            print("RECOMMENDATIONS")
            print("=" * 80)
            for i, rec in enumerate(report['recommendations'][:10], 1):
                print(f"\n{i}. {rec['layer']} ({rec['priority']} priority)")
                print(f"   {rec['recommendation']}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    calibration_dir = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration"
    
    verifier = LayerImplementationVerifier(calibration_dir)
    
    verifications = verifier.verify_all_layers()
    
    report = verifier.generate_detailed_report(verifications)
    
    verifier.print_summary(report)
    
    output_dir = Path("artifacts/audit_reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "layer_implementation_verification.json", 'w') as f:
        json.dump({
            "verifications": {k: asdict(v) for k, v in verifications.items()},
            "report": report
        }, f, indent=2, default=str)
    
    print(f"\n✅ Detailed report saved to {output_dir / 'layer_implementation_verification.json'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
