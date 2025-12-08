#!/usr/bin/env python3
"""
Script to extend canonical_method_catalogue_v2.json with semantic metadata.

Adds three new fields to each method:
1. output_range: [min, max] for numerical outputs
2. semantic_tags: List of semantic classification tags
3. fusion_requirements: Required vs optional inputs
"""

import json
from pathlib import Path
from typing import Any


SEMANTIC_TAG_RULES = {
    "contradiction": ["coherence", "evidence"],
    "detect": ["evidence", "structural"],
    "coherence": ["coherence", "textual_quality"],
    "consistency": ["coherence", "evidence"],
    "temporal": ["temporal", "structural"],
    "causal": ["causal", "evidence"],
    "mechanism": ["causal", "structural"],
    "extract": ["structural", "evidence"],
    "bayesian": ["evidence", "numerical"],
    "calculate": ["numerical"],
    "score": ["evidence", "numerical"],
    "validate": ["evidence", "textual_quality"],
    "inference": ["causal", "evidence"],
    "policy": ["policy", "structural"],
    "goal": ["policy", "causal"],
    "objective": ["policy", "structural"],
    "numerical": ["numerical", "evidence"],
    "quantitative": ["numerical", "evidence"],
    "semantic": ["coherence", "textual_quality"],
    "parse": ["structural"],
    "classify": ["structural", "policy"],
    "aggregate": ["numerical", "evidence"],
    "report": ["structural", "textual_quality"],
    "quality": ["textual_quality"],
    "readability": ["textual_quality"],
}

FUSION_PATTERNS = {
    "analysis": {
        "required": ["extracted_text", "question_id"],
        "optional": ["previous_analysis", "config"]
    },
    "detector": {
        "required": ["extracted_text", "preprocessed_document"],
        "optional": ["embeddings", "config"]
    },
    "extractor": {
        "required": ["preprocessed_document", "question_id"],
        "optional": ["dependency_parse", "extracted_entities"]
    },
    "scorer": {
        "required": ["question_id", "previous_analysis"],
        "optional": ["calibration_params", "model_weights"]
    },
    "validator": {
        "required": ["extracted_text"],
        "optional": ["config", "calibration_params"]
    },
    "temporal": {
        "required": ["extracted_text", "temporal_markers"],
        "optional": ["preprocessed_document", "config"]
    },
    "causal": {
        "required": ["preprocessed_document", "dependency_parse"],
        "optional": ["temporal_markers", "domain_ontology"]
    },
    "bayesian": {
        "required": ["question_id", "previous_analysis"],
        "optional": ["calibration_params"]
    },
    "aggregator": {
        "required": ["previous_analysis", "question_id"],
        "optional": ["config"]
    },
    "reporter": {
        "required": ["previous_analysis", "document_id"],
        "optional": ["document_metadata", "config"]
    },
    "utility": {
        "required": [],
        "optional": ["config"]
    }
}

OUTPUT_RANGE_RULES = {
    "score": [0.0, 1.0],
    "probability": [0.0, 1.0],
    "confidence": [0.0, 1.0],
    "likelihood": [0.0, 1.0],
    "similarity": [0.0, 1.0],
    "coherence": [0.0, 1.0],
    "factor": [0.0, float("inf")],
    "count": [0, float("inf")],
    "weight": [0.0, 1.0],
}


def infer_semantic_tags(method: dict[str, Any]) -> list[str]:
    """Infer semantic tags based on method name and context."""
    name = method.get("canonical_name", "").lower()
    file_path = method.get("file_path", "").lower()
    
    tags = set()
    
    for keyword, tag_list in SEMANTIC_TAG_RULES.items():
        if keyword in name or keyword in file_path:
            tags.update(tag_list)
    
    if "analysis" in file_path and "contradiction" in file_path:
        tags.update(["coherence", "evidence"])
    
    if "derek_beach" in file_path:
        tags.update(["causal", "evidence"])
    
    if "scoring" in file_path:
        tags.update(["evidence", "numerical"])
    
    if not tags:
        tags.add("structural")
    
    return sorted(list(tags))


def infer_output_range(method: dict[str, Any]) -> list[float | int] | None:
    """Infer output range based on method name."""
    name = method.get("canonical_name", "").lower()
    
    for keyword, range_vals in OUTPUT_RANGE_RULES.items():
        if keyword in name:
            return range_vals
    
    if "calculate" in name or "compute" in name:
        return [0.0, float("inf")]
    
    if any(term in name for term in ["check", "validate", "verify", "test"]):
        return [0, 1]
    
    return None


def infer_fusion_requirements(method: dict[str, Any]) -> dict[str, list[str]]:
    """Infer fusion requirements based on method characteristics."""
    name = method.get("canonical_name", "").lower()
    file_path = method.get("file_path", "").lower()
    layer = method.get("layer", "")
    
    for pattern_name, requirements in FUSION_PATTERNS.items():
        if pattern_name in name or pattern_name in file_path:
            return requirements.copy()
    
    if "analysis" in file_path:
        if "contradiction" in file_path or "derek_beach" in file_path:
            return {
                "required": ["extracted_text", "question_id", "preprocessed_document"],
                "optional": ["embeddings", "previous_analysis", "config"]
            }
        return FUSION_PATTERNS["analysis"].copy()
    
    if layer == "class_method" and any(term in name for term in ["__init__", "__post_init__", "__setattr__"]):
        return FUSION_PATTERNS["utility"].copy()
    
    if "compat" in file_path or "ports" in file_path:
        return FUSION_PATTERNS["utility"].copy()
    
    if any(term in name for term in ["detect", "infer", "extract"]):
        return FUSION_PATTERNS["extractor"].copy()
    
    if any(term in name for term in ["score", "calculate", "measure"]):
        return FUSION_PATTERNS["scorer"].copy()
    
    return {
        "required": ["extracted_text"],
        "optional": ["config"]
    }


def extend_method_with_metadata(method: dict[str, Any]) -> dict[str, Any]:
    """Add semantic metadata fields to a method entry."""
    if "semantic_tags" not in method:
        method["semantic_tags"] = infer_semantic_tags(method)
    
    if "output_range" not in method:
        method["output_range"] = infer_output_range(method)
    
    if "fusion_requirements" not in method:
        method["fusion_requirements"] = infer_fusion_requirements(method)
    
    return method


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent
    catalog_path = repo_root / "config" / "canonical_method_catalogue_v2.json"
    
    print(f"Loading catalog from: {catalog_path}")
    
    with open(catalog_path, "r", encoding="utf-8") as f:
        methods = json.load(f)
    
    print(f"Processing {len(methods)} methods...")
    
    extended_methods = []
    for i, method in enumerate(methods):
        extended_method = extend_method_with_metadata(method)
        extended_methods.append(extended_method)
        
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1} methods...")
    
    backup_path = catalog_path.with_suffix(".json.backup")
    print(f"Creating backup at: {backup_path}")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(methods, f, indent=2)
    
    print(f"Writing extended catalog to: {catalog_path}")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(extended_methods, f, indent=2)
    
    print("✓ Successfully extended canonical_method_catalogue_v2.json")
    print(f"  Total methods: {len(extended_methods)}")
    print(f"  Backup saved: {backup_path}")
    
    tag_stats = {}
    for method in extended_methods:
        for tag in method.get("semantic_tags", []):
            tag_stats[tag] = tag_stats.get(tag, 0) + 1
    
    print("\nSemantic tag distribution:")
    for tag, count in sorted(tag_stats.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
