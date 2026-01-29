# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/__init__.py

from .base_vehicle import BaseVehicle, VehicleCapabilities
from .signal_registry import SignalRegistryVehicle
from .signal_context_scoper import SignalContextScoperVehicle
from .signal_evidence_extractor import SignalEvidenceExtractorVehicle
from .signal_intelligence_layer import SignalIntelligenceLayerVehicle
from .signal_loader import SignalLoaderVehicle
from .signal_quality_metrics import SignalQualityMetricsVehicle
from .signal_enhancement_integrator import SignalEnhancementIntegratorVehicle
from .signal_irrigator import SignalIrrigatorVehicle
from .signals import SignalsAggregatorVehicle

# New vehicles for orphan signals
from .contrast.contrast_signals_vehicle import ContrastSignalsVehicle
from .structural.schema_validator_vehicle import SchemaValidatorVehicle

__all__ = [
    "BaseVehicle",
    "VehicleCapabilities",
    "SignalRegistryVehicle",
    "SignalContextScoperVehicle",
    "SignalEvidenceExtractorVehicle",
    "SignalIntelligenceLayerVehicle",
    "SignalLoaderVehicle",
    "SignalQualityMetricsVehicle",
    "SignalEnhancementIntegratorVehicle",
    "SignalIrrigatorVehicle",
    "SignalsAggregatorVehicle",
    # New vehicles for orphan signals
    "ContrastSignalsVehicle",
    "SchemaValidatorVehicle",
]
