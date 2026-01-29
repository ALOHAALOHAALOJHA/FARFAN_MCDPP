#!/usr/bin/env python3
"""
Rollback Manager for GNEA Compliance Implementation.

Provides checkpoint and rollback functionality for GNEA compliance changes.
Document: FPN-GNEA-007
Version: 1.0.0
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class RollbackManager:
    """Manages rollback points for GNEA compliance implementation."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the rollback manager.

        Args:
            repo_root: Path to repository root. Defaults to current working directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self.log_file = self.repo_root / "scripts" / "enforcement" / "rollback_log.jsonl"

    def create_checkpoint(self, description: str) -> str:
        """Create a git checkpoint commit for rollback.

        Args:
            description: Description of the checkpoint

        Returns:
            The commit hash of the checkpoint
        """
        timestamp = datetime.now().isoformat()
        commit_message = f"[GNEA CHECKPOINT] {description}\n\nTimestamp: {timestamp}"

        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self.repo_root,
            check=True,
            capture_output=True
        )

        # Create commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True
        )

        # Get commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_root,
            text=True
        ).strip()

        # Log checkpoint
        self._log_checkpoint(commit_hash, description, timestamp)

        print(f"✓ Checkpoint created: {commit_hash[:8]}")
        print(f"  Description: {description}")
        return commit_hash

    def rollback_to_checkpoint(self, commit_hash: str) -> bool:
        """Rollback to a specific checkpoint commit.

        Args:
            commit_hash: The commit hash to rollback to

        Returns:
            True if rollback succeeded, False otherwise
        """
        try:
            # Reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.repo_root,
                check=True
            )
            print(f"✓ Rolled back to checkpoint: {commit_hash[:8]}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Rollback failed: {e}")
            return False

    def list_checkpoints(self, limit: int = 10) -> list[dict]:
        """List recent GNEA checkpoint commits.

        Args:
            limit: Maximum number of checkpoints to return

        Returns:
            List of checkpoint dictionaries
        """
        result = subprocess.run(
            ["git", "log", f"--oneline=-{limit}", "--grep=GNEA CHECKPOINT"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False
        )

        checkpoints = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    checkpoints.append({
                        "hash": parts[0],
                        "message": parts[1]
                    })

        return checkpoints

    def _log_checkpoint(self, commit_hash: str, description: str, timestamp: str):
        """Log checkpoint to audit file.

        Args:
            commit_hash: The commit hash
            description: Checkpoint description
            timestamp: ISO format timestamp
        """
        import json

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": timestamp,
            "commit_hash": commit_hash,
            "description": description,
            "action": "checkpoint_created"
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GNEA Rollback Manager"
    )
    parser.add_argument(
        "action",
        choices=["checkpoint", "rollback", "list"],
        help="Action to perform"
    )
    parser.add_argument(
        "-d", "--description",
        help="Checkpoint description"
    )
    parser.add_argument(
        "-c", "--commit",
        help="Commit hash for rollback"
    )

    args = parser.parse_args()

    manager = RollbackManager()

    if args.action == "checkpoint":
        if not args.description:
            print("Error: --description required for checkpoint")
            sys.exit(1)
        manager.create_checkpoint(args.description)

    elif args.action == "rollback":
        if not args.commit:
            print("Error: --commit required for rollback")
            sys.exit(1)
        success = manager.rollback_to_checkpoint(args.commit)
        sys.exit(0 if success else 1)

    elif args.action == "list":
        checkpoints = manager.list_checkpoints()
        if checkpoints:
            print("Recent GNEA Checkpoints:")
            for cp in checkpoints:
                print(f"  {cp['hash'][:8]} - {cp['message']}")
        else:
            print("No GNEA checkpoints found")


if __name__ == "__main__":
    main()
