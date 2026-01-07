# Phase 2 Nexus/Carver Parallelization Resolution: Unification Plan

**Document Version:** 1.0
**Date:** 2026-01-07
**Author:** Software Archaeology Team
**Status:** Design Document

---

## Executive Summary

This document presents a comprehensive unification plan for Phase 2 Nexus/Carver validation logic, consolidating parallel implementations into a canonical architecture. The audit identified 37 locations with duplicate validation logic across expected_elements extraction, pattern compilation, and validation rule application.

**Key Metrics:**
- 37+ locations extracting expected_elements from contracts
- 4 parallel pattern compilation methods
- 3 separate validation rule application implementations
- Estimated refactoring scope: ~2,500 lines across 15 files

---

## Part 1: Audit Table - Parallel Logic Locations

### 1.1 Expected Elements Extraction from Contracts

| File | Lines | Current Logic | Replacement API | Priority |
|------|-------|---------------|-----------------|----------|
| `phase2_60_01_contract_validator_cqvr.py` | 307, 421 | `expected_elements = question_context.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | HIGH |
| `phase2_80_00_evidence_nexus.py` | 1028, 2278 | `expected_elements = contract.get("question_context", {}).get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | HIGH |
| `phase2_60_00_base_executor_with_contract.py` | 1054, 1517 | `expected_elements = question_context.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | HIGH |
| `phase2_50_01_task_planner.py` | 305, 406 | `expected_elements = question.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | MEDIUM |
| `phase2_90_00_carver.py` | 743 | `raw_elements = question_context.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | MEDIUM |
| `phase2_50_00_task_executor.py` | 1039, 1076 | `"expected_elements": question_context.expected_elements` | `loader.get_question_complete(question_id)["expected_elements"]` | MEDIUM |
| `phase2_40_03_irrigation_synchronizer.py` | 471, 609, 637 | `expected_elements = question.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | LOW |
| `orchestrator.py` | 2474, 2591 | `"expected_elements": question.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | LOW |
| `analyzer_one.py` | 1578, 2647 | `expected_elements = var/rubric_entry.get("expected_elements", [])` | `loader.get_question_complete(question_id)["expected_elements"]` | LOW |

**Total Locations:** 9 distinct files, 17+ extraction points

### 1.2 Pattern Compilation Methods

| File | Lines | Current Logic | Replacement API | Priority |
|------|-------|---------------|-----------------|----------|
| `policy_processor.py` | 1363-1372 | `_compile_pattern_registry()` - local compilation from `CAUSAL_PATTERN_TAXONOMY` | `PatternResolver.resolve(question_id)` from canonic | HIGH |
| `phase2_60_02_arg_router.py` | 569-574 | Route handler for `_compile_pattern_registry` | Direct import: `from canonic_questionnaire_central import PatternResolver` | HIGH |
| `empirical_extractor_base.py` | N/A | Pattern compilation in `__init__` via `text_processor.compile_pattern()` | `PatternResolver.resolve(question_id)` | MEDIUM |
| `irrigation_synchronizer.py` | N/A | Pattern compilation for signal extraction | `PatternResolver.resolve(question_id)` | MEDIUM |

**Total Locations:** 4 distinct pattern compilation implementations

### 1.3 Validation Rule Application

| File | Lines | Current Logic | Replacement API | Priority |
|------|-------|---------------|-----------------|----------|
| `empirical_extractor_base.py` | 190-208 | `_apply_validation_rule(match, rule)` - handles positive_value, date_range, non_empty | Canonic `validation_rule` structure parsing | HIGH |
| `policy_processor.py` | 1413+ | `_apply_validation_rules(matches, rule_name)` - filters matches through rules | Canonic `validation_rule.rules` iteration | HIGH |
| `phase2_60_01_contract_validator_cqvr.py` | 418-430 | `validation_rules = contract.get("validation_rules", {})` + `rules = validation_rules.get("rules", [])` | Merge with canonic `validation_rule` | HIGH |
| `phase2_80_00_evidence_nexus.py` | 1452-1478 | Extracts `colombian_context` from `contract.validation_rules` | Canonic `context_requirement` + colombia_context.json | HIGH |
| `bayesian_multilevel_system.py` | 78-96 | `ValidationRule` dataclass (validator_type, field_name, expected_range) | Extend to parse canonic validation_rule | MEDIUM |
| `phase2_60_00_base_executor_with_contract.py` | 1930-1961 | `validation_rules_section = contract.get("validation_rules", {})` | Merge with canonic | MEDIUM |

**Total Locations:** 6 distinct validation rule implementations

### 1.4 Context Requirements Gating

| File | Lines | Current Logic | Replacement API | Priority |
|------|-------|---------------|-----------------|----------|
| `phase2_80_00_evidence_nexus.py` | 1488-1549 | `_validate_policy_area_context()` - checks policy_area_id from contract | Canonic `context_requirement.applicability` check | HIGH |
| `signal_enhancement_integrator.py` | 427-431 | `if policy_area_id in validation_rules.get("required_for", [])` | Canonic `context_requirement.applicability` | MEDIUM |
| `phase2_80_00_evidence_nexus.py` | 1512-1530 | Colombian context validation from colombia_context.json | Canonic `context_requirement.applicability` + sections | MEDIUM |

**Total Locations:** 3 distinct context validation implementations

---

## Part 2: Canonical Replacement Strategy

### 2.1 Pattern Resolution Replacement

**Current Implementation (policy_processor.py:1363-1372):**
```python
def _compile_pattern_registry(self) -> dict[CausalDimension, dict[str, list[re.Pattern]]]:
    """Compile all causal patterns into efficient regex objects."""
    registry = {}
    for dimension, categories in CAUSAL_PATTERN_TAXONOMY.items():
        registry[dimension] = {}
        for category, patterns in categories.items():
            registry[dimension][category] = [
                self.text_processor.compile_pattern(p) for p in patterns
            ]
    return registry
```

**Replacement Implementation:**
```python
from canonic_questionnaire_central._scripts.cqc_loader import get_loader
from canonic_questionnaire_central._registry.patterns.pattern_resolver import PatternResolver

class IndustrialPolicyProcessor:
    def __init__(self, *args, **kwargs):
        # ... existing init ...
        self.cqc_loader = get_loader()
        self.pattern_resolver = PatternResolver(self.cqc_loader)

    def get_patterns_for_question(self, question_id: str) -> dict[str, list[re.Pattern]]:
        """
        Resolve patterns from canonic CQC for a specific question.
        Returns compiled patterns by category.
        """
        # Get canonic question
        question = self.cqc_loader.get_question(question_id)
        if not question:
            logger.warning(f"Question {question_id} not found in canonic, using fallback")
            return self._compile_fallback_patterns(question_id)

        # Extract pattern references from canonic question
        pattern_refs = question.get("patterns", [])
        if not pattern_refs:
            return {}

        # Resolve patterns through PatternResolver
        resolved = self.pattern_resolver.resolve(question_id)
        return resolved.get("compiled_patterns", {})

    def _compile_fallback_patterns(self, question_id: str) -> dict[str, list[re.Pattern]]:
        """Fallback to local CAUSAL_PATTERN_TAXONOMY if canonic unavailable."""
        logger.warning(f"Using fallback patterns for {question_id}")
        return self._compile_pattern_registry()  # Original implementation
```

### 2.2 Validation Rules Replacement

**Current Implementation (phase2_60_01_contract_validator_cqvr.py:418-430):**
```python
validation_rules = contract.get("validation_rules", {})
rules = validation_rules.get("rules", [])
# Apply rules locally without canonic integration
```

**Replacement Implementation:**
```python
from canonic_questionnaire_central._scripts.cqc_loader import get_loader

class ContractValidatorCQVR:
    def __init__(self, *args, **kwargs):
        self.cqc_loader = get_loader()

    def load_validation_rules_dual_read(
        self, question_id: str, contract: dict
    ) -> tuple[list[dict], str]:
        """
        Load validation rules with dual-read support.
        Returns: (rules_list, source_used)
        Priority: canonic > contract
        """
        # Try canonic first
        canonic_question = self.cqc_loader.get_question(question_id)
        canonic_rules = None

        if canonic_question:
            canonic_rules = canonic_question.get("validation_rule")
            if canonic_rules:
                logger.info(f"Using canonic validation rules for {question_id}")
                return canonic_rules.get("rules", []), "canonic"

        # Fallback to contract
        contract_rules = contract.get("validation_rules", {}).get("rules", [])
        if contract_rules:
            logger.warning(
                f"Fallback to contract validation rules for {question_id}. "
                f"Add validation_rule to canonic question."
            )
            return contract_rules, "contract_fallback"

        # No rules found
        logger.warning(f"No validation rules found for {question_id}")
        return [], "none"

    def verify_validation_rules(self, contract: dict) -> dict:
        """Verify validation rules with dual-read support."""
        question_context = contract.get("question_context", {})
        question_id = question_context.get("question_id", "")

        # Load rules with source tracking
        rules, source = self.load_validation_rules_dual_read(question_id, contract)

        # Track source for observability
        self._track_validation_source(question_id, source)

        # Apply rules (existing logic)
        score = 0.0
        for rule in rules:
            rule_type = rule.get("type")
            if rule_type == "expected_elements_completeness":
                expected_elements = question_context.get("expected_elements", [])
                # ... existing validation logic ...

        return {"score": score, "source": source}
```

### 2.3 Expected Elements Mapping

**Current Implementation (phase2_80_00_evidence_nexus.py:1028):**
```python
expected_elements = contract.get("question_context", {}).get("expected_elements", [])
```

**Replacement Implementation:**
```python
from canonic_questionnaire_central._scripts.cqc_loader import get_loader
from dataclasses import dataclass
from enum import Enum

class ElementType(Enum):
    CUANTITATIVO = "CUANTITATIVO"
    CUALITATIVO = "CUALITATIVO"
    TEMPORAL = "TEMPORAL"
    FUENTE_OFICIAL = "FUENTE_OFICIAL"

class Importance(Enum):
    CRITICAL = "CRITICAL"
    OPTIONAL = "OPTIONAL"

@dataclass
class ExpectedElement:
    """Canonical expected element structure for Nexus."""
    element_id: str
    element_type: ElementType
    importance: Importance
    synonyms: list[str]
    patterns: list[re.Pattern]
    metadata: dict

class EvidenceNexus:
    def __init__(self, *args, **kwargs):
        self.cqc_loader = get_loader()

    def map_expected_elements(
        self, question_id: str, contract: dict
    ) -> tuple[list[ExpectedElement], str]:
        """
        Map expected elements from canonic to Nexus ExpectedElement format.
        Returns: (expected_elements_list, source_used)
        """
        # Try canonic first
        canonic_question = self.cqc_loader.get_question(question_id)

        if canonic_question:
            canonic_elements = canonic_question.get("expected_elements", [])
            if canonic_elements:
                mapped = [
                    ExpectedElement(
                        element_id=elem.get("type", "unknown"),
                        element_type=self._map_element_type(elem),
                        importance=Importance.CRITICAL if elem.get("required") else Importance.OPTIONAL,
                        synonyms=elem.get("synonyms", []),
                        patterns=self._resolve_element_patterns(elem, question_id),
                        metadata=elem
                    )
                    for elem in canonic_elements
                ]
                logger.info(f"Using canonic expected_elements for {question_id}")
                return mapped, "canonic"

        # Fallback to contract
        contract_elements = contract.get("question_context", {}).get("expected_elements", [])
        if contract_elements:
            logger.warning(f"Fallback to contract expected_elements for {question_id}")
            mapped = [
                ExpectedElement(
                    element_id=elem.get("type", "unknown"),
                    element_type=self._map_element_type(elem),
                    importance=Importance.CRITICAL if elem.get("required") else Importance.OPTIONAL,
                    synonyms=[],
                    patterns=[],
                    metadata=elem
                )
                for elem in contract_elements
            ]
            return mapped, "contract_fallback"

        return [], "none"

    def _map_element_type(self, elem: dict) -> ElementType:
        """Map canonic element type to ElementType enum."""
        elem_type = elem.get("type", "").upper()
        type_mapping = {
            "CUANTITATIVO": ElementType.CUANTITATIVO,
            "CUALITATIVO": ElementType.CUALITATIVO,
            "TEMPORAL": ElementType.TEMPORAL,
            "FUENTE_OFICIAL": ElementType.FUENTE_OFICIAL,
        }
        return type_mapping.get(elem_type, ElementType.CUALITATIVO)

    def _resolve_element_patterns(
        self, elem: dict, question_id: str
    ) -> list[re.Pattern]:
        """Resolve patterns for an expected element from canonic."""
        # Implementation would use PatternResolver
        return []
```

### 2.4 Context Requirement Gating

**Current Implementation (phase2_80_00_evidence_nexus.py:1488-1510):**
```python
def _validate_policy_area_context(
    self, graph: EvidenceGraph, contract: dict[str, Any]
) -> list[ValidationFinding]:
    """Validate evidence against policy-area specific Colombian context."""
    findings = []

    question_context = contract.get("question_context", {})
    identity = contract.get("identity", {})

    # Try multiple field names with fallback
    policy_area_id = (
        question_context.get("policy_area_id")
        or question_context.get("sector_id")
        or identity.get("policy_area_id")
        or identity.get("sector_id", "")
    )
```

**Replacement Implementation:**
```python
from canonic_questionnaire_central._scripts.cqc_loader import get_loader

class EvidenceNexus:
    def __init__(self, *args, **kwargs):
        self.cqc_loader = get_loader()

    def check_context_requirement(
        self, question_id: str, contract: dict
    ) -> tuple[bool, str, SynthesizedAnswer]:
        """
        Check if question is applicable based on context_requirement.
        Returns: (is_applicable, reason, synthesized_answer)
        """
        # Get policy area from contract
        policy_area_id = self._extract_policy_area_id(contract)

        # Get canonic question
        canonic_question = self.cqc_loader.get_question(question_id)

        if not canonic_question:
            # No canonic data, assume applicable
            return True, "no_canonic_data", None

        # Check context_requirement
        context_req = canonic_question.get("context_requirement")
        if not context_req:
            # No context requirement, always applicable
            return True, "no_context_requirement", None

        # Check applicability
        applicability = context_req.get("applicability", [])
        if applicability and policy_area_id not in applicability:
            # Not applicable for this policy area
            reason = f"Question {question_id} not applicable for PA {policy_area_id}. " \
                    f"Required PAs: {applicability}"
            answer = SynthesizedAnswer(
                answer=f"N/A - fuera de aplicabilidad para {policy_area_id}",
                confidence=1.0,
                source="context_requirement_gating",
                metadata={"reason": reason, "applicability": applicability}
            )
            return False, reason, answer

        # Check sections if specified
        required_sections = context_req.get("sections", [])
        if required_sections:
            contract_section = contract.get("identity", {}).get("section", "")
            if contract_section not in required_sections:
                reason = f"Question {question_id} requires section {required_sections}, " \
                        f"got {contract_section}"
                answer = SynthesizedAnswer(
                    answer=f"N/A - sección no aplicable",
                    confidence=1.0,
                    source="context_requirement_gating",
                    metadata={"reason": reason}
                )
                return False, reason, answer

        # Check document types if specified
        required_doc_types = context_req.get("document_types", [])
        if required_doc_types:
            contract_doc_type = contract.get("identity", {}).get("document_type", "")
            if contract_doc_type not in required_doc_types:
                reason = f"Question {question_id} requires doc_type {required_doc_types}"
                answer = SynthesizedAnswer(
                    answer=f"N/A - tipo de documento no aplicable",
                    confidence=1.0,
                    source="context_requirement_gating",
                    metadata={"reason": reason}
                )
                return False, reason, answer

        # All checks passed
        return True, "applicable", None

    def create_evidence_nodes(
        self, question_id: str, contract: dict
    ) -> list[EvidenceNode]:
        """Create evidence nodes with context requirement gating."""
        # Check applicability first
        is_applicable, reason, na_answer = self.check_context_requirement(
            question_id, contract
        )

        if not is_applicable:
            logger.info(f"Skipping evidence node creation for {question_id}: {reason}")
            # Return N/A answer node instead
            return [self._create_na_node(na_answer)]

        # Proceed with normal evidence node creation
        # ... existing logic ...
        return []

    def _extract_policy_area_id(self, contract: dict) -> str:
        """Extract policy area ID from contract with fallbacks."""
        question_context = contract.get("question_context", {})
        identity = contract.get("identity", {})

        return (
            question_context.get("policy_area_id", "")
            or question_context.get("sector_id", "")
            or identity.get("policy_area_id", "")
            or identity.get("sector_id", "")
        )
```

---

## Part 3: Dual-Read Implementation Pattern

### 3.1 Generic Dual-Read Mixin

```python
"""
Dual-Read Backward Compatibility Layer

Provides a generic pattern for reading from both canonic and contract sources
with canonic priority, contract fallback, and observability.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Source of data."""
    CANONIC = "canonic"
    CONTRACT_FALLBACK = "contract_fallback"
    NONE = "none"

@dataclass
class DualReadResult(Generic[TypeVar("T")]):
    """Result of a dual-read operation."""
    data: T
    source: DataSource
    question_id: str
    warnings: list[str]

class DualReadMixin(ABC):
    """
    Mixin providing dual-read capability for Phase 2 components.

    Usage:
        class MyComponent(DualReadMixin):
            def __init__(self):
                self.cqc_loader = get_loader()

            def get_expected_elements(self, question_id, contract):
                return self.dual_read(
                    question_id=question_id,
                    contract=contract,
                    canonic_key="expected_elements",
                    contract_key="question_context.expected_elements",
                    transform=self._transform_elements
                )
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from canonic_questionnaire_central._scripts.cqc_loader import get_loader
        self.cqc_loader = get_loader()
        self._source_tracker = {}

    @abstractmethod
    def transform_canonic(self, data: Any, question_id: str) -> Any:
        """Transform canonic data to component-specific format."""
        pass

    @abstractmethod
    def transform_contract(self, data: Any, question_id: str) -> Any:
        """Transform contract data to component-specific format."""
        pass

    def dual_read(
        self,
        question_id: str,
        contract: dict,
        canonic_key: str,
        contract_key: str,
        default: Any = None,
        transform_canonic: Optional[callable] = None,
        transform_contract: Optional[callable] = None,
    ) -> DualReadResult:
        """
        Perform dual-read with canonic priority and contract fallback.

        Args:
            question_id: Question identifier
            contract: Contract dictionary
            canonic_key: Dot-notation key path in canonic question
            contract_key: Dot-notation key path in contract
            default: Default value if neither source has data
            transform_canonic: Optional transform function for canonic data
            transform_contract: Optional transform function for contract data

        Returns:
            DualReadResult with data, source, and metadata
        """
        warnings = []

        # Try canonic first
        canonic_question = self.cqc_loader.get_question(question_id)
        if canonic_question:
            canonic_data = self._get_nested_key(canonic_question, canonic_key)
            if canonic_data is not None:
                transformed = (
                    (transform_canonic or self.transform_canonic)(
                        canonic_data, question_id
                    )
                    if canonic_data
                    else canonic_data
                )
                self._track_source(question_id, DataSource.CANONIC)
                logger.debug(f"dual_read({question_id}): Using canonic source")
                return DualReadResult(
                    data=transformed,
                    source=DataSource.CANONIC,
                    question_id=question_id,
                    warnings=warnings,
                )

        # Fallback to contract
        contract_data = self._get_nested_key(contract, contract_key)
        if contract_data is not None:
            warnings.append(
                f"Fallback to contract source for {question_id}.{canonic_key}. "
                f"Add data to canonic question."
            )
            transformed = (
                (transform_contract or self.transform_contract)(
                    contract_data, question_id
                )
                if contract_data
                else contract_data
            )
            self._track_source(question_id, DataSource.CONTRACT_FALLBACK)
            logger.warning(f"dual_read({question_id}): Using contract fallback")
            return DualReadResult(
                data=transformed,
                source=DataSource.CONTRACT_FALLBACK,
                question_id=question_id,
                warnings=warnings,
            )

        # No data found
        warnings.append(f"No data found for {question_id}.{canonic_key}")
        self._track_source(question_id, DataSource.NONE)
        logger.warning(f"dual_read({question_id}): No data found")
        return DualReadResult(
            data=default,
            source=DataSource.NONE,
            question_id=question_id,
            warnings=warnings,
        )

    def _get_nested_key(self, data: dict, key_path: str) -> Any:
        """Get nested value from dict using dot-notation key path."""
        keys = key_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _track_source(self, question_id: str, source: DataSource) -> None:
        """Track data source for observability."""
        if question_id not in self._source_tracker:
            self._source_tracker[question_id] = {"canonic_count": 0, "fallback_count": 0}
        if source == DataSource.CANONIC:
            self._source_tracker[question_id]["canonic_count"] += 1
        elif source == DataSource.CONTRACT_FALLBACK:
            self._source_tracker[question_id]["fallback_count"] += 1

    def get_source_statistics(self) -> dict:
        """Get statistics on data source usage."""
        return self._source_tracker.copy()
```

### 3.2 Example Usage in Nexus

```python
class EvidenceNexus(DualReadMixin):
    """Evidence Nexus with dual-read support."""

    def transform_canonic(self, data: Any, question_id: str) -> Any:
        """Transform canonic expected_elements to Nexus format."""
        return [
            ExpectedElement(
                element_id=elem.get("type"),
                element_type=self._map_element_type(elem),
                importance=Importance.CRITICAL if elem.get("required") else Importance.OPTIONAL,
                synonyms=[],
                patterns=[],
                metadata=elem,
            )
            for elem in data
        ]

    def transform_contract(self, data: Any, question_id: str) -> Any:
        """Transform contract expected_elements to Nexus format."""
        return [
            ExpectedElement(
                element_id=elem.get("type"),
                element_type=self._map_element_type(elem),
                importance=Importance.CRITICAL if elem.get("required") else Importance.OPTIONAL,
                synonyms=[],
                patterns=[],
                metadata=elem,
            )
            for elem in data
        ]

    def get_expected_elements(
        self, question_id: str, contract: dict
    ) -> DualReadResult[list[ExpectedElement]]:
        """Get expected elements with dual-read support."""
        return self.dual_read(
            question_id=question_id,
            contract=contract,
            canonic_key="expected_elements",
            contract_key="question_context.expected_elements",
            default=[],
        )
```

---

## Part 4: Deprecation Timeline with CI Gates

### Phase 1: Immediate (Week 0-1)

**Objective:** Add canonic reads alongside contract reads, log both sources

**Actions:**
1. Implement `DualReadMixin` in all Phase 2 components
2. Add canonic data loading for all identified locations
3. Log source usage (canonic vs contract) for each question
4. Add telemetry metrics

**Success Criteria:**
- All 9 files have dual-read capability
- CI gate: `test_dual_read_observability.py` - verify logging works
- CI gate: `test_source_coverage.py` - verify canonic has >= 80% coverage

**CI Gate Implementation:**
```python
# tests/phase_2/test_dual_read_coverage.py
import pytest
from pathlib import Path

def test_canonic_coverage_threshold():
    """
    CI Gate: Ensure canonic questions cover at least 80% of questions used in contracts.
    Fails if coverage < 80%, blocking merge.
    """
    cqc_loader = get_loader()
    all_questions = cqc_loader.load_questionnaire()["blocks"]["micro_questions"]
    canonic_q_ids = {q["question_id"] for q in all_questions}

    # Load test contracts
    test_contracts = load_test_contracts()
    contract_q_ids = set()
    for contract in test_contracts:
        qc = contract.get("question_context", {})
        if "question_id" in qc:
            contract_q_ids.add(qc["question_id"])

    coverage = len(canonic_q_ids & contract_q_ids) / len(contract_q_ids)

    assert coverage >= 0.80, (
        f"Canonic coverage {coverage:.1%} below 80% threshold. "
        f"Add {len(contract_q_ids - canonic_q_ids)} questions to canonic."
    )

    print(f"✓ Canonic coverage: {coverage:.1%}")
```

### Phase 2: Default to Canonic (Week 1-2)

**Objective:** Default to canonic, contract as fallback, emit warnings when fallback used

**Actions:**
1. Change dual-read priority: canonic > contract (already configured)
2. Emit deprecation warnings on each contract fallback
3. Add metrics tracking fallback rate per question
4. Create missing questions in canonic based on fallback data

**Success Criteria:**
- >= 90% of questions use canonic source
- CI gate: `test_fallback_rate_threshold.py` - fail if fallback > 10%
- All missing questions from Phase 1 added to canonic

**CI Gate Implementation:**
```python
# tests/phase_2/test_fallback_rate.py
def test_contract_fallback_rate_threshold():
    """
    CI Gate: Ensure contract fallback rate is below 10%.
    Fails if fallback rate > 10%, indicating incomplete canonic migration.
    """
    # Run test suite and collect source statistics
    nexus = EvidenceNexus()
    # ... run test operations ...

    stats = nexus.get_source_statistics()
    total_reads = sum(
        s["canonic_count"] + s["fallback_count"]
        for s in stats.values()
    )
    total_fallbacks = sum(s["fallback_count"] for s in stats.values())

    fallback_rate = total_fallbacks / total_reads if total_reads > 0 else 0

    assert fallback_rate <= 0.10, (
        f"Contract fallback rate {fallback_rate:.1%} exceeds 10% threshold. "
        f"Complete canonic data migration for {total_fallbacks} questions."
    )

    print(f"✓ Fallback rate: {fallback_rate:.1%}")
```

### Phase 3: Canonic-Only Enforcement (Week 2-3)

**Objective:** Remove contract fallback, enforce canonic-only, fail if canonic data missing

**Actions:**
1. Remove contract fallback code paths
2. Add hard failures for missing canonic data
3. Update all contract test fixtures to include canonic data
4. Remove contract-side expected_elements and validation_rules

**Success Criteria:**
- 0% contract fallback rate
- CI gate: `test_canonic_only.py` - verify no contract paths executed
- All contracts updated to not embed validation data

**CI Gate Implementation:**
```python
# tests/phase_2/test_canonic_only_enforcement.py
def test_no_contract_fallback():
    """
    CI Gate: Ensure NO contract fallback occurs.
    Fails if any contract data is used, enforcing canonic-only architecture.
    """
    nexus = EvidenceNexus()
    # ... run comprehensive test operations ...

    stats = nexus.get_source_statistics()

    for q_id, counts in stats.items():
        assert counts["fallback_count"] == 0, (
            f"Question {q_id} used contract fallback {counts['fallback_count']} times. "
            f"Canonic-only enforcement violation."
        )

    print("✓ Canonic-only enforcement verified")
```

### Phase 4: Cleanup (Week 3-4)

**Objective:** Remove deprecated contract-side code, clean up DualReadMixin

**Actions:**
1. Remove `question_context.expected_elements` from contract schema
2. Remove `contract.validation_rules` from contract schema
3. Replace `DualReadMixin` with direct canonic reads
4. Update documentation

**Success Criteria:**
- Contract schema no longer contains validation metadata
- All Phase 2 components use direct canonic imports
- CI gate: `test_contract_schema_purity.py` - verify contract cleanup

---

## Part 5: Integration Test Cases

### 5.1 PA Mismatch Test (Context Requirement Gating)

```python
# tests/phase_2/test_context_requirement_gating.py
import pytest
from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import EvidenceNexus

@pytest.fixture
def mock_canonic_question():
    """Mock canonic question with context_requirement."""
    return {
        "question_id": "Q-TEST-001",
        "context_requirement": {
            "applicability": ["PA01", "PA05"],
            "sections": ["DIAGNÓSTICO", "LÍNEA BASE"],
            "document_types": ["PDT"]
        },
        "expected_elements": [
            {"type": "indicador", "required": True}
        ]
    }

def test_pa_mismatch_returns_na(mock_canonic_question):
    """
    Test that PA mismatch returns N/A answer with high confidence.
    """
    nexus = EvidenceNexus()
    nexus.cqc_loader.get_question = lambda qid: mock_canonic_question

    contract = {
        "identity": {
            "policy_area_id": "PA10",  # Different from required PA01/PA05
            "section": "DIAGNÓSTICO",
            "document_type": "PDT"
        }
    }

    # Check context requirement
    is_applicable, reason, na_answer = nexus.check_context_requirement(
        "Q-TEST-001", contract
    )

    assert not is_applicable, "Should not be applicable for PA10"
    assert "PA10" in reason
    assert na_answer is not None
    assert "N/A" in na_answer.answer
    assert na_answer.confidence == 1.0
    assert na_answer.source == "context_requirement_gating"

def test_pa_match_proceeds(mock_canonic_question):
    """
    Test that PA match allows evidence node creation.
    """
    nexus = EvidenceNexus()
    nexus.cqc_loader.get_question = lambda qid: mock_canonic_question

    contract = {
        "identity": {
            "policy_area_id": "PA01",  # Matches required
            "section": "DIAGNÓSTICO",
            "document_type": "PDT"
        }
    }

    is_applicable, reason, na_answer = nexus.check_context_requirement(
        "Q-TEST-001", contract
    )

    assert is_applicable, "Should be applicable for PA01"
    assert reason == "applicable"
    assert na_answer is None

def test_section_mismatch_returns_na(mock_canonic_question):
    """
    Test that section mismatch returns N/A answer.
    """
    nexus = EvidenceNexus()
    nexus.cqc_loader.get_question = lambda qid: mock_canonic_question

    contract = {
        "identity": {
            "policy_area_id": "PA01",
            "section": "FORMULACIÓN",  # Different from required DIAGNÓSTICO/LÍNEA BASE
            "document_type": "PDT"
        }
    }

    is_applicable, reason, na_answer = nexus.check_context_requirement(
        "Q-TEST-001", contract
    )

    assert not is_applicable
    assert "sección" in reason.lower()
```

### 5.2 Expected Elements Mapping Test

```python
# tests/phase_2/test_expected_elements_mapping.py
import pytest
from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import EvidenceNexus

def test_canonic_expected_elements_mapping():
    """
    Test that canonic expected_elements map correctly to Nexus ExpectedElement.
    """
    nexus = EvidenceNexus()

    mock_canonic = {
        "question_id": "Q-TEST-002",
        "expected_elements": [
            {"type": "CUANTITATIVO", "required": True},
            {"type": "FUENTE_OFICIAL", "required": False, "minimum": 2}
        ]
    }
    nexus.cqc_loader.get_question = lambda qid: mock_canonic

    elements, source = nexus.map_expected_elements("Q-TEST-002", {})

    assert source == "canonic"
    assert len(elements) == 2

    # Check first element
    assert elements[0].element_id == "CUANTITATIVO"
    assert elements[0].importance.name == "CRITICAL"

    # Check second element
    assert elements[1].element_id == "FUENTE_OFICIAL"
    assert elements[1].importance.name == "OPTIONAL"

def test_contract_fallback_for_expected_elements():
    """
    Test that contract fallback works when canonic unavailable.
    """
    nexus = EvidenceNexus()
    nexus.cqc_loader.get_question = lambda qid: None  # No canonic data

    contract = {
        "question_context": {
            "expected_elements": [
                {"type": "TEMPORAL", "required": True}
            ]
        }
    }

    elements, source = nexus.map_expected_elements("Q-TEST-003", contract)

    assert source == "contract_fallback"
    assert len(elements) == 1
    assert elements[0].element_id == "TEMPORAL"
```

### 5.3 Validation Rule Parsing Test

```python
# tests/phase_2/test_validation_rule_parsing.py
import pytest
from farfan_pipeline.phases.Phase_two.phase2_60_01_contract_validator_cqvr import ContractValidatorCQVR

def test_canonic_validation_rule_parsing():
    """
    Test parsing canonic validation_rule structure.
    """
    validator = ContractValidatorCQVR()

    mock_canonic = {
        "question_id": "Q-TEST-004",
        "validation_rule": {
            "type": "all_of",
            "rules": [
                {
                    "field": "expected_elements",
                    "op": "contains_all",
                    "value": ["indicador", "línea_base"]
                },
                {
                    "field": "signals",
                    "op": "min_confidence",
                    "value": 0.7
                }
            ]
        }
    }
    validator.cqc_loader.get_question = lambda qid: mock_canonic

    rules, source = validator.load_validation_rules_dual_read("Q-TEST-004", {})

    assert source == "canonic"
    assert len(rules) == 2
    assert rules[0]["op"] == "contains_all"
    assert rules[1]["op"] == "min_confidence"

def test_validation_rule_merge():
    """
    Test that canonic and contract rules merge correctly.
    """
    # Implementation would test merging behavior
    pass
```

---

## Part 6: Implementation Checklist

### Phase 1: Foundation (Immediate)

- [ ] Create `DualReadMixin` in `src/farfan_pipeline/phases/Phase_two/dual_read_mixin.py`
- [ ] Add `get_question_complete()` method to `CQCLoader` returning full question with patterns
- [ ] Create `PatternResolver` class in `canonic_questionnaire_central/_registry/patterns/pattern_resolver.py`
- [ ] Implement `_track_source()` logging in DualReadMixin
- [ ] Create `ExpectedElement` dataclass in `phase2_80_00_evidence_nexus.py`
- [ ] Create `ElementType` and `Importance` enums

### Phase 2: Nexus Integration (Week 1)

- [ ] Integrate `DualReadMixin` into `EvidenceNexus`
- [ ] Implement `map_expected_elements()` in Nexus
- [ ] Implement `check_context_requirement()` in Nexus
- [ ] Implement `_parse_canonic_validation_rule()` in Nexus
- [ ] Add context gating to `create_evidence_nodes()`
- [ ] Update `_validate_policy_area_context()` to use canonic

### Phase 3: Carver Integration (Week 1-2)

- [ ] Integrate `DualReadMixin` into `Carver` (phase2_90_00_carver.py)
- [ ] Replace expected_elements extraction at line 743
- [ ] Add pattern resolution via `PatternResolver`
- [ ] Implement validation rule parsing

### Phase 4: Other Phase 2 Components (Week 2)

- [ ] Update `phase2_60_00_base_executor_with_contract.py`
- [ ] Update `phase2_60_01_contract_validator_cqvr.py`
- [ ] Update `phase2_50_01_task_planner.py`
- [ ] Update `phase2_50_00_task_executor.py`
- [ ] Update `phase2_40_03_irrigation_synchronizer.py`

### Phase 5: Policy Processor Refactor (Week 2-3)

- [ ] Replace `_compile_pattern_registry()` in `policy_processor.py`
- [ ] Integrate `PatternResolver.resolve(question_id)`
- [ ] Update `_apply_validation_rules()` to use canonic
- [ ] Remove hardcoded `CAUSAL_PATTERN_TAXONOMY` dependency

### Phase 6: CI Gates & Testing (Week 3)

- [ ] Implement `test_dual_read_coverage.py`
- [ ] Implement `test_fallback_rate_threshold.py`
- [ ] Implement `test_canonic_only_enforcement.py`
- [ ] Implement `test_contract_schema_purity.py`
- [ ] Implement `test_context_requirement_gating.py`
- [ ] Implement `test_expected_elements_mapping.py`
- [ ] Implement `test_validation_rule_parsing.py`

### Phase 7: Cleanup (Week 4)

- [ ] Remove `question_context.expected_elements` from contract schema
- [ ] Remove `contract.validation_rules` from contract schema
- [ ] Replace `DualReadMixin` with direct canonic reads
- [ ] Update all documentation
- [ ] Deprecate contract-side validation logic

---

## Appendix A: File References

### Key Files Modified

1. **`src/farfan_pipeline/phases/Phase_two/dual_read_mixin.py`** (NEW)
   - Generic dual-read implementation

2. **`src/farfan_pipeline/phases/Phase_two/phase2_80_00_evidence_nexus.py`**
   - Lines 1028, 2278: expected_elements extraction
   - Lines 1488-1549: context_requirement gating
   - Add: `map_expected_elements()`, `check_context_requirement()`

3. **`src/farfan_pipeline/phases/Phase_two/phase2_90_00_carver.py`**
   - Line 743: expected_elements extraction
   - Integrate dual-read

4. **`src/farfan_pipeline/phases/Phase_two/phase2_60_01_contract_validator_cqvr.py`**
   - Lines 307, 421: expected_elements extraction
   - Lines 418-430: validation_rules extraction
   - Add: `load_validation_rules_dual_read()`

5. **`src/farfan_pipeline/methods/policy_processor.py`**
   - Lines 1363-1372: `_compile_pattern_registry()`
   - Replace with `PatternResolver.resolve(question_id)`

6. **`canonic_questionnaire_central/_scripts/cqc_loader.py`**
   - Add: `get_question_complete()` method

7. **`canonic_questionnaire_central/_registry/patterns/pattern_resolver.py`** (NEW)
   - Pattern resolution from canonic registry

### Test Files Created

1. `tests/phase_2/test_dual_read_coverage.py`
2. `tests/phase_2/test_fallback_rate.py`
3. `tests/phase_2/test_canonic_only_enforcement.py`
4. `tests/phase_2/test_contract_schema_purity.py`
5. `tests/phase_2/test_context_requirement_gating.py`
6. `tests/phase_2/test_expected_elements_mapping.py`
7. `tests/phase_2/test_validation_rule_parsing.py`

---

## Appendix B: Rollback Plan

If issues arise during migration:

1. **Feature Flags:** Add `USE_CANONIC_VALIDATION` environment variable
   ```python
   USE_CANONIC = os.getenv("USE_CANONIC_VALIDATION", "true").lower() == "true"
   ```

2. **Revert Strategy:**
   - Set `USE_CANONIC_VALIDATION=false` to disable canonic reads
   - All components fall back to contract-based logic
   - No deployment required (environment variable change)

3. **Monitoring:**
   - Track `source_tracker` metrics
   - Alert if fallback rate > 20%
   - Alert if error rate increases post-deployment

---

**End of Document**
