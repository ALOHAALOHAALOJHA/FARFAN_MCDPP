"""
Enhanced Municipal Development Plan Analyzer - Production-Grade Implementation.

This module implements state-of-the-art techniques for comprehensive municipal plan analysis:
- Semantic cubes with knowledge graphs and ontological reasoning
- Multi-dimensional baseline analysis with automated extraction
- Advanced NLP for multimodal text mining and causal discovery
- Real-time monitoring with statistical process control
- Bayesian optimization for resource allocation
- Uncertainty quantification with Monte Carlo methods

Python 3.11+ Compatible Version
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import time
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

# Constants
SAMPLE_MUNICIPAL_PLAN = "sample_municipal_plan.txt"
RANDOM_SEED = 42

# Canonical artifacts
CANONICAL_ROOT = Path("artifacts/plan1")
CG_ROOT = CANONICAL_ROOT / "canonical_ground_truth"
CAL_ROOT = CANONICAL_ROOT / "calibration"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GRACEFUL_DEGRADATION(irreducible): Heavy NLP/ML dependencies availability depends on:
# 1. Installation environment (minimal environments may exclude heavyweight packages)
# 2. Compilation requirements (NumPy requires compilation, may fail on some platforms)
# 3. Additional data downloads (NLTK requires separate corpus downloads)
# 4. Version compatibility constraints (scikit-learn/pandas version conflicts)
# Cannot be resolved statically - package availability is a deployment-time property.
# Severity: QUALITY - Core NLP/ML features unavailable, analysis degrades to basic text processing.
# Usage pattern: Code using these libraries must check `if np is not None:` before use.
try:
    import numpy as np
except ImportError as e:
    logger.warning(f"Missing dependency: {e}")
    np = None

try:
    import pandas as pd
except ImportError as e:
    logger.warning(f"Missing dependency: {e}")
    pd = None

try:
    from sklearn.ensemble import IsolationForest
except ImportError as e:
    logger.warning(f"Missing dependency: {e}")
    IsolationForest = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError as e:
    logger.warning(f"Missing dependency: {e}")
    TfidfVectorizer = None

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize
except ImportError as e:
    logger.warning(f"Missing dependency: {e}")
    sent_tokenize = None
    stopwords = None

# =============================================================================
# CANONICAL CONSTANTS - IMPORT FROM canonical_specs.py
# CANONICAL REFACTORING (2025-12-17): No runtime JSON loading
# ADR: Import frozen constants from single source of truth
# =============================================================================


# DEPRECATED: POLICY_AREAS_CANONICAL hardcoded below
# Migration: Use CANON_POLICY_AREAS from canonical_specs instead
# Historical note: This was extracted from questionnaire_monolith.json and frozen
# Kept for backward compatibility but should import from canonical_specs

POLICY_AREAS_CANONICAL_LEGACY: dict[str, dict[str, Any]] = {
    "PA01": {
        "id": "PA01",
        "name": "Derechos de las mujeres e igualdad de género",
        "cluster_id": "CL02",
        "keywords": [
            "género",
            "mujer",
            "mujeres",
            "igualdad de género",
            "equidad de género",
            "enfoque de género",
            "perspectiva de género",
            "transversalización de género",
            "brecha de género",
            "disparidad de género",
            "discriminación de género",
            "violencia basada en género",
            "VBG",
            "violencia de género",
            "violencia intrafamiliar",
            "VIF",
            "violencia doméstica",
            "violencia sexual",
            "violencia física",
            "violencia psicológica",
            "violencia económica",
            "violencia patrimonial",
            "feminicidio",
            "femicidio",
            "tentativa de feminicidio",
            "acoso sexual",
            "acoso laboral",
            "hostigamiento",
            "violencia obstétrica",
            "violencia institucional",
            "trata de personas",
            "explotación sexual",
            "Secretaría de la Mujer",
            "Consejería de la Mujer",
            "Comisaría de Familia",
            "comisarías",
            "Ley 1257",
            "Ley 1719",
            "Ley 1761",
            "Ley Rosa Elvira Cely",
            "medidas de protección",
            "orden de protección",
            "ruta de atención",
            "protocolo de atención",
            "casas de refugio",
            "casas de acogida",
            "brecha salarial",
            "equidad salarial",
            "igualdad salarial",
            "trabajo no remunerado",
            "carga de cuidado",
            "economía del cuidado",
            "trabajo del cuidado",
            "licencia de maternidad",
            "lactancia materna",
            "emprendimiento femenino",
            "empresarias",
            "empoderamiento económico",
            "autonomía económica",
            "participación política de las mujeres",
            "liderazgo femenino",
            "lideresas",
            "lideresa",
            "cuotas de género",
            "paridad",
            "equidad electoral",
            "violencia política",
            "violencia política contra las mujeres",
            "representación femenina",
            "concejalas",
            "diputadas",
            "salud sexual",
            "salud reproductiva",
            "SSR",
            "derechos reproductivos",
            "planificación familiar",
            "embarazo adolescente",
            "maternidad temprana",
            "anticoncepción",
            "anticonceptivos",
            "mortalidad materna",
            "morbilidad materna",
            "mujeres rurales",
            "mujeres campesinas",
            "mujeres indígenas",
            "mujeres afrodescendientes",
            "mujeres víctimas",
            "mujeres desplazadas",
            "mujeres cabeza de familia",
            "jefatura femenina",
            "adultas mayores",
            "niñas",
            "adolescentes mujeres",
            "mujeres con discapacidad",
            "mujeres LGBTI",
            "mujeres trans",
            "educación con enfoque de género",
            "estereotipos de género",
            "roles de género",
            "masculinidades",
            "nuevas masculinidades",
            "cultura machista",
            "patriarcado",
            "coeducación",
            "educación no sexista",
            # From ET01 - Enfoque de Género transversal
            "mainstreaming de género",
            "análisis de género",
            "indicadores de género",
            "presupuestos sensibles al género",
            "PSG",
            "política de género",
            "plan de igualdad",
            "comité de género",
            "instancia de género",
            "madres",
            "gestantes",
            "lactantes",
            "cuidadoras",
        ],
    },
    "PA02": {
        "id": "PA02",
        "name": "Prevención de la violencia y protección frente al conflicto",
        "cluster_id": "CL01",
        "keywords": [
            "conflicto armado",
            "conflicto interno",
            "grupos armados organizados",
            "GAO",
            "grupos delictivos organizados",
            "GDO",
            "grupos armados ilegales",
            "GAI",
            "disidencias",
            "disidencias FARC",
            "ELN",
            "Ejército de Liberación Nacional",
            "paramilitares",
            "paramilitarismo",
            "bandas criminales",
            "BACRIM",
            "narcotráfico",
            "cultivos ilícitos",
            "violencia",
            "inseguridad",
            "criminalidad",
            "homicidios",
            "asesinatos",
            "muertes violentas",
            "secuestro",
            "extorsión",
            "amenazas",
            "desaparición forzada",
            "desaparecidos",
            "reclutamiento forzado",
            "uso de menores",
            "minas antipersonal",
            "MAP",
            "MUSE",
            "artefactos explosivos improvisados",
            "AEI",
            "confinamiento",
            "restricción a la movilidad",
            "protección",
            "medidas de protección",
            "prevención",
            "prevención temprana",
            "alertas tempranas",
            "SAT",
            "sistema de alertas tempranas",
            "nota de seguimiento",
            "informe de riesgo",
            "análisis de riesgo",
            "escenarios de riesgo",
            "Defensoría del Pueblo",
            "Policía Nacional",
            "Ejército Nacional",
            "Fuerza Pública",
            "fuerzas militares",
            "Fiscalía",
            "Procuraduría",
            "Personería",
            "personero",
            "inspección de policía",
            "inspectores",
            "convivencia",
            "convivencia ciudadana",
            "seguridad ciudadana",
            "seguridad comunitaria",
            "espacio público",
            "recuperación del espacio público",
            "pandillas",
            "pandillismo",
            "delincuencia juvenil",
            "consumo de sustancias",
            "expendio de drogas",
            "riñas",
            "lesiones personales",
            "plan de seguridad",
            "estrategia de seguridad",
            "consejos de seguridad",
            "CONSEA",
            "frentes de seguridad",
            "red de cooperantes",
            "cámaras de seguridad",
            "videovigilancia",
            "CAI",
            "comando de atención inmediata",
            "cuadrantes de policía",
            "desmovilizados",
            "excombatientes",
            "reintegración",
            "reincorporación",
            "DDR",
            "desarme desmovilización reintegración",
            "derechos humanos",
            "DDHH",
            "derecho internacional humanitario",
            "DIH",
            "crímenes de guerra",
            "crímenes de lesa humanidad",
            "justicia transicional",
            "JEP",
        ],
    },
    "PA03": {
        "id": "PA03",
        "name": "Ambiente sano, cambio climático, prevención y atención a desastres",
        "cluster_id": "CL01",
        "keywords": [
            "ambiente",
            "medio ambiente",
            "ambiental",
            "sostenibilidad",
            "sostenibilidad ambiental",
            "desarrollo sostenible",
            "sustentabilidad",
            "ecología",
            "ecosistemas",
            "biodiversidad",
            "conservación",
            "preservación",
            "educación ambiental",
            "conciencia ambiental",
            "cambio climático",
            "calentamiento global",
            "gases de efecto invernadero",
            "GEI",
            "mitigación",
            "adaptación climática",
            "variabilidad climática",
            "fenómenos climáticos",
            "huella de carbono",
            "carbono neutralidad",
            "energías renovables",
            "energía limpia",
            "recurso hídrico",
            "agua",
            "fuentes hídricas",
            "cuencas",
            "microcuencas",
            "acuíferos",
            "quebradas",
            "ríos",
            "humedales",
            "contaminación del agua",
            "calidad del agua",
            "acueducto",
            "alcantarillado",
            "saneamiento básico",
            "PSMV",
            "plan de saneamiento y manejo de vertimientos",
            "suelo",
            "erosión",
            "degradación del suelo",
            "deforestación",
            "tala",
            "reforestación",
            "bosques",
            "páramos",
            "selva",
            "áreas protegidas",
            "reservas naturales",
            "parques naturales",
            "zonas de reserva",
            "ecosistemas estratégicos",
            "residuos sólidos",
            "basuras",
            "desechos",
            "PGIRS",
            "plan de gestión integral de residuos",
            "reciclaje",
            "separación en la fuente",
            "relleno sanitario",
            "botadero",
            "contaminación",
            "contaminación ambiental",
            "contaminación del aire",
            "calidad del aire",
            "gestión del riesgo",
            "gestión de riesgo de desastres",
            "desastres",
            "emergencias",
            "calamidad",
            "prevención de desastres",
            "preparación",
            "atención de emergencias",
            "respuesta",
            "inundaciones",
            "desbordamientos",
            "crecientes",
            "deslizamientos",
            "remoción en masa",
            "avalanchas",
            "incendios forestales",
            "quemas",
            "sequía",
            "desertificación",
            "vendavales",
            "vientos fuertes",
            "sismos",
            "terremotos",
            "Fenómeno del Niño",
            "Fenómeno de la Niña",
            "CAR",
            "corporación autónoma regional",
            "autoridad ambiental",
            "ANLA",
            "IDEAM",
            "CMGRD",
            "UNGRD",
            "Bomberos",
            "Cruz Roja",
            "Defensa Civil",
            "ordenamiento territorial",
            "POT",
            "PBOT",
            "EOT",
            "POMCA",
            "zonificación ambiental",
            "licencia ambiental",
            "permiso ambiental",
            "fauna",
            "flora",
            "especies nativas",
            "minería",
            "minería ilegal",
            "extracción",
        ],
    },
    "PA04": {
        "id": "PA04",
        "name": "Derechos económicos, sociales y culturales",
        "cluster_id": "CL03",
        "keywords": [
            "DESC",
            "derechos económicos",
            "derechos sociales",
            "derechos culturales",
            "pacto DESC",
            "derechos fundamentales",
            "mínimo vital",
            "dignidad humana",
            "calidad de vida",
            "empleo",
            "trabajo",
            "desempleo",
            "generación de empleo",
            "oportunidades laborales",
            "trabajo decente",
            "formalización laboral",
            "informalidad",
            "subempleo",
            "salario",
            "salario mínimo",
            "remuneración",
            "seguridad social",
            "EPS",
            "ARL",
            "SENA",
            "emprendimiento",
            "vivienda",
            "vivienda digna",
            "derecho a la vivienda",
            "vivienda de interés social",
            "VIS",
            "vivienda de interés prioritario",
            "VIP",
            "mejoramiento de vivienda",
            "subsidio de vivienda",
            "hacinamiento",
            "servicios públicos",
            "salud",
            "derecho a la salud",
            "sistema de salud",
            "EPS",
            "IPS",
            "régimen contributivo",
            "régimen subsidiado",
            "SISBÉN",
            "afiliación al sistema",
            "hospital",
            "centro de salud",
            "puesto de salud",
            "ESE",
            "empresa social del estado",
            "Secretaría de Salud",
            "salud mental",
            "vacunación",
            "desnutrición",
            "malnutrición",
            "mortalidad infantil",
            "mortalidad materna",
            "educación",
            "derecho a la educación",
            "acceso a la educación",
            "cobertura educativa",
            "calidad educativa",
            "educación inicial",
            "educación básica",
            "primaria",
            "secundaria",
            "educación media",
            "bachillerato",
            "educación superior",
            "universidad",
            "Secretaría de Educación",
            "docentes",
            "maestros",
            "deserción escolar",
            "abandono escolar",
            "PAE",
            "programa de alimentación escolar",
            "transporte escolar",
            "infraestructura educativa",
            "analfabetismo",
            "alfabetización",
            "cultura",
            "derechos culturales",
            "patrimonio cultural",
            "identidad cultural",
            "biblioteca",
            "casa de la cultura",
            "museo",
            "Secretaría de Cultura",
            "artistas",
            "deporte",
            "recreación",
            "actividad física",
            "escenarios deportivos",
            "polideportivo",
            "parques",
            "alimentación",
            "seguridad alimentaria",
            "soberanía alimentaria",
            "banco de alimentos",
            "primera infancia",
            "niños y niñas",
            "adultos mayores",
            "tercera edad",
            "personas con discapacidad",
            "PcD",
            "familias en acción",
            "jóvenes en acción",
            "transferencias monetarias",
            "subsidios",
            "infraestructura social",
            "espacio público",
            "vías",
            "carreteras",
            "transporte público",
            "desarrollo comunitario",
            "JAC",
            "juntas de acción comunal",
        ],
    },
    "PA05": {
        "id": "PA05",
        "name": "Derechos de las víctimas y construcción de paz",
        "cluster_id": "CL02",
        "keywords": [
            "víctimas",
            "víctima",
            "población víctima",
            "hechos victimizantes",
            "hecho victimizante",
            "RUV",
            "registro único de víctimas",
            "UARIV",
            "unidad de víctimas",
            "Ley 1448",
            "Enlace de Víctimas",
            "enlace municipal",
            "desplazamiento forzado",
            "desplazamiento",
            "desplazados",
            "población desplazada",
            "confinamiento",
            "despojo",
            "despojo de tierras",
            "abandono forzado",
            "homicidio",
            "masacre",
            "desaparición forzada",
            "desaparecidos",
            "secuestro",
            "tortura",
            "violencia sexual",
            "minas antipersonal",
            "reclutamiento forzado",
            "amenazas",
            "atentados",
            "actos terroristas",
            "verdad",
            "derecho a la verdad",
            "justicia",
            "derecho a la justicia",
            "reparación",
            "reparación integral",
            "indemnización",
            "compensación",
            "garantías de no repetición",
            "memoria histórica",
            "dignificación",
            "restitución",
            "restitución de tierras",
            "URT",
            "unidad de restitución de tierras",
            "retornos",
            "retorno de población",
            "reubicaciones",
            "reasentamientos",
            "atención humanitaria",
            "ayuda humanitaria",
            "PAU",
            "punto de atención",
            "SNARIV",
            "sistema nacional de atención",
            "paz",
            "construcción de paz",
            "cultura de paz",
            "acuerdo de paz",
            "proceso de paz",
            "posconflicto",
            "posacuerdo",
            "reconciliación",
            "tejido social",
            "PDET",
            "programas de desarrollo territorial",
            "PAT",
            "territorios PDET",
            "municipios PDET",
            "reforma rural integral",
            "RRI",
            "ART",
            "agencia de renovación del territorio",
            "ZOMAC",
            "zonas más afectadas por el conflicto",
            "justicia transicional",
            "JEP",
            "comisión de la verdad",
            "UBPD",
            "excombatientes",
            "FARC",
            "reincorporación",
            "ETCR",
            "ARN",
            "proyectos productivos",
            "mesas de participación",
            "organizaciones de víctimas",
            "reparación colectiva",
            "PIRC",
            "FONSET",
            "cooperación internacional",
            "OIM",
            "ACNUR",
            "PMA",
        ],
    },
    "PA06": {
        "id": "PA06",
        "name": "Derecho al buen futuro de la niñez, adolescencia, juventud",
        "cluster_id": "CL02",
        "keywords": [
            "niñez",
            "niños",
            "niñas",
            "niño",
            "niña",
            "primera infancia",
            "infancia",
            "adolescencia",
            "adolescentes",
            "adolescente",
            "juventud",
            "jóvenes",
            "joven",
            "menores de edad",
            "menores",
            "código de infancia y adolescencia",
            "Ley 1098",
            "Ley 1804",
            "política de infancia",
            "política pública de juventud",
            "interés superior del niño",
            "derechos de los niños",
            "desarrollo integral",
            "enfoque de derechos",
            "ICBF",
            "instituto colombiano de bienestar familiar",
            "defensor de familia",
            "Comisaría de Familia",
            "SNBF",
            "sistema nacional de bienestar familiar",
            "Consejería de Juventud",
            "plataforma de juventud",
            "De Cero a Siempre",
            "CDI",
            "centro de desarrollo infantil",
            "hogar comunitario",
            "hogar infantil",
            "jardín infantil",
            "madres comunitarias",
            "atención integral",
            "educación inicial",
            "nutrición infantil",
            "restablecimiento de derechos",
            "PARD",
            "vulneración de derechos",
            "hogar sustituto",
            "adopción",
            "protección de niños",
            "entornos protectores",
            "maltrato infantil",
            "trabajo infantil",
            "explotación infantil",
            "ESCNNA",
            "reclutamiento",
            "consumo de SPA",
            "SRPA",
            "sistema de responsabilidad penal adolescente",
            "justicia juvenil",
            "sanciones pedagógicas",
            "CAE",
            "centro de atención especializada",
            "educación para niños",
            "permanencia escolar",
            "deserción",
            "ludotecas",
            "estimulación temprana",
            "salud infantil",
            "vacunación",
            "crecimiento y desarrollo",
            "lactancia materna",
            "obesidad infantil",
            "embarazo adolescente",
            "prevención del embarazo",
            "participación juvenil",
            "consejos de juventud",
            "CMJ",
            "organizaciones juveniles",
            "liderazgo juvenil",
            "empleo juvenil",
            "primer empleo",
            "emprendimiento juvenil",
            "Jóvenes en Acción",
            "casas de juventud",
            "parques infantiles",
            "prevención del suicidio",
            "bullying",
            "acoso escolar",
            "proyecto de vida",
            "habilidades para la vida",
            "niños víctimas",
            "niños con discapacidad",
            "familia",
            "pautas de crianza",
            "crianza positiva",
            "escuela de padres",
            "custodia",
            "cuota alimentaria",
        ],
    },
    "PA07": {
        "id": "PA07",
        "name": "Tierras y territorios",
        "cluster_id": "CL01",
        "keywords": [
            "tierras",
            "tierra",
            "territorio",
            "territorial",
            "tenencia de la tierra",
            "propiedad",
            "baldíos",
            "adjudicación",
            "titulación",
            "formalización",
            "formalización de la propiedad",
            "escrituración",
            "registro de instrumentos públicos",
            "catastro",
            "catastro multipropósito",
            "actualización catastral",
            "avalúo catastral",
            "IGAC",
            "Sistema de Información Geográfica",
            "SIG",
            "ordenamiento territorial",
            "OT",
            "POT",
            "plan de ordenamiento territorial",
            "PBOT",
            "EOT",
            "revisión del POT",
            "uso del suelo",
            "clasificación del suelo",
            "suelo urbano",
            "suelo rural",
            "suelo de expansión",
            "perímetro urbano",
            "zonificación",
            "zonas de riesgo",
            "zonas de protección ambiental",
            "desarrollo rural",
            "reforma rural integral",
            "RRI",
            "economía campesina",
            "agricultura familiar",
            "campesinos",
            "pequeños productores",
            "Unidad Agrícola Familiar",
            "UAF",
            "UMATA",
            "asistencia técnica agropecuaria",
            "extensión rural",
            "secretaría de agricultura",
            "Agencia de Desarrollo Rural",
            "ADR",
            "restitución de tierras",
            "URT",
            "acceso a la tierra",
            "fondo de tierras",
            "conflictos de uso del suelo",
            "ocupación irregular",
            "legalización de barrios",
            "mejoramiento integral de barrios",
            "vías terciarias",
            "caminos veredales",
            "electrificación rural",
            "acueductos veredales",
            "conectividad rural",
            "infraestructura productiva",
            "territorios étnicos",
            "resguardos indígenas",
            "territorios colectivos",
            "consejos comunitarios",
            "consulta previa",
            "autonomía territorial",
            "títulos mineros",
            "concesiones",
            "licencias de urbanismo",
            "licencias de construcción",
            "impuesto predial",
            "valorización",
            "movilidad",
            "conectividad vial",
            "transporte público",
            "espacio público",
            "parques",
            "zonas verdes",
        ],
    },
    "PA08": {
        "id": "PA08",
        "name": "Líderes y defensores de derechos humanos",
        "cluster_id": "CL03",
        "keywords": [
            "líderes sociales",
            "liderazgo social",
            "líderes comunitarios",
            "líderes comunales",
            "lideresas",
            "líder",
            "defensores de derechos humanos",
            "defensores",
            "defensoras",
            "activistas",
            "líderes ambientales",
            "ambientalistas",
            "líderes campesinos",
            "líderes rurales",
            "líderes indígenas",
            "autoridades indígenas",
            "líderes afrodescendientes",
            "líderes de víctimas",
            "líderes sindicales",
            "periodistas",
            "comunicadores sociales",
            "JAC",
            "juntas de acción comunal",
            "presidentes de JAC",
            "dignatarios",
            "gestores de paz",
            "liderazgo territorial",
            "amenazas",
            "amenazas de muerte",
            "intimidación",
            "hostigamiento",
            "riesgo",
            "situación de riesgo",
            "riesgo extraordinario",
            "riesgo extremo",
            "asesinatos de líderes",
            "homicidios",
            "masacres",
            "atentados",
            "agresiones",
            "desplazamiento forzado",
            "exilio",
            "estigmatización",
            "señalamientos",
            "criminalización de la protesta",
            "protección",
            "esquemas de protección",
            "medidas de protección",
            "UNP",
            "escoltas",
            "vehículos blindados",
            "botón de pánico",
            "reubicación temporal",
            "análisis de riesgo",
            "CERREM",
            "prevención",
            "alertas tempranas",
            "SAT",
            "planes de prevención",
            "autoprotección",
            "garantías",
            "Mesa de Garantías",
            "Decreto 660",
            "protocolo de protección",
            "Fiscalía",
            "Unidad Especial de Investigación",
            "impunidad",
            "organizaciones de derechos humanos",
            "participación política",
            "movilización social",
            "protesta social",
            "manifestaciones",
            "libertad de expresión",
            "libertad de prensa",
        ],
    },
    "PA09": {
        "id": "PA09",
        "name": "Crisis de derechos de personas privadas de la libertad",
        "cluster_id": "CL04",
        "keywords": [
            "privados de libertad",
            "PPL",
            "personas privadas de la libertad",
            "internos",
            "reclusos",
            "presos",
            "población carcelaria",
            "población penitenciaria",
            "condenados",
            "sindicados",
            "preventivos",
            "prisión domiciliaria",
            "detención domiciliaria",
            "sistema penitenciario",
            "cárceles",
            "cárcel",
            "prisión",
            "ERON",
            "establecimiento penitenciario",
            "penitenciaría",
            "centro de reclusión",
            "pabellones",
            "patios",
            "celdas",
            "INPEC",
            "instituto nacional penitenciario",
            "guardias penitenciarios",
            "dragoneantes",
            "custodia",
            "vigilancia",
            "hacinamiento",
            "sobrepoblación",
            "sobrecupo",
            "cupos carcelarios",
            "crisis carcelaria",
            "infraestructura carcelaria",
            "construcción de cárceles",
            "condiciones de reclusión",
            "condiciones inhumanas",
            "trato cruel",
            "dignidad",
            "alimentación carcelaria",
            "agua potable",
            "servicios sanitarios",
            "higiene",
            "salud en cárceles",
            "atención médica",
            "medicamentos",
            "tuberculosis",
            "VIH",
            "salud mental",
            "adicciones",
            "muertes en custodia",
            "fallecimientos",
            "seguridad carcelaria",
            "motines",
            "riñas",
            "violencia entre internos",
            "extorsión",
            "corrupción carcelaria",
            "resocialización",
            "reinserción social",
            "tratamiento penitenciario",
            "trabajo penitenciario",
            "educación carcelaria",
            "talleres",
            "redención de pena",
            "descuentos",
            "visitas",
            "visitas familiares",
            "visitas íntimas",
            "comunicación",
            "contacto con la familia",
            "defensa pública",
            "defensoría",
            "jueces de ejecución",
            "hábeas corpus",
            "medidas alternativas",
            "penas alternativas",
            "libertad condicional",
            "casa por cárcel",
            "brazalete electrónico",
            "monitoreo electrónico",
            "beneficios judiciales",
            "permisos de salida",
            "mujeres privadas de libertad",
            "madres en prisión",
            "niños en prisión",
            "jóvenes privados de libertad",
            "estado de cosas inconstitucional",
            "ECI",
            "Sentencia T-388",
            "tutelas",
            "Defensoría del Pueblo",
            "Procuraduría",
            "reincidencia",
            "reingreso",
            # From ET09 - Enfoque Diferencial PPL
            "centros de detención transitoria",
            "medidas de aseguramiento",
            "Instituto Nacional Penitenciario",
            "establecimientos de reclusión",
        ],
    },
    "PA10": {
        "id": "PA10",
        "name": "Migración transfronteriza",
        "cluster_id": "CL04",
        "keywords": [
            "migración",
            "migrantes",
            "migrante",
            "inmigrantes",
            "inmigración",
            "población migrante",
            "flujo migratorio",
            "migración venezolana",
            "venezolanos",
            "refugiados",
            "solicitantes de refugio",
            "solicitantes de asilo",
            "asilo",
            "movilidad humana",
            "regular",
            "irregular",
            "situación migratoria",
            "indocumentados",
            "sin documentos",
            "PEP",
            "permiso especial de permanencia",
            "PPT",
            "permiso por protección temporal",
            "TMF",
            "tarjeta de movilidad fronteriza",
            "regularización",
            "regularización migratoria",
            "cédula de extranjería",
            "visa",
            "pasaporte",
            "RUMV",
            "registro único de migrantes",
            "Migración Colombia",
            "Cancillería",
            "RAMV",
            "Gerencia de Frontera",
            "frontera",
            "zona de frontera",
            "municipios fronterizos",
            "Venezuela",
            "Cúcuta",
            "La Guajira",
            "Arauca",
            "Norte de Santander",
            "pasos fronterizos",
            "trochas",
            "pasos irregulares",
            "control fronterizo",
            "cierre de frontera",
            "crisis humanitaria",
            "emergencia humanitaria",
            "asistencia humanitaria",
            "albergues",
            "integración",
            "integración social",
            "inclusión",
            "cohesión social",
            "comunidades de acogida",
            "xenofobia",
            "acceso a salud",
            "acceso a educación",
            "acceso al trabajo",
            "empleo formal",
            "explotación laboral",
            "trabajo informal",
            "salud de migrantes",
            "vacunación",
            "desnutrición",
            "salud mental",
            "educación de migrantes",
            "niños migrantes",
            "cupos escolares",
            "matrícula",
            "vivienda",
            "hacinamiento",
            "menores no acompañados",
            "mujeres migrantes",
            "trata de personas",
            "tráfico de migrantes",
            "protección internacional",
            "refugio",
            "CONARE",
            "protección temporal",
            "retorno voluntario",
            "deportación",
            "reunificación familiar",
            "gestión migratoria",
            "política migratoria",
            "ACNUR",
            "OIM",
            "UNICEF",
            "Cruz Roja",
            # From ET10 - Enfoque Diferencial Migración
            "ETPV",
            "estatuto temporal de protección",
            "CONPES migratorio",
            "desplazamiento transfronterizo",
            "documento de identidad migrante",
            "empleabilidad migrante",
            "niños, niñas y adolescentes migrantes",
            "familias migrantes",
        ],
    },
}

# CANONICAL REFACTORING: Alias legacy to canonical for backward compatibility
# New code should import CANON_POLICY_AREAS from canonical_specs directly
POLICY_AREAS_CANONICAL = POLICY_AREAS_CANONICAL_LEGACY  # Temporary backward compat

# =============================================================================
# CANONICAL VALUE CHAIN DIMENSIONS (DIM01-DIM06)
# DEPRECATED: This should use CANON_DIMENSIONS from canonical_specs
# Source: questionnaire_monolith.json canonical_notation.dimensions (now frozen in canonical_specs)
# Structure: 3 levels
#   Level 1: Dimension (DIM01-DIM06)
#   Level 2: Analytical variables (compress 5 questions per dimension)
#   Level 3: Expected words (general + by Policy Area)
# =============================================================================

VALUE_CHAIN_DIMENSIONS: dict[str, dict[str, Any]] = {
    "DIM01": {
        "code": "DIM01",
        "name": "INSUMOS",
        "label": "Diagnóstico y Recursos",
        "base_slots": ["D1-Q1", "D1-Q2", "D1-Q3", "D1-Q4", "D1-Q5"],
        "analytical_variables": {
            "linea_base_diagnostico": {
                "slot": "D1-Q1",
                "expected_elements": [
                    "cobertura_territorial_especificada",
                    "fuentes_oficiales",
                    "indicadores_cuantitativos",
                    "series_temporales_años",
                ],
            },
            "dimensionamiento_brecha": {
                "slot": "D1-Q2",
                "expected_elements": ["brecha_cuantificada", "limitaciones_datos", "subregistro"],
            },
            "asignacion_recursos": {
                "slot": "D1-Q3",
                "expected_elements": [
                    "asignacion_explicita",
                    "suficiencia_justificada",
                    "trazabilidad_ppi_bpin",
                ],
            },
            "capacidad_institucional": {
                "slot": "D1-Q4",
                "expected_elements": [
                    "cuellos_botella",
                    "datos_sistemas",
                    "gobernanza",
                    "procesos",
                    "talento_humano",
                ],
            },
            "marco_restricciones": {
                "slot": "D1-Q5",
                "expected_elements": [
                    "coherencia_demostrada",
                    "restricciones_legales",
                    "restricciones_presupuestales",
                    "restricciones_temporales",
                ],
            },
        },
        "keywords_general": [
            "línea base",
            "año base",
            "situación inicial",
            "diagnóstico",
            "DANE",
            "Medicina Legal",
            "Fiscalía",
            "Policía Nacional",
            "SIVIGILA",
            "SISPRO",
            "brecha",
            "déficit",
            "rezago",
            "subregistro",
            "cifra negra",
            "recursos",
            "presupuesto",
            "PPI",
            "BPIN",
            "asignación",
            "millones",
            "capacidad instalada",
            "talento humano",
            "personal idóneo",
            "cuello de botella",
            "limitación institucional",
            "barrera",
            "marco legal",
            "Ley",
            "Decreto",
            "competencias",
            "restricción",
        ],
    },
    "DIM02": {
        "code": "DIM02",
        "name": "ACTIVIDADES",
        "label": "Diseño de Intervención",
        "base_slots": ["D2-Q1", "D2-Q2", "D2-Q3", "D2-Q4", "D2-Q5"],
        "analytical_variables": {
            "estructura_operativa": {
                "slot": "D2-Q1",
                "expected_elements": [
                    "columna_costo",
                    "columna_cronograma",
                    "columna_producto",
                    "columna_responsable",
                    "formato_tabular",
                ],
            },
            "diseño_intervencion": {
                "slot": "D2-Q2",
                "expected_elements": [
                    "instrumento_especificado",
                    "logica_causal_explicita",
                    "poblacion_objetivo_definida",
                ],
            },
            "pertinencia_causal": {
                "slot": "D2-Q3",
                "expected_elements": ["aborda_causa_raiz", "vinculo_diagnostico_actividad"],
            },
            "gestion_riesgos": {
                "slot": "D2-Q4",
                "expected_elements": ["mitigacion_propuesta", "riesgos_identificados"],
            },
            "articulacion_actividades": {
                "slot": "D2-Q5",
                "expected_elements": ["complementariedad_explicita", "secuenciacion_logica"],
            },
        },
        "keywords_general": [
            "matriz operativa",
            "plan de acción",
            "cronograma",
            "responsable",
            "actividad",
            "intervención",
            "programa",
            "proyecto",
            "estrategia",
            "población objetivo",
            "beneficiarios",
            "focalización",
            "causa raíz",
            "árbol de problemas",
            "teoría de cambio",
            "riesgo",
            "mitigación",
            "contingencia",
            "articulación",
            "complementariedad",
            "secuencia",
            "etapa",
            "fase",
        ],
    },
    "DIM03": {
        "code": "DIM03",
        "name": "PRODUCTOS",
        "label": "Productos y Outputs",
        "base_slots": ["D3-Q1", "D3-Q2", "D3-Q3", "D3-Q4", "D3-Q5"],
        "analytical_variables": {
            "indicadores_producto": {
                "slot": "D3-Q1",
                "expected_elements": [
                    "fuente_verificacion",
                    "linea_base_producto",
                    "meta_cuantitativa",
                ],
            },
            "dosificacion_metas": {
                "slot": "D3-Q2",
                "expected_elements": ["dosificacion_definida", "proporcionalidad_meta_brecha"],
            },
            "trazabilidad": {
                "slot": "D3-Q3",
                "expected_elements": ["trazabilidad_organizacional", "trazabilidad_presupuestal"],
            },
            "factibilidad": {
                "slot": "D3-Q4",
                "expected_elements": [
                    "coherencia_recursos",
                    "factibilidad_tecnica",
                    "realismo_plazos",
                ],
            },
            "conexion_resultados": {
                "slot": "D3-Q5",
                "expected_elements": ["conexion_producto_resultado", "mecanismo_causal_explicito"],
            },
        },
        "keywords_general": [
            "producto",
            "output",
            "entregable",
            "bien",
            "servicio",
            "indicador de producto",
            "meta de producto",
            "MP-",
            "línea base",
            "meta cuatrienio",
            "fuente de verificación",
            "dosificación",
            "programación anual",
            "avance",
            "responsable",
            "secretaría",
            "dependencia",
            "entidad",
            "código BPIN",
            "proyecto de inversión",
            "PPI",
            "factible",
            "viable",
            "realista",
            "coherente",
            "genera",
            "produce",
            "contribuye a",
        ],
    },
    "DIM04": {
        "code": "DIM04",
        "name": "RESULTADOS",
        "label": "Resultados y Outcomes",
        "base_slots": ["D4-Q1", "D4-Q2", "D4-Q3", "D4-Q4", "D4-Q5"],
        "analytical_variables": {
            "indicadores_resultado": {
                "slot": "D4-Q1",
                "expected_elements": [
                    "horizonte_temporal",
                    "linea_base_resultado",
                    "meta_resultado",
                    "metrica_outcome",
                ],
            },
            "cadena_causal": {
                "slot": "D4-Q2",
                "expected_elements": [
                    "cadena_causal_explicita",
                    "condiciones_habilitantes",
                    "supuestos_identificados",
                ],
            },
            "alcanzabilidad": {
                "slot": "D4-Q3",
                "expected_elements": [
                    "evidencia_comparada",
                    "justificacion_capacidad",
                    "justificacion_recursos",
                ],
            },
            "coherencia_problematica": {
                "slot": "D4-Q4",
                "expected_elements": ["criterios_exito_definidos", "vinculo_resultado_problema"],
            },
            "alineacion_estrategica": {
                "slot": "D4-Q5",
                "expected_elements": ["alineacion_ods", "alineacion_pnd"],
            },
        },
        "keywords_general": [
            "resultado",
            "outcome",
            "efecto",
            "cambio",
            "transformación",
            "indicador de resultado",
            "meta de resultado",
            "MR-",
            "reducción",
            "incremento",
            "mejora",
            "disminución",
            "tasa",
            "porcentaje",
            "índice",
            "cobertura",
            "supuesto",
            "condición",
            "factor externo",
            "evidencia",
            "buena práctica",
            "caso exitoso",
            "ODS",
            "objetivo de desarrollo sostenible",
            "PND",
            "plan nacional de desarrollo",
            "política nacional",
        ],
    },
    "DIM05": {
        "code": "DIM05",
        "name": "IMPACTOS",
        "label": "Impactos de Largo Plazo",
        "base_slots": ["D5-Q1", "D5-Q2", "D5-Q3", "D5-Q4", "D5-Q5"],
        "analytical_variables": {
            "impacto_esperado": {
                "slot": "D5-Q1",
                "expected_elements": ["impacto_definido", "rezago_temporal", "ruta_transmision"],
            },
            "medicion_impacto": {
                "slot": "D5-Q2",
                "expected_elements": ["justifica_validez", "usa_indices_compuestos", "usa_proxies"],
            },
            "limitaciones_medicion": {
                "slot": "D5-Q3",
                "expected_elements": [
                    "documenta_validez",
                    "proxy_para_intangibles",
                    "reconoce_limitaciones",
                ],
            },
            "riesgos_sistemicos": {
                "slot": "D5-Q4",
                "expected_elements": ["alineacion_marcos", "riesgos_sistemicos"],
            },
            "realismo_impacto": {
                "slot": "D5-Q5",
                "expected_elements": [
                    "analisis_realismo",
                    "efectos_no_deseados",
                    "hipotesis_limite",
                ],
            },
        },
        "keywords_general": [
            "impacto",
            "efecto de largo plazo",
            "transformación estructural",
            "indicador de impacto",
            "meta de impacto",
            "MI-",
            "bienestar",
            "calidad de vida",
            "desarrollo humano",
            "índice",
            "índice de desarrollo",
            "IDH",
            "IPM",
            "pobreza",
            "desigualdad",
            "Gini",
            "NBI",
            "sostenibilidad",
            "perdurabilidad",
            "irreversibilidad",
            "proxy",
            "aproximación",
            "medición indirecta",
            "riesgo sistémico",
            "efecto no deseado",
            "externalidad",
        ],
    },
    "DIM06": {
        "code": "DIM06",
        "name": "CAUSALIDAD",
        "label": "Teoría de Cambio",
        "base_slots": ["D6-Q1", "D6-Q2", "D6-Q3", "D6-Q4", "D6-Q5"],
        "analytical_variables": {
            "teoria_cambio": {
                "slot": "D6-Q1",
                "expected_elements": [
                    "diagrama_causal",
                    "supuestos_verificables",
                    "teoria_cambio_explicita",
                ],
            },
            "coherencia_logica": {
                "slot": "D6-Q2",
                "expected_elements": ["evita_saltos_logicos", "proporcionalidad_eslabones"],
            },
            "testabilidad": {
                "slot": "D6-Q3",
                "expected_elements": ["propone_pilotos_o_pruebas", "reconoce_inconsistencias"],
            },
            "adaptabilidad": {
                "slot": "D6-Q4",
                "expected_elements": [
                    "ciclos_aprendizaje",
                    "mecanismos_correccion",
                    "sistema_monitoreo",
                ],
            },
            "contextualidad": {
                "slot": "D6-Q5",
                "expected_elements": ["analisis_contextual", "enfoque_diferencial"],
            },
        },
        "keywords_general": [
            "teoría de cambio",
            "marco lógico",
            "cadena de valor",
            "si-entonces",
            "porque",
            "genera",
            "produce",
            "causa",
            "mecanismo causal",
            "vínculo causal",
            "conexión lógica",
            "supuesto",
            "hipótesis",
            "condición",
            "premisa",
            "eslabón",
            "nivel",
            "secuencia causal",
            "piloto",
            "prueba",
            "validación",
            "verificación",
            "monitoreo",
            "seguimiento",
            "evaluación",
            "ajuste",
            "contexto",
            "territorio",
            "enfoque diferencial",
            "particularidad",
        ],
    },
}

ALL_BASE_SLOTS: tuple[str, ...] = tuple(
    slot
    for dim_id in sorted(VALUE_CHAIN_DIMENSIONS)
    for slot in VALUE_CHAIN_DIMENSIONS[dim_id]["base_slots"]
)

SLOT_TO_DIMENSION_ID: dict[str, str] = {
    slot: dim_id
    for dim_id, dim_config in VALUE_CHAIN_DIMENSIONS.items()
    for slot in dim_config["base_slots"]
}

SLOT_TO_KEYWORDS_GENERAL: dict[str, list[str]] = {
    slot: dim_config["keywords_general"]
    for dim_id, dim_config in VALUE_CHAIN_DIMENSIONS.items()
    for slot in dim_config["base_slots"]
}

SLOT_TO_EXPECTED_ELEMENTS: dict[str, list[str]] = {
    var_config["slot"]: var_config["expected_elements"]
    for dim_config in VALUE_CHAIN_DIMENSIONS.values()
    for var_config in dim_config["analytical_variables"].values()
}

# ---------------------------------------------------------------------------
# 1. CORE DATA STRUCTURES
# ---------------------------------------------------------------------------


class MunicipalOntology:
    """Core ontology for municipal development domains.

    CANONICAL REFACTORING: Uses frozen constants from canonical_specs.py
    - VALUE_CHAIN_DIMENSIONS: 6 analytical dimensions (DIM01-DIM06)
    - POLICY_AREAS_CANONICAL: 10 policy areas (PA01-PA10)
    Source: Originally extracted from questionnaire_monolith.json, now frozen
    """

    def __init__(self) -> None:
        # Value chain dimensions (DIM01-DIM06) with keywords
        self.value_chain_dimensions = {
            dim_id: dim_config["keywords_general"]
            for dim_id, dim_config in VALUE_CHAIN_DIMENSIONS.items()
        }

        # Policy areas (PA01-PA10) with keywords
        self.policy_domains = {
            pa_id: pa_config["keywords"] for pa_id, pa_config in POLICY_AREAS_CANONICAL.items()
        }


# ---------------------------------------------------------------------------
# 2. SEMANTIC ANALYSIS ENGINE
# ---------------------------------------------------------------------------

# =============================================================================
# CANONICAL PATTERNS FOR SLOT D3-Q3 (Trazabilidad Presupuestal/Organizacional)
# CANONICAL REFACTORING NOTE: question_id mappings (Q013, Q043, etc.) are preserved
# but marked as LEGACY. New code should use policy area (PA01-PA10) directly.
# Rationale: This is method-specific pattern metadata, not questionnaire routing.
# These patterns define evidence requirements (capability metadata), not Q-to-method bindings.
# =============================================================================

PATTERNS_D3_Q3_BY_POLICY_AREA: dict[str, dict[str, Any]] = {
    "PA01": {  # Género
        "question_id": "Q013",  # LEGACY: For traceability only, not for method routing
        "question_text": "¿Los productos de género tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de la Mujer|Oficina de la Mujer|Secretaría de Desarrollo Social",
            r"articulado con la Comisaría de Familia",
            r"corresponsabilidad de|en alianza con",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión asociado",
            r"programa del PPI|línea de inversión",
            r"recursos del proyecto|presupuesto del producto",
        ],
    },
    "PA02": {  # Violencia/Conflicto
        "question_id": "Q073",
        "question_text": "¿Los productos de protección tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Gobierno|Enlace de Víctimas|Personería Municipal",
            r"articulado con la Defensoría del Pueblo|Policía Nacional",
            r"corresponsabilidad de|en alianza con",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para la paz",
            r"programa del PPI|línea de inversión en víctimas",
            r"recursos del proyecto|presupuesto para prevención",
        ],
    },
    "PA03": {  # Ambiente
        "question_id": "Q103",
        "question_text": "¿Los productos ambientales tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Ambiente|Planeación|Infraestructura",
            r"articulado con la CAR|CMGRD",
            r"convenio con|contrato de obra No\.",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para gestión del riesgo",
            r"programa del PPI|línea de inversión en sostenibilidad ambiental",
            r"recursos del proyecto|presupuesto de la obra",
        ],
    },
    "PA04": {  # DESC (Derechos Económicos, Sociales y Culturales)
        "question_id": "Q133",
        "question_text": "¿Los productos sociales tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Educación|Secretaría de Salud|Oficina de Vivienda",
            r"articulado con la ESE Hospital|ICBF",
            r"convenio con|contrato de obra No\.",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para educación|salud|vivienda",
            r"programa del PPI|línea de inversión en desarrollo social",
            r"recursos del proyecto|presupuesto del PAE",
        ],
    },
    "PA05": {  # Víctimas/Paz
        "question_id": "Q163",
        "question_text": "¿Los productos para víctimas tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Enlace Municipal de Víctimas|Secretaría de Gobierno",
            r"articulado con la Personería|UARIV territorial",
            r"convenio con|operado por",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para la paz y reconciliación",
            r"programa del PPI|línea de inversión en víctimas",
            r"recursos del FONSET|presupuesto para el PAT",
        ],
    },
    "PA06": {  # Niñez/Juventud
        "question_id": "Q193",
        "question_text": "¿Los productos para niñez y juventud tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Desarrollo Social|Educación|Salud",
            r"articulado con el ICBF|Comisaría de Familia",
            r"convenio con|operado por",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para primera infancia",
            r"programa del PPI|línea de inversión en juventud",
            r"recursos del SGP para educación|presupuesto del PAE",
        ],
    },
    "PA07": {  # Tierras
        "question_id": "Q223",
        "question_text": "¿Los productos de tierras tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Planeación|Infraestructura|UMATA",
            r"articulado con el IGAC|convenio con INVIAS|operado por",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para catastro multipropósito",
            r"programa del PPI|línea de inversión en desarrollo rural",
            r"recursos del proyecto|presupuesto para la red vial",
        ],
    },
    "PA08": {  # Líderes DDHH
        "question_id": "Q253",
        "question_text": "¿Los productos de protección de líderes tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Gobierno|Despacho del Alcalde|Personería Municipal",
            r"articulado con la UNP|en alianza con plataformas de DDHH",
            r"convenio con|operado por",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para garantías y DDHH",
            r"programa del PPI|línea de inversión en seguridad y convivencia",
            r"recursos del proyecto|presupuesto para la Mesa de Garantías",
        ],
    },
    "PA09": {  # PPL (Personas Privadas de Libertad)
        "question_id": "Q283",
        "question_text": "¿Los productos para PPL tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Gobierno|Secretaría de Salud|Personería Municipal",
            r"articulado con el INPEC|convenio con la ESE del municipio",
            r"contrato de obra No\.|contrato de suministro de alimentos",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para infraestructura carcelaria",
            r"programa del PPI|línea de inversión en seguridad y justicia",
            r"recursos del proyecto|presupuesto para atención a PPL",
        ],
    },
    "PA10": {  # Migración
        "question_id": "Q043",
        "question_text": "¿Los productos para migración tienen trazabilidad presupuestal y organizacional?",
        "trazabilidad_organizacional": [
            r"Secretaría de Gobierno|Desarrollo Social|Enlace de Migración",
            r"articulado con la Personería|operado por un socio de la cooperación \(ONG\)",
            r"convenio con|contrato de suministro",
        ],
        "trazabilidad_presupuestal": [
            r"código BPIN|proyecto de inversión para atención a población migrante",
            r"programa del PPI|línea de inversión en integración",
            r"recursos del proyecto|presupuesto para el PAO",
        ],
    },
}

# Expected elements common to all Policy Areas for D3-Q3
EXPECTED_ELEMENTS_D3_Q3: list[dict[str, Any]] = [
    {"type": "trazabilidad_organizacional", "required": True},
    {"type": "trazabilidad_presupuestal", "required": True},
]

# Scoring configuration for D3-Q3 slot
SCORING_CONFIG_D3_Q3: dict[str, Any] = {
    "scoring_modality": "TYPE_A",
    "modality_behavior": "count_and_scale",
    "aggregation": "presence_threshold",
    "threshold": 0.7,
    "scale": [0, 1, 2, 3],
}


class SemanticAnalyzer:
    """Advanced semantic analysis for municipal documents."""

    def __init__(self, ontology: MunicipalOntology) -> None:
        """
        Initialize SemanticAnalyzer.

        Args:
            ontology: Municipal ontology for semantic classification

        Parameters:
            - Derived from `artifacts/plan1/calibration/analyzer_one_calibration.json`
            - No defaults (hard-fail if calibration is missing)
        """
        self.ontology = ontology

        # CANONICAL REFACTORING NOTE:
        # - Removed: _monolith_index and _patterns_resolved (never used, questionnaire coupling)
        # - Kept: Calibration loading (computational results, method-specific parameters)
        # - Kept: Unit of analysis stats (PDT/PDM structure detection)

        # Load method-specific calibration (computational results, not questionnaire data)
        calib = self._load_json(Path("artifacts/plan1/calibration/analyzer_one_calibration.json"))
        self._calibration = calib
        self.thresholds_by_base_slot = calib["thresholds_by_base_slot"]
        self._slot_thresholds = {slot: self._get_slot_threshold(slot) for slot in ALL_BASE_SLOTS}

        # Load unit of analysis structure stats (PDT/PDM natural blocks)
        self._unit_of_analysis_stats = self._load_unit_of_analysis_stats(
            Path("pdt_analysis_report.json")
        )

        # TF-IDF configuration from calibration
        self.max_features = calib["max_features"]
        self.ngram_range = tuple(calib["ngram_range"])
        self.similarity_threshold = None  # base-slot specific thresholds are used

        if TfidfVectorizer is not None:
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words=None,  # Spanish text - no English stopwords
                ngram_range=self.ngram_range,
            )
        else:
            self.vectorizer = None

    def _load_unit_of_analysis_stats(self, report_path: Path) -> dict[str, int]:
        if not report_path.exists():
            raise FileNotFoundError(f"Required unit-of-analysis report missing: {report_path}")
        report = json.loads(report_path.read_text())
        return self._compute_unit_of_analysis_natural_blocks(report)

    def _compute_unit_of_analysis_natural_blocks(self, report: dict[str, Any]) -> dict[str, int]:
        unit_report = report.get("reporte_unit_of_analysis", {})
        sections = unit_report.get("secciones", [])

        section_ii = next((sec for sec in sections if sec.get("id") == "II"), {})
        headers_examples_count = 0
        for punto in section_ii.get("puntos", []) or []:
            for row in punto.get("tabla_formatos", []) or []:
                examples = row.get("ejemplos_contenido_localizacion")
                if not isinstance(examples, str) or not examples.strip():
                    continue
                headers_examples_count += sum(
                    1 for item in re.split(r"[,\n;]+", examples) if item.strip()
                )

        section_vi = next((sec for sec in sections if sec.get("id") == "VI"), {})
        table_types_count = 0
        for part in section_vi.get("partes", []) or []:
            if isinstance(part, dict):
                for key, value in part.items():
                    if key.startswith("tabla_") and isinstance(value, dict):
                        table_types_count += 1
                for subpart in part.get("subpartes", []) or []:
                    if isinstance(subpart, dict) and isinstance(subpart.get("tabla"), dict):
                        table_types_count += 1

        section_iii = next((sec for sec in sections if sec.get("id") == "III"), {})
        causal_patterns_count = 0
        dimensiones = section_iii.get("dimensiones_causales", {})
        if isinstance(dimensiones, dict):
            for dim_data in dimensiones.values():
                if not isinstance(dim_data, dict):
                    continue
                for value in dim_data.values():
                    if isinstance(value, str) and value.strip():
                        causal_patterns_count += 1
                    elif isinstance(value, list):
                        causal_patterns_count += sum(
                            1 for item in value if isinstance(item, str) and item.strip()
                        )

        natural_blocks_total = headers_examples_count + table_types_count + causal_patterns_count
        return {
            "headers_examples_count": headers_examples_count,
            "table_types_count": table_types_count,
            "causal_patterns_count": causal_patterns_count,
            "natural_blocks_total": natural_blocks_total,
        }

    def _build_segmentation_metadata(self, total_segments: int) -> dict[str, Any]:
        base_slots_count = len(ALL_BASE_SLOTS)
        theoretical_max_segments = (
            int(math.ceil(total_segments / base_slots_count)) if total_segments > 0 else 0
        )
        return {
            "base_slots_count": base_slots_count,
            "theoretical_max_segments_per_slot": theoretical_max_segments,
            "expected_segment_budget_by_slot": dict.fromkeys(
                ALL_BASE_SLOTS, theoretical_max_segments
            ),
            "unit_of_analysis_natural_blocks": self._unit_of_analysis_stats,
            "unit_of_analysis_source_path": "pdt_analysis_report.json",
        }

    def extract_semantic_cube(self, document_segments: list[str]) -> dict[str, Any]:
        """Extract multidimensional semantic cube from document segments."""

        if not document_segments:
            return self._empty_semantic_cube()

        # Vectorize segments
        segment_vectors = self._vectorize_segments(document_segments)

        # Initialize semantic cube with 2 dimensions only:
        # - base_slots (D1-Q1..D6-Q5)
        # - policy_domains (PA01-PA10)
        semantic_cube = {
            "dimensions": {
                "base_slots": {slot: [] for slot in ALL_BASE_SLOTS},
                "policy_domains": defaultdict(list),
            },
            "measures": {"semantic_density": [], "coherence_scores": [], "complexity_metrics": []},
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "total_segments": len(document_segments),
                "processing_parameters": {},
                "segmentation": self._build_segmentation_metadata(len(document_segments)),
            },
        }

        # Process each segment
        for idx, segment in enumerate(document_segments):
            segment_data = self._process_segment(segment, idx, segment_vectors[idx])

            # Classify by policy domains (PA01-PA10)
            domain_scores = self._classify_policy_domain(segment)
            selected_policy_area = self._select_policy_area(domain_scores)
            segment_data["policy_area_id"] = selected_policy_area
            segment_data["expected_elements_signals"] = {}

            for domain, score in domain_scores.items():
                if score > 0.0:
                    semantic_cube["dimensions"]["policy_domains"][domain].append(segment_data)

            slot_scores = self._score_base_slots(segment, selected_policy_area, segment_data)
            for slot, score in slot_scores.items():
                if score >= self._slot_thresholds[slot]:
                    semantic_cube["dimensions"]["base_slots"][slot].append(segment_data)

            # Add measures
            semantic_cube["measures"]["semantic_density"].append(segment_data["semantic_density"])
            semantic_cube["measures"]["coherence_scores"].append(segment_data["coherence_score"])

        # Calculate aggregate measures
        if semantic_cube["measures"]["coherence_scores"]:
            if np is not None:
                semantic_cube["measures"]["overall_coherence"] = np.mean(
                    semantic_cube["measures"]["coherence_scores"]
                )
            else:
                semantic_cube["measures"]["overall_coherence"] = sum(
                    semantic_cube["measures"]["coherence_scores"]
                ) / len(semantic_cube["measures"]["coherence_scores"])
        else:
            semantic_cube["measures"]["overall_coherence"] = 0.0

        semantic_cube["measures"]["semantic_complexity"] = self._calculate_semantic_complexity(
            semantic_cube
        )

        logger.info(f"Extracted semantic cube from {len(document_segments)} segments")
        return semantic_cube

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Required artifact missing: {path}")
        return json.loads(path.read_text())

    def _empty_semantic_cube(self) -> dict[str, Any]:
        """Return empty semantic cube structure.

        Dimensions:
        - base_slots: D1-Q1..D6-Q5 (30 analytical base slots)
        - policy_domains: PA01-PA10 (10 policy areas)
        """
        return {
            "dimensions": {
                "base_slots": {slot: [] for slot in ALL_BASE_SLOTS},
                "policy_domains": {},
            },
            "measures": {
                "semantic_density": [],
                "coherence_scores": [],
                "overall_coherence": 0.0,
                "semantic_complexity": 0.0,
            },
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "total_segments": 0,
                "processing_parameters": {},
                "segmentation": self._build_segmentation_metadata(0),
            },
        }

    def _vectorize_segments(self, segments: list[str]) -> np.ndarray:
        """Vectorize document segments using TF-IDF."""
        calibration_path = CAL_ROOT / "analyzer_one_calibration.json"
        generation_cmd = "PYTHONPATH=src python -m calibration.analyzer_one_calibrator"
        if self.vectorizer is None:
            raise RuntimeError(
                "TF-IDF vectorizer unavailable; aborting (no silent fallback). "
                "Exception: RuntimeError: vectorizer is None. "
                f"Expected calibration artifact: {calibration_path}. "
                f"Generate calibration via: {generation_cmd}"
            )
        try:
            return self.vectorizer.fit_transform(segments).toarray()
        except Exception as exc:
            raise RuntimeError(
                "TF-IDF vectorization failed; aborting (no silent fallback). "
                f"Exception: {type(exc).__name__}: {exc}. "
                f"Expected calibration artifact: {calibration_path}. "
                f"Generate calibration via: {generation_cmd}"
            ) from exc

    def _process_segment(self, segment: str, idx: int, vector) -> dict[str, Any]:
        """Process individual segment and extract features."""

        # Basic text statistics
        words = segment.split()

        # Calculate sentence count
        if sent_tokenize is not None:
            try:
                sentences = sent_tokenize(segment)
            except:
                # Fallback to simple splitting
                sentences = [s.strip() for s in re.split(r"[.!?]+", segment) if len(s.strip()) > 10]
        else:
            # Fallback to simple splitting
            sentences = [s.strip() for s in re.split(r"[.!?]+", segment) if len(s.strip()) > 10]

        # Calculate semantic density (simplified)
        semantic_density = len(set(words)) / len(words) if words else 0.0

        # Calculate coherence score (simplified)
        coherence_score = min(1.0, len(sentences) / 10) if sentences else 0.0

        # Convert vector to list if it's a numpy array
        if np is not None and isinstance(vector, np.ndarray):
            vector = vector.tolist()

        return {
            "segment_id": idx,
            "text": segment,
            "vector": vector,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "semantic_density": semantic_density,
            "coherence_score": coherence_score,
        }

    def _select_policy_area(self, domain_scores: dict[str, float]) -> str | None:
        if not domain_scores:
            return None
        max_score = max(domain_scores.values())
        if max_score <= 0.0:
            return None
        best_policy_areas = sorted(
            policy_area_id for policy_area_id, score in domain_scores.items() if score == max_score
        )
        return best_policy_areas[0] if best_policy_areas else None

    def _get_slot_threshold(self, slot: str) -> float:
        if not isinstance(self.thresholds_by_base_slot, dict):
            raise TypeError("Calibration error: thresholds_by_base_slot must be a dict")
        threshold_value = self.thresholds_by_base_slot.get(slot)
        if not isinstance(threshold_value, (int, float)):
            raise KeyError(f"Missing similarity threshold for slot: {slot}")
        threshold = float(threshold_value)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Invalid similarity threshold for slot {slot}: {threshold}")
        return threshold

    def _keyword_score(self, segment_lower: str, keywords: list[str]) -> float:
        if not keywords:
            return 0.0
        match_count = sum(1 for keyword in keywords if keyword.lower() in segment_lower)
        return match_count / len(keywords)

    def _score_d3_q3_expected_elements(self, segment: str, policy_area_id: str) -> dict[str, float]:
        patterns_config = PATTERNS_D3_Q3_BY_POLICY_AREA.get(policy_area_id)
        if not patterns_config:
            return {}
        scores: dict[str, float] = {}
        for element_type in ["trazabilidad_organizacional", "trazabilidad_presupuestal"]:
            patterns = patterns_config.get(element_type, [])
            if not patterns:
                scores[element_type] = 0.0
                continue
            match_count = sum(1 for p in patterns if re.search(p, segment, re.IGNORECASE))
            scores[element_type] = min(1.0, match_count / max(1, len(patterns)))
        return scores

    def _score_base_slots(
        self,
        segment: str,
        policy_area_id: str | None,
        segment_data: dict[str, Any],
    ) -> dict[str, float]:
        segment_lower = segment.lower()
        d3_q3_signals: dict[str, float] = {}
        if policy_area_id is not None:
            d3_q3_signals = self._score_d3_q3_expected_elements(segment, policy_area_id)
        if d3_q3_signals:
            segment_data["expected_elements_signals"]["D3-Q3"] = d3_q3_signals

        slot_scores: dict[str, float] = {}
        for slot in ALL_BASE_SLOTS:
            keywords_general = SLOT_TO_KEYWORDS_GENERAL.get(slot, [])
            keyword_score = self._keyword_score(segment_lower, keywords_general)
            expected_score = 0.0
            if slot == "D3-Q3" and d3_q3_signals:
                expected_score = sum(d3_q3_signals.values()) / len(d3_q3_signals)
            slot_scores[slot] = min(1.0, keyword_score + expected_score)
        return slot_scores

    def _classify_value_chain_link(self, segment: str) -> dict[str, Any]:
        domain_scores = self._classify_policy_domain(segment)
        policy_area_id = self._select_policy_area(domain_scores)
        segment_data: dict[str, Any] = {"expected_elements_signals": {}}
        slot_scores = self._score_base_slots(segment, policy_area_id, segment_data)
        matched_slots = sorted(
            slot for slot, score in slot_scores.items() if score >= self._slot_thresholds[slot]
        )
        best_slot: str | None = None
        best_score = 0.0
        if slot_scores:
            best_score = max(slot_scores.values())
            if best_score > 0.0:
                best_slots = sorted(
                    slot for slot, score in slot_scores.items() if score == best_score
                )
                best_slot = best_slots[0] if best_slots else None
        return {
            "best_slot": best_slot,
            "best_score": best_score,
            "matched_slots": matched_slots,
            "slot_scores": slot_scores,
            "policy_area_id": policy_area_id,
            "expected_elements_signals": segment_data["expected_elements_signals"],
        }

    def _classify_cross_cutting_themes(self, segment: str) -> dict[str, float]:
        _ = segment
        return {}

    def _classify_policy_domain(self, segment: str) -> dict[str, float]:
        """
        Classify segment by Policy Area (PA01-PA10) using keyword matching.

        CANONICAL REFACTORING: Uses frozen policy areas from canonical_specs.py
        Originally extracted from questionnaire_monolith.json, now deterministic.

        Args:
            segment: Text segment to classify

        Returns:
            dict[str, float]: Score per Policy Area.
                Keys: PA01, PA02, PA03, PA04, PA05, PA06, PA07, PA08, PA09, PA10
                Values: Normalized score [0.0-1.0] based on keyword matches

        Contract:
            - Output keys MUST be exactly: {PA01, PA02, PA03, PA04, PA05, PA06, PA07, PA08, PA09, PA10}
            - Output keys MUST NOT be: {economic_development, social_development,
              territorial_development, institutional_development}
            - Scoring: count(matched_keywords) / len(total_keywords_for_PA)
        """
        policy_area_scores: dict[str, float] = {}
        segment_lower = segment.lower()

        for pa_id, keywords in self.ontology.policy_domains.items():
            if not keywords:
                policy_area_scores[pa_id] = 0.0
                continue

            match_count = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in segment_lower:
                    match_count += 1

            policy_area_scores[pa_id] = match_count / len(keywords)

        # Contract assertion: verify output keys
        expected_keys = {f"PA{i:02d}" for i in range(1, 11)}
        actual_keys = set(policy_area_scores.keys())
        if actual_keys != expected_keys:
            logger.error(
                f"_classify_policy_domain output key mismatch. "
                f"Expected: {expected_keys}, Got: {actual_keys}"
            )

        return policy_area_scores

    def _calculate_semantic_complexity(self, semantic_cube: dict[str, Any]) -> float:
        """Calculate semantic complexity of the cube."""

        # Count unique concepts across dimensions
        unique_concepts = set()
        for dimension_data in semantic_cube["dimensions"].values():
            for category, segments in dimension_data.items():
                if segments:
                    unique_concepts.add(category)

        # Normalize complexity
        max_expected_concepts = 20
        return min(1.0, len(unique_concepts) / max_expected_concepts)


# ---------------------------------------------------------------------------
# 3. PERFORMANCE ANALYZER
# ---------------------------------------------------------------------------


class PerformanceAnalyzer:
    """Analyze value chain performance with operational loss functions."""

    def __init__(self, ontology: MunicipalOntology) -> None:
        self.ontology = ontology
        if IsolationForest is not None:
            self.bottleneck_detector = IsolationForest(contamination=0.1, random_state=RANDOM_SEED)
        else:
            self.bottleneck_detector = None

    def analyze_performance(self, semantic_cube: dict[str, Any]) -> dict[str, Any]:
        """Analyze performance indicators across canonical base slots."""

        performance_analysis = {
            "value_chain_metrics": {},
            "bottleneck_analysis": {},
            "operational_loss_functions": {},
            "optimization_recommendations": [],
            "benchmarks": {},
        }

        segmentation = semantic_cube.get("metadata", {}).get("segmentation", {})
        theoretical_max_segments = segmentation.get("theoretical_max_segments_per_slot")
        if not isinstance(theoretical_max_segments, int):
            total_segments = semantic_cube.get("metadata", {}).get("total_segments", 0)
            if not isinstance(total_segments, int):
                raise TypeError("semantic_cube.metadata.total_segments must be an int")
            theoretical_max_segments = (
                int(math.ceil(total_segments / len(ALL_BASE_SLOTS))) if total_segments > 0 else 0
            )

        efficiency_scores: list[float] = []
        throughputs: list[float] = []

        for dim_id, dim in VALUE_CHAIN_DIMENSIONS.items():
            for var_name, var in dim["analytical_variables"].items():
                slot = var["slot"]
                expected_elements = var.get("expected_elements", [])
                slot_segments = semantic_cube["dimensions"]["base_slots"][slot]

                metrics = self._calculate_throughput_metrics(
                    slot, slot_segments, expected_elements, theoretical_max_segments
                )
                bottlenecks = self._detect_bottlenecks(slot, slot_segments, expected_elements)
                efficiency_scores.append(float(metrics["efficiency_score"]))
                throughputs.append(float(metrics["throughput"]))

                performance_analysis["value_chain_metrics"][slot] = {
                    **metrics,
                    "dimension_id": dim_id,
                    "analytical_variable": var_name,
                    "base_slot": slot,
                }
                performance_analysis["bottleneck_analysis"][slot] = bottlenecks

        target_efficiency = self._percentile(efficiency_scores, 75.0)
        target_throughput = self._percentile(throughputs, 75.0)
        performance_analysis["benchmarks"] = {
            "target_efficiency": target_efficiency,
            "target_throughput": target_throughput,
            "percentile": 75.0,
        }

        for slot, metrics in performance_analysis["value_chain_metrics"].items():
            performance_analysis["operational_loss_functions"][slot] = (
                self._calculate_loss_functions(
                    metrics,
                    target_throughput=target_throughput,
                    target_efficiency=target_efficiency,
                )
            )

        # Generate recommendations
        performance_analysis["optimization_recommendations"] = self._generate_recommendations(
            performance_analysis
        )

        logger.info(
            f"Performance analysis completed for {len(performance_analysis['value_chain_metrics'])} base slots"
        )
        return performance_analysis

    def _calculate_throughput_metrics(
        self,
        slot: str,
        segments: list[dict[str, Any]],
        expected_elements: list[str],
        theoretical_max_segments: int,
    ) -> dict[str, Any]:
        """Calculate throughput metrics for a base slot."""

        if not segments:
            return {
                "throughput": 0.0,
                "efficiency_score": 0.0,
                "capacity_utilization": 0.0,
                "segment_count": 0,
                "expected_elements_coverage": 0.0,
                "expected_elements_detail": {},
            }

        total_semantic_content = sum(seg["semantic_density"] for seg in segments)

        if np is not None:
            avg_coherence = np.mean([seg["coherence_score"] for seg in segments])
        else:
            avg_coherence = sum(seg["coherence_score"] for seg in segments) / len(segments)

        if theoretical_max_segments <= 0:
            raise ValueError(
                f"Invalid theoretical_max_segments derived for slot {slot}: {theoretical_max_segments}"
            )
        capacity_utilization = len(segments) / theoretical_max_segments

        # Efficiency score
        efficiency_score = (total_semantic_content / len(segments)) * avg_coherence

        coverage_detail: dict[str, float] = {}
        if expected_elements:
            for element in expected_elements:
                present = sum(
                    1
                    for seg in segments
                    if seg.get("expected_elements_signals", {}).get(slot, {}).get(element, 0.0)
                    > 0.0
                )
                coverage_detail[element] = present / len(segments)
            expected_elements_coverage = sum(coverage_detail.values()) / len(expected_elements)
        else:
            expected_elements_coverage = 0.0

        throughput = len(segments) * avg_coherence

        return {
            "throughput": float(throughput),
            "efficiency_score": float(efficiency_score),
            "capacity_utilization": float(capacity_utilization),
            "segment_count": len(segments),
            "expected_elements_coverage": float(expected_elements_coverage),
            "expected_elements_detail": coverage_detail,
        }

    def _detect_bottlenecks(
        self,
        slot: str,
        segments: list[dict[str, Any]],
        expected_elements: list[str],
    ) -> dict[str, Any]:
        """Detect bottlenecks in a base slot."""

        bottleneck_analysis = {"capacity_constraints": {}, "bottleneck_scores": {}}

        if expected_elements and segments:
            missing = [
                element
                for element in expected_elements
                if all(
                    seg.get("expected_elements_signals", {}).get(slot, {}).get(element, 0.0) <= 0.0
                    for seg in segments
                )
            ]
            missing_ratio = len(missing) / len(expected_elements)
            bottleneck_analysis["bottleneck_scores"]["expected_elements_missing"] = {
                "score": missing_ratio,
                "severity": (
                    "high" if missing_ratio > 0.5 else "medium" if missing_ratio > 0.2 else "low"
                ),
                "missing": missing,
            }

        return bottleneck_analysis

    def _calculate_loss_functions(
        self,
        metrics: dict[str, Any],
        *,
        target_throughput: float,
        target_efficiency: float,
    ) -> dict[str, Any]:
        """Calculate operational loss functions."""

        # Throughput loss (quadratic)
        throughput_gap = max(0, target_throughput - metrics["throughput"])
        throughput_loss = throughput_gap**2

        # Efficiency loss (exponential)
        efficiency_gap = max(0, target_efficiency - metrics["efficiency_score"])

        if np is not None:
            efficiency_loss = np.exp(efficiency_gap * 2) - 1
        else:
            # Approximate exponential function
            efficiency_loss = (1 + efficiency_gap) ** 2 - 1

        capacity_utilization = metrics["capacity_utilization"]
        time_loss = max(0.0, (1 - capacity_utilization) * 10.0)

        # Composite loss
        composite_loss = 0.4 * throughput_loss + 0.4 * efficiency_loss + 0.2 * time_loss

        return {
            "throughput_loss": float(throughput_loss),
            "efficiency_loss": float(efficiency_loss),
            "time_loss": float(time_loss),
            "composite_loss": float(composite_loss),
        }

    @staticmethod
    def _percentile(values: list[float], percentile: float) -> float:
        if not values:
            return 0.0
        if not 0.0 <= percentile <= 100.0:
            raise ValueError(f"Invalid percentile: {percentile}")
        sorted_values = sorted(values)
        if len(sorted_values) == 1:
            return float(sorted_values[0])
        rank = (len(sorted_values) - 1) * (percentile / 100.0)
        lo = int(math.floor(rank))
        hi = int(math.ceil(rank))
        if lo == hi:
            return float(sorted_values[lo])
        fraction = rank - lo
        return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * fraction)

    def _generate_recommendations(
        self, performance_analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate optimization recommendations."""

        recommendations = []

        for link_name, metrics in performance_analysis["value_chain_metrics"].items():
            if metrics["efficiency_score"] < 0.5:
                recommendations.append(
                    {
                        "link": link_name,
                        "type": "efficiency_improvement",
                        "priority": "high",
                        "description": f"Critical efficiency improvement needed for {link_name}",
                    }
                )

            if metrics["throughput"] < 20:
                recommendations.append(
                    {
                        "link": link_name,
                        "type": "throughput_optimization",
                        "priority": "medium",
                        "description": f"Throughput optimization required for {link_name}",
                    }
                )

        return recommendations


# ---------------------------------------------------------------------------
# 4. TEXT MINING ENGINE
# ---------------------------------------------------------------------------


class TextMiningEngine:
    """Advanced text mining for critical diagnosis."""

    def __init__(self, ontology: MunicipalOntology) -> None:
        self.ontology = ontology

        # Initialize simple keyword extractor
        self.stop_words = set()
        if stopwords is not None:
            try:
                self.stop_words = set(stopwords.words("spanish"))
            except LookupError:
                # Download if not available
                try:
                    import nltk

                    nltk.download("stopwords")
                    self.stop_words = set(stopwords.words("spanish"))
                except:
                    logger.warning("Could not download NLTK stopwords. Using empty set.")

    def diagnose_critical_links(
        self, semantic_cube: dict[str, Any], performance_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Diagnose critical base slots."""

        diagnosis_results = {
            "critical_links": {},
            "risk_assessment": {},
            "intervention_recommendations": {},
        }

        # Identify critical links
        critical_links = self._identify_critical_links(performance_analysis)

        for slot, criticality_score in critical_links.items():
            slot_segments = semantic_cube["dimensions"]["base_slots"][slot]

            # Text analysis
            text_analysis = self._analyze_link_text(slot_segments)

            # Risk assessment
            risk_assessment = self._assess_risks(slot_segments, text_analysis)

            # Intervention recommendations
            interventions = self._generate_interventions(slot, risk_assessment, text_analysis)

            diagnosis_results["critical_links"][slot] = {
                "criticality_score": criticality_score,
                "text_analysis": text_analysis,
            }
            diagnosis_results["risk_assessment"][slot] = risk_assessment
            diagnosis_results["intervention_recommendations"][slot] = interventions

        logger.info(f"Diagnosed {len(critical_links)} critical links")
        return diagnosis_results

    def _identify_critical_links(self, performance_analysis: dict[str, Any]) -> dict[str, float]:
        """Identify critical links based on performance metrics."""

        critical_links = {}

        for link_name, metrics in performance_analysis["value_chain_metrics"].items():
            criticality_score = 0.0  # Refactored

            # Low efficiency indicates criticality
            if metrics["efficiency_score"] < 0.5:
                criticality_score += 0.4

            # Low throughput indicates criticality
            if metrics["throughput"] < 20:
                criticality_score += 0.3

            # High loss functions indicate criticality
            if link_name in performance_analysis["operational_loss_functions"]:
                loss = performance_analysis["operational_loss_functions"][link_name][
                    "composite_loss"
                ]
                normalized_loss = min(1.0, loss / 100)
                criticality_score += normalized_loss * 0.3

            if criticality_score > 0.4:
                critical_links[link_name] = criticality_score

        return critical_links

    def _analyze_link_text(self, segments: list[dict]) -> dict[str, Any]:
        """Analyze text content for a link."""

        if not segments:
            return {"word_count": 0, "keywords": [], "sentiment": "neutral"}

        # Combine all text
        combined_text = " ".join([seg["text"] for seg in segments])
        words = [
            word.lower()
            for word in combined_text.split()
            if word.lower() not in self.stop_words and len(word) > 2
        ]

        # Extract keywords
        word_freq = Counter(words)
        keywords = [word for word, count in word_freq.most_common(10)]

        # Simple sentiment analysis
        positive_words = ["bueno", "excelente", "positivo", "lograr", "éxito"]
        negative_words = ["problema", "dificultad", "limitación", "falta", "déficit"]

        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "word_count": len(words),
            "keywords": keywords,
            "sentiment": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
        }

    def _assess_risks(self, segments: list[dict], text_analysis: dict[str, Any]) -> dict[str, Any]:
        """Assess risks for a value chain link."""

        risk_assessment = {"overall_risk": "low", "risk_factors": []}

        # Sentiment-based risk
        if text_analysis["sentiment"] == "negative":
            risk_assessment["risk_factors"].append("Negative sentiment detected")

        # Content-based risk
        if text_analysis["negative_indicators"] > 3:
            risk_assessment["risk_factors"].append("High frequency of negative indicators")

        # Volume-based risk
        if text_analysis["word_count"] < 50:
            risk_assessment["risk_factors"].append("Limited content volume")

        # Overall risk level
        if len(risk_assessment["risk_factors"]) > 2:
            risk_assessment["overall_risk"] = "high"
        elif len(risk_assessment["risk_factors"]) > 0:
            risk_assessment["overall_risk"] = "medium"

        return risk_assessment

    def _generate_interventions(
        self, link_name: str, risk_assessment: dict[str, Any], text_analysis: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Generate intervention recommendations."""

        interventions = []

        if risk_assessment["overall_risk"] == "high":
            interventions.append(
                {
                    "type": "immediate",
                    "description": f"Priority intervention required for {link_name}",
                    "timeline": "1-3 months",
                }
            )

        if text_analysis["sentiment"] == "negative":
            interventions.append(
                {
                    "type": "stakeholder_engagement",
                    "description": "Address concerns through stakeholder engagement",
                    "timeline": "ongoing",
                }
            )

        if text_analysis["word_count"] < 50:
            interventions.append(
                {
                    "type": "documentation",
                    "description": "Improve documentation and content development",
                    "timeline": "3-6 months",
                }
            )

        return interventions


# ---------------------------------------------------------------------------
# 5. COMPREHENSIVE ANALYZER
# ---------------------------------------------------------------------------


class MunicipalAnalyzer:
    """Main analyzer integrating all components."""

    def __init__(self) -> None:
        self.ontology = MunicipalOntology()
        self.semantic_analyzer = SemanticAnalyzer(self.ontology)
        self.performance_analyzer = PerformanceAnalyzer(self.ontology)
        self.text_miner = TextMiningEngine(self.ontology)

        logger.info("MunicipalAnalyzer initialized successfully")

    def analyze_document(self, document_path: str) -> dict[str, Any]:
        """Perform comprehensive analysis of a municipal document."""

        start_time = time.time()
        logger.info(f"Starting analysis of {document_path}")

        try:
            # Load and process document
            document_segments = self._load_document(document_path)

            # Semantic analysis
            logger.info("Performing semantic analysis...")
            semantic_cube = self.semantic_analyzer.extract_semantic_cube(document_segments)

            # Performance analysis
            logger.info("Analyzing performance indicators...")
            performance_analysis = self.performance_analyzer.analyze_performance(semantic_cube)

            # Text mining and diagnosis
            logger.info("Performing text mining and diagnosis...")
            critical_diagnosis = self.text_miner.diagnose_critical_links(
                semantic_cube, performance_analysis
            )

            # Compile results
            results = {
                "document_path": document_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": time.time() - start_time,
                "semantic_cube": semantic_cube,
                "performance_analysis": performance_analysis,
                "critical_diagnosis": critical_diagnosis,
                "summary": self._generate_summary(
                    semantic_cube, performance_analysis, critical_diagnosis
                ),
            }

            logger.info(f"Analysis completed in {time.time() - start_time:.2f} seconds")
            return results

        except Exception as e:
            logger.error(f"Analysis failed: {e!s}")
            raise

    def _load_document(self, document_path: str) -> list[str]:
        """Load and segment document."""

        # Delegate to factory for I/O operation
# DELETED_MODULE:         from farfan_pipeline.analysis.factory import read_text_file

        content = read_text_file(document_path)

        # Simple sentence segmentation
        sentences = re.split(r"[.!?]+", content)

        # Clean and filter segments
        segments = []
        for sentence in sentences:
            cleaned = sentence.strip()
            if len(cleaned) > 20 and not cleaned.startswith(("Página", "Page")):
                segments.append(cleaned)

        return segments[:100]  # Limit for processing efficiency

    def _generate_summary(
        self,
        semantic_cube: dict[str, Any],
        performance_analysis: dict[str, Any],
        critical_diagnosis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate executive summary of analysis."""

        # Count dimensions
        total_segments = semantic_cube["metadata"]["total_segments"]
        base_slots_covered = sum(
            1 for segments in semantic_cube["dimensions"]["base_slots"].values() if segments
        )
        policy_domain_coverage = len(semantic_cube["dimensions"]["policy_domains"])

        # Performance summary
        if performance_analysis["value_chain_metrics"]:
            if np is not None:
                avg_efficiency = np.mean(
                    [
                        metrics["efficiency_score"]
                        for metrics in performance_analysis["value_chain_metrics"].values()
                    ]
                )
            else:
                avg_efficiency = sum(
                    metrics["efficiency_score"]
                    for metrics in performance_analysis["value_chain_metrics"].values()
                ) / len(performance_analysis["value_chain_metrics"])
        else:
            avg_efficiency = 0.0  # Refactored

        # Critical links count
        critical_links_count = len(critical_diagnosis["critical_links"])

        return {
            "document_coverage": {
                "total_segments_analyzed": total_segments,
                "base_slots_covered": base_slots_covered,
                "policy_domains_covered": policy_domain_coverage,
            },
            "performance_summary": {
                "average_efficiency_score": float(avg_efficiency),
                "recommendations_count": len(performance_analysis["optimization_recommendations"]),
            },
            "risk_assessment": {
                "critical_links_identified": critical_links_count,
                "overall_risk_level": (
                    "high"
                    if critical_links_count > 2
                    else "medium" if critical_links_count > 0 else "low"
                ),
            },
        }


# ---------------------------------------------------------------------------
# 6. EXAMPLE USAGE AND UTILITIES
# ---------------------------------------------------------------------------


def example_usage():
    """Example usage of the Municipal Analyzer."""

    # Initialize analyzer
    analyzer = MunicipalAnalyzer()

    # Create sample document
    sample_text = """
    El Plan de Desarrollo Municipal tiene como objetivo principal fortalecer
    la capacidad institucional y mejorar la calidad de vida de los habitantes.

    En el área de desarrollo económico, se implementarán programas de
    emprendimiento y competitividad empresarial. Los recursos asignados
    permitirán crear 500 nuevos empleos en el sector productivo.

    Para el desarrollo social, se priorizarán proyectos de educación y salud.
    Se construirán 3 nuevos centros de salud y se mejorarán 10 instituciones
    educativas. El presupuesto destinado asciende a 2.5 millones de pesos.

    La estrategia de implementación incluye mecanismos de participación
    ciudadana y seguimiento continuo a través de indicadores de gestión.
    Se establecerán alianzas con el sector privado y organizaciones sociales.

    Los principales riesgos identificados incluyen limitaciones presupuestales
    y posibles cambios en el contexto político. Se requiere fortalecer
    la coordinación interinstitucional para garantizar el éxito.
    """

    # Save sample to file
    # Delegate to factory for I/O operation
# DELETED_MODULE:     from farfan_pipeline.analysis.factory import write_text_file

    write_text_file(sample_text, SAMPLE_MUNICIPAL_PLAN)

    try:
        # Analyze document
        results = analyzer.analyze_document(SAMPLE_MUNICIPAL_PLAN)

        # Print summary
        print("\n" + "=" * 60)
        print("MUNICIPAL DEVELOPMENT PLAN ANALYSIS")
        print("=" * 60)

        print(f"\nDocument: {results['document_path']}")
        print(f"Processing time: {results['processing_time_seconds']:.2f} seconds")

        # Semantic analysis summary
        print("\nSEMANTIC ANALYSIS:")
        cube = results["semantic_cube"]
        print(f"- Total segments processed: {cube['metadata']['total_segments']}")
        print(f"- Overall coherence: {cube['measures']['overall_coherence']:.2f}")
        print(f"- Semantic complexity: {cube['measures']['semantic_complexity']:.2f}")

        print("\nBase Slots Covered:")
        for slot, segments in cube["dimensions"]["base_slots"].items():
            if segments:
                print(f"  - {slot}: {len(segments)} segments")

        print("\nPolicy Domains Covered:")
        for domain, segments in cube["dimensions"]["policy_domains"].items():
            print(f"  - {domain}: {len(segments)} segments")

        # Performance analysis summary
        print("\nPERFORMANCE ANALYSIS:")
        perf = results["performance_analysis"]
        for link, metrics in perf["value_chain_metrics"].items():
            print(f"\n{link.replace('_', ' ').title()}:")
            print(f"  - Efficiency: {metrics['efficiency_score']:.2f}")
            print(f"  - Throughput: {metrics['throughput']:.1f}")
            print(f"  - Capacity utilization: {metrics['capacity_utilization']:.2f}")

        print(f"\nOptimization Recommendations: {len(perf['optimization_recommendations'])}")
        for rec in perf["optimization_recommendations"][:3]:  # Show top 3
            print(f"  - {rec['description']} (Priority: {rec['priority']})")

        # Critical diagnosis summary
        print("\nCRITICAL DIAGNOSIS:")
        diagnosis = results["critical_diagnosis"]
        print(f"Critical links identified: {len(diagnosis['critical_links'])}")

        for link, info in diagnosis["critical_links"].items():
            print(f"\n{link.replace('_', ' ').title()}:")
            print(f"  - Criticality score: {info['criticality_score']:.2f}")
            text_analysis = info["text_analysis"]
            print(f"  - Sentiment: {text_analysis['sentiment']}")
            print(f"  - Key words: {', '.join(text_analysis['keywords'][:5])}")

            # Show risk assessment
            if link in diagnosis["risk_assessment"]:
                risk = diagnosis["risk_assessment"][link]
                print(f"  - Risk level: {risk['overall_risk']}")
                if risk["risk_factors"]:
                    print(f"  - Risk factors: {len(risk['risk_factors'])}")

            # Show interventions
            if link in diagnosis["intervention_recommendations"]:
                interventions = diagnosis["intervention_recommendations"][link]
                print(f"  - Recommended interventions: {len(interventions)}")

        # Overall summary
        print("\nEXECUTIVE SUMMARY:")
        summary = results["summary"]
        print(
            f"- Document coverage: {summary['document_coverage']['total_segments_analyzed']} segments"
        )
        print(
            f"- Average efficiency: {summary['performance_summary']['average_efficiency_score']:.2f}"
        )
        print(f"- Overall risk level: {summary['risk_assessment']['overall_risk_level']}")

        return results

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None
    finally:
        # Clean up
        try:
            import os

            os.remove(SAMPLE_MUNICIPAL_PLAN)
        except (FileNotFoundError, OSError):
            pass


@dataclass
class CanonicalQuestionContract:
    """Canonical contract for evidence collection (method capability metadata).

    CANONICAL REFACTORING: legacy_question_id kept for traceability only.
    Contract defines evidence requirements (what the method needs), not Q-to-method routing.
    """

    legacy_question_id: str  # LEGACY: For traceability, not routing
    policy_area_id: str
    dimension_id: str
    question_number: int
    expected_elements: list[str]
    search_patterns: dict[str, Any]
    verification_patterns: list[str]
    evaluation_criteria: dict[str, Any]
    question_template: str
    scoring_modality: str
    evidence_sources: dict[str, Any]
    policy_area_legacy: str
    dimension_legacy: str
    canonical_question_id: str = ""
    contract_hash: str = ""


@dataclass
class EvidenceSegment:
    """Single segment of text matched against a question contract."""

    segment_index: int
    segment_text: str
    segment_hash: str
    matched_patterns: list[str]


class CanonicalQuestionSegmenter:
    """Deterministic segmenter using frozen canonical patterns.

    CANONICAL REFACTORING: No longer loads questionnaire at runtime.
    Uses PDT/PDM structure patterns from canonical_specs.py
    """

    def __init__(
        self,
        questionnaire_path: str = "questionnaire.json",  # DEPRECATED: Kept for backward compat
        rubric_path: str = "rubric_scoring_FIXED.json",
        segmentation_method: str = "paragraph",
    ) -> None:
        self.questionnaire_path = Path(questionnaire_path)
        self.rubric_path = Path(rubric_path)
        self.segmentation_method = segmentation_method

        (
            self.contracts,
            self.questionnaire_metadata,
            self.rubric_metadata,
            self.contracts_hash,
        ) = DocumentProcessor.load_canonical_question_contracts(
            questionnaire_path=questionnaire_path,
            rubric_path=rubric_path,
        )

    def segment_plan(self, plan_text: str) -> dict[str, Any]:
        """Segment *plan_text* and emit evidence manifests per canonical contract."""

        normalized_text = plan_text or ""
        segments = DocumentProcessor.segment_text(
            normalized_text,
            method=self.segmentation_method,
        )
        normalized_segments = [
            segment.strip() for segment in segments if segment and segment.strip()
        ]

        matched_contracts = 0
        question_segments: dict[tuple[str, str, str], dict[str, Any]] = {}

        for contract in self.contracts:
            manifest = self._build_manifest(contract, normalized_segments)
            if manifest["matched"]:
                matched_contracts += 1

            key_tuple = (
                contract.canonical_question_id,
                contract.policy_area_id,
                contract.dimension_id,
            )

            question_segments[key_tuple] = {
                "legacy_question_id": contract.legacy_question_id,
                "policy_area_id": contract.policy_area_id,
                "dimension_id": contract.dimension_id,
                "policy_area_legacy": contract.policy_area_legacy,
                "dimension_legacy": contract.dimension_legacy,
                "question_number": contract.question_number,
                "question_template": contract.question_template,
                "scoring_modality": contract.scoring_modality,
                "evidence_sources": contract.evidence_sources,
                "contract_hash": contract.contract_hash,
                "evidence_manifest": manifest,
            }

        total_contracts = len(self.contracts)
        metadata = {
            "questionnaire_version": self.questionnaire_metadata.get("version"),
            "rubric_version": self.rubric_metadata.get("version"),
            "total_contracts": total_contracts,
            "covered_contracts": matched_contracts,
            "coverage_ratio": (matched_contracts / total_contracts if total_contracts else 0.0),
            "total_segments": len(normalized_segments),
            "input_sha256": hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
            "contracts_sha256": self.contracts_hash,
            "segmentation_method": self.segmentation_method,
        }

        question_segment_index = [
            {
                "key_tuple": list(key_tuple),
                "canonical_question_id": key_tuple[0],
                "policy_area_id": key_tuple[1],
                "dimension_id": key_tuple[2],
                "legacy_question_id": payload["legacy_question_id"],
                "contract_hash": payload["contract_hash"],
                "evidence_manifest": payload["evidence_manifest"],
            }
            for key_tuple, payload in question_segments.items()
        ]

        return {
            "metadata": metadata,
            "question_segments": question_segments,
            "question_segment_index": question_segment_index,
        }

    def _build_manifest(
        self,
        contract: CanonicalQuestionContract,
        segments: list[str],
    ) -> dict[str, Any]:
        """Build deterministic evidence manifest for *contract* across *segments*."""

        compiled_patterns: list[tuple[str, Any]] = []
        for element, spec in contract.search_patterns.items():
            pattern = spec.get("pattern") if isinstance(spec, dict) else None
            if not pattern or not isinstance(pattern, str):
                continue
            try:
                compiled_patterns.append(
                    (element, re.compile(pattern, flags=re.IGNORECASE | re.MULTILINE))
                )
            except re.error:
                logger.debug(
                    "Invalid regex pattern skipped",
                    extra={"question_id": contract.legacy_question_id, "pattern": pattern},
                )

        for index, pattern in enumerate(contract.verification_patterns):
            if not pattern or not isinstance(pattern, str):
                continue
            try:
                compiled_patterns.append(
                    (
                        f"verification_{index}",
                        re.compile(pattern, flags=re.IGNORECASE | re.MULTILINE),
                    )
                )
            except re.error:
                logger.debug(
                    "Invalid verification pattern skipped",
                    extra={
                        "question_id": contract.legacy_question_id,
                        "pattern_index": index,
                    },
                )

        matched_segments: list[EvidenceSegment] = []
        pattern_hits: dict[str, int] = {}

        for segment_index, segment_text in enumerate(segments):
            matched_labels: list[str] = []
            for label, pattern in compiled_patterns:
                if pattern.search(segment_text):
                    matched_labels.append(label)

            if matched_labels:
                unique_labels = sorted(set(matched_labels))
                segment_hash = hashlib.sha256(segment_text.encode("utf-8")).hexdigest()
                matched_segments.append(
                    EvidenceSegment(
                        segment_index=segment_index,
                        segment_text=segment_text,
                        segment_hash=segment_hash,
                        matched_patterns=unique_labels,
                    )
                )

                for label in unique_labels:
                    pattern_hits[label] = pattern_hits.get(label, 0) + 1

        manifest_segments = [
            {
                "segment_index": segment.segment_index,
                "segment_text": segment.segment_text,
                "segment_hash": segment.segment_hash,
                "matched_patterns": segment.matched_patterns,
            }
            for segment in matched_segments
        ]

        segment_hash_chain = (
            hashlib.sha256(
                "".join(segment["segment_hash"] for segment in manifest_segments).encode("utf-8")
            ).hexdigest()
            if manifest_segments
            else "0" * 64
        )

        return {
            "matched": bool(manifest_segments),
            "matched_segment_count": len(manifest_segments),
            "expected_elements": contract.expected_elements,
            "search_patterns": contract.search_patterns,
            "verification_patterns": contract.verification_patterns,
            "evaluation_criteria": contract.evaluation_criteria,
            "pattern_hits": pattern_hits,
            "matched_segments": manifest_segments,
            "attestation": {
                "contract_sha256": contract.contract_hash,
                "segment_hash_chain": segment_hash_chain,
            },
        }


class DocumentProcessor:
    """Utility class for document processing."""

    @staticmethod
    def load_pdf(pdf_path: str) -> str:
        """Load text from PDF file."""
        try:
            # Delegate to factory for I/O operation
            # Note: PyPDF2 requires file handle, so we need a special approach
            from pathlib import Path

            import PyPDF2

            pdf_path_obj = Path(pdf_path)

            with open(pdf_path_obj, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return ""

    @staticmethod
    def load_docx(docx_path: str) -> str:
        """Load text from DOCX file."""
        try:
            import docx

            doc = docx.Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not available. Install with: pip install python-docx")
            return ""
        except Exception as e:
            logger.error(f"Error loading DOCX: {e}")
            return ""

    @staticmethod
    def segment_text(text: str, method: str = "sentence") -> list[str]:
        """Segment text using different methods."""

        if method == "sentence":
            # Use NLTK sentence tokenizer if available
            if sent_tokenize is not None:
                try:
                    return sent_tokenize(text, language="spanish")
                except LookupError:
                    # Download if not available
                    try:
                        import nltk

                        nltk.download("punkt")
                        return sent_tokenize(text, language="spanish")
                    except:
                        # Fallback to simple splitting
                        return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]
                except Exception:
                    # Fallback to simple splitting
                    return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]
            else:
                # Fallback to simple splitting
                return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]

        elif method == "paragraph":
            return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]

        elif method == "fixed_length":
            words = text.split()
            segments = []
            segment_length = 50  # words per segment

            for i in range(0, len(words), segment_length):
                segment = " ".join(words[i : i + segment_length])
                if len(segment) > 20:
                    segments.append(segment)

            return segments

        else:
            raise ValueError(f"Unknown segmentation method: {method}")

    @staticmethod
    def load_canonical_question_contracts(
        questionnaire_path: str = "questionnaire.json",
        rubric_path: str = "rubric_scoring_FIXED.json",
    ) -> tuple[list[CanonicalQuestionContract], dict[str, Any], dict[str, Any], str]:
        """Load canonical question contracts based on questionnaire and rubric."""

        questionnaire_file = Path(questionnaire_path)
        rubric_file = Path(rubric_path)

        if not questionnaire_file.exists():
            raise FileNotFoundError(f"Questionnaire file not found: {questionnaire_file}")
        if not rubric_file.exists():
            raise FileNotFoundError(f"Rubric file not found: {rubric_file}")

        # Delegate to factory for I/O operation
# DELETED_MODULE:         from farfan_pipeline.analysis.factory import load_json

        questionnaire_data = load_json(questionnaire_file)
        rubric_data = load_json(rubric_file)

        questionnaire_meta = questionnaire_data.get("metadata", {})
        rubric_meta = rubric_data.get("metadata", {})

        policy_area_mapping = questionnaire_meta.get("policy_area_mapping", {})
        inverse_policy_area_map = {
            legacy: canonical
            for canonical, legacy in policy_area_mapping.items()
            if isinstance(legacy, str)
        }

        base_questions = questionnaire_data.get("preguntas_base", [])
        questionnaire_lookup: dict[tuple[str, str, int], dict[str, Any]] = {}
        for question in base_questions:
            if not isinstance(question, dict):
                continue
            legacy_question_id = question.get("id")
            if not legacy_question_id:
                continue
            legacy_policy_area = (
                question.get("metadata", {}).get("policy_area") or legacy_question_id.split("-")[0]
            )
            dimension_legacy = question.get("dimension") or legacy_question_id.split("-")[1]
            try:
                question_number = int(str(question.get("numero")))
            except (TypeError, ValueError):
                question_number = 0
            key = (legacy_policy_area, dimension_legacy, question_number)
            questionnaire_lookup[key] = question

        rubric_questions = rubric_data.get("questions", [])
        rubric_lookup: dict[tuple[str, str, int], dict[str, Any]] = {}
        for question in rubric_questions:
            if not isinstance(question, dict):
                continue
            legacy_question_id = question.get("id")
            if not legacy_question_id:
                continue
            legacy_policy_area = question.get("policy_area") or legacy_question_id.split("-")[0]
            dimension_legacy = question.get("dimension") or legacy_question_id.split("-")[1]
            try:
                raw_number = int(str(question.get("question_no")))
            except (TypeError, ValueError):
                raw_number = 0
            normalized_number = ((raw_number - 1) % 5) + 1 if raw_number else 0
            key = (legacy_policy_area, dimension_legacy, normalized_number)
            rubric_lookup[key] = question

        common_keys = sorted(set(questionnaire_lookup.keys()) & set(rubric_lookup.keys()))
        if not common_keys:
            raise ValueError(
                "No overlapping question definitions between questionnaire and rubric metadata"
            )

        contracts: list[CanonicalQuestionContract] = []

        for key in common_keys:
            questionnaire_entry = questionnaire_lookup[key]
            rubric_entry = rubric_lookup[key]
            legacy_question_id = questionnaire_entry.get("id") or rubric_entry.get("id")

            legacy_policy_area = questionnaire_entry.get("metadata", {}).get(
                "policy_area"
            ) or rubric_entry.get("policy_area", "")
            canonical_policy_area = inverse_policy_area_map.get(
                legacy_policy_area,
                DocumentProcessor._default_policy_area_id(legacy_policy_area),
            )

            dimension_legacy = questionnaire_entry.get("dimension") or rubric_entry.get(
                "dimension", ""
            )
            canonical_dimension = DocumentProcessor._to_canonical_dimension_id(dimension_legacy)

            question_number_value = (
                rubric_entry.get("question_no")
                if rubric_entry.get("question_no") is not None
                else questionnaire_entry.get("numero")
            )
            try:
                question_number = int(str(question_number_value).lstrip("Qq"))
            except (TypeError, ValueError):
                question_number = 0

            expected_elements = rubric_entry.get("expected_elements", [])
            if not isinstance(expected_elements, list):
                expected_elements = []

            search_patterns = rubric_entry.get("search_patterns", {})
            if not isinstance(search_patterns, dict):
                search_patterns = {}

            verification_patterns = questionnaire_entry.get("patrones_verificacion", [])
            if not isinstance(verification_patterns, list):
                verification_patterns = []

            evaluation_criteria = questionnaire_entry.get("criterios_evaluacion", {})
            if not isinstance(evaluation_criteria, dict):
                evaluation_criteria = {}

            evidence_sources = rubric_entry.get("evidence_sources", {})
            if not isinstance(evidence_sources, dict):
                evidence_sources = {}

            contract = CanonicalQuestionContract(
                legacy_question_id=legacy_question_id,
                policy_area_id=canonical_policy_area,
                dimension_id=canonical_dimension,
                question_number=question_number,
                expected_elements=expected_elements,
                search_patterns=search_patterns,
                verification_patterns=verification_patterns,
                evaluation_criteria=evaluation_criteria,
                question_template=(
                    rubric_entry.get("template") or questionnaire_entry.get("texto_template", "")
                ),
                scoring_modality=rubric_entry.get("scoring_modality", ""),
                evidence_sources=evidence_sources,
                policy_area_legacy=legacy_policy_area,
                dimension_legacy=dimension_legacy,
            )

            contracts.append(contract)

        contracts.sort(
            key=lambda contract: (
                contract.policy_area_id,
                contract.dimension_id,
                contract.question_number,
                contract.legacy_question_id,
            )
        )

        for index, contract in enumerate(contracts, start=1):
            canonical_question_id = f"Q{index:03d}"
            contract.canonical_question_id = canonical_question_id
            payload = {
                "canonical_question_id": canonical_question_id,
                "legacy_question_id": contract.legacy_question_id,
                "policy_area_id": contract.policy_area_id,
                "dimension_id": contract.dimension_id,
                "question_number": contract.question_number,
                "expected_elements": contract.expected_elements,
                "search_patterns": contract.search_patterns,
                "verification_patterns": contract.verification_patterns,
                "evaluation_criteria": contract.evaluation_criteria,
                "question_template": contract.question_template,
                "scoring_modality": contract.scoring_modality,
                "evidence_sources": contract.evidence_sources,
            }
            contract.contract_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()

        contracts_hash = (
            hashlib.sha256(
                "".join(contract.contract_hash for contract in contracts).encode("utf-8")
            ).hexdigest()
            if contracts
            else "0" * 64
        )

        return contracts, questionnaire_meta, rubric_meta, contracts_hash

    @staticmethod
    def segment_by_canonical_questionnaire(
        plan_text: str,
        questionnaire_path: str = "questionnaire.json",
        rubric_path: str = "rubric_scoring_FIXED.json",
        segmentation_method: str = "paragraph",
    ) -> dict[str, Any]:
        """Convenience wrapper to segment plan text using canonical contracts."""

        segmenter = CanonicalQuestionSegmenter(
            questionnaire_path=questionnaire_path,
            rubric_path=rubric_path,
            segmentation_method=segmentation_method,
        )
        return segmenter.segment_plan(plan_text)

    @staticmethod
    def _default_policy_area_id(legacy_policy_area: str) -> str:
        """Convert legacy policy-area code into canonical PAxx format."""

        if isinstance(legacy_policy_area, str) and legacy_policy_area.startswith("P"):
            try:
                return f"PA{int(legacy_policy_area[1:]):02d}"
            except ValueError:
                return legacy_policy_area
        return legacy_policy_area

    @staticmethod
    def _to_canonical_dimension_id(dimension_code: str) -> str:
        """Convert legacy dimension code (e.g., D1) into canonical DIMxx format."""

        if isinstance(dimension_code, str) and dimension_code.startswith("D"):
            try:
                return f"DIM{int(dimension_code[1:]):02d}"
            except ValueError:
                return dimension_code
        return dimension_code


class ResultsExporter:
    """Export analysis results to different formats."""

    @staticmethod
    def export_to_json(results: dict[str, Any], output_path: str) -> None:
        """Export results to JSON file."""
        # Delegate to factory for I/O operation
# DELETED_MODULE:         from farfan_pipeline.analysis.factory import save_json

        try:
            save_json(results, output_path)
            logger.info(f"Results exported to JSON: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

    @staticmethod
    def export_to_excel(results: dict[str, Any], output_path: str) -> None:
        """Export results to Excel file."""
        if pd is None:
            logger.warning("pandas not available. Install with: pip install pandas openpyxl")
            return

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

                # Summary sheet
                summary_data = []
                summary = results.get("summary", {})

                for category, data in summary.items():
                    if isinstance(data, dict):
                        for key, value in data.items():
                            summary_data.append(
                                {"Category": category, "Metric": key, "Value": value}
                            )

                if summary_data:
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

                # Performance metrics sheet
                perf_data = []
                perf_analysis = results.get("performance_analysis", {})

                for link, metrics in perf_analysis.get("value_chain_metrics", {}).items():
                    perf_data.append(
                        {
                            "Value_Chain_Link": link,
                            "Efficiency_Score": metrics.get("efficiency_score", 0),
                            "Throughput": metrics.get("throughput", 0),
                            "Capacity_Utilization": metrics.get("capacity_utilization", 0),
                            "Segment_Count": metrics.get("segment_count", 0),
                        }
                    )

                if perf_data:
                    pd.DataFrame(perf_data).to_excel(writer, sheet_name="Performance", index=False)

                # Recommendations sheet
                rec_data = []
                recommendations = perf_analysis.get("optimization_recommendations", [])

                for i, rec in enumerate(recommendations):
                    rec_data.append(
                        {
                            "Recommendation_ID": i + 1,
                            "Link": rec.get("link", ""),
                            "Type": rec.get("type", ""),
                            "Priority": rec.get("priority", ""),
                            "Description": rec.get("description", ""),
                        }
                    )

                if rec_data:
                    pd.DataFrame(rec_data).to_excel(
                        writer, sheet_name="Recommendations", index=False
                    )

            logger.info(f"Results exported to Excel: {output_path}")

        except ImportError:
            logger.warning("openpyxl not available. Install with: pip install openpyxl")
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")

    @staticmethod
    def export_summary_report(results: dict[str, Any], output_path: str) -> None:
        """Export a summary report in text format."""

        try:
            # Build content first
            lines = []
            lines.append("MUNICIPAL DEVELOPMENT PLAN ANALYSIS REPORT\n")
            lines.append("=" * 50 + "\n\n")

            # Basic info
            lines.append(f"Document: {results.get('document_path', 'Unknown')}\n")
            lines.append(f"Analysis Date: {results.get('analysis_timestamp', 'Unknown')}\n")
            lines.append(
                f"Processing Time: {results.get('processing_time_seconds', 0):.2f} seconds\n\n"
            )

            # Summary
            summary = results.get("summary", {})
            lines.append("EXECUTIVE SUMMARY\n")
            lines.append("-" * 20 + "\n")

            doc_coverage = summary.get("document_coverage", {})
            lines.append(f"Segments Analyzed: {doc_coverage.get('total_segments_analyzed', 0)}\n")
            lines.append(f"Base Slots Covered: {doc_coverage.get('base_slots_covered', 0)}\n")
            lines.append(f"Policy Domains: {doc_coverage.get('policy_domains_covered', 0)}\n")

            perf_summary = summary.get("performance_summary", {})
            lines.append(
                f"Average Efficiency: {perf_summary.get('average_efficiency_score', 0):.2f}\n"
            )

            risk_summary = summary.get("risk_assessment", {})
            lines.append(
                f"Overall Risk Level: {risk_summary.get('overall_risk_level', 'Unknown')}\n\n"
            )

            # Performance details
            lines.append("PERFORMANCE ANALYSIS\n")
            lines.append("-" * 20 + "\n")

            perf_analysis = results.get("performance_analysis", {})
            for link, metrics in perf_analysis.get("value_chain_metrics", {}).items():
                lines.append(f"\n{link.replace('_', ' ').title()}:\n")
                lines.append(f"  Efficiency: {metrics.get('efficiency_score', 0):.2f}\n")
                lines.append(f"  Throughput: {metrics.get('throughput', 0):.1f}\n")
                lines.append(f"  Capacity: {metrics.get('capacity_utilization', 0):.2f}\n")

            # Recommendations
            lines.append("\n\nRECOMMENDATE OPTIONS\n")
            lines.append("-" * 20 + "\n")

            recommendations = perf_analysis.get("optimization_recommendations", [])
            for i, rec in enumerate(recommendations, 1):
                lines.append(
                    f"{i}. {rec.get('description', '')} (Priority: {rec.get('priority', '')})\n"
                )

            # Critical links
            lines.append("\n\nCRITICAL LINKS\n")
            lines.append("-" * 15 + "\n")

            diagnosis = results.get("critical_diagnosis", {})
            for link, info in diagnosis.get("critical_links", {}).items():
                lines.append(f"\n{link.replace('_', ' ').title()}:\n")
                lines.append(f"  Criticality: {info.get('criticality_score', 0):.2f}\n")

                text_analysis = info.get("text_analysis", {})
                lines.append(f"  Sentiment: {text_analysis.get('sentiment', 'neutral')}\n")

                if link in diagnosis.get("risk_assessment", {}):
                    risk = diagnosis["risk_assessment"][link]
                    lines.append(f"  Risk Level: {risk.get('overall_risk', 'unknown')}\n")

            # Delegate to factory for I/O operation
# DELETED_MODULE:             from farfan_pipeline.analysis.factory import write_text_file

            write_text_file("".join(lines), output_path)
            logger.info(f"Summary report exported: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting summary report: {e}")


# ---------------------------------------------------------------------------
# 7. MAIN EXECUTION
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 8. ADDITIONAL UTILITIES FOR PRODUCTION USE
# ---------------------------------------------------------------------------


class ConfigurationManager:
    """Manage analyzer configuration."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = config_path or "analyzer_config.json"
        self.config = self.load_config()

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file or create default."""

        default_config = {
            "processing": {
                "max_segments": 200,
                "min_segment_length": 20,
                "segmentation_method": "sentence",
            },
            "analysis": {
                "criticality_threshold": 0.4,
                "efficiency_threshold": 0.5,
                "throughput_threshold": 20,
            },
            "export": {"include_raw_data": False, "export_formats": ["json", "excel", "summary"]},
        }

        if Path(self.config_path).exists():
            # Delegate to factory for I/O operation
# DELETED_MODULE:             from farfan_pipeline.analysis.factory import load_json

            try:
                user_config = load_json(self.config_path)
                # Merge with defaults
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")

        return default_config

    def save_config(self) -> None:
        """Save current configuration to file."""
        # Delegate to factory for I/O operation
# DELETED_MODULE:         from farfan_pipeline.analysis.factory import save_json

        try:
            save_json(self.config, self.config_path)
        except Exception as e:
            logger.error(f"Error saving config: {e}")


class BatchProcessor:
    """Process multiple documents in batch."""

    def __init__(self, analyzer: MunicipalAnalyzer) -> None:
        self.analyzer = analyzer

    def process_directory(self, directory_path: str, pattern: str = "*.txt") -> dict[str, Any]:
        """Process all files matching pattern in directory."""

        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")

        files = list(directory.glob(pattern))
        results = {}

        logger.info(f"Processing {len(files)} files from {directory_path}")

        for file_path in files:
            try:
                logger.info(f"Processing: {file_path.name}")
                result = self.analyzer.analyze_document(str(file_path))
                results[file_path.name] = result
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                results[file_path.name] = {"error": str(e)}

        return results

    def export_batch_results(self, batch_results: dict[str, Any], output_dir: str) -> None:
        """Export batch processing results."""

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Export individual results
        for filename, result in batch_results.items():
            if "error" not in result:
                base_name = Path(filename).stem

                # JSON export
                json_path = output_path / f"{base_name}_results.json"
                ResultsExporter.export_to_json(result, str(json_path))

                # Summary export
                summary_path = output_path / f"{base_name}_summary.txt"
                ResultsExporter.export_summary_report(result, str(summary_path))

        # Create batch summary
        self._create_batch_summary(batch_results, output_path)

    def _create_batch_summary(self, batch_results: dict[str, Any], output_path: Path) -> None:
        """Create summary of batch processing results."""

        summary_file = output_path / "batch_summary.txt"

        try:
            # Build content first
            lines = []
            lines.append("BATCH PROCESSING SUMMARY\n")
            lines.append("=" * 30 + "\n\n")

            total_files = len(batch_results)
            successful = sum(1 for r in batch_results.values() if "error" not in r)
            failed = total_files - successful

            lines.append(f"Total files processed: {total_files}\n")
            lines.append(f"Successful: {successful}\n")
            lines.append(f"Failed: {failed}\n\n")

            if failed > 0:
                lines.append("FAILED FILES:\n")
                lines.append("-" * 15 + "\n")
                for filename, result in batch_results.items():
                    if "error" in result:
                        lines.append(f"- {filename}: {result['error']}\n")
                lines.append("\n")

            if successful > 0:
                lines.append("SUCCESSFUL ANALYSES:\n")
                lines.append("-" * 20 + "\n")

                for filename, result in batch_results.items():
                    if "error" not in result:
                        summary = result.get("summary", {})
                        perf_summary = summary.get("performance_summary", {})
                        risk_summary = summary.get("risk_assessment", {})

                        lines.append(f"\n{filename}:\n")
                        lines.append(
                            f"  Efficiency: {perf_summary.get('average_efficiency_score', 0):.2f}\n"
                        )
                        lines.append(
                            f"  Risk Level: {risk_summary.get('overall_risk_level', 'unknown')}\n"
                        )

            # Delegate to factory for I/O operation
# DELETED_MODULE:             from farfan_pipeline.analysis.factory import write_text_file

            write_text_file("".join(lines), summary_file)
            logger.info(f"Batch summary created: {summary_file}")

        except Exception as e:
            logger.error(f"Error creating batch summary: {e}")


# Simple CLI interface
def main() -> None:
    """Simple command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Municipal Development Plan Analyzer")
    parser.add_argument("input", help="Input file or directory path")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch process directory")
    parser.add_argument("--config", "-c", help="Configuration file path")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = MunicipalAnalyzer()

    if args.batch:
        # Batch processing
        processor = BatchProcessor(analyzer)
        results = processor.process_directory(args.input)
        processor.export_batch_results(results, args.output)
        print(f"Batch processing complete. Results in: {args.output}")
    else:
        # Single file processing
        results = analyzer.analyze_document(args.input)

        # Export results
        exporter = ResultsExporter()
        output_base = Path(args.output) / Path(args.input).stem

        exporter.export_to_json(results, f"{output_base}_results.json")
        exporter.export_summary_report(results, f"{output_base}_summary.txt")

        print(f"Analysis complete. Results in: {args.output}")
