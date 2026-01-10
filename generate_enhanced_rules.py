#!/usr/bin/env python3
"""
Generate enhanced recommendation rules for micro-meso-macro levels
with comprehensive scoring scenarios
"""

import json

# PA definitions with full names
PAS = {
    "PA01": "Política Pública de Género y Equidad",
    "PA02": "Seguridad y Convivencia Ciudadana",
    "PA03": "Educación y Desarrollo del Talento",
    "PA04": "Infraestructura y Vivienda Digna",
    "PA05": "Desarrollo Económico y Empleabilidad",
    "PA06": "Salud Pública y Bienestar",
    "PA07": "Justicia Transicional y Derechos Humanos",
    "PA08": "Medio Ambiente y Sostenibilidad",
    "PA09": "Cultura, Deporte y Recreación",
    "PA10": "Participación Ciudadana y Gobernanza"
}

# Dimension definitions
DIMS = {
    "DIM01": "Línea Base y Diagnóstico",
    "DIM02": "Actividades y Cronograma",
    "DIM03": "BPIN y Presupuesto",
    "DIM04": "Resultados Esperados",
    "DIM05": "Gestión de Riesgos",
    "DIM06": "Datos Abiertos y Gobernanza"
}

# Cluster definitions
CLUSTERS = {
    "CL01": "Seguridad y Paz",
    "CL02": "Desarrollo Social",
    "CL03": "Infraestructura y Territorio",
    "CL04": "Participación y Cultura"
}

# Scoring thresholds (on 3-point scale: 0-3)
MICRO_THRESHOLDS = {
    "CRITICO": {"max": 0.8, "label": "CRÍTICO", "urgency": "INMEDIATA"},
    "DEFICIENTE": {"max": 1.2, "label": "DEFICIENTE", "urgency": "ALTA"},
    "INSUFICIENTE": {"max": 1.65, "label": "INSUFICIENTE", "urgency": "MEDIA"},
    "ACEPTABLE": {"max": 2.0, "label": "ACEPTABLE", "urgency": "BAJA"},
    "BUENO": {"max": 2.4, "label": "BUENO", "urgency": "MANTENIMIENTO"},
    "MUY_BUENO": {"max": 2.7, "label": "MUY BUENO", "urgency": "OPTIMIZACIÓN"}
}

# Responsible entities by PA
RESPONSIBLE_ENTITIES = {
    "PA01": "Secretaría de la Mujer Municipal",
    "PA02": "Secretaría de Gobierno y Seguridad",
    "PA03": "Secretaría de Educación Municipal",
    "PA04": "Secretaría de Infraestructura",
    "PA05": "Secretaría de Desarrollo Económico",
    "PA06": "Secretaría de Salud Municipal",
    "PA07": "Oficina de Derechos Humanos",
    "PA08": "Secretaría de Medio Ambiente",
    "PA09": "Secretaría de Cultura y Deporte",
    "PA10": "Secretaría de Participación Ciudadana"
}

def generate_micro_rules_enhanced():
    """Generate enhanced MICRO level rules with multiple scoring thresholds"""
    rules = []

    for pa_id, pa_name in PAS.items():
        for dim_id, dim_name in DIMS.items():
            for threshold_key, threshold_data in MICRO_THRESHOLDS.items():

                rule_id = f"REC-MICRO-{pa_id}-{dim_id}-{threshold_key}"

                # Context-specific interventions
                interventions = generate_intervention_by_threshold(
                    pa_id, pa_name, dim_id, dim_name, threshold_key, threshold_data
                )

                rule = {
                    "rule_id": rule_id,
                    "level": "MICRO",
                    "scoring_scenario": threshold_data["label"],
                    "urgency": threshold_data["urgency"],
                    "when": {
                        "pa_id": pa_id,
                        "dim_id": dim_id,
                        "score_lt": threshold_data["max"]
                    },
                    "template": {
                        "problem": interventions["problem"],
                        "intervention": interventions["intervention"],
                        "indicator": {
                            "name": f"{pa_id}-{dim_id} mejora {threshold_data['label'].lower()}",
                            "baseline": None,
                            "target": min(threshold_data["max"] + 0.5, 3.0),
                            "unit": "score",
                            "formula": "AVG(dimension_scores)",
                            "acceptable_range": [threshold_data["max"], 3.0],
                            "baseline_measurement_date": "2024-01-01",
                            "measurement_frequency": get_measurement_frequency(threshold_data["urgency"]),
                            "data_source": "Sistema de Seguimiento de Planes (SSP)",
                            "data_source_query": f"SELECT AVG(score) FROM dimension_scores WHERE pa_id = '{pa_id}' AND dim_id = '{dim_id}'",
                            "responsible_measurement": "Oficina de Planeación Municipal",
                            "escalation_if_below": threshold_data["max"] * 0.9
                        },
                        "responsible": {
                            "entity": RESPONSIBLE_ENTITIES.get(pa_id, "Entidad Responsable"),
                            "role": f"lidera la implementación de {pa_name}",
                            "partners": get_partners_by_pa(pa_id),
                            "legal_mandate": get_legal_mandate(pa_id),
                            "approval_chain": get_approval_chain(threshold_data["urgency"]),
                            "escalation_path": get_escalation_path(threshold_data["urgency"])
                        },
                        "horizon": {
                            "start": "T0",
                            "end": get_time_horizon(threshold_data["urgency"]),
                            "start_type": "plan_approval_date",
                            "duration_months": get_duration_months(threshold_data["urgency"]),
                            "milestones": get_milestones(threshold_data["urgency"]),
                            "dependencies": [],
                            "critical_path": threshold_data["urgency"] in ["INMEDIATA", "ALTA"]
                        },
                        "costs": generate_costs(threshold_data["urgency"], pa_id, dim_id),
                        "verification": {
                            "method": get_verification_method(dim_id),
                            "frequency": get_measurement_frequency(threshold_data["urgency"]),
                            "responsible": "Oficina de Control Interno",
                            "evidence_required": get_evidence_requirements(dim_id)
                        }
                    }
                }

                rules.append(rule)

    return rules

def generate_intervention_by_threshold(pa_id, pa_name, dim_id, dim_name, threshold_key, threshold_data):
    """Generate context-specific problem and intervention descriptions"""

    urgency_text = {
        "INMEDIATA": "requiere intervención de emergencia",
        "ALTA": "requiere restructuración urgente",
        "MEDIA": "requiere mejoras significativas",
        "BAJA": "requiere ajustes menores",
        "MANTENIMIENTO": "requiere mantenimiento y vigilancia",
        "OPTIMIZACIÓN": "puede optimizarse para excelencia"
    }

    dim_focus = {
        "DIM01": "línea base y diagnóstico",
        "DIM02": "actividades y cronograma",
        "DIM03": "presupuesto BPIN",
        "DIM04": "resultados esperados",
        "DIM05": "gestión de riesgos",
        "DIM06": "datos abiertos y gobernanza"
    }

    problem = (f"La dimensión {dim_id} ({dim_name}) de {pa_id} ({pa_name}) "
               f"presenta nivel {threshold_data['label']} (< {threshold_data['max']}), "
               f"lo que {urgency_text[threshold_data['urgency']]} en {dim_focus[dim_id]}.")

    intervention = generate_specific_intervention(pa_id, dim_id, threshold_key)

    return {
        "problem": problem,
        "intervention": intervention
    }

def generate_specific_intervention(pa_id, dim_id, threshold_key):
    """Generate specific interventions based on PA, DIM, and severity"""

    base_interventions = {
        "DIM01": {
            "CRITICO": "Levantar línea base de emergencia con datos mínimos viables, establecer fuentes primarias y definir indicadores críticos en 30 días.",
            "DEFICIENTE": "Consolidar línea base con series históricas de al menos 3 años, validar fuentes y establecer metodología de actualización trimestral.",
            "INSUFICIENTE": "Completar brechas en línea base, homologar con estándares nacionales y establecer sistema de seguimiento mensual.",
            "ACEPTABLE": "Refinar línea base con datos desagregados, mejorar calidad de fuentes y establecer comparabilidad territorial.",
            "BUENO": "Mantener actualización de línea base, incorporar nuevos indicadores emergentes y fortalecer capacidades analíticas.",
            "MUY_BUENO": "Optimizar línea base con analítica avanzada, establecer sistema de alertas tempranas y compartir mejores prácticas."
        },
        "DIM02": {
            "CRITICO": "Diseñar cronograma de emergencia con hitos críticos, asignar responsables inmediatos y establecer seguimiento semanal.",
            "DEFICIENTE": "Reestructurar cronograma con metodología de gestión de proyectos, establecer dependencias críticas y sistema de alertas.",
            "INSUFICIENTE": "Ajustar cronograma con hitos verificables, establecer responsables por actividad y sistema de seguimiento quincenal.",
            "ACEPTABLE": "Refinar cronograma con mejores prácticas, optimizar ruta crítica y mejorar sistema de seguimiento.",
            "BUENO": "Mantener cronograma actualizado, gestionar cambios proactivamente y documentar lecciones aprendidas.",
            "MUY_BUENO": "Optimizar cronograma con metodologías ágiles, implementar gestión de cambios avanzada y compartir mejores prácticas."
        },
        "DIM03": {
            "CRITICO": "Estructurar presupuesto mínimo viable, gestionar recursos de emergencia y establecer control diario de ejecución.",
            "DEFICIENTE": "Reestructurar presupuesto con fuentes identificadas, elaborar BPIN completo y establecer sistema de seguimiento semanal.",
            "INSUFICIENTE": "Completar BPIN con todas las fichas requeridas, validar fuentes de financiación y establecer seguimiento quincenal.",
            "ACEPTABLE": "Refinar presupuesto con análisis de eficiencia, diversificar fuentes y mejorar sistema de seguimiento.",
            "BUENO": "Mantener ejecución presupuestal eficiente, gestionar modificaciones proactivamente y optimizar recursos.",
            "MUY_BUENO": "Optimizar eficiencia presupuestal, implementar gestión basada en resultados y compartir mejores prácticas."
        },
        "DIM04": {
            "CRITICO": "Definir resultados mínimos medibles, establecer indicadores de emergencia y sistema de verificación inmediata.",
            "DEFICIENTE": "Reformular cadena de resultados, establecer indicadores SMART completos y sistema de medición trimestral.",
            "INSUFICIENTE": "Completar marco de resultados, refinar indicadores con metas verificables y establecer medición mensual.",
            "ACEPTABLE": "Refinar marco de resultados con teoría de cambio, mejorar calidad de indicadores y optimizar medición.",
            "BUENO": "Mantener sistema de resultados actualizado, gestionar desviaciones proactivamente y documentar logros.",
            "MUY_BUENO": "Optimizar gestión por resultados, implementar evaluación de impacto y compartir aprendizajes."
        },
        "DIM05": {
            "CRITICO": "Identificar riesgos críticos inmediatos, establecer controles de emergencia y sistema de monitoreo diario.",
            "DEFICIENTE": "Elaborar matriz de riesgos completa, establecer controles prioritarios y sistema de monitoreo semanal.",
            "INSUFICIENTE": "Completar gestión de riesgos con controles para todos los riesgos identificados y monitoreo quincenal.",
            "ACEPTABLE": "Refinar gestión de riesgos con análisis cuantitativo, mejorar controles y optimizar monitoreo.",
            "BUENO": "Mantener gestión de riesgos actualizada, gestionar nuevos riesgos proactivamente y fortalecer controles.",
            "MUY_BUENO": "Optimizar gestión de riesgos con enfoque predictivo, implementar controles avanzados y compartir mejores prácticas."
        },
        "DIM06": {
            "CRITICO": "Establecer repositorio mínimo de datos críticos, publicar información básica y establecer actualización semanal.",
            "DEFICIENTE": "Implementar sistema de datos abiertos, publicar datasets prioritarios y establecer actualización quincenal.",
            "INSUFICIENTE": "Completar publicación de datos según estándares, mejorar metadatos y establecer actualización mensual.",
            "ACEPTABLE": "Refinar calidad de datos abiertos, mejorar usabilidad y optimizar frecuencia de actualización.",
            "BUENO": "Mantener datos abiertos actualizados, incorporar nuevos datasets y fortalecer capacidades de usuarios.",
            "MUY_BUENO": "Optimizar ecosistema de datos abiertos, implementar analítica ciudadana y compartir mejores prácticas."
        }
    }

    return base_interventions.get(dim_id, {}).get(threshold_key, "Implementar intervención apropiada según contexto.")

def generate_meso_rules_enhanced():
    """Generate enhanced MESO level rules with cross-cluster and multi-scenario logic"""
    rules = []

    # Cross-cluster dependency rules
    cluster_pairs = [
        ("CL01", "CL02", "Seguridad-Social"),
        ("CL01", "CL03", "Seguridad-Territorio"),
        ("CL02", "CL03", "Social-Territorio"),
        ("CL02", "CL04", "Social-Participación"),
        ("CL03", "CL04", "Territorio-Participación")
    ]

    for cl1, cl2, label in cluster_pairs:
        for score_band in ["CRITICO", "BAJO", "MEDIO", "ALTO", "EXCELENTE"]:
            rule_id = f"REC-MESO-CROSS-{cl1}-{cl2}-{score_band}"

            rule = {
                "rule_id": rule_id,
                "level": "MESO",
                "scoring_scenario": f"DEPENDENCIA {label}",
                "when": {
                    "cluster_ids": [cl1, cl2],
                    "both_in_band": score_band,
                    "interdependency": True
                },
                "template": generate_cross_cluster_template(cl1, cl2, score_band, label),
                "responsible": {
                    "entity": "Comité de Coordinación Interinstitucional",
                    "role": "coordina acción integrada entre clusters",
                    "partners": get_cluster_partners(cl1, cl2),
                    "legal_mandate": "Estatuto Orgánico Municipal",
                    "approval_chain": get_approval_chain("ALTA"),
                    "escalation_path": get_escalation_path("ALTA")
                },
                "horizon": {
                    "start": "T0",
                    "end": "T2",
                    "start_type": "plan_approval_date",
                    "duration_months": 12,
                    "milestones": get_milestones("MEDIA"),
                    "dependencies": [cl1, cl2],
                    "critical_path": True
                }
            }

            rules.append(rule)

    # Multi-PA failure patterns within clusters
    for cluster_id, cluster_name in CLUSTERS.items():
        for num_weak_pas in [2, 3]:
            rule_id = f"REC-MESO-{cluster_id}-MULTI-PA-WEAK-{num_weak_pas}"

            rule = {
                "rule_id": rule_id,
                "level": "MESO",
                "scoring_scenario": f"DEBILIDAD MÚLTIPLE ({num_weak_pas} PAs)",
                "when": {
                    "cluster_id": cluster_id,
                    "weak_pas_count": num_weak_pas,
                    "threshold": 1.5
                },
                "template": generate_multi_pa_weak_template(cluster_id, cluster_name, num_weak_pas),
                "responsible": get_cluster_responsible(cluster_id),
                "horizon": {
                    "start": "T0",
                    "end": "T2",
                    "duration_months": 9,
                    "milestones": get_milestones("ALTA"),
                    "critical_path": True
                }
            }

            rules.append(rule)

    # Momentum tracking rules (improving vs deteriorating)
    for cluster_id in CLUSTERS.keys():
        for momentum in ["MEJORANDO", "DETERIORANDO", "ESTANCADO"]:
            rule_id = f"REC-MESO-{cluster_id}-MOMENTUM-{momentum}"

            rule = {
                "rule_id": rule_id,
                "level": "MESO",
                "scoring_scenario": f"TENDENCIA {momentum}",
                "when": {
                    "cluster_id": cluster_id,
                    "momentum": momentum,
                    "trend_months": 3
                },
                "template": generate_momentum_template(cluster_id, momentum),
                "responsible": get_cluster_responsible(cluster_id),
                "horizon": {
                    "start": "T0",
                    "end": "T1",
                    "duration_months": 6,
                    "milestones": get_milestones("MEDIA")
                }
            }

            rules.append(rule)

    return rules

def generate_macro_rules_enhanced():
    """Generate enhanced MACRO level rules for system-wide scenarios"""
    rules = []

    # Crisis management scenarios
    crisis_scenarios = [
        {
            "id": "CRISIS-MULTISECTORIAL",
            "condition": "3+ clusters en CRÍTICO/DEFICIENTE",
            "intervention": "Plan de Choque Integral Municipal"
        },
        {
            "id": "CRISIS-FOCAL",
            "condition": "1 cluster CRÍTICO, otros ACEPTABLE+",
            "intervention": "Intervención Focalizada con Transferencia de Recursos"
        },
        {
            "id": "ESTANCAMIENTO",
            "condition": "Sin cambios significativos en 6 meses",
            "intervention": "Revisión Estratégica y Renovación de Liderazgos"
        }
    ]

    for scenario in crisis_scenarios:
        rule = {
            "rule_id": f"REC-MACRO-{scenario['id']}",
            "level": "MACRO",
            "scoring_scenario": scenario['id'],
            "when": {
                "condition": scenario['condition'],
                "system_wide": True
            },
            "template": {
                "problem": f"Situación macro de {scenario['id']}: {scenario['condition']}",
                "intervention": scenario['intervention'],
                "indicator": {
                    "name": f"Superación {scenario['id']}",
                    "target": 0.85,
                    "unit": "proporción",
                    "measurement_frequency": "mensual"
                }
            },
            "responsible": {
                "entity": "Despacho del Alcalde",
                "role": "lidera respuesta integral",
                "partners": ["Todas las Secretarías", "Concejo Municipal", "Órganos de Control"]
            },
            "horizon": {
                "start": "T0",
                "end": "T3",
                "duration_months": 18,
                "critical_path": True
            }
        }

        rules.append(rule)

    # Transformation scenarios
    transformation_paths = [
        ("DEFICIENTE_A_ACEPTABLE", "Transformación Básica"),
        ("ACEPTABLE_A_BUENO", "Mejora Continua"),
        ("BUENO_A_EXCELENTE", "Búsqueda de Excelencia"),
        ("EXCELENTE_SOSTENIBLE", "Mantenimiento de Excelencia")
    ]

    for path_id, path_name in transformation_paths:
        rule = {
            "rule_id": f"REC-MACRO-TRANSFORM-{path_id}",
            "level": "MACRO",
            "scoring_scenario": f"TRANSFORMACIÓN: {path_name}",
            "when": {
                "transformation_path": path_id,
                "readiness": True
            },
            "template": generate_transformation_template(path_id, path_name),
            "responsible": {
                "entity": "Secretaría de Planeación Municipal",
                "role": "coordina transformación institucional",
                "partners": ["Todas las Secretarías", "Asesoría externa si requerido"]
            },
            "horizon": {
                "duration_months": 12,
                "milestones": get_milestones("MEDIA")
            }
        }

        rules.append(rule)

    # Inter-cluster balance scenarios
    balance_scenarios = [
        "DESEQUILIBRIO_EXTREMO",  # 1 excelente, 1 crítico
        "DESEQUILIBRIO_MODERADO",  # Varianza > 20 puntos
        "EQUILIBRIO_BAJO",  # Todos cerca, pero todos bajos
        "EQUILIBRIO_ALTO"  # Todos cerca, todos altos
    ]

    for balance in balance_scenarios:
        rule = {
            "rule_id": f"REC-MACRO-BALANCE-{balance}",
            "level": "MACRO",
            "scoring_scenario": f"BALANCE: {balance}",
            "when": {
                "balance_type": balance,
                "cluster_variance": True
            },
            "template": generate_balance_template(balance),
            "responsible": {
                "entity": "Comité de Coordinación Territorial",
                "role": "gestiona equilibrio intersectorial"
            },
            "horizon": {
                "duration_months": 12
            }
        }

        rules.append(rule)

    return rules

# Helper functions
def get_measurement_frequency(urgency):
    freq_map = {
        "INMEDIATA": "semanal",
        "ALTA": "quincenal",
        "MEDIA": "mensual",
        "BAJA": "bimestral",
        "MANTENIMIENTO": "trimestral",
        "OPTIMIZACIÓN": "trimestral"
    }
    return freq_map.get(urgency, "mensual")

def get_time_horizon(urgency):
    horizon_map = {
        "INMEDIATA": "T0+3M",
        "ALTA": "T1",
        "MEDIA": "T1",
        "BAJA": "T2",
        "MANTENIMIENTO": "T2",
        "OPTIMIZACIÓN": "T3"
    }
    return horizon_map.get(urgency, "T1")

def get_duration_months(urgency):
    duration_map = {
        "INMEDIATA": 3,
        "ALTA": 6,
        "MEDIA": 6,
        "BAJA": 9,
        "MANTENIMIENTO": 12,
        "OPTIMIZACIÓN": 12
    }
    return duration_map.get(urgency, 6)

def get_partners_by_pa(pa_id):
    partners_map = {
        "PA01": ["Secretaría de Planeación", "Alta Consejería de la Mujer", "DANE"],
        "PA02": ["Policía Nacional", "Fiscalía", "Unidad para las Víctimas"],
        "PA03": ["Ministerio de Educación", "ICBF", "Instituciones Educativas"],
        "PA04": ["Ministerio de Vivienda", "Findeter", "Empresas de Servicios"],
        "PA05": ["SENA", "Cámara de Comercio", "Gremios Empresariales"],
        "PA06": ["Ministerio de Salud", "EPS", "IPS Municipales"],
        "PA07": ["Fiscalía", "Defensoría del Pueblo", "Organizaciones de Víctimas"],
        "PA08": ["Corporación Autónoma Regional", "Ministerio de Ambiente"],
        "PA09": ["Ministerio de Cultura", "Coldeportes", "Organizaciones Culturales"],
        "PA10": ["Concejos Comunales", "JAC", "Veeduría Ciudadana"]
    }
    return partners_map.get(pa_id, ["Secretaría de Planeación"])

def get_legal_mandate(pa_id):
    mandate_map = {
        "PA01": "Ley 1257 de 2008 - Prevención de violencias contra la mujer",
        "PA02": "Ley 1801 de 2016 - Código Nacional de Policía y Convivencia",
        "PA03": "Ley 115 de 1994 - Ley General de Educación",
        "PA04": "Ley 1537 de 2012 - Vivienda y hábitat",
        "PA05": "Ley 1014 de 2006 - Fomento a la cultura del emprendimiento",
        "PA06": "Ley 1751 de 2015 - Derecho fundamental a la salud",
        "PA07": "Ley 1448 de 2011 - Víctimas y restitución de tierras",
        "PA08": "Ley 99 de 1993 - Sistema Nacional Ambiental",
        "PA09": "Ley 1185 de 2008 - Patrimonio cultural",
        "PA10": "Ley 134 de 1994 - Mecanismos de participación ciudadana"
    }
    return mandate_map.get(pa_id, "Constitución Política y Estatuto Orgánico Municipal")

def get_approval_chain(urgency):
    if urgency in ["INMEDIATA", "ALTA"]:
        return [
            {"level": 1, "role": "Director/Coordinador", "decision": "Aprueba plan inmediato", "max_days": 2},
            {"level": 2, "role": "Secretario/a", "decision": "Aprueba recursos", "max_days": 3},
            {"level": 3, "role": "Alcalde", "decision": "Aprobación final", "max_days": 5}
        ]
    else:
        return [
            {"level": 1, "role": "Director/Coordinador", "decision": "Aprueba plan de trabajo", "max_days": 5},
            {"level": 2, "role": "Secretario/a", "decision": "Aprueba presupuesto", "max_days": 10},
            {"level": 3, "role": "Planeación", "decision": "Valida coherencia PDM", "max_days": 15},
            {"level": 4, "role": "Alcalde", "decision": "Aprobación final (si aplica)", "max_days": 20}
        ]

def get_escalation_path(urgency):
    threshold_map = {
        "INMEDIATA": 3,
        "ALTA": 7,
        "MEDIA": 15,
        "BAJA": 30,
        "MANTENIMIENTO": 45,
        "OPTIMIZACIÓN": 60
    }

    return {
        "threshold_days_delay": threshold_map.get(urgency, 15),
        "escalate_to": "Secretaría de Planeación" if urgency not in ["INMEDIATA", "ALTA"] else "Despacho del Alcalde",
        "final_escalation": "Despacho del Alcalde",
        "consequences": [
            "Revisión presupuestal",
            "Reasignación de responsables",
            "Intervención directa del nivel superior" if urgency in ["INMEDIATA", "ALTA"] else "Asistencia técnica"
        ]
    }

def get_milestones(urgency):
    if urgency in ["INMEDIATA", "ALTA"]:
        return [
            {
                "name": "Inicio inmediato",
                "offset_months": 0.5,
                "deliverables": ["Plan de acción inmediata aprobado"],
                "verification_required": True
            },
            {
                "name": "Primera revisión",
                "offset_months": 1,
                "deliverables": ["Informe de avance inicial"],
                "verification_required": True
            },
            {
                "name": "Entrega final",
                "offset_months": get_duration_months(urgency),
                "deliverables": ["Todos los productos esperados"],
                "verification_required": True
            }
        ]
    else:
        return [
            {
                "name": "Inicio de implementación",
                "offset_months": 1,
                "deliverables": ["Plan de trabajo aprobado"],
                "verification_required": True
            },
            {
                "name": "Revisión intermedia",
                "offset_months": get_duration_months(urgency) / 2,
                "deliverables": ["Informe de avance"],
                "verification_required": True
            },
            {
                "name": "Entrega final",
                "offset_months": get_duration_months(urgency),
                "deliverables": ["Todos los productos esperados"],
                "verification_required": True
            }
        ]

def generate_costs(urgency, pa_id, dim_id):
    base_cost = 500000000  # Base cost in COP

    urgency_multiplier = {
        "INMEDIATA": 2.0,
        "ALTA": 1.5,
        "MEDIA": 1.0,
        "BAJA": 0.7,
        "MANTENIMIENTO": 0.5,
        "OPTIMIZACIÓN": 0.8
    }

    multiplier = urgency_multiplier.get(urgency, 1.0)
    total = int(base_cost * multiplier)

    return {
        "estimated_total": total,
        "currency": "COP",
        "breakdown": {
            "personal": int(total * 0.5),
            "consultancy": int(total * 0.3),
            "technology": int(total * 0.2)
        },
        "funding_sources": [
            {
                "source": "SGP - Sistema General de Participaciones",
                "amount": int(total * 0.6),
                "confirmed": False
            },
            {
                "source": "Recursos Propios",
                "amount": int(total * 0.4),
                "confirmed": False
            }
        ],
        "fiscal_year": 2025
    }

def get_verification_method(dim_id):
    methods = {
        "DIM01": "Auditoría de línea base y fuentes de datos",
        "DIM02": "Revisión de cronogramas y seguimiento de hitos",
        "DIM03": "Auditoría presupuestal y BPIN",
        "DIM04": "Medición de indicadores de resultado",
        "DIM05": "Revisión de matriz de riesgos y controles",
        "DIM06": "Auditoría de datos abiertos y metadatos"
    }
    return methods.get(dim_id, "Verificación estándar")

def get_evidence_requirements(dim_id):
    requirements = {
        "DIM01": ["Documento de línea base", "Series estadísticas", "Validación de fuentes"],
        "DIM02": ["Cronograma detallado", "Actas de seguimiento", "Evidencia de hitos cumplidos"],
        "DIM03": ["Fichas BPIN", "Certificados presupuestales", "Informes de ejecución"],
        "DIM04": ["Mediciones de indicadores", "Bases de datos", "Informes de resultados"],
        "DIM05": ["Matriz de riesgos", "Evidencia de controles", "Informes de monitoreo"],
        "DIM06": ["Datasets publicados", "Metadatos completos", "Registros de actualización"]
    }
    return requirements.get(dim_id, ["Evidencia documental", "Registros oficiales"])

def get_cluster_partners(cl1, cl2):
    cluster_entities = {
        "CL01": ["Secretaría de Gobierno", "Policía Nacional", "Unidad de Víctimas"],
        "CL02": ["Secretaría de la Mujer", "Secretaría de Educación", "Secretaría de Salud"],
        "CL03": ["Secretaría de Infraestructura", "Secretaría de Medio Ambiente"],
        "CL04": ["Secretaría de Cultura", "Secretaría de Participación"]
    }

    partners = cluster_entities.get(cl1, []) + cluster_entities.get(cl2, [])
    return list(set(partners))

def get_cluster_responsible(cluster_id):
    responsible_map = {
        "CL01": {
            "entity": "Consejo de Seguridad y Paz Territorial",
            "role": "coordina articulación de seguridad y paz",
            "partners": ["Secretaría de Gobierno", "Policía", "Fiscalía"]
        },
        "CL02": {
            "entity": "Comité de Desarrollo Social",
            "role": "coordina políticas sociales integradas",
            "partners": ["Secretarías de Mujer, Educación, Salud"]
        },
        "CL03": {
            "entity": "Comité Territorial Socioambiental",
            "role": "coordina desarrollo territorial sostenible",
            "partners": ["Secretarías de Infraestructura, Ambiente"]
        },
        "CL04": {
            "entity": "Consejo de Participación y Cultura",
            "role": "coordina participación ciudadana y cultura",
            "partners": ["Secretarías de Cultura, Participación"]
        }
    }

    return responsible_map.get(cluster_id, {
        "entity": "Comité Coordinador",
        "role": "coordina implementación",
        "partners": ["Secretaría de Planeación"]
    })

def generate_cross_cluster_template(cl1, cl2, score_band, label):
    cluster_names = {
        "CL01": "Seguridad y Paz",
        "CL02": "Desarrollo Social",
        "CL03": "Infraestructura y Territorio",
        "CL04": "Participación y Cultura"
    }

    problem = (f"Los clusters {cl1} ({cluster_names[cl1]}) y {cl2} ({cluster_names[cl2]}) "
               f"presentan ambos nivel {score_band}, evidenciando interdependencia crítica "
               f"en el eje {label} que requiere intervención coordinada.")

    intervention = (f"Implementar plan integrado {label} con objetivos compartidos, "
                   f"recursos coordinados y seguimiento conjunto para superar la situación {score_band} "
                   f"en ambos clusters simultáneamente.")

    return {
        "problem": problem,
        "intervention": intervention,
        "indicator": {
            "name": f"Integración {label} - {score_band}",
            "target": 0.85,
            "unit": "proporción",
            "measurement_frequency": "mensual",
            "data_source": "Sistema de Seguimiento de Planes (SSP)"
        }
    }

def generate_multi_pa_weak_template(cluster_id, cluster_name, num_weak):
    problem = (f"El cluster {cluster_id} ({cluster_name}) presenta {num_weak} Acciones Públicas "
               f"con puntajes deficientes simultáneos, indicando debilidad estructural del cluster "
               f"que compromete su capacidad de cumplir objetivos sectoriales.")

    intervention = (f"Implementar plan de fortalecimiento integral del cluster con intervenciones "
                   f"coordinadas en las {num_weak} PAs débiles, redistribución de recursos, "
                   f"capacitación de equipos y seguimiento intensivo hasta alcanzar nivel aceptable.")

    return {
        "problem": problem,
        "intervention": intervention,
        "indicator": {
            "name": f"{cluster_id} fortalecimiento multi-PA",
            "target": 0.80,
            "unit": "proporción",
            "measurement_frequency": "quincenal"
        }
    }

def generate_momentum_template(cluster_id, momentum):
    momentum_text = {
        "MEJORANDO": "muestra tendencia positiva sostenida en los últimos 3 meses",
        "DETERIORANDO": "muestra deterioro progresivo en los últimos 3 meses",
        "ESTANCADO": "no presenta cambios significativos en los últimos 3 meses"
    }

    intervention_text = {
        "MEJORANDO": "Acelerar impulso positivo con recursos adicionales y visibilización de logros",
        "DETERIORANDO": "Intervención correctiva urgente para revertir tendencia negativa",
        "ESTANCADO": "Renovar enfoque estratégico y movilizar nuevos recursos para activar avance"
    }

    problem = f"El cluster {cluster_id} {momentum_text[momentum]}, requiriendo acción específica."

    return {
        "problem": problem,
        "intervention": intervention_text[momentum],
        "indicator": {
            "name": f"{cluster_id} momentum {momentum}",
            "target": 0.75,
            "unit": "score",
            "measurement_frequency": "mensual"
        }
    }

def generate_transformation_template(path_id, path_name):
    transformations = {
        "DEFICIENTE_A_ACEPTABLE": {
            "problem": "Sistema municipal en nivel DEFICIENTE, requiere transformación básica urgente",
            "intervention": "Plan de Transformación Básica con reformas estructurales, fortalecimiento institucional y recursos prioritarios"
        },
        "ACEPTABLE_A_BUENO": {
            "problem": "Sistema municipal en nivel ACEPTABLE, con potencial de mejora continua",
            "intervention": "Programa de Mejora Continua con optimización de procesos, capacitación avanzada y gestión de calidad"
        },
        "BUENO_A_EXCELENTE": {
            "problem": "Sistema municipal en nivel BUENO, preparado para búsqueda de excelencia",
            "intervention": "Estrategia de Excelencia con innovación, benchmarking internacional y liderazgo sectorial"
        },
        "EXCELENTE_SOSTENIBLE": {
            "problem": "Sistema municipal alcanzó EXCELENCIA, requiere estrategia de sostenibilidad",
            "intervention": "Plan de Sostenibilidad de Excelencia con gestión del conocimiento, mentoría y mejora continua"
        }
    }

    template = transformations.get(path_id, {
        "problem": "Transformación requerida",
        "intervention": "Implementar estrategia de transformación apropiada"
    })

    return {
        "problem": template["problem"],
        "intervention": template["intervention"],
        "indicator": {
            "name": f"Transformación {path_name}",
            "target": 0.85,
            "unit": "proporción",
            "measurement_frequency": "mensual"
        }
    }

def generate_balance_template(balance_type):
    templates = {
        "DESEQUILIBRIO_EXTREMO": {
            "problem": "Desequilibrio extremo: un cluster excelente coexiste con cluster crítico",
            "intervention": "Transferencia de capacidades y recursos desde cluster líder hacia cluster rezagado"
        },
        "DESEQUILIBRIO_MODERADO": {
            "problem": "Desequilibrio moderado con varianza > 20 puntos entre clusters",
            "intervention": "Nivelación gradual con redistribución de recursos y asistencia técnica"
        },
        "EQUILIBRIO_BAJO": {
            "problem": "Equilibrio en niveles bajos: todos los clusters requieren mejora",
            "intervention": "Plan de elevación general con recursos transversales y reforma institucional"
        },
        "EQUILIBRIO_ALTO": {
            "problem": "Equilibrio en niveles altos: oportunidad de liderazgo territorial",
            "intervention": "Estrategia de liderazgo regional y sostenibilidad de resultados"
        }
    }

    template = templates.get(balance_type, {
        "problem": "Situación de balance requiere atención",
        "intervention": "Gestionar equilibrio intersectorial apropiadamente"
    })

    return {
        "problem": template["problem"],
        "intervention": template["intervention"],
        "indicator": {
            "name": f"Balance {balance_type}",
            "target": 0.80,
            "unit": "varianza",
            "measurement_frequency": "mensual"
        }
    }

def main():
    """Generate all enhanced rules and save to JSON"""

    print("Generating enhanced MICRO rules...")
    micro_rules = generate_micro_rules_enhanced()
    print(f"Generated {len(micro_rules)} MICRO rules")

    print("Generating enhanced MESO rules...")
    meso_rules = generate_meso_rules_enhanced()
    print(f"Generated {len(meso_rules)} MESO rules")

    print("Generating enhanced MACRO rules...")
    macro_rules = generate_macro_rules_enhanced()
    print(f"Generated {len(macro_rules)} MACRO rules")

    # Combine all rules
    all_new_rules = micro_rules + meso_rules + macro_rules

    print(f"\nTotal new rules generated: {len(all_new_rules)}")
    print(f"  - MICRO: {len(micro_rules)}")
    print(f"  - MESO: {len(meso_rules)}")
    print(f"  - MACRO: {len(macro_rules)}")

    # Save to temporary file for review
    output_file = "/home/user/FARFAN_MPP/new_enhanced_rules.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_new_rules, f, indent=2, ensure_ascii=False)

    print(f"\nNew rules saved to: {output_file}")
    print("Ready to merge with existing rules.")

    return all_new_rules

if __name__ == "__main__":
    main()
