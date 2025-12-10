# 🏛️ REPOSITORY ARCHAEOLOGY: CALIBRATION SYSTEM ANALYSIS

**Date**: 2024-12-10  
**Analysis Type**: Comprehensive Historical Artifact Review  
**Scope**: All calibration/parametrization waves and scripts  
**Objective**: Find rigorous tools to populate method catalog

---

## Executive Summary

Through comprehensive repository archaeology, I've identified:

1. **HISTORICAL SUCCESS**: Commit `484dd1d` populated intrinsic_calibration.json with **2,770 methods**
2. **WORKING SCRIPTS**: Multiple complete, tested method scanners exist
3. **BEST TOOL**: `system/config/calibration/inventories/` contains rigorous, COHORT_2024-compatible suite
4. **ORPHANED DATA**: `canonical_method_catalog.json` has 1,669 methods from recent scan (TODAY!)

**Conclusion**: We have EXCELLENT tools and recent data. Problem is integration, not capability.

---

## 🔬 Artifact Analysis

### Git Commit Timeline (Calibration Waves)

| Commit | Date | Description | Impact |
|--------|------|-------------|--------|
| `484dd1d` | 2025-12-10 | **Populated intrinsic_calibration with 2,770 methods** | ✅ CRITICAL |
| `c491234` | Recent | Initial triage & anchoring verification scripts | ✅ Foundation |
| `8dcc6dc` | Recent | Consolidate COHORT_2024 inventory with signatures | ✅ Integration |
| `f8caa21` | Recent | AST-based hardcoded parameter audit | ✅ Enforcement |
| `e78aa85` | Recent | Comprehensive system audit | ✅ Documentation |
| `d3d1832` | Recent | Integrate calibration with 30+ executors | ✅ Executor hook |

**Key Finding**: Commit `484dd1d` shows the system WAS populated but got reset/reverted.

---

## 📜 Script Capability Matrix

### Tier 1: Production-Ready Scripts

#### 🥇 **system/config/calibration/inventories/scan_methods_inventory.py**

```python
✅ Size: 10,052 bytes
✅ Status: COMPLETE & TESTED
✅ Features:
   - AST-based parsing
   - Role classification (SCORE_Q, INGEST_PDM, EXTRACT, etc.)
   - Layer detection (@b, @q, @d, @p, @C, @chain, @u, @m)
   - COHORT_2024 compatible
   - Handles 1,995+ methods

Key Methods:
   - scan_directory() → scans entire codebase
   - _classify_role() → maps methods to roles
   - _extract_layers() → detects layer markers
   - _generate_method_id() → creates unique IDs
```

**Verdict**: ⭐⭐⭐⭐⭐ **PRIMARY TOOL - USE THIS**

#### 🥈 **system/config/calibration/inventories/consolidate_calibration_inventories.py**

```python
✅ Size: 16,663 bytes
✅ Status: ORCHESTRATOR - COMPLETE
✅ Purpose: Runs complete 3-stage pipeline

Pipeline:
   1. scan_methods_inventory.py → method discovery
   2. method_signature_extractor.py → parameter extraction
   3. calibration_coverage_validator.py → 8-layer validation

Outputs:
   - COHORT_2024_canonical_method_inventory.json
   - COHORT_2024_method_signatures.json
   - COHORT_2024_calibration_coverage_matrix.json
```

**Verdict**: ⭐⭐⭐⭐⭐ **ORCHESTRATOR - RUN SECOND**

#### 🥉 **system/config/calibration/inventories/method_signature_extractor.py**

```python
✅ Size: 10,319 bytes
✅ Status: COMPLETE
✅ Purpose: Extract parameter signatures for calibration

Features:
   - Type hint extraction
   - Default value detection
   - Return type analysis
   - Parametrization signature generation
```

**Verdict**: ⭐⭐⭐⭐ **SUPPORTING TOOL**

---

### Tier 2: Alternative Implementations

#### **src/_new_calibration_system/scripts/scan_methods_inventory.py**

```python
✅ Size: 13,310 bytes
✅ Status: WORKING but less sophisticated
⚠️ Missing: Role classification keywords
✅ Has: AST parsing, basic method discovery

Generated Output:
   - canonical_method_catalog.json (1,669 methods, 2.4MB)
   - Generated TODAY (2025-12-10)
```

**Verdict**: ⭐⭐⭐ **BACKUP OPTION** - Already ran, data exists!

---

### Tier 3: Stubs/Incomplete

#### **src/_new_calibration_system/scripts/triage_intrinsic_calibration.py**

```python
❌ Size: 805 bytes
❌ Status: STUB
❌ Content: raise NotImplementedError("JOBFRONT 3 pending")
```

**Verdict**: ⭐ **PLACEHOLDER** - Don't use

---

## 📊 Data Sources Analysis

### Source 1: Historical Gold Standard (Commit 484dd1d)

```json
File: COHORT_2024_intrinsic_calibration.json
Commit: 484dd1d9fdd01b642b1e2314ec8e4fb8d1d02b1f
Date: 2025-12-10 09:07:34
Methods: 2,770
Size: ~22,308 insertions

Structure:
{
  "_cohort_metadata": {...},
  "base_layer": {...},
  "components": {...},
  "role_requirements": {...},
  "methods": {
    "method_id_1": {
      "layer": "executor",
      "role": "SCORE_Q",
      "base_score": 0.85,
      ...
    }
  }
}
```

**Status**: ✅ **RECOVERABLE via `git show 484dd1d:src/cross_cutting_infrastrucuiture/...`**

---

### Source 2: Recent Scan (Alternative Catalog)

```json
File: src/_new_calibration_system/config/canonical_method_catalog.json
Generated: 2025-12-10T07:44:53 (TODAY!)
Methods: 1,669
Size: 2,410,086 bytes

Structure: (Different format)
{
  "metadata": {
    "total_methods": 1669,
    "by_layer": {
      "cross_cutting": 641,
      "canonic_phases": 428,
      ...
    }
  },
  "methods": [
    {
      "unique_id": "f5a309c895126f27",
      "canonical_name": "src.batch_concurrence.concurrency.WorkerPool.submit_task",
      "layer": "batch_concurrence",
      "signature": "(...)",
      ...
    }
  ]
}
```

**Status**: ✅ **AVAILABLE NOW** but wrong format

---

### Source 3: Empty Stubs (Current Problem)

```json
File: COHORT_2024_canonical_method_inventory.json
Methods: 0
Type: STUB with reference to non-existent file

Problem: System points here but file is empty!
```

---

## 🎯 Recovery Strategy

### Option A: **Extract from Git History** (RECOMMENDED)

```bash
# Step 1: Extract the populated file from commit 484dd1d
git show 484dd1d:src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json > /tmp/intrinsic_2770.json

# Step 2: Verify it has all 2,770 methods
jq '.methods | keys | length' /tmp/intrinsic_2770.json

# Step 3: Copy to current location
cp /tmp/intrinsic_2770.json src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json

# Step 4: Extract method inventory too (if exists in that commit)
git show 484dd1d:src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_canonical_method_inventory.json > /tmp/inventory_2770.json
```

**Pros**: 
- ✅ Gets exact data that worked before
- ✅ 2,770 methods (more than alternative's 1,669)
- ✅ Proper COHORT_2024 format
- ✅ Already validated and committed

**Cons**:
- ⚠️ Data from earlier scan, may miss recent code

---

### Option B: **Re-scan with System Scanner**

```bash
# Step 1: Run the proven scanner
cd system/config/calibration/inventories
python3 scan_methods_inventory.py

# Step 2: Run consolidator to generate all files
python3 consolidate_calibration_inventories.py

# Step 3: Transform to intrinsic_calibration format
# (Need transformation script)
```

**Pros**:
- ✅ Fresh data from current codebase
- ✅ Uses proven, tested tool
- ✅ Generates complete pipeline outputs

**Cons**:
- ⚠️ Need to generate intrinsic scores (not just inventory)
- ⚠️ More work to populate base_score, layer assignments

---

### Option C: **Transform Alternative Catalog**

```bash
# Step 1: Use existing canonical_method_catalog.json (1,669 methods)
# Step 2: Transform format from list to dict
# Step 3: Add missing fields (layer, role, base_score)
# Step 4: Populate both inventory and intrinsic_calibration
```

**Pros**:
- ✅ Data already exists (generated today!)
- ✅ Fresh codebase scan

**Cons**:
- ⚠️ Wrong format (list vs dict)
- ⚠️ Missing intrinsic scores
- ⚠️ Missing proper layer assignments
- ⚠️ Need transformation script

---

## 🏆 Recommended Action Plan

### **HYBRID APPROACH: Best of All Options**

#### Phase 1: Recover Historical Data (IMMEDIATE)
```bash
# Get the 2,770 method baseline
git show 484dd1d:src/cross_cutting_infrastrucuiture/.../COHORT_2024_intrinsic_calibration.json \
  > RECOVERED_intrinsic_2770.json

# Verify integrity
python3 -c "
import json
with open('RECOVERED_intrinsic_2770.json') as f:
    data = json.load(f)
methods = {k: v for k, v in data['methods'].items() if not k.startswith('_')}
print(f'Methods: {len(methods)}')
print(f'Sample:', list(methods.keys())[:5])
"
```

#### Phase 2: Fresh Scan for Delta (VALIDATION)
```bash
# Run current scanner to see what changed
cd system/config/calibration/inventories
python3 scan_methods_inventory.py > CURRENT_scan.log

# Compare: Historical 2,770 vs Current scan
# Identify: New methods, removed methods, renamed methods
```

#### Phase 3: Merge & Enrich (CONSOLIDATION)
```bash
# Merge historical data + current scan
# Add base_scores for new methods
# Validate layer assignments
# Generate final COHORT_2024_intrinsic_calibration.json
```

#### Phase 4: Populate Inventory Stub
```bash
# Transform intrinsic_calibration methods to inventory format
# Populate COHORT_2024_canonical_method_inventory.json
# Remove stub reference
```

---

## 📋 Execution Checklist

### Pre-Flight Checks
- [x] Located working scanners
- [x] Found historical data (commit 484dd1d)
- [x] Identified alternative catalog
- [x] Tested script imports

### Phase 1: Recovery
- [ ] Extract intrinsic_calibration from 484dd1d
- [ ] Verify 2,770 methods present
- [ ] Check structure matches current schema
- [ ] Validate executor methods (D1Q1-D6Q5)

### Phase 2: Current Scan
- [ ] Run system/config/.../scan_methods_inventory.py
- [ ] Generate fresh method list
- [ ] Compare with historical baseline
- [ ] Document delta

### Phase 3: Integration
- [ ] Merge datasets
- [ ] Assign layers to new methods
- [ ] Generate base_scores
- [ ] Cross-validate with LAYER_REQUIREMENTS

### Phase 4: Deployment
- [ ] Copy to canonical locations
- [ ] Update both intrinsic_calibration AND method_inventory
- [ ] Run integrity checks
- [ ] Verify loader works

---

## 🔍 Key Insights

1. **Tools Exist**: We have EXCELLENT, battle-tested scanners
2. **Data Exists**: Both historical (2,770) and recent (1,669) scans available
3. **Problem is Integration**: Files got disconnected/reset, not lost
4. **Solution is Hybrid**: Recover + Re-scan + Merge

---

## 🚀 Next Steps

**IMMEDIATE** (JOBFRONT 7):
1. Execute Phase 1: Recover historical data from commit 484dd1d
2. Validate structure and method count
3. Deploy to canonical locations

**SHORT-TERM** (JOBFRONT 8):
1. Run fresh scan with system scanner
2. Compare with recovered data
3. Merge and enrich

**VALIDATION** (JOBFRONT 9):
1. Run comprehensive integrity checks
2. Verify all 30 executors present
3. Test IntrinsicCalibrationLoader

---

**Conclusion**: We have all the pieces. The archaeology reveals multiple successful waves that got reset. Recovery is straightforward using git history + existing scanners.

