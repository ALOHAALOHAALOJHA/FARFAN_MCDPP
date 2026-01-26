# Canonical Questionnaire Central - Documentation

**Status**: FROZEN  
**Freeze Date**: 2026-01-26  
**Version**: 1.0.0

---

## Overview

This directory contains the **canonical documentation** for the F.A.R.F.A.N Pipeline's questionnaire central system. These documents are the **single source of truth** for system architecture, notation, and specifications.

## Frozen Documents

All documents in this directory are **FROZEN** as of 2026-01-26. See [DOCUMENTATION_FREEZE_MANIFEST.md](DOCUMENTATION_FREEZE_MANIFEST.md) for full freeze policy.

### Core Specifications

| Document | Version | Purpose | Status |
|----------|---------|---------|--------|
| [CANONICAL_NOTATION_SPECIFICATION.md](CANONICAL_NOTATION_SPECIFICATION.md) | 4.0.0 | Canonical notation system (PA, DIM, Q, Clusters) | ✅ FROZEN |
| [SISAS_2_0_SPECIFICATION.md](SISAS_2_0_SPECIFICATION.md) | 2.0.0 | Signal Irrigation System Architecture | ✅ FROZEN |
| [access_policy.md](access_policy.md) | 1.0.0 | Access control and security policies | ✅ FROZEN |

### Governance Documents

| Document | Purpose |
|----------|---------|
| [DOCUMENTATION_FREEZE_MANIFEST.md](DOCUMENTATION_FREEZE_MANIFEST.md) | Freeze policy, checksums, change procedures |
| [DOCUMENTATION_CHECKSUMS.txt](DOCUMENTATION_CHECKSUMS.txt) | SHA-256 checksums for integrity verification |
| [README.md](README.md) | This file - documentation overview |

---

## Quick Reference

### Policy Areas (PA01-PA10)

```
PA01: MUJ - Derechos de las mujeres e igualdad de género
PA02: VIO - Prevención de la violencia
PA03: AMB - Ambiente sano y cambio climático
PA04: DESC - Derechos económicos, sociales y culturales
PA05: VIC - Derechos de las víctimas y construcción de paz
PA06: NIÑ - Derecho al buen futuro de niñez y adolescencia
PA07: TIE - Tierras y territorios
PA08: LID - Líderes y defensores de derechos humanos
PA09: PPL - Crisis de derechos de personas privadas de libertad
PA10: MIG - Migración transfronteriza
```

### Dimensions (DIM01-DIM06)

```
DIM01: INS - Insumos (Diagnóstico y Líneas Base)
DIM02: ACT - Actividades (Diseño de Intervención)
DIM03: PRO - Productos (Verificables)
DIM04: RES - Resultados (Medibles)
DIM05: IMP - Impactos (Largo Plazo)
DIM06: COH - Coherencia Causal (Teoría de Cambio)
```

### Question Levels

```
MICRO:  Q001-Q300 (300 specific questions)
MESO:   Q301-Q304 (4 cluster integration questions)
MACRO:  Q305      (1 global coherence question)
TOTAL:  305 questions
```

### Clusters (CL01-CL04)

```
CL01: SEC-PAZ      - Seguridad y Paz (PA02, PA05, PA07)
CL02: GP           - Grupos Poblacionales (PA01, PA06, PA08)
CL03: TERR-AMB     - Territorio-Ambiente (PA03, PA04)
CL04: DESC-CRISIS  - Derechos Sociales & Crisis (PA09, PA10)
```

---

## Verification

### Verify Document Integrity

```bash
# Verify all checksums
cd canonic_questionnaire_central/documentation
sha256sum -c DOCUMENTATION_CHECKSUMS.txt

# Expected output:
# CANONICAL_NOTATION_SPECIFICATION.md: OK
# SISAS_2_0_SPECIFICATION.md: OK
# access_policy.md: OK
```

### Check Document Versions

```bash
# Check versions in documents
grep "^Version:" *.md | grep -v FREEZE

# Expected output:
# CANONICAL_NOTATION_SPECIFICATION.md:**Version**: 4.0.0
# SISAS_2_0_SPECIFICATION.md:**Version**: 2.0.0
# access_policy.md:**Version**: 1.0.0
```

---

## Usage Guidelines

### For Developers

1. **Read-Only**: Treat all documents as read-only
2. **Reference**: Link to these documents in code comments and docstrings
3. **Verify**: Run integrity checks before deployment
4. **Report**: Report any discrepancies between docs and implementation

### For System Architects

1. **Authoritative**: These docs define system behavior
2. **Contracts**: Implementation must match specifications
3. **Dependencies**: Update dependent systems when docs change
4. **Reviews**: Include in architecture reviews

### For QA/Testing

1. **Test Basis**: Use specs as test case source
2. **Validation**: Verify implementation matches frozen specs
3. **Regression**: Check for unintended deviations
4. **Coverage**: Ensure all spec sections are tested

---

## Modification Process

### ⚠️ IMPORTANT: Documents are FROZEN

To modify any frozen document:

1. **Proposal**: Submit change proposal (see [DOCUMENTATION_FREEZE_MANIFEST.md](DOCUMENTATION_FREEZE_MANIFEST.md))
2. **Review**: Governance team review and approval
3. **Implementation**: Make approved changes
4. **Version**: Increment document version number
5. **Checksums**: Update checksums in manifest and checksums file
6. **Notify**: Inform all stakeholders
7. **Update**: Update dependent systems

**Do NOT** modify frozen documents without following this process.

---

## Integration Points

### System Components Using These Docs

1. **Orchestrator** (`src/farfan_pipeline/orchestration/`)
   - Uses phase definitions
   - Enforces constitutional invariants

2. **Method Executor** (`src/farfan_pipeline/execution/`)
   - Uses method contracts
   - Implements question execution

3. **Scoring System** (`canonic_questionnaire_central/scoring/`)
   - Uses dimension definitions
   - Implements aggregation rules

4. **Signal Distribution** (`canonic_questionnaire_central/core/`)
   - Uses SISAS 2.0 specification
   - Implements signal routing

5. **Contract Executors** (`contracts/executor_contracts/`)
   - Uses question IDs and slot notation
   - Implements Q001-Q300 contracts

6. **API Layer** (`canonic_questionnaire_central/api/`)
   - Uses access policies
   - Implements authentication/authorization

---

## Related Documentation

### Root Directory

- **ORCHESTRATOR_CANONICAL_FLUX_AUDIT_REPORT.md** - Phase audit results
- **PHASE_0_ORCHESTRATION_ANALYSIS.md** - Phase 0 verification
- **CANONICAL_PHASE_ARCHITECTURE.md** - Overall architecture (if exists)

### Build Artifacts

- **_build/build_manifest.json** - Build metadata
- **_build/integrity_report.json** - System-wide integrity checks
- **_build/IMPLEMENTATION_PROGRESS_REPORT.md** - Implementation status

### Registry

- **_registry/questionnaire_index.json** - Question registry
- **_registry/questionnaire_monolith.json** - Complete questionnaire
- **_registry/EMPIRICAL_CORPUS_INDEX.json** - Empirical calibration data

---

## Support

### Questions?

- **Technical**: Check implementation code comments
- **Specification**: Read the frozen documents
- **Changes**: Contact F.A.R.F.A.N Pipeline Governance Team
- **Issues**: Report discrepancies via issue tracker

### Emergency

For critical security or system-breaking issues, see "Emergency Unfreeze" section in [DOCUMENTATION_FREEZE_MANIFEST.md](DOCUMENTATION_FREEZE_MANIFEST.md).

---

## Document History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0.0 | 2026-01-26 | Initial freeze | F.A.R.F.A.N Pipeline Governance Team |

---

**Maintained By**: F.A.R.F.A.N Pipeline Governance Team  
**Last Updated**: 2026-01-26  
**Next Review**: 2026-04-26 (90 days)

---

## Checksums

```
5fc636dc2c50e09da60efdb7a1db1334c9ba55fa63cacedb9c40b0b3f8c364e6  CANONICAL_NOTATION_SPECIFICATION.md
23bc51ee7e5eb4c455109c433d9d001fd28d856c2b1272a657960e2464dc1eab  SISAS_2_0_SPECIFICATION.md
5d37e5daef3000eeff69a0893283afbbb527b8f6ff0a5c5895e683d73711069d  access_policy.md
```

**Verification**: `sha256sum -c DOCUMENTATION_CHECKSUMS.txt`

---

**END OF README**
