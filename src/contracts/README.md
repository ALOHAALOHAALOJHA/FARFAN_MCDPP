# Contract System

This directory contains the complete contract system for F.A.R.F.A.N.

## Structure

- `core/` - Core contract infrastructure (single source of truth)
- `specialized/` - Phase-specific contracts (phase0, phase2, sisas)
- `definitions/` - Static contract definitions (JSON)
- `tools/` - Contract utilities and scripts
- `wiring/` - Contract integration code
- `tests/` - Contract tests

## Usage

```python
from farfan_pipeline.contracts.core import ContractLoader
from farfan_pipeline.contracts.specialized.phase2 import ExecutorContract

# Load contract
loader = ContractLoader()
contract = loader.load('Q001.v3.json')
```

See individual directories for more documentation.
