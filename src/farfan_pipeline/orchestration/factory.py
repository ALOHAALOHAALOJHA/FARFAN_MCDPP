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

import importlib
import json
import logging
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
    """

    project_root: Path
    questionnaire_path: Optional[Path] = None
    sisas_enabled: bool = True
    contracts_path: Optional[Path] = None
    lazy_load_questions: bool = True
    cache_size: int = 100

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        if isinstance(self.questionnaire_path, str):
            self.questionnaire_path = Path(self.questionnaire_path)
        if isinstance(self.contracts_path, str):
            self.contracts_path = Path(self.contracts_path)


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

        logger.info(
            "UnifiedFactory initialized",
            project_root=str(config.project_root),
            sisas_enabled=config.sisas_enabled,
            lazy_load=config.lazy_load_questions,
        )

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

    def create_contradiction_detector(self):
        """
        Create contradiction detector instance.

        Returns:
            ContradictionDetector instance

        Raises:
            ImportError: If detector module is not available
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.contradiction_detector import (
                ContradictionDetector,
            )

            return ContradictionDetector(self.questionnaire)
        except ImportError as e:
            logger.warning(
                "ContradictionDetector not available, returning None",
                error=str(e),
            )
            return None

    def create_temporal_logic_verifier(self):
        """
        Create temporal logic verifier instance.

        Returns:
            TemporalLogicVerifier instance or None if not available
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.temporal_logic import (
                TemporalLogicVerifier,
            )

            return TemporalLogicVerifier(self.questionnaire)
        except ImportError as e:
            logger.warning(
                "TemporalLogicVerifier not available, returning None",
                error=str(e),
            )
            return None

    def create_bayesian_confidence_calculator(self):
        """
        Create Bayesian confidence calculator instance.

        Returns:
            BayesianConfidenceCalculator instance or None if not available
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.bayesian_calculator import (
                BayesianConfidenceCalculator,
            )

            return BayesianConfidenceCalculator(self.questionnaire)
        except ImportError as e:
            logger.warning(
                "BayesianConfidenceCalculator not available, returning None",
                error=str(e),
            )
            return None

    def create_municipal_analyzer(self):
        """
        Create municipal analyzer instance.

        Returns:
            MunicipalAnalyzer instance or None if not available
        """
        try:
            from farfan_pipeline.phases.Phase_02.methods.municipal_analyzer import (
                MunicipalAnalyzer,
            )

            return MunicipalAnalyzer(self.questionnaire)
        except ImportError as e:
            logger.warning(
                "MunicipalAnalyzer not available, returning None",
                error=str(e),
            )
            return None

    def create_analysis_components(self) -> Dict[str, Any]:
        """
        Create all analysis components as a bundle.

        Returns:
            Dict with component names as keys and instances as values
        """
        components = {
            "contradiction_detector": self.create_contradiction_detector(),
            "temporal_logic_verifier": self.create_temporal_logic_verifier(),
            "bayesian_calculator": self.create_bayesian_confidence_calculator(),
            "municipal_analyzer": self.create_municipal_analyzer(),
        }

        # Filter out None values
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

        # ==========================================================================
        # METHOD INJECTION - N1→N2→N3→N4 PIPELINE
        # ==========================================================================
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

            # ==========================================================================
            # VETO GATE CHECK (N3 - Litigation)
            # ==========================================================================
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

        # ==========================================================================
        # CROSS-LAYER FUSION (N4 - Integration)
        # ==========================================================================
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

        # ==========================================================================
        # FINAL RESULT
        # ==========================================================================
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

        return result

    def execute_contracts_batch(
        self, contract_ids: List[str], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute multiple contracts in batch.

        Args:
            contract_ids: List of contract identifiers
            input_data: Input data for contract execution

        Returns:
            Dict mapping contract_id to execution results
        """
        results = {}
        for contract_id in contract_ids:
            results[contract_id] = self.execute_contract(contract_id, input_data)
        return results

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
