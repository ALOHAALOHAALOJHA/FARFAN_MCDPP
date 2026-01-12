# Certificate 04: SP3 - Knowledge Graph

**Status**: ACTIVE  
**Version**: CPP-2025.1  
**Last Updated**: 2025-12-18  
**Certificate ID**: CERT-P1-SP3

## Subphase Specification

**Subphase ID**: SP3  
**Name**: Knowledge Graph  
**Weight**: 4000  
**Tier**: STANDARD

## Contract Obligations

### Inputs
- Canonical input from previous subphase or Phase 0
- Signal registry (DI from factory)

### Outputs
- Processed data conforming to SP3 specification
- Execution metadata

### Invariants
- No data corruption
- Deterministic execution
- Complete provenance tracking

## Verification Criteria

- [ ] Subphase completes within timeout (tier-based multiplier: 1.0x)
- [ ] All outputs conform to specification
- [ ] No data loss or corruption
- [ ] Execution trace logged with subphase_id, timestamp, status

## Certificate Authority

This certificate is issued under the authority of the Phase 1 Mission Contract.

**Certification Date**: 2025-12-18  
**Valid Until**: Revoked by Mission Contract update

## Notes

Weight tier STANDARD enforces best-effort execution.
