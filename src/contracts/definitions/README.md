# Contract Definitions

This directory contains static contract definitions in JSON format.

## Executor Contracts

- `executor/base/` - 30 base executor contracts (D1-Q1 through D6-Q5)
- `executor/specialized/` - 300 specialized contracts (Q001-Q300)

## Schema Documentation

All contracts follow the V3 schema with the following structure:
- `identity` - Contract identification
- `executor_binding` - Executor class binding
- `method_binding` - Method execution configuration
- `question_context` - Question text and patterns
- `evidence_assembly` - Assembly rules
- `output_contract` - Output schema
- `validation_rules` - Validation configuration
- `signal_requirements` - SISAS signal requirements
