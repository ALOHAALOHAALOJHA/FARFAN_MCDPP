# Discovery Protocol Quick Reference

## Execution

```bash
# Run from repository root
python3 scripts/discovery_protocol.py
```

## Output Location

```
PHASE2_INVENTORY.yaml (repository root)
```

## Key Metrics (Current State)

- **Total files scanned**: 1,456
- **Python files**: 491
- **JSON files**: 440
- **Markdown files**: 525
- **Phase 2 files**: 358
- **Executor files**: 350
- **Contract files**: 526
- **Legacy artifacts**: 4

## Four Mandatory Command Sets

1. **Exhaustive Discovery**: Phase 2, executor, carver, orchestrator, SISAS, dura_lex, synchronization, irrigation, contract, validator files
2. **Directory Mapping**: All Python, JSON, Markdown files
3. **Import Dependencies**: Traces imports across executor, carver, contract, SISAS, orchestrator
4. **Legacy Detection**: Finds batch_*.py, *_v2*, *_final*, *_old* files

## Testing

```bash
# Run all discovery protocol tests
pytest tests/test_discovery_protocol.py -v -m updated

# Expected: 11 tests passing
```

## Use Cases

- **Pre-refactoring baseline**: Document current state before changes
- **Post-change verification**: Confirm expected impact
- **Audit compliance**: Generate inventory for review
- **Architecture analysis**: Understand component relationships

## Documentation

- Full documentation: `DISCOVERY_PROTOCOL_README.md`
- Implementation: `scripts/discovery_protocol.py`
- Test suite: `tests/test_discovery_protocol.py`
- Output schema: See DISCOVERY_PROTOCOL_README.md section "Inventory Structure"
