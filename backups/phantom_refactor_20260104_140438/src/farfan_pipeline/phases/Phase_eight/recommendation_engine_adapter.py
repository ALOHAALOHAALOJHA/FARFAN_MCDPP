"""
Recommendation engine adapter for infrastructure layer.

Implements RecommendationEnginePort using the concrete RecommendationEngine
from the analysis module. This adapter follows the Ports and Adapters pattern,
allowing the orchestrator to depend on abstractions rather than concrete implementations.

Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RecommendationEngineAdapter:
    """Adapter implementing RecommendationEnginePort.

    This adapter wraps the concrete RecommendationEngine from the analysis module,
    providing a clean boundary between the orchestrator (core) and analysis (domain).
    """

    def __init__(
        self,
        rules_path: str | Path,
        schema_path: str | Path,
        questionnaire_provider: Any = None,
        orchestrator: Any = None,
    ) -> None:
        """Initialize recommendation engine adapter.

        Args:
            rules_path: Path to recommendation rules JSON file
            schema_path: Path to JSON schema for validation
            questionnaire_provider: QuestionnaireResourceProvider instance
            orchestrator: Orchestrator instance for accessing thresholds (can be set later)

        Raises:
            ImportError: If RecommendationEngine cannot be imported
            Exception: If engine initialization fails
        """
        self._rules_path = Path(rules_path)
        self._schema_path = Path(schema_path)
        self._questionnaire_provider = questionnaire_provider
        self._orchestrator = orchestrator
        self._engine: Any = None

        self._initialize_engine()

    def set_orchestrator(self, orchestrator: Any) -> None:
        """Set orchestrator reference after construction.

        This handles circular dependency between orchestrator and recommendation engine.

        Args:
            orchestrator: Orchestrator instance
        """
        self._orchestrator = orchestrator
        if self._engine is not None:
            self._engine.orchestrator = orchestrator

    def _initialize_engine(self) -> None:
        """Initialize the concrete RecommendationEngine.

        Raises:
            ImportError: If RecommendationEngine cannot be imported
            Exception: If engine initialization fails
        """
        try:
            from farfan_pipeline.analysis.recommendation_engine import (
                RecommendationEngine,
            )

            self._engine = RecommendationEngine(
                rules_path=str(self._rules_path),
                schema_path=str(self._schema_path),
                questionnaire_provider=self._questionnaire_provider,
                orchestrator=self._orchestrator,
            )
            logger.info(
                f"RecommendationEngine initialized via adapter: "
                f"{len(self._engine.rules_by_level.get('MICRO', []))} MICRO, "
                f"{len(self._engine.rules_by_level.get('MESO', []))} MESO, "
                f"{len(self._engine.rules_by_level.get('MACRO', []))} MACRO rules"
            )
        except ImportError as e:
            logger.error(f"Failed to import RecommendationEngine: {e}")
            raise ImportError(
                "RecommendationEngine not available. "
                "Ensure farfan_pipeline.analysis.recommendation_engine is installed."
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize RecommendationEngine: {e}")
            raise

    def generate_all_recommendations(
        self,
        micro_scores: dict[str, float],
        cluster_data: dict[str, Any],
        macro_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate recommendations at all three levels.

        Delegates to the concrete RecommendationEngine implementation.

        Args:
            micro_scores: Dictionary mapping "PA##-DIM##" to scores
            cluster_data: Dictionary with cluster metrics
            macro_data: Dictionary with macro-level metrics
            context: Optional context for template rendering

        Returns:
            Dictionary mapping level to RecommendationSet

        Raises:
            RuntimeError: If engine is not initialized
        """
        if self._engine is None:
            raise RuntimeError("RecommendationEngine not initialized")

        return self._engine.generate_all_recommendations(
            micro_scores=micro_scores,
            cluster_data=cluster_data,
            macro_data=macro_data,
            context=context,
        )

    def generate_micro_recommendations(
        self, scores: dict[str, float], context: dict[str, Any] | None = None
    ) -> Any:
        """Generate MICRO-level recommendations.

        Args:
            scores: Dictionary mapping "PA##-DIM##" to scores
            context: Optional context for template rendering

        Returns:
            RecommendationSet with MICRO recommendations

        Raises:
            RuntimeError: If engine is not initialized
        """
        if self._engine is None:
            raise RuntimeError("RecommendationEngine not initialized")

        return self._engine.generate_micro_recommendations(
            scores=scores, context=context
        )

    def generate_meso_recommendations(
        self, cluster_data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> Any:
        """Generate MESO-level recommendations.

        Args:
            cluster_data: Dictionary with cluster metrics
            context: Optional context for template rendering

        Returns:
            RecommendationSet with MESO recommendations

        Raises:
            RuntimeError: If engine is not initialized
        """
        if self._engine is None:
            raise RuntimeError("RecommendationEngine not initialized")

        return self._engine.generate_meso_recommendations(
            cluster_data=cluster_data, context=context
        )

    def generate_macro_recommendations(
        self, macro_data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> Any:
        """Generate MACRO-level recommendations.

        Args:
            macro_data: Dictionary with macro-level metrics
            context: Optional context for template rendering

        Returns:
            RecommendationSet with MACRO recommendations

        Raises:
            RuntimeError: If engine is not initialized
        """
        if self._engine is None:
            raise RuntimeError("RecommendationEngine not initialized")

        return self._engine.generate_macro_recommendations(
            macro_data=macro_data, context=context
        )

    def reload_rules(self) -> None:
        """Reload recommendation rules from disk.

        Raises:
            RuntimeError: If engine is not initialized
        """
        if self._engine is None:
            raise RuntimeError("RecommendationEngine not initialized")

        self._engine.reload_rules()
        logger.info("Recommendation rules reloaded via adapter")


def create_recommendation_engine_adapter(
    rules_path: str | Path,
    schema_path: str | Path,
    questionnaire_provider: Any = None,
    orchestrator: Any = None,
) -> RecommendationEngineAdapter:
    """Factory function to create RecommendationEngineAdapter.

    This is the primary entry point for creating recommendation engine instances
    in the infrastructure layer. It handles initialization and error handling.

    Args:
        rules_path: Path to recommendation rules JSON file
        schema_path: Path to JSON schema for validation
        questionnaire_provider: QuestionnaireResourceProvider instance
        orchestrator: Orchestrator instance for accessing thresholds

    Returns:
        RecommendationEngineAdapter instance

    Raises:
        ImportError: If RecommendationEngine cannot be imported
        Exception: If engine initialization fails

    Example:
        >>> from pathlib import Path
        >>> adapter = create_recommendation_engine_adapter(
        ...     rules_path=Path("config/recommendation_rules_enhanced.json"),
        ...     schema_path=Path("rules/recommendation_rules_enhanced.schema.json"),
        ...     questionnaire_provider=provider,
        ...     orchestrator=orch
        ... )
    """
    return RecommendationEngineAdapter(
        rules_path=rules_path,
        schema_path=schema_path,
        questionnaire_provider=questionnaire_provider,
        orchestrator=orchestrator,
    )


__all__ = [
    "RecommendationEngineAdapter",
    "create_recommendation_engine_adapter",
]
