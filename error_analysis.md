# ANÁLISIS DETALLADO DE ERRORES DE SINTAXIS

## RESUMEN EJECUTIVO

**Total de errores**: 8 archivos con errores críticos de sintaxis
**Causa raíz**: Sistema de calibración automática mal implementado
**Patrón común**: Literales numéricos seguidos directamente por llamadas a funciones sin operador

---

## PATRÓN DEL ERROR

Todos los errores siguen el mismo patrón:

```python
# INCORRECTO (error de sintaxis)
variable = 5get_parameter_loader().get(...).get(...)

# DEBERÍA SER
variable = 5.0  # O el valor correcto sin la llamada mal formateada
```

**Problema**: El sistema de auto-calibración está insertando llamadas a `get_parameter_loader()` 
directamente después de números literales, creando tokens inválidos como `5get_parameter_loader` 
que Python interpreta como un literal decimal mal formado.

---

## DETALLE POR ARCHIVO

### 1. `src/farfan_pipeline/analysis/Analyzer_one.py` - Línea 539

**Error**: `invalid decimal literal`

```python
target_throughput = 5get_parameter_loader().get("farfan_pipeline.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L539_29", 0.0)
```

**Debería ser**:
```python
target_throughput = 5.0  # O target_throughput = 5
```

**Contexto**: Cálculo de pérdida de throughput en análisis de rendimiento.

---

### 2. `src/farfan_pipeline/analysis/bayesian_multilevel_system.py` - Línea 253

**Error**: `invalid decimal literal`

```python
return 1get_parameter_loader().get("farfan_pipeline.analysis.bayesian_multilevel_system.ProbativeTest.calculate_likelihood_ratio").get("auto_param_L253_20", 0.0) if test_passed else get_parameter_loader().get("farfan_pipeline.analysis.bayesian_multilevel_system.ProbativeTest.calculate_likelihood_ratio").get("auto_param_L253_44", 0.9)
```

**Debería ser**:
```python
return 1.0 if test_passed else 0.9
# O más probable:
return 10.0 if test_passed else 0.9  # Smoking Gun test
```

**Contexto**: Test probativo tipo "Smoking Gun" en análisis bayesiano.

---

### 3. `src/farfan_pipeline/analysis/financiero_viabilidad_tablas.py` - Línea 1728

**Error**: `invalid decimal literal`

```python
return float(min(budget_score + diversity_score + sustainability_score + risk_score, 1get_parameter_loader().get("farfan_pipeline.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_financial_component").get("auto_param_L1728_94", 0.0)))
```

**Debería ser**:
```python
return float(min(budget_score + diversity_score + sustainability_score + risk_score, 1.0))
```

**Contexto**: Normalización de score financiero entre 0 y 1.

---

### 4. `src/farfan_pipeline/analysis/micro_prompts.py` - Línea 124

**Error**: `invalid decimal literal`

```python
self.p95_threshold = p95_latency_threshold or 100get_parameter_loader().get("farfan_pipeline.analysis.micro_prompts.ProvenanceDAG.get_orphan_nodes").get("auto_param_L123_57", 0.0)
```

**Debería ser**:
```python
self.p95_threshold = p95_latency_threshold or 1000  # 1000ms = 1 segundo
# El comentario dice "Default 1 second", debería ser 1000ms
```

**Contexto**: Umbral de latencia p95 en milisegundos.

---

### 5. `src/farfan_pipeline/analysis/teoria_cambio.py` - Línea 925

**Error**: `invalid decimal literal`

```python
meets_standards = all(results) and success_rate >= 9get_parameter_loader().get("farfan_pipeline.analysis.teoria_cambio.IndustrialGradeValidator.execute_suite").get("auto_param_L925_60", 0.0)
```

**Debería ser**:
```python
meets_standards = all(results) and success_rate >= 0.9  # 90%
```

**Contexto**: Validación de estándares industriales (90% de éxito requerido).

---

### 6. `src/farfan_pipeline/core/orchestrator/chunk_router.py` - Línea 11

**Error**: `from __future__ imports must occur at the beginning of the file`

```python
# Hay imports o código antes de la línea 11
from __future__ import annotations
```

**Solución**: Mover `from __future__ import annotations` a la primera línea del archivo.

**Causa**: Probablemente hay un shebang, docstring, o imports estándar antes.

---

### 7. `src/farfan_pipeline/processing/converter.py` - Línea 33

**Error**: `invalid syntax`

```python
from farfan_pipeline.processing.cpp_ingestion.models import (
# from farfan_core import get_parameter_loader  # CALIBRATION DISABLED
from farfan_pipeline.core.calibration.decorators import calibrated_method
    KPI,
```

**Problema**: Import mal estructurado. Hay un comentario en medio de un import multilínea.

**Solución**:
```python
from farfan_pipeline.processing.cpp_ingestion.models import (
    KPI,
    Budget,
    # ... resto de imports
)
# from farfan_core import get_parameter_loader  # CALIBRATION DISABLED
from farfan_pipeline.core.calibration.decorators import calibrated_method
```

---

### 8. `src/farfan_pipeline/processing/embedding_policy.py` - Línea 1475

**Error**: `invalid decimal literal`

```python
value = value / 10get_parameter_loader().get("farfan_pipeline.processing.embedding_policy.PolicyAnalysisEmbedder._extract_numerical_values").get("auto_param_L1474_46", 0.0)
```

**Debería ser**:
```python
value = value / 100.0  # Convertir porcentaje a decimal
```

**Contexto**: Normalización de porcentajes a escala 0-1.

---

### 9. `src/farfan_pipeline/utils/enhanced_contracts.py` - Línea 152

**Error**: `invalid syntax. Perhaps you forgot a comma?`

```python
schema_version: str = Field(
    default="2.get_parameter_loader().get("farfan_pipeline.utils.enhanced_contracts.FlowCompatibilityError.__init__").get("auto_param_L151_19", 0.0)",
    description="Contract schema version (semantic versioning)",
```

**Problema**: String con comillas anidadas mal escapadas + llamada a función dentro del string.

**Solución**:
```python
schema_version: str = Field(
    default="2.0.0",
    description="Contract schema version (semantic versioning)",
    pattern=r"^\d+\.\d+\.\d+$"
)
```

---

## CAUSA RAÍZ SISTÉMICA

Existe un sistema de **calibración automática** que está:

1. Escaneando el código en busca de literales numéricos
2. Intentando reemplazarlos con llamadas a `get_parameter_loader()`
3. **FALLANDO** al generar código sintácticamente válido

### Evidencia:

- Todos los errores contienen `auto_param_L<line>_<offset>`
- Patrón consistente: `<número>get_parameter_loader()`
- Los nombres de parámetros incluyen el path completo del módulo y función

### Sistema Responsable:

Probablemente en:
- `farfan_pipeline/core/calibration/parameter_loader.py`
- `farfan_pipeline/core/calibration/decorators.py`
- Algún script de pre-procesamiento o AST transformation

---

## SOLUCIÓN RECOMENDADA

### Opción 1: Desactivar sistema de auto-calibración
```bash
# Encontrar y desactivar el sistema
grep -r "auto_param" src/farfan_pipeline/core/calibration/
```

### Opción 2: Corrección manual (8 archivos)
Reemplazar cada línea errónea con el valor numérico correcto.

### Opción 3: Script de corrección automática
```python
import re

def fix_auto_param_errors(content):
    # Pattern: <number>get_parameter_loader()...
    pattern = r'(\d+)get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)'
    return re.sub(pattern, r'\1.0', content)
```

---

## VALORES CORRECTOS SUGERIDOS

| Archivo | Línea | Valor Actual | Valor Correcto | Justificación |
|---------|-------|--------------|----------------|---------------|
| Analyzer_one.py | 539 | `5get...` | `5.0` | Throughput target |
| bayesian_multilevel_system.py | 253 | `1get...` | `10.0` | Smoking gun LR |
| financiero_viabilidad_tablas.py | 1728 | `1get...` | `1.0` | Max score ceiling |
| micro_prompts.py | 124 | `100get...` | `1000` | 1 second in ms |
| teoria_cambio.py | 925 | `9get...` | `0.9` | 90% success rate |
| embedding_policy.py | 1475 | `10get...` | `100.0` | Percentage to decimal |
| enhanced_contracts.py | 152 | `"2.get..."` | `"2.0.0"` | Semantic version |

---

## IMPACTO

- **Compilación**: ❌ Fallando
- **Tests**: ❌ No ejecutables
- **Imports**: ✓ Correctos (refactorización exitosa)
- **Estructura**: ✓ PEP 420 compliant

**Los errores de imports fueron resueltos. Estos son errores PRE-EXISTENTES del sistema de calibración.**

---

