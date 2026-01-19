# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/contracts.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from abc import ABC, abstractmethod


class ContractType(Enum):
    """Tipos de contrato"""
    PUBLICATION = "publication"    # Contrato de quién puede publicar
    CONSUMPTION = "consumption"    # Contrato de quién puede consumir
    IRRIGATION = "irrigation"      # Contrato de irrigación


class ContractStatus(Enum):
    """Estado del contrato"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class SignalTypeSpec:
    """Especificación de un tipo de señal permitido en el contrato"""
    signal_type: str
    required_confidence: str = "LOW"  # Mínimo:  HIGH, MEDIUM, LOW
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    validators: List[Callable] = field(default_factory=list)


@dataclass
class PublicationContract:
    """
    Contrato de Publicación. 
    Define QUÉ puede publicar un vehículo y CÓMO. 
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.PUBLICATION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Quién publica
    publisher_vehicle: str = ""
    
    # Qué puede publicar
    allowed_signal_types: List[SignalTypeSpec] = field(default_factory=list)
    
    # A qué buses puede publicar
    allowed_buses:  List[str] = field(default_factory=list)
    
    # Restricciones
    max_signals_per_second: int = 1000
    require_context:  bool = True
    require_source: bool = True
    
    # Validaciones
    pre_publish_validators: List[Callable] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def validate_signal(self, signal: Any) -> tuple[bool, List[str]]:
        """
        Valida que una señal cumpla el contrato.
        Retorna (es_válido, lista_de_errores)
        """
        errors = []
        
        # Verificar tipo permitido
        signal_type = getattr(signal, 'signal_type', None)
        allowed_types = [spec.signal_type for spec in self.allowed_signal_types]
        
        if signal_type not in allowed_types:
            errors.append(f"Signal type '{signal_type}' not allowed.  Allowed:  {allowed_types}")
        
        # Verificar contexto
        if self.require_context and not hasattr(signal, 'context'):
            errors.append("Signal must have context")
        elif self.require_context and signal.context is None:
            errors.append("Signal context cannot be None")
        
        # Verificar source
        if self.require_source and not hasattr(signal, 'source'):
            errors.append("Signal must have source")
        elif self.require_source and signal.source is None:
            errors.append("Signal source cannot be None")
        
        # Ejecutar validadores custom
        for validator in self.pre_publish_validators:
            try:
                is_valid, msg = validator(signal)
                if not is_valid:
                    errors.append(msg)
            except Exception as e:
                errors.append(f"Validator error: {str(e)}")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id":  self.contract_id,
            "contract_type": self.contract_type.value,
            "status": self.status.value,
            "publisher_vehicle": self.publisher_vehicle,
            "allowed_signal_types": [s.signal_type for s in self.allowed_signal_types],
            "allowed_buses": self. allowed_buses,
            "version": self.version
        }


@dataclass
class ConsumptionContract:
    """
    Contrato de Consumo. 
    Define QUÉ puede consumir un consumidor y CÓMO debe procesarlo.
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.CONSUMPTION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Quién consume
    consumer_id: str = ""
    consumer_phase: str = ""
    
    # Qué puede consumir
    subscribed_signal_types: List[str] = field(default_factory=list)
    subscribed_buses: List[str] = field(default_factory=list)
    
    # Filtros
    context_filters: Dict[str, List[str]] = field(default_factory=dict)
    # Ejemplo: {"node_type": ["policy_area", "dimension"], "phase": ["phase_00"]}
    
    # Restricciones de procesamiento
    max_processing_time_ms: int = 5000
    require_acknowledgement: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3
    
    # Capacidades requeridas (del vocabulario)
    required_capabilities: List[str] = field(default_factory=list)
    
    # Callbacks
    on_receive:  Optional[Callable] = None
    on_process_complete: Optional[Callable] = None
    on_process_error:  Optional[Callable] = None
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def matches_signal(self, signal: Any) -> bool:
        """
        Verifica si una señal cumple los filtros del contrato.
        """
        # Verificar tipo
        if signal.signal_type not in self. subscribed_signal_types: 
            return False
        
        # Verificar filtros de contexto
        if self.context_filters:
            signal_context = signal.context. to_dict() if signal.context else {}
            
            for filter_key, allowed_values in self.context_filters.items():
                if filter_key in signal_context:
                    if signal_context[filter_key] not in allowed_values:
                        return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self. contract_id,
            "contract_type": self.contract_type.value,
            "status":  self.status.value,
            "consumer_id": self.consumer_id,
            "consumer_phase": self.consumer_phase,
            "subscribed_signal_types": self.subscribed_signal_types,
            "subscribed_buses":  self.subscribed_buses,
            "context_filters": self. context_filters,
            "required_capabilities": self.required_capabilities,
            "version": self.version
        }


@dataclass
class IrrigationContract:
    """
    Contrato de Irrigación. 
    Define la relación completa entre un archivo canónico,
    sus vehículos de transporte, y sus consumidores.
    """
    
    contract_id: str
    contract_type: ContractType = ContractType.IRRIGATION
    status: ContractStatus = ContractStatus.DRAFT
    
    # Archivo canónico fuente
    source_file: str = ""
    source_path: str = ""
    source_phase: str = ""
    
    # Vehículos que transportan
    vehicles: List[str] = field(default_factory=list)
    
    # Consumidores destino
    consumers: List[str] = field(default_factory=list)
    
    # Señales que se generan
    generated_signals: List[str] = field(default_factory=list)
    
    # Requisitos de vocabulario
    required_signal_vocabulary: List[str] = field(default_factory=list)
    required_capability_vocabulary: List[str] = field(default_factory=list)
    
    # Estado de alineación
    vocabulary_aligned: bool = False
    gaps:  List[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    def is_irrigable(self) -> bool:
        """
        Verifica si el contrato permite irrigación.
        """
        return (
            len(self.vehicles) > 0 and
            len(self. consumers) > 0 and
            self.vocabulary_aligned and
            len(self.gaps) == 0 and
            self.status == ContractStatus.ACTIVE
        )
    
    def get_blocking_gaps(self) -> List[str]:
        """Retorna gaps que bloquean la irrigación"""
        blocking = []
        
        if len(self.vehicles) == 0:
            blocking.append("NECESITA_VEHICULO")
        
        if len(self.consumers) == 0:
            blocking. append("NECESITA_CONSUMIDOR")
        
        if not self.vocabulary_aligned:
            if "VOCAB_SEÑALES_NO_ALINEADO" in self.gaps:
                blocking.append("VOCAB_SEÑALES_NO_ALINEADO")
            if "VOCAB_CAPACIDADES_NO_ALINEADO" in self.gaps:
                blocking.append("VOCAB_CAPACIDADES_NO_ALINEADO")
        
        return blocking
    
    def to_dict(self) -> Dict[str, Any]: 
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type.value,
            "status": self.status. value,
            "source_file": self.source_file,
            "source_path": self. source_path,
            "source_phase": self.source_phase,
            "vehicles": self. vehicles,
            "consumers": self.consumers,
            "generated_signals": self.generated_signals,
            "vocabulary_aligned": self.vocabulary_aligned,
            "gaps": self. gaps,
            "is_irrigable": self.is_irrigable(),
            "version":  self.version
        }


@dataclass
class ContractRegistry:
    """
    Registro central de todos los contratos.
    """
    
    publication_contracts: Dict[str, PublicationContract] = field(default_factory=dict)
    consumption_contracts: Dict[str, ConsumptionContract] = field(default_factory=dict)
    irrigation_contracts: Dict[str, IrrigationContract] = field(default_factory=dict)
    
    def register_publication(self, contract: PublicationContract) -> str:
        """Registra contrato de publicación"""
        self.publication_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def register_consumption(self, contract: ConsumptionContract) -> str:
        """Registra contrato de consumo"""
        self.consumption_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def register_irrigation(self, contract: IrrigationContract) -> str:
        """Registra contrato de irrigación"""
        self.irrigation_contracts[contract.contract_id] = contract
        return contract.contract_id
    
    def get_contracts_for_vehicle(self, vehicle: str) -> List[PublicationContract]:
        """Obtiene contratos de publicación para un vehículo"""
        return [c for c in self. publication_contracts.values() 
                if c.publisher_vehicle == vehicle]
    
    def get_contracts_for_consumer(self, consumer: str) -> List[ConsumptionContract]:
        """Obtiene contratos de consumo para un consumidor"""
        return [c for c in self.consumption_contracts.values() 
                if c.consumer_id == consumer]
    
    def get_irrigation_for_file(self, source_path: str) -> Optional[IrrigationContract]: 
        """Obtiene contrato de irrigación para un archivo"""
        for contract in self.irrigation_contracts. values():
            if contract.source_path == source_path:
                return contract
        return None
    
    def get_irrigable_contracts(self) -> List[IrrigationContract]: 
        """Obtiene todos los contratos que pueden irrigar ahora"""
        return [c for c in self.irrigation_contracts.values() if c.is_irrigable()]
    
    def get_blocked_contracts(self) -> List[tuple[IrrigationContract, List[str]]]:
        """Obtiene contratos bloqueados con sus gaps"""
        result = []
        for contract in self.irrigation_contracts.values():
            if not contract.is_irrigable():
                result.append((contract, contract.get_blocking_gaps()))
        return result