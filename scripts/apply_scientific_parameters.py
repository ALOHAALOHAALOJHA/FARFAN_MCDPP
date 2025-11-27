"""Apply Scientific Parameters.

Classifies methods into epistemological domains and applies rigorous,
academically grounded parameters to method_parameters.json.
"""

import os
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# 1. Define Scientific Profiles
PROFILES = {
    "bayesian": {
        "description": "Bayesian Inference: Probabilistic reasoning updating priors with evidence.",
        "params": {
            "prior_alpha": 1.0,          # Jeffrey's Prior
            "prior_beta": 1.0,
            "evidence_threshold": 10.0,  # Deciban/Hartley scale
            "credible_interval": 0.95,   # Standard convention
            "threshold": 0.7             # Derived for compatibility
        }
    },
    "frequentist": {
        "description": "Statistical Analysis: Hypothesis testing and distribution analysis.",
        "params": {
            "alpha_significance": 0.05,  # Standard p-value
            "power_target": 0.80,        # Standard power
            "min_sample_size": 30,       # CLT baseline
            "outlier_threshold": 3.0,    # Z-score
            "threshold": 0.95            # Derived (1 - alpha)
        }
    },
    "causal": {
        "description": "Causal Mechanism: Determining cause-effect relationships.",
        "params": {
            "do_calculus_depth": 3,      # Pearl's Ladder
            "confounder_threshold": 0.1, # Sensitivity analysis
            "strength_threshold": 0.6,   # Cohen's d medium
            "threshold": 0.6             # Mapped to strength
        }
    },
    "semantic": {
        "description": "Semantic/NLP: Embedding space operations.",
        "params": {
            "cosine_similarity_threshold": 0.75, # Empirical equivalence
            "embedding_dimension": 768,          # BERT standard
            "token_overlap_ratio": 0.5,
            "threshold": 0.75                    # Mapped to cosine
        }
    },
    "optimization": {
        "description": "Optimization/RL: Maximizing reward functions.",
        "params": {
            "learning_rate": 0.001,      # Adam standard
            "gamma_discount": 0.99,      # Long-term horizon
            "epsilon_greedy": 0.1,       # Exploration baseline
            "threshold": 0.8             # Success threshold
        }
    }
}

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def classify_method(method_id, filepath):
    # Heuristics based on path and name
    lower_id = method_id.lower()
    path_str = str(filepath).lower()
    
    if "bayes" in lower_id or "probabil" in lower_id:
        return "bayesian"
    if "stat" in lower_id or "significan" in lower_id or "outlier" in lower_id:
        return "frequentist"
    if "causal" in lower_id or "spc" in lower_id or "bridge" in lower_id:
        return "causal"
    if "semantic" in lower_id or "embed" in lower_id or "nlp" in lower_id or "ingest" in lower_id:
        return "semantic"
    if "optimiz" in lower_id or "rl" in lower_id or "reward" in lower_id:
        return "optimization"
    
    # Fallback based on module
    if "analysis" in path_str:
        return "frequentist" # Default for analysis
    if "processing" in path_str:
        return "semantic"    # Default for processing
    
    return "frequentist" # Default safe fallback

def apply_parameters():
    print("🔬 Applying Scientific Parameters...")
    
    params_path = REPO_ROOT / "config/method_parameters.json"
    intrinsic_path = REPO_ROOT / "config/intrinsic_calibration.json"
    
    params_data = load_json(params_path)
    intrinsic_data = load_json(intrinsic_path)
    
    # We iterate over keys in params_data (which should cover all methods now)
    # But we need filepaths to classify better.
    # Let's re-scan to map IDs to files.
    
    method_to_file = {}
    scan_dirs = [
        "src/saaaaaa/executors", 
        "src/saaaaaa/processing",
        "src/saaaaaa/analysis",
        "src/saaaaaa/optimization",
        "src/saaaaaa/utils",
        "src/saaaaaa/api"
    ]
    
    for d in scan_dirs:
        path = REPO_ROOT / d
        if not path.exists(): continue
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"): continue
                filepath = Path(root) / file
                # We don't parse AST again, just use filename for heuristics if needed
                # But we need to match the ID.
                # The ID is module.Class.method
                # module is rel_path.replace('/', '.')
                
                rel_path = filepath.relative_to(REPO_ROOT / "src").with_suffix("")
                module_base = str(rel_path).replace("/", ".")
                
                # We can't easily map back from ID to file without parsing or guessing.
                # Let's just use the ID string for classification, it contains the module.
                pass

    updated_count = 0
    
    for method_id in params_data:
        # Classify
        category = classify_method(method_id, method_id) # Use ID as proxy for path
        profile = PROFILES[category]
        
        # Apply parameters
        # We preserve existing keys if they are NOT in the profile (e.g. auto_params)
        # But we overwrite/set the scientific ones.
        
        current_params = params_data[method_id]
        
        # Add metadata
        current_params["_scientific_domain"] = category
        current_params["_domain_description"] = profile["description"]
        
        # Merge profile params
        for k, v in profile["params"].items():
            current_params[k] = v
            
        params_data[method_id] = current_params
        updated_count += 1
        
        # Also update intrinsic layer if generic
        if method_id in intrinsic_data:
            if intrinsic_data[method_id].get("layer") == "utility":
                # Upgrade layer based on category
                if category == "semantic": intrinsic_data[method_id]["layer"] = "processor"
                elif category == "bayesian": intrinsic_data[method_id]["layer"] = "analyzer"
                elif category == "causal": intrinsic_data[method_id]["layer"] = "analyzer"

    print(f"💾 Updated {updated_count} methods with scientific profiles.")
    save_json(params_path, params_data)
    save_json(intrinsic_path, intrinsic_data)
    print("✅ Scientific parameterization complete.")

if __name__ == "__main__":
    apply_parameters()
