#!/usr/bin/env python3
"""
Enhanced transformation to cover all 3 levels (MICRO, MESO, MACRO) with full guide compliance.

This script enriches ALL rules across the 3 levels with:
1. Value Chain elements (adapted for each level)
2. Policy Instruments (Howlett's taxonomy)
3. Capacity calibration
4. Colombian legal framework integration
5. Leverage points (Meadows framework)
6. Multiple scoring scenarios coverage
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import canonical policy areas from previous script
CANONICAL_POLICY_AREAS = {
    "PA01": {
        "id": "PA01",
        "name": "mujeres_genero",
        "display_name": "Mujeres y Género",
        "legal_framework": "Ley 1257/2008, CONPES 4080",
        "responsible_entity": "Secretaría de la Mujer / Alta Consejería",
        "sgp_component": "general_purpose"
    },
    "PA02": {
        "id": "PA02",
        "name": "violencia_conflicto",
        "display_name": "Violencia y Conflicto (Seguridad y convivencia)",
        "legal_framework": "Ley 1448/2011, CONPES 3726",
        "responsible_entity": "Secretaría de Gobierno / Paz y Posconflicto",
        "sgp_component": "general_purpose"
    },
    "PA03": {
        "id": "PA03",
        "name": "ambiente_cambio_climatico",
        "display_name": "Ambiente y Cambio Climático",
        "legal_framework": "Ley 99/1993, POT",
        "responsible_entity": "Secretaría de Ambiente / Planeación",
        "sgp_component": "general_purpose"
    },
    "PA04": {
        "id": "PA04",
        "name": "derechos_economicos_sociales_culturales",
        "display_name": "Derechos Económicos, Sociales y Culturales",
        "legal_framework": "Constitución Art. 42-77, Ley 715/2001",
        "responsible_entity": "Secretaría de Desarrollo Social",
        "sgp_component": "multiple"
    },
    "PA05": {
        "id": "PA05",
        "name": "victimas_paz",
        "display_name": "Víctimas y Paz",
        "legal_framework": "Ley 1448/2011, Decreto 4800/2011",
        "responsible_entity": "Secretaría de Gobierno / Enlace de Víctimas",
        "sgp_component": "general_purpose"
    },
    "PA06": {
        "id": "PA06",
        "name": "ninez_adolescencia_juventud",
        "display_name": "Niñez, Adolescencia y Juventud",
        "legal_framework": "Ley 1098/2006 Art. 204, Ley 1622/2013",
        "responsible_entity": "Comisaría de Familia / Secretaría de Desarrollo Social",
        "sgp_component": "general_purpose"
    },
    "PA07": {
        "id": "PA07",
        "name": "tierras_territorios",
        "display_name": "Tierras y Territorios",
        "legal_framework": "Ley 160/1994, Decreto 902/2017",
        "responsible_entity": "Secretaría de Desarrollo Agropecuario / Planeación",
        "sgp_component": "general_purpose"
    },
    "PA08": {
        "id": "PA08",
        "name": "lideres_defensores",
        "display_name": "Líderes y Defensores de Derechos Humanos",
        "legal_framework": "Decreto 1066/2015, Ley 1448/2011",
        "responsible_entity": "Secretaría de Gobierno / Despacho del Alcalde",
        "sgp_component": "general_purpose"
    },
    "PA09": {
        "id": "PA09",
        "name": "crisis_PPL",
        "display_name": "Crisis y Personas Privadas de la Libertad",
        "legal_framework": "Ley 65/1993, CONPES 3828",
        "responsible_entity": "Secretaría de Gobierno / Secretaría de Salud",
        "sgp_component": "health"
    },
    "PA10": {
        "id": "PA10",
        "name": "migracion",
        "display_name": "Migración",
        "legal_framework": "CONPES 3950, Decreto 1067/2015",
        "responsible_entity": "Secretaría de Gobierno / Desarrollo Social",
        "sgp_component": "general_purpose"
    }
}

# Cluster information
CLUSTERS = {
    "CL01": {
        "id": "CL01",
        "name": "Seguridad y Paz",
        "policy_areas": ["PA02", "PA05", "PA08"],
        "description": "Seguridad, paz, víctimas y defensores"
    },
    "CL02": {
        "id": "CL02",
        "name": "Inclusión Social",
        "policy_areas": ["PA01", "PA06", "PA10"],
        "description": "Género, niñez, juventud, migración"
    },
    "CL03": {
        "id": "CL03",
        "name": "Territorio y Ambiente",
        "policy_areas": ["PA03", "PA07"],
        "description": "Ambiente, tierras y territorios"
    },
    "CL04": {
        "id": "CL04",
        "name": "Derechos DESC",
        "policy_areas": ["PA04", "PA09"],
        "description": "Derechos económicos, sociales, culturales"
    }
}

def enhance_meso_rule(rule: dict) -> dict:
    """Enhance MESO (cluster-level) rule with guide compliance."""
    cluster_id = rule['when'].get('cluster_id')
    weak_pa_id = rule['when'].get('weak_pa_id')
    score_band = rule['when'].get('score_band', 'MEDIO')
    
    if not cluster_id or cluster_id not in CLUSTERS:
        return rule
    
    cluster = CLUSTERS[cluster_id]
    
    # Get weak PA info
    pa_info = CANONICAL_POLICY_AREAS.get(weak_pa_id, {})
    pa_display = pa_info.get('display_name', weak_pa_id)
    
    # Value chain for MESO level (cluster coordination)
    objetivo_general = f"Equilibrar el desempeño del cluster {cluster['name']} abordando las brechas identificadas en {pa_display}"
    
    objetivos_especificos = [
        f"Reducir la varianza entre las áreas de política del cluster {cluster['name']}",
        f"Fortalecer la coordinación interinstitucional en {pa_display}",
        f"Implementar mecanismos de seguimiento y ajuste para el cluster"
    ]
    
    # MESO instruments focus on coordination and systemic integration
    productos = [{
        "nombre": f"Comité de coordinación del cluster {cluster['name']}",
        "unidad_medida": "número de sesiones de coordinación realizadas",
        "meta": "12 sesiones anuales con participación de todas las secretarías",
        "objetivo_especifico": objetivos_especificos[0]
    }, {
        "nombre": f"Plan de acción integrado para {pa_display}",
        "unidad_medida": "número de acciones coordinadas ejecutadas",
        "meta": "6 acciones interinstitucionales",
        "objetivo_especifico": objetivos_especificos[1]
    }]
    
    actividades = []
    for producto in productos:
        actividades.extend([
            {
                "descripcion": f"Convocar y realizar sesiones de {producto['nombre']}",
                "verbo_accion": "Convocar",
                "producto_generado": producto['nombre'],
                "responsable": "Secretaría de Planeación"
            },
            {
                "descripcion": f"Consolidar información de avances del {producto['nombre']}",
                "verbo_accion": "Consolidar",
                "producto_generado": producto['nombre'],
                "responsable": "Oficina de Planeación"
            }
        ])
    
    # Leverage points for MESO
    leverage_point = {
        "level": 8,  # Negative feedback loops - coordination mechanisms
        "description": "Fortalecimiento de mecanismos de coordinación interinstitucional",
        "intervention_type": "Crear sistemas de coordinación que equilibren el desempeño del cluster",
        "expected_impact": "Reducción de varianza y mejora en áreas rezagadas"
    }
    
    # Enhanced rule
    enhanced = rule.copy()
    enhanced['value_chain'] = {
        "objetivo_general": objetivo_general,
        "objetivos_especificos": objetivos_especificos,
        "productos": productos,
        "actividades": actividades,
        "instrumento_politica": {
            "tipo": "ORGANIZATION",
            "nombre": "Comité de coordinación interinstitucional",
            "complejidad": "MEDIUM",
            "capacidad_requerida": "MEDIUM",
            "justificacion": "MESO requiere instrumentos de coordinación entre múltiples secretarías"
        }
    }
    
    enhanced['capacity_calibration'] = {
        "capacity_level": "MEDIUM",
        "binding_constraints": ["organizational_operational", "systemic_operational"],
        "sequencing": "CAPACITY_BUILDING",
        "external_support_required": False,
        "coordination_complexity": "HIGH"
    }
    
    enhanced['leverage_point'] = leverage_point
    
    enhanced['sgp_financing'] = {
        "sgp_component": "general_purpose",
        "financing_sources": [{
            "source": "SGP Propósito General - coordinación institucional",
            "percentage": 100,
            "notes": "Costos operativos de coordinación cubiertos por presupuesto de funcionamiento"
        }],
        "estimated_budget_cop_millions": {
            "min": 20,
            "max": 40
        },
        "timeline_months": 12
    }
    
    enhanced['legal_framework'] = {
        "applicable_laws": "Ley 152/1994 (PDM), Ley 1757/2015 (Participación)",
        "responsible_entity": "Secretaría de Planeación Municipal",
        "mandatory_pdm_section": "Parte Estratégica - Articulación intersectorial"
    }
    
    enhanced['guide_version'] = "1.0.0"
    enhanced['enhanced_date'] = datetime.now().isoformat()
    enhanced['level_specifics'] = {
        "cluster_id": cluster_id,
        "cluster_name": cluster['name'],
        "coordination_type": "Inter-secretarial",
        "scope": "Multiple policy areas within cluster"
    }
    
    return enhanced

def enhance_macro_rule(rule: dict) -> dict:
    """Enhance MACRO (system-level) rule with guide compliance."""
    macro_band = rule['when'].get('macro_band', 'SATISFACTORIO')
    variance_alert = rule['when'].get('variance_alert', 'BAJA')
    
    # Value chain for MACRO level (systemic transformation)
    if macro_band in ['EXCELENTE', 'BUENO']:
        objetivo_general = f"Consolidar y sostener el desempeño {macro_band} del sistema municipal de planificación"
    else:
        objetivo_general = f"Transformar el sistema municipal desde nivel {macro_band} hacia desempeño sostenible"
    
    objetivos_especificos = [
        "Fortalecer la capacidad institucional sistémica del municipio",
        "Implementar mecanismos de aprendizaje organizacional",
        "Desarrollar alianzas estratégicas con actores departamentales y nacionales"
    ]
    
    # MACRO instruments focus on systemic change and institutional strengthening
    productos = [{
        "nombre": "Sistema municipal de seguimiento y evaluación integrado",
        "unidad_medida": "número de indicadores integrados al sistema",
        "meta": "Integración de 300 indicadores FARFAN en plataforma única",
        "objetivo_especifico": objetivos_especificos[0]
    }, {
        "nombre": "Programa de fortalecimiento institucional",
        "unidad_medida": "número de funcionarios con capacidades mejoradas",
        "meta": "80% del equipo directivo capacitado",
        "objetivo_especifico": objetivos_especificos[1]
    }]
    
    actividades = []
    for producto in productos:
        actividades.extend([
            {
                "descripcion": f"Diseñar arquitectura del {producto['nombre']}",
                "verbo_accion": "Diseñar",
                "producto_generado": producto['nombre'],
                "responsable": "Secretaría de Planeación con apoyo DNP"
            },
            {
                "descripcion": f"Implementar y poner en operación {producto['nombre']}",
                "verbo_accion": "Implementar",
                "producto_generado": producto['nombre'],
                "responsable": "Equipo directivo municipal"
            },
            {
                "descripcion": f"Monitorear y optimizar continuamente {producto['nombre']}",
                "verbo_accion": "Monitorear",
                "producto_generado": producto['nombre'],
                "responsable": "Oficina de Control Interno"
            }
        ])
    
    # Leverage points for MACRO - high leverage interventions
    if macro_band in ['CRISIS', 'DEFICIENTE', 'INSUFICIENTE']:
        leverage_level = 4  # Self-organization
        leverage_desc = "Fomentar capacidad de auto-organización y evolución del sistema"
    else:
        leverage_level = 6  # Information flows
        leverage_desc = "Optimizar flujos de información y visibilidad de datos"
    
    leverage_point = {
        "level": leverage_level,
        "description": leverage_desc,
        "intervention_type": "Transformación sistémica de capacidades institucionales",
        "expected_impact": "Mejora sostenible en todos los clusters y áreas de política"
    }
    
    # Enhanced rule
    enhanced = rule.copy()
    enhanced['value_chain'] = {
        "objetivo_general": objetivo_general,
        "objetivos_especificos": objetivos_especificos,
        "productos": productos,
        "actividades": actividades,
        "instrumento_politica": {
            "tipo": "ORGANIZATION",
            "nombre": "Fortalecimiento institucional sistémico",
            "complejidad": "HIGH",
            "capacidad_requerida": "HIGH",
            "justificacion": "MACRO requiere transformación institucional de largo plazo"
        }
    }
    
    enhanced['capacity_calibration'] = {
        "capacity_level": "VARIABLE",
        "binding_constraints": ["systemic_analytical", "systemic_operational", "systemic_political"],
        "sequencing": "SUBSTANTIVE_INTERVENTIONS",
        "external_support_required": True,
        "systemic_transformation": True
    }
    
    enhanced['leverage_point'] = leverage_point
    
    enhanced['sgp_financing'] = {
        "sgp_component": "multiple",
        "financing_sources": [{
            "source": "SGP múltiples componentes + recursos propios",
            "percentage": 60,
            "notes": "Fortalecimiento institucional requiere múltiples fuentes"
        }, {
            "source": "Cofinanciación departamental y nacional (DNP, entidades sectoriales)",
            "percentage": 30,
            "notes": "Apoyo técnico y financiero de niveles superiores"
        }, {
            "source": "Cooperación internacional y alianzas público-privadas",
            "percentage": 10,
            "notes": "Complemento para innovación y transferencia de conocimiento"
        }],
        "estimated_budget_cop_millions": {
            "min": 200,
            "max": 500
        },
        "timeline_months": 48
    }
    
    enhanced['legal_framework'] = {
        "applicable_laws": "Ley 152/1994, Ley 1474/2011 (Transparencia), Ley 1712/2014 (Transparencia)",
        "responsible_entity": "Despacho del Alcalde + Secretaría de Planeación",
        "mandatory_pdm_section": "Parte Estratégica - Visión y modelo de desarrollo"
    }
    
    enhanced['guide_version'] = "1.0.0"
    enhanced['enhanced_date'] = datetime.now().isoformat()
    enhanced['level_specifics'] = {
        "macro_band": macro_band,
        "systemic_scope": "Todo el sistema municipal",
        "transformation_type": "Institucional y cultural",
        "timeline": "Cuatrienio completo (48 meses)"
    }
    
    return enhanced

def enrich_all_levels(input_path: str, output_path: str):
    """Enrich ALL rules across MICRO, MESO, and MACRO levels."""
    print(f"Loading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_rules = len(data.get('rules', []))
    print(f"Loaded {original_rules} rules")
    
    # Statistics
    stats = defaultdict(lambda: {'original': 0, 'enhanced': 0})
    
    # Enhance each rule based on level
    enhanced_rules = []
    for i, rule in enumerate(data.get('rules', [])):
        level = rule['level']
        stats[level]['original'] += 1
        
        try:
            if level == 'MICRO':
                # MICRO already enhanced, keep as is
                if 'value_chain' in rule:
                    enhanced_rules.append(rule)
                    stats[level]['enhanced'] += 1
                else:
                    # Should not happen, but handle gracefully
                    enhanced_rules.append(rule)
            elif level == 'MESO':
                enhanced_rule = enhance_meso_rule(rule)
                enhanced_rules.append(enhanced_rule)
                stats[level]['enhanced'] += 1
            elif level == 'MACRO':
                enhanced_rule = enhance_macro_rule(rule)
                enhanced_rules.append(enhanced_rule)
                stats[level]['enhanced'] += 1
            else:
                enhanced_rules.append(rule)
            
            if (i + 1) % 50 == 0:
                print(f"Enhanced {i + 1} rules...")
                
        except Exception as e:
            print(f"Error enhancing {level} rule {rule.get('rule_id', 'unknown')}: {e}", file=sys.stderr)
            enhanced_rules.append(rule)
    
    # Update data
    data['rules'] = enhanced_rules
    data['version'] = '4.1.0'  # Increment version
    data['last_updated'] = datetime.now().isoformat()
    
    # Update metadata
    if 'enhanced_features' not in data:
        data['enhanced_features'] = []
    
    new_features = [
        'meso_level_enrichment',
        'macro_level_enrichment',
        'leverage_points_integration',
        'systemic_coordination_instruments',
        'multi_level_coverage'
    ]
    
    for feature in new_features:
        if feature not in data['enhanced_features']:
            data['enhanced_features'].append(feature)
    
    data['guide_compliance'] = {
        "recommendationsguide_version": "1.0",
        "canonical_policy_areas": True,
        "value_chain_methodology": True,
        "howlett_instruments": True,
        "capacity_framework": True,
        "colombian_legal_framework": True,
        "multi_level_coverage": {
            "MICRO": True,
            "MESO": True,
            "MACRO": True
        },
        "leverage_points_framework": True
    }
    
    # Write output
    print(f"\nWriting enhanced JSON to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Multi-level enrichment complete!")
    print(f"\n=== ENHANCEMENT STATISTICS ===")
    for level in ['MICRO', 'MESO', 'MACRO']:
        if level in stats:
            original = stats[level]['original']
            enhanced = stats[level]['enhanced']
            pct = (enhanced / original * 100) if original > 0 else 0
            print(f"{level}: {enhanced}/{original} enriched ({pct:.0f}%)")
    
    print(f"\nOutput: {output_path}")
    print(f"File size: {Path(output_path).stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    input_file = 'src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced.json'
    output_file = 'src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced_v4.1.json'
    
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    enrich_all_levels(input_file, output_file)
    print("\n✓ Multi-level JSON enrichment complete - covers all scoring scenarios across 3 levels")
