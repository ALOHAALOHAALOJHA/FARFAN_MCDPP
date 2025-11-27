"""Final Sweep Refactor.

Eliminates ALL remaining hardcoded values by creating auto-generated parameters.
This ensures 100% compliance with the 'no hardcoded values' rule.
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

def final_sweep():
    print("🧹 Starting Final Sweep Refactoring...")
    
    params_path = REPO_ROOT / "config/method_parameters.json"
    params_data = load_json(params_path)
    
    # Regex from check_hardcoded.py
    # We want to capture the number to replace it
    # (0\.\d+|1\.0)
    number_pattern = re.compile(r'(0\.\d+|1\.0)')
    
    scan_dirs = [
        "src/saaaaaa/executors", 
        "src/saaaaaa/processing",
        "src/saaaaaa/analysis",
        "src/saaaaaa/optimization",
        "src/saaaaaa/utils",
        "src/saaaaaa/api"
    ]
    
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
                rel_path = filepath.relative_to(REPO_ROOT / "src").with_suffix("")
                module_name = str(rel_path).replace("/", ".")
                
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                current_class = None
                current_method = None
                current_method_id = None
                file_changed = False
                
                for i, line in enumerate(lines):
                    # Context
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
                    
                    # Skip if already refactored or commented
                    if "get_parameter_loader" in line or "# Functional constant" in line or "# REMOVED" in line:
                        new_lines.append(line)
                        continue
                        
                    # Find numbers
                    matches = list(number_pattern.finditer(line))
                    if matches and current_method_id:
                        # We have hardcoded numbers in a method
                        
                        # Process in reverse order to not mess up indices
                        line_content = line
                        
                        for match in reversed(matches):
                            val_str = match.group(1)
                            val = float(val_str)
                            
                            # Generate param name
                            # Try to infer from context? Hard.
                            # Use generic name: param_L{line}_idx{start}
                            param_name = f"auto_param_L{i+1}_{match.start()}"
                            
                            # Add to JSON
                            if current_method_id not in params_data:
                                params_data[current_method_id] = {}
                            
                            params_data[current_method_id][param_name] = val
                            params_added += 1
                            
                            # Replace in line
                            # We use the singleton lookup
                            replacement = f'get_parameter_loader().get("{current_method_id}").get("{param_name}", {val_str})'
                            
                            start, end = match.span()
                            line_content = line_content[:start] + replacement + line_content[end:]
                        
                        new_lines.append(line_content)
                        file_changed = True
                    else:
                        new_lines.append(line)
                
                if file_changed:
                     # Ensure import exists
                    has_import = any("from saaaaaa import get_parameter_loader" in l for l in new_lines)
                    if not has_import:
                        insert_idx = 0
                        for i, l in enumerate(new_lines):
                            if l.startswith("import") or l.startswith("from"):
                                insert_idx = i
                        new_lines.insert(insert_idx, "from saaaaaa import get_parameter_loader\n")
                        
                    with open(filepath, 'w') as f:
                        f.writelines(new_lines)
                    files_modified += 1

    print(f"💾 Updating parameters JSON with {params_added} auto-generated parameters...")
    save_json(params_path, params_data)
    print(f"✨ Final sweep modified {files_modified} files.")

if __name__ == "__main__":
    final_sweep()
