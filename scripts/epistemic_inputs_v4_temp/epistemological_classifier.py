#!/usr/bin/env python3
"""
Epistemological Method Classifier v1.0
=====================================

Classifies methods according to episte_refact.md criteria:
- N1-EMP: Empirical (extraction, parsing)  
- N2-INF: Inferential (analysis, scoring, calculation)
- N3-AUD: Audit (validation, contradiction detection)
- N4-SYN: Synthesis (narrative generation)

This replaces the broken "has computation" heuristic with proper
functional analysis based on the epistemological guide.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ClassificationResult:
    """Result of epistemological classification for a method."""
    class_name: str
    method_name: str
    mother_file: str
    layer: str  # N1-EMP, N2-INF, N3-AUD, N4-SYN
    output_type: str  # FACT, PARAMETER, CONSTRAINT, NARRATIVE
    fusion_behavior: str  # additive, multiplicative, gate, terminal
    rationale: str
    classification_evidence: dict = field(default_factory=dict)
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW


# =============================================================================
# LEXICAL PATTERNS (from episte_refact.md Part II, Section 2.2)
# =============================================================================

LEXICAL_PATTERNS = {
    "N1-EMP": {
        "prefixes": ["extract_", "parse_", "mine_", "chunk_", "_extract_", "_parse_"],
        "description": "Methods that perform direct observation without interpretation",
    },
    "N2-INF": {
        "prefixes": ["analyze_", "score_", "calculate_", "infer_", "evaluate_", 
                     "compare_", "process", "_analyze_", "_score_", "_calculate_",
                     "_infer_", "_evaluate_", "_compare_", "diagnose_", "_diagnose_",
                     "_match_", "embed_", "_embed_", "_simulate_", "_test_effect",
                     "_bayesian_", "_compute_", "_refine_"],
        "description": "Methods that transform observations into analytical constructs",
    },
    "N3-AUD": {
        "prefixes": ["validate_", "detect_", "audit_", "check_", "_validate_", 
                     "_detect_", "_audit_", "_check_", "verify_", "_verify_",
                     "_statistical_significance", "counterfactual_", "_is_"],
        "contains": ["contradiction", "inconsistenc", "allocation_gap"],
        "description": "Methods that validate/refute findings with veto power",
    },
    "N4-SYN": {
        "prefixes": ["generate_", "synthesize_", "report_", "_generate_", 
                     "_synthesize_", "_interpret_"],
        "contains": ["narrative", "report", "summary"],
        "description": "Methods that construct human-readable output",
    },
}

# Output type mapping
LAYER_TO_OUTPUT_TYPE = {
    "N1-EMP": "FACT",
    "N2-INF": "PARAMETER", 
    "N3-AUD": "CONSTRAINT",
    "N4-SYN": "NARRATIVE",
}

LAYER_TO_FUSION_BEHAVIOR = {
    "N1-EMP": "additive",
    "N2-INF": "multiplicative",
    "N3-AUD": "gate",
    "N4-SYN": "terminal",
}


class EpistemologicalClassifier:
    """
    Classifies methods into epistemological layers (N1/N2/N3/N4) using:
    1. Lexical Analysis - method name patterns
    2. Functional Analysis - return type, input types, code patterns
    3. Dependency Analysis - what data the method requires
    """
    
    def __init__(self, methods_dir: Path):
        """Initialize with path to methods source files."""
        self.methods_dir = methods_dir
        self._source_cache: dict[str, str] = {}
        self._ast_cache: dict[str, ast.Module] = {}
    
    def classify_method(
        self,
        class_name: str,
        method_name: str,
        mother_file: str,
    ) -> ClassificationResult:
        """
        Classify a method into its epistemological layer.
        
        Returns ClassificationResult with layer, output_type, rationale.
        """
        evidence = {}
        
        # Step 1: Lexical Analysis
        lexical_layer, lexical_rationale = self._lexical_analysis(method_name)
        evidence["lexical"] = {"layer": lexical_layer, "rationale": lexical_rationale}
        
        # Step 2: Functional Analysis (from source code)
        func_layer, func_rationale = self._functional_analysis(
            class_name, method_name, mother_file
        )
        evidence["functional"] = {"layer": func_layer, "rationale": func_rationale}
        
        # Step 3: Resolve conflicts and determine final layer
        final_layer, confidence = self._resolve_classification(
            lexical_layer, func_layer, method_name
        )
        
        # Build rationale
        rationale = self._build_rationale(method_name, final_layer, evidence)
        
        return ClassificationResult(
            class_name=class_name,
            method_name=method_name,
            mother_file=mother_file,
            layer=final_layer,
            output_type=LAYER_TO_OUTPUT_TYPE[final_layer],
            fusion_behavior=LAYER_TO_FUSION_BEHAVIOR[final_layer],
            rationale=rationale,
            classification_evidence=evidence,
            confidence=confidence,
        )
    
    def _lexical_analysis(self, method_name: str) -> tuple[str, str]:
        """
        Classify based on method name patterns.
        
        From episte_refact.md Section 2.1.2 Step 1.
        """
        method_lower = method_name.lower()
        
        # Check each layer in order of specificity
        for layer, patterns in LEXICAL_PATTERNS.items():
            # Check prefix patterns
            for prefix in patterns.get("prefixes", []):
                if method_lower.startswith(prefix) or f"_{prefix}" in method_lower:
                    return layer, f"Method name matches pattern '{prefix}*'"
            
            # Check contains patterns
            for contains in patterns.get("contains", []):
                if contains in method_lower:
                    return layer, f"Method name contains '{contains}'"
        
        # Default to N2-INF if no pattern matches (most methods are inferential)
        return "N2-INF", "No specific pattern matched; defaulting to inferential"
    
    def _functional_analysis(
        self,
        class_name: str,
        method_name: str,
        mother_file: str,
    ) -> tuple[str, str]:
        """
        Analyze method implementation for classification signals.
        
        Looks for:
        - assert/raise patterns → N3-AUD
        - Return type hints → informs layer
        - Code patterns (regex extraction, validation, etc.)
        """
        source_path = self.methods_dir / mother_file
        if not source_path.exists():
            return "N2-INF", "Source file not found; using lexical classification"
        
        try:
            source = self._get_source(source_path)
            
            # Look for method in source
            method_source = self._extract_method_source(source, class_name, method_name)
            if not method_source:
                return "N2-INF", "Method not found in source; using lexical"
            
            # Check for validation patterns (N3-AUD signals)
            validation_patterns = [
                r'\bassert\b',
                r'\braise\s+\w+Error',
                r'\braise\s+ValueError',
                r'\braise\s+ValidationError',
                r'if\s+not\s+.*:\s*raise',
                r'confidence_multiplier',
                r'veto',
                r'block_branch',
            ]
            for pattern in validation_patterns:
                if re.search(pattern, method_source, re.IGNORECASE):
                    return "N3-AUD", f"Contains validation pattern: {pattern}"
            
            # Check for extraction patterns (N1-EMP signals)
            extraction_patterns = [
                r're\.findall\s*\(',
                r're\.search\s*\(',
                r're\.match\s*\(',
                r'\.strip\s*\(\s*\)',
                r'\.split\s*\(',
                r'text\s*\[.*:.*\]',
            ]
            # Only if no computation
            computation_patterns = [
                r'\*\s*\d',
                r'/\s*\d',
                r'sum\s*\(',
                r'mean\s*\(',
                r'np\.\w+\s*\(',
                r'posterior',
                r'bayesian',
            ]
            
            has_extraction = any(re.search(p, method_source) for p in extraction_patterns)
            has_computation = any(re.search(p, method_source, re.IGNORECASE) for p in computation_patterns)
            
            if has_extraction and not has_computation:
                return "N1-EMP", "Contains extraction patterns without computation"
            
            # Check for synthesis/narrative patterns (N4-SYN signals)
            synthesis_patterns = [
                r'\.format\s*\(',
                r'f[\"\'].*{.*}.*[\"\']',
                r'template',
                r'narrative',
                r'markdown',
            ]
            # Only for generate_* or synthesize_* methods
            if method_name.lower().startswith(('generate_', 'synthesize_', '_interpret_')):
                if any(re.search(p, method_source, re.IGNORECASE) for p in synthesis_patterns):
                    return "N4-SYN", "Synthesis method with formatting patterns"
            
            return "N2-INF", "Default inferential classification from functional analysis"
            
        except Exception as e:
            return "N2-INF", f"Analysis error: {e}; using lexical"
    
    def _get_source(self, path: Path) -> str:
        """Get source code with caching."""
        key = str(path)
        if key not in self._source_cache:
            self._source_cache[key] = path.read_text(encoding='utf-8')
        return self._source_cache[key]
    
    def _extract_method_source(
        self, source: str, class_name: str, method_name: str
    ) -> str | None:
        """Extract source code of a specific method."""
        # Simple regex-based extraction (AST would be better but more complex)
        # Look for method definition
        pattern = rf'def\s+{re.escape(method_name)}\s*\([^)]*\).*?(?=\n    def\s|\nclass\s|\Z)'
        match = re.search(pattern, source, re.DOTALL)
        if match:
            return match.group(0)
        return None
    
    def _resolve_classification(
        self,
        lexical_layer: str,
        func_layer: str,
        method_name: str,
    ) -> tuple[str, str]:
        """
        Resolve conflicts between lexical and functional classification.
        
        Priority:
        1. Functional analysis takes precedence for N3-AUD (validation detection)
        2. Lexical analysis takes precedence for N1-EMP (extraction patterns)
        3. Otherwise use lexical as primary
        """
        confidence = "HIGH"
        
        # N3-AUD from functional analysis is strong signal
        if func_layer == "N3-AUD":
            return "N3-AUD", "HIGH"
        
        # N1-EMP from either is good
        if lexical_layer == "N1-EMP" or func_layer == "N1-EMP":
            return "N1-EMP", "HIGH"
        
        # N4-SYN from either
        if lexical_layer == "N4-SYN" or func_layer == "N4-SYN":
            return "N4-SYN", "HIGH"
        
        # If they disagree on N2 vs other, note lower confidence
        if lexical_layer != func_layer:
            confidence = "MEDIUM"
        
        return lexical_layer, confidence
    
    def _build_rationale(
        self,
        method_name: str,
        final_layer: str,
        evidence: dict,
    ) -> str:
        """Build human-readable rationale for classification."""
        layer_desc = LEXICAL_PATTERNS.get(final_layer, {}).get("description", "")
        lexical_reason = evidence.get("lexical", {}).get("rationale", "")
        func_reason = evidence.get("functional", {}).get("rationale", "")
        
        parts = [layer_desc]
        if lexical_reason and "default" not in lexical_reason.lower():
            parts.append(f"Lexical: {lexical_reason}")
        if func_reason and "default" not in func_reason.lower():
            parts.append(f"Functional: {func_reason}")
        
        return "; ".join(parts)
    
    def classify_slot(
        self,
        slot_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Classify all methods in a slot.
        
        Returns slot data with corrected classifications.
        """
        classified_methods = []
        layer_counts = {"N1-EMP": 0, "N2-INF": 0, "N3-AUD": 0, "N4-SYN": 0}
        
        for method_info in slot_data.get("methods", []):
            result = self.classify_method(
                class_name=method_info["class"],
                method_name=method_info["method"],
                mother_file=method_info.get("mother_file", 
                           self._infer_mother_file(method_info["class"])),
            )
            
            layer_counts[result.layer] += 1
            classified_methods.append({
                "class": result.class_name,
                "method": result.method_name,
                "mother_file": result.mother_file,
                "layer": result.layer,
                "output_type": result.output_type,
                "fusion_behavior": result.fusion_behavior,
                "rationale": result.rationale,
                "confidence": result.confidence,
            })
        
        return {
            "BASE_SLOT": slot_data["BASE_SLOT"],
            "REPRESENTATIVE_QUESTION_ID": slot_data["REPRESENTATIVE_QUESTION_ID"],
            "methods": classified_methods,
            "layer_summary": layer_counts,
            "method_count": len(classified_methods),
        }
    
    def _infer_mother_file(self, class_name: str) -> str:
        """Infer mother file from class name if not provided."""
        # Common mappings
        class_to_file = {
            "TextMiningEngine": "analyzer_one.py",
            "SemanticAnalyzer": "analyzer_one.py",
            "PerformanceAnalyzer": "analyzer_one.py",
            "CausalExtractor": "derek_beach.py",
            "FinancialAuditor": "derek_beach.py",
            "BayesianMechanismInference": "derek_beach.py",
            "BayesianCounterfactualAuditor": "derek_beach.py",
            "OperationalizationAuditor": "derek_beach.py",
            "IndustrialPolicyProcessor": "policy_processor.py",
            "PolicyContradictionDetector": "contradiction_deteccion.py",
            "BayesianNumericalAnalyzer": "embedding_policy.py",
            "BayesianConfidenceCalculator": "embedding_policy.py",
            "SemanticProcessor": "semantic_chunking_policy.py",
            "PDETMunicipalPlanAnalyzer": "financiero_viabilidad_tablas.py",
            "TeoriaCambio": "teoria_cambio.py",
            "TemporalLogicVerifier": "contradiction_deteccion.py",
            "MechanismPartExtractor": "derek_beach.py",
            "CausalInferenceSetup": "derek_beach.py",
            "PDFProcessor": "derek_beach.py",
            "ReportingEngine": "derek_beach.py",
            "BeachEvidentialTest": "derek_beach.py",
            "AdaptivePriorCalculator": "derek_beach.py",
        }
        return class_to_file.get(class_name, "unknown.py")


def classify_all_slots(
    slots_file: Path,
    methods_dir: Path,
    output_file: Path,
) -> None:
    """
    Classify all 30 slots and write corrected classifications.
    """
    classifier = EpistemologicalClassifier(methods_dir)
    
    with open(slots_file, 'r', encoding='utf-8') as f:
        slots_data = json.load(f)
    
    classified_slots = []
    for slot in slots_data:
        classified = classifier.classify_slot(slot)
        classified_slots.append(classified)
        print(f"Classified {slot['BASE_SLOT']}: "
              f"N1={classified['layer_summary']['N1-EMP']}, "
              f"N2={classified['layer_summary']['N2-INF']}, "
              f"N3={classified['layer_summary']['N3-AUD']}, "
              f"N4={classified['layer_summary']['N4-SYN']}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified_slots, f, indent=2, ensure_ascii=False)
    
    print(f"\nWrote classified slots to {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Classify methods epistemologically")
    parser.add_argument(
        "--slots-file",
        type=Path,
        default=Path("slots_30_method_classification.json"),
        help="Input slots file (method-to-slot mapping)",
    )
    parser.add_argument(
        "--methods-dir",
        type=Path,
        default=Path("src/farfan_pipeline/methods"),
        help="Directory containing method source files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("epistemological_classification_v4.json"),
        help="Output file for corrected classifications",
    )
    
    args = parser.parse_args()
    classify_all_slots(args.slots_file, args.methods_dir, args.output)
