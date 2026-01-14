#!/usr/bin/env python3
"""
SISAS Quality Audit Script

Verifica el cumplimiento exacto del inventario de calidad obligatorio para los módulos CORE y SIGNALS.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class AuditResult:
    passed: bool
    module: str
    requirement: str
    details: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO

class SISASQualityAuditor:
    def __init__(self):
        self.results: List[AuditResult] = []
        self.base_path = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS")

    def add_result(self, passed: bool, module: str, requirement: str, details: str, severity: str = "ERROR"):
        self.results.append(AuditResult(passed, module, requirement, details, severity))

    def audit_file_exists(self, filepath: str, module: str) -> bool:
        """Verifica que un archivo existe"""
        path = self.base_path / filepath
        exists = path.exists()
        self.add_result(
            exists,
            module,
            "Existencia del archivo",
            f"{'✅' if exists else '❌'} {filepath}"
        )
        return exists

    def audit_line_count(self, filepath: str, module: str, expected_min: int, expected_max: int):
        """Verifica el número de líneas de un archivo"""
        path = self.base_path / filepath
        if not path.exists():
            return

        line_count = len(path.read_text().splitlines())
        passed = expected_min <= line_count <= expected_max
        self.add_result(
            passed,
            module,
            "Número de líneas",
            f"{'✅' if passed else '⚠️'} {filepath}: {line_count} líneas (esperado: {expected_min}-{expected_max})",
            "WARNING" if not passed else "INFO"
        )

    def audit_module_exports(self, filepath: str, module: str, expected_exports: List[str]):
        """Verifica que un módulo __init__.py exporta lo esperado"""
        path = self.base_path / filepath
        if not path.exists():
            return

        content = path.read_text(encoding='utf-8', errors='ignore')

        # Verificar __all__
        has_all = "__all__" in content
        self.add_result(
            has_all,
            module,
            "Define __all__",
            f"{'✅' if has_all else '❌'} __all__ definido"
        )

        # Verificar docstring
        has_docstring = '"""' in content or "'''" in content
        self.add_result(
            has_docstring,
            module,
            "Docstring de módulo",
            f"{'✅' if has_docstring else '❌'} Docstring presente"
        )

        # Verificar exports
        missing_exports = []
        for export in expected_exports:
            if export not in content:
                missing_exports.append(export)

        if missing_exports:
            self.add_result(
                False,
                module,
                "Exports completos",
                f"❌ Faltan exports: {', '.join(missing_exports)}"
            )
        else:
            self.add_result(
                True,
                module,
                "Exports completos",
                f"✅ Todos los exports presentes ({len(expected_exports)} items)"
            )

    def audit_class_exists(self, filepath: str, module: str, classname: str) -> bool:
        """Verifica que una clase existe en un archivo"""
        path = self.base_path / filepath
        if not path.exists():
            return False

        content = path.read_text(encoding='utf-8', errors='ignore')
        exists = f"class {classname}" in content
        self.add_result(
            exists,
            module,
            f"Clase {classname}",
            f"{'✅' if exists else '❌'} Clase definida",
            "WARNING" if not exists else "INFO"
        )
        return exists

    def audit_method_exists(self, filepath: str, module: str, classname: str, method: str):
        """Verifica que un método existe en una clase"""
        path = self.base_path / filepath
        if not path.exists():
            return

        content = path.read_text(encoding='utf-8', errors='ignore')
        exists = f"def {method}(" in content
        self.add_result(
            exists,
            module,
            f"{classname}.{method}()",
            f"{'✅' if exists else '❌'} Método definido",
            "WARNING" if not exists else "INFO"
        )

    def audit_axiom_documented(self, filepath: str, module: str, axioms: List[str]):
        """Verifica que los axiomas están documentados"""
        path = self.base_path / filepath
        if not path.exists():
            return

        content = path.read_text(encoding='utf-8', errors='ignore')
        missing_axioms = []
        for axiom in axioms:
            if axiom.lower() not in content.lower():
                missing_axioms.append(axiom)

        if missing_axioms:
            self.add_result(
                False,
                module,
                "Axiomas documentados",
                f"⚠️ Axiomas sin documentar: {', '.join(missing_axioms)}",
                "WARNING"
            )
        else:
            self.add_result(
                True,
                module,
                "Axiomas documentados",
                f"✅ Todos los axiomas documentados ({len(axioms)} axiomas)"
            )

    def audit_enum_members(self, filepath: str, module: str, enum_name: str, expected_members: List[str]):
        """Verifica que un Enum tiene todos los miembros esperados"""
        path = self.base_path / filepath
        if not path.exists():
            return

        content = path.read_text(encoding='utf-8', errors='ignore')
        missing_members = []
        for member in expected_members:
            if f'{member} =' not in content and f'{member}=' not in content:
                missing_members.append(member)

        if missing_members:
            self.add_result(
                False,
                module,
                f"Enum {enum_name} completo",
                f"❌ Faltan miembros: {', '.join(missing_members)}"
            )
        else:
            self.add_result(
                True,
                module,
                f"Enum {enum_name} completo",
                f"✅ Todos los miembros presentes ({len(expected_members)} miembros)"
            )

    def run_audit(self):
        """Ejecuta auditoría completa"""
        print("=" * 80)
        print("AUDITORÍA DE CALIDAD OBLIGATORIA SISAS")
        print("Módulos: CORE y SIGNALS")
        print("=" * 80)
        print()

        # MÓDULO 1: CORE
        print("📁 MÓDULO 1: CORE")
        print("-" * 80)

        # 1.1 core/__init__.py
        if self.audit_file_exists("core/__init__.py", "core"):
            self.audit_module_exports(
                "core/__init__.py",
                "core",
                ["Signal", "SignalContext", "SignalSource", "Event", "EventStore",
                 "PublicationContract", "ConsumptionContract", "IrrigationContract",
                 "ContractRegistry", "SignalBus", "BusRegistry"]
            )

        # 1.2 core/signal.py
        if self.audit_file_exists("core/signal.py", "core/signal"):
            self.audit_line_count("core/signal.py", "core/signal", 150, 350)

            # Classes
            self.audit_class_exists("core/signal.py", "core/signal", "SignalCategory")
            self.audit_class_exists("core/signal.py", "core/signal", "SignalConfidence")
            self.audit_class_exists("core/signal.py", "core/signal", "SignalContext")
            self.audit_class_exists("core/signal.py", "core/signal", "SignalSource")
            self.audit_class_exists("core/signal.py", "core/signal", "Signal")

            # Axiomas
            self.audit_axiom_documented(
                "core/signal.py",
                "core/signal",
                ["derived", "deterministic", "versioned", "contextual", "auditable", "non_imperative"]
            )

            # Métodos requeridos
            self.audit_method_exists("core/signal.py", "core/signal", "Signal", "compute_hash")
            self.audit_method_exists("core/signal.py", "core/signal", "Signal", "is_valid")
            self.audit_method_exists("core/signal.py", "core/signal", "Signal", "to_dict")
            self.audit_method_exists("core/signal.py", "core/signal", "Signal", "add_audit_entry")
            self.audit_method_exists("core/signal.py", "core/signal", "Signal", "__post_init__")

        # 1.3 core/event.py
        if self.audit_file_exists("core/event.py", "core/event"):
            self.audit_line_count("core/event.py", "core/event", 200, 400)

            # Classes
            self.audit_class_exists("core/event.py", "core/event", "EventType")
            self.audit_class_exists("core/event.py", "core/event", "EventPayload")
            self.audit_class_exists("core/event.py", "core/event", "Event")
            self.audit_class_exists("core/event.py", "core/event", "EventStore")

            # EventTypes requeridos
            self.audit_enum_members(
                "core/event.py",
                "core/event",
                "EventType",
                ["CANONICAL_DATA_LOADED", "IRRIGATION_STARTED", "SIGNAL_GENERATED"]
            )

            # EventStore métodos
            self.audit_method_exists("core/event.py", "core/event", "EventStore", "append")
            self.audit_method_exists("core/event.py", "core/event", "EventStore", "get_by_id")
            self.audit_method_exists("core/event.py", "core/event", "EventStore", "get_by_type")
            self.audit_method_exists("core/event.py", "core/event", "EventStore", "count")

        # 1.4 core/contracts.py
        if self.audit_file_exists("core/contracts.py", "core/contracts"):
            self.audit_line_count("core/contracts.py", "core/contracts", 300, 500)

            # Classes
            self.audit_class_exists("core/contracts.py", "core/contracts", "ContractType")
            self.audit_class_exists("core/contracts.py", "core/contracts", "ContractStatus")
            self.audit_class_exists("core/contracts.py", "core/contracts", "PublicationContract")
            self.audit_class_exists("core/contracts.py", "core/contracts", "ConsumptionContract")
            self.audit_class_exists("core/contracts.py", "core/contracts", "IrrigationContract")
            self.audit_class_exists("core/contracts.py", "core/contracts", "ContractRegistry")

            # Método crítico
            self.audit_method_exists("core/contracts.py", "core/contracts", "IrrigationContract", "is_irrigable")

        # 1.5 core/bus.py
        if self.audit_file_exists("core/bus.py", "core/bus"):
            self.audit_line_count("core/bus.py", "core/bus", 250, 400)

            # Classes
            self.audit_class_exists("core/bus.py", "core/bus", "BusType")
            self.audit_class_exists("core/bus.py", "core/bus", "BusMessage")
            self.audit_class_exists("core/bus.py", "core/bus", "SignalBus")
            self.audit_class_exists("core/bus.py", "core/bus", "BusRegistry")

            # BusTypes
            self.audit_enum_members(
                "core/bus.py",
                "core/bus",
                "BusType",
                ["STRUCTURAL", "INTEGRITY", "EPISTEMIC", "CONTRAST", "OPERATIONAL", "CONSUMPTION", "UNIVERSAL"]
            )

            # SignalBus métodos
            self.audit_method_exists("core/bus.py", "core/bus", "SignalBus", "publish")
            self.audit_method_exists("core/bus.py", "core/bus", "SignalBus", "subscribe")
            self.audit_method_exists("core/bus.py", "core/bus", "SignalBus", "get_stats")

        # MÓDULO 2: SIGNALS
        print()
        print("📁 MÓDULO 2: SIGNALS")
        print("-" * 80)

        # 2.1 signals/__init__.py
        if self.audit_file_exists("signals/__init__.py", "signals"):
            self.audit_module_exports(
                "signals/__init__.py",
                "signals",
                ["StructuralAlignmentSignal", "EventPresenceSignal", "AnswerDeterminacySignal",
                 "DecisionDivergenceSignal", "ExecutionAttemptSignal", "FrequencySignal"]
            )

        # 2.2 signals/registry.py
        if self.audit_file_exists("signals/registry.py", "signals/registry"):
            self.audit_line_count("signals/registry.py", "signals/registry", 80, 200)
            self.audit_class_exists("signals/registry.py", "signals/registry", "SignalRegistry")
            self.audit_method_exists("signals/registry.py", "signals/registry", "SignalRegistry", "get_signal_class")
            self.audit_method_exists("signals/registry.py", "signals/registry", "SignalRegistry", "is_valid_signal_type")
            self.audit_method_exists("signals/registry.py", "signals/registry", "SignalRegistry", "create_signal")

        # 2.3 - 2.8 Signal types
        signal_types = [
            ("structural.py", ["StructuralAlignmentSignal", "SchemaConflictSignal", "CanonicalMappingSignal"], 120, 200),
            ("integrity.py", ["EventPresenceSignal", "EventCompletenessSignal", "DataIntegritySignal"], 100, 180),
            ("epistemic.py", ["AnswerDeterminacySignal", "AnswerSpecificitySignal", "EmpiricalSupportSignal", "MethodApplicationSignal"], 180, 350),
            ("contrast.py", ["DecisionDivergenceSignal", "ConfidenceDropSignal", "TemporalContrastSignal"], 120, 200),
            ("operational.py", ["ExecutionAttemptSignal", "FailureModeSignal", "LegacyActivitySignal", "LegacyDependencySignal"], 150, 250),
            ("consumption.py", ["FrequencySignal", "TemporalCouplingSignal", "ConsumerHealthSignal"], 80, 150),
        ]

        for filename, classes, min_lines, max_lines in signal_types:
            filepath = f"signals/types/{filename}"
            if self.audit_file_exists(filepath, f"signals/types/{filename}"):
                self.audit_line_count(filepath, f"signals/types/{filename}", min_lines, max_lines)
                for classname in classes:
                    self.audit_class_exists(filepath, f"signals/types/{filename}", classname)
                    # Verificar que retorna category
                    self.audit_method_exists(filepath, f"signals/types/{filename}", classname, "category")

    def generate_report(self):
        """Genera reporte final"""
        print()
        print("=" * 80)
        print("REPORTE FINAL DE AUDITORÍA")
        print("=" * 80)
        print()

        # Agrupar por severidad
        errors = [r for r in self.results if not r.passed and r.severity == "ERROR"]
        warnings = [r for r in self.results if not r.passed and r.severity == "WARNING"]
        passed = [r for r in self.results if r.passed]

        print(f"✅ PASARON: {len(passed)}/{len(self.results)} requisitos")
        print(f"❌ ERRORES: {len(errors)} requisitos críticos")
        print(f"⚠️  ADVERTENCIAS: {len(warnings)} requisitos opcionales")
        print()

        if errors:
            print("ERRORES CRÍTICOS:")
            print("-" * 80)
            for result in errors:
                print(f"  [{result.module}] {result.requirement}")
                print(f"    {result.details}")
            print()

        if warnings:
            print("ADVERTENCIAS:")
            print("-" * 80)
            for result in warnings[:10]:  # Mostrar máximo 10
                print(f"  [{result.module}] {result.requirement}")
                print(f"    {result.details}")
            if len(warnings) > 10:
                print(f"  ... y {len(warnings) - 10} advertencias más")
            print()

        # Resumen por módulo
        modules = {}
        for result in self.results:
            if result.module not in modules:
                modules[result.module] = {"passed": 0, "failed": 0}
            if result.passed:
                modules[result.module]["passed"] += 1
            else:
                modules[result.module]["failed"] += 1

        print("RESUMEN POR MÓDULO:")
        print("-" * 80)
        for module, stats in sorted(modules.items()):
            total = stats["passed"] + stats["failed"]
            percentage = (stats["passed"] / total * 100) if total > 0 else 0
            status = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            print(f"  {status} {module}: {stats['passed']}/{total} ({percentage:.1f}%)")

        print()
        print("=" * 80)

        # Return exit code
        return 0 if len(errors) == 0 else 1

def main():
    auditor = SISASQualityAuditor()
    auditor.run_audit()
    exit_code = auditor.generate_report()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
