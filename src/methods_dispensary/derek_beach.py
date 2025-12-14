#!/usr/bin/env python3
"""
Causal Deconstruction and Audit Framework (CDAF) v2.0
Framework de Producción para Análisis Causal de Planes de Desarrollo Territorial

THEORETICAL FOUNDATION (Derek Beach):
"A causal mechanism is a system of interlocking parts (entities engaging in
activities) that transmits causal forces from X to Y" (Beach 2016: 465)

This framework implements Theory-Testing Process Tracing with mechanistic evidence
evaluation using Beach's evidential tests taxonomy (Beach & Pedersen 2019).

Author: AI Systems Architect
Version: 2.1.0 (CVC Model Refactoring)
"""

import argparse
import hashlib
import json
import logging
import re
import sys
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    TypedDict,
    cast,
)

if TYPE_CHECKING:
    import fitz

# Core dependencies
try:
    import networkx as nx
    import numpy as np
    import pandas as pd
    import spacy
    import yaml
    from fuzzywuzzy import fuzz, process
    from pydantic import BaseModel, Field, ValidationError, validator
    from pydot import Dot, Edge, Node
    from scipy.spatial.distance import cosine
    from scipy.special import rel_entr
except ImportError as e:
    print(f"ERROR: Dependencia faltante. Ejecute: pip install {e.name}")
    sys.exit(1)

# DNP Standards Integration
try:
    from dnp_integration import ValidadorDNP

    DNP_AVAILABLE = True
except ImportError:
    DNP_AVAILABLE = False
    warnings.warn("Módulos DNP no disponibles. Validación DNP deshabilitada.", stacklevel=2)

# Refactored Bayesian Engine (F1.2: Architectural Refactoring)
try:
    from inference.bayesian_adapter import BayesianEngineAdapter

    REFACTORED_BAYESIAN_AVAILABLE = True
except ImportError:
    REFACTORED_BAYESIAN_AVAILABLE = False
    warnings.warn("Motor Bayesiano refactorizado no disponible. Usando implementación legacy.", stacklevel=2)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ============================================================================
# CANONICAL CONSTANTS FROM GUIDES
# ============================================================================

# ============================================================================
# CANONICAL CONSTANTS FROM GUIDES - PDET-Focused Policy Areas
# ============================================================================
# Source: questionnaire_monolith.json + PDET/territorial planning methodology
# All parameters are deterministic and traceable to official DNP/SisPT guides
# ============================================================================

MICRO_LEVELS = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.00
}

CANON_POLICY_AREAS = {
    "PA01": {
        "name": "Derechos de las mujeres e igualdad de género",
        "legacy": "P1",
        "pdet_focus": "Mujeres rurales, víctimas del conflicto y liderazgo femenino en territorios PDET",
        "keywords": [
            # Core concepts
            "género", "mujer", "mujeres", "igualdad de género", "equidad de género",
            "mujeres rurales", "campesinas", "mujeres indígenas", "mujeres afrodescendientes",
            
            # Violence and protection - PDET context
            "violencia basada en género", "VBG", "feminicidio", "violencia intrafamiliar",
            "violencia sexual", "violencia económica", "violencia psicológica",
            "violencia sexual en el conflicto", "violencia de género en zonas rurales",
            "ruta de atención VBG rural", "casas de justicia", "comisarías de familia rural",
            
            # Economic rights - Rural focus
            "brecha salarial", "participación laboral", "emprendimiento femenino",
            "economía del cuidado", "trabajo no remunerado",
            "proyectos productivos mujeres", "asociaciones de mujeres", "cooperativas femeninas",
            "acceso a crédito rural", "fondo de mujeres", "empoderamiento económico",
            "mujeres cabeza de familia", "jefatura femenina hogar",
            
            # Political participation - Territorial
            "participación política", "liderazgo femenino", "paridad", "cuotas de género",
            "consejos comunitarios", "JAC", "Juntas de Acción Comunal",
            "mesas de mujeres", "organizaciones de mujeres", "redes de mujeres",
            "veeduría ciudadana", "control social", "presupuestos participativos",
            
            # Health and rights - Rural context
            "salud sexual y reproductiva", "derechos reproductivos", "mortalidad materna",
            "parto humanizado", "partería tradicional", "medicina ancestral",
            "atención prenatal rural", "planificación familiar", "IVE",
            "salud mental mujeres", "atención psicosocial",
            
            # Land and property rights
            "acceso a tierras", "titulación predios", "adjudicación tierras mujeres",
            "baldíos", "UAF", "Unidades Agrícolas Familiares",
            
            # PDET-specific
            "PATR", "Planes de Acción para la Transformación Regional",
            "iniciativas PDET género", "pilares PDET", "ART", "Agencia de Renovación del Territorio",
            
            # Data sources
            "DANE", "Medicina Legal", "SIVIGILA", "SISPRO", "Fiscalía",
            "censo agropecuario", "terridata", "sistema de información PDET"
        ]
    },
    
    "PA02": {
        "name": "Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales",
        "legacy": "P2",
        "pdet_focus": "Prevención en territorios post-acuerdo, alertas tempranas y protección comunitaria",
        "keywords": [
            # Conflict and violence - Post-agreement
            "conflicto armado", "violencia", "prevención", "protección",
            "post-conflicto", "post-acuerdo", "implementación del acuerdo de paz",
            "territorios PDET", "municipios PDET", "subregiones PDET",
            
            # Armed groups and violence
            "grupos armados organizados", "GAO", "grupos de delincuencia organizada", "GDO",
            "disidencias", "estructuras armadas", "economías ilícitas",
            "narcotráfico", "cultivos ilícitos", "coca", "sustitución voluntaria", "PNIS",
            "minería ilegal", "extorsión", "control territorial",
            
            # Human rights violations
            "derechos humanos", "DIH", "derecho internacional humanitario",
            "violaciones a derechos humanos", "crímenes de guerra",
            "masacres", "desplazamiento forzado", "confinamiento",
            "reclutamiento forzado", "minas antipersona", "MAP", "MUSE",
            
            # Early warning - Territorial
            "alertas tempranas", "SAT", "sistema de alertas", "riesgo",
            "informes de riesgo", "notas de seguimiento", "Defensoría del Pueblo",
            "comités territoriales de prevención", "planes de contingencia",
            "mapeo de riesgos", "análisis de contexto",
            
            # Protection mechanisms
            "medidas de protección", "rutas de protección", "UNP",
            "protección colectiva", "planes de protección comunitaria",
            "guardias indígenas", "guardias cimarronas", "guardias campesinas",
            "autoprotección", "sistema de protección territorial",
            
            # Victims and vulnerable populations
            "víctimas", "afectados", "población vulnerable",
            "desplazados", "comunidades étnicas", "campesinos",
            
            # Institutions and programs
            "CIAT", "Comisión Intersectorial de Alertas Tempranas",
            "CIPRAT", "consejos de seguridad", "fuerza pública",
            "Policía comunitaria", "Ejército"
        ]
    },
    
    "PA03": {
        "name": "Ambiente sano, cambio climático, prevención y atención a desastres",
        "legacy": "P3",
        "pdet_focus": "Sostenibilidad ambiental rural, ordenamiento territorial y gestión de riesgos",
        "keywords": [
            # Environmental rights - Rural context
            "ambiente sano", "medio ambiente", "ambiental", "sostenible", "sostenibilidad",
            "economía campesina sostenible", "agroecología", "sistemas agroforestales",
            "bioeconomía", "negocios verdes", "cadenas de valor sostenibles",
            
            # Climate change - Territorial impact
            "cambio climático", "adaptación climática", "mitigación", "emisiones",
            "gases de efecto invernadero", "carbono neutral",
            "variabilidad climática", "sequías", "inundaciones",
            "seguridad hídrica", "estrés hídrico",
            
            # Ecosystems - Strategic regions
            "ecosistemas", "biodiversidad", "conservación", "áreas protegidas",
            "páramos", "humedales", "bosques", "selva", "Amazonía",
            "corredores biológicos", "reservas naturales", "zonas de amortiguación",
            "deforestación", "restauración ecológica", "reforestación",
            
            # Illegal activities impact
            "cultivos ilícitos impacto ambiental", "aspersión", "glifosato",
            "minería ilegal", "contaminación por mercurio", "afectación de fuentes hídricas",
            "tala ilegal", "tráfico de fauna", "pesca ilegal",
            
            # Disasters - Rural vulnerability
            "desastres", "gestión del riesgo", "prevención de desastres",
            "atención de emergencias", "resiliencia",
            "deslizamientos", "avalanchas", "crecientes súbitas",
            "incendios forestales", "temporada seca", "temporada de lluvias",
            "POMCA", "planes de ordenamiento de cuencas",
            
            # Water and resources - Rural access
            "recursos hídricos", "cuencas", "agua potable", "saneamiento básico",
            "acueductos comunitarios", "acueductos veredales", "pozos",
            "sistemas de abastecimiento rural", "tratamiento de aguas",
            "alcantarillado rural", "soluciones individuales",
            
            # PDET-specific
            "pilar ambiental PDET", "planes de manejo ambiental",
            "guardabosques", "familias guardabosques",
            
            # Institutions
            "CAR", "CRC", "Corporación Autónoma Regional", "IDEAM", "MinAmbiente",
            "Parques Nacionales Naturales", "UNGRD", "consejos de cuenca",
            "consejos municipales de gestión del riesgo", "CMGRD"
        ]
    },
    
    "PA04": {
        "name": "Derechos económicos, sociales y culturales",
        "legacy": "P4",
        "pdet_focus": "Infraestructura rural, servicios básicos y desarrollo económico territorial",
        "keywords": [
            # Economic rights - Rural development
            "derechos económicos", "DESC", "desarrollo económico", "empleo", "trabajo decente",
            "economía campesina", "agricultura familiar", "pequeños productores",
            "desarrollo rural integral", "economía solidaria", "cooperativas",
            "asociatividad", "encadenamientos productivos",
            
            # Rural infrastructure - Critical needs
            "infraestructura", "vías", "conectividad", "transporte", "movilidad",
            "vías terciarias", "vías rurales", "caminos veredales", "puentes",
            "placa huella", "mantenimiento vial", "maquinaria amarilla",
            "accesibilidad rural", "integración territorial",
            
            # Basic services - Rural coverage
            "servicios básicos", "acueducto", "alcantarillado", "energía eléctrica",
            "gas natural", "telecomunicaciones", "internet",
            "electrificación rural", "energías alternativas", "paneles solares",
            "conectividad digital", "puntos vive digital", "zonas wifi",
            "telefonía móvil", "cobertura rural",
            
            # Social rights - Rural context
            "salud", "educación", "vivienda", "seguridad social",
            "salud rural", "puestos de salud", "centros de salud rural",
            "IPS", "EPS", "régimen subsidiado", "ARL",
            "educación rural", "escuelas rurales", "colegios agropecuarios",
            "transporte escolar", "alimentación escolar", "PAE",
            "jornada única", "etnoeducación", "pedagogías rurales",
            "vivienda rural", "mejoramiento de vivienda", "saneamiento básico vivienda",
            "materiales locales", "vivienda digna",
            
            # Agricultural development
            "asistencia técnica", "extensión agropecuaria", "EPSEA",
            "adecuación de tierras", "distritos de riego", "infraestructura productiva",
            "centros de acopio", "plantas de transformación", "agroindustria rural",
            "comercialización", "mercados campesinos", "compras públicas",
            
            # Financial inclusion
            "inclusión financiera", "crédito rural", "FINAGRO", "Banco Agrario",
            "microcrédito", "fondos rotatorios", "garantías",
            
            # Cultural rights - Territorial identity
            "cultura", "patrimonio cultural", "identidad cultural", "diversidad cultural",
            "cultura campesina", "saberes ancestrales", "patrimonio inmaterial",
            "casas de cultura", "bibliotecas rurales", "escenarios culturales",
            "fiestas tradicionales", "gastronomía regional",
            
            # Food security - Territorial
            "seguridad alimentaria", "soberanía alimentaria", "nutrición",
            "autosuficiencia alimentaria", "huertas caseras", "seguridad nutricional",
            "desnutrición infantil", "malnutrición",
            
            # PDET-specific
            "PATR componente infraestructura", "obras por impuestos",
            "catastro multipropósito", "formalización empresarial",
            
            # Institutions
            "MinSalud", "MinEducación", "MinVivienda", "MinTransporte",
            "MinAgricultura", "ADR", "Agencia de Desarrollo Rural",
            "INVIAS", "IPSE", "MinTIC"
        ]
    },
    
    "PA05": {
        "name": "Derechos de las víctimas y construcción de paz",
        "legacy": "P5",
        "pdet_focus": "Reparación integral, retornos y construcción de paz territorial",
        "keywords": [
            # Victims' rights - Comprehensive
            "víctimas", "derechos de las víctimas", "reparación", "indemnización",
            "restitución", "rehabilitación", "satisfacción", "garantías de no repetición",
            "registro único de víctimas", "RUV", "caracterización de víctimas",
            "enfoque diferencial", "enfoque de género", "enfoque étnico",
            
            # Types of victimization
            "desplazamiento forzado", "despojo de tierras", "abandono forzado",
            "homicidio", "desaparición forzada", "secuestro", "tortura",
            "violencia sexual", "reclutamiento forzado", "minas antipersona",
            "masacres", "ataques a poblaciones", "confinamiento",
            
            # Return and relocation
            "retornos", "reubicaciones", "reasentamientos",
            "planes de retorno", "acompañamiento al retorno", "garantías de seguridad",
            "reconstrucción del proyecto de vida", "estabilización socioeconómica",
            
            # Peacebuilding - Territorial
            "construcción de paz", "paz territorial", "reconciliación", "convivencia",
            "perdón", "memoria histórica", "pedagogía de la paz",
            "culturas de paz", "resolución pacífica de conflictos",
            "pactos de convivencia", "planes de convivencia",
            
            # Psychosocial support
            "atención psicosocial", "acompañamiento psicosocial", "PAPSIVI",
            "salud mental", "trauma", "duelo", "sanación colectiva",
            "estrategia de recuperación emocional", "grupos de apoyo mutuo",
            
            # Truth and justice
            "verdad", "justicia", "justicia transicional", "JEP",
            "Jurisdicción Especial para la Paz", "CEV", "Comisión de la Verdad",
            "búsqueda de desaparecidos", "UBPD", "exhumaciones",
            "sentencias", "macrocasos", "reconocimiento de responsabilidad",
            
            # Memory and non-repetition
            "memoria histórica", "lugares de memoria", "museos de memoria",
            "iniciativas de memoria", "archivos de memoria",
            "monumentos", "conmemoraciones", "actos de reconocimiento",
            "garantías de no repetición", "reformas institucionales",
            
            # Community participation
            "participación de víctimas", "mesas de víctimas", "organizaciones de víctimas",
            "redes de víctimas", "voceros de víctimas",
            "planes de reparación colectiva", "sujetos de reparación colectiva",
            
            # Land restitution
            "restitución de tierras", "Unidad de Restitución",
            "jueces de restitución", "sentencias de restitución",
            "formalización de predios restituidos", "proyectos productivos post-restitución",
            
            # PDET-specific
            "territorios de paz", "laboratorios de paz",
            "PDET como mecanismo de reparación", "transformación territorial",
            
            # Institutions
            "Unidad de Víctimas", "UARIV", "Fiscalía", "Defensoría del Pueblo",
            "CNMH", "Centro Nacional de Memoria Histórica",
            "Sistema Integral de Verdad, Justicia, Reparación y No Repetición", "SIVJRNR"
        ]
    },
    
    "PA06": {
        "name": "Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores",
        "legacy": "P6",
        "pdet_focus": "Protección de niñez rural, prevención de reclutamiento y oportunidades para jóvenes",
        "keywords": [
            # Children and adolescents - Rural context
            "niñez", "niños", "niñas", "adolescencia", "adolescentes",
            "primera infancia", "infancia",
            "niñez rural", "infancia campesina", "niños indígenas", "niños afrodescendientes",
            
            # Protection - Conflict-affected areas
            "protección integral", "derechos de la niñez", "interés superior del niño",
            "prevención de violencia", "abuso infantil", "explotación sexual",
            "prevención de reclutamiento", "reclutamiento forzado", "utilización de niños",
            "niños víctimas del conflicto", "niños desvinculados",
            "rutas de protección rural", "comisarías de familia",
            "sistema de responsabilidad penal adolescente", "SRPA",
            
            # Development - Rural needs
            "desarrollo integral", "educación", "salud infantil", "nutrición infantil",
            "estimulación temprana", "desarrollo cognitivo",
            "centros de desarrollo infantil", "CDI", "hogares comunitarios",
            "jardines sociales", "atención integral primera infancia",
            "educación inicial", "transiciones educativas",
            "desnutrición crónica", "bajo peso al nacer", "retardo en talla",
            "lactancia materna", "complementación alimentaria",
            
            # Education - Rural context
            "educación rural", "escuela nueva", "modelos flexibles",
            "transporte escolar", "internados", "residencias escolares",
            "alimentación escolar", "PAE", "útiles escolares",
            "deserción escolar", "repitencia", "analfabetismo",
            "educación media", "articulación con educación superior",
            
            # Youth - Opportunities and participation
            "juventud", "jóvenes", "adolescentes y jóvenes",
            "jóvenes rurales", "juventud campesina",
            "participación juvenil", "consejos de juventud", "voz de los jóvenes",
            "plataformas juveniles", "organizaciones juveniles",
            "liderazgo juvenil", "formación política juvenil",
            
            # Opportunities - Economic and social
            "oportunidades", "empleabilidad juvenil", "emprendimiento juvenil",
            "formación para el trabajo", "SENA rural", "técnica", "tecnológica",
            "primer empleo", "pasantías rurales", "experiencia laboral",
            "proyectos productivos juveniles", "relevo generacional",
            "acceso a tierras jóvenes", "arraigo rural",
            
            # Recreation and culture
            "recreación", "deporte", "cultura", "tiempo libre",
            "escuelas deportivas", "ludotecas", "bibliotecas",
            "acceso a tecnología", "alfabetización digital",
            
            # Mental health and substance abuse
            "salud mental juvenil", "prevención de suicidio",
            "prevención de consumo de sustancias", "farmacodependencia",
            "embarazo adolescente", "prevención de embarazo temprano",
            "educación sexual", "proyectos de vida",
            
            # PDET-specific
            "estrategia para niñez y adolescencia PDET",
            "jóvenes constructores de paz", "semilleros de paz",
            
            # Institutions
            "ICBF", "Instituto Colombiano de Bienestar Familiar",
            "Comisarías de Familia", "Defensorías de Familia",
            "Ministerio de Educación", "Secretarías de Educación",
            "Colombia Joven", "Sistema Nacional de Juventud"
        ]
    },
    
    "PA07": {
        "name": "Tierras y territorios",
        "legacy": "P7",
        "pdet_focus": "Acceso, formalización, ordenamiento territorial y catastro multipropósito",
        "keywords": [
            # Land rights - Rural focus
            "tierras", "territorio", "territorial", "ordenamiento territorial",
            "uso del suelo", "tenencia de la tierra", "propiedad rural",
            "derecho a la tierra", "función social de la propiedad",
            "pequeña propiedad", "mediana propiedad", "UAF",
            
            # Land distribution and access
            "acceso a tierras", "redistribución", "reforma agraria integral",
            "fondo de tierras", "adjudicación de baldíos", "baldíos",
            "extinción de dominio", "tierras inexplotadas",
            "concentración de la tierra", "latifundio", "minifundio",
            
            # Formalization
            "formalización de la propiedad", "titulación", "saneamiento de títulos",
            "clarificación de la propiedad", "procedimientos agrarios",
            "registro de tierras", "inscripción en registro",
            "escrituración", "notarías", "costo de formalización",
            
            # Planning - Municipal and rural
            "POT", "Plan de Ordenamiento Territorial", "PBOT", "EOT",
            "esquema de ordenamiento territorial", "plan básico de ordenamiento",
            "zonificación", "usos del suelo", "clasificación del suelo",
            "suelo rural", "suelo de expansión", "suelo de protección",
            "suelo suburbano", "centros poblados", "áreas urbanas",
            "conflictos de uso del suelo", "aptitud del suelo",
            
            # Cadastre - Multipurpose
            "catastro", "gestión catastral", "actualización catastral", "avalúo catastral",
            "catastro multipropósito", "barrido predial", "censo predial",
            "información catastral", "formación catastral",
            "impuesto predial", "base gravable", "estratificación rural",
            
            # Land restitution - Post-conflict
            "restitución de tierras", "despojo", "abandono forzado",
            "Unidad de Restitución de Tierras", "URT",
            "jueces de restitución", "oposiciones", "falsas tradiciones",
            "micro-focalización", "caracterización de predios",
            "protección jurídica", "protección material",
            
            # Rural development - Territorial
            "desarrollo rural", "acceso a factores productivos",
            "infraestructura rural", "servicios rurales",
            "centros regionales", "articulación urbano-rural",
            "sistemas de ciudades", "mercados regionales",
            
            # Indigenous and afro territories
            "territorios étnicos", "resguardos indígenas", "territorios colectivos",
            "consejos comunitarios", "títulos colectivos",
            "consulta previa", "consentimiento previo libre e informado",
            "autonomía territorial", "gobierno propio", "autoridades tradicionales",
            "planes de vida", "planes de etnodesarrollo",
            "ampliación de resguardos", "saneamiento de resguardos",
            
            # Land conflicts
            "conflictos agrarios", "conflictos por tierras",
            "disputas territoriales", "ocupación irregular",
            "invasiones", "desalojos", "legalización de asentamientos",
            
            # Environmental zoning
            "áreas protegidas", "zonas de reserva forestal",
            "sustracción de reservas", "zonificación ambiental",
            "ordenamiento productivo", "sistemas agroforestales",
            
            # PDET-specific
            "pilar tierras PDET", "ordenamiento social de la propiedad",
            "cierre de la frontera agrícola", "ZRC", "Zonas de Reserva Campesina",
            
            # Institutions
            "ANT", "Agencia Nacional de Tierras",
            "IGAC", "Instituto Geográfico Agustín Codazzi",
            "Superintendencia de Notariado y Registro",
            "UPRA", "Unidad de Planificación Rural Agropecuaria",
            "DNP", "Ministerio de Agricultura"
        ]
    },
    
    "PA08": {
        "name": "Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza",
        "legacy": "P8",
        "pdet_focus": "Protección de líderes sociales y comunitarios en territorios PDET",
        "keywords": [
            # Leaders and defenders - Rural context
            "líderes sociales", "liderazgo social", "defensores de derechos humanos",
            "defensores", "activistas", "líderes comunitarios",
            "líderes rurales", "líderes campesinos", "líderes veredales",
            "presidentes de JAC", "líderes de organizaciones sociales",
            
            # Types of leaders - Specific
            "líderes ambientales", "líderes indígenas", "líderes afrodescendientes",
            "líderes de restitución", "líderes de sustitución de cultivos",
            "líderes de víctimas", "líderes de mujeres",
            "líderes comunales", "voceros comunitarios",
            "defensores de territorio", "guardias indígenas líderes",
            
            # Threats and violence - Systematic
            "amenazas", "asesinatos", "homicidios", "agresiones", "intimidación",
            "hostigamiento", "estigmatización", "señalamiento",
            "seguimientos", "vigilancia", "presiones", "extorsión",
            "desplazamiento de líderes", "exilio interno",
            "atentados", "sicariato", "violencia sistemática",
            
            # Risk factors
            "territorios de alto riesgo", "zonas rojas", "corredores estratégicos",
            "presencia de grupos armados", "economías ilícitas",
            "conflictos territoriales", "megaproyectos",
            "oposición a proyectos extractivos",
            
            # Protection - Comprehensive
            "protección", "medidas de protección", "esquemas de seguridad",
            "rutas de protección", "UNP", "Unidad Nacional de Protección",
            "medidas individuales", "medidas colectivas",
            "chaleco antibalas", "vehículo blindado", "escoltas",
            "medios de comunicación", "botones de pánico",
            "reubicación temporal", "traslados",
            
            # Community protection
            "protección colectiva", "planes de protección comunitaria",
            "autoprotección", "protección territorial",
            "sistemas comunitarios de alerta temprana",
            "redes de protección", "acompañamiento internacional",
            
            # Prevention
            "prevención", "alertas tempranas", "análisis de riesgo", "mapeo de riesgos",
            "caracterización de amenazas", "planes de contingencia",
            "protocolos de seguridad", "cultura de seguridad",
            "evaluaciones de riesgo", "rutas de evacuación",
            
            # Justice and accountability
            "investigación", "judicialización", "impunidad", "Fiscalía",
            "Fiscalía especializada", "investigaciones efectivas",
            "esclarecimiento", "identificación de autores",
            "garantías de no repetición", "sanciones",
            "justicia para líderes asesinados",
            
            # Institutional response
            "comisión intersectorial", "planes de acción oportuna", "PAO",
            "sistema de prevención y alerta", "articulación institucional",
            "presencia institucional", "fortalecimiento institucional local",
            
            # Participation guarantees
            "garantías para la participación", "espacios seguros",
            "protección de procesos organizativos",
            "libertad de expresión", "libertad de asociación",
            "derecho a la protesta", "movilización social",
            
            # Documentation and monitoring
            "registro de agresiones", "bases de datos", "observatorios",
            "monitoreo de situación", "informes de riesgo",
            "documentación de casos", "sistemas de información",
            
            # PDET-specific
            "líderes PDET", "implementadores del acuerdo",
            "defensores de la paz", "constructores de paz",
            
            # Institutions
            "Defensoría del Pueblo", "Procuraduría", "Fiscalía General",
            "Unidad Nacional de Protección", "UNP",
            "Ministerio del Interior", "Comisión Nacional de Garantías de Seguridad",
            "OACNUDH", "Oficina del Alto Comisionado ONU DDHH",
            "ONG de derechos humanos", "organizaciones internacionales"
        ]
    },
    
    "PA09": {
        "name": "Crisis de derechos de personas privadas de la libertad",
        "legacy": "P9",
        "pdet_focus": "Condiciones carcelarias y alternativas de justicia en zonas rurales",
        "keywords": [
            # Prison population
            "población privada de la libertad", "PPL", "personas privadas",
            "reclusos", "internos", "detenidos", "condenados", "sindicados",
            "presos políticos", "prisioneros de guerra",
            
            # Facilities - Regional
            "cárcel", "centro penitenciario", "establecimiento carcelario",
            "INPEC", "Instituto Nacional Penitenciario y Carcelario",
            "cárceles regionales", "cárceles municipales", "estaciones de policía",
            "centros de reclusión", "pabellones", "patios",
            
            # Crisis - Structural problems
            "hacinamiento", "sobrepoblación carcelaria", "crisis carcelaria",
            "condiciones inhumanas", "violación de derechos",
            "trato cruel", "tortura", "tratos degradantes",
            "motines", "disturbios", "incendios", "emergencias carcelarias",
            
            # Rights violations
            "derechos humanos", "dignidad humana", "salud en prisión",
            "alimentación", "visitas", "comunicación",
            "derecho a la salud", "atención médica", "medicamentos",
            "enfermedades", "tuberculosis", "VIH", "enfermedades crónicas",
            "salud mental en prisión", "suicidios", "autolesiones",
            "hacinamiento y salud", "condiciones sanitarias",
            
            # Vulnerable groups
            "mujeres privadas de la libertad", "madres gestantes", "madres lactantes",
            "niños en prisión", "adultos mayores", "población LGBTI",
            "personas con discapacidad", "enfermos terminales",
            "indígenas privados de libertad", "enfoque diferencial",
            
            # Reintegration
            "resocialización", "rehabilitación", "reinserción social",
            "programas de tratamiento", "educación en prisión", "trabajo penitenciario",
            "redención de pena", "beneficios administrativos",
            "preparación para la libertad", "pos-penados",
            "acompañamiento post-carcelario", "seguimiento",
            
            # Justice - Alternatives
            "justicia", "debido proceso", "medidas alternativas", "prisión domiciliaria",
            "vigilancia electrónica", "mecanismos sustitutivos",
            "detención preventiva", "hacinamiento por sindicados",
            "justicia restaurativa", "conciliación",
            "descongestión judicial", "oralidad",
            
            # Rural and PDET context
            "privados de libertad de zonas rurales", "campesinos recluidos",
            "delitos relacionados con cultivos ilícitos", "pequeños cultivadores",
            "criminalización de la pobreza", "dosis mínima",
            "personas privadas por delitos menores",
            
            # Conflict-related imprisonment
            "excombatientes privados de libertad", "presos políticos",
            "delitos políticos", "conexidad", "amnistía", "indulto",
            "privados de libertad por el conflicto",
            
            # Family and social connections
            "visitas familiares", "visita íntima", "comunicación familiar",
            "distancia de las cárceles", "traslados", "cercanía familiar",
            "impacto en familias rurales", "costos de visita",
            
            # Infrastructure problems
            "infraestructura carcelaria", "deterioro de instalaciones",
            "construcción de cárceles", "ampliación de cupos",
            "espacios inadecuados", "celdas", "calabozos",
            
            # PDET-specific
            "acceso a justicia en zonas rurales", "defensores públicos",
            "casas de justicia", "consultorios jurídicos",
            
            # Institutions
            "Defensoría del Pueblo", "Procuraduría", "Corte Constitucional",
            "INPEC", "Ministerio de Justicia", "Fiscalía",
            "jueces de ejecución de penas", "defensoría pública"
        ]
    },
    
    "PA10": {
        "name": "Migración transfronteriza",
        "legacy": "P10",
        "pdet_focus": "Migración venezolana en zonas de frontera, integración rural y desafíos humanitarios",
        "keywords": [
            # Migration - General
            "migración", "migrante", "migrantes", "migración transfronteriza",
            "flujos migratorios", "movilidad humana", "migración internacional",
            "migración irregular", "migración pendular", "caminantes",
            "tránsito migratorio", "rutas migratorias",
            
            # Refugees and asylum
            "refugiado", "refugiados", "solicitantes de asilo", "protección internacional",
            "estatuto de refugiado", "reconocimiento de refugiado",
            "necesidad de protección", "persecución",
            
            # Venezuelan migration - Dominant flow
            "migración venezolana", "venezolanos", "éxodo venezolano",
            "crisis venezolana", "diáspora venezolana",
            "familias venezolanas", "población venezolana",
            "refugiados venezolanos", "migrantes económicos",
            
            # Border - Regional context
            "frontera", "zona de frontera", "paso fronterizo", "control migratorio",
            "frontera colombo-venezolana", "frontera norte", "frontera sur",
            "La Guajira", "Norte de Santander", "Arauca", "Vichada", "Guainía",
            "Cúcuta", "Maicao", "Paraguachón", "Arauca ciudad",
            "pasos irregulares", "trochas", "cruces informales",
            "cierre de frontera", "reapertura de frontera",
            
            # Regularization - Documentation
            "regularización", "documentación", "permisos", "PPT", "Permiso de Permanencia",
            "PEP", "Permiso Especial de Permanencia", "TMF", "Tarjeta de Movilidad Fronteriza",
            "PPT-E", "Permiso por Protección Temporal", "Estatuto Temporal",
            "registro biométrico", "cédula de extranjería",
            "documentos de identidad", "pasaportes", "certificados",
            "caracterización migratoria", "RAMV", "Registro Administrativo",
            
            # Integration - Social and economic
            "integración", "inclusión social", "acceso a servicios", "derechos de migrantes",
            "integración socioeconómica", "integración laboral",
            "empleabilidad de migrantes", "trabajo informal",
            "explotación laboral", "precarización laboral",
            "emprendimiento migrante", "medios de vida",
            "convivencia ciudadana", "cohesión social",
            "discriminación", "xenofobia", "rechazo social",
            
            # Access to services - Critical needs
            "salud para migrantes", "atención en salud", "vacunación",
            "salud materno-infantil", "desnutrición infantil migrante",
            "educación para migrantes", "acceso escolar", "validación de estudios",
            "convalidación de títulos", "niños migrantes en escuelas",
            "vivienda para migrantes", "alojamiento temporal",
            "saneamiento básico", "condiciones habitacionales",
            
            # Humanitarian - Emergency response
            "crisis humanitaria", "asistencia humanitaria", "albergues", "atención humanitaria",
            "ayuda humanitaria", "emergencia humanitaria",
            "puntos de atención", "PAAMS", "Puestos de Atención",
            "kits humanitarios", "alimentación", "agua potable",
            "atención de emergencia", "primeros auxilios",
            "protección en tránsito", "riesgos en ruta",
            
            # Vulnerable populations
            "mujeres migrantes", "niños migrantes", "familias migrantes",
            "migrantes LGBTI", "adultos mayores migrantes",
            "personas con discapacidad migrantes",
            "mujeres gestantes migrantes", "partos de migrantes",
            "niñez migrante", "adolescentes migrantes",
            "menores no acompañados", "separación familiar",
            
            # Protection risks
            "trata de personas", "tráfico de migrantes", "explotación sexual",
            "reclutamiento forzado de migrantes", "violencia basada en género",
            "extorsión a migrantes", "criminalidad contra migrantes",
            "redes de tráfico", "rutas de trata",
            
            # Rural and PDET context
            "migración en zonas rurales", "migrantes en áreas rurales",
            "trabajo agrícola migrante", "jornaleros migrantes",
            "mano de obra rural", "agricultura y migración",
            "asentamientos informales rurales", "ocupación de baldíos",
            "frontera agrícola y migración",
            
            # Economic impact
            "impacto económico de la migración", "mercado laboral",
            "competencia laboral", "informalidad",
            "remesas", "economía local", "comercio fronterizo",
            "servicios públicos", "presión sobre servicios",
            
            # Social cohesion
            "convivencia", "tejido social", "conflictos sociales",
            "competencia por recursos", "tensiones comunitarias",
            "mediación comunitaria", "diálogo intercultural",
            
            # Mixed migration
            "flujos mixtos", "otras nacionalidades", "migración haitiana",
            "migración cubana", "tránsito hacia otros países",
            "migración extracontinental", "migración africana",
            "migración asiática", "Darién", "ruta del Pacífico",
            
            # Return and circulation
            "retorno voluntario", "retorno asistido", "deportaciones",
            "migración circular", "ida y vuelta", "retornados colombianos",
            "colombianos en el exterior", "diáspora colombiana",
            
            # Legal framework
            "normatividad migratoria", "Ley de Migración", "decretos",
            "resoluciones migratorias", "marco legal",
            "derechos de los migrantes", "principio de no devolución",
            "debido proceso migratorio",
            
            # Institutional coordination
            "coordinación interinstitucional", "Grupo de Migración",
            "GIFMM", "Grupo Interagencial sobre Flujos Migratorios Mixtos",
            "mesas de trabajo", "comités territoriales",
            "articulación nacional-territorial",
            
            # Data and monitoring
            "información migratoria", "caracterización", "censos",
            "monitoreo de flujos", "estadísticas migratorias",
            "sistemas de información", "datos desagregados",
            
            # PDET-specific
            "migración en municipios PDET", "frontera y PDET",
            "integración en territorios rurales",
            "impacto en construcción de paz",
            
            # Institutions
            "Migración Colombia", "ACNUR", "Alto Comisionado de las Naciones Unidas para los Refugiados",
            "OIM", "Organización Internacional para las Migraciones",
            "UNICEF", "OPS/OMS", "PMA", "Programa Mundial de Alimentos",
            "Cancillería", "Ministerio de Relaciones Exteriores",
            "Gerencia de Frontera", "GIFMM local",
            "Cruz Roja", "organizaciones humanitarias", "ONG migratorias"
        ]
    }
}

PDT_PATTERNS = {
    # ============================================================================
    # SECTION DELIMITERS - Hierarchical structure patterns
    # ============================================================================
    "section_delimiters": re.compile(
        r'^(?:'
        # Major titles (H1)
        r'CAPÍTULO\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|'
        r'TÍTULO\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|'
        r'PARTE\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|'
        # Strategic lines (H2/H3)
        r'Línea\s+[Ee]stratégica\s*[IVX\d]*(?:\.|:)?|'
        r'Eje\s+[Ee]stratégico\s*[IVX\d]*(?:\.|:)?|'
        r'Pilar\s*[IVX\d]*(?:\.|:)?|'
        # Sectoral components (H3/H4)
        r'Sector:\s*[\w\s]+|'
        r'Programa:\s*[\w\s]+|'
        # Numbered sections
        r'\#{3,5}\s*\d+\.\d+|'  # Markdown headers
        r'\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ]|'  # Decimal numbering
        r'\d+\.\s+[A-ZÁÉÍÓÚÑ]'  # Simple numbering
        r')',
        re.MULTILINE | re.IGNORECASE
    ),
    
    # ============================================================================
    # PRODUCT AND PROJECT CODES - MGA, BPIN, sectoral codes
    # ============================================================================
    "product_codes": re.compile(
        r'(?:'
        r'\b\d{7}\b|'  # 7-digit product codes
        r'Cód\.\s*(?:Producto|Programa|indicador):\s*[\w\-]+|'
        r'BPIN\s*:\s*\d{10,13}|'  # BPIN codes
        r'Código\s+(?:MGA|de\s+Producto):\s*\d+|'
        r'\b[MP][RIP]-\d{3}\b'  # Meta/Programa codes
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # INDICATOR MATRIX HEADERS - Planning matrices
    # ============================================================================
    "indicator_matrix_headers": re.compile(
        r'(?:'
        r'Línea\s+Estratégica|'
        r'Cód\.\s*Programa|'
        r'Cód\.\s*Producto|'
        r'Cód\.\s*indicador|'
        r'Programas\s+presupuestales|'
        r'Indicadores?\s+(?:de\s+)?producto|'
        r'Indicadores?\s+(?:de\s+)?resultado|'
        r'Unidad\s+de\s+medida|'
        r'Línea\s+base|'
        r'Año\s+línea\s+base|'
        r'Meta\s+(?:Total\s+)?(?:Cuatrienio|202[4-7])|'
        r'Meta\s+de\s+(?:Producto|Resultado|Bienestar)|'
        r'Fuente\s+de\s+información|'
        r'Metas\s+de\s+producto'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # PPI (PLAN PLURIANUAL DE INVERSIONES) HEADERS
    # ============================================================================
    "ppi_headers": re.compile(
        r'(?:'
        r'TOTAL\s+202[4-7]|'
        r'Costo\s+Total\s+Cuatrienio|'
        r'Valor\s+total\s+inversión|'
        r'Vigencia\s+202[4-7]|'
        # Funding sources
        r'SGP|Sistema\s+General\s+de\s+Participaciones|'
        r'SGR|Sistema\s+General\s+de\s+Regalías|'
        r'Regalías|'
        r'Recursos\s+Propios|'
        r'Otras\s+Fuentes|'
        r'Fondo\s+subregional|'
        r'Cooperación\s+internacional|'
        # Financial categories
        r'Gestión\s+e\s+inversión|'
        r'Plan\s+Plurianual\s+de\s+Inversiones|'
        r'PPI|POAI'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # CAUSAL CHAIN VOCABULARY - Theory of change language
    # ============================================================================
    "causal_connectors": re.compile(
        r'(?:'
        # Purpose connectors
        r'con\s+el\s+fin\s+de|a\s+través\s+de|mediante|para\s+lograr|'
        r'con\s+el\s+propósito\s+de|con\s+el\s+objetivo\s+de|'
        # Causal connectors
        r'contribuye\s+al\s+logro|cierre\s+de\s+brechas|permite|'
        r'genera|produce|resulta\s+en|'
        r'gracias\s+a|como\s+resultado\s+de|debido\s+a|porque|'
        r'por\s+medio\s+de|permitirá|contribuirá\s+a|'
        # Implementation verbs
        r'implementar|realizar|desarrollar|adelantar|ejecutar|'
        r'contempla\s+actividades|'
        # Transformation language
        r'transformación|desarrollo|mejora|cambio|efecto|impacto'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # DIAGNOSTIC PATTERNS - Problem identification
    # ============================================================================
    "diagnostic_markers": re.compile(
        r'(?:'
        r'diagnóstico|caracterización|análisis\s+situacional|'
        r'línea\s+base|año\s+base|situación\s+inicial|'
        r'brecha|déficit|rezago|carencia|limitación|'
        r'problemática|necesidad|'
        r'Ejes\s+problemáticos|Problemáticas\s+priorizadas|'
        r'brechas\s+territoriales|'
        r'ausencia\s+de|falta\s+de|desactualizado'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # STRATEGIC PATTERNS - Decision and planning language
    # ============================================================================
    "strategic_markers": re.compile(
        r'(?:'
        r'Parte\s+Estratégica|Componente\s+estratégico|'
        r'objetivos?|metas?|indicadores?|'
        r'apuestas|priorización|'
        r'definición\s+de\s+los\s+objetivos|'
        r'alternativas\s+de\s+solución|'
        r'se\s+abordaran\s+en\s+el\s+presente\s+cuatrienio|'
        r'grandes\s+apuestas'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # LEGAL REFERENCES - Colombian legal framework
    # ============================================================================
    "legal_references": re.compile(
        r'(?:'
        r'Ley\s+\d+\s+de\s+\d{4}|'
        r'DECRETO\s+\d+\s+DE\s+\d{4}|'
        r'Resolución\s+\d+\s+de\s+\d{4}|'
        r'Acuerdo\s+(?:Municipal\s+)?(?:No\s+)?\d+\s+de\s+\d{4}|'
        r'Constitución\s+Política|'
        r'Art\.\s*\d+|Artículo\s+\d+|'
        r'Circular\s+conjunta\s+[\d\-]+|'
        r'Estatuto\s+Orgánico'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # TEMPORAL EXPRESSIONS - Time references
    # ============================================================================
    "temporal_expressions": re.compile(
        r'(?:'
        # Periods
        r'cuatrienio|202[4-7]|vigencia\s+202[4-7]|'
        r'período\s+de\s+cuatro\s+años|'
        r'corto\s+plazo|mediano\s+plazo|largo\s+plazo|'
        # Dates
        r'\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|'
        r'\d{2}-\d{2}-\d{4}|'
        # Fiscal references
        r'Marco\s+Fiscal\s+de\s+Mediano\s+Plazo|MFMP|'
        r'POAI|Plan\s+Operativo\s+Anual|'
        r'año\s+fiscal|'
        # Historical references
        r'serie\s+histórica|evolución\s+20\d{2}-20\d{2}|'
        r'tendencia\s+de\s+los\s+últimos|'
        r'vigencia\s+anterior|cuatrienio\s+anterior'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # TERRITORIAL REFERENCES - Geographic scope
    # ============================================================================
    "territorial_references": re.compile(
        r'(?:'
        # Administrative levels
        r'Municipio\s+de\s+[\w\s]+|'
        r'Departamento\s+del\s+Cauca|Gobernación\s+de\s+Cauca|'
        # Territorial types
        r'territorio|urbano|rural|'
        r'cabecera\s+(?:urbana|municipal)|'
        r'corregimiento|vereda|'
        r'centro\s+poblado|'
        # Regional groupings
        r'región\s+(?:Norte|Sur|Centro)\s+del\s+Cauca|'
        r'Alto\s+Patía|'
        r'subregión|'
        # Special zones
        r'PDET|Programas\s+de\s+Desarrollo\s+con\s+Enfoque\s+Territorial|'
        r'zonas?\s+PDET|'
        r'municipios\s+más\s+afectados\s+por\s+el\s+conflicto|'
        # Ethnic territories
        r'Consejo\s+Comunitario|'
        r'resguardo\s+indígena|'
        r'territorios?\s+(?:étnicos?|colectivos?)'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # INSTITUTIONAL ENTITIES - Colombian institutions
    # ============================================================================
    "institutional_entities": re.compile(
        r'(?:'
        # National entities
        r'DNP|Departamento\s+Nacional\s+de\s+Planeación|'
        r'DANE|Departamento\s+Administrativo\s+Nacional\s+de\s+Estadística|'
        r'Ministerio\s+de\s+(?:Salud|Educación|Vivienda|Transporte|Ambiente)|'
        r'Min(?:Salud|Educación|Vivienda|Transporte|Ambiente)|'
        r'Fiscalía|JEP|UBPD|UARIV|'
        r'Banco\s+de\s+la\s+República|'
        r'ANT|Agencia\s+Nacional\s+de\s+Tierras|'
        r'IGAC|'
        # Departmental
        r'Gobernación|'
        r'CAR|CRC|Corporación\s+Autónoma\s+Regional|'
        # Municipal
        r'Alcaldía|Administración\s+Municipal|'
        r'Secretaría\s+de\s+(?:Planeación|Hacienda|Gobierno|Salud|Educación)|'
        r'Consejo\s+Municipal|'
        r'Comisaría\s+de\s+Familia|'
        # Civil society
        r'Junta\s+de\s+Acción\s+Comunal|JAC|'
        r'Mesa\s+de\s+participación'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # FINANCIAL PATTERNS - Budget and costs
    # ============================================================================
    "financial_patterns": re.compile(
        r'(?:'
        # Currency amounts
        r'\$\s*[\d,\.]+(?:\s*(?:millones?|COP))?|'
        r'[\d,\.]+\s*(?:millones?|COP)|'
        # Financial terms
        r'presupuesto|inversión|costo|valor|monto|'
        r'recursos?\s+(?:propios|financieros)|'
        r'asignación\s+de\s+recursos|'
        r'fuentes?\s+de\s+financiación|'
        r'cofinanciación|'
        # Funding mechanisms
        r'crédito|cooperación|transferencia'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # MEASUREMENT UNITS - Indicators and metrics
    # ============================================================================
    "measurement_units": re.compile(
        r'(?:'
        # Rates and percentages
        r'\d+(?:\.\d+)?%|'
        r'\d+\s*por\s+(?:cada\s+)?(?:100\.000|100|mil)|'
        r'tasa\s+de|índice\s+de|razón\s+de|'
        # Quantities
        r'número\s+de|cantidad\s+de|'
        r'kilómetros?|metros?|hectáreas?|'
        r'personas?|hogares?|familias?|'
        r'unidades?\s+productivas?|'
        r'documentos?\s+elaborados?|'
        r'campañas?\s+implementadas?|'
        # Coverage
        r'cobertura|tasa\s+de\s+cobertura|'
        r'población\s+beneficiada|'
        r'beneficiarios?'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # PEACE AND CONFLICT PATTERNS - PDET, RRI, victims
    # ============================================================================
    "peace_patterns": re.compile(
        r'(?:'
        r'construcción\s+de\s+paz|paz\s+territorial|'
        r'Reforma\s+Rural\s+Integral|RRI|'
        r'Plan\s+Marco\s+de\s+Implementación|PMI|'
        r'PDET|PATR|'
        r'víctimas?|reparación|restitución|'
        r'conflicto\s+armado|'
        r'desmovilización|reintegración|DDR|'
        r'excombatientes?|'
        r'memoria\s+histórica|verdad|justicia\s+transicional|'
        r'reconciliación|convivencia'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # PLANNING METHODOLOGY - DNP frameworks
    # ============================================================================
    "methodology_patterns": re.compile(
        r'(?:'
        r'Metodología\s+General\s+Ajustada|MGA|'
        r'cadena\s+de\s+valor|'
        r'Matriz\s+Causal|'
        r'eslabones?\s+(?:clave\s+)?de\s+la\s+cadena|'
        r'SisPT|Sistema\s+de\s+Planificación\s+Territorial|'
        r'TerriData|'
        r'Catálogo\s+de\s+Productos|'
        r'coherencia\s+entre\s+diagnóstico\s+y\s+propuesta|'
        r'articulación\s+lógica'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # SECTORAL PATTERNS - Key policy sectors
    # ============================================================================
    "sectoral_patterns": re.compile(
        r'(?:'
        # Social sectors
        r'Salud\s+Pública|Protección\s+Social|'
        r'Educación|Primera\s+Infancia|'
        r'Vivienda|Agua\s+Potable|Saneamiento\s+Básico|'
        # Economic sectors
        r'Agricultura|Desarrollo\s+Rural|'
        r'Infraestructura|Vías|Transporte|'
        r'Empleo|Trabajo\s+Decente|'
        # Environmental
        r'Medio\s+Ambiente|Gestión\s+Ambiental|'
        r'Cambio\s+Climático|'
        r'Gestión\s+del\s+Riesgo|'
        # Justice and governance
        r'Justicia|Seguridad|Convivencia|'
        r'Fortalecimiento\s+Institucional|'
        r'Participación\s+Ciudadana'
        r')',
        re.IGNORECASE
    ),
    
    # ============================================================================
    # TRANSITION PHRASES - Content flow markers
    # ============================================================================
    "transition_phrases": re.compile(
        r'(?:'
        r'se\s+(?:describe|presenta|enuncia)n?\s+a\s+continuación|'
        r'dando\s+continuidad\s+al\s+proceso|'
        r'a\s+continuación\s+se\s+(?:dan?\s+a\s+conocer|presenta)|'
        r'por\s+lo\s+tanto|'
        r'en\s+este\s+sentido|'
        r'de\s+esta\s+manera|'
        r'así\s+mismo|'
        r'la\s+tabla\s+siguiente\s+presenta|'
        r'se\s+presenta\s+de\s+forma\s+detallada'
        r')',
        re.IGNORECASE
    )
}

# ============================================================================
# CAUSAL CHAIN VOCABULARY - Exhaustive 5-Link Value Chain (DNP Methodology)
# ============================================================================
# Based on DNP/SisPT territorial planning methodology and MGA framework
# Organized by: Insumos → Actividades → Productos → Resultados → Impactos
# 
# NOTE: Causal connectors (con el fin de, a través de, etc.) are in 
# PDT_PATTERNS["causal_connectors"] as regex. This list contains only
# dimension-specific vocabulary for each value chain link.
# ============================================================================

CAUSAL_CHAIN_VOCABULARY = [
    # ========================================================================
    # 1. INSUMOS (INPUT) - Recursos iniciales movilizados
    # ========================================================================
    # Financial Resources
    "recursos financieros", "fondos", "apropiaciones", "recursos propios",
    "recursos tributarios", "recursos no tributarios",
    "SGP", "Sistema General de Participaciones",
    "SGR", "Sistema General de Regalías",
    "asignaciones directas", "inversión local", "inversión regional",
    "cofinanciación", "cooperación", "crédito", "obras por impuestos",
    "Plan Plurianual de Inversiones", "PPI",
    "matriz de costeo", "ingresos proyectados",
    "Marco Fiscal de Mediano Plazo", "MFMP",
    
    # Human Resources
    "recursos humanos", "personal de planta", "personal técnico",
    "personal especializado", "personal capacitado",
    "talento humano", "MIPG",
    "estructura administrativa", "diagnóstico institucional",
    "requerimientos de personal", "capacidad institucional",
    
    # Material and Capital Resources
    "recursos materiales", "recursos de capital",
    "infraestructura existente", "equipos", "tecnología",
    "TIC", "sistemas de información", "terrenos",
    "inventario de equipamientos", "dotación",
    "infraestructura precaria", "necesidades de mejora",
    
    # ========================================================================
    # 2. ACTIVIDADES (PROCESS) - Procesos y operaciones
    # ========================================================================
    # Process Types
    "procesos", "operaciones", "actividades",
    "talleres", "foros", "jornadas",
    "implementación de estrategias", "seguimiento",
    "articulación interinstitucional", "coordinación",
    "diseño de rutas", "formulación de políticas",
    "reuniones", "mesas de diálogo", "estudios",
    
    # Action Verbs (specific to activities, not general connectors)
    "gestión de proyectos", "fortalecer", "apoyo", "asistencia",
    
    # Documentation
    "cronogramas", "fechas de inicio", "fechas de fin",
    "avance físico", "avance financiero",
    "reportes de supervisión", "desarrollo de procesos",
    "Plan Operativo Anual de Inversiones", "POAI",
    "Plan de Acción Institucional", "PAI",
    
    # ========================================================================
    # 3. PRODUCTOS (OUTPUT) - Bienes y servicios entregados
    # ========================================================================
    # Tangible Goods
    "bienes tangibles", "infraestructura construida",
    "hospitales construidos", "placa huella construida",
    "dotaciones entregadas", "ambientes de aprendizaje dotados",
    "bancos de maquinaria dotados", "equipamiento instalado",
    "viviendas construidas", "viviendas mejoradas",
    "hogares beneficiados",
    
    # Intangible Services/Products
    "servicios", "productos intangibles",
    "asistencia técnica brindada", "capacitaciones realizadas",
    "personas capacitadas", "documentos elaborados",
    "plan formulado", "casos atendidos",
    "personas asistidas", "lineamientos técnicos",
    
    # Measurement
    "Código MGA", "código de producto",
    "indicador de producto", "unidad de medida",
    "metas de producto", "número", "porcentaje",
    "matriz de metas", "componente estratégico",
    "Catálogo de Productos",
    
    # ========================================================================
    # 4. RESULTADOS (OUTCOME) - Efectos directos sobre población objetivo
    # ========================================================================
    # Social Improvements
    "mejoras en indicadores sociales",
    "tasa de cobertura incrementada",
    "reducción de la tasa de deserción",
    "reducción de la pobreza multidimensional", "IPM",
    "aumento de la percepción de seguridad",
    "reducción de la informalidad",
    "tasa de mortalidad infantil",
    "tasa bruta de natalidad",
    "valor agregado por actividades económicas",
    
    # Measurable Effects
    "efectos directos", "efectos inmediatos",
    "cierre de brechas sociales",
    "mejora en la calidad de vida",
    "mayor acceso a servicios",
    "población con acceso incrementado",
    "fortalecimiento del tejido social",
    
    # Indicators
    "indicador de resultado", "IR",
    "línea base", "meta", "meta cuatrienio",
    "matriz de indicadores de resultado",
    "cambios en percepción", "cambios en conocimiento",
    "cambios en condiciones de bienestar",
    
    # ========================================================================
    # 5. IMPACTOS - Efectos a largo plazo atribuibles
    # ========================================================================
    # Structural Transformation
    "transformación estructural",
    "consolidación de la paz estable y duradera",
    "superación de la pobreza",
    "desarrollo humano integral",
    "ruptura de ciclos de violencia",
    "equidad y justicia social",
    "justicia ambiental",
    "transformación del campo",
    
    # Strategic Alignment
    "alineación con marcos globales",
    "Objetivos de Desarrollo Sostenible", "ODS",
    "Acuerdo de Paz", "PDET",
    "Plan Nacional de Desarrollo", "PND",
    "Plan de Desarrollo Departamental", "PDD",
    "visión", "misión", "fundamentos conceptuales",
    "ejes estratégicos", "propósitos fundamentales",
    
    # Long-term Vision
    "efectos a largo plazo",
    "exclusivamente atribuibles",
    "desarrollo sostenible",
    "paz territorial",
    "potencial transformador",
    "visión de largo plazo",
    "cambio significativo",
    
    # ========================================================================
    # DIAGNOSTIC & STRATEGIC TERMS (not in regex patterns)
    # ========================================================================
    "diagnóstico", "caracterización", "análisis situacional",
    "año base", "situación inicial",
    "brecha", "déficit", "rezago", "carencia", "limitación",
    "problemática", "necesidad",
    "articulación", "concertación",
    "coherencia entre diagnóstico y propuesta",
    "articulación lógica",
    "cadena de valor", "matriz causal",
    "eslabones de la cadena",
    "Metodología General Ajustada", "MGA",
    
    # ========================================================================
    # VERIFICATION SOURCES - Where to find evidence in PDT
    # ========================================================================
    "diagnóstico sectorial",
    "capítulo estratégico",
    "programas y proyectos",
    "matriz de metas e indicadores",
    "SisPT", "Sistema de Planificación Territorial",
    "TerriData",
    "tablas de alineación estratégica"
]

COLOMBIAN_ENTITIES = {
    "DNP": "Departamento Nacional de Planeación",
    "DANE": "Departamento Administrativo Nacional de Estadística",
    "MinSalud": "Ministerio de Salud y Protección Social",
    "MinEducación": "Ministerio de Educación Nacional",
    "MinVivienda": "Ministerio de Vivienda, Ciudad y Territorio",
    "SIVIGILA": "Sistema de Vigilancia en Salud Pública",
    "SISPRO": "Sistema Integral de Información de la Protección Social",
    "SIMAT": "Sistema Integrado de Matrícula",
    "CAR": "Corporación Autónoma Regional",
    "CRC": "Corporación Autónoma Regional del Cauca",
    "Gobernación": "Gobernación Departamental",
    "Alcaldía": "Alcaldía Municipal",
    "Secretaría": "Secretaría"
}

ALIGNMENT_THRESHOLD = (MICRO_LEVELS["ACEPTABLE"] + MICRO_LEVELS["BUENO"]) / 2
RISK_THRESHOLDS = {
    "excellent": 1 - MICRO_LEVELS["EXCELENTE"],
    "good": 1 - MICRO_LEVELS["BUENO"],
    "acceptable": 1 - MICRO_LEVELS["ACEPTABLE"]
}

# Legacy constants for backward compatibility
DEFAULT_CONFIG_FILE = "config.yaml"
EXTRACTION_REPORT_SUFFIX = "_extraction_confidence_report.json"
CAUSAL_MODEL_SUFFIX = "_causal_model.json"
DNP_REPORT_SUFFIX = "_dnp_compliance_report.txt"

# Type definitions
NodeType = Literal["programa", "producto", "resultado", "impacto"]
RigorStatus = Literal["fuerte", "débil", "sin_evaluar"]
TestType = Literal["hoop_test", "smoking_gun", "doubly_decisive", "straw_in_wind"]
DynamicsType = Literal["suma", "decreciente", "constante", "indefinido"]

# ============================================================================
# BEACH THEORETICAL PRIMITIVES - Added to existing code
# ============================================================================

class BeachEvidentialTest:
    """
    Derek Beach evidential tests implementation (Beach & Pedersen 2019: Ch 5).

    FOUR-FOLD TYPOLOGY calibrated by necessity (N) and sufficiency (S):

    HOOP TEST [N: High, S: Low]:
    - Fail → ELIMINATES hypothesis (definitive knock-out)
    - Pass → Hypothesis survives but not proven
    - Example: "Responsible entity must be documented"

    SMOKING GUN [N: Low, S: High]:
    - Pass → Strongly confirms hypothesis
    - Fail → Doesn't eliminate (could be false negative)
    - Example: "Unique policy instrument only used for this mechanism"

    DOUBLY DECISIVE [N: High, S: High]:
    - Pass → Conclusively confirms
    - Fail → Conclusively eliminates
    - Extremely rare in social science

    STRAW-IN-WIND [N: Low, S: Low]:
    - Pass/Fail → Marginal confidence change
    - Used for preliminary screening

    REFERENCE: Beach & Pedersen (2019), pp 117-126
    """

    @staticmethod
    def classify_test(necessity: float, sufficiency: float) -> TestType:
        """
        Classify evidential test type based on necessity and sufficiency.

        Beach calibration:
        - Necessity > 0.7 → High necessity
        - Sufficiency > 0.7 → High sufficiency
        """
        high_n = necessity > 0.7
        high_s = sufficiency > 0.7

        if high_n and high_s:
            return "doubly_decisive"
        elif high_n and not high_s:
            return "hoop_test"
        elif not high_n and high_s:
            return "smoking_gun"
        else:
            return "straw_in_wind"

    @staticmethod
    def apply_test_logic(test_type: TestType, evidence_found: bool,
                         prior: float, bayes_factor: float) -> tuple[float, str]:
        """
        Apply Beach test-specific logic to Bayesian updating.

        CRITICAL RULES:
        1. Hoop Test FAIL → posterior ≈ 0 (knock-out)
        2. Smoking Gun PASS → multiply prior by large BF (>10)
        3. Doubly Decisive → extreme updates (BF > 100 or < 0.01)

        Returns: (posterior_confidence, interpretation)
        """
        if test_type == "hoop_test":
            if not evidence_found:
                # KNOCK-OUT per Beach: "hypothesis must jump through hoop"
                return 0.01, "HOOP_TEST_FAILURE: Hypothesis eliminated"
            else:
                # Pass: necessary condition met, use standard Bayesian
                posterior = min(0.95, prior * bayes_factor)
                return posterior, "HOOP_TEST_PASSED: Hypothesis survives, not proven"

        elif test_type == "smoking_gun":
            if evidence_found:
                # Strong confirmation: unique evidence found
                posterior = min(0.98, prior * max(bayes_factor, 10.0))
                return posterior, "SMOKING_GUN_FOUND: Strong confirmation"
            else:
                # Doesn't eliminate: could be false negative
                posterior = prior * 0.9  # slight penalty
                return posterior, "SMOKING_GUN_NOT_FOUND: Doesn't eliminate"

        elif test_type == "doubly_decisive":
            if evidence_found:
                return 0.99, "DOUBLY_DECISIVE_CONFIRMED: Conclusive"
            else:
                return 0.01, "DOUBLY_DECISIVE_ELIMINATED: Conclusive"

        # Marginal update only
        elif evidence_found:
            posterior = min(0.95, prior * min(bayes_factor, 2.0))
            return posterior, "STRAW_IN_WIND: Weak support"
        else:
            posterior = max(0.05, prior / min(bayes_factor, 2.0))
            return posterior, "STRAW_IN_WIND: Weak disconfirmation"

# ============================================================================
# Custom Exceptions - Structured Error Semantics
# ============================================================================

class CDAFException(Exception):
    """Base exception for CDAF framework with structured payloads"""

    def __init__(self, message: str, details: dict[str, Any] | None = None,
                 stage: str | None = None, recoverable: bool = False) -> None:
        self.message = message
        self.details = details or {}
        self.stage = stage
        self.recoverable = recoverable
        super().__init__(self._format_message())

    
    def _format_message(self) -> str:
        """Format error message with structured information"""
        parts = ["[CDAF Error]"]
        if self.stage:
            parts.append(f"[Stage: {self.stage}]")
        parts.append(self.message)
        if self.details:
            parts.append(f"Details: {json.dumps(self.details, indent=2)}")
        return " ".join(parts)

    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to structured dictionary"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details,
            'stage': self.stage,
            'recoverable': self.recoverable
        }

class CDAFValidationError(CDAFException):
    """Configuration or data validation error"""
    pass

class CDAFProcessingError(CDAFException):
    """Error during document processing"""
    pass

class CDAFBayesianError(CDAFException):
    """Error during Bayesian inference"""
    pass

class CDAFConfigError(CDAFException):
    """Configuration loading or validation error"""
    pass

# ============================================================================
# Pydantic Configuration Models - Schema Validation at Load Time
# ============================================================================

class BayesianThresholdsConfig(BaseModel):
    """Bayesian inference thresholds configuration"""
    kl_divergence: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="KL divergence threshold for convergence"
    )
    convergence_min_evidence: int = Field(
        default=2,
        ge=1,
        description="Minimum evidence count for convergence check"
    )
    prior_alpha: float = Field(
        default=2.0,
        ge=0.1,
        description="Default alpha parameter for Beta prior"
    )
    prior_beta: float = Field(
        default=2.0,
        ge=0.1,
        description="Default beta parameter for Beta prior"
    )
    laplace_smoothing: float = Field(
        default=1.0,
        ge=0.0,
        description="Laplace smoothing parameter"
    )

class CapacityComposition(BaseModel):
    """
    Capacity Composition Vector (CVC) model.
    Replaces the legacy, mutually exclusive MechanismTypeConfig.
    Represents the multidimensional nature of a causal mechanism.
    """
    analytical: float = Field(
        default=0.25, ge=0.0, le=1.0,
        description="Analytical Capacity (Técnico): Ability to use knowledge, analysis, and methods for design."
    )
    operational: float = Field(
        default=0.30, ge=0.0, le=1.0,
        description="Operational Capacity (Administrativo): Ability to align resources with actions and manage implementation."
    )
    financial: float = Field(
        default=0.20, ge=0.0, le=1.0,
        description="Financial Capacity (Financiero): Availability of funds and budget."
    )
    political: float = Field(
        default=0.15, ge=0.0, le=1.0,
        description="Political Capacity (Político): Derived metric of consistency and systemic risk of A, O, and F."
    )

    @validator('*', pre=True, always=True)
    def check_sum_to_one(cls, v, values):
        """Validate that probabilities sum to approximately 1.0"""
        if len(values) == 3:  # All other fields loaded
            total = sum(values.values()) + v
            if abs(total - 1.0) > 0.01:
                # Adjust the last value to ensure the sum is 1.0
                # This is a soft normalization for convenience
                v = 1.0 - sum(values.values())
        return v

class PerformanceConfig(BaseModel):
    """Performance and optimization settings"""
    enable_vectorized_ops: bool = Field(
        default=True,
        description="Use vectorized numpy operations where possible"
    )
    enable_async_processing: bool = Field(
        default=False,
        description="Enable async processing for large PDFs (experimental)"
    )
    max_context_length: int = Field(
        default=1000,
        ge=100,
        description="Maximum context length for spaCy processing"
    )
    cache_embeddings: bool = Field(
        default=True,
        description="Cache spaCy embeddings for reuse"
    )

class SelfReflectionConfig(BaseModel):
    """Self-reflective learning configuration"""
    enable_prior_learning: bool = Field(
        default=False,
        description="Enable learning from audit feedback to update priors"
    )
    feedback_weight: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Weight for feedback in prior updates (0=ignore, 1=full)"
    )
    prior_history_path: str | None = Field(
        default=None,
        description="Path to save/load historical priors"
    )
    min_documents_for_learning: int = Field(
        default=5,
        ge=1,
        description="Minimum documents before applying learned priors"
    )

class CDAFConfigSchema(BaseModel):
    """Complete CDAF configuration schema with validation"""
    patterns: dict[str, str] = Field(
        description="Regex patterns for document parsing"
    )
    lexicons: dict[str, Any] = Field(
        description="Lexicons for causal logic, classification, etc."
    )
    entity_aliases: dict[str, str] = Field(
        description="Entity name aliases and mappings"
    )
    verb_sequences: dict[str, int] = Field(
        description="Verb sequence ordering for temporal coherence"
    )
    bayesian_thresholds: BayesianThresholdsConfig = Field(
        default_factory=BayesianThresholdsConfig,
        description="Bayesian inference thresholds"
    )
    capacity_composition_priors: CapacityComposition = Field(
        default_factory=CapacityComposition,
        description="Prior probabilities for CVC dimensions"
    )
    performance: PerformanceConfig = Field(
        default_factory=PerformanceConfig,
        description="Performance and optimization settings"
    )
    self_reflection: SelfReflectionConfig = Field(
        default_factory=SelfReflectionConfig,
        description="Self-reflective learning configuration"
    )

    class Config:
        extra = 'allow'  # Allow additional fields for extensibility

class GoalClassification(NamedTuple):
    """Classification structure for goals"""
    type: NodeType
    dynamics: DynamicsType
    test_type: TestType
    confidence: float

class EntityActivity(NamedTuple):
    """
    Entity-Activity tuple for mechanism parts (Beach 2016).

    BEACH DEFINITION:
    "A mechanism part consists of an entity (organization, actor, structure)
    engaging in an activity that transmits causal forces" (Beach 2016: 465)

    This is the FUNDAMENTAL UNIT of mechanistic evidence in Process Tracing.
    """
    entity: str
    activity: str
    verb_lemma: str
    confidence: float

class CausalLink(TypedDict):
    """Structure for causal links in the graph"""
    source: str
    target: str
    logic: str
    strength: float
    evidence: list[str]
    posterior_mean: float | None
    posterior_std: float | None
    kl_divergence: float | None
    converged: bool | None

class AuditResult(TypedDict):
    """Audit result structure"""
    passed: bool
    warnings: list[str]
    errors: list[str]
    recommendations: list[str]

@dataclass
class MetaNode:
    """Comprehensive node structure for goals/metas"""
    id: str
    text: str
    type: NodeType
    baseline: float | str | None = None
    target: float | str | None = None
    unit: str | None = None
    responsible_entity: str | None = None
    entity_activity: EntityActivity | None = None
    financial_allocation: float | None = None
    unit_cost: float | None = None
    rigor_status: RigorStatus = "sin_evaluar"
    dynamics: DynamicsType = "indefinido"
    test_type: TestType = "straw_in_wind"
    contextual_risks: list[str] = field(default_factory=list)
    causal_justification: list[str] = field(default_factory=list)
    audit_flags: list[str] = field(default_factory=list)
    confidence_score: float = 0.0

class ConfigLoader:
    """External configuration management with Pydantic schema validation"""

    def __init__(self, config_path: Path) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_path = config_path
        self.config: dict[str, Any] = {}
        self.validated_config: CDAFConfigSchema | None = None
        # HARMONIC FRONT 4: Track uncertainty over iterations
        self._uncertainty_history: list[float] = []
        self._load_config()
        self._validate_config()
        self._load_uncertainty_history()

    
    def _load_config(self) -> None:
        """Load YAML configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Configuración cargada desde {self.config_path}")
        except FileNotFoundError:
            self.logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
            self._load_default_config()
        except Exception as e:
            raise CDAFConfigError(
                "Error cargando configuración",
                details={'path': str(self.config_path), 'error': str(e)},
                stage="config_load",
                recoverable=True
            )

    
    def _load_default_config(self) -> None:
        """Load default configuration with PDT/PDM-aware patterns"""
        self.config = {
            'patterns': {
                'section_titles': PDT_PATTERNS["section_delimiters"].pattern,
                'goal_codes': PDT_PATTERNS["product_codes"].pattern,
                'numeric_formats': r'[\d,]+(?:\.\d+)?%?|por\s+100\.000',
                'table_headers': PDT_PATTERNS["indicator_matrix_headers"].pattern,
                'financial_headers': PDT_PATTERNS["ppi_headers"].pattern
            },
            'lexicons': {
                'causal_logic': CAUSAL_CHAIN_VOCABULARY,
                'goal_classification': {
                    'tasa': 'decreciente',
                    'índice': 'constante',
                    'número': 'suma',
                    'porcentaje': 'constante',
                    'cantidad': 'suma',
                    'cobertura': 'suma',
                    'por 100.000': 'tasa'
                },
                'contextual_factors': [
                    'riesgo', 'amenaza', 'obstáculo', 'limitación',
                    'restricción', 'desafío', 'brecha', 'déficit',
                    'vulnerabilidad', 'hipótesis alternativa'
                ],
                'administrative_keywords': [
                    'gestión', 'administración', 'coordinación', 'regulación',
                    'normativa', 'institucional', 'gobernanza', 'reglamento',
                    'decreto', 'resolución', 'acuerdo'
                ]
            },
            'entity_aliases': COLOMBIAN_ENTITIES,
            'verb_sequences': {
                'diagnosticar': 1,
                'identificar': 2,
                'analizar': 3,
                'diseñar': 4,
                'planificar': 5,
                'implementar': 6,
                'ejecutar': 7,
                'monitorear': 8,
                'evaluar': 9
            },
            'bayesian_thresholds': {
                'kl_divergence': 0.01,
                'convergence_min_evidence': 2,
                'prior_alpha': 2.0,
                'prior_beta': 2.0,
                'laplace_smoothing': 1.0
            },
            'capacity_composition_priors': {
                'analytical': 0.40,
                'operational': 0.30,
                'financial': 0.20,
                'political': 0.10
            },
            'performance': {
                'enable_vectorized_ops': True,
                'enable_async_processing': False,
                'max_context_length': 1000,
                'cache_embeddings': True
            },
            'self_reflection': {
                'enable_prior_learning': False,
                'feedback_weight': 0.1,
                'prior_history_path': None,
                'min_documents_for_learning': 5
            }
        }
        self.logger.warning("Usando configuración por defecto PDT/PDM-aware")

    
    def _validate_config(self) -> None:
        """Validate configuration structure using Pydantic schema"""
        try:
            # Rename for compatibility
            if 'mechanism_type_priors' in self.config:
                self.config['capacity_composition_priors'] = self.config.pop('mechanism_type_priors')
                # Map old keys to new keys if necessary
                mapping = {'tecnico': 'analytical', 'administrativo': 'operational', 'financiero': 'financial', 'politico': 'political'}
                if not all(k in self.config['capacity_composition_priors'] for k in mapping.values()):
                     self.config['capacity_composition_priors'] = {mapping.get(k, k): v for k, v in self.config['capacity_composition_priors'].items() if k not in ['mixto']}

            # Validate with Pydantic schema
            self.validated_config = CDAFConfigSchema(**self.config)
            self.logger.info("✓ Configuración validada exitosamente con esquema Pydantic")
        except ValidationError as e:
            error_details = {
                'validation_errors': [
                    {
                        'field': '.'.join(str(x) for x in err['loc']),
                        'error': err['msg'],
                        'type': err['type']
                    }
                    for err in e.errors()
                ]
            }
            raise CDAFValidationError(
                "Configuración inválida - errores de esquema",
                details=error_details,
                stage="config_validation",
                recoverable=False
            )

        # Legacy validation for required sections
        required_sections = ['patterns', 'lexicons', 'entity_aliases', 'verb_sequences']
        for section in required_sections:
            if section not in self.config:
                self.logger.warning(f"Sección faltante en configuración: {section}")
                self.config[section] = {}

    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    
    def get_bayesian_threshold(self, key: str) -> float:
        """Get Bayesian threshold with type safety"""
        if self.validated_config:
            return getattr(self.validated_config.bayesian_thresholds, key)
        return self.get(f'bayesian_thresholds.{key}', 0.01)

    
    def get_capacity_prior(self, capacity_dimension: str) -> float:
        """Get capacity dimension prior probability with type safety"""
        if self.validated_config:
            return getattr(self.validated_config.capacity_composition_priors, capacity_dimension, 0.0)
        return self.get(f'capacity_composition_priors.{capacity_dimension}', 0.0)

    
    def get_performance_setting(self, key: str) -> Any:
        """Get performance setting with type safety"""
        if self.validated_config:
            return getattr(self.validated_config.performance, key)
        return self.get(f'performance.{key}')

    
    def update_priors_from_feedback(self, feedback_data: dict[str, Any]) -> None:
        """
        Self-reflective loop: Update priors based on audit feedback
        Implements frontier paradigm of learning from results

        HARMONIC FRONT 4 ENHANCEMENT:
        - Applies penalties to mechanism types with implementation_failure flags
        - Heavily penalizes "miracle" mechanisms failing necessity/sufficiency tests
        - Ensures mean mech_uncertainty decreases by ≥5% over iterations
        """
        if not self.validated_config or not self.validated_config.self_reflection.enable_prior_learning:
            self.logger.debug("Prior learning disabled")
            return

        feedback_weight = self.validated_config.self_reflection.feedback_weight

        # Track initial priors for uncertainty measurement
        initial_priors = self.validated_config.capacity_composition_priors.dict()


        # Update mechanism type priors based on observed frequencies
        if 'capacity_frequencies' in feedback_data:
            for cap_type, observed_freq in feedback_data['capacity_frequencies'].items():
                if hasattr(self.validated_config.capacity_composition_priors, cap_type):
                    current_prior = getattr(self.validated_config.capacity_composition_priors, cap_type)
                    # Weighted update: new_prior = (1-weight)*current + weight*observed
                    updated_prior = (1 - feedback_weight) * current_prior + feedback_weight * observed_freq
                    setattr(self.validated_config.capacity_composition_priors, cap_type, updated_prior)
                    self.config['capacity_composition_priors'][cap_type] = updated_prior

        # NEW: Apply penalty factors for failing mechanism types
        if 'penalty_factors' in feedback_data:
            penalty_weight = feedback_weight * 1.5  # Heavier penalty than positive feedback
            for cap_type, penalty_factor in feedback_data['penalty_factors'].items():
                if hasattr(self.validated_config.capacity_composition_priors, cap_type):
                    current_prior = getattr(self.validated_config.capacity_composition_priors, cap_type)
                    # Apply penalty: reduce prior for frequently failing types
                    penalized_prior = current_prior * penalty_factor
                    # Blend with current
                    updated_prior = (1 - penalty_weight) * current_prior + penalty_weight * penalized_prior
                    setattr(self.validated_config.capacity_composition_priors, cap_type, updated_prior)
                    self.config['capacity_composition_priors'][cap_type] = updated_prior
                    self.logger.info(f"Applied penalty to {cap_type}: {current_prior:.4f} -> {updated_prior:.4f}")

        # NEW: Heavy penalty for "miracle" mechanisms failing necessity/sufficiency
        test_failures = feedback_data.get('test_failures', {})
        if test_failures.get('necessity_failures', 0) > 0 or test_failures.get('sufficiency_failures', 0) > 0:
            miracle_types = ['political']
            miracle_penalty = 0.85
            for cap_type in miracle_types:
                if hasattr(self.validated_config.capacity_composition_priors, cap_type):
                    current_prior = getattr(self.validated_config.capacity_composition_priors, cap_type)
                    updated_prior = current_prior * miracle_penalty
                    setattr(self.validated_config.capacity_composition_priors, cap_type, updated_prior)
                    self.config['capacity_composition_priors'][cap_type] = updated_prior
                    self.logger.info(
                        f"Miracle mechanism penalty for {cap_type}: {current_prior:.4f} -> {updated_prior:.4f}")

        # Renormalize to ensure priors sum to 1.0
        current_priors = self.validated_config.capacity_composition_priors.dict()
        total_prior = sum(current_priors.values())
        if total_prior > 0:
            for attr, value in current_priors.items():
                normalized = value / total_prior
                setattr(self.validated_config.capacity_composition_priors, attr, normalized)
                self.config['capacity_composition_priors'][attr] = normalized

        # Calculate uncertainty reduction for quality criteria
        final_priors = self.validated_config.capacity_composition_priors.dict()

        # Calculate entropy as uncertainty measure
        initial_entropy = -sum(p * np.log(p + 1e-10) for p in initial_priors.values() if p > 0)
        final_entropy = -sum(p * np.log(p + 1e-10) for p in final_priors.values() if p > 0)
        uncertainty_reduction = ((initial_entropy - final_entropy) / max(initial_entropy, 1e-10)) * 100

        self.logger.info(f"Uncertainty reduction: {uncertainty_reduction:.2f}%")

        # Save updated priors if history path configured
        if self.validated_config.self_reflection.prior_history_path:
            self._save_prior_history(feedback_data, uncertainty_reduction)

        self.logger.info(f"Priors actualizados con peso de retroalimentación {feedback_weight}")

    
    def _save_prior_history(self, feedback_data: dict[str, Any] | None = None,
                            uncertainty_reduction: float | None = None) -> None:
        """
        Save prior history for learning across documents

        HARMONIC FRONT 4 ENHANCEMENT:
        - Tracks uncertainty reduction over iterations
        - Records penalty applications and test failures
        """
        if not self.validated_config or not self.validated_config.self_reflection.prior_history_path:
            return

        try:
            history_path = Path(self.validated_config.self_reflection.prior_history_path)
            history_path.parent.mkdir(parents=True, exist_ok=True)

            # Load existing history if available
            history_records = []
            if history_path.exists():
                try:
                    with open(history_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    if isinstance(existing_data, list):
                        history_records = existing_data
                    elif isinstance(existing_data, dict) and 'history' in existing_data:
                        history_records = existing_data['history']
                except json.JSONDecodeError:
                    self.logger.warning("Existing history file corrupted, starting fresh")

            # Create new record
            history_record = {
                'capacity_composition_priors': self.config.get('capacity_composition_priors', {}),
                'timestamp': pd.Timestamp.now().isoformat(),
                'version': '2.1'
            }

            # Add feedback metrics if available
            if feedback_data:
                history_record['audit_quality'] = feedback_data.get('audit_quality', {})
                history_record['test_failures'] = feedback_data.get('test_failures', {})
                history_record['penalty_factors'] = feedback_data.get('penalty_factors', {})

            if uncertainty_reduction is not None:
                history_record['uncertainty_reduction_percent'] = uncertainty_reduction

            history_records.append(history_record)

            # Save complete history
            history_data = {
                'version': '2.1',
                'harmonic_front': 4,
                'last_updated': pd.Timestamp.now().isoformat(),
                'total_iterations': len(history_records),
                'history': history_records
            }

            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)

            self.logger.info(f"Historial de priors guardado en {history_path} (iteración {len(history_records)})")
        except Exception as e:
            self.logger.warning(f"Error guardando historial de priors: {e}")

    
    def _load_uncertainty_history(self) -> None:
        """
        Load historical uncertainty measurements

        HARMONIC FRONT 4: Required for tracking ≥5% reduction over 10 iterations
        """
        if not self.validated_config or not self.validated_config.self_reflection.prior_history_path:
            return

        try:
            history_path = Path(self.validated_config.self_reflection.prior_history_path)
            if history_path.exists():
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                if isinstance(history_data, dict) and 'history' in history_data:
                    # Extract uncertainty from each record
                    for record in history_data['history']:
                        if 'uncertainty_reduction_percent' in record:
                            self._uncertainty_history.append(
                                record['uncertainty_reduction_percent']
                            )
                self.logger.info(f"Loaded {len(self._uncertainty_history)} uncertainty measurements")
        except Exception as e:
            self.logger.warning(f"Could not load uncertainty history: {e}")

    
    def check_uncertainty_reduction_criterion(self, current_uncertainty: float) -> dict[str, Any]:
        """
        Check if mean capacity composition uncertainty has decreased ≥5% over 10 iterations

        HARMONIC FRONT 4 QUALITY CRITERIA:
        Success verified if mean mech_uncertainty decreases by ≥5% over 10 sequential PDM analyses
        """
        self._uncertainty_history.append(current_uncertainty)

        # Keep only last 10 iterations
        recent_history = self._uncertainty_history[-10:]

        result = {
            'current_uncertainty': current_uncertainty,
            'iterations_tracked': len(recent_history),
            'criterion_met': False,
            'reduction_percent': 0.0,
            'status': 'insufficient_data'
        }

        if len(recent_history) >= 10:
            initial_uncertainty = recent_history[0]
            final_uncertainty = recent_history[-1]

            if initial_uncertainty > 0:
                reduction_percent = ((initial_uncertainty - final_uncertainty) / initial_uncertainty) * 100
                result['reduction_percent'] = reduction_percent
                result['criterion_met'] = reduction_percent >= 5.0
                result['status'] = 'success' if result['criterion_met'] else 'needs_improvement'

                self.logger.info(
                    f"Uncertainty reduction over 10 iterations: {reduction_percent:.2f}% "
                    f"(criterion: ≥5%, met: {result['criterion_met']})"
                )
        else:
            self.logger.info(
                f"Uncertainty tracking: {len(recent_history)}/10 iterations "
                f"(need {10 - len(recent_history)} more for criterion check)"
            )

        return result
...
# The rest of the file remains the same, only the BayesianMechanismInference class and related parts are changed.
...
class BayesianMechanismInference:
    """
    Bayesian inference for causal mechanisms based on the CVC Model.
    Refactored from a discrete type classification to a continuous,
    multi-dimensional capacity vector (CVC) representation.
    The Political Capacity (PC) is a derived metric, adjusted by penalties.
    """

    def __init__(self, config: ConfigLoader, nlp_model: spacy.Language) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.nlp = nlp_model
        # Load verb sequences from config for temporal coherence checks
        self.verb_sequences = self.config.get('verb_sequences', {})
        self.mechanism_sequences = self.config.get('lexicons.mechanism_sequences', {}) # Legacy, may be removed
        self._mean_mechanism_uncertainty = 0.5

    def infer_mechanisms(self, nodes: dict[str, MetaNode], text: str) -> dict[str, dict[str, Any]]:
        """
        Infer the CVC vector for each node and derive the Political Capacity score.
        """
        inferred_mechanisms = {}
        all_uncertainties = []

        for node_id, node in nodes.items():
            if node.type == 'producto':
                context = self._get_node_context(node_id, text)
                observations = self._extract_observations(context)

                # Step 1: Infer the base A-O-F composition vector
                cvc_composition = self._infer_cvc_composition(observations)

                # Step 2: Establish the baseline Political Capacity (PC)
                pc_baseline = self._get_pc_baseline(node)

                # Step 3: Calculate penalties based on analytical/operational deficiencies
                de_rigor_penalty = self._calculate_de_rigor_penalty(node, observations)
                systemic_risk_penalty = self._calculate_systemic_risk_penalty(node, observations)

                # Step 4: Derive the final PC Score
                total_penalty = de_rigor_penalty + systemic_risk_penalty
                final_pc_score = pc_baseline * (1 - total_penalty)

                # Update the CVC vector with the derived PC score
                cvc_composition['political'] = final_pc_score

                # Normalize the final vector to sum to 1
                total_composition = sum(cvc_composition.values())
                if total_composition > 0:
                    final_cvc_vector = {k: v / total_composition for k, v in cvc_composition.items()}
                else:
                    final_cvc_vector = cvc_composition

                # Multi-axial Hoop Test
                necessity_result = self._test_necessity(node, observations, final_cvc_vector)

                # Quantify uncertainty
                uncertainty = self._quantify_uncertainty(final_cvc_vector)
                all_uncertainties.append(uncertainty['total'])

                inferred_mechanisms[node_id] = {
                    'cvc_vector': final_cvc_vector,
                    'pc_score_derived': final_pc_score,
                    'pc_baseline': pc_baseline,
                    'total_penalty': total_penalty,
                    'penalties': {
                        'de_rigor': de_rigor_penalty,
                        'systemic_risk': systemic_risk_penalty
                    },
                    'necessity_test': necessity_result,
                    'uncertainty': uncertainty,
                    'audit_gaps': self._detect_gaps(node, observations, uncertainty)
                }

        if all_uncertainties:
            self._mean_mechanism_uncertainty = float(np.mean(all_uncertainties))

        return inferred_mechanisms

    def _get_node_context(self, node_id: str, text: str) -> str:
        """Extracts the textual context around a node."""
        # Simple implementation: find node_id and get surrounding text
        match = re.search(re.escape(node_id), text, re.IGNORECASE)
        if not match:
            return ""
        start, end = match.span()
        context_start = max(0, start - 500)
        context_end = min(len(text), end + 500)
        return text[context_start:context_end]

    def _extract_observations(self, context: str) -> dict[str, Any]:
        """Extracts relevant features from the text for CVC inference."""
        doc = self.nlp(context)
        verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'GPE']]

        # Simple budget extraction
        budget_match = re.search(r'\$\s*([\d,.]+)', context)
        budget = float(budget_match.group(1).replace(',', '')) if budget_match else 0.0

        return {
            'text': context,
            'verbs': verbs,
            'entities': entities,
            'budget': budget,
            'entity_activity': {'entity': entities[0] if entities else None, 'activity': verbs[0] if verbs else None}
        }

    def _infer_cvc_composition(self, observations: dict[str, Any]) -> dict[str, float]:
        """
        Infers the weights for Analytical, Operational, and Financial capacities.
        Political capacity is derived later.
        """
        scores = {
            'analytical': self.config.get_capacity_prior('analytical'),
            'operational': self.config.get_capacity_prior('operational'),
            'financial': self.config.get_capacity_prior('financial')
        }

        text = observations.get('text', '').lower()
        verbs = observations.get('verbs', [])

        # Analytical score based on keywords
        analytical_kw = ['diseñar', 'diagnosticar', 'analizar', 'planificar', 'evaluar', 'método', 'racionalidad']
        if any(kw in text for kw in analytical_kw) or any(v in analytical_kw for v in verbs):
            scores['analytical'] += 0.2

        # Operational score based on keywords
        operational_kw = ['ejecutar', 'implementar', 'gestionar', 'coordinar', 'logística', 'personal']
        if any(kw in text for kw in operational_kw) or any(v in operational_kw for v in verbs):
            scores['operational'] += 0.2

        # Financial score based on budget
        if observations.get('budget', 0.0) > 0:
            scores['financial'] += 0.3

        # Normalize A-O-F scores
        total = sum(scores.values())
        if total > 0:
            composition = {k: v / total for k, v in scores.items()}
        else:
            composition = scores

        composition['political'] = 0.0 # Placeholder, will be derived
        return composition

    def _get_pc_baseline(self, node: MetaNode) -> float:
        """
        Establishes the initial Political Capacity score based on the axiom
        that an approved plan has a high initial mandate.
        """
        # Axiom: Plan approved by competent authority (Council/Mayor)
        # gives initial capacity to generate a mandate.
        return 0.95

    def _calculate_de_rigor_penalty(self, node: MetaNode, observations: dict[str, Any]) -> float:
        """
        Calculates penalty for analytical and operational deficiencies.
        (Falta de Trazabilidad, Rigor Lógico, Alta Incertidumbre)
        """
        penalty = 0.0

        # Penalty for lack of traceability (missing Entity->Activity)
        if not observations.get('entity_activity', {}).get('entity') or not observations.get('entity_activity', {}).get('activity'):
            penalty += 0.25 # Critical failure of operationalization

        # Penalty for logical sequence violations (e.g., execute before plan)
        # This is a simplified check. A full implementation would use the graph.
        verbs = observations.get('verbs', [])
        if 'ejecutar' in verbs and 'planificar' in verbs:
            if verbs.index('ejecutar') < verbs.index('planificar'):
                penalty += 0.15 # Poor conceptual design

        # Penalty for high uncertainty (ambiguity, opacity)
        uncertainty = self._quantify_uncertainty(self._infer_cvc_composition(observations))
        if uncertainty['total'] > 0.7:
             penalty += 0.10

        return min(penalty, 1.0)

    def _calculate_systemic_risk_penalty(self, node: MetaNode, observations: dict[str, Any]) -> float:
        """
        Calculates penalty for implementation cost and systemic risk.
        (Mecanismo No Necesario, Riesgo de Cascada, Incoherencia de Población)
        """
        penalty = 0.0

        # Penalty for unnecessary mechanism (Placebo)
        # Simplified: check if budget is optional (would need counterfactual_budget_check)
        if "opcional" in observations.get('text', '').lower() and "presupuesto" in observations.get('text', '').lower():
            penalty += 0.20 # High political cost for unnecessary spending

        # Penalty for cascade risk (high risk_score from AGUJA III)
        # Simplified: check for risk keywords. A real implementation would get this from the auditor.
        if "riesgo" in observations.get('text', '').lower() or "frágil" in observations.get('text', '').lower():
            penalty += 0.15 # High future political cost

        # Penalty for target population incoherence
        # Simplified: check for mismatch keywords. A real implementation needs OP-AUDIT-014.
        if "población no alineada" in observations.get('text', '').lower() or "beneficiarios incorrectos" in observations.get('text', '').lower():
            penalty += 0.20 # Reduces political legitimacy

        return min(penalty, 1.0)

    def _test_necessity(self, node: MetaNode, observations: dict[str, Any], cvc_vector: dict[str, float]) -> dict[str, Any]:
        """
        Multi-Axial Hoop Test based on CVC vector weights.
        A mechanism must pass the necessity tests for its required capacity dimensions.
        """
        missing_components = []

        # Analytical Capacity Hoop Test (e.g., D3-Q1/Ficha Técnica)
        if cvc_vector.get('analytical', 0.0) > 0.3:
            if not node.baseline or not node.target:
                missing_components.append('analytical_ficha_tecnica (baseline/meta)')

        # Financial Capacity Hoop Test (e.g., Counterfactual Budget Check)
        if cvc_vector.get('financial', 0.0) > 0.25:
            if observations.get('budget', 0.0) <= 0:
                missing_components.append('financial_budget_allocation')

        # Operational Capacity Hoop Test (Entity->Activity Traceability)
        if cvc_vector.get('operational', 0.0) > 0.35:
            if not observations.get('entity_activity', {}).get('entity') or not observations.get('entity_activity', {}).get('activity'):
                missing_components.append('operational_entity_activity_traceability')

        is_necessary = len(missing_components) == 0

        return {
            'score': 1.0 if is_necessary else 0.0,
            'is_necessary': is_necessary,
            'missing_components': missing_components,
            'hoop_test_passed': is_necessary
        }

    def _quantify_uncertainty(self, cvc_vector: dict[str, float]) -> dict[str, float]:
        """Quantify epistemic uncertainty from the CVC vector distribution."""
        probs = list(cvc_vector.values())
        if not probs or sum(probs) == 0:
            return {'total': 1.0, 'composition_entropy': 1.0}

        entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
        max_entropy = np.log(len(probs))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 1.0

        return {
            'total': normalized_entropy,
            'composition_entropy': normalized_entropy
        }

    def _detect_gaps(self, node: MetaNode, observations: dict[str, Any], uncertainty: dict[str, float]) -> list[dict[str, str]]:
        """Detect documentation gaps based on uncertainty and missing observations."""
        gaps = []

        if uncertainty['total'] > 0.6:
            gaps.append({
                'type': 'high_uncertainty',
                'severity': 'high',
                'message': f"Mecanismo para {node.id} tiene alta incertidumbre ({uncertainty['total']:.2f})",
                'suggestion': "Se requiere más documentación sobre el mecanismo causal (E->A, principios causales)"
            })

        if not observations.get('entity_activity', {}).get('entity'):
            gaps.append({
                'type': 'missing_entity',
                'severity': 'high',
                'message': f"No se especifica entidad responsable para {node.id}",
                'suggestion': "Definir 'Quién' ejecuta la acción."
            })

        if not observations.get('entity_activity', {}).get('activity'):
            gaps.append({
                'type': 'missing_activity',
                'severity': 'high',
                'message': f"No se especifica la actividad para {node.id}",
                'suggestion': "Definir 'Qué' acción se realiza."
            })

        if observations.get('budget', 0.0) <= 0:
            gaps.append({
                'type': 'missing_budget',
                'severity': 'medium',
                'message': f"Sin asignación presupuestaria para {node.id}",
                'suggestion': "Asignar recursos financieros para garantizar la viabilidad."
            })

        return gaps

# ... (The rest of the file continues from here)
...
class CDAFFramework:
...
# In CDAFFramework.__init__
...
        self.pdf_processor = PDFProcessor(self.config, retry_handler=self.retry_handler if retry_enabled else None)
        self.causal_extractor = CausalExtractor(self.config, self.nlp)
        self.mechanism_extractor = MechanismPartExtractor(self.config, self.nlp)
        self.bayesian_mechanism = BayesianMechanismInference(self.config, self.nlp) # This line is already correct
        self.financial_auditor = FinancialAuditor(self.config)
...
# (The rest of the file remains unchanged)
...
