# phase8_30_00_colombian_legal_framework.py - Colombian Legal Framework Engine
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework
Purpose: Colombian legal framework for PDM formulation and compliance validation
Owner: phase8_enhanced
Stage: 30 (Legal Framework)
Order: 00
Type: FRAMEWORK
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    ⚖️ COLOMBIAN LEGAL FRAMEWORK - PDM Compliance Engine ⚖️
═══════════════════════════════════════════════════════════════════════════════════

THEORETICAL FOUNDATION:
    Comprehensive legal framework for Colombian municipal development planning,
    integrating Law 1551/2012 (Modernización municipal), Law 152/1994 (PDM 
    formulation), and sectoral laws governing the 10 FARFAN policy areas.
    
    MUNICIPAL CATEGORIZATION (Law 617/2000, Law 1551/2012):
    - Special Category: >500,000 inhabitants, income >400,000 SMMLV
    - Category 1: 100,001-500,000 inhabitants, income 100,000-400,000 SMMLV
    - Category 2: 50,001-100,000 inhabitants, income 50,000-100,000 SMMLV
    - Category 3: 30,001-50,000 inhabitants, income 30,000-50,000 SMMLV
    - Category 4: 20,001-30,000 inhabitants, income 25,000-30,000 SMMLV
    - Category 5: 10,001-20,000 inhabitants, income 15,000-25,000 SMMLV
    - Category 6: <10,000 inhabitants, income <15,000 SMMLV
    
    SGP ALLOCATION (Law 715/2001):
    - Education: 58.5% (certificados: Special, 1, 2; no certificados: 3-6)
    - Health: 24.5% (regimen subsidiado, salud pública)
    - General Purpose: 11.6% (42% discretionary for categories 4-6)
    - Water & Sanitation: 5.4%
    
    PDM FORMULATION TIMELINE (Law 152/1994):
    - January-February: Diagnostic consolidation
    - March: Strategic part formulation (objetivo general, específicos)
    - April: Investment plan and budget (Cadena de Valor)
    - May: CTP approval and submission to Concejo Municipal

KEY FEATURES:
    1. Municipal category classification with competency mapping
    2. SGP sectoral allocation calculator
    3. Legal obligation mapping for 10 FARFAN policy areas
    4. PDM compliance validation
    5. Financing source identification by instrument and category
    6. Timeline requirements by formulation phase

INTEGRATION:
    - Uses capacity profiles from phase8_27
    - Uses instrument selection from phase8_28
    - Uses value chain structures from phase8_29
    - Feeds narrative generation (phase8_31)
    - Validates budget allocation against legal constraints

LEGAL FRAMEWORK COVERAGE:
    PA01 (Gender Equality) → Ley 1257/2008 (violencia contra la mujer)
    PA02 (Victims' Rights) → Ley 1448/2011 (víctimas del conflicto)
    PA03 (Environment) → Ley 99/1993, POT (medio ambiente)
    PA04 (Children/Youth) → Ley 1098/2006 Art. 204 (infancia y adolescencia)
    PA05 (Human Rights Defenders) → Decree 1066/2015 (defensores DDHH)
    PA06 (Economic Development) → Competencia municipal discrecional
    PA07 (Infrastructure/Mobility) → POT + competencia municipal
    PA08 (Education) → Ley 715/2001 (educación)
    PA09 (Health) → Ley 715/2001 (salud)
    PA10 (Institutional Capacity) → Ley 1474/2011 (transparencia)

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
__stage__ = 30
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "LEGAL-FRAMEWORK"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "MunicipalCategory",
    "SGPComponent",
    "FinancingSource",
    "LegalFramework",
    "PDMFormulationPhase",
    "PDMFormulationTimeline",
    "ComplianceReport",
    "ColombianLegalFrameworkEngine",
]

# =============================================================================
# ENUMERATIONS
# =============================================================================


class MunicipalCategory(str, Enum):
    """
    Municipal categorization per Law 617/2000 and Law 1551/2012.
    
    Determines:
    - Budget allocation rules (SGP discretionary percentages)
    - Planning requirements depth
    - Competency scope (e.g., education certification)
    - Administrative structure requirements
    """
    SPECIAL = "SPECIAL"  # >500k inhabitants, >400k SMMLV income
    CATEGORY_1 = "CATEGORY_1"  # 100-500k, 100-400k SMMLV
    CATEGORY_2 = "CATEGORY_2"  # 50-100k, 50-100k SMMLV
    CATEGORY_3 = "CATEGORY_3"  # 30-50k, 30-50k SMMLV
    CATEGORY_4 = "CATEGORY_4"  # 20-30k, 25-30k SMMLV
    CATEGORY_5 = "CATEGORY_5"  # 10-20k, 15-25k SMMLV
    CATEGORY_6 = "CATEGORY_6"  # <10k, <15k SMMLV


class SGPComponent(str, Enum):
    """
    Sistema General de Participaciones (SGP) components per Law 715/2001.
    
    Distribution:
    - EDUCATION: 58.5% (certificados only: Special, 1, 2)
    - HEALTH: 24.5% (all municipalities)
    - GENERAL_PURPOSE: 11.6% (42% discretionary for categories 4-6)
    - WATER: 5.4% (all municipalities)
    """
    EDUCATION = "EDUCATION"  # 58.5% - Certificados only
    HEALTH = "HEALTH"  # 24.5% - All municipalities
    GENERAL_PURPOSE = "GENERAL_PURPOSE"  # 11.6% - Includes discretionary
    WATER_SANITATION = "WATER_SANITATION"  # 5.4% - All municipalities


class FinancingSource(str, Enum):
    """
    Available financing sources for municipal PDM implementation.
    
    Availability varies by municipal category, instrument type, and sector.
    """
    SGP_EDUCATION = "SGP_EDUCATION"  # Only certificados
    SGP_HEALTH = "SGP_HEALTH"  # All municipalities
    SGP_GENERAL_PURPOSE = "SGP_GENERAL_PURPOSE"  # All (limited discretion)
    SGP_WATER = "SGP_WATER"  # All municipalities
    RECURSOS_PROPIOS = "RECURSOS_PROPIOS"  # Own resources (taxes, fees)
    REGALIAS = "REGALIAS"  # Royalties (OCAD approval required)
    CREDITO = "CREDITO"  # Credit (debt capacity limits apply)
    COFINANCIACION_NACIONAL = "COFINANCIACION_NACIONAL"  # National co-financing
    COFINANCIACION_DEPARTAMENTAL = "COFINANCIACION_DEPARTAMENTAL"  # Department co-financing
    COOPERACION_INTERNACIONAL = "COOPERACION_INTERNACIONAL"  # International cooperation


class PDMFormulationPhase(str, Enum):
    """
    PDM formulation phases per Law 152/1994 and Decree 1082/2015.
    
    Timeline: January-May (first 5 months of mayoral term)
    """
    DIAGNOSTIC = "DIAGNOSTIC"  # Jan-Feb: Problem identification, evidence collection
    STRATEGIC_PART = "STRATEGIC_PART"  # March: Objectives, lines, programs
    INVESTMENT_PLAN = "INVESTMENT_PLAN"  # April: Budget, Cadena de Valor, indicators
    CTP_APPROVAL = "CTP_APPROVAL"  # April-May: Consejo Territorial de Planeación review
    COUNCIL_APPROVAL = "COUNCIL_APPROVAL"  # May: Concejo Municipal approval (Acuerdo)


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class LegalFramework:
    """
    Legal framework requirement for a policy area.
    
    Maps specific laws to FARFAN policy areas and defines compliance requirements.
    """
    law_number: str  # e.g., "1257", "1448", "715"
    law_year: int  # e.g., 2008, 2011, 2001
    description: str  # Brief description of law's purpose
    applicable_municipalities: list[MunicipalCategory]  # Which categories must comply
    mandatory_pdm_section: str  # Required section in PDM (e.g., "Programa de Mujer y Género")
    verification_entity: str  # Entity that verifies compliance (e.g., "Consejería Presidencial")
    budget_earmark: float | None = None  # Mandatory budget % (None if not specified)
    coordination_required: list[str] = field(default_factory=list)  # Inter-institutional coordination
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PDMFormulationTimeline:
    """
    Month-by-month PDM formulation requirements.
    
    Based on Law 152/1994 mandatory timeline for new mayors.
    """
    phase: PDMFormulationPhase
    month: str  # "Enero", "Febrero", etc.
    start_date: date  # Typical start date (year-agnostic)
    end_date: date  # Typical end date
    key_activities: list[str]  # Required activities
    required_products: list[str]  # Deliverables expected
    responsible_entities: list[str]  # Who must participate
    legal_basis: str  # Legal citation
    critical_path: bool  # Is this a blocking phase?
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """
    PDM compliance validation report for a specific recommendation.
    
    Validates legal alignment, financing viability, and timeline feasibility.
    """
    recommendation_id: str
    policy_area: str
    municipality_category: MunicipalCategory
    
    # Legal compliance
    applicable_laws: list[LegalFramework]
    is_legally_compliant: bool
    legal_gaps: list[str]  # Missing legal requirements
    
    # Financing compliance
    required_financing_sources: list[FinancingSource]
    financing_viability: str  # "VIABLE", "CONSTRAINED", "INFEASIBLE"
    financing_gaps: list[str]  # Unavailable sources needed
    
    # Timeline compliance
    formulation_phase: PDMFormulationPhase
    is_timeline_feasible: bool
    timeline_risks: list[str]  # Potential delays
    
    # Overall compliance
    overall_compliance_score: float  # 0-1
    compliance_level: str  # "FULL", "PARTIAL", "NON_COMPLIANT"
    recommendations_for_compliance: list[str]  # How to achieve compliance
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# COLOMBIAN LEGAL FRAMEWORK ENGINE
# =============================================================================


class ColombianLegalFrameworkEngine:
    """
    Comprehensive Colombian legal framework engine for PDM formulation.
    
    Validates recommendations against:
    - Municipal categorization rules
    - SGP allocation constraints
    - Sectoral legal obligations
    - PDM formulation timeline
    - Financing source availability
    """
    
    # SGP allocation percentages by component
    SGP_ALLOCATIONS = {
        SGPComponent.EDUCATION: 0.585,  # 58.5%
        SGPComponent.HEALTH: 0.245,  # 24.5%
        SGPComponent.GENERAL_PURPOSE: 0.116,  # 11.6%
        SGPComponent.WATER_SANITATION: 0.054,  # 5.4%
    }
    
    # Discretionary percentage of General Purpose for categories 4-6
    GENERAL_PURPOSE_DISCRETIONARY = {
        MunicipalCategory.SPECIAL: 0.0,  # 0% discretionary (fully earmarked)
        MunicipalCategory.CATEGORY_1: 0.0,
        MunicipalCategory.CATEGORY_2: 0.0,
        MunicipalCategory.CATEGORY_3: 0.0,
        MunicipalCategory.CATEGORY_4: 0.42,  # 42% discretionary
        MunicipalCategory.CATEGORY_5: 0.42,
        MunicipalCategory.CATEGORY_6: 0.42,
    }
    
    # Municipal category thresholds
    CATEGORY_THRESHOLDS = {
        MunicipalCategory.SPECIAL: {"min_population": 500_001, "min_income_smmlv": 400_000},
        MunicipalCategory.CATEGORY_1: {"min_population": 100_001, "min_income_smmlv": 100_000},
        MunicipalCategory.CATEGORY_2: {"min_population": 50_001, "min_income_smmlv": 50_000},
        MunicipalCategory.CATEGORY_3: {"min_population": 30_001, "min_income_smmlv": 30_000},
        MunicipalCategory.CATEGORY_4: {"min_population": 20_001, "min_income_smmlv": 25_000},
        MunicipalCategory.CATEGORY_5: {"min_population": 10_001, "min_income_smmlv": 15_000},
        MunicipalCategory.CATEGORY_6: {"min_population": 0, "min_income_smmlv": 0},
    }
    
    # Legal frameworks by FARFAN policy area
    POLICY_AREA_LEGAL_FRAMEWORKS = {
        "PA01": [  # Gender Equality
            {
                "law_number": "1257",
                "law_year": 2008,
                "description": "Sensibilización, prevención y sanción de formas de violencia y discriminación contra las mujeres",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Equidad de Género y Prevención de Violencias",
                "verification_entity": "Consejería Presidencial para la Equidad de la Mujer",
                "coordination_required": ["Comisaría de Familia", "Personería Municipal"],
            }
        ],
        "PA02": [  # Victims' Rights
            {
                "law_number": "1448",
                "law_year": 2011,
                "description": "Atención, asistencia y reparación integral a las víctimas del conflicto armado interno",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Atención a Víctimas del Conflicto",
                "verification_entity": "Unidad para las Víctimas",
                "coordination_required": ["Personería Municipal", "Enlace de Víctimas"],
            }
        ],
        "PA03": [  # Environment
            {
                "law_number": "99",
                "law_year": 1993,
                "description": "Sistema Nacional Ambiental (SINA) y gestión ambiental municipal",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Eje Ambiental y Sostenibilidad",
                "verification_entity": "Corporación Autónoma Regional (CAR)",
                "coordination_required": ["CAR", "Secretaría de Planeación", "POT"],
            },
            {
                "law_number": "388",
                "law_year": 1997,
                "description": "Ordenamiento Territorial (POT, PBOT, EOT)",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Articulación PDM-POT",
                "verification_entity": "Secretaría de Planeación Municipal",
                "coordination_required": ["POT", "CAR", "Curaduría Urbana"],
            },
        ],
        "PA04": [  # Children and Youth
            {
                "law_number": "1098",
                "law_year": 2006,
                "description": "Código de Infancia y Adolescencia - Art. 204 (obligaciones municipales)",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Primera Infancia, Infancia y Adolescencia",
                "verification_entity": "Instituto Colombiano de Bienestar Familiar (ICBF)",
                "coordination_required": ["ICBF", "Comisaría de Familia", "Secretaría de Educación"],
            }
        ],
        "PA05": [  # Human Rights Defenders
            {
                "law_number": "1066",
                "law_year": 2015,
                "description": "Decreto Único Reglamentario - Programa de Protección a Defensores de DDHH",
                "applicable_municipalities": [MunicipalCategory.SPECIAL, MunicipalCategory.CATEGORY_1, MunicipalCategory.CATEGORY_2],
                "mandatory_pdm_section": "Programa de Protección a Líderes Sociales y Defensores DDHH",
                "verification_entity": "Unidad Nacional de Protección (UNP)",
                "coordination_required": ["UNP", "Personería Municipal", "Policía Nacional"],
            }
        ],
        "PA06": [  # Economic Development
            {
                "law_number": "1551",
                "law_year": 2012,
                "description": "Modernización municipal - Competencia en desarrollo económico local",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Eje de Desarrollo Económico Local",
                "verification_entity": "Autonomía municipal (no verificación externa obligatoria)",
                "coordination_required": ["Cámara de Comercio", "Gobernación (opcional)"],
            }
        ],
        "PA07": [  # Infrastructure and Mobility
            {
                "law_number": "1551",
                "law_year": 2012,
                "description": "Competencia municipal en infraestructura vial y servicios públicos",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Eje de Infraestructura y Movilidad",
                "verification_entity": "Autonomía municipal (articulación con POT obligatoria)",
                "coordination_required": ["POT", "Secretaría de Obras Públicas", "INVIAS (vías terciarias)"],
            },
            {
                "law_number": "388",
                "law_year": 1997,
                "description": "Articulación con POT para infraestructura urbana",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Articulación PDM-POT en Infraestructura",
                "verification_entity": "Secretaría de Planeación Municipal",
                "coordination_required": ["POT", "Curaduría Urbana"],
            },
        ],
        "PA08": [  # Education
            {
                "law_number": "715",
                "law_year": 2001,
                "description": "SGP Educación - Competencias certificados y no certificados",
                "applicable_municipalities": [MunicipalCategory.SPECIAL, MunicipalCategory.CATEGORY_1, MunicipalCategory.CATEGORY_2],  # Certificados
                "mandatory_pdm_section": "Programa de Educación (gestión directa)",
                "verification_entity": "Ministerio de Educación Nacional",
                "budget_earmark": 0.585,  # 58.5% of SGP
                "coordination_required": ["MEN", "Secretaría de Educación Municipal"],
            },
            {
                "law_number": "715",
                "law_year": 2001,
                "description": "SGP Educación - Infraestructura educativa para no certificados",
                "applicable_municipalities": [MunicipalCategory.CATEGORY_3, MunicipalCategory.CATEGORY_4, 
                                              MunicipalCategory.CATEGORY_5, MunicipalCategory.CATEGORY_6],
                "mandatory_pdm_section": "Programa de Infraestructura Educativa",
                "verification_entity": "Secretaría de Educación Departamental",
                "coordination_required": ["Secretaría de Educación Departamental"],
            },
        ],
        "PA09": [  # Health
            {
                "law_number": "715",
                "law_year": 2001,
                "description": "SGP Salud - Régimen subsidiado y salud pública",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Salud Pública y Aseguramiento",
                "verification_entity": "Ministerio de Salud y Protección Social",
                "budget_earmark": 0.245,  # 24.5% of SGP
                "coordination_required": ["Ministerio de Salud", "Secretaría de Salud Departamental"],
            }
        ],
        "PA10": [  # Institutional Capacity
            {
                "law_number": "1474",
                "law_year": 2011,
                "description": "Estatuto Anticorrupción - Transparencia y control interno",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Fortalecimiento Institucional y Transparencia",
                "verification_entity": "Contraloría y Procuraduría",
                "coordination_required": ["Contraloría", "Procuraduría", "Secretaría General"],
            },
            {
                "law_number": "1712",
                "law_year": 2014,
                "description": "Transparencia y Acceso a la Información Pública",
                "applicable_municipalities": list(MunicipalCategory),
                "mandatory_pdm_section": "Programa de Transparencia y Acceso a la Información",
                "verification_entity": "Procuraduría General de la Nación",
                "coordination_required": ["Procuraduría", "Secretaría General"],
            },
        ],
    }
    
    # PDM formulation timeline (month-by-month requirements)
    PDM_TIMELINE = [
        {
            "phase": PDMFormulationPhase.DIAGNOSTIC,
            "month": "Enero-Febrero",
            "key_activities": [
                "Consolidación del diagnóstico territorial (10 áreas de política FARFAN)",
                "Identificación de problemas centrales por área",
                "Recopilación de evidencia cuantitativa y cualitativa",
                "Consulta ciudadana y mesas de trabajo sectoriales",
            ],
            "required_products": [
                "Documento de diagnóstico territorial",
                "Árbol de problemas por área de política",
                "Base de datos de evidencia FARFAN",
                "Informe de participación ciudadana",
            ],
            "responsible_entities": ["Secretaría de Planeación", "Todas las secretarías sectoriales"],
            "legal_basis": "Ley 152/1994 Art. 31, Ley 1551/2012 Art. 5",
            "critical_path": True,
        },
        {
            "phase": PDMFormulationPhase.STRATEGIC_PART,
            "month": "Marzo",
            "key_activities": [
                "Formulación de la visión de desarrollo municipal",
                "Definición de ejes estratégicos",
                "Formulación de Objetivo General por eje",
                "Formulación de Objetivos Específicos",
                "Identificación de programas y subprogramas",
            ],
            "required_products": [
                "Documento de parte estratégica del PDM",
                "Matriz de Objetivos Generales y Específicos",
                "Árbol de objetivos (conversión del árbol de problemas)",
                "Estructura programática preliminar",
            ],
            "responsible_entities": ["Secretaría de Planeación", "Despacho del Alcalde"],
            "legal_basis": "Ley 152/1994 Art. 31, Decreto 1082/2015",
            "critical_path": True,
        },
        {
            "phase": PDMFormulationPhase.INVESTMENT_PLAN,
            "month": "Abril",
            "key_activities": [
                "Construcción de Cadenas de Valor por programa",
                "Especificación de productos y actividades",
                "Formulación de indicadores de resultado y producto",
                "Elaboración del Plan Plurianual de Inversiones",
                "Identificación de fuentes de financiación",
                "Validación de viabilidad presupuestal",
            ],
            "required_products": [
                "Cadenas de Valor completas (Insumos → Impactos)",
                "Plan Plurianual de Inversiones (4 años)",
                "Matriz de indicadores (Producto, Resultado, Impacto)",
                "Análisis de fuentes de financiación",
                "Cronograma de ejecución",
            ],
            "responsible_entities": ["Secretaría de Planeación", "Secretaría de Hacienda", "Todas las secretarías"],
            "legal_basis": "Ley 152/1994 Art. 31, Decreto 1082/2015, DNP Cadena de Valor",
            "critical_path": True,
        },
        {
            "phase": PDMFormulationPhase.CTP_APPROVAL,
            "month": "Abril-Mayo",
            "key_activities": [
                "Presentación del borrador del PDM al Consejo Territorial de Planeación (CTP)",
                "Recepción de concepto del CTP",
                "Ajustes al PDM según observaciones del CTP",
                "Preparación del proyecto de Acuerdo para el Concejo",
            ],
            "required_products": [
                "Concepto del CTP (obligatorio pero no vinculante)",
                "Documento de respuesta a observaciones del CTP",
                "Proyecto de Acuerdo del PDM",
            ],
            "responsible_entities": ["Secretaría de Planeación", "Consejo Territorial de Planeación", "Despacho del Alcalde"],
            "legal_basis": "Ley 152/1994 Art. 33-40 (CTP obligatorio)",
            "critical_path": True,
        },
        {
            "phase": PDMFormulationPhase.COUNCIL_APPROVAL,
            "month": "Mayo",
            "key_activities": [
                "Radicación del proyecto de Acuerdo ante el Concejo Municipal",
                "Debate en comisiones del Concejo",
                "Aprobación del PDM mediante Acuerdo Municipal",
                "Sanción del Acuerdo por el Alcalde",
                "Publicación oficial del PDM",
            ],
            "required_products": [
                "Acuerdo Municipal de aprobación del PDM",
                "PDM sancionado y publicado",
                "Documento oficial del PDM para ejecución (4 años)",
            ],
            "responsible_entities": ["Concejo Municipal", "Despacho del Alcalde", "Secretaría General"],
            "legal_basis": "Ley 152/1994 Art. 40, Ley 136/1994 (Concejo Municipal)",
            "critical_path": True,
        },
    ]
    
    def __init__(self):
        """Initialize the Colombian Legal Framework Engine."""
        logger.info("ColombianLegalFrameworkEngine initialized")
    
    def get_municipality_category(
        self, 
        population: int, 
        income_smmlv: float
    ) -> MunicipalCategory:
        """
        Determine municipal category based on population and income.
        
        Args:
            population: Total municipal population
            income_smmlv: Annual income in Salarios Mínimos Mensuales Legales Vigentes
            
        Returns:
            MunicipalCategory classification
            
        Note:
            Uses Law 617/2000 and Law 1551/2012 thresholds.
            Both criteria must be met for each category.
        """
        # Check from highest to lowest category
        for category, thresholds in sorted(
            self.CATEGORY_THRESHOLDS.items(),
            key=lambda x: x[1]["min_population"],
            reverse=True
        ):
            if (population >= thresholds["min_population"] and 
                income_smmlv >= thresholds["min_income_smmlv"]):
                logger.info(
                    f"Municipality classified as {category.value} "
                    f"(pop={population:,}, income={income_smmlv:,.0f} SMMLV)"
                )
                return category
        
        # Default to Category 6
        return MunicipalCategory.CATEGORY_6
    
    def get_sgp_allocation(
        self, 
        category: MunicipalCategory, 
        sector: SGPComponent
    ) -> dict[str, float]:
        """
        Calculate SGP allocation percentages for a municipality and sector.
        
        Args:
            category: Municipal category
            sector: SGP component (Education, Health, etc.)
            
        Returns:
            Dictionary with:
                - total_percentage: % of total SGP allocated to sector
                - discretionary_percentage: % that is discretionary (0 for most)
                - earmarked_percentage: % that is legally earmarked
                - receives_sector: bool indicating if municipality receives this sector
                
        Example:
            >>> engine.get_sgp_allocation(MunicipalCategory.CATEGORY_4, SGPComponent.GENERAL_PURPOSE)
            {
                'total_percentage': 0.116,
                'discretionary_percentage': 0.04872,  # 42% of 11.6%
                'earmarked_percentage': 0.06728,
                'receives_sector': True
            }
        """
        base_percentage = self.SGP_ALLOCATIONS[sector]
        
        # Education only for certificados (Special, 1, 2)
        if sector == SGPComponent.EDUCATION:
            receives = category in [
                MunicipalCategory.SPECIAL,
                MunicipalCategory.CATEGORY_1,
                MunicipalCategory.CATEGORY_2,
            ]
            return {
                "total_percentage": base_percentage if receives else 0.0,
                "discretionary_percentage": 0.0,  # Education is fully earmarked
                "earmarked_percentage": base_percentage if receives else 0.0,
                "receives_sector": receives,
            }
        
        # General Purpose has discretionary component for categories 4-6
        if sector == SGPComponent.GENERAL_PURPOSE:
            discretionary_pct = self.GENERAL_PURPOSE_DISCRETIONARY[category]
            discretionary = base_percentage * discretionary_pct
            earmarked = base_percentage * (1 - discretionary_pct)
            return {
                "total_percentage": base_percentage,
                "discretionary_percentage": discretionary,
                "earmarked_percentage": earmarked,
                "receives_sector": True,
            }
        
        # Health and Water are fully earmarked for all municipalities
        return {
            "total_percentage": base_percentage,
            "discretionary_percentage": 0.0,
            "earmarked_percentage": base_percentage,
            "receives_sector": True,
        }
    
    def get_legal_obligations(self, policy_area: str) -> list[LegalFramework]:
        """
        Get legal framework obligations for a FARFAN policy area.
        
        Args:
            policy_area: FARFAN policy area code (PA01-PA10)
            
        Returns:
            List of LegalFramework objects with all applicable laws
            
        Example:
            >>> engine.get_legal_obligations("PA01")
            [LegalFramework(law_number="1257", law_year=2008, ...)]
        """
        framework_data = self.POLICY_AREA_LEGAL_FRAMEWORKS.get(policy_area, [])
        
        legal_frameworks = []
        for data in framework_data:
            framework = LegalFramework(
                law_number=data["law_number"],
                law_year=data["law_year"],
                description=data["description"],
                applicable_municipalities=data["applicable_municipalities"],
                mandatory_pdm_section=data["mandatory_pdm_section"],
                verification_entity=data["verification_entity"],
                budget_earmark=data.get("budget_earmark"),
                coordination_required=data.get("coordination_required", []),
            )
            legal_frameworks.append(framework)
        
        logger.info(
            f"Retrieved {len(legal_frameworks)} legal frameworks for {policy_area}"
        )
        return legal_frameworks
    
    def validate_pdm_compliance(
        self,
        recommendation_id: str,
        policy_area: str,
        municipality_category: MunicipalCategory,
        required_financing_sources: list[FinancingSource],
        formulation_phase: PDMFormulationPhase,
    ) -> ComplianceReport:
        """
        Validate a recommendation for legal, financing, and timeline compliance.
        
        Args:
            recommendation_id: Unique recommendation identifier
            policy_area: FARFAN policy area (PA01-PA10)
            municipality_category: Municipal category
            required_financing_sources: Financing sources needed
            formulation_phase: PDM phase this recommendation targets
            
        Returns:
            ComplianceReport with detailed validation results
        """
        # Get applicable laws
        applicable_laws = self.get_legal_obligations(policy_area)
        
        # Filter laws applicable to this municipality category
        applicable_laws_filtered = [
            law for law in applicable_laws
            if municipality_category in law.applicable_municipalities
        ]
        
        # Check legal compliance
        legal_gaps = []
        if not applicable_laws_filtered:
            legal_gaps.append(
                f"No legal framework found for {policy_area} in {municipality_category.value}"
            )
        
        is_legally_compliant = len(legal_gaps) == 0
        
        # Check financing viability
        financing_gaps = []
        for source in required_financing_sources:
            if source == FinancingSource.SGP_EDUCATION:
                if municipality_category not in [
                    MunicipalCategory.SPECIAL,
                    MunicipalCategory.CATEGORY_1,
                    MunicipalCategory.CATEGORY_2,
                ]:
                    financing_gaps.append(
                        f"{source.value} not available to {municipality_category.value} (not certificado)"
                    )
        
        if financing_gaps:
            financing_viability = "CONSTRAINED"
        elif not required_financing_sources:
            financing_viability = "INFEASIBLE"
            financing_gaps.append("No financing sources identified")
        else:
            financing_viability = "VIABLE"
        
        # Check timeline feasibility
        timeline_risks = []
        is_timeline_feasible = True
        
        # Timeline always feasible if following standard phases
        if formulation_phase not in PDMFormulationPhase:
            timeline_risks.append("Invalid formulation phase specified")
            is_timeline_feasible = False
        
        # Calculate overall compliance score
        legal_score = 1.0 if is_legally_compliant else 0.5
        financing_score = {
            "VIABLE": 1.0,
            "CONSTRAINED": 0.6,
            "INFEASIBLE": 0.0,
        }[financing_viability]
        timeline_score = 1.0 if is_timeline_feasible else 0.5
        
        overall_compliance_score = (legal_score + financing_score + timeline_score) / 3.0
        
        # Determine compliance level
        if overall_compliance_score >= 0.9:
            compliance_level = "FULL"
        elif overall_compliance_score >= 0.6:
            compliance_level = "PARTIAL"
        else:
            compliance_level = "NON_COMPLIANT"
        
        # Generate recommendations for compliance
        recommendations_for_compliance = []
        if legal_gaps:
            recommendations_for_compliance.append(
                f"Articular con {applicable_laws_filtered[0].verification_entity if applicable_laws_filtered else 'entidad competente'} para cumplir marco legal"
            )
        if financing_gaps:
            recommendations_for_compliance.append(
                "Identificar fuentes de financiación alternativas (recursos propios, cofinanciación)"
            )
        if timeline_risks:
            recommendations_for_compliance.append(
                "Ajustar cronograma para cumplir con fases obligatorias de formulación del PDM"
            )
        
        compliance_report = ComplianceReport(
            recommendation_id=recommendation_id,
            policy_area=policy_area,
            municipality_category=municipality_category,
            applicable_laws=applicable_laws_filtered,
            is_legally_compliant=is_legally_compliant,
            legal_gaps=legal_gaps,
            required_financing_sources=required_financing_sources,
            financing_viability=financing_viability,
            financing_gaps=financing_gaps,
            formulation_phase=formulation_phase,
            is_timeline_feasible=is_timeline_feasible,
            timeline_risks=timeline_risks,
            overall_compliance_score=overall_compliance_score,
            compliance_level=compliance_level,
            recommendations_for_compliance=recommendations_for_compliance,
        )
        
        logger.info(
            f"Compliance validation for {recommendation_id}: "
            f"{compliance_level} (score={overall_compliance_score:.2f})"
        )
        
        return compliance_report
    
    def get_financing_sources(
        self,
        instrument_type: str,
        municipality_category: MunicipalCategory,
        policy_area: str,
    ) -> list[FinancingSource]:
        """
        Identify available financing sources for a policy instrument.
        
        Args:
            instrument_type: Type of policy instrument (e.g., "INFRASTRUCTURE", "SERVICE_DELIVERY")
            municipality_category: Municipal category
            policy_area: FARFAN policy area (PA01-PA10)
            
        Returns:
            List of available FinancingSource enums
            
        Logic:
            - PA08 (Education) → SGP_EDUCATION if certificado
            - PA09 (Health) → SGP_HEALTH (all municipalities)
            - PA03 (Environment) → SGP_WATER, RECURSOS_PROPIOS, COFINANCIACION
            - Infrastructure instruments → RECURSOS_PROPIOS, CREDITO, REGALIAS
            - Service delivery → SGP_GENERAL_PURPOSE, RECURSOS_PROPIOS
        """
        available_sources = []
        
        # Education financing (only certificados)
        if policy_area == "PA08":
            if municipality_category in [
                MunicipalCategory.SPECIAL,
                MunicipalCategory.CATEGORY_1,
                MunicipalCategory.CATEGORY_2,
            ]:
                available_sources.append(FinancingSource.SGP_EDUCATION)
            available_sources.append(FinancingSource.RECURSOS_PROPIOS)
            available_sources.append(FinancingSource.COFINANCIACION_DEPARTAMENTAL)
        
        # Health financing (all municipalities)
        elif policy_area == "PA09":
            available_sources.append(FinancingSource.SGP_HEALTH)
            available_sources.append(FinancingSource.RECURSOS_PROPIOS)
            available_sources.append(FinancingSource.COFINANCIACION_NACIONAL)
        
        # Water and Environment
        elif policy_area == "PA03":
            available_sources.append(FinancingSource.SGP_WATER)
            available_sources.append(FinancingSource.RECURSOS_PROPIOS)
            available_sources.append(FinancingSource.COFINANCIACION_NACIONAL)
            available_sources.append(FinancingSource.COOPERACION_INTERNACIONAL)
        
        # Infrastructure instruments
        elif "INFRASTRUCTURE" in instrument_type.upper():
            available_sources.append(FinancingSource.RECURSOS_PROPIOS)
            available_sources.append(FinancingSource.SGP_GENERAL_PURPOSE)
            available_sources.append(FinancingSource.CREDITO)
            available_sources.append(FinancingSource.REGALIAS)
            available_sources.append(FinancingSource.COFINANCIACION_DEPARTAMENTAL)
        
        # General service delivery
        else:
            available_sources.append(FinancingSource.SGP_GENERAL_PURPOSE)
            available_sources.append(FinancingSource.RECURSOS_PROPIOS)
            
            # Categories 4-6 have more discretionary resources
            if municipality_category in [
                MunicipalCategory.CATEGORY_4,
                MunicipalCategory.CATEGORY_5,
                MunicipalCategory.CATEGORY_6,
            ]:
                available_sources.append(FinancingSource.COFINANCIACION_DEPARTAMENTAL)
        
        logger.info(
            f"Identified {len(available_sources)} financing sources for "
            f"{instrument_type} in {policy_area} ({municipality_category.value})"
        )
        
        return available_sources
    
    def get_pdm_timeline_requirements(
        self, phase: PDMFormulationPhase
    ) -> dict[str, Any]:
        """
        Get detailed timeline requirements for a PDM formulation phase.
        
        Args:
            phase: PDM formulation phase
            
        Returns:
            Dictionary with phase details (month, activities, products, etc.)
        """
        for timeline_entry in self.PDM_TIMELINE:
            if timeline_entry["phase"] == phase:
                logger.info(f"Retrieved timeline requirements for {phase.value}")
                return timeline_entry
        
        logger.warning(f"No timeline requirements found for {phase.value}")
        return {}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def create_legal_framework_engine() -> ColombianLegalFrameworkEngine:
    """
    Factory function to create a Colombian Legal Framework Engine.
    
    Returns:
        Initialized ColombianLegalFrameworkEngine instance
    """
    return ColombianLegalFrameworkEngine()


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    # Example usage
    engine = create_legal_framework_engine()
    
    # Example 1: Determine municipality category
    category = engine.get_municipality_category(population=45_000, income_smmlv=35_000)
    print(f"Municipality Category: {category.value}")
    
    # Example 2: Get SGP allocation
    sgp_health = engine.get_sgp_allocation(category, SGPComponent.HEALTH)
    print(f"Health SGP: {sgp_health['total_percentage']*100:.1f}%")
    
    # Example 3: Get legal obligations
    legal_frameworks = engine.get_legal_obligations("PA01")
    print(f"PA01 Legal Frameworks: {len(legal_frameworks)}")
    
    # Example 4: Validate compliance
    compliance = engine.validate_pdm_compliance(
        recommendation_id="PA01-DIM01-CRISIS",
        policy_area="PA01",
        municipality_category=category,
        required_financing_sources=[FinancingSource.RECURSOS_PROPIOS],
        formulation_phase=PDMFormulationPhase.INVESTMENT_PLAN,
    )
    print(f"Compliance Level: {compliance.compliance_level}")
