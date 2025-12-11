# F.A.R.F.A.N Pipeline Determinism Certification Report

**Version:** 1.0.0
**Generated:** 2025-12-11T07:53:35.607142
**Overall Score:** 0.389
**Overall Status:** `NOT_CERTIFIED`

---

## Executive Summary

- **Total Phases:** 10
- **Certified Phases:** 2
- **Certified With Notes Phases:** 4
- **Not Certified Phases:** 4
- **Total Issues:** 478
- **Critical Issues:** 11
- **Overall Score:** 0.389
- **Recommendation:** Pipeline is NOT CERTIFIED. Critical determinism issues must be addressed before certification.

---

## Phase-by-Phase Analysis

### Phase 0: Validation & Bootstrap

**Phase ID:** `Phase_zero`  
**Status:** `NOT_CERTIFIED`  
**Determinism Score:** 0.000  
**Files Scanned:** 24  
**Total Lines:** 9649  

#### Issues by Severity

##### CRITICAL (7 issues)

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:44**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:54**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:63**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:73**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:163**
  - Type: `uuid_generation`
  - Code: `default_factory=lambda: str(uuid.uuid4()),`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/enhanced_contracts.py:379**
  - Type: `uuid_generation`
  - Code: `default_factory=lambda: str(uuid.uuid4()),`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_zero/deterministic_execution.py:212**
  - Type: `uuid_generation`
  - Code: `correlation_id = str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

##### HIGH (25 issues)

- **src/canonic_phases/Phase_zero/schema_monitor.py:98**
  - Type: `random_unseeded`
  - Code: `return random.random() < self.sample_rate`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism.py:290**
  - Type: `random_unseeded`
  - Code: `...     v1 = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism.py:291**
  - Type: `np_random_unseeded`
  - Code: `...     a1 = np.random.rand(3)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

- **src/canonic_phases/Phase_zero/determinism.py:293**
  - Type: `random_unseeded`
  - Code: `...     v2 = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/determinism.py:294**
  - Type: `np_random_unseeded`
  - Code: `...     a2 = np.random.rand(3)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

- **src/canonic_phases/Phase_zero/deterministic_execution.py:49**
  - Type: `random_unseeded`
  - Code: `...     value = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/deterministic_execution.py:113**
  - Type: `random_unseeded`
  - Code: `...     result = random.randint(0, 100)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/deterministic_execution.py:171**
  - Type: `random_unseeded`
  - Code: `...     return x + random.randint(0, 10)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/deterministic_execution.py:400**
  - Type: `random_unseeded`
  - Code: `initial_value = random.random()`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/canonic_phases/Phase_zero/deterministic_execution.py:402**
  - Type: `random_unseeded`
  - Code: `_ = random.random()  # Different value inside scope`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

  *(... and 15 more)*

##### LOW (26 issues)

- **src/canonic_phases/Phase_zero/bootstrap.py:101**
  - Type: `dict_keys_iteration`
  - Code: `accessed_keys=list(result.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/bootstrap.py:116**
  - Type: `dict_keys_iteration`
  - Code: `accessed_keys=list(result.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/bootstrap.py:409**
  - Type: `set_iteration`
  - Code: `for warning in warnings:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/bootstrap.py:971**
  - Type: `dict_keys_iteration`
  - Code: `provider_keys = sorted(provider._data.keys()) if hasattr(provider, '_data') else []`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:121**
  - Type: `dict_keys_iteration`
  - Code: `keys = set(payload.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:128**
  - Type: `set_iteration`
  - Code: `for key in keys:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:162**
  - Type: `dict_keys_iteration`
  - Code: `sources = [source] if source else list(self.stats_by_source.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:164**
  - Type: `set_iteration`
  - Code: `for src in sources:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:288**
  - Type: `dict_keys_iteration`
  - Code: `"sources": list(self.stats_by_source.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_zero/schema_monitor.py:354**
  - Type: `dict_keys_iteration`
  - Code: `payload_keys = set(payload.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

  *(... and 16 more)*

##### ACCEPTABLE (6 issues)

- **src/canonic_phases/Phase_zero/bootstrap.py:405**
  - Type: `time_time`
  - Code: `self._start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_zero/bootstrap.py:501**
  - Type: `time_time`
  - Code: `elapsed = time.time() - self._start_time`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_zero/bootstrap.py:515**
  - Type: `time_time`
  - Code: `elapsed = time.time() - self._start_time`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_zero/signature_validator.py:46**
  - Type: `datetime_now`
  - Code: `timestamp: str = field(default_factory=lambda: datetime.now().isoformat())`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/canonic_phases/Phase_zero/signature_validator.py:379**
  - Type: `datetime_now`
  - Code: `"audit_timestamp": datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/canonic_phases/Phase_zero/coverage_gate.py:105**
  - Type: `datetime_now`
  - Code: `"timestamp": datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

---

### Phase 1: Document Ingestion

**Phase ID:** `Phase_one`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.200  
**Files Scanned:** 10  
**Total Lines:** 5840  

#### Issues by Severity

##### LOW (40 issues)

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

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:411**
  - Type: `set_iteration`
  - Code: `for field in REQUIRED_METADATA:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:426**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:666**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:676**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py:968**
  - Type: `set_iteration`
  - Code: `for page in doc:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 30 more)*

---

### Phase 2: Micro Analysis (300 Executors)

**Phase ID:** `Phase_two`  
**Status:** `NOT_CERTIFIED`  
**Determinism Score:** 0.000  
**Files Scanned:** 20  
**Total Lines:** 18377  

#### Issues by Severity

##### CRITICAL (1 issues)

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:325**
  - Type: `uuid_generation`
  - Code: `self.correlation_id = str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

##### HIGH (1 issues)

- **src/canonic_phases/Phase_two/arg_router.py:397**
  - Type: `random_unseeded`
  - Code: `if random.random() > self.sample_rate:`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

##### LOW (73 issues)

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

- **src/canonic_phases/Phase_two/evidence_nexus.py:1089**
  - Type: `set_iteration`
  - Code: `for ev_type in EvidenceType:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1113**
  - Type: `set_iteration`
  - Code: `for type_str in required_types:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1140**
  - Type: `set_iteration`
  - Code: `for node in primary_nodes:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1149**
  - Type: `set_iteration`
  - Code: `for n in supporting:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1241**
  - Type: `set_iteration`
  - Code: `for c in citations:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1357**
  - Type: `set_iteration`
  - Code: `for elem in expected_elements:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_two/evidence_nexus.py:1699**
  - Type: `set_iteration`
  - Code: `for rule in assembly_rules:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 63 more)*

##### ACCEPTABLE (21 issues)

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

- **src/canonic_phases/Phase_two/evidence_nexus.py:1600**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/evidence_nexus.py:1631**
  - Type: `time_time`
  - Code: `processing_time_ms = (time.time() - start_time) * 1000`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/evidence_nexus.py:2016**
  - Type: `time_time`
  - Code: `"timestamp":  time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/evidence_nexus.py:2097**
  - Type: `time_time`
  - Code: `"processing_timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/executor_calibration_integration.py:426**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:352**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_two/irrigation_synchronizer.py:367**
  - Type: `time_time`
  - Code: `"timestamp": time.time(),`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

  *(... and 11 more)*

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
**Determinism Score:** 0.600  
**Files Scanned:** 5  
**Total Lines:** 3778  

#### Issues by Severity

##### LOW (20 issues)

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

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:201**
  - Type: `set_iteration`
  - Code: `for question in micro_questions:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:218**
  - Type: `set_iteration`
  - Code: `for area in policy_areas:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:372**
  - Type: `set_iteration`
  - Code: `for area in policy_areas:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:401**
  - Type: `set_iteration`
  - Code: `for cluster in clusters:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:470**
  - Type: `set_iteration`
  - Code: `for item in items:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:493**
  - Type: `dict_keys_iteration`
  - Code: `missing_keys = set(required_keys.keys()) - set(res_dict.keys())`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_four_five_six_seven/aggregation.py:791**
  - Type: `dict_keys_iteration`
  - Code: `msg = f"Invalid policy area ID: {area_id}. Valid codes: {sorted(canonical_areas.keys())}"`
  - Recommendation: Use sorted(dict.keys()) if order matters

  *(... and 10 more)*

---

### Phase 8: Recommendations

**Phase ID:** `Phase_eight`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.840  
**Files Scanned:** 3  
**Total Lines:** 1438  

#### Issues by Severity

##### LOW (8 issues)

- **src/canonic_phases/Phase_eight/recommendation_engine.py:256**
  - Type: `set_iteration`
  - Code: `for question in micro_questions:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:727**
  - Type: `set_iteration`
  - Code: `for key in required_keys:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:819**
  - Type: `set_iteration`
  - Code: `for field in required_fields:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:913**
  - Type: `set_iteration`
  - Code: `for artifact in verification:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:929**
  - Type: `set_iteration`
  - Code: `for key in required_artifact_fields:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:964**
  - Type: `dict_keys_iteration`
  - Code: `missing = required_keys - execution.keys()`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:986**
  - Type: `dict_keys_iteration`
  - Code: `missing = required_keys - budget.keys()`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/canonic_phases/Phase_eight/recommendation_engine.py:1005**
  - Type: `set_iteration`
  - Code: `for source in funding_sources:`
  - Recommendation: Use sorted(set) if order matters

---

### Phase 9: Report Assembly

**Phase ID:** `Phase_nine`  
**Status:** `NOT_CERTIFIED`  
**Determinism Score:** 0.170  
**Files Scanned:** 2  
**Total Lines:** 1280  

#### Issues by Severity

##### CRITICAL (3 issues)

- **src/canonic_phases/Phase_nine/report_assembly.py:74**
  - Type: `uuid_generation`
  - Code: `self.event_id = event_id or str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_nine/report_assembly.py:190**
  - Type: `uuid_generation`
  - Code: `default_factory=lambda: str(uuid.uuid4()),`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

- **src/canonic_phases/Phase_nine/report_assembly.py:561**
  - Type: `uuid_generation`
  - Code: `correlation_id = str(uuid.uuid4())`
  - Recommendation: Use deterministic ID generation based on correlation_id and context

##### LOW (4 issues)

- **src/canonic_phases/Phase_nine/report_assembly.py:736**
  - Type: `set_iteration`
  - Code: `for question in micro_questions:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_nine/report_assembly.py:803**
  - Type: `set_iteration`
  - Code: `for item in raw_clusters:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_nine/report_assembly.py:868**
  - Type: `set_iteration`
  - Code: `for rec in raw_recs:`
  - Recommendation: Use sorted(set) if order matters

- **src/canonic_phases/Phase_nine/report_assembly.py:1164**
  - Type: `dict_keys_iteration`
  - Code: `print(f"   ✓ Structured dict: {list(e.to_dict().keys())}")`
  - Recommendation: Use sorted(dict.keys()) if order matters

##### ACCEPTABLE (4 issues)

- **src/canonic_phases/Phase_nine/report_assembly.py:539**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_nine/report_assembly.py:685**
  - Type: `time_time`
  - Code: `latency_ms = (time.time() - start_time) * 1000`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_nine/report_assembly.py:915**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/canonic_phases/Phase_nine/report_assembly.py:934**
  - Type: `time_time`
  - Code: `latency_ms = (time.time() - start_time) * 1000`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

---

### Orchestration Layer

**Phase ID:** `orchestration`  
**Status:** `CERTIFIED_WITH_NOTES`  
**Determinism Score:** 0.080  
**Files Scanned:** 33  
**Total Lines:** 13279  

#### Issues by Severity

##### HIGH (1 issues)

- **src/orchestration/memory_safety.py:212**
  - Type: `random_unseeded`
  - Code: `return random.sample(items, max_elements)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

##### LOW (41 issues)

- **src/orchestration/task_planner.py:147**
  - Type: `dict_keys_iteration`
  - Code: `sorted_keys = sorted(set(question_schema.keys()) & set(chunk_schema.keys()))`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/task_planner.py:148**
  - Type: `set_iteration`
  - Code: `for key in sorted_keys:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/task_planner.py:295**
  - Type: `set_iteration`
  - Code: `for signal in resolved_signals:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/factory.py:722**
  - Type: `set_iteration`
  - Code: `for policy_area_id in policy_areas:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/factory.py:1322**
  - Type: `dict_keys_iteration`
  - Code: `"policy_areas": sorted(bundle.enriched_signal_packs.keys()),`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/factory.py:1408**
  - Type: `dict_keys_iteration`
  - Code: `for class_name in class_paths.keys():`
  - Recommendation: Use sorted(dict.keys()) if order matters

- **src/orchestration/factory.py:1417**
  - Type: `set_iteration`
  - Code: `for executor_info in executors_methods:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/factory.py:1421**
  - Type: `set_iteration`
  - Code: `for method_info in methods:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/factory.py:1570**
  - Type: `set_iteration`
  - Code: `for dim_id in expected_dims:`
  - Recommendation: Use sorted(set) if order matters

- **src/orchestration/factory.py:1583**
  - Type: `set_iteration`
  - Code: `for pa_id in expected_pas:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 31 more)*

##### ACCEPTABLE (3 issues)

- **src/orchestration/factory.py:486**
  - Type: `time_time`
  - Code: `construction_start = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/orchestration/factory.py:520**
  - Type: `time_time`
  - Code: `construction_duration = time.time() - construction_start`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

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
**Status:** `NOT_CERTIFIED`  
**Determinism Score:** 0.000  
**Files Scanned:** 11  
**Total Lines:** 22412  

#### Issues by Severity

##### HIGH (19 issues)

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:1905**
  - Type: `datetime_now`
  - Code: `report += f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2110**
  - Type: `datetime_now`
  - Code: `start_time = datetime.now()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2149**
  - Type: `datetime_now`
  - Code: `'processing_time_seconds': (datetime.now() - start_time).total_seconds(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2195**
  - Type: `datetime_now`
  - Code: `elapsed = (datetime.now() - start_time).total_seconds()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:1905**
  - Type: `datetime_now`
  - Code: `report += f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:2110**
  - Type: `datetime_now`
  - Code: `start_time = datetime.now()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:2149**
  - Type: `datetime_now`
  - Code: `'processing_time_seconds': (datetime.now() - start_time).total_seconds(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:2195**
  - Type: `datetime_now`
  - Code: `elapsed = (datetime.now() - start_time).total_seconds()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/derek_beach.py:5154**
  - Type: `random_unseeded`
  - Code: `idx = np.random.choice(len(predictions), size=len(predictions), replace=True)`
  - Recommendation: Ensure random.seed() is called with deterministic seed before use

- **src/methods_dispensary/derek_beach.py:5154**
  - Type: `np_random_unseeded`
  - Code: `idx = np.random.choice(len(predictions), size=len(predictions), replace=True)`
  - Recommendation: Use np.random.default_rng(seed) or ensure np.random.seed() is called

  *(... and 9 more)*

##### LOW (155 issues)

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

- **src/methods_dispensary/semantic_chunking_policy.py:756**
  - Type: `set_iteration`
  - Code: `for chunk in chunks:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/bayesian_multilevel_system.py:701**
  - Type: `set_iteration`
  - Code: `for analysis in meso_analyses:`
  - Recommendation: Use sorted(set) if order matters

- **src/methods_dispensary/bayesian_multilevel_system.py:753**
  - Type: `set_iteration`
  - Code: `for micro in micro_analyses:`
  - Recommendation: Use sorted(set) if order matters

  *(... and 145 more)*

##### ACCEPTABLE (20 issues)

- **src/methods_dispensary/financiero_viabilidad_tablas copy.py:2148**
  - Type: `datetime_now`
  - Code: `'analysis_date': datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/financiero_viabilidad_tablas.py:2148**
  - Type: `datetime_now`
  - Code: `'analysis_date': datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:180**
  - Type: `datetime_now`
  - Code: `base_metadata["created"] = datetime.now().isoformat()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:233**
  - Type: `datetime_now`
  - Code: `return datetime.now().isoformat()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:746**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/methods_dispensary/teoria_cambio.py:751**
  - Type: `datetime_now`
  - Code: `plan_name, seed, datetime.now().isoformat()`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:781**
  - Type: `datetime_now`
  - Code: `timestamp=datetime.now().isoformat(),`
  - Recommendation: Use datetime.utcnow() or inject clock for testing, document if used only for logging

- **src/methods_dispensary/teoria_cambio.py:795**
  - Type: `time_time`
  - Code: `computation_time=time.time() - start_time,`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/methods_dispensary/teoria_cambio.py:1140**
  - Type: `time_time`
  - Code: `start_time = time.time()`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

- **src/methods_dispensary/teoria_cambio.py:1149**
  - Type: `time_time`
  - Code: `total_time = time.time() - start_time`
  - Recommendation: Acceptable for performance metrics, ensure not used in computation

  *(... and 10 more)*

---

## Recommendations

Pipeline is NOT CERTIFIED. Critical determinism issues must be addressed before certification.

### Priority Actions

1. **Address all CRITICAL issues** - These prevent certification
2. **Review HIGH severity issues** - May compromise reproducibility
3. **Document ACCEPTABLE patterns** - Ensure they don't affect computation
