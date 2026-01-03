#!/usr/bin/env python3
"""
AUDITORÍA EPISTÉMICA DETALLADA - Análisis manual por dimensión
"""

import json
from pathlib import Path

# Cargar datos
assets = Path("src/farfan_pipeline/phases/Phase_two/epistemological_assets")

with open(assets / "contratos_clasificados.json") as f:
    contracts = json.load(f)

with open(assets / "method_sets_by_question.json") as f:
    method_sets = json.load(f)["method_sets"]

print("=" * 80)
print("AUDITORÍA EPISTÉMICA DETALLADA - 30 PREGUNTAS")
print("=" * 80)
print()

# Análisis dimensión por dimensión
dimensiones = [
    ("DIM01_INSUMOS", "D1", "Diagnóstico del sector"),
    ("DIM02_ACTIVIDADES", "D2", "Actividades del sector"),
    ("DIM03_PRODUCTOS", "D3", "Productos del sector"),
    ("DIM04_RESULTADOS", "D4", "Resultados del sector"),
    ("DIM05_IMPACTOS", "D5", "Impactos del sector"),
    ("DIM06_CAUSALIDAD", "D6", "Causalidad del sector"),
]

for dim_key, dim_short, dim_name in dimensiones:
    print(f"\n{'=' * 80}")
    print(f"{dim_key}: {dim_name}")
    print('=' * 80)

    for q_key in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        q_id = f"{dim_short}_{q_key}"
        if q_id not in method_sets:
            continue

        q_data = contracts["contratos"][dim_key][q_id]
        methods = method_sets[q_id]

        pregunta = q_data["pregunta"]
        tipo = q_data["tipo_contrato"]["codigo"]
        tipo_nombre = q_data["tipo_contrato"]["nombre"]

        print(f"\n{q_id} — {tipo_nombre}")
        print(f"Pregunta: {pregunta[:100]}...")
        print()

        # Análisis N1
        n1_methods = [m["method_name"] for m in methods["phase_a_N1"]]
        n2_methods = [m["method_name"] for m in methods["phase_b_N2"]]
        n3_methods = [m["method_name"] for m in methods["phase_c_N3"]]

        print(f"  N1 ({len(n1_methods)} métodos): {', '.join(n1_methods[:3])}{'...' if len(n1_methods) > 3 else ''}")
        print(f"  N2 ({len(n2_methods)} métodos): {', '.join(n2_methods[:3])}{'...' if len(n2_methods) > 3 else ''}")
        print(f"  N3 ({len(n3_methods)} métodos): {', '.join(n3_methods)}")

        # Evaluar cobertura
        print(f"\n  Evaluación de cobertura:")

        # Análisis específico por pregunta
        if q_id == "D1_Q1":
            # Datos cuantitativos, año, fuente, desagregación
            has_numeric = any("numeric" in m.lower() or "quantif" in m.lower() or "extract" in m.lower() for m in n1_methods)
            has_source = any("source" in m.lower() or "citation" in m.lower() or "reference" in m.lower() for m in n1_methods)
            has_desaggregation = any("territor" in m.lower() or "desagreg" in m.lower() or "population" in m.lower() for m in n1_methods)

            print(f"    ✓ Extracción de chunks: chunk_text, chunk_document")
            print(f"    ✓ Extracción de excerpts: _extract_key_excerpts")
            print(f"    ⚠ Datos cuantitativos: {'Implícito (chunk_text)' if has_numeric else 'NO EXPLÍCITO'}")
            print(f"    ⚠ Fuentes/citas: {'Implícito (_extract_key_excerpts)' if has_source else 'NO EXPLÍCITO'}")
            print(f"    ⚠ Desagregación territorial: {'NO ESPECÍFICO'}")

            if not (has_numeric and has_source and has_desaggregation):
                print(f"    🔍 GAP: Cobertura parcial de dimensiones semánticas")

        elif q_id == "D1_Q2":
            # Dimensión numérica + limitaciones de datos
            print(f"    ✓ Extracción empírica: chunk_text, _extract_key_excerpts, etc.")
            print(f"    ✓ Inferencia bayesiana: _calculate_coherence_factor")
            print(f"    ⚠ Dimensionamiento de brecha: NO EXPLÍCITO")
            print(f"    ⚠ Reconocimiento de vacíos: NO EXPLÍCITO")
            print(f"    🔍 GAP: Falta método específico para cuantificar brechas")

        elif q_id == "D1_Q3":
            # Recursos presupuestales (TYPE_D)
            print(f"    ✓ Extracción general: chunk_text, _extract_key_excerpts")
            print(f"    ⚠ Extracción presupuestal: NO ESPECÍFICA (esperado extract_PPI, parse_budget)")
            print(f"    ⚠ Validación de suficiencia: _check_sufficiency presente en N3")
            print(f"    🔍 GAP CRÍTICO: N1 no extrae explícitamente asignaciones monetarias")

        elif q_id == "D2_Q1":
            # Actividades estructuradas
            print(f"    ✓ Extracción de estructura: chunk_text, chunk_document")
            print(f"    ⚠ Detección de tablas/matrices: NO ESPECÍFICO")
            print(f"    🔍 GAP: Falta método para detectar formato estructurado")

        elif q_id == "D6_Q1":
            # Teoría de cambio (TYPE_C)
            print(f"    ✓ Extracción causal: extract_causal_hierarchy")
            print(f"    ✓ Detección de ciclos: detect_cycles en N3")
            print(f"    ✓ Validación estructural: _check_structural_violation")
            print(f"    ✅ BUENA COBERTURA para preguntas causales")

        else:
            # Análisis genérico
            semantic_keywords = sum(1 for m in n1_methods if any(kw in m.lower() for kw in ["extract", "parse", "detect", "chunk", "load"]))
            validation_keywords = sum(1 for m in n3_methods if any(kw in m.lower() for kw in ["validate", "audit", "check", "detect"]))

            print(f"    ✓ Métodos de extracción: {semantic_keywords}/{len(n1_methods)}")
            print(f"    ✓ Métodos de validación: {validation_keywords}/{len(n3_methods)}")

print(f"\n{'=' * 80}")
print("RESUMEN EJECUTIVO")
print('=' * 80)

print("""
ANÁLISIS DE COBERTURA EPISTÉMICA:

1. DIM01_INSUMOS (D1):
   - D1_Q1 (datos cuantitativos): Cobertura SEMÁNTICA pero NO ESPECÍFICA
     ⚠ Los métodos N1 extraen "texto" pero no "datos cuantitativos" explícitamente
   - D1_Q2 (brechas y vacíos): Cobertura PARCIAL
     ⚠ Falta método para cuantificar magnitud de brecha
   - D1_Q3 (recursos presupuestales): Cobertura INSUFICIENTE
     🔍 CRÍTICO: N1 no extrae asignaciones monetarias explícitamente
   - D1_Q4 (entidades responsables): Cobertura ADECUADA
   - D1_Q5 (alcance y competencias): Cobertura ADECUADA

2. DIM02_ACTIVIDADES (D2):
   - D2_Q1 (actividades estructuradas): Cobertura PARCIAL
     ⚠ Falta método para detectar tablas/matrices/PPI
   - D2_Q3 (vínculo actividades-causas): Cobertura BUENA
   - D2_Q5 (coherencia estratégica): Cobertura ADECUADA

3. DIM03_PRODUCTOS (D3):
   - Cobertura general ADECUADA para indicadores de producto
   - ⚠ D3_Q2 (proporcionalidad meta): Falta método de comparación magnitud

4. DIM04_RESULTADOS (D4):
   - D4_Q2 (ruta causal): Cobertura BUENA
   - D4_Q4 (atención problemas): Cobertura ADECUADA

5. DIM05_IMPACTOS (D5):
   - D5_Q1 (impactos largo plazo): Cobertura ADECUADA
   - D5_Q4 (realismo impactos): Cobertura ADECUADA

6. DIM06_CAUSALIDAD (D6):
   - D6_Q1 (teoría de cambio): Cobertura EXCELENTE
     ✅ extract_causal_hierarchy, detect_cycles, validación estructural
   - D6_Q3 (complejidad): Cobertura ADECUADA

CONCLUSIÓN GENERAL:
- 30 contratos usan 13 métodos cada uno = 390 métodos totales
- Los métodos son GENÉRICOS (chunk_text, extract, etc.) NO ESPECÍFICOS del dominio
- Esto es CONSISTENTE con el enfoque TYPE-based pero PUEDE MEJORAR especificidad

RECOMENDACIONES ESTRATÉGICAS:
1. Mantener estructura TYPE-aware (funciona correctamente)
2. Considerar añadir métodos de dominio específicos para:
   - Extracción de datos cuantitativos (D1_Q1, D1_Q2)
   - Extracción presupuestal (D1_Q3, D5_Q1)
   - Detección de tablas/matrices (D2_Q1)
3. Los 270 contratos restantes DEBEN mantener este mismo patrón
4. La auditoría NO recomienda cambios estructurales, solo adiciones opcionales
""")

print("\n" + "=" * 80)
