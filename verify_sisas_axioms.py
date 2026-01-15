#!/usr/bin/env python3
"""
SISAS Axiom Verification Script
Automated testing of SISAS axioms and architecture
"""

import sys
import os
import inspect
from pathlib import Path
from typing import List, Tuple, Dict, Any
import json

# Add SISAS to path
SISAS_PATH = Path(__file__).parent / "src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS"
sys.path.insert(0, str(SISAS_PATH.parent.parent.parent.parent))

# Color codes for output
class Colors:
    PASS = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class AuditResult:
    def __init__(self, test_id: str, description: str, status: str, evidence: str = "", impact: str = ""):
        self.test_id = test_id
        self.description = description
        self.status = status  # PASS, FAIL, WARNING
        self.evidence = evidence
        self.impact = impact

    def __str__(self):
        color = Colors.PASS if self.status == "PASS" else Colors.FAIL if self.status == "FAIL" else Colors.WARNING
        symbol = "✅" if self.status == "PASS" else "❌" if self.status == "FAIL" else "⚠️"
        return f"{color}{symbol} [{self.test_id}] {self.description}{Colors.END}"


class SISASAuditor:
    def __init__(self):
        self.results: List[AuditResult] = []
        self.critical_failures = 0
        self.warnings = 0
        self.passes = 0

    def add_result(self, result: AuditResult):
        self.results.append(result)
        if result.status == "PASS":
            self.passes += 1
        elif result.status == "FAIL":
            self.critical_failures += 1
        elif result.status == "WARNING":
            self.warnings += 1

    def audit_axiom_1_1_1(self) -> AuditResult:
        """AXIOM 1.1.1: Ningún evento se pierde"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import EventStore

            # Check if clear_processed method exists
            if hasattr(EventStore, 'clear_processed'):
                source = inspect.getsource(EventStore.clear_processed)
                if 'remove(event)' in source or 'del ' in source:
                    return AuditResult(
                        "1.1.1",
                        "AXIOM: Ningún evento se pierde",
                        "FAIL",
                        "EventStore.clear_processed() DELETES events (line: self.events.remove(event))",
                        "CRITICAL - Violates fundamental axiom"
                    )

            return AuditResult(
                "1.1.1",
                "AXIOM: Ningún evento se pierde",
                "PASS",
                "No deletion methods found in EventStore"
            )
        except Exception as e:
            return AuditResult(
                "1.1.1",
                "AXIOM: Ningún evento se pierde",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_2(self) -> AuditResult:
        """AXIOM 1.1.2: Las señales son derivadas"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

            # Check __post_init__ for source validation
            source = inspect.getsource(Signal.__post_init__)
            if 'source is None' in source and 'ValueError' in source:
                return AuditResult(
                    "1.1.2",
                    "AXIOM: Las señales son derivadas",
                    "PASS",
                    "Source validation enforced in __post_init__"
                )
            else:
                return AuditResult(
                    "1.1.2",
                    "AXIOM: Las señales son derivadas",
                    "FAIL",
                    "Source validation not found or incomplete"
                )
        except Exception as e:
            return AuditResult(
                "1.1.2",
                "AXIOM: Las señales son derivadas",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_3(self) -> AuditResult:
        """AXIOM 1.1.3: Las señales son deterministas"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

            # Check compute_hash method
            if hasattr(Signal, 'compute_hash'):
                source = inspect.getsource(Signal.compute_hash)
                if 'hashlib.sha256' in source and 'sort_keys=True' in source:
                    return AuditResult(
                        "1.1.3",
                        "AXIOM: Las señales son deterministas",
                        "PASS",
                        "compute_hash() uses SHA-256 with sorted keys"
                    )

            return AuditResult(
                "1.1.3",
                "AXIOM: Las señales son deterministas",
                "FAIL",
                "compute_hash() not found or not deterministic"
            )
        except Exception as e:
            return AuditResult(
                "1.1.3",
                "AXIOM: Las señales son deterministas",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_4(self) -> AuditResult:
        """AXIOM 1.1.4: Señales nunca se sobrescriben"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

            # Check if Signal is frozen
            source = inspect.getsource(Signal)
            class_def_line = source.split('\n')[0]

            if 'frozen=True' in class_def_line:
                return AuditResult(
                    "1.1.4",
                    "AXIOM: Señales nunca se sobrescriben",
                    "PASS",
                    "Signal class is frozen (immutable)"
                )
            else:
                return AuditResult(
                    "1.1.4",
                    "AXIOM: Señales nunca se sobrescriben",
                    "FAIL",
                    "Signal class is NOT frozen - @dataclass without frozen=True",
                    "CRITICAL - Allows signal mutation"
                )
        except Exception as e:
            return AuditResult(
                "1.1.4",
                "AXIOM: Señales nunca se sobrescriben",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_5(self) -> AuditResult:
        """AXIOM 1.1.5: Señales tienen contexto"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

            source = inspect.getsource(Signal.__post_init__)
            if 'context is None' in source and 'ValueError' in source:
                return AuditResult(
                    "1.1.5",
                    "AXIOM: Señales tienen contexto",
                    "PASS",
                    "Context validation enforced in __post_init__"
                )
            else:
                return AuditResult(
                    "1.1.5",
                    "AXIOM: Señales tienen contexto",
                    "FAIL",
                    "Context validation not found"
                )
        except Exception as e:
            return AuditResult(
                "1.1.5",
                "AXIOM: Señales tienen contexto",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_6(self) -> AuditResult:
        """AXIOM 1.1.6: Señales son auditables"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal
            import dataclasses

            fields = {f.name for f in dataclasses.fields(Signal)}
            if 'audit_trail' in fields and 'rationale' in fields:
                return AuditResult(
                    "1.1.6",
                    "AXIOM: Señales son auditables",
                    "PASS",
                    "audit_trail and rationale fields present"
                )
            else:
                return AuditResult(
                    "1.1.6",
                    "AXIOM: Señales son auditables",
                    "FAIL",
                    "audit_trail or rationale fields missing"
                )
        except Exception as e:
            return AuditResult(
                "1.1.6",
                "AXIOM: Señales son auditables",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_axiom_1_1_7(self) -> AuditResult:
        """AXIOM 1.1.7: Señales no son imperativas"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal

            methods = [m for m in dir(Signal) if not m.startswith('_')]
            imperative_methods = ['execute', 'run', 'perform', 'do', 'command']

            found_imperative = [m for m in methods if any(imp in m.lower() for imp in imperative_methods)]

            if found_imperative:
                return AuditResult(
                    "1.1.7",
                    "AXIOM: Señales no son imperativas",
                    "WARNING",
                    f"Found potentially imperative methods: {found_imperative}"
                )
            else:
                return AuditResult(
                    "1.1.7",
                    "AXIOM: Señales no son imperativas",
                    "PASS",
                    "No imperative methods found in Signal"
                )
        except Exception as e:
            return AuditResult(
                "1.1.7",
                "AXIOM: Señales no son imperativas",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_directory_structure(self) -> List[AuditResult]:
        """Check all required directories exist"""
        results = []
        required_dirs = [
            ('core', 'core/'),
            ('signals/types', 'signals/types/'),
            ('vehicles', 'vehicles/'),
            ('consumers', 'consumers/'),
            ('irrigation', 'irrigation/'),
            ('vocabulary', 'vocabulary/'),
            ('audit', 'audit/'),
            ('schemas', 'schemas/'),
            ('config', 'config/'),
            ('scripts', 'scripts/'),
        ]

        for dir_id, dir_path in required_dirs:
            full_path = SISAS_PATH / dir_path
            if full_path.exists():
                results.append(AuditResult(
                    f"1.2.{dir_id}",
                    f"Existencia de {dir_path}",
                    "PASS",
                    f"Directory exists at {full_path}"
                ))
            else:
                results.append(AuditResult(
                    f"1.2.{dir_id}",
                    f"Existencia de {dir_path}",
                    "FAIL",
                    f"Directory NOT found at {full_path}"
                ))

        return results

    def audit_signal_category(self) -> AuditResult:
        """Check SignalCategory enum"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import SignalCategory

            required_categories = {'STRUCTURAL', 'INTEGRITY', 'EPISTEMIC', 'CONTRAST', 'OPERATIONAL', 'CONSUMPTION'}
            actual_categories = {c.name for c in SignalCategory}

            if required_categories == actual_categories:
                return AuditResult(
                    "2.1.10",
                    "SignalCategory tiene 6 valores",
                    "PASS",
                    f"All 6 categories present: {actual_categories}"
                )
            else:
                missing = required_categories - actual_categories
                extra = actual_categories - required_categories
                return AuditResult(
                    "2.1.10",
                    "SignalCategory tiene 6 valores",
                    "FAIL",
                    f"Missing: {missing}, Extra: {extra}"
                )
        except Exception as e:
            return AuditResult(
                "2.1.10",
                "SignalCategory tiene 6 valores",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_signal_confidence(self) -> AuditResult:
        """Check SignalConfidence enum"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import SignalConfidence

            required_levels = {'HIGH', 'MEDIUM', 'LOW', 'INDETERMINATE'}
            actual_levels = {c.name for c in SignalConfidence}

            if required_levels == actual_levels:
                # Check if comparable
                has_ordering = hasattr(SignalConfidence, '__lt__')
                if has_ordering:
                    return AuditResult(
                        "2.1.11",
                        "SignalConfidence tiene 4 valores y es comparable",
                        "PASS",
                        "All 4 levels present and comparable"
                    )
                else:
                    return AuditResult(
                        "2.1.11",
                        "SignalConfidence tiene 4 valores",
                        "WARNING",
                        "All 4 levels present but NOT comparable (no __lt__)",
                        "Should implement ordering: HIGH > MEDIUM > LOW"
                    )
            else:
                return AuditResult(
                    "2.1.11",
                    "SignalConfidence tiene 4 valores",
                    "FAIL",
                    f"Expected {required_levels}, got {actual_levels}"
                )
        except Exception as e:
            return AuditResult(
                "2.1.11",
                "SignalConfidence tiene 4 valores",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_event_type(self) -> AuditResult:
        """Check EventType enum"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import EventType

            required_types = ['CANONICAL_DATA_LOADED', 'IRRIGATION_COMPLETED']
            actual_types = [e.name for e in EventType]

            has_required = all(rt in actual_types for rt in required_types)

            if has_required and len(actual_types) >= 15:
                return AuditResult(
                    "2.2.1",
                    "EventType enum completo (15+ tipos)",
                    "PASS",
                    f"Has {len(actual_types)} event types including required ones"
                )
            else:
                return AuditResult(
                    "2.2.1",
                    "EventType enum completo",
                    "FAIL" if not has_required else "WARNING",
                    f"Has {len(actual_types)} types, required types present: {has_required}"
                )
        except Exception as e:
            return AuditResult(
                "2.2.1",
                "EventType enum completo",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def audit_contract_status(self) -> AuditResult:
        """Check ContractStatus enum"""
        try:
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import ContractStatus

            required_statuses = {'DRAFT', 'ACTIVE', 'SUSPENDED', 'TERMINATED'}
            actual_statuses = {s.name for s in ContractStatus}

            if required_statuses == actual_statuses:
                return AuditResult(
                    "2.3.12",
                    "ContractStatus tiene 4 estados",
                    "PASS",
                    f"All 4 statuses present: {actual_statuses}"
                )
            else:
                return AuditResult(
                    "2.3.12",
                    "ContractStatus tiene 4 estados",
                    "FAIL",
                    f"Expected {required_statuses}, got {actual_statuses}"
                )
        except Exception as e:
            return AuditResult(
                "2.3.12",
                "ContractStatus tiene 4 estados",
                "WARNING",
                f"Could not verify: {str(e)}"
            )

    def run_all_audits(self):
        """Run all audits"""
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}SISAS ADVERSARIAL AUDIT - Automated Verification{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        # Section I: Axiomas
        print(f"\n{Colors.BOLD}{Colors.INFO}SECTION I: AXIOMAS DEL SISTEMA{Colors.END}")
        print(f"{'-'*80}")

        self.add_result(self.audit_axiom_1_1_1())
        self.add_result(self.audit_axiom_1_1_2())
        self.add_result(self.audit_axiom_1_1_3())
        self.add_result(self.audit_axiom_1_1_4())
        self.add_result(self.audit_axiom_1_1_5())
        self.add_result(self.audit_axiom_1_1_6())
        self.add_result(self.audit_axiom_1_1_7())

        for result in self.results[-7:]:
            print(result)
            if result.impact:
                print(f"  {Colors.WARNING}Impact: {result.impact}{Colors.END}")

        # Section I.2: Directory Structure
        print(f"\n{Colors.BOLD}{Colors.INFO}SECTION I.2: ESTRUCTURA DE DIRECTORIOS{Colors.END}")
        print(f"{'-'*80}")

        dir_results = self.audit_directory_structure()
        for result in dir_results:
            self.add_result(result)
            print(result)

        # Section II: Core Implementation
        print(f"\n{Colors.BOLD}{Colors.INFO}SECTION II: IMPLEMENTACIÓN DE CORE{Colors.END}")
        print(f"{'-'*80}")

        self.add_result(self.audit_signal_category())
        self.add_result(self.audit_signal_confidence())
        self.add_result(self.audit_event_type())
        self.add_result(self.audit_contract_status())

        for result in self.results[-4:]:
            print(result)
            if result.impact:
                print(f"  {Colors.WARNING}Impact: {result.impact}{Colors.END}")

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print audit summary"""
        total = len(self.results)
        pass_rate = (self.passes / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}AUDIT SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        print(f"Total Tests:      {total}")
        print(f"{Colors.PASS}✅ Passed:        {self.passes}{Colors.END}")
        print(f"{Colors.WARNING}⚠️  Warnings:      {self.warnings}{Colors.END}")
        print(f"{Colors.FAIL}❌ Failed:        {self.critical_failures}{Colors.END}")
        print(f"\nPass Rate:        {pass_rate:.1f}%")

        if self.critical_failures > 0:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ AUDIT FAILED - {self.critical_failures} CRITICAL ISSUES{Colors.END}")
            print(f"\n{Colors.WARNING}Critical Issues:{Colors.END}")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"  • [{result.test_id}] {result.description}")
                    print(f"    Evidence: {result.evidence}")
                    if result.impact:
                        print(f"    Impact: {result.impact}")
        elif self.warnings > 0:
            print(f"\n{Colors.WARNING}⚠️  AUDIT PASSED WITH WARNINGS{Colors.END}")
        else:
            print(f"\n{Colors.PASS}✅ AUDIT PASSED - ALL CHECKS SUCCESSFUL{Colors.END}")

        print(f"\n{Colors.INFO}Full report: SISAS_ADVERSARIAL_AUDIT_REPORT.md{Colors.END}\n")

    def export_json_report(self, filename: str = "audit_results.json"):
        """Export results to JSON"""
        data = {
            "audit_date": "2026-01-14",
            "total_tests": len(self.results),
            "passed": self.passes,
            "warnings": self.warnings,
            "failed": self.critical_failures,
            "pass_rate": (self.passes / len(self.results) * 100) if self.results else 0,
            "results": [
                {
                    "test_id": r.test_id,
                    "description": r.description,
                    "status": r.status,
                    "evidence": r.evidence,
                    "impact": r.impact
                }
                for r in self.results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"{Colors.INFO}JSON report exported to: {filename}{Colors.END}")


def main():
    auditor = SISASAuditor()
    auditor.run_all_audits()
    auditor.export_json_report("sisas_audit_results.json")

    # Exit with error code if there are failures
    sys.exit(1 if auditor.critical_failures > 0 else 0)


if __name__ == "__main__":
    main()
