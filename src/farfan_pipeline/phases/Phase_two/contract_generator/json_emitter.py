"""
Módulo: json_emitter.py
Propósito: Emitir contratos como JSON determinista
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class JSONEmitter:
    """
    Emisor de contratos JSON.

    PROPIEDADES:
    1. Determinista: misma entrada → mismo output byte-a-byte
    2. Ordenado: claves en orden consistente
    3. Legible: indentación de 2 espacios
    4. UTF-8: encoding explícito
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def emit_contract(
        self,
        contract: "GeneratedContract",
        validation_report: "ValidationReport",
    ) -> Path:
        """
        Emite contrato como archivo JSON.

        NAMING: {dimension}_{question}_contract_v4.json
        e.g., D1_Q1_contract_v4.json

        Args:
            contract: GeneratedContract a emitir
            validation_report: ValidationReport para incluir status

        Returns:
            Path al archivo emitido

        Raises:
            ValueError: Si validación tiene critical failures
        """
        if not validation_report.is_valid:
            raise ValueError(
                f"Cannot emit contract {validation_report.contract_id}: "
                f"{validation_report.critical_failures} critical failures"
            )

        # Construir nombre de archivo
        base_slot = contract.identity.get("base_slot", "UNKNOWN")
        filename = f"{base_slot.replace('-', '_')}_contract_v4.json"
        output_path = self.output_dir / filename

        # Construir diccionario final con validation status
        contract_dict = contract.to_dict()
        contract_dict["audit_annotations"]["audit_checklist"] = {
            "structure_validated": True,
            "epistemic_coherence_validated": True,
            "temporal_validity_validated": True,
            "cross_reference_validated": True,
            "validation_pass_rate": validation_report.pass_rate,
            "validation_timestamp": contract.identity.get("created_at"),
        }

        # Emitir con formato determinista
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                contract_dict,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,  # Preservar orden de inserción
            )
            f.write("\n")  # Trailing newline

        return output_path

    def emit_generation_manifest(
        self,
        contracts: list["GeneratedContract"],
        reports: list["ValidationReport"],
        generation_timestamp: str,
    ) -> Path:
        """
        Emite manifiesto de generación.

        El manifiesto contiene:
        - Lista de contratos generados
        - Estadísticas de validación
        - Hashes de inputs
        """
        manifest = {
            "generation_metadata": {
                "timestamp": generation_timestamp,
                "total_contracts": len(contracts),
                "valid_contracts": sum(1 for r in reports if r.is_valid),
                "invalid_contracts": sum(1 for r in reports if not r.is_valid),
            },
            "contracts": [
                {
                    "contract_id": c.identity.get("representative_question_id"),
                    "question_id": c.identity.get("base_slot"),
                    "type": c.identity.get("contract_type"),
                    "method_count": c.method_binding.get("method_count"),
                    "efficiency_score": c.method_binding.get("efficiency_score"),
                    "validation_pass_rate": r.pass_rate,
                    "is_valid": r.is_valid,
                }
                for c, r in zip(contracts, reports)
            ],
            "input_hashes": contracts[0].audit_annotations.get(
                "generation_metadata", {}
            ).get("input_hashes", {}) if contracts else {},
        }

        output_path = self.output_dir / "generation_manifest.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")

        return output_path
