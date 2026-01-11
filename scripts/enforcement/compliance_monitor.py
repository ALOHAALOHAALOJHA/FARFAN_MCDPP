#!/usr/bin/env python3
"""
Compliance Monitor for GNEA Implementation.

Provides audit logging and real-time compliance tracking.
Document: FPN-GNEA-008
Version: 1.0.0
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class ComplianceMonitor:
    """Monitors and logs GNEA compliance actions."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the compliance monitor.

        Args:
            repo_root: Path to repository root. Defaults to current working directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self.log_file = self.repo_root / "scripts" / "enforcement" / "compliance_log.jsonl"

    def log_action(
        self,
        action: str,
        files: list[str],
        status: str,
        details: Optional[dict[str, Any]] = None
    ):
        """Log a compliance action to the audit trail.

        Args:
            action: The action performed (e.g., "file_renamed", "metadata_injected")
            files: List of files affected by the action
            status: Status of the action ("success", "failed", "skipped")
            details: Optional additional details about the action
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "files": files,
            "status": status,
            "details": details or {}
        }

        self._write_log(entry)

    def log_phase_start(self, phase: int, phase_name: str):
        """Log the start of a GNEA implementation phase.

        Args:
            phase: Phase number
            phase_name: Name/description of the phase
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "phase_start",
            "phase": phase,
            "phase_name": phase_name,
            "status": "started"
        }

        self._write_log(entry)
        print(f"📋 Phase {phase}: {phase_name} - Started")

    def log_phase_complete(self, phase: int, phase_name: str, metrics: Optional[dict] = None):
        """Log the completion of a GNEA implementation phase.

        Args:
            phase: Phase number
            phase_name: Name/description of the phase
            metrics: Optional metrics about the phase completion
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "phase_complete",
            "phase": phase,
            "phase_name": phase_name,
            "status": "completed",
            "metrics": metrics or {}
        }

        self._write_log(entry)
        print(f"✓ Phase {phase}: {phase_name} - Completed")
        if metrics:
            print(f"  Metrics: {metrics}")

    def log_error(self, action: str, error: str, context: Optional[dict] = None):
        """Log an error during compliance implementation.

        Args:
            action: The action that failed
            error: Error message
            context: Optional context about the error
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "status": "error",
            "error": error,
            "context": context or {}
        }

        self._write_log(entry)
        print(f"✗ Error in {action}: {error}")

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of compliance actions.

        Returns:
            Dictionary with action counts and status breakdown
        """
        if not self.log_file.exists():
            return {"total": 0, "by_status": {}, "by_action": {}}

        summary = {
            "total": 0,
            "by_status": {},
            "by_action": {}
        }

        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    summary["total"] += 1

                    status = entry.get("status", "unknown")
                    summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

                    action = entry.get("action", "unknown")
                    summary["by_action"][action] = summary["by_action"].get(action, 0) + 1
                except json.JSONDecodeError:
                    continue

        return summary

    def _write_log(self, entry: dict[str, Any]):
        """Write a log entry to the log file.

        Args:
            entry: The log entry to write
        """
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GNEA Compliance Monitor"
    )
    parser.add_argument(
        "action",
        choices=["summary", "log"],
        help="Action to perform"
    )
    parser.add_argument(
        "--action-type",
        help="Action type for log entry"
    )
    parser.add_argument(
        "--status",
        help="Status for log entry"
    )

    args = parser.parse_args()

    monitor = ComplianceMonitor()

    if args.action == "summary":
        summary = monitor.get_summary()
        print("Compliance Log Summary:")
        print(f"  Total entries: {summary['total']}")
        print(f"  By status: {summary['by_status']}")
        print(f"  By action: {summary['by_action']}")

    elif args.action == "log":
        if not args.action_type or not args.status:
            print("Error: --action-type and --status required for log")
            return
        monitor.log_action(args.action_type, [], args.status)


if __name__ == "__main__":
    main()
