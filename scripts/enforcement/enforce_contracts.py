#!/usr/bin/env python3
"""
Executor Contract Enforcer
Enforces rigid naming policies for executor contracts
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
import shutil

class ContractEnforcer:
    """Enforces naming policies for executor contract files."""
    
    def __init__(self):
        self.contract_pattern = re.compile(r'^Q\d{3}_.*\.json$')
        self.violations = []
        
    def scan_contract_files(self, contracts_dir: str) -> List[Dict]:
        """Scan contract files for naming violations."""
        violations = []
        
        contracts_path = Path(contracts_dir)
        if not contracts_path.exists():
            return violations
            
        # Check all JSON files in the directory
        for json_file in contracts_path.rglob("*.json"):
            violations.extend(self._check_contract_naming(json_file))
        
        return violations
    
    def _check_contract_naming(self, file_path: Path) -> List[Dict]:
        """Check if a contract file follows the correct naming convention."""
        violations = []
        
        # Check if filename matches the QXXX pattern
        if not self.contract_pattern.match(file_path.name):
            violations.append({
                'type': 'INVALID_CONTRACT_NAMING',
                'file': str(file_path),
                'severity': 'ERROR',
                'message': f'Contract file {file_path.name} does not match required pattern: QXXX_*.json'
            })
        
        # Check for required contract structure
        violations.extend(self._check_contract_content(file_path))
        
        return violations
    
    def _check_contract_content(self, file_path: Path) -> List[Dict]:
        """Check if contract file has required content structure."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Check for required contract structure
            required_fields = ['question_id', 'method_binding', 'input_schema', 'output_schema']
            for field in required_fields:
                if field not in content:
                    violations.append({
                        'type': 'MISSING_CONTRACT_FIELD',
                        'file': str(file_path),
                        'severity': 'ERROR',
                        'message': f'Missing required field "{field}" in contract {file_path.name}'
                    })
        
        except json.JSONDecodeError:
            violations.append({
                'type': 'INVALID_JSON',
                'file': str(file_path),
                'severity': 'CRITICAL',
                'message': f'Invalid JSON in contract file {file_path.name}'
            })
        except Exception as e:
            violations.append({
                'type': 'FILE_READ_ERROR',
                'file': str(file_path),
                'severity': 'ERROR',
                'message': f'Could not read contract file {file_path}: {str(e)}'
            })
        
        return violations
    
    def enforce_contracts(self, contracts_dir: str, dry_run: bool = True) -> Dict:
        """Enforce compliance for contract files."""
        violations = self.scan_contract_files(contracts_dir)
        
        if not violations:
            print("✅ All contract files are compliant!")
            return {'violations_found': 0, 'violations_fixed': 0, 'dry_run': dry_run}
        
        print(f"Found {len(violations)} violations in contract files:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation['severity']}] {violation['message']}")
        
        if not dry_run:
            fixed_count = self._fix_contract_violations(violations)
            print(f"Fixed {fixed_count} violations")
        
        return {
            'violations_found': len(violations),
            'violations_fixed': self._fix_contract_violations(violations) if not dry_run else 0,
            'dry_run': dry_run
        }
    
    def _fix_contract_violations(self, violations: List[Dict]) -> int:
        """Attempt to fix contract violations."""
        fixed_count = 0
        
        for violation in violations:
            if violation['type'] == 'INVALID_CONTRACT_NAMING':
                # Try to fix by renaming the file to follow the correct pattern
                file_path = Path(violation['file'])
                if self._attempt_rename_contract_file(file_path):
                    fixed_count += 1
            elif violation['type'] == 'INVALID_JSON':
                # Try to fix by creating a minimal valid contract
                file_path = Path(violation['file'])
                if self._attempt_fix_invalid_json(file_path):
                    fixed_count += 1
            elif violation['type'] == 'MISSING_CONTRACT_FIELD':
                # Try to fix by adding missing fields
                file_path = Path(violation['file'])
                if self._attempt_add_missing_fields(file_path):
                    fixed_count += 1
        
        return fixed_count
    
    def _attempt_rename_contract_file(self, file_path: Path) -> bool:
        """Attempt to rename a contract file to follow correct naming."""
        # Extract potential question number from filename
        stem = file_path.stem
        # Look for any 3-digit number in the stem
        import re
        matches = re.findall(r'\d{3}', stem)
        
        if matches:
            # Use the first 3-digit number found
            q_num = matches[0]
        else:
            # If no 3-digit number found, use a default
            q_num = "999"
        
        new_name = f"Q{q_num}_{stem.replace('-', '_').lower()}.json"
        new_path = file_path.parent / new_name
        
        print(f"    Renaming {file_path.name} → {new_name}")
        
        # Actually rename the file
        try:
            file_path.rename(new_path)
            return True
        except Exception as e:
            print(f"    Failed to rename {file_path}: {e}")
            return False
    
    def _attempt_fix_invalid_json(self, file_path: Path) -> bool:
        """Attempt to fix an invalid JSON file by creating a minimal valid contract."""
        minimal_contract = {
            "schema_version": "3.0.0",
            "question_id": "Q999",
            "method_binding": {
                "methods": [],
                "execution_order": []
            },
            "input_schema": {
                "type": "object",
                "properties": {}
            },
            "output_schema": {
                "type": "object", 
                "properties": {}
            },
            "validation_rules": {},
            "metadata": {
                "created": "2025-01-07T00:00:00Z",
                "updated": "2025-01-07T00:00:00Z",
                "status": "draft"
            }
        }
        
        print(f"    Fixing invalid JSON in {file_path.name}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(minimal_contract, f, indent=2)
            return True
        except Exception as e:
            print(f"    Failed to fix JSON in {file_path}: {e}")
            return False
    
    def _attempt_add_missing_fields(self, file_path: Path) -> bool:
        """Attempt to add missing required fields to a contract."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Add missing required fields
            if 'question_id' not in content:
                # Extract from filename if possible
                match = re.search(r'Q(\d{3})', file_path.name)
                content['question_id'] = match.group(1) if match else "Q999"
            
            if 'method_binding' not in content:
                content['method_binding'] = {
                    "methods": [],
                    "execution_order": []
                }
            
            if 'input_schema' not in content:
                content['input_schema'] = {
                    "type": "object",
                    "properties": {}
                }
            
            if 'output_schema' not in content:
                content['output_schema'] = {
                    "type": "object",
                    "properties": {}
                }
            
            print(f"    Adding missing fields to {file_path.name}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"    Failed to add missing fields to {file_path}: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Executor Contract Enforcer')
    parser.add_argument('--path', default='./executor_contracts', 
                       help='Path to contracts directory (default: ./executor_contracts)')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (otherwise dry run)')
    
    args = parser.parse_args()
    
    enforcer = ContractEnforcer()
    result = enforcer.enforce_contracts(args.path, dry_run=not args.fix)
    
    print(f"\n📊 Contract Enforcement Summary:")
    print(f"   Violations found: {result['violations_found']}")
    print(f"   Violations fixed: {result['violations_fixed']}")
    print(f"   Dry run: {result['dry_run']}")


if __name__ == "__main__":
    main()