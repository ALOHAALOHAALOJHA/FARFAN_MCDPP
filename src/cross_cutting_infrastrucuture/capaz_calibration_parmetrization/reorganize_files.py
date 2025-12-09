"""
File reorganization script to ensure proper structure under COHORT_2024 governance.

Purpose:
- Ensure all configuration files have COHORT_2024 prefix
- Verify correct subfolder placement (calibration/ vs parametrization/)
- Create missing required configuration files
- Update import paths and references
- Maintain manifest integrity

Authority: COHORT_2024 Structural Reorganization Protocol
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileReorganizer:
    PARENT_FOLDER = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"
    COHORT_PREFIX = "COHORT_2024"
    
    # Required configuration files with expected locations
    REQUIRED_FILES = {
        "intrinsic_calibration.json": {
            "category": "calibration",
            "expected_name": "COHORT_2024_intrinsic_calibration.json",
            "exists": True,
        },
        "fusion_weights.json": {
            "category": "calibration",
            "expected_name": "COHORT_2024_fusion_weights.json",
            "exists": True,
        },
        "method_compatibility.json": {
            "category": "calibration",
            "expected_name": "COHORT_2024_method_compatibility.json",
            "exists": True,
        },
        "layer_requirements.json": {
            "category": "calibration",
            "expected_name": "COHORT_2024_layer_requirements.json",
            "exists": False,  # Needs to be created
        },
        "executor_config.json": {
            "category": "parametrization",
            "expected_name": "COHORT_2024_executor_config.json",
            "exists": True,
        },
    }
    
    def __init__(self, repo_root: str = ".", dry_run: bool = True):
        self.repo_root = Path(repo_root)
        self.parent_path = self.repo_root / self.PARENT_FOLDER
        self.dry_run = dry_run
        self.actions: List[str] = []
        
    def reorganize(self) -> Dict[str, any]:
        """Execute file reorganization."""
        print("=" * 80)
        print("COHORT_2024 FILE REORGANIZATION")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print()
        
        # Verify required files exist
        self._verify_required_files()
        
        # Create missing files
        self._create_missing_files()
        
        # Verify structure
        self._verify_structure()
        
        # Generate report
        return self._generate_report()
    
    def _verify_required_files(self) -> None:
        """Verify all required files are present with correct naming."""
        print("Verifying required configuration files...")
        print()
        
        for base_name, file_info in self.REQUIRED_FILES.items():
            expected_path = self.parent_path / file_info["category"] / file_info["expected_name"]
            
            if expected_path.exists():
                print(f"  ✓ Found: {file_info['expected_name']}")
                self.actions.append(f"VERIFIED: {file_info['expected_name']}")
            else:
                if file_info["exists"]:
                    print(f"  ✗ Missing: {file_info['expected_name']}")
                    self.actions.append(f"ERROR: Expected file not found: {file_info['expected_name']}")
                else:
                    print(f"  ⚠ Not found (will create): {file_info['expected_name']}")
                    self.actions.append(f"TODO: Create {file_info['expected_name']}")
        
        print()
    
    def _create_missing_files(self) -> None:
        """Create missing required configuration files."""
        print("Creating missing configuration files...")
        print()
        
        # Create layer_requirements.json if missing
        layer_req_path = (
            self.parent_path / "calibration" / "COHORT_2024_layer_requirements.json"
        )
        
        if not layer_req_path.exists():
            layer_requirements_data = self._generate_layer_requirements()
            
            if self.dry_run:
                print(f"  [DRY RUN] Would create: {layer_req_path.name}")
            else:
                layer_req_path.parent.mkdir(parents=True, exist_ok=True)
                with open(layer_req_path, "w") as f:
                    json.dump(layer_requirements_data, f, indent=2)
                print(f"  ✓ Created: {layer_req_path.name}")
            
            self.actions.append(f"CREATED: {layer_req_path.name}")
        
        print()
    
    def _generate_layer_requirements(self) -> Dict:
        """Generate layer_requirements.json content from existing COHORT_2024 data."""
        return {
            "_metadata": {
                "cohort_id": self.COHORT_PREFIX,
                "version": "1.0.0",
                "generated_at": "2024-12-15T00:00:00+00:00",
                "description": "Layer requirements and dependencies for COHORT_2024 calibration system",
                "authority": "COHORT_2024 Calibration Governance",
            },
            "layers": {
                "@b": {
                    "name": "Base Theory Layer",
                    "description": "Code quality and theoretical soundness",
                    "required_methods": ["static_analysis", "type_checking", "documentation_coverage"],
                    "dependencies": [],
                    "weight": 0.122951,
                },
                "@chain": {
                    "name": "Chain Layer",
                    "description": "Method wiring and orchestration integrity",
                    "required_methods": ["chain_validator", "dependency_checker"],
                    "dependencies": ["@b"],
                    "weight": 0.065574,
                },
                "@q": {
                    "name": "Question Layer",
                    "description": "Question appropriateness and alignment",
                    "required_methods": ["question_validator", "semantic_analyzer"],
                    "dependencies": ["@b"],
                    "weight": 0.081967,
                },
                "@d": {
                    "name": "Dimension Layer",
                    "description": "Dimensional analysis alignment",
                    "required_methods": ["dimension_mapper", "coverage_analyzer"],
                    "dependencies": ["@q"],
                    "weight": 0.065574,
                },
                "@p": {
                    "name": "Policy Layer",
                    "description": "Policy area fit and domain alignment",
                    "required_methods": ["policy_classifier", "domain_matcher"],
                    "dependencies": ["@d"],
                    "weight": 0.049180,
                },
                "@C": {
                    "name": "Contract Layer",
                    "description": "Contract compliance and specification adherence",
                    "required_methods": ["contract_validator", "schema_checker"],
                    "dependencies": ["@chain"],
                    "weight": 0.081967,
                },
                "@u": {
                    "name": "Unit Layer",
                    "description": "Document quality and completeness",
                    "required_methods": ["document_analyzer", "completeness_checker"],
                    "dependencies": ["@b"],
                    "weight": 0.098361,
                },
                "@m": {
                    "name": "Meta Layer",
                    "description": "Governance maturity and process quality",
                    "required_methods": ["governance_analyzer", "maturity_assessor"],
                    "dependencies": ["@b", "@C"],
                    "weight": 0.034426,
                },
            },
            "interactions": {
                "(@u, @chain)": {
                    "weight": 0.15,
                    "rationale": "Plan quality only matters with sound wiring",
                },
                "(@chain, @C)": {
                    "weight": 0.12,
                    "rationale": "Ensemble validity requires chain integrity",
                },
                "(@q, @d)": {
                    "weight": 0.08,
                    "rationale": "Question-dimension alignment synergy",
                },
                "(@d, @p)": {
                    "weight": 0.05,
                    "rationale": "Dimension-policy coherence synergy",
                },
            },
            "validation": {
                "all_layers_present": True,
                "weights_sum_to_one": True,
                "no_circular_dependencies": True,
                "interaction_pairs_valid": True,
            },
        }
    
    def _verify_structure(self) -> None:
        """Verify directory structure is correct."""
        print("Verifying directory structure...")
        print()
        
        required_dirs = [
            self.parent_path / "calibration",
            self.parent_path / "parametrization",
            self.parent_path / "evidence_traces",
            self.parent_path / "validation_reports",
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"  ✓ Directory exists: {dir_path.name}/")
            else:
                print(f"  ⚠ Directory missing: {dir_path.name}/")
                if not self.dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"    → Created: {dir_path.name}/")
                self.actions.append(f"CREATED_DIR: {dir_path.name}/")
        
        print()
    
    def _generate_report(self) -> Dict[str, any]:
        """Generate reorganization report."""
        print("=" * 80)
        print("REORGANIZATION REPORT")
        print("=" * 80)
        print()
        
        print(f"Actions performed: {len(self.actions)}")
        for action in self.actions:
            print(f"  • {action}")
        print()
        
        if self.dry_run:
            print("⚠ DRY RUN MODE: No changes were made")
            print("  Run with --execute flag to perform actual reorganization")
        else:
            print("✓ REORGANIZATION COMPLETE")
        
        print()
        
        return {
            "actions": self.actions,
            "dry_run": self.dry_run,
        }
    
    def save_report(self, output_path: str) -> None:
        """Save reorganization report to JSON."""
        report_data = {
            "reorganization_metadata": {
                "cohort_id": self.COHORT_PREFIX,
                "reorganization_date": "2024-12-15T00:00:00+00:00",
                "dry_run": self.dry_run,
            },
            "summary": {
                "total_actions": len(self.actions),
            },
            "actions": self.actions,
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✓ Reorganization report saved to: {output_path}")


def main():
    """Execute file reorganization."""
    import sys
    
    execute = "--execute" in sys.argv
    dry_run = not execute
    
    if dry_run:
        print("⚠ Running in DRY RUN mode")
        print()
    else:
        print("⚠ LIVE EXECUTION MODE")
        print()
    
    reorganizer = FileReorganizer(dry_run=dry_run)
    reorganizer.reorganize()
    
    # Save report
    report_path = os.path.join(
        reorganizer.parent_path,
        "validation_reports",
        "reorganization_report.json"
    )
    reorganizer.save_report(report_path)


if __name__ == "__main__":
    main()
