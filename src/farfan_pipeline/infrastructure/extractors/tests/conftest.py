"""
Pytest configuration for extractor tests.

Provides fixtures and test data for empirically-calibrated extractors.
"""

import pytest
import json
from pathlib import Path


@pytest.fixture(scope="session")
def calibration_data():
    """Load empirical calibration data."""
    calibration_file = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / \
                      "canonic_questionnaire_central" / "_registry" / \
                      "membership_criteria" / "_calibration" / "extractor_calibration.json"

    with open(calibration_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def gold_standards(calibration_data):
    """Extract gold standard examples from calibration data."""
    return calibration_data.get("signal_type_catalog", {})


@pytest.fixture
def financial_chain_examples(gold_standards):
    """Gold standard examples for financial chains."""
    return gold_standards.get("FINANCIAL_CHAIN", {}).get("gold_standard_examples", [])


@pytest.fixture
def causal_verb_text_samples():
    """Sample texts with causal verbs from real PDT plans."""
    return [
        "Fortalecer la capacidad institucional de la Secretaría de Salud para mejorar la atención primaria",
        "Implementar el programa de vacunación con el fin de reducir la mortalidad infantil",
        "Garantizar el acceso a educación de calidad mediante la construcción de 5 escuelas rurales",
        "Promover el desarrollo económico local a través de proyectos productivos",
        "Mejorar la infraestructura vial para aumentar la conectividad territorial",
        "Desarrollar estrategias de prevención del consumo de sustancias psicoactivas en jóvenes",
        "Consolidar el sistema de información territorial con el apoyo del DNP",
        "Impulsar la participación ciudadana para lograr una mayor gobernanza democrática"
    ]


@pytest.fixture
def institutional_entities_samples():
    """Sample texts with institutional entities from real PDT plans."""
    return [
        "La Alcaldía Municipal en coordinación con el DNP implementará el proyecto",
        "El DANE proporcionará los datos estadísticos necesarios para las líneas base",
        "El ICBF será responsable de los programas de primera infancia",
        "MinSalud apoyará técnicamente la implementación del Plan Territorial de Salud",
        "La Gobernación del Cauca coordinará las mesas de articulación regional",
        "El SENA desarrollará programas de formación técnica para jóvenes rurales",
        "La Secretaría de Educación en articulación con MinEducación fortalecerá la calidad educativa",
        "La Unidad de Víctimas (UARIV) acompañará los procesos de reparación colectiva"
    ]


@pytest.fixture
def quantitative_triplet_samples():
    """Sample texts with quantitative triplets (LB/Meta/Año)."""
    return [
        "Tasa de cobertura educativa neta: línea base 45.2% (2023), meta 2027: 65.0%",
        "Niños con esquema completo de vacunación: línea base 5,420 (2023), meta 2027: 7,800",
        "Kilómetros de vías pavimentadas: Línea Base 2023: 38.5 km, Meta cuatrienio: 85 km",
        "Índice de pobreza multidimensional: línea base: 52.3% (2023), meta 2027: 42.0%"
    ]


@pytest.fixture
def normative_reference_samples():
    """Sample texts with normative references."""
    return [
        "De acuerdo con la Ley 152 de 1994, el plan debe contener estrategias y orientaciones generales",
        "En cumplimiento de la Ley 1448 de 2011, se implementarán medidas de reparación colectiva",
        "Según el Decreto 1865 de 1994, se establecen las normas de planificación territorial",
        "El CONPES 3932 de 2018 orienta la política de crecimiento verde",
        "El Artículo 339 de la Constitución establece el Sistema Nacional de Planeación"
    ]
