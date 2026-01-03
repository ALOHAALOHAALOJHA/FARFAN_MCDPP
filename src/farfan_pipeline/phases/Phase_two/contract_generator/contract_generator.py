"""
Módulo: contract_generator.py
Propósito: Orquestador principal de generación de contratos
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Imports de módulos internos
from .input_registry import InputLoader, InputRegistry, SectorDefinition
from .method_expander import MethodExpander
from .chain_composer import ChainComposer
from .contract_assembler import ContractAssembler, GeneratedContract
from .contract_validator import ContractValidator, ValidationReport
from .json_emitter import JSONEmitter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ContractGenerator")


class ContractGenerator:
    """
    Orquestador principal de generación de contratos.

    FLUJO:
    1. Cargar y validar inputs
    2. Para cada pregunta:
       a. Obtener method_set asignado
       b. Expandir métodos
       c. Componer cadena epistémica
       d. Ensamblar contrato
       e. Validar contrato
    3. Emitir contratos válidos
    4. Emitir manifiesto

    INVARIANTES:
    - Fail-loud en cualquier error
    - Determinismo total
    - Sin inferencia de métodos
    - Preservación de orden
    """

    VERSION = "4.0.0-granular"

    def __init__(
        self,
        assets_path: Path,
        output_path: Path,
        strict_mode: bool = True,
    ):
        """
        Args:
            assets_path: Directorio con insumos
            output_path: Directorio de salida
            strict_mode: Si True, falla en cualquier warning
        """
        self.assets_path = assets_path
        self.output_path = output_path
        self.strict_mode = strict_mode

        # Timestamp de generación (único para toda la ejecución)
        self.generation_timestamp = datetime.now(timezone.utc).isoformat()

        # Componentes (inicializados en generate())
        self.registry: InputRegistry | None = None
        self.expander: MethodExpander | None = None
        self.composer: ChainComposer | None = None
        self.assembler: ContractAssembler | None = None
        self.validator: ContractValidator | None = None
        self.emitter: JSONEmitter | None = None

    def generate(self) -> dict[str, Any]:
        """
        Genera todos los contratos.

        Returns:
            Diccionario con estadísticas de generación

        Raises:
            ValueError: Si cualquier paso falla
            FileNotFoundError: Si inputs no existen
        """
        logger.info("=" * 60)
        logger.info("INICIANDO GENERACIÓN DE CONTRATOS")
        logger.info(f"Timestamp: {self.generation_timestamp}")
        logger.info(f"Assets: {self.assets_path}")
        logger.info(f"Output: {self.output_path}")
        logger.info("=" * 60)

        # Paso 1: Cargar inputs
        logger.info("Paso 1: Cargando inputs...")
        self._initialize_components()
        logger.info(f"  - Métodos cargados: {self.registry.total_methods}")
        logger.info(f"  - Contratos a generar: {self.registry.total_contracts}")
        logger.info(f"  - Hash classified_methods: {self.registry.classified_methods_hash}")
        logger.info(f"  - Hash contratos_clasificados: {self.registry.contratos_clasificados_hash}")
        logger.info(f"  - Hash method_sets: {self.registry.method_sets_hash}")

        # Paso 2: Generar contratos
        logger.info("Paso 2: Generando contratos...")
        contracts: list[GeneratedContract] = []
        reports: list[ValidationReport] = []

        # Obtener orden determinista de preguntas y sectores
        question_ids = sorted(self.registry.method_sets_by_question.keys())
        sectors = self.registry.sectors_ordered  # Ya está ordenado PA01-PA10

        # Contador global de contratos (1-300)
        contract_number = 0

        # BUCLE ANIDADO: 30 preguntas × 10 sectores = 300 contratos
        for q_idx, question_id in enumerate(question_ids, 1):
            for s_idx, sector in enumerate(sectors, 1):
                contract_number += 1

                logger.info(
                    f"  [{contract_number:03d}/300] Procesando {question_id} × {sector.sector_id} "
                    f"(Q{q_idx}/30, S{s_idx}/10)..."
                )

                try:
                    contract, report = self._generate_single_contract(
                        question_id, sector, contract_number
                    )
                    contracts.append(contract)
                    reports.append(report)

                    status = "✓" if report.is_valid else "✗"
                    logger.info(
                        f"    {status} {report.contract_id}: "
                        f"{report.passed_checks}/{report.total_checks} checks passed, "
                        f"{contract.method_binding.get('method_count')} methods"
                    )

                except Exception as e:
                    logger.error(f"    ✗ FALLO en {question_id} × {sector.sector_id}: {e}")
                    if self.strict_mode:
                        raise

        # Paso 3: Emitir contratos
        logger.info("Paso 3: Emitiendo contratos...")
        emitted_paths = []

        for contract, report in zip(contracts, reports):
            if report.is_valid:
                path = self.emitter.emit_contract(contract, report)
                emitted_paths.append(path)
                logger.info(f"  ✓ Emitido: {path.name}")
            else:
                logger.warning(
                    f"  ✗ NO emitido (inválido): {report.contract_id}"
                )

        # Paso 4: Emitir manifiesto
        logger.info("Paso 4: Emitiendo manifiesto...")
        manifest_path = self.emitter.emit_generation_manifest(
            contracts, reports, self.generation_timestamp
        )
        logger.info(f"  ✓ Manifiesto: {manifest_path.name}")

        # Estadísticas finales
        valid_count = sum(1 for r in reports if r.is_valid)
        invalid_count = len(reports) - valid_count

        logger.info("=" * 60)
        logger.info("GENERACIÓN COMPLETADA")
        logger.info(f"  Total contratos: {len(contracts)}")
        logger.info(f"  Válidos: {valid_count}")
        logger.info(f"  Inválidos: {invalid_count}")
        logger.info(f"  Archivos emitidos: {len(emitted_paths)}")
        logger.info("=" * 60)

        return {
            "timestamp": self.generation_timestamp,
            "total_contracts": len(contracts),
            "valid_contracts": valid_count,
            "invalid_contracts": invalid_count,
            "emitted_files": len(emitted_paths),
            "manifest_path": str(manifest_path),
        }

    def _initialize_components(self) -> None:
        """Inicializa todos los componentes"""
        loader = InputLoader(self.assets_path)
        self.registry = loader.load_and_validate()

        self.expander = MethodExpander(self.generation_timestamp)
        self.composer = ChainComposer(self.expander)
        self.assembler = ContractAssembler(
            self.registry,
            self.generation_timestamp,
            self.VERSION,
        )
        self.validator = ContractValidator()
        self.emitter = JSONEmitter(self.output_path)

    def _generate_single_contract(
        self, question_id: str, sector: "SectorDefinition", contract_number: int
    ) -> tuple[GeneratedContract, ValidationReport]:
        """
        Genera un único contrato.

        SECUENCIA:
        1. Obtener method_set del registry
        2. Obtener classification del registry
        3. Componer cadena epistémica
        4. Ensamblar contrato con sector específico
        5. Validar contrato

        Args:
            question_id: ID de la pregunta (D1_Q1, etc.)
            sector: Definición del sector de política pública
            contract_number: Número de contrato (1-300)
        """
        # Obtener datos del registry
        method_set = self.registry.method_sets_by_question[question_id]
        classification = self.registry.contracts_by_id[question_id]

        # Componer cadena epistémica (Layer 1 + Layer 2)
        chain = self.composer.compose_chain(method_set, classification)

        # Ensamblar contrato (Layer 3) con sector y número
        contract = self.assembler.assemble_contract(chain, classification, sector, contract_number)

        # Validar contrato (Layer 4)
        report = self.validator.validate_contract(contract)

        return contract, report


def main():
    """
    Punto de entrada principal.

    USO:
        python -m farfan_pipeline.phases.Phase_two.contract_generator.contract_generator \
            --assets /path/to/epistemological_assets \
            --output /path/to/output \
            [--strict]
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generador Granular de Contratos Ejecutores F.A.R.F.A.N"
    )
    parser.add_argument(
        "--assets",
        type=Path,
        required=True,
        help="Directorio con insumos epistemológicos"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directorio de salida para contratos"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Modo estricto: falla en cualquier warning"
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Modo permisivo: continúa con warnings"
    )

    args = parser.parse_args()

    generator = ContractGenerator(
        assets_path=args.assets,
        output_path=args.output,
        strict_mode=args.strict,
    )

    try:
        result = generator.generate()
        logger.info(f"Resultado: {result}")
        return 0
    except Exception as e:
        logger.error(f"FALLO CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
