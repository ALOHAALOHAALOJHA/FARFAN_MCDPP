#!/usr/bin/env python3
"""
Update Phase Manifests to Match DAG Files

This script updates each phase manifest to accurately reflect the Python files
currently present in the phase directory (the DAG). It preserves the existing
manifest structure while updating the module listings.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# ANSI color codes
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def get_canonical_phases(phases_dir: Path) -> List[Path]:
    """Get all canonical phase directories."""
    canonical_phases = []
    for d in sorted(phases_dir.iterdir()):
        if d.is_dir() and d.name.startswith("Phase_") and d.name not in ["Phase_4", "Phase_zero"]:
            canonical_phases.append(d)
    return canonical_phases


def get_actual_files(phase_dir: Path) -> List[str]:
    """Get all Python files in a phase directory."""
    files = []
    for f in sorted(phase_dir.glob("*.py")):
        files.append(f.name)
    return files


def classify_file(filename: str, phase_number: str) -> Dict:
    """Classify a file and extract metadata from its name."""
    # Remove .py extension
    basename = filename[:-3] if filename.endswith('.py') else filename
    
    # Special cases
    if filename == "__init__.py":
        return {
            "canonical_name": "__init__",
            "type": "INFRA",
            "criticality": "LOW",
            "purpose": "Package initialization",
            "stage_code": 0
        }
    
    if filename.upper().startswith("PHASE_") and filename.upper().endswith("_CONSTANTS.py"):
        return {
            "canonical_name": basename,
            "type": "CFG",
            "criticality": "HIGH",
            "purpose": "Phase constants and configuration",
            "stage_code": 0
        }
    
    # Parse standard naming pattern: phaseX_YY_ZZ_name.py
    if basename.startswith(f"phase{phase_number}_"):
        parts = basename.split('_')
        if len(parts) >= 3:
            try:
                stage_code = int(parts[1])
                return {
                    "canonical_name": basename,
                    "type": classify_type(stage_code),
                    "criticality": classify_criticality(stage_code),
                    "purpose": humanize_name(parts[3:] if len(parts) > 3 else [parts[2]]),
                    "stage_code": stage_code
                }
            except (ValueError, IndexError):
                pass
    
    # Fallback for files that don't match pattern
    return {
        "canonical_name": basename,
        "type": "UTIL",
        "criticality": "MEDIUM",
        "purpose": humanize_name([basename]),
        "stage_code": 99
    }


def classify_type(stage_code: int) -> str:
    """Classify module type based on stage code."""
    if stage_code == 0:
        return "INFRA"
    elif stage_code <= 19:
        return "CFG"
    elif stage_code <= 39:
        return "ENF"
    elif stage_code <= 59:
        return "VAL"
    elif stage_code <= 79:
        return "PROC"
    elif stage_code <= 89:
        return "ORCH"
    else:
        return "UTIL"


def classify_criticality(stage_code: int) -> str:
    """Classify module criticality based on stage code."""
    if stage_code in [0, 10, 20, 30, 40, 50, 90]:
        return "CRITICAL"
    elif stage_code in [15, 25, 35, 45, 55]:
        return "HIGH"
    elif stage_code in [60, 70, 80]:
        return "MEDIUM"
    else:
        return "LOW"


def humanize_name(parts: List[str]) -> str:
    """Convert snake_case parts to human-readable purpose."""
    return ' '.join(part.replace('_', ' ').title() for part in parts)


def group_files_by_stage(files: List[str], phase_number: str) -> Dict[int, List[Dict]]:
    """Group files by their stage code."""
    stages = {}
    for filename in files:
        metadata = classify_file(filename, phase_number)
        stage_code = metadata.pop("stage_code")
        
        if stage_code not in stages:
            stages[stage_code] = []
        
        stages[stage_code].append({
            "order": len(stages[stage_code]),
            "canonical_name": metadata["canonical_name"],
            "type": metadata["type"],
            "criticality": metadata["criticality"],
            "purpose": metadata["purpose"]
        })
    
    return stages


def update_manifest(manifest_path: Path, phase_dir: Path, actual_files: List[str]) -> bool:
    """Update a manifest file with current DAG files."""
    phase_number = phase_dir.name.split('_')[1].lstrip('0') or '0'
    
    # Load existing manifest or create new one
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        manifest = {
            "$schema": "phase_manifest_schema.json",
            "manifest_version": "1.0.0",
            "phase": {
                "number": int(phase_number),
                "name": f"Phase {phase_number}",
                "codename": "UNKNOWN",
                "label": f"Phase {phase_number}",
                "description": f"Phase {phase_number} description"
            },
            "metadata": {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "modified": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0.0",
                "author": "F.A.R.F.A.N Core Architecture Team",
                "status": "ACTIVE"
            }
        }
    
    # Handle different manifest formats
    if "metadata" not in manifest:
        # Legacy format - add metadata section
        manifest["metadata"] = {
            "created": manifest.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            "modified": datetime.now().strftime("%Y-%m-%d"),
            "version": manifest.get("version", "1.0.0"),
            "author": "F.A.R.F.A.N Core Architecture Team",
            "status": manifest.get("status", "ACTIVE")
        }
    
    # Group files by stage
    stages_dict = group_files_by_stage(actual_files, phase_number)
    
    # Build stages array
    stages_array = []
    for stage_code in sorted(stages_dict.keys()):
        modules = stages_dict[stage_code]
        stages_array.append({
            "code": stage_code,
            "name": get_stage_name(stage_code),
            "description": get_stage_description(stage_code),
            "execution_order": len(stages_array) + 1,
            "module_count": len(modules),
            "modules": modules
        })
    
    # Update manifest
    manifest["stages"] = stages_array
    manifest["statistics"] = {
        "total_modules": len(actual_files),
        "stages": len(stages_array)
    }
    manifest["metadata"]["modified"] = datetime.now().strftime("%Y-%m-%d")
    
    # Write updated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return True


def get_stage_name(stage_code: int) -> str:
    """Get human-readable stage name."""
    names = {
        0: "Infrastructure",
        10: "Configuration",
        20: "Enforcement",
        30: "Resource Management",
        40: "Validation",
        50: "Execution",
        60: "Integration",
        70: "Aggregation",
        80: "Evidence",
        90: "Orchestration",
        95: "Profiling"
    }
    return names.get(stage_code, f"Stage {stage_code}")


def get_stage_description(stage_code: int) -> str:
    """Get stage description."""
    descriptions = {
        0: "Base infrastructure and types",
        10: "Configuration and setup",
        20: "Determinism and enforcement",
        30: "Resource control and limits",
        40: "Input validation",
        50: "Core execution logic",
        60: "Integration components",
        70: "Aggregation logic",
        80: "Evidence management",
        90: "Orchestration and coordination",
        95: "Profiling and metrics"
    }
    return descriptions.get(stage_code, f"Stage {stage_code} modules")


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent.parent
    phases_dir = repo_root / "src" / "farfan_pipeline" / "phases"
    
    print(f"{Colors.BOLD}Updating Phase Manifests{Colors.ENDC}\n")
    
    canonical_phases = get_canonical_phases(phases_dir)
    updated_count = 0
    
    for phase_dir in canonical_phases:
        # Find manifest
        manifest_files = list(phase_dir.glob("PHASE_*_MANIFEST.json"))
        if not manifest_files:
            phase_num = phase_dir.name.split('_')[1].lstrip('0') or '0'
            manifest_path = phase_dir / f"PHASE_{phase_num}_MANIFEST.json"
        else:
            manifest_path = manifest_files[0]
        
        # Get actual files
        actual_files = get_actual_files(phase_dir)
        
        print(f"{Colors.BOLD}{phase_dir.name}{Colors.ENDC}")
        print(f"  Manifest: {manifest_path.name}")
        print(f"  Files: {len(actual_files)}")
        
        # Update manifest
        try:
            update_manifest(manifest_path, phase_dir, actual_files)
            print(f"  {Colors.OKGREEN}✓ Updated{Colors.ENDC}\n")
            updated_count += 1
        except Exception as e:
            print(f"  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}\n")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  Updated {updated_count}/{len(canonical_phases)} manifests")
    
    if updated_count == len(canonical_phases):
        print(f"\n{Colors.OKGREEN}✓ All manifests updated successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.WARNING}⚠ Some manifests failed to update{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
