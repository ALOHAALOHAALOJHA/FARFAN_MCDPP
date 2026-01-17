"""
Module: phase2_10_00_factory
PHASE_LABEL: Phase 2
Sequence: W

"""
from __future__ import annotations

"""
Factory module — canonical Dependency Injection (DI) and access control for F.A.R.F.A.N. 

This module is the SINGLE AUTHORITATIVE BOUNDARY for:
- Canonical monolith access (CanonicalQuestionnaire) - loaded ONCE with integrity verification
- Signal registry construction (QuestionnaireSignalRegistry v2.0) from canonical source ONLY
- Method injection via MethodExecutor with signal registry DI
- Orchestrator construction with full DI (questionnaire, method_executor, executor_config)
- EnrichedSignalPack creation and injection per executor (30 executors)
- Hard contracts and validation constants for Phase 1
- SeedRegistry singleton initialization for determinism

METHOD DISPENSARY PATTERN - Core Architecture:
==============================================

The pipeline uses a "method dispensary" pattern where monolithic analyzer classes
serve as "dispensaries" that provide methods to executors. This architecture enables:

1. LOOSE COUPLING: Executors orchestrate methods without direct imports
2. PARTIAL REUSE: Same method used by multiple executors with different contexts
3. CENTRALIZED MANAGEMENT: All method routing through MethodExecutor with validation
4. SIGNAL AWARENESS: Methods receive signal packs for pattern matching

Dispensary Registry (~20 monolith classes, 240+ methods):
---------------------------------------------------------
- IndustrialPolicyProcessor (17 methods): Pattern matching, evidence extraction
- PDETMunicipalPlanAnalyzer (52+ methods): LARGEST - financial, causal, entity analysis
- CausalExtractor (28 methods): Goal extraction, causal hierarchy, semantic distance
- FinancialAuditor (13 methods): Budget tracing, allocation gaps, sufficiency
- BayesianMechanismInference (14 methods): Necessity/sufficiency tests, coherence
- BayesianCounterfactualAuditor (9 methods): SCM construction, refutation
- TextMiningEngine (8 methods): Critical link diagnosis, intervention generation
- SemanticAnalyzer (12 methods): Semantic cube, domain classification
- PerformanceAnalyzer (5 methods): Performance metrics, loss functions
- PolicyContradictionDetector (8 methods): Contradiction detection, coherence
- [... 10+ more classes]

Executor Usage Pattern:
----------------------
Each of 30 executors uses a UNIQUE COMBINATION of methods:
- D1-Q1 (QuantitativeBaselineExtractor): 17 methods from 9 classes
- D3-Q2 (TargetProportionalityAnalyzer): 24 methods from 7 classes
- D3-Q5 (OutputOutcomeLinkageAnalyzer): 28 methods from 6 classes
- D6-Q3 (ValidationTestingAnalyzer): 8 methods from 4 classes

Methods are orchestrated via:
```python
result = self.method_executor.execute(
    class_name="PDETMunicipalPlanAnalyzer",
    method_name="_score_indicators",
    document=doc,
    signal_pack=pack,
    **context
)
```

NOT ALL METHODS ARE USED:
- Monoliths contain more methods than executors need
- Only methods in executors_methods.json are actively used
- Phase 1 (ingestion) uses additional methods not in executor contracts
- 14 methods in validation failures (deprecated/private)

Design Principles (Factory Pattern + DI):
=========================================

1. FACTORY PATTERN: AnalysisPipelineFactory is the ONLY place that instantiates:
   - Orchestrator, MethodExecutor, QuestionnaireSignalRegistry, BaseExecutor instances
   - NO other module should directly instantiate these classes
   
2. DEPENDENCY INJECTION: All components receive dependencies via __init__:
   - Orchestrator receives: questionnaire, method_executor, executor_config, validation_constants
   - MethodExecutor receives: method_registry, arg_router, signal_registry
   - BaseExecutor (30 classes) receive: enriched_signal_pack, method_executor, config
   
3. CANONICAL MONOLITH CONTROL:
   - load_questionnaire() called ONCE by factory only (singleton + integrity hash)
   - Orchestrator uses self.questionnaire object, NEVER file paths
   - Search codebase: NO other load_questionnaire() calls should exist
   
4. SIGNAL REGISTRY CONTROL:
   - create_signal_registry(questionnaire) - from canonical source ONLY
   - signal_loader.py MUST BE DELETED (legacy JSON loaders eliminated)
   - Registry injected into MethodExecutor, NOT accessed globally
   
5. ENRICHED SIGNAL PACK INJECTION:
   - Factory builds EnrichedSignalPack per executor (semantic expansion + context filtering)
   - Each BaseExecutor receives its specific pack, NOT full registry
   
6. DETERMINISM:
   - SeedRegistry singleton initialized by factory for reproducibility
   - ExecutorConfig encapsulates operational params (max_tokens, retries)
   
7. PHASE 1 HARD CONTRACTS:
   - Validation constants (P01_EXPECTED_CHUNK_COUNT=60, etc.) loaded by factory
   - Injected into Orchestrator for Phase 1 chunk validation
   - Execution FAILS if contracts violated

8. PHASE 0 INTEGRATION:
   - RuntimeConfig loaded from environment (or passed explicitly)
   - Phase 0 boot checks validate system dependencies
   - Phase 0 exit gates (7 gates) ensure all prerequisites are met
   - Phase0ValidationResult passed to Orchestrator for runtime validation
   - Factory controls Phase 0 execution via run_phase0_validation parameter

Phase 0 Sequence (when run_phase0_validation=True):
    P0.0: Bootstrap (RuntimeConfig.from_env(), SeedRegistry initialization)
    P0.1: Input Verification (SHA256 hashes of PDF and questionnaire)
    P0.2: Boot Checks (Python version, packages, calibration files)
    P0.3: Determinism (RNG seeding: random, numpy mandatory)
    Exit Gates: 7 gates checked (bootstrap, input_verification, boot_checks,
                 determinism, questionnaire_integrity, method_registry, smoke_tests)

Factory Usage:
    # With Phase 0 validation (recommended for production)
    factory = AnalysisPipelineFactory(
        questionnaire_path="path/to/questionnaire.json",
        run_phase0_validation=True,  # Run Phase 0 before orchestrator creation
        strict_validation=True,
    )

    # Without Phase 0 (for testing/development)
    factory = AnalysisPipelineFactory(
        questionnaire_path="path/to/questionnaire.json",
        run_phase0_validation=False,
    )

SIN_CARRETA Compliance:
- All construction paths emit structured telemetry with timestamps and hashes
- Determinism enforced via explicit validation of canonical questionnaire integrity
- Contract assertions guard all factory outputs (no silent degradation)
- Auditability via immutable ProcessorBundle with provenance metadata
- Phase 0 validation ensures system readiness before pipeline execution
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

# Phase 2 orchestration components
from farfan_pipeline.phases.Phase_02.phase2_60_02_arg_router import ExtendedArgRouter
from orchestration.class_registry import build_class_registry, get_class_paths
from farfan_pipeline.phases.Phase_02.phase2_10_03_executor_config import ExecutorConfig
from farfan_pipeline.phases.Phase_02.phase2_60_00_base_executor_with_contract import BaseExecutorWithContract

# Core orchestration
if TYPE_CHECKING:
    from orchestration.orchestrator import MethodExecutor, Orchestrator
from orchestration.method_registry import (
    MethodRegistry,
    setup_default_instantiation_rules,
)

# Canonical method injection (direct method access, no class instantiation)
from farfan_pipeline.phases.Phase_02.phase2_10_02_methods_registry import (
    inject_canonical_methods,
)

# SISAS - Signal Intelligence Layer (Nivel 2)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_intelligence_layer import (
    EnrichedSignalPack,
    create_enriched_signal_pack,
)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    QuestionnaireSignalRegistry,
    create_signal_registry,
)

# Phase 1 validation constants module
# NOTE: validation_constants module does not exist in current architecture
# Using empty fallback - implement in future JOBFRONT if needed
PHASE1_VALIDATION_CONSTANTS: dict[str, Any] = {}
VALIDATION_CONSTANTS_AVAILABLE = False

# =============================================================================
# EPISTEMIC CALIBRATION REGISTRY (FASE 4: WIRING)
# =============================================================================

# Import calibration registry for epistemic level calibration
from farfan_pipeline.calibration.registry import (
    EpistemicCalibrationRegistry,
    CalibrationResolutionError,
    create_registry,
    MockPDMProfile,
)

CALIBRATION_REGISTRY_AVAILABLE = True

def load_validation_constants() -> dict[str, Any]:
    """Stub for validation constants loading (module not yet implemented)."""
    return PHASE1_VALIDATION_CONSTANTS

# Optional: CoreModuleFactory for I/O helpers
# NOTE: CoreModuleFactory does not exist in current architecture
CoreModuleFactory = None
CORE_MODULE_FACTORY_AVAILABLE = False

# SeedRegistry for determinism
from orchestration.seed_registry import SeedRegistry
SEED_REGISTRY_AVAILABLE = True

# CP-0.1 & CP-0.2: Phase 1 Validation
from farfan_pipeline.validators.phase1_output_validator import Phase1OutputValidator
from farfan_pipeline.core.types import PreprocessedDocument

# Phase 0 integration
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    get_runtime_config,
)
from farfan_pipeline.phases.Phase_zero.phase0_90_01_verified_pipeline_runner import (
    VerifiedPipelineRunner,
)
from farfan_pipeline.phases.Phase_zero.phase0_50_01_exit_gates import (
    check_all_gates,
)

logger = logging.getLogger(__name__)


# ============================================================================
# CANONICAL QUESTIONNAIRE RESOLVER - NIVEL 1
# Uses modular resolver instead of monolithic file
# Según AGENTS.md - Migrated to modular architecture per SISAS 2.0
# ============================================================================
_REPO_ROOT = Path(__file__).resolve().parents[2]
# DEPRECATED: CANONICAL_QUESTIONNAIRE_PATH = _REPO_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"
# NEW: Use CanonicalQuestionnaireResolver for modular assembly
# Import CanonicalQuestionnaire from modular resolver (SISAS 2.0)
from canonic_questionnaire_central.resolver import (
    CanonicalQuestionnaire,
    QuestionnairePort,
    ResolverError,
)


class QuestionnaireLoadError(Exception):
    """Error al cargar el cuestionario."""
    pass


class QuestionnaireIntegrityError(QuestionnaireLoadError):
    """Hash del cuestionario no coincide."""
    pass


def load_questionnaire(
    expected_hash: str | None = None,
    force_rebuild: bool = False,
) -> CanonicalQuestionnaire:
    """
    Carga el cuestionario canónico usando el resolver modular.

    NIVEL 1: ÚNICA función autorizada para assembly del questionnaire.
    CONSUMIDOR: Solo AnalysisPipelineFactory._load_canonical_questionnaire

    REFACTORED (2026-01-17): Migrated from monolithic file loading to modular resolver.
    Now uses canonic_questionnaire_central.resolver.CanonicalQuestionnaireResolver
    which assembles from granular components (dimensions/, policy_areas/, etc.)

    Args:
        expected_hash: Hash SHA256 esperado para verificación (optional)
        force_rebuild: If True, bypass cache and rebuild from modular sources

    Returns:
        CanonicalQuestionnaire: Objeto inmutable verificado from modular assembly

    Raises:
        QuestionnaireLoadError: Si el assembly falla
        QuestionnaireIntegrityError: Si hash no coincide
    """
    try:
        # Import modular resolver
        from canonic_questionnaire_central.resolver import (
            CanonicalQuestionnaireResolver,
            AssemblyError,
            IntegrityError as ResolverIntegrityError,
        )
        
        # Initialize resolver
        resolver = CanonicalQuestionnaireResolver(
            root=_REPO_ROOT / "canonic_questionnaire_central",
            strict_mode=True,
            cache_enabled=True,
            sdo_enabled=True,  # Enable SISAS 2.0 Signal Distribution Orchestrator
        )
        
        # Resolve questionnaire from modular sources
        questionnaire = resolver.resolve(
            expected_hash=expected_hash,
            force_rebuild=force_rebuild,
        )
        
        logger.info(
            "questionnaire_loaded_via_modular_resolver",
            sha256=questionnaire.sha256[:16],
            version=questionnaire.version,
            source=questionnaire.source,
            question_count=len(questionnaire.micro_questions),
            assembly_duration_ms=questionnaire.provenance.assembly_duration_ms,
        )
        
        return questionnaire
        
    except ResolverIntegrityError as e:
        raise QuestionnaireIntegrityError(str(e)) from e
    except AssemblyError as e:
        raise QuestionnaireLoadError(f"Modular assembly failed: {e}") from e
    except Exception as e:
        raise QuestionnaireLoadError(
            f"Unexpected error loading questionnaire via resolver: {e}"
        ) from e


# =============================================================================
# Exceptions
# =============================================================================


class FactoryError(Exception):
    """Base exception for factory construction failures."""
    pass


class QuestionnaireValidationError(FactoryError):
    """Raised when questionnaire validation fails."""
    pass


class IntegrityError(FactoryError):
    """Raised when questionnaire integrity check (SHA-256) fails."""
    pass


class RegistryConstructionError(FactoryError):
    """Raised when signal registry construction fails."""
    pass


class ExecutorConstructionError(FactoryError):
    """Raised when method executor construction fails."""
    pass


class SingletonViolationError(FactoryError):
    """Raised when singleton pattern is violated."""
    pass


# =============================================================================
# Processor Bundle (typed DI container with provenance)
# =============================================================================


@dataclass(frozen=True)
class ProcessorBundle:
    """Aggregated orchestrator dependencies built by the Factory.

    This is the COMPLETE DI container returned by AnalysisPipelineFactory.

    Attributes:
        orchestrator: Fully configured Orchestrator (main entry point).
        method_executor: MethodExecutor with signal registry injected.
        questionnaire: Immutable, validated CanonicalQuestionnaire (monolith).
        signal_registry: QuestionnaireSignalRegistry v2.0 from canonical source.
        executor_config: ExecutorConfig for operational parameters.
        enriched_signal_packs: Dict of EnrichedSignalPack per policy area.
        validation_constants: Phase 1 hard contracts (chunk counts, etc.).
        calibration_registry: EpistemicCalibrationRegistry for level calibration (FASE 4.1).
        pdm_profile: PDM structural profile for dynamic calibration (FASE 4.1).
        core_module_factory: Optional CoreModuleFactory for I/O helpers.
        seed_registry_initialized: Whether SeedRegistry singleton was set up.
        provenance: Construction metadata for audit trails.
    """

    orchestrator: Orchestrator
    method_executor: MethodExecutor
    questionnaire: CanonicalQuestionnaire
    signal_registry: QuestionnaireSignalRegistry
    executor_config: ExecutorConfig
    enriched_signal_packs: dict[str, EnrichedSignalPack]
    validation_constants: dict[str, Any]
    calibration_registry: Any | None = None  # FASE 4.1: EpistemicCalibrationRegistry
    pdm_profile: Any | None = None  # FASE 4.1: MockPDMProfile
    core_module_factory: Any | None = None
    seed_registry_initialized: bool = False
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """SIN_CARRETA § Contract Enforcement: validate bundle integrity."""
        errors = []

        # Critical components validation
        if self.orchestrator is None:
            errors.append("orchestrator must not be None")
        if self.method_executor is None:
            errors.append("method_executor must not be None")
        if self.questionnaire is None:
            errors.append("questionnaire must not be None")
        if self.signal_registry is None:
            errors.append("signal_registry must not be None")
        if self.executor_config is None:
            errors.append("executor_config must not be None")
        if self.enriched_signal_packs is None:
            errors.append("enriched_signal_packs must not be None")
        elif not isinstance(self.enriched_signal_packs, dict):
            errors.append("enriched_signal_packs must be dict[str, EnrichedSignalPack]")

        if self.validation_constants is None:
            errors.append("validation_constants must not be None")

        # Provenance validation
        if not self.provenance.get("construction_timestamp_utc"):
            errors.append("provenance must include construction_timestamp_utc")
        if not self.provenance.get("canonical_sha256"):
            errors.append("provenance must include canonical_sha256")
        if self.provenance.get("signal_registry_version") != "2.0":
            errors.append("provenance must indicate signal_registry_version=2.0")

        # Factory pattern enforcement check
        if not self.provenance.get("factory_instantiation_confirmed"):
            errors.append("provenance must confirm factory instantiation (not direct construction)")

        if errors:
            raise FactoryError(f"ProcessorBundle validation failed: {'; '.join(errors)}")

        logger.info(
            "processor_bundle_validated "
            "canonical_sha256=%s construction_ts=%s policy_areas=%d validation_constants=%d",
            self.provenance.get("canonical_sha256", "")[:16],
            self.provenance.get("construction_timestamp_utc"),
            len(self.enriched_signal_packs),
            len(self.validation_constants),
        )


# =============================================================================
# Analysis Pipeline Factory (Main Factory Class)
# =============================================================================


class AnalysisPipelineFactory:
    """Factory for constructing the complete analysis pipeline.
    
    This is the ONLY class that should instantiate:
    - Orchestrator
    - MethodExecutor  
    - QuestionnaireSignalRegistry
    - BaseExecutor instances (30 executor classes)
    
    CRITICAL: No other module should directly instantiate these classes.
    All dependencies are injected via constructor parameters.
    
    Usage:
        factory = AnalysisPipelineFactory(
            questionnaire_path="path/to/questionnaire.json",
            expected_hash="abc123...",
            seed=42
        )
        bundle = factory.create_orchestrator()
        orchestrator = bundle.orchestrator
    """

    # Singleton tracking for load_questionnaire() call
    _questionnaire_loaded = False
    _questionnaire_instance: CanonicalQuestionnaire | None = None

    def __init__(
        self,
        *,
        questionnaire_path: str | None = None,
        expected_questionnaire_hash: str | None = None,
        runtime_config: RuntimeConfig | None = None,
        executor_config: ExecutorConfig | None = None,
        validation_constants: dict[str, Any] | None = None,
        enable_intelligence_layer: bool = True,
        seed_for_determinism: int | None = None,
        strict_validation: bool = True,
        run_phase0_validation: bool = True,
    ):
        """Initialize the Analysis Pipeline Factory.

        Args:
            questionnaire_path: Path to canonical questionnaire JSON.
            expected_questionnaire_hash: Expected SHA-256 hash for integrity check.
            runtime_config: Optional RuntimeConfig (defaults to from_env() if None).
            executor_config: Custom executor configuration (if None, uses default).
            validation_constants: Phase 1 validation constants (if None, loads from config).
            enable_intelligence_layer: Whether to build enriched signal packs.
            seed_for_determinism: Seed for SeedRegistry singleton.
            strict_validation: If True, fail on any validation error.
            run_phase0_validation: If True, run Phase 0 boot checks and exit gates.
        """
        self._questionnaire_path = questionnaire_path
        self._expected_hash = expected_questionnaire_hash
        self._executor_config = executor_config
        self._validation_constants = validation_constants
        self._enable_intelligence = enable_intelligence_layer
        self._seed = seed_for_determinism
        self._strict = strict_validation
        self._run_phase0 = run_phase0_validation

        # Initialize RuntimeConfig (load from env if not provided)
        if runtime_config is None:
            try:
                self._runtime_config = get_runtime_config()
                logger.info(
                    "factory_runtime_config_loaded mode=%s",
                    self._runtime_config.mode.value
                )
            except Exception as e:
                if run_phase0_validation:
                    raise FactoryError(
                        f"Failed to load RuntimeConfig and Phase 0 validation requested: {e}"
                    ) from e
                # In non-Phase0 mode, continue without RuntimeConfig
                self._runtime_config = None
                logger.warning("factory_runtime_config_not_loaded phase0_disabled")
        else:
            self._runtime_config = runtime_config

        # Internal state (set during construction)
        self._canonical_questionnaire: CanonicalQuestionnaire | None = None
        self._signal_registry: QuestionnaireSignalRegistry | None = None
        self._method_executor: MethodExecutor | None = None
        self._enriched_packs: dict[str, EnrichedSignalPack] = {}

        # FASE 4.1: Initialize Calibration Registry (Epistemic Level Calibration)
        self._calibration_registry: EpistemicCalibrationRegistry | None = None
        self._pdm_profile: MockPDMProfile | None = None

        logger.info(
            "factory_initialized questionnaire_path=%s intelligence_layer=%s seed=%s calibration_enabled=%s",
            questionnaire_path or "default",
            enable_intelligence_layer,
            seed_for_determinism is not None,
            CALIBRATION_REGISTRY_AVAILABLE,
        )

    def create_orchestrator(self) -> ProcessorBundle:
        """Create fully configured Orchestrator with all dependencies injected.
        
        This is the PRIMARY ENTRY POINT for the factory.
        Returns a complete ProcessorBundle with Orchestrator ready to use.
        
        Returns:
            ProcessorBundle: Immutable bundle with all dependencies wired.
            
        Raises:
            QuestionnaireValidationError: If questionnaire validation fails.
            IntegrityError: If questionnaire hash doesn't match expected.
            RegistryConstructionError: If signal registry construction fails.
            ExecutorConstructionError: If method executor construction fails.
        """
        construction_start = time.time()
        timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        logger.info("factory_create_orchestrator_start timestamp=%s", timestamp_utc)

        try:
            # Step 0: Run Phase 0 validation (boot checks + exit gates)
            phase0_validation = None
            if self._run_phase0:
                phase0_validation = self._run_phase0_validation()
                logger.info(
                    "factory_phase0_complete passed=%s",
                    phase0_validation.all_passed
                )

            # Step 1: Load canonical questionnaire (ONCE, with integrity check)
            self._load_canonical_questionnaire()

            # Step 2: Build signal registry from canonical source
            self._build_signal_registry()

            # Step 2.5: FASE 4.1 - Initialize Calibration Registry (Epistemic Level Calibration)
            self._initialize_calibration_registry()

            # Step 3: Build enriched signal packs (intelligence layer)
            self._build_enriched_signal_packs()

            # Step 4: Initialize seed registry for determinism
            seed_initialized = self._initialize_seed_registry()

            # Step 5: Build method executor with signal registry DI
            self._build_method_executor()

            # Step 6: Load Phase 1 validation constants
            validation_constants = self._load_validation_constants()

            # Step 7: Get or create executor config
            executor_config = self._get_executor_config()

            # Step 8: Build orchestrator with full DI
            orchestrator = self._build_orchestrator(
                executor_config=executor_config,
                runtime_config=self._runtime_config,
                phase0_validation=phase0_validation,
            )

            # Step 9: Assemble provenance metadata
            construction_duration = time.time() - construction_start
            canonical_hash = self._compute_questionnaire_hash()

            provenance = {
                "construction_timestamp_utc": timestamp_utc,
                "canonical_sha256": canonical_hash,
                "signal_registry_version": "2.0",
                "intelligence_layer_enabled": self._enable_intelligence,
                "enriched_packs_count": len(self._enriched_packs),
                "validation_constants_count": len(validation_constants),
                "construction_duration_seconds": round(construction_duration, 3),
                "seed_registry_initialized": seed_initialized,
                "core_module_factory_available": CORE_MODULE_FACTORY_AVAILABLE,
                "strict_validation": self._strict,
                "factory_instantiation_confirmed": True,  # Critical for bundle validation
                "factory_class": "AnalysisPipelineFactory",
                # Phase 0 metadata
                "phase0_validation_ran": self._run_phase0,
                "phase0_validation_passed": phase0_validation.all_passed if phase0_validation else None,
                "phase0_gate_count": len(phase0_validation.gate_results) if phase0_validation else 0,
                "runtime_mode": self._runtime_config.mode.value if self._runtime_config else None,
                # FASE 4.1: Calibration metadata
                "calibration_registry_available": self._calibration_registry is not None,
                "calibration_method_levels": len(self._calibration_registry.method_level_map) if self._calibration_registry else 0,
                "calibration_type_configs": len(self._calibration_registry.type_overrides) if self._calibration_registry else 0,
                "pdm_profile_available": self._pdm_profile is not None,
                "pdm_profile_hierarchy_depth": getattr(self._pdm_profile, "hierarchy_depth", None) if self._pdm_profile else None,
                "pdm_profile_financial": getattr(self._pdm_profile, "contains_financial_data", None) if self._pdm_profile else None,
            }

            # Step 10: Build complete bundle
            bundle = ProcessorBundle(
                orchestrator=orchestrator,
                method_executor=self._method_executor,
                questionnaire=self._canonical_questionnaire,
                signal_registry=self._signal_registry,
                executor_config=executor_config,
                enriched_signal_packs=self._enriched_packs,
                validation_constants=validation_constants,
                calibration_registry=self._calibration_registry,  # FASE 4.1
                pdm_profile=self._pdm_profile,  # FASE 4.1
                core_module_factory=self._build_core_module_factory(),
                seed_registry_initialized=seed_initialized,
                provenance=provenance,
            )

            logger.info(
                "factory_create_orchestrator_complete duration=%.3fs hash=%s",
                construction_duration,
                canonical_hash[:16],
            )

            return bundle

        except Exception as e:
            logger.error("factory_create_orchestrator_failed error=%s", str(e), exc_info=True)
            raise FactoryError(f"Failed to create orchestrator: {e}") from e

    def validate_phase1_handoff(self, doc: PreprocessedDocument, artifacts_path: Path | None = None) -> bool:
        """
        CP-0.1 & CP-0.2: Validates the handoff from Phase 1.
        
        Args:
            doc: The PreprocessedDocument to validate.
            artifacts_path: Optional path to artifacts directory for manifest validation.
            
        Returns:
            bool: True if validation passes, False otherwise.
        """
        logger.info("phase1_handoff_validation_start document_id=%s", doc.document_id)
        
        # 1. Validate Document Structure (Matrix 60x6)
        matrix_result = Phase1OutputValidator.validate_matrix_coordinates(doc)
        if not matrix_result.is_valid:
            logger.error(
                "phase1_handoff_validation_failed matrix_errors=%s",
                matrix_result.errors
            )
            if self._strict:
                return False
        else:
             logger.info(
                "phase1_matrix_validation_passed score=%.2f%% integrity_hash=%s",
                matrix_result.matrix_completeness_score,
                matrix_result.integrity_hash
            )

        # 2. Validate Manifest (if path provided)
        if artifacts_path:
            manifest_valid = Phase1OutputValidator.validate_phase1_manifest(artifacts_path)
            if not manifest_valid:
                 logger.error("phase1_manifest_validation_failed")
                 if self._strict:
                     return False
            else:
                logger.info("phase1_manifest_validation_passed")
        
        return True

    def get_calibration_registry(self) -> EpistemicCalibrationRegistry | None:
        """Get the epistemic calibration registry (FASE 4.1).

        Returns:
            EpistemicCalibrationRegistry if initialized, else None.

        Usage:
            factory = AnalysisPipelineFactory(...)
            bundle = factory.create_orchestrator()
            registry = factory.get_calibration_registry()

            # Resolve calibration for a method
            calibration = registry.resolve_calibration(
                method_id="PDETMunicipalPlanAnalyzer._score_indicators",
                contract_type="TYPE_A",
                pdm_profile=bundle.pdm_profile,
            )
        """
        return self._calibration_registry

    def extract_pdm_profile(
        self,
        doc: PreprocessedDocument | None = None,
    ) -> MockPDMProfile:
        """Extract PDM structural profile from PreprocessedDocument (FASE 4.1).

        This is a public API for extracting PDM profiles that can be called
        externally. It wraps the internal _extract_pdm_profile_from_cpp method.

        Args:
            doc: Optional PreprocessedDocument to analyze. If None, returns default profile.

        Returns:
            MockPDMProfile with extracted structural characteristics.

        Usage:
            factory = AnalysisPipelineFactory(...)
            pdm_profile = factory.extract_pdm_profile(preprocessed_document)
        """
        return self._extract_pdm_profile_from_cpp(doc)

    # =========================================================================
    # Internal Construction Methods
    # =========================================================================

    def _load_canonical_questionnaire(self) -> None:
        """Load canonical questionnaire with singleton enforcement and integrity check.
        
        CRITICAL REQUIREMENTS:
        1. This is the ONLY place in the codebase that calls load_questionnaire()
        2. Must enforce singleton pattern (only load once)
        3. Must verify SHA-256 hash for integrity
        4. Must raise IntegrityError if hash doesn't match
        
        Raises:
            SingletonViolationError: If load_questionnaire() already called.
            IntegrityError: If questionnaire hash doesn't match expected.
            QuestionnaireValidationError: If questionnaire structure invalid.
        """
        # Enforce singleton pattern
        if AnalysisPipelineFactory._questionnaire_loaded:
            if AnalysisPipelineFactory._questionnaire_instance is not None:
                logger.info("questionnaire_singleton_reused using_cached_instance")
                self._canonical_questionnaire = AnalysisPipelineFactory._questionnaire_instance
                return
            else:
                raise SingletonViolationError(
                    "load_questionnaire() was called but instance is None. "
                    "This indicates a singleton pattern violation."
                )

        logger.info("questionnaire_loading_start path=%s", self._questionnaire_path or "default")

        try:
            # Load questionnaire (this should be the ONLY call in the entire codebase)
            questionnaire = load_questionnaire(self._questionnaire_path)

            # Mark singleton as loaded
            AnalysisPipelineFactory._questionnaire_loaded = True
            AnalysisPipelineFactory._questionnaire_instance = questionnaire

            # Compute integrity hash
            actual_hash = self._compute_questionnaire_hash_from_instance(questionnaire)

            # Verify integrity if expected hash provided
            if self._expected_hash is not None:
                if actual_hash != self._expected_hash:
                    raise IntegrityError(
                        f"Questionnaire integrity check FAILED. "
                        f"Expected: {self._expected_hash[:16]}... "
                        f"Actual: {actual_hash[:16]}... "
                        f"The canonical questionnaire may have been tampered with."
                    )
                logger.info("questionnaire_integrity_verified hash=%s", actual_hash[:16])
            else:
                logger.warning(
                    "questionnaire_integrity_not_verified no_expected_hash_provided "
                    "actual_hash=%s",
                    actual_hash[:16]
                )

            # Validate structure
            if not hasattr(questionnaire, 'questions'):
                if self._strict:
                    raise QuestionnaireValidationError("Questionnaire missing 'questions' attribute")
                logger.warning("questionnaire_validation_warning missing_questions_attribute")

            questions = getattr(questionnaire, 'questions', [])
            if not questions:
                if self._strict:
                    raise QuestionnaireValidationError("Questionnaire has no questions")
                logger.warning("questionnaire_validation_warning no_questions")

            self._canonical_questionnaire = questionnaire

            logger.info(
                "questionnaire_loaded_successfully questions=%d hash=%s singleton=established",
                len(questions),
                actual_hash[:16],
            )

        except Exception as e:
            if isinstance(e, (IntegrityError, SingletonViolationError, QuestionnaireValidationError)):
                raise
            raise QuestionnaireValidationError(f"Failed to load questionnaire: {e}") from e

    def _run_phase0_validation(
        self,
        plan_pdf_path: Path | None = None,
    ):
        """
        Run complete Phase 0 validation (boot checks + exit gates).

        This method executes the full Phase 0 sequence:
        P0.0: Bootstrap (RuntimeConfig, SeedRegistry)
        P0.1: Input Verification (SHA256 hashes)
        P0.2: Boot Checks (dependencies, PROD: fatal, DEV: warn)
        P0.3: Determinism (RNG seeding)
        Exit Gates: All 7 gates checked

        Args:
            plan_pdf_path: Path to input PDF for hashing (optional)

        Returns:
            Phase0ValidationResult with gate check results

        Raises:
            FactoryError: If Phase 0 validation fails and strict_validation=True
        """
        from orchestration.orchestrator import Phase0ValidationResult
        from datetime import datetime, timezone

        logger.info("factory_phase0_validation_start")

        # Use default PDF path if not provided
        if plan_pdf_path is None:
            plan_pdf_path = Path("input_plan.pdf")
            if not plan_pdf_path.exists():
                # Create dummy path for gate validation (won't be hashed)
                plan_pdf_path = Path("/dev/null")

        # Use questionnaire path from factory
        questionnaire_path = Path(self._questionnaire_path or CANONICAL_QUESTIONNAIRE_PATH)

        # Create Phase 0 runner
        runner = VerifiedPipelineRunner(
            plan_pdf_path=plan_pdf_path,
            artifacts_dir=Path.cwd() / "artifacts" / "phase0",
            questionnaire_path=questionnaire_path,
            runtime_config=self._runtime_config,
        )

        # Run Phase 0 (async method)
        try:
            import asyncio
            phase0_passed = asyncio.run(runner.run_phase_zero())
        except Exception as e:
            error_msg = f"Phase 0 execution failed: {e}"
            logger.error("factory_phase0_execution_failed error=%s", error_msg)

            if self._strict:
                raise FactoryError(error_msg) from e

            # In non-strict mode, create failed result
            return Phase0ValidationResult(
                all_passed=False,
                gate_results=[],
                validation_time=datetime.now(timezone.utc).isoformat(),
            )

        # Check exit gates
        all_passed, gate_results = check_all_gates(runner)

        # Create Phase0ValidationResult
        validation_result = Phase0ValidationResult(
            all_passed=all_passed,
            gate_results=gate_results,
            validation_time=datetime.now(timezone.utc).isoformat(),
        )

        # Log results
        logger.info(
            "factory_phase0_validation_complete passed=%s gates=%d/%d",
            all_passed,
            sum(1 for g in gate_results if g.passed),
            len(gate_results),
        )

        # Fail if gates failed and strict mode is on
        if not all_passed and self._strict:
            failed_gates = validation_result.get_failed_gates()
            failed_names = [g.gate_name for g in failed_gates]
            raise FactoryError(
                f"Phase 0 exit gates failed: {failed_names}. "
                f"Bootstrap must complete successfully before pipeline execution."
            )

        return validation_result

    def _build_signal_registry(self) -> None:
        """Build signal registry from canonical questionnaire.
        
        CRITICAL REQUIREMENTS:
        1. Use create_signal_registry(questionnaire) ONLY
        2. Pass self._canonical_questionnaire as ONLY argument
        3. NO other signal loading methods allowed (signal_loader.py DELETED)
        
        Raises:
            RegistryConstructionError: If registry construction fails.
        """
        if self._canonical_questionnaire is None:
            raise RegistryConstructionError(
                "Cannot build signal registry: canonical questionnaire not loaded"
            )

        logger.info("signal_registry_building_start")

        try:
            # Build registry from canonical source ONLY
            registry = create_signal_registry(self._canonical_questionnaire)

            # Validate registry
            if not hasattr(registry, 'get_all_policy_areas'):
                if self._strict:
                    raise RegistryConstructionError("Registry missing required methods")
                logger.warning("registry_validation_warning missing_methods")

            policy_areas = registry.get_all_policy_areas() if hasattr(registry, 'get_all_policy_areas') else []

            self._signal_registry = registry

            logger.info(
                "signal_registry_built_successfully version=2.0 policy_areas=%d",
                len(policy_areas),
            )

        except Exception as e:
            if isinstance(e, RegistryConstructionError):
                raise
            raise RegistryConstructionError(f"Failed to build signal registry: {e}") from e

    def _build_enriched_signal_packs(self) -> None:
        """Build enriched signal packs for all policy areas.
        
        Each BaseExecutor receives its own EnrichedSignalPack (NOT full registry).
        Pack includes semantic expansion and context filtering.
        
        Raises:
            RegistryConstructionError: If pack construction fails in strict mode.
        """
        if not self._enable_intelligence:
            logger.info("enriched_packs_disabled intelligence_layer=off")
            self._enriched_packs = {}
            return

        if self._signal_registry is None:
            raise RegistryConstructionError(
                "Cannot build enriched packs: signal registry not built"
            )

        logger.info("enriched_packs_building_start")

        enriched_packs: dict[str, EnrichedSignalPack] = {}

        try:
            policy_areas = self._signal_registry.get_all_policy_areas() if hasattr(self._signal_registry, 'get_all_policy_areas') else []

            if not policy_areas:
                logger.warning("enriched_packs_warning no_policy_areas_found")
                self._enriched_packs = enriched_packs
                return

            for policy_area_id in policy_areas:
                try:
                    # Get base pack from registry
                    base_pack = self._signal_registry.get(policy_area_id) if hasattr(self._signal_registry, 'get') else None

                    if base_pack is None:
                        logger.warning("base_pack_missing policy_area=%s", policy_area_id)
                        continue

                    base_metadata = getattr(base_pack, "metadata", {}) or {}
                    pattern_specs = base_metadata.get("pattern_specs", [])
                    if not isinstance(pattern_specs, list):
                        pattern_specs = []

                    # Create enriched pack (semantic expansion + context filtering)
                    # NOTE: EnrichedSignalPack expects dict-based pattern specs, not raw strings.
                    enriched_pack = create_enriched_signal_pack(
                        base_signal_pack={"patterns": pattern_specs},
                        enable_semantic_expansion=True,
                    )

                    enriched_packs[policy_area_id] = enriched_pack

                    logger.debug(
                        "enriched_pack_created policy_area=%s",
                        policy_area_id,
                    )

                except Exception as e:
                    msg = f"Failed to create enriched pack for {policy_area_id}: {e}"
                    if self._strict:
                        raise RegistryConstructionError(msg) from e
                    logger.error("enriched_pack_creation_failed policy_area=%s", policy_area_id, exc_info=True)

            self._enriched_packs = enriched_packs

            logger.info(
                "enriched_packs_built_successfully count=%d",
                len(enriched_packs),
            )

        except Exception as e:
            if isinstance(e, RegistryConstructionError):
                raise
            raise RegistryConstructionError(f"Failed to build enriched packs: {e}") from e

    def _initialize_calibration_registry(self) -> None:
        """Initialize the Epistemic Calibration Registry for level-specific calibration.

        FASE 4.1: Factory con Dependency Injection

        This method initializes the calibration registry which provides:
        - Level-specific calibration parameters (N0-N4)
        - Contract type overrides (TYPE_A-E, SUBTIPO_F)
        - PDM-driven adjustments based on document structure

        The registry is used by TaskExecutor to resolve calibration for N1/N2/N3 methods.

        Raises:
            FactoryError: If calibration registry initialization fails.
        """
        if not CALIBRATION_REGISTRY_AVAILABLE:
            logger.warning("calibration_registry_unavailable module_not_imported")
            self._calibration_registry = None
            return

        logger.info("calibration_registry_initializing_start")

        try:
            # Create calibration registry with default root path
            self._calibration_registry = create_registry()

            # Create default PDM profile (will be replaced with actual extraction in future)
            self._pdm_profile = MockPDMProfile(
                table_schemas=[],
                hierarchy_depth=2,
                contains_financial_data=False,
                temporal_structure={"has_baselines": False, "requires_ordering": False},
            )

            logger.info(
                "calibration_registry_initialized method_levels=%d type_configs=%d",
                len(self._calibration_registry.method_level_map),
                len(self._calibration_registry.type_overrides),
            )

        except Exception as e:
            if self._strict:
                raise FactoryError(f"Failed to initialize calibration registry: {e}") from e
            logger.warning(f"calibration_registry_init_failed non_strict_mode: {e}")
            self._calibration_registry = None

    def _extract_pdm_profile_from_cpp(self, doc: PreprocessedDocument | None = None) -> MockPDMProfile:
        """Extract PDM (Process Document Matrix) structural profile from PreprocessedDocument.

        FASE 4.1: PDM Profile Extraction

        This method analyzes the document structure to extract:
        - Table schemas (PPI, PAI, POI, financial tables)
        - Hierarchy depth (nested section levels)
        - Financial data presence
        - Temporal structure (baselines, ordering requirements)

        Args:
            doc: Optional PreprocessedDocument to analyze. If None, returns default profile.

        Returns:
            MockPDMProfile with extracted structural characteristics.

        Note:
            This is a simplified implementation. Future versions will integrate
            with the full PDM parametrization module for comprehensive structural analysis.
        """
        if doc is None:
            logger.debug("pdm_profile_extraction no_document_provided using_default")
            return MockPDMProfile()

        # Extract table schemas from document
        table_schemas = []
        hierarchy_depth = 2
        contains_financial_data = False
        temporal_structure = {"has_baselines": False, "requires_ordering": False}

        # Analyze document structure if available
        if hasattr(doc, "document_structure"):
            structure = doc.document_structure

            # Extract table schemas
            if hasattr(structure, "tables"):
                for table in structure.tables:
                    if hasattr(table, "schema_type"):
                        table_schemas.append(table.schema_type)

            # Determine hierarchy depth
            if hasattr(structure, "max_depth"):
                hierarchy_depth = structure.max_depth

            # Detect financial data
            if hasattr(structure, "contains_financial_data"):
                contains_financial_data = structure.contains_financial_data

            # Detect temporal structure
            if hasattr(structure, "temporal_elements"):
                temporal_structure["has_baselines"] = structure.temporal_elements.get("has_baselines", False)
                temporal_structure["requires_ordering"] = structure.temporal_elements.get("requires_ordering", False)

        profile = MockPDMProfile(
            table_schemas=table_schemas,
            hierarchy_depth=hierarchy_depth,
            contains_financial_data=contains_financial_data,
            temporal_structure=temporal_structure,
        )

        logger.debug(
            "pdm_profile_extracted tables=%d hierarchy_depth=%d financial=%s",
            len(table_schemas),
            hierarchy_depth,
            contains_financial_data,
        )

        return profile

    def _initialize_seed_registry(self) -> bool:
        """Initialize SeedRegistry singleton for deterministic operations.
        
        Returns:
            bool: True if seed registry was initialized, False otherwise.
        """
        if not SEED_REGISTRY_AVAILABLE:
            logger.warning("seed_registry_unavailable module_not_found determinism_not_guaranteed")
            return False

        if self._seed is None:
            logger.info("seed_registry_not_initialized no_seed_provided")
            return False

        try:
            SeedRegistry.initialize(master_seed=self._seed)
            logger.info("seed_registry_initialized master_seed=%d determinism=enabled", self._seed)
            return True
        except Exception:
            logger.error("seed_registry_initialization_failed", exc_info=True)
            return False

    def _build_method_executor(self) -> None:
        """Build MethodExecutor with CANONICAL METHOD INJECTION.
        
        CRITICAL INTEGRATION POINT - Direct Method Injection Pattern:
        ==============================================================
        
        This method now uses CANONICAL METHOD INJECTION as the default operation.
        Instead of instantiating full classes to get methods, we:
        
        1. Load canonical_methods_triangulated.json (348 verified methods)
        2. Import each method directly from its mother module
        3. Wrap methods with lazy class instantiation (only on first call)
        4. Inject wrapped methods into registry._direct_methods
        
        Benefits:
        ---------
        - NO upfront class instantiation (faster startup)
        - Methods are verified to exist at load time
        - Lazy instantiation only when method is actually called
        - Single source of truth: canonical_methods_triangulated.json
        
        Fallback:
        ---------
        If canonical injection fails, falls back to class_registry which
        loads classes on-demand via MethodRegistry._get_instance().
        
        Architecture Flow:
        -----------------
        1. inject_canonical_methods(registry) pre-populates 348 methods
        2. build_class_registry() provides fallback for non-canonical methods
        3. ExtendedArgRouter handles argument routing
        4. MethodExecutor.execute() calls registry.get_method() which:
           a. First checks _direct_methods (canonical, fast path)
           b. Falls back to _get_instance() if not found
        
        Raises:
            ExecutorConstructionError: If executor construction fails.
            
        See Also:
            - canonical_methods_triangulated.json: Verified method inventory
            - inject_canonical_methods(): Direct injection logic
            - phase2_10_02_methods_registry.py: Registry implementation
        """
        if self._signal_registry is None:
            raise ExecutorConstructionError(
                "Cannot build method executor: signal registry not built"
            )

        logger.info("method_executor_building_start canonical_injection=enabled")

        try:
            # Step 1: Build method registry with special instantiation rules
            # MethodRegistry handles shared instances (e.g., MunicipalOntology singleton)
            # and custom instantiation logic for complex analyzers
            method_registry = MethodRegistry()
            setup_default_instantiation_rules(method_registry)

            logger.info("method_registry_built instantiation_rules=configured")

            # Step 2: CANONICAL METHOD INJECTION (NEW DEFAULT)
            # Inject all 348 canonical methods directly into registry
            # This bypasses class instantiation - methods are pre-loaded as callables
            # Classes are only instantiated lazily on first method call
            try:
                injection_stats = inject_canonical_methods(method_registry)
                logger.info(
                    "canonical_methods_injected injected=%d failed=%d classes=%d",
                    injection_stats.get("injected", 0),
                    injection_stats.get("failed", 0),
                    len(injection_stats.get("classes_loaded", [])),
                )
                if injection_stats.get("failed", 0) > 0:
                    logger.warning(
                        "canonical_injection_failures count=%d first_failures=%s",
                        injection_stats["failed"],
                        injection_stats.get("failures", [])[:5],
                    )
            except Exception as e:
                logger.warning(
                    "canonical_injection_failed falling_back_to_class_instantiation error=%s",
                    e
                )

            # Step 3: Build class registry - FALLBACK for non-canonical methods
            # This loads ~30 monolith classes as backup for methods not in canonical inventory
            class_registry = build_class_registry()

            logger.info(
                "class_registry_built dispensaries=%d fallback_mode=enabled",
                len(class_registry)
            )

            # Step 4: Build extended arg router with special routes
            # Handles 30+ high-traffic method routes + generic routing
            arg_router = ExtendedArgRouter(class_registry)

            special_routes = arg_router.get_special_route_coverage() if hasattr(arg_router, 'get_special_route_coverage') else 0

            logger.info(
                "arg_router_built special_routes=%d generic_routing=enabled",
                special_routes
            )

            # Step 4: Build method executor WITH signal registry injected
            # This is the CORE integration point - executors call methods through this
            # Local import to avoid circular dependency
            from orchestration.orchestrator import MethodExecutor
            method_executor = MethodExecutor(
                method_registry=method_registry,
                arg_router=arg_router,
                signal_registry=self._signal_registry,  # DI: inject signal registry
            )

            # Step 5: PRE-EXECUTION CONTRACT VERIFICATION
            # Verify all 30 base executor contracts (D1-Q1 through D6-Q5) before execution
            # This ensures contract integrity and method class availability at startup
            logger.info("contract_verification_start verifying_30_base_contracts")



            verification_result = BaseExecutorWithContract.verify_all_base_contracts(
                class_registry=class_registry
            )

            if not verification_result["passed"]:
                error_summary = f"{len(verification_result['errors'])} contract validation errors"
                logger.error(
                    "contract_verification_failed errors=%d warnings=%d",
                    len(verification_result["errors"]),
                    len(verification_result.get("warnings", [])),
                )

                for error in verification_result["errors"][:10]:
                    logger.error("contract_error: %s", error)

                if self._strict:
                    raise ExecutorConstructionError(
                        f"Pre-execution contract verification failed: {error_summary}. "
                        f"See logs for details. Total errors: {len(verification_result['errors'])}"
                    )
                else:
                    logger.warning(
                        "contract_verification_failed_non_strict continuing_with_errors=%d",
                        len(verification_result["errors"])
                    )
            else:
                logger.info(
                    "contract_verification_passed verified=%d warnings=%d",
                    len(verification_result["verified_contracts"]),
                    len(verification_result.get("warnings", []))
                )

                for warning in verification_result.get("warnings", [])[:5]:
                    logger.warning("contract_warning: %s", warning)

            # Validate construction
            if not hasattr(method_executor, 'execute'):
                if self._strict:
                    raise ExecutorConstructionError("MethodExecutor missing 'execute' method")
                logger.warning("method_executor_validation_warning missing_execute")

            self._method_executor = method_executor

            logger.info(
                "method_executor_built_successfully "
                "dispensaries=%d special_routes=%d signal_registry=injected",
                len(class_registry),
                special_routes,
            )

        except Exception as e:
            if isinstance(e, ExecutorConstructionError):
                raise
            raise ExecutorConstructionError(f"Failed to build method executor: {e}") from e

    def _load_validation_constants(self) -> dict[str, Any]:
        """Load Phase 1 validation constants (hard contracts).
        
        These constants are injected into Orchestrator for Phase 1 validation:
        - P01_EXPECTED_CHUNK_COUNT = 60
        - P02_MIN_TABLE_COUNT = 5
        - etc.
        
        Returns:
            dict[str, Any]: Validation constants.
        """
        if self._validation_constants is not None:
            logger.info("validation_constants_using_provided count=%d", len(self._validation_constants))
            return self._validation_constants

        if VALIDATION_CONSTANTS_AVAILABLE:
            try:
                raw_constants = (
                    load_validation_constants()
                    if callable(load_validation_constants)
                    else PHASE1_VALIDATION_CONSTANTS
                )
                if not isinstance(raw_constants, Mapping):
                    raise TypeError(
                        f"Validation constants must be a mapping, got {type(raw_constants)!r}"
                    )

                constants = dict(raw_constants)
                logger.info("validation_constants_loaded_from_config count=%d", len(constants))
                return constants
            except Exception:
                logger.error("validation_constants_load_failed using_defaults", exc_info=True)

        # Default validation constants
        default_constants = {
            "P01_EXPECTED_CHUNK_COUNT": 60,
            "P01_MIN_CHUNK_LENGTH": 100,
            "P01_MAX_CHUNK_LENGTH": 2000,
            "P02_MIN_TABLE_COUNT": 5,
            "P02_MAX_TABLES_PER_DOCUMENT": 100,
        }

        logger.warning(
            "validation_constants_using_defaults count=%d constants_module_unavailable",
            len(default_constants),
        )

        return default_constants

    def _get_executor_config(self) -> ExecutorConfig:
        """Get or create ExecutorConfig."""
        if self._executor_config is not None:
            return self._executor_config
        return ExecutorConfig.default()

    def _build_orchestrator(
        self,
        executor_config: ExecutorConfig,
        runtime_config: RuntimeConfig | None = None,
        phase0_validation: Any = None,  # Phase0ValidationResult from orchestrator module
    ) -> Orchestrator:
        """Build Orchestrator with full dependency injection.

        CRITICAL: Orchestrator receives (in order):
        1. method_executor: MethodExecutor
        2. questionnaire: CanonicalQuestionnaire
        3. executor_config: ExecutorConfig
        4. runtime_config: RuntimeConfig | None
        5. phase0_validation: Phase0ValidationResult | None

        Note: signal_registry is accessed via method_executor.signal_registry
        Note: validation_constants are NOT passed to Orchestrator (not in signature)

        Args:
            executor_config: ExecutorConfig instance.
            runtime_config: RuntimeConfig for phase execution control.
            phase0_validation: Phase0ValidationResult with gate check results.

        Returns:
            Orchestrator: Fully configured orchestrator.

        Raises:
            ExecutorConstructionError: If orchestrator construction fails.
        """
        if self._canonical_questionnaire is None:
            raise ExecutorConstructionError("Cannot build orchestrator: questionnaire not loaded")
        if self._method_executor is None:
            raise ExecutorConstructionError("Cannot build orchestrator: method executor not built")

        logger.info("orchestrator_building_start")

        try:
            # Build orchestrator with FULL dependency injection
            # Local import to avoid circular dependency
            from orchestration.orchestrator import Orchestrator
            orchestrator = Orchestrator(
                method_executor=self._method_executor,       # 1st parameter - correct order
                questionnaire=self._canonical_questionnaire,  # 2nd parameter - correct order
                executor_config=executor_config,              # 3rd parameter - correct order
                runtime_config=runtime_config,                # 4th parameter - Phase 0 integration
                phase0_validation=phase0_validation,          # 5th parameter - Phase 0 integration
                # signal_registry is accessed via method_executor.signal_registry
                # validation_constants NOT in Orchestrator signature
            )

            logger.info("orchestrator_built_successfully")

            return orchestrator

        except Exception as e:
            raise ExecutorConstructionError(f"Failed to build orchestrator: {e}") from e

    def _build_core_module_factory(self) -> Any | None:
        """Build CoreModuleFactory if available."""
        if not CORE_MODULE_FACTORY_AVAILABLE:
            return None

        try:
            factory = CoreModuleFactory()
            logger.info("core_module_factory_built")
            return factory
        except Exception:
            logger.error("core_module_factory_construction_error", exc_info=True)
            return None

    def _compute_questionnaire_hash(self) -> str:
        """Compute SHA-256 hash of loaded questionnaire."""
        if self._canonical_questionnaire is None:
            return ""
        return self._compute_questionnaire_hash_from_instance(self._canonical_questionnaire)

    @staticmethod
    def _compute_questionnaire_hash_from_instance(questionnaire: CanonicalQuestionnaire) -> str:
        """Compute deterministic SHA-256 hash of questionnaire content."""
        try:
            # Try to get JSON representation if available
            if hasattr(questionnaire, 'to_dict'):
                content = json.dumps(questionnaire.to_dict(), sort_keys=True)
            elif hasattr(questionnaire, '__dict__'):
                content = json.dumps(questionnaire.__dict__, sort_keys=True, default=str)
            else:
                content = str(questionnaire)

            return hashlib.sha256(content.encode('utf-8')).hexdigest()

        except Exception as e:
            logger.warning("questionnaire_hash_computation_degraded error=%s", str(e))
            # Fallback to simple string hash
            return hashlib.sha256(str(questionnaire).encode('utf-8')).hexdigest()

    def create_executor_instance(
        self,
        executor_class: type,
        policy_area_id: str,
        **extra_kwargs: Any,
    ) -> Any:
        """Create BaseExecutor instance with EnrichedSignalPack injected.
        
        This method is called for each of the ~30 BaseExecutor classes.
        Each executor receives its specific EnrichedSignalPack, NOT the full registry.
        
        Args:
            executor_class: BaseExecutor subclass to instantiate.
            policy_area_id: Policy area identifier for signal pack selection.
            **extra_kwargs: Additional kwargs to pass to constructor.
            
        Returns:
            BaseExecutor instance with dependencies injected.
            
        Raises:
            ExecutorConstructionError: If executor instantiation fails.
        """
        if self._method_executor is None:
            raise ExecutorConstructionError(
                "Cannot create executor: method executor not built"
            )

        # Get enriched signal pack for this policy area
        enriched_pack = self._enriched_packs.get(policy_area_id)

        if enriched_pack is None and self._enable_intelligence:
            logger.warning(
                "executor_creation_warning no_enriched_pack policy_area=%s executor=%s",
                policy_area_id,
                executor_class.__name__,
            )

        try:
            # Inject dependencies into executor
            executor_instance = executor_class(
                method_executor=self._method_executor,  # DI: inject method executor
                signal_registry=self._signal_registry,  # DI: inject signal registry
                config=self._get_executor_config(),  # DI: inject config
                questionnaire_provider=self._canonical_questionnaire,  # DI: inject questionnaire
                enriched_pack=enriched_pack,  # DI: inject enriched signal pack (specific to policy area)
                **extra_kwargs,
            )

            logger.debug(
                "executor_instance_created executor=%s policy_area=%s",
                executor_class.__name__,
                policy_area_id,
            )

            return executor_instance

        except Exception as e:
            raise ExecutorConstructionError(
                f"Failed to create executor {executor_class.__name__}: {e}"
            ) from e


# =============================================================================
# Convenience Functions
# =============================================================================


def create_analysis_pipeline(
    questionnaire_path: str | None = None,
    expected_hash: str | None = None,
    seed: int | None = None,
    runtime_config: RuntimeConfig | None = None,
    run_phase0: bool = True,
) -> ProcessorBundle:
    """Convenience function to create complete analysis pipeline.

    This is the RECOMMENDED entry point for most use cases.

    Args:
        questionnaire_path: Path to canonical questionnaire JSON.
        expected_hash: Expected SHA-256 hash for integrity check.
        seed: Seed for reproducibility.
        runtime_config: Optional RuntimeConfig (defaults to from_env()).
        run_phase0: Whether to run Phase 0 validation (default: True).

    Returns:
        ProcessorBundle with Orchestrator ready to use.
    """
    factory = AnalysisPipelineFactory(
        questionnaire_path=questionnaire_path,
        expected_questionnaire_hash=expected_hash,
        runtime_config=runtime_config,
        seed_for_determinism=seed,
        enable_intelligence_layer=True,
        strict_validation=True,
        run_phase0_validation=run_phase0,
    )
    return factory.create_orchestrator()


def create_minimal_pipeline(
    questionnaire_path: str | None = None,
    run_phase0: bool = False,
) -> ProcessorBundle:
    """Create minimal pipeline without intelligence layer.

    Useful for testing or when enriched signals are not needed.
    Phase 0 validation is disabled by default for minimal pipelines.

    Args:
        questionnaire_path: Path to canonical questionnaire JSON.
        run_phase0: Whether to run Phase 0 validation (default: False).

    Returns:
        ProcessorBundle with basic dependencies only.
    """
    factory = AnalysisPipelineFactory(
        questionnaire_path=questionnaire_path,
        enable_intelligence_layer=False,
        strict_validation=False,
        run_phase0_validation=run_phase0,
    )
    return factory.create_orchestrator()


# Alias for backward compatibility with Phase 2 executors
build_processor = create_analysis_pipeline


# =============================================================================
# Validation and Diagnostics
# =============================================================================


def validate_factory_singleton() -> dict[str, Any]:
    """Validate that load_questionnaire() was called exactly once.
    
    Returns:
        dict with validation results.
    """
    return {
        "questionnaire_loaded": AnalysisPipelineFactory._questionnaire_loaded,
        "questionnaire_instance_exists": AnalysisPipelineFactory._questionnaire_instance is not None,
        "singleton_pattern_valid": (
            AnalysisPipelineFactory._questionnaire_loaded and
            AnalysisPipelineFactory._questionnaire_instance is not None
        ),
    }


def validate_bundle(bundle: ProcessorBundle) -> dict[str, Any]:
    """Validate bundle integrity and return diagnostics."""
    diagnostics = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "components": {},
        "metrics": {},
    }

    # Validate orchestrator
    if bundle.orchestrator is None:
        diagnostics["valid"] = False
        diagnostics["errors"].append("orchestrator is None")
    else:
        diagnostics["components"]["orchestrator"] = "present"

    # Validate method executor
    if bundle.method_executor is None:
        diagnostics["valid"] = False
        diagnostics["errors"].append("method_executor is None")
    else:
        diagnostics["components"]["method_executor"] = "present"
        if hasattr(bundle.method_executor, 'arg_router'):
            router = bundle.method_executor.arg_router
            if hasattr(router, 'get_special_route_coverage'):
                diagnostics["metrics"]["special_routes"] = router.get_special_route_coverage()

    # Validate questionnaire
    if bundle.questionnaire is None:
        diagnostics["valid"] = False
        diagnostics["errors"].append("questionnaire is None")
    else:
        diagnostics["components"]["questionnaire"] = "present"
        if hasattr(bundle.questionnaire, 'questions'):
            diagnostics["metrics"]["question_count"] = len(bundle.questionnaire.questions)

    # Validate signal registry
    if bundle.signal_registry is None:
        diagnostics["valid"] = False
        diagnostics["errors"].append("signal_registry is None")
    else:
        diagnostics["components"]["signal_registry"] = "present"
        if hasattr(bundle.signal_registry, 'get_all_policy_areas'):
            diagnostics["metrics"]["policy_areas"] = len(bundle.signal_registry.get_all_policy_areas())

    # Validate enriched packs
    diagnostics["components"]["enriched_packs"] = len(bundle.enriched_signal_packs)
    diagnostics["metrics"]["enriched_pack_count"] = len(bundle.enriched_signal_packs)

    # Validate validation constants
    diagnostics["components"]["validation_constants"] = len(bundle.validation_constants)
    diagnostics["metrics"]["validation_constant_count"] = len(bundle.validation_constants)

    # FASE 4.1: Validate calibration registry
    if bundle.calibration_registry is not None:
        diagnostics["components"]["calibration_registry"] = "present"
        if hasattr(bundle.calibration_registry, 'method_level_map'):
            diagnostics["metrics"]["calibration_method_levels"] = len(bundle.calibration_registry.method_level_map)
        if hasattr(bundle.calibration_registry, 'type_overrides'):
            diagnostics["metrics"]["calibration_type_configs"] = len(bundle.calibration_registry.type_overrides)
    else:
        diagnostics["warnings"].append("CalibrationRegistry not initialized - epistemic calibration disabled")

    # FASE 4.1: Validate PDM profile
    if bundle.pdm_profile is not None:
        diagnostics["components"]["pdm_profile"] = "present"
        diagnostics["metrics"]["pdm_hierarchy_depth"] = getattr(bundle.pdm_profile, "hierarchy_depth", None)
        diagnostics["metrics"]["pdm_financial"] = getattr(bundle.pdm_profile, "contains_financial_data", None)
    else:
        diagnostics["warnings"].append("PDM profile not extracted - using default calibration")

    # Validate seed registry
    if not bundle.seed_registry_initialized:
        diagnostics["warnings"].append("SeedRegistry not initialized - determinism not guaranteed")

    # Check factory instantiation
    if not bundle.provenance.get("factory_instantiation_confirmed"):
        diagnostics["errors"].append("Bundle not created via AnalysisPipelineFactory")
        diagnostics["valid"] = False

    return diagnostics


def get_bundle_info(bundle: ProcessorBundle) -> dict[str, Any]:
    """Get human-readable information about bundle."""
    return {
        "construction_time": bundle.provenance.get("construction_timestamp_utc"),
        "canonical_hash": bundle.provenance.get("canonical_sha256", "")[:16],
        "policy_areas": sorted(bundle.enriched_signal_packs.keys()),
        "policy_area_count": len(bundle.enriched_signal_packs),
        "intelligence_layer": bundle.provenance.get("intelligence_layer_enabled"),
        "validation_constants": len(bundle.validation_constants),
        "construction_duration": bundle.provenance.get("construction_duration_seconds"),
        "seed_initialized": bundle.seed_registry_initialized,
        "factory_class": bundle.provenance.get("factory_class"),
        # FASE 4.1: Calibration info
        "calibration_available": bundle.calibration_registry is not None,
        "calibration_method_levels": bundle.provenance.get("calibration_method_levels", 0),
        "calibration_type_configs": bundle.provenance.get("calibration_type_configs", 0),
        "pdm_available": bundle.pdm_profile is not None,
        "pdm_hierarchy_depth": bundle.provenance.get("pdm_profile_hierarchy_depth"),
        "pdm_financial": bundle.provenance.get("pdm_profile_financial"),
    }


# =============================================================================
# Module-level Checks
# =============================================================================


def check_legacy_signal_loader_deleted() -> dict[str, Any]:
    """Check that signal_loader.py has been deleted.
    
    Returns:
        dict with check results.
    """
    try:
        import cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_loader
        return {
            "legacy_loader_deleted": False,
            "error": "signal_loader.py still exists - must be deleted per architecture requirements",
        }
    except ImportError:
        return {
            "legacy_loader_deleted": True,
            "message": "signal_loader.py correctly deleted - no legacy signal loading",
        }


def verify_single_questionnaire_load_point() -> dict[str, Any]:
    """Verify that only AnalysisPipelineFactory calls load_questionnaire().
    
    This requires manual code search but provides guidance.
    
    Returns:
        dict with verification instructions.
    """
    return {
        "verification_required": True,
        "search_command": "grep -r 'load_questionnaire(' --exclude-dir=__pycache__ --exclude='*.pyc'",
        "expected_result": "Should ONLY appear in: factory.py (AnalysisPipelineFactory._load_canonical_questionnaire)",
        "instructions": (
            "1. Run grep command above\n"
            "2. Verify ONLY factory.py calls load_questionnaire()\n"
            "3. Remove any other calls found\n"
            "4. Update tests to use AnalysisPipelineFactory"
        ),
    }


def get_method_dispensary_info() -> dict[str, Any]:
    """Get information about the method dispensary pattern.
    
    Returns detailed statistics about:
    - Which monolith classes serve as dispensaries
    - How many methods each dispensary provides
    - Which executors use which dispensaries
    - Method reuse patterns
    
    Returns:
        dict with dispensary statistics and usage patterns.
    """


    class_paths = get_class_paths()

    # Load executor→methods mapping
    try:
        import json
        from pathlib import Path
        executors_methods_path = Path(__file__).resolve().parent / "executors_methods.json"
        if executors_methods_path.exists():
            with open(executors_methods_path) as f:
                executors_methods = json.load(f)
        else:
            executors_methods = []
    except Exception:
        executors_methods = []

    # Build dispensary statistics
    dispensaries = {}
    for class_name in class_paths.keys():
        dispensaries[class_name] = {
            "module": class_paths[class_name],
            "methods_provided": [],
            "used_by_executors": [],
            "total_usage_count": 0,
        }

    # Count method usage per dispensary
    for executor_info in executors_methods:
        executor_id = executor_info.get("executor_id")
        methods = executor_info.get("methods", [])

        for method_info in methods:
            class_name = method_info.get("class")
            method_name = method_info.get("method")

            if class_name in dispensaries:
                if method_name not in dispensaries[class_name]["methods_provided"]:
                    dispensaries[class_name]["methods_provided"].append(method_name)

                if executor_id not in dispensaries[class_name]["used_by_executors"]:
                    dispensaries[class_name]["used_by_executors"].append(executor_id)

                dispensaries[class_name]["total_usage_count"] += 1

    # Sort by usage count
    sorted_dispensaries = sorted(
        dispensaries.items(),
        key=lambda x: x[1]["total_usage_count"],
        reverse=True
    )

    # Build summary statistics
    total_methods = sum(len(d["methods_provided"]) for _, d in sorted_dispensaries)
    total_usage = sum(d["total_usage_count"] for _, d in sorted_dispensaries)

    return {
        "pattern": "method_dispensary",
        "description": "Monolith classes serve as method dispensaries for 30 executors",
        "total_dispensaries": len(dispensaries),
        "total_unique_methods": total_methods,
        "total_method_calls": total_usage,
        "avg_reuse_per_method": round(total_usage / max(total_methods, 1), 2),
        "dispensaries": {
            name: {
                "methods_count": len(info["methods_provided"]),
                "executor_count": len(info["used_by_executors"]),
                "total_calls": info["total_usage_count"],
                "reuse_factor": round(info["total_usage_count"] / max(len(info["methods_provided"]), 1), 2),
            }
            for name, info in sorted_dispensaries[:10]  # Top 10
        },
        "top_dispensaries": [
            {
                "class": name,
                "methods": len(info["methods_provided"]),
                "executors": len(info["used_by_executors"]),
                "calls": info["total_usage_count"],
            }
            for name, info in sorted_dispensaries[:5]
        ],
    }


def validate_method_dispensary_pattern() -> dict[str, Any]:
    """Validate that the method dispensary pattern is correctly implemented.
    
    Checks:
    1. All executor methods exist in class_registry
    2. No executor directly imports monolith classes
    3. All methods route through MethodExecutor
    4. Signal registry is injected (not globally accessed)
    
    Returns:
        dict with validation results.
    """


    class_paths = get_class_paths()
    validation_results = {
        "pattern_valid": True,
        "errors": [],
        "warnings": [],
        "checks": {},
    }

    # Check 1: Verify class_registry is populated
    if not class_paths:
        validation_results["pattern_valid"] = False
        validation_results["errors"].append(
            "class_registry is empty - no dispensaries registered"
        )
    else:
        validation_results["checks"]["dispensaries_registered"] = len(class_paths)

    # Check 2: Verify executor_methods.json exists
    try:
        import json
        from pathlib import Path
        executors_methods_path = Path(__file__).resolve().parent / "executors_methods.json"
        if not executors_methods_path.exists():
            validation_results["warnings"].append(
                "executors_methods.json not found - cannot validate method mappings"
            )
        else:
            with open(executors_methods_path) as f:
                executors_methods = json.load(f)
            validation_results["checks"]["executor_method_mappings"] = len(executors_methods)
    except Exception as e:
        validation_results["warnings"].append(
            f"Failed to load executors_methods.json: {e}"
        )

    # Check 3: Verify validation file exists
    try:
        validation_path = Path(__file__).resolve().parent / "executor_factory_validation.json"
        if not validation_path.exists():
            validation_results["warnings"].append(
                "executor_factory_validation.json not found - cannot validate method catalog"
            )
        else:
            with open(validation_path) as f:
                validation_data = json.load(f)
            validation_results["checks"]["method_pairs_validated"] = validation_data.get("validated_against_catalog", 0)
            validation_results["checks"]["validation_failures"] = len(validation_data.get("failures", []))
    except Exception as e:
        validation_results["warnings"].append(
            f"Failed to load executor_factory_validation.json: {e}"
        )

    return validation_results


# _validate_questionnaire_structure moved to orchestration.questionnaire_validation
# to break import cycle between factory and orchestrator.
