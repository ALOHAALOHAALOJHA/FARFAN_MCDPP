import os
import libcst as cst
from scripts.fix_farfan_imports import FixFarfanImports

TARGET_DIR = "farfan_core"

def apply_fix():
    print(f"Scanning {TARGET_DIR} for import fixes...")
    # Instantiate the transformer.
    transformer = FixFarfanImports()
    
    count = 0
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        source = f.read()
                    
                    # Parse
                    tree = cst.parse_module(source)
                    
                    # Transform
                    modified_tree = tree.visit(transformer)
                    
                    # Check for changes
                    if modified_tree.code != source:
                        print(f"Fixing imports in: {path}")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(modified_tree.code)
                        count += 1
                            
                except Exception as e:
                    print(f"Failed to process {path}: {e}")
    
    print(f"Refactoring complete. Modified {count} files.")

if __name__ == "__main__":
    apply_fix()
