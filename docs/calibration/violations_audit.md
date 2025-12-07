# Hardcoding Audit Report (SIN_CARRETA compliance)

Found 76 potential violations.

**File:** `src/farfan_pipeline/contracts/tools/sort_sanity.py`
**Line:** 11
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": 1, "score": 0.5, "content_hash": "z"},
```
---
**File:** `src/farfan_pipeline/contracts/tools/sort_sanity.py`
**Line:** 12
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": 2, "score": 0.5, "content_hash": "a"},
```
---
**File:** `src/farfan_pipeline/contracts/tools/sort_sanity.py`
**Line:** 13
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": 3, "score": 0.8, "content_hash": "m"}
```
---
**File:** `src/farfan_pipeline/contracts/tools/rcc_report.py`
**Line:** 21
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
print(f"Threshold: {result['threshold']:.4f}")
```
---
**File:** `src/farfan_pipeline/contracts/tests/test_toc.py`
**Line:** 13
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"score": 10, "content_hash": "b"},
```
---
**File:** `src/farfan_pipeline/contracts/tests/test_toc.py`
**Line:** 14
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"score": 10, "content_hash": "a"},
```
---
**File:** `src/farfan_pipeline/contracts/tests/test_toc.py`
**Line:** 15
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"score": 5, "content_hash": "c"}
```
---
**File:** `src/farfan_pipeline/contracts/tests/test_toc.py`
**Line:** 28
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"score": 10, "content_hash": "b"},
```
---
**File:** `src/farfan_pipeline/contracts/tests/test_toc.py`
**Line:** 29
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"score": 10, "content_hash": "a"}
```
---
**File:** `src/farfan_pipeline/utils/metadata_loader.py`
**Line:** 12
**Issue:** YAML reference found
**Code:**
```python
import yaml
```
---
**File:** `src/farfan_pipeline/utils/metadata_loader.py`
**Line:** 184
**Issue:** YAML reference found
**Code:**
```python
elif path.suffix in ['.yaml', '.yml']:
```
---
**File:** `src/farfan_pipeline/utils/metadata_loader.py`
**Line:** 271
**Issue:** YAML reference found
**Code:**
```python
Load and validate execution_mapping.yaml
```
---
**File:** `src/farfan_pipeline/utils/metadata_loader.py`
**Line:** 274
**Issue:** YAML reference found
**Code:**
```python
path: Path to execution mapping (default: execution_mapping.yaml)
```
---
**File:** `src/farfan_pipeline/utils/metadata_loader.py`
**Line:** 281
**Issue:** YAML reference found
**Code:**
```python
path = proj_root() / "execution_mapping.yaml"
```
---
**File:** `src/farfan_pipeline/utils/paths.py`
**Line:** 310
**Issue:** YAML reference found
**Code:**
```python
>>> resources("farfan_core.core", "config", "default.yaml")
```
---
**File:** `src/farfan_pipeline/utils/paths.py`
**Line:** 311
**Issue:** YAML reference found
**Code:**
```python
Path('/path/to/farfan_core/core/config/default.yaml')
```
---
**File:** `src/farfan_pipeline/utils/coverage_gate.py`
**Line:** 207
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
print(f"Threshold:               {results['totals']['threshold']:4}")
```
---
**File:** `src/farfan_pipeline/utils/coverage_gate.py`
**Line:** 224
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
print(f"Required: {results['totals']['threshold']} methods")
```
---
**File:** `src/farfan_pipeline/utils/coverage_gate.py`
**Line:** 226
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
print(f"Gap:      {results['totals']['threshold'] - results['totals']['file_total_methods']} methods")
```
---
**File:** `src/farfan_pipeline/core/method_inventory.py`
**Line:** 215
**Issue:** YAML reference found
**Code:**
```python
if node.value.endswith((".yml", ".yaml")):
```
---
**File:** `src/farfan_pipeline/core/analysis_port.py`
**Line:** 38
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'CL01': {'score': 75.0, 'variance': 0.15, 'weak_pa': 'PA02'},
```
---
**File:** `src/farfan_pipeline/core/analysis_port.py`
**Line:** 39
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'CL02': {'score': 62.0, 'variance': 0.22, 'weak_pa': 'PA05'},
```
---
**File:** `src/farfan_pipeline/core/orchestrator/resource_alerts.py`
**Line:** 173
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
metadata={"threshold": self.thresholds.memory_critical_percent},
```
---
**File:** `src/farfan_pipeline/core/orchestrator/resource_alerts.py`
**Line:** 184
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
metadata={"threshold": self.thresholds.memory_warning_percent},
```
---
**File:** `src/farfan_pipeline/core/orchestrator/resource_alerts.py`
**Line:** 199
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
metadata={"threshold": self.thresholds.cpu_critical_percent},
```
---
**File:** `src/farfan_pipeline/core/orchestrator/resource_alerts.py`
**Line:** 209
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
metadata={"threshold": self.thresholds.cpu_warning_percent},
```
---
**File:** `src/farfan_pipeline/core/orchestrator/executors.py`
**Line:** 2139
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
observations={"coherence": (performance_analysis or {}).get("resource_fit", {}).get("score", 0.0)}
```
---
**File:** `src/farfan_pipeline/core/orchestrator/executors.py`
**Line:** 2967
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
(dnp_compliance or {}).get("score", 0)) / 2
```
---
**File:** `src/farfan_pipeline/core/orchestrator/executors_snapshot/executors.py`
**Line:** 1849
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
observations={"coherence": performance_analysis.get("resource_fit", {}).get("score", 0.0)}
```
---
**File:** `src/farfan_pipeline/core/calibration/congruence_layer.py`
**Line:** 60
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("congruence_single_method", extra={"score": 1.0, "method_id": method_id})
```
---
**File:** `src/farfan_pipeline/core/calibration/congruence_layer.py`
**Line:** 63
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.warning("congruence_single_method_missing", extra={"score": 0.0, "method_id": method_id})
```
---
**File:** `src/farfan_pipeline/core/calibration/congruence_layer.py`
**Line:** 77
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("c_scale_computed", extra={"score": c_scale})
```
---
**File:** `src/farfan_pipeline/core/calibration/congruence_layer.py`
**Line:** 81
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("c_sem_computed", extra={"score": c_sem})
```
---
**File:** `src/farfan_pipeline/core/calibration/congruence_layer.py`
**Line:** 87
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("c_fusion_computed", extra={"score": c_fusion})
```
---
**File:** `src/farfan_pipeline/core/calibration/meta_layer.py`
**Line:** 79
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("m_transp_computed", extra={"score": m_transp})
```
---
**File:** `src/farfan_pipeline/core/calibration/meta_layer.py`
**Line:** 85
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("m_gov_computed", extra={"score": m_gov})
```
---
**File:** `src/farfan_pipeline/core/calibration/meta_layer.py`
**Line:** 89
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.debug("m_cost_computed", extra={"score": m_cost})
```
---
**File:** `src/farfan_pipeline/core/calibration/unit_layer.py`
**Line:** 46
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
metadata={"gate": "structural", "threshold": self.config.min_structural_compliance}
```
---
**File:** `src/farfan_pipeline/core/calibration/layer_influence_model.py`
**Line:** 160
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
conditions={'threshold': 3}
```
---
**File:** `src/farfan_pipeline/core/calibration/chain_layer.py`
**Line:** 114
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
logger.info("chain_valid", extra={"method": method_id, "score": 1.0})
```
---
**File:** `src/farfan_pipeline/analysis/recommendation_engine.py`
**Line:** 399
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'CL01': {'score': 75.0, 'variance': ParameterLoaderV2.get("farfan_core.analysis.recommendation_engine.RecommendationEngine.get_thresholds_from_monolith", "auto_param_L398_56", 0.15), 'weak_pa': 'PA02'},
```
---
**File:** `src/farfan_pipeline/analysis/recommendation_engine.py`
**Line:** 400
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'CL02': {'score': 62.0, 'variance': ParameterLoaderV2.get("farfan_core.analysis.recommendation_engine.RecommendationEngine.get_thresholds_from_monolith", "auto_param_L399_56", 0.22), 'weak_pa': 'PA05'},
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 47
**Issue:** YAML reference found
**Code:**
```python
import yaml
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 84
**Issue:** YAML reference found
**Code:**
```python
DEFAULT_CONFIG_FILE = "config.yaml"
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 4849
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'semantic': evidence_dict.get('semantic', {}).get('score', 0.0),
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 4850
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'temporal': evidence_dict.get('temporal', {}).get('score', 0.0),
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 4851
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'financial': evidence_dict.get('financial', {}).get('score', 0.0),
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 4852
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'structural': evidence_dict.get('structural', {}).get('score', 0.0)
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 4970
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
domain: evidence_dict.get(domain, {'score': 0.0})
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 5175
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
validation_samples[i]['evidence'].get(d, {}).get('score', 0)
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 5179
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
validation_samples[i + 1]['evidence'].get(d, {}).get('score', 0)
```
---
**File:** `src/farfan_pipeline/analysis/derek_beach.py`
**Line:** 6269
**Issue:** YAML reference found
**Code:**
```python
El framework busca config.yaml en el directorio actual.
```
---
**File:** `src/farfan_pipeline/analysis/Analyzer_one.py`
**Line:** 981
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
print(f"  - {rec['description']} (Priority: {rec['priority']})")
```
---
**File:** `src/farfan_pipeline/analysis/Analyzer_one.py`
**Line:** 1692
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
lines.append(f"{i}. {rec.get('description', '')} (Priority: {rec.get('priority', '')})\n")
```
---
**File:** `src/farfan_pipeline/analysis/report_assembly.py`
**Line:** 255
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
details={'score': v, 'min': min_score, 'max': max_score},
```
---
**File:** `src/farfan_pipeline/flux/phases.py`
**Line:** 1139
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
phase_latency_histogram.record(duration_ms, {"phase": "score"})
```
---
**File:** `src/farfan_pipeline/flux/phases.py`
**Line:** 1140
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
phase_counter.add(1, {"phase": "score"})
```
---
**File:** `src/farfan_pipeline/api/dashboard_data_service.py`
**Line:** 371
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
questions_raw.append({'question_id': key, 'score': value})
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 45
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "arauca", "name": "Arauca", "score": 85, "x": 15, "y": 20, "municipalities": 7},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 46
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "catatumbo", "name": "Catatumbo", "score": 72, "x": 25, "y": 15, "municipalities": 8},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 47
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "montes_maria", "name": "Montes de María", "score": 91, "x": 35, "y": 10, "municipalities": 15},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 48
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "pacifico_medio", "name": "Pacífico Medio", "score": 64, "x": 10, "y": 40, "municipalities": 4},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 49
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "putumayo", "name": "Putumayo", "score": 78, "x": 20, "y": 80, "municipalities": 9},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 50
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "sierra_nevada", "name": "Sierra Nevada", "score": 88, "x": 40, "y": 5, "municipalities": 8},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 51
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "uraba", "name": "Urabá Antioqueño", "score": 69, "x": 20, "y": 25, "municipalities": 8},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 52
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "choco", "name": "Chocó", "score": 55, "x": 8, "y": 30, "municipalities": 12},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 53
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "macarena", "name": "Macarena - Guaviare", "score": 82, "x": 45, "y": 50, "municipalities": 12},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 54
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "pacifico_nariñense", "name": "Pacífico Nariñense", "score": 60, "x": 5, "y": 70, "municipalities": 11},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 55
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "cuenca_caguan", "name": "Cuenca del Caguán", "score": 75, "x": 30, "y": 60, "municipalities": 6},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 56
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "sur_tolima", "name": "Sur del Tolima", "score": 89, "x": 25, "y": 45, "municipalities": 4},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 57
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "sur_bolivar", "name": "Sur de Bolívar", "score": 67, "x": 30, "y": 20, "municipalities": 7},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 58
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "bajo_cauca", "name": "Bajo Cauca", "score": 71, "x": 28, "y": 22, "municipalities": 13},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 59
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "sur_cordoba", "name": "Sur de Córdoba", "score": 63, "x": 22, "y": 18, "municipalities": 5},
```
---
**File:** `src/farfan_pipeline/api/dashboard_server.py`
**Line:** 60
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
{"id": "alto_patia", "name": "Alto Patía", "score": 80, "x": 15, "y": 65, "municipalities": 24}
```
---
**File:** `src/farfan_pipeline/api/api_server.py`
**Line:** 646
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
'score': summary.get('scores', {}).get('overall'),
```
---
**File:** `src/farfan_pipeline/api/api_server.py`
**Line:** 1299
**Issue:** Potential hardcoded calibration data in dict literal
**Code:**
```python
"CL01": {"score": 72.0, "variance": ParameterLoaderV2.get("farfan_core.api.api_server.DataService.get_evidence_stream", "auto_param_L865_52", 0.25), "weak_pa": "PA02"},
```
---
