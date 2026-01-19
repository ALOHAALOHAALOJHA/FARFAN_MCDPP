# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/wiring/wiring_config.py

"""
PILAR 3: WIRING - Configuración de conexiones entre componentes

Este módulo implementa el tercer pilar de SISAS: el wiring (cableado).

AXIOMA: Todas las conexiones en SISAS son configurables y validables.
          Ninguna conexión está harcodeada.
"""

from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple

# Importaciones SISAS
from ..core.signal import Signal, SignalCategory, SignalContext
from ..core.bus import BusType, SignalBus
from ..core.contracts import (
    PublicationContract,
    ConsumptionContract,
    ContractRegistry,
    ContractType,
    ContractStatus
)
from ..vocabulary.signal_vocabulary import SignalVocabulary
from ..vocabulary.capability_vocabulary import CapabilityVocabulary


# =============================================================================
# VALIDATION REPORT
# =============================================================================

@dataclass
class WiringIssue:
    """Issue encontrado durante la validación de wiring"""
    type: str  # "SIGNAL_NOT_IN_VOCAB", "BUS_NOT_FOUND", etc.
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details
        }


@dataclass
class WiringValidationReport:
    """
    Reporte de validación de wiring.

    Contiene todos los issues encontrados durante la validación
    y el estado final del wiring.
    """
    is_valid: bool = False
    issues: List[WiringIssue] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def critical_issues(self) -> List[WiringIssue]:
        return [i for i in self.issues if i.severity == "CRITICAL"]

    @property
    def high_issues(self) -> List[WiringIssue]:
        return [i for i in self.issues if i.severity == "HIGH"]

    @property
    def blocking_issues(self) -> List[WiringIssue]:
        """Issues que bloquean la operación"""
        return [i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]]

    @property
    def issues_by_type(self) -> Dict[str, List[WiringIssue]]:
        counts = {}
        for issue in self.issues:
            issue_type = issue.type
            counts[issue_type] = counts.get(issue_type, [])
            counts[issue_type].append(issue)
        return counts

    @property
    def issues_by_severity(self) -> Dict[str, int]:
        counts = {}
        for issue in self.issues:
            sev = issue.severity
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def add_critical(self, issue_type: str, message: str, **details):
        """Añade un issue crítico"""
        self.issues.append(WiringIssue(
            type=issue_type,
            severity="CRITICAL",
            message=message,
            details=details
        ))
        self.is_valid = False

    def add_error(self, issue_type: str, message: str, **details):
        """Añade un error (HIGH)"""
        self.issues.append(WiringIssue(
            type=issue_type,
            severity="HIGH",
            message=message,
            details=details
        ))

    def add_warning(self, issue_type: str, message: str, **details):
        """Añade un warning (MEDIUM)"""
        self.issues.append(WiringIssue(
            type=issue_type,
            severity="MEDIUM",
            message=message,
            details=details
        ))

    def add_info(self, issue_type: str, message: str, **details):
        """Añade info (LOW)"""
        self.issues.append(WiringIssue(
            type=issue_type,
            severity="LOW",
            message=message,
            details=details
        ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_issues": len(self.issues),
            "blocking_issues": len(self.blocking_issues),
            "issues_by_severity": self.issues_by_severity,
            "issues": [i.to_dict() for i in self.issues],
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


# =============================================================================
# MAIN WIRING CONFIGURATION
# =============================================================================

class WiringConfiguration:
    """
    Configuración maestra de conexiones SISAS.

    Responsabilidad: Definir y validar TODAS las conexiones en el sistema.

    Este es el PILAR 3 de SISAS: WIRING.

    Conexiones gestionadas:
        1. SIGNAL → BUS: Qué tipo de señal va a qué bus
        2. VEHICLE → PUBLICATION CONTRACT: Qué vehículo publica qué señales
        3. CONSUMER → CONSUMPTION CONTRACT: Qué consumidor consume qué señales
        4. FILE PATTERN → VEHICLE: Qué vehículo procesa qué archivos
        5. VEHICLE → CONSUMERS: Routing de vehículos a consumidores

    Uso:
        wiring = WiringConfiguration.from_defaults()
        report = wiring.validate_wiring()

        if not report.is_valid:
            for issue in report.blocking_issues:
                print(f"BLOCKING: {issue.message}")

        # Usar wiring para routing
        bus = wiring.get_bus_for_signal(my_signal)
        vehicles = wiring.get_vehicles_for_file(my_file_path)
    """

    def __init__(
        self,
        signal_to_bus: Optional[Dict[str, str]] = None,
        vehicle_contracts: Optional[Dict[str, PublicationContract]] = None,
        consumer_contracts: Optional[Dict[str, ConsumptionContract]] = None,
        file_to_vehicle: Optional[Dict[str, str]] = None,
        vehicle_to_consumers: Optional[Dict[str, List[str]]] = None,
        signal_vocabulary: Optional[SignalVocabulary] = None,
        capability_vocabulary: Optional[CapabilityVocabulary] = None
    ):
        """
        Inicializa la configuración de wiring.

        Args:
            signal_to_bus: Mapeo signal_type → bus_name
            vehicle_contracts: Contratos de publicación por vehículo
            consumer_contracts: Contratos de consumo por consumidor
            file_to_vehicle: Mapeo file_pattern → vehicle_id
            vehicle_to_consumers: Mapeo vehicle_id → [consumer_ids]
            signal_vocabulary: Vocabulario de señales
            capability_vocabulary: Vocabulario de capacidades
        """
        # ═══════════════════════════════════════════════════════
        # WIRING 1: SIGNAL → BUS
        # ═══════════════════════════════════════════════════════
        self.signal_to_bus = signal_to_bus or self._get_default_signal_to_bus()

        # ═══════════════════════════════════════════════════════
        # WIRING 2: VEHICLE → PUBLICATION CONTRACT
        # ═══════════════════════════════════════════════════════
        self.vehicle_contracts = vehicle_contracts or self._get_default_vehicle_contracts()

        # ═══════════════════════════════════════════════════════
        # WIRING 3: CONSUMER → CONSUMPTION CONTRACT
        # ═══════════════════════════════════════════════════════
        self.consumer_contracts = consumer_contracts or self._get_default_consumer_contracts()

        # ═══════════════════════════════════════════════════════
        # WIRING 4: FILE PATTERN → VEHICLE
        # ═══════════════════════════════════════════════════════
        self.file_to_vehicle = file_to_vehicle or self._get_default_file_to_vehicle()

        # ═══════════════════════════════════════════════════════
        # WIRING 5: VEHICLE → CONSUMERS (routing)
        # ═══════════════════════════════════════════════════════
        self.vehicle_to_consumers = vehicle_to_consumers or self._get_default_vehicle_to_consumers()

        # ═══════════════════════════════════════════════════════
        # VOCABULARIOS
        # ═══════════════════════════════════════════════════════
        self.signal_vocabulary = signal_vocabulary or SignalVocabulary()
        self.capability_vocabulary = capability_vocabulary or CapabilityVocabulary()

    # =========================================================================
    # VALIDATION API
    # =========================================================================

    def validate_wiring(self) -> WiringValidationReport:
        """
        Valida que el wiring es consistente.

        Checks:
            1. Todos los signal_types en contracts existen en vocabulario
            2. Todos los buses existen en BusRegistry
            3. No hay consumers huérfanos (sin señales)
            4. No hay señales sin consumers (dead letters)
            5. Vehículos en file_to_vehicle existen
            6. Consumers en vehicle_to_consumers existen

        Returns:
            WiringValidationReport con los issues encontrados
        """
        report = WiringValidationReport(is_valid=True)

        # ═══════════════════════════════════════════════════════
        # CHECK 1: SIGNAL TYPES EN VOCABULARIO
        # ═══════════════════════════════════════════════════════
        signal_types_in_contracts = set()
        for vehicle, contract in self.vehicle_contracts.items():
            for spec in contract.allowed_signal_types:
                signal_types_in_contracts.add(spec.signal_type)

        for signal_type in signal_types_in_contracts:
            if signal_type not in ["*", "all"] and signal_type not in self.signal_vocabulary.definitions:
                report.add_error(
                    "SIGNAL_NOT_IN_VOCAB",
                    f"Signal type '{signal_type}' not in SignalVocabulary",
                    vehicle=vehicle,
                    signal_type=signal_type
                )

        # ═══════════════════════════════════════════════════════
        # CHECK 2: BUSES EXISTEN
        # ═══════════════════════════════════════════════════════
        known_buses = set(BusType._member_names_)
        configured_buses = set(self.signal_to_bus.values())

        for bus_name in configured_buses:
            if bus_name != "universal_bus" and bus_name not in known_buses:
                report.add_error(
                    "BUS_NOT_FOUND",
                    f"Bus '{bus_name}' not in BusType",
                    bus=bus_name,
                    known_buses=list(known_buses)
                )

        # ═══════════════════════════════════════════════════════
        # CHECK 3: NO HAY CONSUMERS HUÉRFANOS
        # ═══════════════════════════════════════════════════════
        for consumer, contract in self.consumer_contracts.items():
            if not contract.subscribed_signal_types:
                report.add_warning(
                    "CONSUMER_ORPHAN",
                    f"Consumer '{consumer}' no está suscrito a ninguna señal",
                    consumer=consumer
                )

        # ═══════════════════════════════════════════════════════
        # CHECK 4: NO HAY SEÑALES SIN CONSUMERS (DEAD LETTERS)
        # ═══════════════════════════════════════════════════════
        all_published_signals = set()
        for contract in self.vehicle_contracts.values():
            for spec in contract.allowed_signal_types:
                all_published_signals.add(spec.signal_type)

        all_consumed_signals = set()
        for contract in self.consumer_contracts.values():
            for signal_type in contract.subscribed_signal_types:
                all_consumed_signals.add(signal_type)

        dead_signals = all_published_signals - all_consumed_signals
        for signal_type in dead_signals:
            if signal_type not in ["*", "all"]:
                # Encontrar qué vehículo lo publica
                publishers = [
                    v for v, c in self.vehicle_contracts.items()
                    if any(s.signal_type == signal_type for s in c.allowed_signal_types)
                ]
                report.add_warning(
                    "SIGNAL_DEAD_LETTER",
                    f"Signal '{signal_type}' published but never consumed",
                    signal_type=signal_type,
                    publishers=publishers
                )

        # ═══════════════════════════════════════════════════════
        # CHECK 5: VEHÍCULOS EN FILE_TO_VEHICLE EXISTEN
        # ═══════════════════════════════════════════════════════
        known_vehicles = set(self.vehicle_contracts.keys())
        for pattern, vehicle in self.file_to_vehicle.items():
            if vehicle not in known_vehicles:
                report.add_warning(
                    "VEHICLE_NOT_FOUND",
                    f"Vehicle '{vehicle}' in file_to_vehicle not in contracts",
                    pattern=pattern,
                    vehicle=vehicle,
                    known_vehicles=list(known_vehicles)
                )

        # ═══════════════════════════════════════════════════════
        # CHECK 6: CONSUMERS EN VEHICLE_TO_CONSUMERS EXISTEN
        # ═══════════════════════════════════════════════════════
        known_consumers = set(self.consumer_contracts.keys())
        for vehicle, consumers in self.vehicle_to_consumers.items():
            for consumer in consumers:
                if consumer not in known_consumers:
                    report.add_warning(
                        "CONSUMER_NOT_FOUND",
                        f"Consumer '{consumer}' in vehicle_to_consumers not in contracts",
                        vehicle=vehicle,
                        consumer=consumer,
                        known_consumers=list(known_consumers)
                    )

        # Determinar validez final
        report.is_valid = len(report.blocking_issues) == 0

        return report

    # =========================================================================
    # WIRING QUERIES
    # =========================================================================

    def get_bus_for_signal(self, signal_type: str) -> str:
        """
        Retorna el bus apropiado para un tipo de señal.

        Args:
            signal_type: Tipo de señal

        Returns:
            Nombre del bus (usa universal_bus como fallback)
        """
        return self.signal_to_bus.get(signal_type, "universal_bus")

    def get_vehicle_for_file(self, file_path: str) -> Optional[str]:
        """
        Retorna el vehicle apropiado para un archivo.

        Busca en file_to_vehicle usando patrones fnmatch.

        Args:
            file_path: Path del archivo canónico

        Returns:
            vehicle_id o None si no hay match
        """
        for pattern, vehicle in self.file_to_vehicle.items():
            if fnmatch.fnmatch(file_path, pattern):
                return vehicle

        # No hay match explícito, intentar inferir
        return self._infer_vehicle_for_file(file_path)

    def get_vehicles_for_file(self, file_path: str) -> List[str]:
        """
        Retorna todos los vehículos apropiados para un archivo.

        Puede retornar múltiples vehículos si el archivo lo requiere.

        Args:
            file_path: Path del archivo canónico

        Returns:
            Lista de vehicle_ids
        """
        vehicle = self.get_vehicle_for_file(file_path)
        if vehicle:
            return [vehicle]

        # Intentar inferir múltiples vehículos
        return self._infer_multiple_vehicles_for_file(file_path)

    def get_consumers_for_vehicle(self, vehicle_id: str) -> List[str]:
        """
        Retorna consumers que deberían recibir señales de un vehículo.

        Args:
            vehicle_id: ID del vehículo

        Returns:
            Lista de consumer_ids
        """
        return self.vehicle_to_consumers.get(vehicle_id, [])

    def get_bus_for_vehicle(self, vehicle_id: str, signal_type: str) -> str:
        """
        Retorna el bus donde un vehículo publica un tipo de señal.

        Args:
            vehicle_id: ID del vehículo
            signal_type: Tipo de señal

        Returns:
            Nombre del bus
        """
        # Primero: buscar signal_to_bus directo
        if signal_type in self.signal_to_bus:
            return self.signal_to_bus[signal_type]

        # Segundo: buscar en contract del vehículo
        if vehicle_id in self.vehicle_contracts:
            contract = self.vehicle_contracts[vehicle_id]
            for spec in contract.allowed_signal_types:
                if spec.signal_type == signal_type:
                    # Retornar el primer bus permitido para este vehículo
                    if contract.allowed_buses:
                        return contract.allowed_buses[0]

        # Fallback: universal_bus
        return "universal_bus"

    # =========================================================================
    # FACTORIES
    # =========================================================================

    @classmethod
    def from_defaults(cls) -> 'WiringConfiguration':
        """Crea configuración desde valores predeterminados"""
        return cls()

    @classmethod
    def from_contracts(
        cls,
        contract_registry: ContractRegistry,
        signal_vocabulary: Optional[SignalVocabulary] = None
    ) -> 'WiringConfiguration':
        """
        Crea configuración desde un registro de contratos existente.

        Args:
            contract_registry: Registro con contratos ya creados
            signal_vocabulary: Vocabulario de señales (opcional)
        """
        return cls(
            vehicle_contracts={
                k: v for k, v in contract_registry.publication_contracts.items()
            },
            consumer_contracts={
                k: v for k, v in contract_registry.consumption_contracts.items()
            },
            signal_vocabulary=signal_vocabulary
        )

    # =========================================================================
    # DEFAULT CONFIGURATIONS
    # =========================================================================

    def _get_default_signal_to_bus(self) -> Dict[str, str]:
        """Mapeo predeterminado signal_type → bus"""
        return {
            # Señales estructurales → structural_bus
            "StructuralAlignmentSignal": "structural_bus",
            "CanonicalMappingSignal": "structural_bus",
            "SchemaConflictSignal": "structural_bus",

            # Señales de integridad → integrity_bus
            "EventPresenceSignal": "integrity_bus",
            "EventCompletenessSignal": "integrity_bus",
            "DataIntegritySignal": "integrity_bus",

            # Señales epistémicas → epistemic_bus
            "AnswerDeterminacySignal": "epistemic_bus",
            "AnswerSpecificitySignal": "epistemic_bus",
            "EmpiricalSupportSignal": "epistemic_bus",
            "MethodApplicationSignal": "epistemic_bus",

            # Señales operacionales → operational_bus
            "ExecutionAttemptSignal": "operational_bus",
            "FailureModeSignal": "operational_bus",

            # Señales de consumo → consumption_bus
            "FrequencySignal": "consumption_bus",
            "ConsumerHealthSignal": "consumption_bus",

            # Fallback para cualquier señal no mapeada
            "*": "universal_bus"
        }

    def _get_default_vehicle_contracts(self) -> Dict[str, PublicationContract]:
        """Contratos de publicación predeterminados"""
        from ..vehicles import (
            SignalRegistryVehicle,
            SignalContextScoperVehicle,
            SignalQualityMetricsVehicle,
            SignalEvidenceExtractorVehicle,
            SignalIntelligenceLayerVehicle,
            SignalEnhancementIntegratorVehicle
        )

        return {
            "signal_registry": PublicationContract(
                contract_id="pub_signal_registry",
                publisher_vehicle="signal_registry",
                allowed_signal_types=[
                    {"signal_type": "StructuralAlignmentSignal", "required_confidence": "LOW"},
                    {"signal_type": "CanonicalMappingSignal", "required_confidence": "LOW"},
                    {"signal_type": "EventPresenceSignal", "required_confidence": "LOW"}
                ],
                allowed_buses=["structural_bus", "integrity_bus"]
            ),
            "signal_context_scoper": PublicationContract(
                contract_id="pub_signal_context_scoper",
                publisher_vehicle="signal_context_scoper",
                allowed_signal_types=[
                    {"signal_type": "CanonicalMappingSignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "AnswerDeterminacySignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "AnswerSpecificitySignal", "required_confidence": "MEDIUM"}
                ],
                allowed_buses=["structural_bus", "epistemic_bus"]
            ),
            "signal_quality_metrics": PublicationContract(
                contract_id="pub_signal_quality_metrics",
                publisher_vehicle="signal_quality_metrics",
                allowed_signal_types=[
                    {"signal_type": "DataIntegritySignal", "required_confidence": "HIGH"},
                    {"signal_type": "EventCompletenessSignal", "required_confidence": "HIGH"}
                ],
                allowed_buses=["integrity_bus"]
            ),
            "signal_evidence_extractor": PublicationContract(
                contract_id="pub_signal_evidence_extractor",
                publisher_vehicle="signal_evidence_extractor",
                allowed_signal_types=[
                    {"signal_type": "EmpiricalSupportSignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "MethodApplicationSignal", "required_confidence": "MEDIUM"}
                ],
                allowed_buses=["epistemic_bus"]
            ),
            "signal_intelligence_layer": PublicationContract(
                contract_id="pub_signal_intelligence_layer",
                publisher_vehicle="signal_intelligence_layer",
                allowed_signal_types=[
                    {"signal_type": "MethodApplicationSignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "AnswerDeterminacySignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "AnswerSpecificitySignal", "required_confidence": "MEDIUM"}
                ],
                allowed_buses=["epistemic_bus"]
            ),
            "signal_enhancement_integrator": PublicationContract(
                contract_id="pub_signal_enhancement_integrator",
                publisher_vehicle="signal_enhancement_integrator",
                allowed_signal_types=[
                    {"signal_type": "StructuralAlignmentSignal", "required_confidence": "MEDIUM"},
                    {"signal_type": "CanonicalMappingSignal", "required_confidence": "MEDIUM"}
                ],
                allowed_buses=["structural_bus"]
            ),
        }

    def _get_default_consumer_contracts(self) -> Dict[str, ConsumptionContract]:
        """Contratos de consumo predeterminados"""
        return {
            "phase0_bootstrap": ConsumptionContract(
                contract_id="cons_phase0_bootstrap",
                consumer_id="phase0_bootstrap",
                consumer_phase="phase_0",
                subscribed_signal_types=[
                    "StructuralAlignmentSignal",
                    "EventPresenceSignal",
                    "DataIntegritySignal"
                ],
                subscribed_buses=["structural_bus", "integrity_bus"]
            ),
            "phase0_providers": ConsumptionContract(
                contract_id="cons_phase0_providers",
                consumer_id="phase0_providers",
                consumer_phase="phase_0",
                subscribed_signal_types=[
                    "CanonicalMappingSignal",
                    "EventCompletenessSignal"
                ],
                subscribed_buses=["structural_bus", "integrity_bus"]
            ),
            "phase1_signal_enrichment": ConsumptionContract(
                contract_id="cons_phase1_signal_enrichment",
                consumer_id="phase1_signal_enrichment",
                consumer_phase="phase_1",
                subscribed_signal_types=[
                    "MethodApplicationSignal",
                    "EmpiricalSupportSignal",
                    "AnswerDeterminacySignal"
                ],
                subscribed_buses=["epistemic_bus"]
            ),
            "phase2_factory_consumer": ConsumptionContract(
                contract_id="cons_phase2_factory_consumer",
                consumer_id="phase2_factory_consumer",
                consumer_phase="phase_2",
                subscribed_signal_types=[
                    "CanonicalMappingSignal",
                    "EventPresenceSignal"
                ],
                subscribed_buses=["structural_bus", "integrity_bus"]
            ),
            "phase2_evidence_consumer": ConsumptionContract(
                contract_id="cons_phase2_evidence_consumer",
                consumer_id="phase2_evidence_consumer",
                consumer_phase="phase_2",
                subscribed_signal_types=[
                    "EmpiricalSupportSignal",
                    "MethodApplicationSignal"
                ],
                subscribed_buses=["epistemic_bus"]
            ),
            "phase3_scoring": ConsumptionContract(
                contract_id="cons_phase3_scoring",
                consumer_id="phase3_scoring",
                consumer_phase="phase_3",
                subscribed_signal_types=[
                    "DataIntegritySignal",
                    "EventCompletenessSignal"
                ],
                subscribed_buses=["integrity_bus"]
            ),
            "phase8_recommendations": ConsumptionContract(
                contract_id="cons_phase8_recommendations",
                consumer_id="phase8_recommendations",
                consumer_phase="phase_8",
                subscribed_signal_types=[
                    "EmpiricalSupportSignal",
                    "MethodApplicationSignal",
                    "AnswerDeterminacySignal",
                    "AnswerSpecificitySignal"
                ],
                subscribed_buses=["epistemic_bus"]
            ),
        }

    def _get_default_file_to_vehicle(self) -> Dict[str, str]:
        """Mapeo predeterminado file_pattern → vehicle"""
        return {
            "dimensions/*/questions/*.json": "signal_registry",
            "dimensions/*/metadata.json": "signal_enhancement_integrator",
            "policy_areas/*/questions/*.json": "signal_registry",
            "policy_areas/*/metadata.json": "signal_enhancement_integrator",
            "clusters/*/questions/*.json": "signal_registry",
            "clusters/*/metadata.json": "signal_enhancement_integrator",
            "_registry/membership_criteria/MC*.json": "signal_context_scoper",
            "_registry/patterns/**/*.json": "signal_context_scoper",
            "questions/**/*.json": "signal_context_scoper",
            "micro_questions/**/*.json": "signal_evidence_extractor",
            "atomized_questions/**/*.json": "signal_evidence_extractor",
            "**/metadata.json": "signal_quality_metrics",
            "**/keywords.json": "signal_context_scoper",
            "**/aggregation_rules.json": "signal_intelligence_layer",
            "**/scoring_system.json": "signal_intelligence_layer",
            "**/governance.json": "signal_enhancement_integrator",
        }

    def _get_default_vehicle_to_consumers(self) -> Dict[str, List[str]]:
        """Mapeo predeterminado vehicle → consumers"""
        return {
            "signal_registry": [
                "phase0_bootstrap",
                "phase1_signal_enrichment",
                "phase3_scoring"
            ],
            "signal_context_scoper": [
                "phase2_factory_consumer",
                "phase2_evidence_consumer"
            ],
            "signal_quality_metrics": [
                "phase0_bootstrap",
                "phase0_providers",
                "phase1_cpp_ingestion",
                "phase2_contract_consumer",
                "phase3_scoring",
                "phase8_recommendations"
            ],
            "signal_evidence_extractor": [
                "phase2_evidence_consumer",
                "phase8_recommendations"
            ],
            "signal_intelligence_layer": [
                "phase1_signal_enrichment",
                "phase8_recommendations"
            ],
            "signal_enhancement_integrator": [
                "phase0_bootstrap",
                "phase1_signal_enrichment"
            ],
        }

    # =========================================================================
    # INFERENCE HELPERS
    # =========================================================================

    def _infer_vehicle_for_file(self, file_path: str) -> Optional[str]:
        """Infiere el vehículo apropiado para un archivo"""
        filename = os.path.basename(file_path)

        if "metadata" in filename:
            return "signal_quality_metrics"
        elif "questions" in filename:
            return "signal_context_scoper"
        elif "keywords" in filename:
            return "signal_context_scoper"
        elif "aggregation" in filename:
            return "signal_intelligence_layer"
        else:
            return "signal_quality_metrics"  # Default

    def _infer_multiple_vehicles_for_file(self, file_path: str) -> List[str]:
        """Infiere múltiples vehículos para un archivo"""
        filename = os.path.basename(file_path)

        if "metadata" in filename:
            return ["signal_quality_metrics", "signal_enhancement_integrator"]
        elif "questions" in filename:
            return ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"]
        elif "keywords" in filename:
            return ["signal_registry", "signal_context_scoper"]
        else:
            return ["signal_context_scoper", "signal_quality_metrics"]


# =============================================================================
# EXPORTS
# =============================================================================

WIRING_DEFAULTS = WiringConfiguration.from_defaults
