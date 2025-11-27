"""Advanced Refactor Methods.

Intelligently identifies hardcoded assignments, promotes them to parameters,
and replaces code with dynamic lookups.
"""

import os
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def advanced_refactor():
    print("🛠️  Starting Advanced Refactoring...")
    
    params_path = REPO_ROOT / "config/method_parameters.json"
    params_data = load_json(params_path)
    
    scan_dirs = [
        "src/saaaaaa/executors", 
        "src/saaaaaa/processing",
        "src/saaaaaa/analysis",
        "src/saaaaaa/optimization",
        "src/saaaaaa/utils",
        "src/saaaaaa/api"
    ]
    
    # Regex to find assignments: var_name = 0.X
    # Group 1: var_name
    # Group 2: value
    assignment_pattern = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(0\.\d+|1\.0)\s*(?:#.*)?$')
    
    # Regex to find class/method to build ID
    class_pattern = re.compile(r'^\s*class\s+([a-zA-Z0-9_]+)')
    method_pattern = re.compile(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(self')
    
    files_modified = 0
    params_added = 0
    
    for d in scan_dirs:
        path = REPO_ROOT / d
        if not path.exists(): continue
        
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"): continue
                
                filepath = Path(root) / file
                
                # Construct module path
                rel_path = filepath.relative_to(REPO_ROOT / "src").with_suffix("")
                module_name = str(rel_path).replace("/", ".")
                
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                current_class = None
                current_method = None
                current_method_id = None
                file_changed = False
                
                # We need to track if we are inside a method to associate params
                # But we also need to handle the decorator injection if missing (handled by prev script)
                # This script focuses on the assignments
                
                for line in lines:
                    # Track context
                    class_match = class_pattern.match(line)
                    if class_match:
                        current_class = class_match.group(1)
                        new_lines.append(line)
                        continue
                        
                    method_match = method_pattern.match(line)
                    if method_match:
                        current_method = method_match.group(1)
                        if current_class:
                            current_method_id = f"{module_name}.{current_class}.{current_method}"
                        new_lines.append(line)
                        continue
                    
                    # Check assignment
                    assign_match = assignment_pattern.match(line)
                    if assign_match and current_method_id:
                        var_name = assign_match.group(1)
                        value = float(assign_match.group(2))
                        
                        # Ignore if it looks like a counter or index (unlikely with float, but still)
                        
                        # 1. Add to JSON
                        if current_method_id not in params_data:
                            params_data[current_method_id] = {}
                        
                        # Only update if not exists or different (keep existing if already set)
                        if var_name not in params_data[current_method_id]:
                            params_data[current_method_id][var_name] = value
                            params_added += 1
                        
                        # 2. Replace Line
                        # We assume 'params' is available because of @calibrated_method decorator
                        # But wait, the decorator passes params as kwargs to the function?
                        # OR the function needs to call param_loader?
                        # The user's pattern: 
                        # @calibrated_method
                        # def func(self, ...):
                        #    ...
                        
                        # If the method signature doesn't have **kwargs, the decorator might fail if we pass extra args.
                        # BUT, the decorator in `decorators.py` does:
                        # params = param_loader.get(method_id)
                        # for k, v in params.items(): if k not in kwargs: kwargs[k] = v
                        # raw_result = func(self, *args, **kwargs)
                        
                        # So the params are passed as kwargs.
                        # So inside the function, we should access them via arguments?
                        # NO, existing code `var = 0.5` defines a local variable.
                        # We want `var = kwargs.get('var', 0.5)`?
                        # But `kwargs` might not be in the signature.
                        
                        # Safest approach for refactoring without breaking signatures:
                        # Use the singleton loader inside the method (or assume it's available via self.params if we changed init, but we didn't).
                        # OR: `from saaaaaa import get_parameter_loader` is already likely there or we add it.
                        # `var = get_parameter_loader().get("ID").get("var", 0.5)`
                        
                        # Let's use the singleton look up inline. It's verbose but safe.
                        # We need to make sure `get_parameter_loader` is imported.
                        
                        indent = line[:line.find(var_name)]
                        new_line = f'{indent}{var_name} = get_parameter_loader().get("{current_method_id}").get("{var_name}", {value}) # Refactored\n'
                        new_lines.append(new_line)
                        file_changed = True
                        continue
                    
                    # Check for "if x > 0.5" patterns
                    # We can't easily replace these without a variable name.
                    # We will mark them as functional constants if we can't parameterize.
                    # But user wants "100% limpieza".
                    # We will try to replace `0.X` with a generic lookup if it looks like a threshold.
                    # This is risky. Let's stick to assignments first, they were the bulk.
                    
                    new_lines.append(line)
                
                if file_changed:
                    # Ensure import exists
                    has_import = any("from saaaaaa import get_parameter_loader" in l for l in new_lines)
                    if not has_import:
                        # Add import at top
                        insert_idx = 0
                        for i, l in enumerate(new_lines):
                            if l.startswith("import") or l.startswith("from"):
                                insert_idx = i
                        new_lines.insert(insert_idx, "from saaaaaa import get_parameter_loader\n")
                    
                    with open(filepath, 'w') as f:
                        f.writelines(new_lines)
                    files_modified += 1

    print(f"💾 Updating parameters JSON with {params_added} new parameters...")
    save_json(params_path, params_data)
    print(f"✨ Modified {files_modified} files.")

if __name__ == "__main__":
    advanced_refactor()
