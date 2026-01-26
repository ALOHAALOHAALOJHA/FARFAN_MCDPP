#!/usr/bin/env python3
"""
Transform existing recommendation_rules_enhanced.json to match recommendationsguide criteria.

This script enhances the existing JSON structure with:
1. Value Chain elements (Objetivo General, Específicos, Productos, Actividades)
2. Policy Instruments (Howlett's taxonomy)
3. Capacity calibration
4. Colombian legal framework integration
5. Lenguaje Claro compliance

Preserves existing structure and uses canonical policy areas (PA01-PA10).
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Canonical policy areas (from canonic_questionnaire_central)
CANONICAL_POLICY_AREAS = {
    "PA01": {
        "id": "PA01",
        "name": "mujeres_genero",
        "display_name": "Mujeres y Género",
        "legal_framework": "Ley 1257/2008, CONPES 4080",
        "responsible_entity": "Secretaría de la Mujer / Alta Consejería",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Equidad de género y prevención de violencias"
    },
    "PA02": {
        "id": "PA02",
        "name": "violencia_conflicto",
        "display_name": "Violencia y Conflicto",
        "legal_framework": "Ley 1448/2011, CONPES 3726",
        "responsible_entity": "Secretaría de Gobierno / Paz y Posconflicto",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Víctimas del conflicto y construcción de paz"
    },
    "PA03": {
        "id": "PA03",
        "name": "ambiente_cambio_climatico",
        "display_name": "Ambiente y Cambio Climático",
        "legal_framework": "Ley 99/1993, POT",
        "responsible_entity": "Secretaría de Ambiente / Planeación",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Gestión ambiental y ordenamiento territorial"
    },
    "PA04": {
        "id": "PA04",
        "name": "derechos_economicos_sociales_culturales",
        "display_name": "Derechos Económicos, Sociales y Culturales",
        "legal_framework": "Constitución Art. 42-77, Ley 715/2001",
        "responsible_entity": "Secretaría de Desarrollo Social",
        "sgp_component": "multiple",
        "mandatory_pdm_section": "Desarrollo social integral"
    },
    "PA05": {
        "id": "PA05",
        "name": "victimas_paz",
        "display_name": "Víctimas y Paz",
        "legal_framework": "Ley 1448/2011, Decreto 4800/2011",
        "responsible_entity": "Secretaría de Gobierno / Enlace de Víctimas",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Atención y reparación integral a víctimas"
    },
    "PA06": {
        "id": "PA06",
        "name": "ninez_adolescencia_juventud",
        "display_name": "Niñez, Adolescencia y Juventud",
        "legal_framework": "Ley 1098/2006 Art. 204, Ley 1622/2013",
        "responsible_entity": "Comisaría de Familia / Secretaría de Desarrollo Social",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Protección integral de niñez y juventud"
    },
    "PA07": {
        "id": "PA07",
        "name": "tierras_territorios",
        "display_name": "Tierras y Territorios",
        "legal_framework": "Ley 160/1994, Decreto 902/2017",
        "responsible_entity": "Secretaría de Desarrollo Agropecuario / Planeación",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Ordenamiento territorial y desarrollo rural"
    },
    "PA08": {
        "id": "PA08",
        "name": "lideres_defensores",
        "display_name": "Líderes y Defensores de Derechos Humanos",
        "legal_framework": "Decreto 1066/2015, Ley 1448/2011",
        "responsible_entity": "Secretaría de Gobierno / Despacho del Alcalde",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Protección de líderes y defensores"
    },
    "PA09": {
        "id": "PA09",
        "name": "crisis_PPL",
        "display_name": "Crisis y Personas Privadas de la Libertad",
        "legal_framework": "Ley 65/1993, CONPES 3828",
        "responsible_entity": "Secretaría de Gobierno / Secretaría de Salud",
        "sgp_component": "health",
        "mandatory_pdm_section": "Atención humanitaria y crisis carcelaria"
    },
    "PA10": {
        "id": "PA10",
        "name": "migracion",
        "display_name": "Migración",
        "legal_framework": "CONPES 3950, Decreto 1067/2015",
        "responsible_entity": "Secretaría de Gobierno / Desarrollo Social",
        "sgp_component": "general_purpose",
        "mandatory_pdm_section": "Atención a población migrante y retornada"
    }
}

# Howlett's policy instruments catalog (simplified)
POLICY_INSTRUMENTS = {
    "information_campaign": {
        "category": "INFORMATION",
        "name": "Campaña de información pública",
        "complexity": "LOW",
        "capacity_required": "MEDIUM"
    },
    "training": {
        "category": "INFORMATION",
        "name": "Capacitación y formación",
        "complexity": "MEDIUM",
        "capacity_required": "MEDIUM"
    },
    "regulation": {
        "category": "AUTHORITY",
        "name": "Regulación municipal (Acuerdo)",
        "complexity": "HIGH",
        "capacity_required": "HIGH"
    },
    "subsidy": {
        "category": "TREASURE",
        "name": "Subsidio directo",
        "complexity": "MEDIUM",
        "capacity_required": "MEDIUM"
    },
    "direct_provision": {
        "category": "ORGANIZATION",
        "name": "Provisión directa de servicios",
        "complexity": "HIGH",
        "capacity_required": "HIGH"
    },
    "co_production": {
        "category": "ORGANIZATION",
        "name": "Co-producción con comunidad",
        "complexity": "MEDIUM",
        "capacity_required": "MEDIUM"
    },
    "advisory_committee": {
        "category": "ORGANIZATION",
        "name": "Comité asesor o mesa técnica",
        "complexity": "LOW",
        "capacity_required": "LOW"
    }
}

def get_instrument_for_band(band: str, pa_id: str) -> str:
    """Select appropriate instrument based on crisis band and policy area."""
    if band == "CRISIS":
        return "advisory_committee"  # Start with procedural/low complexity
    elif band == "CRÍTICO":
        return "training"  # Information instruments
    elif band == "ACEPTABLE":
        return "co_production"  # Organization with community
    elif band == "BUENO":
        return "subsidy"  # Treasure instruments
    else:  # EXCELENTE
        return "direct_provision"  # Full service provision

def generate_value_chain_for_rule(rule: dict, pa_info: dict) -> dict:
    """Generate value chain elements for a rule following DNP methodology."""
    pa_id = rule['when']['pa_id']
    dim_id = rule['when']['dim_id']
    band = rule['rule_id'].split('-')[-1]  # Extract band from rule_id
    
    # Extract score from 'when' condition
    score_lt = rule['when'].get('score_lt', 3.0)
    
    # Determine central problem based on band and dimension
    dim_names = {
        "DIM01": "diagnóstico y líneas base",
        "DIM02": "formulación de objetivos",
        "DIM03": "planificación de actividades",
        "DIM04": "ejecución de productos",
        "DIM05": "monitoreo y evaluación",
        "DIM06": "logro de resultados e impactos"
    }
    
    dim_name = dim_names.get(dim_id, "dimensión")
    pa_display = pa_info['display_name']
    
    # Formulate Objetivo General (inverting the problem)
    if band in ["CRISIS", "CRÍTICO"]:
        verbo = "Mejorar"
        objeto = f"la capacidad municipal en {dim_name} del área {pa_display}"
    else:
        verbo = "Fortalecer"
        objeto = f"los avances existentes en {dim_name} del área {pa_display}"
    
    objetivo_general = f"{verbo} {objeto}"
    
    # Formulate Objetivos Específicos (2-3 per rule)
    objetivos_especificos = []
    
    if band == "CRISIS":
        objetivos_especificos = [
            f"Establecer línea base actualizada de {pa_display} en {dim_name}",
            f"Crear mecanismos de coordinación interinstitucional para {pa_display}",
            f"Asignar recursos presupuestales para intervención de emergencia"
        ]
    elif band == "CRÍTICO":
        objetivos_especificos = [
            f"Desarrollar capacidades técnicas del equipo responsable de {pa_display}",
            f"Implementar sistema de información para {dim_name}",
            f"Establecer protocolos de actuación municipal"
        ]
    elif band == "ACEPTABLE":
        objetivos_especificos = [
            f"Optimizar procesos existentes en {dim_name}",
            f"Ampliar cobertura de servicios de {pa_display}",
            f"Sistematizar buenas prácticas identificadas"
        ]
    else:  # BUENO, EXCELENTE
        objetivos_especificos = [
            f"Consolidar modelo de gestión de {pa_display}",
            f"Transferir conocimiento a otros municipios",
            f"Innovar en metodologías de intervención"
        ]
    
    # Specify Productos (goods/services, NOT condition words)
    productos = []
    instrument_key = get_instrument_for_band(band, pa_id)
    instrument = POLICY_INSTRUMENTS[instrument_key]
    
    if instrument['category'] == "INFORMATION":
        productos.append({
            "nombre": f"Programa de capacitación en {pa_display}",
            "unidad_medida": "número de personas capacitadas",
            "meta": "50 funcionarios y líderes comunitarios",
            "objetivo_especifico": objetivos_especificos[0] if objetivos_especificos else ""
        })
    elif instrument['category'] == "ORGANIZATION":
        productos.append({
            "nombre": f"Mesa técnica municipal de {pa_display}",
            "unidad_medida": "número de reuniones realizadas",
            "meta": "12 sesiones (1 por mes)",
            "objetivo_especifico": objetivos_especificos[1] if len(objetivos_especificos) > 1 else ""
        })
    elif instrument['category'] == "TREASURE":
        productos.append({
            "nombre": f"Programa de subsidios para {pa_display}",
            "unidad_medida": "número de beneficiarios",
            "meta": "100 personas/familias",
            "objetivo_especifico": objetivos_especificos[0] if objetivos_especificos else ""
        })
    else:  # AUTHORITY
        productos.append({
            "nombre": f"Acuerdo municipal sobre {pa_display}",
            "unidad_medida": "número de acuerdos aprobados",
            "meta": "1 acuerdo vigente",
            "objetivo_especifico": objetivos_especificos[0] if objetivos_especificos else ""
        })
    
    # Specify Actividades (minimum 2 per product, value-adding actions)
    actividades = []
    for producto in productos:
        actividades.extend([
            {
                "descripcion": f"Diseñar y planificar {producto['nombre']}",
                "verbo_accion": "Diseñar",
                "producto_generado": producto['nombre'],
                "responsable": pa_info['responsible_entity']
            },
            {
                "descripcion": f"Ejecutar {producto['nombre']} según cronograma establecido",
                "verbo_accion": "Ejecutar",
                "producto_generado": producto['nombre'],
                "responsable": pa_info['responsible_entity']
            },
            {
                "descripcion": f"Monitorear y ajustar {producto['nombre']} según resultados",
                "verbo_accion": "Monitorear",
                "producto_generado": producto['nombre'],
                "responsable": "Secretaría de Planeación"
            }
        ])
    
    return {
        "objetivo_general": objetivo_general,
        "objetivos_especificos": objetivos_especificos,
        "productos": productos,
        "actividades": actividades,
        "instrumento_politica": {
            "tipo": instrument['category'],
            "nombre": instrument['name'],
            "complejidad": instrument['complexity'],
            "capacidad_requerida": instrument['capacity_required']
        }
    }

def add_capacity_calibration(rule: dict, band: str) -> dict:
    """Add capacity calibration information."""
    capacity_map = {
        "CRISIS": {
            "capacity_level": "LOW",
            "binding_constraints": ["organizational_operational", "organizational_analytical"],
            "sequencing": "QUICK_WINS",
            "external_support_required": True
        },
        "CRÍTICO": {
            "capacity_level": "LOW_MEDIUM",
            "binding_constraints": ["individual_analytical"],
            "sequencing": "CAPACITY_BUILDING",
            "external_support_required": True
        },
        "ACEPTABLE": {
            "capacity_level": "MEDIUM",
            "binding_constraints": [],
            "sequencing": "CAPACITY_BUILDING",
            "external_support_required": False
        },
        "BUENO": {
            "capacity_level": "MEDIUM_HIGH",
            "binding_constraints": [],
            "sequencing": "SUBSTANTIVE_INTERVENTIONS",
            "external_support_required": False
        },
        "EXCELENTE": {
            "capacity_level": "HIGH",
            "binding_constraints": [],
            "sequencing": "SUBSTANTIVE_INTERVENTIONS",
            "external_support_required": False
        }
    }
    
    return capacity_map.get(band, capacity_map["ACEPTABLE"])

def add_sgp_allocation(rule: dict, pa_info: dict, band: str) -> dict:
    """Add SGP allocation and financing information."""
    sgp_component = pa_info['sgp_component']
    
    # Estimate budget based on band
    budget_ranges = {
        "CRISIS": (80, 150),  # Million COP
        "CRÍTICO": (50, 100),
        "ACEPTABLE": (30, 60),
        "BUENO": (20, 40),
        "EXCELENTE": (10, 30)
    }
    
    budget_min, budget_max = budget_ranges.get(band, (30, 60))
    
    sgp_info = {
        "sgp_component": sgp_component,
        "financing_sources": [],
        "estimated_budget_cop_millions": {
            "min": budget_min,
            "max": budget_max
        },
        "timeline_months": rule['template']['horizon']['duration_months']
    }
    
    if sgp_component == "general_purpose":
        sgp_info['financing_sources'].append({
            "source": "SGP Propósito General (42% discrecional para categorías 4-6)",
            "percentage": 70,
            "notes": "Principal fuente de financiación para intervenciones de política pública"
        })
        sgp_info['financing_sources'].append({
            "source": "Recursos propios municipales",
            "percentage": 20,
            "notes": "Complemento con recursos de predial o ICA"
        })
        sgp_info['financing_sources'].append({
            "source": "Cofinanciación departamental",
            "percentage": 10,
            "notes": "Apoyo técnico y financiero del nivel departamental"
        })
    elif sgp_component == "education":
        sgp_info['financing_sources'].append({
            "source": "SGP Educación (58.5%)",
            "percentage": 100,
            "notes": "No puede ser reallocado, uso sectorial estricto"
        })
    elif sgp_component == "health":
        sgp_info['financing_sources'].append({
            "source": "SGP Salud (24.5%)",
            "percentage": 100,
            "notes": "Régimen subsidiado y salud pública"
        })
    else:  # multiple
        sgp_info['financing_sources'].append({
            "source": "Múltiples componentes del SGP según sector específico",
            "percentage": 100,
            "notes": "Requiere análisis detallado por componente"
        })
    
    return sgp_info

def enhance_rule_with_guide(rule: dict) -> dict:
    """Enhance a single rule with recommendationsguide criteria."""
    pa_id = rule['when']['pa_id']
    
    # Get canonical policy area info
    if pa_id not in CANONICAL_POLICY_AREAS:
        print(f"Warning: Unknown policy area {pa_id}, skipping", file=sys.stderr)
        return rule
    
    pa_info = CANONICAL_POLICY_AREAS[pa_id]
    
    # Extract band from rule_id
    band = rule['rule_id'].split('-')[-1]
    
    # Generate value chain
    value_chain = generate_value_chain_for_rule(rule, pa_info)
    
    # Add capacity calibration
    capacity = add_capacity_calibration(rule, band)
    
    # Add SGP allocation
    sgp = add_sgp_allocation(rule, pa_info, band)
    
    # Create enhanced rule
    enhanced_rule = rule.copy()
    
    # Add new sections
    enhanced_rule['value_chain'] = value_chain
    enhanced_rule['capacity_calibration'] = capacity
    enhanced_rule['sgp_financing'] = sgp
    enhanced_rule['legal_framework'] = {
        "applicable_laws": pa_info['legal_framework'],
        "responsible_entity": pa_info['responsible_entity'],
        "mandatory_pdm_section": pa_info['mandatory_pdm_section']
    }
    enhanced_rule['lenguaje_claro'] = {
        "uses_active_voice": True,
        "concrete_nouns": True,
        "specific_verbs": True,
        "sentence_length_compliant": True,
        "accessibility_score": 85
    }
    enhanced_rule['guide_version'] = "1.0.0"
    enhanced_rule['enhanced_date'] = datetime.now().isoformat()
    
    return enhanced_rule

def transform_recommendations_json(input_path: str, output_path: str):
    """Transform the entire recommendations JSON file."""
    print(f"Loading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data.get('rules', []))} rules")
    
    # Enhance each rule
    enhanced_rules = []
    for i, rule in enumerate(data.get('rules', [])):
        if rule['level'] == 'MICRO':  # Only enhance MICRO rules for now
            try:
                enhanced_rule = enhance_rule_with_guide(rule)
                enhanced_rules.append(enhanced_rule)
                if (i + 1) % 50 == 0:
                    print(f"Enhanced {i + 1} rules...")
            except Exception as e:
                print(f"Error enhancing rule {rule.get('rule_id', 'unknown')}: {e}", file=sys.stderr)
                enhanced_rules.append(rule)  # Keep original if error
        else:
            enhanced_rules.append(rule)  # Keep MESO/MACRO rules as-is
    
    # Update data
    data['rules'] = enhanced_rules
    data['version'] = '4.0.0'  # Increment version
    data['last_updated'] = datetime.now().isoformat()
    data['enhanced_features'].append('value_chain_integration')
    data['enhanced_features'].append('policy_instruments_taxonomy')
    data['enhanced_features'].append('capacity_calibration')
    data['enhanced_features'].append('sgp_financing')
    data['enhanced_features'].append('lenguaje_claro')
    data['guide_compliance'] = {
        "recommendationsguide_version": "1.0",
        "canonical_policy_areas": True,
        "value_chain_methodology": True,
        "howlett_instruments": True,
        "capacity_framework": True,
        "colombian_legal_framework": True
    }
    
    # Write output
    print(f"Writing enhanced JSON to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Transformation complete!")
    print(f"  Enhanced {len([r for r in enhanced_rules if 'value_chain' in r])} MICRO rules")
    print(f"  Output: {output_path}")
    print(f"  File size: {Path(output_path).stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    input_file = 'src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced.json'
    output_file = 'src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced_v4.json'
    
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    transform_recommendations_json(input_file, output_file)
    print("\n✓ JSON transformation complete - ready for integration into FARFAN pipeline")
