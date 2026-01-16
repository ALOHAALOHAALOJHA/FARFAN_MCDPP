# Phase 4 Anomalies & Corrections

## 2026-01-16
- **Duplicados fuera del DAG**: `aggregation_validation.py`, `aggregation_provenance.py`, `choquet_adapter.py`, `uncertainty_quantification.py`.
  - **Acción**: eliminados. Se conservan solo los módulos canónicos `phase4_10_00_*`.
- **Folder no estándar**: `interface/`.
  - **Acción**: eliminado. El folder canónico es `interphase/`.
- **Notas de calibración/parametrización**: stubs y decoradores removidos en `phase4_10_00_aggregation.py`.
  - **Acción**: removidos por mandato “no parametrización” (constantes de negocio/presentación se mantienen).

## Pendiente
- **DAG visual**: generar `phase4_import_dag.png` con el comando de auditoría cuando se habilite ejecución.
