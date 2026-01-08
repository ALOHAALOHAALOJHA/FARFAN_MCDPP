#!/usr/bin/env python3
"""
Documentation Enforcer
Enforces rigid naming policies for documentation files
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
import shutil

class DocumentationEnforcer:
    """Enforces naming policies for documentation files."""
    
    def __init__(self):
        self.documentation_pattern = re.compile(r'^[A-Z][A-Z0-9_]*\.md$')
        self.violations = []
        
    def scan_documentation_files(self, docs_dir: str) -> List[Dict]:
        """Scan documentation files for naming violations."""
        violations = []
        
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            return violations
            
        # Check all markdown files in the directory
        for md_file in docs_path.rglob("*.md"):
            violations.extend(self._check_documentation_naming(md_file))
        
        return violations
    
    def _check_documentation_naming(self, file_path: Path) -> List[Dict]:
        """Check if a documentation file follows the correct naming convention."""
        violations = []
        
        # Check if filename matches the uppercase pattern
        if not self.documentation_pattern.match(file_path.name):
            violations.append({
                'type': 'INVALID_DOCUMENTATION_NAMING',
                'file': str(file_path),
                'severity': 'ERROR',
                'message': f'Documentation file {file_path.name} does not match required pattern: UPPERCASE_WITH_UNDERSCORES.md'
            })
        
        # Check for required documentation structure
        violations.extend(self._check_documentation_content(file_path))
        
        return violations
    
    def _check_documentation_content(self, file_path: Path) -> List[Dict]:
        """Check if documentation file has required content structure."""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for required documentation sections
            required_sections = ['Abstract', 'Introduction', 'Methodology', 'Results', 'Conclusion']
            missing_sections = []
            
            for section in required_sections:
                if f'# {section}' not in content and f'## {section}' not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                violations.append({
                    'type': 'MISSING_DOCUMENTATION_SECTIONS',
                    'file': str(file_path),
                    'severity': 'WARNING',
                    'message': f'Missing required sections in documentation {file_path.name}: {", ".join(missing_sections)}'
                })
        
        except Exception as e:
            violations.append({
                'type': 'FILE_READ_ERROR',
                'file': str(file_path),
                'severity': 'ERROR',
                'message': f'Could not read documentation file {file_path}: {str(e)}'
            })
        
        return violations
    
    def enforce_documentation(self, docs_dir: str, dry_run: bool = True) -> Dict:
        """Enforce compliance for documentation files."""
        violations = self.scan_documentation_files(docs_dir)
        
        if not violations:
            print("✅ All documentation files are compliant!")
            return {'violations_found': 0, 'violations_fixed': 0, 'dry_run': dry_run}
        
        print(f"Found {len(violations)} violations in documentation files:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation['severity']}] {violation['message']}")
        
        if not dry_run:
            fixed_count = self._fix_documentation_violations(violations)
            print(f"Fixed {fixed_count} violations")
        
        return {
            'violations_found': len(violations),
            'violations_fixed': self._fix_documentation_violations(violations) if not dry_run else 0,
            'dry_run': dry_run
        }
    
    def _fix_documentation_violations(self, violations: List[Dict]) -> int:
        """Attempt to fix documentation violations."""
        fixed_count = 0
        
        for violation in violations:
            if violation['type'] == 'INVALID_DOCUMENTATION_NAMING':
                # Try to fix by renaming the file to follow the correct pattern
                file_path = Path(violation['file'])
                if self._attempt_rename_documentation_file(file_path):
                    fixed_count += 1
            elif violation['type'] == 'MISSING_DOCUMENTATION_SECTIONS':
                # Try to fix by adding missing sections
                file_path = Path(violation['file'])
                if self._attempt_add_missing_sections(file_path):
                    fixed_count += 1
        
        return fixed_count
    
    def _attempt_rename_documentation_file(self, file_path: Path) -> bool:
        """Attempt to rename a documentation file to follow correct naming."""
        # Convert to uppercase with underscores
        stem = file_path.stem
        new_stem = stem.upper().replace('-', '_')
        new_name = f"{new_stem}.md"
        new_path = file_path.parent / new_name
        
        print(f"    Renaming {file_path.name} → {new_name}")
        
        # Actually rename the file
        try:
            file_path.rename(new_path)
            return True
        except Exception as e:
            print(f"    Failed to rename {file_path}: {e}")
            return False
    
    def _attempt_add_missing_sections(self, file_path: Path) -> bool:
        """Attempt to add missing required sections to documentation."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Add required sections if missing
            required_sections = ['Abstract', 'Introduction', 'Methodology', 'Results', 'Conclusion']
            sections_to_add = []
            
            for section in required_sections:
                if f'# {section}' not in content and f'## {section}' not in content:
                    sections_to_add.append(section)
            
            if sections_to_add:
                # Add missing sections to the end of the file
                for section in sections_to_add:
                    content += f"\n## {section}\n\n[Content for {section} section]\n"
                
                print(f"    Adding missing sections to {file_path.name}")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            print(f"    Failed to add missing sections to {file_path}: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Enforcer')
    parser.add_argument('--path', default='./docs', 
                       help='Path to documentation directory (default: ./docs)')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (otherwise dry run)')
    
    args = parser.parse_args()
    
    enforcer = DocumentationEnforcer()
    result = enforcer.enforce_documentation(args.path, dry_run=not args.fix)
    
    print(f"\n📊 Documentation Enforcement Summary:")
    print(f"   Violations found: {result['violations_found']}")
    print(f"   Violations fixed: {result['violations_fixed']}")
    print(f"   Dry run: {result['dry_run']}")


if __name__ == "__main__":
    main()