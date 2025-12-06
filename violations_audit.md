# SIN_CARRETA Compliance Audit Report

## Violations Detected

### src/farfan_pipeline/processing/spc_ingestion.py
- Hardcoded calibration value detected: SEMANTIC_COHERENCE_THRESHOLD = 0.72 (Line 354)
- Hardcoded calibration value detected: ENTITY_EXTRACTION_THRESHOLD = 0.55 (Line 357)
- Hardcoded calibration value detected: HIERARCHICAL_CLUSTER_THRESHOLD = 0.7 (Line 367)
- Hardcoded calibration value detected: MIN_COHERENCE_SCORE = 0.55 (Line 380)
- Hardcoded calibration value detected: DEDUPLICATION_THRESHOLD = 0.88 (Line 385)
- Hardcoded calibration value detected: NEAR_DUPLICATE_THRESHOLD = 0.92 (Line 386)
- Hardcoded calibration value detected: score = 0.0 (Line 1076)
- Hardcoded calibration value detected: strength_score = 0.5 (Line 2134)

### src/farfan_pipeline/processing/quality_gates.py
- Hardcoded calibration value detected: MIN_STRATEGIC_SCORE = 0.3 (Line 27)
- Hardcoded calibration value detected: MIN_QUALITY_SCORE = 0.5 (Line 28)

### src/farfan_pipeline/contracts/tools/sort_sanity.py
- Potential hardcoded calibration dict detected at Line 11
- Potential hardcoded calibration dict detected at Line 12
- Potential hardcoded calibration dict detected at Line 13

### src/farfan_pipeline/contracts/tools/refusal_matrix.py
- Potential hardcoded calibration dict detected at Line 11
- Potential hardcoded calibration dict detected at Line 12
- Potential hardcoded calibration dict detected at Line 13

### src/farfan_pipeline/contracts/tools/rcc_report.py
- Hardcoded calibration value detected: alpha = 0.05 (Line 15)

### src/farfan_pipeline/contracts/tests/test_rcc.py
- Hardcoded calibration value detected: alpha = 0.1 (Line 15)
- Hardcoded calibration value detected: alpha = 0.1 (Line 30)

### src/farfan_pipeline/contracts/tests/test_refusal.py
- Potential hardcoded calibration dict detected at Line 19
- Potential hardcoded calibration dict detected at Line 23

### src/farfan_pipeline/core/method_inventory.py
- Reference to YAML file detected (YAML is prohibited)

### src/farfan_pipeline/core/calibration/orchestrator.py
- Hardcoded calibration value detected: CALIBRATION_THRESHOLD = 0.7 (Line 35)

### src/farfan_pipeline/core/calibration/unit_layer.py
- Potential hardcoded calibration dict detected at Line 193
- Potential hardcoded calibration dict detected at Line 199
- Hardcoded calibration value detected: total_weight = 0.0 (Line 206)
- Hardcoded calibration value detected: weighted_score = 0.0 (Line 207)
- Hardcoded calibration value detected: score = 0.0 (Line 214)
- Hardcoded calibration value detected: total_struct_score = 0.0 (Line 265)

### src/farfan_pipeline/core/calibration/chain_layer.py
- Potential hardcoded calibration dict detected at Line 114

### src/farfan_pipeline/core/calibration/compatibility.py
- Potential hardcoded calibration dict detected at Line 92

### src/farfan_pipeline/core/calibration/congruence_layer.py
- Potential hardcoded calibration dict detected at Line 60
- Potential hardcoded calibration dict detected at Line 63

### src/farfan_pipeline/core/orchestrator/signal_registry.py
- SyntaxError: Could not parse file for AST analysis

### src/farfan_pipeline/core/orchestrator/irrigation_synchronizer.py
- Hardcoded calibration value detected: SKEW_THRESHOLD_CV = 0.3 (Line 68)

### src/farfan_pipeline/analysis/bayesian_multilevel_system.py
- SyntaxError: Could not parse file for AST analysis

### src/farfan_pipeline/analysis/meso_cluster_analysis.py
- Hardcoded calibration value detected: weighted_sum = 0.0 (Line 79)

### src/farfan_pipeline/analysis/macro_prompts.py
- Hardcoded calibration value detected: total_weight = 0.0 (Line 240)
- Hardcoded calibration value detected: weighted_sum = 0.0 (Line 241)
- Hardcoded calibration value detected: weighted_sum = 0.0 (Line 652)
- Hardcoded calibration value detected: weighted_sq_diff = 0.0 (Line 712)

### src/farfan_pipeline/analysis/teoria_cambio.py
- Potential hardcoded calibration dict detected at Line 626

### src/farfan_pipeline/analysis/report_assembly.py
- Hardcoded calibration value detected: min_score = 0.0 (Line 250)
- Hardcoded calibration value detected: max_score = 1.0 (Line 251)

### src/farfan_pipeline/analysis/derek_beach.py
- Reference to YAML file detected (YAML is prohibited)
- Potential hardcoded calibration dict detected at Line 4586
- Potential hardcoded calibration dict detected at Line 4970

### src/farfan_pipeline/utils/metadata_loader.py
- Reference to YAML file detected (YAML is prohibited)

### src/farfan_pipeline/utils/paths.py
- Reference to YAML file detected (YAML is prohibited)

### src/farfan_pipeline/api/dashboard_data_service.py
- Potential hardcoded calibration dict detected at Line 264

### src/farfan_pipeline/api/api_server.py
- SyntaxError: Could not parse file for AST analysis

