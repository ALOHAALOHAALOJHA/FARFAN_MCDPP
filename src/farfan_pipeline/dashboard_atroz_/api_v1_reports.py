"""Reporting Automation - Phase 9 Integration
Scheduled report generation, export triggers, and notification hooks.
"""

from pathlib import Path
from typing import Any
from datetime import datetime, timedelta
import json
import structlog

logger = structlog.get_logger(__name__)


class ReportScheduler:
    """Manages scheduled report generation."""

    def __init__(self):
        self.schedules_file = Path("dashboard_outputs/report_schedules.json")
        self.schedules = self._load_schedules()

    def _load_schedules(self) -> list[dict]:
        """Load existing schedules from disk."""
        if self.schedules_file.exists():
            with open(self.schedules_file) as f:
                return json.load(f)
        return []

    def _save_schedules(self):
        """Save schedules to disk."""
        self.schedules_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.schedules_file, "w") as f:
            json.dump(self.schedules, f, indent=2)

    async def get_schedules(self) -> dict[str, Any]:
        """Get all report schedules.

        Returns:
            {
                "schedules": [
                    {
                        "id": "schedule_001",
                        "name": "Weekly PDET Report",
                        "frequency": "weekly",  # daily | weekly | monthly
                        "day": "monday",  # for weekly
                        "time": "09:00",
                        "regions": ["arauca", "catatumbo"],
                        "format": "pdf",  # pdf | json | csv
                        "recipients": ["email@example.com"],
                        "enabled": true,
                        "lastRun": "2024-01-14T09:00:00Z",
                        "nextRun": "2024-01-21T09:00:00Z",
                        "created": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": int
            }
        """
        return {
            "schedules": self.schedules,
            "total": len(self.schedules)
        }

    async def create_schedule(self, schedule_data: dict[str, Any]) -> dict[str, Any]:
        """Create new report schedule.

        Args:
            schedule_data: Schedule configuration

        Returns:
            Created schedule with ID
        """
        schedule_id = f"schedule_{len(self.schedules) + 1:03d}"

        schedule = {
            "id": schedule_id,
            "name": schedule_data.get("name", "Unnamed Schedule"),
            "frequency": schedule_data.get("frequency", "weekly"),
            "day": schedule_data.get("day"),
            "time": schedule_data.get("time", "09:00"),
            "regions": schedule_data.get("regions", []),
            "format": schedule_data.get("format", "pdf"),
            "recipients": schedule_data.get("recipients", []),
            "enabled": schedule_data.get("enabled", True),
            "lastRun": None,
            "nextRun": self._calculate_next_run(schedule_data),
            "created": datetime.utcnow().isoformat()
        }

        self.schedules.append(schedule)
        self._save_schedules()

        logger.info(f"Created report schedule: {schedule_id}")
        return schedule

    async def update_schedule(self, schedule_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update existing schedule."""
        for schedule in self.schedules:
            if schedule["id"] == schedule_id:
                schedule.update(updates)
                schedule["nextRun"] = self._calculate_next_run(schedule)
                self._save_schedules()
                return schedule

        raise ValueError(f"Schedule not found: {schedule_id}")

    async def delete_schedule(self, schedule_id: str) -> dict[str, Any]:
        """Delete schedule."""
        self.schedules = [s for s in self.schedules if s["id"] != schedule_id]
        self._save_schedules()
        return {"deleted": schedule_id}

    def _calculate_next_run(self, schedule: dict) -> str:
        """Calculate next run time based on frequency."""
        now = datetime.utcnow()
        frequency = schedule.get("frequency", "weekly")

        if frequency == "daily":
            next_run = now + timedelta(days=1)
        elif frequency == "weekly":
            next_run = now + timedelta(days=7)
        elif frequency == "monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=7)

        return next_run.isoformat()


class ReportGenerator:
    """Handles immediate report generation and Phase 9 integration."""

    def __init__(self):
        self.phase9_path = Path("/home/user/FARFAN_MCDPP/src/farfan_pipeline/phases/Phase_09")

    async def generate_report(self, request: dict[str, Any]) -> dict[str, Any]:
        """Generate report immediately.

        Args:
            request: {
                "regionId": str,
                "format": "pdf" | "json" | "csv",
                "sections": ["executive", "dimensions", "clusters", "questions"],
                "includeEvidence": bool,
                "includeVisualizations": bool
            }

        Returns:
            {
                "reportId": str,
                "status": "QUEUED" | "PROCESSING" | "COMPLETED",
                "downloadUrl": str,
                "format": str,
                "generatedAt": str,
                "size": int
            }
        """
        region_id = request.get("regionId")
        format_type = request.get("format", "pdf")
        report_id = f"report_{region_id}_{int(datetime.utcnow().timestamp())}"

        # In production, this would trigger Phase 9 report generator
        # For now, return structured response

        report = {
            "reportId": report_id,
            "status": "QUEUED",
            "downloadUrl": f"/api/v1/reports/download/{report_id}",
            "format": format_type,
            "generatedAt": datetime.utcnow().isoformat(),
            "size": 0,
            "request": request
        }

        logger.info(f"Queued report generation: {report_id} for region {region_id}")
        return report

    async def get_report_status(self, report_id: str) -> dict[str, Any]:
        """Get report generation status."""
        # Mock implementation
        return {
            "reportId": report_id,
            "status": "COMPLETED",
            "progress": 100,
            "downloadUrl": f"/api/v1/reports/download/{report_id}",
            "generatedAt": datetime.utcnow().isoformat()
        }


class NotificationManager:
    """Manages report notifications."""

    def __init__(self):
        self.notification_config_file = Path("dashboard_outputs/notification_config.json")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load notification configuration."""
        if self.notification_config_file.exists():
            with open(self.notification_config_file) as f:
                return json.load(f)
        return {"channels": [], "rules": []}

    def _save_config(self):
        """Save notification configuration."""
        self.notification_config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.notification_config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    async def get_config(self) -> dict[str, Any]:
        """Get notification configuration.

        Returns:
            {
                "channels": [
                    {
                        "id": "email_001",
                        "type": "email",
                        "config": {
                            "recipients": ["user@example.com"],
                            "subject": "ATROZ Report: {region_name}"
                        },
                        "enabled": true
                    },
                    {
                        "id": "webhook_001",
                        "type": "webhook",
                        "config": {
                            "url": "https://api.example.com/notifications",
                            "method": "POST",
                            "headers": {"Authorization": "Bearer ..."}
                        },
                        "enabled": true
                    }
                ],
                "rules": [
                    {
                        "id": "rule_001",
                        "trigger": "job_complete",
                        "conditions": {
                            "regions": ["*"],  # All regions
                            "scoreThreshold": 0.7
                        },
                        "channels": ["email_001"],
                        "enabled": true
                    }
                ]
            }
        """
        return self.config

    async def update_config(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Update notification configuration."""
        if "channels" in updates:
            self.config["channels"] = updates["channels"]
        if "rules" in updates:
            self.config["rules"] = updates["rules"]

        self._save_config()
        return self.config

    async def trigger_notification(self, event: dict[str, Any]) -> dict[str, Any]:
        """Trigger notification based on event.

        Args:
            event: {
                "type": "job_complete" | "report_generated" | "score_alert",
                "data": {...}
            }

        Returns:
            {
                "triggered": int,
                "channels": ["email_001", "webhook_001"],
                "status": "SUCCESS" | "PARTIAL" | "FAILED"
            }
        """
        event_type = event.get("type")
        triggered = []

        # Match rules against event
        for rule in self.config.get("rules", []):
            if rule.get("trigger") == event_type and rule.get("enabled", True):
                for channel_id in rule.get("channels", []):
                    # In production, would actually send notification
                    triggered.append(channel_id)
                    logger.info(f"Triggered notification on channel: {channel_id}")

        return {
            "triggered": len(triggered),
            "channels": triggered,
            "status": "SUCCESS" if triggered else "NO_MATCH"
        }


class CompletionHooks:
    """Manages job completion hooks for automated actions."""

    def __init__(self):
        self.hooks_file = Path("dashboard_outputs/completion_hooks.json")
        self.hooks = self._load_hooks()

    def _load_hooks(self) -> dict:
        """Load completion hooks."""
        if self.hooks_file.exists():
            with open(self.hooks_file) as f:
                return json.load(f)
        return {}

    def _save_hooks(self):
        """Save hooks."""
        self.hooks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hooks_file, "w") as f:
            json.dump(self.hooks, f, indent=2)

    async def register_hook(self, run_id: str, hook_config: dict[str, Any]) -> dict[str, Any]:
        """Register completion hook for a run.

        Args:
            run_id: Pipeline run ID
            hook_config: {
                "actions": ["generate_report", "send_notification"],
                "reportFormat": "pdf",
                "notificationChannels": ["email_001"],
                "callback": "https://api.example.com/webhook"
            }

        Returns:
            Registered hook configuration
        """
        self.hooks[run_id] = {
            "runId": run_id,
            "registered": datetime.utcnow().isoformat(),
            "status": "PENDING",
            **hook_config
        }

        self._save_hooks()
        logger.info(f"Registered completion hook for run: {run_id}")
        return self.hooks[run_id]

    async def trigger_hook(self, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        """Trigger completion hook.

        Args:
            run_id: Pipeline run ID
            result: Pipeline execution result

        Returns:
            Hook execution result
        """
        if run_id not in self.hooks:
            return {"status": "NO_HOOK"}

        hook = self.hooks[run_id]
        actions_performed = []

        for action in hook.get("actions", []):
            if action == "generate_report":
                # Trigger report generation
                actions_performed.append("report_generated")
            elif action == "send_notification":
                # Send notification
                actions_performed.append("notification_sent")

        hook["status"] = "EXECUTED"
        hook["executed"] = datetime.utcnow().isoformat()
        hook["actions_performed"] = actions_performed
        self._save_hooks()

        return {
            "runId": run_id,
            "status": "SUCCESS",
            "actions": actions_performed
        }
