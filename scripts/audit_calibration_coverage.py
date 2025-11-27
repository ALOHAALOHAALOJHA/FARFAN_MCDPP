"""Audit Calibration Coverage.

Scans the codebase for methods and checks if they are present in the
central configuration files.
"""

import os
import ast
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r') as f:
        return json.load(f)

def audit():
    print("📊 Auditing Calibration & Parameterization Coverage...")
    
    intrinsic = load_json(REPO_ROOT / "config/intrinsic_calibration.json")
    params = load_json(REPO_ROOT / "config/method_parameters.json")
    
    methods_found = []
    
    # Scan for public methods in executors and processing
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
                if file.startswith("__"): continue
                
                filepath = Path(root) / file
                with open(filepath, 'r') as f:
                    try:
                        tree = ast.parse(f.read())
                    except:
                        continue
                
                # Construct module path roughly
                rel_path = filepath.relative_to(REPO_ROOT / "src").with_suffix("")
                module_name = str(rel_path).replace("/", ".")
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if not item.name.startswith("_"):
                                    method_id = f"{module_name}.{class_name}.{item.name}"
                                    # Also check short form (e.g. executors.D1Q1_Executor.execute)
                                    # The user uses "executors.D1Q1_Executor.execute" in examples
                                    # but the file is src/saaaaaa/executors/D1Q1_executor.py
                                    # so module is saaaaaa.executors.D1Q1_executor
                                    
                                    # We'll just store the method name and file for manual check if ID matching is hard
                                    methods_found.append(method_id)

    total = len(methods_found)
    calibrated = 0
    parameterized = 0
    
    print(f"\nFound {total} potential methods in target directories.")
    
    # Loose matching because IDs might vary slightly
    intrinsic_keys = set(intrinsic.keys())
    param_keys = set(params.keys())
    
    for m in methods_found:
        # Check exact or partial match
        is_cal = m in intrinsic_keys
        is_param = m in param_keys
        
        # Try to match suffix (e.g. D1Q1_Executor.execute)
        if not is_cal:
            for k in intrinsic_keys:
                if k in m or m in k:
                    is_cal = True
                    break
        
        if not is_param:
            for k in param_keys:
                if k in m or m in k:
                    is_param = True
                    break
                    
        if is_cal: calibrated += 1
        if is_param: parameterized += 1

    print("-" * 40)
    print(f"Calibration Coverage:     {calibrated}/{total} ({calibrated/total*100:.1f}%)")
    print(f"Parameterization Coverage: {parameterized}/{total} ({parameterized/total*100:.1f}%)")
    print("-" * 40)
    
    if calibrated < total or parameterized < total:
        print("❌ Coverage is INCOMPLETE.")
    else:
        print("✅ Coverage is COMPLETE.")

if __name__ == "__main__":
    audit()
