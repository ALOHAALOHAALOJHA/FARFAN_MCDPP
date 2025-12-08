# JQ filter to add semantic metadata fields to canonical_method_catalogue_v2.json

def get_semantic_tags:
  .canonical_name as $name |
  .file_path as $path |
  (
    (if ($name | ascii_downcase | test("contradiction|coherence|consistency")) then ["coherence", "evidence"] else [] end) +
    (if ($name | ascii_downcase | test("temporal|timeline")) or ($path | ascii_downcase | contains("temporal")) then ["temporal", "structural"] else [] end) +
    (if ($name | ascii_downcase | test("causal|mechanism|inference")) then ["causal", "evidence"] else [] end) +
    (if ($name | ascii_downcase | test("bayesian|probability|likelihood")) then ["evidence", "numerical"] else [] end) +
    (if ($name | ascii_downcase | test("extract|parse")) then ["structural"] else [] end) +
    (if ($name | ascii_downcase | test("calculate|compute|score|measure")) then ["numerical"] else [] end) +
    (if ($name | ascii_downcase | test("policy|goal|objective")) then ["policy", "structural"] else [] end) +
    (if ($name | ascii_downcase | test("validate|verify|check")) then ["evidence", "textual_quality"] else [] end) +
    (if ($path | ascii_downcase | contains("derek_beach")) then ["causal", "evidence"] else [] end) +
    (if ($path | ascii_downcase | contains("contradiction")) then ["coherence"] else [] end) +
    (if ($path | ascii_downcase | contains("scoring")) then ["numerical", "evidence"] else [] end) +
    (if ($name | ascii_downcase | test("quality|readability|completeness")) then ["textual_quality"] else [] end) +
    (if ($name | ascii_downcase | test("aggregate|combine|merge")) then ["numerical"] else [] end) +
    (if ($name | ascii_downcase | test("report|summarize|format")) then ["structural"] else [] end)
  ) | unique | sort | if length == 0 then ["structural"] else . end;

def get_output_range:
  .canonical_name as $name |
  if ($name | ascii_downcase | test("score|probability|confidence|likelihood|similarity|coherence|weight")) then [0.0, 1.0]
  elif ($name | ascii_downcase | test("factor")) and ($name | ascii_downcase | contains("bayes")) then [0.0, null]
  elif ($name | ascii_downcase | test("count|number|size")) then [0, null]
  elif ($name | ascii_downcase | test("check|validate|verify|test|^is_|^has_")) then [0, 1]
  else null
  end;

def get_fusion_requirements:
  .canonical_name as $name |
  .file_path as $path |
  .layer as $layer |
  if ($layer == "class_method") and ($name | test("__init__|__post_init__|__setattr__|__repr__")) then
    {"required": [], "optional": ["config"]}
  elif ($path | ascii_downcase | test("compat|ports|boot_checks|runtime_config|dependency")) then
    {"required": [], "optional": ["config"]}
  elif ($path | ascii_downcase | contains("derek_beach")) or ($path | ascii_downcase | contains("contradiction")) then
    if ($name | ascii_downcase | test("detect|infer|extract|identify")) then
      {"required": ["extracted_text", "question_id", "preprocessed_document"], "optional": ["embeddings", "previous_analysis", "config", "dependency_parse"]}
    elif ($name | ascii_downcase | test("calculate|score|measure")) then
      {"required": ["question_id", "previous_analysis"], "optional": ["calibration_params", "model_weights", "config"]}
    else
      {"required": ["extracted_text", "question_id"], "optional": ["previous_analysis", "config"]}
    end
  elif ($name | ascii_downcase | contains("temporal")) or ($path | ascii_downcase | contains("temporal")) then
    {"required": ["extracted_text", "temporal_markers"], "optional": ["preprocessed_document", "config"]}
  elif ($name | ascii_downcase | test("causal|mechanism")) then
    {"required": ["preprocessed_document", "dependency_parse"], "optional": ["temporal_markers", "domain_ontology", "config"]}
  elif ($name | ascii_downcase | test("aggregate|combine")) then
    {"required": ["previous_analysis", "question_id"], "optional": ["config", "calibration_params"]}
  elif ($name | ascii_downcase | test("report|generate|format")) then
    {"required": ["previous_analysis", "document_id"], "optional": ["document_metadata", "config"]}
  elif ($path | ascii_downcase | contains("analysis")) then
    {"required": ["extracted_text", "question_id"], "optional": ["previous_analysis", "config"]}
  else
    {"required": ["extracted_text"], "optional": ["config"]}
  end;

# Add the three new fields to each method
map(
  . + {
    "semantic_tags": get_semantic_tags,
    "output_range": get_output_range,
    "fusion_requirements": get_fusion_requirements
  }
)
