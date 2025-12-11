#!/usr/bin/env python3
"""
Calibration Inventory Consolidation Script for COHORT_2024

Orchestrates the complete calibration inventory process:
1. Scans codebase for all methods (scan_methods_inventory.py)
2. Extracts parametrization signatures (method_signature_extractor.py)
3. Validates calibration coverage across 8 layers (calibration_coverage_validator.py)
4. Generates comprehensive summary report

Outputs three authoritative files in system/config/calibration/inventories/:
- COHORT_2024_canonical_method_inventory.json
- COHORT_2024_method_signatures.json
- COHORT_2024_calibration_coverage_matrix.json
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('calibration_consolidation.log')
    ]
)
logger = logging.getLogger(__name__)


class CalibrationInventoryConsolidator:
    """Orchestrates complete calibration inventory generation and consolidation."""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.inventory_dir = self.root_path / 'system/config/calibration/inventories'
        self.source_calibration_dir = (
            self.root_path / 'src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration'
        )
        
        # Output file paths
        self.inventory_file = self.inventory_dir / 'COHORT_2024_canonical_method_inventory.json'
        self.signatures_file = self.inventory_dir / 'COHORT_2024_method_signatures.json'
        self.coverage_file = self.inventory_dir / 'COHORT_2024_calibration_coverage_matrix.json'
        self.summary_file = self.inventory_dir / 'COHORT_2024_consolidation_summary.md'
        
    def consolidate_all(self) -> bool:
        """Run complete consolidation process."""
        logger.info("="*80)
        logger.info("COHORT_2024 Calibration Inventory Consolidation")
        logger.info("="*80)
        
        try:
            # Step 1: Scan methods inventory
            logger.info("\n[STEP 1/3] Scanning method inventory...")
            if not self._run_scanner():
                logger.error("Method inventory scan failed")
                return False
            
            # Step 2: Extract signatures
            logger.info("\n[STEP 2/3] Extracting method signatures...")
            if not self._run_signature_extractor():
                logger.error("Signature extraction failed")
                return False
            
            # Step 3: Generate coverage matrix
            logger.info("\n[STEP 3/3] Generating calibration coverage matrix...")
            if not self._run_coverage_validator():
                logger.error("Coverage validation failed")
                return False
            
            # Step 4: Generate summary report
            logger.info("\n[STEP 4/4] Generating summary report...")
            self._generate_summary_report()
            
            logger.info("\n" + "="*80)
            logger.info("Consolidation completed successfully!")
            logger.info("="*80)
            
            self._print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Consolidation failed: {e}", exc_info=True)
            return False
    
    def _run_scanner(self) -> bool:
        """Run method inventory scanner."""
        from scan_methods_inventory import MethodInventoryScanner
        
        try:
            scanner = MethodInventoryScanner(
                root_path=self.root_path,
                src_dirs=['src', 'tests']
            )
            
            inventory = scanner.scan_all()
            
            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2)
            
            logger.info(f"✓ Inventory saved: {self.inventory_file}")
            logger.info(f"  Total methods: {inventory['metadata']['total_methods']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Scanner failed: {e}", exc_info=True)
            return False
    
    def _run_signature_extractor(self) -> bool:
        """Run method signature extractor."""
        from method_signature_extractor import MethodSignatureExtractor
        
        try:
            extractor = MethodSignatureExtractor(self.inventory_file)
            signatures = extractor.extract_all_signatures()
            
            with open(self.signatures_file, 'w', encoding='utf-8') as f:
                json.dump(signatures, f, indent=2)
            
            logger.info(f"✓ Signatures saved: {self.signatures_file}")
            logger.info(f"  Total signatures: {signatures['metadata']['total_signatures']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Signature extractor failed: {e}", exc_info=True)
            return False
    
    def _run_coverage_validator(self) -> bool:
        """Run calibration coverage validator."""
        from calibration_coverage_validator import CalibrationCoverageValidator
        
        try:
            intrinsic_path = self.source_calibration_dir / 'COHORT_2024_intrinsic_calibration.json'
            compat_path = self.source_calibration_dir / 'COHORT_2024_method_compatibility.json'
            
            validator = CalibrationCoverageValidator(
                inventory_path=self.inventory_file,
                intrinsic_calibration_path=intrinsic_path,
                method_compatibility_path=compat_path
            )
            
            coverage_matrix = validator.generate_coverage_matrix()
            
            with open(self.coverage_file, 'w', encoding='utf-8') as f:
                json.dump(coverage_matrix, f, indent=2)
            
            logger.info(f"✓ Coverage matrix saved: {self.coverage_file}")
            stats = coverage_matrix['statistics']
            logger.info(f"  Fully calibrated: {stats['fully_calibrated']}/{stats['total_methods']}")
            logger.info(f"  Calibration %: {stats['calibration_percentage']}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Coverage validator failed: {e}", exc_info=True)
            return False
    
    def _generate_summary_report(self) -> None:
        """Generate comprehensive markdown summary report."""
        try:
            # Load all three files
            inventory = self._load_json(self.inventory_file)
            signatures = self._load_json(self.signatures_file)
            coverage = self._load_json(self.coverage_file)
            
            # Build report
            report_lines = [
                "# COHORT_2024 Calibration Inventory Consolidation Summary",
                "",
                f"**Generated:** {datetime.now().isoformat()}",
                f"**Wave Version:** REFACTOR_WAVE_2024_12",
                "",
                "## Overview",
                "",
                "This report summarizes the consolidated calibration inventory for the COHORT_2024",
                "calibration system, including method discovery, parametrization analysis, and",
                "calibration coverage across all 8 layers.",
                "",
                "## Consolidated Artifacts",
                "",
                "### 1. Canonical Method Inventory",
                f"- **File:** `{self.inventory_file.name}`",
                f"- **Total Methods:** {inventory.get('metadata', {}).get('total_methods', 0)}",
                f"- **Scan Timestamp:** {inventory.get('metadata', {}).get('scan_timestamp', 'N/A')}",
                "",
                "Complete inventory of all methods in the codebase with MODULE:CLASS.METHOD@LAYER",
                "notation and role classifications.",
                "",
                "### 2. Method Signatures",
                f"- **File:** `{self.signatures_file.name}`",
                f"- **Total Signatures:** {signatures.get('metadata', {}).get('total_signatures', 0)}",
                "",
                "Detailed parametrization specifications including:",
                "- Required inputs (mandatory parameters)",
                "- Optional inputs (with defaults)",
                "- Output types (return annotations)",
                "",
                "### 3. Calibration Coverage Matrix",
                f"- **File:** `{self.coverage_file.name}`",
                "",
                "Comprehensive mapping of methods to computed layer scores across all 8 layers.",
                "",
                "## Statistics",
                "",
                "### Method Count",
                f"- **Total Methods Discovered:** {inventory.get('metadata', {}).get('total_methods', 0)}",
                "",
                "### Parametrization Coverage",
            ]
            
            # Calculate parametrization coverage
            total_methods = inventory.get('metadata', {}).get('total_methods', 0)
            total_signatures = signatures.get('metadata', {}).get('total_signatures', 0)
            param_coverage = round(total_signatures / total_methods * 100, 2) if total_methods > 0 else 0.0
            
            report_lines.extend([
                f"- **Methods with Signatures:** {total_signatures}/{total_methods}",
                f"- **Coverage Percentage:** {param_coverage}%",
                "",
                "### Calibration Coverage (Per-Layer)",
                ""
            ])
            
            # Add per-layer statistics
            stats = coverage.get('statistics', {})
            layer_coverage = stats.get('per_layer_coverage', {})
            
            report_lines.extend([
                "| Layer | Symbol | Computed | Pending | Coverage % |",
                "|-------|--------|----------|---------|------------|"
            ])
            
            layer_names = coverage.get('layer_definitions', {})
            for layer in ['@b', '@q', '@d', '@p', '@C', '@chain', '@u', '@m']:
                layer_name = layer_names.get(layer, layer)
                layer_stats = layer_coverage.get(layer, {})
                computed = layer_stats.get('computed', 0)
                pending = layer_stats.get('pending', 0)
                percentage = layer_stats.get('percentage', 0.0)
                report_lines.append(
                    f"| {layer_name} | `{layer}` | {computed} | {pending} | {percentage}% |"
                )
            
            report_lines.extend([
                "",
                "### Overall Calibration Status",
                f"- **Fully Calibrated:** {stats.get('fully_calibrated', 0)} methods",
                f"- **Partially Calibrated:** {stats.get('partially_calibrated', 0)} methods",
                f"- **Not Calibrated:** {stats.get('not_calibrated', 0)} methods",
                f"- **Overall Calibration %:** {stats.get('calibration_percentage', 0.0)}%",
                "",
                "### Per-Role Coverage",
                "",
                "| Role | Total Methods | Calibrated | Coverage % |",
                "|------|---------------|------------|------------|"
            ])
            
            # Add per-role statistics
            role_coverage = stats.get('per_role_coverage', {})
            for role, role_stats in sorted(role_coverage.items()):
                total = role_stats.get('total', 0)
                calibrated = role_stats.get('calibrated', 0)
                coverage_pct = round(calibrated / total * 100, 2) if total > 0 else 0.0
                report_lines.append(
                    f"| {role} | {total} | {calibrated} | {coverage_pct}% |"
                )
            
            report_lines.extend([
                "",
                "## Layer Definitions",
                "",
                "The 8-layer calibration system:",
                "",
                "1. **@b (Base Layer)** - Intrinsic quality of method code",
                "2. **@q (Question Layer)** - Compatibility with specific questions",
                "3. **@d (Dimension Layer)** - Compatibility with policy dimensions",
                "4. **@p (Policy Layer)** - Compatibility with policy areas",
                "5. **@C (Congruence Layer)** - Cross-method consistency",
                "6. **@chain (Chain Layer)** - Method chaining compatibility",
                "7. **@u (Unit Layer)** - Unit test coverage and validation",
                "8. **@m (Meta Layer)** - Meta-analysis and reflection capabilities",
                "",
                "## Files Location",
                "",
                f"All consolidated inventories are located in:",
                f"```",
                f"{self.inventory_dir}/",
                f"├── COHORT_2024_canonical_method_inventory.json",
                f"├── COHORT_2024_method_signatures.json",
                f"├── COHORT_2024_calibration_coverage_matrix.json",
                f"└── COHORT_2024_consolidation_summary.md (this file)",
                f"```",
                "",
                "## Next Steps",
                "",
                "1. Review methods with pending calibration in coverage matrix",
                "2. Run calibration computations for uncalibrated methods",
                "3. Update layer-specific configuration files with new scores",
                "4. Re-run consolidation to verify completeness",
                "",
                "## Notes",
                "",
                f"- Source calibration configs: `{self.source_calibration_dir}/`",
                "- Scanner script: `scan_methods_inventory.py`",
                "- Signature extractor: `method_signature_extractor.py`",
                "- Coverage validator: `calibration_coverage_validator.py`",
                "- Orchestrator: `consolidate_calibration_inventories.py`",
                "",
                "---",
                f"*Generated by COHORT_2024 Calibration Inventory Consolidator*"
            ])
            
            # Write report
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            logger.info(f"✓ Summary report saved: {self.summary_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}", exc_info=True)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}
    
    def _print_summary(self) -> None:
        """Print summary to console."""
        try:
            inventory = self._load_json(self.inventory_file)
            signatures = self._load_json(self.signatures_file)
            coverage = self._load_json(self.coverage_file)
            
            stats = coverage.get('statistics', {})
            
            print("\n" + "="*80)
            print("CONSOLIDATION SUMMARY")
            print("="*80)
            print(f"\nTotal Methods Discovered: {inventory.get('metadata', {}).get('total_methods', 0)}")
            print(f"Method Signatures Extracted: {signatures.get('metadata', {}).get('total_signatures', 0)}")
            print(f"\nCalibration Status:")
            print(f"  Fully Calibrated: {stats.get('fully_calibrated', 0)}")
            print(f"  Partially Calibrated: {stats.get('partially_calibrated', 0)}")
            print(f"  Not Calibrated: {stats.get('not_calibrated', 0)}")
            print(f"  Overall Calibration %: {stats.get('calibration_percentage', 0.0)}%")
            print(f"\nOutput Files:")
            print(f"  1. {self.inventory_file}")
            print(f"  2. {self.signatures_file}")
            print(f"  3. {self.coverage_file}")
            print(f"  4. {self.summary_file}")
            print("="*80 + "\n")
            
        except Exception as e:
            logger.error(f"Failed to print summary: {e}")


def main():
    """Main entry point."""
    root_path = Path(__file__).parent.parent.parent.parent.parent
    
    consolidator = CalibrationInventoryConsolidator(root_path)
    
    success = consolidator.consolidate_all()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
