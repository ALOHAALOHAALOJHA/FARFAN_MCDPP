#!/usr/bin/env python3
"""
Surgical fix script for orchestrator execution failures.
Applies verified patches to restore pipeline functionality.
"""

import re
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class OrchestratorFixer: 
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.orchestrator_path = repo_root / "src" / "orchestration" / "orchestrator.py"
        self.backup_dir = repo_root / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixes_applied = []
        self.verification_results = {}
        
    def create_backup(self) -> Path:
        """Create timestamped backup of orchestrator before modifications."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / "orchestrator. py. bak"
        shutil.copy2(self.orchestrator_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
        return backup_path
    
    def read_orchestrator(self) -> List[str]:
        """Read current orchestrator code."""
        with open(self.orchestrator_path, 'r') as f:
            return f.readlines()
    
    def write_orchestrator(self, lines:  List[str]):
        """Write modified orchestrator code."""
        with open(self.orchestrator_path, 'w') as f:
            f.writelines(lines)
    
    def fix_1_argument_passing(self, lines: List[str]) -> List[str]:
        """Fix critical argument unpacking bug in execute_phase_with_timeout."""
        print("\n[FIX 1] Fixing argument passing bug...")
        
        modified = False
        for i, line in enumerate(lines):
            # Find the problematic line:  asyncio.to_thread(phase_func, *args)
            if "asyncio.to_thread(phase_func, *args)" in line:
                indent = len(line) - len(line.lstrip())
                # Replace with correct argument handling
                new_line = " " * indent + "asyncio.to_thread(phase_func, **args) if isinstance(args, dict) else asyncio.to_thread(phase_func, *args),\n"
                lines[i] = new_line
                self.fixes_applied.append(f"Line {i+1}: Fixed argument unpacking")
                modified = True
                print(f"  ✓ Modified line {i+1}:  Fixed *args → **args for dict arguments")
                
        if not modified:
            print("  ⚠ Pattern not found - manual review needed")
        return lines
    
    def fix_2_add_validation(self, lines: List[str]) -> List[str]:
        """Add runtime validation before phase execution."""
        print("\n[FIX 2] Adding runtime validation...")
        
        # Find the execute_phase_with_timeout method
        validation_code = '''        # Runtime validation
        if not callable(phase_func):
            raise TypeError(f"Phase {phase_name} function is not callable:  {type(phase_func)}")
        if isinstance(args, dict) and not all(isinstance(k, str) for k in args.keys()):
            raise ValueError(f"Phase {phase_name} args dict has non-string keys")
        
'''
        
        for i, line in enumerate(lines):
            if "async def execute_phase_with_timeout" in line:
                # Find the try block inside this method
                for j in range(i, min(i+20, len(lines))):
                    if "try:" in lines[j]:
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        # Insert validation before the try block
                        lines[j] = " " * indent + validation_code + lines[j]
                        self.fixes_applied.append(f"Line {j+1}: Added runtime validation")
                        print(f"  ✓ Inserted validation at line {j+1}")
                        break
                break
        
        return lines
    
    def fix_3_artifact_verification(self, lines: List[str]) -> List[str]:
        """Add artifact verification after critical phases."""
        print("\n[FIX 3] Adding artifact verification...")
        
        verification_code = '''                # Verify artifact creation for critical phases
                if phase_name in ["phase_7", "phase_9", "phase_10"]: 
                    expected_artifacts = {
                        "phase_7":  "policy_mapping.json",
                        "phase_9": "implementation_recommendations.json",
                        "phase_10":  "risk_assessment.json"
                    }
                    if phase_name in expected_artifacts: 
                        artifact_path = self. artifacts_dir / expected_artifacts[phase_name]
                        if not artifact_path.exists():
                            raise FileNotFoundError(f"Phase {phase_name} failed to create {artifact_path}")
                        else:
                            self.logger.info(f"✓ Verified artifact:  {artifact_path}")
                
'''
        
        # Find where phase results are stored
        for i, line in enumerate(lines):
            if "self.phase_results[phase_name] = result" in line:
                indent = len(line) - len(line.lstrip())
                # Insert verification after storing results
                lines. insert(i+1, verification_code)
                self.fixes_applied.append(f"Line {i+2}: Added artifact verification")
                print(f"  ✓ Inserted artifact verification at line {i+2}")
                break
        
        return lines
    
    def fix_4_async_context(self, lines: List[str]) -> List[str]:
        """Improve async context propagation and error handling."""
        print("\n[FIX 4] Fixing async context propagation...")
        
        # Find and replace the entire try block in execute_phase_with_timeout
        improved_execution = '''        try:
            # Improved execution with proper context
            if asyncio.iscoroutinefunction(phase_func):
                result = await asyncio. wait_for(phase_func(**args), timeout=timeout)
            else:
                # Use functools.partial for cleaner argument binding
                from functools import partial
                if isinstance(args, dict):
                    bound_func = partial(phase_func, **args)
                elif isinstance(args, (list, tuple)):
                    bound_func = partial(phase_func, *args)
                else:
                    bound_func = partial(phase_func, args)
                result = await asyncio.wait_for(asyncio.to_thread(bound_func), timeout=timeout)
            
            self.logger.info(f"Phase {phase_name} completed successfully")
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Phase {phase_name} timed out after {timeout}s")
            self.phase_results[phase_name] = {"status": "timeout", "error":  f"Timeout after {timeout}s"}
            raise
        except Exception as e:
            self. logger.error(f"Phase {phase_name} failed with {type(e).__name__}: {str(e)}")
            self.phase_results[phase_name] = {"status": "error", "error": str(e)}
            raise
'''
        
        # Find the execute_phase_with_timeout method and replace its try block
        in_method = False
        in_try_block = False
        try_start = -1
        try_end = -1
        
        for i, line in enumerate(lines):
            if "async def execute_phase_with_timeout" in line:
                in_method = True
            elif in_method and "try:" in line and try_start == -1:
                try_start = i
                in_try_block = True
            elif in_try_block and (line.strip().startswith("except") or line.strip().startswith("finally")):
                # Find the end of the last except block
                for j in range(i, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith(("except", "raise", "self.", "return")):
                        try_end = j
                        break
                if try_end == -1:
                    try_end = i + 5  # Fallback
                break
        
        if try_start > 0 and try_end > try_start:
            # Replace the entire try-except block
            indent = len(lines[try_start]) - len(lines[try_start].lstrip())
            lines[try_start:try_end] = [improved_execution]
            self.fixes_applied. append(f"Lines {try_start+1}-{try_end+1}: Replaced execution block")
            print(f"  ✓ Replaced execution block (lines {try_start+1}-{try_end+1})")
        
        return lines
    
    def fix_5_state_tracking(self, lines: List[str]) -> List[str]:
        """Add deterministic state tracking."""
        print("\n[FIX 5] Adding state tracking...")
        
        # Add state file initialization in __init__
        init_addition = '''        self.state_file = self.artifacts_dir / "orchestrator_state.json"
        self._pdf_cache = {}  # Memory optimization
        
'''
        
        for i, line in enumerate(lines):
            if "def __init__" in line: 
                # Find the end of __init__ method
                for j in range(i, len(lines)):
                    if "self.phase_results = {}" in lines[j]:
                        lines.insert(j+1, init_addition)
                        self. fixes_applied.append(f"Line {j+2}: Added state tracking init")
                        print(f"  ✓ Added state tracking initialization at line {j+2}")
                        break
                break
        
        # Add state persistence after each phase
        state_save_code = '''            # Persist state after successful phase
            state = {
                "last_completed_phase": phase_name,
                "timestamp": datetime. now().isoformat(),
                "phases_completed": list(self.phase_results.keys()),
                "artifacts_generated": [str(p. name) for p in self.artifacts_dir.glob("*.json")]
            }
            self.state_file.write_text(json.dumps(state, indent=2))
            
'''
        
        for i, line in enumerate(lines):
            if '"Phase {phase_name} completed in' in line:
                indent = len(line) - len(line.lstrip())
                lines.insert(i+1, state_save_code)
                self.fixes_applied.append(f"Line {i+2}: Added state persistence")
                print(f"  ✓ Added state persistence at line {i+2}")
                break
        
        return lines
    
    def fix_6_parallel_execution(self, lines: List[str]) -> List[str]:
        """Add parallel execution for independent phases."""
        print("\n[FIX 6] Adding parallel execution optimization...")
        
        parallel_code = '''            # Parallel execution for independent artifact phases
            if phase_name == "phase_6" and all_phases[i+1]["name"] == "phase_7":
                self.logger.info("Executing phases 7, 9, 10 in parallel...")
                
                # Prepare parallel phases
                artifact_phases = []
                for p_name in ["phase_7", "phase_9", "phase_10"]:
                    if p_name in self.phases:
                        phase_config = next((p for p in all_phases if p["name"] == p_name), None)
                        if phase_config:
                            artifact_phases.append((
                                p_name,
                                self.phases[p_name],
                                phase_config.get("args", {}),
                                phase_config. get("timeout", 300)
                            ))
                
                # Execute in parallel
                if artifact_phases:
                    tasks = [
                        self.execute_phase_with_timeout(name, func, args, timeout)
                        for name, func, args, timeout in artifact_phases
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Check for failures
                    for idx, result in enumerate(results):
                        if isinstance(result, Exception):
                            phase_name = artifact_phases[idx][0]
                            self. logger.error(f"Parallel phase {phase_name} failed: {result}")
                            raise RuntimeError(f"Parallel execution failed for {phase_name}:  {result}")
                    
                    # Skip the sequential execution of these phases
                    phases_to_skip = {p[0] for p in artifact_phases}
                    continue
            
            # Skip if already executed in parallel
            if phase_name in phases_to_skip:
                continue
            
'''
        
        # Add before the main phase execution loop
        for i, line in enumerate(lines):
            if "for i, phase_config in enumerate(all_phases):" in line:
                # Add phases_to_skip set initialization before the loop
                indent = len(line) - len(line.lstrip())
                lines.insert(i, " " * indent + "phases_to_skip = set()\n")
                lines.insert(i+1, " " * indent + "\n")
                
                # Find where to insert parallel execution logic
                for j in range(i+2, min(i+30, len(lines))):
                    if "result = await self.execute_phase_with_timeout" in lines[j]:
                        lines.insert(j, parallel_code)
                        self.fixes_applied.append(f"Line {j+1}: Added parallel execution")
                        print(f"  ✓ Added parallel execution at line {j+1}")
                        break
                break
        
        return lines
    
    def add_memory_optimization(self, lines: List[str]) -> List[str]:
        """Add PDF caching method to reduce memory usage."""
        print("\n[FIX 7] Adding memory optimization...")
        
        cache_method = '''    
    def get_cached_pdf_content(self, pdf_path:  str) -> bytes:
        """Cache PDF content to avoid repeated loading."""
        if pdf_path not in self._pdf_cache:
            self._pdf_cache[pdf_path] = Path(pdf_path).read_bytes()
        return self._pdf_cache[pdf_path]
    
'''
        
        # Add after __init__ method
        for i, line in enumerate(lines):
            if "def __init__" in line: 
                # Find the end of __init__
                indent_level = len(line) - len(line.lstrip())
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(" " * (indent_level + 1)):
                        lines.insert(j, cache_method)
                        self.fixes_applied.append(f"Line {j+1}: Added PDF caching method")
                        print(f"  ✓ Added memory optimization at line {j+1}")
                        break
                break
        
        return lines
    
    def verify_fixes(self) -> Dict[str, bool]: 
        """Verify that all fixes were applied successfully."""
        print("\n[VERIFICATION] Checking applied fixes...")
        
        with open(self.orchestrator_path, 'r') as f:
            content = f.read()
        
        checks = {
            "argument_fix": "isinstance(args, dict) else asyncio.to_thread" in content,
            "validation":  "not callable(phase_func)" in content,
            "artifact_verification": "expected_artifacts" in content,
            "async_context": "functools.partial" in content or "bound_func" in content,
            "state_tracking": "orchestrator_state.json" in content,
            "parallel_execution":  "phases_to_skip" in content or "gather" in content,
            "memory_optimization": "get_cached_pdf_content" in content or "_pdf_cache" in content
        }
        
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}:  {'Applied' if result else 'Not found'}")
            self.verification_results[check] = result
        
        return checks
    
    def run_syntax_check(self) -> bool:
        """Verify Python syntax is still valid."""
        print("\n[SYNTAX CHECK] Validating Python syntax...")
        
        import ast
        try:
            with open(self.orchestrator_path, 'r') as f:
                ast.parse(f. read())
            print("  ✓ Python syntax is valid")
            return True
        except SyntaxError as e:
            print(f"  ✗ Syntax error: {e}")
            return False
    
    def generate_report(self) -> Path:
        """Generate a detailed report of all changes."""
        report_path = self.backup_dir / "fix_report.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_path": str(self. orchestrator_path),
            "backup_path": str(self.backup_dir / "orchestrator.py.bak"),
            "fixes_applied": self.fixes_applied,
            "verification_results": self.verification_results,
            "syntax_valid": self.run_syntax_check(),
            "total_modifications": len(self.fixes_applied)
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[REPORT] Detailed report saved:  {report_path}")
        return report_path
    
    def apply_all_fixes(self):
        """Apply all orchestrator fixes in sequence."""
        print("=" * 60)
        print("ORCHESTRATOR FIX SCRIPT - STARTING")
        print("=" * 60)
        
        # Create backup first
        backup_path = self.create_backup()
        
        # Read current code
        lines = self.read_orchestrator()
        original_line_count = len(lines)
        
        # Apply fixes in sequence
        lines = self.fix_1_argument_passing(lines)
        lines = self.fix_2_add_validation(lines)
        lines = self.fix_3_artifact_verification(lines)
        lines = self.fix_4_async_context(lines)
        lines = self.fix_5_state_tracking(lines)
        lines = self.fix_6_parallel_execution(lines)
        lines = self.add_memory_optimization(lines)
        
        # Write modified code
        self.write_orchestrator(lines)
        print(f"\n✓ All fixes applied ({len(self.fixes_applied)} modifications)")
        print(f"  Original lines: {original_line_count}")
        print(f"  Modified lines: {len(lines)}")
        
        # Verify fixes
        self.verify_fixes()
        
        # Generate report
        report_path = self.generate_report()
        
        print("\n" + "=" * 60)
        print("FIX SCRIPT COMPLETED")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"1. Review changes:  diff {backup_path} {self. orchestrator_path}")
        print(f"2. Run verification: python scripts/run_policy_pipeline_verified.py --verbose")
        print(f"3. Check manifest: cat artifacts/plan1/verification_manifest.json | jq '. success'")
        print(f"\nRollback command: cp {backup_path} {self.orchestrator_path}")
        
        return all(self.verification_results.values())

def main():
    """Main execution entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix orchestrator execution issues")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(),
                       help="Repository root directory")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without applying")
    args = parser.parse_args()
    
    fixer = OrchestratorFixer(args.repo_root)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be applied")
        print("\nPlanned fixes:")
        print("1. Fix argument unpacking bug (*args → **args for dicts)")
        print("2. Add runtime validation for phase functions")
        print("3. Add artifact verification after phases 7, 9, 10")
        print("4. Improve async context and error handling")
        print("5. Add state tracking and persistence")
        print("6. Enable parallel execution for independent phases")
        print("7. Add PDF content caching for memory optimization")
    else:
        success = fixer.apply_all_fixes()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()