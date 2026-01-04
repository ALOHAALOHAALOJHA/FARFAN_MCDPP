"""
Módulo: contract_generator.py
Propósito: Orquestador principal de generación de 300 contratos ejecutores

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/contract_generator.py

RESPONSABILIDADES:
1. Cargar y validar todos los inputs (método, contratos, sectores)
2. Para cada combinación (pregunta × sector):
   a. Obtener method_set asignado
   b. Expandir métodos
   c. Componer cadena epistémica
   d. Ensamblar contrato con sector embebido
   e. Validar contrato
3. Emitir contratos válidos
4. Emitir manifiesto de generación

OBJETIVO:  300 CONTRATOS = 30 preguntas × 10 sectores

INVARIANTES:
- Fail-loud en cualquier error
- Determinismo total (misma entrada → misma salida)
- Sin inferencia de métodos
- Preservación de orden
- Cada contrato tiene sector embebido con patterns/regex distintos

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Imports de módulos internos
from .input_registry import InputLoader, InputRegistry, SectorDefinition
from .method_expander import MethodExpander
from .chain_composer import ChainComposer, EpistemicChain
from . contract_assembler import ContractAssembler, GeneratedContract
from .contract_validator import ContractValidator, ValidationReport
from .json_emitter import JSONEmitter

if TYPE_CHECKING:
    from .input_registry import ContractClassification, QuestionMethodSet

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE LOGGING
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ContractGenerator")


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

GENERATOR_VERSION = "4.0.0-granular"

# Total esperado de contratos
EXPECTED_BASE_CONTRACTS = 30  # Preguntas
EXPECTED_SECTORS = 10  # Sectores de política
EXPECTED_TOTAL_CONTRACTS = EXPECTED_BASE_CONTRACTS * EXPECTED_SECTORS  # 300


# ══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL - ORQUESTADOR
# ══════════════════════════════════════════════════════════════════════════════


class ContractGenerator:
    """
    Orquestador principal de generación de 300 contratos ejecutores. 

    FLUJO DE GENERACIÓN:
    1. Cargar y validar inputs (métodos, contratos, sectores)
    2. Inicializar componentes (expander, composer, assembler, validator, emitter)
    3. Para cada pregunta (30):
       a. Obtener method_set asignado
       b. Obtener classification
       c. Componer cadena epistémica (UNA VEZ - métodos son iguales)
       d. Para cada sector (10):
          i.   Ensamblar contrato con sector embebido
          ii. Validar contrato
          iii. Emitir contrato si válido
    4. Emitir manifiesto de generación
    5. Reportar estadísticas

    INVARIANTES: 
    - Fail-loud en cualquier error (modo estricto)
    - Determinismo total:  misma entrada → misma salida byte-idéntica
    - Sin inferencia de métodos:  solo usa lo que está en inputs
    - Preservación de orden: métodos en orden exacto de input

    USO:
        generator = ContractGenerator(assets_path, output_path)
        result = generator.generate()
    """

    def __init__(
        self,
        assets_path: Path,
        output_path: Path,
        strict_mode: bool = True,
    ):
        """
        Inicializa el generador. 

        Args:
            assets_path: Directorio con insumos epistemológicos
            output_path: Directorio de salida para contratos
            strict_mode:  Si True, falla en cualquier warning (recomendado)
        """
        self.assets_path = Path(assets_path)
        self.output_path = Path(output_path)
        self.strict_mode = strict_mode

        # Timestamp de generación (único para toda la ejecución)
        self.generation_timestamp = datetime.now(timezone.utc).isoformat()

        # Componentes (inicializados en _initialize_components)
        self.registry: InputRegistry | None = None
        self. expander: MethodExpander | None = None
        self.composer: ChainComposer | None = None
        self.assembler: ContractAssembler | None = None
        self.validator: ContractValidator | None = None
        self.emitter: JSONEmitter | None = None

        # Estadísticas de generación
        self._stats = {
            "contracts_generated": 0,
            "contracts_valid": 0,
            "contracts_invalid": 0,
            "contracts_emitted": 0,
            "validation_failures": [],
        }

        logger.info(f"ContractGenerator initialized, version {GENERATOR_VERSION}")

    def generate(self) -> dict[str, Any]:
        """
        Genera todos los 300 contratos.

        SECUENCIA:
        1. Cargar y validar inputs
        2. Inicializar componentes
        3.  Generar contratos (30 preguntas × 10 sectores)
        4. Emitir manifiesto
        5. Retornar estadísticas

        Returns:
            Diccionario con estadísticas de generación: 
            - timestamp: ISO timestamp de generación
            - total_contracts: Total de contratos intentados
            - valid_contracts:  Contratos que pasaron validación
            - invalid_contracts: Contratos que fallaron validación
            - emitted_files: Archivos JSON emitidos
            - manifest_path: Path al manifiesto

        Raises:
            ValueError: Si cualquier paso falla y strict_mode=True
            FileNotFoundError: Si inputs no existen
        """
        self._log_banner("INICIANDO GENERACIÓN DE 300 CONTRATOS EJECUTORES")
        logger.info(f"Timestamp: {self. generation_timestamp}")
        logger.info(f"Assets: {self.assets_path}")
        logger.info(f"Output: {self.output_path}")
        logger.info(f"Strict mode: {self.strict_mode}")

        # ══════════════════════════════════════════════════════════════════
        # PASO 1: CARGAR Y VALIDAR INPUTS
        # ══════════════════════════════════════════════════════════════════
        self._log_step(1, "Cargando y validando inputs")
        self._initialize_components()
        self._log_registry_stats()

        # ══════════════════════════════════════════════════════════════════
        # PASO 2: GENERAR CONTRATOS (30 × 10 = 300)
        # ══════════════════════════════════════════════════════════════════
        self._log_step(2, "Generando contratos")
        contracts, reports = self._generate_all_contracts()

        # ══════════════════════════════════════════════════════════════════
        # PASO 3: EMITIR CONTRATOS VÁLIDOS
        # ══════════════════════════════════════════════════════════════════
        self._log_step(3, "Emitiendo contratos válidos")
        emitted_paths = self._emit_valid_contracts(contracts, reports)

        # ══════════════════════════════════════════════════════════════════
        # PASO 4: EMITIR MANIFIESTO
        # ══════════════════════════════════════════════════════════════════
        self._log_step(4, "Emitiendo manifiesto de generación")
        manifest_path = self. emitter.emit_generation_manifest(
            contracts=contracts,
            reports=reports,
            timestamp=self.generation_timestamp,
            generator_version=GENERATOR_VERSION,
        )
        logger.info(f"  ✓ Manifiesto: {manifest_path.name}")

        # ══════════════════════════════════════════════════════════════════
        # PASO 5: REPORTAR ESTADÍSTICAS
        # ══════════════════════════════════════════════════════════════════
        self._log_final_stats(contracts, reports, emitted_paths, manifest_path)

        return {
            "timestamp": self.generation_timestamp,
            "generator_version": GENERATOR_VERSION,
            "total_contracts": len(contracts),
            "valid_contracts": self._stats["contracts_valid"],
            "invalid_contracts": self._stats["contracts_invalid"],
            "emitted_files": len(emitted_paths),
            "manifest_path": str(manifest_path),
            "input_hashes": {
                "classified_methods": self. registry.classified_methods_hash,
                "contratos_clasificados": self.registry.contratos_clasificados_hash,
                "method_sets": self.registry.method_sets_hash,
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # INICIALIZACIÓN DE COMPONENTES
    # ══════════════════════════════════════════════════════════════════════════

    def _initialize_components(self) -> None:
        """
        Inicializa todos los componentes del generador. 

        ORDEN DE INICIALIZACIÓN:
        1. InputLoader → InputRegistry
        2. MethodExpander
        3. ChainComposer (depende de expander)
        4. ContractAssembler (depende de registry)
        5. ContractValidator
        6. JSONEmitter

        Raises:
            FileNotFoundError: Si algún archivo de input no existe
            ValueError: Si algún archivo tiene estructura inválida
        """
        # 1. Cargar y validar todos los inputs
        loader = InputLoader(self.assets_path)
        self.registry = loader.load_and_validate()

        # 2. Inicializar expander con timestamp único
        self.expander = MethodExpander(timestamp=self.generation_timestamp)

        # 3. Inicializar composer con expander
        self.composer = ChainComposer(expander=self.expander)

        # 4. Inicializar assembler con registry
        self.assembler = ContractAssembler(
            registry=self. registry,
            generation_timestamp=self.generation_timestamp,
            generator_version=GENERATOR_VERSION,
        )

        # 5. Inicializar validator
        self.validator = ContractValidator(strict_mode=self.strict_mode)

        # 6. Inicializar emitter
        self.emitter = JSONEmitter(output_path=self.output_path)

        logger.info("  ✓ Todos los componentes inicializados")

    def _log_registry_stats(self) -> None:
        """Loguea estadísticas del registry cargado."""
        logger.info(f"  - Métodos totales: {self.registry.total_methods}")
        logger.info(f"  - Preguntas base: {self.registry.total_contracts}")
        logger.info(f"  - Sectores: {self.registry.total_sectors}")
        logger.info(f"  - Contratos a generar: {self.registry. total_contracts * self.registry.total_sectors}")
        logger.info(f"  - Hash classified_methods: {self.registry.classified_methods_hash}")
        logger.info(f"  - Hash contratos_clasificados: {self.registry.contratos_clasificados_hash}")
        logger.info(f"  - Hash method_sets: {self.registry. method_sets_hash}")

        # Validar totales esperados
        if self.registry. total_contracts != EXPECTED_BASE_CONTRACTS:
            raise ValueError(
                f"Expected {EXPECTED_BASE_CONTRACTS} base contracts, "
                f"found {self.registry.total_contracts}"
            )

        if self.registry.total_sectors != EXPECTED_SECTORS: 
            raise ValueError(
                f"Expected {EXPECTED_SECTORS} sectors, "
                f"found {self.registry.total_sectors}"
            )

    # ══════════════════════════════════════════════════════════════════════════
    # GENERACIÓN DE CONTRATOS
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_all_contracts(
        self,
    ) -> tuple[list[GeneratedContract], list[ValidationReport]]:
        """
        Genera todos los 300 contratos.

        ESTRATEGIA:
        - Para cada pregunta, componer cadena epistémica UNA VEZ
        - Para cada sector, ensamblar contrato con sector embebido
        - Los métodos son iguales; lo que cambia es el sector

        Returns:
            Tupla de (lista de contratos, lista de reportes de validación)
        """
        contracts:  list[GeneratedContract] = []
        reports: list[ValidationReport] = []

        # Obtener orden determinista de preguntas
        question_ids = sorted(self.registry.method_sets_by_question. keys())

        # Obtener orden determinista de sectores
        sector_ids = sorted(self.registry.sectors_by_id.keys())

        contract_number = 0

        for q_idx, question_id in enumerate(question_ids, 1):
            logger.info(f"  [{q_idx: 02d}/30] Pregunta {question_id}")

            # Obtener datos del registry
            method_set = self.registry.method_sets_by_question[question_id]
            classification = self.registry.contracts_by_id[question_id]

            # ══════════════════════════════════════════════════════════════
            # COMPONER CADENA EPISTÉMICA (UNA VEZ POR PREGUNTA)
            # Los métodos son iguales para todos los sectores de esta pregunta
            # ══════════════════════════════════════════════════════════════
            try:
                chain = self.composer.compose_chain(method_set, classification)
            except Exception as e:
                logger.error(f"    ✗ Error componiendo cadena:  {e}")
                if self.strict_mode:
                    raise
                continue

            # ══════════════════════════════════════════════════════════════
            # GENERAR CONTRATO PARA CADA SECTOR (10 por pregunta)
            # ══════════════════════════════════════════════════════════════
            for s_idx, sector_id in enumerate(sector_ids, 1):
                contract_number += 1
                sector = self.registry.sectors_by_id[sector_id]

                try:
                    contract, report = self._generate_single_contract(
                        chain=chain,
                        classification=classification,
                        sector=sector,
                        contract_number=contract_number,
                    )
                    contracts.append(contract)
                    reports.append(report)

                    self._stats["contracts_generated"] += 1
                    if report.is_valid:
                        self._stats["contracts_valid"] += 1
                        status = "✓"
                    else: 
                        self._stats["contracts_invalid"] += 1
                        self._stats["validation_failures"].append(report.contract_id)
                        status = "✗"

                    logger.debug(
                        f"    {status} [{contract_number:03d}] "
                        f"{classification.contract_id}_{sector_id}:  "
                        f"{report.passed_checks}/{report.total_checks} checks"
                    )

                except Exception as e:
                    logger.error(
                        f"    ✗ Error en contrato {contract_number} "
                        f"({question_id}_{sector_id}): {e}"
                    )
                    if self.strict_mode:
                        raise

            # Log progreso por pregunta
            logger.info(
                f"    → {len(sector_ids)} contratos generados para {question_id}"
            )

        return contracts, reports

    def _generate_single_contract(
        self,
        chain: EpistemicChain,
        classification: "ContractClassification",
        sector: SectorDefinition,
        contract_number:  int,
    ) -> tuple[GeneratedContract, ValidationReport]: 
        """
        Genera un único contrato para una combinación pregunta+sector.

        SECUENCIA:
        1. Ensamblar contrato con sector embebido
        2. Validar contrato completo
        3. Retornar contrato y reporte

        Args:
            chain: Cadena epistémica ya compuesta
            classification: Clasificación del contrato base
            sector: Definición del sector
            contract_number: Número secuencial del contrato (1-300)

        Returns:
            Tupla de (contrato generado, reporte de validación)
        """
        # Ensamblar contrato con sector
        contract = self.assembler. assemble_contract(
            chain=chain,
            classification=classification,
            sector=sector,
            contract_number=contract_number,
        )

        # Validar contrato
        report = self.validator.validate_contract(contract)

        return contract, report

    # ══════════════════════════════════════════════════════════════════════════
    # EMISIÓN DE CONTRATOS
    # ══════════════════════════════════════════════════════════════════════════

    def _emit_valid_contracts(
        self,
        contracts: list[GeneratedContract],
        reports:  list[ValidationReport],
    ) -> list[Path]:
        """
        Emite los contratos que pasaron validación.

        Args:
            contracts: Lista de contratos generados
            reports: Lista de reportes de validación (mismo orden)

        Returns:
            Lista de paths de archivos emitidos
        """
        emitted_paths:  list[Path] = []

        for contract, report in zip(contracts, reports):
            if report.is_valid:
                path = self.emitter.emit_contract(contract, report)
                emitted_paths.append(path)
                self._stats["contracts_emitted"] += 1
                logger.debug(f"  ✓ Emitido: {path.name}")
            else:
                logger.warning(
                    f"  ✗ NO emitido (inválido): {report.contract_id} "
                    f"({report.critical_failures} critical failures)"
                )

        logger.info(f"  → {len(emitted_paths)} contratos emitidos")

        return emitted_paths

    # ══════════════════════════════════════════════════════════════════════════
    # LOGGING HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _log_banner(self, message: str) -> None:
        """Loguea un banner."""
        logger.info("=" * 70)
        logger.info(message)
        logger.info("=" * 70)

    def _log_step(self, step_num: int, description: str) -> None:
        """Loguea un paso numerado."""
        logger.info("")
        logger.info(f"PASO {step_num}: {description}")
        logger.info("-" * 50)

    def _log_final_stats(
        self,
        contracts: list[GeneratedContract],
        reports: list[ValidationReport],
        emitted_paths: list[Path],
        manifest_path: Path,
    ) -> None:
        """Loguea estadísticas finales."""
        logger.info("")
        self._log_banner("GENERACIÓN COMPLETADA")
        logger.info(f"  Timestamp: {self.generation_timestamp}")
        logger.info(f"  Total contratos intentados: {len(contracts)}")
        logger.info(f"  Contratos válidos: {self._stats['contracts_valid']}")
        logger.info(f"  Contratos inválidos: {self._stats['contracts_invalid']}")
        logger.info(f"  Archivos emitidos: {len(emitted_paths)}")
        logger.info(f"  Manifiesto: {manifest_path}")

        # Reportar contratos inválidos si los hay
        if self._stats["validation_failures"]:
            logger. warning("")
            logger.warning("Contratos que fallaron validación:")
            for cid in self._stats["validation_failures"]:
                logger.warning(f"  - {cid}")

        # Validar total esperado
        if len(contracts) != EXPECTED_TOTAL_CONTRACTS:
            logger.error(
                f"ADVERTENCIA: Se esperaban {EXPECTED_TOTAL_CONTRACTS} contratos, "
                f"se generaron {len(contracts)}"
            )

        logger.info("=" * 70)


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    """
    Punto de entrada principal. 

    USO:
        python -m farfan_pipeline.phases.Phase_two.contract_generator. contract_generator \
            --assets /path/to/epistemological_assets \
            --output /path/to/output \
            [--strict | --no-strict]

    Returns:
        0 si éxito, 1 si error
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generador Granular de 300 Contratos Ejecutores F. A.R.F.A. N",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Generar contratos en modo estricto (por defecto)
  python contract_generator.py --assets ./epistemological_assets --output ./contracts

  # Generar contratos en modo permisivo (continúa con warnings)
  python contract_generator. py --assets ./epistemological_assets --output ./contracts --no-strict
        """,
    )
    parser.add_argument(
        "--assets",
        type=Path,
        required=True,
        help="Directorio con insumos epistemológicos (classified_methods.json, etc.)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directorio de salida para contratos generados",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Modo estricto: falla en cualquier error (por defecto)",
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Modo permisivo: continúa con warnings",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Logging verbose (DEBUG level)",
    )

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validar que assets existe
    if not args.assets. exists():
        logger.error(f"Directorio de assets no existe: {args.assets}")
        return 1

    # Crear directorio de output si no existe
    args.output.mkdir(parents=True, exist_ok=True)

    # Crear y ejecutar generador
    generator = ContractGenerator(
        assets_path=args.assets,
        output_path=args.output,
        strict_mode=args.strict,
    )

    try:
        result = generator.generate()
        logger.info(f"Resultado final: {result}")

        # Retornar 0 solo si todos los contratos son válidos
        if result["invalid_contracts"] > 0:
            logger.warning(
                f"{result['invalid_contracts']} contratos inválidos - revisar logs"
            )
            return 1 if args.strict else 0

        return 0

    except KeyboardInterrupt:
        logger. warning("Generación interrumpida por usuario")
        return 130

    except Exception as e:
        logger.exception(f"FALLO CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())