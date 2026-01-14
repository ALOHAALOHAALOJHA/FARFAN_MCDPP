# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_enhancement_integrator.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import json

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.structural import (
    StructuralAlignmentSignal,
    AlignmentStatus,
    CanonicalMappingSignal,
    MappingQuality
)


@dataclass
class SignalEnhancementIntegratorVehicle(BaseVehicle):
    """
    Vehículo: signal_enhancement_integrator
    
    Responsabilidad: Integrar enriquecimientos de múltiples fuentes (cross_cutting,
    scoring, semantic, validations) para generar señales de alineación y mapeo mejoradas.
    
    Archivos que procesa (según spec):
    - cross_cutting/*.json
    - scoring/*.json
    - semantic/*.json
    - validations/*.json
    
    Señales que produce (según spec):
    - StructuralAlignmentSignal
    - CanonicalMappingSignal
    """
    
    vehicle_id: str = field(default="signal_enhancement_integrator")
    vehicle_name: str = field(default="Signal Enhancement Integrator Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=True,
        can_enrich=True,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[
            "StructuralAlignmentSignal",
            "CanonicalMappingSignal"
        ]
    ))
    
    # Esquemas esperados por tipo
    cross_cutting_schema: List[str] = field(default_factory=lambda: [
        "id", "name", "applies_to", "impact_areas"
    ])
    
    scoring_schema: List[str] = field(default_factory=lambda: [
        "dimension_id", "weights", "thresholds", "calculation_method"
    ])
    
    semantic_schema: List[str] = field(default_factory=lambda: [
        "terms", "relationships", "ontology"
    ])
    
    validation_schema: List[str] = field(default_factory=lambda: [
        "rules", "constraints", "validators"
    ])
    
    # Cache de mapeos conocidos
    known_mappings: Dict[str, Set[str]] = field(default_factory=lambda: {
        "policy_areas": set(),
        "dimensions": set(),
        "clusters": set(),
        "questions": set()
    })

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa archivos de enriquecimiento y genera señales de integración.
        """
        signals = []
        
        # Crear evento de integración
        event = self.create_event(
            event_type="signal_generated",
            payload={"integration_type": "enhancement", "source": context.node_type},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Determinar tipo de archivo
        file_category = self._determine_file_category(context.node_id)
        
        # 1. Señal de alineación estructural
        alignment_signal = self._generate_alignment_signal(
            data, context, source, file_category
        )
        signals.append(alignment_signal)
        
        # 2. Señal de mapeo canónico (si aplica)
        if self._should_generate_mapping(data, file_category):
            mapping_signal = self._generate_mapping_signal(
                data, context, source, file_category
            )
            signals.append(mapping_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _determine_file_category(self, node_id: str) -> str:
        """Determina la categoría del archivo"""
        node_lower = node_id.lower()
        
        if "cross" in node_lower or "cutting" in node_lower:
            return "cross_cutting"
        elif "scoring" in node_lower or "score" in node_lower:
            return "scoring"
        elif "semantic" in node_lower:
            return "semantic"
        elif "validation" in node_lower or "validator" in node_lower:
            return "validation"
        
        return "unknown"
    
    def _generate_alignment_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource,
        file_category: str
    ) -> StructuralAlignmentSignal:
        """Genera señal de alineación estructural basada en enriquecimiento"""
        
        # Seleccionar esquema según categoría
        if file_category == "cross_cutting":
            expected_fields = self.cross_cutting_schema
        elif file_category == "scoring":
            expected_fields = self.scoring_schema
        elif file_category == "semantic":
            expected_fields = self.semantic_schema
        elif file_category == "validation":
            expected_fields = self.validation_schema
        else:
            expected_fields = ["id", "name", "description"]
        
        # Analizar estructura
        actual_fields = list(data.keys()) if isinstance(data, dict) else []
        missing_elements = [f for f in expected_fields if f not in actual_fields]
        extra_elements = [f for f in actual_fields if f not in expected_fields and expected_fields]
        
        # Determinar estado de alineación
        if not missing_elements and not extra_elements:
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.HIGH
        elif not missing_elements and len(extra_elements) <= 3:
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.MEDIUM
        elif len(missing_elements) <= len(expected_fields) // 2:
            status = AlignmentStatus.PARTIAL
            confidence = SignalConfidence.MEDIUM
        else:
            status = AlignmentStatus.MISALIGNED
            confidence = SignalConfidence.HIGH
        
        # Elementos con tipos para análisis detallado
        mismatched_elements = []
        for field in expected_fields:
            if field in data:
                value = data[field]
                # Inferir tipo esperado vs actual
                if field.endswith("_id") or field == "id":
                    if not isinstance(value, (str, int)):
                        mismatched_elements.append({
                            "element": field,
                            "expected_type": "str|int",
                            "actual_type": type(value).__name__
                        })
                elif field.endswith("s") or field in ["rules", "terms", "weights"]:
                    if not isinstance(value, (list, dict)):
                        mismatched_elements.append({
                            "element": field,
                            "expected_type": "list|dict",
                            "actual_type": type(value).__name__
                        })
        
        return StructuralAlignmentSignal(
            context=context,
            source=source,
            alignment_status=status,
            canonical_path=f"{file_category}/{context.node_id}",
            actual_path=source.source_path,
            missing_elements=missing_elements,
            extra_elements=extra_elements,
            mismatched_elements=mismatched_elements,
            confidence=confidence,
            rationale=f"Enhancement integration alignment: category={file_category}, "
                     f"missing={len(missing_elements)}, extra={len(extra_elements)}, "
                     f"mismatched={len(mismatched_elements)}"
        )
    
    def _should_generate_mapping(self, data: Dict[str, Any], file_category: str) -> bool:
        """Determina si debe generar señal de mapeo"""
        # Generar mapeo si el archivo tiene referencias a entidades canónicas
        if not isinstance(data, dict):
            return False
        
        # Buscar campos que indiquen mapeos
        mapping_indicators = [
            "applies_to", "related_to", "dimension_id", "policy_area_id",
            "cluster_id", "question_ids", "references"
        ]
        
        return any(indicator in data for indicator in mapping_indicators)
    
    def _generate_mapping_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource,
        file_category: str
    ) -> CanonicalMappingSignal:
        """Genera señal de mapeo canónico con enriquecimiento"""
        
        mapped_entities = {}
        unmapped_aspects = []
        alternative_mappings = {}
        
        # Extraer mapeos según categoría
        if file_category == "cross_cutting":
            # Cross-cutting afecta múltiples áreas
            if "applies_to" in data:
                applies = data["applies_to"]
                if isinstance(applies, list):
                    mapped_entities["policy_areas"] = applies
                elif isinstance(applies, str):
                    mapped_entities["policy_areas"] = [applies]
                else:
                    unmapped_aspects.append("policy_areas")
            
            if "impact_areas" in data:
                mapped_entities["impact_areas"] = data["impact_areas"]
        
        elif file_category == "scoring":
            # Scoring mapea a dimensiones
            if "dimension_id" in data:
                mapped_entities["dimension"] = data["dimension_id"]
            else:
                unmapped_aspects.append("dimension")
            
            if "applies_to_questions" in data:
                mapped_entities["questions"] = data["applies_to_questions"]
        
        elif file_category == "semantic":
            # Semantic relaciona términos
            if "related_to" in data:
                mapped_entities["semantic_relations"] = data["related_to"]
            
            if "concepts" in data:
                concepts = data["concepts"]
                if isinstance(concepts, list):
                    # Buscar referencias a entidades
                    for concept in concepts[:10]:
                        if isinstance(concept, dict) and "maps_to" in concept:
                            alternative_mappings[concept.get("term", "unknown")] = concept["maps_to"]
        
        elif file_category == "validation":
            # Validations mapean a constraints
            if "applies_to" in data:
                mapped_entities["validation_targets"] = data["applies_to"]
        
        # Calcular completitud del mapeo
        total_possible = len(mapped_entities) + len(unmapped_aspects)
        mapping_completeness = len(mapped_entities) / total_possible if total_possible > 0 else 1.0
        
        # Determinar calidad
        if mapping_completeness >= 0.9:
            mapping_quality = MappingQuality.EXCELLENT
            confidence = SignalConfidence.HIGH
        elif mapping_completeness >= 0.7:
            mapping_quality = MappingQuality.GOOD
            confidence = SignalConfidence.HIGH
        elif mapping_completeness >= 0.5:
            mapping_quality = MappingQuality.ACCEPTABLE
            confidence = SignalConfidence.MEDIUM
        elif mapping_completeness > 0:
            mapping_quality = MappingQuality.POOR
            confidence = SignalConfidence.MEDIUM
        else:
            mapping_quality = MappingQuality.CRITICAL
            confidence = SignalConfidence.LOW
        
        # Calcular confidence score basado en enriquecimiento
        enrichment_indicators = 0
        if "weights" in data:
            enrichment_indicators += 1
        if "thresholds" in data:
            enrichment_indicators += 1
        if "relationships" in data or "relations" in data:
            enrichment_indicators += 1
        if "metadata" in data:
            enrichment_indicators += 1
        
        confidence_score = min(0.95, 0.5 + (enrichment_indicators * 0.1))
        
        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=context.node_id,
            mapped_entities=mapped_entities,
            unmapped_aspects=unmapped_aspects,
            mapping_completeness=mapping_completeness,
            alternative_mappings=alternative_mappings,
            mapping_quality=mapping_quality,
            confidence_score=confidence_score,
            confidence=confidence,
            rationale=f"Enhancement mapping: category={file_category}, "
                     f"completeness={mapping_completeness:.2f}, "
                     f"quality={mapping_quality.value}, "
                     f"enrichment_indicators={enrichment_indicators}"
        )
    
    def register_known_mapping(self, entity_type: str, entity_id: str):
        """Registra un mapeo conocido para referencia futura"""
        if entity_type in self.known_mappings:
            self.known_mappings[entity_type].add(entity_id)
    
    def get_mapping_coverage(self) -> Dict[str, int]:
        """Obtiene cobertura de mapeos registrados"""
        return {
            entity_type: len(ids)
            for entity_type, ids in self.known_mappings.items()
        }
