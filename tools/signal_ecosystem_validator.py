#!/usr/bin/env python3
"""
Signal Ecosystem Validator - Análisis basado en AST

Este script analiza SOLO imports reales en tu código para determinar
qué archivos de signals están realmente en uso.

NO hace suposiciones. NO adivina. Solo lee el AST.
"""

import ast
from pathlib import Path
from typing import Dict, Set, List
from dataclasses import dataclass, field


@dataclass
class ModuleAnalysis:
    """Resultado del análisis de un módulo."""
    
    filepath: Path
    imports_from_signals: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    is_dead_code: bool = False
    reason: str = ""


class SignalEcosystemValidator:
    """Validador del ecosistema de signals basado en AST."""
    
    SIGNAL_MODULES = [
        'signal_aliasing',
        'signal_cache_invalidation', 
        'signal_consumption',
        'signal_context_scoper',
        'signal_contract_validator',
        'signal_evidence_extractor',
        'signal_fallback_fusion',
        'signal_intelligence_layer',
        'signal_loader',
        'signal_quality_metrics',
        'signal_registry',
        'signal_resolution',
        'signal_semantic_expander',
        'signals',
    ]
    
    def __init__(self, src_root: Path):
        """Inicializa validador con ruta raíz del código."""
        self.src_root = src_root
        self.orchestrator_dir = src_root / "core" / "orchestrator"
        self.results: Dict[str, ModuleAnalysis] = {}
        
    def analyze_file(self, filepath: Path) -> ModuleAnalysis:
        """Analiza un archivo Python y extrae sus imports reales."""
        analysis = ModuleAnalysis(filepath=filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            # Extraer imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    
                    # ¿Importa desde signals?
                    for signal_mod in self.SIGNAL_MODULES:
                        if signal_mod in module:
                            analysis.imports_from_signals.add(signal_mod)
                            
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        for signal_mod in self.SIGNAL_MODULES:
                            if signal_mod in name:
                                analysis.imports_from_signals.add(signal_mod)
        
        except Exception as e:
            analysis.reason = f"Error parsing: {e}"
        
        return analysis
    
    def scan_ecosystem(self) -> Dict[str, ModuleAnalysis]:
        """Escanea todo el ecosistema de orchestrator."""
        
        # 1. Analizar TODOS los archivos de signals primero
        print("📂 Scanning signal modules...")
        for signal_mod in self.SIGNAL_MODULES:
            signal_file = self.orchestrator_dir / f"{signal_mod}.py"
            if signal_file.exists():
                self.results[signal_mod] = self.analyze_file(signal_file)
                print(f"  ✓ {signal_mod}.py")
        
        # 2. Construir grafo de dependencias ENTRE signals
        print("\n🔗 Building signal-to-signal dependency graph...")
        for signal_mod, analysis in self.results.items():
            for imported_signal in analysis.imports_from_signals:
                if imported_signal in self.results:
                    self.results[imported_signal].imported_by.add(f"{signal_mod}.py")
                    print(f"  {signal_mod} → imports → {imported_signal}")
        
        # 3. Analizar archivos principales del orchestrator
        print("\n📋 Scanning main orchestrator files...")
        main_files = [
            'evidence_assembler.py', 'evidence_registry.py', 'evidence_validator.py', 'executor_config.py',  'executor_profiler.py', 'executors.py',        'core.py',
            'chunk_router.py', 
            'resource_integration.py', 'resource_manager.py', 'task_planner.py', 'executor_config.py',
            'factory.py',
            'base_executor_with_contract.py', 
            'irrigation_synchronizer.py',
            'arg_router.py',
            'method_registry.py',
        ]
        
        for main_file in main_files:
            main_path = self.orchestrator_dir / main_file
            if main_path.exists():
                analysis = self.analyze_file(main_path)
                
                # Marcar qué signals son importados por archivos principales
                for signal_mod in analysis.imports_from_signals:
                    if signal_mod in self.results:
                        self.results[signal_mod].imported_by.add(main_file)
                        print(f"  {main_file} → imports → {signal_mod}")
        
        # 4. Identificar ROOT nodes (importados por código principal)
        print("\n🌳 Identifying root nodes...")
        root_nodes = set()
        for signal_mod, analysis in self.results.items():
            for importer in analysis.imported_by:
                if not importer.startswith('signal_'):
                    root_nodes.add(signal_mod)
                    print(f"  ROOT: {signal_mod} (used by {importer})")
        
        # 5. Propagar vitalidad desde roots usando BFS
        print("\n♻️  Propagating liveness from roots...")
        alive = set(root_nodes)
        queue = list(root_nodes)
        
        while queue:
            current = queue.pop(0)
            if current not in self.results:
                continue
                
            # Marcar dependencias transitivas como vivas
            for dep in self.results[current].imports_from_signals:
                if dep not in alive and dep in self.results:
                    alive.add(dep)
                    queue.append(dep)
                    print(f"  {dep} is alive (transitively via {current})")
        
        # 6. Marcar código muerto (no alcanzable desde roots)
        print("\n💀 Marking dead code...")
        for signal_mod, analysis in self.results.items():
            if signal_mod not in alive:
                analysis.is_dead_code = True
                analysis.reason = "Not reachable from any main orchestrator file"
                print(f"  DEAD: {signal_mod}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Genera reporte de análisis."""
        
        lines = []
        lines.append("=" * 80)
        lines.append("SIGNAL ECOSYSTEM ANALYSIS - COMPLETE GRAPH TRAVERSAL")
        lines.append("=" * 80)
        lines.append("")
        
        # ROOT NODES: Importados directamente por código principal
        root_nodes = {}
        for mod, analysis in self.results.items():
            for importer in analysis.imported_by:
                if not importer.startswith('signal_'):
                    root_nodes[mod] = analysis
                    break
        
        if root_nodes:
            lines.append("🌳 ROOT NODES (imported by main orchestrator code)")
            lines.append("-" * 80)
            for mod, analysis in sorted(root_nodes.items()):
                importers = [i for i in analysis.imported_by if not i.startswith('signal_')]
                lines.append(f"  {mod}.py")
                lines.append(f"    → Used by: {', '.join(sorted(importers))}")
            lines.append("")
        
        # TRANSITIVE: Importados indirectamente (signal → signal)
        transitive = {}
        for mod, analysis in self.results.items():
            if not analysis.is_dead_code and mod not in root_nodes:
                transitive[mod] = analysis
        
        if transitive:
            lines.append("🔗 TRANSITIVE DEPENDENCIES (signal → signal chain)")
            lines.append("-" * 80)
            for mod, analysis in sorted(transitive.items()):
                signal_importers = [i for i in analysis.imported_by if i.startswith('signal_')]
                lines.append(f"  {mod}.py")
                lines.append(f"    → Used by signals: {', '.join(sorted(signal_importers))}")
            lines.append("")
        
        # DEAD CODE: No alcanzable desde roots
        dead = {k: v for k, v in self.results.items() if v.is_dead_code}
        if dead:
            lines.append("💀 DEAD CODE (not reachable from any main file)")
            lines.append("-" * 80)
            for mod in sorted(dead.keys()):
                lines.append(f"  {mod}.py")
            lines.append("")
        
        # Estadísticas
        lines.append("📊 STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total signal modules analyzed: {len(self.results)}")
        lines.append(f"Root nodes (directly used): {len(root_nodes)}")
        lines.append(f"Transitive dependencies: {len(transitive)}")
        lines.append(f"Dead code modules: {len(dead)}")
        lines.append(f"Dead code percentage: {100 * len(dead) / len(self.results):.1f}%")
        lines.append("")
        
        # Recomendaciones
        lines.append("✅ RECOMMENDATIONS")
        lines.append("-" * 80)
        lines.append("1. KEEP ALL: Root nodes + transitive dependencies")
        lines.append("2. REVIEW: Dead code modules - verify with git blame/history")
        lines.append("3. MOVE: Experimental/proposed code to /experiments or /proposals")
        lines.append("4. DELETE: Confirmed abandoned code after team review")
        lines.append("")
        
        # Dependency chains
        lines.append("📈 LONGEST DEPENDENCY CHAINS")
        lines.append("-" * 80)
        chains = self._find_longest_chains()
        for i, chain in enumerate(chains[:5], 1):
            lines.append(f"{i}. {' → '.join(chain)}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _find_longest_chains(self) -> List[List[str]]:
        """Encuentra las cadenas de dependencias más largas."""
        chains = []
        
        # Empezar desde cada root node
        for mod, analysis in self.results.items():
            has_non_signal_importer = any(
                not i.startswith('signal_') for i in analysis.imported_by
            )
            if has_non_signal_importer:
                chains.extend(self._dfs_chains(mod, []))
        
        # Ordenar por longitud descendente
        chains.sort(key=len, reverse=True)
        return chains
    
    def _dfs_chains(self, node: str, current_chain: List[str]) -> List[List[str]]:
        """DFS para encontrar todas las cadenas desde un nodo."""
        if node in current_chain:  # Evitar ciclos
            return [current_chain + [node]]
        
        new_chain = current_chain + [node]
        
        if node not in self.results:
            return [new_chain]
        
        deps = self.results[node].imports_from_signals
        if not deps:
            return [new_chain]
        
        all_chains = []
        for dep in deps:
            all_chains.extend(self._dfs_chains(dep, new_chain))
        
        return all_chains if all_chains else [new_chain]
    
    def get_dependency_graph(self) -> str:
        """Genera grafo de dependencias en formato texto."""
        
        lines = []
        lines.append("DEPENDENCY GRAPH")
        lines.append("-" * 80)
        
        for mod, analysis in sorted(self.results.items()):
            if not analysis.is_dead_code:
                lines.append(f"\n{mod}")
                if analysis.imports_from_signals:
                    for dep in sorted(analysis.imports_from_signals):
                        lines.append(f"  └── depends on: {dep}")
                if analysis.imported_by:
                    for user in sorted(analysis.imported_by):
                        lines.append(f"  ↑ used by: {user}")
        
        return "\n".join(lines)


def main():
    """Ejecuta análisis del ecosistema."""
    
    # AJUSTA ESTA RUTA a tu proyecto
    src_root = Path("src/farfan_pipeline")
    
    if not src_root.exists():
        print(f"❌ ERROR: {src_root} no existe")
        print("Ajusta la ruta 'src_root' en main()")
        return
    
    validator = SignalEcosystemValidator(src_root)
    
    print("Escaneando ecosystem...")
    validator.scan_ecosystem()
    
    print(validator.generate_report())
    print(validator.get_dependency_graph())
    
    # Exportar resultados
    report_file = Path("signal_ecosystem_analysis.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(validator.generate_report())
        f.write("\n\n")
        f.write(validator.get_dependency_graph())
    
    print(f"\n✅ Reporte guardado en: {report_file}")


if __name__ == "__main__":
    main()
