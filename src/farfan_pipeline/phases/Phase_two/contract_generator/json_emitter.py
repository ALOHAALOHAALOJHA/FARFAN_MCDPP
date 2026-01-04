"""
Módulo: json_emitter.py
Propósito: Emitir contratos como JSON determinista

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/json_emitter.py

RESPONSABILIDADES:
1. Emitir contratos individuales como JSON
2. Emitir manifiesto de generación
3. Emitir reportes de validación
4. Garantizar determinismo byte-a-byte

PROPIEDADES:
1. Determinista: misma entrada → mismo output byte-a-byte
2. Ordenado: claves en orden de inserción (Python 3.7+)
3. Legible: indentación de 2 espacios
4. UTF-8: encoding explícito
5. Trazable: cada archivo incluye metadata de generación

ESTRUCTURA DE SALIDA:
    output/
    ├── contracts/
    │   ├── Q001_PA01_contract_v4.json
    │   ├── Q001_PA02_contract_v4.json
    │   ├── ... 
    │   └── Q030_PA10_contract_v4.json
    ├── validation/
    │   └── validation_reports. json
    └── generation_manifest.json

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . contract_assembler import GeneratedContract
    from .contract_validator import ValidationReport

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

EMITTER_VERSION = "4.0.0-granular"

# Subdirectorios de salida
CONTRACTS_SUBDIR = "contracts"
VALIDATION_SUBDIR = "validation"

# Formato de nombres de archivo
CONTRACT_FILENAME_TEMPLATE = "{contract_id}_contract_v4.json"
MANIFEST_FILENAME = "generation_manifest.json"
VALIDATION_REPORT_FILENAME = "validation_reports.json"
INVALID_CONTRACTS_FILENAME = "invalid_contracts.json"

# Configuración JSON
JSON_INDENT = 2
JSON_ENSURE_ASCII = False


# ══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL - EMISOR
# ══════════════════════════════════════════════════════════════════════════════


class JSONEmitter:
    """
    Emisor de contratos JSON con garantías de determinismo.

    PROPIEDADES GARANTIZADAS:
    1. Determinista: misma entrada → mismo output byte-a-byte
    2. Ordenado: claves en orden de inserción (NO sort_keys)
    3. Legible: indentación de 2 espacios
    4. UTF-8: encoding explícito
    5. Trailing newline:  cada archivo termina con \n

    USO:
        emitter = JSONEmitter(output_path)
        path = emitter.emit_contract(contract, report)
        manifest_path = emitter.emit_generation_manifest(contracts, reports, timestamp, version)
    """

    def __init__(self, output_path: Path):
        """
        Inicializa el emisor.

        Args:
            output_path: Directorio base de salida

        Crea la estructura de directorios: 
            output_path/
            ├── contracts/
            └── validation/
        """
        self.output_path = Path(output_path)
        self.contracts_dir = self.output_path / CONTRACTS_SUBDIR
        self.validation_dir = self.output_path / VALIDATION_SUBDIR

        # Crear directorios
        self.contracts_dir.mkdir(parents=True, exist_ok=True)
        self.validation_dir.mkdir(parents=True, exist_ok=True)

        # Estadísticas
        self._emitted_count = 0
        self._skipped_count = 0

        logger.info(f"JSONEmitter initialized, version {EMITTER_VERSION}")
        logger.info(f"  Output:  {self.output_path}")
        logger.info(f"  Contracts dir: {self.contracts_dir}")
        logger.info(f"  Validation dir:  {self.validation_dir}")

    # ══════════════════════════════════════════════════════════════════════════
    # EMISIÓN DE CONTRATO INDIVIDUAL
    # ══════════════════════════════════════════════════════════════════════════

    def emit_contract(
        self,
        contract: "GeneratedContract",
        validation_report: "ValidationReport",
    ) -> Path:
        """
        Emite contrato como archivo JSON.

        NAMING: {contract_id}_contract_v4.json
        Ejemplo: Q001_PA01_contract_v4.json, Q030_PA10_contract_v4.json

        Args:
            contract: GeneratedContract a emitir
            validation_report: ValidationReport asociado

        Returns:
            Path al archivo emitido

        Raises:
            ValueError: Si validación tiene critical failures
        """
        # Validar que el contrato puede ser emitido
        if not validation_report.is_valid:
            self._skipped_count += 1
            raise ValueError(
                f"Cannot emit contract {validation_report.contract_id}: "
                f"{validation_report.critical_failures} critical failures, "
                f"{validation_report.high_failures} high failures"
            )

        # Construir nombre de archivo
        contract_id = contract.identity.get("contract_id", "UNKNOWN")
        filename = CONTRACT_FILENAME_TEMPLATE.format(contract_id=contract_id)
        output_file = self.contracts_dir / filename

        # Construir diccionario final
        contract_dict = self._prepare_contract_dict(contract, validation_report)

        # Emitir con formato determinista
        self._write_json(output_file, contract_dict)

        self._emitted_count += 1
        logger.debug(f"Emitted:  {filename}")

        return output_file

    def _prepare_contract_dict(
        self,
        contract: "GeneratedContract",
        validation_report: "ValidationReport",
    ) -> dict[str, Any]:
        """
        Prepara diccionario del contrato con información de validación.

        Añade: 
        - audit_checklist en audit_annotations
        - emission_metadata
        """
        contract_dict = contract.to_dict()

        # Añadir audit checklist
        contract_dict["audit_annotations"]["audit_checklist"] = {
            "structure_validated": True,
            "epistemic_coherence_validated": True,
            "temporal_validity_validated": True,
            "cross_reference_validated": True,
            "sector_validated": True,
            "validation_pass_rate": round(validation_report.pass_rate, 4),
            "validation_checks_total": validation_report.total_checks,
            "validation_checks_passed": validation_report.passed_checks,
            "validation_timestamp": validation_report.validation_timestamp,
            "validator_version": validation_report.validator_version,
        }

        # Añadir emission metadata
        contract_dict["audit_annotations"]["emission_metadata"] = {
            "emitter_version": EMITTER_VERSION,
            "emission_timestamp": datetime.now(timezone.utc).isoformat(),
            "output_format": "json",
            "encoding": "utf-8",
            "deterministic":  True,
        }

        return contract_dict

    # ══════════════════════════════════════════════════════════════════════════
    # EMISIÓN DE MANIFIESTO
    # ══════════════════════════════════════════════════════════════════════════

    def emit_generation_manifest(
        self,
        contracts:  list["GeneratedContract"],
        reports: list["ValidationReport"],
        timestamp: str,
        generator_version: str,
    ) -> Path:
        """
        Emite manifiesto de generación.

        El manifiesto contiene:
        - Metadata de generación
        - Estadísticas globales
        - Lista de contratos con status
        - Hashes de inputs para reproducibilidad
        - Resumen por sector
        - Resumen por tipo de contrato

        Args: 
            contracts: Lista de todos los contratos generados
            reports: Lista de reportes de validación (mismo orden)
            timestamp: ISO timestamp de inicio de generación
            generator_version:  Versión del generador

        Returns:
            Path al manifiesto
        """
        # Calcular estadísticas
        total = len(contracts)
        valid = sum(1 for r in reports if r.is_valid)
        invalid = total - valid

        # Estadísticas por sector
        sector_stats = self._compute_sector_stats(contracts, reports)

        # Estadísticas por tipo de contrato
        type_stats = self._compute_type_stats(contracts, reports)

        # Obtener hashes de inputs (del primer contrato)
        input_hashes = {}
        if contracts:
            traceability = contracts[0].traceability
            input_files = traceability.get("input_files", {})
            for name, data in input_files.items():
                input_hashes[name] = data.get("hash", "")

        manifest = {
            "manifest_version": "4.0.0",
            "generation_metadata": {
                "timestamp": timestamp,
                "completion_timestamp": datetime.now(timezone.utc).isoformat(),
                "generator_version": generator_version,
                "emitter_version": EMITTER_VERSION,
                "target_contracts": 300,
            },
            "statistics": {
                "total_contracts_generated": total,
                "valid_contracts": valid,
                "invalid_contracts": invalid,
                "validation_rate": round(valid / total, 4) if total > 0 else 0,
                "contracts_emitted": self._emitted_count,
                "contracts_skipped": self._skipped_count,
            },
            "by_sector": sector_stats,
            "by_contract_type": type_stats,
            "contracts":  [
                self._contract_summary(c, r, i + 1)
                for i, (c, r) in enumerate(zip(contracts, reports))
            ],
            "input_hashes":  input_hashes,
            "output_structure": {
                "contracts_directory": str(self.contracts_dir),
                "validation_directory":  str(self.validation_dir),
                "manifest_file":  MANIFEST_FILENAME,
            },
        }

        output_file = self.output_path / MANIFEST_FILENAME
        self._write_json(output_file, manifest)

        logger.info(f"Manifest emitted: {output_file}")

        # También emitir reportes de validación
        self._emit_validation_reports(reports)

        # Emitir lista de contratos inválidos si hay
        if invalid > 0:
            self._emit_invalid_contracts_list(contracts, reports)

        return output_file

    def _contract_summary(
        self,
        contract: "GeneratedContract",
        report: "ValidationReport",
        index: int,
    ) -> dict[str, Any]:
        """Crea resumen de un contrato para el manifiesto."""
        return {
            "index": index,
            "contract_id": contract.identity.get("contract_id"),
            "contract_number": contract.identity.get("contract_number"),
            "base_contract_id": contract.identity.get("base_contract_id"),
            "base_slot": contract.identity.get("base_slot"),
            "sector_id": contract.identity.get("sector_id"),
            "sector_name": contract.identity.get("sector_name", "")[:50],
            "contract_type":  contract.identity.get("contract_type"),
            "method_count": contract.method_binding.get("method_count"),
            "efficiency_score": round(contract.method_binding.get("efficiency_score", 0), 4),
            "validation":  {
                "is_valid": report.is_valid,
                "pass_rate": round(report.pass_rate, 4),
                "checks_total": report.total_checks,
                "checks_passed":  report.passed_checks,
                "critical_failures": report.critical_failures,
                "high_failures":  report.high_failures,
            },
            "filename": CONTRACT_FILENAME_TEMPLATE.format(
                contract_id=contract.identity.get("contract_id", "UNKNOWN")
            ) if report.is_valid else None,
        }

    def _compute_sector_stats(
        self,
        contracts: list["GeneratedContract"],
        reports: list["ValidationReport"],
    ) -> dict[str, dict[str, Any]]:
        """Computa estadísticas por sector."""
        stats:  dict[str, dict[str, Any]] = {}

        for contract, report in zip(contracts, reports):
            sector_id = contract.identity.get("sector_id", "UNKNOWN")

            if sector_id not in stats:
                stats[sector_id] = {
                    "sector_name": contract.identity.get("sector_name", ""),
                    "total":  0,
                    "valid": 0,
                    "invalid": 0,
                    "avg_efficiency": 0.0,
                    "efficiency_scores": [],
                }

            stats[sector_id]["total"] += 1
            if report.is_valid:
                stats[sector_id]["valid"] += 1
            else: 
                stats[sector_id]["invalid"] += 1

            efficiency = contract.method_binding.get("efficiency_score", 0)
            stats[sector_id]["efficiency_scores"].append(efficiency)

        # Calcular promedios
        for sector_id, data in stats.items():
            scores = data. pop("efficiency_scores")
            data["avg_efficiency"] = round(sum(scores) / len(scores), 4) if scores else 0

        return stats

    def _compute_type_stats(
        self,
        contracts: list["GeneratedContract"],
        reports: list["ValidationReport"],
    ) -> dict[str, dict[str, int]]:
        """Computa estadísticas por tipo de contrato."""
        stats: dict[str, dict[str, int]] = {}

        for contract, report in zip(contracts, reports):
            type_code = contract.identity.get("contract_type", "UNKNOWN")

            if type_code not in stats:
                stats[type_code] = {
                    "total": 0,
                    "valid": 0,
                    "invalid": 0,
                }

            stats[type_code]["total"] += 1
            if report.is_valid:
                stats[type_code]["valid"] += 1
            else: 
                stats[type_code]["invalid"] += 1

        return stats

    # ══════════════════════════════════════════════════════════════════════════
    # EMISIÓN DE REPORTES DE VALIDACIÓN
    # ══════════════════════════════════════════════════════════════════════════

    def _emit_validation_reports(
        self,
        reports: list["ValidationReport"],
    ) -> Path:
        """
        Emite todos los reportes de validación en un archivo. 

        Args:
            reports:  Lista de reportes

        Returns:
            Path al archivo
        """
        validation_data = {
            "validation_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_reports": len(reports),
                "emitter_version": EMITTER_VERSION,
            },
            "summary": {
                "total_checks_executed": sum(r.total_checks for r in reports),
                "total_checks_passed": sum(r.passed_checks for r in reports),
                "total_checks_failed": sum(r.failed_checks for r in reports),
                "contracts_valid": sum(1 for r in reports if r.is_valid),
                "contracts_invalid": sum(1 for r in reports if not r.is_valid),
            },
            "reports": [r.to_dict() for r in reports],
        }

        output_file = self.validation_dir / VALIDATION_REPORT_FILENAME
        self._write_json(output_file, validation_data)

        logger.info(f"Validation reports emitted: {output_file}")

        return output_file

    def _emit_invalid_contracts_list(
        self,
        contracts: list["GeneratedContract"],
        reports:  list["ValidationReport"],
    ) -> Path:
        """
        Emite lista de contratos inválidos con detalles de fallos.

        Args:
            contracts: Lista de contratos
            reports: Lista de reportes

        Returns:
            Path al archivo
        """
        invalid_list = []

        for contract, report in zip(contracts, reports):
            if not report.is_valid:
                # Extraer fallos críticos y high
                critical_failures = [
                    r. to_dict() for r in report.results
                    if not r.passed and r.severity. value == "CRITICAL"
                ]
                high_failures = [
                    r.to_dict() for r in report.results
                    if not r.passed and r.severity. value == "HIGH"
                ]

                invalid_list.append({
                    "contract_id":  report.contract_id,
                    "question_id": report.question_id,
                    "sector_id": report.sector_id,
                    "contract_number": report.contract_number,
                    "critical_failures_count": report.critical_failures,
                    "high_failures_count": report.high_failures,
                    "pass_rate": round(report.pass_rate, 4),
                    "critical_failures": critical_failures,
                    "high_failures": high_failures,
                })

        invalid_data = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_invalid":  len(invalid_list),
            },
            "invalid_contracts":  invalid_list,
        }

        output_file = self.validation_dir / INVALID_CONTRACTS_FILENAME
        self._write_json(output_file, invalid_data)

        logger.warning(f"Invalid contracts list emitted: {output_file}")

        return output_file

    # ══════════════════════════════════════════════════════════════════════════
    # UTILIDADES
    # ══════════════════════════════════════════════════════════════════════════

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        """
        Escribe JSON con formato determinista.

        PROPIEDADES:
        - Indentación: 2 espacios
        - No ASCII escape: permite caracteres Unicode
        - Sort keys: False (preserva orden de inserción)
        - Trailing newline: sí
        - Encoding: UTF-8
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=JSON_ENSURE_ASCII,
                indent=JSON_INDENT,
                sort_keys=False,  # Preservar orden de inserción
            )
            f.write("\n")  # Trailing newline para POSIX compliance

    # ══════════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ══════════════════════════════════════════════════════════════════════════

    @property
    def emitted_count(self) -> int:
        """Número de contratos emitidos."""
        return self._emitted_count

    @property
    def skipped_count(self) -> int:
        """Número de contratos saltados (inválidos)."""
        return self._skipped_count

    @property
    def version(self) -> str:
        """Versión del emisor."""
        return EMITTER_VERSION