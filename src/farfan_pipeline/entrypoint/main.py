"""Main entry point for the FARFAN pipeline CLI.

This module provides the `farfan-pipeline` command-line interface
for running the analysis pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """Main entry point for farfan-pipeline CLI command.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Import CLI only when needed to avoid import-time overhead
        from farfan_pipeline.orchestration.cli import main as cli_main
        
        return cli_main()
    except ImportError as e:
        print(f"Error: Failed to import CLI module: {e}", file=sys.stderr)
        print("Please ensure the package is properly installed.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
