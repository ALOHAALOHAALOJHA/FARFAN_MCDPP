"""
Core type definitions for FARFAN pipeline.

This module contains fundamental enumerations and types used across the pipeline,
particularly for causal chain analysis and theory of change validation.

Author: F.A.R.F.A.N Core Team
Created: 2026-01-16
"""

from __future__ import annotations

from enum import Enum


class CategoriaCausal(Enum):
    """
    Jerarquía de categorías causales en el Marco Lógico / Teoría de Cambio.
    
    Representa las cinco categorías del encadenamiento causal estándar:
    INSUMOS → PROCESOS → PRODUCTOS → RESULTADOS → CAUSALIDAD
    
    Values:
        INSUMOS (1): Diagnóstico y recursos iniciales
        PROCESOS (2): Actividades y operaciones (también llamado ACTIVIDADES)
        PRODUCTOS (3): Outputs y entregables verificables
        RESULTADOS (4): Outcomes y cambios en la población
        CAUSALIDAD (5): Teoría de cambio explícita e impactos de largo plazo
    
    Esta jerarquía es fundamental para validar la coherencia estructural de
    planes de desarrollo territorial y asegurar la completitud de las teorías
    de cambio.
    """
    
    INSUMOS = 1      # D1: Diagnóstico y Recursos
    PROCESOS = 2     # D2: Diseño de Intervención (también ACTIVIDADES)
    PRODUCTOS = 3    # D3: Productos y Outputs
    RESULTADOS = 4   # D4: Resultados y Outcomes
    CAUSALIDAD = 5   # D5+D6: Impactos y Teoría de Cambio
