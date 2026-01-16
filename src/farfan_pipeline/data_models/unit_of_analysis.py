"""
Unit of analysis definitions for calibration and Bayesian analysis.

This module provides classes to represent the territorial and fiscal context
of municipalities for proper calibration of Bayesian priors and analysis.

Author: F.A.R.F.A.N Core Team
Created: 2026-01-16
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class FiscalContext(Enum):
    """
    Categorización de la capacidad fiscal de municipios colombianos.
    
    Esta clasificación se basa en la dependencia del Sistema General de Participaciones (SGP)
    y la capacidad de generación de recursos propios.
    
    Values:
        HIGH_CAPACITY: Municipios con alta capacidad fiscal y generación de recursos propios
        MEDIUM_CAPACITY: Municipios con capacidad fiscal moderada
        LOW_CAPACITY: Municipios dependientes del SGP (Sistema General de Participaciones)
    """
    
    HIGH_CAPACITY = auto()
    MEDIUM_CAPACITY = auto()
    LOW_CAPACITY = auto()


@dataclass
class UnitOfAnalysis:
    """
    Representa las características de una unidad territorial de análisis.
    
    Esta clase encapsula las propiedades municipales relevantes para calibrar
    los análisis Bayesianos y ajustar priors según el contexto territorial.
    
    Attributes:
        municipality_code: Código DANE del municipio
        municipality_name: Nombre oficial del municipio
        department: Departamento al que pertenece
        population: Población estimada
        fiscal_context: Categoría de capacidad fiscal
        pdet_municipality: Si es municipio PDET (Programa de Desarrollo con Enfoque Territorial)
        conflict_affected: Si ha sido afectado por conflicto armado
        rural_share: Proporción de población rural (0.0 a 1.0)
        poverty_index: Índice de pobreza multidimensional (0.0 a 1.0)
    """
    
    municipality_code: str
    municipality_name: str
    department: str
    population: int
    fiscal_context: FiscalContext
    pdet_municipality: bool = False
    conflict_affected: bool = False
    rural_share: float = 0.5  # Default 50% rural
    poverty_index: float = 0.0  # Default no poverty data
    
    def complexity_score(self) -> float:
        """
        Calcula un score de complejidad basado en características municipales.
        
        La complejidad se determina por:
        - Tamaño de población (más población = más complejo)
        - Contexto PDET (PDET = más complejo)
        - Afectación por conflicto (conflicto = más complejo)
        - Ruralidad (más rural = más complejo)
        - Pobreza (más pobreza = más complejo)
        
        Returns:
            float: Score de complejidad entre 0.0 (simple) y 1.0 (muy complejo)
        """
        score = 0.0
        
        # Population complexity (normalized logarithmically)
        if self.population > 100000:
            score += 0.3
        elif self.population > 50000:
            score += 0.2
        elif self.population > 20000:
            score += 0.1
        
        # PDET adds complexity
        if self.pdet_municipality:
            score += 0.2
        
        # Conflict affected adds complexity
        if self.conflict_affected:
            score += 0.2
        
        # High rurality adds complexity
        if self.rural_share > 0.7:
            score += 0.2
        elif self.rural_share > 0.5:
            score += 0.1
        
        # Poverty adds complexity
        if self.poverty_index > 0.5:
            score += 0.2
        elif self.poverty_index > 0.3:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"UnitOfAnalysis(code={self.municipality_code}, "
            f"name={self.municipality_name}, "
            f"pop={self.population:,}, "
            f"fiscal={self.fiscal_context.name}, "
            f"complexity={self.complexity_score():.2f})"
        )
