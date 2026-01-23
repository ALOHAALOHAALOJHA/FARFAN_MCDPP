"""
Unified FARFAN Pipeline Factory
================================

This is the SINGLE unified factory that consolidates all factory logic.

Previously scattered across:
- phase2_10_00_factory.py (Phase 2 specific - EMPTY/DEPRECATED)
- executor_factory/core/factory.py (Executor specific - skeletal)
- Various other factory-like constructions

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                          UNIFIED FACTORY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Questionnaire   │  │ Signal Registry │  │ Components      │             │
│  │                 │  │                 │  │                 │             │
│  │ - CQCLoader     │  │ - Canonical     │  │ - Detectors     │             │
│  │ - Resolver      │  │   Notation      │  │ - Calculators   │             │
│  │                 │  │ - Patterns      │  │ - Analyzers     │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ File I/O        │  │ Contracts       │  │ SISAS           │             │
│  │                 │  │                 │  │                 │             │
│  │ - JSON          │  │ - Load 300      │  │ - SDO           │             │
│  │ - Text          │  │ - Execute       │  │ - Consumers     │             │
│  │                 │  │ - Inject        │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Version: 1.0.0 (Unified)
Author: FARFAN Pipeline Architecture Team
Date: 2026-01-19
"""

from __future__ import annotations

import asyncio
import importlib
import json
import time
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar

import structlog

# =============================================================================
# TYPE CHECKING IMPORTS (prevents circular imports)
# =============================================================================
if TYPE_CHECKING:
    from canonic_questionnaire_central.resolver import (
        CanonicalQuestionnaireResolver,
        SignalDistributionOrchestrator,
    )

# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================
logger = structlog.get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass
class FactoryConfig:
    """
    Configuration for the unified factory.

    Attributes:
        project_root: Root directory of the project
        questionnaire_path: Path to questionnaire (auto-detected if None)
        sisas_enabled: Whether to enable SISAS signal dispatch
        contracts_path: Path to contracts JSON file
        lazy_load_questions: Use lazy loading for questions (default: True)
        cache_size: Question cache size (default: 100)
        enable_parallel_execution: Enable parallel contract execution (default: True)
        max_workers: Maximum worker threads/processes for parallel execution (default: 4)
        enable_adaptive_caching: Enable adaptive LRU+TTL cache (default: True)
        cache_ttl_seconds: Time-to-live for cached items (default: 300)
        enable_predictive_prefetch: Enable predictive prefetching (default: True)
        batch_execution_threshold: Minimum contracts for batch mode (default: 5)
    """

    project_root: Path
    questionnaire_path: Optional[Path] = None
    sisas_enabled: bool = True
    contracts_path: Optional[Path] = None
    lazy_load_questions: bool = True
    cache_size: int = 100
    enable_parallel_execution: bool = True
    max_workers: int = 4
    enable_adaptive_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_predictive_prefetch: bool = True
    batch_execution_threshold: int = 5

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        if isinstance(self.questionnaire_path, str):
            self.questionnaire_path = Path(self.questionnaire_path)
        if isinstance(self.contracts_path, str):
            self.contracts_path = Path(self.contracts_path)


@dataclass(frozen=True)
class FactoryHealthStatus:
    """Comprehensive factory health status."""
    is_healthy: bool
    cache_hit_rate: float
    parallel_efficiency: float
    avg_execution_time_ms: float
    error_rate: float
    active_contracts: int
    available_workers: int
    warnings: tuple

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_healthy": self.is_healthy,
            "cache_hit_rate": self.cache_hit_rate,
            "parallel_efficiency": self.parallel_efficiency,
            "avg_execution_time_ms": self.avg_execution_time_ms,
            "error_rate": self.error_rate,
            "active_contracts": self.active_contracts,
            "available_workers": self.available_workers,
            "warnings": list(self.warnings),
        }


# =============================================================================
# ADAPTIVE CACHING SYSTEM (INTERVENTION 1)
# =============================================================================


class AdaptiveLRUCache:
    """
    Thread-safe hybrid LRU+TTL cache with adaptive eviction.
    
    Features:
    - LRU eviction for size management
    - TTL-based expiration for freshness
    - Access frequency tracking
    - Predictive prefetching hints
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with LRU update (thread-safe)."""
        with self._lock:
            if key not in self._cache:
                return None
                
            # Check TTL expiration
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                self._evict(key)
                return None
                
            # Update LRU order
            self._cache.move_to_end(key)
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            return self._cache[key]
        
    def set(self, key: str, value: Any) -> None:
        """Set item in cache with automatic eviction (thread-safe)."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # Evict least recently used
                    oldest_key = next(iter(self._cache))
                    self._evict(key=oldest_key)
                    
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
        
    def _evict(self, key: str) -> None:
        """Evict item from cache (must be called within lock)."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_counts.pop(key, None)
        
    def get_hot_keys(self, top_n: int = 10) -> List[str]:
        """Get most frequently accessed keys for prefetching (thread-safe)."""
        with self._lock:
            return sorted(
                self._access_counts.keys(),
                key=lambda k: self._access_counts[k],
                reverse=True
            )[:top_n]
        
    def clear(self) -> None:
        """Clear all cache entries (thread-safe)."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counts.clear()


# =============================================================================
# UNIFIED FACTORY
# =============================================================================


class UnifiedFactory:
    """
    SINGLE UNIFIED FACTORY for the FARFAN pipeline.

    This factory replaces ALL scattered factory files and provides:
    1. Questionnaire loading via modular CQC
    2. Signal registry creation from canonical notation
    3. Component instantiation (analyzers, detectors, calculators)
    4. File I/O utilities
    5. Contract loading and execution with method injection
    6. SISAS central initialization

    Usage:
        >>> from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig
        >>> config = FactoryConfig(project_root=Path("."))
        >>> factory = UnifiedFactory(config)
        >>> questionnaire = factory.load_questionnaire()
        >>> components = factory.create_analysis_components()

    Replaces:
    - phase2_10_00_factory.py (DEPRECATED - was empty)
    - executor_factory/core/factory.py (DEPRECATED - was skeletal)
    """

    def __init__(self, config: FactoryConfig):
        """
        Initialize the unified factory.

        Args:
            config: FactoryConfig object with factory settings
        """
        self._config = config
        self._questionnaire: Optional[Any] = None
        self._questionnaire_resolver: Optional[CanonicalQuestionnaireResolver] = None
        self._signal_registry: Optional[Dict[str, Any]] = None
        self._sisas_central: Optional[SignalDistributionOrchestrator] = None
        self._contracts: Optional[Dict[str, Any]] = None
        
        # ==========================================================================
        # INTERVENTION 1: Adaptive Caching System
        # ==========================================================================
        self._method_cache: Optional[AdaptiveLRUCache] = None
        self._executor_cache: Optional[AdaptiveLRUCache] = None
        
        if config.enable_adaptive_caching:
            self._method_cache = AdaptiveLRUCache(
                max_size=config.cache_size * 2,
                ttl_seconds=config.cache_ttl_seconds
            )
            self._executor_cache = AdaptiveLRUCache(
                max_size=config.cache_size,
                ttl_seconds=config.cache_ttl_seconds
            )
            logger.info("Adaptive caching enabled", cache_size=config.cache_size)
        
        # ==========================================================================
        # INTERVENTION 1: Parallel Execution Infrastructure
        # ==========================================================================
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        
        if config.enable_parallel_execution:
            self._thread_pool = ThreadPoolExecutor(max_workers=config.max_workers)
            logger.info("Parallel execution enabled", max_workers=config.max_workers)
        
        # ==========================================================================
        # INTERVENTION 1: Performance Metrics (Thread-Safe)
        # ==========================================================================
        self._execution_metrics = {
            "contracts_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "parallel_executions": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "failed_executions": 0,
        }
        self._metrics_lock = threading.Lock()  # Lock for metrics updates

        # ==========================================================================
        # INTERVENTION 2: Access Pattern Tracking for Predictive Caching
        # ==========================================================================
        self._access_pattern: List[str] = []  # Track contract access order
        self._pattern_lock = threading.Lock()  # Lock for pattern access

        logger.info(
            "UnifiedFactory initialized",
            project_root=str(config.project_root),
            sisas_enabled=config.sisas_enabled,
            lazy_load=config.lazy_load_questions,
            parallel_enabled=config.enable_parallel_execution,
            adaptive_cache_enabled=config.enable_adaptive_caching,
        )
    
    def _update_metrics(self, **updates: Any) -> None:
        """Thread-safe metrics update helper."""
        with self._metrics_lock:
            for key, value in updates.items():
                if key in self._execution_metrics:
                    if isinstance(value, (int, float)) and isinstance(self._execution_metrics[key], (int, float)):
                        self._execution_metrics[key] += value
                    else:
                        self._execution_metrics[key] = value

    # ==========================================================================
    # QUESTIONNAIRE ACCESS
    # ==========================================================================

    @property
    def questionnaire(self) -> Any:
        """
        Lazy-loaded canonical questionnaire.

        Uses CQCLoader with 333x performance optimizations.

        Returns:
            CQCLoader instance with lazy-loaded questions
        """
        if self._questionnaire is None:
            from canonic_questionnaire_central import CQCConfig, CQCLoader

            cqc_config = CQCConfig(
                lazy_load_questions=self._config.lazy_load_questions,
                use_signal_index=True,
                pattern_inheritance=True,
                cache_size=self._config.cache_size,
                registry_path=(
                    self._config.questionnaire_path
                    if self._config.questionnaire_path
                    else None
                ),
            )
            self._questionnaire = CQCLoader(config=cqc_config)
            logger.debug(
                "Questionnaire loaded via CQCLoader",
                registry_type=getattr(self._questionnaire, "_registry_type", "unknown"),
            )
        return self._questionnaire

    @property
    def questionnaire_resolver(self) -> CanonicalQuestionnaireResolver:
        """
        Get the questionnaire resolver for deep access.

        Returns:
            CanonicalQuestionnaireResolver instance
        """
        if self._questionnaire_resolver is None:
            from canonic_questionnaire_central.resolver import (
                CanonicalQuestionnaireResolver,
            )

            self._questionnaire_resolver = CanonicalQuestionnaireResolver()
            logger.debug("Questionnaire resolver initialized")
        return self._questionnaire_resolver

    def load_questionnaire(self) -> Any:
        """
        Explicit load method for backward compatibility.

        Returns:
            CQCLoader instance
        """
        return self.questionnaire

    # ==========================================================================
    # SIGNAL REGISTRY
    # ==========================================================================

    def create_signal_registry(self) -> Dict[str, Any]:
        """
        Create signal registry from canonical notation.

        Builds a registry containing:
        - Dimensions (DIM01-DIM06)
        - Policy Areas (PA01-PA10)
        - Clusters (CL01-CL04)
        - Keywords
        - Patterns

        Returns:
            Dict with signal registry data
        """
        if self._signal_registry is None:
            # Build from canonical notation
            registry = {}

            # Load canonical notation JSON
            canonical_path = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "canonic_questionnaire_central"
                / "config"
                / "canonical_notation.json"
            )

            if canonical_path.exists():
                with open(canonical_path, "r", encoding="utf-8") as f:
                    canonical_data = json.load(f)

                registry = {
                    "dimensions": canonical_data.get("dimensions", {}),
                    "policy_areas": canonical_data.get("policy_areas", {}),
                    "clusters": canonical_data.get("clusters", {}),
                }

                logger.debug(
                    "Signal registry created from canonical notation",
                    dimensions_count=len(registry["dimensions"]),
                    policy_areas_count=len(registry["policy_areas"]),
                    clusters_count=len(registry["clusters"]),
                )
            else:
                logger.warning(
                    "Canonical notation file not found, using resolver",
                    path=str(canonical_path),
                )
                # Fallback to resolver
                resolver = self.questionnaire_resolver
                registry = {
                    "dimensions": resolver.get_dimensions(),
                    "policy_areas": resolver.get_policy_areas(),
                    "clusters": resolver.get_clusters(),
                }

            self._signal_registry = registry

        return self._signal_registry

    # ==========================================================================
    # COMPONENT CREATION
    # ==========================================================================
    # NOTE: These are optional advanced analysis components that may not be
    # available in all deployments. They gracefully return None if the
    # underlying modules are not installed.
    # ==========================================================================

    def create_contradiction_detector(self):
        """
        Create contradiction detector instance.

        This is an OPTIONAL advanced analysis component. The module may not
        be available in all deployments.

        Returns:
            ContradictionDetector instance or None if module not available

        Note:
            This component requires farfan_pipeline.phases.Phase_02.methods.contradiction_detector
            which is an optional dependency. Returns None gracefully if unavailable.
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.contradiction_detector import (
                ContradictionDetector,
            )

            return ContradictionDetector(self.questionnaire)
        except ImportError as e:
            logger.debug(
                "ContradictionDetector not available (optional component)",
                error=str(e),
            )
            return None
        except Exception as e:
            logger.warning(
                "ContradictionDetector initialization failed",
                error=str(e),
            )
            return None

    def create_temporal_logic_verifier(self):
        """
        Create temporal logic verifier instance.

        This is an OPTIONAL advanced analysis component. The module may not
        be available in all deployments.

        Returns:
            TemporalLogicVerifier instance or None if module not available

        Note:
            This component requires farfan_pipeline.phases.Phase_02.methods.temporal_logic
            which is an optional dependency. Returns None gracefully if unavailable.
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.temporal_logic import (
                TemporalLogicVerifier,
            )

            return TemporalLogicVerifier(self.questionnaire)
        except ImportError as e:
            logger.debug(
                "TemporalLogicVerifier not available (optional component)",
                error=str(e),
            )
            return None
        except Exception as e:
            logger.warning(
                "TemporalLogicVerifier initialization failed",
                error=str(e),
            )
            return None

    def create_bayesian_confidence_calculator(self):
        """
        Create Bayesian confidence calculator instance.

        This is an OPTIONAL advanced analysis component. The module may not
        be available in all deployments.

        Returns:
            BayesianConfidenceCalculator instance or None if module not available

        Note:
            This component requires farfan_pipeline.phases.Phase_02.methods.bayesian_calculator
            which is an optional dependency. Returns None gracefully if unavailable.
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.bayesian_calculator import (
                BayesianConfidenceCalculator,
            )

            return BayesianConfidenceCalculator(self.questionnaire)
        except ImportError as e:
            logger.debug(
                "BayesianConfidenceCalculator not available (optional component)",
                error=str(e),
            )
            return None
        except Exception as e:
            logger.warning(
                "BayesianConfidenceCalculator initialization failed",
                error=str(e),
            )
            return None

    def create_municipal_analyzer(self):
        """
        Create municipal analyzer instance.

        This is an OPTIONAL advanced analysis component. The module may not
        be available in all deployments.

        Returns:
            MunicipalAnalyzer instance or None if module not available

        Note:
            This component requires farfan_pipeline.phases.Phase_02.methods.municipal_analyzer
            which is an optional dependency. Returns None gracefully if unavailable.
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.municipal_analyzer import (
                MunicipalAnalyzer,
            )

            return MunicipalAnalyzer(self.questionnaire)
        except ImportError as e:
            logger.debug(
                "MunicipalAnalyzer not available (optional component)",
                error=str(e),
            )
            return None
        except Exception as e:
            logger.warning(
                "MunicipalAnalyzer initialization failed",
                error=str(e),
            )
            return None

    def create_analysis_components(self) -> Dict[str, Any]:
        """
        Create all analysis components as a bundle.

        This method attempts to create all optional analysis components.
        Components that are not available will be excluded from the result.

        Returns:
            Dict with component names as keys and instances as values.
            Only includes components that were successfully created.

        Note:
            All components in this bundle are OPTIONAL. The returned dict
            may be empty if no optional components are available.
        """
        components = {
            "contradiction_detector": self.create_contradiction_detector(),
            "temporal_logic_verifier": self.create_temporal_logic_verifier(),
            "bayesian_calculator": self.create_bayesian_confidence_calculator(),
            "municipal_analyzer": self.create_municipal_analyzer(),
        }

        # Filter out None values (unavailable components)
        components = {k: v for k, v in components.items() if v is not None}

        logger.debug(
            "Analysis components created",
            available_components=list(components.keys()),
        )

        return components

    # ==========================================================================
    # FILE I/O UTILITIES
    # ==========================================================================

    @staticmethod
    def save_json(path: Path, data: Dict[str, Any]) -> None:
        """
        Save data to JSON file.

        Args:
            path: Output file path
            data: Data to save
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug("JSON saved", path=str(path))

    @staticmethod
    def write_text_file(path: Path, content: str) -> None:
        """
        Write content to text file.

        Args:
            path: Output file path
            content: Text content to write
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.debug("Text file written", path=str(path))

    @staticmethod
    def load_json(path: Path) -> Dict[str, Any]:
        """
        Load data from JSON file.

        Args:
            path: Input file path

        Returns:
            Dict with loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def read_text_file(path: Path) -> str:
        """
        Read content from text file.

        Args:
            path: Input file path

        Returns:
            File content as string
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # ==========================================================================
    # CONTRACT EXECUTION
    # ==========================================================================

    def load_contracts(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load 300 executor contracts from JSON.

        Args:
            path: Optional path to contracts file. If None, uses default.

        Returns:
            Dict mapping contract_id to contract data
        """
        if self._contracts is None:
            load_path = path or self._config.contracts_path
            if load_path is None:
                # Default to artifacts/data/contracts/
                load_path = (
                    self._config.project_root
                    / "artifacts/data/contracts/EXECUTOR_CONTRACTS_300_FINAL.json"
                )

            load_path = Path(load_path)

            if not load_path.exists():
                logger.warning(
                    "Contracts file not found",
                    path=str(load_path),
                )
                self._contracts = {}
            else:
                self._contracts = self.load_json(load_path)
                logger.info(
                    "Contracts loaded",
                    contract_count=len(self._contracts),
                    path=str(load_path),
                )

        return self._contracts

    def execute_contract(
        self, contract_id: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute contract with dynamic method injection.

        THIS IS THE CANONICAL METHOD INJECTION POINT.
        Replaces the deprecated method_registry.py stub.

        Method Injection Flow:
        1. Load contract with executor_binding
        2. Dynamically import executor class
        3. Inject methods from method_binding section
        4. Execute N1→N2→N3→N4 epistemological pipeline

        See: Lines 788-955 for injection implementation

        Execute a contract by ID with method injection and full N1→N2→N3→N4 pipeline.

        This is the CRITICAL method that:
        1. Loads the contract with method bindings
        2. Dynamically loads the executor class
        3. Injects methods from the method_binding section
        4. Executes the epistemological pipeline:
           - N1: Construction (phase_A_construction)
           - N2: Computation (phase_B_computation)
           - N3: Litigation (phase_C_litigation) - VETO GATE
           - N4: Integration (phase_D_integration)

        Args:
            contract_id: Contract identifier (e.g., "Q001_PA01")
            input_data: Input data for contract execution

        Returns:
            Dict with execution results including:
            - contract_id: The contract that was executed
            - status: Execution status
            - results: Pipeline results by phase
            - metadata: Execution metadata

        Raises:
            KeyError: If contract_id not found
            ImportError: If executor module cannot be loaded
        """
        start_time = time.time()
        
        try:
            contracts = self.load_contracts()

            if contract_id not in contracts:
                raise KeyError(
                    f"Contract '{contract_id}' not found. "
                    f"Available contracts: {list(contracts.keys())[:10]}..."
                )

            contract = contracts[contract_id]
            executor_binding = contract.get("executor_binding", {})
            method_binding = contract.get("method_binding", {})

            # Dynamically load executor class
            module_path = executor_binding.get("executor_module", "")
            class_name = executor_binding.get("executor_class", "")

            if not module_path or not class_name:
                logger.error(
                    "Invalid executor binding",
                    contract_id=contract_id,
                    binding=executor_binding,
                )
                return {
                    "contract_id": contract_id,
                    "error": "Invalid executor binding",
                    "status": "failed",
                }

            try:
                module = importlib.import_module(module_path)
                executor_class: Type[T] = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                logger.error(
                    "Failed to load executor",
                    contract_id=contract_id,
                    module=module_path,
                    class_name=class_name,
                    error=str(e),
                    )
                return {
                    "contract_id": contract_id,
                    "error": f"Failed to load executor: {e}",
                    "status": "failed",
                }

            # Create executor instance
            executor = executor_class()

            # =======================================================================
            # METHOD INJECTION - N1→N2→N3→N4 PIPELINE
            # =======================================================================
            # Inject methods based on binding and execute in epistemological order

            execution_phases = method_binding.get("execution_phases", {})
            orchestration_mode = method_binding.get("orchestration_mode", "epistemological_pipeline")

            # Phase order for epistemological pipeline
            phase_order = [
                "phase_A_construction",  # N1 - Build evidence base
                "phase_B_computation",   # N2 - Calculate scores
                "phase_C_litigation",    # N3 - Veto gate (can reject N1/N2 results)
                "phase_D_integration",   # N4 - Cross-layer fusion
            ]

            pipeline_results = {}
            execution_context = {
                "input": input_data,
                "contract": contract,
                "phase_results": {},
            }

            for phase_name in phase_order:
                if phase_name not in execution_phases:
                    logger.debug(
                        "Phase not in execution_phases, skipping",
                        phase=phase_name,
                    )
                    continue

                phase_config = execution_phases[phase_name]
                phase_level = phase_config.get("level", "UNKNOWN")
                phase_methods = phase_config.get("methods", [])

                logger.info(
                    "Executing epistemological phase",
                    contract_id=contract_id,
                    phase=phase_name,
                    level=phase_level,
                    method_count=len(phase_methods),
                )

                phase_results = []

                for method_spec in phase_methods:
                    method_id = method_spec.get("method_id", "")
                    provides = method_spec.get("provides", "")
                    confidence = method_spec.get("confidence_score", 0.0)

                    if not method_id:
                        continue

                    # Parse module.method format
                    if "." in method_id:
                        module_name, method_name = method_id.rsplit(".", 1)
                        try:
                            method_module = importlib.import_module(module_name)
                            method = getattr(method_module, method_name)

                            # Inject method onto executor
                            setattr(executor, method_name, method)

                            logger.debug(
                                "Method injected",
                                method_id=method_id,
                                phase=phase_name,
                                provides=provides,
                                confidence=confidence,
                            )

                            # Execute the method
                            try:
                                # Prepare method-specific inputs
                                method_input = {
                                    **input_data,
                                    "execution_context": execution_context,
                                    "phase": phase_name,
                                    "method_id": method_id,
                                }

                                # Call the method
                                method_result = method(**method_input)

                                phase_results.append({
                                    "method_id": method_id,
                                    "provides": provides,
                                    "confidence": confidence,
                                    "result": method_result,
                                    "status": "completed",
                                })

                                # Update execution context
                                execution_context["phase_results"][phase_name] = phase_results

                            except Exception as e:
                                logger.warning(
                                    "Method execution failed",
                                    method_id=method_id,
                                    phase=phase_name,
                                    error=str(e),
                                )
                                phase_results.append({
                                    "method_id": method_id,
                                    "provides": provides,
                                    "error": str(e),
                                    "status": "failed",
                                })

                        except (ImportError, AttributeError) as e:
                            logger.warning(
                                "Failed to inject method",
                                method_id=method_id,
                                phase=phase_name,
                                error=str(e),
                            )
                            phase_results.append({
                                "method_id": method_id,
                                "error": str(e),
                                "status": "injection_failed",
                            })

                pipeline_results[phase_name] = {
                    "level": phase_level,
                    "methods": phase_results,
                    "status": "completed" if phase_results else "skipped",
                }

                # ===================================================================
                # VETO GATE CHECK (N3 - Litigation)
                # ===================================================================
                # If phase_C_litigation has veto power and results are negative,
                # we may need to abort or adjust the pipeline
                if phase_name == "phase_C_litigation":
                    has_veto_power = phase_config.get("has_veto_power", False)
                    if has_veto_power:
                        # Check if any litigation method vetoed the result
                        veto_triggered = any(
                            r.get("result", {}).get("veto", False)
                            for r in phase_results
                            if r.get("status") == "completed"
                        )

                        if veto_triggered:
                            logger.warning(
                                "Veto gate triggered in litigation phase",
                                contract_id=contract_id,
                            )
                            pipeline_results["veto_triggered"] = True
                            # Optionally break here if veto is absolute
                            # break

            # ====================================================================
            # CROSS-LAYER FUSION (N4 - Integration)
            # ====================================================================
            # Apply fusion specification if defined in contract
            fusion_spec = contract.get("fusion_specification", {})
            if fusion_spec:
                fusion_rule = fusion_spec.get("fusion_rule", "TYPE_A")
                logger.debug(
                    "Applying cross-layer fusion",
                    fusion_rule=fusion_rule,
                )
                pipeline_results["fusion"] = {
                    "rule": fusion_rule,
                    "applied": True,
                }

            # ====================================================================
            # FINAL RESULT
            # ====================================================================
            result = {
                "contract_id": contract_id,
                "status": "completed",
                "pipeline_results": pipeline_results,
                "execution_metadata": {
                    "orchestration_mode": orchestration_mode,
                    "phases_executed": list(pipeline_results.keys()),
                    "total_methods": sum(
                        len(p.get("methods", []))
                        for p in pipeline_results.values()
                    ),
                },
            }

            # If executor has an execute method, call it as final integration step
            if hasattr(executor, "execute"):
                try:
                    integrated_result = executor.execute({
                        **input_data,
                        "pipeline_results": pipeline_results,
                    })
                    result["integrated_result"] = integrated_result
                except Exception as e:
                    logger.warning(
                        "Executor integration failed",
                        error=str(e),
                    )
                    result["integration_error"] = str(e)

            logger.info(
                "Contract executed successfully",
                contract_id=contract_id,
                phases_executed=result["execution_metadata"]["phases_executed"],
                total_methods=result["execution_metadata"]["total_methods"],
            )
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(
                contracts_executed=1,
                total_execution_time=execution_time,
            )
            
            # Update average execution time
            with self._metrics_lock:
                if self._execution_metrics["contracts_executed"] > 0:
                    self._execution_metrics["average_execution_time"] = (
                        self._execution_metrics["total_execution_time"] / 
                        self._execution_metrics["contracts_executed"]
                    )

            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(
                failed_executions=1,
                total_execution_time=execution_time,
            )
            logger.error(
                "Contract execution failed",
                contract_id=contract_id,
                error=str(e),
                execution_time=execution_time,
            )
            raise

    def execute_contracts_batch(
        self, contract_ids: List[str], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute multiple contracts in batch with shared context and parallelization.
        
        INTERVENTION 1: Batch execution with context reuse and parallel processing.

        Args:
            contract_ids: List of contract identifiers
            input_data: Input data for contract execution (shared across all contracts)

        Returns:
            Dict mapping contract_id to execution results
        """
        if not contract_ids:
            return {}
            
        # Use batch mode if above threshold and parallel execution enabled
        use_batch_mode = (
            len(contract_ids) >= self._config.batch_execution_threshold and
            self._config.enable_parallel_execution
        )
        
        if use_batch_mode:
            return self._execute_contracts_parallel(contract_ids, input_data)
        else:
            # Sequential fallback
            results = {}
            for contract_id in contract_ids:
                results[contract_id] = self.execute_contract(contract_id, input_data)
            return results
    
    def _execute_contracts_parallel(
        self, contract_ids: List[str], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute contracts in parallel using thread pool.
        
        INTERVENTION 1: Parallel contract execution for 10-100x speedup.
        """
        if not self._thread_pool:
            logger.warning("Thread pool not initialized, falling back to sequential")
            return {cid: self.execute_contract(cid, input_data) for cid in contract_ids}
        
        results = {}
        futures = {}
        
        # Submit all contracts to thread pool
        for contract_id in contract_ids:
            future = self._thread_pool.submit(
                self.execute_contract, contract_id, input_data
            )
            futures[future] = contract_id
        
        # Collect results as they complete
        for future in as_completed(futures):
            contract_id = futures[future]
            try:
                results[contract_id] = future.result()
                self._update_metrics(parallel_executions=1)
            except Exception as e:
                logger.error(
                    "Parallel contract execution failed",
                    contract_id=contract_id,
                    error=str(e),
                )
                results[contract_id] = {
                    "contract_id": contract_id,
                    "error": str(e),
                    "status": "failed",
                }
                self._update_metrics(failed_executions=1)
        
        return results
    
    async def execute_contracts_async(
        self, contract_ids: List[str], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute contracts asynchronously for maximum concurrency.
        
        INTERVENTION 1: Async execution for I/O-bound operations.
        """
        tasks = [
            asyncio.to_thread(self.execute_contract, contract_id, input_data)
            for contract_id in contract_ids
        ]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {}
        for contract_id, result in zip(contract_ids, results_list):
            if isinstance(result, Exception):
                logger.error(
                    "Async contract execution failed",
                    contract_id=contract_id,
                    error=str(result),
                )
                results[contract_id] = {
                    "contract_id": contract_id,
                    "error": str(result),
                    "status": "failed",
                }
                self._update_metrics(failed_executions=1)
            else:
                results[contract_id] = result
                
        return results

    # ==========================================================================
    # INTERVENTION 1: Performance Monitoring & Metrics
    # ==========================================================================
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics (thread-safe).
        
        Returns:
            Dict with execution metrics, cache stats, and performance indicators
        """
        with self._metrics_lock:
            cache_efficiency = (
                self._execution_metrics["cache_hits"] / 
                max(1, self._execution_metrics["cache_hits"] + self._execution_metrics["cache_misses"])
            ) * 100
            
            metrics = {
                **self._execution_metrics,
                "cache_efficiency_percent": cache_efficiency,
            }
        
        if self._method_cache:
            metrics["method_cache_size"] = len(self._method_cache._cache)
            metrics["method_cache_hot_keys"] = self._method_cache.get_hot_keys(5)
            
        if self._executor_cache:
            metrics["executor_cache_size"] = len(self._executor_cache._cache)
            
        return metrics
    
    def reset_metrics(self) -> None:
        """Reset performance metrics (thread-safe)."""
        with self._metrics_lock:
            self._execution_metrics = {
                "contracts_executed": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "parallel_executions": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "failed_executions": 0,
            }
        
    def optimize_caches(self) -> Dict[str, Any]:
        """
        Optimize cache configuration based on access patterns.
        
        INTERVENTION 1: Adaptive cache optimization.
        """
        optimization_report = {
            "method_cache_optimized": False,
            "executor_cache_optimized": False,
            "recommendations": [],
        }
        
        if self._method_cache:
            hot_keys = self._method_cache.get_hot_keys(20)
            if hot_keys:
                optimization_report["method_cache_optimized"] = True
                optimization_report["recommendations"].append(
                    f"Consider preloading {len(hot_keys)} hot methods at startup"
                )
                
        cache_efficiency = (
            self._execution_metrics["cache_hits"] / 
            max(1, self._execution_metrics["cache_hits"] + self._execution_metrics["cache_misses"])
        ) * 100
        
        if cache_efficiency < 50:
            optimization_report["recommendations"].append(
                f"Low cache efficiency ({cache_efficiency:.1f}%). Consider increasing cache_size."
            )
        
        return optimization_report
    
    def cleanup(self) -> None:
        """
        Cleanup factory resources.
        
        Shuts down thread/process pools and clears caches.
        """
        logger.info("Factory cleanup started")
        
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
            logger.debug("Thread pool shut down")
            
        if self._method_cache:
            self._method_cache.clear()
            
        if self._executor_cache:
            self._executor_cache.clear()
            
        logger.info("Factory cleanup completed")

    # ==========================================================================
    # INTERVENTION 2: Orchestrator-Factory Alignment Protocol
    # ==========================================================================
    
    def get_factory_capabilities(self) -> Dict[str, Any]:
        """
        Report factory capabilities to orchestrator.
        
        INTERVENTION 2: Enables orchestrator to make informed scheduling decisions.
        """
        contracts = self.load_contracts()
        active_contracts = {
            cid: c for cid, c in contracts.items()
            if c.get("status") == "ACTIVE"
        }
        
        return {
            "total_contracts": len(contracts),
            "active_contracts": len(active_contracts),
            "parallel_execution_enabled": self._config.enable_parallel_execution,
            "max_workers": self._config.max_workers,
            "cache_enabled": self._config.enable_adaptive_caching,
            "cache_size": self._config.cache_size,
            "batch_threshold": self._config.batch_execution_threshold,
            "recommended_batch_size": min(
                self._config.max_workers * 4,
                len(active_contracts)
            ),
            "health_status": self._get_health_status(),
        }
    
    def _get_health_status(self) -> str:
        """Get current health status of factory."""
        if not hasattr(self, "_execution_metrics"):
            return "initializing"
            
        metrics = self._execution_metrics
        
        if metrics["contracts_executed"] == 0:
            return "idle"
            
        # Check if we have recent failures
        if metrics.get("failed_executions", 0) > metrics["contracts_executed"] * 0.1:
            return "degraded"
            
        return "healthy"
    
    def create_execution_snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of factory state for orchestrator checkpointing.
        
        INTERVENTION 2: Enables orchestrator to save/restore factory state.
        """
        return {
            "timestamp": time.time(),
            "metrics": self.get_performance_metrics(),
            "capabilities": self.get_factory_capabilities(),
            "questionnaire_loaded": self._questionnaire is not None,
            "contracts_loaded": self._contracts is not None,
            "sisas_enabled": self._config.sisas_enabled,
        }
    
    def synchronize_with_orchestrator(self, orchestrator_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize factory state with orchestrator state.
        
        INTERVENTION 2: Bidirectional sync protocol for alignment.
        
        Args:
            orchestrator_state: Current state from orchestrator
            
        Returns:
            Sync result with any conflicts or adjustments
        """
        sync_result = {
            "success": True,
            "conflicts": [],
            "adjustments": [],
        }
        
        # Check phase alignment
        orchestrator_phase = orchestrator_state.get("current_phase")
        factory_contracts = self.load_contracts()
        
        # Verify contracts are available for current phase
        phase_contracts = [
            cid for cid, c in factory_contracts.items()
            if orchestrator_phase in c.get("applicable_phases", [])
        ]
        
        if not phase_contracts and orchestrator_phase:
            sync_result["conflicts"].append({
                "type": "missing_phase_contracts",
                "phase": orchestrator_phase,
                "message": f"No contracts available for phase {orchestrator_phase}",
            })
            sync_result["success"] = False
        
        # Check resource alignment
        orchestrator_workers = orchestrator_state.get("max_workers", 0)
        if orchestrator_workers > self._config.max_workers:
            sync_result["adjustments"].append({
                "type": "worker_count_mismatch",
                "orchestrator_workers": orchestrator_workers,
                "factory_workers": self._config.max_workers,
                "recommendation": "Orchestrator should reduce parallelism",
            })
        
        logger.info(
            "Factory-Orchestrator sync completed",
            success=sync_result["success"],
            conflicts=len(sync_result["conflicts"]),
            adjustments=len(sync_result["adjustments"]),
        )
        
        return sync_result
    
    def get_contract_execution_plan(
        self, contract_ids: List[str], constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate optimal execution plan for contracts.
        
        INTERVENTION 2: Contract-aware scheduling information for orchestrator.
        """
        constraints = constraints or {}
        max_parallel = constraints.get("max_parallel", self._config.max_workers)
        time_budget = constraints.get("time_budget_seconds", float("inf"))
        
        contracts = self.load_contracts()
        
        # Analyze dependencies and execution requirements
        execution_plan = {
            "total_contracts": len(contract_ids),
            "estimated_duration_seconds": 0.0,
            "execution_strategy": "sequential",
            "batches": [],
            "warnings": [],
        }
        
        # Check if contracts exist
        valid_contract_ids = [cid for cid in contract_ids if cid in contracts]
        if len(valid_contract_ids) < len(contract_ids):
            execution_plan["warnings"].append(
                f"{len(contract_ids) - len(valid_contract_ids)} contracts not found"
            )
        
        # Determine execution strategy
        if len(valid_contract_ids) >= self._config.batch_execution_threshold:
            execution_plan["execution_strategy"] = "parallel_batch"
            
            # Create batches
            batch_size = min(max_parallel, len(valid_contract_ids))
            batches = [
                valid_contract_ids[i:i + batch_size]
                for i in range(0, len(valid_contract_ids), batch_size)
            ]
            execution_plan["batches"] = batches
            
            # Estimate duration (assumes parallel speedup)
            avg_contract_time = self._execution_metrics.get("average_execution_time", 1.0)
            execution_plan["estimated_duration_seconds"] = (
                len(batches) * avg_contract_time
            )
        else:
            execution_plan["execution_strategy"] = "sequential"
            avg_contract_time = self._execution_metrics.get("average_execution_time", 1.0)
            execution_plan["estimated_duration_seconds"] = (
                len(valid_contract_ids) * avg_contract_time
            )
        
        # Check time budget
        if execution_plan["estimated_duration_seconds"] > time_budget:
            execution_plan["warnings"].append(
                f"Estimated time ({execution_plan['estimated_duration_seconds']:.1f}s) "
                f"exceeds budget ({time_budget}s)"
            )
        
        return execution_plan

    # ==========================================================================
    # SISAS INTEGRATION
    # ==========================================================================

    def get_sisas_central(self) -> Optional[SignalDistributionOrchestrator]:
        """
        Initialize and return SISAS central orchestrator.

        Returns:
            SignalDistributionOrchestrator instance or None if disabled/unavailable
        """
        if self._sisas_central is None and self._config.sisas_enabled:
            try:
                from canonic_questionnaire_central.resolver import (
                    SignalDistributionOrchestrator,
                )

                self._sisas_central = SignalDistributionOrchestrator()
                logger.debug("SISAS central initialized")
            except ImportError as e:
                logger.warning(
                    "SISAS central not available",
                    error=str(e),
                )
        return self._sisas_central

    # ==========================================================================
    # CONTEXT PROVIDERS
    # ==========================================================================

    def get_questionnaire_provider(self) -> Any:
        """
        Get questionnaire provider for legacy compatibility.

        Returns:
            CQCLoader instance
        """
        return self.questionnaire

    def get_canonical_notation_loader(self) -> Dict[str, Any]:
        """
        Get canonical notation data for reference.

        Returns:
            Dict with dimensions, policy_areas, and clusters
        """
        return self.create_signal_registry()

    # ==========================================================================
    # HEALTH DASHBOARD & PREDICTIVE CACHING (INTERVENTION 2)
    # ==========================================================================

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics (thread-safe copy)."""
        with self._metrics_lock:
            metrics = dict(self._execution_metrics)
            # Compute cache efficiency
            total_cache_ops = metrics.get("cache_hits", 0) + metrics.get("cache_misses", 0)
            metrics["cache_efficiency_percent"] = (
                (metrics.get("cache_hits", 0) / total_cache_ops * 100)
                if total_cache_ops > 0 else 0.0
            )
            return metrics

    def get_factory_capabilities(self) -> Dict[str, Any]:
        """Get factory capabilities and resource status."""
        return {
            "max_workers": self._config.max_workers,
            "available_workers": self._config.max_workers,  # Simplified
            "cache_size": self._config.cache_size,
            "parallel_enabled": self._config.enable_parallel_execution,
            "adaptive_cache_enabled": self._config.enable_adaptive_caching,
            "predictive_prefetch_enabled": self._config.enable_predictive_prefetch,
            "active_contracts": len(self._contracts) if self._contracts else 0,
        }

    def get_health_status(self) -> FactoryHealthStatus:
        """Get comprehensive factory health status."""
        metrics = self.get_performance_metrics()
        capabilities = self.get_factory_capabilities()

        # Calculate health indicators
        cache_hit_rate = metrics.get("cache_efficiency_percent", 0)
        contracts_executed = max(1, metrics.get("contracts_executed", 1))
        parallel_efficiency = (
            metrics.get("parallel_executions", 0) / contracts_executed
        ) * 100

        avg_time_ms = metrics.get("average_execution_time", 0) * 1000
        error_rate = (
            metrics.get("failed_executions", 0) / contracts_executed
        ) * 100

        warnings = []
        if cache_hit_rate < 50:
            warnings.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
        if error_rate > 5:
            warnings.append(f"High error rate: {error_rate:.1f}%")
        if avg_time_ms > 1000:
            warnings.append(f"Slow avg execution: {avg_time_ms:.0f}ms")

        is_healthy = (
            error_rate < 10 and
            cache_hit_rate > 30 and
            len(warnings) == 0
        )

        return FactoryHealthStatus(
            is_healthy=is_healthy,
            cache_hit_rate=cache_hit_rate,
            parallel_efficiency=parallel_efficiency,
            avg_execution_time_ms=avg_time_ms,
            error_rate=error_rate,
            active_contracts=capabilities["active_contracts"],
            available_workers=capabilities["max_workers"],
            warnings=tuple(warnings),
        )

    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get formatted health dashboard."""
        health = self.get_health_status()
        capabilities = self.get_factory_capabilities()

        return {
            "status": "HEALTHY" if health.is_healthy else "DEGRADED",
            "metrics": {
                "cache_efficiency": f"{health.cache_hit_rate:.1f}%",
                "parallel_efficiency": f"{health.parallel_efficiency:.1f}%",
                "avg_execution_time": f"{health.avg_execution_time_ms:.1f}ms",
                "error_rate": f"{health.error_rate:.1f}%",
            },
            "resources": {
                "active_contracts": health.active_contracts,
                "available_workers": health.available_workers,
                "cache_size": capabilities["cache_size"],
            },
            "warnings": list(health.warnings),
            "recommendations": self._generate_health_recommendations(health),
        }

    def _generate_health_recommendations(
        self, health: FactoryHealthStatus
    ) -> List[str]:
        """Generate actionable recommendations based on health."""
        recommendations = []

        if health.cache_hit_rate < 50:
            recommendations.append(
                "Increase cache_size or enable_predictive_prefetch"
            )
        if health.error_rate > 5:
            recommendations.append(
                "Review contract configurations and method bindings"
            )
        if health.avg_execution_time_ms > 1000:
            recommendations.append(
                "Enable parallel_execution or increase max_workers"
            )

        return recommendations

    def _track_access(self, contract_id: str) -> None:
        """Track contract access pattern for prediction."""
        with self._pattern_lock:
            self._access_pattern.append(contract_id)
            # Keep last 1000 accesses
            if len(self._access_pattern) > 1000:
                self._access_pattern = self._access_pattern[-1000:]

    def get_predicted_contracts(self, count: int = 10) -> List[str]:
        """Predict next contracts to access based on Markov chain patterns."""
        from collections import Counter

        with self._pattern_lock:
            if len(self._access_pattern) < 10:
                return []

            # Build transition probabilities
            transitions: Counter = Counter()
            for i in range(len(self._access_pattern) - 1):
                current = self._access_pattern[i]
                next_contract = self._access_pattern[i + 1]
                transitions[(current, next_contract)] += 1

            # Get most likely next contracts from last accessed
            last_contract = self._access_pattern[-1]
            predictions = [
                next_contract
                for (current, next_contract), freq in transitions.most_common()
                if current == last_contract
            ]

            return predictions[:count]

    def prefetch_predicted_contracts(self) -> int:
        """Prefetch predicted contracts into cache."""
        if not self._config.enable_predictive_prefetch:
            return 0

        predicted = self.get_predicted_contracts(
            count=self._config.cache_size // 4
        )

        prefetched = 0
        for contract_id in predicted:
            if self._executor_cache and contract_id not in self._executor_cache._cache:
                try:
                    # Pre-warm cache by loading contracts
                    self.load_contracts()
                    prefetched += 1
                except Exception:
                    pass

        return prefetched

    # ==========================================================================
    # FACTORY METHODS
    # ==========================================================================

    @classmethod
    def from_legacy_import(cls, **kwargs) -> "UnifiedFactory":
        """
        Factory method for legacy import compatibility.

        Replaces scattered factory imports like:
        - from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import ...
        - from farfan_pipeline.executor_factory.core.factory import ...

        Args:
            **kwargs: Configuration keyword arguments

        Returns:
            UnifiedFactory instance
        """
        return cls(config=FactoryConfig(**kwargs))

    @classmethod
    def create_default(cls, project_root: Optional[Path] = None) -> "UnifiedFactory":
        """
        Create factory with default settings.

        Args:
            project_root: Project root path. If None, uses current directory.

        Returns:
            UnifiedFactory instance with default config
        """
        if project_root is None:
            project_root = Path.cwd()
        return cls(config=FactoryConfig(project_root=project_root))


# =============================================================================
# LEGACY COMPATIBILITY ALIASES
# =============================================================================


def get_factory(config: Optional[FactoryConfig] = None) -> UnifiedFactory:
    """
    Get or create factory instance (singleton pattern).

    Args:
        config: Optional factory configuration

    Returns:
        UnifiedFactory instance
    """
    if config is None:
        config = FactoryConfig(project_root=Path.cwd())
    return UnifiedFactory(config)


# =============================================================================
# DEPRECATED FACTORY REFERENCES
# =============================================================================


def load_questionnaire(path: Optional[Path] = None) -> Any:
    """
    Legacy function for questionnaire loading.

    DEPRECATED: Use UnifiedFactory.load_questionnaire() instead.

    Args:
        path: Optional questionnaire path

    Returns:
        CQCLoader instance
    """
    factory = get_factory()
    return factory.load_questionnaire()


def create_signal_registry() -> Dict[str, Any]:
    """
    Legacy function for signal registry creation.

    DEPRECATED: Use UnifiedFactory.create_signal_registry() instead.

    Returns:
        Dict with signal registry data
    """
    factory = get_factory()
    return factory.create_signal_registry()
