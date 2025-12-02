#!/usr/bin/env python3
"""Comprehensive import dependency analyzer."""
import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ImportInfo:
    module: str
    names: List[str]
    lineno: int
    is_relative: bool
    level: int


@dataclass
class CircularChain:
    modules: List[str]
    severity: str
    reason: str


@dataclass
class LayerViolation:
    source_module: str
    source_layer: str
    target_module: str
    target_layer: str
    line_number: int


class ComprehensiveImportAnalyzer:
    FORBIDDEN = [
        ('core.calibration', 'analysis'),
        ('core.wiring', 'analysis'),
        ('core.orchestrator', 'analysis'),
        ('processing', 'core.orchestrator'),
        ('api', 'processing'),
        ('api', 'analysis'),
        ('utils', 'core.orchestrator'),
    ]

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.modules = {}
        self.import_graph = defaultdict(set)
        self.cycles = []
        self.violations = []
        self.stats = {'total_modules': 0, 'total_imports': 0, 'relative_imports': 0}

    def analyze(self):
        py_files = [f for f in self.root_path.rglob('*.py') if '__pycache__' not in str(f)]
        print(f"Analyzing {len(py_files)} Python files...")
        
        for py_file in py_files:
            module_name = self._path_to_module(py_file)
            imports = self._extract_imports(py_file)
            self.modules[module_name] = {'imports': imports, 'layer': self._get_layer(module_name)}
            self.stats['total_modules'] += 1
            
            for imp in imports:
                self.stats['total_imports'] += 1
                if imp.is_relative:
                    self.stats['relative_imports'] += 1
                    resolved = self._resolve_relative(module_name, imp.level, imp.module)
                else:
                    resolved = imp.module
                if 'farfan_pipeline' in resolved:
                    self.import_graph[module_name].add(resolved)
        
        self.cycles = self._find_cycles()
        self.violations = self._find_violations()
        return self

    def _path_to_module(self, path: Path) -> str:
        try:
            rel = path.relative_to(self.root_path)
            parts = list(rel.parts)
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            if parts[-1] == '__init__':
                parts = parts[:-1]
            return '.'.join(parts)
        except:
            return str(path)

    def _get_layer(self, module: str) -> str:
        parts = module.split('.')
        if 'farfan_pipeline' in parts:
            parts = parts[parts.index('farfan_pipeline')+1:]
        if not parts:
            return 'root'
        if parts[0] == 'core' and len(parts) > 1:
            return f'core.{parts[1]}'
        return parts[0]

    def _resolve_relative(self, current: str, level: int, module: Optional[str]) -> str:
        parts = current.split('.')
        if level > len(parts):
            return f"<invalid-{level}>"
        parent = parts[:-level] if level > 0 else parts
        if module:
            return '.'.join(parent + module.split('.'))
        return '.'.join(parent)

    def _extract_imports(self, path: Path) -> List[ImportInfo]:
        imports = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportInfo(alias.name, [alias.name], node.lineno, False, 0))
                elif isinstance(node, ast.ImportFrom):
                    level = getattr(node, 'level', 0)
                    imports.append(ImportInfo(node.module or '', [a.name for a in node.names], node.lineno, level > 0, level))
        except:
            pass
        return imports

    def _find_cycles(self) -> List[CircularChain]:
        visited, stack, cycles = set(), set(), []
        
        def dfs(node, path):
            visited.add(node)
            stack.add(node)
            path.append(node)
            for neighbor in self.import_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in stack:
                    idx = path.index(neighbor)
                    cycle = path[idx:] + [neighbor]
                    norm = min([cycle[i:] + cycle[:i] for i in range(len(cycle)-1)], key=tuple)
                    if norm not in [c.modules for c in cycles]:
                        sev, reason = self._assess_severity(norm)
                        cycles.append(CircularChain(norm, sev, reason))
            path.pop()
            stack.remove(node)
        
        for node in self.import_graph:
            if node not in visited:
                dfs(node, [])
        return cycles

    def _assess_severity(self, cycle: List[str]) -> Tuple[str, str]:
        n = len(cycle) - 1
        if n > 4:
            return 'CRITICAL', f'{n}-module chain - high risk'
        if n == 2:
            return 'WARNING', 'Two-way circular import'
        return 'BENIGN', 'Circular but likely safe'

    def _find_violations(self) -> List[LayerViolation]:
        violations = []
        for mod, data in self.modules.items():
            src_layer = data['layer']
            for imp in data['imports']:
                tgt = self._resolve_relative(mod, imp.level, imp.module) if imp.is_relative else imp.module
                if 'farfan_pipeline' not in tgt:
                    continue
                tgt_layer = self._get_layer(tgt)
                for fsrc, ftgt in self.FORBIDDEN:
                    if fsrc in src_layer and ftgt in tgt_layer:
                        violations.append(LayerViolation(mod, src_layer, tgt, tgt_layer, imp.lineno))
        return violations

    def generate_report(self, output: Path):
        with open(output, 'w') as f:
            f.write("# IMPORT HEALTH REPORT\n\n")
            f.write(f"**Analysis Date**: {self._get_timestamp()}\n")
            f.write(f"**Root Path**: `{self.root_path}`\n\n")
            
            f.write("## Executive Summary\n\n")
            status = self._get_health_status()
            f.write(f"**Health Status**: {status['icon']} {status['label']}\n\n")
            f.write(f"- **Total Modules Analyzed**: {self.stats['total_modules']}\n")
            f.write(f"- **Total Import Statements**: {self.stats['total_imports']}\n")
            f.write(f"- **Relative Imports**: {self.stats['relative_imports']} ({self._pct(self.stats['relative_imports'], self.stats['total_imports'])}%)\n")
            f.write(f"- **Absolute Imports**: {self.stats['total_imports'] - self.stats['relative_imports']} ({self._pct(self.stats['total_imports'] - self.stats['relative_imports'], self.stats['total_imports'])}%)\n")
            f.write(f"- **Circular Import Chains Found**: {len(self.cycles)}\n")
            f.write(f"- **Layer Violations Detected**: {len(self.violations)}\n\n")
            
            f.write("## Import Pattern Statistics\n\n")
            self._write_pattern_stats(f)
            
            f.write("\n## Dependency Graph Overview\n\n")
            self._write_graph_stats(f)
            
            if self.cycles:
                f.write(f"\n## 🔄 Circular Import Chains ({len(self.cycles)})\n\n")
                critical = [c for c in self.cycles if c.severity == 'CRITICAL']
                warning = [c for c in self.cycles if c.severity == 'WARNING']
                benign = [c for c in self.cycles if c.severity == 'BENIGN']
                
                if critical:
                    f.write(f"### 🔴 CRITICAL Issues ({len(critical)})\n\n")
                    for i, c in enumerate(critical, 1):
                        f.write(f"#### {i}. {c.reason}\n\n")
                        f.write(f"**Chain**: `{' → '.join(c.modules)}`\n\n")
                        f.write("**Resolution**: Refactor to break circular dependency. Consider:\n")
                        f.write("- Moving shared code to a common module\n")
                        f.write("- Using dependency injection\n")
                        f.write("- Lazy imports within functions\n\n")
                
                if warning:
                    f.write(f"### ⚠️  WARNING Issues ({len(warning)})\n\n")
                    for i, c in enumerate(warning, 1):
                        f.write(f"#### {i}. {c.reason}\n\n")
                        f.write(f"**Chain**: `{' → '.join(c.modules)}`\n\n")
                
                if benign:
                    f.write(f"### ℹ️  BENIGN Patterns ({len(benign)})\n\n")
                    for i, c in enumerate(benign, 1):
                        f.write(f"- {' → '.join(c.modules)}\n")
                    f.write("\n")
            else:
                f.write("\n## ✅ Circular Import Analysis\n\n")
                f.write("**No circular import chains detected!** The codebase has a clean dependency structure.\n\n")
            
            if self.violations:
                f.write(f"\n## 🚫 Layer Violations ({len(self.violations)})\n\n")
                f.write("The following imports violate the layered architecture contracts defined in `pyproject.toml`:\n\n")
                f.write("| # | Source Module | Source Layer | → | Target Module | Target Layer | Line |\n")
                f.write("|---|---------------|--------------|---|---------------|--------------|------|\n")
                for i, v in enumerate(self.violations, 1):
                    src_short = self._shorten(v.source_module, 40)
                    tgt_short = self._shorten(v.target_module, 40)
                    f.write(f"| {i} | `{src_short}` | `{v.source_layer}` | → | `{tgt_short}` | `{v.target_layer}` | {v.line_number} |\n")
                
                f.write("\n### Resolution Recommendations\n\n")
                self._write_violation_recommendations(f)
            else:
                f.write("\n## ✅ Layer Architecture Compliance\n\n")
                f.write("**All imports comply with layer architecture!** No violations detected.\n\n")
            
            f.write("\n## Relative Import Analysis\n\n")
            self._write_relative_import_analysis(f)
            
            f.write("\n## Layer Dependency Matrix\n\n")
            self._write_layer_matrix(f)
            
            f.write("\n## Recommendations\n\n")
            self._write_recommendations(f)
            
        print(f"Report written to {output}")

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _pct(self, num, total):
        return round(100 * num / total, 1) if total > 0 else 0

    def _shorten(self, text, maxlen):
        return text if len(text) <= maxlen else f"...{text[-(maxlen-3):]}"

    def _get_health_status(self):
        critical = [c for c in self.cycles if c.severity == 'CRITICAL']
        if critical or len(self.violations) > 5:
            return {'icon': '🔴', 'label': 'CRITICAL - Immediate action required'}
        if len(self.cycles) > 0 or len(self.violations) > 0:
            return {'icon': '⚠️ ', 'label': 'WARNING - Issues detected'}
        return {'icon': '✅', 'label': 'HEALTHY - No issues found'}

    def _write_pattern_stats(self, f):
        layers = defaultdict(int)
        for mod, data in self.modules.items():
            layers[data['layer']] += 1
        
        f.write("### Modules by Layer\n\n")
        for layer in sorted(layers.keys()):
            f.write(f"- **{layer}**: {layers[layer]} modules\n")

    def _write_graph_stats(self, f):
        total_edges = sum(len(deps) for deps in self.import_graph.values())
        modules_with_deps = len([m for m in self.import_graph if self.import_graph[m]])
        
        f.write(f"- **Total dependency edges**: {total_edges}\n")
        f.write(f"- **Modules with dependencies**: {modules_with_deps}\n")
        f.write(f"- **Average dependencies per module**: {total_edges / modules_with_deps if modules_with_deps else 0:.1f}\n")

    def _write_relative_import_analysis(self, f):
        invalid = []
        for mod, data in self.modules.items():
            for imp in data['imports']:
                if imp.is_relative:
                    resolved = self._resolve_relative(mod, imp.level, imp.module)
                    if '<invalid' in resolved:
                        invalid.append((mod, imp, resolved))
        
        f.write(f"Total relative imports: {self.stats['relative_imports']}\n\n")
        if invalid:
            f.write(f"### ⚠️  Invalid Relative Imports ({len(invalid)})\n\n")
            for mod, imp, resolved in invalid:
                f.write(f"- `{mod}` line {imp.lineno}: level {imp.level} - {resolved}\n")
        else:
            f.write("✅ All relative imports are properly scoped.\n")

    def _write_layer_matrix(self, f):
        layer_deps = defaultdict(lambda: defaultdict(int))
        for mod, data in self.modules.items():
            src_layer = data['layer']
            for imp in data['imports']:
                tgt = self._resolve_relative(mod, imp.level, imp.module) if imp.is_relative else imp.module
                if 'farfan_pipeline' in tgt:
                    tgt_layer = self._get_layer(tgt)
                    if src_layer != tgt_layer:
                        layer_deps[src_layer][tgt_layer] += 1
        
        layers = sorted(set(list(layer_deps.keys()) + [t for targets in layer_deps.values() for t in targets.keys()]))
        
        f.write("Cross-layer dependencies count:\n\n")
        f.write("| From \\ To | " + " | ".join(layers) + " |\n")
        f.write("|" + "---|" * (len(layers) + 1) + "\n")
        
        for src in layers:
            row = [src]
            for tgt in layers:
                count = layer_deps.get(src, {}).get(tgt, 0)
                row.append(str(count) if count > 0 else "·")
            f.write("| " + " | ".join(row) + " |\n")

    def _write_violation_recommendations(self, f):
        by_type = defaultdict(list)
        for v in self.violations:
            key = f"{v.source_layer} → {v.target_layer}"
            by_type[key].append(v)
        
        for vtype, vlist in sorted(by_type.items()):
            f.write(f"#### {vtype} ({len(vlist)} violations)\n\n")
            f.write(self._get_resolution_advice(vtype))
            f.write("\n")

    def _get_resolution_advice(self, violation_type):
        advice = {
            "api → processing": "API layer should only call orchestrator. Move logic to orchestrator entry points.",
            "api → analysis": "API layer should only call orchestrator. Move logic to orchestrator entry points.",
            "utils → core.orchestrator": "Utils must remain leaf modules. Extract shared code or use dependency injection.",
            "processing → core.orchestrator": "Processing modules should not import orchestrator. Use ports/interfaces instead.",
            "core.orchestrator → analysis": "Orchestrator should not directly import analysis. Use dynamic loading or registry pattern.",
        }
        return advice.get(violation_type, "Review layer architecture and refactor to comply with contracts.\n")

    def _write_recommendations(self, f):
        f.write("### General Recommendations\n\n")
        f.write("1. **Maintain layer boundaries**: Respect the architecture contracts in `pyproject.toml`\n")
        f.write("2. **Avoid circular imports**: Use dependency injection, lazy imports, or refactor shared code\n")
        f.write("3. **Minimize cross-layer dependencies**: Keep coupling low between architectural layers\n")
        f.write("4. **Use relative imports carefully**: Ensure they stay within package boundaries\n")
        f.write("5. **Regular analysis**: Run this tool regularly to catch issues early\n\n")
        
        if self.violations:
            f.write("### Priority Actions\n\n")
            f.write(f"1. Fix {len(self.violations)} layer violation(s)\n")
        if [c for c in self.cycles if c.severity == 'CRITICAL']:
            f.write(f"2. Resolve CRITICAL circular imports immediately\n")
        if [c for c in self.cycles if c.severity == 'WARNING']:
            f.write(f"3. Review and fix WARNING-level circular imports\n")


def main():
    root = Path(__file__).parent.parent.parent / 'src' / 'farfan_pipeline'
    if not root.exists():
        print(f"Error: {root} not found")
        return 1
    
    analyzer = ComprehensiveImportAnalyzer(root)
    analyzer.analyze()
    
    report_path = Path(__file__).parent.parent.parent / 'IMPORT_HEALTH_REPORT.md'
    analyzer.generate_report(report_path)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Modules: {analyzer.stats['total_modules']}")
    print(f"Circular chains: {len(analyzer.cycles)}")
    print(f"Layer violations: {len(analyzer.violations)}")
    
    return 0 if not [c for c in analyzer.cycles if c.severity == 'CRITICAL'] else 1


if __name__ == '__main__':
    sys.exit(main())
