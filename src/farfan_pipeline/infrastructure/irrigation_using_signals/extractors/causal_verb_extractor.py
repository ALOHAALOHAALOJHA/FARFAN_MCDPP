"""
Causal Verb Extractor (MC08)

Extracts causal relationships from text and emits MC08 signals.

Identifies:
- Causal verbs (garantizar, fortalecer, implementar, etc.)
- Causal connectors (mediante, a través de, para, etc.)
- Causal chains (action → connector → outcome)

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import re
from typing import Any, Dict, List, Optional, Tuple
import logging

from .base_extractor import BaseSignalExtractor, ExtractionContext

from canonic_questionnaire_central.core.signal import Signal, SignalType

logger = logging.getLogger(__name__)


class CausalVerbExtractor(BaseSignalExtractor):
    """
    Extracts causal verb chains and emits MC08 signals.
    
    Calibrated empirical availability: 0.72 (from MC08_causal_verbs.json)
    """
    
    SIGNAL_TYPE = SignalType.MC08_CAUSAL
    CAPABILITIES_REQUIRED = ["CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION", "VERB_ANALYSIS"]
    EMPIRICAL_AVAILABILITY = 0.72
    DEFAULT_PHASE = "phase_01"
    DEFAULT_SLOT = "D6-Q1"  # Causal explanation dimension
    
    # Causal action verbs (Spanish - Colombian administrative context)
    CAUSAL_VERBS = [
        # Transformative
        "garantizar", "fortalecer", "implementar", "promover", "mejorar",
        "facilitar", "generar", "desarrollar", "impulsar", "transformar",
        # Supportive
        "contribuir", "apoyar", "fomentar", "consolidar", "potenciar",
        # Corrective
        "reducir", "eliminar", "prevenir", "mitigar", "superar",
        # Structural
        "establecer", "crear", "diseñar", "formular", "articular",
        # Monitoring
        "verificar", "evaluar", "monitorear", "seguir", "supervisar"
    ]
    
    # Causal connectors
    CAUSAL_CONNECTORS = [
        # Purpose
        "para", "con el fin de", "con el propósito de", "con el objetivo de",
        "a fin de", "buscando", "orientado a",
        # Means
        "mediante", "a través de", "por medio de", "usando", "utilizando",
        # Result
        "lo cual", "lo que", "permitiendo", "logrando", "generando",
        # Condition
        "que permita", "que facilite", "que garantice", "que contribuya",
        # Implication
        "esto implica", "esto significa", "esto requiere", "esto conlleva"
    ]
    
    # Outcome indicators
    OUTCOME_INDICATORS = [
        "mejora", "aumento", "reducción", "incremento", "disminución",
        "fortalecimiento", "consolidación", "desarrollo", "transformación",
        "bienestar", "calidad", "acceso", "cobertura", "eficiencia"
    ]
    
    def __init__(self, sdo):
        super().__init__(sdo)
        
        # Compile patterns
        self._verb_pattern = re.compile(
            r'\b(' + '|'.join(self.CAUSAL_VERBS) + r')\w*\b',
            re.IGNORECASE
        )
        self._connector_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(c) for c in self.CAUSAL_CONNECTORS) + r')\b',
            re.IGNORECASE
        )
        self._outcome_pattern = re.compile(
            r'\b(' + '|'.join(self.OUTCOME_INDICATORS) + r')\w*\b',
            re.IGNORECASE
        )
    
    def extract(self, text: str, context: ExtractionContext) -> List[Signal]:
        """
        Extract causal chains from text.
        
        Returns list of MC08 signals with causal relationship data.
        """
        signals = []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        for sent_idx, sentence in enumerate(sentences):
            chains = self._extract_causal_chains(sentence)
            
            for chain in chains:
                payload = {
                    "action_verb": chain["verb"],
                    "connector": chain["connector"],
                    "outcome": chain.get("outcome"),
                    "full_sentence": sentence.strip(),
                    "sentence_index": sent_idx,
                    "chain_structure": chain["structure"],
                    "confidence": chain["confidence"],
                    "verb_category": self._categorize_verb(chain["verb"])
                }
                
                # Determine slot based on causal type
                slot = self._determine_slot(chain)
                
                signal = self.create_signal(
                    payload=payload,
                    context=context,
                    slot=slot,
                    extraction_pattern=f"CAUSAL_CHAIN:{chain['structure']}",
                    enrichment=True
                )
                
                signals.append(signal)
        
        logger.debug(f"Extracted {len(signals)} causal chain signals")
        return signals
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - could be enhanced with spaCy
        sentences = re.split(r'[.!?]\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_causal_chains(self, sentence: str) -> List[Dict[str, Any]]:
        """Extract all causal chains from a sentence."""
        chains = []
        
        verb_matches = list(self._verb_pattern.finditer(sentence))
        connector_matches = list(self._connector_pattern.finditer(sentence))
        outcome_matches = list(self._outcome_pattern.finditer(sentence))
        
        if not verb_matches:
            return chains
        
        for verb_match in verb_matches:
            verb = verb_match.group(0).lower()
            
            # Look for connectors after the verb
            relevant_connectors = [
                m for m in connector_matches 
                if m.start() > verb_match.end()
            ]
            
            if relevant_connectors:
                connector = relevant_connectors[0].group(0)
                
                # Look for outcomes after connector
                relevant_outcomes = [
                    m for m in outcome_matches
                    if m.start() > relevant_connectors[0].end()
                ]
                
                outcome = relevant_outcomes[0].group(0) if relevant_outcomes else None
                
                chain = {
                    "verb": verb,
                    "connector": connector,
                    "outcome": outcome,
                    "structure": "VERB-CONNECTOR-OUTCOME" if outcome else "VERB-CONNECTOR",
                    "confidence": self._calculate_chain_confidence(verb, connector, outcome)
                }
                chains.append(chain)
            
            else:
                # Verb without explicit connector - still valuable
                chain = {
                    "verb": verb,
                    "connector": None,
                    "outcome": None,
                    "structure": "VERB_ONLY",
                    "confidence": 0.5
                }
                chains.append(chain)
        
        return chains
    
    def _calculate_chain_confidence(
        self, 
        verb: str, 
        connector: Optional[str], 
        outcome: Optional[str]
    ) -> float:
        """Calculate confidence for a causal chain."""
        base = 0.6
        
        # Full chain bonus
        if verb and connector and outcome:
            base = 0.85
        elif verb and connector:
            base = 0.75
        
        # High-value verb bonus
        high_value_verbs = {"garantizar", "implementar", "establecer", "fortalecer"}
        if verb.lower() in high_value_verbs:
            base += 0.1
        
        # Strong connector bonus
        strong_connectors = {"mediante", "a través de", "con el fin de"}
        if connector and connector.lower() in strong_connectors:
            base += 0.05
        
        return min(base, 1.0)
    
    def _categorize_verb(self, verb: str) -> str:
        """Categorize the causal verb."""
        verb_lower = verb.lower()
        
        transformative = {"garantizar", "fortalecer", "implementar", "promover", "mejorar", 
                         "facilitar", "generar", "desarrollar", "impulsar", "transformar"}
        supportive = {"contribuir", "apoyar", "fomentar", "consolidar", "potenciar"}
        corrective = {"reducir", "eliminar", "prevenir", "mitigar", "superar"}
        structural = {"establecer", "crear", "diseñar", "formular", "articular"}
        monitoring = {"verificar", "evaluar", "monitorear", "seguir", "supervisar"}
        
        if verb_lower in transformative:
            return "TRANSFORMATIVE"
        elif verb_lower in supportive:
            return "SUPPORTIVE"
        elif verb_lower in corrective:
            return "CORRECTIVE"
        elif verb_lower in structural:
            return "STRUCTURAL"
        elif verb_lower in monitoring:
            return "MONITORING"
        else:
            return "OTHER"
    
    def _determine_slot(self, chain: Dict[str, Any]) -> str:
        """Determine question slot based on chain characteristics."""
        verb_category = chain.get("verb_category", self._categorize_verb(chain["verb"]))
        
        if verb_category == "TRANSFORMATIVE":
            return "D6-Q1"  # Main causal mechanism
        elif verb_category == "CORRECTIVE":
            return "D6-Q2"  # Problem-solution link
        elif verb_category == "STRUCTURAL":
            return "D6-Q3"  # Institutional arrangement
        elif verb_category == "MONITORING":
            return "D6-Q4"  # Evaluation mechanism
        elif verb_category == "SUPPORTIVE":
            return "D6-Q5"  # Supporting factors
        
        return self.DEFAULT_SLOT
