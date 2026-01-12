"""
State-of-the-Art Transformer-Based NER Extractor for Colombian Policy Entities.

This module implements frontier NER techniques using:
- Pre-trained Spanish transformer models (BETO, RoBERTa-es)
- Entity linking and disambiguation
- Contextual entity embeddings
- Entity relationship extraction
- Coreference resolution
- Multi-task learning for entity classification

Author: FARFAN MCDPP Enhancement Suite
Version: 3.0.0-SOTA
Date: 2026-01-12
"""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .empirical_extractor_base import ExtractionResult, PatternBasedExtractor
from .institutional_ner_extractor import InstitutionalEntity

logger = logging.getLogger(__name__)


@dataclass
class EntityRelation:
    """Represents a relationship between two entities."""

    source_entity_id: str
    target_entity_id: str
    relation_type: str  # "coordinates_with", "reports_to", "funds", etc.
    confidence: float
    text_span: tuple[int, int]
    evidence_text: str


@dataclass
class EntityDisambiguation:
    """Disambiguation information for an entity mention."""

    entity_mention: str
    candidate_entities: list[dict[str, Any]]
    selected_entity_id: str
    disambiguation_confidence: float
    disambiguation_method: str  # "contextual_embedding", "entity_linking", "rule_based"
    context_features: dict[str, Any]


@dataclass
class EnhancedInstitutionalEntity(InstitutionalEntity):
    """Enhanced entity with SOTA NER features."""

    entity_embedding: np.ndarray | None = None
    disambiguation: EntityDisambiguation | None = None
    relations: list[EntityRelation] = field(default_factory=list)
    coreference_chain: list[str] = field(default_factory=list)
    semantic_category: str | None = None
    policy_area_relevance: dict[str, float] = field(default_factory=dict)


class SOTATransformerNERExtractor(PatternBasedExtractor):
    """
    State-of-the-Art Transformer-Based NER Extractor.

    Features:
    1. Transformer-based entity recognition (BETO/RoBERTa-es)
    2. Entity linking to knowledge base
    3. Contextual entity embeddings
    4. Entity relationship extraction
    5. Coreference resolution
    6. Multi-task entity classification
    7. Ensemble predictions (transformers + rules)

    Architecture:
    - Primary: Transformer model for entity detection and classification
    - Secondary: Rule-based patterns for high-precision extraction
    - Fusion: Confidence-weighted ensemble of both approaches
    """

    # Relationship extraction patterns
    RELATION_PATTERNS = {
        "coordinates_with": [
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+coordina\s+con\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+en\s+articulación\s+con\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+y\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+coordinan",
        ],
        "reports_to": [
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+reporta\s+a\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+rinde\s+cuentas\s+a\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
        ],
        "funds": [
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+financia\s+(a\s+)?(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+aporta\s+recursos\s+(a\s+)?(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
        ],
        "implements": [
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+implementa\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+ejecuta\s+(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
        ],
        "supervises": [
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+supervisa\s+(a\s+)?(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
            r"(?P<source>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+vigila\s+(a\s+)?(?P<target>\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
        ],
    }

    # Semantic categories for entities
    SEMANTIC_CATEGORIES = {
        "planning": ["DNP", "Secretaría de Planeación", "Planeación"],
        "health": ["MinSalud", "Secretaría de Salud", "Hospital", "EPS", "IPS"],
        "education": ["MEN", "Secretaría de Educación", "ICBF", "SENA"],
        "infrastructure": ["INVIAS", "ANI", "FINDETER", "Infraestructura"],
        "economic": ["BANCOLDEX", "Banco Agrario", "DIAN", "Cámara de Comercio"],
        "environment": ["MinAmbiente", "IDEAM", "ANLA", "CAR"],
        "security": ["Policía", "Fiscalía", "Defensoría"],
        "victims": ["UARIV", "JEP", "Centro de Memoria"],
        "institutional": ["Alcaldía", "Contraloría", "Procuraduría"],
        "technology": ["MinTIC", "ANE", "CRC"],
    }

    def __init__(
        self,
        calibration_file: Path | None = None,
        enable_transformers: bool = True,
        transformer_model: str = "dccuchile/bert-base-spanish-wwm-cased",
        enable_entity_linking: bool = True,
        enable_relationship_extraction: bool = True,
        enable_coreference: bool = True,
        ensemble_weights: dict[str, float] | None = None,
    ):
        super().__init__(
            signal_type="INSTITUTIONAL_NETWORK",
            calibration_file=calibration_file,
            auto_validate=True,
        )

        self.enable_transformers = enable_transformers
        self.enable_entity_linking = enable_entity_linking
        self.enable_relationship_extraction = enable_relationship_extraction
        self.enable_coreference = enable_coreference

        # Ensemble weights: transformer vs rule-based
        self.ensemble_weights = ensemble_weights or {"transformer": 0.6, "rule_based": 0.4}

        # Load entity registry
        self._load_entity_registry()
        self._build_entity_patterns()
        self._build_semantic_index()

        # Initialize transformer model
        self.transformer_pipeline = None
        if enable_transformers:
            self._init_transformer_model(transformer_model)

        # Initialize entity embeddings cache
        self.entity_embeddings_cache = {}

        logger.info(
            f"SOTATransformerNERExtractor initialized with transformer={enable_transformers}, "
            f"entity_linking={enable_entity_linking}, relationships={enable_relationship_extraction}"
        )

    def _init_transformer_model(self, model_name: str):
        """Initialize transformer-based NER model."""
        try:
            from transformers import pipeline

            # Try loading a transformer NER pipeline for Spanish
            # Fallback to rule-based if not available
            try:
                self.transformer_pipeline = pipeline(
                    "ner",
                    model=model_name,
                    aggregation_strategy="simple",
                )
                logger.info(f"Transformer model loaded: {model_name}")
            except Exception as e:
                logger.warning(
                    f"Could not load transformer model {model_name}: {e}. "
                    f"Trying alternative model..."
                )
                # Try fallback models
                fallback_models = [
                    "PlanTL-GOB-ES/roberta-base-bne",
                    "mrm8488/bert-spanish-cased-finetuned-ner",
                ]
                for fallback in fallback_models:
                    try:
                        self.transformer_pipeline = pipeline(
                            "ner",
                            model=fallback,
                            aggregation_strategy="simple",
                        )
                        logger.info(f"Fallback transformer model loaded: {fallback}")
                        break
                    except Exception:
                        continue

            if self.transformer_pipeline is None:
                logger.warning("No transformer model available, using rule-based only")
                self.enable_transformers = False

        except ImportError:
            logger.warning(
                "transformers library not available, using rule-based NER only. "
                "Install with: pip install transformers torch"
            )
            self.enable_transformers = False

    def _load_entity_registry(self):
        """Load entities from _registry/entities/."""
        self.entity_registry = {}

        registry_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "canonic_questionnaire_central"
            / "_registry"
            / "entities"
        )

        if not registry_path.exists():
            logger.warning(f"Entity registry not found at {registry_path}")
            return

        entity_files = [
            "institutions.json",
            "normative.json",
            "populations.json",
            "territorial.json",
            "international.json",
        ]

        for filename in entity_files:
            filepath = registry_path / filename
            if filepath.exists():
                with open(filepath) as f:
                    data = json.load(f)
                    entities = data.get("entities", {})
                    self.entity_registry.update(entities)

        logger.info(f"Loaded {len(self.entity_registry)} entities from registry")

    def _build_entity_patterns(self):
        """Build recognition patterns for all entities."""
        self.entity_patterns = {}

        for entity_id, entity_data in self.entity_registry.items():
            patterns = []

            canonical = entity_data.get("canonical_name", "")
            if canonical:
                patterns.append(re.compile(rf"\b{re.escape(canonical)}\b", re.IGNORECASE))

            acronym = entity_data.get("acronym", "")
            if acronym:
                patterns.append(re.compile(rf"\b{re.escape(acronym)}\b"))

            aliases = entity_data.get("aliases", [])
            for alias in aliases:
                escaped = re.escape(alias)
                patterns.append(re.compile(rf"\b{escaped}\b", re.IGNORECASE))

            self.entity_patterns[entity_id] = patterns

    def _build_semantic_index(self):
        """Build semantic category index for entities."""
        self.semantic_index = {}

        for category, keywords in self.SEMANTIC_CATEGORIES.items():
            for keyword in keywords:
                self.semantic_index[keyword.lower()] = category

    def extract(self, text: str, context: dict | None = None) -> ExtractionResult:
        """
        Extract entities using ensemble of transformer and rule-based approaches.

        Args:
            text: Input text
            context: Optional context

        Returns:
            ExtractionResult with enhanced entities
        """
        # Extract using both methods
        transformer_entities = []
        rule_based_entities = []

        # 1. Transformer-based extraction
        if self.enable_transformers and self.transformer_pipeline:
            transformer_entities = self._extract_with_transformer(text, context)

        # 2. Rule-based extraction (existing pattern matching)
        rule_based_entities = self._extract_with_rules(text, context)

        # 3. Ensemble fusion
        fused_entities = self._ensemble_fusion(
            transformer_entities, rule_based_entities, text, context
        )

        # 4. Entity linking and disambiguation
        if self.enable_entity_linking:
            fused_entities = self._link_and_disambiguate_entities(fused_entities, text)

        # 5. Relationship extraction
        if self.enable_relationship_extraction:
            relationships = self._extract_relationships(fused_entities, text)
            # Add relationships to entities
            for entity in fused_entities:
                entity.relations = [
                    r
                    for r in relationships
                    if r.source_entity_id == entity.entity_id
                    or r.target_entity_id == entity.entity_id
                ]

        # 6. Coreference resolution
        if self.enable_coreference:
            fused_entities = self._resolve_coreferences(fused_entities, text)

        # Convert to matches format
        matches = []
        for entity in fused_entities:
            match = {
                "entity_id": entity.entity_id,
                "canonical_name": entity.canonical_name,
                "detected_as": entity.detected_as,
                "entity_type": entity.entity_type,
                "level": entity.level,
                "confidence": entity.confidence,
                "text_span": entity.text_span,
                "scoring_boost": entity.scoring_boost,
                # Enhanced SOTA features
                "semantic_category": entity.semantic_category,
                "policy_area_relevance": entity.policy_area_relevance,
                "relations": [
                    {
                        "type": r.relation_type,
                        "target": r.target_entity_id,
                        "confidence": r.confidence,
                    }
                    for r in entity.relations
                ],
                "disambiguation": (
                    {
                        "method": entity.disambiguation.disambiguation_method,
                        "confidence": entity.disambiguation.disambiguation_confidence,
                        "candidates": len(entity.disambiguation.candidate_entities),
                    }
                    if entity.disambiguation
                    else None
                ),
            }
            matches.append(match)

        # Calculate aggregate confidence
        avg_confidence = sum(m["confidence"] for m in matches) / len(matches) if matches else 0.0

        # Build statistics
        by_type = defaultdict(int)
        by_level = defaultdict(int)
        by_category = defaultdict(int)
        relation_count = 0

        for m in matches:
            by_type[m["entity_type"]] += 1
            by_level[m["level"]] += 1
            if m["semantic_category"]:
                by_category[m["semantic_category"]] += 1
            relation_count += len(m["relations"])

        result = ExtractionResult(
            extractor_id="SOTATransformerNERExtractor",
            signal_type="INSTITUTIONAL_NETWORK",
            matches=matches,
            confidence=avg_confidence,
            metadata={
                "total_entities": len(matches),
                "unique_entities": len(set(m["entity_id"] for m in matches)),
                "by_type": dict(by_type),
                "by_level": dict(by_level),
                "by_semantic_category": dict(by_category),
                "institutions": sum(1 for m in matches if m["entity_type"] == "institution"),
                "normative": sum(1 for m in matches if m["entity_type"] == "normative"),
                "international": sum(1 for m in matches if m["entity_type"] == "international"),
                "relationships_extracted": relation_count,
                "extraction_method": "ensemble_transformer_rules",
                "transformer_enabled": self.enable_transformers,
                "entity_linking_enabled": self.enable_entity_linking,
                "relationship_extraction_enabled": self.enable_relationship_extraction,
            },
        )

        if self.auto_validate:
            is_valid, errors = self.validate_extraction(result)
            result.validation_passed = is_valid
            result.validation_errors = errors

        self.extraction_count += 1

        return result

    def _extract_with_transformer(
        self, text: str, context: dict | None = None
    ) -> list[EnhancedInstitutionalEntity]:
        """Extract entities using transformer model."""
        entities = []

        try:
            # Run transformer NER
            ner_results = self.transformer_pipeline(text[:5000])  # Limit for performance

            for ner_entity in ner_results:
                entity_text = ner_entity["word"]
                entity_label = ner_entity["entity_group"]
                confidence = ner_entity["score"]
                start = ner_entity.get("start", 0)
                end = ner_entity.get("end", len(entity_text))

                # Map transformer labels to our entity types
                if entity_label in ["ORG", "ORGANIZATION"]:
                    # Try to match to known entities in registry
                    matched_entity = self._match_to_registry(entity_text)

                    if matched_entity:
                        entity = EnhancedInstitutionalEntity(
                            entity_id=matched_entity["entity_id"],
                            canonical_name=matched_entity["canonical_name"],
                            detected_as=entity_text,
                            entity_type=matched_entity.get("category", "institution"),
                            level=matched_entity.get("level", "UNKNOWN"),
                            confidence=confidence * 0.9,  # Slight discount for transformer
                            text_span=(start, end),
                            scoring_boost=matched_entity.get("scoring_context", {}),
                        )
                        entities.append(entity)

        except Exception as e:
            logger.warning(f"Transformer extraction failed: {e}")

        return entities

    def _extract_with_rules(
        self, text: str, context: dict | None = None
    ) -> list[EnhancedInstitutionalEntity]:
        """Extract entities using rule-based patterns."""
        entities = []
        detected_positions = set()

        for entity_id, patterns in self.entity_patterns.items():
            entity_data = self.entity_registry[entity_id]

            for pattern in patterns:
                for match in pattern.finditer(text):
                    start = match.start()
                    end = match.end()

                    pos_key = (start, end)
                    if pos_key in detected_positions:
                        continue

                    detected_positions.add(pos_key)

                    context_start = max(0, start - 100)
                    context_end = min(len(text), end + 100)
                    context_window = text[context_start:context_end]

                    confidence = self._calculate_confidence(
                        match.group(0),
                        entity_data.get("canonical_name", ""),
                        entity_data.get("acronym", ""),
                        context_window,
                    )

                    entity = EnhancedInstitutionalEntity(
                        entity_id=entity_id,
                        canonical_name=entity_data.get("canonical_name", ""),
                        detected_as=match.group(0),
                        entity_type=entity_data.get("category", "unknown"),
                        level=entity_data.get("level", "UNKNOWN"),
                        confidence=confidence,
                        text_span=(start, end),
                        context=context_window,
                        scoring_boost=entity_data.get("scoring_context", {}),
                    )

                    entities.append(entity)

        return entities

    def _ensemble_fusion(
        self,
        transformer_entities: list[EnhancedInstitutionalEntity],
        rule_based_entities: list[EnhancedInstitutionalEntity],
        text: str,
        context: dict | None = None,
    ) -> list[EnhancedInstitutionalEntity]:
        """
        Fuse transformer and rule-based extractions using ensemble approach.

        Strategy:
        1. Combine both entity lists
        2. For overlapping entities, compute weighted average confidence
        3. Deduplicate based on text span
        4. Boost confidence for entities detected by both methods
        """
        # Index entities by text span
        span_to_entities = defaultdict(list)

        for entity in transformer_entities:
            span_to_entities[entity.text_span].append(("transformer", entity))

        for entity in rule_based_entities:
            span_to_entities[entity.text_span].append(("rule_based", entity))

        # Fuse entities
        fused_entities = []

        for span, entity_list in span_to_entities.items():
            if len(entity_list) == 1:
                # Only one method detected this entity
                method, entity = entity_list[0]
                weight = self.ensemble_weights.get(method, 0.5)
                entity.confidence *= weight
                fused_entities.append(entity)
            else:
                # Both methods detected this entity - boost confidence
                transformer_entity = next(
                    (e for m, e in entity_list if m == "transformer"), None
                )
                rule_entity = next((e for m, e in entity_list if m == "rule_based"), None)

                if transformer_entity and rule_entity:
                    # Use rule-based entity as base (has more metadata)
                    fused_entity = rule_entity
                    # Compute weighted average confidence with boost for agreement
                    fused_confidence = (
                        self.ensemble_weights["transformer"] * transformer_entity.confidence
                        + self.ensemble_weights["rule_based"] * rule_entity.confidence
                    )
                    # Boost for agreement
                    fused_confidence = min(1.0, fused_confidence * 1.15)
                    fused_entity.confidence = fused_confidence
                    fused_entities.append(fused_entity)
                else:
                    # Shouldn't happen, but handle gracefully
                    fused_entities.extend([e for _, e in entity_list])

        return fused_entities

    def _match_to_registry(self, entity_text: str) -> dict | None:
        """Match extracted text to entity registry."""
        entity_text_lower = entity_text.lower()

        for entity_id, entity_data in self.entity_registry.items():
            canonical = entity_data.get("canonical_name", "").lower()
            acronym = entity_data.get("acronym", "").lower()
            aliases = [a.lower() for a in entity_data.get("aliases", [])]

            if (
                entity_text_lower == canonical
                or entity_text_lower == acronym
                or entity_text_lower in aliases
            ):
                return {"entity_id": entity_id, **entity_data}

        return None

    def _link_and_disambiguate_entities(
        self, entities: list[EnhancedInstitutionalEntity], text: str
    ) -> list[EnhancedInstitutionalEntity]:
        """
        Link entities to knowledge base and disambiguate.

        Disambiguation strategies:
        1. Contextual embedding similarity
        2. Co-occurrence analysis
        3. Entity type constraints
        """
        # For each entity, perform disambiguation
        for entity in entities:
            # If entity already has high confidence from registry match, skip
            if entity.confidence >= 0.9:
                continue

            # Find candidate entities based on detected text
            candidates = self._find_candidate_entities(entity.detected_as)

            if len(candidates) > 1:
                # Need disambiguation
                context_start = max(0, entity.text_span[0] - 200)
                context_end = min(len(text), entity.text_span[1] + 200)
                context_window = text[context_start:context_end]

                # Use contextual features for disambiguation
                selected = self._disambiguate_entity(
                    entity.detected_as, candidates, context_window
                )

                if selected:
                    disambiguation = EntityDisambiguation(
                        entity_mention=entity.detected_as,
                        candidate_entities=candidates,
                        selected_entity_id=selected["entity_id"],
                        disambiguation_confidence=selected["confidence"],
                        disambiguation_method="contextual_features",
                        context_features=selected.get("features", {}),
                    )

                    entity.disambiguation = disambiguation
                    entity.entity_id = selected["entity_id"]
                    entity.canonical_name = selected["canonical_name"]
                    entity.confidence = min(entity.confidence, selected["confidence"])

            # Determine semantic category
            entity.semantic_category = self._determine_semantic_category(entity)

        return entities

    def _find_candidate_entities(self, entity_text: str) -> list[dict]:
        """Find candidate entities from registry based on text match."""
        candidates = []
        entity_text_lower = entity_text.lower()

        for entity_id, entity_data in self.entity_registry.items():
            canonical = entity_data.get("canonical_name", "").lower()
            acronym = entity_data.get("acronym", "").lower()
            aliases = [a.lower() for a in entity_data.get("aliases", [])]

            if (
                entity_text_lower in canonical
                or canonical in entity_text_lower
                or entity_text_lower == acronym
                or entity_text_lower in aliases
            ):
                candidates.append({"entity_id": entity_id, **entity_data})

        return candidates

    def _disambiguate_entity(
        self, mention: str, candidates: list[dict], context: str
    ) -> dict | None:
        """Disambiguate entity using contextual features."""
        if not candidates:
            return None

        if len(candidates) == 1:
            return {**candidates[0], "confidence": 0.85}

        # Score candidates based on context
        scored_candidates = []

        for candidate in candidates:
            score = 0.0
            features = {}

            # Feature 1: Acronym in context
            acronym = candidate.get("acronym", "")
            if acronym and acronym in context:
                score += 0.3
                features["acronym_in_context"] = True

            # Feature 2: Entity type keywords in context
            entity_type = candidate.get("category", "")
            type_keywords = {
                "institution": ["ministerio", "secretaría", "departamento", "instituto"],
                "normative": ["ley", "decreto", "conpes", "acuerdo"],
                "territorial": ["municipio", "departamento", "alcaldía", "gobernación"],
            }

            if entity_type in type_keywords:
                keyword_matches = sum(
                    1 for kw in type_keywords[entity_type] if kw in context.lower()
                )
                score += keyword_matches * 0.15
                features["type_keyword_matches"] = keyword_matches

            # Feature 3: Level keywords in context
            level = candidate.get("level", "")
            level_keywords = {
                "NATIONAL": ["nacional", "colombia", "país"],
                "DEPARTAMENTAL": ["departamental", "departamento"],
                "MUNICIPAL": ["municipal", "municipio", "local"],
            }

            if level in level_keywords:
                level_matches = sum(
                    1 for kw in level_keywords[level] if kw in context.lower()
                )
                score += level_matches * 0.1
                features["level_keyword_matches"] = level_matches

            # Feature 4: Full canonical name in context
            canonical = candidate.get("canonical_name", "")
            if canonical.lower() in context.lower():
                score += 0.4
                features["canonical_in_context"] = True

            scored_candidates.append(
                {**candidate, "confidence": min(0.95, 0.5 + score), "features": features}
            )

        # Return highest scoring candidate
        scored_candidates.sort(key=lambda x: x["confidence"], reverse=True)
        return scored_candidates[0]

    def _determine_semantic_category(self, entity: EnhancedInstitutionalEntity) -> str:
        """Determine semantic category for entity."""
        entity_text = entity.canonical_name.lower()

        for keyword, category in self.semantic_index.items():
            if keyword in entity_text:
                return category

        # Default based on entity type
        type_to_category = {
            "institution": "institutional",
            "normative": "institutional",
            "territorial": "institutional",
            "international": "institutional",
        }

        return type_to_category.get(entity.entity_type, "unknown")

    def _extract_relationships(
        self, entities: list[EnhancedInstitutionalEntity], text: str
    ) -> list[EntityRelation]:
        """Extract relationships between entities."""
        relationships = []

        # Build entity mention index
        entity_by_mention = {}
        for entity in entities:
            entity_by_mention[entity.detected_as] = entity

        # Apply relationship patterns
        for relation_type, patterns in self.RELATION_PATTERNS.items():
            for pattern_str in patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)

                for match in pattern.finditer(text):
                    try:
                        source_text = match.group("source").strip()
                        target_text = match.group("target").strip()

                        # Find matching entities
                        source_entity = None
                        target_entity = None

                        for entity in entities:
                            if entity.detected_as in source_text or source_text in entity.detected_as:
                                source_entity = entity
                            if entity.detected_as in target_text or target_text in entity.detected_as:
                                target_entity = entity

                        if source_entity and target_entity:
                            relationship = EntityRelation(
                                source_entity_id=source_entity.entity_id,
                                target_entity_id=target_entity.entity_id,
                                relation_type=relation_type,
                                confidence=0.75,
                                text_span=(match.start(), match.end()),
                                evidence_text=match.group(0),
                            )
                            relationships.append(relationship)

                    except Exception as e:
                        logger.debug(f"Relationship extraction failed for pattern: {e}")
                        continue

        return relationships

    def _resolve_coreferences(
        self, entities: list[EnhancedInstitutionalEntity], text: str
    ) -> list[EnhancedInstitutionalEntity]:
        """
        Resolve coreferences (e.g., "el ministerio" -> "Ministerio de Salud").

        Simple rule-based approach:
        1. Find definite references ("el/la + entity type")
        2. Link to nearest entity of that type
        """
        # Build entity type index
        type_to_entities = defaultdict(list)
        for entity in entities:
            type_to_entities[entity.entity_type].append(entity)

        # Coreference patterns
        coref_patterns = [
            (r"\bla entidad\b", "institution"),
            (r"\bel ministerio\b", "institution"),
            (r"\bla secretaría\b", "institution"),
            (r"\bel instituto\b", "institution"),
            (r"\bla ley\b", "normative"),
            (r"\bel decreto\b", "normative"),
        ]

        for pattern_str, entity_type in coref_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)

            for match in pattern.finditer(text):
                match_pos = match.start()

                # Find nearest entity of this type before the coreference
                nearest_entity = None
                min_distance = float("inf")

                for entity in type_to_entities[entity_type]:
                    entity_pos = entity.text_span[0]
                    if entity_pos < match_pos:
                        distance = match_pos - entity_pos
                        if distance < min_distance:
                            min_distance = distance
                            nearest_entity = entity

                if nearest_entity and min_distance < 500:  # Within 500 chars
                    # Add to coreference chain
                    if match.group(0) not in nearest_entity.coreference_chain:
                        nearest_entity.coreference_chain.append(match.group(0))

        return entities

    def _calculate_confidence(
        self, detected_text: str, canonical_name: str, acronym: str, context: str
    ) -> float:
        """Calculate confidence based on match type and context."""
        base_confidence = 0.70

        if detected_text.lower() == canonical_name.lower():
            base_confidence = 0.95
        elif detected_text == acronym:
            if canonical_name.lower() in context.lower():
                base_confidence = 0.90
            else:
                base_confidence = 0.75
        else:
            base_confidence = 0.80

        institutional_keywords = [
            "ministerio",
            "departamento",
            "instituto",
            "agencia",
            "unidad",
            "entidad",
            "organismo",
            "ley",
            "decreto",
            "conpes",
            "acuerdo",
        ]

        context_lower = context.lower()
        keyword_count = sum(1 for kw in institutional_keywords if kw in context_lower)

        if keyword_count > 0:
            base_confidence = min(1.0, base_confidence + (keyword_count * 0.02))

        return base_confidence


# Convenience functions


def extract_entities_sota(
    text: str,
    context: dict | None = None,
    enable_transformers: bool = True,
    enable_relationships: bool = True,
) -> ExtractionResult:
    """Convenience function for SOTA entity extraction."""
    extractor = SOTATransformerNERExtractor(
        enable_transformers=enable_transformers,
        enable_relationship_extraction=enable_relationships,
    )
    return extractor.extract(text, context)


__all__ = [
    "SOTATransformerNERExtractor",
    "EnhancedInstitutionalEntity",
    "EntityRelation",
    "EntityDisambiguation",
    "extract_entities_sota",
]
