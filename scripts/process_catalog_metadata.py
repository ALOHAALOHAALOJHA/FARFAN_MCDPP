#!/usr/bin/env python3
"""
Process canonical_method_catalogue_v2.json to add semantic metadata fields.
This script reads the catalog, enriches each method entry, and writes back.
"""

import json
import sys
from pathlib import Path


def get_semantic_tags(method):
    """Assign semantic tags based on method name and file path."""
    name = method.get("canonical_name", "").lower()
    path = method.get("file_path", "").lower()
    
    tags = []
    
    if any(k in name or k in path for k in ["contradiction", "coherence", "consistency"]):
        tags.extend(["coherence", "evidence"])
    
    if "temporal" in name or "temporal" in path or "timeline" in name:
        tags.extend(["temporal", "structural"])
    
    if any(k in name for k in ["causal", "mechanism", "inference"]):
        tags.extend(["causal", "evidence"])
    
    if any(k in name for k in ["bayesian", "probability", "likelihood"]):
        tags.extend(["evidence", "numerical"])
    
    if any(k in name for k in ["extract", "parse"]):
        if "extract" not in tags:
            tags.append("structural")
    
    if any(k in name for k in ["calculate", "compute", "score", "measure"]):
        if "numerical" not in tags:
            tags.append("numerical")
    
    if any(k in name for k in ["policy", "goal", "objective"]):
        tags.extend(["policy", "structural"])
    
    if any(k in name for k in ["validate", "verify", "check"]):
        tags.extend(["evidence", "textual_quality"])
    
    if "derek_beach" in path:
        if "causal" not in tags:
            tags.append("causal")
        if "evidence" not in tags:
            tags.append("evidence")
    
    if "contradiction_deteccion" in path:
        if "coherence" not in tags:
            tags.append("coherence")
    
    if "scoring" in path:
        if "numerical" not in tags:
            tags.append("numerical")
        if "evidence" not in tags:
            tags.append("evidence")
    
    if any(k in name for k in ["quality", "readability", "completeness"]):
        if "textual_quality" not in tags:
            tags.append("textual_quality")
    
    if any(k in name for k in ["aggregate", "combine", "merge"]):
        if "numerical" not in tags:
            tags.append("numerical")
    
    if any(k in name for k in ["report", "summarize", "format"]):
        if "structural" not in tags:
            tags.append("structural")
    
    if not tags or ("analysis" in path and len(tags) == 0):
        tags.append("structural")
    
    return sorted(list(set(tags)))


def get_output_range(method):
    """Determine output range based on method characteristics."""
    name = method.get("canonical_name", "").lower()
    
    if any(k in name for k in ["score", "probability", "confidence", "likelihood", "similarity", "coherence", "weight"]):
        return [0.0, 1.0]
    
    if "factor" in name and "bayes" in name:
        return [0.0, None]
    
    if any(k in name for k in ["count", "number", "size"]):
        return [0, None]
    
    if any(k in name for k in ["check", "validate", "verify", "test", "is_", "has_"]):
        return [0, 1]
    
    return None


def get_fusion_requirements(method):
    """Determine fusion requirements (required vs optional inputs)."""
    name = method.get("canonical_name", "").lower()
    path = method.get("file_path", "").lower()
    layer = method.get("layer", "")
    
    if layer == "class_method" and any(k in name for k in ["__init__", "__post_init__", "__setattr__", "__repr__"]):
        return {"required": [], "optional": ["config"]}
    
    if any(k in path for k in ["compat", "ports", "boot_checks", "runtime_config", "dependency"]):
        return {"required": [], "optional": ["config"]}
    
    if "derek_beach" in path or "contradiction" in path:
        if any(k in name for k in ["detect", "infer", "extract", "identify"]):
            return {
                "required": ["extracted_text", "question_id", "preprocessed_document"],
                "optional": ["embeddings", "previous_analysis", "config", "dependency_parse"]
            }
        elif any(k in name for k in ["calculate", "score", "measure"]):
            return {
                "required": ["question_id", "previous_analysis"],
                "optional": ["calibration_params", "model_weights", "config"]
            }
    
    if "temporal" in name or "temporal" in path:
        return {
            "required": ["extracted_text", "temporal_markers"],
            "optional": ["preprocessed_document", "config"]
        }
    
    if any(k in name for k in ["causal", "mechanism"]):
        return {
            "required": ["preprocessed_document", "dependency_parse"],
            "optional": ["temporal_markers", "domain_ontology", "config"]
        }
    
    if any(k in name for k in ["aggregate", "combine"]):
        return {
            "required": ["previous_analysis", "question_id"],
            "optional": ["config", "calibration_params"]
        }
    
    if any(k in name for k in ["report", "generate", "format"]):
        return {
            "required": ["previous_analysis", "document_id"],
            "optional": ["document_metadata", "config"]
        }
    
    if "analysis" in path:
        return {
            "required": ["extracted_text", "question_id"],
            "optional": ["previous_analysis", "config"]
        }
    
    return {
        "required": ["extracted_text"],
        "optional": ["config"]
    }


def process_catalog():
    """Main processing function."""
    repo_root = Path(__file__).parent.parent
    catalog_path = repo_root / "config" / "canonical_method_catalogue_v2.json"
    
    if not catalog_path.exists():
        print(f"ERROR: Catalog not found at {catalog_path}", file=sys.stderr)
        return 1
    
    print(f"Reading catalog from: {catalog_path}")
    with open(catalog_path, "r", encoding="utf-8") as f:
        methods = json.load(f)
    
    print(f"Processing {len(methods)} methods...")
    
    processed = 0
    for method in methods:
        if "semantic_tags" not in method:
            method["semantic_tags"] = get_semantic_tags(method)
        
        if "output_range" not in method:
            method["output_range"] = get_output_range(method)
        
        if "fusion_requirements" not in method:
            method["fusion_requirements"] = get_fusion_requirements(method)
        
        processed += 1
        if processed % 1000 == 0:
            print(f"  Processed {processed} methods...")
    
    backup_path = catalog_path.with_suffix(".json.bak")
    print(f"Creating backup: {backup_path}")
    with open(backup_path, "w", encoding="utf-8") as f:
        with open(catalog_path, "r", encoding="utf-8") as orig:
            f.write(orig.read())
    
    print(f"Writing updated catalog: {catalog_path}")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(methods, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully processed {processed} methods")
    
    tag_counts = {}
    for method in methods:
        for tag in method.get("semantic_tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\nSemantic tag distribution:")
    for tag in sorted(tag_counts.keys()):
        print(f"  {tag}: {tag_counts[tag]}")
    
    return 0


if __name__ == "__main__":
    sys.exit(process_catalog())
