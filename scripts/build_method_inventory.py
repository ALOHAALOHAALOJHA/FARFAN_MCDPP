#!/usr/bin/env python3
import os
import ast
import json
import re
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
INVENTORY_FILE = ROOT_DIR / "canonical_method_inventory.json"
STATS_FILE = ROOT_DIR / "method_statistics.json"
EXCLUDED_FILE = ROOT_DIR / "excluded_methods.json"

# Regex patterns
EXECUTOR_PATTERN = re.compile(r"D[1-6]Q[1-5]_Executor")

# Layer Mapping Rules (Heuristic based on path and name)
def determine_layer(module_path, class_name, method_name):
    path_str = str(module_path).lower()
    if "ingestion" in path_str:
        return "ingestion"
    if "processor" in path_str or "process" in method_name:
        return "processor"
    if "analyzer" in path_str or "analysis" in path_str:
        return "analyzer"
    if "orchestrator" in path_str:
        return "orchestrator"
    if "executor" in path_str or EXECUTOR_PATTERN.search(class_name):
        return "executor"
    return "utility" # Default

class MethodVisitor(ast.NodeVisitor):
    def __init__(self, module_path):
        self.module_path = module_path
        self.methods = []
        self.current_class = None

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        if self.current_class: # Only interested in methods within classes for now, or all functions? 
            # The prompt implies "methods", but often functions are key too. 
            # "canonical_name, class, method, layer, signature"
            # If no class, class is None.
            
            method_name = node.name
            class_name = self.current_class if self.current_class else "Global"
            
            # Signature extraction
            args = [arg.arg for arg in node.args.args]
            signature = f"({', '.join(args)})"
            
            layer = determine_layer(self.module_path, class_name, method_name)
            
            # Canonical Notation: MODULE:CLASS.METHOD@LAYER[FLAGS]{STATUS}
            # We'll just generate the ID part here: MODULE:CLASS.METHOD
            module_str = str(self.module_path).replace("/", ".").replace(".py", "")
            if module_str.startswith("src."):
                module_str = module_str[4:]
            
            canonical_name = f"{module_str}:{class_name}.{method_name}"
            method_id = f"{module_str}::{class_name}::{method_name}"
            
            self.methods.append({
                "method_id": method_id,
                "canonical_name": canonical_name,
                "module": str(self.module_path),
                "class": class_name,
                "method": method_name,
                "signature": signature,
                "layer": layer,
                "is_executor": bool(EXECUTOR_PATTERN.search(class_name))
            })
        
        self.generic_visit(node)

def build_inventory():
    print(f"Building method inventory from {SRC_DIR}...")
    
    inventory = {}
    stats = {"total": 0, "by_layer": {}, "executors": 0}
    excluded = []
    
    if not SRC_DIR.exists():
        print(f"Source directory {SRC_DIR} not found!")
        return

    for filepath in SRC_DIR.rglob("*.py"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=filepath)
                
            rel_path = filepath.relative_to(ROOT_DIR)
            visitor = MethodVisitor(rel_path)
            visitor.visit(tree)
            
            for m in visitor.methods:
                inventory[m["method_id"]] = m
                
                # Stats
                stats["total"] += 1
                layer = m["layer"]
                stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
                if m["is_executor"]:
                    stats["executors"] += 1
                    
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")

    # Save Inventory
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
        
    # Save Stats
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Inventory complete. Found {stats['total']} methods.")
    print(f"Saved to {INVENTORY_FILE}")

if __name__ == "__main__":
    build_inventory()
