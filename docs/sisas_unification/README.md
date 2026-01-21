# SISAS Unification Technical Specification

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## Overview

The SISAS (Signal-Irrigated Scoring and Assessment System) Unification consolidates the F.A.R.F.A.N. framework's distributed signal processing into a cohesive orchestration layer. This specification defines the canonical architecture, protocols, and operational standards for unified signal distribution across all 10 processing phases.

## Table of Contents

### Core Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Visual architecture with Mermaid diagrams showing component hierarchy, signal flow, gate sequence, and consumer registry |
| [CONSUMER_REGISTRY.md](./CONSUMER_REGISTRY.md) | Complete specification of all 10 phase consumers including scopes, capabilities, and signal types |
| [SIGNAL_CATALOG.md](./SIGNAL_CATALOG.md) | Reference for all 17 SignalTypes with categories, phases, and availability ranges |
| [GATE_SPECIFICATIONS.md](./GATE_SPECIFICATIONS.md) | Detailed validation rules for all 4 gates in the signal pipeline |

### Operational Documentation

| Document | Description |
|----------|-------------|
| [IRRIGATION_INVENTORY.md](./IRRIGATION_INVENTORY.md) | Complete inventory of 347 irrigable items with mappings |
| [MIGRATION_CHECKLIST.md](./MIGRATION_CHECKLIST.md) | Step-by-step migration and rollback procedures |
| [METRICS_DASHBOARD.md](./METRICS_DASHBOARD.md) | KPIs, metrics definitions, and performance targets |

## Quick Reference

### System Summary

- **Orchestrator:** UnifiedOrchestrator → UnifiedFactory → SignalDistributionOrchestrator
- **Gates:** 4 sequential validation gates
- **Consumers:** 10 phase-specific consumers (phase_00 through phase_09)
- **Signal Types:** 17 categorized signal types
- **Irrigable Items:** 347 total (300 questions + 10 PAs + 6 dimensions + 4 clusters + 17 signal types + 10 phases)

### Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    UnifiedOrchestrator                       │
├─────────────────────────────────────────────────────────────┤
│  UnifiedFactory → SignalDistributionOrchestrator            │
├─────────────────────────────────────────────────────────────┤
│  Gate 1 → Gate 2 → Gate 3 → Gate 4 → Consumer Distribution  │
└─────────────────────────────────────────────────────────────┘
```

### Performance Targets

| Metric | Target |
|--------|--------|
| Dead Letter Rate | < 10% |
| Error Rate | < 5% |
| Dispatch Latency (p99) | < 100ms |

## Document Conventions

- **MUST/SHALL:** Mandatory requirement
- **SHOULD:** Recommended but not required
- **MAY:** Optional feature
- **Signal:** A typed message carrying assessment data between components
- **Gate:** A validation checkpoint in the signal pipeline
- **Consumer:** A phase-specific signal processor

## Changelog

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-19 | Initial canonical specification |

---

*This document is the authoritative index for all SISAS Unification documentation.*
