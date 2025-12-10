#!/usr/bin/env python3
"""
Method Signature Extractor for COHORT_2024 Calibration System

Analyzes methods to extract parametrization specifications including:
- required_inputs: mandatory parameters
- optional_inputs: optional parameters with defaults
- output_type: return type annotation or inferred type
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import inspect

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MethodSignatureExtractor:
    """Extracts detailed parametrization signatures from methods."""
    
    def __init__(self, inventory_path: Path):
        self.inventory_path = Path(inventory_path)
        self.inventory = self._load_inventory()
        self.signatures: Dict[str, Dict[str, Any]] = {}
        
    def _load_inventory(self) -> Dict[str, Any]:
        """Load the canonical method inventory."""
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Inventory not found: {self.inventory_path}")
        
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_all_signatures(self) -> Dict[str, Any]:
        """Extract signatures for all methods in inventory."""
        methods = self.inventory.get('methods', {})
        
        logger.info(f"Extracting signatures for {len(methods)} methods...")
        
        for full_notation, method_info in methods.items():
            try:
                signature = self._extract_method_signature(method_info)
                if signature:
                    self.signatures[full_notation] = signature
            except Exception as e:
                logger.error(f"Error extracting signature for {full_notation}: {e}")
        
        # Build output structure
        result = {
            '_cohort_metadata': {
                'cohort_id': 'COHORT_2024',
                'creation_date': datetime.now().isoformat(),
                'wave_version': 'REFACTOR_WAVE_2024_12',
                'extraction_timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'extraction_timestamp': datetime.now().isoformat(),
                'source_inventory': str(self.inventory_path),
                'total_signatures': len(self.signatures),
                'description': 'Method parametrization signatures with required/optional inputs and output types'
            },
            'signatures': self.signatures
        }
        
        return result
    
    def _extract_method_signature(self, method_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract detailed signature for a single method."""
        file_path = Path(self.inventory_path).parent.parent.parent.parent.parent / method_info['file_path']
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Find the specific method
            method_node = self._find_method_node(
                tree,
                method_info['method_name'],
                method_info.get('class_name')
            )
            
            if not method_node:
                return None
            
            return self._parse_signature(method_node, method_info)
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _find_method_node(
        self,
        tree: ast.AST,
        method_name: str,
        class_name: Optional[str]
    ) -> Optional[ast.FunctionDef]:
        """Find the AST node for a specific method."""
        if class_name:
            # Find within class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            return item
        else:
            # Find standalone function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    return node
        
        return None
    
    def _parse_signature(
        self,
        node: ast.FunctionDef,
        method_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse function signature to extract parametrization details."""
        required_inputs = []
        optional_inputs = []
        
        # Process arguments
        args = node.args
        
        # Get default values (aligned with the end of args)
        num_defaults = len(args.defaults)
        num_args = len(args.args)
        
        for i, arg in enumerate(args.args):
            if arg.arg == 'self' or arg.arg == 'cls':
                continue
            
            param_info = {
                'name': arg.arg,
                'type': self._get_type_annotation(arg),
                'description': self._extract_param_description(method_info.get('docstring', ''), arg.arg)
            }
            
            # Check if this arg has a default value
            default_index = i - (num_args - num_defaults)
            if default_index >= 0:
                default_value = self._get_default_value(args.defaults[default_index])
                param_info['default'] = default_value
                optional_inputs.append(param_info)
            else:
                required_inputs.append(param_info)
        
        # Process *args
        if args.vararg:
            optional_inputs.append({
                'name': f"*{args.vararg.arg}",
                'type': 'tuple',
                'description': 'Variable positional arguments'
            })
        
        # Process **kwargs
        if args.kwarg:
            optional_inputs.append({
                'name': f"**{args.kwarg.arg}",
                'type': 'dict',
                'description': 'Variable keyword arguments'
            })
        
        # Extract return type
        output_type = self._get_return_type(node)
        
        return {
            'required_inputs': required_inputs,
            'optional_inputs': optional_inputs,
            'output_type': output_type,
            'method_id': method_info['method_id'],
            'role': method_info['role'],
            'layers': method_info['layers']
        }
    
    def _get_type_annotation(self, arg: ast.arg) -> str:
        """Extract type annotation from argument."""
        if arg.annotation:
            try:
                if hasattr(ast, 'unparse'):
                    return ast.unparse(arg.annotation)
                else:
                    return self._annotation_to_string(arg.annotation)
            except:
                pass
        return 'Any'
    
    def _annotation_to_string(self, annotation: ast.AST) -> str:
        """Convert AST annotation to string representation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            value = self._annotation_to_string(annotation.value)
            slice_val = self._annotation_to_string(annotation.slice)
            return f"{value}[{slice_val}]"
        return 'Any'
    
    def _get_default_value(self, default: ast.AST) -> Any:
        """Extract default value from AST node."""
        if isinstance(default, ast.Constant):
            return default.value
        elif isinstance(default, ast.Name):
            return default.id
        elif isinstance(default, ast.List):
            return []
        elif isinstance(default, ast.Dict):
            return {}
        elif isinstance(default, ast.Tuple):
            return ()
        else:
            return 'complex_default'
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation."""
        if node.returns:
            try:
                if hasattr(ast, 'unparse'):
                    return ast.unparse(node.returns)
                else:
                    return self._annotation_to_string(node.returns)
            except:
                pass
        return 'Any'
    
    def _extract_param_description(self, docstring: str, param_name: str) -> str:
        """Extract parameter description from docstring."""
        if not docstring:
            return ''
        
        # Simple parsing for common docstring formats
        lines = docstring.split('\n')
        for i, line in enumerate(lines):
            if param_name in line and (':' in line or 'param' in line.lower()):
                # Try to get description from same or next line
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        return parts[1].strip()
                elif i + 1 < len(lines):
                    return lines[i + 1].strip()
        
        return ''


def main():
    """Main entry point for signature extractor."""
    import sys
    
    inventory_path = Path(__file__).parent / 'COHORT_2024_canonical_method_inventory.json'
    
    if not inventory_path.exists():
        logger.error(f"Inventory file not found: {inventory_path}")
        logger.error("Please run scan_methods_inventory.py first")
        return 1
    
    extractor = MethodSignatureExtractor(inventory_path)
    
    logger.info("Starting signature extraction...")
    signatures = extractor.extract_all_signatures()
    
    output_file = Path(__file__).parent / 'COHORT_2024_method_signatures.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(signatures, f, indent=2)
    
    logger.info(f"Signatures saved to {output_file}")
    logger.info(f"Total signatures extracted: {signatures['metadata']['total_signatures']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
