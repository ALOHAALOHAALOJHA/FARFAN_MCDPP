#!/usr/bin/env python3
"""
Method Inventory Scanner for COHORT_2024 Calibration System

Scans the entire codebase to discover all methods with MODULE:CLASS.METHOD@LAYER notation
and role classifications. Generates canonical_method_inventory.json with 1995+ methods.
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MethodSignature:
    """Represents a discovered method with full metadata."""
    method_id: str
    module_path: str
    class_name: Optional[str]
    method_name: str
    full_notation: str  # MODULE:CLASS.METHOD@LAYER
    role: str
    layers: List[str]
    file_path: str
    line_number: int
    docstring: Optional[str]
    parameters: List[str]
    returns: Optional[str]


class MethodInventoryScanner:
    """Scans Python codebase to build complete method inventory."""
    
    # Role keywords for classification
    ROLE_KEYWORDS = {
        'SCORE_Q': ['score', 'rating', 'evaluate', 'assess', 'question'],
        'INGEST_PDM': ['ingest', 'load', 'read', 'parse', 'import'],
        'STRUCTURE': ['structure', 'organize', 'format', 'schema'],
        'EXTRACT': ['extract', 'retrieve', 'get', 'fetch', 'find'],
        'AGGREGATE': ['aggregate', 'summarize', 'combine', 'merge'],
        'REPORT': ['report', 'generate', 'output', 'format', 'export'],
        'META_TOOL': ['meta', 'tool', 'utility', 'helper'],
        'TRANSFORM': ['transform', 'convert', 'process', 'normalize'],
    }
    
    # Layer markers
    LAYER_MARKERS = ['@b', '@q', '@d', '@p', '@C', '@chain', '@u', '@m']
    
    def __init__(self, root_path: Path, src_dirs: List[str] = None):
        self.root_path = Path(root_path)
        self.src_dirs = src_dirs or ['src', 'farfan_core']
        self.methods: Dict[str, MethodSignature] = {}
        
    def scan_directory(self, directory: Path) -> List[MethodSignature]:
        """Recursively scan directory for Python files and extract methods."""
        methods = []
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return methods
            
        for py_file in directory.rglob('*.py'):
            try:
                file_methods = self._scan_file(py_file)
                methods.extend(file_methods)
                logger.info(f"Scanned {py_file.relative_to(self.root_path)}: {len(file_methods)} methods")
            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")
                
        return methods
    
    def _scan_file(self, file_path: Path) -> List[MethodSignature]:
        """Parse Python file and extract all method definitions."""
        methods = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Get module path relative to root
            rel_path = file_path.relative_to(self.root_path)
            module_path = str(rel_path).replace('/', '.').replace('.py', '')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a class method or standalone function
                    parent_class = self._get_parent_class(tree, node)
                    method_sig = self._create_method_signature(
                        node, module_path, parent_class, file_path
                    )
                    if method_sig:
                        methods.append(method_sig)
                        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            
        return methods
    
    def _get_parent_class(self, tree: ast.AST, func_node: ast.FunctionDef) -> Optional[str]:
        """Find parent class of a function if it exists."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item == func_node:
                        return node.name
        return None
    
    def _create_method_signature(
        self,
        node: ast.FunctionDef,
        module_path: str,
        class_name: Optional[str],
        file_path: Path
    ) -> Optional[MethodSignature]:
        """Create MethodSignature from AST node."""
        method_name = node.name
        
        # Skip private methods unless they're important
        if method_name.startswith('_') and not method_name.startswith('__'):
            return None
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract parameters
        parameters = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        # Extract return type annotation
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # Classify role based on method name and docstring
        role = self._classify_role(method_name, docstring or '')
        
        # Detect layers from docstring or default
        layers = self._detect_layers(docstring or '')
        if not layers:
            layers = ['@b', '@u', '@m']  # Default minimum layers
        
        # Build full notation: MODULE:CLASS.METHOD@LAYER
        if class_name:
            full_notation = f"{module_path}:{class_name}.{method_name}@{','.join(layers)}"
            method_id = f"{class_name}.{method_name}"
        else:
            full_notation = f"{module_path}:{method_name}@{','.join(layers)}"
            method_id = method_name
        
        return MethodSignature(
            method_id=method_id,
            module_path=module_path,
            class_name=class_name,
            method_name=method_name,
            full_notation=full_notation,
            role=role,
            layers=layers,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            docstring=docstring,
            parameters=parameters,
            returns=returns
        )
    
    def _classify_role(self, method_name: str, docstring: str) -> str:
        """Classify method role based on name and docstring."""
        text = f"{method_name} {docstring}".lower()
        
        role_scores = {}
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                role_scores[role] = score
        
        if role_scores:
            return max(role_scores.items(), key=lambda x: x[1])[0]
        
        return 'META_TOOL'  # Default role
    
    def _detect_layers(self, docstring: str) -> List[str]:
        """Detect layer markers in docstring."""
        layers = []
        for layer in self.LAYER_MARKERS:
            if layer in docstring:
                layers.append(layer)
        return layers
    
    def scan_all(self) -> Dict[str, Any]:
        """Scan all configured directories and build inventory."""
        all_methods = []
        
        for src_dir in self.src_dirs:
            src_path = self.root_path / src_dir
            if src_path.exists():
                logger.info(f"Scanning directory: {src_path}")
                methods = self.scan_directory(src_path)
                all_methods.extend(methods)
            else:
                logger.warning(f"Source directory not found: {src_path}")
        
        # Build inventory dictionary
        inventory = {
            '_cohort_metadata': {
                'cohort_id': 'COHORT_2024',
                'creation_date': datetime.now().isoformat(),
                'wave_version': 'REFACTOR_WAVE_2024_12',
                'scan_timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'scan_timestamp': datetime.now().isoformat(),
                'repository': 'F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE',
                'total_methods': len(all_methods),
                'description': 'Canonical method inventory for F.A.R.F.A.N policy analysis pipeline',
                'scanned_directories': self.src_dirs
            },
            'methods': {}
        }
        
        # Add methods to inventory
        for method in all_methods:
            inventory['methods'][method.full_notation] = {
                'method_id': method.method_id,
                'module_path': method.module_path,
                'class_name': method.class_name,
                'method_name': method.method_name,
                'role': method.role,
                'layers': method.layers,
                'file_path': method.file_path,
                'line_number': method.line_number,
                'docstring': method.docstring,
                'parameters': method.parameters,
                'returns': method.returns
            }
        
        return inventory


def main():
    """Main entry point for scanner."""
    import sys
    
    root_path = Path(__file__).parent.parent.parent.parent.parent
    
    scanner = MethodInventoryScanner(
        root_path=root_path,
        src_dirs=['src', 'farfan_core', 'tests']
    )
    
    logger.info("Starting method inventory scan...")
    inventory = scanner.scan_all()
    
    output_file = Path(__file__).parent / 'COHORT_2024_canonical_method_inventory.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2)
    
    logger.info(f"Inventory saved to {output_file}")
    logger.info(f"Total methods discovered: {inventory['metadata']['total_methods']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
