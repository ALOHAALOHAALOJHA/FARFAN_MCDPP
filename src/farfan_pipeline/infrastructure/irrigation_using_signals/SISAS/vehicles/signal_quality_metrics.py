# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_quality_metrics.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import json

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.integrity import (
    DataIntegritySignal,
    IntegrityViolationType,
    EventCompletenessSignal,
    CompletenessLevel
)


@dataclass
class SignalQualityMetricsVehicle(BaseVehicle):
    """
    Vehículo: signal_quality_metrics
    
    Responsabilidad: Calcular métricas de calidad sobre archivos de policy areas,
    validando keywords y questions para detectar problemas de integridad y completitud.
    
    Archivos que procesa (según spec):
    - policy_areas/*/keywords.json
    - policy_areas/*/questions.json
    
    Señales que produce (según spec):
    - DataIntegritySignal
    - EventCompletenessSignal
    """
    
    vehicle_id: str = field(default="signal_quality_metrics")
    vehicle_name: str = field(default="Signal Quality Metrics Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=True,
        can_transform=False,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=[
            "DataIntegritySignal",
            "EventCompletenessSignal"
        ]
    ))
    
    # Esquemas esperados
    keywords_schema: List[str] = field(default_factory=lambda: [
        "keywords", "synonyms", "related_terms", "exclusions"
    ])
    
    questions_schema: List[str] = field(default_factory=lambda: [
        "questions", "id", "text", "type", "category"
    ])
    
    # Métricas de calidad
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "min_keywords": 5,
        "min_questions": 3,
        "max_duplicate_ratio": 0.1,
        "min_keyword_length": 3,
        "max_keyword_length": 50
    })

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa archivos de policy areas y genera señales de calidad.
        """
        signals = []
        
        # Crear evento de análisis
        event = self.create_event(
            event_type="signal_generated",
            payload={"analysis_type": "quality_metrics", "file_type": context.node_type},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Determinar tipo de archivo
        file_type = self._determine_file_type(context.node_id, data)
        
        if file_type == "keywords":
            # Analizar keywords
            integrity_signal = self._analyze_keywords_integrity(data, context, source)
            signals.append(integrity_signal)
            
            completeness_signal = self._analyze_keywords_completeness(data, context, source)
            signals.append(completeness_signal)
            
        elif file_type == "questions":
            # Analizar questions
            integrity_signal = self._analyze_questions_integrity(data, context, source)
            signals.append(integrity_signal)
            
            completeness_signal = self._analyze_questions_completeness(data, context, source)
            signals.append(completeness_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _determine_file_type(self, node_id: str, data: Dict[str, Any]) -> str:
        """Determina el tipo de archivo"""
        if "keywords" in node_id.lower() or "keywords" in data:
            return "keywords"
        elif "questions" in node_id.lower() or "questions" in data:
            return "questions"
        return "unknown"
    
    def _analyze_keywords_integrity(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> DataIntegritySignal:
        """Analiza integridad de keywords"""
        
        violations = []
        violation_types = set()
        
        # Extraer keywords
        keywords = data.get("keywords", [])
        if isinstance(keywords, dict):
            keywords = list(keywords.values())
        
        # Validar duplicados
        if keywords:
            duplicates = self._find_duplicates(keywords)
            if duplicates:
                violations.append({
                    "type": "duplicate_keywords",
                    "count": len(duplicates),
                    "examples": list(duplicates)[:5]
                })
                violation_types.add(IntegrityViolationType.DUPLICATE_VALUE)
        
        # Validar longitud de keywords
        invalid_length = []
        for kw in keywords[:100]:  # Limitar análisis
            if isinstance(kw, str):
                if len(kw) < self.quality_thresholds["min_keyword_length"]:
                    invalid_length.append(kw)
                elif len(kw) > self.quality_thresholds["max_keyword_length"]:
                    invalid_length.append(kw)
        
        if invalid_length:
            violations.append({
                "type": "invalid_keyword_length",
                "count": len(invalid_length),
                "examples": invalid_length[:5]
            })
            violation_types.add(IntegrityViolationType.INVALID_VALUE)
        
        # Validar keywords vacíos
        empty_keywords = [kw for kw in keywords if not kw or (isinstance(kw, str) and not kw.strip())]
        if empty_keywords:
            violations.append({
                "type": "empty_keywords",
                "count": len(empty_keywords)
            })
            violation_types.add(IntegrityViolationType.NULL_VALUE)
        
        # Calcular score de integridad
        total_issues = len(duplicates) if 'duplicates' in locals() else 0
        total_issues += len(invalid_length) + len(empty_keywords)
        total_keywords = max(len(keywords), 1)
        
        integrity_score = max(0.0, 1.0 - (total_issues / total_keywords))
        
        # Referencias a otros archivos
        referenced_files = []
        if "related_policy_areas" in data:
            referenced_files.extend(data["related_policy_areas"])
        
        return DataIntegritySignal(
            context=context,
            source=source,
            source_file=context.node_id,
            source_file_type="keywords",
            referenced_files=referenced_files,
            valid_references=referenced_files,  # Asumimos válidos
            broken_references=[],
            violations=violations,
            integrity_score=integrity_score,
            violation_types=violation_types,
            confidence=SignalConfidence.HIGH,
            rationale=f"Keywords integrity: {len(violations)} violation types, score: {integrity_score:.2f}"
        )
    
    def _analyze_keywords_completeness(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventCompletenessSignal:
        """Analiza completitud de keywords"""
        
        required_fields = self.keywords_schema
        present_fields = [f for f in required_fields if f in data and data[f]]
        
        # Validar cantidad mínima de keywords
        keywords = data.get("keywords", [])
        if isinstance(keywords, dict):
            keywords = list(keywords.values())
        
        has_sufficient_keywords = len(keywords) >= self.quality_thresholds["min_keywords"]
        
        # Calcular nivel de completitud
        field_completeness = len(present_fields) / len(required_fields) if required_fields else 1.0
        
        if field_completeness == 1.0 and has_sufficient_keywords:
            level = CompletenessLevel.COMPLETE
            score = 1.0
        elif field_completeness >= 0.75 and has_sufficient_keywords:
            level = CompletenessLevel.MOSTLY_COMPLETE
            score = 0.85
        elif field_completeness >= 0.5 or has_sufficient_keywords:
            level = CompletenessLevel.INCOMPLETE
            score = 0.6
        else:
            level = CompletenessLevel.EMPTY
            score = 0.3
        
        return EventCompletenessSignal(
            context=context,
            source=source,
            completeness_level=level,
            required_fields=required_fields,
            present_fields=present_fields,
            completeness_score=score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Keywords completeness: {len(present_fields)}/{len(required_fields)} fields, "
                     f"{len(keywords)} keywords (min: {self.quality_thresholds['min_keywords']})"
        )
    
    def _analyze_questions_integrity(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> DataIntegritySignal:
        """Analiza integridad de questions"""
        
        violations = []
        violation_types = set()
        
        # Extraer questions
        questions = data.get("questions", [])
        if not isinstance(questions, list):
            questions = []
        
        # Validar IDs únicos
        question_ids = []
        for q in questions:
            if isinstance(q, dict) and "id" in q:
                question_ids.append(q["id"])
        
        duplicate_ids = self._find_duplicates(question_ids)
        if duplicate_ids:
            violations.append({
                "type": "duplicate_question_ids",
                "count": len(duplicate_ids),
                "ids": list(duplicate_ids)[:10]
            })
            violation_types.add(IntegrityViolationType.DUPLICATE_VALUE)
        
        # Validar estructura de questions
        malformed_questions = []
        for i, q in enumerate(questions[:50]):  # Limitar análisis
            if not isinstance(q, dict):
                malformed_questions.append(f"index_{i}")
            elif "id" not in q or "text" not in q:
                malformed_questions.append(q.get("id", f"index_{i}"))
        
        if malformed_questions:
            violations.append({
                "type": "malformed_questions",
                "count": len(malformed_questions),
                "examples": malformed_questions[:5]
            })
            violation_types.add(IntegrityViolationType.INVALID_FORMAT)
        
        # Calcular score
        total_issues = len(duplicate_ids) + len(malformed_questions)
        total_questions = max(len(questions), 1)
        integrity_score = max(0.0, 1.0 - (total_issues / total_questions))
        
        return DataIntegritySignal(
            context=context,
            source=source,
            source_file=context.node_id,
            source_file_type="questions",
            referenced_files=[],
            valid_references=[],
            broken_references=[],
            violations=violations,
            integrity_score=integrity_score,
            violation_types=violation_types,
            confidence=SignalConfidence.HIGH,
            rationale=f"Questions integrity: {len(violations)} violation types, "
                     f"{len(questions)} questions analyzed"
        )
    
    def _analyze_questions_completeness(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventCompletenessSignal:
        """Analiza completitud de questions"""
        
        required_fields = self.questions_schema
        present_fields = [f for f in required_fields if f in data and data[f]]
        
        # Validar cantidad de questions
        questions = data.get("questions", [])
        if not isinstance(questions, list):
            questions = []
        
        has_sufficient_questions = len(questions) >= self.quality_thresholds["min_questions"]
        
        # Calcular completitud de campos en questions
        if questions:
            question_completeness_scores = []
            for q in questions[:20]:  # Muestra
                if isinstance(q, dict):
                    q_fields = ["id", "text", "type"]
                    q_present = sum(1 for f in q_fields if f in q and q[f])
                    question_completeness_scores.append(q_present / len(q_fields))
            
            avg_question_completeness = sum(question_completeness_scores) / len(question_completeness_scores) if question_completeness_scores else 0
        else:
            avg_question_completeness = 0
        
        # Nivel global
        field_completeness = len(present_fields) / len(required_fields) if required_fields else 1.0
        overall_score = (field_completeness + avg_question_completeness) / 2
        
        if overall_score >= 0.9 and has_sufficient_questions:
            level = CompletenessLevel.COMPLETE
        elif overall_score >= 0.7:
            level = CompletenessLevel.MOSTLY_COMPLETE
        elif overall_score >= 0.4:
            level = CompletenessLevel.INCOMPLETE
        else:
            level = CompletenessLevel.EMPTY
        
        return EventCompletenessSignal(
            context=context,
            source=source,
            completeness_level=level,
            required_fields=required_fields,
            present_fields=present_fields,
            completeness_score=overall_score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Questions completeness: {len(questions)} questions, "
                     f"avg field completeness: {avg_question_completeness:.2f}"
        )
    
    def _find_duplicates(self, items: List[Any]) -> Set[Any]:
        """Encuentra elementos duplicados en una lista"""
        seen = set()
        duplicates = set()
        
        for item in items:
            # Normalizar para comparación
            normalized = str(item).lower().strip() if item else ""
            if normalized:
                if normalized in seen:
                    duplicates.add(item)
                seen.add(normalized)
        
        return duplicates
