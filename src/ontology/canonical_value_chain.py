"""
Canonical value chain specification and validator.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from orchestration.factory import get_canonical_questionnaire

VALUE_CHAIN_DIMENSIONS: Dict[str, Dict[str, Any]] = {
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
                "expected_elements": [
                    "brecha_cuantificada",
                    "limitaciones_datos",
                    "subregistro",
                ],
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
                "expected_elements": [
                    "aborda_causa_raiz",
                    "vinculo_diagnostico_actividad",
                ],
            },
            "gestion_riesgos": {
                "slot": "D2-Q4",
                "expected_elements": [
                    "mitigacion_propuesta",
                    "riesgos_identificados",
                ],
            },
            "articulacion_actividades": {
                "slot": "D2-Q5",
                "expected_elements": [
                    "complementariedad_explicita",
                    "secuenciacion_logica",
                ],
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
                "expected_elements": [
                    "dosificacion_definida",
                    "proporcionalidad_meta_brecha",
                ],
            },
            "trazabilidad": {
                "slot": "D3-Q3",
                "expected_elements": [
                    "trazabilidad_organizacional",
                    "trazabilidad_presupuestal",
                ],
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
                "expected_elements": [
                    "conexion_producto_resultado",
                    "mecanismo_causal_explicito",
                ],
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
                "expected_elements": [
                    "criterios_exito_definidos",
                    "vinculo_resultado_problema",
                ],
            },
            "alineacion_estrategica": {
                "slot": "D4-Q5",
                "expected_elements": [
                    "alineacion_ods",
                    "alineacion_pnd",
                ],
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
                "expected_elements": [
                    "impacto_definido",
                    "rezago_temporal",
                    "ruta_transmision",
                ],
            },
            "medicion_impacto": {
                "slot": "D5-Q2",
                "expected_elements": [
                    "justifica_validez",
                    "usa_indices_compuestos",
                    "usa_proxies",
                ],
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
                "expected_elements": [
                    "alineacion_marcos",
                    "riesgos_sistemicos",
                ],
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
                "expected_elements": [
                    "evita_saltos_logicos",
                    "proporcionalidad_eslabones",
                ],
            },
            "testabilidad": {
                "slot": "D6-Q3",
                "expected_elements": [
                    "propone_pilotos_o_pruebas",
                    "reconoce_inconsistencias",
                ],
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
                "expected_elements": [
                    "analisis_contextual",
                    "enfoque_diferencial",
                ],
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


@dataclass
class ValidationResult:
    passed: bool
    errors: List[Dict[str, Any]]
    input_hashes: Dict[str, str]


def validate_value_chain_spec(
    monolith_path: Path,
    output_path: Path,
) -> ValidationResult:
    canonical_questionnaire = get_canonical_questionnaire(
        questionnaire_path=monolith_path,
    )
    monolith = canonical_questionnaire.data
    micro_questions = monolith.get("blocks", {}).get("micro_questions", [])
    universe_expected = set()
    for mq in micro_questions:
        for elem in mq.get("expected_elements", []) or []:
            if isinstance(elem, str):
                universe_expected.add(elem)
    errors: List[Dict[str, Any]] = []
    for dim_id, dim_cfg in VALUE_CHAIN_DIMENSIONS.items():
        base_slots = set(dim_cfg.get("base_slots", []))
        for var_name, var_cfg in dim_cfg.get("analytical_variables", {}).items():
            slot = var_cfg.get("slot")
            if slot not in base_slots:
                errors.append(
                    {
                        "dimension": dim_id,
                        "variable": var_name,
                        "error": "slot_not_in_base_slots",
                        "slot": slot,
                    }
                )
            for element in var_cfg.get("expected_elements", []):
                if element not in universe_expected:
                    errors.append(
                        {
                            "dimension": dim_id,
                            "variable": var_name,
                            "missing_expected_element": element,
                        }
                    )
    passed = len(errors) == 0
    input_hashes = {str(monolith_path): canonical_questionnaire.sha256}
    output = {
        "passed": passed,
        "errors": errors,
        "input_hashes": input_hashes,
        "record_counts": {"micro_questions": len(micro_questions)},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    return ValidationResult(passed=passed, errors=errors, input_hashes=input_hashes)


__all__ = ["VALUE_CHAIN_DIMENSIONS", "validate_value_chain_spec", "ValidationResult"]
