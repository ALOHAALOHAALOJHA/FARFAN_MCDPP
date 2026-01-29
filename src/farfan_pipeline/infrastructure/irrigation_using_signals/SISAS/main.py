# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/main.py

#!/usr/bin/env python3
"""
SISAS - Signal-Irrigated System for Analytical Support
Main entry point for irrigation execution
"""

import argparse
import logging
import sys
import os
from pathlib import Path

from .core.bus import BusRegistry
from .core.contracts import ContractRegistry, ContractStatus
from .core.event import EventStore
from .vocabulary.signal_vocabulary import SignalVocabulary
from .vocabulary.capability_vocabulary import CapabilityVocabulary
from .vocabulary.alignment_checker import VocabularyAlignmentChecker
from .irrigation.irrigation_map import IrrigationMap
from .irrigation.irrigation_executor import IrrigationExecutor
from .vehicles.signal_registry import SignalRegistryVehicle
from .vehicles.signal_context_scoper import SignalContextScoperVehicle


def setup_logging(level:  str = "INFO"):
    """Configura logging"""
    os.makedirs("_logs", exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('_logs/sisas.log')
        ]
    )


def initialize_system():
    """Inicializa el sistema SISAS completo"""
    logger = logging.getLogger("SISAS. Init")
    logger.info("Initializing SISAS...")
    
    # 1. Crear registros
    bus_registry = BusRegistry()
    contract_registry = ContractRegistry()
    event_store = EventStore()
    
    # 2. Crear vocabularios
    signal_vocab = SignalVocabulary()
    capability_vocab = CapabilityVocabulary()
    
    # 3. Verificar alineación
    alignment_checker = VocabularyAlignmentChecker(
        signal_vocabulary=signal_vocab,
        capability_vocabulary=capability_vocab
    )
    alignment_report = alignment_checker.check_alignment()
    
    if not alignment_report.is_aligned:
        logger.warning(f"Vocabulary alignment issues:  {len(alignment_report.issues)}")
        for issue in alignment_report.issues:
            if issue.severity == "critical":
                logger.error(f"  CRITICAL: {issue.details}")
    
    # 4. Crear vehículos
    vehicles = {
        "signal_registry": SignalRegistryVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        ),
        "signal_context_scoper": SignalContextScoperVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )
    }
    
    # 5. Crear ejecutor de irrigación
    executor = IrrigationExecutor(
        bus_registry=bus_registry,
        contract_registry=contract_registry,
        event_store=event_store
    )
    
    # Registrar vehículos
    for vehicle in vehicles.values():
        executor.register_vehicle(vehicle)
    
    logger.info("SISAS initialized successfully")
    
    return {
        "executor": executor,
        "bus_registry": bus_registry,
        "contract_registry": contract_registry,
        "event_store":  event_store,
        "signal_vocab": signal_vocab,
        "capability_vocab": capability_vocab,
        "alignment_checker": alignment_checker
    }


def load_irrigation_map(csv_path: str) -> IrrigationMap:
    """Carga mapa de irrigación desde CSV"""
    import csv
    
    if not os.path.exists(csv_path):
        return IrrigationMap()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    return IrrigationMap.from_sabana_csv(data)


def run_irrigation(args):
    """Ejecuta irrigación"""
    logger = logging.getLogger("SISAS.Run")
    
    # Inicializar
    system = initialize_system()
    executor = system["executor"]
    
    # Cargar mapa
    irrigation_map = load_irrigation_map(args.csv_path)
    executor.irrigation_map = irrigation_map
    
    # Estadísticas
    stats = irrigation_map.get_statistics()
    logger.info(f"Loaded irrigation map:  {stats['total_routes']} routes")
    logger.info(f"  Irrigable now: {stats['irrigable_now']}")
    logger.info(f"  Not irrigable yet: {stats['not_irrigable_yet']}")
    
    # Ejecutar según modo
    if args.phase: 
        logger.info(f"Executing phase:  {args.phase}")
        results = executor.execute_phase(args.phase, args.base_path)
    elif args.all:
        logger.info("Executing all irrigable routes")
        results = executor.execute_all_irrigable(args.base_path)
    else:
        logger.error("Specify --phase or --all")
        return
    
    # Reportar resultados
    summary = executor.get_execution_summary()
    logger.info(f"Execution complete:")
    logger.info(f"  Total:  {summary['total_executions']}")
    logger.info(f"  Successful: {summary['successful']}")
    logger.info(f"  Failed: {summary['failed']}")
    logger.info(f"  Signals generated: {summary['total_signals_generated']}")


def check_alignment(args):
    """Verifica alineación de vocabularios"""
    logger = logging.getLogger("SISAS.Check")
    
    system = initialize_system()
    checker = system["alignment_checker"]
    
    report = checker.check_alignment()
    
    print(f"\n{'='*60}")
    print("SISAS Vocabulary Alignment Report")
    print(f"{'='*60}")
    print(f"Aligned: {report.is_aligned}")
    print(f"Signals checked: {report.signals_checked}")
    print(f"Capabilities checked: {report.capabilities_checked}")
    print(f"Coverage: {report.coverage_percentage:.1f}%")
    print(f"Issues: {len(report.issues)}")
    
    if report.issues:
        print(f"\n{'Issues by severity:'}")
        for severity in ["critical", "warning", "info"]:
            issues = [i for i in report.issues if i.severity == severity]
            if issues:
                print(f"\n  {severity.upper()} ({len(issues)}):")
                for issue in issues[: 5]:  # Mostrar máximo 5 por categoría
                    print(f"    - {issue.component}: {issue.details}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
    
    # Generar plan de resolución si hay issues
    if report.issues:
        plan = checker.generate_gap_resolution_plan(report)
        print(f"\n{'='*60}")
        print("Gap Resolution Plan")
        print(f"{'='*60}")
        for step in plan:
            print(f"\nPriority {step['priority']}: {step['action']}")
            print(f"  Description: {step['description']}")
            print(f"  Severity: {step['severity']}")
            print(f"  Items affected: {len(step['items'])}")


def generate_contracts(args):
    """Genera contratos desde CSV"""
    logger = logging.getLogger("SISAS. Contracts")
    
    from .scripts.generate_contracts import (
        generate_contracts_from_csv,
        export_contracts_to_json,
        generate_gap_resolution_tasks
    )
    
    logger.info(f"Generating contracts from {args.csv_path}")
    
    registry = generate_contracts_from_csv(args.csv_path)
    
    # Exportar
    output_path = args.output or "_registry/irrigation_contracts.json"
    export_contracts_to_json(registry, output_path)
    logger.info(f"Contracts exported to {output_path}")
    
    # Generar tareas
    tasks = generate_gap_resolution_tasks(registry)
    tasks_path = output_path.replace(".json", "_tasks.json")
    
    import json
    with open(tasks_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    logger.info(f"Resolution tasks exported to {tasks_path}")
    
    # Estadísticas
    stats = {
        "total":  len(registry.irrigation_contracts),
        "active": len([c for c in registry.irrigation_contracts.values() 
                      if c.status == ContractStatus.ACTIVE]),
        "pending": len([c for c in registry.irrigation_contracts.values() 
                       if c.status == ContractStatus.DRAFT]),
        "tasks":  len(tasks)
    }
    
    print(f"\nContract Generation Summary:")
    print(f"  Total contracts: {stats['total']}")
    print(f"  Active (ready to irrigate): {stats['active']}")
    print(f"  Pending (have gaps): {stats['pending']}")
    print(f"  Resolution tasks: {stats['tasks']}")


def show_stats(args):
    """Muestra estadísticas del sistema"""
    logger = logging.getLogger("SISAS.Stats")
    
    # Cargar mapa de irrigación
    irrigation_map = load_irrigation_map(args.csv_path)
    stats = irrigation_map.get_statistics()
    
    print(f"\n{'='*60}")
    print("SISAS Irrigation Statistics")
    print(f"{'='*60}")
    print(f"\nRoutes:")
    print(f"  Total: {stats['total_routes']}")
    print(f"  Irrigable now: {stats['irrigable_now']} ({stats['irrigable_percentage']:.1f}%)")
    print(f"  Not irrigable yet: {stats['not_irrigable_yet']}")
    print(f"  Definitely not:  {stats['definitely_not']}")
    
    print(f"\nPhases:  {', '.join(stats['phases'])}")
    print(f"Vehicles in use: {len(stats['vehicles_in_use'])}")
    for v in stats['vehicles_in_use']:
        print(f"  - {v}")
    
    print(f"\nConsumers registered: {len(stats['consumers_registered'])}")
    
    print(f"\nGap Summary:")
    for gap, count in sorted(stats['gap_summary'].items(), key=lambda x: -x[1]):
        print(f"  {gap}: {count} files")


def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(
        description="SISAS - Signal-Irrigated System for Analytical Support"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Comando:  run
    run_parser = subparsers.add_parser("run", help="Run irrigation")
    run_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    run_parser.add_argument("--base-path", default="", help="Base path for canonical files")
    run_parser.add_argument("--phase", help="Execute specific phase")
    run_parser.add_argument("--all", action="store_true", help="Execute all irrigable routes")
    run_parser.set_defaults(func=run_irrigation)
    
    # Comando: check
    check_parser = subparsers.add_parser("check", help="Check vocabulary alignment")
    check_parser.set_defaults(func=check_alignment)
    
    # Comando: contracts
    contracts_parser = subparsers.add_parser("contracts", help="Generate irrigation contracts")
    contracts_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    contracts_parser.add_argument("--output", help="Output path for contracts JSON")
    contracts_parser.set_defaults(func=generate_contracts)
    
    # Comando: stats
    stats_parser = subparsers.add_parser("stats", help="Show irrigation statistics")
    stats_parser.add_argument("--csv-path", required=True, help="Path to sabana CSV")
    stats_parser.set_defaults(func=show_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging(args.log_level)
    args.func(args)


if __name__ == "__main__": 
    main()