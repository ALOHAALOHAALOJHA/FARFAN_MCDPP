# JOBFRONT 7: EMERGENCY METHOD CATALOG GENERATION

**Status**: EXECUTABLE ACTION PLAN  
**Duration**: 2-3 hours  
**Objective**: Generate complete method inventory with metadata for current codebase

---

## Phase 1: Audit & Adapt Scanner (30 min)

### Step 1.1: Test System Scanner on Current Codebase
```bash
cd system/config/calibration/inventories
python3 << 'TEST'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scan_methods_inventory import MethodInventoryScanner

# Test on small subset first
scanner = MethodInventoryScanner(
    root_path=Path("../../.."),
    src_dirs=['src']
)

# Scan just one directory to verify
test_dir = Path("../../../src/core")
if test_dir.exists():
    methods = scanner.scan_directory(test_dir)
    print(f"✅ Scanner works: Found {len(methods)} methods in src/core")
    if methods:
        print(f"Sample: {methods[0].method_id}")
else:
    print("❌ Test directory not found")
TEST
```

### Step 1.2: Identify What Needs Updating
```bash
# Check for SISAS
find src -type d -name "*sisas*" -o -name "*SISAS*" | head -10

# Count Python files per major directory
for dir in src/core src/orchestration src/canonic_phases src/cross_cutting_infrastrucuiture; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.py" | wc -l)
        echo "$dir: $count Python files"
    fi
done
```

---

## Phase 2: Generate Full Inventory (45 min)

### Step 2.1: Run Full Scan with Adapted Script
```python
#!/usr/bin/env python3
"""
JOBFRONT 7: Current Codebase Method Inventory Scanner
Adapted from system/config/calibration/inventories/scan_methods_inventory.py
"""
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MethodMetadata:
    method_id: str
    canonical_name: str
    module_path: str
    class_name: Optional[str]
    method_name: str
    file_path: str
    line_number: int
    role: str
    inferred_layer: str
    docstring: Optional[str]
    parameter_count: int
    has_type_hints: bool

class CurrentCodebaseScanner:
    """Scans current codebase including SISAS and all new modules."""
    
    ROLE_KEYWORDS = {
        'executor': ['execute', 'executor', 'D[0-9]Q[0-9]'],
        'processor': ['process', 'processor', 'parse', 'transform'],
        'analyzer': ['analyze', 'analyser', 'analysis'],
        'extractor': ['extract', 'extractor', 'retrieve'],
        'ingest': ['ingest', 'load', 'read', 'import'],
        'score': ['score', 'scoring', 'rate', 'rating'],
        'orchestrator': ['orchestrate', 'coordinate', 'manage'],
        'utility': ['util', 'helper', 'tool'],
    }
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.methods: List[MethodMetadata] = []
        
    def scan_all(self) -> List[MethodMetadata]:
        """Scan entire src/ directory."""
        src_dir = self.root_path / 'src'
        if not src_dir.exists():
            raise RuntimeError(f"src/ directory not found at {src_dir}")
        
        logger.info(f"Scanning {src_dir}...")
        self._scan_directory(src_dir)
        logger.info(f"✅ Scan complete: {len(self.methods)} methods found")
        return self.methods
    
    def _scan_directory(self, directory: Path):
        """Recursively scan directory."""
        for py_file in directory.rglob('*.py'):
            if '__pycache__' in str(py_file) or '.venv' in str(py_file):
                continue
            try:
                self._scan_file(py_file)
            except Exception as e:
                logger.debug(f"Skip {py_file}: {e}")
    
    def _scan_file(self, file_path: Path):
        """Parse Python file and extract methods."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            rel_path = file_path.relative_to(self.root_path)
            module_path = str(rel_path).replace('/', '.').replace('.py', '')
            
            # Find all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    
                    parent_class = self._find_parent_class(tree, node)
                    method_meta = self._create_metadata(
                        node, module_path, parent_class, file_path
                    )
                    if method_meta:
                        self.methods.append(method_meta)
                        
        except SyntaxError:
            pass  # Skip files with syntax errors
    
    def _find_parent_class(self, tree, func_node) -> Optional[str]:
        """Find parent class of a function."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return node.name
        return None
    
    def _create_metadata(
        self, node: ast.FunctionDef, module_path: str, 
        class_name: Optional[str], file_path: Path
    ) -> Optional[MethodMetadata]:
        """Create metadata for a method."""
        
        # Build canonical name
        if class_name:
            canonical_name = f"{module_path}.{class_name}.{node.name}"
        else:
            canonical_name = f"{module_path}.{node.name}"
        
        # Generate unique ID
        method_id = hashlib.md5(canonical_name.encode()).hexdigest()[:16]
        
        # Infer role
        role = self._infer_role(canonical_name, node.name)
        
        # Infer layer
        layer = self._infer_layer(file_path)
        
        # Check type hints
        has_type_hints = any(
            arg.annotation is not None 
            for arg in node.args.args
        ) or node.returns is not None
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        return MethodMetadata(
            method_id=method_id,
            canonical_name=canonical_name,
            module_path=module_path,
            class_name=class_name,
            method_name=node.name,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            role=role,
            inferred_layer=layer,
            docstring=docstring[:200] if docstring else None,
            parameter_count=len(node.args.args),
            has_type_hints=has_type_hints,
        )
    
    def _infer_role(self, canonical_name: str, method_name: str) -> str:
        """Infer method role from name patterns."""
        name_lower = f"{canonical_name} {method_name}".lower()
        
        for role, keywords in self.ROLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return role
        
        return 'utility'  # default
    
    def _infer_layer(self, file_path: Path) -> str:
        """Infer layer from file path."""
        path_str = str(file_path)
        
        if 'executor' in path_str or 'Phase_two' in path_str:
            return 'executor'
        elif 'core' in path_str:
            return 'core'
        elif 'orchestration' in path_str:
            return 'orchestrator'
        elif 'processing' in path_str or 'ingest' in path_str:
            return 'processor'
        elif 'analysis' in path_str:
            return 'analyzer'
        elif 'cross_cutting' in path_str:
            return 'utility'
        else:
            return 'utility'
    
    def save_inventory(self, output_path: Path):
        """Save inventory to JSON."""
        data = {
            "_metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "scanner": "JOBFRONT_7_CurrentCodebaseScanner",
                "total_methods": len(self.methods),
                "repository_state": "CURRENT_WITH_SISAS"
            },
            "methods": {
                m.method_id: {
                    "canonical_name": m.canonical_name,
                    "module_path": m.module_path,
                    "class_name": m.class_name,
                    "method_name": m.method_name,
                    "file_path": m.file_path,
                    "line_number": m.line_number,
                    "role": m.role,
                    "layer": m.inferred_layer,
                    "docstring": m.docstring,
                    "parameter_count": m.parameter_count,
                    "has_type_hints": m.has_type_hints,
                }
                for m in self.methods
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved inventory: {output_path}")

if __name__ == "__main__":
    scanner = CurrentCodebaseScanner(root_path=Path("."))
    methods = scanner.scan_all()
    
    # Save to both locations
    output1 = Path("src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_canonical_method_inventory.json")
    output1.parent.mkdir(parents=True, exist_ok=True)
    scanner.save_inventory(output1)
    
    print(f"\n{'='*80}")
    print(f"✅ INVENTORY GENERATED: {len(methods)} methods")
    print(f"{'='*80}")
    
    # Statistics
    from collections import Counter
    role_counts = Counter(m.role for m in methods)
    layer_counts = Counter(m.inferred_layer for m in methods)
    
    print(f"\n📊 By Role:")
    for role, count in role_counts.most_common():
        print(f"   {role}: {count}")
    
    print(f"\n📊 By Layer:")
    for layer, count in layer_counts.most_common():
        print(f"   {layer}: {count}")
