# F.A.R.F.A.N Pipeline Orchestrator

Orchestration layer for the Municipal Development Plan Causal Evaluation Pipeline.

## Structure

```
orchestrator/
├── contracts/
│   ├── _contract_template.yaml    # Template for new contracts
│   └── stages/                    # Per-stage contracts
│       ├── phase_2_evidence_extraction.yaml
│       └── phase_3_scoring.yaml
├── docs/
│   ├── fmea.csv                   # Failure Mode and Effects Analysis
│   └── traceability_matrix.csv    # Requirements traceability
├── infra/                         # Infrastructure configs (future)
├── inventory/
│   ├── pipeline_inventory.yaml    # Complete stage inventory
│   └── raw_files.txt              # Discovered executables
├── src/
│   ├── orchestrator.py            # Main orchestrator
│   └── workflow_definition.yaml   # DAG definition
└── tests/                         # Test suite (future)
```

## Quick Start

```bash
# Validate workflow DAG
python -c "
import yaml
import networkx as nx
data = yaml.safe_load(open('src/workflow_definition.yaml'))
G = nx.DiGraph()
for s in data['workflow']['stages']:
    for n in s.get('next', []):
        G.add_edge(s['name'], n)
assert nx.is_directed_acyclic_graph(G)
print('DAG válido ✅')
"

# Run pipeline (placeholder)
python src/orchestrator.py --municipality 05001 --document path/to/plan.pdf
```

## Design Principles

1. **Design by Contract**: Every stage has explicit input/output contracts
2. **Idempotency**: Execution keys prevent duplicate processing
3. **Observability**: Structured logs, metrics, and traces
4. **Fail Fast**: Contract violations stop execution immediately
5. **Compensating Actions**: Rollback on failure

## Status

| Component | Status |
|-----------|--------|
| Inventory | ✅ Complete |
| Contracts | 🟡 Partial (2/10 stages) |
| FMEA | ✅ Complete |
| Traceability | ✅ Complete |
| Orchestrator | 🟡 Skeleton |
| Tests | ❌ Pending |
