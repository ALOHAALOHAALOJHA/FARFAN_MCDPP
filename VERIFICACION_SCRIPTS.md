# VERIFICACIÓN DE SCRIPTS E IMPORTS

## ESTADO ACTUAL

### ✅ SCRIPTS CORRECTOS (mayoría)
```bash
scripts/pipeline/run_complete_analysis_plan1.py
scripts/pipeline/run_policy_pipeline_verified.py
scripts/recommendation_cli.py
scripts/operations/build_monolith.py
scripts/dev/test_calibration_empirically.py
... y muchos más
```

Todos usan: `from farfan_pipeline.xxx import yyy` ✓

---

### ❌ TESTS CON IMPORTS INCORRECTOS (4 archivos)

**tests/core/test_spc_adapter.py**
```python
# INCORRECTO:
from farfan_pipeline.farfan_pipeline.utils.cpp_adapter import CPPAdapter

# DEBE SER:
from farfan_pipeline.utils.cpp_adapter import CPPAdapter
```

**tests/core/test_spc_adapter_integration.py**
```python
# INCORRECTO:
from farfan_pipeline.farfan_pipeline.utils.cpp_adapter import CPPAdapter
from farfan_pipeline.farfan_pipeline.core.phases.phase1_models import Chunk
from farfan_pipeline.farfan_pipeline.core.orchestrator.core import PreprocessedDocument

# DEBE SER:
from farfan_pipeline.utils.cpp_adapter import CPPAdapter
from farfan_pipeline.core.phases.phase1_models import Chunk
from farfan_pipeline.core.orchestrator.core import PreprocessedDocument
```

---

## ¿POR QUÉ PASÓ ESTO?

Estos tests tenían la vieja estructura duplicada:
```
farfan_core/farfan_core/...
```

Mi script de refactorización reemplazó `farfan_core` → `farfan_pipeline` en TODA la cadena:
```
farfan_core.farfan_core → farfan_pipeline.farfan_pipeline  ❌
```

Debería haber quedado:
```
farfan_core.farfan_core → farfan_pipeline  ✓
```

---

## VERIFICACIÓN DE FUNCIONAMIENTO

### Scripts funcionan correctamente:
```bash
$ python3 -c "import farfan_pipeline"
✓ Import exitoso desde src/farfan_pipeline/
```

### Tests con doble path fallarán:
```bash
$ python3 -c "from farfan_pipeline.farfan_pipeline.utils import cpp_adapter"
ModuleNotFoundError: No module named 'farfan_pipeline.farfan_pipeline'
```

---

## SOLUCIÓN

Corregir 3 archivos de tests:
1. tests/core/test_spc_adapter.py
2. tests/core/test_spc_adapter_integration.py  
3. tests/core/test_method_inventory_ast.py (verificar)

Reemplazar:
`farfan_pipeline.farfan_pipeline` → `farfan_pipeline`

