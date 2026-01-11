#!/usr/bin/env python3
"""Fix remaining GNEA violations by renaming non-compliant files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


# Mapping of old files to new compliant names
RENAME_MAP = {
    # Phase 1
    "src/farfan_pipeline/phases/Phase_1/interfaces/phase1_protocols.py": "src/farfan_pipeline/phases/Phase_1/interfaces/phase1_10_00_protocols.py",
    "src/farfan_pipeline/phases/Phase_1/interfaces/phase1_types.py": "src/farfan_pipeline/phases/Phase_1/interfaces/phase1_10_00_types.py",
    "src/farfan_pipeline/phases/Phase_1/primitives/truncation_audit.py": "src/farfan_pipeline/phases/Phase_1/primitives/phase1_00_00_truncation_audit.py",
    "src/farfan_pipeline/phases/Phase_1/primitives/streaming_extractor.py": "src/farfan_pipeline/phases/Phase_1/primitives/phase1_00_00_streaming_extractor.py",
    "src/farfan_pipeline/phases/Phase_1/tests/test_streaming_pdf_extractor.py": "src/farfan_pipeline/phases/Phase_1/tests/phase1_10_00_test_streaming_pdf_extractor.py",
    "src/farfan_pipeline/phases/Phase_1/tests/conftest.py": "src/farfan_pipeline/phases/Phase_1/tests/phase1_10_00_conftest.py",
    # Phase 2
    "src/farfan_pipeline/phases/Phase_2/contract_generator/contract_assembler.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_contract_assembler.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/run.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_run.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/json_emitter.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_json_emitter.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/contract_validator.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_contract_validator.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/input_registry.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_input_registry.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/contract_generator.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_contract_generator.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/method_expander.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_method_expander.py",
    "src/farfan_pipeline/phases/Phase_2/contract_generator/chain_composer.py": "src/farfan_pipeline/phases/Phase_2/contract_generator/phase2_10_00_chain_composer.py",
    "src/farfan_pipeline/phases/Phase_2/epistemological_assets/audit_v4_rigorous.py": "src/farfan_pipeline/phases/Phase_2/epistemological_assets/phase2_10_00_audit_v4_rigorous.py",
    "src/farfan_pipeline/phases/Phase_2/epistemological_assets/epistemological_method_classifier.py": "src/farfan_pipeline/phases/Phase_2/epistemological_assets/phase2_10_00_epistemological_method_classifier.py",
    "src/farfan_pipeline/phases/Phase_2/tests/conftest.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_conftest.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_contract_integrity.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_contract_integrity.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_execution_flow.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_execution_flow.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_end_to_end.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_end_to_end.py",
    "src/farfan_pipeline/phases/Phase_2/tests/run_adversarial_tests.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_run_adversarial_tests.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_architecture_compliance.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_architecture_compliance.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_adversarial_edge_cases.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_adversarial_edge_cases.py",
    "src/farfan_pipeline/phases/Phase_2/tests/test_per_file_validation.py": "src/farfan_pipeline/phases/Phase_2/tests/phase2_10_00_test_per_file_validation.py",
    # Phase 3
    "src/farfan_pipeline/phases/Phase_3/interface/phase3_exit_contract.py": "src/farfan_pipeline/phases/Phase_3/interface/phase3_10_00_exit_contract.py",
    "src/farfan_pipeline/phases/Phase_3/interface/phase3_entry_contract.py": "src/farfan_pipeline/phases/Phase_3/interface/phase3_10_00_entry_contract.py",
    "src/farfan_pipeline/phases/Phase_3/interface/phase3_nexus_interface_validator.py": "src/farfan_pipeline/phases/Phase_3/interface/phase3_10_00_nexus_interface_validator.py",
    "src/farfan_pipeline/phases/Phase_3/primitives/quality_levels.py": "src/farfan_pipeline/phases/Phase_3/primitives/phase3_00_00_quality_levels.py",
    "src/farfan_pipeline/phases/Phase_3/primitives/scoring_modalities.py": "src/farfan_pipeline/phases/Phase_3/primitives/phase3_00_00_scoring_modalities.py",
    "src/farfan_pipeline/phases/Phase_3/primitives/mathematical_foundation.py": "src/farfan_pipeline/phases/Phase_3/primitives/phase3_00_00_mathematical_foundation.py",
    # Phase 4
    "src/farfan_pipeline/phases/Phase_4/enhancements/adaptive_meso_scoring.py": "src/farfan_pipeline/phases/Phase_4/enhancements/phase4_95_00_adaptive_meso_scoring.py",
    "src/farfan_pipeline/phases/Phase_4/enhancements/enhanced_aggregators.py": "src/farfan_pipeline/phases/Phase_4/enhancements/phase4_95_00_enhanced_aggregators.py",
    "src/farfan_pipeline/phases/Phase_4/enhancements/signal_enriched_aggregation.py": "src/farfan_pipeline/phases/Phase_4/enhancements/phase4_95_00_signal_enriched_aggregation.py",
    "src/farfan_pipeline/phases/Phase_4/interface/phase4_7_exit_contract.py": "src/farfan_pipeline/phases/Phase_4/interface/phase4_10_00_7_exit_contract.py",
    "src/farfan_pipeline/phases/Phase_4/interface/phase4_7_entry_contract.py": "src/farfan_pipeline/phases/Phase_4/interface/phase4_10_00_7_entry_contract.py",
    "src/farfan_pipeline/phases/Phase_4/primitives/quality_levels.py": "src/farfan_pipeline/phases/Phase_4/primitives/phase4_00_00_quality_levels.py",
    "src/farfan_pipeline/phases/Phase_4/primitives/signal_enriched_primitives.py": "src/farfan_pipeline/phases/Phase_4/primitives/phase4_00_00_signal_enriched_primitives.py",
    "src/farfan_pipeline/phases/Phase_4/primitives/choquet_primitives.py": "src/farfan_pipeline/phases/Phase_4/primitives/phase4_00_00_choquet_primitives.py",
    "src/farfan_pipeline/phases/Phase_4/primitives/uncertainty_metrics.py": "src/farfan_pipeline/phases/Phase_4/primitives/phase4_00_00_uncertainty_metrics.py",
    "src/farfan_pipeline/phases/Phase_4/validation/phase4_7_validation.py": "src/farfan_pipeline/phases/Phase_4/validation/phase4_40_00_7_validation.py",
    # Phase 5
    "src/farfan_pipeline/phases/Phase_5/PHASE_5_CONSTANTS.py": "src/farfan_pipeline/phases/Phase_5/phase5_10_00_phase_5_constants.py",
    # Phase 6
    "src/farfan_pipeline/phases/Phase_6/PHASE_6_CONSTANTS.py": "src/farfan_pipeline/phases/Phase_6/phase6_10_00_phase_6_constants.py",
    # Phase 7
    "src/farfan_pipeline/phases/Phase_7/PHASE_7_CONSTANTS.py": "src/farfan_pipeline/phases/Phase_7/phase7_10_00_phase_7_constants.py",
    # Phase 8
    "src/farfan_pipeline/phases/Phase_8/interfaces/interface_validator.py": "src/farfan_pipeline/phases/Phase_8/interfaces/phase8_10_00_interface_validator.py",
    "src/farfan_pipeline/phases/Phase_8/primitives/PHASE_8_CONSTANTS.py": "src/farfan_pipeline/phases/Phase_8/primitives/phase8_00_00_phase_8_constants.py",
    "src/farfan_pipeline/phases/Phase_8/primitives/PHASE_8_ENUMS.py": "src/farfan_pipeline/phases/Phase_8/primitives/phase8_00_00_phase_8_enums.py",
    "src/farfan_pipeline/phases/Phase_8/primitives/PHASE_8_TYPES.py": "src/farfan_pipeline/phases/Phase_8/primitives/phase8_00_00_phase_8_types.py",
    "src/farfan_pipeline/phases/Phase_8/tests/generative_testing.py": "src/farfan_pipeline/phases/Phase_8/tests/phase8_10_00_generative_testing.py",
}


def rename_file(old_path: str, new_path: str) -> bool:
    """Rename a file using git mv.

    Args:
        old_path: Current file path
        new_path: New file path

    Returns:
        True if successful, False otherwise
    """
    old = Path(old_path)
    new = Path(new_path)

    if not old.exists():
        print(f"  SKIP: {old_path} (not found)")
        return False

    # Create parent directory if it doesn't exist
    new.parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["git", "mv", str(old), str(new)],
            check=True,
            capture_output=True
        )
        print(f"  ✓ {old.name} -> {new.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to rename {old_path}: {e}")
        return False


def main():
    """Main entry point."""
    print(f"Renaming {len(RENAME_MAP)} non-compliant files...\n")

    renamed = 0
    for old_path, new_path in RENAME_MAP.items():
        if rename_file(old_path, new_path):
            renamed += 1

    print(f"\nRenamed {renamed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
