# CQVR v2.1 Severity Enhancement - Quick Reference

## At-a-Glance Comparison

### Decision Thresholds

| Metric | v2.0 (Original) | v2.1 (Enhanced) | Change |
|--------|-----------------|-----------------|--------|
| **TIER1_THRESHOLD** | 35/55 | **40/55** | +5 pts (+14%) |
| **TIER1_PRODUCTION** | 45/55 | **50/55** | +5 pts (+11%) |
| **TIER2_MINIMUM** | None | **20/30** | NEW (67% min) |
| **TIER3_MINIMUM** | None | **8/15** | NEW (53% min) |
| **TOTAL_PRODUCTION** | 80/100 | **85/100** | +5 pts (+6%) |
| **Blockers for PRODUCCION** | Some allowed | **ZERO** | Strict |
| **Blockers for PARCHEAR** | ≤2 | **≤1** | Halved |
| **PARCHEAR Tier 1** | 40 | **45** | +5 pts |
| **PARCHEAR Total** | 70 | **75** | +5 pts |

### Validation Enhancements

| Check | v2.0 | v2.1 | Impact |
|-------|------|------|--------|
| **Source Hash Length** | Any | **≥32 chars** | Ensures proper hash |
| **"TODO" Placeholder** | Warning | **CRITICAL blocker** | Blocks production |
| **Missing Source Hash** | -1 pt | **0 pts + CRITICAL** | Provenance required |

## Results Comparison

### Estimated Impact (based on 300 contracts)

| Status | v2.0 (est.) | v2.1 (actual) | Change |
|--------|-------------|---------------|--------|
| **PRODUCCION** | ~50-80 | **25** | -50% to -69% |
| **PARCHEAR** | ~30-50 | **2** | -93% to -96% |
| **REFORMULAR** | ~170-220 | **273** | +24% to +60% |

### Quality Bar Raised

```
v2.0: More lenient ──────────────────────── v2.1: Strict
      [_____|_____|_____|_____|_____]             [___|__|_]
       35   45    70    80   100                  40 50 85

      Production threshold ↑                       Only top tier →
```

## Key Severity Points Addressed

### 1. Critical Component Failures (Tier 1)
- **Before**: Tier 1 ≥ 35 was acceptable
- **After**: Tier 1 ≥ 40 required, ≥50 for production
- **Why**: Ensures identity-schema, method-assembly integrity

### 2. Functional Quality (Tier 2)
- **Before**: No minimum enforced
- **After**: Tier 2 ≥ 20 required
- **Why**: Patterns, specificity, validation must meet baseline

### 3. Documentation Quality (Tier 3)
- **Before**: No minimum enforced
- **After**: Tier 3 ≥ 8 required
- **Why**: Documentation, templates, metadata matter

### 4. Zero-Blocker Production
- **Before**: Production allowed some blockers
- **After**: ZERO blockers for production
- **Why**: No known issues in deployed contracts

### 5. Provenance Chain
- **Before**: source_hash could be placeholder
- **After**: Must be ≥32 chars, no "TODO"
- **Why**: Traceability is non-negotiable

## Usage

### Evaluate Single Contract
```bash
python scripts/cqvr_evaluator_standalone.py --contract Q001.v3.json
```

### Evaluate All 300 & Generate Dashboard
```bash
python scripts/generate_enhanced_cqvr_dashboard.py
# Outputs: cqvr_dashboard_enhanced_v2.1.html
```

### View Dashboard
```bash
open cqvr_dashboard_enhanced_v2.1.html
# Interactive, filterable, shows all 300 scores
```

## Decision Making Guide

### ✅ PRODUCCION (25 contracts = 8.3%)
**Action**: Deploy after final review
**Confidence**: High - passed strict multi-tier validation
**Error Risk**: Low

### ⚠️ PARCHEAR (2 contracts = 0.7%)
**Action**: Apply targeted fixes, re-evaluate
**Confidence**: Medium - fixable with patches
**Error Risk**: Medium (after patches: Low)

### ✗ REFORMULAR (273 contracts = 91.0%)
**Action**: Prioritize by policy area, regenerate or fix
**Priority Areas**:
1. Identity-schema mismatches
2. Method-assembly orphans
3. Missing/invalid source hashes
4. Pattern coverage gaps

## Files Generated

1. **`cqvr_dashboard_enhanced_v2.1.html`** - Interactive dashboard
2. **`cqvr_evaluation_enhanced_v2.1.json`** - Full results (300 contracts)
3. **`CQVR_ENHANCED_SEVERITY_REPORT.md`** - Detailed analysis
4. **`scripts/cqvr_evaluator_standalone.py`** - Enhanced evaluator
5. **`scripts/generate_enhanced_cqvr_dashboard.py`** - Dashboard generator

## Summary

**Enhanced severity successfully reduces error probability** by:
- Raising quality bar across all tiers
- Enforcing multi-dimensional minimums
- Requiring zero blockers for production
- Validating provenance chain integrity

**Only 8.3% of contracts pass production** - ensuring only the highest quality implementations are deployed.

---
Version: CQVR v2.1
Date: 2025-12-17
Contracts Evaluated: 300
Commit: d4e88e7
