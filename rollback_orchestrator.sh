#!/bin/bash
# Rollback orchestrator to previous state

set -e

echo "=========================================="
echo "ORCHESTRATOR ROLLBACK"
echo "=========================================="

# Find latest backup
BACKUP_DIR=$(ls -td backups/*/ 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "✗ No backup found in backups/"
    exit 1
fi

BACKUP_FILE="${BACKUP_DIR}orchestrator.py.bak"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "✗ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Found backup: $BACKUP_FILE"
echo "Rolling back..."

# Create safety backup of current state
cp src/orchestration/orchestrator.py src/orchestration/orchestrator.py.before_rollback

# Restore from backup
cp "$BACKUP_FILE" src/orchestration/orchestrator.py

echo "✓ Rollback complete"
echo ""
echo "Verification:"
python -m py_compile src/orchestration/orchestrator.py && echo "✓ Python syntax valid"

echo ""
echo "Safety backup saved to: src/orchestration/orchestrator.py.before_rollback"