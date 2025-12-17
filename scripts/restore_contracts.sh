#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$PROJECT_ROOT/backups"
CONTRACTS_DIR="$PROJECT_ROOT/src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"

usage() {
    cat << EOF
Usage: $0 --backup <backup_identifier>

Restore contracts from a specific backup.

Options:
    --backup IDENTIFIER  Backup to restore (date or full path)
    -h, --help          Show this help message

Examples:
    $0 --backup 2026-01-14
    $0 --backup contracts_20260114_120000
    $0 --backup /path/to/backup

EOF
    exit 1
}

main() {
    local backup=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup)
                backup="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                echo "ERROR: Unknown option: $1" >&2
                usage
                ;;
        esac
    done
    
    if [ -z "$backup" ]; then
        echo "ERROR: --backup is required" >&2
        usage
    fi
    
    exec "$SCRIPT_DIR/rollback.sh" --version "$backup"
}

main "$@"
