"""
Institutional NER Extractor (MC09)

Extracts institutional entities from text and emits MC09 signals.

Identifies:
- Colombian government institutions
- International organizations
- NGOs and civil society
- Local government entities
- PDET-specific actors

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging

from .base_extractor import BaseSignalExtractor, ExtractionContext

from canonic_questionnaire_central.core.signal import Signal, SignalType

logger = logging.getLogger(__name__)


class InstitutionalNERExtractor(BaseSignalExtractor):
    """
    Extracts institutional entities and emits MC09 signals.
    
    Calibrated empirical availability: 0.68 (from MC09_institutional_network.json)
    
    Uses pre-loaded entity dictionary from _registry/entities/
    """
    
    SIGNAL_TYPE = SignalType.MC09_INSTITUTIONAL
    CAPABILITIES_REQUIRED = ["NER_EXTRACTION", "ENTITY_RESOLUTION", "COREFERENCE"]
    EMPIRICAL_AVAILABILITY = 0.68
    DEFAULT_PHASE = "phase_1"
    DEFAULT_SLOT = "D2-Q2"  # Institutional actors dimension
    
    # Institution type hierarchy
    INSTITUTION_TYPES = {
        "NATIONAL": ["ministerio", "departamento", "agencia", "superintendencia", "unidad"],
        "TERRITORIAL": ["gobernación", "alcaldía", "secretaría", "umata"],
        "JUSTICE": ["juzgado", "tribunal", "fiscalía", "defensoría"],
        "CONTROL": ["contraloría", "procuraduría", "personería"],
        "INTERNATIONAL": ["onu", "pnud", "unicef", "oim", "acnur", "oea"],
        "CIVIL_SOCIETY": ["fundación", "corporación", "asociación", "organización"],
        "PDET_SPECIFIC": ["aut", "art", "ctjt", "pnis", "patr"]
    }
    
    def __init__(self, sdo, entities_path: Optional[str] = None):
        super().__init__(sdo)
        
        # Load entity dictionary
        self._entities: Dict[str, Dict] = {}
        self._entity_patterns: List[tuple] = []
        
        if entities_path:
            self._load_entities(entities_path)
        else:
            # Default path
            default_path = Path(__file__).resolve().parents[5] / "canonic_questionnaire_central" / "_registry" / "entities"
            self._load_entities_from_directory(default_path)
        
        # Build lookup structures
        self._build_lookup()
    
    def _load_entities(self, path: str) -> None:
        """Load entities from a single JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for entity in data:
                    name = entity.get("name", "").lower()
                    if name:
                        self._entities[name] = entity
            elif isinstance(data, dict):
                if "entities" in data:
                    for entity in data["entities"]:
                        name = entity.get("name", "").lower()
                        if name:
                            self._entities[name] = entity
                else:
                    for name, entity_data in data.items():
                        self._entities[name.lower()] = entity_data
            
            logger.info(f"Loaded {len(self._entities)} entities from {path}")
        except Exception as e:
            logger.warning(f"Could not load entities from {path}: {e}")
    
    def _load_entities_from_directory(self, directory: Path) -> None:
        """Load entities from all JSON files in a directory."""
        if not directory.exists():
            logger.warning(f"Entities directory not found: {directory}")
            return
        
        for json_file in directory.glob("*.json"):
            if "index" in json_file.name.lower():
                continue  # Skip index files
            
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                entities_list = data if isinstance(data, list) else data.get("entities", [])
                
                for entity in entities_list:
                    name = entity.get("name", "").lower()
                    if name:
                        self._entities[name] = entity
                        
                        # Also add acronyms/aliases
                        for alias in entity.get("aliases", []):
                            self._entities[alias.lower()] = entity
                
            except Exception as e:
                logger.debug(f"Could not parse {json_file}: {e}")
        
        logger.info(f"Loaded {len(self._entities)} total entities from {directory}")
    
    def _build_lookup(self) -> None:
        """Build efficient lookup patterns."""
        # Sort by length (longest first) for greedy matching
        sorted_names = sorted(self._entities.keys(), key=len, reverse=True)
        
        # Build regex patterns for each entity
        for name in sorted_names:
            # Escape special characters
            pattern = re.escape(name)
            # Add word boundaries
            compiled = re.compile(r'\b' + pattern + r'\b', re.IGNORECASE)
            self._entity_patterns.append((compiled, name))
    
    def extract(self, text: str, context: ExtractionContext) -> List[Signal]:
        """
        Extract institutional entities from text.
        
        Returns list of MC09 signals with entity information.
        """
        signals = []
        found_entities: Set[str] = set()
        
        # Method 1: Dictionary lookup
        for pattern, name in self._entity_patterns:
            matches = list(pattern.finditer(text))
            if matches and name not in found_entities:
                found_entities.add(name)
                
                entity_data = self._entities.get(name, {})
                
                payload = {
                    "entity_name": entity_data.get("name", name),
                    "entity_type": self._determine_entity_type(name, entity_data),
                    "entity_id": entity_data.get("id", f"ENT_{hash(name) % 100000}"),
                    "occurrences": len(matches),
                    "positions": [(m.start(), m.end()) for m in matches[:5]],  # First 5
                    "context_snippets": [
                        self._get_context_window(text, m) for m in matches[:3]
                    ],
                    "metadata": {
                        "jurisdiction": entity_data.get("jurisdiction"),
                        "sector": entity_data.get("sector"),
                        "pdet_relevance": entity_data.get("pdet_relevance", False)
                    },
                    "confidence": self._calculate_confidence(matches, entity_data)
                }
                
                # Determine slot based on entity type
                slot = self._determine_slot(payload["entity_type"])
                
                signal = self.create_signal(
                    payload=payload,
                    context=context,
                    slot=slot,
                    extraction_pattern="DICTIONARY_MATCH",
                    enrichment=True
                )
                
                signals.append(signal)
        
        # Method 2: Pattern-based detection for unknown entities
        signals.extend(self._extract_unknown_entities(text, context, found_entities))
        
        logger.debug(f"Extracted {len(signals)} institutional entity signals")
        return signals
    
    def _extract_unknown_entities(
        self, 
        text: str, 
        context: ExtractionContext,
        known_entities: Set[str]
    ) -> List[Signal]:
        """Extract potential entities not in dictionary."""
        signals = []
        
        # Pattern for potential institutions
        institution_pattern = re.compile(
            r'\b((?:ministerio|secretar[íi]a|departamento|agencia|unidad|oficina|direcci[óo]n)\s+'
            r'(?:de\s+)?[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)\b',
            re.IGNORECASE
        )
        
        for match in institution_pattern.finditer(text):
            entity_name = match.group(1).lower()
            
            if entity_name in known_entities:
                continue
            
            payload = {
                "entity_name": match.group(1),
                "entity_type": "UNKNOWN",
                "entity_id": f"UNK_{hash(entity_name) % 100000}",
                "occurrences": 1,
                "positions": [(match.start(), match.end())],
                "context_snippets": [self._get_context_window(text, match)],
                "metadata": {
                    "source": "PATTERN_DETECTION",
                    "requires_validation": True
                },
                "confidence": 0.5  # Lower confidence for unknown entities
            }
            
            signal = self.create_signal(
                payload=payload,
                context=context,
                slot=self.DEFAULT_SLOT,
                extraction_pattern="PATTERN_DETECTION",
                enrichment=False  # Not enrichment since unvalidated
            )
            
            signals.append(signal)
            known_entities.add(entity_name)
        
        return signals
    
    def _determine_entity_type(self, name: str, entity_data: Dict) -> str:
        """Determine the type of institution."""
        # Check entity data first
        if entity_data.get("type"):
            return entity_data["type"]
        
        name_lower = name.lower()
        
        for type_name, keywords in self.INSTITUTION_TYPES.items():
            if any(kw in name_lower for kw in keywords):
                return type_name
        
        return "OTHER"
    
    def _get_context_window(self, text: str, match: re.Match, window: int = 100) -> str:
        """Get surrounding context."""
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        return text[start:end].strip()
    
    def _calculate_confidence(self, matches: List, entity_data: Dict) -> float:
        """Calculate confidence score."""
        base = 0.7
        
        # Multiple occurrences increase confidence
        if len(matches) > 3:
            base += 0.1
        elif len(matches) > 1:
            base += 0.05
        
        # Known entity bonus
        if entity_data.get("id"):
            base += 0.1
        
        # PDET relevance bonus
        if entity_data.get("pdet_relevance"):
            base += 0.05
        
        return min(base, 1.0)
    
    def _determine_slot(self, entity_type: str) -> str:
        """Determine question slot based on entity type."""
        slot_map = {
            "NATIONAL": "D2-Q1",
            "TERRITORIAL": "D2-Q2",
            "JUSTICE": "D2-Q3",
            "CONTROL": "D2-Q3",
            "INTERNATIONAL": "D2-Q4",
            "CIVIL_SOCIETY": "D2-Q5",
            "PDET_SPECIFIC": "D2-Q2"
        }
        return slot_map.get(entity_type, self.DEFAULT_SLOT)
