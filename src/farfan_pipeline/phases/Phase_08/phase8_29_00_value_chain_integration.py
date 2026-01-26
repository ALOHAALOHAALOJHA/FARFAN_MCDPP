# phase8_29_00_value_chain_integration.py - Colombian Value Chain Methodology
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_29_00_value_chain_integration
Purpose: Colombian Cadena de Valor methodology for PDM formulation
Owner: phase8_enhanced
Stage: 29 (Value Chain)
Order: 00
Type: FRAMEWORK
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    ⛓️ VALUE CHAIN INTEGRATION - Colombian Cadena de Valor ⛓️
═══════════════════════════════════════════════════════════════════════════════════

THEORETICAL FOUNDATION:
    Colombian Dirección de Inversiones y Finanzas Públicas value chain methodology
    for investment project quality improvement.
    
    VALUE CHAIN STRUCTURE:
    INSUMOS → ACTIVIDADES → PRODUCTOS → OBJETIVOS ESPECÍFICOS → 
    OBJETIVO GENERAL → RESULTADOS → IMPACTOS
    
    For FARFAN transformation (backwards flow):
    Diagnostic → Objetivo General → Objetivos Específicos → Productos → Actividades

OBJECTIVE FORMULATION RULES:
    
    Objetivo General Structure:
    [VERBO INFINITIVO] + [OBJETO] + [ELEMENTOS DESCRIPTIVOS]
    
    Common errors to AVOID:
    ✗ Including solution mechanisms ("mediante la construcción de...")
    ✗ Including effects/impacts ("para mejorar la calidad de vida")
    ✗ Describing partial actions ("adquirir equipos")
    ✗ Excessive breadth
    ✗ Including meta targets

PRODUCT SPECIFICATION RULES:
    
    Product Structure:
    [BIEN O SERVICIO] + [COMPLEMENTO]
    
    NEVER include condition words (elaborado, implementado, entregado)
    Condition appears in the indicator, not the product name.

KEY FEATURES:
    1. Problem tree construction (effects → problem → causes)
    2. Objective formulation (Objetivo General + Específicos)
    3. Product specification with quantifiable units
    4. Activity identification (value-adding transformations)
    5. Full value chain validation

INTEGRATION:
    - Uses problem identification from FARFAN diagnostics
    - Uses instrument selection from phase8_28
    - Feeds narrative generation (phase8_31)
    - Validates against DNP methodological guidelines

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
__stage__ = 29
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "VALUE-CHAIN"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .phase8_28_00_howlett_instruments import InstrumentMix, PolicyInstrument

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "ProblemTree",
    "ObjetivoGeneral",
    "ObjetivoEspecifico",
    "Producto",
    "Actividad",
    "ValueChainStructure",
    "ValueChainValidator",
    "build_value_chain_from_farfan",
]

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class ProblemTree:
    """Problem tree structure (árbol de problemas)"""
    central_problem: str  # Negative situation requiring intervention
    causes: list[str]  # Why the problem exists
    effects: list[str]  # Consequences of the problem
    evidence: list[str]  # FARFAN diagnostic evidence
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObjetivoGeneral:
    """General objective (objetivo general)"""
    text: str  # Complete objective statement
    verb: str  # Infinitive verb
    object: str  # What is being achieved
    descriptive_elements: list[str]  # Qualifying elements
    problem_addressed: str  # Original problem being solved
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObjetivoEspecifico:
    """Specific objective (objetivo específico)"""
    text: str  # Complete objective statement
    verb: str  # Strategic-level verb (not operational)
    cause_addressed: str  # Which cause this addresses
    measurability: str  # How this will be measured
    contribution_to_general: str  # How this contributes to general objective
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Producto:
    """Product/service (producto)"""
    name: str  # Good or service name (NO condition words)
    unit_of_measure: str  # Unidad de medida
    target: str  # Meta (quantitative target)
    specific_objective: str  # Which objective this product serves
    indicator: str  # How product will be verified
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Actividad:
    """Activity (actividad)"""
    description: str  # Value-adding action description
    action_verb: str  # Specific action verb
    product_generated: str  # Which product this activity generates
    resources_required: list[str]  # Key resources needed
    responsible: str  # Entity responsible
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValueChainStructure:
    """Complete value chain structure"""
    municipality_id: str
    policy_area: str
    dimension: str
    
    # Problem identification
    problem_tree: ProblemTree
    
    # Objectives
    objetivo_general: ObjetivoGeneral
    objetivos_especificos: list[ObjetivoEspecifico]
    
    # Products and activities
    productos: list[Producto]  # At least 1 per specific objective
    actividades: list[Actividad]  # At least 2 per product
    
    # Instrument mapping
    instrument_mapping: dict[str, InstrumentMix]  # Obj. Específico -> Instrument
    
    # Validation
    is_valid: bool
    validation_report: str
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# VALUE CHAIN VALIDATOR
# =============================================================================


class ValueChainValidator:
    """
    Validates value chain structures against DNP methodology.
    """
    
    # Forbidden verbs in Objetivo General (too operational or vague)
    FORBIDDEN_GENERAL_VERBS = [
        "adquirir", "contratar", "instalar", "comprar",  # Too operational
        "fortalecer", "garantizar", "asegurar", "promover"  # Too vague
    ]
    
    # Forbidden verbs in Objetivos Específicos (too operational)
    FORBIDDEN_SPECIFIC_VERBS = [
        "contratar", "instalar", "adquirir", "comprar"
    ]
    
    # Condition words forbidden in product names
    FORBIDDEN_PRODUCT_CONDITIONS = [
        "elaborado", "implementado", "entregado", "construido",
        "realizado", "ejecutado", "completado"
    ]
    
    # Required activity verbs (specific action verbs, not generic)
    GENERIC_ACTIVITY_VERBS = [
        "fortalecer", "garantizar", "implementar", "asegurar"
    ]
    
    @staticmethod
    def validate_objetivo_general(objetivo: ObjetivoGeneral) -> list[str]:
        """Validate Objetivo General against DNP rules"""
        errors = []
        
        # Check structure: must have verb + object
        if not objetivo.verb or not objetivo.object:
            errors.append("Objetivo General must have identifiable verb and object")
        
        # Check for forbidden verbs
        if objetivo.verb.lower() in ValueChainValidator.FORBIDDEN_GENERAL_VERBS:
            errors.append(
                f"Verb '{objetivo.verb}' is forbidden in Objetivo General "
                "(too operational or vague)"
            )
        
        # Check for solution mechanisms (mediante, a través de, por medio de)
        solution_patterns = [r"mediante", r"a través de", r"por medio de"]
        for pattern in solution_patterns:
            if re.search(pattern, objetivo.text, re.IGNORECASE):
                errors.append(
                    "Objetivo General should not include solution mechanisms "
                    f"(found '{pattern}')"
                )
        
        # Check for effects/impacts (para mejorar, con el fin de)
        effect_patterns = [r"para mejorar", r"con el fin de"]
        for pattern in effect_patterns:
            if re.search(pattern, objetivo.text, re.IGNORECASE):
                errors.append(
                    "Objetivo General should not include effects/impacts "
                    f"(found '{pattern}')"
                )
        
        # Check for meta/targets (numbers with %)
        if re.search(r"\d+%", objetivo.text):
            errors.append(
                "Objetivo General should not include percentage targets"
            )
        
        return errors
    
    @staticmethod
    def validate_objetivo_especifico(
        objetivo: ObjetivoEspecifico,
        objetivo_general: ObjetivoGeneral
    ) -> list[str]:
        """Validate Objetivo Específico against DNP rules"""
        errors = []
        
        # Check for forbidden verbs
        if objetivo.verb.lower() in ValueChainValidator.FORBIDDEN_SPECIFIC_VERBS:
            errors.append(
                f"Verb '{objetivo.verb}' is forbidden in Objetivo Específico "
                "(too operational)"
            )
        
        # Check measurability
        if not objetivo.measurability:
            errors.append(
                "Objetivo Específico must be measurable/quantifiable through products"
            )
        
        # Check contribution to general objective
        if not objetivo.contribution_to_general:
            errors.append(
                "Objetivo Específico must explain contribution to Objetivo General"
            )
        
        return errors
    
    @staticmethod
    def validate_producto(producto: Producto) -> list[str]:
        """Validate Producto against DNP rules"""
        errors = []
        
        # Check for condition words in product name
        for condition in ValueChainValidator.FORBIDDEN_PRODUCT_CONDITIONS:
            if condition in producto.name.lower():
                errors.append(
                    f"Product name should not include condition word '{condition}' "
                    "(condition belongs in indicator)"
                )
        
        # Check for coherent unit of measure
        if not producto.unit_of_measure:
            errors.append("Product must have coherent, quantifiable unit of measure")
        
        # Check for quantitative target
        if not producto.target:
            errors.append("Product must have specified target (meta)")
        
        # Check that product is actually a good/service, not a beneficiary
        beneficiary_words = ["desplazados", "mujeres", "niños", "familias"]
        if any(word in producto.name.lower() for word in beneficiary_words):
            if not any(service in producto.name.lower() 
                      for service in ["servicio", "programa", "atención"]):
                errors.append(
                    "Product name appears to be beneficiary, not good/service "
                    "(e.g., 'desplazados' instead of 'servicio de atención a desplazados')"
                )
        
        return errors
    
    @staticmethod
    def validate_actividad(actividad: Actividad, producto: Producto) -> list[str]:
        """Validate Actividad against DNP rules"""
        errors = []
        
        # Check for generic activity verbs
        if any(verb in actividad.action_verb.lower() 
               for verb in ValueChainValidator.GENERIC_ACTIVITY_VERBS):
            errors.append(
                f"Activity should use specific action verb, not generic '{actividad.action_verb}'"
            )
        
        # Check that activity describes transformation, not input acquisition
        input_patterns = [r"adquirir", r"comprar", r"conseguir"]
        for pattern in input_patterns:
            if re.search(pattern, actividad.description, re.IGNORECASE):
                errors.append(
                    "Activity should describe value-adding transformation, "
                    f"not input acquisition (found '{pattern}')"
                )
        
        return errors
    
    @staticmethod
    def validate_product_activity_relationship(
        producto: Producto,
        actividades: list[Actividad]
    ) -> list[str]:
        """Validate product has at least 2 activities"""
        errors = []
        
        # Find activities for this product
        product_activities = [
            a for a in actividades 
            if a.product_generated == producto.name
        ]
        
        if len(product_activities) < 2:
            errors.append(
                f"Product '{producto.name}' must have at least 2 activities "
                f"(found {len(product_activities)}). If only one activity generates "
                "the product, it's likely misidentified as a product."
            )
        
        return errors
    
    @staticmethod
    def validate_full_chain(chain: ValueChainStructure) -> tuple[bool, str]:
        """Validate complete value chain structure"""
        all_errors = []
        
        # Validate Objetivo General
        general_errors = ValueChainValidator.validate_objetivo_general(
            chain.objetivo_general
        )
        if general_errors:
            all_errors.append(f"Objetivo General errors: {', '.join(general_errors)}")
        
        # Validate Objetivos Específicos
        for i, obj_esp in enumerate(chain.objetivos_especificos, 1):
            esp_errors = ValueChainValidator.validate_objetivo_especifico(
                obj_esp, chain.objetivo_general
            )
            if esp_errors:
                all_errors.append(
                    f"Objetivo Específico {i} errors: {', '.join(esp_errors)}"
                )
        
        # Check at least one product per specific objective
        for obj_esp in chain.objetivos_especificos:
            matching_products = [
                p for p in chain.productos 
                if p.specific_objective == obj_esp.text
            ]
            if not matching_products:
                all_errors.append(
                    f"Objetivo Específico '{obj_esp.text[:50]}...' has no products"
                )
        
        # Validate Productos
        for producto in chain.productos:
            prod_errors = ValueChainValidator.validate_producto(producto)
            if prod_errors:
                all_errors.append(
                    f"Product '{producto.name}' errors: {', '.join(prod_errors)}"
                )
            
            # Validate product-activity relationship
            rel_errors = ValueChainValidator.validate_product_activity_relationship(
                producto, chain.actividades
            )
            if rel_errors:
                all_errors.append(', '.join(rel_errors))
        
        # Validate Actividades
        for actividad in chain.actividades:
            matching_product = next(
                (p for p in chain.productos if p.name == actividad.product_generated),
                None
            )
            if matching_product:
                act_errors = ValueChainValidator.validate_actividad(
                    actividad, matching_product
                )
                if act_errors:
                    all_errors.append(
                        f"Activity '{actividad.description[:50]}...' errors: "
                        f"{', '.join(act_errors)}"
                    )
        
        # Generate report
        is_valid = len(all_errors) == 0
        if is_valid:
            report = "✓ Value chain structure is valid per DNP methodology"
        else:
            report = "✗ Value chain validation failed:\n" + "\n".join(
                f"  - {error}" for error in all_errors
            )
        
        return is_valid, report


# =============================================================================
# VALUE CHAIN BUILDER
# =============================================================================


def build_value_chain_from_farfan(
    municipality_id: str,
    policy_area: str,
    dimension: str,
    farfan_diagnostic: dict[str, Any],
    instrument_mixes: dict[str, InstrumentMix]
) -> ValueChainStructure:
    """
    Build complete value chain structure from FARFAN diagnostic.
    
    Args:
        municipality_id: Municipality identifier
        policy_area: Policy area (e.g., "Gender Equality")
        dimension: Dimension (e.g., "DIM01")
        farfan_diagnostic: FARFAN diagnostic data with scores and evidence
        instrument_mixes: Selected instrument mixes per objective
        
    Returns:
        ValueChainStructure object
    """
    # Step 1: Construct problem tree
    problem_tree = _construct_problem_tree(farfan_diagnostic, policy_area)
    
    # Step 2: Formulate Objetivo General (invert central problem)
    objetivo_general = _formulate_objetivo_general(problem_tree, policy_area)
    
    # Step 3: Formulate Objetivos Específicos (convert causes)
    objetivos_especificos = _formulate_objetivos_especificos(
        problem_tree, objetivo_general
    )
    
    # Step 4: Specify products from instrument mixes
    productos = _specify_productos(objetivos_especificos, instrument_mixes)
    
    # Step 5: Identify activities
    actividades = _identify_actividades(productos, instrument_mixes)
    
    # Step 6: Validate full chain
    chain = ValueChainStructure(
        municipality_id=municipality_id,
        policy_area=policy_area,
        dimension=dimension,
        problem_tree=problem_tree,
        objetivo_general=objetivo_general,
        objetivos_especificos=objetivos_especificos,
        productos=productos,
        actividades=actividades,
        instrument_mapping=instrument_mixes,
        is_valid=False,  # Will be set by validation
        validation_report="",
        metadata={
            "framework_version": __version__
        }
    )
    
    is_valid, report = ValueChainValidator.validate_full_chain(chain)
    chain.is_valid = is_valid
    chain.validation_report = report
    
    return chain


def _construct_problem_tree(
    farfan_diagnostic: dict[str, Any],
    policy_area: str
) -> ProblemTree:
    """Construct problem tree from FARFAN diagnostic data"""
    # Extract evidence from diagnostic
    evidence = farfan_diagnostic.get("evidence", [])
    
    # Construct central problem (simplified - should use NLP/templates)
    central_problem = farfan_diagnostic.get(
        "central_problem",
        f"[Policy area] population lacks access to [services/rights]"
    )
    
    # Identify causes (simplified - should analyze evidence)
    causes = farfan_diagnostic.get("causes", [
        "Insufficient awareness of rights and mechanisms",
        "Absence of specialized services",
        "No institutional structure for policy implementation",
        "Zero budget allocation"
    ])
    
    # Identify effects (simplified)
    effects = farfan_diagnostic.get("effects", [
        "Perpetuation of problematic conditions",
        "Lack of access to justice and reparation",
        "Increased vulnerability of affected population"
    ])
    
    return ProblemTree(
        central_problem=central_problem,
        causes=causes,
        effects=effects,
        evidence=evidence,
        metadata={"policy_area": policy_area}
    )


def _formulate_objetivo_general(
    problem_tree: ProblemTree,
    policy_area: str
) -> ObjetivoGeneral:
    """Formulate Objetivo General by inverting central problem"""
    # Simple inversion (should use templates and NLP)
    problem = problem_tree.central_problem.lower()
    
    # Extract key elements
    if "lack" in problem or "lacks" in problem:
        verb = "Garantizar"
        obj_match = re.search(r"lacks?\s+(?:access to\s+)?(.+)", problem)
        object_text = obj_match.group(1) if obj_match else "services"
    else:
        verb = "Mejorar"
        object_text = "condition"
    
    text = f"{verb} {object_text}"
    
    return ObjetivoGeneral(
        text=text,
        verb=verb,
        object=object_text,
        descriptive_elements=[],
        problem_addressed=problem_tree.central_problem,
        metadata={"policy_area": policy_area}
    )


def _formulate_objetivos_especificos(
    problem_tree: ProblemTree,
    objetivo_general: ObjetivoGeneral
) -> list[ObjetivoEspecifico]:
    """Formulate Objetivos Específicos by converting causes"""
    objetivos = []
    
    for i, cause in enumerate(problem_tree.causes, 1):
        # Convert negative cause to positive objective (simplified)
        if "insufficient" in cause.lower() or "lack" in cause.lower():
            verb = "Aumentar"
        elif "absence" in cause.lower() or "no " in cause.lower():
            verb = "Establecer"
        elif "zero" in cause.lower():
            verb = "Asignar"
        else:
            verb = "Mejorar"
        
        # Extract object from cause
        object_text = re.sub(
            r"(insufficient|absence of|lack of|no|zero)\s+",
            "",
            cause,
            flags=re.IGNORECASE
        )
        
        text = f"{verb} {object_text}"
        
        objetivos.append(ObjetivoEspecifico(
            text=text,
            verb=verb,
            cause_addressed=cause,
            measurability=f"Through products that quantify {object_text}",
            contribution_to_general=f"Addresses one cause of the problem in Objetivo General",
            metadata={"objective_number": i}
        ))
    
    return objetivos


def _specify_productos(
    objetivos_especificos: list[ObjetivoEspecifico],
    instrument_mixes: dict[str, InstrumentMix]
) -> list[Producto]:
    """Specify productos from instrument mixes and objectives"""
    productos = []
    
    for obj_esp in objetivos_especificos:
        # Get instrument mix for this objective
        instrument_mix = instrument_mixes.get(obj_esp.text)
        
        if instrument_mix:
            # Create product based on primary instrument
            primary = instrument_mix.primary_instrument
            
            # Generate product name (simplified - should use templates)
            if "training" in primary.description.lower():
                product_name = f"Programa de capacitación en {obj_esp.text[:30]}"
                unit = "Número de personas capacitadas"
                target = "100 personas"
            elif "campaign" in primary.description.lower():
                product_name = f"Campaña comunicacional sobre {obj_esp.text[:30]}"
                unit = "Número de campañas"
                target = "1 campaña"
            elif "subsidy" in primary.description.lower():
                product_name = f"Programa de subsidios para {obj_esp.text[:30]}"
                unit = "Número de beneficiarios"
                target = "50 familias"
            else:
                product_name = f"Servicio de {obj_esp.text[:30]}"
                unit = "Número de beneficiarios"
                target = "100 personas"
            
            productos.append(Producto(
                name=product_name,
                unit_of_measure=unit,
                target=target,
                specific_objective=obj_esp.text,
                indicator=f"{product_name} implementado y operativo",
                metadata={"instrument_type": primary.instrument_type.value}
            ))
    
    return productos


def _identify_actividades(
    productos: list[Producto],
    instrument_mixes: dict[str, InstrumentMix]
) -> list[Actividad]:
    """Identify activities that generate products"""
    actividades = []
    
    for producto in productos:
        # Generate at least 2 activities per product (simplified)
        # Activity 1: Design/Planning
        actividades.append(Actividad(
            description=f"Diseñar y planificar {producto.name}",
            action_verb="Diseñar",
            product_generated=producto.name,
            resources_required=["Personal técnico", "Presupuesto de diseño"],
            responsible="Secretaría de Planeación"
        ))
        
        # Activity 2: Implementation
        actividades.append(Actividad(
            description=f"Ejecutar {producto.name}",
            action_verb="Ejecutar",
            product_generated=producto.name,
            resources_required=["Presupuesto de ejecución", "Personal operativo"],
            responsible="Secretaría ejecutora"
        ))
        
        # Activity 3: Monitoring (optional)
        actividades.append(Actividad(
            description=f"Realizar seguimiento y monitoreo de {producto.name}",
            action_verb="Monitorear",
            product_generated=producto.name,
            resources_required=["Sistema de información", "Personal M&E"],
            responsible="Oficina de Control Interno"
        ))
    
    return actividades
