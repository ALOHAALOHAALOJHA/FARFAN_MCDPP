#!/usr/bin/env python3
"""
Discovery Protocol (Triangulation Phase) - Section 1.1

MANDATORY INVENTORY ACQUISITION tool that executes exhaustive repository scanning
and produces PHASE2_INVENTORY.yaml according to strict specification.

This tool implements the 4 mandatory command sets:
1. Exhaustive file discovery (Phase 2, executor, carver, orchestrator, SISAS, dura_lex, synchron, irrigation, contract, validator)
2. Directory structure mapping (all .py, .json, .md files)
3. Import dependency graph (executor, carver, contract, SISAS, orchestrator imports)
4. Legacy artifact detection (executors.py, batch_*.py, *_v2*, *_final*, *_old*)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml


@dataclass
class InventoryResult:
    """Structured inventory results from discovery protocol."""

    inventory_timestamp: str
    inventory_version: str = "1.0.0"
    total_files_scanned: int = 0
    command_set_1_exhaustive_discovery: list[str] = field(default_factory=list)
    command_set_2_directory_mapping: list[str] = field(default_factory=list)
    command_set_3_import_dependencies: list[str] = field(default_factory=list)
    command_set_4_legacy_artifacts: list[str] = field(default_factory=list)

    phase2_files: list[str] = field(default_factory=list)
    executor_files: list[str] = field(default_factory=list)
    carver_files: list[str] = field(default_factory=list)
    orchestrator_files: list[str] = field(default_factory=list)
    sisas_files: list[str] = field(default_factory=list)
    dura_lex_files: list[str] = field(default_factory=list)
    synchronization_files: list[str] = field(default_factory=list)
    irrigation_files: list[str] = field(default_factory=list)
    contract_files: list[str] = field(default_factory=list)
    validator_files: list[str] = field(default_factory=list)

    python_files_count: int = 0
    json_files_count: int = 0
    markdown_files_count: int = 0

    executor_imports: list[str] = field(default_factory=list)
    carver_imports: list[str] = field(default_factory=list)
    contract_imports: list[str] = field(default_factory=list)
    sisas_imports: list[str] = field(default_factory=list)
    orchestrator_imports: list[str] = field(default_factory=list)

    legacy_executors_py: list[str] = field(default_factory=list)
    legacy_batch_py: list[str] = field(default_factory=list)
    legacy_v2_files: list[str] = field(default_factory=list)
    legacy_final_files: list[str] = field(default_factory=list)
    legacy_old_files: list[str] = field(default_factory=list)


class DiscoveryProtocol:
    """Discovery Protocol implementation for Phase 2 inventory acquisition."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        if not self.repo_root.exists():
            raise ValueError(f"Repository root does not exist: {self.repo_root}")

    def run_command(self, command: str) -> list[str]:
        """Execute shell command and return output as list of lines."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout.strip()
            if not output:
                return []
            return [line for line in output.split("\n") if line.strip()]
        except Exception as e:
            print(f"Warning: Command failed: {command}\n  Error: {e}")
            return []

    def execute_command_set_1(self) -> list[str]:
        """COMMAND_SET_1: Exhaustive file discovery."""
        command = (
            "git ls-files | grep -Ei "
            "'phase. ?2|executor|carver|orchestrat|sisas|dura_lex|synchron|irrigation|contract|validator'"
        )
        return self.run_command(command)

    def execute_command_set_2(self) -> list[str]:
        """COMMAND_SET_2: Directory structure mapping."""
        command = (
            "find . -type f \\( -name '*.py' -o -name '*.json' -o -name '*.md' \\) 2>/dev/null | sort"
        )
        return self.run_command(command)

    def execute_command_set_3(self) -> list[str]:
        """COMMAND_SET_3: Import dependency graph."""
        command = (
            "grep -r '^from\\|^import' src/ --include='*.py' | "
            "grep -Ei 'executor|carver|contract|sisas|orchestrat'"
        )
        return self.run_command(command)

    def execute_command_set_4(self) -> list[str]:
        """COMMAND_SET_4: Legacy artifact detection."""
        command = (
            "find . -type f \\( -name 'executors.py' -o -name 'batch_*.py' "
            "-o -name '*_v2*' -o -name '*_final*' -o -name '*_old*' \\) 2>/dev/null"
        )
        return self.run_command(command)

    def categorize_files(self, files: list[str]) -> dict[str, list[str]]:
        """Categorize files by keyword match."""
        categories: dict[str, list[str]] = {
            "phase2": [],
            "executor": [],
            "carver": [],
            "orchestrator": [],
            "sisas": [],
            "dura_lex": [],
            "synchronization": [],
            "irrigation": [],
            "contract": [],
            "validator": [],
        }

        for filepath in files:
            lower_path = filepath.lower()
            if "phase_two" in lower_path or "phase2" in lower_path:
                categories["phase2"].append(filepath)
            if "executor" in lower_path:
                categories["executor"].append(filepath)
            if "carver" in lower_path:
                categories["carver"].append(filepath)
            if "orchestrat" in lower_path:
                categories["orchestrator"].append(filepath)
            if "sisas" in lower_path:
                categories["sisas"].append(filepath)
            if "dura_lex" in lower_path:
                categories["dura_lex"].append(filepath)
            if "synchron" in lower_path:
                categories["synchronization"].append(filepath)
            if "irrigation" in lower_path:
                categories["irrigation"].append(filepath)
            if "contract" in lower_path:
                categories["contract"].append(filepath)
            if "validat" in lower_path:
                categories["validator"].append(filepath)

        return categories

    def categorize_imports(self, imports: list[str]) -> dict[str, list[str]]:
        """Categorize import statements by component."""
        categories: dict[str, list[str]] = {
            "executor": [],
            "carver": [],
            "contract": [],
            "sisas": [],
            "orchestrator": [],
        }

        for import_line in imports:
            lower_line = import_line.lower()
            if "executor" in lower_line:
                categories["executor"].append(import_line)
            if "carver" in lower_line:
                categories["carver"].append(import_line)
            if "contract" in lower_line:
                categories["contract"].append(import_line)
            if "sisas" in lower_line:
                categories["sisas"].append(import_line)
            if "orchestrat" in lower_line:
                categories["orchestrator"].append(import_line)

        return categories

    def categorize_legacy(self, files: list[str]) -> dict[str, list[str]]:
        """Categorize legacy artifacts."""
        categories: dict[str, list[str]] = {
            "executors_py": [],
            "batch_py": [],
            "v2_files": [],
            "final_files": [],
            "old_files": [],
        }

        for filepath in files:
            filename = Path(filepath).name.lower()
            if filename == "executors.py":
                categories["executors_py"].append(filepath)
            if filename.startswith("batch_") and filename.endswith(".py"):
                categories["batch_py"].append(filepath)
            if "_v2" in filename:
                categories["v2_files"].append(filepath)
            if "_final" in filename:
                categories["final_files"].append(filepath)
            if "_old" in filename:
                categories["old_files"].append(filepath)

        return categories

    def count_file_types(self, files: list[str]) -> dict[str, int]:
        """Count files by extension."""
        counts = {"py": 0, "json": 0, "md": 0}
        for filepath in files:
            if filepath.endswith(".py"):
                counts["py"] += 1
            elif filepath.endswith(".json"):
                counts["json"] += 1
            elif filepath.endswith(".md"):
                counts["md"] += 1
        return counts

    def execute_discovery(self) -> InventoryResult:
        """Execute complete discovery protocol and return structured inventory."""
        timestamp = datetime.now(UTC).isoformat()

        print("Executing COMMAND_SET_1: Exhaustive file discovery...")
        cmd1_results = self.execute_command_set_1()

        print("Executing COMMAND_SET_2: Directory structure mapping...")
        cmd2_results = self.execute_command_set_2()

        print("Executing COMMAND_SET_3: Import dependency graph...")
        cmd3_results = self.execute_command_set_3()

        print("Executing COMMAND_SET_4: Legacy artifact detection...")
        cmd4_results = self.execute_command_set_4()

        print("Categorizing files...")
        file_categories = self.categorize_files(cmd1_results)

        print("Categorizing imports...")
        import_categories = self.categorize_imports(cmd3_results)

        print("Categorizing legacy artifacts...")
        legacy_categories = self.categorize_legacy(cmd4_results)

        print("Counting file types...")
        file_counts = self.count_file_types(cmd2_results)

        inventory = InventoryResult(
            inventory_timestamp=timestamp,
            total_files_scanned=len(cmd2_results),
            command_set_1_exhaustive_discovery=cmd1_results,
            command_set_2_directory_mapping=cmd2_results,
            command_set_3_import_dependencies=cmd3_results,
            command_set_4_legacy_artifacts=cmd4_results,
            phase2_files=file_categories["phase2"],
            executor_files=file_categories["executor"],
            carver_files=file_categories["carver"],
            orchestrator_files=file_categories["orchestrator"],
            sisas_files=file_categories["sisas"],
            dura_lex_files=file_categories["dura_lex"],
            synchronization_files=file_categories["synchronization"],
            irrigation_files=file_categories["irrigation"],
            contract_files=file_categories["contract"],
            validator_files=file_categories["validator"],
            python_files_count=file_counts["py"],
            json_files_count=file_counts["json"],
            markdown_files_count=file_counts["md"],
            executor_imports=import_categories["executor"],
            carver_imports=import_categories["carver"],
            contract_imports=import_categories["contract"],
            sisas_imports=import_categories["sisas"],
            orchestrator_imports=import_categories["orchestrator"],
            legacy_executors_py=legacy_categories["executors_py"],
            legacy_batch_py=legacy_categories["batch_py"],
            legacy_v2_files=legacy_categories["v2_files"],
            legacy_final_files=legacy_categories["final_files"],
            legacy_old_files=legacy_categories["old_files"],
        )

        return inventory

    def save_inventory(self, inventory: InventoryResult, output_path: Path) -> None:
        """Save inventory to YAML file."""
        inventory_dict = {
            "inventory_timestamp": inventory.inventory_timestamp,
            "inventory_version": inventory.inventory_version,
            "total_files_scanned": inventory.total_files_scanned,
            "file_type_counts": {
                "python_files": inventory.python_files_count,
                "json_files": inventory.json_files_count,
                "markdown_files": inventory.markdown_files_count,
            },
            "command_results": {
                "command_set_1_exhaustive_discovery": {
                    "count": len(inventory.command_set_1_exhaustive_discovery),
                    "files": inventory.command_set_1_exhaustive_discovery,
                },
                "command_set_2_directory_mapping": {
                    "count": len(inventory.command_set_2_directory_mapping),
                    "files": inventory.command_set_2_directory_mapping,
                },
                "command_set_3_import_dependencies": {
                    "count": len(inventory.command_set_3_import_dependencies),
                    "imports": inventory.command_set_3_import_dependencies,
                },
                "command_set_4_legacy_artifacts": {
                    "count": len(inventory.command_set_4_legacy_artifacts),
                    "files": inventory.command_set_4_legacy_artifacts,
                },
            },
            "categorized_files": {
                "phase2_files": {
                    "count": len(inventory.phase2_files),
                    "files": inventory.phase2_files,
                },
                "executor_files": {
                    "count": len(inventory.executor_files),
                    "files": inventory.executor_files,
                },
                "carver_files": {
                    "count": len(inventory.carver_files),
                    "files": inventory.carver_files,
                },
                "orchestrator_files": {
                    "count": len(inventory.orchestrator_files),
                    "files": inventory.orchestrator_files,
                },
                "sisas_files": {
                    "count": len(inventory.sisas_files),
                    "files": inventory.sisas_files,
                },
                "dura_lex_files": {
                    "count": len(inventory.dura_lex_files),
                    "files": inventory.dura_lex_files,
                },
                "synchronization_files": {
                    "count": len(inventory.synchronization_files),
                    "files": inventory.synchronization_files,
                },
                "irrigation_files": {
                    "count": len(inventory.irrigation_files),
                    "files": inventory.irrigation_files,
                },
                "contract_files": {
                    "count": len(inventory.contract_files),
                    "files": inventory.contract_files,
                },
                "validator_files": {
                    "count": len(inventory.validator_files),
                    "files": inventory.validator_files,
                },
            },
            "import_dependencies": {
                "executor_imports": {
                    "count": len(inventory.executor_imports),
                    "imports": inventory.executor_imports,
                },
                "carver_imports": {
                    "count": len(inventory.carver_imports),
                    "imports": inventory.carver_imports,
                },
                "contract_imports": {
                    "count": len(inventory.contract_imports),
                    "imports": inventory.contract_imports,
                },
                "sisas_imports": {
                    "count": len(inventory.sisas_imports),
                    "imports": inventory.sisas_imports,
                },
                "orchestrator_imports": {
                    "count": len(inventory.orchestrator_imports),
                    "imports": inventory.orchestrator_imports,
                },
            },
            "legacy_artifacts": {
                "legacy_executors_py": {
                    "count": len(inventory.legacy_executors_py),
                    "files": inventory.legacy_executors_py,
                },
                "legacy_batch_py": {
                    "count": len(inventory.legacy_batch_py),
                    "files": inventory.legacy_batch_py,
                },
                "legacy_v2_files": {
                    "count": len(inventory.legacy_v2_files),
                    "files": inventory.legacy_v2_files,
                },
                "legacy_final_files": {
                    "count": len(inventory.legacy_final_files),
                    "files": inventory.legacy_final_files,
                },
                "legacy_old_files": {
                    "count": len(inventory.legacy_old_files),
                    "files": inventory.legacy_old_files,
                },
            },
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(
                inventory_dict,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

        print(f"\nInventory saved to: {output_path}")


def main() -> None:
    """Main entry point for discovery protocol."""
    import sys

    repo_root = Path(__file__).parent.parent.resolve()

    print("=" * 80)
    print("DISCOVERY PROTOCOL - SECTION 1.1: MANDATORY INVENTORY ACQUISITION")
    print("=" * 80)
    print(f"\nRepository root: {repo_root}")
    print("\nExecuting 4 mandatory command sets...\n")

    protocol = DiscoveryProtocol(repo_root)

    try:
        inventory = protocol.execute_discovery()

        output_path = repo_root / "PHASE2_INVENTORY.yaml"
        protocol.save_inventory(inventory, output_path)

        print("\n" + "=" * 80)
        print("INVENTORY SUMMARY")
        print("=" * 80)
        print(f"Total files scanned: {inventory.total_files_scanned}")
        print(f"Python files: {inventory.python_files_count}")
        print(f"JSON files: {inventory.json_files_count}")
        print(f"Markdown files: {inventory.markdown_files_count}")
        print(f"\nPhase 2 files: {len(inventory.phase2_files)}")
        print(f"Executor files: {len(inventory.executor_files)}")
        print(f"Carver files: {len(inventory.carver_files)}")
        print(f"Orchestrator files: {len(inventory.orchestrator_files)}")
        print(f"SISAS files: {len(inventory.sisas_files)}")
        print(f"Dura Lex files: {len(inventory.dura_lex_files)}")
        print(f"Synchronization files: {len(inventory.synchronization_files)}")
        print(f"Irrigation files: {len(inventory.irrigation_files)}")
        print(f"Contract files: {len(inventory.contract_files)}")
        print(f"Validator files: {len(inventory.validator_files)}")
        print(f"\nLegacy artifacts detected: {len(inventory.command_set_4_legacy_artifacts)}")
        print("=" * 80)
        print("\n✓ Discovery protocol completed successfully")

    except Exception as e:
        print(f"\n✗ Discovery protocol failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
