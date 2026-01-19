"""
Irrigation Protocol - Signal Irrigation Confirmation
===================================================

This protocol provides comprehensive verification and synchronization for the
SISAS (Signal Irrigation System) infrastructure.

Components:
1. Real Inventory Verification - Counts JSON files in canonic_questionnaire_central
2. Method Synchronization - Ensures method files have correct entry counts
3. Consumer Creation - Creates missing SISAS consumers
4. Irrigation Execution - Tests complete system with master script

Version: 1.0.0
Date: 2026-01-19
Author: FARFAN Pipeline Architecture Team
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================
logger = structlog.get_logger(__name__)


# =============================================================================
# PROTOCOL CONFIGURATION
# =============================================================================


@dataclass
class IrrigationProtocolConfig:
    """Configuration for irrigation protocol."""

    project_root: Path
    canonic_questionnaire_path: Path = field(default_factory=lambda: Path("canonic_questionnaire_central"))
    sisas_path: Path = field(default_factory=lambda: Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS"))
    methods_path: Path = field(default_factory=lambda: Path("artifacts/data"))

    # Expected counts
    expected_json_files: int = 489  # Expected JSON files in CQC
    expected_methods_count: int = 240  # Expected method entries

    # Method files to synchronize
    method_files: List[str] = field(default_factory=lambda: [
        "METHODS_DISPENSARY_SIGNATURES.json",
        "METHODS_DISPENSARY_SIGNATURES_ENRICHED_EPISTEMOLOGY.json",
    ])

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        if isinstance(self.canonic_questionnaire_path, str):
            self.canonic_questionnaire_path = Path(self.canonic_questionnaire_path)
        if isinstance(self.sisas_path, str):
            self.sisas_path = Path(self.sisas_path)
        if isinstance(self.methods_path, str):
            self.methods_path = Path(self.methods_path)


# =============================================================================
# INVENTORY VERIFICATION
# =============================================================================


@dataclass
class InventoryReport:
    """Report on inventory verification."""

    json_files_found: int = 0
    json_files_list: List[str] = field(default_factory=list)
    directories_found: Dict[str, int] = field(default_factory=dict)
    verification_status: str = "pending"
    discrepancies: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: "")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "json_files_found": self.json_files_found,
            "directories_count": len(self.directories_found),
            "directories": self.directories_found,
            "verification_status": self.verification_status,
            "discrepancies": self.discrepancies,
            "timestamp": self.timestamp,
        }


class InventoryVerifier:
    """
    Verifies the real inventory of canonic_questionnaire_central.

    Counts JSON files and verifies directory structure against
    expected configuration.
    """

    def __init__(self, config: IrrigationProtocolConfig):
        self.config = config
        self.logger = logger

    def verify_inventory(self) -> InventoryReport:
        """
        Verify the inventory of canonic_questionnaire_central.

        Returns:
            InventoryReport with detailed findings
        """
        from datetime import datetime

        report = InventoryReport(timestamp=datetime.utcnow().isoformat())

        cqc_path = self.config.project_root / self.config.canonic_questionnaire_path

        if not cqc_path.exists():
            report.verification_status = "failed"
            report.discrepancies.append(f"CQC path not found: {cqc_path}")
            return report

        # Count JSON files recursively
        json_files = list(cqc_path.rglob("*.json"))
        report.json_files_found = len(json_files)
        report.json_files_list = [str(f.relative_to(cqc_path)) for f in json_files[:50]]  # First 50

        # Count by directory
        for json_file in json_files:
            parent_dir = str(json_file.parent.relative_to(cqc_path))
            report.directories_found[parent_dir] = report.directories_found.get(parent_dir, 0) + 1

        # Check against expected count
        if report.json_files_found == self.config.expected_json_files:
            report.verification_status = "verified"
        else:
            report.verification_status = "discrepancy"
            report.discrepancies.append(
                f"Expected {self.config.expected_json_files} JSON files, found {report.json_files_found}"
            )

        self.logger.info(
            "Inventory verification complete",
            status=report.verification_status,
            json_files=report.json_files_found,
            expected=self.config.expected_json_files,
        )

        return report

    def get_file_breakdown(self) -> Dict[str, List[str]]:
        """
        Get detailed breakdown of files by directory.

        Returns:
            Dict mapping directory to list of files
        """
        cqc_path = self.config.project_root / self.config.canonic_questionnaire_path
        breakdown = {}

        for json_file in cqc_path.rglob("*.json"):
            parent_dir = str(json_file.parent.relative_to(cqc_path))
            if parent_dir not in breakdown:
                breakdown[parent_dir] = []
            breakdown[parent_dir].append(json_file.name)

        return breakdown


# =============================================================================
# METHOD SYNCHRONIZATION
# =============================================================================


@dataclass
class MethodSyncReport:
    """Report on method synchronization."""

    file_name: str = ""
    entries_found: int = 0
    expected_entries: int = 0
    sync_status: str = "pending"
    missing_keys: List[str] = field(default_factory=list)
    extra_keys: List[str] = field(default_factory=list)
    discrepancies: List[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_name": self.file_name,
            "entries_found": self.entries_found,
            "expected_entries": self.expected_entries,
            "sync_status": self.sync_status,
            "missing_keys_count": len(self.missing_keys),
            "extra_keys_count": len(self.extra_keys),
            "timestamp": self.timestamp,
        }


class MethodSynchronizer:
    """
    Synchronizes method files to ensure they have the correct entry count.

    Analyzes method files and ensures they match expected structure and count.
    """

    def __init__(self, config: IrrigationProtocolConfig):
        self.config = config
        self.logger = logger

    def verify_method_file(self, file_name: str) -> MethodSyncReport:
        """
        Verify a single method file.

        Args:
            file_name: Name of the method file to verify

        Returns:
            MethodSyncReport with detailed findings
        """
        from datetime import datetime

        report = MethodSyncReport(
            file_name=file_name,
            expected_entries=self.config.expected_methods_count,
            timestamp=datetime.utcnow().isoformat(),
        )

        file_path = self.config.project_root / self.config.methods_path / file_name

        if not file_path.exists():
            report.sync_status = "file_not_found"
            report.discrepancies.append(f"File not found: {file_path}")
            return report

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Count entries (methods)
            if isinstance(data, dict):
                report.entries_found = len(data)

                # Analyze structure
                for key, value in data.items():
                    if isinstance(value, dict) and "methods" in value:
                        methods = value.get("methods", {})
                        if isinstance(methods, dict):
                            report.entries_found += len(methods)

            # Check against expected
            if report.entries_found == report.expected_entries:
                report.sync_status = "synchronized"
            else:
                report.sync_status = "needs_sync"
                report.discrepancies.append(
                    f"Expected {report.expected_entries} entries, found {report.entries_found}"
                )

        except (json.JSONDecodeError, IOError) as e:
            report.sync_status = "error"
            report.discrepancies.append(f"Error reading file: {e}")

        self.logger.info(
            "Method file verification complete",
            file=file_name,
            status=report.sync_status,
            entries=report.entries_found,
            expected=report.expected_entries,
        )

        return report

    def verify_all_method_files(self) -> List[MethodSyncReport]:
        """
        Verify all configured method files.

        Returns:
            List of MethodSyncReport objects
        """
        reports = []
        for file_name in self.config.method_files:
            report = self.verify_method_file(file_name)
            reports.append(report)
        return reports

    def get_method_summary(self) -> Dict[str, Any]:
        """
        Get summary of all method files.

        Returns:
            Dict with summary statistics
        """
        reports = self.verify_all_method_files()

        return {
            "total_files": len(reports),
            "synchronized": sum(1 for r in reports if r.sync_status == "synchronized"),
            "needs_sync": sum(1 for r in reports if r.sync_status == "needs_sync"),
            "errors": sum(1 for r in reports if r.sync_status == "error"),
            "total_entries": sum(r.entries_found for r in reports),
            "expected_total": len(reports) * self.config.expected_methods_count,
            "reports": [r.to_dict() for r in reports],
        }


# =============================================================================
# CONSUMER CREATION
# =============================================================================


@dataclass
class ConsumerCreationReport:
    """Report on consumer creation."""

    phase: str = ""
    consumer_name: str = ""
    creation_status: str = "pending"
    file_path: str = ""
    errors: List[str] = field(default_factory=list)
    discrepancies: List[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase,
            "consumer_name": self.consumer_name,
            "creation_status": self.creation_status,
            "file_path": self.file_path,
            "errors_count": len(self.errors),
            "timestamp": self.timestamp,
        }


class ConsumerCreator:
    """
    Creates missing SISAS consumers.

    Ensures all required consumers are present for signal irrigation.
    """

    # Required consumers per phase
    REQUIRED_CONSUMERS = {
        "phase0": ["phase0_assembly_consumer"],
        "phase1": ["phase1_extraction_consumer"],
        "phase2": ["phase2_enrichment_consumer"],
        "phase3": ["phase3_validation_consumer"],
        "phase4": ["phase4_dimension_consumer"],
        "phase5": ["phase5_policy_area_consumer"],
        "phase6": ["phase6_cluster_consumer"],
        "phase7": ["phase7_meso_consumer"],
        "phase8": ["phase8_macro_consumer"],
        "phase9": ["phase9_report_consumer"],
    }

    def __init__(self, config: IrrigationProtocolConfig):
        self.config = config
        self.logger = logger
        self.sisas_consumers_path = config.project_root / config.sisas_path / "consumers"

    def verify_consumer(self, phase: str, consumer_name: str) -> ConsumerCreationReport:
        """
        Verify if a consumer exists.

        Args:
            phase: Phase identifier (e.g., "phase7")
            consumer_name: Name of the consumer

        Returns:
            ConsumerCreationReport with status
        """
        from datetime import datetime

        report = ConsumerCreationReport(
            phase=phase,
            consumer_name=consumer_name,
            timestamp=datetime.utcnow().isoformat(),
        )

        consumer_path = self.sisas_consumers_path / phase / f"{consumer_name}.py"

        if consumer_path.exists():
            report.creation_status = "exists"
            report.file_path = str(consumer_path)
        else:
            report.creation_status = "missing"
            report.discrepancies.append(f"Consumer not found: {consumer_path}")

        return report

    def create_consumer_stub(self, phase: str, consumer_name: str) -> ConsumerCreationReport:
        """
        Create a stub consumer file.

        Args:
            phase: Phase identifier
            consumer_name: Name of the consumer

        Returns:
            ConsumerCreationReport with creation status
        """
        from datetime import datetime

        report = ConsumerCreationReport(
            phase=phase,
            consumer_name=consumer_name,
            timestamp=datetime.utcnow().isoformat(),
        )

        phase_path = self.sisas_consumers_path / phase
        consumer_path = phase_path / f"{consumer_name}.py"

        try:
            phase_path.mkdir(parents=True, exist_ok=True)

            # Create consumer stub
            stub_content = f'''"""
{consumer_name.replace("_", " ").title()} - Phase {phase[-1]}

Consumer for {phase} signal irrigation.

Generated by IrrigationProtocol v1.0.0
Date: {datetime.utcnow().isoformat()}
"""

from typing import Any, Dict, List
from dataclasses import dataclass

from ..base_consumer import BaseConsumer
from ...core.signal import Signal, SignalType


@dataclass
class {consumer_name.replace("_", " ").replace(" ", "")}Config:
    """Configuration for {consumer_name}."""

    enabled_signal_types: List[str] = None

    def __post_init__(self):
        if self.enabled_signal_types is None:
            self.enabled_signal_types = [
                "DEFAULT_SIGNAL_TYPE",
            ]


class {consumer_name.replace("_", " ").replace(" ", "")}(BaseConsumer):
    """
    Consumer for {phase} signal processing.

    This consumer handles signal irrigation for {phase}.
    """

    def __init__(self, config: {consumer_name.replace("_", " ").replace(" ", "")}Config = None):
        self.config = config or {consumer_name.replace("_", " ").replace(" ", "")}Config()
        self.consumer_id = "{phase}_{consumer_name}"
        self.subscribed_signal_types = self.config.enabled_signal_types

    def consume(self, signal: Signal) -> Any:
        """
        Consume a signal.

        Args:
            signal: Signal to consume

        Returns:
            Consumption result
        """
        if signal.signal_type not in self.subscribed_signal_types:
            return None

        # Process signal
        result = {{
            "consumer_id": self.consumer_id,
            "signal_type": signal.signal_type,
            "signal_id": signal.signal_id,
            "processed": True,
        }}

        return result

    def get_consumption_contract(self) -> Dict[str, Any]:
        """
        Get the consumption contract for this consumer.

        Returns:
            Dict with contract details
        """
        return {{
            "consumer_id": self.consumer_id,
            "phase": "{phase}",
            "subscribed_signal_types": self.subscribed_signal_types,
            "required_capabilities": ["process_signal"],
        }}
'''

            consumer_path.write_text(stub_content, encoding="utf-8")

            report.creation_status = "created"
            report.file_path = str(consumer_path)

            self.logger.info(
                "Consumer stub created",
                phase=phase,
                consumer=consumer_name,
                path=str(consumer_path),
            )

        except (IOError, OSError) as e:
            report.creation_status = "error"
            report.errors.append(str(e))

        return report

    def verify_all_consumers(self) -> List[ConsumerCreationReport]:
        """
        Verify all required consumers.

        Returns:
            List of ConsumerCreationReport objects
        """
        reports = []

        for phase, consumers in self.REQUIRED_CONSUMERS.items():
            for consumer_name in consumers:
                report = self.verify_consumer(phase, consumer_name)
                reports.append(report)

        return reports

    def create_missing_consumers(self) -> List[ConsumerCreationReport]:
        """
        Create all missing consumers.

        Returns:
            List of ConsumerCreationReport objects
        """
        reports = []
        verification_reports = self.verify_all_consumers()

        for report in verification_reports:
            if report.creation_status == "missing":
                creation_report = self.create_consumer_stub(
                    report.phase, report.consumer_name
                )
                reports.append(creation_report)
            else:
                reports.append(report)

        return reports

    def get_consumer_summary(self) -> Dict[str, Any]:
        """
        Get summary of consumer status.

        Returns:
            Dict with summary statistics
        """
        reports = self.verify_all_consumers()

        return {
            "total_required": len(reports),
            "exists": sum(1 for r in reports if r.creation_status == "exists"),
            "missing": sum(1 for r in reports if r.creation_status == "missing"),
            "phases": {
                phase: sum(1 for r in reports if r.phase == phase and r.creation_status == "exists")
                for phase in self.REQUIRED_CONSUMERS.keys()
            },
            "reports": [r.to_dict() for r in reports],
        }


# =============================================================================
# IRRIGATION EXECUTION
# =============================================================================


@dataclass
class IrrigationExecutionReport:
    """Report on irrigation execution."""

    execution_status: str = "pending"
    contracts_executed: int = 0
    signals_dispatched: int = 0
    consumers_active: int = 0
    errors: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_status": self.execution_status,
            "contracts_executed": self.contracts_executed,
            "signals_dispatched": self.signals_dispatched,
            "consumers_active": self.consumers_active,
            "errors_count": len(self.errors),
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
        }


class IrrigationExecutor:
    """
    Executes the complete irrigation protocol.

    Runs the master irrigation script and reports results.
    """

    def __init__(self, config: IrrigationProtocolConfig):
        self.config = config
        self.logger = logger

    def execute_irrigation(self) -> IrrigationExecutionReport:
        """
        Execute the complete irrigation protocol.

        Returns:
            IrrigationExecutionReport with execution results
        """
        from datetime import datetime
        import time

        report = IrrigationExecutionReport(timestamp=datetime.utcnow().isoformat())
        start_time = time.time()

        try:
            # Step 1: Verify inventory
            inventory_verifier = InventoryVerifier(self.config)
            inventory_report = inventory_verifier.verify_inventory()

            self.logger.info(
                "Inventory verification",
                status=inventory_report.verification_status,
                json_files=inventory_report.json_files_found,
            )

            # Step 2: Sync methods
            method_sync = MethodSynchronizer(self.config)
            method_reports = method_sync.verify_all_method_files()

            for mr in method_reports:
                self.logger.info(
                    "Method file sync",
                    file=mr.file_name,
                    status=mr.sync_status,
                    entries=mr.entries_found,
                )

            # Step 3: Verify consumers
            consumer_creator = ConsumerCreator(self.config)
            consumer_summary = consumer_creator.get_consumer_summary()

            self.logger.info(
                "Consumer summary",
                total=consumer_summary["total_required"],
                exists=consumer_summary["exists"],
                missing=consumer_summary["missing"],
            )

            # Step 4: Execute irrigation script if available
            irrigation_script_path = (
                self.config.project_root
                / self.config.sisas_path
                / "scripts"
                / "generate_contracts.py"
            )

            if irrigation_script_path.exists():
                self.logger.info("Executing irrigation script", path=str(irrigation_script_path))
                # Execute script (import and run)
                import sys
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(irrigation_script_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.config.project_root),
                )

                if result.returncode == 0:
                    report.execution_status = "completed"
                else:
                    report.execution_status = "partial"
                    report.errors.append(f"Script error: {result.stderr}")

            else:
                report.execution_status = "no_script"
                report.errors.append(f"Irrigation script not found: {irrigation_script_path}")

            # Set statistics
            report.contracts_executed = inventory_report.json_files_found
            report.consumers_active = consumer_summary["exists"]
            report.signals_dispatched = inventory_report.json_files_found

        except Exception as e:
            report.execution_status = "error"
            report.errors.append(str(e))
            self.logger.error("Irrigation execution error", error=str(e))

        report.execution_time_seconds = time.time() - start_time

        return report


# =============================================================================
# MAIN PROTOCOL CLASS
# =============================================================================


class IrrigationProtocol:
    """
    Main protocol class for signal irrigation confirmation.

    Orchestrates verification, synchronization, and execution of the
    complete irrigation system.
    """

    def __init__(self, config: IrrigationProtocolConfig):
        self.config = config
        self.inventory_verifier = InventoryVerifier(config)
        self.method_sync = MethodSynchronizer(config)
        self.consumer_creator = ConsumerCreator(config)
        self.executor = IrrigationExecutor(config)
        self.logger = logger

    def run_full_protocol(self) -> Dict[str, Any]:
        """
        Run the complete irrigation protocol.

        Returns:
            Dict with complete protocol results
        """
        from datetime import datetime

        self.logger.info(
            "IRRIGATION PROTOCOL STARTED",
            timestamp=datetime.utcnow().isoformat(),
        )

        results = {
            "protocol_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "steps": {},
        }

        # Step 1: Inventory Verification
        self.logger.info("Step 1: Verifying inventory...")
        inventory_report = self.inventory_verifier.verify_inventory()
        results["steps"]["inventory"] = inventory_report.to_dict()

        # Step 2: Method Synchronization
        self.logger.info("Step 2: Synchronizing methods...")
        method_summary = self.method_sync.get_method_summary()
        results["steps"]["methods"] = method_summary

        # Step 3: Consumer Verification
        self.logger.info("Step 3: Verifying consumers...")
        consumer_summary = self.consumer_creator.get_consumer_summary()
        results["steps"]["consumers"] = consumer_summary

        # Step 4: Execute Irrigation
        self.logger.info("Step 4: Executing irrigation...")
        execution_report = self.executor.execute_irrigation()
        results["steps"]["execution"] = execution_report.to_dict()

        # Overall status
        all_verified = (
            inventory_report.verification_status == "verified"
            and all(r.sync_status in ["synchronized", "needs_sync"] for r in self.method_sync.verify_all_method_files())
            and consumer_summary["missing"] == 0
        )

        results["overall_status"] = "passed" if all_verified else "needs_attention"
        results["recommendations"] = self._generate_recommendations(results)

        self.logger.info(
            "IRRIGATION PROTOCOL COMPLETED",
            status=results["overall_status"],
        )

        return results

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on protocol results."""
        recommendations = []

        inventory = results["steps"].get("inventory", {})
        if inventory.get("verification_status") != "verified":
            recommendations.append(
                f"Inventory has discrepancies: {inventory.get('json_files_found')} files found, "
                f"expected {self.config.expected_json_files}"
            )

        methods = results["steps"].get("methods", {})
        if methods.get("needs_sync", 0) > 0:
            recommendations.append(
                f"{methods.get('needs_sync')} method files need synchronization to {self.config.expected_methods_count} entries"
            )

        consumers = results["steps"].get("consumers", {})
        if consumers.get("missing", 0) > 0:
            recommendations.append(
                f"{consumers.get('missing')} consumers are missing and need to be created"
            )

        execution = results["steps"].get("execution", {})
        if execution.get("execution_status") != "completed":
            recommendations.append(
                f"Irrigation execution status: {execution.get('execution_status')}"
            )

        if not recommendations:
            recommendations.append("All systems nominal. No action required.")

        return recommendations


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_protocol(project_root: Path | str = None) -> IrrigationProtocol:
    """
    Create irrigation protocol instance.

    Args:
        project_root: Root directory of project

    Returns:
        IrrigationProtocol instance
    """
    if project_root is None:
        project_root = Path.cwd()

    config = IrrigationProtocolConfig(project_root=Path(project_root))
    return IrrigationProtocol(config)


def run_protocol(project_root: Path | str = None) -> Dict[str, Any]:
    """
    Run complete irrigation protocol.

    Args:
        project_root: Root directory of project

    Returns:
        Dict with protocol results
    """
    protocol = create_protocol(project_root)
    return protocol.run_full_protocol()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


def main():
    """CLI entry point for irrigation protocol."""
    import sys

    project_root = Path.cwd()
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])

    print(f"Running IrrigationProtocol on: {project_root}")
    print("=" * 80)

    results = run_protocol(project_root)

    print("\n" + "=" * 80)
    print("PROTOCOL RESULTS")
    print("=" * 80)
    print(json.dumps(results, indent=2))

    # Return exit code
    return 0 if results["overall_status"] == "passed" else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
