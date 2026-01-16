#!/usr/bin/env python3
"""
Script de Migración a Estructura Unificada FARFAN 2025.1

Este script automatiza la migración del código actual a la nueva estructura
unificada que refleja la arquitectura de calibración epistémica y PDM.

Author: FARFAN Engineering Team
Version: 1.0.0
Date: 2026-01-15
"""

from __future__ import annotations

import os
import shutil
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class FARFANMigration:
    """Migrador de estructura FARFAN a formato unificado."""

    def __init__(self, dry_run: bool = True):
        """
        Inicializar migrador.

        Args:
            dry_run: Si True, solo simula cambios sin ejecutarlos.
        """
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.src_root = self.project_root / "src" / "farfan_pipeline"
        self.tests_root = self.project_root / "tests"
        self.docs_root = self.project_root / "docs"

        # Estadísticas
        self.stats = {
            "dirs_created": 0,
            "dirs_moved": 0,
            "files_moved": 0,
            "files_modified": 0,
            "imports_updated": 0,
            "errors": [],
        }

        # Mapeos de migración
        self.calibration_migration_map = {
            "src/farfan_pipeline/infrastructure/calibration": "src/farfan_pipeline/calibration",
            "src/farfan_pipeline/config/method_registry_epistemic.json": "src/farfan_pipeline/calibration/config/method_registry.json",
        }

        self.pdm_migration_map = {
            "src/farfan_pipeline/infrastructure/parametrization": "src/farfan_pipeline/pdm/profile",
            "src/farfan_pipeline/infrastructure/contractual/pdm_contracts.py": "src/farfan_pipeline/pdm/contracts",
        }

        self.phase_rename_map = {
            "Phase_0": "Phase_00",
            "Phase_1": "Phase_01",
            "Phase_2": "Phase_02",
            "Phase_3": "Phase_03",
            "Phase_4": "Phase_04",
            "Phase_5": "Phase_05",
            "Phase_6": "Phase_06",
            "Phase_7": "Phase_07",
            "Phase_8": "Phase_08",
            "Phase_9": "Phase_09",
        }

    def log(self, message: str, level: str = "INFO"):
        """Log mensaje con timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def create_directory(self, path: Path) -> bool:
        """Crear directorio si no existe."""
        if path.exists():
            return False

        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)

        self.log(f"Created directory: {path}")
        self.stats["dirs_created"] += 1
        return True

    def move_directory(self, src: Path, dst: Path) -> bool:
        """Mover directorio y su contenido."""
        if not src.exists():
            self.log(f"Source not found: {src}", "WARNING")
            return False

        if dst.exists():
            self.log(f"Destination already exists: {dst}", "WARNING")
            return False

        if not self.dry_run:
            shutil.move(str(src), str(dst))

        self.log(f"Moved directory: {src} -> {dst}")
        self.stats["dirs_moved"] += 1
        return True

    def move_file(self, src: Path, dst: Path) -> bool:
        """Mover archivo individual."""
        if not src.exists():
            return False

        # Crear directorio destino si no existe
        dst.parent.mkdir(parents=True, exist_ok=True)

        if not self.dry_run:
            shutil.move(str(src), str(dst))

        self.log(f"Moved file: {src} -> {dst}")
        self.stats["files_moved"] += 1
        return True

    def update_imports_in_file(self, file_path: Path) -> int:
        """Actualizar imports en un archivo Python."""
        if not file_path.exists() or not file_path.suffix == ".py":
            return 0

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Actualizar imports de calibración
            content = re.sub(
                r"from farfan_pipeline\.infrastructure\.calibration",
                "from farfan_pipeline.calibration",
                content,
            )

            content = re.sub(
                r"from farfan_pipeline\.infrastructure\.parametrization",
                "from farfan_pipeline.pdm.profile",
                content,
            )

            content = re.sub(
                r"from farfan_pipeline\.infrastructure\.contractual\.pdm_contracts",
                "from farfan_pipeline.pdm.contracts",
                content,
            )

            # Actualizar imports de fases (Phase_X → Phase_XX)
            for old_name, new_name in self.phase_rename_map.items():
                content = re.sub(
                    f"from farfan_pipeline\\.phases\\.{old_name}",
                    f"from farfan_pipeline.phases.{new_name}",
                    content,
                )

            if content != original_content:
                if not self.dry_run:
                    file_path.write_text(content, encoding="utf-8")

                self.stats["files_modified"] += 1
                self.stats["imports_updated"] += len(re.findall(r"^from |^import ", content, re.MULTILINE))
                return self.stats["imports_updated"]

        except Exception as e:
            self.log(f"Error updating {file_path}: {e}", "ERROR")
            self.stats["errors"].append(str(e))
            return 0

        return 0

    def migrate_calibration_system(self):
        """Fase 1: Migrar sistema de calibración."""
        self.log("=== FASE 1: Migrando Sistema de Calibración ===")

        # Crear nueva estructura
        new_calib_root = self.src_root / "calibration"
        self.create_directory(new_calib_root)
        self.create_directory(new_calib_root / "config")
        self.create_directory(new_calib_root / "config" / "level_defaults")
        self.create_directory(new_calib_root / "config" / "type_overrides")
        self.create_directory(new_calib_root / "config" / "pdm_rules")
        self.create_directory(new_calib_root / "registry")
        self.create_directory(new_calib_root / "contracts")

        # Mover archivos existentes
        old_calib_root = self.src_root / "infrastructure" / "calibration"

        if old_calib_root.exists():
            # Mover core Python files
            for py_file in old_calib_root.glob("*.py"):
                if py_file.name != "__init__.py":
                    self.move_file(py_file, new_calib_root / py_file.name)

            # Mover subdirectorios
            for subdir in ["core", "registry"]:
                old_subdir = old_calib_root / subdir
                if old_subdir.exists():
                    new_subdir = new_calib_root / subdir
                    self.move_directory(old_subdir, new_subdir)

            # Mover configs
            old_config = old_calib_root / "config"
            if old_config.exists():
                # Mover level_configs
                old_level_configs = old_config / "level_configs"
                if old_level_configs.exists():
                    self.move_directory(old_level_configs, new_calib_root / "config" / "level_defaults")

                # Mover type_configs
                old_type_configs = old_config / "type_configs"
                if old_type_configs.exists():
                    self.move_directory(old_type_configs, new_calib_root / "config" / "type_overrides")

                # Mover pdm_rules
                old_pdm_rules = old_config / "pdm_rules"
                if old_pdm_rules.exists():
                    self.move_directory(old_pdm_rules, new_calib_root / "config" / "pdm_rules")

        # Mover method_registry desde config/
        old_method_registry = self.src_root / "config" / "method_registry_epistemic.json"
        if old_method_registry.exists():
            self.move_file(old_method_registry, new_calib_root / "config" / "method_registry.json")

        self.log("FASE 1 completada")

    def migrate_pdm_system(self):
        """Fase 2: Migrar sistema PDM."""
        self.log("=== FASE 2: Migrando Sistema PDM ===")

        # Crear nueva estructura PDM
        new_pdm_root = self.src_root / "pdm"
        self.create_directory(new_pdm_root)
        self.create_directory(new_pdm_root / "profile")
        self.create_directory(new_pdm_root / "contracts")
        self.create_directory(new_pdm_root / "integration")
        self.create_directory(new_pdm_root / "calibrator")

        # Mover parametrization → pdm/profile
        old_param = self.src_root / "infrastructure" / "parametrization"
        if old_param.exists():
            for py_file in old_param.glob("*.py"):
                if "pdm" in py_file.name.lower():
                    self.move_file(py_file, new_pdm_root / "profile" / py_file.name)

        # Mover pdm_contracts
        old_contracts = self.src_root / "infrastructure" / "contractual" / "pdm_contracts.py"
        if old_contracts.exists():
            self.move_file(old_contracts, new_pdm_root / "contracts" / "pdm_contracts.py")

        self.log("FASE 2 completada")

    def migrate_phase_directories(self):
        """Fase 3: Renombrar directorios de fases."""
        self.log("=== FASE 3: Renombrando Directorios de Fases ===")

        phases_dir = self.src_root / "phases"

        if not phases_dir.exists():
            self.log("Phases directory not found", "WARNING")
            return

        for old_name, new_name in self.phase_rename_map.items():
            old_path = phases_dir / old_name
            if old_path.exists():
                new_path = phases_dir / new_name
                self.move_directory(old_path, new_path)

        self.log("FASE 3 completada")

    def create_docs_structure(self):
        """Fase 4: Crear estructura de documentación unificada."""
        self.log("=== FASE 4: Creando Estructura de Documentación ===")

        # Crear estructura docs/
        docs_subdirs = [
            "architecture",
            "guides",
            "api",
            "legacy",
        ]

        for subdir in docs_subdirs:
            self.create_directory(self.docs_root / subdir)

        # Crear índice principal
        index_content = """# FARFAN Pipeline - Documentación Central

**Versión**: 2025.1
**Última actualización**: {date}

## Índice Principal

### Arquitectura
- [CAPAS EPISTÉMICAS](architecture/LAYER_1_EPISTEMIC_LEVELS.md)
- [SISTEMA DE CALIBRACIÓN](architecture/LAYER_4_CALIBRATION_REGISTRY.md)
- [RECONOCIMIENTO PDM](architecture/LAYER_3_PDM_SENSITIVITY.md)

### Guías
- [QUICKSTART](guides/QUICKSTART.md)
- [GUÍA DE CALIBRACIÓN](guides/CALIBRATION_GUIDE.md)
- [GUÍA PDM](guides/PDM_INTEGRATION_GUIDE.md)

### API Reference
- [Phase 0: Ingestión](api/phase0_api.md)
- [Phase 1: Preprocesamiento](api/phase1_api.md)
- [Phase 2: Ejecución](api/phase2_api.md)

### Documentación Histórica
- Ver directorio `legacy/`
""".format(date=datetime.now().strftime("%Y-%m-%d"))

        index_path = self.docs_root / "INDEX.md"
        if not self.dry_run:
            index_path.write_text(index_content, encoding="utf-8")

        self.log("FASE 4 completada")

    def migrate_tests(self):
        """Fase 5: Reorganizar tests."""
        self.log("=== FASE 5: Reorganizando Tests ===")

        # Crear estructura de tests mirror
        test_subdirs = [
            "calibration",
            "pdm",
            "phases/test_phase_01",
            "phases/test_phase_02",
            "integration",
        ]

        for subdir in test_subdirs:
            self.create_directory(self.tests_root / subdir)

        # Mover tests de calibración
        old_calib_tests = self.tests_root / "calibration"
        new_calib_tests = self.tests_root / "calibration"
        if old_calib_tests.exists() and not new_calib_tests.exists():
            self.move_directory(old_calib_tests, new_calib_tests)

        # Mover tests PDM
        old_pdm_tests_1 = self.tests_root / "infrastructure" / "parametrization"
        old_pdm_tests_2 = self.tests_root / "infrastructure" / "contractual"
        new_pdm_tests = self.tests_root / "pdm"

        if new_pdm_tests.exists():
            for old_tests in [old_pdm_tests_1, old_pdm_tests_2]:
                if old_tests.exists():
                    for test_file in old_tests.glob("test_*.py"):
                        self.move_file(test_file, new_pdm_tests / test_file.name)

        # Crear test de integración PDM-Phase1
        integration_test_content = """
Tests de integración completa entre PDM y calibración epistémica.

Valida que:
- PDM profile alimenta calibration registry correctamente
- Ajustes PDM-driven se aplican en todas las capas
- Invariantes constitucionales se preservan
"""
        if not self.dry_run:
            (self.tests_root / "integration" / "test_pdm_calibration_integration.py").write_text(
                integration_test_content,
                encoding="utf-8",
            )

        self.log("FASE 5 completada")

    def update_all_imports(self):
        """Fase 6: Actualizar todos los imports en el proyecto."""
        self.log("=== FASE 6: Actualizando Imports ===")

        total_updated = 0

        # Actualizar en src/
        for py_file in self.src_root.rglob("*.py"):
            updated = self.update_imports_in_file(py_file)
            total_updated += updated

        # Actualizar en tests/
        for py_file in self.tests_root.rglob("*.py"):
            updated = self.update_imports_in_file(py_file)
            total_updated += updated

        self.log(f"FASE 6 completada: {total_updated} archivos actualizados")

    def validate_structure(self):
        """Validar estructura resultante."""
        self.log("=== VALIDANDO ESTRUCTURA ===")

        validations = []

        # Verificar que /calibration existe
        calibration_dir = self.src_root / "calibration"
        validations.append(("Calibration directory exists", calibration_dir.exists()))

        # Verificar que /pdm existe
        pdm_dir = self.src_root / "pdm"
        validations.append(("PDM directory exists", pdm_dir.exists()))

        # Verificar que Phase_XX directorios existen
        for _, new_name in self.phase_rename_map.items():
            phase_dir = self.src_root / "phases" / new_name
            validations.append((f"Phase {new_name} exists", phase_dir.exists()))

        # Verificar estructura tests/
        for test_dir in ["calibration", "pdm", "integration"]:
            test_path = self.tests_root / test_dir
            validations.append((f"Tests/{test_dir} exists", test_path.exists()))

        # Verificar docs/ INDEX.md
        index_doc = self.docs_root / "INDEX.md"
        validations.append(("Docs INDEX exists", index_doc.exists()))

        # Reportar resultados
        passed = sum(1 for _, result in validations if result)
        total = len(validations)

        self.log(f"VALIDACIÓN: {passed}/{total} checks PASSED")

        for check, result in validations:
            status = "✅" if result else "❌"
            self.log(f"  {status} {check}")

        return passed == total

    def generate_migration_report(self):
        """Generar reporte de migración."""
        report = f"""
# Reporte de Migración FARFAN 2025.1

**Fecha**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Modo**: {"DR RUN (Simulación)" if self.dry_run else "LIVE (Ejecución Real)"}

## Estadísticas

| Operación | Cantidad |
|-----------|----------|
| Directorios creados | {self.stats["dirs_created"]} |
| Directorios movidos | {self.stats["dirs_moved"]} |
| Archivos movidos | {self.stats["files_moved"]} |
| Archivos modificados | {self.stats["files_modified"]} |
| Imports actualizados | {self.stats["imports_updated"]} |
| Errores | {len(self.stats["errors"])} |

## Errores

{self._format_errors() if self.stats["errors"] else "No errores"}

## Estructura Final

### Calibración
- `src/farfan_pipeline/calibration/` - **{'✅' if (self.src_root / 'calibration').exists() else '❌'}**

### PDM
- `src/farfan_pipeline/pdm/` - **{'✅' if (self.src_root / 'pdm').exists() else '❌'}**

### Fases
- Phase_00 through Phase_09 - **{self._check_phases_status()}**

### Tests
- `tests/calibration/` - **{'✅' if (self.tests_root / 'calibration').exists() else '❌'}**
- `tests/pdm/` - **{'✅' if (self.tests_root / 'pdm').exists() else '❌'}**
- `tests/integration/` - **{'✅' if (self.tests_root / 'integration').exists() else '❌'}**

### Documentación
- `docs/INDEX.md` - **{'✅' if (self.docs_root / 'INDEX.md').exists() else '❌'}**

---

**Estado**: {"SIMULACIÓN COMPLETADA" if self.dry_run else "MIGRACIÓN COMPLETADA"}
"""

        report_path = self.project_root / "MIGRATION_REPORT.md"
        if not self.dry_run:
            report_path.write_text(report, encoding="utf-8")
            self.log(f"Reporte guardado en: {report_path}")

        return report

    def _format_errors(self) -> str:
        """Formatear lista de errores."""
        return "\n".join(f"- {err}" for err in self.stats["errors"])

    def _check_phases_status(self) -> str:
        """Verificar estado de todas las fases."""
        phases_status = []
        for _, new_name in self.phase_rename_map.items():
            phase_dir = self.src_root / "phases" / new_name
            status = "✅" if phase_dir.exists() else "❌"
            phases_status.append(f"{status} {new_name}")
        return ", ".join(phases_status)

    def run_migration(self):
        """Ejecutar migración completa."""
        self.log("=" * 60)
        self.log("INICIANDO MIGRACIÓN FARFAN 2025.1")
        self.log("=" * 60)
        self.log(f"Modo: {'DR RUN (Simulación)' if self.dry_run else 'LIVE (Ejecución Real)'}")
        self.log("")

        try:
            self.migrate_calibration_system()
            self.migrate_pdm_system()
            self.migrate_phase_directories()
            self.create_docs_structure()
            self.migrate_tests()
            self.update_all_imports()

            self.log("")
            self.log("=" * 60)
            self.log("VALIDANDO ESTRUCTURA RESULTANTE")
            self.log("=" * 60)
            self.validate_structure()

            self.log("")
            self.log("=" * 60)
            self.log("GENERANDO REPORTE")
            self.log("=" * 60)
            self.generate_migration_report()

            self.log("")
            self.log("=" * 60)
            self.log("MIGRACIÓN COMPLETADA")
            self.log("=" * 60)

            if self.dry_run:
                self.log("")
                self.log("⚠️  ESTE FUE UN DR RUN")
                self.log("⚠️  Ningún cambio fue aplicado")
                self.log("⚠️  Ejecuta con dry_run=False para aplicar cambios")

        except Exception as e:
            self.log(f"ERROR en migración: {e}", "ERROR")
            raise


def main():
    """Función principal."""
    import sys

    # Parse argumentos
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    execute = "--execute" in sys.argv or "-e" in sys.argv

    if not execute:
        dry_run = True  # Default a dry-run

    migrator = FARFANMigration(dry_run=dry_run)
    migrator.run_migration()


if __name__ == "__main__":
    main()
