#!/usr/bin/env python3
"""
Static Analysis Policy Capacity Mapper
======================================

This tool performs STATIC ANALYSIS of method source code to derive policy capacity
mappings based STRICTLY on episteme_rules.md classification rules.

UNTRUSTED SOURCES (ignored):
- All existing JSON classification files
- classified_methods.json
- method_sets_by_question.json
- METHODS_OPERACIONALIZACION.json
- METHODS_TO_QUESTIONS_AND_FILES.json

TRUSTED SOURCE (only):
- src/farfan_pipeline/phases/Phase_02/epistemological_assets/episteme_rules.md
- Source code files in src/farfan_pipeline/methods/

Classification Rules (from episteme_rules.md PARTE II, Sec 2.2-2.3):

N1-EMP (Empirical - FACT):
    - Prefixes: extract_*, parse_*, mine_*, chunk_*, load_*
    - Reads PreprocesadoMetadata directly
    - No transformation/interpretation
    - Output: literals (strings, numbers, lists)

N2-INF (Inferential - PARAMETER):
    - Prefixes: analyze_*, score_*, calculate_*, infer_*, evaluate_*, compare_*
    - Consumes N1 outputs
    - Produces derived quantities: scores, probabilities, embeddings
    - Classes: BayesianNumericalAnalyzer, AdaptivePriorCalculator, etc.

N3-AUD (Audit - CONSTRAINT):
    - Prefixes: validate_*, detect_*, audit_*, check_*, test_*, verify_*
    - Consumes N1 AND N2
    - Acts as VETO GATES
    - Classes: PolicyContradictionDetector, FinancialAuditor, etc.

Policy Capacity Mapping:
- N1-EMP → CA-I (Analytical @ Individual) - Observable facts
- N2-INF → CA-O / CO-O (Organizational - mixed) - Inference
- N3-AUD → CO-S / CP-O (Systemic/Political - mixed) - Validation/Audit
"""

import ast
import json
import os
import re
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict


# =============================================================================
# EPISTEME_RULES.MD CLASSIFICATION SYSTEM
# =============================================================================

class EpistemologicalLevel(Enum):
    """From episteme_rules.md PARTE I, Sec 1.2"""
    N0_INFRA = ("N0-INFRA", "Infrastructural support", "Instrumentalismo", "INFRASTRUCTURE")
    N1_EMP = ("N1-EMP", "Raw fact extraction", "Empirismo positivista", "FACT")
    N2_INF = ("N2-INF", "Probabilistic inference", "Bayesianismo subjetivista", "PARAMETER")
    N3_AUD = ("N3-AUD", "Critical validation", "Falsacionismo popperiano", "CONSTRAINT")
    N4_META = ("N4-META", "Meta-analysis", "Reflexividad crítica", "META_ANALYSIS")
    
    def __init__(self, code: str, description: str, epistemology: str, output_type: str):
        self.code = code
        self.description = description
        self.epistemology = epistemology
        self.output_type = output_type


class PolicySkill(Enum):
    """Wu Framework: Three types of policy skills"""
    ANALYTICAL = "Analytical"
    OPERATIONAL = "Operational"
    POLITICAL = "Political"


class PolicyLevel(Enum):
    """Wu Framework: Three levels of capabilities"""
    INDIVIDUAL = "Individual"
    ORGANIZATIONAL = "Organizational"
    SYSTEMIC = "Systemic"


class CapacityType(Enum):
    """Wu Framework: 9 capacity types (3 skills × 3 levels)"""
    CA_I = ("CA-I", PolicySkill.ANALYTICAL, PolicyLevel.INDIVIDUAL)
    CA_O = ("CA-O", PolicySkill.ANALYTICAL, PolicyLevel.ORGANIZATIONAL)
    CA_S = ("CA-S", PolicySkill.ANALYTICAL, PolicyLevel.SYSTEMIC)
    CO_I = ("CO-I", PolicySkill.OPERATIONAL, PolicyLevel.INDIVIDUAL)
    CO_O = ("CO-O", PolicySkill.OPERATIONAL, PolicyLevel.ORGANIZATIONAL)
    CO_S = ("CO-S", PolicySkill.OPERATIONAL, PolicyLevel.SYSTEMIC)
    CP_I = ("CP-I", PolicySkill.POLITICAL, PolicyLevel.INDIVIDUAL)
    CP_O = ("CP-O", PolicySkill.POLITICAL, PolicyLevel.ORGANIZATIONAL)
    CP_S = ("CP-S", PolicySkill.POLITICAL, PolicyLevel.SYSTEMIC)
    
    def __init__(self, code: str, skill: PolicySkill, level: PolicyLevel):
        self.code = code
        self.skill = skill
        self.level = level


# =============================================================================
# CLASSIFICATION PATTERNS (from episteme_rules.md PARTE II)
# =============================================================================

# Pattern rules for method name classification
METHOD_NAME_PATTERNS = {
    EpistemologicalLevel.N1_EMP: {
        "prefixes": ["extract_", "_extract_", "parse_", "_parse_", "mine_", "_mine_",
                     "chunk_", "_chunk_", "load_", "_load_"],
        "keywords": ["extraction", "literal", "raw", "segment"],
    },
    EpistemologicalLevel.N2_INF: {
        "prefixes": ["analyze_", "_analyze_", "score_", "_score_", "calculate_", "_calculate_",
                     "infer_", "_infer_", "evaluate_", "_evaluate_", "compare_", "_compare_",
                     "compute_", "_compute_", "embed_", "_embed_",
                     "integrate_", "_integrate_", "aggregate_", "_aggregate_"],
        "keywords": ["bayesian", "posterior", "likelihood", "confidence", "semantic", "inference"],
    },
    EpistemologicalLevel.N3_AUD: {
        "prefixes": ["validate_", "_validate_", "detect_", "_detect_", "audit_", "_audit_",
                     "check_", "_check_", "test_", "_test_", "verify_", "_verify_",
                     "veto_", "_veto_"],
        "keywords": ["contradiction", "validator", "auditor", "coherence", "consistency", "veto"],
    },
}

# Class-based classification (from episteme_rules.md examples)
CLASS_LEVEL_MAPPING = {
    # N1-EMP classes
    "TextMiningEngine": EpistemologicalLevel.N1_EMP,
    "IndustrialPolicyProcessor": EpistemologicalLevel.N1_EMP,
    "CausalExtractor": EpistemologicalLevel.N1_EMP,
    "PDETMunicipalPlanAnalyzer": EpistemologicalLevel.N1_EMP,
    "SemanticProcessor": EpistemologicalLevel.N1_EMP,
    "MunicipalAnalyzer": EpistemologicalLevel.N1_EMP,
    "DocumentProcessor": EpistemologicalLevel.N1_EMP,
    
    # N2-INF classes
    "BayesianNumericalAnalyzer": EpistemologicalLevel.N2_INF,
    "AdaptivePriorCalculator": EpistemologicalLevel.N2_INF,
    "HierarchicalGenerativeModel": EpistemologicalLevel.N2_INF,
    "BayesianMechanismInference": EpistemologicalLevel.N2_INF,
    "TeoriaCambio": EpistemologicalLevel.N2_INF,
    "SemanticAnalyzer": EpistemologicalLevel.N2_INF,
    "BayesianEvidenceIntegrator": EpistemologicalLevel.N2_INF,
    "BayesianEvidenceScorer": EpistemologicalLevel.N2_INF,
    "DispersionEngine": EpistemologicalLevel.N2_INF,
    
    # N3-AUD classes
    "PolicyContradictionDetector": EpistemologicalLevel.N3_AUD,  # Detects contradictions
    "FinancialAuditor": EpistemologicalLevel.N3_AUD,
    "IndustrialGradeValidator": EpistemologicalLevel.N3_AUD,
    "AdvancedDAGValidator": EpistemologicalLevel.N3_AUD,
    "BayesianCounterfactualAuditor": EpistemologicalLevel.N3_AUD,
    "OperationalizationAuditor": EpistemologicalLevel.N3_AUD,
    "TemporalLogicVerifier": EpistemologicalLevel.N3_AUD,
    "ContradictionDominator": EpistemologicalLevel.N3_AUD,
    "LogicalConsistencyChecker": EpistemologicalLevel.N3_AUD,
    "DAGCycleDetector": EpistemologicalLevel.N3_AUD,
    "StatisticalGateAuditor": EpistemologicalLevel.N3_AUD,
}

# Epistemological level → Policy capacity mapping rules
EPISTEME_TO_CAPACITY_RULES = {
    EpistemologicalLevel.N1_EMP: {
        "primary": CapacityType.CA_I,  # Individual analytical - observable facts
        "weight": 1.0,
    },
    EpistemologicalLevel.N2_INF: {
        "primary": CapacityType.CA_O,  # Organizational analytical
        "secondary": CapacityType.CO_O,  # Organizational operational
        "split_rule": "class_based",  # Use class name to decide
        "analytical_classes": ["SemanticAnalyzer", "BayesianNumericalAnalyzer", 
                               "AdaptivePriorCalculator", "HierarchicalGenerativeModel"],
        "operational_classes": ["BayesianMechanismInference", "TeoriaCambio",
                                "BayesianEvidenceIntegrator", "DispersionEngine"],
    },
    EpistemologicalLevel.N3_AUD: {
        "primary": CapacityType.CO_S,  # Systemic operational
        "secondary": CapacityType.CP_O,  # Organizational political
        "split_rule": "name_based",  # Use method name to decide
        "operational_keywords": ["validate", "audit", "check", "verify", "test"],
        "political_keywords": ["detect", "contradict", "consistency", "coherence"],
    },
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class MethodInfo:
    """Information about a method extracted via static analysis"""
    class_name: str
    method_name: str
    file_path: str
    is_public: bool
    epistemological_level: Optional[str] = None
    output_type: Optional[str] = None
    capacity_type: Optional[str] = None
    classification_confidence: float = 0.0
    classification_evidence: List[str] = None
    
    def __post_init__(self):
        if self.classification_evidence is None:
            self.classification_evidence = []


# =============================================================================
# STATIC ANALYSIS ENGINE
# =============================================================================

class StaticMethodAnalyzer:
    """Extracts methods from Python source files using AST"""
    
    def __init__(self, methods_dir: Path):
        self.methods_dir = methods_dir
        self.methods: List[MethodInfo] = []
    
    def analyze_all_files(self) -> List[MethodInfo]:
        """Analyze all Python files in methods directory"""
        python_files = list(self.methods_dir.glob("*.py"))
        
        for file_path in python_files:
            if file_path.name.startswith("__"):
                continue
            
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"Warning: Could not analyze {file_path.name}: {e}")
        
        return self.methods
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"Syntax/encoding error in {file_path.name}: {e}")
                return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)
    
    def _analyze_class(self, class_node: ast.ClassDef, file_path: Path):
        """Extract methods from a class"""
        class_name = class_node.name
        
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_name = item.name
                
                # Skip magic methods (dunder methods like __init__)
                if method_name.startswith("__") and method_name.endswith("__"):
                    continue
                
                is_public = not method_name.startswith("_")
                
                method_info = MethodInfo(
                    class_name=class_name,
                    method_name=method_name,
                    file_path=file_path.name,
                    is_public=is_public
                )
                
                self.methods.append(method_info)


class EpistemologicalClassifier:
    """Classifies methods according to episteme_rules.md"""
    
    def classify_method(self, method: MethodInfo) -> MethodInfo:
        """Classify a single method"""
        evidence = []
        confidence = 0.0
        level = None
        
        # Rule 1: Class-based classification (highest confidence)
        if method.class_name in CLASS_LEVEL_MAPPING:
            level = CLASS_LEVEL_MAPPING[method.class_name]
            confidence = 0.9
            evidence.append(f"Class '{method.class_name}' is in CLASS_LEVEL_MAPPING")
        
        # Rule 2: Method name pattern matching
        if level is None:
            for ep_level, patterns in METHOD_NAME_PATTERNS.items():
                # Check prefixes
                for prefix in patterns["prefixes"]:
                    if method.method_name.startswith(prefix):
                        level = ep_level
                        confidence = 0.8
                        evidence.append(f"Method name starts with '{prefix}'")
                        break
                
                if level:
                    break
                
                # Check keywords in method name
                method_lower = method.method_name.lower()
                for keyword in patterns.get("keywords", []):
                    if keyword in method_lower:
                        level = ep_level
                        confidence = 0.6
                        evidence.append(f"Method name contains keyword '{keyword}'")
                        break
                
                if level:
                    break
        
        # Default: Mark as unclassified if we can't determine level
        # This avoids systematic bias toward N2-INF
        if level is None:
            # Use N2-INF as fallback but flag with very low confidence
            level = EpistemologicalLevel.N2_INF
            confidence = 0.2  # Lower confidence to indicate uncertainty
            evidence.append("UNCLASSIFIED - defaulted to N2-INF (insufficient pattern match)")
        
        # Set level and output type
        method.epistemological_level = level.code
        method.output_type = level.output_type
        method.classification_confidence = confidence
        method.classification_evidence = evidence
        
        return method


class PolicyCapacityMapper:
    """Maps epistemological levels to policy capacity types"""
    
    def map_to_capacity(self, method: MethodInfo) -> MethodInfo:
        """Map method to policy capacity type"""
        
        # Parse epistemological level
        ep_level = None
        for level in EpistemologicalLevel:
            if level.code == method.epistemological_level:
                ep_level = level
                break
        
        if ep_level is None:
            return method
        
        # Get mapping rules
        rules = EPISTEME_TO_CAPACITY_RULES.get(ep_level)
        if not rules:
            return method
        
        # Apply mapping
        if "split_rule" not in rules:
            # Simple mapping
            method.capacity_type = rules["primary"].code
        
        elif rules["split_rule"] == "class_based":
            # N2-INF: split by class
            if method.class_name in rules["analytical_classes"]:
                method.capacity_type = rules["primary"].code  # CA-O
            elif method.class_name in rules["operational_classes"]:
                method.capacity_type = rules["secondary"].code  # CO-O
            else:
                # Default to primary
                method.capacity_type = rules["primary"].code
        
        elif rules["split_rule"] == "name_based":
            # N3-AUD: split by method name
            method_lower = method.method_name.lower()
            
            operational_match = any(kw in method_lower for kw in rules["operational_keywords"])
            political_match = any(kw in method_lower for kw in rules["political_keywords"])
            
            if operational_match and not political_match:
                method.capacity_type = rules["primary"].code  # CO-S
            elif political_match:
                method.capacity_type = rules["secondary"].code  # CP-O
            else:
                # Default to primary
                method.capacity_type = rules["primary"].code
        
        return method


# =============================================================================
# MAIN ANALYSIS PIPELINE
# =============================================================================

def main():
    """Main analysis pipeline"""
    
    print("=" * 80)
    print("STATIC ANALYSIS POLICY CAPACITY MAPPER")
    print("Based on episteme_rules.md (TRUSTED SOURCE ONLY)")
    print("=" * 80)
    print()
    
    # Find methods directory
    repo_root = Path(__file__).parent.parent.parent
    methods_dir = repo_root / "src" / "farfan_pipeline" / "methods"
    
    if not methods_dir.exists():
        print(f"ERROR: Methods directory not found: {methods_dir}")
        return
    
    print(f"Analyzing methods in: {methods_dir}")
    print()
    
    # Step 1: Extract methods via static analysis
    print("Step 1: Extracting methods from source code...")
    analyzer = StaticMethodAnalyzer(methods_dir)
    methods = analyzer.analyze_all_files()
    print(f"   Found {len(methods)} methods across {len(set(m.file_path for m in methods))} files")
    print()
    
    # Step 2: Classify by epistemological level
    print("Step 2: Classifying methods per episteme_rules.md...")
    classifier = EpistemologicalClassifier()
    for method in methods:
        classifier.classify_method(method)
    print(f"   Classified {len(methods)} methods")
    print()
    
    # Step 3: Map to policy capacity types
    print("Step 3: Mapping to policy capacity types...")
    mapper = PolicyCapacityMapper()
    for method in methods:
        mapper.map_to_capacity(method)
    print(f"   Mapped {len(methods)} methods to capacity types")
    print()
    
    # Step 4: Generate statistics
    print("Step 4: Generating statistics...")
    stats = _generate_statistics(methods)
    _print_statistics(stats)
    print()
    
    # Step 5: Save results
    print("Step 5: Saving results...")
    output_dir = Path(__file__).parent
    
    # Save detailed JSON
    json_path = output_dir / "static_analysis_results.json"
    _save_json(methods, stats, json_path)
    print(f"   Saved JSON: {json_path}")
    
    # Save markdown report
    md_path = output_dir / "STATIC_ANALYSIS_REPORT.md"
    _save_markdown(methods, stats, md_path)
    print(f"   Saved markdown: {md_path}")
    print()
    
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


def _generate_statistics(methods: List[MethodInfo]) -> Dict:
    """Generate statistics from classified methods"""
    
    stats = {
        "total_methods": len(methods),
        "by_epistemology": defaultdict(int),
        "by_capacity": defaultdict(int),
        "by_file": defaultdict(int),
        "high_confidence": 0,
        "medium_confidence": 0,
        "low_confidence": 0,
    }
    
    for method in methods:
        # Count by epistemology
        if method.epistemological_level:
            stats["by_epistemology"][method.epistemological_level] += 1
        
        # Count by capacity
        if method.capacity_type:
            stats["by_capacity"][method.capacity_type] += 1
        
        # Count by file
        stats["by_file"][method.file_path] += 1
        
        # Confidence bins
        if method.classification_confidence >= 0.8:
            stats["high_confidence"] += 1
        elif method.classification_confidence >= 0.5:
            stats["medium_confidence"] += 1
        else:
            stats["low_confidence"] += 1
    
    return stats


def _print_statistics(stats: Dict):
    """Print statistics to console"""
    
    print(f"Total Methods: {stats['total_methods']}")
    print()
    
    print("By Epistemological Level:")
    for level in sorted(stats['by_epistemology'].keys()):
        count = stats['by_epistemology'][level]
        pct = 100 * count / stats['total_methods']
        print(f"  {level:15s}: {count:4d} ({pct:5.1f}%)")
    print()
    
    print("By Policy Capacity Type:")
    for capacity in sorted(stats['by_capacity'].keys()):
        count = stats['by_capacity'][capacity]
        pct = 100 * count / stats['total_methods']
        print(f"  {capacity:10s}: {count:4d} ({pct:5.1f}%)")
    print()
    
    print("Classification Confidence:")
    print(f"  High (≥0.8):   {stats['high_confidence']:4d}")
    print(f"  Medium (≥0.5): {stats['medium_confidence']:4d}")
    print(f"  Low (<0.5):    {stats['low_confidence']:4d}")


def _save_json(methods: List[MethodInfo], stats: Dict, output_path: Path):
    """Save results to JSON"""
    
    output = {
        "metadata": {
            "version": "2.0.0",
            "source": "static_analysis",
            "trusted_source": "episteme_rules.md",
            "untrusted_sources_ignored": [
                "classified_methods.json",
                "method_sets_by_question.json",
                "METHODS_OPERACIONALIZACION.json",
                "METHODS_TO_QUESTIONS_AND_FILES.json"
            ],
            "total_methods": stats["total_methods"],
        },
        "statistics": dict(stats),
        "methods": [asdict(m) for m in methods]
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)


def _save_markdown(methods: List[MethodInfo], stats: Dict, output_path: Path):
    """Save results to markdown"""
    
    content = f"""# Static Analysis Report
## Policy Capacity Mapping from Source Code

**Generated:** {Path(__file__).name}  
**Trusted Source:** episteme_rules.md  
**Total Methods:** {stats['total_methods']}

---

## Methodology

This analysis performs **static code analysis** of Python source files in
`src/farfan_pipeline/methods/` to classify methods according to episteme_rules.md.

### Untrusted Sources (Ignored)

All existing JSON classification files are considered UNTRUSTED and ignored:
- `classified_methods.json`
- `method_sets_by_question.json`
- `METHODS_OPERACIONALIZACION.json`
- `METHODS_TO_QUESTIONS_AND_FILES.json`

### Classification Rules

Classification is based on:

1. **Class name matching** (confidence: 0.9)
2. **Method name prefix matching** (confidence: 0.8)
3. **Method name keyword matching** (confidence: 0.6)

---

## Results

### Epistemological Distribution

| Level | Count | Percentage |
|-------|-------|------------|
"""
    
    for level in sorted(stats['by_epistemology'].keys()):
        count = stats['by_epistemology'][level]
        pct = 100 * count / stats['total_methods']
        content += f"| {level} | {count} | {pct:.1f}% |\n"
    
    content += f"""
### Policy Capacity Distribution

| Capacity Type | Count | Percentage |
|---------------|-------|------------|
"""
    
    for capacity in sorted(stats['by_capacity'].keys()):
        count = stats['by_capacity'][capacity]
        pct = 100 * count / stats['total_methods']
        content += f"| {capacity} | {count} | {pct:.1f}% |\n"
    
    content += f"""
### Classification Confidence

| Level | Count |
|-------|-------|
| High (≥0.8) | {stats['high_confidence']} |
| Medium (≥0.5) | {stats['medium_confidence']} |
| Low (<0.5) | {stats['low_confidence']} |

---

## Sample Methods

First 20 methods with high confidence classification:

| Class | Method | File | Level | Capacity | Confidence |
|-------|--------|------|-------|----------|------------|
"""
    
    high_conf_methods = [m for m in methods if m.classification_confidence >= 0.8][:20]
    for m in high_conf_methods:
        content += f"| {m.class_name} | {m.method_name} | {m.file_path} | {m.epistemological_level} | {m.capacity_type} | {m.classification_confidence:.2f} |\n"
    
    content += "\n---\n\n## Complete Method List\n\nSee `static_analysis_results.json` for complete details.\n"
    
    with open(output_path, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    main()
