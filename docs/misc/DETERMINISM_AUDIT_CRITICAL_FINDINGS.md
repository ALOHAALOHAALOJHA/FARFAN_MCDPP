# SIN_CARRETA Determinism Audit - CRITICAL FINDINGS

**Status**: ⚠️ **NON-COMPLIANT** - 2 CRITICAL violations found  
**Date**: 2025-12-12

---

## 🔴 CRITICAL VIOLATIONS (Must Fix Immediately)

### CRITICAL-1: Unseeded Random in arg_router.py

**File**: `src/canonic_phases/Phase_two/arg_router.py` (line 397)

**Current Code** (BROKEN):
```python
def maybe_validate(self, payload, *, producer, consumer):
    if not self.enabled:
        return
    if random.random() > self.sample_rate:  # ❌ UNSEEDED!
        return
```

**Fixed Code**:
```python
class PayloadDriftMonitor:
    def __init__(self, *, sample_rate: float, enabled: bool, seed: int = 42):
        self.sample_rate = max(0.0, min(sample_rate, 1.0))
        self.enabled = enabled and self.sample_rate > 0.0
        self._rng = random.Random(seed)  # ✅ Seeded RNG instance
    
    def maybe_validate(self, payload, *, producer, consumer):
        if not self.enabled:
            return
        if self._rng.random() > self.sample_rate:  # ✅ Use seeded instance
            return
        # ... rest unchanged
```

**Fix Time**: 15 minutes

---

### CRITICAL-2: Unseeded Random in schema_monitor.py

**File**: `src/canonic_phases/Phase_zero/schema_monitor.py` (line 96)

**Current Code** (BROKEN):
```python
return random.random() < self.sample_rate  # ❌ UNSEEDED!
```

**Fixed Code**: Same pattern as CRITICAL-1 - add seeded RNG instance to class

**Fix Time**: 15 minutes

---

## 📊 Additional Issues (Lower Priority)

- **HIGH**: 52 timestamp violations (using `datetime.utcnow()` instead of `datetime.now(timezone.utc)`)
- **HIGH**: 12 non-deterministic UUID4 event IDs
- **MEDIUM**: 97 dashboard timestamp issues (display-only, doesn't affect pipeline)

---

## 🎯 Compliance Score

**Current**: 67% (4/6 SIN_CARRETA principles passing)  
**After Critical Fixes**: 83% (5/6 principles passing)  
**Target**: 100%

---

## ✅ Next Action

**Option 1 (Recommended)**: I fix the 2 critical violations now (30 min total)  
**Option 2**: You review the code changes first, then I apply them  
**Option 3**: Proceed with full remediation plan (critical + high priority)

**Full audit report**: `/Users/recovered/.gemini/antigravity/brain/ae1021a6-6885-4504-b3a3-9c632a3c9120/determinism_audit_report.md`
