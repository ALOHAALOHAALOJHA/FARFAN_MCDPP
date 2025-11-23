# Questionnaire Coverage Audit Report

This report summarizes the structural and contract coverage of the questionnaire monolith.
The audit was generated on **2025-11-23**.

## 1. Executive Summary

The audit reveals significant gaps in contract coverage for the micro-questions. While the core structure of the monolith and contracts appears sound (no orphan contracts), the vast majority of questions lack a corresponding contract file, which is a critical prerequisite for their execution in the pipeline.

The current contract coverage is **6.67%**.

## 2. Key Metrics

| Metric                               | Value |
| ------------------------------------ | ----- |
| Total Micro-Questions                | 300   |
| Questions with Contract              | 20    |
| Questions without Contract           | 280   |
| Orphan Contracts                     | 0     |
| Contract Coverage                    | 6.67% |
| Questions with Executor Mapping      | 2     |
| Questions with Valid Executor        | 2     |
| Questions with Valid Method Route    | 2     |

## 3. Coverage Gaps

This section details the specific gaps found during the audit.

### 3.1. Micro-Questions Without Contracts

A total of **280** micro-questions do not have a corresponding contract file in the `config/executor_contracts/` directory. This prevents them from being executed.

The following **28 unique question IDs** are missing contracts across all policy areas:

- Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010
- Q011, Q012, Q013, Q014, Q015, Q016, Q017, Q018, Q019, Q020
- Q021, Q022, Q023, Q024, Q025, Q026, Q027, Q028, Q029, Q030
- Q033, Q034, Q035, Q036, Q037, Q038, Q039, Q040
- Q041, Q042, Q043, Q044, Q045, Q046, Q047, Q048, Q049, Q050
- Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q059, Q060
- Q063, Q064, Q065, Q066, Q067, Q068, Q069, Q070
- Q071, Q072, Q073, Q074, Q075, Q076, Q077, Q078, Q079, Q080
- Q081, Q082, Q083, Q084, Q085, Q086, Q087, Q088, Q089, Q090
- Q093, Q094, Q095, Q096, Q097, Q098, Q099, Q100
- Q101, Q102, Q103, Q104, Q105, Q106, Q107, Q108, Q109, Q110
- Q111, Q112, Q113, Q114, Q115, Q116, Q117, Q118, Q119, Q120
- Q123, Q124, Q125, Q126, Q127, Q128, Q129, Q130
- Q131, Q132, Q133, Q134, Q135, Q136, Q137, Q138, Q139, Q140
- Q141, Q142, Q143, Q144, Q145, Q146, Q147, Q148, Q149, Q150
- Q153, Q154, Q155, Q156, Q157, Q158, Q159, Q160
- Q161, Q162, Q163, Q164, Q165, Q166, Q167, Q168, Q169, Q170
- Q171, Q172, Q173, Q174, Q175, Q176, Q177, Q178, Q179, Q180
- Q183, Q184, Q185, Q186, Q187, Q188, Q189, Q190
- Q191, Q192, Q193, Q194, Q195, Q196, Q197, Q198, Q199, Q200
- Q201, Q202, Q203, Q204, Q205, Q206, Q207, Q208, Q209, Q210

... and so on. A full list can be found in the `audit_manifest.json` artifact.

### 3.2. Orphan Contracts

There are **0** orphan contracts. All existing contracts correspond to at least one micro-question in the monolith.

### 3.3. Invalid Executor or Method Mappings

There are no invalid executor or method mappings in the existing contracts.

## 4. Recommendations

1.  **Prioritize Contract Creation**: The highest priority is to create the missing 28 contract files. This will immediately increase the contract coverage and enable the execution of more questions.
2.  **Automate Contract Scaffolding**: To accelerate the process, a script could be created to automatically generate placeholder contract files for the missing questions.
3.  **Enforce Coverage in CI**: The `verify_contract_completeness.py` script should be integrated into the CI/CD pipeline to prevent new questions from being added without corresponding contracts.

---
*This report was generated automatically by the `audit_questionnaire_coverage.py` script.*
