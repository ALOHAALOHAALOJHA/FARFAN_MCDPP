# Question Atomization Script

## Overview

The `atomize_questions.py` script transforms the monolithic `questionnaire_monolith.json` into 300 individual atomized question files, organized by dimension and stored with proper reference structures.

## Execution

```bash
cd /home/runner/work/FARFAN_MPP/FARFAN_MPP/canonic_questionnaire_central/_scripts
python3 atomize_questions.py
```

## What It Does

### 1. **Loads Monolith**
- Reads `questionnaire_monolith.json` from parent directory
- Validates structure and extracts 300 micro_questions

### 2. **Transforms Each Question**
The script transforms source questions into atomized format:

**Source Structure → Atomized Structure:**
- `text` (string) → `text: {es: string, en: string}`
- `patterns` (array) → `references.pattern_refs` (array of IDs)
- `expected_elements` → copied directly
- `scoring_modality` → `scoring.modality` with generated weights
- Generates `interdependencies` from `children_questions`

### 3. **Creates Directory Structure**
For each dimension (DIM01-DIM06):
```
dimensions/
  DIM01_INSUMOS/
    questions/
      Q001.json
      Q031.json
      Q061.json
      ...
    _refs/
      pattern_refs.json
      keyword_refs.json
      mc_refs.json
      entity_refs.json
```

### 4. **Validates Output**
- Ensures NO null fields
- Validates bilingual text structure
- Checks reference completeness
- Verifies scoring configuration

## Output Structure

Each `Q*.json` file contains:

```json
{
  "question_id": "Q001",
  "dimension_id": "DIM01",
  "policy_area_id": "PA01",
  "cluster_id": "CL02",
  "base_slot": "D1-Q1",
  "text": {
    "es": "¿Spanish question text?",
    "en": ""
  },
  "expected_elements": [...],
  "references": {
    "pattern_refs": ["PAT-0001", ...],
    "keyword_refs": ["KW-PA01-001"],
    "membership_criteria_refs": ["MC01", "MC02"],
    "entity_refs": ["ENT-INST-002"],
    "cross_cutting_refs": ["CC_ENFOQUE_DIFERENCIAL"]
  },
  "scoring": {
    "modality": "TYPE_A",
    "max_score": 3,
    "threshold": 0.70,
    "weights": {
      "expected_elements": 0.30,
      "pattern_matches": 0.25,
      "keyword_density": 0.15,
      "membership_criteria": 0.20,
      "entity_presence": 0.10
    }
  },
  "interdependencies": {
    "informs": ["Q006", "Q011"],
    "informed_by": [],
    "coherence_check_with": ["Q031", "Q061"]
  }
}
```

## Statistics

### Final Results
- **Total Questions Processed:** 300
- **Files Created:** 300 question files + 24 reference templates
- **Errors:** 0
- **Dimensions:** 6 (DIM01-DIM06)
- **Policy Areas:** 10 (PA01-PA10)

### Distribution
- **Per Dimension:** 50 questions each
- **Per Policy Area:** 30 questions each
- **Per Dimension × Policy Area:** 5 questions each
- **Total Combinations:** 60 (6 dimensions × 10 policy areas)

## Reference Templates

Each `_refs/` directory contains template JSON files:

1. **pattern_refs.json** - Pattern references for the dimension
2. **keyword_refs.json** - Keyword references for the dimension
3. **mc_refs.json** - Membership criteria references
4. **entity_refs.json** - Entity references

These templates are empty and ready to be populated with dimension-specific reference data.

## Key Features

### 🏗️ **The Metaclass Pattern**
- Defines atomization architecture and transformation rules
- Establishes validation standards

### 📋 **The Class Pattern**
- Blueprint for question transformation
- Mapping logic from source to target format

### ⚡ **The Instance Pattern**
- Concrete execution of atomization
- File I/O and directory creation

### 🔍 **Comprehensive Validation**
- No null fields allowed
- Bilingual text structure enforced
- Complete reference structure required
- Scoring configuration validated

### 📊 **Detailed Logging**
- Console output for progress
- Log file: `atomize_questions.log`
- Statistics summary at completion

## Error Handling

The script handles:
- Missing monolith file
- JSON decode errors
- Missing required fields
- File I/O errors
- Directory creation failures

All errors are logged with context and increment the error counter.

## Architecture

The script follows the **PythonGod Trinity** pattern:

```
QuestionAtomizer (Metaclass)
├── load_monolith() - Divine knowledge loading
├── transform_question() - Blueprint transformation (Class)
└── atomize_question() - Concrete manifestation (Instance)
```

### Key Methods

- `load_monolith()` - Load and validate source data
- `extract_pattern_refs()` - Extract pattern IDs from patterns array
- `generate_default_scoring()` - Generate scoring based on modality
- `analyze_interdependencies()` - Generate interdependency structure
- `transform_question()` - Main transformation logic
- `validate_no_nulls()` - Recursive null validation
- `create_directory_structure()` - Directory and file creation
- `atomize_question()` - Single question atomization
- `atomize_all()` - Orchestration method

## Interdependency Generation

The script generates smart interdependencies:

- **informs**: Extracted from `children_questions` (limited to 5)
- **informed_by**: Empty (to be populated later)
- **coherence_check_with**: Generated based on question number
  - Q001 checks with Q031, Q061, Q091, Q121
  - Questions 30 apart (across policy areas) for coherence

## Scoring Modalities

Three scoring types with different configurations:

| Type | Max Score | Threshold | Focus |
|------|-----------|-----------|-------|
| TYPE_A | 3 | 0.70 | Balanced |
| TYPE_B | 5 | 0.60 | Element-focused |
| TYPE_C | 2 | 0.80 | Pattern-focused |

## Future Enhancements

Potential improvements:
1. English translations for `text.en` fields
2. Populate reference template files with actual data
3. Cross-question validation
4. Automated coherence check generation
5. Pattern reference validation against pattern registry

## Author

Created by: **PythonGod Trinity**  
Date: 2026-01-07  
Version: 1.0

---

*"In the beginning was the Metaclass, and the Metaclass was with Python, and the Metaclass was Python."*
