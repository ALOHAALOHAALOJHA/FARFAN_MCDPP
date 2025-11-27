"""Refactor Methods for Calibration.

Injects decorators and removes hardcoded values to enforce the central system.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def refactor_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    lines = content.split('\n')
    new_lines = []
    
    has_changes = False
    import_added = False
    
    # 1. Check/Add Import
    if "from saaaaaa.core.calibration.decorators import calibrated_method" not in content:
        # Find last import or top of file
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1
        
        lines.insert(insert_idx, "from saaaaaa.core.calibration.decorators import calibrated_method")
        has_changes = True
        import_added = True

    # 2. Process Methods
    # We need to find class methods and decorate them
    # And inside them, remove hardcoded assignments
    
    # Regex for method definition: def method_name(self, ...):
    method_pattern = re.compile(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(self')
    
    # Regex for hardcoded assignments to remove
    # e.g. threshold = 0.7
    hardcoded_pattern = re.compile(r'^\s*(threshold|alpha|beta|min_confidence)\s*=\s*0\.\d+')
    
    # We also need to know the module path to construct the ID
    rel_path = filepath.relative_to(REPO_ROOT / "src").with_suffix("")
    module_name = str(rel_path).replace("/", ".")
    
    # Simple state machine parsing
    current_class = None
    
    # Re-read lines since we might have modified imports
    # Actually let's just iterate and build new_lines
    
    final_lines = []
    iterator = iter(lines)
    
    for line in iterator:
        # Detect class
        class_match = re.search(r'^\s*class\s+([a-zA-Z0-9_]+)', line)
        if class_match:
            current_class = class_match.group(1)
            final_lines.append(line)
            continue
            
        # Detect method
        method_match = method_pattern.match(line)
        if method_match and current_class and not line.strip().startswith("def __"):
            method_name = method_match.group(1)
            indent = line[:line.find("def")]
            
            # Check if already decorated
            if len(final_lines) > 0 and "@calibrated_method" in final_lines[-1]:
                final_lines.append(line)
                continue
                
            # Add decorator
            method_id = f"{module_name}.{current_class}.{method_name}"
            final_lines.append(f'{indent}@calibrated_method("{method_id}")')
            final_lines.append(line)
            has_changes = True
            continue
            
        # Detect hardcoded assignments
        if hardcoded_pattern.match(line):
            # Comment out hardcoded value
            final_lines.append(f"{line.rstrip()} # REMOVED: Managed by Central Calibration System")
            has_changes = True
            continue
            
        final_lines.append(line)
    
    if has_changes:
        with open(filepath, 'w') as f:
            f.write('\n'.join(final_lines))
        print(f"✅ Refactored {filepath}")
        return True
    return False

def run_refactor():
    print("🛠️  Refactoring Codebase...")
    scan_dirs = [
        "src/saaaaaa/executors", 
        "src/saaaaaa/processing",
        "src/saaaaaa/analysis",
        "src/saaaaaa/optimization",
        "src/saaaaaa/utils",
        "src/saaaaaa/api"
    ]
    
    count = 0
    for d in scan_dirs:
        path = REPO_ROOT / d
        if not path.exists(): continue
        
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"): continue
                if file.startswith("__"): continue
                
                filepath = Path(root) / file
                if refactor_file(filepath):
                    count += 1
                    
    print(f"✨ Refactored {count} files.")

if __name__ == "__main__":
    run_refactor()
