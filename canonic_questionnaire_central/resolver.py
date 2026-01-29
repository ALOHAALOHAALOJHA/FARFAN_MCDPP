"""
Canonical Questionnaire Resolver
================================

SINGLE POINT OF TRUTH for questionnaire data assembly.

This resolver:
1. Assembles modular assets into unified QuestionnairePort-compatible payload
2. Maintains hash integrity across modular structure
3. Provides provenance tracking for governance
4. Is the ONLY authorized source for UnifiedFactory (replaces deprecated AnalysisPipelineFactory)
5. [v2.0] Integrates Signal Distribution Orchestrator for active signal routing

GOVERNANCE:
- All questionnaire access MUST go through this resolver
- Direct file reads are PROHIBITED outside this module
- SISAS receives questionnaire from UnifiedFactory, which uses this resolver
- [v2.0] Signal dispatch goes through SDO for validation and routing

Factory Migration:
- ❌ DEPRECATED: AnalysisPipelineFactory (phase2_10_00_factory.py - stub only)
- ✅ CURRENT: UnifiedFactory (orchestration/factory.py)

Author: F. A. R.F.A.N Pipeline Team
Version: 2.0.1
Date: 2026-01-23
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# Import SISAS 2.0 Core (SDO)
try:
    from .core.signal_distribution_orchestrator import SignalDistributionOrchestrator
    from .core.signal import Signal, SignalType, SignalScope, SignalProvenance
    SDO_AVAILABLE = True
except ImportError:
    SDO_AVAILABLE = False
    logger.warning("SDO not available - running in v1.x compatibility mode")


# ============================================================================
# PROTOCOL DEFINITION (QuestionnairePort compatibility)
# ============================================================================


@runtime_checkable
class QuestionnairePort(Protocol):
    """
    Minimal questionnaire contract for SISAS compatibility.

    Any object implementing this protocol can be used with:
    - QuestionnaireSignalRegistry
    - Orchestrator
    - All downstream consumers
    """

    @property
    def data(self) -> dict[str, Any]:
        """Raw questionnaire data dictionary."""
        ...

    @property
    def version(self) -> str:
        """Semantic version of the questionnaire."""
        ...

    @property
    def sha256(self) -> str:
        """SHA-256 hash of the questionnaire for integrity verification."""
        ...

    @property
    def micro_questions(self) -> list[dict[str, Any]]:
        """List of 300 micro-level questions (Q001-Q300)."""
        ...

    def __iter__(self):
        """Iterator over micro questions for compatibility."""
        ...


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class AssemblyProvenance:
    """Immutable provenance record for assembled questionnaire."""

    assembly_timestamp: str
    resolver_version: str
    source_file_count: int
    source_paths: tuple[str, ...]
    assembly_duration_ms: float
    git_commit: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "assembly_timestamp": self.assembly_timestamp,
            "resolver_version": self.resolver_version,
            "source_file_count": self.source_file_count,
            "source_paths": list(self.source_paths),
            "assembly_duration_ms": self.assembly_duration_ms,
            "git_commit": self.git_commit,
        }


@dataclass
class AssemblyMetrics:
    """Metrics for resolver observability."""

    files_loaded: int = 0
    questions_assembled: int = 0
    patterns_merged: int = 0
    validation_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class CanonicalQuestionnaire:
    """
    Assembled canonical questionnaire implementing QuestionnairePort.

    This is the object passed to:
    - UnifiedFactory (replaces deprecated AnalysisPipelineFactory)
    - QuestionnaireSignalRegistry (via UnifiedFactory)
    - Orchestrator (via UnifiedFactory)
    """

    _data: dict[str, Any]
    _sha256: str
    _version: str
    _micro_questions: list[dict[str, Any]]
    source: str  # 'modular_resolver' or 'legacy_monolith'
    provenance: AssemblyProvenance

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def version(self) -> str:
        return self._version

    @property
    def sha256(self) -> str:
        return self._sha256

    @property
    def micro_questions(self) -> list[dict[str, Any]]:
        return self._micro_questions

    def __iter__(self):
        """Iterator over micro questions for compatibility."""
        return iter(self._micro_questions)


# ============================================================================
# RESOLVER EXCEPTIONS
# ============================================================================


class ResolverError(Exception):
    """Base exception for resolver errors."""

    pass


class AssemblyError(ResolverError):
    """Error during questionnaire assembly."""

    pass


class IntegrityError(ResolverError):
    """Hash or integrity verification failure."""

    pass


class ValidationError(ResolverError):
    """Validation error during assembly."""

    pass


# ============================================================================
# RESOLVER IMPLEMENTATION
# ============================================================================


class CanonicalQuestionnaireResolver:
    """
    Assembles modular questionnaire structure into unified payload.

    DESIGN PRINCIPLES:
    1. SINGLE SOURCE: Only authorized way to load questionnaire
    2. IMMUTABLE OUTPUT: Returns frozen CanonicalQuestionnaire
    3. HASH INTEGRITY: Computes deterministic hash over assembled content
    4. PROVENANCE: Tracks all source files and assembly metadata
    5. LAZY CACHING: Caches assembled payload until invalidated
    6. [v2.0] SIGNAL ROUTING: Integrates SDO for active signal dispatch

    USAGE:
        resolver = CanonicalQuestionnaireResolver()
        questionnaire = resolver.resolve()

        # Pass to UnifiedFactory (NEW - replaces deprecated AnalysisPipelineFactory)
        from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig
        factory = UnifiedFactory(config=FactoryConfig(project_root=Path(".")))
        
        # Access SDO for signal dispatch
        resolver.sdo.dispatch(signal)

    THREAD SAFETY: Not thread-safe. Use separate instances per thread.
    """

    RESOLVER_VERSION = "2.0.0"
    EXPECTED_QUESTION_COUNT = 300
    EXPECTED_DIMENSION_COUNT = 6
    EXPECTED_POLICY_AREA_COUNT = 10
    EXPECTED_CLUSTER_COUNT = 4

    def __init__(
        self,
        root: Path | None = None,
        strict_mode: bool = True,
        cache_enabled: bool = True,
        sdo_enabled: bool = True,
    ):
        """
        Initialize resolver.

        Args:
            root: Root path to canonic_questionnaire_central/
                  Defaults to this file's parent directory.
            strict_mode:  If True, fail on any validation error.
                        If False, log warnings and continue.
            cache_enabled: If True, cache assembled payload.
            sdo_enabled: If True, initialize Signal Distribution Orchestrator.
        """
        self._root = root or Path(__file__).resolve().parent
        self._strict_mode = strict_mode
        self._cache_enabled = cache_enabled
        self._sdo_enabled = sdo_enabled and SDO_AVAILABLE

        # Cached payload
        self._cached_questionnaire: CanonicalQuestionnaire | None = None
        self._cache_hash: str | None = None

        # Metrics
        self._metrics = AssemblyMetrics()
        
        # Initialize SDO (Signal Distribution Orchestrator)
        self._sdo: SignalDistributionOrchestrator | None = None
        if self._sdo_enabled:
            self._init_sdo()

        # Validate root exists
        if not self._root.exists():
            raise ResolverError(f"Root path does not exist: {self._root}")

        logger.info(
            "resolver_initialized",
            root=str(self._root),
            strict_mode=strict_mode,
            cache_enabled=cache_enabled,
            sdo_enabled=self._sdo_enabled,
            resolver_version=self.RESOLVER_VERSION,
        )
    
    def _init_sdo(self) -> None:
        """Initialize Signal Distribution Orchestrator with routing rules."""
        rules_path = self._root / "_registry" / "irrigation_validation_rules.json"
        
        if rules_path.exists():
            self._sdo = SignalDistributionOrchestrator(str(rules_path))
        else:
            # Use defaults
            self._sdo = SignalDistributionOrchestrator()
            logger.warning("SDO initialized with default rules - irrigation_validation_rules.json not found")
        
        # Register phase consumers
        self._register_phase_consumers()
        
        logger.info("sdo_initialized", rules_path=str(rules_path), consumers_registered=len(self._sdo.consumers))
    
    def _register_phase_consumers(self) -> None:
        """Register consumers for each pipeline phase."""
        if not self._sdo:
            return
        
        # Phase 0: Assembly (this resolver handles static load)
        self._sdo.register_consumer(
            consumer_id="phase_0_assembly",
            scopes=[{"phase": "phase_00", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["STATIC_LOAD", "SIGNAL_PACK"],
            handler=self._handle_phase_0_signal
        )
        
        # Phase 1: Extraction (MC01-MC10)
        self._sdo.register_consumer(
            consumer_id="phase_1_extraction",
            scopes=[{"phase": "phase_01", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=[
                "NUMERIC_PARSING", "FINANCIAL_ANALYSIS", "CURRENCY_NORMALIZATION",
                "CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION", "VERB_ANALYSIS",
                "NER_EXTRACTION", "ENTITY_RESOLUTION", "COREFERENCE",
                "STRUCTURAL_PARSING", "SECTION_DETECTION",
                "NORMATIVE_LOOKUP", "CITATION_PARSING",
                "HIERARCHY_PARSING", "TREE_CONSTRUCTION",
                "TRIPLET_EXTRACTION",
                "POPULATION_PARSING", "DEMOGRAPHIC_ANALYSIS",
                "TEMPORAL_PARSING", "DATE_NORMALIZATION",
                "SEMANTIC_SIMILARITY", "EMBEDDING_LOOKUP"
            ],
            handler=self._handle_phase_1_signal
        )
        
        # Phase 2: Enrichment
        self._sdo.register_consumer(
            consumer_id="phase_2_enrichment",
            scopes=[{"phase": "phase_02", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["PATTERN_MATCHING", "REGEX_ENGINE", "KEYWORD_MATCHING", "TF_IDF", "ENTITY_LINKING"],
            handler=self._handle_phase_2_signal
        )
        
        # Phase 3: Validation
        self._sdo.register_consumer(
            consumer_id="phase_3_validation",
            scopes=[{"phase": "phase_03", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NORMATIVE_LOOKUP", "COMPLIANCE_CHECK", "ENTITY_RESOLUTION", "EXISTENCE_CHECK", "CONSISTENCY_CHECK"],
            handler=self._handle_phase_3_signal
        )
        
        # Phases 4-6: Scoring
        for phase_num in [4, 5, 6]:
            self._sdo.register_consumer(
                consumer_id=f"phase_{phase_num:02d}_scoring",
                scopes=[{"phase": f"phase_{phase_num:02d}", "policy_area": "ALL", "slot": "ALL"}],
                capabilities=["SCORING_ENGINE", "WEIGHT_APPLICATION"],
                handler=self._handle_scoring_signal
            )
        
        # Phase 7: MESO Aggregation
        self._sdo.register_consumer(
            consumer_id="phase_7_meso",
            scopes=[{"phase": "phase_07", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["AGGREGATION_ENGINE", "CLUSTER_SCORING", "CLUSTER_ROUTING"],
            handler=self._handle_meso_signal
        )
        
        # Phase 8: MACRO Aggregation
        self._sdo.register_consumer(
            consumer_id="phase_8_macro",
            scopes=[{"phase": "phase_08", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["AGGREGATION_ENGINE", "HOLISTIC_SCORING", "FINAL_ASSEMBLY"],
            handler=self._handle_macro_signal
        )
        
        # Phase 9: Report
        self._sdo.register_consumer(
            consumer_id="phase_9_report",
            scopes=[{"phase": "phase_09", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["TEMPLATE_ENGINE", "MARKDOWN_GENERATION"],
            handler=self._handle_report_signal
        )
    
    # Signal handlers (placeholder implementations - to be wired to actual phase processors)
    def _handle_phase_0_signal(self, signal: Signal) -> None:
        """Handle Phase 0 (Assembly) signals."""
        logger.debug("phase_0_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_phase_1_signal(self, signal: Signal) -> None:
        """Handle Phase 1 (Extraction) signals - MC01-MC10."""
        logger.debug("phase_1_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
        # Store in extraction results buffer
        if not hasattr(self, '_extraction_buffer'):
            self._extraction_buffer = []
        self._extraction_buffer.append(signal)
    
    def _handle_phase_2_signal(self, signal: Signal) -> None:
        """Handle Phase 2 (Enrichment) signals."""
        logger.debug("phase_2_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_phase_3_signal(self, signal: Signal) -> None:
        """Handle Phase 3 (Validation) signals."""
        logger.debug("phase_3_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_scoring_signal(self, signal: Signal) -> None:
        """Handle Phases 4-6 (Scoring) signals."""
        logger.debug("scoring_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_meso_signal(self, signal: Signal) -> None:
        """Handle Phase 7 (MESO Aggregation) signals."""
        logger.debug("meso_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_macro_signal(self, signal: Signal) -> None:
        """Handle Phase 8 (MACRO Aggregation) signals."""
        logger.debug("macro_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    def _handle_report_signal(self, signal: Signal) -> None:
        """Handle Phase 9 (Report) signals."""
        logger.debug("report_signal_received", signal_id=signal.signal_id, signal_type=str(signal.signal_type))
    
    @property
    def sdo(self) -> SignalDistributionOrchestrator | None:
        """Access the Signal Distribution Orchestrator."""
        return self._sdo
    
    def dispatch_signal(self, signal: Signal) -> bool:
        """
        Dispatch a signal through the SDO.
        
        This is the primary method for sending signals into the SISAS system.
        
        Args:
            signal: The Signal to dispatch
            
        Returns:
            True if signal was delivered to at least one consumer
        """
        if not self._sdo:
            logger.warning("dispatch_failed_sdo_disabled", signal_id=signal.signal_id)
            return False
        
        return self._sdo.dispatch(signal)
    
    def get_sdo_health(self) -> dict[str, Any]:
        """Get SDO health check results."""
        if not self._sdo:
            return {"status": "DISABLED", "reason": "SDO not enabled"}
        return self._sdo.health_check()

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def resolve(
        self,
        expected_hash: str | None = None,
        force_rebuild: bool = False,
    ) -> CanonicalQuestionnaire:
        """
        Resolve modular structure into CanonicalQuestionnaire.

        This is the PRIMARY entry point for questionnaire loading.

        Args:
            expected_hash: If provided, verify assembled hash matches.
            force_rebuild: If True, ignore cache and rebuild.

        Returns:
            CanonicalQuestionnaire implementing QuestionnairePort

        Raises:
            AssemblyError: If assembly fails
            IntegrityError: If hash verification fails
        """
        # Check cache
        if self._cache_enabled and not force_rebuild and self._cached_questionnaire is not None:
            logger.debug("resolver_cache_hit")
            if expected_hash and self._cached_questionnaire.sha256 != expected_hash:
                raise IntegrityError(
                    f"Cached questionnaire hash mismatch. "
                    f"Expected: {expected_hash[:16]}..., "
                    f"Got: {self._cached_questionnaire.sha256[:16]}..."
                )
            return self._cached_questionnaire

        # Build fresh
        start_time = time.perf_counter()
        self._metrics = AssemblyMetrics()  # Reset metrics

        try:
            questionnaire = self._assemble()

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "questionnaire_assembled",
                sha256=questionnaire.sha256[:16],
                version=questionnaire.version,
                question_count=len(questionnaire.micro_questions),
                elapsed_ms=round(elapsed_ms, 2),
                source_files=questionnaire.provenance.source_file_count,
            )

            # Verify hash if expected
            if expected_hash and questionnaire.sha256 != expected_hash:
                raise IntegrityError(
                    f"Assembled questionnaire hash mismatch. "
                    f"Expected: {expected_hash[:16]}..., "
                    f"Got: {questionnaire.sha256[:16]}..."
                )

            # Cache
            if self._cache_enabled:
                self._cached_questionnaire = questionnaire

            return questionnaire

        except Exception as e:
            logger.error(
                "assembly_failed",
                error=str(e),
                metrics=self._metrics.__dict__,
            )
            raise

    def invalidate_cache(self) -> None:
        """Invalidate cached questionnaire."""
        self._cached_questionnaire = None
        self._cache_hash = None
        logger.info("resolver_cache_invalidated")

    def get_metrics(self) -> dict[str, Any]:
        """Get resolver metrics for observability."""
        metrics = {
            "files_loaded": self._metrics.files_loaded,
            "questions_assembled": self._metrics.questions_assembled,
            "patterns_merged": self._metrics.patterns_merged,
            "validation_errors": self._metrics.validation_errors,
            "warnings": self._metrics.warnings,
            "cache_enabled": self._cache_enabled,
            "cache_populated": self._cached_questionnaire is not None,
            "sdo_enabled": self._sdo_enabled,
        }
        
        # Add SDO metrics if available
        if self._sdo:
            metrics["sdo_metrics"] = self._sdo.get_metrics()
            metrics["sdo_health"] = self._sdo.health_check()
        
        return metrics

    # ========================================================================
    # ASSEMBLY PIPELINE
    # ========================================================================

    def _assemble(self) -> CanonicalQuestionnaire:
        """
        Execute full assembly pipeline.

        Assembly Order (dependencies respected):
        1. Load canonical_notation.json (foundation)
        2. Load governance/ (integrity, versioning)
        3. Load dimensions/ (DIM01-DIM06)
        4. Load policy_areas/ (PA01-PA10)
        5. Load clusters/ (CL01-CL04)
        6. Load scoring/ (modalities, levels)
        7. Load patterns/ (merged index)
        8. Load semantic/ (embedding config)
        9. Load cross_cutting/ (themes, interdependencies)
        10. Load meso_questions.json
        11. Load macro_question.json
        12. Assemble micro_questions from dimensions × policy_areas
        13. Merge all into unified structure
        14. Compute integrity hash
        15. Create provenance record
        """
        source_paths: list[str] = []
        start_time = time.perf_counter()

        # 1. Canonical Notation (foundation) - located in config/
        canonical_notation = self._load_json("config/canonical_notation.json")
        source_paths.append(str(self._root / "config/canonical_notation.json"))

        # 2. Governance
        governance = self._load_governance()
        source_paths.extend(self._get_dir_paths("governance"))

        # 3. Dimensions
        dimensions = self._load_dimensions()
        source_paths.extend(self._get_dir_paths("dimensions"))

        # 4. Policy Areas
        policy_areas = self._load_policy_areas()
        source_paths.extend(self._get_dir_paths("policy_areas"))

        # 5. Clusters
        clusters = self._load_clusters()
        source_paths.extend(self._get_dir_paths("clusters"))

        # 6. Scoring
        scoring = self._load_scoring()
        source_paths.extend(self._get_dir_paths("scoring"))

        # 7. Patterns
        patterns = self._load_patterns()
        source_paths.extend(self._get_dir_paths("patterns"))

        # 8. Semantic
        semantic = self._load_semantic()
        source_paths.extend(self._get_dir_paths("semantic"))

        # 9. Cross-Cutting
        cross_cutting = self._load_cross_cutting()
        source_paths.extend(self._get_dir_paths("cross_cutting"))

        # 10. MESO Questions - located in _registry/questions/
        meso_questions = self._load_json_safe("_registry/questions/meso_questions.json", default=[])
        if (self._root / "_registry/questions/meso_questions.json").exists():
            source_paths.append(str(self._root / "_registry/questions/meso_questions.json"))

        # 11. MACRO Question - located in _registry/questions/
        macro_question = self._load_json_safe("_registry/questions/macro_question.json", default={})
        if (self._root / "_registry/questions/macro_question.json").exists():
            source_paths.append(str(self._root / "_registry/questions/macro_question.json"))

        # 12. Assemble Micro Questions
        micro_questions = self._assemble_micro_questions(dimensions, policy_areas, patterns)

        # Validate counts
        self._validate_counts(
            dimensions=dimensions,
            policy_areas=policy_areas,
            clusters=clusters,
            micro_questions=micro_questions,
        )

        # 13. Merge into unified structure
        assembled_data = {
            "schema_version": "2.0.0",
            "version": governance.get("versioning", {}).get("current_version", "1.0.0"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "canonical_notation": canonical_notation,
            "blocks": {
                "micro_questions": micro_questions,
                "meso_questions": meso_questions,
                "macro_question": macro_question,
                "scoring": scoring,
                "semantic_layers": semantic,
                "niveles_abstraccion": {
                    "clusters": clusters,
                    "policy_areas": list(policy_areas.values()),
                },
            },
            "integrity": governance.get("integrity", {}),
            "observability": governance.get("observability", {}),
            "cross_cutting": cross_cutting,
            "patterns": patterns,
        }

        # 14. Compute integrity hash
        sha256 = self._compute_hash(assembled_data)

        # 15. Create provenance
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        provenance = AssemblyProvenance(
            assembly_timestamp=datetime.now(timezone.utc).isoformat(),
            resolver_version=self.RESOLVER_VERSION,
            source_file_count=len(source_paths),
            source_paths=tuple(source_paths),
            assembly_duration_ms=round(elapsed_ms, 2),
            git_commit=self._get_git_commit(),
        )

        # Add provenance to data
        assembled_data["provenance"] = provenance.to_dict()

        return CanonicalQuestionnaire(
            _data=assembled_data,
            _sha256=sha256,
            _version=assembled_data["version"],
            _micro_questions=micro_questions,
            source="modular_resolver",
            provenance=provenance,
        )

    # ========================================================================
    # COMPONENT LOADERS
    # ========================================================================

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        """Load JSON file from root."""
        path = self._root / relative_path
        if not path.exists():
            raise AssemblyError(f"Required file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._metrics.files_loaded += 1
        return data

    def _load_json_safe(
        self,
        relative_path: str,
        default: Any = None,
    ) -> Any:
        """Load JSON file, return default if not found."""
        path = self._root / relative_path
        if not path.exists():
            return default

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._metrics.files_loaded += 1
        return data

    def _get_dir_paths(self, dirname: str) -> list[str]:
        """Get all JSON file paths in directory."""
        dir_path = self._root / dirname
        if not dir_path.exists():
            return []

        paths = []
        for item in dir_path.rglob("*.json"):
            paths.append(str(item))
        return paths

    def _load_governance(self) -> dict[str, Any]:
        """Load governance configuration."""
        governance_dir = self._root / "governance"
        if not governance_dir.exists():
            return {}

        result = {}
        for name in ["integrity", "observability", "versioning"]:
            path = governance_dir / f"{name}.json"
            if path.exists():
                result[name] = self._load_json(f"governance/{name}.json")

        return result

    def _load_dimensions(self) -> dict[str, dict[str, Any]]:
        """Load all dimension definitions."""
        dimensions_dir = self._root / "dimensions"
        if not dimensions_dir.exists():
            raise AssemblyError("dimensions/ directory not found")

        dimensions = {}
        for dim_dir in sorted(dimensions_dir.iterdir()):
            if not dim_dir.is_dir() or dim_dir.name.startswith("_"):
                continue

            dim_id = dim_dir.name  # e.g., "DIM01_INSUMOS"
            # Extract just the DIM ID part
            dim_code = dim_id.split("_")[0] if "_" in dim_id else dim_id
            
            metadata_path = dim_dir / "metadata.json"
            questions_path = dim_dir / "questions.json"

            if metadata_path.exists():
                questions_data = []
                if questions_path.exists():
                    loaded_questions = self._load_json(f"dimensions/{dim_id}/questions.json")
                    # Extract questions array from wrapper object
                    if isinstance(loaded_questions, dict):
                        questions_data = loaded_questions.get("questions", [])
                    elif isinstance(loaded_questions, list):
                        questions_data = loaded_questions
                    else:
                        logger.warning(
                            "dimension_questions_invalid_format",
                            dim_id=dim_code,
                            type=type(loaded_questions).__name__,
                        )
                
                dimensions[dim_code] = {
                    "metadata": self._load_json(f"dimensions/{dim_id}/metadata.json"),
                    "questions": questions_data,
                }
                self._metrics.files_loaded += 1

        return dimensions

    def _load_policy_areas(self) -> dict[str, dict[str, Any]]:
        """Load all policy area definitions."""
        pa_dir = self._root / "policy_areas"
        if not pa_dir.exists():
            raise AssemblyError("policy_areas/ directory not found")

        policy_areas = {}
        for pa_subdir in sorted(pa_dir.iterdir()):
            if not pa_subdir.is_dir() or pa_subdir.name.startswith("_"):
                continue

            # Extract PA ID from directory name (e.g., "PA01_genero" -> "PA01")
            pa_id = pa_subdir.name.split("_")[0]

            metadata_path = pa_subdir / "metadata.json"
            questions_path = pa_subdir / "questions.json"
            keywords_path = pa_subdir / "keywords.json"

            if metadata_path.exists():
                pa_data = {
                    "metadata": self._load_json(f"policy_areas/{pa_subdir.name}/metadata.json"),
                    "questions": [],
                    "keywords": [],
                }

                if questions_path.exists():
                    questions_data = self._load_json(
                        f"policy_areas/{pa_subdir.name}/questions.json"
                    )
                    # Extract questions array from the wrapper object
                    if isinstance(questions_data, dict):
                        pa_data["questions"] = questions_data.get("questions", [])
                    elif isinstance(questions_data, list):
                        pa_data["questions"] = questions_data
                    else:
                        logger.warning(
                            "policy_area_questions_invalid_format",
                            pa_id=pa_id,
                            type=type(questions_data).__name__,
                        )

                if keywords_path.exists():
                    keywords_data = self._load_json(f"policy_areas/{pa_subdir.name}/keywords.json")
                    pa_data["keywords"] = keywords_data.get("keywords", [])

                policy_areas[pa_id] = pa_data

        return policy_areas

    def _load_clusters(self) -> list[dict[str, Any]]:
        """Load cluster definitions."""
        clusters_dir = self._root / "clusters"
        if not clusters_dir.exists():
            return []

        clusters = []
        for cluster_dir in sorted(clusters_dir.iterdir()):
            if not cluster_dir.is_dir() or cluster_dir.name.startswith("_"):
                continue

            # Extract cluster ID (e.g., "CL01_seguridad_paz" -> "CL01")
            cluster_id = cluster_dir.name.split("_")[0]

            metadata_path = cluster_dir / "metadata.json"
            if metadata_path.exists():
                metadata = self._load_json(f"clusters/{cluster_dir.name}/metadata.json")
                clusters.append(
                    {
                        "cluster_id": cluster_id,
                        "name": metadata.get("name", cluster_dir.name),
                        "policy_area_ids": metadata.get("policy_area_ids", []),
                        **metadata,
                    }
                )

        return clusters

    def _load_scoring(self) -> dict[str, Any]:
        """Load scoring configuration."""
        scoring_dir = self._root / "scoring"
        if not scoring_dir.exists():
            return {}

        scoring = {}
        for name in ["modality_definitions", "micro_levels", "quality_thresholds"]:
            path = scoring_dir / f"{name}.json"
            if path.exists():
                scoring[name] = self._load_json(f"scoring/{name}.json")

        return scoring

    def _load_patterns(self) -> dict[str, Any]:
        """Load pattern registry."""
        patterns_dir = self._root / "patterns"
        if not patterns_dir.exists():
            return {}

        # Prefer index.json if exists
        index_path = patterns_dir / "index.json"
        if index_path.exists():
            return self._load_json("patterns/index.json")

        # Fallback to pattern_registry_v3.json
        v3_path = patterns_dir / "pattern_registry_v3.json"
        if v3_path.exists():
            return self._load_json("patterns/pattern_registry_v3.json")

        return {}

    def _load_semantic(self) -> dict[str, Any]:
        """Load semantic configuration."""
        semantic_dir = self._root / "semantic"
        if not semantic_dir.exists():
            return {}

        semantic = {}
        for name in ["embedding_strategy", "semantic_layers"]:
            path = semantic_dir / f"{name}.json"
            if path.exists():
                semantic[name] = self._load_json(f"semantic/{name}.json")

        return semantic

    def _load_cross_cutting(self) -> dict[str, Any]:
        """Load cross-cutting themes and interdependencies."""
        cc_dir = self._root / "cross_cutting"
        if not cc_dir.exists():
            return {}

        cross_cutting = {}
        for name in ["themes", "interdependencies"]:
            path = cc_dir / f"{name}.json"
            if path.exists():
                cross_cutting[name] = self._load_json(f"cross_cutting/{name}.json")

        return cross_cutting

    # ========================================================================
    # MICRO QUESTION ASSEMBLY
    # ========================================================================

    def _assemble_micro_questions(
        self,
        dimensions: dict[str, dict[str, Any]],
        policy_areas: dict[str, dict[str, Any]],
        patterns: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Assemble 300 micro questions from dimensions × policy_areas.

        Question ID format: Q{seq:03d} where seq = 1-300

        Matrix:
        - 6 dimensions × 10 policy areas × 5 questions per cell = 300
        """
        micro_questions = []
        question_seq = 1

        # Get pattern index for enrichment
        pattern_index = patterns.get("patterns", {})

        for dim_id in sorted(dimensions.keys()):
            dim_data = dimensions[dim_id]
            dim_questions = dim_data.get("questions", [])

            # If dimension has pre-assembled questions, use them
            if isinstance(dim_questions, list) and dim_questions:
                for q in dim_questions:
                    # Enrich with patterns if needed
                    q_patterns = q.get("patterns", [])
                    if not q_patterns:
                        q["patterns"] = self._get_patterns_for_question(
                            q.get("question_id", f"Q{question_seq:03d}"),
                            pattern_index,
                        )

                    micro_questions.append(q)
                    self._metrics.questions_assembled += 1
                    question_seq += 1
            else:
                # Generate from policy areas
                for pa_id in sorted(policy_areas.keys()):
                    pa_data = policy_areas[pa_id]
                    pa_questions = pa_data.get("questions", [])

                    # Filter questions for this dimension
                    dim_pa_questions = [q for q in pa_questions if q.get("dimension_id") == dim_id]

                    for q in dim_pa_questions:
                        q_id = q.get("question_id", f"Q{question_seq:03d}")

                        # Ensure required fields
                        assembled_q = {
                            "question_id": q_id,
                            "dimension_id": dim_id,
                            "policy_area_id": pa_id,
                            "cluster_id": pa_data.get("metadata", {}).get("cluster_id"),
                            "text": q.get("text", ""),
                            "scoring_modality": q.get("scoring_modality", "TYPE_A"),
                            "patterns": q.get("patterns", []),
                            "expected_elements": q.get("expected_elements", []),
                            "validations": q.get("validations", {}),
                            "failure_contract": q.get("failure_contract", {}),
                            "method_sets": q.get("method_sets", []),
                            **{
                                k: v
                                for k, v in q.items()
                                if k
                                not in [
                                    "question_id",
                                    "dimension_id",
                                    "policy_area_id",
                                    "cluster_id",
                                    "text",
                                    "scoring_modality",
                                    "patterns",
                                    "expected_elements",
                                    "validations",
                                    "failure_contract",
                                    "method_sets",
                                ]
                            },
                        }

                        # Enrich patterns
                        if not assembled_q["patterns"]:
                            assembled_q["patterns"] = self._get_patterns_for_question(
                                q_id, pattern_index
                            )

                        micro_questions.append(assembled_q)
                        self._metrics.questions_assembled += 1
                        question_seq += 1

        return micro_questions

    def _get_patterns_for_question(
        self,
        question_id: str,
        pattern_index: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Get patterns applicable to a question."""
        patterns = []

        for pattern_id, pattern_data in pattern_index.items():
            if not isinstance(pattern_data, dict):
                continue

            applies_to = pattern_data.get("applies_to_questions", [])
            if question_id in applies_to or "*" in applies_to:
                patterns.append(
                    {
                        "id": pattern_id,
                        "pattern": pattern_data.get("pattern", ""),
                        "match_type": pattern_data.get("match_type", "REGEX"),
                        "category": pattern_data.get("category", "GENERAL"),
                        "confidence_weight": pattern_data.get("confidence_weight", 0.85),
                        "semantic_expansion": pattern_data.get("semantic_expansion", []),
                        "context_requirement": pattern_data.get("context_requirement"),
                        "evidence_boost": pattern_data.get("evidence_boost", 1.0),
                    }
                )
                self._metrics.patterns_merged += 1

        return patterns

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def _validate_counts(
        self,
        dimensions: dict,
        policy_areas: dict,
        clusters: list,
        micro_questions: list,
    ) -> None:
        """Validate expected counts."""
        errors = []

        if len(dimensions) != self.EXPECTED_DIMENSION_COUNT:
            msg = (
                f"Dimension count mismatch: "
                f"expected {self.EXPECTED_DIMENSION_COUNT}, got {len(dimensions)}"
            )
            errors.append(msg)

        if len(policy_areas) != self.EXPECTED_POLICY_AREA_COUNT:
            msg = (
                f"Policy area count mismatch: "
                f"expected {self.EXPECTED_POLICY_AREA_COUNT}, got {len(policy_areas)}"
            )
            errors.append(msg)

        if len(clusters) != self.EXPECTED_CLUSTER_COUNT:
            msg = (
                f"Cluster count mismatch: "
                f"expected {self.EXPECTED_CLUSTER_COUNT}, got {len(clusters)}"
            )
            errors.append(msg)

        if len(micro_questions) != self.EXPECTED_QUESTION_COUNT:
            msg = (
                f"Micro question count mismatch: "
                f"expected {self.EXPECTED_QUESTION_COUNT}, got {len(micro_questions)}"
            )
            errors.append(msg)

        if errors:
            self._metrics.validation_errors.extend(errors)
            if self._strict_mode:
                raise AssemblyError(f"Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
            else:
                for error in errors:
                    logger.warning("validation_error", error=error)

    # ========================================================================
    # INTEGRITY
    # ========================================================================

    def _compute_hash(self, data: dict[str, Any]) -> str:
        """Compute deterministic SHA-256 hash of assembled data."""
        # Remove non-deterministic fields for hashing
        data_for_hash = {k: v for k, v in data.items() if k not in ("generated_at", "provenance")}

        # Serialize deterministically
        serialized = json.dumps(
            data_for_hash,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(serialized).hexdigest()

    def _get_git_commit(self) -> str | None:
        """Get current git commit hash if available."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self._root,
            )
            if result.returncode == 0:
                return result.stdout.strip()[:12]
        except Exception as e:
            logger.debug(f"Exception silenced: {str(e)}")
        return None


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

_GLOBAL_RESOLVER: CanonicalQuestionnaireResolver | None = None


def get_resolver(
    root: Path | None = None,
    strict_mode: bool = True,
) -> CanonicalQuestionnaireResolver:
    """
    Get or create global resolver instance.

    For singleton behavior across the application.
    """
    global _GLOBAL_RESOLVER

    if _GLOBAL_RESOLVER is None:
        _GLOBAL_RESOLVER = CanonicalQuestionnaireResolver(
            root=root,
            strict_mode=strict_mode,
        )

    return _GLOBAL_RESOLVER


def resolve_questionnaire(
    expected_hash: str | None = None,
    force_rebuild: bool = False,
) -> CanonicalQuestionnaire:
    """
    Convenience function to resolve questionnaire.

    USAGE:
        questionnaire = resolve_questionnaire()
    """
    resolver = get_resolver()
    return resolver.resolve(
        expected_hash=expected_hash,
        force_rebuild=force_rebuild,
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main classes
    "CanonicalQuestionnaireResolver",
    "CanonicalQuestionnaire",
    "AssemblyProvenance",
    # Protocol
    "QuestionnairePort",
    # Exceptions
    "ResolverError",
    "AssemblyError",
    "IntegrityError",
    "ValidationError",
    # Factory functions
    "get_resolver",
    "resolve_questionnaire",
    # SDO availability flag
    "SDO_AVAILABLE",
]
