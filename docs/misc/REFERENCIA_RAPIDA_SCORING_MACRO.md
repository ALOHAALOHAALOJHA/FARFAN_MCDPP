# Referencia Rápida: Procedimientos Matemáticos de Scoring Macro

## 🎯 Guía Rápida para Desarrolladores

### 1. Weighted Average

```python
# Fórmula
score = Σ(score_i * weight_i)

# Requisitos
- Σ(weights) = 1.0 ± 1e-6
- len(weights) == len(scores)
- All scores ∈ [0, 3]

# Ubicación
aggregation.py:869-917
```

**Uso Típico:**
```python
scores = [2.5, 2.8, 2.3]
weights = [0.4, 0.3, 0.3]  # Suma = 1.0
result = calculate_weighted_average(scores, weights)
# result ≈ 2.54
```

---

### 2. Choquet Integral

```python
# Fórmula
Cal(I) = Σ(a_l·x_l) + Σ(a_lk·min(x_l,x_k))

# Requisitos
- All layer_scores ∈ [0, 1]
- Σ(a_lk) ≤ min(Σ(a_l), 1.0) * 0.5
- Cal(I) ∈ [0, 1]

# Ubicación
choquet_aggregator.py:354-437
```

**Uso Típico:**
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.2},
    interaction_weights={("@b", "@chain"): 0.1}
)
aggregator = ChoquetAggregator(config)
result = aggregator.aggregate(
    subject="method_X",
    layer_scores={"@b": 0.8, "@chain": 0.7, "@q": 0.9}
)
# result.calibration_score ∈ [0, 1]
```

---

### 3. Coherence

```python
# Fórmula
coherence = 1 - (std_dev / max_std)

# Donde
std_dev = √(Σ((x_i - mean)²) / n)
max_std = 3.0  # Para rango [0,3]

# Requisitos
- scores ∈ [0, 3]
- coherence ∈ [0, 1]

# Ubicación
aggregation.py:1866-1902
```

**Interpretación:**
- `coherence = 1.0`: Perfecta consistencia (todos los scores iguales)
- `coherence = 0.5`: Consistencia moderada
- `coherence = 0.0`: Máxima variación

---

### 4. Penalty Factor

```python
# Fórmula
penalty_factor = 1 - (normalized_std * PENALTY_WEIGHT)
adjusted_score = weighted_score * penalty_factor

# Donde
normalized_std = min(std_dev / MAX_SCORE, 1.0)
PENALTY_WEIGHT = 0.3  # 30% máximo de penalización

# Requisitos
- PENALTY_WEIGHT ∈ [0, 1]
- penalty_factor ∈ [0, 1]

# Ubicación
aggregation.py:1689-1691
```

**Ejemplo:**
```python
# Alta varianza → mayor penalización
std_dev = 1.2
MAX_SCORE = 3.0
normalized_std = min(1.2/3.0, 1.0) = 0.4
penalty_factor = 1 - (0.4 * 0.3) = 0.88  # 12% penalización
```

---

### 5. Threshold Application

```python
# Normalización
normalized_score = clamped_score / 3.0  # → [0, 1]

# Umbrales
if normalized_score >= 0.85:    quality = "EXCELENTE"
elif normalized_score >= 0.70:  quality = "BUENO"
elif normalized_score >= 0.55:  quality = "ACEPTABLE"
else:                           quality = "INSUFICIENTE"

# Ubicación
aggregation.py:975-1022 (Dimension)
aggregation.py:1492-1539 (Area)
aggregation.py:2263-2310 (Macro)
```

**Conversión de Scores:**
```python
score = 2.4  # [0, 3]
normalized = 2.4 / 3.0 = 0.80
quality = "BUENO"  # 0.70 <= 0.80 < 0.85
```

---

### 6. Weight Normalization

```python
# Fórmula
normalized_weights = {k: w/total for k, w in weights.items()}

# Donde
total = Σ(positive_weights)  # Solo pesos ≥ 0

# Fallbacks
- Si all weights < 0: equal weights
- Si total == 0: equal weights

# Ubicación
aggregation.py:310-322
```

**Ejemplo:**
```python
raw_weights = {"A": 0.8, "B": 0.5, "C": 0.3}
total = 0.8 + 0.5 + 0.3 = 1.6
normalized = {
    "A": 0.8/1.6 = 0.5,
    "B": 0.5/1.6 = 0.3125,
    "C": 0.3/1.6 = 0.1875
}
# Σ(normalized) = 1.0 ✓
```

---

### 7. Score Normalization

```python
# Fórmula
normalized = max(0.0, min(max_expected, score)) / max_expected

# Donde
max_expected = validation_details.get('score_max', 3.0)

# Ubicación
aggregation.py:1473-1490
```

**Ejemplo:**
```python
score = 2.7
max_expected = 3.0
clamped = max(0.0, min(3.0, 2.7)) = 2.7
normalized = 2.7 / 3.0 = 0.9
```

---

## 🔍 Checklist de Validación

### Antes de Modificar Código de Scoring

- [ ] ¿La modificación afecta alguna fórmula matemática?
- [ ] ¿Se mantiene la normalización de pesos (Σ = 1.0)?
- [ ] ¿Se preserva el boundedness ([0,1] o [0,3] según contexto)?
- [ ] ¿Hay validaciones apropiadas para casos edge?
- [ ] ¿Se mantiene el logging para observabilidad?
- [ ] ¿Los tests unitarios cubren el cambio?

### Después de Modificar Código de Scoring

- [ ] Ejecutar auditoría: `python audit_mathematical_scoring_macro.py`
- [ ] Verificar 0 issues críticos
- [ ] Revisar reporte: `AUDIT_MATHEMATICAL_SCORING_MACRO.md`
- [ ] Ejecutar tests: `python test_mathematical_audit.py`
- [ ] Validar reproducibilidad con fixed seeds

---

## 📊 Rangos y Límites

| Concepto | Rango | Notas |
|----------|-------|-------|
| Micro score | [0, 3] | 6 modalidades de scoring |
| Normalized score | [0, 1] | Para thresholds |
| Weight | [0, 1] | Post-normalización |
| Coherence | [0, 1] | 1 = perfecta |
| Penalty factor | [0, 1] | 1 = sin penalización |
| Choquet Cal(I) | [0, 1] | Strictly bounded |
| PENALTY_WEIGHT | 0.3 | Configurable |
| Tolerance (weights) | 1e-6 | Float64 precision |

---

## 🚨 Errores Comunes a Evitar

### 1. División por Cero
```python
# ❌ MAL
avg = sum(scores) / len(scores)

# ✓ BIEN
if not scores:
    return 0.0
avg = sum(scores) / len(scores)
```

### 2. Pesos No Normalizados
```python
# ❌ MAL
weights = [0.4, 0.3, 0.5]  # Suma = 1.2

# ✓ BIEN
raw_weights = [0.4, 0.3, 0.5]
total = sum(raw_weights)
weights = [w/total for w in raw_weights]  # Suma = 1.0
```

### 3. Scores Fuera de Rango
```python
# ❌ MAL
normalized = score / 3.0  # Si score > 3, normalized > 1

# ✓ BIEN
clamped = max(0.0, min(3.0, score))
normalized = clamped / 3.0  # Garantiza [0, 1]
```

### 4. Choquet sin Validación
```python
# ❌ MAL
cal_i = linear_sum + interaction_sum  # Puede exceder 1.0

# ✓ BIEN
cal_i = linear_sum + interaction_sum
if cal_i < 0.0 or cal_i > 1.0:
    raise CalibrationConfigError(f"Boundedness violated: {cal_i}")
cal_i = max(0.0, min(1.0, cal_i))  # Clamping defensivo
```

---

## 🛠️ Comandos Útiles

### Ejecutar Auditoría
```bash
python audit_mathematical_scoring_macro.py
```

### Ejecutar Tests
```bash
python test_mathematical_audit.py
```

### Generar Reportes
```bash
# Auditoría genera automáticamente:
# - AUDIT_MATHEMATICAL_SCORING_MACRO.md
# - audit_mathematical_scoring_macro.json
```

### Verificar Ubicaciones
```bash
grep -n "def calculate_weighted_average" src/canonic_phases/Phase_four_five_six_seven/aggregation.py
grep -n "class ChoquetAggregator" src/canonic_phases/Phase_four_five_six_seven/choquet_aggregator.py
```

---

## 📚 Referencias Rápidas

### Documentación Completa
- `AUDIT_MATHEMATICAL_SCORING_MACRO.md`: Reporte detallado
- `RESUMEN_EJECUTIVO_AUDITORIA_MATEMATICA_MACRO.md`: Resumen ejecutivo
- `audit_mathematical_scoring_macro.py`: Código del auditor

### Código Fuente
- `aggregation.py`: Fases 4-7 (líneas 1-2423)
- `choquet_aggregator.py`: Choquet Integral (líneas 1-438)

### Tests
- `test_mathematical_audit.py`: Suite de tests del auditor

---

**Última actualización**: 11 de diciembre de 2025  
**Versión**: 1.0
