# Phase 1 CPP Repository Inventory Artifact (RIA)

Generated: `2025-12-18T01:52:41.902028+00:00`

## 1) Phase 1 File Inventory

files=26

| Category | Path | Bytes | SHA-256 |
|---|---|---:|---|
| `phase1_documentation` | `artifacts/reports/PHASE1_CERTIFICATION.md` | 5819 | `dfdf5c422b46a6f7d53694f44c86f543f3d66b68a7221948a281f5861ce2f9ea` |
| `phase1_documentation` | `artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md` | 41933195 | `c137da8e6d49f4bac19babc1e0540aa7b6106ce83eca3a2d1f9843011537a54c` |
| `phase1_documentation` | `artifacts/reports/PHASE_1_AUDIT_SUMMARY.md` | 9948 | `e7ad676d7dd54ee47013c537c1c6a45150c04767380846305c21a00c91f522e7` |
| `phase1_documentation` | `docs/PHASE_1_CIRCUIT_BREAKER.md` | 11498 | `59e96cff3c41818b6ce233c4ed30f09b4b947dc8fd5f69637b5c0aaf5717cfc0` |
| `phase1_documentation` | `requirements-phase1.txt` | 848 | `7597b60a6367249b80fcc2ad9a17543b74dea7dac3efbfeaeb0ea1a59024a7e3` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/FORCING ROUTE` | 39460 | `c3dd70cb710d3502b7dc3a97914a2f2fe5be6693ea45d42aa63d82c09a8ddd47` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/__init__.py` | 2667 | `1bde976674e576ef0e738199c839980631f86efce6b43502ab1b5f0d861af384` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/cpp_models.py` | 18365 | `cc9ea621b469e235a984944839350d25a2b83ac5e824da2f5fd436780ee885f3` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py` | 18122 | `1768ff2d6c837663050d85fd4aa6a5f41c0db1dcac25e965ce3202851f95ffdd` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py` | 19818 | `cf27b26b9c268f36de33c185c2862f62ae4a9a325f8b44dece4f9f59e068e502` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py` | 136094 | `5d42c75032ba54f5489f6410d37afd46568bf53b814b474354d5e5bcd5743a73` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py` | 13805 | `9bbb94590ddfc5aa1af7700e49b28b5006adffdf9dd5df47a4fcec3de0ed1ac2` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_models.py` | 11942 | `52f2ff6f836d5864742e7322c25941a006e666a04b05896674c43ac6b15f8d43` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py` | 8326 | `ef7c5f82d83e80522b8672475e68827763a9dfa4be5d8edc59297ccaeb2729e1` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py` | 137866 | `ff4ff2fd647a472329d2a83f3a6ce2a1e6f8c166f260cf83fe574cfcb042ad99` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase_protocol.py` | 12623 | `8e5f4bcf4cc78a303334d535631e029e0dc6fceebf158c9875826cb0ccfeaaac` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/signal_enrichment.py` | 22493 | `79188cb275c98c1d9faaaad65dceb69e063b06fad0d7761761ff23c980ecf0be` |
| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/structural.py` | 3387 | `1e2d09c85c394420ace79c130f2ae2e8c9cc764e8f7e71cf34b3cff096e665b8` |
| `phase1_tests` | `tests/test_model_output_verification.py` | 22455 | `2a62c235edee3d9e637c4d941628c83b24e1964c96aa393c4e403c81808ffe35` |
| `phase1_tests` | `tests/test_phase0_complete.py` | 26279 | `0bc5c89cc4ef1c86395adddc7e1404ae74619ab8b4b399e04e58d9cd46bd8666` |
| `phase1_tests` | `tests/test_phase1_circuit_breaker.py` | 11095 | `45f328fe4a01948ec353629c63442557feca86613b9ea3f768dc659da108fa27` |
| `phase1_tests` | `tests/test_phase1_complete.py` | 12209 | `c4ab1d7e4c7d25dac162abd11fd3658ec9ad7740153f54f7a7c62641dee909b7` |
| `phase1_tests` | `tests/test_phase1_severe.py` | 41187 | `1cb455859304a452fb37dbc8bad9caea68b1f439a2fde52c520d55f1e3f42833` |
| `phase1_tests` | `tests/test_phase1_signal_enrichment.py` | 14250 | `a896d5eb93bf21c531676ff1824776b051dd272ba32b04ca58a9bf16e275b424` |
| `phase1_tests` | `tests/test_phase1_type_integration.py` | 14034 | `2e13b21e7034f344ef4bde31c1606b7d9158c4fe33b4b09e334f539814633b6e` |
| `phase1_tests` | `tests/test_phase1_type_structure.py` | 11452 | `a58271386aba0dcdbfed02be9e54f00a3f0f314201f19972c0289b1ca1a57d54` |

## 2) Import/Reference Inventory

### canonic_phases.Phase_one

hits=315

```text
./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:39:### canonic_phases.Phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:44:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:45:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:46:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:47:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:48:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:49:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:50:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:51:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:52:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:53:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:54:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:55:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:56:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:57:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:58:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:59:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:60:./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:61:./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:62:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:63:./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:64:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:65:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:66:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:67:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:68:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:69:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:70:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:71:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:72:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:73:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:74:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:75:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:76:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:77:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:78:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:79:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:80:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:81:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:82:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:83:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:84:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:85:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:86:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:87:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:88:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:89:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:90:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:91:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:92:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:93:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:94:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:95:./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:96:./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:97:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:98:./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:99:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:100:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:101:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:102:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:103:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:104:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:105:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:106:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:107:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:108:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:109:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:110:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:111:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:112:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:113:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:114:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:115:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:116:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:117:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:118:./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:119:./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:120:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:121:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:122:./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:123:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:124:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:125:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:126:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:127:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:128:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:129:./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:130:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:131:./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:132:./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:141:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:142:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:143:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:144:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:145:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:146:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:147:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:148:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:149:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:150:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:151:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:168:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:181:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:187:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:188:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:189:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:195:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:196:./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:197:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:198:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:200:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:206:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:207:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:208:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:209:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:210:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:211:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:212:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:213:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:214:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:215:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:216:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:217:./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:218:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:219:./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:221:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:222:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:223:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:224:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:225:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:226:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:227:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:228:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:229:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:231:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:232:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:234:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:235:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:236:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:243:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:246:./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:247:./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:266:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:269:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:270:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:271:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:275:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:276:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:279:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:283:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:285:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:297:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:298:./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:299:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:300:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:302:./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:303:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:304:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:305:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:306:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:307:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:308:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:309:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:310:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:311:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:312:./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:313:./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:314:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:315:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:316:./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:317:./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:318:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:319:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:320:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:321:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:322:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:323:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:324:./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:325:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:369:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:372:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:374:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:375:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:376:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:378:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:379:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:402:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:428:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:449:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:450:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:451:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:452:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:453:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:454:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:455:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:456:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:457:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:458:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:459:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:474:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:478:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:479:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:480:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:489:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:493:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:499:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:501:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:519:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:520:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:521:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:542:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:543:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:546:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:550:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:557:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:558:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:559:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:560:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:564:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:672:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:692:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:701:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:716:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:728:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:731:### from canonic_phases.Phase_one import ...
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:739:### from canonic_phases.Phase_one\.phase1_.*
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./scripts/generate_phase1_ria.py:187:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./scripts/generate_phase1_ria.py:214:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./scripts/generate_phase1_ria.py:215:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1fa2339b948eaf5e7 [... omitted end of long line]
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
```

### Phase_one

hits=642

```text
./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./src/farfan_pipeline.egg-info/SOURCES.txt:138:src/farfan_pipeline/phases/Phase_one/__init__.py
./src/farfan_pipeline.egg-info/SOURCES.txt:139:src/farfan_pipeline/phases/Phase_one/cpp_models.py
./src/farfan_pipeline.egg-info/SOURCES.txt:140:src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py
./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./src/farfan_pipeline.egg-info/SOURCES.txt:147:src/farfan_pipeline/phases/Phase_one/phase_protocol.py
./src/farfan_pipeline.egg-info/SOURCES.txt:148:src/farfan_pipeline/phases/Phase_one/signal_enrichment.py
./src/farfan_pipeline.egg-info/SOURCES.txt:149:src/farfan_pipeline/phases/Phase_one/structural.py
./artifacts/reports/PHASE1_CERTIFICATION.md:19:- ✓ src/canonic_phases/Phase_one/__init__.py
./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:290:- `src/canonic_phases/Phase_one/phase_protocol.py` - Removed unused pydantic import
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:291:- `src/canonic_phases/Phase_one/phase0_input_validation.py` - Made pydantic optional, extracted shared validation logic
./DEPENDENCIES.md:101:│   ├── Phase_one/__init__.py
./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./audit_signal_irrigation_blockers_report.json:55:    "Phase_one": {
./src/canonic_phases/__init__.py:24:    "Phase_one",
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:81:│   └── Phase_one/            # Incomplete
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:131:    │   ├── phase_01_ingestion/       # ← Phase_one renamed
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:288:    'src/canonic_phases/Phase_one': 'src/farfan/phases/phase_01_ingestion',
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:387:move_and_log "src/canonic_phases/Phase_one" "src/farfan/phases/phase_01_ingestion"
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
./SIGNAL_OPTIMIZATION_SUMMARY.md:14:**File**: `src/canonic_phases/Phase_one/signal_enrichment.py` (600+ lines)
./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:380:**Location**: `src/canonic_phases/Phase_one/phase0_input_validation.py:110-119`
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:445:**Location**: `src/canonic_phases/Phase_one/phase0_input_validation.py:179-209`
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:541:**Location**: `src/canonic_phases/Phase_one/phase_protocol.py`
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1379:**Contract Files** (Phase_one/):
./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_phase1_type_structure.py:74:    cpp_models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./audit_signal_irrigation_blockers.py:175:        "Phase_one": "Phase 1 (Ingestion)",
./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE_1_SIGNAL_ENRICHMENT.md:425:- Signal Enrichment Module: `src/canonic_phases/Phase_one/signal_enrichment.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/PHASE1_TYPE_INTEGRATION.md:41:- `src/canonic_phases/Phase_one/cpp_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE1_TYPE_INTEGRATION.md:309:- **CPP Models**: `src/canonic_phases/Phase_one/cpp_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./all_py_files.txt:247:./src/farfan_pipeline/phases/Phase_one/__init__.py
./all_py_files.txt:248:./src/farfan_pipeline/phases/Phase_one/cpp_models.py
./all_py_files.txt:249:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py
./all_py_files.txt:250:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py
./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./all_py_files.txt:257:./src/farfan_pipeline/phases/Phase_one/signal_enrichment.py
./all_py_files.txt:258:./src/farfan_pipeline/phases/Phase_one/structural.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_integration.py:161:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./scripts/generate_phase1_ria.py:28:    REPO_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_one"
./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./scripts/generate_phase1_ria.py:187:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./scripts/generate_phase1_ria.py:188:        ("Phase_one", r"\bPhase_one\b"),
./scripts/generate_phase1_ria.py:214:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./scripts/generate_phase1_ria.py:215:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./PHASE_0_COMPLETE_ANALYSIS.md:54:### Contract Definitions (Phase_one/)
./PHASE_0_COMPLETE_ANALYSIS.md:56:src/canonic_phases/Phase_one/
./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./tests/test_phase1_complete.py:39:        'src/canonic_phases/Phase_one/__init__.py',
./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:30:  - `Phase_one` (Title Case, Number word)
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:56:3.  **Circular/Confused Dependencies**: `Phase_zero` tests import from `Phase_one` (`phase0_input_validation`).
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:85:    │   ├── phase_01_ingestion/# Was Phase_one
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:114:    - `Phase_one` -> `phase_01_ingestion` (snake_case + numeric sortable + descriptive).
./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./PHASE1_WIRING_DOCUMENTATION.md:368:- `src/canonic_phases/Phase_one/phase0_input_validation.py` - Contratos
./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./PHASE1_WIRING_DOCUMENTATION.md:370:- `src/canonic_phases/Phase_one/cpp_models.py` - Modelos de output
./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./PHASE1_WIRING_DOCUMENTATION.md:665:- **Phase 1**: `src/canonic_phases/Phase_one/`
./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
./src/farfan_pipeline/phases/__init__.py:9:    "Phase_one",
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1fa2339b948eaf5e7 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:15:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/FORCING ROUTE` | 39460 | `c3dd70cb710d3502b7dc3a97914a2f2fe5be6693ea45d42aa63d82c09a8ddd47` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:16:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/__init__.py` | 2667 | `1bde976674e576ef0e738199c839980631f86efce6b43502ab1b5f0d861af384` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:17:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/cpp_models.py` | 18365 | `cc9ea621b469e235a984944839350d25a2b83ac5e824da2f5fd436780ee885f3` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:18:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py` | 18122 | `1768ff2d6c837663050d85fd4aa6a5f41c0db1dcac25e965ce3202851f95ffdd` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:19:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py` | 19818 | `cf27b26b9c268f36de33c185c2862f62ae4a9a325f8b44dece4f9f59e068e502` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:20:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py` | 136094 | `5d42c75032ba54f5489f6410d37afd46568bf53b814b474354d5e5bcd5743a73` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:21:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py` | 13805 | `9bbb94590ddfc5aa1af7700e49b28b5006adffdf9dd5df47a4fcec3de0ed1ac2` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:22:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_models.py` | 11942 | `52f2ff6f836d5864742e7322c25941a006e666a04b05896674c43ac6b15f8d43` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:23:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py` | 8326 | `ef7c5f82d83e80522b8672475e68827763a9dfa4be5d8edc59297ccaeb2729e1` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:24:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py` | 137866 | `ff4ff2fd647a472329d2a83f3a6ce2a1e6f8c166f260cf83fe574cfcb042ad99` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:25:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase_protocol.py` | 12623 | `8e5f4bcf4cc78a303334d535631e029e0dc6fceebf158c9875826cb0ccfeaaac` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:26:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/signal_enrichment.py` | 22493 | `79188cb275c98c1d9faaaad65dceb69e063b06fad0d7761761ff23c980ecf0be` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:27:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/structural.py` | 3387 | `1e2d09c85c394420ace79c130f2ae2e8c9cc764e8f7e71cf34b3cff096e665b8` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:39:### canonic_phases.Phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:44:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:45:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:46:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:47:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:48:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:49:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:50:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:51:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:52:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:53:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:54:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:55:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:56:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:57:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:58:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:59:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:60:./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:61:./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:62:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:63:./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:64:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:65:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:66:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:67:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:68:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:69:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:70:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:71:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:72:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:73:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:74:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:75:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:76:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:77:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:78:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:79:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:80:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:81:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:82:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:83:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:84:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:85:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:86:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:87:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:88:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:89:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:90:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:91:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:92:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:93:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:94:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:95:./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:96:./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:97:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:98:./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:99:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:100:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:101:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:102:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:103:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:104:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:105:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:106:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:107:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:108:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:109:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:110:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:111:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:112:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:113:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:114:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:115:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:116:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:117:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:118:./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:119:./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:120:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:121:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:122:./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:123:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:124:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:125:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:126:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:127:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:128:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:129:./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:130:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:131:./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:132:./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:135:### Phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:140:./artifacts/reports/PHASE1_CERTIFICATION.md:19:- ✓ src/canonic_phases/Phase_one/__init__.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:141:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:142:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:143:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1484:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:144:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:163:| `canonic_phases.Phase_one.phase_protocol` | ✅ | No dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:145:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:164:| `canonic_phases.Phase_one.phase0_input_validation` | ✅ | Graceful pydantic fallback |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:146:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:147:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:166:| `canonic_phases.Phase_one.cpp_models` | ✅ | Optional SISAS imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:148:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:167:| `canonic_phases.Phase_one.structural` | ✅ | No issues |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:149:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:150:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:169:| `canonic_phases.Phase_one` | ✅ | Package imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:151:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:152:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:290:- `src/canonic_phases/Phase_one/phase_protocol.py` - Removed unused pydantic import
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:153:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:291:- `src/canonic_phases/Phase_one/phase0_input_validation.py` - Made pydantic optional, extracted shared validation logic
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:154:./src/farfan_pipeline.egg-info/SOURCES.txt:138:src/farfan_pipeline/phases/Phase_one/__init__.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:155:./src/farfan_pipeline.egg-info/SOURCES.txt:139:src/farfan_pipeline/phases/Phase_one/cpp_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:156:./src/farfan_pipeline.egg-info/SOURCES.txt:140:src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:157:./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:158:./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:159:./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:160:./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:161:./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:162:./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:163:./src/farfan_pipeline.egg-info/SOURCES.txt:147:src/farfan_pipeline/phases/Phase_one/phase_protocol.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:164:./src/farfan_pipeline.egg-info/SOURCES.txt:148:src/farfan_pipeline/phases/Phase_one/signal_enrichment.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:165:./src/farfan_pipeline.egg-info/SOURCES.txt:149:src/farfan_pipeline/phases/Phase_one/structural.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:166:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:167:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:168:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:50:from canonic_phases.Phase_one import ...         # TitleCase
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:169:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:81:│   └── Phase_one/            # Incomplete
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:170:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:131:    │   ├── phase_01_ingestion/       # ← Phase_one renamed
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:171:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:288:    'src/canonic_phases/Phase_one': 'src/farfan/phases/phase_01_ingestion',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:172:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:387:move_and_log "src/canonic_phases/Phase_one" "src/farfan/phases/phase_01_ingestion"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:173:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:174:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:175:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:176:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:177:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:178:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:179:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:180:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:181:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:182:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:183:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:184:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:380:**Location**: `src/canonic_phases/Phase_one/phase0_input_validation.py:110-119`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:185:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:445:**Location**: `src/canonic_phases/Phase_one/phase0_input_validation.py:179-209`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:186:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:541:**Location**: `src/canonic_phases/Phase_one/phase_protocol.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:187:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:188:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1143:    from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:189:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:190:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1379:**Contract Files** (Phase_one/):
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:191:./SIGNAL_OPTIMIZATION_SUMMARY.md:14:**File**: `src/canonic_phases/Phase_one/signal_enrichment.py` (600+ lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:192:./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:193:./audit_signal_irrigation_blockers_report.json:55:    "Phase_one": {
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:194:./DEPENDENCIES.md:101:│   ├── Phase_one/__init__.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:195:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:196:./tests/test_phase0_complete.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:197:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:198:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:199:./src/canonic_phases/__init__.py:24:    "Phase_one",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:200:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:201:./tests/test_phase1_type_structure.py:74:    cpp_models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:202:./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:203:./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:204:./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:205:./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:206:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:207:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:208:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:209:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:210:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:211:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:212:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:213:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:214:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:215:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:216:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:217:./tests/test_model_output_verification.py:25:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:218:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:219:./tests/test_model_output_verification.py:52:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:220:./tests/test_phase1_complete.py:39:        'src/canonic_phases/Phase_one/__init__.py',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:221:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:222:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:223:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:224:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:225:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:226:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:227:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:228:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:229:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:230:./scripts/generate_phase1_ria.py:28:    REPO_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_one"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:231:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:232:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:233:./scripts/generate_phase1_ria.py:185:        ("Phase_one", r"\bPhase_one\b"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:234:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:235:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:236:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:237:./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:238:./tests/test_phase1_type_integration.py:161:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:239:./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:240:./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:241:./audit_signal_irrigation_blockers.py:175:        "Phase_one": "Phase 1 (Ingestion)",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:242:./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:243:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:244:./PHASE_0_COMPLETE_ANALYSIS.md:54:### Contract Definitions (Phase_one/)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:245:./PHASE_0_COMPLETE_ANALYSIS.md:56:src/canonic_phases/Phase_one/
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:246:./PHASE_0_COMPLETE_ANALYSIS.md:127:- `canonic_phases.Phase_one.*` (phase0_input_validation, phase_protocol)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:247:./IMPORT_FIX_COMPLETE.md:106:from canonic_phases.Phase_one import run_phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:248:./all_py_files.txt:247:./src/farfan_pipeline/phases/Phase_one/__init__.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:249:./all_py_files.txt:248:./src/farfan_pipeline/phases/Phase_one/cpp_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:250:./all_py_files.txt:249:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:251:./all_py_files.txt:250:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:252:./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:253:./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:254:./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:255:./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:256:./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:257:./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:258:./all_py_files.txt:257:./src/farfan_pipeline/phases/Phase_one/signal_enrichment.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:259:./all_py_files.txt:258:./src/farfan_pipeline/phases/Phase_one/structural.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:260:./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:261:./docs/PHASE_1_SIGNAL_ENRICHMENT.md:425:- Signal Enrichment Module: `src/canonic_phases/Phase_one/signal_enrichment.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:262:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:30:  - `Phase_one` (Title Case, Number word)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:263:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:56:3.  **Circular/Confused Dependencies**: `Phase_zero` tests import from `Phase_one` (`phase0_input_validation`).
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:264:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:85:    │   ├── phase_01_ingestion/# Was Phase_one
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:265:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:114:    - `Phase_one` -> `phase_01_ingestion` (snake_case + numeric sortable + descriptive).
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:266:./ARCHITECTURE_ANALYSIS_AND_PROPOSAL.md:142:- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:267:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:268:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:269:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:270:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:271:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:272:./PHASE1_WIRING_DOCUMENTATION.md:368:- `src/canonic_phases/Phase_one/phase0_input_validation.py` - Contratos
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:273:./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:274:./PHASE1_WIRING_DOCUMENTATION.md:370:- `src/canonic_phases/Phase_one/cpp_models.py` - Modelos de output
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:275:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:276:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:277:./PHASE1_WIRING_DOCUMENTATION.md:665:- **Phase 1**: `src/canonic_phases/Phase_one/`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:278:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:279:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:280:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:281:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:282:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:283:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:284:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:285:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:286:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:287:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:288:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:289:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:290:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:291:./docs/PHASE1_TYPE_INTEGRATION.md:41:- `src/canonic_phases/Phase_one/cpp_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:292:./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:293:./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:294:./docs/PHASE1_TYPE_INTEGRATION.md:309:- **CPP Models**: `src/canonic_phases/Phase_one/cpp_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:295:./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:296:./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:297:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:298:./docs/PHASE_1_CIRCUIT_BREAKER.md:113:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:299:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:300:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:301:./src/farfan_pipeline/phases/__init__.py:9:    "Phase_one",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:302:./src/farfan_pipeline/phases/Phase_zero/main.py:720:            from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:303:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:304:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:305:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:306:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:307:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:308:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:309:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:310:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:311:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:74:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:312:./src/farfan_pipeline/phases/Phase_one/__init__.py:25:from canonic_phases.Phase_one.phase_protocol import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:313:./src/farfan_pipeline/phases/Phase_one/__init__.py:33:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:314:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:315:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:316:./src/farfan_pipeline/phases/Phase_one/__init__.py:62:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:317:./backups/20251214_135858/orchestrator. py. bak:1464:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:318:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:319:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:320:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:321:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:322:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:323:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:324:./src/farfan_pipeline/orchestration/orchestrator.py:2031:            from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:325:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:334:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:441:            'phase': 'PHASE_1_CPP_INGESTION',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:342:./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:343:./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:344:./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:345:./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:346:./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:347:./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:358:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:359:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:360:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:362:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:365:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:366:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:367:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:369:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:370:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:371:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:372:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:374:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:375:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:376:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:378:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:379:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:380:./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:390:./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:394:./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:396:./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:398:./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:402:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:405:./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:406:./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:407:./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:408:./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:409:./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:410:./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:423:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:424:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:428:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:433:./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:440:./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:446:./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:449:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:450:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:451:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:452:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:453:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:454:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:455:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:456:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:457:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:458:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:459:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:474:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:478:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:479:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:480:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:484:./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:486:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:488:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:489:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:492:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:493:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:494:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:495:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:496:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:499:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:500:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:501:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:502:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:503:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:506:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:508:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:509:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:510:./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:511:./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:516:./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:517:./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:519:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:520:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:521:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:530:./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:542:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:543:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:544:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:545:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2623:            'phase1_version': 'CPP-2025.1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:546:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:547:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:212:[ERR-004] | MANIFEST | DEBE generarse phase1_error_manifest.json en caso de error fatal | verify archivo existe en filesystem | WARNING: Audito [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:548:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:407:        metadata={'source': 'phase1_spc_ingestion', 'cpp_schema': cpp.schema_version}
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:549:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:452:8. **ERROR MANIFEST**: En caso de error fatal, SIEMPRE generar `phase1_error_manifest.json`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:550:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:551:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:27:phase1_spc_ingestion:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:552:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:31:phase1_to_phase2_adapter:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:553:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:341:def validate_phase1_dependencies() -> bool:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:554:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:352:def generate_fix_script(output_path: str = "fix_phase1_dependencies.sh") -> None:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:555:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:376:        default="fix_phase1_dependencies.sh",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:556:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:385:        success = validate_phase1_dependencies()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:557:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:558:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:559:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:560:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:561:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:562:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2666:            'phase1_version': 'SPC-2025.1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:563:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py:352:            test_file = Path('.phase1_write_test')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:564:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:623:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:624:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:625:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1115:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:626:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1182:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:627:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1350:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:628:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1498:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:629:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1602:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:630:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1706:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:631:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1807:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:632:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1912:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:633:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1992:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:634:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2090:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:635:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2154:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:636:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2276:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:637:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2373:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:638:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2411:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:639:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2470:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:640:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2687:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:641:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:81:# These tools ensure idempotency and full traceability per FORCING ROUTE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:642:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:155:        """Validate PDF path format with zero tolerance per FORCING ROUTE [PRE-003]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:643:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:163:        """Validate run_id format with zero tolerance per FORCING ROUTE [PRE-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:644:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:64:        """Alias for paragraph_mapping per FORCING ROUTE [EXEC-SP2-005]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:645:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:161:        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:646:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:174:        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:647:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:190:        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:648:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:210:        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:649:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:223:        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:650:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:241:        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:651:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:652:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:653:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1123:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:654:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1190:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:655:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1358:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:656:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1506:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:657:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1610:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:658:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1714:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:659:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1815:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:660:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1920:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:661:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2005:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:662:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2112:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:663:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2184:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:664:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2306:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:665:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2404:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:666:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2442:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:667:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2513:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:668:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2730:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:669:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:6:All models are frozen dataclasses per [INV-010] FORCING ROUTE requirement.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:670:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:179:    Invariants per FORCING ROUTE:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:671:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:430:    Validator for CanonPolicyPackage per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:672:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:692:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:700:./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:701:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:716:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:722:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2757:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:723:./src/farfan_pipeline/phases/Phase_one/__init__.py:55:    execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:724:./src/farfan_pipeline/phases/Phase_one/__init__.py:96:    "execute_phase_1_with_full_contract",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:725:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2800:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:728:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:731:### from canonic_phases.Phase_one import ...
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:736:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:739:### from canonic_phases.Phase_one\.phase1_.*
```

### phase_1_cpp_ingestion

hits=5

```text
./scripts/generate_phase1_ria.py:189:        ("phase_1_cpp_ingestion", r"phase_1_cpp_ingestion"),
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:441:            'phase': 'PHASE_1_CPP_INGESTION',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:328:### phase_1_cpp_ingestion
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:333:./scripts/generate_phase1_ria.py:186:        ("phase_1_cpp_ingestion", r"phase_1_cpp_ingestion"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:334:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:441:            'phase': 'PHASE_1_CPP_INGESTION',
```

### phase1_

hits=743

```text
./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./src/farfan_pipeline.egg-info/SOURCES.txt:233:tests/test_phase1_circuit_breaker.py
./src/farfan_pipeline.egg-info/SOURCES.txt:234:tests/test_phase1_complete.py
./src/farfan_pipeline.egg-info/SOURCES.txt:235:tests/test_phase1_severe.py
./src/farfan_pipeline.egg-info/SOURCES.txt:236:tests/test_phase1_signal_enrichment.py
./src/farfan_pipeline.egg-info/SOURCES.txt:237:tests/test_phase1_type_integration.py
./src/farfan_pipeline.egg-info/SOURCES.txt:238:tests/test_phase1_type_structure.py
./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:15:- `phase1_method_guards.py` - Wrappers with try-catch and fallbacks
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:16:- `test_phase1_method_guards.py` - Tests for wrappers
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:17:- `PHASE1_METHOD_HARDENING.md` - Documentation
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:61:Created `phase1_pre_import_validator.py`:
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:151:- `docs/PHASE1_DEPENDENCY_MANAGEMENT.md` - Documents correct approach
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:155:- `tests/test_phase1_method_guards.py` - Tests for wrong approach
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:156:- `docs/PHASE1_METHOD_HARDENING.md` - Documented wrong approach
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:190:# phase1_spc_ingestion_full.py (to be integrated)
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./SIGNAL_OPTIMIZATION_SUMMARY.md:46:**File**: `tests/test_phase1_signal_enrichment.py` (400+ lines)
./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CERTIFICATION.md:105:grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:258:   grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./DEPENDENCIES.md:124:grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./audit_signal_irrigation_blockers_report.json:61:          "phase1_spc_ingestion_full.py"
./audit_signal_irrigation_blockers_report.json:65:          "phase1_spc_ingestion_full.py",
./CONTRACT_UPDATE_PHASE1_VALIDATION.md:196:- `CONTRACT_UPDATE_PHASE1_VALIDATION.md`: This document
./implement_phase1_subgroup_a.py:290:    report_path = Path("artifacts/cqvr_reports/batch4_Q076_Q100/SUBGROUP_A_PHASE1_REPORT.json")
./CANONICAL_REFACTORING_PHASE2_POLICY_PROCESSOR.md:297:- Phase 1: `CANONICAL_REFACTORING_PHASE1_COMPLETE.md`
./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:212:    chunk_source: str               # "phase1_spc_ingestion"
./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:312:            chunk_source="phase1_spc_ingestion",
./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:442:        "chunk_source": "phase1_spc_ingestion",
./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:800:    chunks_deliverable = run_phase1_spc_ingestion(test_document)
./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./tests/test_phase1_complete.py:101:    grid_spec = phase1_cpp_ingestion_full.PADimGridSpecification
./tests/test_phase1_type_structure.py:110:def test_phase1_models_imports_types():
./tests/test_phase1_type_structure.py:111:    """Test that phase1_models.py imports canonical types"""
./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_structure.py:119:        print(f"  ✗ phase1_models.py NOT found")
./tests/test_phase1_type_structure.py:156:def test_phase1_ingestion_uses_enums():
./tests/test_phase1_type_structure.py:157:    """Test that phase1_spc_ingestion_full.py uses enum types"""
./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_structure.py:165:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_structure.py:219:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_structure.py:265:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./tests/test_phase1_type_structure.py:310:        test_phase1_models_imports_types,
./tests/test_phase1_type_structure.py:311:        test_phase1_ingestion_uses_enums,
./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./tests/phase2_contracts/test_severe_interpreter.py:1254:            "phase1_complete",
./tests/test_metrics_persistence_integration.py:47:    phase1_instr = PhaseInstrumentation(
./tests/test_metrics_persistence_integration.py:53:    phase1_instr.start()
./tests/test_metrics_persistence_integration.py:54:    phase1_instr.increment(latency=0.456)
./tests/test_metrics_persistence_integration.py:55:    phase1_instr.complete()
./tests/test_metrics_persistence_integration.py:63:                "1": phase1_instr.build_metrics()
./tests/test_executor_chunk_synchronization.py:97:        chunk_source="phase1_spc_ingestion"
./tests/test_phase1_type_integration.py:48:def test_phase1_models_have_enum_fields():
./tests/test_phase1_type_integration.py:55:        # Import phase1_models using standard import
./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./tests/test_phase1_type_integration.py:57:        Chunk = phase1_models.Chunk
./tests/test_phase1_type_integration.py:58:        SmartChunk = phase1_models.SmartChunk
./tests/test_phase1_type_integration.py:59:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./tests/test_phase1_type_integration.py:99:            "phase1_models",
./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_integration.py:102:        phase1_models = importlib.util.module_from_spec(spec)
./tests/test_phase1_type_integration.py:103:        sys.modules['phase1_models_test2'] = phase1_models
./tests/test_phase1_type_integration.py:104:        spec.loader.exec_module(phase1_models)
./tests/test_phase1_type_integration.py:106:        SmartChunk = phase1_models.SmartChunk
./tests/test_phase1_type_integration.py:107:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./tests/test_phase1_type_integration.py:201:            "phase1_models",
./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./tests/test_phase1_type_integration.py:204:        phase1_models = importlib.util.module_from_spec(spec)
./tests/test_phase1_type_integration.py:205:        sys.modules['phase1_models_test3'] = phase1_models
./tests/test_phase1_type_integration.py:206:        spec.loader.exec_module(phase1_models)
./tests/test_phase1_type_integration.py:208:        SmartChunk = phase1_models.SmartChunk
./tests/test_phase1_type_integration.py:209:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./tests/test_phase1_type_integration.py:298:        source = phase1_file.read_text()
./tests/test_phase1_type_integration.py:324:        test_phase1_models_have_enum_fields,
./docs/DETERMINISM.md:185:    "phase1_chunking": get_derived_seed(42, "phase1_semantic_chunking"),
./docs/DETERMINISM.md:585:      "phase1_chunking": 3456789012,
./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/VALIDATION_GUIDE.md:138:    ops = ["phase0", "phase1_chunking", "phase2_D1_Q1", "phase3_scoring"]
./scripts/generate_phase1_ria.py:10:  python scripts/generate_phase1_ria.py
./scripts/generate_phase1_ria.py:27:PHASE1_IMPL_DIR = (
./scripts/generate_phase1_ria.py:71:def _collect_phase1_files() -> list[FileRecord]:
./scripts/generate_phase1_ria.py:74:    if PHASE1_IMPL_DIR.exists():
./scripts/generate_phase1_ria.py:75:        for p in sorted(PHASE1_IMPL_DIR.rglob("*")):
./scripts/generate_phase1_ria.py:83:                    category="phase1_implementation",
./scripts/generate_phase1_ria.py:94:                    category="phase1_documentation",
./scripts/generate_phase1_ria.py:108:                        category="phase1_documentation",
./scripts/generate_phase1_ria.py:120:                    category="phase1_tests",
./scripts/generate_phase1_ria.py:138:                    category="phase1_tests",
./scripts/generate_phase1_ria.py:190:        ("phase1_", r"phase1_"),
./scripts/generate_phase1_ria.py:215:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./scripts/generate_phase1_ria.py:235:        help="Output path for the report (default: artifacts/reports/PHASE1_CPP_RIA_YYYY-MM-DD.md)",
./scripts/generate_phase1_ria.py:241:        REPO_ROOT / "artifacts" / "reports" / f"PHASE1_CPP_RIA_{today}.md"
./scripts/generate_phase1_ria.py:245:    records = _collect_phase1_files()
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:74:**File**: `tests/test_phase1_circuit_breaker.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/IRRIGATION_SYNCHRONIZER_JOIN_TABLE_INTEGRATION.md:388:    preprocessed = run_phase1_spc_ingestion(pdf_path)
./all_py_files.txt:38:./implement_phase1_subgroup_a.py
./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./all_py_files.txt:417:./tests/test_phase1_circuit_breaker.py
./all_py_files.txt:418:./tests/test_phase1_complete.py
./all_py_files.txt:419:./tests/test_phase1_severe.py
./all_py_files.txt:420:./tests/test_phase1_signal_enrichment.py
./all_py_files.txt:421:./tests/test_phase1_type_integration.py
./all_py_files.txt:422:./tests/test_phase1_type_structure.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:56:# In phase1_spc_ingestion_full.py lines 115-133
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:231:| "ERROR: Dependencia faltante. Ejecute: pip install networkx" | Missing numpy/scipy/networkx/etc | Pre-validate with `phase1_pre_import_validator.py` |
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:241:The previous approach (phase1_method_guards.py) was **fundamentally wrong** because:
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:455:def test_phase1_fails_without_derek_beach():
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:459:        import_phase1_module()
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:518:**Solution**: Update `phase1_pre_import_validator.py` with any new dependencies found in `derek_beach.py` or `teoria_cambio.py`
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE1_TYPE_INTEGRATION.md:89:**Location**: `_execute_sp4_segmentation()` in `phase1_spc_ingestion_full.py`
./docs/PHASE1_TYPE_INTEGRATION.md:115:**Location**: `_construct_cpp_with_verification()` in `phase1_spc_ingestion_full.py`
./docs/PHASE1_TYPE_INTEGRATION.md:209:**File**: `tests/test_phase1_type_structure.py`
./docs/PHASE1_TYPE_INTEGRATION.md:212:$ python tests/test_phase1_type_structure.py
./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./docs/PHASE1_TYPE_INTEGRATION.md:312:- **Tests**: `tests/test_phase1_type_structure.py`
./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./docs/design/canonic_full_descrioption_FARFAN.md:43:    Adapter → Fase 2, con contratos en `phase0_input_validation.py`, `phase1_spc_ingestion.py`,
./docs/design/canonic_full_descrioption_FARFAN.md:44:    `phase1_to_phase2_adapter/`).
./PHASE_1_COMPREHENSIVE_AUDIT.md:7:**File**: `phase1_spc_ingestion_full.py` (1,969 lines, 32 methods)
./PHASE_1_COMPREHENSIVE_AUDIT.md:619:- ✅ `SmartChunk` model (phase1_models.py)
./PHASE_1_COMPREHENSIVE_AUDIT.md:1249:grep -i "stub\|placeholder\|mock\|TODO\|FIXME\|XXX\|HACK" phase1_spc_ingestion_full.py
./PHASE_1_COMPREHENSIVE_AUDIT.md:1427:def test_phase1_full_execution():
./PHASE_1_COMPREHENSIVE_AUDIT.md:1499:- `phase1_spc_ingestion_full.py`: 1,969 lines
./PHASE_1_COMPREHENSIVE_AUDIT.md:1500:- `phase1_models.py`: ~500 lines (estimated)
./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./PHASE1_WIRING_DOCUMENTATION.md:632:PYTHONPATH=src python3 -m pytest tests/test_phase1_wiring.py -v
./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./docs/design/ARCHITECTURE.md:180:**Implementación**: `src/farfan_core/core/phases/phase1_spc_ingestion_full.py`
./docs/design/ARCHITECTURE.md:263:# - Error report JSON (phase1_error_manifest.json)
./docs/design/ARCHITECTURE.md:282:from farfan_core.core.phases.phase1_spc_ingestion_full import (
./docs/design/ARCHITECTURE.md:295:**Tests**: `tests/test_phase1_full.py` (3 tests, 100% passing)
./src/farfan_pipeline/phases/Phase_two/executor_chunk_synchronizer.py:94:        chunk_source: Source of chunk data (typically "phase1_spc_ingestion")
./src/farfan_pipeline/phases/Phase_two/executor_chunk_synchronizer.py:279:            chunk_source="phase1_spc_ingestion",
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2623:            'phase1_version': 'CPP-2025.1',
./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:212:[ERR-004] | MANIFEST | DEBE generarse phase1_error_manifest.json en caso de error fatal | verify archivo existe en filesystem | WARNING: Auditoría comprometida
./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:407:        metadata={'source': 'phase1_spc_ingestion', 'cpp_schema': cpp.schema_version}
./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:452:8. **ERROR MANIFEST**: En caso de error fatal, SIEMPRE generar `phase1_error_manifest.json`:
./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:27:phase1_spc_ingestion:
./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:31:phase1_to_phase2_adapter:
./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:341:def validate_phase1_dependencies() -> bool:
./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:352:def generate_fix_script(output_path: str = "fix_phase1_dependencies.sh") -> None:
./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:376:        default="fix_phase1_dependencies.sh",
./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:385:        success = validate_phase1_dependencies()
./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2666:            'phase1_version': 'SPC-2025.1',
./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py:352:            test_file = Path('.phase1_write_test')
./src/farfan_pipeline/orchestration/factory.py:144:PHASE1_VALIDATION_CONSTANTS: dict[str, Any] = {}
./src/farfan_pipeline/orchestration/factory.py:149:    return PHASE1_VALIDATION_CONSTANTS
./src/farfan_pipeline/orchestration/factory.py:998:                    else PHASE1_VALIDATION_CONSTANTS
./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1fa2339b948eaf5e7 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:11:| `phase1_documentation` | `artifacts/reports/PHASE1_CERTIFICATION.md` | 5819 | `dfdf5c422b46a6f7d53694f44c86f543f3d66b68a7221948a281f5861ce2f9ea` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:12:| `phase1_documentation` | `artifacts/reports/PHASE_1_AUDIT_SUMMARY.md` | 9948 | `e7ad676d7dd54ee47013c537c1c6a45150c04767380846305c21a00c91f522e7` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:13:| `phase1_documentation` | `docs/PHASE_1_CIRCUIT_BREAKER.md` | 11498 | `59e96cff3c41818b6ce233c4ed30f09b4b947dc8fd5f69637b5c0aaf5717cfc0` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:14:| `phase1_documentation` | `requirements-phase1.txt` | 848 | `7597b60a6367249b80fcc2ad9a17543b74dea7dac3efbfeaeb0ea1a59024a7e3` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:15:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/FORCING ROUTE` | 39460 | `c3dd70cb710d3502b7dc3a97914a2f2fe5be6693ea45d42aa63d82c09a8ddd47` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:16:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/__init__.py` | 2667 | `1bde976674e576ef0e738199c839980631f86efce6b43502ab1b5f0d861af384` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:17:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/cpp_models.py` | 18365 | `cc9ea621b469e235a984944839350d25a2b83ac5e824da2f5fd436780ee885f3` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:18:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py` | 18122 | `1768ff2d6c837663050d85fd4aa6a5f41c0db1dcac25e965ce3202851f95ffdd` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:19:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py` | 19818 | `cf27b26b9c268f36de33c185c2862f62ae4a9a325f8b44dece4f9f59e068e502` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:20:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py` | 136094 | `5d42c75032ba54f5489f6410d37afd46568bf53b814b474354d5e5bcd5743a73` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:21:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py` | 13805 | `9bbb94590ddfc5aa1af7700e49b28b5006adffdf9dd5df47a4fcec3de0ed1ac2` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:22:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_models.py` | 11942 | `52f2ff6f836d5864742e7322c25941a006e666a04b05896674c43ac6b15f8d43` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:23:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py` | 8326 | `ef7c5f82d83e80522b8672475e68827763a9dfa4be5d8edc59297ccaeb2729e1` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:24:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py` | 137866 | `ff4ff2fd647a472329d2a83f3a6ce2a1e6f8c166f260cf83fe574cfcb042ad99` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:25:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/phase_protocol.py` | 12623 | `8e5f4bcf4cc78a303334d535631e029e0dc6fceebf158c9875826cb0ccfeaaac` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:26:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/signal_enrichment.py` | 22493 | `79188cb275c98c1d9faaaad65dceb69e063b06fad0d7761761ff23c980ecf0be` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:27:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/structural.py` | 3387 | `1e2d09c85c394420ace79c130f2ae2e8c9cc764e8f7e71cf34b3cff096e665b8` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:28:| `phase1_tests` | `tests/test_model_output_verification.py` | 22455 | `2a62c235edee3d9e637c4d941628c83b24e1964c96aa393c4e403c81808ffe35` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:29:| `phase1_tests` | `tests/test_phase0_complete.py` | 26279 | `0bc5c89cc4ef1c86395adddc7e1404ae74619ab8b4b399e04e58d9cd46bd8666` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:30:| `phase1_tests` | `tests/test_phase1_circuit_breaker.py` | 11095 | `45f328fe4a01948ec353629c63442557feca86613b9ea3f768dc659da108fa27` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:31:| `phase1_tests` | `tests/test_phase1_complete.py` | 12209 | `c4ab1d7e4c7d25dac162abd11fd3658ec9ad7740153f54f7a7c62641dee909b7` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:32:| `phase1_tests` | `tests/test_phase1_severe.py` | 41187 | `1cb455859304a452fb37dbc8bad9caea68b1f439a2fde52c520d55f1e3f42833` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:33:| `phase1_tests` | `tests/test_phase1_signal_enrichment.py` | 14250 | `a896d5eb93bf21c531676ff1824776b051dd272ba32b04ca58a9bf16e275b424` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:34:| `phase1_tests` | `tests/test_phase1_type_integration.py` | 14034 | `2e13b21e7034f344ef4bde31c1606b7d9158c4fe33b4b09e334f539814633b6e` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:35:| `phase1_tests` | `tests/test_phase1_type_structure.py` | 11452 | `a58271386aba0dcdbfed02be9e54f00a3f0f314201f19972c0289b1ca1a57d54` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:46:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:47:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:49:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:50:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:51:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:54:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:57:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:59:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:62:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:64:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:65:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:66:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:67:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:68:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:69:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:70:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:71:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:72:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:73:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:74:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:75:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:76:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:77:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:78:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:79:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:80:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:81:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:82:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:83:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:84:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:85:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:86:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:87:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:88:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:90:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:91:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:92:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:93:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:94:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:97:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:99:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:100:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:102:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:103:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:104:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:106:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:107:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:108:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:109:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:110:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:111:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:112:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:113:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:114:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:115:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:116:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:120:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:121:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:123:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:124:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:125:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:126:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:127:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:128:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:130:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:140:./artifacts/reports/PHASE1_CERTIFICATION.md:19:- ✓ src/canonic_phases/Phase_one/__init__.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:141:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:142:./artifacts/reports/PHASE1_CERTIFICATION.md:161:3. Import and use: `from canonic_phases.Phase_one import Phase1SPCIngestionFullContract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:146:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:149:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:151:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:157:./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:158:./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:159:./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:160:./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:161:./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:162:./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:166:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:167:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:174:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:175:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:176:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:177:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:178:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:179:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:180:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:181:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:182:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:183:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:187:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:189:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:192:./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:195:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:197:./tests/test_phase1_signal_enrichment.py:17:from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:198:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:200:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:201:./tests/test_phase1_type_structure.py:74:    cpp_models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:202:./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:203:./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:204:./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:205:./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:206:./tests/test_phase1_severe.py:30:from canonic_phases.Phase_one.phase0_input_validation import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:207:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:208:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:209:./tests/test_phase1_severe.py:53:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:210:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:211:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:212:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:213:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:214:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:215:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:218:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:220:./tests/test_phase1_complete.py:39:        'src/canonic_phases/Phase_one/__init__.py',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:221:./tests/test_phase1_complete.py:69:        ('canonic_phases.Phase_one.phase_protocol', 'Phase Protocol'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:222:./tests/test_phase1_complete.py:70:        ('canonic_phases.Phase_one.phase0_input_validation', 'Phase 0 Input Validation'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:223:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:224:./tests/test_phase1_complete.py:72:        ('canonic_phases.Phase_one.cpp_models', 'CPP Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:225:./tests/test_phase1_complete.py:73:        ('canonic_phases.Phase_one.structural', 'Structural Normalizer'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:226:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:227:./tests/test_phase1_complete.py:75:        ('canonic_phases.Phase_one', 'Phase One Package'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:228:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:229:./tests/test_phase1_complete.py:192:    from canonic_phases.Phase_one.phase0_input_validation import Phase0InputValidator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:230:./scripts/generate_phase1_ria.py:28:    REPO_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_one"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:231:./scripts/generate_phase1_ria.py:132:        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:232:./scripts/generate_phase1_ria.py:184:        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:233:./scripts/generate_phase1_ria.py:185:        ("Phase_one", r"\bPhase_one\b"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:234:./scripts/generate_phase1_ria.py:211:        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:235:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:236:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:237:./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:238:./tests/test_phase1_type_integration.py:161:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:239:./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:240:./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:252:./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:253:./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:254:./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:255:./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:256:./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:257:./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:260:./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:267:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:268:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:269:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:270:./PHASE1_WIRING_DOCUMENTATION.md:233:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:271:./PHASE1_WIRING_DOCUMENTATION.md:317:    from canonic_phases.Phase_one import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:272:./PHASE1_WIRING_DOCUMENTATION.md:368:- `src/canonic_phases/Phase_one/phase0_input_validation.py` - Contratos
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:273:./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:274:./PHASE1_WIRING_DOCUMENTATION.md:370:- `src/canonic_phases/Phase_one/cpp_models.py` - Modelos de output
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:275:./PHASE1_WIRING_DOCUMENTATION.md:563:- ✅ Import correcto: `from canonic_phases.Phase_one import ...`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:276:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:277:./PHASE1_WIRING_DOCUMENTATION.md:665:- **Phase 1**: `src/canonic_phases/Phase_one/`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:278:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:279:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:280:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:281:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:282:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:283:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:284:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:285:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:286:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:287:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:288:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:289:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:290:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:291:./docs/PHASE1_TYPE_INTEGRATION.md:41:- `src/canonic_phases/Phase_one/cpp_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:292:./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:293:./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:294:./docs/PHASE1_TYPE_INTEGRATION.md:309:- **CPP Models**: `src/canonic_phases/Phase_one/cpp_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:295:./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:296:./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:297:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:299:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:300:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:303:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:304:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:305:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:306:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:307:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:308:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:309:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:310:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:314:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:315:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:318:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:69:from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:319:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:320:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:77:from canonic_phases.Phase_one.cpp_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:321:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:322:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:190:    from canonic_phases.Phase_one.signal_enrichment import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:323:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:207:    from canonic_phases.Phase_one.structural import StructuralNormalizer
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:325:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:333:./scripts/generate_phase1_ria.py:186:        ("phase_1_cpp_ingestion", r"phase_1_cpp_ingestion"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:334:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:441:            'phase': 'PHASE_1_CPP_INGESTION',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:337:### phase1_
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:342:./src/farfan_pipeline.egg-info/SOURCES.txt:141:src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:343:./src/farfan_pipeline.egg-info/SOURCES.txt:142:src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:344:./src/farfan_pipeline.egg-info/SOURCES.txt:143:src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:345:./src/farfan_pipeline.egg-info/SOURCES.txt:144:src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:346:./src/farfan_pipeline.egg-info/SOURCES.txt:145:src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:347:./src/farfan_pipeline.egg-info/SOURCES.txt:146:src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:348:./src/farfan_pipeline.egg-info/SOURCES.txt:233:tests/test_phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:349:./src/farfan_pipeline.egg-info/SOURCES.txt:234:tests/test_phase1_complete.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:350:./src/farfan_pipeline.egg-info/SOURCES.txt:235:tests/test_phase1_severe.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:351:./src/farfan_pipeline.egg-info/SOURCES.txt:236:tests/test_phase1_signal_enrichment.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:352:./src/farfan_pipeline.egg-info/SOURCES.txt:237:tests/test_phase1_type_integration.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:353:./src/farfan_pipeline.egg-info/SOURCES.txt:238:tests/test_phase1_type_structure.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:354:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:15:- `phase1_method_guards.py` - Wrappers with try-catch and fallbacks
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:355:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:16:- `test_phase1_method_guards.py` - Tests for wrappers
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:356:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:17:- `PHASE1_METHOD_HARDENING.md` - Documentation
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:357:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:61:Created `phase1_pre_import_validator.py`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:358:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:109:src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:359:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:149:- `src/canonic_phases/Phase_one/phase1_pre_import_validator.py` - Pre-validates deps
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:360:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:150:- `src/canonic_phases/Phase_one/phase1_dependency_validator.py` - Comprehensive validator
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:361:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:151:- `docs/PHASE1_DEPENDENCY_MANAGEMENT.md` - Documents correct approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:362:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:154:- `src/canonic_phases/Phase_one/phase1_method_guards.py` - Wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:363:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:155:- `tests/test_phase1_method_guards.py` - Tests for wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:364:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:156:- `docs/PHASE1_METHOD_HARDENING.md` - Documented wrong approach
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:365:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:166:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:366:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:180:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:367:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:184:python3 src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:368:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:190:# phase1_spc_ingestion_full.py (to be integrated)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:369:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:192:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:370:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:197:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:371:./PHASE1_DEPENDENCY_FIX_SUMMARY.md:260:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:372:./artifacts/reports/PHASE1_CERTIFICATION.md:102:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:373:./artifacts/reports/PHASE1_CERTIFICATION.md:105:grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:374:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:165:| `canonic_phases.Phase_one.phase1_models` | ✅ | Clean imports |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:375:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:168:| `canonic_phases.Phase_one.phase1_spc_ingestion_full` | ✅ | Multiple optional dependencies |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:376:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:257:   from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:377:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:258:   grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:378:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1132:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:379:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1147:    from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:380:./SIGNAL_OPTIMIZATION_SUMMARY.md:31:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` (+250 lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:381:./SIGNAL_OPTIMIZATION_SUMMARY.md:46:**File**: `tests/test_phase1_signal_enrichment.py` (400+ lines)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:382:./CANONICAL_REFACTORING_PHASE2_POLICY_PROCESSOR.md:297:- Phase 1: `CANONICAL_REFACTORING_PHASE1_COMPLETE.md`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:383:./implement_phase1_subgroup_a.py:290:    report_path = Path("artifacts/cqvr_reports/batch4_Q076_Q100/SUBGROUP_A_PHASE1_REPORT.json")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:384:./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:212:    chunk_source: str               # "phase1_spc_ingestion"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:385:./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:312:            chunk_source="phase1_spc_ingestion",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:386:./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:442:        "chunk_source": "phase1_spc_ingestion",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:387:./EXECUTOR_CHUNK_SYNCHRONIZATION_ASSESSMENT.md:800:    chunks_deliverable = run_phase1_spc_ingestion(test_document)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:388:./tests/test_phase1_type_structure.py:110:def test_phase1_models_imports_types():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:389:./tests/test_phase1_type_structure.py:111:    """Test that phase1_models.py imports canonical types"""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:390:./tests/test_phase1_type_structure.py:116:    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:391:./tests/test_phase1_type_structure.py:119:        print(f"  ✗ phase1_models.py NOT found")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:392:./tests/test_phase1_type_structure.py:156:def test_phase1_ingestion_uses_enums():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:393:./tests/test_phase1_type_structure.py:157:    """Test that phase1_spc_ingestion_full.py uses enum types"""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:394:./tests/test_phase1_type_structure.py:162:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:395:./tests/test_phase1_type_structure.py:165:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:396:./tests/test_phase1_type_structure.py:216:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:397:./tests/test_phase1_type_structure.py:219:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:398:./tests/test_phase1_type_structure.py:262:    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:399:./tests/test_phase1_type_structure.py:265:        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:400:./tests/test_phase1_type_structure.py:310:        test_phase1_models_imports_types,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:401:./tests/test_phase1_type_structure.py:311:        test_phase1_ingestion_uses_enums,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:402:./tests/test_model_output_verification.py:32:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:403:./tests/phase2_contracts/test_severe_interpreter.py:1254:            "phase1_complete",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:404:./all_py_files.txt:38:./implement_phase1_subgroup_a.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:405:./all_py_files.txt:251:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:406:./all_py_files.txt:252:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:407:./all_py_files.txt:253:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:408:./all_py_files.txt:254:./src/farfan_pipeline/phases/Phase_one/phase1_models.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:409:./all_py_files.txt:255:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:410:./all_py_files.txt:256:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:411:./all_py_files.txt:417:./tests/test_phase1_circuit_breaker.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:412:./all_py_files.txt:418:./tests/test_phase1_complete.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:413:./all_py_files.txt:419:./tests/test_phase1_severe.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:414:./all_py_files.txt:420:./tests/test_phase1_signal_enrichment.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:415:./all_py_files.txt:421:./tests/test_phase1_type_integration.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:416:./all_py_files.txt:422:./tests/test_phase1_type_structure.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:417:./CONTRACT_UPDATE_PHASE1_VALIDATION.md:196:- `CONTRACT_UPDATE_PHASE1_VALIDATION.md`: This document
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:418:./tests/test_metrics_persistence_integration.py:47:    phase1_instr = PhaseInstrumentation(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:419:./tests/test_metrics_persistence_integration.py:53:    phase1_instr.start()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:420:./tests/test_metrics_persistence_integration.py:54:    phase1_instr.increment(latency=0.456)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:421:./tests/test_metrics_persistence_integration.py:55:    phase1_instr.complete()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:422:./tests/test_metrics_persistence_integration.py:63:                "1": phase1_instr.build_metrics()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:423:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:156:- **File Modified**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:424:./PHASE_1_CONTRACT_REVIEW_SUMMARY.md:194:- Modified code: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:425:./tests/test_executor_chunk_synchronization.py:97:        chunk_source="phase1_spc_ingestion"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:426:./tests/test_phase1_type_integration.py:48:def test_phase1_models_have_enum_fields():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:427:./tests/test_phase1_type_integration.py:55:        # Import phase1_models using standard import
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:428:./tests/test_phase1_type_integration.py:56:        from canonic_phases.Phase_one import phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:429:./tests/test_phase1_type_integration.py:57:        Chunk = phase1_models.Chunk
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:430:./tests/test_phase1_type_integration.py:58:        SmartChunk = phase1_models.SmartChunk
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:431:./tests/test_phase1_type_integration.py:59:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:432:./tests/test_phase1_type_integration.py:99:            "phase1_models",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:433:./tests/test_phase1_type_integration.py:100:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:434:./tests/test_phase1_type_integration.py:102:        phase1_models = importlib.util.module_from_spec(spec)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:435:./tests/test_phase1_type_integration.py:103:        sys.modules['phase1_models_test2'] = phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:436:./tests/test_phase1_type_integration.py:104:        spec.loader.exec_module(phase1_models)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:437:./tests/test_phase1_type_integration.py:106:        SmartChunk = phase1_models.SmartChunk
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:438:./tests/test_phase1_type_integration.py:107:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:439:./tests/test_phase1_type_integration.py:201:            "phase1_models",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:440:./tests/test_phase1_type_integration.py:202:            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:441:./tests/test_phase1_type_integration.py:204:        phase1_models = importlib.util.module_from_spec(spec)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:442:./tests/test_phase1_type_integration.py:205:        sys.modules['phase1_models_test3'] = phase1_models
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:443:./tests/test_phase1_type_integration.py:206:        spec.loader.exec_module(phase1_models)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:444:./tests/test_phase1_type_integration.py:208:        SmartChunk = phase1_models.SmartChunk
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:445:./tests/test_phase1_type_integration.py:209:        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:446:./tests/test_phase1_type_integration.py:297:        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:447:./tests/test_phase1_type_integration.py:298:        source = phase1_file.read_text()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:448:./tests/test_phase1_type_integration.py:324:        test_phase1_models_have_enum_fields,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:449:./tests/test_phase1_signal_enrichment.py:24:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:450:./tests/test_phase1_circuit_breaker.py:20:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:451:./tests/test_phase1_severe.py:35:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:452:./tests/test_phase1_severe.py:42:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:453:./tests/test_phase1_severe.py:577:        from canonic_phases.Phase_one.phase1_models import CausalChains
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:454:./tests/test_phase1_severe.py:595:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:455:./tests/test_phase1_severe.py:614:        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:456:./tests/test_phase1_severe.py:633:        from canonic_phases.Phase_one.phase1_models import Arguments
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:457:./tests/test_phase1_severe.py:651:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:458:./tests/test_phase1_severe.py:720:        from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:459:./DEPENDENCIES.md:121:from canonic_phases.Phase_one import phase1_spc_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:460:./DEPENDENCIES.md:124:grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:461:./audit_signal_irrigation_blockers_report.json:61:          "phase1_spc_ingestion_full.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:462:./audit_signal_irrigation_blockers_report.json:65:          "phase1_spc_ingestion_full.py",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:463:./scripts/generate_phase1_ria.py:10:  python scripts/generate_phase1_ria.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:464:./scripts/generate_phase1_ria.py:27:PHASE1_IMPL_DIR = (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:465:./scripts/generate_phase1_ria.py:71:def _collect_phase1_files() -> list[FileRecord]:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:466:./scripts/generate_phase1_ria.py:74:    if PHASE1_IMPL_DIR.exists():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:467:./scripts/generate_phase1_ria.py:75:        for p in sorted(PHASE1_IMPL_DIR.rglob("*")):
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:468:./scripts/generate_phase1_ria.py:83:                    category="phase1_implementation",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:469:./scripts/generate_phase1_ria.py:94:                    category="phase1_documentation",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:470:./scripts/generate_phase1_ria.py:108:                        category="phase1_documentation",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:471:./scripts/generate_phase1_ria.py:120:                    category="phase1_tests",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:472:./scripts/generate_phase1_ria.py:138:                    category="phase1_tests",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:473:./scripts/generate_phase1_ria.py:187:        ("phase1_", r"phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:474:./scripts/generate_phase1_ria.py:212:        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:475:./scripts/generate_phase1_ria.py:232:        help="Output path for the report (default: artifacts/reports/PHASE1_CPP_RIA_YYYY-MM-DD.md)",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:476:./scripts/generate_phase1_ria.py:238:        REPO_ROOT / "artifacts" / "reports" / f"PHASE1_CPP_RIA_{today}.md"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:477:./scripts/generate_phase1_ria.py:242:    records = _collect_phase1_files()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:478:./tests/test_phase1_complete.py:71:        ('canonic_phases.Phase_one.phase1_models', 'Phase 1 Models'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:479:./tests/test_phase1_complete.py:74:        ('canonic_phases.Phase_one.phase1_cpp_ingestion_full', 'Phase 1 CPP Ingestion'),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:480:./tests/test_phase1_complete.py:99:    from canonic_phases.Phase_one import phase1_cpp_ingestion_full
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:481:./tests/test_phase1_complete.py:101:    grid_spec = phase1_cpp_ingestion_full.PADimGridSpecification
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:482:./docs/DETERMINISM.md:185:    "phase1_chunking": get_derived_seed(42, "phase1_semantic_chunking"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:483:./docs/DETERMINISM.md:585:      "phase1_chunking": 3456789012,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:484:./docs/PHASE_1_SIGNAL_ENRICHMENT.md:424:- Phase 1 Implementation: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:485:./docs/VALIDATION_GUIDE.md:138:    ops = ["phase0", "phase1_chunking", "phase2_D1_Q1", "phase3_scoring"]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:486:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:52:**File**: `src/canonic_phases/Phase_one/phase1_circuit_breaker.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:487:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:74:**File**: `tests/test_phase1_circuit_breaker.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:488:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:114:**File**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:489:./docs/PHASE_1_ROBUSTNESS_COMPLETE.md:119:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:490:./docs/IRRIGATION_SYNCHRONIZER_JOIN_TABLE_INTEGRATION.md:388:    preprocessed = run_phase1_spc_ingestion(pdf_path)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:491:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:56:# In phase1_spc_ingestion_full.py lines 115-133
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:492:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:101:**Created**: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:493:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:146:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:494:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:153:    logger.error("Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:495:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:168:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:496:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:218:$ python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:497:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:231:| "ERROR: Dependencia faltante. Ejecute: pip install networkx" | Missing numpy/scipy/networkx/etc | Pre-validate with `phase1_pre_import_validator.py` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:498:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:241:The previous approach (phase1_method_guards.py) was **fundamentally wrong** because:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:499:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:288:from canonic_phases.Phase_one.phase1_pre_import_validator import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:500:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:318:In `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:501:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:337:from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:502:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:342:        "Run: python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py"
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:503:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:400:    python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:504:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:455:def test_phase1_fails_without_derek_beach():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:505:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:459:        import_phase1_module()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:506:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:489:python3 src/canonic_phases/Phase_one/phase1_pre_import_validator.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:507:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:518:**Solution**: Update `phase1_pre_import_validator.py` with any new dependencies found in `derek_beach.py` or `teoria_cambio.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:508:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:529:- Phase 1 SPC Ingestion: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:509:./docs/PHASE1_DEPENDENCY_MANAGEMENT.md:530:- Pre-Import Validator: `src/canonic_phases/Phase_one/phase1_pre_import_validator.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:510:./docs/PHASE1_TYPE_INTEGRATION.md:42:- `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:511:./docs/PHASE1_TYPE_INTEGRATION.md:43:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:512:./docs/PHASE1_TYPE_INTEGRATION.md:89:**Location**: `_execute_sp4_segmentation()` in `phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:513:./docs/PHASE1_TYPE_INTEGRATION.md:115:**Location**: `_construct_cpp_with_verification()` in `phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:514:./docs/PHASE1_TYPE_INTEGRATION.md:209:**File**: `tests/test_phase1_type_structure.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:515:./docs/PHASE1_TYPE_INTEGRATION.md:212:$ python tests/test_phase1_type_structure.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:516:./docs/PHASE1_TYPE_INTEGRATION.md:310:- **Phase 1 Models**: `src/canonic_phases/Phase_one/phase1_models.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:517:./docs/PHASE1_TYPE_INTEGRATION.md:311:- **Phase 1 Ingestion**: `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:518:./docs/PHASE1_TYPE_INTEGRATION.md:312:- **Tests**: `tests/test_phase1_type_structure.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:519:./docs/PHASE_1_CIRCUIT_BREAKER.md:110:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:520:./docs/PHASE_1_CIRCUIT_BREAKER.md:122:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:521:./docs/PHASE_1_CIRCUIT_BREAKER.md:145:from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:522:./docs/design/canonic_full_descrioption_FARFAN.md:43:    Adapter → Fase 2, con contratos en `phase0_input_validation.py`, `phase1_spc_ingestion.py`,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:523:./docs/design/canonic_full_descrioption_FARFAN.md:44:    `phase1_to_phase2_adapter/`).
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:524:./PHASE_1_COMPREHENSIVE_AUDIT.md:7:**File**: `phase1_spc_ingestion_full.py` (1,969 lines, 32 methods)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:525:./PHASE_1_COMPREHENSIVE_AUDIT.md:619:- ✅ `SmartChunk` model (phase1_models.py)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:526:./PHASE_1_COMPREHENSIVE_AUDIT.md:1249:grep -i "stub\|placeholder\|mock\|TODO\|FIXME\|XXX\|HACK" phase1_spc_ingestion_full.py
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:527:./PHASE_1_COMPREHENSIVE_AUDIT.md:1427:def test_phase1_full_execution():
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:528:./PHASE_1_COMPREHENSIVE_AUDIT.md:1499:- `phase1_spc_ingestion_full.py`: 1,969 lines
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:529:./PHASE_1_COMPREHENSIVE_AUDIT.md:1500:- `phase1_models.py`: ~500 lines (estimated)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:530:./PHASE1_WIRING_DOCUMENTATION.md:369:- `src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py` - Ejecución
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:531:./PHASE1_WIRING_DOCUMENTATION.md:632:PYTHONPATH=src python3 -m pytest tests/test_phase1_wiring.py -v
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:532:./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:533:./docs/design/ARCHITECTURE.md:180:**Implementación**: `src/farfan_core/core/phases/phase1_spc_ingestion_full.py`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:534:./docs/design/ARCHITECTURE.md:263:# - Error report JSON (phase1_error_manifest.json)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:535:./docs/design/ARCHITECTURE.md:282:from farfan_core.core.phases.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:536:./docs/design/ARCHITECTURE.md:295:**Tests**: `tests/test_phase1_full.py` (3 tests, 100% passing)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:537:./src/farfan_pipeline/orchestration/factory.py:144:PHASE1_VALIDATION_CONSTANTS: dict[str, Any] = {}
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:538:./src/farfan_pipeline/orchestration/factory.py:149:    return PHASE1_VALIDATION_CONSTANTS
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:539:./src/farfan_pipeline/orchestration/factory.py:998:                    else PHASE1_VALIDATION_CONSTANTS
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:540:./src/farfan_pipeline/phases/Phase_two/executor_chunk_synchronizer.py:94:        chunk_source: Source of chunk data (typically "phase1_spc_ingestion")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:541:./src/farfan_pipeline/phases/Phase_two/executor_chunk_synchronizer.py:279:            chunk_source="phase1_spc_ingestion",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:542:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:543:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:544:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:545:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2623:            'phase1_version': 'CPP-2025.1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:546:./src/farfan_pipeline/phases/Phase_zero/main.py:724:            from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:547:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:212:[ERR-004] | MANIFEST | DEBE generarse phase1_error_manifest.json en caso de error fatal | verify archivo existe en filesystem | WARNING: Audito [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:548:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:407:        metadata={'source': 'phase1_spc_ingestion', 'cpp_schema': cpp.schema_version}
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:549:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:452:8. **ERROR MANIFEST**: En caso de error fatal, SIEMPRE generar `phase1_error_manifest.json`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:550:./src/farfan_pipeline/phases/Phase_one/phase1_pre_import_validator.py:180:        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:551:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:27:phase1_spc_ingestion:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:552:./src/farfan_pipeline/phases/Phase_one/phase_protocol.py:31:phase1_to_phase2_adapter:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:553:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:341:def validate_phase1_dependencies() -> bool:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:554:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:352:def generate_fix_script(output_path: str = "fix_phase1_dependencies.sh") -> None:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:555:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:376:        default="fix_phase1_dependencies.sh",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:556:./src/farfan_pipeline/phases/Phase_one/phase1_dependency_validator.py:385:        success = validate_phase1_dependencies()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:557:./src/farfan_pipeline/phases/Phase_one/__init__.py:39:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:558:./src/farfan_pipeline/phases/Phase_one/__init__.py:53:from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:559:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:70:from canonic_phases.Phase_one.phase1_models import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:560:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:90:from canonic_phases.Phase_one.phase1_circuit_breaker import (
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:561:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:458:            with open('phase1_error_manifest.json', 'w') as f:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:562:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2666:            'phase1_version': 'SPC-2025.1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:563:./src/farfan_pipeline/phases/Phase_one/phase1_circuit_breaker.py:352:            test_file = Path('.phase1_write_test')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:564:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:591:./artifacts/reports/PHASE1_CERTIFICATION.md:8:Phase 1 of the F.A.R.F.A.N pipeline has been **FULLY VALIDATED** and is **READY FOR IMPLEMENTATION**. All FORCING ROUTE constitutional invariants are met, [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:592:./artifacts/reports/PHASE1_CERTIFICATION.md:41:### ✅ 3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE] - PASSED
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:593:./artifacts/reports/PHASE1_CERTIFICATION.md:43:All constitutional invariants from FORCING ROUTE document are verified:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:594:./artifacts/reports/PHASE1_CERTIFICATION.md:68:- ✓ FORCING ROUTE error codes present ([PRE-002], [PRE-003])
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:595:./artifacts/reports/PHASE1_CERTIFICATION.md:124:- [x] FORCING ROUTE requirements met
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:596:./artifacts/reports/PHASE1_CERTIFICATION.md:143:All critical requirements from the FORCING ROUTE document are met:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:597:./artifacts/reports/PHASE1_CERTIFICATION.md:162:4. Follow FORCING ROUTE specifications for execution
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:598:./artifacts/reports/PHASE1_CERTIFICATION.md:165:Phase 1 is production-ready with zero tolerance for contract violations and full adherence to FORCING ROUTE requirements.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:603:./tests/test_phase1_complete.py:7:It validates ALL requirements from the FORCING ROUTE document.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:604:./tests/test_phase1_complete.py:96:@test_section("3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE]")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:605:./tests/test_phase1_complete.py:98:    """Verify all FORCING ROUTE constitutional invariants"""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:606:./tests/test_phase1_complete.py:222:    # Test 4: Verify FORCING ROUTE error codes
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:607:./tests/test_phase1_complete.py:227:            print("  ✓ FORCING ROUTE error codes present ([PRE-002])")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:608:./tests/test_phase1_complete.py:229:            print(f"  ⚠ FORCING ROUTE error codes may be missing: {str(e)[:60]}")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:609:./tests/test_phase1_complete.py:320:        print("\n  All FORCING ROUTE requirements verified.")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:620:./scripts/generate_phase1_ria.py:190:        ("FORCING ROUTE", r"FORCING ROUTE"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:623:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:624:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:625:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1115:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:626:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1182:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:627:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1350:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:628:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1498:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:629:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1602:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:630:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1706:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:631:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1807:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:632:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1912:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:633:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1992:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:634:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2090:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:635:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2154:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:636:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2276:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:637:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2373:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:638:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2411:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:639:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2470:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:640:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2687:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:644:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:64:        """Alias for paragraph_mapping per FORCING ROUTE [EXEC-SP2-005]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:645:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:161:        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:646:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:174:        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:647:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:190:        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:648:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:210:        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:649:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:223:        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:650:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:241:        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:651:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:652:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:653:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1123:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:654:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1190:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:655:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1358:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:656:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1506:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:657:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1610:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:658:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1714:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:659:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1815:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:660:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1920:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:661:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2005:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:662:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2112:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:663:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2184:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:664:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2306:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:665:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2404:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:666:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2442:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:667:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2513:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:668:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2730:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:672:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:697:./scripts/generate_phase1_ria.py:210:        ("execute_phase_1_with_full_contract (all call sites)", r"execute_phase_1_with_full_contract"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:704:./PHASE1_WIRING_DOCUMENTATION.md:71:            └─ execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:705:./PHASE1_WIRING_DOCUMENTATION.md:211:   canon_package = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:706:./PHASE1_WIRING_DOCUMENTATION.md:235:        execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:707:./PHASE1_WIRING_DOCUMENTATION.md:265:    canon_package = execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:708:./PHASE1_WIRING_DOCUMENTATION.md:281:execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:709:./PHASE1_WIRING_DOCUMENTATION.md:290:execute_phase_1_with_full_contract(canonical_input, signal_registry)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:710:./PHASE1_WIRING_DOCUMENTATION.md:319:        execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:711:./PHASE1_WIRING_DOCUMENTATION.md:349:    canon_package = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:712:./PHASE1_WIRING_DOCUMENTATION.md:375:def execute_phase_1_with_full_contract(canonical_input: CanonicalInput) -> CanonPolicyPackage:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:713:./PHASE1_WIRING_DOCUMENTATION.md:517:       ├─ Llama execute_phase_1_with_full_contract()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:714:./PHASE1_WIRING_DOCUMENTATION.md:520:4. Phase 1: execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:715:./PHASE1_WIRING_DOCUMENTATION.md:566:- ✅ Llama `execute_phase_1_with_full_contract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:716:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:717:./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:722:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2757:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:725:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2800:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:728:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:739:### from canonic_phases.Phase_one\.phase1_.*
```

### importlib.import_module

hits=0

```text
(no hits)
```

### __import__(

hits=4

```text
[rg_error] rc=2 stderr=rg: regex parse error:
    (?:__import__\\()
    ^
error: unclosed group
```

### FORCING ROUTE

hits=173

```text
./artifacts/reports/PHASE1_CERTIFICATION.md:8:Phase 1 of the F.A.R.F.A.N pipeline has been **FULLY VALIDATED** and is **READY FOR IMPLEMENTATION**. All FORCING ROUTE constitutional invariants are met, all required packages are properly structured [... omitted end of long line]
./artifacts/reports/PHASE1_CERTIFICATION.md:41:### ✅ 3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE] - PASSED
./artifacts/reports/PHASE1_CERTIFICATION.md:43:All constitutional invariants from FORCING ROUTE document are verified:
./artifacts/reports/PHASE1_CERTIFICATION.md:68:- ✓ FORCING ROUTE error codes present ([PRE-002], [PRE-003])
./artifacts/reports/PHASE1_CERTIFICATION.md:124:- [x] FORCING ROUTE requirements met
./artifacts/reports/PHASE1_CERTIFICATION.md:143:All critical requirements from the FORCING ROUTE document are met:
./artifacts/reports/PHASE1_CERTIFICATION.md:162:4. Follow FORCING ROUTE specifications for execution
./artifacts/reports/PHASE1_CERTIFICATION.md:165:Phase 1 is production-ready with zero tolerance for contract violations and full adherence to FORCING ROUTE requirements.
./MODEL_OUTPUT_VERIFICATION_REPORT.md:177:paragraph_to_section -> paragraph_mapping  # ✅ Per FORCING ROUTE
./MODEL_OUTPUT_VERIFICATION_REPORT.md:516:**FORCING ROUTE Requirements**:
./DEPENDENCIES.md:8:- Deterministic execution (as per FORCING ROUTE)
./DEPENDENCIES.md:35:- Required for FORCING ROUTE compliance (deterministic execution requirement)
./DEPENDENCIES.md:44:- FORCING ROUTE [EXEC-SP1-001] through [EXEC-SP1-011]
./DEPENDENCIES.md:46:**Consequence if missing**: Cannot execute SP1 preprocessing (FORCING ROUTE FATAL)
./DEPENDENCIES.md:53:- FORCING ROUTE [EXEC-SP0-001] through [EXEC-SP0-005]
./DEPENDENCIES.md:55:**Consequence if missing**: Cannot execute SP0 language detection (FORCING ROUTE FATAL)
./DEPENDENCIES.md:62:- FORCING ROUTE [PRE-003] PDF path validation
./DEPENDENCIES.md:64:**Consequence if missing**: Cannot process PDF inputs (FORCING ROUTE FATAL)
./DEPENDENCIES.md:141:Phase 1 enforces strict constitutional invariants as defined in the FORCING ROUTE document:
./tests/test_model_output_verification.py:457:        # Verify thresholds per FORCING ROUTE
./tests/test_phase1_complete.py:7:It validates ALL requirements from the FORCING ROUTE document.
./tests/test_phase1_complete.py:96:@test_section("3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE]")
./tests/test_phase1_complete.py:98:    """Verify all FORCING ROUTE constitutional invariants"""
./tests/test_phase1_complete.py:222:    # Test 4: Verify FORCING ROUTE error codes
./tests/test_phase1_complete.py:227:            print("  ✓ FORCING ROUTE error codes present ([PRE-002])")
./tests/test_phase1_complete.py:229:            print(f"  ⚠ FORCING ROUTE error codes may be missing: {str(e)[:60]}")
./tests/test_phase1_complete.py:320:        print("\n  All FORCING ROUTE requirements verified.")
./scripts/generate_phase1_ria.py:193:        ("FORCING ROUTE", r"FORCING ROUTE"),
./requirements-phase1.txt:5:# as per the dura_lex contract system and FORCING ROUTE specification.
./docs/PHASE_1_CIRCUIT_BREAKER.md:408:- Phase 1 FORCING ROUTE specification
./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1fa2339b948eaf5e7 [... omitted end of long line]
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1115:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1182:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1350:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1498:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1602:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1706:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1807:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1912:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1992:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2090:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2154:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2276:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2373:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2411:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2470:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2687:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:81:# These tools ensure idempotency and full traceability per FORCING ROUTE
./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:155:        """Validate PDF path format with zero tolerance per FORCING ROUTE [PRE-003]."""
./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:163:        """Validate run_id format with zero tolerance per FORCING ROUTE [PRE-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:64:        """Alias for paragraph_mapping per FORCING ROUTE [EXEC-SP2-005]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:161:        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:174:        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:190:        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:210:        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:223:        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_models.py:241:        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1123:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1190:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1358:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1506:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1610:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1714:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1815:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1920:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2005:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2112:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2184:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2306:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2404:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2442:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2513:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2730:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./src/farfan_pipeline/phases/Phase_one/cpp_models.py:6:All models are frozen dataclasses per [INV-010] FORCING ROUTE requirement.
./src/farfan_pipeline/phases/Phase_one/cpp_models.py:179:    Invariants per FORCING ROUTE:
./src/farfan_pipeline/phases/Phase_one/cpp_models.py:430:    Validator for CanonPolicyPackage per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:12:This audit was conducted in accordance with the FORCING ROUTE document specifications for Phase 1 of the F.A.R.F.A.N pipeline. All constitutional invariants have been verified, package structure issue [... omitted end of long line]
./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:123:According to the FORCING ROUTE document, Phase 1 must maintain strict constitutional invariants:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:15:| `phase1_implementation` | `src/farfan_pipeline/phases/Phase_one/FORCING ROUTE` | 39460 | `c3dd70cb710d3502b7dc3a97914a2f2fe5be6693ea45d42aa63d82c09a8ddd47` |
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:88:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:325:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:547:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:212:[ERR-004] | MANIFEST | DEBE generarse phase1_error_manifest.json en caso de error fatal | verify archivo existe en filesystem | WARNING: Audito [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:548:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:407:        metadata={'source': 'phase1_spc_ingestion', 'cpp_schema': cpp.schema_version}
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:549:./src/farfan_pipeline/phases/Phase_one/FORCING ROUTE:452:8. **ERROR MANIFEST**: En caso de error fatal, SIEMPRE generar `phase1_error_manifest.json`:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:564:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:586:### FORCING ROUTE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:591:./artifacts/reports/PHASE1_CERTIFICATION.md:8:Phase 1 of the F.A.R.F.A.N pipeline has been **FULLY VALIDATED** and is **READY FOR IMPLEMENTATION**. All FORCING ROUTE constitutional invariants are met, [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:592:./artifacts/reports/PHASE1_CERTIFICATION.md:41:### ✅ 3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE] - PASSED
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:593:./artifacts/reports/PHASE1_CERTIFICATION.md:43:All constitutional invariants from FORCING ROUTE document are verified:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:594:./artifacts/reports/PHASE1_CERTIFICATION.md:68:- ✓ FORCING ROUTE error codes present ([PRE-002], [PRE-003])
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:595:./artifacts/reports/PHASE1_CERTIFICATION.md:124:- [x] FORCING ROUTE requirements met
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:596:./artifacts/reports/PHASE1_CERTIFICATION.md:143:All critical requirements from the FORCING ROUTE document are met:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:597:./artifacts/reports/PHASE1_CERTIFICATION.md:162:4. Follow FORCING ROUTE specifications for execution
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:598:./artifacts/reports/PHASE1_CERTIFICATION.md:165:Phase 1 is production-ready with zero tolerance for contract violations and full adherence to FORCING ROUTE requirements.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:599:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:12:This audit was conducted in accordance with the FORCING ROUTE document specifications for Phase 1 of the F.A.R.F.A.N pipeline. All constitutional invari [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:600:./artifacts/reports/PHASE_1_AUDIT_SUMMARY.md:123:According to the FORCING ROUTE document, Phase 1 must maintain strict constitutional invariants:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:601:./MODEL_OUTPUT_VERIFICATION_REPORT.md:177:paragraph_to_section -> paragraph_mapping  # ✅ Per FORCING ROUTE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:602:./MODEL_OUTPUT_VERIFICATION_REPORT.md:516:**FORCING ROUTE Requirements**:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:603:./tests/test_phase1_complete.py:7:It validates ALL requirements from the FORCING ROUTE document.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:604:./tests/test_phase1_complete.py:96:@test_section("3. CONSTITUTIONAL INVARIANTS [FORCING ROUTE]")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:605:./tests/test_phase1_complete.py:98:    """Verify all FORCING ROUTE constitutional invariants"""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:606:./tests/test_phase1_complete.py:222:    # Test 4: Verify FORCING ROUTE error codes
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:607:./tests/test_phase1_complete.py:227:            print("  ✓ FORCING ROUTE error codes present ([PRE-002])")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:608:./tests/test_phase1_complete.py:229:            print(f"  ⚠ FORCING ROUTE error codes may be missing: {str(e)[:60]}")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:609:./tests/test_phase1_complete.py:320:        print("\n  All FORCING ROUTE requirements verified.")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:610:./tests/test_model_output_verification.py:457:        # Verify thresholds per FORCING ROUTE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:611:./DEPENDENCIES.md:8:- Deterministic execution (as per FORCING ROUTE)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:612:./DEPENDENCIES.md:35:- Required for FORCING ROUTE compliance (deterministic execution requirement)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:613:./DEPENDENCIES.md:44:- FORCING ROUTE [EXEC-SP1-001] through [EXEC-SP1-011]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:614:./DEPENDENCIES.md:46:**Consequence if missing**: Cannot execute SP1 preprocessing (FORCING ROUTE FATAL)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:615:./DEPENDENCIES.md:53:- FORCING ROUTE [EXEC-SP0-001] through [EXEC-SP0-005]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:616:./DEPENDENCIES.md:55:**Consequence if missing**: Cannot execute SP0 language detection (FORCING ROUTE FATAL)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:617:./DEPENDENCIES.md:62:- FORCING ROUTE [PRE-003] PDF path validation
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:618:./DEPENDENCIES.md:64:**Consequence if missing**: Cannot process PDF inputs (FORCING ROUTE FATAL)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:619:./DEPENDENCIES.md:141:Phase 1 enforces strict constitutional invariants as defined in the FORCING ROUTE document:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:620:./scripts/generate_phase1_ria.py:190:        ("FORCING ROUTE", r"FORCING ROUTE"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:621:./requirements-phase1.txt:5:# as per the dura_lex contract system and FORCING ROUTE specification.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:622:./docs/PHASE_1_CIRCUIT_BREAKER.md:408:- Phase 1 FORCING ROUTE specification
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:623:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:624:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:625:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1115:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:626:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1182:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:627:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1350:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:628:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1498:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:629:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1602:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:630:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1706:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:631:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1807:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:632:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1912:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:633:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:1992:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:634:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2090:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:635:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2154:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:636:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2276:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:637:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2373:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:638:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2411:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:639:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2470:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:640:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2687:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:641:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:81:# These tools ensure idempotency and full traceability per FORCING ROUTE
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:642:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:155:        """Validate PDF path format with zero tolerance per FORCING ROUTE [PRE-003]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:643:./src/farfan_pipeline/phases/Phase_one/phase0_input_validation.py:163:        """Validate run_id format with zero tolerance per FORCING ROUTE [PRE-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:644:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:64:        """Alias for paragraph_mapping per FORCING ROUTE [EXEC-SP2-005]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:645:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:161:        """Alias per FORCING ROUTE [EXEC-SP5-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:646:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:174:        """Alias per FORCING ROUTE [EXEC-SP6-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:647:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:190:        """Alias per FORCING ROUTE [EXEC-SP7-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:648:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:210:        """Alias per FORCING ROUTE [EXEC-SP8-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:649:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:223:        """Alias per FORCING ROUTE [EXEC-SP9-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:650:./src/farfan_pipeline/phases/Phase_one/phase1_models.py:241:        """Alias per FORCING ROUTE [EXEC-SP10-002]."""
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:651:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:982:        SP0: Language Detection per FORCING ROUTE SECCIÓN 2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:652:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1041:        SP1: Advanced Preprocessing per FORCING ROUTE SECCIÓN 3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:653:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1123:        SP2: Structural Analysis per FORCING ROUTE SECCIÓN 4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:654:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1190:        SP3: Knowledge Graph Construction per FORCING ROUTE SECCIÓN 4.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:655:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1358:        SP4: Structured PA×DIM Segmentation per FORCING ROUTE SECCIÓN 5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:656:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1506:        SP5: Causal Chain Extraction per FORCING ROUTE SECCIÓN 6.1.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:657:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1610:        SP6: Integrated Causal Analysis per FORCING ROUTE SECCIÓN 6.2.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:658:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1714:        SP7: Argumentative Analysis per FORCING ROUTE SECCIÓN 6.3.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:659:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1815:        SP8: Temporal Analysis per FORCING ROUTE SECCIÓN 6.4.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:660:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:1920:        SP9: Discourse Analysis per FORCING ROUTE SECCIÓN 6.5.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:661:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2005:        SP10: Strategic Integration per FORCING ROUTE SECCIÓN 6.6.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:662:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2112:        SP11: Smart Chunk Generation per FORCING ROUTE SECCIÓN 7.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:663:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2184:        SP12: Inter-Chunk Enrichment per FORCING ROUTE SECCIÓN 8.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:664:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2306:        SP13: Integrity Validation per FORCING ROUTE SECCIÓN 11.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:665:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2404:        SP14: Deduplication per FORCING ROUTE SECCIÓN 9.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:666:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2442:        SP15: Strategic Ranking per FORCING ROUTE SECCIÓN 10.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:667:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2513:        CPP Construction per FORCING ROUTE SECCIÓN 12.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:668:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2730:        Postcondition Verification per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:669:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:6:All models are frozen dataclasses per [INV-010] FORCING ROUTE requirement.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:670:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:179:    Invariants per FORCING ROUTE:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:671:./src/farfan_pipeline/phases/Phase_one/cpp_models.py:430:    Validator for CanonPolicyPackage per FORCING ROUTE SECCIÓN 13.
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:672:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:728:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
```


## 3) Orchestrator Call Graph Evidence

### execute_phase_1_with_full_contract (all call sites)

hits=105

```text
./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1486:                execute_phase_1_with_full_contract,
./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1536:            canon_package = execute_phase_1_with_full_contract(
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1124:**Phase 1 Entry Point**: `execute_phase_1_with_full_contract()`
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1133:    execute_phase_1_with_full_contract
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1137:cpp = execute_phase_1_with_full_contract(canonical_input)
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1148:        execute_phase_1_with_full_contract,
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1161:    cpp = execute_phase_1_with_full_contract(canonical_input)
./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1188:    execute_phase_1_with_full_contract(
./PHASE_1_WEIGHT_CONTRACT_ENHANCEMENT.md:433:    cpp = execute_phase_1_with_full_contract(valid_input)
./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./scripts/generate_phase1_ria.py:213:        ("execute_phase_1_with_full_contract (all call sites)", r"execute_phase_1_with_full_contract"),
./docs/PHASE_1_CIRCUIT_BREAKER.md:111:    execute_phase_1_with_full_contract
./docs/PHASE_1_CIRCUIT_BREAKER.md:116:cpp = execute_phase_1_with_full_contract(canonical_input)
./PHASE_0_ORCHESTRATOR_WIRING_SPECIFICATION.md:72:    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
./PHASE_0_ORCHESTRATOR_WIRING_SPECIFICATION.md:478:    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
./docs/design/ARCHITECTURE.md:283:    execute_phase_1_with_full_contract
./docs/design/ARCHITECTURE.md:288:canon_package = execute_phase_1_with_full_contract(canonical_input)
./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./execute_full_pipeline.py:90:    cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
./execute_full_pipeline.py:160:    print(f"Phase 1: ✓ REAL EXECUTION (execute_phase_1_with_full_contract)")
./PHASE1_WIRING_DOCUMENTATION.md:71:            └─ execute_phase_1_with_full_contract(
./PHASE1_WIRING_DOCUMENTATION.md:211:   canon_package = execute_phase_1_with_full_contract(canonical_input)
./PHASE1_WIRING_DOCUMENTATION.md:235:        execute_phase_1_with_full_contract,
./PHASE1_WIRING_DOCUMENTATION.md:265:    canon_package = execute_phase_1_with_full_contract(
./PHASE1_WIRING_DOCUMENTATION.md:281:execute_phase_1_with_full_contract(canonical_input)
./PHASE1_WIRING_DOCUMENTATION.md:290:execute_phase_1_with_full_contract(canonical_input, signal_registry)
./PHASE1_WIRING_DOCUMENTATION.md:319:        execute_phase_1_with_full_contract,
./PHASE1_WIRING_DOCUMENTATION.md:349:    canon_package = execute_phase_1_with_full_contract(canonical_input)
./PHASE1_WIRING_DOCUMENTATION.md:375:def execute_phase_1_with_full_contract(canonical_input: CanonicalInput) -> CanonPolicyPackage:
./PHASE1_WIRING_DOCUMENTATION.md:517:       ├─ Llama execute_phase_1_with_full_contract()
./PHASE1_WIRING_DOCUMENTATION.md:520:4. Phase 1: execute_phase_1_with_full_contract(canonical_input)
./PHASE1_WIRING_DOCUMENTATION.md:566:- ✅ Llama `execute_phase_1_with_full_contract`
./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./src/farfan_pipeline/phases/Phase_zero/main.py:725:                execute_phase_1_with_full_contract,
./src/farfan_pipeline/phases/Phase_zero/main.py:738:            cpp = execute_phase_1_with_full_contract(canonical_input)
./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2757:def execute_phase_1_with_full_contract(
./backups/20251214_135858/orchestrator. py. bak:1466:                execute_phase_1_with_full_contract,
./backups/20251214_135858/orchestrator. py. bak:1522:            canon_package = execute_phase_1_with_full_contract(
./src/farfan_pipeline/phases/Phase_one/__init__.py:55:    execute_phase_1_with_full_contract,
./src/farfan_pipeline/phases/Phase_one/__init__.py:96:    "execute_phase_1_with_full_contract",
./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2800:def execute_phase_1_with_full_contract(
./src/farfan_pipeline/orchestration/orchestrator.py:2033:                execute_phase_1_with_full_contract,
./src/farfan_pipeline/orchestration/orchestrator.py:2083:            canon_package = execute_phase_1_with_full_contract(
./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1fa2339b948eaf5e7 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:88:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:89:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:101:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:109:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:216:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:242:./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:243:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:276:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:325:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:532:./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:564:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:672:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:678:### execute_phase_1_with_full_contract (all call sites)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:683:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1486:                execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:684:./src/orchestration/orchestrator.py~1738f0eae4f67a51d31bb3e035e302d789b3050f:1536:            canon_package = execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:685:./PHASE_1_WEIGHT_CONTRACT_ENHANCEMENT.md:433:    cpp = execute_phase_1_with_full_contract(valid_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:686:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1124:**Phase 1 Entry Point**: `execute_phase_1_with_full_contract()`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:687:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1133:    execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:688:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1137:cpp = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:689:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1148:        execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:690:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1161:    cpp = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:691:./PHASE_0_COMPREHENSIVE_SPECIFICATION.md:1188:    execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:692:./RUN_PIPELINE.py:5:print('Phase 1: canonic_phases.Phase_one.execute_phase_1_with_full_contract()')
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:693:./docs/PHASE_1_CIRCUIT_BREAKER.md:111:    execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:694:./docs/PHASE_1_CIRCUIT_BREAKER.md:116:cpp = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:695:./docs/design/ARCHITECTURE.md:283:    execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:696:./docs/design/ARCHITECTURE.md:288:canon_package = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:697:./scripts/generate_phase1_ria.py:210:        ("execute_phase_1_with_full_contract (all call sites)", r"execute_phase_1_with_full_contract"),
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:698:./PHASE_0_ORCHESTRATOR_WIRING_SPECIFICATION.md:72:    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:699:./PHASE_0_ORCHESTRATOR_WIRING_SPECIFICATION.md:478:    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:700:./execute_full_pipeline.py:8:- Phase 1: execute_phase_1_with_full_contract (Phase_one/)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:701:./execute_full_pipeline.py:29:from canonic_phases.Phase_one import execute_phase_1_with_full_contract, CanonicalInput
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:702:./execute_full_pipeline.py:90:    cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:703:./execute_full_pipeline.py:160:    print(f"Phase 1: ✓ REAL EXECUTION (execute_phase_1_with_full_contract)")
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:704:./PHASE1_WIRING_DOCUMENTATION.md:71:            └─ execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:705:./PHASE1_WIRING_DOCUMENTATION.md:211:   canon_package = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:706:./PHASE1_WIRING_DOCUMENTATION.md:235:        execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:707:./PHASE1_WIRING_DOCUMENTATION.md:265:    canon_package = execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:708:./PHASE1_WIRING_DOCUMENTATION.md:281:execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:709:./PHASE1_WIRING_DOCUMENTATION.md:290:execute_phase_1_with_full_contract(canonical_input, signal_registry)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:710:./PHASE1_WIRING_DOCUMENTATION.md:319:        execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:711:./PHASE1_WIRING_DOCUMENTATION.md:349:    canon_package = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:712:./PHASE1_WIRING_DOCUMENTATION.md:375:def execute_phase_1_with_full_contract(canonical_input: CanonicalInput) -> CanonPolicyPackage:
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:713:./PHASE1_WIRING_DOCUMENTATION.md:517:       ├─ Llama execute_phase_1_with_full_contract()
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:714:./PHASE1_WIRING_DOCUMENTATION.md:520:4. Phase 1: execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:715:./PHASE1_WIRING_DOCUMENTATION.md:566:- ✅ Llama `execute_phase_1_with_full_contract`
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:716:./PHASE1_WIRING_DOCUMENTATION.md:620:from canonic_phases.Phase_one import execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:717:./PHASE1_WIRING_DOCUMENTATION.md:668:  - `phase1_spc_ingestion_full.py` - execute_phase_1_with_full_contract
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:718:./backups/20251214_135858/orchestrator. py. bak:1466:                execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:719:./backups/20251214_135858/orchestrator. py. bak:1522:            canon_package = execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:720:./src/farfan_pipeline/orchestration/orchestrator.py:2033:                execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:721:./src/farfan_pipeline/orchestration/orchestrator.py:2083:            canon_package = execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:722:./src/farfan_pipeline/phases/Phase_one/phase1_cpp_ingestion_full.py:2757:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:723:./src/farfan_pipeline/phases/Phase_one/__init__.py:55:    execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:724:./src/farfan_pipeline/phases/Phase_one/__init__.py:96:    "execute_phase_1_with_full_contract",
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:725:./src/farfan_pipeline/phases/Phase_one/phase1_spc_ingestion_full.py:2800:def execute_phase_1_with_full_contract(
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:726:./src/farfan_pipeline/phases/Phase_zero/main.py:725:                execute_phase_1_with_full_contract,
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:727:./src/farfan_pipeline/phases/Phase_zero/main.py:738:            cpp = execute_phase_1_with_full_contract(canonical_input)
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:728:./bundle.json:1:{"root": "/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE", "file_count": 325, "total_bytes": 7816416, "files": [{"path": "AGENTS.md", "sha256": "67104bd83544371cb511e1 [... omitted end of long line]
```

### from canonic_phases.Phase_one import ...

hits=3

```text
./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:173:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
./artifacts/reports/PHASE1_CPP_RIA_2025-12-18.md:736:./ARCHITECTURAL_TRANSFORMATION_MASTER_PLAN.md:447:    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
```

### from canonic_phases.Phase_one\.phase1_.*

hits=0

```text
(no hits)
```

