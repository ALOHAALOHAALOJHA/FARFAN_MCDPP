# Missing Concepts Resolution Log

**Generated:** 2026-01-17
**Purpose:** Phase 6 adjudication of classes imported from `orchestration.orchestrator` that never existed

---

## Resolution Summary

| Concept | Status | Canonical Location | Call Sites |
|---------|--------|-------------------|------------|
| `MethodExecutor` | ✅ FOUND | `farfan_pipeline.orchestration.core_orchestrator:780+` | 5+ |
| `Orchestrator` | ✅ FOUND | `farfan_pipeline.orchestration.core_orchestrator:950+` | 10+ |
| `ScoredMicroQuestion` | ✅ FOUND | `farfan_pipeline.phases.Phase_03.contracts.phase03_output_contract:13` | 3+ |
| `MicroQuestionRun` | ✅ FOUND | `farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter:101` | 2+ |
| `ResourceLimits` | ✅ FOUND | `farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller:80` | 3+ |
| `QuestionnaireSignalRegistry` | ✅ FOUND | `farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry:76` | 2+ |
| `MacroEvaluation` | 🔄 ALIAS | Use `MacroScore` from `farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score:37` | 1 (TYPE_CHECKING only) |
| `Evidence` | 🔍 AMBIGUOUS | Multiple Evidence classes exist, context-dependent | Many |
| `PhaseInstrumentation` | ❌ MISSING | Not found - likely test-only phantom | 2 (tests only) |
| `AbortSignal` | ❌ MISSING | Not found - may be in domain_errors | 0 |
| `execute_phase_with_timeout` | 🔍 INVESTIGATE | May be in core_orchestrator methods | Unknown |

---

## Detailed Resolutions

### ✅ MethodExecutor
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.orchestration.core_orchestrator` (line ~780+)
- **Justification:** Core class for phase method execution
- **Evidence:** Found in core_orchestrator.py
- **Call Sites:**
  - `phase2_60_00_base_executor_with_contract.py:79`
  - Multiple test files (7+ locations)
- **Action:** REDIRECT all imports to canonical location
- **Date:** 2026-01-17

---

### ✅ Orchestrator
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.orchestration.core_orchestrator` (line ~950+)
- **Justification:** Main pipeline orchestrator (compatibility alias for PipelineOrchestrator)
- **Evidence:** Found in core_orchestrator.py
- **Call Sites:** Multiple test files (10+ locations)
- **Action:** REDIRECT all imports to canonical location
- **Date:** 2026-01-17

---

### ✅ ScoredMicroQuestion
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.phases.Phase_03.contracts.phase03_output_contract:13`
- **Justification:** Phase 3 output contract for scored micro-questions
- **Evidence:** Dataclass defined in Phase_03 contracts
- **Call Sites:**
  - `phase4_10_00_aggregation_integration.py:19` (TYPE_CHECKING)
  - `test_orchestrator_signal_validation.py:304`
- **Action:** REDIRECT imports to Phase_03 contract
- **Date:** 2026-01-17

---

### ✅ MicroQuestionRun
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter:101`
- **Justification:** Phase 2→3 adapter contract for micro-question execution
- **Evidence:** Frozen dataclass in phase2_phase3_adapter.py
- **Call Sites:**
  - `test_phase3_contracts.py:18`
  - Phase 2 interphase usage
- **Action:** REDIRECT imports to Phase_02 interphase
- **Date:** 2026-01-17

---

### ✅ ResourceLimits
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller:80`
- **Justification:** Resource allocation and limits dataclass
- **Evidence:** Defined in Phase_00 resource_controller module
- **Call Sites:**
  - `tests/orchestration/test_resource_limits.py:15`
  - `tests/orchestration/test_resource_limits_integration.py:17`
  - `tests/orchestration/test_resource_limits_regression.py:17`
- **Action:** REDIRECT imports to Phase_00 resource_controller
- **Date:** 2026-01-17

---

### ✅ QuestionnaireSignalRegistry
- **Status:** FOUND
- **Canonical Location:** `farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry:76`
- **Justification:** Signal registry for questionnaire signal routing
- **Evidence:** Class defined in Phase_02 registries
- **Call Sites:**
  - `test_phase2_sisas_checklist.py:95`
  - Phase 02 internal usage
- **Action:** REDIRECT imports to Phase_02 registries
- **Date:** 2026-01-17

---

### 🔄 MacroEvaluation
- **Status:** ALIAS (use MacroScore instead)
- **Replacement:** `farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score.MacroScore`
- **Justification:** `MacroEvaluation` never existed as a proper class; `MacroScore` is the canonical macro aggregation type
- **Evidence:**
  - Only used in TYPE_CHECKING block in `phase4_10_00_aggregation_integration.py:19`
  - Function signature at line 476 returns `MacroEvaluation` but constructs from `MacroScore`
  - `MacroEvaluationIn` exists only in API schemas (dashboard_atroz_)
- **Call Sites:** 1 (TYPE_CHECKING only, not runtime)
- **Action:**
  - **Option 1 (PREFERRED):** Replace TYPE_CHECKING import with `MacroScore`
  - **Option 2:** Create type alias: `MacroEvaluation = MacroScore` in Phase_07
- **Decision:** Use MacroScore directly (no alias needed for single TYPE_CHECKING usage)
- **Date:** 2026-01-17

---

### 🔍 Evidence
- **Status:** AMBIGUOUS - Multiple Evidence classes exist
- **Findings:**
  - `EvidenceStore` in `infrastructure/contractual/dura_lex/idempotency_dedup.py:10`
  - `EvidenceSegment` in `methods/analyzer_one.py:3008`
  - `EvidenceBundle` in `methods/policy_processor.py:1273`
  - `EvidenceType`, `EvidenceNode`, `EvidenceEdge`, `EvidenceGraph`, `EvidenceNexus` in Phase_02/phase2_80_00_evidence_nexus.py
- **Justification:** No single "Evidence" class - concept distributed across specific evidence types
- **Call Sites:**
  - `test_phase3_contracts.py:18` imports `Evidence` (needs context investigation)
- **Action:**
  - **INVESTIGATE** which Evidence class is intended in each context
  - Most likely: Import from `phase2_80_00_evidence_nexus` or use `Any | None` for evidence field
- **Date:** 2026-01-17

---

### ❌ PhaseInstrumentation
- **Status:** MISSING (phantom import)
- **Justification:** Not found in any source files, only imported in tests
- **Evidence:** Grep search returned no class definition
- **Call Sites:**
  - `tests/orchestration/test_resource_limits_integration.py:275`
  - `tests/orchestration/test_resource_limits_regression.py:238`
- **Action:**
  - **DELETE** test assertions that depend on this class
  - **INVESTIGATE** if similar instrumentation exists in core_orchestrator
  - If needed, replace with actual monitoring/instrumentation from core_orchestrator
- **Date:** 2026-01-17

---

### ❌ AbortSignal
- **Status:** MISSING (not found)
- **Justification:** No grep results, possibly phantom or in domain_errors
- **Evidence:** Not found in initial search
- **Call Sites:** 0 (listed in BROKEN_IMPORTS_COMPLETE_LIST.txt but no actual usages found)
- **Action:**
  - **VERIFY** if actually used anywhere
  - If used, check `phase0_00_01_domain_errors` for abort-related errors
  - If not used, no action needed (phantom listing)
- **Date:** 2026-01-17

---

### 🔍 execute_phase_with_timeout
- **Status:** INVESTIGATE
- **Justification:** Function name suggests timeout execution, may exist as method in core_orchestrator
- **Evidence:** Not found as standalone function
- **Call Sites:** Unknown (listed in BROKEN_IMPORTS_COMPLETE_LIST.txt)
- **Action:**
  - **SEARCH** for timeout-related methods in PipelineOrchestrator
  - Likely integrated into orchestrator execution methods
  - May not exist as standalone import
- **Date:** 2026-01-17

---

## Decision Matrix Summary

```
FOUND + REDIRECT:
- MethodExecutor → farfan_pipeline.orchestration.core_orchestrator
- Orchestrator → farfan_pipeline.orchestration.core_orchestrator
- ScoredMicroQuestion → farfan_pipeline.phases.Phase_03.contracts.phase03_output_contract
- MicroQuestionRun → farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter
- ResourceLimits → farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller
- QuestionnaireSignalRegistry → farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry

ALIAS/REPLACE:
- MacroEvaluation → Use MacroScore from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score

INVESTIGATE:
- Evidence → Multiple classes, context-dependent
- execute_phase_with_timeout → May not exist as standalone

DELETE FROM TESTS:
- PhaseInstrumentation → Phantom class, rewrite tests
- AbortSignal → Verify usage, may not actually be used
```

---

## Validation

After remediation, verify:
1. All imports compile without errors
2. Tests pass or are rewritten to assert current behavior
3. No references to `orchestration.orchestrator` remain
4. TYPE_CHECKING blocks use correct canonical paths

---

**Last Updated:** 2026-01-17
**Next Review:** After Phase 5 remediation completion
