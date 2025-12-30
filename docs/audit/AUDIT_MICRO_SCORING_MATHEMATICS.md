================================================================================
MATHEMATICAL AUDIT OF MICRO-LEVEL SCORING PROCEDURES
================================================================================

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Total Questions:          300
Total Contracts:          300
Scoring Modalities:       6

CRITICAL Findings:        0
HIGH Findings:            0
MEDIUM Findings:          1
LOW Findings:             0

SCORING MODALITY DISTRIBUTION
--------------------------------------------------------------------------------
  TYPE_A              : 260 questions ( 86.7%)
  TYPE_B              :  30 questions ( 10.0%)
  TYPE_E              :  10 questions (  3.3%)

SCORING MODALITY MATHEMATICAL FORMULAS
--------------------------------------------------------------------------------

TYPE_A: High precision balanced scoring
  Formula:      score = 0.4*E + 0.3*S + 0.3*P
  Threshold:    0.65
  Aggregation:  weighted_mean
  Weights:      Elements=0.4, Similarity=0.3, Patterns=0.3
  Failure Code: INSUFFICIENT_EVIDENCE_TYPE_A

TYPE_B: Evidence-focused high threshold
  Formula:      score = 0.5*E + 0.25*S + 0.25*P
  Threshold:    0.7
  Aggregation:  weighted_mean
  Weights:      Elements=0.5, Similarity=0.25, Patterns=0.25
  Failure Code: INSUFFICIENT_EVIDENCE_TYPE_B

TYPE_C: Semantic similarity focused
  Formula:      score = 0.25*E + 0.5*S + 0.25*P
  Threshold:    0.6
  Aggregation:  weighted_mean
  Weights:      Elements=0.25, Similarity=0.5, Patterns=0.25
  Failure Code: INSUFFICIENT_SIMILARITY_TYPE_C

TYPE_D: Pattern matching focused
  Formula:      score = 0.25*E + 0.25*S + 0.5*P
  Threshold:    0.6
  Aggregation:  weighted_mean
  Weights:      Elements=0.25, Similarity=0.25, Patterns=0.5
  Failure Code: INSUFFICIENT_PATTERNS_TYPE_D

TYPE_E: Conservative maximum aggregation
  Formula:      score = max(E, S, P)
  Threshold:    0.75
  Aggregation:  max
  Weights:      Elements=1.0, Similarity=1.0, Patterns=1.0
  Failure Code: INSUFFICIENT_EVIDENCE_TYPE_E

TYPE_F: Strict minimum aggregation
  Formula:      score = min(E, S, P)
  Threshold:    0.55
  Aggregation:  min
  Weights:      Elements=1.0, Similarity=1.0, Patterns=1.0
  Failure Code: INSUFFICIENT_EVIDENCE_TYPE_F

MEDIUM FINDINGS
--------------------------------------------------------------------------------
  1. QQ044: Expected elements mismatch - Missing: {"{'required': True, 'type': 'financiamiento_realista'}", "{'required': True, 'type': 'capacidad_institucional_realista'}"}, Extra: {"{'required': True, 'type': 'realismo_plazos'}", "{'required': True, 'type': 'coherencia_recursos'}", "{'required': True, 'type': 'factibilidad_tecnica'}"}

RECOMMENDATIONS
--------------------------------------------------------------------------------
✓ No critical or high-severity issues found.
✓ Mathematical scoring procedures are correctly implemented.
✓ Contract-questionnaire alignment is maintained.

================================================================================
END OF AUDIT REPORT
================================================================================