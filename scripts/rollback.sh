#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$PROJECT_ROOT/backups"
CONTRACTS_DIR="$PROJECT_ROOT/src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"

usage() {
    cat << EOF
Usage: $0 --version <backup_version>

Rollback contracts to a previous backup version.

Options:
    --version VERSION    Backup version to restore (e.g., previous, 2026-01-14, or specific timestamp)
    -h, --help          Show this help message

Examples:
    $0 --version previous              # Restore most recent backup
    $0 --version 2026-01-14            # Restore backup from specific date
    $0 --version contracts_20260114    # Restore specific backup directory

EOF
    exit 1
}

find_backup_dir() {
    local version="$1"
    
    if [ "$version" = "previous" ]; then
        local latest_backup
        latest_backup=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "contracts_*" | sort -r | head -n1)
        if [ -z "$latest_backup" ]; then
            echo "ERROR: No backups found in $BACKUP_DIR" >&2
            exit 1
        fi
        echo "$latest_backup"
    elif [ -d "$BACKUP_DIR/$version" ]; then
        echo "$BACKUP_DIR/$version"
    elif [ -d "$BACKUP_DIR/contracts_$version" ]; then
        echo "$BACKUP_DIR/contracts_$version"
    else
        local date_backup
        date_backup=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "contracts_${version}*" | head -n1)
        if [ -n "$date_backup" ]; then
            echo "$date_backup"
        else
            echo "ERROR: Backup version '$version' not found" >&2
            exit 1
        fi
    fi
}

verify_backup() {
    local backup_dir="$1"
    
    if [ ! -d "$backup_dir" ]; then
        echo "ERROR: Backup directory does not exist: $backup_dir" >&2
        exit 1
    fi
    
    local contract_count
    contract_count=$(find "$backup_dir" -name "Q*.v3.json" | wc -l)
    
    if [ "$contract_count" -eq 0 ]; then
        echo "ERROR: No contracts found in backup: $backup_dir" >&2
        exit 1
    fi
    
    echo "Found $contract_count contracts in backup"
}

create_pre_rollback_backup() {
    local timestamp
    timestamp=$(date -u +%Y%m%d_%H%M%S)
    local pre_rollback_dir="$BACKUP_DIR/pre_rollback_$timestamp"
    
    mkdir -p "$pre_rollback_dir"
    
    echo "Creating pre-rollback backup: $pre_rollback_dir"
    cp -r "$CONTRACTS_DIR"/*.json "$pre_rollback_dir/" 2>/dev/null || true
    
    echo "$pre_rollback_dir"
}

restore_contracts() {
    local backup_dir="$1"
    
    echo "Restoring contracts from: $backup_dir"
    
    local restored=0
    local failed=0
    
    for contract_file in "$backup_dir"/Q*.v3.json; do
        if [ -f "$contract_file" ]; then
            local filename
            filename=$(basename "$contract_file")
            local target="$CONTRACTS_DIR/$filename"
            
            if cp "$contract_file" "$target"; then
                ((restored++))
            else
                echo "WARNING: Failed to restore $filename" >&2
                ((failed++))
            fi
        fi
    done
    
    echo "Restored: $restored contracts"
    echo "Failed: $failed contracts"
    
    if [ "$failed" -gt 0 ]; then
        return 1
    fi
}

main() {
    local version=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                version="$2"
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
    
    if [ -z "$version" ]; then
        echo "ERROR: --version is required" >&2
        usage
    fi
    
    echo "========================================"
    echo "Contract Rollback Script"
    echo "========================================"
    echo ""
    
    local backup_dir
    backup_dir=$(find_backup_dir "$version")
    echo "Target backup: $backup_dir"
    
    verify_backup "$backup_dir"
    
    local pre_rollback_backup
    pre_rollback_backup=$(create_pre_rollback_backup)
    
    if restore_contracts "$backup_dir"; then
        echo ""
        echo "✅ ROLLBACK SUCCESSFUL"
        echo ""
        echo "Contracts restored from: $backup_dir"
        echo "Pre-rollback backup saved: $pre_rollback_backup"
        echo ""
        echo "To verify, run:"
        echo "  python3 scripts/evaluate_all_contracts.py"
    else
        echo ""
        echo "❌ ROLLBACK FAILED"
        echo ""
        echo "Some contracts could not be restored."
        echo "Pre-rollback backup available at: $pre_rollback_backup"
        exit 1
    fi
}

main "$@"
