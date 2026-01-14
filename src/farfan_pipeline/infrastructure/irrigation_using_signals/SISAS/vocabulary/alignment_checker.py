# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/alignment_checker.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .signal_vocabulary import SignalVocabulary
from .capability_vocabulary import CapabilityVocabulary


@dataclass
class AlignmentIssue:
    """Problema de alineación detectado"""
    issue_type: str  # "missing_signal", "missing_capability", "incompatible_version", "orphan_signal"
    severity: str    # "critical", "warning", "info"
    component: str   # Componente afectado
    details: str     # Descripción del problema
    suggested_fix: str = ""


@dataclass
class AlignmentReport:
    """Reporte de alineación de vocabularios"""
    is_aligned: bool
    issues: List[AlignmentIssue] = field(default_factory=list)
    signals_checked: int = 0
    capabilities_checked: int = 0
    coverage_percentage: float = 0.0

    def add_issue(self, issue: AlignmentIssue):
        self.issues.append(issue)
        if issue.severity == "critical":
            self.is_aligned = False


@dataclass
class VocabularyAlignmentChecker:
    """
    Verificador de alineación entre vocabularios de señales y capacidades.

    Detecta:
    1. Señales sin productor
    2. Señales sin consumidor
    3. Capacidades que requieren señales inexistentes
    4. Capacidades que producen señales no definidas
    """

    signal_vocabulary: SignalVocabulary = field(default_factory=SignalVocabulary)
    capability_vocabulary: CapabilityVocabulary = field(default_factory=CapabilityVocabulary)

    def check_alignment(self) -> AlignmentReport:
        """
        Verifica alineación completa entre vocabularios.
        """
        report = AlignmentReport(is_aligned=True)

        # 1. Verificar que cada señal tiene al menos un productor
        self._check_signal_producers(report)

        # 2. Verificar que cada señal tiene al menos un consumidor potencial
        self._check_signal_consumers(report)

        # 3. Verificar que las capacidades referencian señales válidas
        self._check_capability_signals(report)

        # 4. Verificar dependencias de capacidades
        self._check_capability_dependencies(report)

        # Calcular cobertura
        total_signals = len(self.signal_vocabulary.definitions)
        total_capabilities = len(self.capability_vocabulary.definitions)
        critical_issues = sum(1 for i in report.issues if i.severity == "critical")

        report.signals_checked = total_signals
        report.capabilities_checked = total_capabilities

        if total_signals + total_capabilities > 0:
            report.coverage_percentage = (
                1 - (critical_issues / (total_signals + total_capabilities))
            ) * 100

        return report

    def _check_signal_producers(self, report: AlignmentReport):
        """Verifica que cada señal tiene productor"""
        for signal_type in self.signal_vocabulary.definitions:
            producers = self.capability_vocabulary.get_producers_of(signal_type)

            if not producers:
                report.add_issue(AlignmentIssue(
                    issue_type="orphan_signal",
                    severity="warning",
                    component=signal_type,
                    details=f"Signal type '{signal_type}' has no defined producer capability",
                    suggested_fix=f"Add a capability that produces '{signal_type}'"
                ))

    def _check_signal_consumers(self, report: AlignmentReport):
        """Verifica que cada señal tiene consumidor potencial"""
        for signal_type in self.signal_vocabulary.definitions:
            consumers = self.capability_vocabulary.get_consumers_of(signal_type)

            # No es crítico si no tiene consumidor, pero es una advertencia
            if not consumers:
                report.add_issue(AlignmentIssue(
                    issue_type="unused_signal",
                    severity="info",
                    component=signal_type,
                    details=f"Signal type '{signal_type}' has no defined consumer capability",
                    suggested_fix=f"Consider if '{signal_type}' is needed or add a consumer"
                ))

    def _check_capability_signals(self, report: AlignmentReport):
        """Verifica que las capacidades referencian señales válidas"""
        for cap_id, cap_def in self.capability_vocabulary.definitions.items():
            # Verificar señales requeridas
            for signal_type in cap_def.required_signals:
                if signal_type != "*" and not self.signal_vocabulary.is_valid_type(signal_type):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_signal",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' requires undefined signal '{signal_type}'",
                        suggested_fix=f"Define signal type '{signal_type}' in SignalVocabulary"
                    ))

            # Verificar señales producidas
            for signal_type in cap_def.produced_signals:
                if signal_type != "*" and not self.signal_vocabulary.is_valid_type(signal_type):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_signal",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' produces undefined signal '{signal_type}'",
                        suggested_fix=f"Define signal type '{signal_type}' in SignalVocabulary"
                    ))

    def _check_capability_dependencies(self, report: AlignmentReport):
        """Verifica dependencias entre capacidades"""
        for cap_id, cap_def in self.capability_vocabulary.definitions.items():
            for dep_id in cap_def.dependencies:
                if not self.capability_vocabulary.is_valid(dep_id):
                    report.add_issue(AlignmentIssue(
                        issue_type="missing_capability",
                        severity="critical",
                        component=cap_id,
                        details=f"Capability '{cap_id}' depends on undefined capability '{dep_id}'",
                        suggested_fix=f"Define capability '{dep_id}' in CapabilityVocabulary"
                    ))

    def check_vehicle_alignment(
        self,
        vehicle_id: str,
        declared_signals: List[str],
        declared_capabilities: List[str]
    ) -> AlignmentReport:
        """
        Verifica alineación de un vehículo específico.
        """
        report = AlignmentReport(is_aligned=True)

        # Verificar señales declaradas
        for signal_type in declared_signals:
            if not self.signal_vocabulary.is_valid_type(signal_type):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_signal",
                    severity="critical",
                    component=vehicle_id,
                    details=f"Vehicle declares undefined signal type '{signal_type}'",
                    suggested_fix=f"Add '{signal_type}' to SignalVocabulary or remove from vehicle"
                ))

        # Verificar capacidades declaradas
        for cap_id in declared_capabilities:
            if not self.capability_vocabulary.is_valid(cap_id):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_capability",
                    severity="critical",
                    component=vehicle_id,
                    details=f"Vehicle declares undefined capability '{cap_id}'",
                    suggested_fix=f"Add '{cap_id}' to CapabilityVocabulary or remove from vehicle"
                ))

        report.signals_checked = len(declared_signals)
        report.capabilities_checked = len(declared_capabilities)

        return report

    def check_irrigation_route_alignment(
        self,
        route_id: str,
        vehicles: List[str],
        required_signals: List[str],
        target_consumers: List[str]
    ) -> AlignmentReport:
        """
        Verifica alineación de una ruta de irrigación.
        """
        report = AlignmentReport(is_aligned=True)

        # Verificar que los vehículos pueden producir las señales requeridas
        for signal_type in required_signals:
            if not self.signal_vocabulary.is_valid_type(signal_type):
                report.add_issue(AlignmentIssue(
                    issue_type="missing_signal",
                    severity="critical",
                    component=route_id,
                    details=f"Route requires undefined signal type '{signal_type}'",
                    suggested_fix=f"Define '{signal_type}' or update route requirements"
                ))

        return report

    def generate_gap_resolution_plan(self, report: AlignmentReport) -> List[Dict[str, Any]]:
        """
        Genera plan de resolución de gaps basado en el reporte.
        """
        plan = []

        # Agrupar issues por tipo
        by_type:  Dict[str, List[AlignmentIssue]] = {}
        for issue in report.issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)

        # Generar pasos del plan
        priority = 1

        # Primero resolver señales faltantes (críticas)
        if "missing_signal" in by_type:
            plan.append({
                "priority": priority,
                "action": "DEFINE_MISSING_SIGNALS",
                "description": "Definir tipos de señales faltantes en SignalVocabulary",
                "items": [i.component for i in by_type["missing_signal"]],
                "severity": "critical"
            })
            priority += 1

        # Luego resolver capacidades faltantes
        if "missing_capability" in by_type:
            plan.append({
                "priority": priority,
                "action": "DEFINE_MISSING_CAPABILITIES",
                "description": "Definir capacidades faltantes en CapabilityVocabulary",
                "items": [i.component for i in by_type["missing_capability"]],
                "severity":  "critical"
            })
            priority += 1

        # Luego resolver señales huérfanas
        if "orphan_signal" in by_type:
            plan.append({
                "priority":  priority,
                "action": "ASSIGN_PRODUCERS",
                "description": "Asignar productores a señales huérfanas",
                "items": [i.component for i in by_type["orphan_signal"]],
                "severity":  "warning"
            })
            priority += 1

        # Finalmente revisar señales no usadas
        if "unused_signal" in by_type:
            plan.append({
                "priority": priority,
                "action":  "REVIEW_UNUSED_SIGNALS",
                "description": "Revisar si las señales no usadas son necesarias",
                "items": [i.component for i in by_type["unused_signal"]],
                "severity": "info"
            })

        return plan
