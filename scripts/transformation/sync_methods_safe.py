#!/usr/bin/env python3
"""
FARFAN Method Synchronization - Production Safe Edition

Safely syncs micro_questions method_sets with canonical_methods_triangulated.

Safety guarantees:
1. Verified backup before any changes (instant rollback)
2. Atomic writes (no partial corruption)
3. Metadata preservation (no data loss)
4. Structure validation (no broken output)
5. Detailed change log (full audit trail)
"""

import json
import shutil
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Configuration
CANONICAL_PATH = 'src/farfan_pipeline/phases/Phase_two/json_files_phase_two/canonical_methods_triangulated.json'
MONOLITH_PATH = 'canonic_questionnaire_central/questionnaire_monolith.json'
BACKUP_DIR = Path('backups/method_sync')
DRY_RUN = False  # Set False to execute

# Safety limits
MAX_CHANGES = 100  # Sanity check
MIN_QUESTIONS = 10  # Sanity check


def calculate_sha256(filepath: str) -> str:
    """Calculate file checksum for verification"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_verified_backup(filepath: str, backup_dir: Path) -> Path:
    """Create backup with checksum verification"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{Path(filepath).name}.{timestamp}.backup"
    
    # Calculate original checksum
    original_hash = calculate_sha256(filepath)
    
    # Copy
    shutil.copy2(filepath, backup_path)
    
    # Verify
    backup_hash = calculate_sha256(backup_path)
    if original_hash != backup_hash:
        backup_path.unlink()
        raise ValueError("Backup checksum verification failed!")
    
    print(f"✓ Backup: {backup_path}")
    print(f"  Hash: {original_hash[:16]}...")
    return backup_path


def get_base_question(qid: str) -> str:
    """Extract base question from ID (Q1-Q30 pattern repeats)"""
    if qid.startswith('Q'):
        q_num = int(qid[1:])
        return str((q_num - 1) % 30 + 1).zfill(2)
    return None


def build_canonical_lookup(canonical_data: list) -> Dict[str, List[Tuple[str, str]]]:
    """
    Build lookup: base_question -> [(class, method), ...]
    Canonical uses 'method' field
    """
    lookup = {}
    for entry in canonical_data:
        base_q = entry['base_question']
        methods = [(m['class'], m['method']) for m in entry['canonical_methods']]
        lookup[base_q] = methods
    return lookup


def sync_method_sets(micro_questions: list, canonical_lookup: dict) -> Tuple[int, List[dict]]:
    """
    Sync method_sets with canonical data.
    
    CRITICAL: 
    - Canonical has 'method' field
    - Monolith has 'function' field
    - Must preserve ALL existing metadata
    
    Returns: (num_modified, change_log)
    """
    modified_count = 0
    change_log = []
    
    for question in micro_questions:
        qid = question['question_id']
        base_q = get_base_question(qid)
        
        if not base_q or base_q not in canonical_lookup:
            continue
        
        # Get current method_sets (uses 'function' field)
        current_methods = question.get('method_sets', [])
        current_set = set((m['class'], m['function']) for m in current_methods 
                         if 'class' in m and 'function' in m)
        
        # Get canonical methods (uses 'method' field)
        canonical_set = set(canonical_lookup[base_q])
        
        if current_set == canonical_set:
            continue  # Already in sync
        
        # Build new method_sets
        new_methods = []
        
        # Create lookup of existing methods by (class, function) for fast access
        existing_by_key = {(m['class'], m['function']): m 
                          for m in current_methods 
                          if 'class' in m and 'function' in m}
        
        for idx, (cls, method_name) in enumerate(canonical_lookup[base_q], 1):
            key = (cls, method_name)
            
            if key in existing_by_key:
                # Method exists - preserve ALL metadata
                new_methods.append(existing_by_key[key])
            else:
                # New method - create minimal entry with 'function' field
                new_methods.append({
                    'class': cls,
                    'function': method_name,  # CRITICAL: use 'function' not 'method'
                    'method_type': 'primary',
                    'priority': idx  # Sequential priority from canonical order
                })
        
        # Log the change
        change_log.append({
            'question_id': qid,
            'base_question': base_q,
            'removed': list(current_set - canonical_set),
            'added': list(canonical_set - current_set),
            'old_count': len(current_methods),
            'new_count': len(new_methods)
        })
        
        # Apply change
        question['method_sets'] = new_methods
        modified_count += 1
    
    return modified_count, change_log


def validate_structure(data: dict) -> None:
    """Validate monolith structure is intact"""
    if 'blocks' not in data:
        raise ValueError("Missing 'blocks' key")
    if 'micro_questions' not in data['blocks']:
        raise ValueError("Missing 'micro_questions' in blocks")
    if not isinstance(data['blocks']['micro_questions'], list):
        raise ValueError("micro_questions must be a list")


def atomic_write_json(data: dict, filepath: str) -> None:
    """Write JSON atomically using temp file + rename"""
    temp_path = f"{filepath}.tmp.{os.getpid()}"
    
    try:
        # Write to temp
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        
        # Verify temp file
        with open(temp_path) as f:
            json.load(f)  # Will raise if invalid JSON
        
        # Atomic rename (POSIX guarantees atomicity)
        os.replace(temp_path, filepath)
        
        print(f"✓ Saved: {filepath}")
        
    finally:
        # Cleanup temp file if it still exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n{'='*80}")
    print(f"FARFAN METHOD SYNC - {'🔍 DRY RUN' if DRY_RUN else '🔥 LIVE MODE'}")
    print(f"{'='*80}\n")
    
    # === STEP 1: Load data ===
    print("Step 1: Loading files...")
    try:
        with open(CANONICAL_PATH) as f:
            canonical_data = json.load(f)
        with open(MONOLITH_PATH) as f:
            monolith_data = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load files: {e}")
        sys.exit(1)
    
    validate_structure(monolith_data)
    micro_questions = monolith_data['blocks']['micro_questions']
    
    if len(micro_questions) < MIN_QUESTIONS:
        print(f"✗ Only {len(micro_questions)} questions (expected {MIN_QUESTIONS}+)")
        sys.exit(1)
    
    print(f"  Canonical entries: {len(canonical_data)}")
    print(f"  Micro questions: {len(micro_questions)}")
    
    # === STEP 2: Build lookup ===
    print("\nStep 2: Building canonical lookup...")
    canonical_lookup = build_canonical_lookup(canonical_data)
    print(f"  Base questions: {len(canonical_lookup)}")
    
    # === STEP 3: Analyze changes ===
    print("\nStep 3: Analyzing changes needed...")
    
    # Work on a deep copy to avoid modifying original in dry run
    import copy
    work_data = copy.deepcopy(monolith_data)
    work_questions = work_data['blocks']['micro_questions']
    
    modified_count, change_log = sync_method_sets(work_questions, canonical_lookup)
    
    if modified_count == 0:
        print("\n✅ No changes needed - already in sync!")
        return
    
    # === STEP 4: Display changes ===
    print(f"\n{'='*80}")
    print(f"CHANGES PREVIEW")
    print(f"{'='*80}")
    
    for change in change_log[:10]:  # Show first 10
        print(f"\n{change['question_id']} (base {change['base_question']}):")
        for cls, func in change['removed']:
            print(f"  🗑️  Remove: {cls}.{func}")
        for cls, func in change['added']:
            print(f"  ➕ Add: {cls}.{func}")
    
    if len(change_log) > 10:
        print(f"\n... and {len(change_log) - 10} more questions")
    
    # === STEP 5: Summary ===
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Questions to modify: {modified_count}")
    print(f"Total removals: {sum(len(c['removed']) for c in change_log)}")
    print(f"Total additions: {sum(len(c['added']) for c in change_log)}")
    
    if modified_count > MAX_CHANGES:
        print(f"\n✗ Too many changes ({modified_count} > {MAX_CHANGES})")
        print("  Increase MAX_CHANGES if this is expected")
        sys.exit(1)
    
    if DRY_RUN:
        print(f"\n🔍 DRY RUN - No files modified")
        print(f"   Set DRY_RUN = False to execute")
        
        # Save change log even in dry run
        log_path = BACKUP_DIR / f"changes_preview_{timestamp}.json"
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(change_log, f, indent=2)
        print(f"\n   Preview saved: {log_path}")
        return
    
    # === STEP 6: Confirmation ===
    print(f"\n⚠️  READY TO MODIFY {MONOLITH_PATH}")
    response = input("Type 'YES' to proceed: ")
    if response != 'YES':
        print("Aborted.")
        return
    
    # === STEP 7: Backup ===
    print("\nStep 7: Creating backup...")
    backup_path = create_verified_backup(MONOLITH_PATH, BACKUP_DIR)
    
    # === STEP 8: Validate output ===
    print("\nStep 8: Validating output structure...")
    validate_structure(work_data)
    print("  ✓ Structure valid")
    
    # === STEP 9: Write ===
    print("\nStep 9: Writing changes...")
    atomic_write_json(work_data, MONOLITH_PATH)
    
    # === STEP 10: Save log ===
    log_path = BACKUP_DIR / f"changes_{timestamp}.json"
    with open(log_path, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'backup': str(backup_path),
            'modified_count': modified_count,
            'changes': change_log
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS")
    print(f"{'='*80}")
    print(f"Modified: {modified_count} questions")
    print(f"Backup: {backup_path}")
    print(f"Log: {log_path}")
    print(f"\nTo rollback: cp {backup_path} {MONOLITH_PATH}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
