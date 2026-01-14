# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_loader.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import json
import os
from pathlib import Path

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.integrity import (
    DataIntegritySignal,
    IntegrityViolationType,
    EventPresenceSignal,
    PresenceStatus
)


@dataclass
class SignalLoaderVehicle(BaseVehicle):
    """
    Vehículo: signal_loader
    
    Responsabilidad: Cargar archivos canónicos del sistema y validar
    su integridad referencial (referencias entre archivos, claves foráneas, etc.)
    
    Archivos que procesa:
    - config/* (configuraciones del sistema)
    - Todos los archivos canónicos para validación de integridad
    - Referencias cruzadas entre entidades
    """
    
    vehicle_id: str = field(default="signal_loader")
    vehicle_name: str = field(default="Signal Loader Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=[
            "DataIntegritySignal",
            "EventPresenceSignal"
        ]
    ))
    
    # Cache de datos cargados para validación de referencias
    loaded_data_cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Registro de IDs conocidos por tipo
    known_ids: Dict[str, Set[str]] = field(default_factory=lambda: {
        "policy_area": set(),
        "dimension": set(),
        "cluster": set(),
        "question": set(),
        "institution": set(),
        "method": set()
    })
    
    # Patrones de campos de referencia por tipo
    reference_fields: Dict[str, List[str]] = field(default_factory=lambda: {
        "question": ["policy_area_id", "dimension_id", "cluster_id"],
        "dimension": ["policy_area_id"],
        "cluster": ["dimension_id", "policy_area_id"],
        "method": ["applicable_to_questions"],
        "response": ["question_id"]
    })

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa carga de datos y valida integridad.
        """
        signals = []
        
        # Crear evento de carga
        event = self.create_event(
            event_type="canonical_data_loaded",
            payload={
                "file_type": context.node_type,
                "file_id": context.node_id,
                "data_keys": list(data.keys()) if isinstance(data, dict) else []
            },
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Cachear datos para referencias futuras
        cache_key = f"{context.node_type}/{context.node_id}"
        self.loaded_data_cache[cache_key] = data
        
        # Actualizar IDs conocidos
        self._update_known_ids(data, context)
        
        # 1. Señal de presencia de datos
        presence_signal = self._generate_presence_signal(data, context, source)
        signals.append(presence_signal)
        
        # 2. Señal de integridad referencial
        integrity_signal = self._generate_integrity_signal(data, context, source)
        signals.append(integrity_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _update_known_ids(self, data: Dict[str, Any], context: SignalContext):
        """Actualiza registro de IDs conocidos"""
        
        # Extraer ID del contexto o datos
        if "id" in data:
            entity_id = str(data["id"])
        else:
            entity_id = context.node_id
        
        # Registrar según tipo
        if context.node_type in self.known_ids:
            self.known_ids[context.node_type].add(entity_id)
        
        # Registrar IDs anidados (para listas de entidades)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and "id" in item:
                            # Inferir tipo del nombre de la clave
                            if "question" in key.lower():
                                self.known_ids["question"].add(str(item["id"]))
                            elif "dimension" in key.lower():
                                self.known_ids["dimension"].add(str(item["id"]))
                            elif "cluster" in key.lower():
                                self.known_ids["cluster"].add(str(item["id"]))
    
    def _generate_presence_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventPresenceSignal:
        """Genera señal de presencia de datos"""
        
        # Verificar presencia de datos
        is_empty = not data or (isinstance(data, dict) and all(
            v is None or v == [] or v == {} for v in data.values()
        ))
        
        if is_empty:
            presence_status = PresenceStatus.ABSENT
            confidence = SignalConfidence.HIGH
        else:
            presence_status = PresenceStatus.PRESENT
            confidence = SignalConfidence.HIGH
        
        # Verificar duplicados (si hay ID)
        duplicate_ids = []
        if "id" in data:
            entity_id = str(data["id"])
            # Buscar en cache si ya existe
            for cache_key, cached_data in self.loaded_data_cache.items():
                if cache_key != f"{context.node_type}/{context.node_id}":
                    if isinstance(cached_data, dict) and cached_data.get("id") == entity_id:
                        duplicate_ids.append(cache_key)
        
        if duplicate_ids:
            presence_status = PresenceStatus.DUPLICATED
        
        return EventPresenceSignal(
            context=context,
            source=source,
            expected_event_type="canonical_data_loaded",
            presence_status=presence_status,
            event_count=1,
            first_occurrence=source.generation_timestamp.isoformat(),
            last_occurrence=source.generation_timestamp.isoformat(),
            expected_count=1,
            duplicate_ids=duplicate_ids,
            event_ids=[source.event_id],
            confidence=confidence,
            rationale=f"Data presence: {presence_status.value}, duplicates: {len(duplicate_ids)}"
        )
    
    def _generate_integrity_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> DataIntegritySignal:
        """Genera señal de integridad referencial"""
        
        # Extraer referencias del archivo
        referenced_files = self._extract_references(data, context)
        
        # Validar referencias
        valid_references = []
        broken_references = []
        violations = []
        violation_types = set()
        
        for ref in referenced_files:
            if self._validate_reference(ref, context):
                valid_references.append(ref)
            else:
                broken_references.append(ref)
                violations.append({
                    "type": "missing_reference",
                    "reference": ref,
                    "context": f"{context.node_type}/{context.node_id}"
                })
                violation_types.add(IntegrityViolationType.MISSING_REFERENCE)
        
        # Detectar referencias circulares
        circular_refs = self._detect_circular_references(data, context)
        if circular_refs:
            violations.extend(circular_refs)
            violation_types.add(IntegrityViolationType.CIRCULAR_REFERENCE)
        
        # Calcular score de integridad
        if referenced_files:
            integrity_score = len(valid_references) / len(referenced_files)
        else:
            integrity_score = 1.0  # Sin referencias = integridad perfecta
        
        # Determinar confianza
        if integrity_score == 1.0:
            confidence = SignalConfidence.HIGH
        elif integrity_score >= 0.7:
            confidence = SignalConfidence.MEDIUM
        else:
            confidence = SignalConfidence.LOW
        
        return DataIntegritySignal(
            context=context,
            source=source,
            source_file=context.node_id,
            source_file_type=context.node_type,
            referenced_files=referenced_files,
            valid_references=valid_references,
            broken_references=broken_references,
            violations=violations,
            integrity_score=integrity_score,
            violation_types=violation_types,
            confidence=confidence,
            rationale=f"Integrity: {len(valid_references)}/{len(referenced_files)} valid references, "
                     f"{len(violations)} violations"
        )
    
    def _extract_references(
        self,
        data: Dict[str, Any],
        context: SignalContext
    ) -> List[str]:
        """Extrae referencias a otros archivos/entidades"""
        references = []
        
        # Obtener campos de referencia según tipo
        ref_fields = self.reference_fields.get(context.node_type, [])
        
        def extract_recursive(obj, depth=0):
            if depth > 3:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Buscar campos de referencia conocidos
                    if key in ref_fields or key.endswith("_id") or key.endswith("_ref"):
                        if isinstance(value, str):
                            references.append(value)
                        elif isinstance(value, list):
                            references.extend([str(v) for v in value if v])
                    else:
                        extract_recursive(value, depth + 1)
            
            elif isinstance(obj, list):
                for item in obj[:20]:  # Limitar profundidad
                    extract_recursive(item, depth + 1)
        
        extract_recursive(data)
        
        # También buscar patrones comunes de IDs
        data_str = json.dumps(data, default=str)
        
        # Policy areas: PA01, PA02, etc.
        import re
        pa_pattern = r'PA\d{2}'
        references.extend(re.findall(pa_pattern, data_str))
        
        # Dimensions: DIM01, DIM02, etc.
        dim_pattern = r'DIM\d{2}'
        references.extend(re.findall(dim_pattern, data_str))
        
        # Questions: Q001, Q147, etc.
        q_pattern = r'Q\d{3,4}'
        references.extend(re.findall(q_pattern, data_str))
        
        # Clusters: CL01, CL02, etc.
        cl_pattern = r'CL\d{2}'
        references.extend(re.findall(cl_pattern, data_str))
        
        return list(set(references))  # Eliminar duplicados
    
    def _validate_reference(self, reference: str, context: SignalContext) -> bool:
        """Valida que una referencia exista"""
        
        # Determinar tipo de referencia
        if reference.startswith("PA"):
            return reference in self.known_ids["policy_area"]
        elif reference.startswith("DIM"):
            return reference in self.known_ids["dimension"]
        elif reference.startswith("Q"):
            return reference in self.known_ids["question"]
        elif reference.startswith("CL"):
            return reference in self.known_ids["cluster"]
        
        # Buscar en cache general
        for cached_data in self.loaded_data_cache.values():
            if isinstance(cached_data, dict):
                if cached_data.get("id") == reference:
                    return True
                # Buscar en listas anidadas
                for value in cached_data.values():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and item.get("id") == reference:
                                return True
        
        # Si no se encuentra, asumir válida (puede no haberse cargado aún)
        return True
    
    def _detect_circular_references(
        self,
        data: Dict[str, Any],
        context: SignalContext
    ) -> List[Dict[str, Any]]:
        """Detecta referencias circulares"""
        violations = []
        
        # Obtener ID actual
        current_id = data.get("id", context.node_id)
        
        # Buscar referencias que apunten de vuelta a este ID
        def check_circular(obj, path="", depth=0):
            if depth > 5:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    
                    # Si encontramos una referencia al ID actual
                    if isinstance(value, str) and value == current_id:
                        violations.append({
                            "type": "circular_reference",
                            "reference": current_id,
                            "path": new_path,
                            "context": f"{context.node_type}/{context.node_id}"
                        })
                    else:
                        check_circular(value, new_path, depth + 1)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj[:10]):
                    check_circular(item, f"{path}[{i}]", depth + 1)
        
        # Verificar en datos cacheados
        for cache_key, cached_data in self.loaded_data_cache.items():
            if cache_key != f"{context.node_type}/{context.node_id}":
                check_circular(cached_data)
        
        return violations
    
    def load_file(self, file_path: str, context: SignalContext) -> Optional[Dict[str, Any]]:
        """
        Carga un archivo y genera señales.
        Método de conveniencia para uso externo.
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Procesar y generar señales
            signals = self.process(data, context)
            
            # Publicar señales si hay bus registry
            if self.bus_registry and self.publication_contract:
                for signal in signals:
                    self.publish_signal(signal)
            
            return data
            
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def get_integrity_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de integridad del sistema"""
        return {
            "files_loaded": len(self.loaded_data_cache),
            "known_ids": {
                entity_type: len(ids)
                for entity_type, ids in self.known_ids.items()
            },
            "total_known_entities": sum(len(ids) for ids in self.known_ids.values())
        }
