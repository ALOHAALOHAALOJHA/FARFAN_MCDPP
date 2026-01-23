# src/farfan_pipeline/orchestration/dependency_graph.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import deque
import logging


class DependencyStatus(Enum):
    """Estado de un nodo en el grafo de dependencias"""
    NOT_STARTED = auto()
    PENDING = auto()          # Esperando dependencias
    PENDING_RETRY = auto()    # Esperando reintento
    READY = auto()            # Dependencias satisfechas
    RUNNING = auto()
    COMPLETED = auto()
    PARTIAL = auto()          # Completado parcialmente
    FAILED = auto()
    BLOCKED = auto()          # Bloqueado por fallo upstream


@dataclass(frozen=True)
class DependencyEdge:
    """
    Arista del grafo de dependencias.
    
    Inmutable para garantizar integridad estructural.
    """
    source: str              # Fase que debe completar primero
    target: str              # Fase que depende de source
    edge_type: str = "hard"  # "hard" (obligatorio) o "soft" (opcional)
    
    def __hash__(self):
        return hash((self.source, self.target))


@dataclass
class DependencyNode:
    """
    Nodo del grafo de dependencias representando una fase.
    """
    phase_id: str
    phase_name: str
    status: DependencyStatus = DependencyStatus.NOT_STARTED
    
    # Configuración de la fase
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Señales esperadas de esta fase
    expected_signals: List[str] = field(default_factory=list)
    
    # Capacidades requeridas
    required_capabilities: List[str] = field(default_factory=list)
    
    # Metadatos de ejecución
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_ready(self, completed_phases: Set[str], graph: 'DependencyGraph') -> bool:
        """Verifica si esta fase puede ejecutarse"""
        if self.status not in [DependencyStatus.NOT_STARTED, DependencyStatus.PENDING, DependencyStatus.PENDING_RETRY]:
            return False
        
        # Verificar todas las dependencias hard
        dependencies = graph.get_upstream_dependencies(self.phase_id)
        for dep in dependencies:
            dep_node = graph.get_node(dep)
            if dep_node is None:
                return False
            
            edge = graph.get_edge(dep, self.phase_id)
            if edge and edge.edge_type == "hard":
                if dep_node.status not in [DependencyStatus.COMPLETED, DependencyStatus.PARTIAL]:
                    return False
        
        return True


@dataclass
class DependencyGraphValidationResult:
    """Resultado de validación del grafo"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cycles_detected: List[List[str]] = field(default_factory=list)
    orphan_nodes: List[str] = field(default_factory=list)
    missing_dependencies: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class DependencyGraph:
    """
    Grafo dirigido acíclico (DAG) de dependencias entre fases.
    
    RESPONSABILIDADES:
    1. Mantener estructura de dependencias
    2. Validar ausencia de ciclos
    3. Determinar qué fases están listas
    4. Propagar bloqueos por fallos
    
    INVARIANTES:
    - La estructura del grafo es inmutable después de la carga
    - Solo el estado de los nodos puede mutar
    - Debe ser un DAG válido (sin ciclos)
    """
    
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: Set[DependencyEdge] = field(default_factory=set)
    
    # Índices para búsqueda eficiente
    _upstream_index: Dict[str, Set[str]] = field(default_factory=dict)   # target -> sources
    _downstream_index: Dict[str, Set[str]] = field(default_factory=dict) # source -> targets
    
    # Estado de validación
    _validated: bool = False
    _validation_result: Optional[DependencyGraphValidationResult] = None
    
    # Logger
    _logger: logging.Logger = field(default=None)
    
    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestrator.DependencyGraph")
        
        # Construir índices
        self._rebuild_indices()
    
    # =========================================================================
    # GRAPH CONSTRUCTION
    # =========================================================================
    
    def add_node(self, node: DependencyNode):
        """Añade un nodo al grafo"""
        if self._validated:
            raise RuntimeError("Cannot modify graph after validation")
        
        self.nodes[node.phase_id] = node
        
        # Inicializar índices para este nodo
        if node.phase_id not in self._upstream_index:
            self._upstream_index[node.phase_id] = set()
        if node.phase_id not in self._downstream_index:
            self._downstream_index[node.phase_id] = set()
    
    def add_edge(self, edge: DependencyEdge):
        """Añade una arista al grafo"""
        if self._validated:
            raise RuntimeError("Cannot modify graph after validation")
        
        # Verificar que los nodos existen
        if edge.source not in self.nodes:
            raise ValueError(f"Source node '{edge.source}' not found")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node '{edge.target}' not found")
        
        self.edges.add(edge)
        
        # Actualizar índices
        self._upstream_index[edge.target].add(edge.source)
        self._downstream_index[edge.source].add(edge.target)
    
    def _rebuild_indices(self):
        """Reconstruye índices de búsqueda"""
        self._upstream_index = {node_id: set() for node_id in self.nodes}
        self._downstream_index = {node_id: set() for node_id in self.nodes}
        
        for edge in self.edges:
            if edge.target in self._upstream_index:
                self._upstream_index[edge.target].add(edge.source)
            if edge.source in self._downstream_index:
                self._downstream_index[edge.source].add(edge.target)
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate(self) -> DependencyGraphValidationResult: 
        """
        Valida el grafo de dependencias.
        
        Verifica: 
        1. Ausencia de ciclos
        2. No hay nodos huérfanos (sin entrada ni salida y no es raíz/hoja válida)
        3. Todas las dependencias referenciadas existen
        """
        errors = []
        warnings = []
        cycles = []
        orphans = []
        missing_deps = []
        
        # 1. Detectar ciclos usando DFS
        cycles = self._detect_cycles()
        if cycles:
            for cycle in cycles:
                errors.append(f"Cycle detected: {' -> '.join(cycle)}")
        
        # 2. Detectar nodos huérfanos
        root_phases = self._get_root_phases()
        leaf_phases = self._get_leaf_phases()
        
        for node_id in self.nodes:
            has_upstream = len(self._upstream_index.get(node_id, set())) > 0
            has_downstream = len(self._downstream_index.get(node_id, set())) > 0
            
            if not has_upstream and not has_downstream and node_id not in root_phases:
                orphans.append(node_id)
                warnings.append(f"Orphan node detected: {node_id}")
        
        # 3. Verificar dependencias referenciadas
        for edge in self.edges:
            if edge.source not in self.nodes:
                missing_deps.append((edge.target, edge.source))
                errors.append(f"Missing dependency: {edge.target} depends on non-existent {edge.source}")
        
        is_valid = len(errors) == 0
        
        self._validation_result = DependencyGraphValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            cycles_detected=cycles,
            orphan_nodes=orphans,
            missing_dependencies=missing_deps
        )
        
        if is_valid:
            self._validated = True
        
        return self._validation_result
    
    def _detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos usando DFS con coloreo de nodos"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node_id: WHITE for node_id in self.nodes}
        cycles = []
        
        def dfs(node_id: str, path: List[str]) -> bool:
            color[node_id] = GRAY
            path.append(node_id)
            
            for downstream in self._downstream_index.get(node_id, set()):
                if color[downstream] == GRAY:
                    # Ciclo encontrado
                    cycle_start = path.index(downstream)
                    cycles.append(path[cycle_start:] + [downstream])
                    return True
                elif color[downstream] == WHITE:
                    if dfs(downstream, path):
                        return True
            
            color[node_id] = BLACK
            path.pop()
            return False
        
        for node_id in self.nodes:
            if color[node_id] == WHITE:
                dfs(node_id, [])
        
        return cycles
    
    # =========================================================================
    # QUERY METHODS
    # =========================================================================
    
    def get_node(self, phase_id: str) -> Optional[DependencyNode]:
        """Obtiene un nodo por ID"""
        return self.nodes.get(phase_id)
    
    def get_edge(self, source: str, target: str) -> Optional[DependencyEdge]:
        """Obtiene una arista específica"""
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                return edge
        return None
    
    def get_upstream_dependencies(self, phase_id: str) -> Set[str]:
        """Obtiene fases de las que depende phase_id"""
        return self._upstream_index.get(phase_id, set()).copy()
    
    def get_downstream_dependents(self, phase_id: str) -> Set[str]:
        """Obtiene fases que dependen de phase_id"""
        return self._downstream_index.get(phase_id, set()).copy()
    
    def get_all_upstream_recursive(self, phase_id: str) -> Set[str]:
        """Obtiene todas las dependencias upstream recursivamente"""
        result = set()
        queue = deque([phase_id])
        
        while queue:
            current = queue.popleft()
            upstream = self._upstream_index.get(current, set())
            for up in upstream:
                if up not in result:
                    result.add(up)
                    queue.append(up)
        
        return result
    
    def get_all_downstream_recursive(self, phase_id: str) -> Set[str]:
        """Obtiene todos los dependientes downstream recursivamente"""
        result = set()
        queue = deque([phase_id])
        
        while queue:
            current = queue.popleft()
            downstream = self._downstream_index.get(current, set())
            for down in downstream: 
                if down not in result: 
                    result.add(down)
                    queue.append(down)
        
        return result
    
    def _get_root_phases(self) -> Set[str]:
        """Fases sin dependencias upstream (puntos de entrada)"""
        return {node_id for node_id in self.nodes 
                if len(self._upstream_index.get(node_id, set())) == 0}
    
    def _get_leaf_phases(self) -> Set[str]:
        """Fases sin dependientes downstream (puntos de salida)"""
        return {node_id for node_id in self.nodes 
                if len(self._downstream_index.get(node_id, set())) == 0}
    
    def get_ready_phases(self, completed: Set[str], failed: Set[str], active: Set[str]) -> Set[str]:
        """
        Obtiene fases que están listas para ejecutar.
        
        Una fase está lista si:
        1. No está completada, fallida, ni activa
        2. Todas sus dependencias hard están completadas (o parcialmente completadas)
        3. No está bloqueada por fallo upstream
        """
        ready = set()
        
        for node_id, node in self.nodes.items():
            # Saltar si ya procesada o activa
            if node_id in completed or node_id in failed or node_id in active: 
                continue
            
            # Verificar si está bloqueada
            if node.status == DependencyStatus.BLOCKED: 
                continue
            
            # Verificar dependencias
            if node.is_ready(completed, self):
                ready.add(node_id)
        
        return ready
    
    def get_newly_unblocked(self, completed_phase_id: str) -> List[str]:
        """
        Obtiene fases que se desbloquearon al completar una fase.
        
        Útil para emitir señales de coordinación.
        """
        newly_unblocked = []
        downstream = self.get_downstream_dependents(completed_phase_id)
        
        for phase_id in downstream:
            node = self.nodes.get(phase_id)
            if node and node.status == DependencyStatus.PENDING: 
                # Verificar si ahora está lista
                upstream = self.get_upstream_dependencies(phase_id)
                all_upstream_done = all(
                    self.nodes[up].status in [DependencyStatus.COMPLETED, DependencyStatus.PARTIAL]
                    for up in upstream
                    if up in self.nodes
                )
                if all_upstream_done:
                    newly_unblocked.append(phase_id)
        
        return newly_unblocked
    
    def get_permanently_blocked(self) -> Set[str]:
        """
        Obtiene fases permanentemente bloqueadas por fallos upstream.
        """
        blocked = set()
        
        for node_id, node in self.nodes.items():
            if node.status == DependencyStatus.BLOCKED:
                blocked.add(node_id)
            elif node.status == DependencyStatus.FAILED:
                # Propagar bloqueo a downstream
                downstream = self.get_all_downstream_recursive(node_id)
                blocked.update(downstream)
        
        return blocked
    
    # =========================================================================
    # STATE MUTATION
    # =========================================================================
    
    def update_node_status(self, phase_id: str, new_status: DependencyStatus):
        """
        Actualiza el estado de un nodo. 
        
        ÚNICA forma permitida de mutar estado del grafo. 
        """
        node = self.nodes.get(phase_id)
        if node is None:
            raise ValueError(f"Node '{phase_id}' not found")
        
        old_status = node.status
        node.status = new_status
        
        self._logger.debug(f"Node {phase_id}: {old_status.name} -> {new_status.name}")
        
        # Propagar bloqueo si es fallo
        if new_status == DependencyStatus.FAILED:
            self._propagate_block(phase_id)
    
    def _propagate_block(self, failed_phase_id: str):
        """
        Propaga bloqueo a fases downstream cuando una fase falla.
        """
        downstream = self.get_all_downstream_recursive(failed_phase_id)
        
        for phase_id in downstream:
            node = self.nodes.get(phase_id)
            if node and node.status in [DependencyStatus.NOT_STARTED, DependencyStatus.PENDING]:
                node.status = DependencyStatus.BLOCKED
                self._logger.warning(f"Phase {phase_id} blocked due to failure of {failed_phase_id}")
    
    def reset_for_retry(self, phase_id: str):
        """
        Resetea una fase para reintento.
        """
        node = self.nodes.get(phase_id)
        if node:
            node.status = DependencyStatus.PENDING_RETRY
            node.execution_metadata = {}
    
    # =========================================================================
    # SERIALIZATION & SNAPSHOTS
    # =========================================================================
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Obtiene snapshot completo del estado actual del grafo.
        
        Útil para auditoría y debugging.
        """
        return {
            "nodes": {
                node_id: {
                    "phase_id": node.phase_id,
                    "phase_name": node.phase_name,
                    "status": node.status.name,
                    "upstream": list(self._upstream_index.get(node_id, set())),
                    "downstream": list(self._downstream_index.get(node_id, set()))
                }
                for node_id, node in self.nodes.items()
            },
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.edge_type
                }
                for edge in self.edges
            ],
            "summary": self.get_summary()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen del grafo. 
        """
        status_counts = {}
        for node in self.nodes.values():
            status_name = node.status.name
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "root_phases": list(self._get_root_phases()),
            "leaf_phases": list(self._get_leaf_phases()),
            "status_distribution": status_counts,
            "is_validated": self._validated
        }
    
    def get_node_config(self, phase_id: str) -> Dict[str, Any]:
        """Obtiene configuración de un nodo"""
        node = self.nodes.get(phase_id)
        return node.config if node else {}
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DependencyGraph':
        """
        Construye grafo desde configuración YAML/JSON.
        
        Formato esperado:
        {
            "phases": [
                {
                    "id": "phase_00",
                    "name": "Bootstrap Phase",
                    "depends_on": [],
                    "expected_signals": ["StructuralAlignmentSignal"],
                    "config": {... }
                },
                {
                    "id": "phase_01",
                    "name": "Enrichment Phase",
                    "depends_on": ["phase_00"],
                    ... 
                }
            ]
        }
        """
        graph = cls()
        
        # Crear nodos
        for phase_config in config.get("phases", []):
            node = DependencyNode(
                phase_id=phase_config["id"],
                phase_name=phase_config.get("name", phase_config["id"]),
                expected_signals=phase_config.get("expected_signals", []),
                required_capabilities=phase_config.get("required_capabilities", []),
                config=phase_config.get("config", {})
            )
            graph.add_node(node)
        
        # Crear aristas
        for phase_config in config.get("phases", []):
            target = phase_config["id"]
            for source in phase_config.get("depends_on", []):
                edge_type = "hard"  # Por defecto
                if isinstance(source, dict):
                    edge_type = source.get("type", "hard")
                    source = source["phase"]
                
                edge = DependencyEdge(
                    source=source,
                    target=target,
                    edge_type=edge_type
                )
                graph.add_edge(edge)
        
        return graph
    
    @classmethod
    def from_yaml_file(cls, file_path: str) -> 'DependencyGraph':
        """Carga grafo desde archivo YAML"""
        import yaml
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return cls.from_config(config)
    # =========================================================================
    # VISUALIZATION
    # =========================================================================

    def export_to_dot(self, output_path: str) -> None:
        """Export dependency graph to DOT format for Graphviz."""
        dot_lines = [
            "digraph FARFAN_Dependency_Graph {",
            "  rankdir=TD;",  # Top to bottom
            "  node [shape=box];",
            "  ",
        ]

        # Add nodes with status-based styling
        for node_id, node in self.nodes.items():
            status_color = self._get_status_color(node.status)
            label = f"{node_id}\\n({node.status.name})"
            dot_lines.append(f'  "{node_id}" [label="{label}" fillcolor="{status_color}" style=filled];')

        # Add edges
        for edge in self.edges:
            edge_style = "solid" if edge.edge_type == "hard" else "dashed"
            dot_lines.append(f'  "{edge.source}" -> "{edge.target}" [style={edge_style}];')

        dot_lines.append("}")

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(dot_lines))

    def _get_status_color(self, status: DependencyStatus) -> str:
        """Get color for node status."""
        colors = {
            DependencyStatus.PENDING: "lightgray",
            DependencyStatus.READY: "lightblue",
            DependencyStatus.RUNNING: "yellow",
            DependencyStatus.COMPLETED: "lightgreen",
            DependencyStatus.FAILED: "lightcoral",
            DependencyStatus.BLOCKED: "orange",
            DependencyStatus.NOT_STARTED: "white",
            DependencyStatus.PENDING_RETRY: "pink",
            DependencyStatus.PARTIAL: "lightgreen", # Same as completed usually
        }
        return colors.get(status, "white")

    def export_to_mermaid(self, output_path: str) -> None:
        """Export to Mermaid.js format for Markdown rendering."""
        lines = ["graph TD"]

        # Add nodes
        for node_id, node in self.nodes.items():
            status_icon = self._get_status_icon(node.status)
            lines.append(f"  {node_id}[{status_icon} {node_id}<br/>{node.status.name}]")

        # Add edges
        for edge in self.edges:
            style = " -.-> " if edge.edge_type == "soft" else " --> "
            lines.append(f"  {edge.source}{style}{edge.target}")

        # Add classes for styling (basic)
        lines.append("\n  classDef completed fill:#90EE90,stroke:#333,stroke-width:2px")
        lines.append("  classDef failed fill:#F08080,stroke:#333,stroke-width:2px")
        lines.append("  classDef running fill:#FFD700,stroke:#333,stroke-width:2px")
        
        # Apply classes based on status (simplified)
        for node_id, node in self.nodes.items():
            if node.status == DependencyStatus.COMPLETED:
                lines.append(f"  class {node_id} completed")
            elif node.status == DependencyStatus.FAILED:
                lines.append(f"  class {node_id} failed")
            elif node.status == DependencyStatus.RUNNING:
                lines.append(f"  class {node_id} running")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _get_status_icon(self, status: DependencyStatus) -> str:
        """Get emoji icon for status."""
        icons = {
            DependencyStatus.NOT_STARTED: "⚪",
            DependencyStatus.PENDING: "⏳",
            DependencyStatus.PENDING_RETRY: "🔄",
            DependencyStatus.READY: "✅",
            DependencyStatus.RUNNING: "🚀",
            DependencyStatus.COMPLETED: "✅",
            DependencyStatus.PARTIAL: "⚠️",
            DependencyStatus.FAILED: "❌",
            DependencyStatus.BLOCKED: "🚫",
        }
        return icons.get(status, "❓")
