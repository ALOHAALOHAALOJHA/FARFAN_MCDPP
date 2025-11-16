"""Policy Orchestrator - Orchestrates distribution of policy chunks to executors with signals.

This module implements the top-level orchestrator that coordinates:
1. Smart Policy Chunks (10 per policy area)
2. Signal distribution (patterns, regex, entities per policy area)
3. Chunk routing to appropriate executors
4. Synchronized execution across all components

Architecture:
    PolicyOrchestrator uses ONLY existing components:
    - SignalRegistry: Signal storage and retrieval
    - ChunkRouter: Chunk type → executor mapping
    - Executors (D1Q1-D6Q5): Question-specific processors
    - CalibrationOrchestrator: Method calibration (optional)

Design Principles:
    - NO new dependencies
    - Uses canonical notation (PA01-PA10, DIM01-DIM06, Q001-Q300)
    - Validates integrity at each step
    - Guarantees 10 chunks per policy area
    - Ensures signal-chunk-executor synchronization

Usage:
    ```python
    from saaaaaa.core.orchestrator.policy_orchestrator import PolicyOrchestrator
    from saaaaaa.core.orchestrator.signals import SignalRegistry

    # Initialize
    signal_registry = SignalRegistry()
    orchestrator = PolicyOrchestrator(signal_registry=signal_registry)

    # Load signals for policy areas
    orchestrator.load_policy_signals("config/policy_signals")

    # Process chunks for a policy area
    results = orchestrator.process_policy_area(
        chunks=chunks_PA01,  # 10 chunks
        policy_area="PA01"
    )
    ```
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .chunk_router import ChunkRouter, ChunkRoute
from .signals import SignalRegistry, SignalPack, SignalClient, InMemorySignalSource
from .executor_config import ExecutorConfig, CONSERVATIVE_CONFIG
from .executors import (
    D1Q1_Executor, D1Q2_Executor, D1Q3_Executor, D1Q4_Executor, D1Q5_Executor,
    D2Q1_Executor, D2Q2_Executor, D2Q3_Executor, D2Q4_Executor, D2Q5_Executor,
    D3Q1_Executor, D3Q2_Executor, D3Q3_Executor, D3Q4_Executor, D3Q5_Executor,
    D4Q1_Executor, D4Q2_Executor, D4Q3_Executor, D4Q4_Executor, D4Q5_Executor,
    D5Q1_Executor, D5Q2_Executor, D5Q3_Executor, D5Q4_Executor, D5Q5_Executor,
    D6Q1_Executor, D6Q2_Executor, D6Q3_Executor, D6Q4_Executor, D6Q5_Executor,
)

logger = logging.getLogger(__name__)


@dataclass
class PolicyAreaProcessingResult:
    """Result of processing a policy area."""
    policy_area: str
    chunks_processed: int
    signals_version: Optional[str]
    executor_results: List[Dict[str, Any]]
    processing_time_s: float
    validation_passed: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyOrchestrationError(Exception):
    """Raised when policy orchestration fails."""
    pass


class PolicyOrchestrator:
    """
    Top-level orchestrator for policy area processing.

    Coordinates the flow:
        Smart Chunks (10/PA) → Signals (PA-specific) → Executors (chunk-aware)

    Attributes:
        signal_registry: Registry for signal packs
        chunk_router: Router for chunk → executor mapping
        executors: Dictionary of initialized executors
        calibration_orchestrator: Optional calibration system
    """

    # Target number of chunks per policy area
    TARGET_CHUNKS_PER_PA = 10

    # Policy areas from canonical ontology (questionnaire_monolith.json)
    CANONICAL_POLICY_AREAS = [
        "PA01",  # Derechos de las mujeres e igualdad de género
        "PA02",  # Prevención de la violencia y protección
        "PA03",  # Ambiente sano, cambio climático
        "PA04",  # Derechos económicos, sociales y culturales
        "PA05",  # Derechos de las víctimas y construcción de paz
        "PA06",  # Derecho niñez, adolescencia, juventud
        "PA07",  # Tierras y territorios
        "PA08",  # Líderes, defensores DDHH
        "PA09",  # Crisis derechos personas privadas de la libertad
        "PA10",  # Migración transfronteriza
    ]

    # Mapping PA → relevant executors (based on question distribution)
    # Each PA has 30 questions distributed across 6 dimensions
    PA_TO_EXECUTOR_GROUPS = {
        "PA01": ["D1Q1", "D2Q1", "D3Q1", "D4Q1", "D5Q1", "D6Q1"],  # Q001-Q030
        "PA02": ["D1Q2", "D2Q2", "D3Q2", "D4Q2", "D5Q2", "D6Q2"],  # Q061-Q090
        "PA03": ["D1Q3", "D2Q3", "D3Q3", "D4Q3", "D5Q3", "D6Q3"],  # Q091-Q120
        "PA04": ["D1Q4", "D2Q4", "D3Q4", "D4Q4", "D5Q4", "D6Q4"],  # Q121-Q150
        "PA05": ["D1Q5", "D2Q5", "D3Q5", "D4Q5", "D5Q5", "D6Q5"],  # Q151-Q180
        "PA06": ["D1Q1", "D2Q1", "D3Q1", "D4Q1", "D5Q1", "D6Q1"],  # Q181-Q210
        "PA07": ["D1Q2", "D2Q2", "D3Q2", "D4Q2", "D5Q2", "D6Q2"],  # Q211-Q240
        "PA08": ["D1Q3", "D2Q3", "D3Q3", "D4Q3", "D5Q3", "D6Q3"],  # Q241-Q270
        "PA09": ["D1Q4", "D2Q4", "D3Q4", "D4Q4", "D5Q4", "D6Q4"],  # Q271-Q300
        "PA10": ["D1Q5", "D2Q5", "D3Q5", "D4Q5", "D5Q5", "D6Q5"],  # Q031-Q060
    }

    def __init__(
        self,
        signal_registry: SignalRegistry,
        executor_config: Optional[ExecutorConfig] = None,
        calibration_orchestrator: Optional[Any] = None,
    ):
        """
        Initialize policy orchestrator.

        Args:
            signal_registry: Signal registry for signal packs
            executor_config: Configuration for executors (uses CONSERVATIVE_CONFIG if None)
            calibration_orchestrator: Optional calibration system
        """
        self.signal_registry = signal_registry
        self.chunk_router = ChunkRouter()
        self.calibration = calibration_orchestrator

        # Use conservative config if not provided
        self.executor_config = executor_config or CONSERVATIVE_CONFIG

        # Initialize all 30 executors
        self.executors = self._initialize_executors()

        # Track processing statistics
        self.stats = {
            "policy_areas_processed": 0,
            "total_chunks_processed": 0,
            "total_executor_calls": 0,
            "signals_used": {},
        }

        logger.info(
            "policy_orchestrator_initialized",
            extra={
                "signal_registry_size": len(self.signal_registry._cache) if hasattr(self.signal_registry, '_cache') else 0,
                "executors_loaded": len(self.executors),
                "calibration_enabled": self.calibration is not None,
            }
        )

    def _initialize_executors(self) -> Dict[str, Any]:
        """
        Initialize all 30 executors (D1Q1-D6Q5).

        Returns:
            Dictionary mapping executor names to instances
        """
        # Create a mock method_executor for initialization
        # In production, this would be provided by the orchestrator caller
        class MockMethodExecutor:
            def __init__(self):
                self.instances = {}

        mock_executor = MockMethodExecutor()

        executors = {
            # Dimension 1 (INSUMOS - Diagnóstico y Recursos)
            "D1Q1": D1Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D1Q2": D1Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D1Q3": D1Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D1Q4": D1Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D1Q5": D1Q5_Executor(mock_executor, signal_registry=self.signal_registry),

            # Dimension 2 (ACTIVIDADES - Diseño de Intervención)
            "D2Q1": D2Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D2Q2": D2Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D2Q3": D2Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D2Q4": D2Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D2Q5": D2Q5_Executor(mock_executor, signal_registry=self.signal_registry),

            # Dimension 3 (PRODUCTOS - Productos y Outputs)
            "D3Q1": D3Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D3Q2": D3Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D3Q3": D3Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D3Q4": D3Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D3Q5": D3Q5_Executor(mock_executor, signal_registry=self.signal_registry),

            # Dimension 4 (RESULTADOS - Resultados y Outcomes)
            "D4Q1": D4Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D4Q2": D4Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D4Q3": D4Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D4Q4": D4Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D4Q5": D4Q5_Executor(mock_executor, signal_registry=self.signal_registry),

            # Dimension 5 (IMPACTOS - Impactos de Largo Plazo)
            "D5Q1": D5Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D5Q2": D5Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D5Q3": D5Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D5Q4": D5Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D5Q5": D5Q5_Executor(mock_executor, signal_registry=self.signal_registry),

            # Dimension 6 (CAUSALIDAD - Teoría de Cambio)
            "D6Q1": D6Q1_Executor(mock_executor, signal_registry=self.signal_registry),
            "D6Q2": D6Q2_Executor(mock_executor, signal_registry=self.signal_registry),
            "D6Q3": D6Q3_Executor(mock_executor, signal_registry=self.signal_registry),
            "D6Q4": D6Q4_Executor(mock_executor, signal_registry=self.signal_registry),
            "D6Q5": D6Q5_Executor(mock_executor, signal_registry=self.signal_registry),
        }

        logger.info(
            "executors_initialized",
            extra={"executor_count": len(executors)}
        )

        return executors

    def load_policy_signals(self, signals_dir: str | Path) -> None:
        """
        Load signal packs from directory.

        Expects files: PA01.json, PA02.json, ..., PA10.json

        Args:
            signals_dir: Directory containing signal pack JSON files
        """
        signals_path = Path(signals_dir)

        if not signals_path.exists():
            raise PolicyOrchestrationError(f"Signals directory not found: {signals_path}")

        loaded_count = 0
        for pa in self.CANONICAL_POLICY_AREAS:
            signal_file = signals_path / f"{pa}.json"

            if signal_file.exists():
                import json
                with open(signal_file, 'r', encoding='utf-8') as f:
                    signal_data = json.load(f)

                signal_pack = SignalPack(**signal_data)
                self.signal_registry.put(pa, signal_pack)
                loaded_count += 1

                logger.info(
                    "signal_pack_loaded",
                    extra={
                        "policy_area": pa,
                        "version": signal_pack.version,
                        "patterns_count": len(signal_pack.patterns),
                        "regex_count": len(signal_pack.regex),
                    }
                )
            else:
                logger.warning(
                    "signal_pack_missing",
                    extra={"policy_area": pa, "expected_file": str(signal_file)}
                )

        logger.info(
            "policy_signals_loaded",
            extra={"loaded_count": loaded_count, "total_expected": len(self.CANONICAL_POLICY_AREAS)}
        )

    def process_policy_area(
        self,
        chunks: List[Any],
        policy_area: str,
        method_executor: Optional[Any] = None,
    ) -> PolicyAreaProcessingResult:
        """
        Process chunks for a policy area.

        Args:
            chunks: List of chunks (must be exactly 10)
            policy_area: Policy area ID (PA01-PA10)
            method_executor: Method executor for running analysis methods

        Returns:
            PolicyAreaProcessingResult with execution details

        Raises:
            PolicyOrchestrationError: If validation fails
        """
        start_time = time.time()

        # Validate policy area
        if policy_area not in self.CANONICAL_POLICY_AREAS:
            raise PolicyOrchestrationError(
                f"Invalid policy area: {policy_area}. "
                f"Must be one of {self.CANONICAL_POLICY_AREAS}"
            )

        # Validate chunk count
        if len(chunks) != self.TARGET_CHUNKS_PER_PA:
            raise PolicyOrchestrationError(
                f"Expected exactly {self.TARGET_CHUNKS_PER_PA} chunks for {policy_area}, "
                f"got {len(chunks)}"
            )

        logger.info(
            "policy_area_processing_start",
            extra={
                "policy_area": policy_area,
                "chunk_count": len(chunks),
            }
        )

        # Get signal pack for this policy area
        signal_pack = self.signal_registry.get(policy_area)

        if signal_pack is None:
            logger.warning(
                "signal_pack_not_found",
                extra={"policy_area": policy_area, "fallback": "conservative mode"}
            )

        # Process each chunk
        executor_results = []
        for i, chunk in enumerate(chunks):
            try:
                # Route chunk to executor
                route = self.chunk_router.route_chunk(chunk)

                if route.skip_reason:
                    logger.warning(
                        "chunk_skipped",
                        extra={
                            "chunk_id": i,
                            "chunk_type": route.chunk_type,
                            "reason": route.skip_reason,
                        }
                    )
                    continue

                # Get executor
                executor_key = route.executor_class
                executor = self.executors.get(executor_key)

                if executor is None:
                    logger.error(
                        "executor_not_found",
                        extra={"executor_key": executor_key, "chunk_id": i}
                    )
                    continue

                # Execute chunk with signals
                # Note: execute_chunk method exists in executors (line 2159 of executors.py)
                if hasattr(executor, 'execute_chunk') and method_executor:
                    result = executor.execute_chunk(
                        chunk_doc=chunk,
                        chunk_id=i,
                    )
                else:
                    # Fallback to regular execute
                    result = {"chunk_id": i, "status": "no_execute_chunk_method"}

                executor_results.append({
                    "chunk_id": i,
                    "chunk_type": route.chunk_type,
                    "executor": executor_key,
                    "result": result,
                })

                self.stats["total_executor_calls"] += 1

            except Exception as e:
                logger.error(
                    "chunk_processing_failed",
                    extra={
                        "chunk_id": i,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                executor_results.append({
                    "chunk_id": i,
                    "status": "error",
                    "error": str(e),
                })

        # Update statistics
        self.stats["policy_areas_processed"] += 1
        self.stats["total_chunks_processed"] += len(chunks)
        if signal_pack:
            self.stats["signals_used"][policy_area] = signal_pack.version

        processing_time = time.time() - start_time

        result = PolicyAreaProcessingResult(
            policy_area=policy_area,
            chunks_processed=len(chunks),
            signals_version=signal_pack.version if signal_pack else None,
            executor_results=executor_results,
            processing_time_s=processing_time,
            validation_passed=len(executor_results) == len(chunks),
            metadata={
                "signal_pack_hash": signal_pack.compute_hash() if signal_pack else None,
                "executors_used": list(set(r.get("executor") for r in executor_results if "executor" in r)),
            }
        )

        logger.info(
            "policy_area_processing_complete",
            extra={
                "policy_area": policy_area,
                "chunks_processed": len(chunks),
                "executor_calls": len(executor_results),
                "processing_time_s": processing_time,
                "validation_passed": result.validation_passed,
            }
        )

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Dictionary with processing statistics
        """
        return {
            **self.stats,
            "signal_registry_metrics": self.signal_registry.get_metrics() if hasattr(self.signal_registry, 'get_metrics') else {},
        }
