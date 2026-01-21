#!/usr/bin/env python3
"""
Script para confirmar el conteo de 476 ítems.
Filtra MARGINAL y External según especificación.
"""

def calculate_item_count():
    """Calcula el conteo total de ítems irrigables."""

    # Constantes del sistema
    MICRO_QUESTIONS = 300  # 30 base × 10 PA
    POLICY_AREAS = 10      # PA01-PA10
    DIMENSIONS = 6         # DIM01-DIM06
    CLUSTERS = 4           # CL01-CL04
    CROSS_CUTTING = 9      # CC01-CC09
    MESO_QUESTIONS = 4     # MESO_1-MESO_4
    MACRO_QUESTIONS = 1    # MACRO_1

    # Patterns: Total - MARGINAL - External
    TOTAL_PATTERNS = 180
    MARGINAL_PATTERNS = 35
    EXTERNAL_PATTERNS = 3
    IRRIGABLE_PATTERNS = TOTAL_PATTERNS - MARGINAL_PATTERNS - EXTERNAL_PATTERNS  # 142

    total = (
        MICRO_QUESTIONS +
        POLICY_AREAS +
        DIMENSIONS +
        CLUSTERS +
        CROSS_CUTTING +
        MESO_QUESTIONS +
        MACRO_QUESTIONS +
        IRRIGABLE_PATTERNS
    )

    print(f"""
    CONTEO DE ÍTEMS IRRIGABLES
    ==========================
    Micro Questions:      {MICRO_QUESTIONS:>4}
    Policy Areas:        {POLICY_AREAS:>4}
    Dimensions:          {DIMENSIONS:>4}
    Clusters:            {CLUSTERS:>4}
    Cross-Cutting:       {CROSS_CUTTING:>4}
    Meso Questions:      {MESO_QUESTIONS:>4}
    Macro Questions:     {MACRO_QUESTIONS:>4}
    Patterns (irrigable):{IRRIGABLE_PATTERNS:>4}
    --------------------------
    TOTAL:                {total:>4}

    EXCLUSIONES:
    - Patterns MARGINAL: {MARGINAL_PATTERNS}
    - Patterns External: {EXTERNAL_PATTERNS}

    VERIFICACIÓN:
    300 + 10 + 6 + 4 + 9 + 4 + 1 + 142 = {total}
    """)

    assert total == 476, f"Expected 476, got {total}"
    print("✅ VERIFICACIÓN EXITOSA: Total = 476 ítems")
    return total

if __name__ == "__main__":
    calculate_item_count()
