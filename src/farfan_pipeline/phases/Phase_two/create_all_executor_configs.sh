#!/bin/bash
# Generate all 30 executor configuration files

CONFIGS_DIR="$(dirname "$0")/executor_configs"
mkdir -p "$CONFIGS_DIR"

# Array of all executors: (ID, DIM, Q, EPISTEMIC, METHODS)
EXECUTORS=(
  "D1_Q2_ProblemDimensioningAnalyzer|D1|Q2|bayesian,statistical,normative|12"
  "D1_Q3_BudgetAllocationTracer|D1|Q3|structural,financial,normative|13"
  "D1_Q4_InstitutionalCapacityIdentifier|D1|Q4|semantic,structural|11"
  "D1_Q5_ScopeJustificationValidator|D1|Q5|temporal,consistency,structural|7"
  "D2_Q1_StructuredPlanningValidator|D2|Q1|structural,normative|7"
  "D2_Q2_InterventionLogicInferencer|D2|Q2|causal,bayesian,structural|11"
  "D2_Q3_RootCauseLinkageAnalyzer|D2|Q3|causal,bayesian,semantic|9"
  "D2_Q4_RiskManagementAnalyzer|D2|Q4|bayesian,statistical,normative|10"
  "D2_Q5_StrategicCoherenceEvaluator|D2|Q5|normative,consistency,statistical|8"
  "D3_Q1_IndicatorQualityValidator|D3|Q1|normative,semantic,structural|8"
  "D3_Q4_TechnicalFeasibilityEvaluator|D3|Q4|structural,causal,statistical|26"
  "D3_Q5_OutputOutcomeLinkageAnalyzer|D3|Q5|causal,bayesian,semantic|25"
  "D4_Q1_OutcomeMetricsValidator|D4|Q1|semantic,temporal,statistical|17"
  "D4_Q2_CausalChainValidator|D4|Q2|causal,bayesian,structural|8"
  "D4_Q3_AmbitionJustificationAnalyzer|D4|Q3|bayesian,statistical|8"
  "D4_Q4_ProblemSolvencyEvaluator|D4|Q4|normative,consistency|7"
  "D4_Q5_VerticalAlignmentValidator|D4|Q5|normative,structural|6"
  "D5_Q1_LongTermVisionAnalyzer|D5|Q1|causal,temporal,semantic|8"
  "D5_Q2_CompositeMeasurementValidator|D5|Q2|bayesian,statistical,normative|14"
  "D5_Q3_IntangibleMeasurementAnalyzer|D5|Q3|semantic,normative|7"
  "D5_Q4_SystemicRiskEvaluator|D5|Q4|bayesian,causal,statistical|9"
  "D5_Q5_RealismAndSideEffectsAnalyzer|D5|Q5|causal,bayesian,normative|9"
  "D6_Q2_LogicalProportionalityValidator|D6|Q2|normative,causal,statistical|8"
  "D6_Q3_ValidationTestingAnalyzer|D6|Q3|bayesian,causal,statistical|9"
  "D6_Q4_FeedbackLoopAnalyzer|D6|Q4|causal,temporal,structural|8"
  "D6_Q5_ContextualAdaptabilityEvaluator|D6|Q5|semantic,normative,contextual|8"
)

for EXECUTOR_DEF in "${EXECUTORS[@]}"; do
  IFS='|' read -r ID DIM Q EPISTEMIC METHODS <<< "$EXECUTOR_DEF"
  
  # Convert epistemic string to JSON array
  EPISTEMIC_JSON=$(echo "$EPISTEMIC" | sed 's/,/", "/g' | sed 's/^/"/' | sed 's/$/"/')
  
  # Extract dimension number and question number
  DIM_NUM=$(echo "$DIM" | sed 's/D//')
  Q_NUM=$(echo "$Q" | sed 's/Q//')
  
  # Extract executor name (after D{X}_Q{Y}_)
  NAME=$(echo "$ID" | sed 's/^D[0-9]_Q[0-9]_//')
  NAME_UPPER=$(echo "$NAME" | tr '[:lower:]' '[:upper:]')
  
  # Create config file
  cat > "$CONFIGS_DIR/${ID}.json" << EOF
{
  "executor_id": "$ID",
  "dimension": "$DIM",
  "question": "$Q",
  "canonical_label": "DIM$(printf '%02d' $DIM_NUM)_Q$(printf '%02d' $Q_NUM)_${NAME_UPPER}",
  "role": "SCORE_Q",
  "required_layers": [
    "@b",
    "@chain",
    "@q",
    "@d",
    "@p",
    "@C",
    "@u",
    "@m"
  ],
  "runtime_parameters": {
    "timeout_s": 300,
    "retry": 3,
    "temperature": 0.0,
    "max_tokens": 4096,
    "memory_limit_mb": 512,
    "enable_profiling": true
  },
  "thresholds": {
    "min_quality_score": 0.5,
    "min_evidence_confidence": 0.6,
    "max_runtime_ms": 60000
  },
  "epistemic_mix": [
    $EPISTEMIC_JSON
  ],
  "contextual_params": {
    "expected_methods": $METHODS,
    "critical_methods": []
  },
  "calibration_settings": {
    "enabled": true,
    "capture_runtime_metrics": true,
    "capture_memory_metrics": true,
    "store_results": true
  }
}
EOF

  echo "Created: $ID.json"
done

echo ""
echo "Configuration files created in: $CONFIGS_DIR"
echo "Total files: $(ls -1 "$CONFIGS_DIR"/*.json 2>/dev/null | grep -v template | wc -l | tr -d ' ')"
