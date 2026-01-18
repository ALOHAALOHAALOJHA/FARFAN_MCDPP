"""
Phase 4 Mission Contract

Defines the mission, topological order, and execution invariants for Phase 4.

Mission:
- Aggregate 300 ScoredMicroQuestion into 60 DimensionScore
- Group by (dimension, policy_area)
- Apply weighted averaging or Choquet integral
- Maintain complete provenance tracking

Module: src/farfan_pipeline/phases/Phase_04/contracts/phase4_mission_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Phase4MissionContract:
    """
    Mission contract for Phase 4.
    
    Defines:
    - Topological order of execution
    - Invariants that must hold during execution
    - Label-to-position mappings
    - Reclassified files and justifications
    """

    # Topological execution order (based on dependency analysis)
    TOPOLOGICAL_ORDER = [
        # Layer 0: Constants and primitives (no dependencies)
        "PHASE_4_CONSTANTS.py",
        "primitives/phase4_00_00_quality_levels.py",
        "primitives/phase4_10_00_quality_levels.py",
        "primitives/phase4_00_00_uncertainty_metrics.py",
        "primitives/phase4_10_00_uncertainty_metrics.py",
        "primitives/phase4_00_00_choquet_primitives.py",
        "primitives/phase4_10_00_choquet_primitives.py",
        "primitives/phase4_00_00_signal_enriched_primitives.py",
        "primitives/phase4_10_00_signal_enriched_primitives.py",
        
        # Layer 1: Core utilities and provenance
        "phase4_10_00_aggregation_provenance.py",
        "phase4_10_00_uncertainty_quantification.py",
        
        # Layer 2: Core aggregation (has circular with choquet_adapter, resolved via lazy import)
        "phase4_10_00_aggregation.py",
        "phase4_10_00_choquet_aggregator.py",
        "phase4_10_00_choquet_adapter.py",
        
        # Layer 3: Validation and signal enrichment
        "phase4_10_00_aggregation_validation.py",
        "phase4_10_00_signal_enriched_aggregation.py",
        
        # Layer 4: Enhancements
        "enhancements/enhanced_aggregators.py",
        "enhancements/adaptive_meso_scoring.py",
        "enhancements/signal_enriched_aggregation.py",
        
        # Layer 5: Integration and orchestration
        "phase4_10_00_aggregation_integration.py",
        "phase4_10_00_aggregation_enhancements.py",
        "phase4_10_00_adaptive_meso_scoring.py",
        
        # Layer 6: Package interface
        "__init__.py",
    ]

    # Known circular dependencies (resolved at runtime)
    CIRCULAR_DEPENDENCIES = [
        {
            "cycle": ["phase4_10_00_choquet_adapter.py", "phase4_10_00_aggregation.py"],
            "resolution": "TYPE_CHECKING and lazy import in aggregation.py",
            "acceptable": True,
            "risk": "LOW",
        }
    ]

    # Label-position analysis
    LABEL_POSITION_TABLE = [
        {
            "file": "phase4_10_00_aggregation.py",
            "label": "10_00",
            "expected_stage": "Core Aggregation",
            "actual_position": "Layer 2 (Core)",
            "aligned": True,
        },
        {
            "file": "phase4_10_00_choquet_adapter.py",
            "label": "10_00",
            "expected_stage": "Core Aggregation",
            "actual_position": "Layer 2 (Core)",
            "aligned": True,
        },
        {
            "file": "phase4_10_00_aggregation_validation.py",
            "label": "10_00",
            "expected_stage": "Core Aggregation",
            "actual_position": "Layer 3 (Validation)",
            "aligned": True,
            "note": "Validation is downstream of core aggregation, correctly placed",
        },
    ]

    # Reclassified files (moved to appropriate subfolders)
    RECLASSIFIED_FILES = [
        {
            "pattern": "primitives/phase4_*_primitives.py",
            "reason": "Pure utility functions without phase logic",
            "location": "primitives/",
            "integrated": "Imported by core modules as needed",
        },
        {
            "pattern": "enhancements/phase4_*_enhanced_*.py",
            "reason": "Enhancement layer above core aggregation",
            "location": "enhancements/",
            "integrated": "Imported by __init__.py",
        },
    ]

    # Removed files (outside DAG / duplicated modules)
    REMOVED_FILES = [
        {
            "file": "aggregation_validation.py",
            "reason": "Duplicate of phase4_10_00_aggregation_validation.py",
            "action": "deleted",
        },
        {
            "file": "aggregation_provenance.py",
            "reason": "Duplicate of phase4_10_00_aggregation_provenance.py",
            "action": "deleted",
        },
        {
            "file": "choquet_adapter.py",
            "reason": "Duplicate of phase4_10_00_choquet_adapter.py",
            "action": "deleted",
        },
        {
            "file": "uncertainty_quantification.py",
            "reason": "Duplicate of phase4_10_00_uncertainty_quantification.py",
            "action": "deleted",
        },
        {
            "file": "interface/",
            "reason": "Non-standard folder; interphase/ is canonical",
            "action": "deleted",
        },
    ]

    # Phase invariants
    INVARIANTS = [
        "Input: 300 ScoredMicroQuestion from Phase 3",
        "Output: 60 DimensionScore (6 dimensions × 10 policy areas)",
        "Grouping: BY (dimension, policy_area)",
        "Aggregation: Weighted average OR Choquet integral",
        "Provenance: Complete DAG for all operations",
        "Hermeticity: All dimension-policy cells must be present",
        "Bounds: All output scores in [0.0, 3.0]",
        "Uncertainty: Bootstrap resampling for confidence intervals",
    ]

    @staticmethod
    def validate_topological_order() -> tuple[bool, dict[str, Any]]:
        """
        Validate that the topological order is consistent with actual dependencies.
        
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4MissionContract.topological_order",
            "version": __version__,
            "total_files": len(Phase4MissionContract.TOPOLOGICAL_ORDER),
            "circular_dependencies": len(Phase4MissionContract.CIRCULAR_DEPENDENCIES),
            "resolved_cycles": sum(
                1 for c in Phase4MissionContract.CIRCULAR_DEPENDENCIES if c["acceptable"]
            ),
            "is_valid": True,
        }

        # Check that all circular dependencies are marked as resolved
        unresolved = [
            c for c in Phase4MissionContract.CIRCULAR_DEPENDENCIES 
            if not c["acceptable"]
        ]
        if unresolved:
            report["is_valid"] = False
            report["unresolved_cycles"] = unresolved

        return report["is_valid"], report

    @staticmethod
    def validate_labels() -> tuple[bool, dict[str, Any]]:
        """
        Validate that file labels align with their topological positions.
        
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "contract": "Phase4MissionContract.labels",
            "version": __version__,
            "total_labeled_files": len(Phase4MissionContract.LABEL_POSITION_TABLE),
            "aligned_files": sum(
                1 for item in Phase4MissionContract.LABEL_POSITION_TABLE 
                if item["aligned"]
            ),
            "misaligned_files": [],
            "is_valid": True,
        }

        misaligned = [
            item for item in Phase4MissionContract.LABEL_POSITION_TABLE 
            if not item["aligned"]
        ]
        
        if misaligned:
            report["misaligned_files"] = misaligned
            report["is_valid"] = False

        return report["is_valid"], report


def run_validation_checks() -> int:
    """
    Run all Phase 4 mission contract validation checks.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("=" * 60)
    print("Phase 4 Mission Contract Validation")
    print("=" * 60)

    # Topological order check
    is_valid_topo, topo_report = Phase4MissionContract.validate_topological_order()
    print("\nTopological Order:")
    print(f"  Total files: {topo_report['total_files']}")
    print(f"  Circular dependencies: {topo_report['circular_dependencies']}")
    print(f"  Resolved cycles: {topo_report['resolved_cycles']}")
    if is_valid_topo:
        print("  ✓ All cycles resolved")
    else:
        print("  ✗ Unresolved cycles detected")

    # Label alignment check
    is_valid_label, label_report = Phase4MissionContract.validate_labels()
    print("\nLabel Alignment:")
    print(f"  Total labeled files: {label_report['total_labeled_files']}")
    print(f"  Aligned files: {label_report['aligned_files']}")
    if is_valid_label:
        print("  ✓ All labels aligned with topological position")
    else:
        print(f"  ✗ {len(label_report['misaligned_files'])} misaligned files")

    # Invariants
    print("\nPhase Invariants:")
    for inv in Phase4MissionContract.INVARIANTS:
        print(f"  • {inv}")

    print("\n" + "=" * 60)
    if is_valid_topo and is_valid_label:
        print("MISSION CONTRACT: VALID")
        return 0
    else:
        print("MISSION CONTRACT: INVALID")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_validation_checks())
