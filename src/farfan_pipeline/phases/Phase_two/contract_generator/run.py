#!/usr/bin/env python3
"""
Script ejecutable para generar 300 contratos epistemológicos. 

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/run.py

USO: 
    # Desde el directorio del script
    python3 run.py

    # Desde cualquier ubicación
    python3 /path/to/run.py --assets /path/to/assets --output /path/to/output

    # Con opciones
    python3 run.py --verbose --no-strict

ESTRUCTURA ESPERADA:
    src/farfan_pipeline/phases/Phase_two/
    ├── epistemological_assets/
    │   ├── classified_methods.json
    │   ├── contratos_clasificados.json
    │   ├── method_sets_by_question.json
    │   └── sectors. json
    ├── contract_generator/
    │   ├── __init__.py
    │   ├── run.py                    ← ESTE ARCHIVO
    │   ├── input_registry.py
    │   ├── method_expander. py
    │   ├── chain_composer.py
    │   ├── contract_assembler.py
    │   ├── contract_validator.py
    │   ├── json_emitter.py
    │   └── contract_generator.py
    └── generated_contracts/          ← SALIDA
        ├── contracts/
        │   └── Q001_PA01_contract_v4.json ... 
        ├── validation/
        └── generation_manifest.json

SALIDA ESPERADA:  300 contratos (30 preguntas × 10 sectores)

Versión:  4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import NoReturn

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

SCRIPT_VERSION = "4.0.0-granular"
EXPECTED_CONTRACTS = 300

# Paths relativos desde este script
SCRIPT_DIR = Path(__file__).parent. resolve()
PHASE_TWO_DIR = SCRIPT_DIR. parent
DEFAULT_ASSETS_PATH = PHASE_TWO_DIR / "epistemological_assets"
DEFAULT_OUTPUT_PATH = PHASE_TWO_DIR / "generated_contracts"


# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════


def setup_logging(verbose: bool = False) -> None:
    """Configura logging con formato consistente."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Formato con timestamp, nivel, y módulo
    formatter = logging. Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Handler para stdout
    handler = logging.StreamHandler(sys. stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers. clear()
    root_logger.addHandler(handler)


logger = logging.getLogger("run")


# ══════════════════════════════════════════════════════════════════════════════
# IMPORTACIÓN DINÁMICA DE MÓDULOS
# ══════════════════════════════════════════════════════════════════════════════


def load_generator_modules() -> dict:
    """
    Carga todos los módulos del contract_generator.
    
    Uses package imports when running as a module, falls back to
    dynamic loading for direct script execution.
    
    Returns:
        Diccionario con módulos cargados
    
    Raises:
        ImportError: Si algún módulo no puede cargarse
    """
    # Try package imports first (when running as module)
    try:
        from farfan_pipeline.phases.Phase_two.contract_generator import (
            input_registry,
            method_expander,
            chain_composer,
            contract_assembler,
            contract_validator,
            json_emitter,
            contract_generator,
        )
        logger.debug("Loaded modules via package imports")
        return {
            "input_registry": input_registry,
            "method_expander": method_expander,
            "chain_composer": chain_composer,
            "contract_assembler": contract_assembler,
            "contract_validator": contract_validator,
            "json_emitter": json_emitter,
            "contract_generator": contract_generator,
        }
    except ImportError:
        pass
    
    # Fallback to dynamic loading for direct execution
    import importlib.util
    
    modules_to_load = [
        "input_registry",
        "method_expander",
        "chain_composer",
        "contract_assembler",
        "contract_validator",
        "json_emitter",
        "contract_generator",
    ]
    
    loaded_modules = {}
    
    for module_name in modules_to_load:
        module_path = SCRIPT_DIR / f"{module_name}.py"
        
        if not module_path.exists():
            raise ImportError(
                f"Module not found: {module_path}\n"
                f"Ensure all contract_generator modules are present."
            )
        
        try:
            spec = importlib. util.spec_from_file_location(
                module_name,
                module_path,
            )
            module = importlib. util.module_from_spec(spec)
            
            # Registrar en sys.modules para que imports internos funcionen
            sys.modules[module_name] = module
            
            spec.loader.exec_module(module)
            loaded_modules[module_name] = module
            
            logger.debug(f"Loaded module: {module_name}")
            
        except Exception as e:
            raise ImportError(
                f"Failed to load module '{module_name}' from {module_path}:  {e}"
            ) from e
    
    return loaded_modules


# ══════════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DE PREREQUISITES
# ══════════════════════════════════════════════════════════════════════════════


def validate_assets_directory(assets_path: Path) -> None:
    """
    Valida que el directorio de assets existe y tiene los archivos requeridos.
    
    Args:
        assets_path: Path al directorio de assets
    
    Raises:
        FileNotFoundError: Si falta algún archivo requerido
    """
    if not assets_path.exists():
        raise FileNotFoundError(
            f"Assets directory not found:  {assets_path}\n"
            f"Create it and add the required JSON files."
        )
    
    required_files = [
        "classified_methods.json",
        "contratos_clasificados.json",
        "method_sets_by_question.json",
        # sectors.json removed: loaded dynamically from canonic_questionnaire_central
    ]
    
    missing = []
    for filename in required_files:
        filepath = assets_path / filename
        if not filepath.exists():
            missing.append(filename)
    
    if missing:
        raise FileNotFoundError(
            f"Missing required files in {assets_path}:\n"
            + "\n".join(f"  - {f}" for f in missing)
        )
    
    logger.info(f"✓ Assets directory validated: {assets_path}")
    for filename in required_files:
        filepath = assets_path / filename
        size_kb = filepath.stat().st_size / 1024
        logger. info(f"  - {filename}: {size_kb:.1f} KB")


def ensure_output_directory(output_path: Path) -> None:
    """
    Asegura que el directorio de salida existe y está limpio.
    
    Args:
        output_path: Path al directorio de salida
    """
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Crear subdirectorios
    (output_path / "contracts").mkdir(exist_ok=True)
    (output_path / "validation").mkdir(exist_ok=True)
    
    logger.info(f"✓ Output directory ready: {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════


def run_generation(
    assets_path: Path,
    output_path: Path,
    strict_mode: bool = True,
    verbose: bool = False,
) -> int:
    """
    Ejecuta la generación de contratos. 
    
    Args:
        assets_path:  Directorio con insumos epistemológicos
        output_path: Directorio de salida
        strict_mode: Si True, falla en cualquier warning
        verbose: Si True, logging verbose
    
    Returns:
        0 si éxito total, 1 si hubo errores
    """
    start_time = time.time()
    
    # Banner inicial
    print("=" * 70)
    print("F. A.R.F.A. N - GENERADOR DE CONTRATOS EPISTEMOLÓGICOS")
    print(f"Versión: {SCRIPT_VERSION}")
    print(f"Objetivo: {EXPECTED_CONTRACTS} contratos (30 preguntas × 10 sectores)")
    print("=" * 70)
    print()
    
    try:
        # 1. Validar prerequisites
        logger.info("PASO 0: Validando prerequisites...")
        validate_assets_directory(assets_path)
        ensure_output_directory(output_path)
        
        # 2. Cargar módulos
        logger.info("PASO 1: Cargando módulos...")
        modules = load_generator_modules()
        
        # 3. Obtener clase ContractGenerator
        ContractGenerator = modules["contract_generator"].ContractGenerator
        
        # 4. Crear instancia
        logger.info("PASO 2: Inicializando generador...")
        generator = ContractGenerator(
            assets_path=assets_path,
            output_path=output_path,
            strict_mode=strict_mode,
        )
        
        # 5. Ejecutar generación
        logger.info("PASO 3: Ejecutando generación...")
        result = generator.generate()
        
        # 6. Reportar resultado
        elapsed = time.time() - start_time
        
        print()
        print("=" * 70)
        print("RESULTADO DE GENERACIÓN")
        print("=" * 70)
        print(f"  Timestamp:            {result['timestamp']}")
        print(f"  Versión generador:   {result['generator_version']}")
        print(f"  Total contratos:     {result['total_contracts']}")
        print(f"  Contratos válidos:   {result['valid_contracts']}")
        print(f"  Contratos inválidos: {result['invalid_contracts']}")
        print(f"  Archivos emitidos:   {result['emitted_files']}")
        print(f"  Manifiesto:           {result['manifest_path']}")
        print(f"  Tiempo total:        {elapsed:.2f} segundos")
        print("=" * 70)
        
        # Determinar código de salida
        if result["invalid_contracts"] > 0:
            print()
            print(f"⚠️  ADVERTENCIA:  {result['invalid_contracts']} contratos inválidos")
            print(f"   Revisar:  {output_path}/validation/invalid_contracts.json")
            return 1 if strict_mode else 0
        
        if result["total_contracts"] != EXPECTED_CONTRACTS:
            print()
            print(f"⚠️  ADVERTENCIA: Se esperaban {EXPECTED_CONTRACTS} contratos, "
                  f"se generaron {result['total_contracts']}")
            return 1
        
        print()
        print(f"✅ ÉXITO: {result['emitted_files']} contratos generados correctamente")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"ARCHIVO NO ENCONTRADO: {e}")
        return 1
        
    except ImportError as e:
        logger. error(f"ERROR DE IMPORTACIÓN: {e}")
        return 1
        
    except ValueError as e:
        logger.error(f"ERROR DE VALIDACIÓN: {e}")
        return 1
        
    except KeyboardInterrupt:
        print()
        logger.warning("Generación interrumpida por usuario (Ctrl+C)")
        return 130
        
    except Exception as e:
        logger.exception(f"ERROR CRÍTICO: {e}")
        return 1


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════


def parse_arguments() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Generador de 300 Contratos Epistemológicos F.A.R.F.A.N",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos: 
  # Usar paths por defecto
  python3 run.py

  # Especificar paths
  python3 run.py --assets ./my_assets --output ./my_output

  # Modo permisivo con verbose
  python3 run.py --no-strict --verbose

Estructura de assets esperada:
  epistemological_assets/
  ├── classified_methods.json
  ├── contratos_clasificados.json
  ├── method_sets_by_question.json
  └── sectors. json
        """,
    )
    
    parser.add_argument(
        "--assets",
        type=Path,
        default=DEFAULT_ASSETS_PATH,
        help=f"Directorio con insumos epistemológicos (default: {DEFAULT_ASSETS_PATH})",
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Directorio de salida para contratos (default: {DEFAULT_OUTPUT_PATH})",
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Modo estricto: falla en cualquier error (default)",
    )
    
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Modo permisivo: continúa con warnings",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Logging verbose (DEBUG level)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    
    return parser.parse_args()


def main() -> NoReturn:
    """Punto de entrada principal."""
    args = parse_arguments()
    
    # Configurar logging
    setup_logging(verbose=args.verbose)
    
    # Ejecutar generación
    exit_code = run_generation(
        assets_path=args.assets. resolve(),
        output_path=args.output.resolve(),
        strict_mode=args.strict,
        verbose=args.verbose,
    )
    
    sys.exit(exit_code)


# ══════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN DIRECTA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()