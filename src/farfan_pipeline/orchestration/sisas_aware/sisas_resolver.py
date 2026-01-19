"""
SISAS-Aware Questionnaire Resolver Wrapper

This module provides a signal-aware wrapper for the ModularQuestionnaireResolver
that integrates with SISAS vehicles for signal-based irrigation.

AXIOMS:
- Signal-First: All data operations emit signals
- Vehicle-Driven: All signal generation uses appropriate vehicles
- Observable: Every load operation generates appropriate signals

Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from farfan_pipeline.infrastructure.questionnaire.modular_resolver import (
    QuestionnaireModularResolver,
    QuestionnaireSlice,
    AggregatePayload,
)

# SISAS imports
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    Signal,
    SignalContext,
    SignalSource,
    SignalConfidence,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import Event
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles import (
    SignalRegistryVehicle,
    SignalContextScoperVehicle,
    SignalQualityMetricsVehicle,
    SignalEnhancementIntegratorVehicle,
    SchemaValidatorVehicle,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.signal_vocabulary import SignalVocabulary

logger = logging.getLogger("SISAS.ResolverWrapper")


class SISASResolverError(Exception):
    """Base error for SISAS resolver operations."""
    pass


class VehicleIntegrationError(SISASResolverError):
    """Raised when vehicle integration fails."""
    pass


@dataclass
class ResolverLoadResult:
    """Result of a resolver load operation with signals."""
    data: Any
    signals: List[Signal]
    load_time_seconds: float
    signal_count: int


class SISASQuestionnaireResolver:
    """
    SISAS-aware wrapper for QuestionnaireModularResolver.

    This wrapper integrates SISAS vehicles with the modular resolver to:
    - Emit signals when loading questionnaire data
    - Validate data integrity through signal vehicles
    - Track all operations via signal audit trail

    Usage:
        resolver = SISASQuestionnaireResolver(
            root_path="/path/to/canonic_questionnaire_central"
        )

        # Load with signals
        result = resolver.load_policy_area("PA01_MUJERES_GENERO")
        print(f"Loaded {len(result.data.questions)} questions")
        print(f"Generated {result.signal_count} signals")
    """

    def __init__(
        self,
        root_path: Optional[Path] = None,
        bus_registry: Optional[BusRegistry] = None,
        enable_signal_generation: bool = True,
    ):
        """
        Initialize the SISAS-aware resolver.

        Args:
            root_path: Path to canonical questionnaire central
            bus_registry: Optional BusRegistry for signal publication
            enable_signal_generation: Whether to generate signals
        """
        self.root_path = root_path
        self.enable_signal_generation = enable_signal_generation
        self.bus_registry = bus_registry or BusRegistry()

        # Initialize the underlying resolver
        self._resolver = QuestionnaireModularResolver(root=root_path)

        # Initialize SISAS vehicles
        self._vehicles: Dict[str, Any] = {}
        if enable_signal_generation:
            self._initialize_vehicles()

        # Signal vocabulary for validation
        self.vocabulary = SignalVocabulary()

        # Statistics
        self._stats = {
            "total_loads": 0,
            "total_signals_generated": 0,
            "signal_errors": 0,
        }

    def _initialize_vehicles(self):
        """Initialize SISAS vehicles for signal generation."""
        try:
            self._vehicles["signal_registry"] = SignalRegistryVehicle(
                vehicle_id="resolver_signal_registry",
                bus_registry=self.bus_registry,
            )
            self._vehicles["signal_context_scoper"] = SignalContextScoperVehicle(
                vehicle_id="resolver_context_scoper",
                bus_registry=self.bus_registry,
            )
            self._vehicles["signal_quality_metrics"] = SignalQualityMetricsVehicle(
                vehicle_id="resolver_quality_metrics",
                bus_registry=self.bus_registry,
            )
            self._vehicles["signal_enhancement_integrator"] = SignalEnhancementIntegratorVehicle(
                vehicle_id="resolver_enhancement_integrator",
                bus_registry=self.bus_registry,
            )
            self._vehicles["schema_validator_vehicle"] = SchemaValidatorVehicle(
                vehicle_id="resolver_schema_validator",
                bus_registry=self.bus_registry,
            )

            # Activate vehicles
            for vehicle in self._vehicles.values():
                vehicle.activate()

            logger.info(f"Initialized {len(self._vehicles)} vehicles for resolver")

        except Exception as e:
            raise VehicleIntegrationError(f"Failed to initialize vehicles: {str(e)}")

    def load_policy_area(self, pa_id: str, *, validate_ids: bool = True) -> ResolverLoadResult:
        """
        Load a policy area with signal generation.

        Args:
            pa_id: Policy area ID (e.g., "PA01_MUJERES_GENERO")
            validate_ids: Whether to validate question IDs

        Returns:
            ResolverLoadResult with data and generated signals
        """
        import time
        start_time = time.time()

        # Load data using underlying resolver
        slice_obj = self._resolver.load_policy_area(pa_id, validate_ids=validate_ids)

        # Generate signals
        signals = []
        if self.enable_signal_generation:
            signals = self._generate_load_signals(slice_obj, "policy_area", pa_id)

        load_time = time.time() - start_time
        self._stats["total_loads"] += 1
        self._stats["total_signals_generated"] += len(signals)

        return ResolverLoadResult(
            data=slice_obj,
            signals=signals,
            load_time_seconds=load_time,
            signal_count=len(signals),
        )

    def load_dimension(self, dim_id: str, *, validate_ids: bool = True) -> ResolverLoadResult:
        """Load a dimension with signal generation."""
        import time
        start_time = time.time()

        slice_obj = self._resolver.load_dimension(dim_id, validate_ids=validate_ids)

        signals = []
        if self.enable_signal_generation:
            signals = self._generate_load_signals(slice_obj, "dimension", dim_id)

        load_time = time.time() - start_time
        self._stats["total_loads"] += 1
        self._stats["total_signals_generated"] += len(signals)

        return ResolverLoadResult(
            data=slice_obj,
            signals=signals,
            load_time_seconds=load_time,
            signal_count=len(signals),
        )

    def load_cluster(self, cluster_id: str) -> ResolverLoadResult:
        """Load a cluster with signal generation."""
        import time
        start_time = time.time()

        slice_obj = self._resolver.load_cluster(cluster_id)

        signals = []
        if self.enable_signal_generation:
            signals = self._generate_load_signals(slice_obj, "cluster", cluster_id)

        load_time = time.time() - start_time
        self._stats["total_loads"] += 1
        self._stats["total_signals_generated"] += len(signals)

        return ResolverLoadResult(
            data=slice_obj,
            signals=signals,
            load_time_seconds=load_time,
            signal_count=len(signals),
        )

    def build_monolith_payload(self) -> AggregatePayload:
        """Build monolith payload (delegates to underlying resolver)."""
        return self._resolver.build_monolith_payload()

    def _generate_load_signals(
        self,
        slice_obj: QuestionnaireSlice,
        entity_type: str,
        entity_id: str,
    ) -> List[Signal]:
        """Generate signals for a load operation."""
        signals = []

        try:
            # Create signal context
            context = SignalContext(
                node_type=entity_type,
                node_id=entity_id,
                phase="phase_0",  # Loading happens in phase 0
                consumer_scope="resolver",
            )

            # Create event
            event = self._vehicles["signal_registry"].create_event(
                event_type="data_loaded",
                payload={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "question_count": len(slice_obj.questions),
                },
                source_file=str(slice_obj.path),
                source_path=f"{entity_type}/{entity_id}",
                phase="phase_0",
                consumer_scope="resolver",
            )

            source = self._vehicles["signal_registry"].create_signal_source(event)

            # Generate quality signals
            quality_vehicle = self._vehicles["signal_quality_metrics"]
            quality_signals = quality_vehicle.process(slice_obj.questions, context)
            signals.extend(quality_signals)

            # Generate structural signals
            enhancement_vehicle = self._vehicles["signal_enhancement_integrator"]
            structural_signals = enhancement_vehicle.process({"questions": slice_obj.questions}, context)
            signals.extend(structural_signals)

            # Generate schema validation signals
            schema_vehicle = self._vehicles["schema_validator_vehicle"]
            schema_signals = schema_vehicle.process({"questions": slice_obj.questions}, context)
            signals.extend(schema_signals)

            # Publish signals to bus registry
            for signal in signals:
                try:
                    self.bus_registry.publish_to_appropriate_bus(
                        signal=signal,
                        publisher_vehicle="sisas_resolver",
                        publication_contract=None,  # Will use default
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish signal {signal.signal_type}: {str(e)}")
                    self._stats["signal_errors"] += 1

        except Exception as e:
            logger.error(f"Error generating signals for {entity_type}/{entity_id}: {str(e)}")
            self._stats["signal_errors"] += 1

        return signals

    def get_statistics(self) -> Dict[str, Any]:
        """Get resolver statistics."""
        return {
            **self._stats,
            "vehicles_initialized": len(self._vehicles),
            "signal_generation_enabled": self.enable_signal_generation,
        }

    def shutdown(self):
        """Shutdown the resolver and vehicles."""
        for vehicle in self._vehicles.values():
            vehicle.deactivate()
        logger.info("SISAS resolver shut down")
