#!/usr/bin/env python3
"""
Script de ejecución independiente para el generador de contratos F.A.R.F.A.N v4.0.0
Evita imports problemáticos en __init__.py de Phase_two
"""

import sys
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

def load_module_from_file(module_name, file_path):
    """Carga un módulo desde un archivo sin ejecutar __init__.py del paquete"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Agregar src al path
src_path = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(src_path))  # noqa: E501

# Cargar módulos del generador directamente desde archivos
base_path = src_path / 'farfan_pipeline/phases/Phase_two/contract_generator'

input_registry = load_module_from_file(
    'contract_generator.input_registry',
    base_path / 'input_registry.py'
)

method_expander = load_module_from_file(
    'contract_generator.method_expander',
    base_path / 'method_expander.py'
)

chain_composer = load_module_from_file(
    'contract_generator.chain_composer',
    base_path / 'chain_composer.py'
)

contract_assembler = load_module_from_file(
    'contract_generator.contract_assembler',
    base_path / 'contract_assembler.py'
)

contract_validator = load_module_from_file(
    'contract_generator.contract_validator',
    base_path / 'contract_validator.py'
)

json_emitter = load_module_from_file(
    'contract_generator.json_emitter',
    base_path / 'json_emitter.py'
)

# Importar clases necesarias
InputLoader = input_registry.InputLoader
MethodExpander = method_expander.MethodExpander
ChainComposer = chain_composer.ChainComposer
ContractAssembler = contract_assembler.ContractAssembler
ContractValidator = contract_validator.ContractValidator
JSONEmitter = json_emitter.JSONEmitter

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ContractGenerator")


class ContractGeneratorStandalone:
    """Versión standalone del generador que evita imports problemáticos"""

    VERSION = "4.0.0-granular"

    def __init__(self, assets_path: Path, output_path: Path, strict_mode: bool = True):
        self.assets_path = assets_path
        self.output_path = output_path
        self.strict_mode = strict_mode
        self.generation_timestamp = datetime.now(timezone.utc).isoformat()

        # Componentes
        self.registry = None
        self.expander = None
        self.composer = None
        self.assembler = None
        self.validator = None
        self.emitter = None

    def generate(self) -> dict:
        logger.info("=" * 60)
        logger.info("INICIANDO GENERACIÓN DE CONTRATOS F.A.R.F.A.N v4.0.0")
        logger.info(f"Timestamp: {self.generation_timestamp}")
        logger.info("=" * 60)

        # Paso 1: Cargar inputs
        logger.info("Paso 1: Cargando inputs...")
        loader = InputLoader(self.assets_path)
        self.registry = loader.load_and_validate()
        logger.info(f"  - Métodos cargados: {self.registry.total_methods}")
        logger.info(f"  - Contratos a generar: {self.registry.total_contracts}")

        # Inicializar componentes
        self.expander = MethodExpander(self.generation_timestamp)
        self.composer = ChainComposer(self.expander)
        self.assembler = ContractAssembler(
            self.registry,
            self.generation_timestamp,
            self.VERSION,
        )
        self.validator = ContractValidator()
        self.emitter = JSONEmitter(self.output_path)

        # Paso 2: Generar contratos
        logger.info("Paso 2: Generando contratos...")
        contracts = []
        reports = []

        question_ids = sorted(self.registry.method_sets_by_question.keys())

        for i, question_id in enumerate(question_ids, 1):
            logger.info(f"  [{i:02d}/30] Procesando {question_id}...")

            try:
                method_set = self.registry.method_sets_by_question[question_id]
                classification = self.registry.contracts_by_id[question_id]

                # Componer cadena
                chain = self.composer.compose_chain(method_set, classification)

                # Ensamblar contrato
                contract = self.assembler.assemble_contract(chain, classification)

                # Validar
                report = self.validator.validate_contract(contract)

                contracts.append(contract)
                reports.append(report)

                status = "✓" if report.is_valid else "✗"
                logger.info(
                    f"    {status} {report.contract_id}: "
                    f"{report.passed_checks}/{report.total_checks} checks passed"
                )

            except Exception as e:
                logger.error(f"    ✗ FALLO en {question_id}: {e}")
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
                logger.warning(f"  ✗ NO emitido (inválido): {report.contract_id}")

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


if __name__ == "__main__":
    generator = ContractGeneratorStandalone(
        assets_path=Path("src/farfan_pipeline/phases/Phase_two/epistemological_assets"),
        output_path=Path("src/farfan_pipeline/phases/Phase_two/generated_contracts"),
        strict_mode=True,
    )

    result = generator.generate()

    print(f"\n{'='*60}")
    print(f"CONTRATOS GENERADOS EXITOSAMENTE")
    print(f"{'='*60}")
    print(f"Total: {result['total_contracts']}")
    print(f"Válidos: {result['valid_contracts']}")
    print(f"Inválidos: {result['invalid_contracts']}")
    print(f"Archivos: {result['emitted_files']}")
    print(f"Manifiesto: {result['manifest_path']}")
