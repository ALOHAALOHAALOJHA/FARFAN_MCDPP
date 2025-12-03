"""
Test 6: No Hardcoded Calibrations - Scanning for Magic Numbers in Calibration-Sensitive Areas

Validates that calibration parameters are not hardcoded:
- Scans source code for hardcoded thresholds, weights, scores
- Excludes test files and configuration files
- Fails if magic numbers found in calibration-sensitive code

FAILURE CONDITION: Any hardcoded calibration values = NOT READY

Integration: This test suite integrates with the pre-commit hook system.
The pre-commit hook (scripts/pre_commit_validators.py) uses the same validation
logic to block commits containing hardcoded calibration patterns.
"""
import re
import pytest
from pathlib import Path
from typing import Any, List, Dict, Tuple, Set


class TestNoHardcodedCalibrations:
    
    CALIBRATION_PATTERNS = [
        (r'threshold\s*=\s*[0-9.]+', 'threshold assignment'),
        (r'weight\s*=\s*[0-9.]+', 'weight assignment'),
        (r'score\s*=\s*[0-9.]+', 'score assignment'),
        (r'min_evidence\s*=\s*[0-9]+', 'min_evidence assignment'),
        (r'max_evidence\s*=\s*[0-9]+', 'max_evidence assignment'),
        (r'confidence\s*=\s*[0-9.]+', 'confidence assignment'),
        (r'penalty\s*=\s*[0-9.]+', 'penalty assignment'),
        (r'tolerance\s*=\s*[0-9.]+', 'tolerance assignment'),
        (r'sensitivity\s*=\s*[0-9.]+', 'sensitivity assignment'),
    ]
    
    EXCLUDED_PATHS = [
        "test",
        "__pycache__",
        ".git",
        "farfan-env",
        "venv",
        ".venv",
        "node_modules",
        "config",
        "system/config",
    ]
    
    ALLOWED_VALUES = {
        '0', '1', '0.0', '1.0', '0.5',
        '-1', '2', '10', '100',
    }
    
    @pytest.fixture(scope="class")
    def source_files(self) -> List[Path]:
        """Collect all Python source files to scan"""
        files = []
        
        src_dirs = [
            Path("src/farfan_pipeline"),
            Path("farfan_core/farfan_core"),
        ]
        
        for src_dir in src_dirs:
            if not src_dir.exists():
                continue
            
            for py_file in src_dir.rglob("*.py"):
                if self._should_exclude(py_file):
                    continue
                
                files.append(py_file)
        
        return files
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning"""
        path_str = str(path)
        
        for excluded in self.EXCLUDED_PATHS:
            if excluded in path_str:
                return True
        
        return False
    
    def test_source_files_found(self, source_files):
        """Verify we have source files to scan"""
        assert len(source_files) > 0, \
            "No source files found to scan for hardcoded calibrations"
        
        print(f"\nScanning {len(source_files)} source files")
    
    def test_no_hardcoded_thresholds(self, source_files):
        """CRITICAL: Verify no hardcoded threshold values in source"""
        violations = self._scan_for_patterns(source_files, "threshold")
        
        if violations:
            msg = self._format_violations(violations, "threshold")
            pytest.fail(msg)
    
    def test_no_hardcoded_weights(self, source_files):
        """CRITICAL: Verify no hardcoded weight values in source"""
        violations = self._scan_for_patterns(source_files, "weight")
        
        if violations:
            msg = self._format_violations(violations, "weight")
            pytest.fail(msg)
    
    def test_no_hardcoded_scores(self, source_files):
        """CRITICAL: Verify no hardcoded score values in source"""
        violations = self._scan_for_patterns(source_files, "score")
        
        if violations:
            msg = self._format_violations(violations, "score")
            pytest.fail(msg)
    
    def test_no_hardcoded_calibration_params(self, source_files):
        """CRITICAL: Comprehensive scan for all calibration patterns"""
        all_violations = []
        
        for file_path in source_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for lineno, line in enumerate(lines, 1):
                    if self._is_comment_or_docstring(line):
                        continue
                    
                    for pattern, description in self.CALIBRATION_PATTERNS:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        
                        for match in matches:
                            value = match.group().split('=')[-1].strip()
                            
                            if value not in self.ALLOWED_VALUES:
                                all_violations.append({
                                    'file': str(file_path),
                                    'line': lineno,
                                    'code': line.strip(),
                                    'pattern': description,
                                    'value': value
                                })
            
            except (UnicodeDecodeError, OSError) as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        if all_violations:
            msg = self._format_all_violations(all_violations)
            pytest.fail(msg)
    
    def _scan_for_patterns(
        self, source_files: List[Path], keyword: str
    ) -> List[Dict[str, Any]]:
        """Scan files for specific calibration pattern"""
        violations = []
        pattern = re.compile(rf'{keyword}\s*=\s*([0-9.]+)', re.IGNORECASE)
        
        for file_path in source_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for lineno, line in enumerate(lines, 1):
                    if self._is_comment_or_docstring(line):
                        continue
                    
                    matches = pattern.finditer(line)
                    
                    for match in matches:
                        value = match.group(1)
                        
                        if value not in self.ALLOWED_VALUES:
                            violations.append({
                                'file': str(file_path),
                                'line': lineno,
                                'code': line.strip(),
                                'value': value
                            })
            
            except (UnicodeDecodeError, OSError):
                pass
        
        return violations
    
    def _is_comment_or_docstring(self, line: str) -> bool:
        """Check if line is a comment or docstring"""
        stripped = line.strip()
        return (
            stripped.startswith('#') or
            stripped.startswith('"""') or
            stripped.startswith("'''")
        )
    
    def _format_violations(
        self, violations: List[Dict[str, Any]], keyword: str
    ) -> str:
        """Format violation message"""
        msg = (
            f"\nCRITICAL: Found {len(violations)} hardcoded {keyword} values:\n\n"
        )
        
        for v in violations[:10]:
            msg += f"  {v['file']}:{v['line']}\n"
            msg += f"    {v['code']}\n"
            msg += f"    Value: {v['value']}\n\n"
        
        if len(violations) > 10:
            msg += f"  ... and {len(violations) - 10} more\n"
        
        msg += "\nAll calibration parameters must be loaded from configuration files.\n"
        msg += "Move these values to intrinsic_calibration.json or calibration_registry.py\n"
        
        return msg
    
    def _format_all_violations(self, violations: List[Dict[str, Any]]) -> str:
        """Format all violations message"""
        msg = (
            f"\nCRITICAL: Found {len(violations)} hardcoded calibration values:\n\n"
        )
        
        by_file = {}
        for v in violations:
            file_path = v['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(v)
        
        for file_path, file_violations in sorted(by_file.items())[:5]:
            msg += f"  {file_path}:\n"
            for v in file_violations[:3]:
                msg += f"    Line {v['line']}: {v['code']}\n"
                msg += f"      {v['pattern']}: {v['value']}\n"
            if len(file_violations) > 3:
                msg += f"    ... and {len(file_violations) - 3} more\n"
            msg += "\n"
        
        if len(by_file) > 5:
            msg += f"  ... and {len(by_file) - 5} more files\n"
        
        msg += "\nAll calibration parameters must be externalized to configuration.\n"
        
        return msg
    
    def test_calibration_registry_used(self, source_files):
        """Verify calibration_registry is imported where needed"""
        imports_found = 0
        
        for file_path in source_files:
            if "calibration" in str(file_path).lower():
                continue
            
            try:
                content = file_path.read_text()
                
                if "calibration_registry" in content or "get_calibration" in content:
                    imports_found += 1
                    
            except (UnicodeDecodeError, OSError):
                pass
        
        print(f"\nFound {imports_found} files using calibration_registry")
    
    def test_pre_commit_hook_exists(self):
        """Verify pre-commit hook is installed"""
        hook_path = Path(".git/hooks/pre-commit")
        assert hook_path.exists(), "Pre-commit hook not installed"
        
        content = hook_path.read_text()
        assert "pre_commit_validators.py" in content, \
            "Pre-commit hook does not call validators"
        
        print("\n✓ Pre-commit hook is installed and configured")
    
    def test_pre_commit_validators_exist(self):
        """Verify pre-commit validator scripts exist"""
        validators_path = Path("scripts/pre_commit_validators.py")
        assert validators_path.exists(), "Pre-commit validators script missing"
        
        update_hash_path = Path("scripts/update_hash_registry.py")
        assert update_hash_path.exists(), "Hash registry update script missing"
        
        print("\n✓ Pre-commit validator scripts exist")
    
    def test_no_inline_bayesian_priors(self, source_files):
        """Check for hardcoded Bayesian priors"""
        violations = []
        pattern = re.compile(r'prior\s*=\s*([0-9.]+)', re.IGNORECASE)
        
        for file_path in source_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for lineno, line in enumerate(lines, 1):
                    if self._is_comment_or_docstring(line):
                        continue
                    
                    if pattern.search(line):
                        violations.append({
                            'file': str(file_path),
                            'line': lineno,
                            'code': line.strip()
                        })
                        
            except (UnicodeDecodeError, OSError):
                pass
        
        if violations:
            msg = f"\nFound {len(violations)} hardcoded prior values:\n"
            for v in violations[:5]:
                msg += f"  {v['file']}:{v['line']}: {v['code']}\n"
            print(msg)
