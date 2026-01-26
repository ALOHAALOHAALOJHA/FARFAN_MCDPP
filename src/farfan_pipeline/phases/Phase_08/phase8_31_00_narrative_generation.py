# phase8_31_00_narrative_generation.py - Narrative Prose Generation with Lenguaje Claro
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation
Purpose: Generate clear, actionable prose recommendations using Carver principles
Owner: phase8_enhanced
Stage: 31 (Narrative Generation)
Order: 00
Type: FRAMEWORK
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    ✍️ NARRATIVE GENERATION - Lenguaje Claro for PDM Recommendations ✍️
═══════════════════════════════════════════════════════════════════════════════════

THEORETICAL FOUNDATION:
    Carver principles for clear, accessible public policy writing:
    
    CARVER PRINCIPLES (Adapted from Raymond Carver's minimalist prose):
    1. ACTIVE VOICE: "La alcaldía construirá" NOT "Será construido por la alcaldía"
    2. CONCRETE NOUNS: "10 aulas" NOT "infraestructura educativa"
    3. SPECIFIC VERBS: "construir", "entregar", "capacitar" NOT "fortalecer", "garantizar"
    4. SHORT SENTENCES: Maximum 25 words per sentence
    5. FAMILIAR VOCABULARY: Avoid unnecessary jargon, define technical terms
    
    DNP LENGUAJE CLARO GUIDELINES:
    - Write for citizens, not bureaucrats
    - Specify WHO does WHAT, WHEN, WHERE, and HOW
    - Use data and concrete targets, not vague promises
    - Make verification mechanisms explicit
    - Connect to legal frameworks for legitimacy

NARRATIVE STRUCTURE (6 SECTIONS):
    1. DIAGNOSIS_CONTEXT: FARFAN findings that justify intervention
    2. INTERVENTION_DESCRIPTION: Instruments, activities, and products
    3. TIMELINE_SPECIFICATION: Month-by-month implementation schedule
    4. BUDGET_DETAILS: Sources, amounts, responsible entities
    5. VERIFICATION_MECHANISMS: Indicators, frequency, responsible parties
    6. SUSTAINABILITY_APPROACH: Long-term maintenance and institutionalization

EXAMPLE PROSE PATTERN:
    "El diagnóstico FARFAN reveló que [EVIDENCE]. Esta grave carencia demanda que 
    la [RESPONSIBLE ENTITY], en alianza estratégica con [PARTNER], [ACTION] para 
    garantizar que [TARGET] accedan a [SERVICE] durante el período [TIMELINE]. 
    
    La intervención comprende [INSTRUMENTS]: [ACTIVITY 1], [ACTIVITY 2], y [ACTIVITY 3].
    Cada actividad generará [PRODUCT] medido mediante [INDICATOR].
    
    La ejecución iniciará en [MONTH] y finalizará en [MONTH], con hitos trimestrales...
    
    El financiamiento provendrá de [SOURCE 1] ($X millones) y [SOURCE 2] ($Y millones),
    bajo responsabilidad de [ENTITY].
    
    El seguimiento se realizará mediante [INDICATOR] con frecuencia [FREQUENCY],
    reportado a [VERIFICATION ENTITY]."

KEY FEATURES:
    1. Carver principle validation (active voice, concrete nouns, etc.)
    2. Bullet-to-prose conversion with natural flow
    3. Responsible entity specification by municipality category
    4. Legal framework integration for legitimacy
    5. Compliance scoring (0-100)
    6. Sectioned output for PDM document structure

INTEGRATION:
    - Uses value chain structures from phase8_29
    - Uses legal frameworks from phase8_30
    - Uses instrument selection from phase8_28
    - Uses capacity profiles from phase8_27
    - Generates final recommendations for PDM drafting

Author: F.A.R.F.A.N Architecture Team
Python: 3.10+
═══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 31
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "NARRATIVE-GENERATION"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

# Conditional imports for type checking (avoids circular imports)
if TYPE_CHECKING:
    from .phase8_27_00_policy_capacity_framework import ComprehensiveCapacityProfile
    from .phase8_28_00_howlett_instruments import InstrumentMix
    from .phase8_29_00_value_chain_integration import ValueChainStructure
    from .phase8_30_00_colombian_legal_framework import (
        ColombianLegalFrameworkEngine,
        MunicipalCategory,
    )

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "CarverPrinciples",
    "CarverViolation",
    "NarrativeTemplate",
    "ProseRecommendation",
    "NarrativeGenerator",
    "convert_bullets_to_prose",
]

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class CarverViolation:
    """
    A violation of Carver principles in prose text.
    
    Used for quality control and iterative refinement.
    """
    principle: str  # Which principle violated (e.g., "ACTIVE_VOICE")
    line_number: int  # Line number in text (1-indexed)
    sentence: str  # The problematic sentence
    explanation: str  # Why this violates the principle
    suggested_fix: str  # How to fix it
    severity: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class NarrativeTemplate:
    """
    Template structure for narrative recommendations.
    
    Six mandatory sections following DNP PDM structure.
    """
    # Section 1: Diagnostic context
    diagnosis_context: str  # FARFAN findings justifying intervention
    
    # Section 2: Intervention description
    intervention_description: str  # Instruments, activities, products
    
    # Section 3: Timeline specification
    timeline_specification: str  # Month-by-month implementation schedule
    
    # Section 4: Budget details
    budget_details: str  # Sources, amounts, responsible entities
    
    # Section 5: Verification mechanisms
    verification_mechanisms: str  # Indicators, frequency, responsible parties
    
    # Section 6: Sustainability approach
    sustainability_approach: str  # Long-term maintenance, institutionalization
    
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProseRecommendation:
    """
    Complete prose recommendation with quality metrics.
    
    Output of narrative generation process.
    """
    recommendation_id: str  # e.g., "PA01-DIM01-CRISIS"
    policy_area: str  # e.g., "PA01"
    dimension: str  # e.g., "DIM01"
    municipality_category: Any  # MunicipalCategory (avoid import at module level)
    
    # Full narrative text
    full_text: str  # Complete prose recommendation (all sections)
    
    # Sectioned text (for PDM document structure)
    sections: dict[str, str]  # Section name → section text
    
    # Quality metrics
    word_count: int
    sentence_count: int
    average_sentence_length: float  # Words per sentence
    carver_compliance_score: float  # 0-100
    carver_violations: list[CarverViolation]
    
    # Traceability
    value_chain_id: str  # Links to ValueChainStructure
    legal_frameworks_cited: list[str]  # Laws cited (e.g., ["Ley 1257/2008"])
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# CARVER PRINCIPLES VALIDATOR
# =============================================================================


class CarverPrinciples:
    """
    Validator for Carver principles of clear writing.
    
    Checks text against 5 core principles:
    1. Active voice
    2. Sentence length (<25 words)
    3. Concrete nouns
    4. Specific verbs (not vague)
    5. Familiar vocabulary (no unnecessary jargon)
    """
    
    # Passive voice markers in Spanish
    PASSIVE_VOICE_MARKERS = [
        r"\bserá\s+\w+ado\b",  # será construido
        r"\bserá\s+\w+ido\b",  # será garantizado
        r"\bfueron?\s+\w+ados?\b",  # fue/fueron ejecutados
        r"\bfueron?\s+\w+idos?\b",  # fue/fueron construidos
        r"\bhan\s+sido\s+\w+ados?\b",  # han sido implementados
        r"\bhan\s+sido\s+\w+idos?\b",  # han sido construidos
        r"\bse\s+(realizará|ejecutará|implementará)\b",  # se realizará (impersonal)
    ]
    
    # Vague verbs to avoid (fortalecer, garantizar, etc.)
    VAGUE_VERBS = [
        "fortalecer", "fortalecerá", "fortalecimiento",
        "garantizar", "garantizará", "garantía",
        "asegurar", "asegurará", "aseguramiento",
        "promover", "promoverá", "promoción",
        "impulsar", "impulsará", "impulso",
        "fomentar", "fomentará", "fomento",
        "mejorar", "mejorará", "mejoramiento",  # Too vague without specifics
        "optimizar", "optimizará", "optimización",  # Too vague
    ]
    
    # Abstract nouns to flag (prefer concrete alternatives)
    ABSTRACT_NOUNS = [
        "gobernanza", "empoderamiento", "articulación", "fortalecimiento",
        "transversalización", "institucionalidad", "sostenibilidad"
    ]
    
    # Jargon to flag (define or replace with plain language)
    UNNECESSARY_JARGON = [
        "sinergia", "holístico", "integral", "transversal", "sistémico",
        "paradigma", "estratégico", "estructural", "coyuntural"
    ]
    
    @staticmethod
    def check_active_voice(text: str) -> list[CarverViolation]:
        """
        Identify passive voice constructions.
        
        Args:
            text: Text to check
            
        Returns:
            List of violations found
        """
        violations = []
        sentences = text.split(". ")
        
        for i, sentence in enumerate(sentences, start=1):
            for pattern in CarverPrinciples.PASSIVE_VOICE_MARKERS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    violations.append(CarverViolation(
                        principle="ACTIVE_VOICE",
                        line_number=i,
                        sentence=sentence.strip(),
                        explanation="Passive voice detected (e.g., 'será construido'). Use active voice.",
                        suggested_fix="Identify the actor and use active construction (e.g., 'La alcaldía construirá')",
                        severity="HIGH",
                    ))
                    break  # Only report one violation per sentence
        
        return violations
    
    @staticmethod
    def check_sentence_length(text: str, max_words: int = 25) -> list[CarverViolation]:
        """
        Flag sentences exceeding maximum word count.
        
        Args:
            text: Text to check
            max_words: Maximum words per sentence (default: 25)
            
        Returns:
            List of violations found
        """
        violations = []
        sentences = text.split(". ")
        
        for i, sentence in enumerate(sentences, start=1):
            word_count = len(sentence.split())
            if word_count > max_words:
                violations.append(CarverViolation(
                    principle="SENTENCE_LENGTH",
                    line_number=i,
                    sentence=sentence.strip(),
                    explanation=f"Sentence has {word_count} words (max: {max_words})",
                    suggested_fix="Break into shorter sentences or remove unnecessary clauses",
                    severity="MEDIUM" if word_count < 35 else "HIGH",
                ))
        
        return violations
    
    @staticmethod
    def check_concrete_nouns(text: str) -> list[CarverViolation]:
        """
        Identify abstract nouns that should be replaced with concrete alternatives.
        
        Args:
            text: Text to check
            
        Returns:
            List of violations found
        """
        violations = []
        sentences = text.split(". ")
        
        for i, sentence in enumerate(sentences, start=1):
            for abstract_noun in CarverPrinciples.ABSTRACT_NOUNS:
                if re.search(rf"\b{abstract_noun}\b", sentence, re.IGNORECASE):
                    violations.append(CarverViolation(
                        principle="CONCRETE_NOUNS",
                        line_number=i,
                        sentence=sentence.strip(),
                        explanation=f"Abstract noun '{abstract_noun}' found. Use concrete alternatives.",
                        suggested_fix=f"Replace '{abstract_noun}' with specific, measurable elements (e.g., '10 aulas' instead of 'infraestructura')",
                        severity="MEDIUM",
                    ))
                    break  # Only report first abstract noun per sentence
        
        return violations
    
    @staticmethod
    def check_specific_verbs(text: str) -> list[CarverViolation]:
        """
        Identify vague verbs that should be replaced with specific actions.
        
        Args:
            text: Text to check
            
        Returns:
            List of violations found
        """
        violations = []
        sentences = text.split(". ")
        
        for i, sentence in enumerate(sentences, start=1):
            for vague_verb in CarverPrinciples.VAGUE_VERBS:
                if re.search(rf"\b{vague_verb}\b", sentence, re.IGNORECASE):
                    violations.append(CarverViolation(
                        principle="SPECIFIC_VERBS",
                        line_number=i,
                        sentence=sentence.strip(),
                        explanation=f"Vague verb '{vague_verb}' found. Use specific action verbs.",
                        suggested_fix=f"Replace '{vague_verb}' with concrete action (e.g., 'construir', 'capacitar', 'entregar')",
                        severity="HIGH",
                    ))
                    break  # Only report first vague verb per sentence
        
        return violations
    
    @staticmethod
    def check_familiar_vocabulary(text: str) -> list[CarverViolation]:
        """
        Flag unnecessary jargon that should be defined or replaced.
        
        Args:
            text: Text to check
            
        Returns:
            List of violations found
        """
        violations = []
        sentences = text.split(". ")
        
        for i, sentence in enumerate(sentences, start=1):
            for jargon in CarverPrinciples.UNNECESSARY_JARGON:
                if re.search(rf"\b{jargon}\b", sentence, re.IGNORECASE):
                    violations.append(CarverViolation(
                        principle="FAMILIAR_VOCABULARY",
                        line_number=i,
                        sentence=sentence.strip(),
                        explanation=f"Jargon '{jargon}' found. Define or use plain language.",
                        suggested_fix=f"Replace '{jargon}' with plain language or provide definition",
                        severity="LOW",
                    ))
                    break  # Only report first jargon per sentence
        
        return violations
    
    @staticmethod
    def validate_all(text: str) -> tuple[float, list[CarverViolation]]:
        """
        Run all Carver principle checks and compute compliance score.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (compliance_score, violations_list)
            - compliance_score: 0-100 (100 = perfect compliance)
            - violations_list: All violations found
        """
        all_violations = []
        
        # Run all checks
        all_violations.extend(CarverPrinciples.check_active_voice(text))
        all_violations.extend(CarverPrinciples.check_sentence_length(text))
        all_violations.extend(CarverPrinciples.check_concrete_nouns(text))
        all_violations.extend(CarverPrinciples.check_specific_verbs(text))
        all_violations.extend(CarverPrinciples.check_familiar_vocabulary(text))
        
        # Compute score
        sentence_count = len(text.split(". "))
        if sentence_count == 0:
            return 0.0, all_violations
        
        # Weight violations by severity
        penalty = sum(
            10 if v.severity == "HIGH" else 5 if v.severity == "MEDIUM" else 2
            for v in all_violations
        )
        
        # Score formula: start at 100, subtract penalties, normalize by sentence count
        raw_score = 100 - (penalty / sentence_count)
        compliance_score = max(0.0, min(100.0, raw_score))
        
        return compliance_score, all_violations


# =============================================================================
# NARRATIVE GENERATOR
# =============================================================================


class NarrativeGenerator:
    """
    Generate clear, actionable prose recommendations using Carver principles.
    
    Converts structured data (value chains, instruments, capacities) into
    flowing narrative prose suitable for PDM documents.
    """
    
    def __init__(self, legal_engine: "ColombianLegalFrameworkEngine | None" = None):
        """
        Initialize narrative generator.
        
        Args:
            legal_engine: Legal framework engine (creates one if None)
        """
        if legal_engine is None:
            # Lazy import to avoid circular dependencies - use absolute import
            try:
                from .phase8_30_00_colombian_legal_framework import ColombianLegalFrameworkEngine
            except ImportError:
                # Fallback to absolute import if relative fails
                from phase8_30_00_colombian_legal_framework import ColombianLegalFrameworkEngine
            self.legal_engine = ColombianLegalFrameworkEngine()
        else:
            self.legal_engine = legal_engine
        logger.info("NarrativeGenerator initialized")
    
    def generate_prose_recommendation(
        self,
        value_chain: "ValueChainStructure",
        instruments: "InstrumentMix",
        capacity_profile: "ComprehensiveCapacityProfile",
    ) -> ProseRecommendation:
        """
        Generate complete prose recommendation from structured inputs.
        
        Args:
            value_chain: Value chain structure with objectives and products
            instruments: Selected policy instruments
            capacity_profile: Municipal capacity assessment
            
        Returns:
            ProseRecommendation with full narrative text and quality metrics
        """
        logger.info(
            f"Generating prose recommendation for {value_chain.policy_area}, "
            f"dimension {value_chain.dimension}"
        )
        
        # Generate each section
        diagnosis = self._generate_diagnosis_section(value_chain)
        intervention = self._generate_intervention_section(value_chain, instruments)
        timeline = self._generate_timeline_section(value_chain, instruments)
        budget = self._generate_budget_section(
            value_chain, capacity_profile.municipality_category
        )
        verification = self._generate_verification_section(value_chain)
        sustainability = self._generate_sustainability_section(
            value_chain, capacity_profile
        )
        
        # Create narrative template
        template = NarrativeTemplate(
            diagnosis_context=diagnosis,
            intervention_description=intervention,
            timeline_specification=timeline,
            budget_details=budget,
            verification_mechanisms=verification,
            sustainability_approach=sustainability,
        )
        
        # Combine sections into full text
        full_text = self._combine_sections(template)
        
        # Apply Carver principles refinement
        refined_text = self.apply_carver_principles(full_text)
        
        # Calculate metrics
        word_count = len(refined_text.split())
        sentences = [s for s in refined_text.split(". ") if s.strip()]
        sentence_count = len(sentences)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Validate Carver compliance
        carver_score, violations = CarverPrinciples.validate_all(refined_text)
        
        # Get legal frameworks cited
        legal_frameworks = self.legal_engine.get_legal_obligations(value_chain.policy_area)
        legal_citations = [
            f"Ley {law.law_number}/{law.law_year}"
            for law in legal_frameworks
        ]
        
        # Create ProseRecommendation
        recommendation = ProseRecommendation(
            recommendation_id=f"{value_chain.policy_area}-{value_chain.dimension}",
            policy_area=value_chain.policy_area,
            dimension=value_chain.dimension,
            municipality_category=capacity_profile.municipality_category,
            full_text=refined_text,
            sections={
                "diagnosis": diagnosis,
                "intervention": intervention,
                "timeline": timeline,
                "budget": budget,
                "verification": verification,
                "sustainability": sustainability,
            },
            word_count=word_count,
            sentence_count=sentence_count,
            average_sentence_length=avg_sentence_length,
            carver_compliance_score=carver_score,
            carver_violations=violations,
            value_chain_id=f"{value_chain.municipality_id}-{value_chain.policy_area}-{value_chain.dimension}",
            legal_frameworks_cited=legal_citations,
        )
        
        logger.info(
            f"Prose recommendation generated: {word_count} words, "
            f"Carver score={carver_score:.1f}"
        )
        
        return recommendation
    
    def _generate_diagnosis_section(self, value_chain: ValueChainStructure) -> str:
        """Generate diagnosis context section from problem tree."""
        problem = value_chain.problem_tree.central_problem
        evidence = value_chain.problem_tree.evidence
        
        # Convert evidence list to prose
        evidence_prose = self.convert_bullets_to_prose(evidence)
        
        diagnosis = (
            f"El diagnóstico FARFAN reveló que {problem.lower()}. "
            f"{evidence_prose} "
            f"Esta situación crítica demanda intervención inmediata para revertir "
            f"las causas estructurales identificadas."
        )
        
        return diagnosis
    
    def _generate_intervention_section(
        self, value_chain: ValueChainStructure, instruments: InstrumentMix
    ) -> str:
        """Generate intervention description section."""
        objetivo_general = value_chain.objetivo_general.text
        
        # List instruments in prose
        instrument_names = [inst.name for inst in instruments.instruments[:3]]  # Top 3
        if len(instrument_names) == 1:
            instruments_prose = instrument_names[0]
        elif len(instrument_names) == 2:
            instruments_prose = f"{instrument_names[0]} y {instrument_names[1]}"
        else:
            instruments_prose = (
                f"{', '.join(instrument_names[:-1])}, y {instrument_names[-1]}"
            )
        
        # List products
        products = [p.name for p in value_chain.productos[:2]]  # First 2 products
        if len(products) == 1:
            products_prose = products[0]
        else:
            products_prose = f"{products[0]} y {products[1]}"
        
        intervention = (
            f"Para abordar este desafío, el municipio {objetivo_general.lower()}. "
            f"La intervención se ejecutará mediante {instruments_prose}, "
            f"generando {products_prose} como productos principales. "
            f"Cada producto se diseñará siguiendo estándares técnicos "
            f"y normativas sectoriales aplicables."
        )
        
        return intervention
    
    def _generate_timeline_section(
        self, value_chain: ValueChainStructure, instruments: InstrumentMix
    ) -> str:
        """Generate timeline specification section."""
        # Determine complexity-based duration
        num_activities = len(value_chain.actividades)
        if num_activities <= 3:
            duration = "6 meses"
            phases = "dos fases trimestrales"
        elif num_activities <= 6:
            duration = "12 meses"
            phases = "cuatro fases trimestrales"
        else:
            duration = "18 meses"
            phases = "seis fases trimestrales"
        
        timeline = (
            f"La ejecución se desarrollará en {phases} durante un período de {duration}. "
            f"La fase inicial (meses 1-3) contempla diseño detallado, contratación y adquisiciones. "
            f"Las fases intermedias se enfocan en implementación de actividades y entrega de productos. "
            f"La fase final incluye evaluación, sistematización de lecciones aprendidas y "
            f"transferencia a actores locales para sostenibilidad."
        )
        
        return timeline
    
    def _generate_budget_section(
        self, value_chain: ValueChainStructure, category: MunicipalCategory
    ) -> str:
        """Generate budget details section."""
        # Get financing sources
        financing_sources = self.legal_engine.get_financing_sources(
            instrument_type="GENERAL",
            municipality_category=category,
            policy_area=value_chain.policy_area,
        )
        
        # Convert to prose
        if len(financing_sources) == 1:
            sources_prose = financing_sources[0].value.replace("_", " ").lower()
        elif len(financing_sources) == 2:
            sources_prose = (
                f"{financing_sources[0].value.replace('_', ' ').lower()} "
                f"y {financing_sources[1].value.replace('_', ' ').lower()}"
            )
        else:
            sources_list = [s.value.replace("_", " ").lower() for s in financing_sources[:3]]
            sources_prose = f"{', '.join(sources_list[:-1])}, y {sources_list[-1]}"
        
        # Specify responsible office
        responsible = self.specify_responsible_entities("budget", category)
        
        budget = (
            f"El financiamiento provendrá de {sources_prose}, "
            f"bajo la responsabilidad de {responsible}. "
            f"El presupuesto se ejecutará mediante el Sistema General de Regalías "
            f"y el Plan Operativo Anual de Inversiones (POAI), "
            f"garantizando transparencia y trazabilidad de recursos. "
            f"Se establecerán controles fiduciarios y técnicos en cada fase."
        )
        
        return budget
    
    def _generate_verification_section(self, value_chain: ValueChainStructure) -> str:
        """Generate verification mechanisms section."""
        # Use first product's indicator as example
        if value_chain.productos:
            indicator = value_chain.productos[0].indicator
        else:
            indicator = "indicadores de resultado definidos"
        
        verification = (
            f"El seguimiento se realizará mediante {indicator}, "
            f"con medición trimestral y reportes a la Secretaría de Planeación Municipal. "
            f"La verificación incluirá visitas de campo, revisión documental "
            f"y validación con beneficiarios directos. "
            f"Los resultados se reportarán al Sistema de Seguimiento al Plan de Desarrollo (SSPD) "
            f"y al Banco de Proyectos de Inversión Municipal."
        )
        
        return verification
    
    def _generate_sustainability_section(
        self, value_chain: ValueChainStructure, capacity_profile: ComprehensiveCapacityProfile
    ) -> str:
        """Generate sustainability approach section."""
        # Determine sustainability strategy based on capacity
        if capacity_profile.overall_capacity_level.value == "HIGH":
            strategy = "fortalecimiento institucional y transferencia de capacidades locales"
        elif capacity_profile.overall_capacity_level.value == "MEDIUM":
            strategy = "acompañamiento técnico continuado y alianzas estratégicas"
        else:
            strategy = "coordinación interinstitucional y cofinanciación departamental"
        
        sustainability = (
            f"La sostenibilidad de la intervención se garantiza mediante {strategy}. "
            f"Se establecerán mecanismos de operación y mantenimiento con presupuesto recurrente "
            f"en el Plan Plurianual de Inversiones. "
            f"Se formalizarán acuerdos interinstitucionales para continuidad más allá del período de gobierno. "
            f"La institucionalización incluye protocolos, manuales operativos y capacitación a funcionarios."
        )
        
        return sustainability
    
    def _combine_sections(self, template: NarrativeTemplate) -> str:
        """Combine all sections into flowing full text."""
        full_text = (
            f"{template.diagnosis_context}\n\n"
            f"{template.intervention_description}\n\n"
            f"{template.timeline_specification}\n\n"
            f"{template.budget_details}\n\n"
            f"{template.verification_mechanisms}\n\n"
            f"{template.sustainability_approach}"
        )
        return full_text
    
    def apply_carver_principles(self, text: str) -> str:
        """
        Apply Carver principles to refine text.
        
        Args:
            text: Original text
            
        Returns:
            Refined text with improved clarity
            
        Note:
            This is a first-pass automatic refinement.
            For production, manual review is recommended.
        """
        refined = text
        
        # Fix common passive voice patterns
        refined = re.sub(
            r"será\s+(\w+ado|ado)\s+por\s+la\s+(\w+)",
            r"la \2 \1rá",
            refined,
            flags=re.IGNORECASE
        )
        
        # Replace vague verbs with more specific ones (context-dependent)
        vague_to_specific = {
            "fortalecer": "capacitar",
            "garantizar": "entregar",
            "asegurar": "verificar",
            "promover": "implementar",
        }
        
        for vague, specific in vague_to_specific.items():
            # Only replace in certain contexts (conservative)
            refined = re.sub(
                rf"\b{vague} la capacidad\b",
                f"{specific} formación",
                refined,
                flags=re.IGNORECASE
            )
        
        return refined
    
    def convert_bullets_to_prose(self, bullet_list: list[str]) -> str:
        """
        Convert bullet point list to flowing prose paragraph.
        
        Args:
            bullet_list: List of bullet points
            
        Returns:
            Flowing prose paragraph
            
        Example:
            >>> bullets = ["Falta de agua", "Infraestructura deteriorada", "No hay personal"]
            >>> convert_bullets_to_prose(bullets)
            "Se identificó falta de agua, infraestructura deteriorada, y ausencia de personal."
        """
        if not bullet_list:
            return ""
        
        if len(bullet_list) == 1:
            return f"Se identificó {bullet_list[0].lower()}."
        
        # Clean bullets (remove leading markers like "- " or "• ")
        cleaned = [re.sub(r"^[-•*]\s*", "", item).strip() for item in bullet_list]
        
        # Convert to lowercase (except proper nouns - heuristic)
        cleaned = [
            item if item[0].isupper() and len(item.split()[0]) > 3 else item.lower()
            for item in cleaned
        ]
        
        # Join with commas and "y" before last item
        if len(cleaned) == 2:
            prose = f"Se identificó {cleaned[0]} y {cleaned[1]}."
        else:
            prose = f"Se identificó {', '.join(cleaned[:-1])}, y {cleaned[-1]}."
        
        return prose
    
    def specify_responsible_entities(
        self, activity: str, municipality_category: Any
    ) -> str:
        """
        Specify responsible entities based on activity and municipality size.
        
        Args:
            activity: Activity type (e.g., "budget", "implementation", "verification")
            municipality_category: Municipal category (MunicipalCategory enum)
            
        Returns:
            Specific office name (e.g., "Secretaría de Hacienda Municipal")
        """
        # Lazy import to avoid circular dependency - try both import methods
        try:
            from .phase8_30_00_colombian_legal_framework import MunicipalCategory
        except ImportError:
            from phase8_30_00_colombian_legal_framework import MunicipalCategory
        
        # Map activity to responsible entity
        if activity == "budget":
            if municipality_category in [MunicipalCategory.SPECIAL, MunicipalCategory.CATEGORY_1]:
                return "la Secretaría de Hacienda Municipal"
            else:
                return "la Tesorería Municipal"
        
        elif activity == "implementation":
            return "la Secretaría de Planeación Municipal"
        
        elif activity == "verification":
            if municipality_category in [MunicipalCategory.SPECIAL, MunicipalCategory.CATEGORY_1]:
                return "la Oficina de Control Interno"
            else:
                return "el Despacho del Alcalde"
        
        else:
            return "la autoridad municipal competente"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def convert_bullets_to_prose(bullet_list: list[str]) -> str:
    """
    Standalone helper to convert bullet list to prose.
    
    Args:
        bullet_list: List of bullet points
        
    Returns:
        Flowing prose paragraph
    """
    # Direct implementation without instantiating generator (avoid import issues)
    if not bullet_list:
        return ""
    
    if len(bullet_list) == 1:
        return f"Se identificó {bullet_list[0].lower()}."
    
    # Clean bullets (remove leading markers like "- " or "• ")
    import re
    cleaned = [re.sub(r"^[-•*]\s*", "", item).strip() for item in bullet_list]
    
    # Convert to lowercase (except proper nouns - heuristic)
    cleaned = [
        item if item[0].isupper() and len(item.split()[0]) > 3 else item.lower()
        for item in cleaned
    ]
    
    # Join with commas and "y" before last item
    if len(cleaned) == 2:
        prose = f"Se identificó {cleaned[0]} y {cleaned[1]}."
    else:
        prose = f"Se identificó {', '.join(cleaned[:-1])}, y {cleaned[-1]}."
    
    return prose


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    # Example usage
    from .phase8_27_00_policy_capacity_framework import (
        CapacityLevel,
        CapacityDimension,
        CapacityAssessment,
    )
    from .phase8_28_00_howlett_instruments import PolicyInstrument, InstrumentType
    from .phase8_29_00_value_chain_integration import (
        ProblemTree,
        ObjetivoGeneral,
        ObjetivoEspecifico,
        Producto,
        Actividad,
    )
    from .phase8_30_00_colombian_legal_framework import MunicipalCategory
    
    # Create mock data for demonstration
    print("=== NARRATIVE GENERATION DEMO ===\n")
    
    # Example 1: Carver validation
    bad_text = (
        "Se fortalecerá la gobernanza mediante la implementación de una estrategia "
        "holística que será ejecutada por la alcaldía para garantizar la sostenibilidad "
        "del proceso de empoderamiento comunitario."
    )
    
    print("1. Carver Validation Example:")
    print(f"Text: {bad_text}\n")
    
    score, violations = CarverPrinciples.validate_all(bad_text)
    print(f"Carver Score: {score:.1f}/100")
    print(f"Violations found: {len(violations)}\n")
    
    for v in violations[:3]:  # Show first 3
        print(f"  - {v.principle}: {v.explanation}")
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: Convert bullets to prose
    bullets = [
        "Falta de infraestructura educativa en zona rural",
        "Docentes sin capacitación en pedagogía actualizada",
        "Ausencia de material didáctico",
    ]
    
    print("2. Bullet-to-Prose Conversion:")
    print("Bullets:")
    for b in bullets:
        print(f"  • {b}")
    
    prose = convert_bullets_to_prose(bullets)
    print(f"\nProse: {prose}")
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Specify responsible entities
    generator = NarrativeGenerator()
    
    print("3. Responsible Entity Specification:")
    for category in [MunicipalCategory.SPECIAL, MunicipalCategory.CATEGORY_4]:
        responsible = generator.specify_responsible_entities("budget", category)
        print(f"  {category.value}: {responsible}")
