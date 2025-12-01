# FARFAN CALIBRATION SYSTEM - CANONICAL STRUCTURE
# ================================================

## UBICACIÓN ÚNICA DE TODOS LOS ARTEFACTOS

```
system/
├── config/
│   ├── calibration/
│   │   └── intrinsic_calibration.json          # Capa Base (@b) - POR GENERAR
│   └── questionnaire/
│       └── questionnaire_monolith.json         # Capas Contextuales (@q, @d, @p)
└── artifacts/
    └── inventory/
        ├── method_inventory_verified.json      # 1270 métodos escaneados
        ├── method_inventory_scanner.py         # Scanner AST completo
        ├── validation_report.txt               # Reporte de verificación
        ├── scan1.hash                          # Checksum run 1
        └── scan2.hash                          # Checksum run 2
```

## ARCHIVOS GENERADOS

### ✅ Completados
- `method_inventory_verified.json` - 1.7MB, 1270 métodos con AST hashing
- `questionnaire_monolith.json` - 2.4MB, 300+ preguntas con method_sets
- `method_inventory_scanner.py` - Scanner production-grade
- `validation_report.txt` - Verificación completa

### 🔄 Por Generar
- `intrinsic_calibration.json` - Capa Base (@b) para 1270 métodos

## SIGUIENTE PASO

Generar `system/config/calibration/intrinsic_calibration.json` con:
- 1270 entradas (una por método)
- Estructura: `{"ClassName.method_name": {"b_theory": 0.5, "b_impl": 0.5, "b_deploy": 0.5}}`
- Valores conservadores iniciales (0.5)

## COMANDOS DE VERIFICACIÓN

```bash
# Ver estructura
tree system/

# Verificar archivos
ls -lh system/config/calibration/
ls -lh system/config/questionnaire/
ls -lh system/artifacts/inventory/

# Validar JSON
python3 -m json.tool system/config/questionnaire/questionnaire_monolith.json > /dev/null && echo "✅ Monolith válido"
python3 -m json.tool system/artifacts/inventory/method_inventory_verified.json > /dev/null && echo "✅ Inventory válido"
```

## PROHIBICIONES

❌ NO crear archivos fuera de `system/`
❌ NO duplicar archivos en múltiples ubicaciones
❌ NO usar rutas relativas ambiguas
✅ SIEMPRE usar rutas absolutas desde repo root
✅ SIEMPRE mantener estructura canónica
