# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vocabulary/alignment_checker.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import json

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
    """Reporte de alineación de vocabularios con análisis avanzado"""
    is_aligned: bool
    issues: List[AlignmentIssue] = field(default_factory=list)
    signals_checked: int = 0
    capabilities_checked: int = 0
    coverage_percentage: float = 0.0
    # Enhancement: Análisis de dependencias
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    orphaned_components: List[str] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)

    def add_issue(self, issue: AlignmentIssue):
        self.issues.append(issue)
        if issue.severity == "critical":
            self.is_aligned = False
    
    def get_issues_by_severity(self, severity: str) -> List[AlignmentIssue]:
        """Obtiene issues filtrados por severidad"""
        return [i for i in self.issues if i.severity == severity]
    
    def get_issues_by_type(self, issue_type: str) -> List[AlignmentIssue]:
        """Obtiene issues filtrados por tipo"""
        return [i for i in self.issues if i.issue_type == issue_type]


@dataclass
class VocabularyAlignmentChecker:
    """
    Verificador de alineación entre vocabularios con análisis de grafos.

    Detecta:
    1. Señales sin productor
    2. Señales sin consumidor
    3. Capacidades que requieren señales inexistentes
    4. Capacidades que producen señales no definidas
    5. Dependencias circulares
    6. Componentes huérfanos
    7. Rutas críticas en el grafo de dependencias
    """

    signal_vocabulary: SignalVocabulary = field(default_factory=SignalVocabulary)
    capability_vocabulary: CapabilityVocabulary = field(default_factory=CapabilityVocabulary)
    
    # Enhancement: Cache de análisis
    _last_report: Optional[AlignmentReport] = None
    _report_cache_valid: bool = False

    def check_alignment(self, use_cache: bool = True) -> AlignmentReport:
        """
        Verifica alineación completa entre vocabularios con análisis de grafos.
        """
        if use_cache and self._report_cache_valid and self._last_report:
            return self._last_report
        
        report = AlignmentReport(is_aligned=True)

        # 1. Verificar que cada señal tiene al menos un productor
        self._check_signal_producers(report)

        # 2. Verificar que cada señal tiene al menos un consumidor potencial
        self._check_signal_consumers(report)

        # 3. Verificar que las capacidades referencian señales válidas
        self._check_capability_signals(report)

        # 4. Verificar dependencias de capacidades
        self._check_capability_dependencies(report)
        
        # Enhancement: Análisis de grafos
        # 5. Construir grafo de dependencias
        report.dependency_graph = self._build_dependency_graph()
        
        # 6. Detectar dependencias circulares
        report.circular_dependencies = self._detect_circular_dependencies(report.dependency_graph)
        if report.circular_dependencies:
            for cycle in report.circular_dependencies:
                report.add_issue(AlignmentIssue(
                    issue_type="circular_dependency",
                    severity="warning",
                    component=" -> ".join(cycle),
                    details=f"Circular dependency detected in capability chain",
                    suggested_fix="Review and break circular dependency"
                ))
        
        # 7. Identificar componentes huérfanos
        report.orphaned_components = self._find_orphaned_components(report.dependency_graph)
        for orphan in report.orphaned_components:
            report.add_issue(AlignmentIssue(
                issue_type="orphaned_component",
                severity="info",
                component=orphan,
                details=f"Component has no incoming or outgoing dependencies",
                suggested_fix="Consider if component is needed or add connections"
            ))
        
        # 8. Calcular ruta crítica
        report.critical_path = self._calculate_critical_path(report.dependency_graph)

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
        
        # Cachear reporte
        self._last_report = report
        self._report_cache_valid = True

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
        by_type: Dict[str, List[AlignmentIssue]] = {}
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
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Construye grafo de dependencias entre capacidades"""
        graph = defaultdict(list)
        
        for cap_id, cap_def in self.capability_vocabulary.definitions.items():
            for dep_id in cap_def.dependencies:
                if self.capability_vocabulary.is_valid(dep_id):
                    graph[cap_id].append(dep_id)
        
        return dict(graph)
    
    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detecta ciclos en el grafo de dependencias usando DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Encontramos un ciclo
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _find_orphaned_components(self, graph: Dict[str, List[str]]) -> List[str]:
        """Identifica componentes sin conexiones"""
        all_nodes = set(graph.keys())
        referenced_nodes = set()
        
        for deps in graph.values():
            referenced_nodes.update(deps)
        
        # Nodos que no tienen dependencias y no son referenciados
        orphans = []
        for node in all_nodes:
            has_outgoing = len(graph.get(node, [])) > 0
            has_incoming = node in referenced_nodes
            
            if not has_outgoing and not has_incoming:
                orphans.append(node)
        
        return orphans
    
    def _calculate_critical_path(self, graph: Dict[str, List[str]]) -> List[str]:
        """Calcula la ruta crítica (camino más largo) en el grafo"""
        # Realizar ordenamiento topológico
        in_degree = defaultdict(int)
        for node in graph:
            for dep in graph.get(node, []):
                in_degree[dep] += 1
        
        # Cola de nodos sin dependencias entrantes
        queue = deque([node for node in graph if in_degree[node] == 0])
        
        # Distancias (profundidad) desde nodos raíz
        distances = defaultdict(int)
        predecessors = {}
        
        while queue:
            node = queue.popleft()
            
            for dep in graph.get(node, []):
                # Actualizar distancia si encontramos camino más largo
                if distances[node] + 1 > distances[dep]:
                    distances[dep] = distances[node] + 1
                    predecessors[dep] = node
                
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        
        # Encontrar el nodo con mayor distancia (final del camino crítico)
        if not distances:
            return []
        
        end_node = max(distances.items(), key=lambda x: x[1])[0]
        
        # Reconstruir camino
        path = [end_node]
        current = end_node
        while current in predecessors:
            current = predecessors[current]
            path.append(current)
        
        return list(reversed(path))
    
    def invalidate_cache(self):
        """Invalida el cache de reportes"""
        self._report_cache_valid = False
    
    def get_dependency_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del grafo de dependencias"""
        if not self._report_cache_valid or not self._last_report:
            self.check_alignment()
        
        graph = self._last_report.dependency_graph
        
        # Calcular métricas básicas
        total_nodes = len(graph)
        total_edges = sum(len(deps) for deps in graph.values())
        
        # Nodos con más dependencias (fan-out)
        max_fan_out = max((len(deps) for deps in graph.values()), default=0)
        
        # Nodos más referenciados (fan-in)
        ref_count = defaultdict(int)
        for deps in graph.values():
            for dep in deps:
                ref_count[dep] += 1
        max_fan_in = max(ref_count.values(), default=0)
        
        # Profundidad máxima
        max_depth = len(self._last_report.critical_path)
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "max_fan_out": max_fan_out,
            "max_fan_in": max_fan_in,
            "max_depth": max_depth,
            "has_cycles": len(self._last_report.circular_dependencies) > 0,
            "cycle_count": len(self._last_report.circular_dependencies),
            "orphan_count": len(self._last_report.orphaned_components),
            "density": (total_edges / (total_nodes * (total_nodes - 1))) if total_nodes > 1 else 0
        }
    
    def suggest_automated_fixes(self, report: AlignmentReport) -> List[Dict[str, Any]]:
        """Sugiere fixes automáticos basados en análisis de patrones"""
        suggestions = []
        
        # Agrupar issues por tipo para detectar patrones
        missing_signals = report.get_issues_by_type("missing_signal")
        orphan_signals = report.get_issues_by_type("orphan_signal")
        
        # Sugerir productores para señales huérfanas basado en categoría
        for issue in orphan_signals:
            signal_type = issue.component
            definition = self.signal_vocabulary.get(signal_type)
            if definition:
                # Buscar capacidades en la misma categoría
                similar_caps = [
                    cap_id for cap_id, cap_def in self.capability_vocabulary.definitions.items()
                    if definition.category.lower() in cap_id.lower()
                ]
                
                if similar_caps:
                    suggestions.append({
                        "issue_id": signal_type,
                        "fix_type": "assign_producer",
                        "suggested_producer": similar_caps[0],
                        "confidence": "medium",
                        "reasoning": f"Category match between signal and capability"
                    })
        
        return suggestions
