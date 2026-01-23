# FARFAN Factory Architecture

## Overview

The FARFAN pipeline uses a **Unified Factory Pattern** to manage all component creation, questionnaire loading, and contract execution. This document describes the factory architecture and the relationship between the deprecated Phase 2 factory and the new UnifiedFactory.

## Factory Components

### UnifiedFactory (Primary)
**Location:** `src/farfan_pipeline/orchestration/factory.py`

The UnifiedFactory is the **single source of truth** for all factory operations in the FARFAN pipeline.

#### Key Features:
- **Questionnaire Loading**: Lazy-loads questionnaires via CQCLoader with 333x performance optimizations
- **Signal Registry**: Creates signal registries from canonical notation
- **Component Creation**: Instantiates detectors, calculators, analyzers
- **Contract Execution**: Loads and executes 300 contracts with method injection
- **SISAS Integration**: Initializes SISAS central for signal distribution
- **Adaptive Caching**: LRU+TTL hybrid cache for performance
- **Parallel Execution**: ThreadPool-based parallel contract execution

#### Core Classes:
```python
class UnifiedFactory:
    """Single unified factory for the FARFAN pipeline."""
    
    def __init__(self, config: FactoryConfig):
        """Initialize with FactoryConfig."""
        
    def load_questionnaire(self) -> Any:
        """Load questionnaire via CQCLoader."""
        
    def create_signal_registry(self) -> Dict[str, Any]:
        """Create signal registry from canonical notation."""
        
    def create_analysis_components(self) -> Dict[str, Any]:
        """Create analysis components (detectors, calculators, etc.)."""
        
    def execute_contract(self, contract_id: str, input_data: Dict) -> Dict:
        """Execute a single contract with method injection."""
        
    def execute_contracts_batch(self, contract_ids: List[str], input_data: Dict) -> Dict:
        """Execute multiple contracts in batch mode."""

@dataclass
class FactoryConfig:
    """Configuration for the unified factory."""
    project_root: Path
    questionnaire_path: Optional[Path] = None
    sisas_enabled: bool = True
    lazy_load_questions: bool = True
    enable_parallel_execution: bool = True
    enable_adaptive_caching: bool = True
```

### Deprecated Phase 2 Factory (Legacy Stub)
**Location:** `src/farfan_pipeline/phases/Phase_02/phase2_10_00_factory.py`

This file is **DEPRECATED** and serves only as a compatibility stub that redirects to UnifiedFactory.

#### Purpose:
- Maintains backward compatibility during migration
- Emits deprecation warnings when used
- Redirects all calls to UnifiedFactory

#### Example:
```python
def load_questionnaire(path: str | Path | None = None) -> Any:
    """
    LEGACY STUB - Redirects to UnifiedFactory.
    DEPRECATED: Use UnifiedFactory.load_questionnaire() instead.
    """
    _emit_deprecation_warning("load_questionnaire")
    from farfan_pipeline.orchestration.factory import get_factory
    
    factory = get_factory()
    return factory.load_questionnaire()
```

## Factory Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPRECATED PHASE 2 FACTORY                   │
│                 (phase2_10_00_factory.py - 243 lines)           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Legacy Functions (Stubs with Deprecation Warnings)       │  │
│  │  - load_questionnaire()        ──────┐                   │  │
│  │  - create_signal_registry()    ──────┤                   │  │
│  │  - create_analysis_components()──────┤  Redirect to      │  │
│  │  - save_json()                 ──────┤  get_factory()    │  │
│  │  - load_json()                 ──────┘                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────┬───────────────────────────┘
                                      │
                                      │ imports & redirects
                                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                       UNIFIED FACTORY                           │
│                  (factory.py - 1760 lines)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    UnifiedFactory                         │  │
│  │  ┌────────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │ Questionnaire  │  │ Signal      │  │ Components   │  │  │
│  │  │ - CQCLoader    │  │ Registry    │  │ - Detectors  │  │  │
│  │  │ - Lazy Load    │  │ - Canonical │  │ - Calculators│  │  │
│  │  │ - Caching      │  │ - Patterns  │  │ - Analyzers  │  │  │
│  │  └────────────────┘  └─────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌────────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │ Contracts      │  │ File I/O    │  │ SISAS        │  │  │
│  │  │ - Load 300     │  │ - JSON      │  │ - Central    │  │  │
│  │  │ - Execute      │  │ - Text      │  │ - Consumers  │  │  │
│  │  │ - Batch        │  │ - Cache     │  │ - Dispatch   │  │  │
│  │  └────────────────┘  └─────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ Performance Infrastructure                          │ │  │
│  │  │ - AdaptiveLRUCache (LRU+TTL hybrid)                │ │  │
│  │  │ - ThreadPoolExecutor (parallel execution)          │ │  │
│  │  │ - Metrics tracking (thread-safe)                   │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FactoryConfig                          │  │
│  │  - project_root, questionnaire_path                      │  │
│  │  - sisas_enabled, lazy_load_questions                    │  │
│  │  - enable_parallel_execution, max_workers                │  │
│  │  - enable_adaptive_caching, cache_ttl_seconds           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Patterns

### Modern Pattern (Recommended)
```python
from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig
from pathlib import Path

# 1. Create configuration
config = FactoryConfig(
    project_root=Path("."),
    sisas_enabled=True,
    enable_parallel_execution=True,
)

# 2. Create factory
factory = UnifiedFactory(config)

# 3. Use factory methods
questionnaire = factory.load_questionnaire()
registry = factory.create_signal_registry()
components = factory.create_analysis_components()

# 4. Execute contracts
contracts = factory.load_contracts()
result = factory.execute_contract("C001", input_data)
```

### Legacy Pattern (Deprecated)
```python
# ⚠️ DEPRECATED - Emits deprecation warnings
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    load_questionnaire,
    create_signal_registry,
)

questionnaire = load_questionnaire()  # ⚠️ Deprecation warning
registry = create_signal_registry()   # ⚠️ Deprecation warning
```

### Singleton Pattern (Convenient)
```python
from farfan_pipeline.orchestration.factory import get_factory

# Get or create factory instance (singleton-like behavior)
factory = get_factory()
questionnaire = factory.load_questionnaire()
```

## Migration Guide

### For Code Using Phase 2 Factory

**Before:**
```python
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
    load_questionnaire,
    create_signal_registry,
    create_contradiction_detector,
)

questionnaire = load_questionnaire()
registry = create_signal_registry()
detector = create_contradiction_detector()
```

**After:**
```python
from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig

factory = UnifiedFactory(config=FactoryConfig(project_root=Path(".")))
questionnaire = factory.load_questionnaire()
registry = factory.create_signal_registry()
components = factory.create_analysis_components()
detector = components["contradiction_detector"]
```

## Factory Audit

The factory can be audited using the audit script:

```bash
python scripts/audit/audit_factory.py
```

### Audit Checks:
1. ✅ Factory File Structure (1760 lines, 4 classes)
2. ✅ Deprecated Factory Stub Relationship
3. ✅ Legacy Signal Loader Deletion
4. ✅ Single Questionnaire Load Point
5. ✅ Method Dispensary Files
6. ✅ Factory Documentation
7. ✅ Factory Pattern Implementation
8. ✅ Dependency Injection
9. ✅ Singleton Pattern Enforcement
10. ✅ Method Dispensary Pattern
11. ⚠️ Security & Integrity (partial)

**Current Status:** 92.3% (12/13 checks passed)

## Performance Features

### Adaptive Caching
- **LRU Eviction**: Removes least recently used items when cache is full
- **TTL Expiration**: Items expire after configurable time-to-live
- **Thread-Safe**: Uses reentrant locks for multi-threaded access
- **Access Tracking**: Tracks access frequency for optimization

### Parallel Execution
- **ThreadPoolExecutor**: Parallel contract execution with configurable workers
- **Batch Processing**: Efficient batch execution of multiple contracts
- **Error Handling**: Graceful degradation on execution failures
- **Metrics Tracking**: Real-time performance metrics

## Related Files

- **Factory Implementation**: `src/farfan_pipeline/orchestration/factory.py`
- **Deprecated Stub**: `src/farfan_pipeline/phases/Phase_02/phase2_10_00_factory.py`
- **Factory Tests**: `tests/test_factory_integration.py`
- **Factory Audit**: `scripts/audit/audit_factory.py`
- **Method Registry**: `src/farfan_pipeline/phases/Phase_02/phase2_10_01_class_registry.py`

## Version History

- **v1.0.0 (2026-01-19)**: Initial UnifiedFactory implementation
- **v1.0.1 (2026-01-23)**: Audit script updated to check UnifiedFactory

## Support

For questions or issues with the factory:
1. Review this documentation
2. Run the factory audit: `python scripts/audit/audit_factory.py`
3. Check test suite: `pytest tests/test_factory_integration.py`
4. Review code in `src/farfan_pipeline/orchestration/factory.py`
