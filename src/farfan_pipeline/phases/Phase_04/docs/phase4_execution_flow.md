# Phase 4 Execution Flow

## Objetivo
Agregar 300 micro-preguntas puntuadas (Fase 3) en 60 puntajes de dimensión (6 dimensiones × 10 áreas de política), con trazabilidad completa, validación de hermeticidad y control de rangos.

## Flujo Secuencial
1. **Carga de configuración**: `AggregationSettings` (pesos y agrupaciones canónicas).
2. **Validación de entradas**: cobertura mínima y consistencia de IDs.
3. **Agrupación por dimensión y área**: agrupación determinista por claves canónicas.
4. **Cálculo de puntajes**:
   - Promedio ponderado por defecto.
   - Choquet integral cuando aplica (SOTA habilitado).
5. **Proveniencia**: registro de nodos y aristas en DAG.
6. **Incertidumbre**: bootstrap para métricas de confiabilidad (cuando aplica).
7. **Salida**: lista de `DimensionScore` con metadata de trazabilidad.

## Entradas
- `ScoredResult` (300 micro-preguntas).

## Salidas
- `DimensionScore` (60 dimensiones).
