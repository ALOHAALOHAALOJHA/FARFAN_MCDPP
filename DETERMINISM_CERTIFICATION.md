# F.A.R.F.A.N Pipeline Determinism Certification Report

**Version:** 1.0.0
**Generated:** 2025-12-11T08:04:44.419667
**Overall Score:** 0.578
**Overall Status:** `NOT_CERTIFIED`

---

## Executive Summary

- **Total Phases:** 10
- **Certified Phases:** 2
- **Certified With Notes Phases:** 7
- **Not Certified Phases:** 1
- **Total Issues:** 219
- **Critical Issues:** 0
- **Overall Score:** 0.578
- **Recommendation:** Pipeline is NOT CERTIFIED. Critical determinism issues must be addressed before certification.

---

## Phase-by-Phase Analysis

### Phase 0: Validation & Bootstrap

**Phase ID:** `Phase_zero`  
**Status:** `NOT_CERTIFIED`  
**Determinism Score:** 0.060  
**Files Scanned:** 24  
**Total Lines:** 9673  

#### Issues by Severity

##### HIGH (6 issues)

- **src/canonic_phases/Phase_zero/deterministic_execution.py:113**
  - Type: `random_unseeded`
  - Code: `...     result = random.randint(0, 100)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/deterministic_execution.py:171**
  - Type: `random_unseeded`
  - Code: `...     return x + random.randint(0, 10)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism_helpers.py:84**
  - Type: `random_unseeded`
  - Code: `...     v1 = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism_helpers.py:85**
  - Type: `np_random_unseeded`
  - Code: `...     a1 = np.random.rand(3)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

- **src/canonic_phases/Phase_zero/determinism_helpers.py:87**
  - Type: `random_unseeded`
  - Code: `...     v2 = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism_helpers.py:88**
  - Type: `np_random_unseeded`
  - Code: `...     a2 = np.random.rand(3)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

##### LOW (17 issues)

- **src/canonic_phases/Phase_zero/bootstrap.py:101**
  - Type: `dict_keys_iteration`
  - Code: `accessed_keys=list(result.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/bootstrap.py:116**
  - Type: `dict_keys_iteration`
  - Code: `accessed_keys=list(result.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:288**
  - Type: `dict_keys_iteration`
  - Code: `"sources": list(self.stats_by_source.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:354**
  - Type: `dict_keys_iteration`
  - Code: `payload_keys = set(payload.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/paths.py:318**
  - Type: `set_iteration`
  - Code: `for part in path_parts:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/determinism.py:158**
  - Type: `set_iteration`
  - Code: `for component in OPTIONAL_SEEDS:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/determinism.py:193**
  - Type: `set_iteration`
  - Code: `for component in MANDATORY_SEEDS:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/main.py:1137**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/main.py:1164**
  - Type: `set_iteration`
  - Code: `for node in nodes:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/main.py:1169**
  - Type: `set_iteration`
  - Code: `for edge in edges:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 7 more)*

##### ACCEPTABLE (4 issues)

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:63**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:86**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:180**
  - Type: `uuid_generation`
  - Code: `default_factory=lambda: str(uuid.uuid4()),  # FALLBACK ONLY - provide explicitly!`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/coverage_gate.py:105**
  - Type: `datetime_now`
  - Code: `"timestamp": datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

---

### Phase 1: Document Ingestion

**Phase ID:** `Phase_one`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.280  
**Files Scanned:** 10  
**Total Lines:** 5840  

#### Issues by Severity

##### LOW (36 issues)

- **src/canonic_phases/Phase_one/signal_enrichment.py:340**
  - Type: `set_iteration`
  - Code: `for marker in markers:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/signal_enrichment.py:493**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/signal_enrichment.py:554**
  - Type: `dict_keys_iteration`
  - Code: `'signal_packs_loaded': list(self.context.signal_packs.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_one/signal_enrichment.py:555**
  - Type: `dict_keys_iteration`
  - Code: `'quality_metrics_available': list(self.context.quality_metrics.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_one/structural.py:88**
  - Type: `set_iteration`
  - Code: `for keyword in keywords_list:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:968**
  - Type: `set_iteration`
  - Code: `for page in doc:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:1084**
  - Type: `set_iteration`
  - Code: `for section in sections:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:1132**
  - Type: `set_iteration`
  - Code: `for pattern in patterns:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:1135**
  - Type: `set_iteration`
  - Code: `for match in matches:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:1417**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 26 more)*

---

### Phase 2: Micro Analysis (300 Executors)

**Phase ID:** `Phase_two`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.120  
**Files Scanned:** 20  
**Total Lines:** 18384  

#### Issues by Severity

##### LOW (44 issues)

- **src/canonic_phases/Phase_two/evidence_nexus.py:632**
  - Type: `set_iteration`
  - Code: `for node_id in sorted_nodes:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:643**
  - Type: `set_iteration`
  - Code: `for edge in incoming:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:792**
  - Type: `set_iteration`
  - Code: `for elem in expected_elements:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1113**
  - Type: `set_iteration`
  - Code: `for type_str in required_types:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1835**
  - Type: `set_iteration`
  - Code: `for source in sources:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1892**
  - Type: `set_iteration`
  - Code: `for v in values:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1964**
  - Type: `set_iteration`
  - Code: `for node in nodes:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/batch_executor.py:515**
  - Type: `set_iteration`
  - Code: `>>> async for batch_result in batches:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/phase6_validation.py:214**
  - Type: `dict_keys_iteration`
  - Code: `question_keys = set(question_schema.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_two/phase6_validation.py:215**
  - Type: `dict_keys_iteration`
  - Code: `chunk_keys = set(chunk_schema.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

  *(... and 34 more)*

##### ACCEPTABLE (10 issues)

- **src/canonic_phases/Phase_two/evidence_nexus.py:207**
  - Type: `time_time`
  - Code: `extraction_timestamp=time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/evidence_nexus.py:341**
  - Type: `time_time`
  - Code: `validation_timestamp=time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/evidence_nexus.py:1066**
  - Type: `time_time`
  - Code: `synthesis_timestamp=time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1187**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1199**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1248**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1299**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1435**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1468**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:1605**
  - Type: `time_time`
  - Code: `"timestamp": time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

---

### Phase 3: Scoring

**Phase ID:** `Phase_three`  
**Status:** `CERTIFIED`  
**Determinism Score:** 1.000  
**Files Scanned:** 2  
**Total Lines:** 242  

✅ **No determinism issues found**

---

### Phases 4-7: Hierarchical Aggregation

**Phase ID:** `Phase_four_five_six_seven`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.940  
**Files Scanned:** 5  
**Total Lines:** 3778  

#### Issues by Severity

##### LOW (3 issues)

- **src/canonic_phases/Phase_four_five_six_seven/choquet_aggregator.py:386**
  - Type: `dict_keys_iteration`
  - Code: `missing_layers = set(self.config.linear_weights.keys()) - set(layer_scores.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/choquet_aggregator.py:390**
  - Type: `dict_keys_iteration`
  - Code: `f"Expected: {set(self.config.linear_weights.keys())}"`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:121**
  - Type: `dict_keys_iteration`
  - Code: `cluster_ids = list(cluster_policy_areas.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

---

### Phase 8: Recommendations

**Phase ID:** `Phase_eight`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.980  
**Files Scanned:** 3  
**Total Lines:** 1438  

#### Issues by Severity

##### LOW (1 issues)

- **src/canonic_phases/Phase_eight/recommendation_engine.py:256**
  - Type: `set_iteration`
  - Code: `for question in micro_questions:`
  - Recommendation: Use sorted(set) if order matters

---

### Phase 9: Report Assembly

**Phase ID:** `Phase_nine`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.960  
**Files Scanned:** 2  
**Total Lines:** 1291  

#### Issues by Severity

##### LOW (2 issues)

- **src/canonic_phases/Phase_nine/report_assembly.py:814**
  - Type: `set_iteration`
  - Code: `for item in raw_clusters:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_nine/report_assembly.py:1175**
  - Type: `dict_keys_iteration`
  - Code: `print(f"   ✓ Structured dict: {list(e.to_dict().keys())}")`
  - Recommendation: Use sorted(dict.keys()) if order matters

##### ACCEPTABLE (4 issues)

- **src/canonic_phases/Phase_nine/report_assembly.py:76**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_nine/report_assembly.py:195**
  - Type: `uuid_generation`
  - Code: `default_factory=lambda: str(uuid.uuid4()),  # FALLBACK ONLY - provide explicitly!`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_nine/report_assembly.py:544**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_nine/report_assembly.py:696**
  - Type: `time_time`
  - Code: `latency_ms = (time.time() - start_time) * 1000`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

---

### Orchestration Layer

**Phase ID:** `orchestration`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.440  
**Files Scanned:** 34  
**Total Lines:** 13498  

#### Issues by Severity

##### HIGH (1 issues)

- **src/orchestration/memory_safety.py:212**
  - Type: `random_unseeded`
  - Code: `return random.sample(items, max_elements)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

##### LOW (23 issues)

- **src/orchestration/orchestrator.py:661**
  - Type: `dict_keys_iteration`
  - Code: `return list(self._registry._class_paths.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/orchestrator.py:664**
  - Type: `dict_keys_iteration`
  - Code: `return [self.get(name) for name in self.keys()]`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/orchestrator.py:667**
  - Type: `dict_keys_iteration`
  - Code: `return [(name, self.get(name)) for name in self.keys()]`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/method_registry.py:320**
  - Type: `dict_keys_iteration`
  - Code: `"instantiated_class_names": list(self._instance_cache.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/signature_runtime_validator.py:96**
  - Type: `set_iteration`
  - Code: `for required_input in required_inputs:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/signature_runtime_validator.py:108**
  - Type: `set_iteration`
  - Code: `for critical_input in critical_optional:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/method_source_validator.py:15**
  - Type: `set_iteration`
  - Code: `for file in files:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/method_source_validator.py:48**
  - Type: `set_iteration`
  - Code: `for executor_info in executor_data:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/method_source_validator.py:58**
  - Type: `set_iteration`
  - Code: `for method_fqn in declared_methods:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/precision_tracking.py:108**
  - Type: `dict_keys_iteration`
  - Code: `"context_fields": list(document_context.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

  *(... and 13 more)*

##### ACCEPTABLE (1 issues)

- **src/orchestration/orchestrator.py:1340**
  - Type: `time_time`
  - Code: `run_id=f"run_{document_id}_{int(time.time())}",`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

---

### Cross-Cutting Infrastructure

**Phase ID:** `cross_cutting_infrastrucuiture`  
**Status:** `CERTIFIED`  
**Determinism Score:** 1.000  
**Files Scanned:** 0  
**Total Lines:** 0  

✅ **No determinism issues found**

---

### Methods Dispensary

**Phase ID:** `methods_dispensary`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.000  
**Files Scanned:** 11  
**Total Lines:** 22412  

#### Issues by Severity

##### HIGH (2 issues)

- **src/methods_dispensary/derek_beach.py:5154**
  - Type: `random_unseeded`
  - Code: `idx = np.random.choice(len(predictions), size=len(predictions), replace=True)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/methods_dispensary/derek_beach.py:5154**
  - Type: `np_random_unseeded`
  - Code: `idx = np.random.choice(len(predictions), size=len(predictions), replace=True)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

##### LOW (60 issues)

- **src/methods_dispensary/embedding_policy.py:485**
  - Type: `set_iteration`
  - Code: `for section in sections:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/embedding_policy.py:1317**
  - Type: `dict_keys_iteration`
  - Code: `"pdq_filter_keys": sorted(pdq_filter.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/methods_dispensary/embedding_policy.py:1403**
  - Type: `set_iteration`
  - Code: `for idx in remaining_indices:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/embedding_policy.py:1449**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/embedding_policy.py:1452**
  - Type: `set_iteration`
  - Code: `for pattern in patterns:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/embedding_policy.py:1455**
  - Type: `set_iteration`
  - Code: `for match in matches:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/semantic_chunking_policy.py:188**
  - Type: `set_iteration`
  - Code: `for section in sections:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/bayesian_multilevel_system.py:785**
  - Type: `set_iteration`
  - Code: `for meso in meso_analyses:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2213**
  - Type: `set_iteration`
  - Code: `for page in doc:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2312**
  - Type: `set_iteration`
  - Code: `for pattern in product_patterns:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 50 more)*

##### ACCEPTABLE (5 issues)

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:1905**
  - Type: `datetime_now`
  - Code: `report += f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:1905**
  - Type: `datetime_now`
  - Code: `report += f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:1140**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/methods_dispensary/teoria_cambio.py:1149**
  - Type: `time_time`
  - Code: `total_time = time.time() - start_time`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/methods_dispensary/analyzer_one.py:219**
  - Type: `datetime_now`
  - Code: `"extraction_timestamp": datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

---

## Recommendations

Pipeline is NOT CERTIFIED. Critical determinism issues must be addressed before certification.

### Priority Actions

1. **Address all CRITICAL issues** - These prevent certification
2. **Review HIGH severity issues** - May compromise reproducibility
3. **Document ACCEPTABLE patterns** - Ensure they don't affect computation
