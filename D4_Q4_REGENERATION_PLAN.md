# D4-Q4 (Q019) Contract Regeneration Plan

## STATUS: IN PROGRESS - Rigorous Guide-Following Approach

### Completed Steps (PASO 1-3)

**PASO 1: Method Extraction** ✅
- Source: `method_classification_all_30.json` → D4-Q4 entry
- Extracted: 7 methods total
- Classes: PolicyContradictionDetector (3), OperationalizationAuditor (2), BayesianCounterfactualAuditor (1), FinancialAuditor (1)

**PASO 2: Epistemological Reclassification** ✅
Applied decision tree from OPERACIONALIZACIÓN_CONTRATOS_VERSION_4:
```
N1-EMP (Empirical): 0 methods
N2-INF (Inferential): 5 methods
  - PolicyContradictionDetector._calculate_objective_alignment
  - PolicyContradictionDetector._identify_affected_sections  
  - PolicyContradictionDetector._generate_resolution_recommendations
  - OperationalizationAuditor._generate_optimal_remediations
  - BayesianCounterfactualAuditor.aggregate_risk_and_prioritize

N3-AUD (Audit/Veto): 1 method
  - FinancialAuditor._detect_allocation_gaps

EXCLUDED (N4-SYN): 1 method
  - OperationalizationAuditor._get_remediation_text (Layer L4_synthesis)
```

**PASO 3: Contract Type Determination** ✅
- Dominant classes: PolicyContradictionDetector, OperationalizationAuditor
- **Contract Type**: TYPE_E (Lógico)
- **Primary Strategy**: weighted_mean (N2 fusion)
- **Focus**: Detección de contradicciones lógicas y coherencia de políticas

### Next Steps (PASO 4-5)

**PASO 4: Generate Complete Contract Structure**
Following D2-Q5-v4.json (TYPE_E reference), must include all 15 mandatory sections:

1. ✅ identity - Contract metadata
2. ✅ executor_binding - Executor configuration
3. ✅ method_binding - 6 methods classified (0 N1, 5 N2, 1 N3)
4. ⏳ question_context - Monolith reference
5. ⏳ signal_requirements - Derivation rules
6. ⏳ evidence_assembly - Type system + 4 assembly rules (R1-R4)
7. ⏳ fusion_specification - TYPE_E strategies
8. ⏳ cross_layer_fusion - Popperian asymmetry
9. ⏳ human_answer_structure - 4 sections (S1-S4) with templates
10. ⏳ output_contract - Output specifications
11. ⏳ validation_rules - Validation criteria
12. ⏳ error_handling - Error strategies
13. ⏳ traceability - Audit trail
14. ⏳ compatibility - Version compatibility
15. ⏳ calibration - Calibration parameters

**PASO 5: Validation Checklist**
- [ ] All methods in exactly ONE phase (A, B, or C)
- [ ] method_count = phase_A.length + phase_B.length + phase_C.length = 6
- [ ] provides in methods match sources in assembly_rules
- [ ] NO spaces in provides, sources, module paths
- [ ] N3 methods have veto_conditions defined
- [ ] contract_type (TYPE_E) matches primary_strategy (weighted_mean)

## Commitment

This contract will be completed following **EACH INSTRUCTION** from the guide, with:
- NO bulk generation scripts
- NO placeholders or incomplete sections
- Complete human_answer_structure with template.structure arrays
- Type-specific epistemological patterns (TYPE_E)
- Full evidence assembly rules properly mapped to actual methods

## Evidence Trail

All decisions documented in:
- `/tmp/q019_methods.json` - Raw extraction
- `/tmp/q019_classified.json` - Classification results
- `/tmp/q019_contract_meta.json` - Contract metadata
- `/tmp/D4-Q4-v4_partial.json` - Partial structure (sections 1-3)

Ready to complete remaining sections with same rigor.
