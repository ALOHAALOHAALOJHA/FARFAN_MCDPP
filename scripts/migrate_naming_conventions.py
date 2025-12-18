#!/usr/bin/env python3
"""
Complete migration script to rename all legacy files to comply with naming conventions.

This script:
1. Renames 17 Phase_two Python files to phase2_X_name.py format
2. Renames 1 schema file to proper format
3. Renames 15 certificate files to proper format
4. Updates all imports across the codebase
5. Removes exemption system
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

# Mapping of old names to new names for Phase_two files
PHASE2_RENAMES = {
    "arg_router.py": "phase2_a_arg_router.py",
    "base_executor_with_contract.py": "phase2_b_base_executor_with_contract.py",
    "batch_executor.py": "phase2_c_batch_executor.py",
    "batch_generate_all_configs.py": "phase2_d_batch_generate_all_configs.py",
    "calibration_policy.py": "phase2_e_calibration_policy.py",
    "carver.py": "phase2_f_carver.py",
    "contract_validator_cqvr.py": "phase2_g_contract_validator_cqvr.py",
    "evidence_nexus.py": "phase2_h_evidence_nexus.py",
    "executor_config.py": "phase2_i_executor_config.py",
    "executor_instrumentation_mixin.py": "phase2_j_executor_instrumentation_mixin.py",
    "executor_profiler.py": "phase2_k_executor_profiler.py",
    "executor_tests.py": "phase2_l_executor_tests.py",
    "generate_all_executor_configs.py": "phase2_m_generate_all_executor_configs.py",
    "generate_all_executor_configs_complete.py": "phase2_n_generate_all_executor_configs_complete.py",
    "generate_executor_configs.py": "phase2_o_generate_executor_configs.py",
    "irrigation_synchronizer.py": "phase2_p_irrigation_synchronizer.py",
    "phase6_validation.py": "phase2_q_phase6_validation.py",
}

# Schema file rename
SCHEMA_RENAMES = {
    "system/config/log_schema.json": "system/config/log.schema.json",
}

# Certificate renames
CERT_RENAMES = {
    "CERTIFICATE_P3_01.md": "CERTIFICATE_01_PHASE3_MICRO_SCORING.md",
    "CERTIFICATE_P3_02.md": "CERTIFICATE_02_PHASE3_DIMENSION_ALIGNMENT.md",
    "CERTIFICATE_P3_03.md": "CERTIFICATE_03_PHASE3_POLICY_AREA_FIT.md",
    "CERTIFICATE_P3_04.md": "CERTIFICATE_04_PHASE3_METHOD_EXTRACTION.md",
    "CERTIFICATE_P3_05.md": "CERTIFICATE_05_PHASE3_SCORE_BOUNDS.md",
    "CERTIFICATE_P3_06.md": "CERTIFICATE_06_PHASE3_DETERMINISM.md",
    "CERTIFICATE_P3_07.md": "CERTIFICATE_07_PHASE3_VALIDATION.md",
    "CERTIFICATE_P3_08.md": "CERTIFICATE_08_PHASE3_TRANSFORMATION.md",
    "CERTIFICATE_P3_09.md": "CERTIFICATE_09_PHASE3_PROVENANCE.md",
    "CERTIFICATE_P3_10.md": "CERTIFICATE_10_PHASE3_METADATA.md",
    "CERTIFICATE_P3_11.md": "CERTIFICATE_11_PHASE3_QUALITY_GATES.md",
    "CERTIFICATE_P3_12.md": "CERTIFICATE_12_PHASE3_SIGNAL_ENRICHMENT.md",
    "CERTIFICATE_P3_13.md": "CERTIFICATE_13_PHASE3_INTEGRATION.md",
    "CERTIFICATE_P3_14.md": "CERTIFICATE_14_PHASE3_COMPLETENESS.md",
    "CERTIFICATE_P3_15.md": "CERTIFICATE_15_PHASE3_ORCHESTRATION.md",
}

REPO_ROOT = Path("/home/runner/work/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL")


def rename_phase2_files():
    """Rename Phase_two files to comply with phase2_X_name.py pattern."""
    phase2_dir = REPO_ROOT / "src/farfan_pipeline/phases/Phase_two"
    
    renamed_count = 0
    for old_name, new_name in PHASE2_RENAMES.items():
        old_path = phase2_dir / old_name
        new_path = phase2_dir / new_name
        
        if old_path.exists():
            print(f"Renaming: {old_name} → {new_name}")
            old_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"Warning: {old_path} not found")
    
    return renamed_count


def rename_schema_files():
    """Rename schema files to comply with name.schema.json pattern."""
    renamed_count = 0
    for old_rel_path, new_rel_path in SCHEMA_RENAMES.items():
        old_path = REPO_ROOT / old_rel_path
        new_path = REPO_ROOT / new_rel_path
        
        if old_path.exists():
            print(f"Renaming: {old_rel_path} → {new_rel_path}")
            old_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"Warning: {old_path} not found")
    
    return renamed_count


def rename_certificate_files():
    """Rename certificate files to comply with CERTIFICATE_NN_NAME.md pattern."""
    cert_dir = REPO_ROOT / "src/canonic_phases/phase_3_scoring_transformation/contracts/certificates"
    
    renamed_count = 0
    for old_name, new_name in CERT_RENAMES.items():
        old_path = cert_dir / old_name
        new_path = cert_dir / new_name
        
        if old_path.exists():
            print(f"Renaming: {old_name} → {new_name}")
            old_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"Warning: {old_path} not found")
    
    return renamed_count


def update_imports():
    """Update all imports across the codebase."""
    print("\nUpdating imports...")
    
    # Find all Python files
    python_files = list(REPO_ROOT.glob("**/*.py"))
    python_files = [f for f in python_files if ".venv" not in str(f) and "__pycache__" not in str(f) and ".git" not in str(f)]
    
    total_replacements = 0
    
    for py_file in python_files:
        try:
            content = py_file.read_text()
            original_content = content
            
            # Update Phase_two imports
            for old_name, new_name in PHASE2_RENAMES.items():
                old_module = old_name.replace(".py", "")
                new_module = new_name.replace(".py", "")
                
                # Various import patterns
                patterns = [
                    (f"from canonic_phases.Phase_two.{old_module}", f"from canonic_phases.Phase_two.{new_module}"),
                    (f"from src.farfan_pipeline.phases.Phase_two.{old_module}", f"from src.farfan_pipeline.phases.Phase_two.{new_module}"),
                    (f"from farfan_pipeline.phases.Phase_two.{old_module}", f"from farfan_pipeline.phases.Phase_two.{new_module}"),
                    (f"import canonic_phases.Phase_two.{old_module}", f"import canonic_phases.Phase_two.{new_module}"),
                    (f"Phase_two.{old_module}", f"Phase_two.{new_module}"),
                ]
                
                for old_pattern, new_pattern in patterns:
                    content = content.replace(old_pattern, new_pattern)
            
            if content != original_content:
                py_file.write_text(content)
                total_replacements += 1
                print(f"  Updated: {py_file.relative_to(REPO_ROOT)}")
        
        except Exception as e:
            print(f"  Error updating {py_file}: {e}")
    
    print(f"\nUpdated imports in {total_replacements} file(s)")
    return total_replacements


def remove_exemption_file():
    """Remove the .naming_exemptions file."""
    exemption_file = REPO_ROOT / ".naming_exemptions"
    if exemption_file.exists():
        print(f"\nRemoving {exemption_file}")
        exemption_file.unlink()
        return True
    return False


def update_validator_for_strict_mode():
    """Update validator to use strict mode by default."""
    validator_file = REPO_ROOT / "scripts/validate_naming_conventions.py"
    
    if validator_file.exists():
        print(f"\nUpdating validator to default to strict mode...")
        content = validator_file.read_text()
        
        # Change default behavior to strict (no exemptions)
        if 'if not args.strict:' in content:
            content = content.replace(
                'if not args.strict:',
                'if False:  # Legacy exemptions removed - strict mode always enabled'
            )
            validator_file.write_text(content)
            print("  Validator updated")
            return True
    return False


def main():
    """Run complete migration."""
    print("="*80)
    print("COMPLETE NAMING CONVENTION MIGRATION")
    print("="*80)
    print()
    
    print("Step 1: Renaming Phase_two files...")
    phase2_count = rename_phase2_files()
    
    print("\nStep 2: Renaming schema files...")
    schema_count = rename_schema_files()
    
    print("\nStep 3: Renaming certificate files...")
    cert_count = rename_certificate_files()
    
    print("\nStep 4: Updating imports...")
    import_count = update_imports()
    
    print("\nStep 5: Removing exemption file...")
    exemption_removed = remove_exemption_file()
    
    print("\nStep 6: Updating validator for strict mode...")
    validator_updated = update_validator_for_strict_mode()
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE")
    print("="*80)
    print()
    print(f"Summary:")
    print(f"  - Phase_two files renamed: {phase2_count}")
    print(f"  - Schema files renamed: {schema_count}")
    print(f"  - Certificate files renamed: {cert_count}")
    print(f"  - Import updates: {import_count}")
    print(f"  - Exemption file removed: {exemption_removed}")
    print(f"  - Validator updated: {validator_updated}")
    print()
    print("Next steps:")
    print("1. Run: python scripts/validate_naming_conventions.py")
    print("2. Run tests to verify no breakages")
    print("3. Commit changes")


if __name__ == "__main__":
    main()
