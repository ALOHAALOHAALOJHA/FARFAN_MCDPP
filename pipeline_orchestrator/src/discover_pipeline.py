#!/usr/bin/env python3
"""
Pipeline Discovery Script - Step 1.1
Descubre todos los ejecutables reales del pipeline FARFAN
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import json
import re


class PipelineDiscoverer:
    """Descubre todos los ejecutables y dependencias del pipeline."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.phases_dir = project_root / "src" / "farfan_pipeline" / "phases"
        self.scripts_dir = project_root / "scripts"

        # Resultados del descubrimiento
        self.raw_files: List[Path] = []
        self.executables: Dict[str, List[Dict]] = {}
        self.io_patterns: Dict[str, List[Dict]] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def discover_all_files(self) -> None:
        """Paso 1.1: Descubrir todos los archivos ejecutables."""
        print("🔍 Descubriendo archivos ejecutables...")

        extensions = {".py", ".sh", ".yaml", ".yml", ".sql", ".ipynb"}
        exclude_dirs = {
            "__pycache__",
            ".git",
            "farfan-env",
            ".pytest_cache",
            "node_modules",
            "_build",
            "venv",
            "env"
        }

        for root, dirs, files in os.walk(self.project_root):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                ext = Path(file).suffix
                if ext in extensions:
                    full_path = Path(root) / file
                    # Solo incluir archivos relevantes del proyecto
                    if self._is_project_file(full_path):
                        self.raw_files.append(full_path)

        print(f"   ✅ Encontrados {len(self.raw_files)} archivos ejecutables")

    def _is_project_file(self, path: Path) -> bool:
        """Verifica si el archivo es parte del proyecto principal."""
        path_str = str(path)
        # Excluir bibliotecas de terceros en subdirectorios
        if "site-packages" in path_str:
            return False
        if "farfan-env" in path_str:
            return False
        return True

    def analyze_phase_structure(self) -> None:
        """Analiza la estructura de fases del pipeline."""
        print("\n🏗️  Analizando estructura de fases...")

        if not self.phases_dir.exists():
            print(f"   ⚠️  Directorio de fases no encontrado: {self.phases_dir}")
            return

        for phase_path in sorted(self.phases_dir.iterdir()):
            if phase_path.is_dir() and phase_path.name.startswith("Phase_"):
                # Extraer número de fase, ignorando symlink "Phase_zero"
                parts = phase_path.name.split("_")
                if len(parts) >= 2 and parts[1].isdigit():
                    phase_num = parts[1]
                    self.executables[phase_num] = []

                # Buscar archivos Python en la fase
                py_files = list(phase_path.rglob("*.py"))
                for py_file in py_files:
                    if "__pycache__" not in str(py_file):
                        info = self._analyze_python_file(py_file, phase_num)
                        if info:
                            self.executables[phase_num].append(info)

        print(f"   ✅ Analizadas {len(self.executables)} fases")

    def _analyze_python_file(self, path: Path, phase_num: str) -> Dict | None:
        """Analiza un archivo Python para extraer metadatos."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(path))

            info = {
                "path": str(path.relative_to(self.project_root)),
                "module": self._get_module_name(path),
                "classes": [],
                "functions": [],
                "imports": [],
                "docstring": ast.get_docstring(tree) or ""
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    info["functions"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info["imports"].append(node.module)

            return info

        except (SyntaxError, UnicodeDecodeError):
            return None

    def _get_module_name(self, path: Path) -> str:
        """Obtiene el nombre del módulo Python."""
        parts = path.relative_to(self.project_root / "src").parts
        if parts[0] == "farfan_pipeline":
            return ".".join(parts[1:]).replace(".py", "")
        return str(path)

    def discover_io_patterns(self) -> None:
        """Paso 1.2: Identificar patrones de entrada/salida."""
        print("\n🔌 Identificando patrones de E/S...")

        patterns = {
            "s3": r's3://[^\s"\'\)]+',
            "gcs": r'gs://[^\s"\'\)]+',
            "http": r'https?://[^\s"\'\)]+',
            "file_read": r'open\([\'"]([^\'"]+)[\'"]\s*,\s*["\']r["\']',
            "file_write": r'open\([\'"]([^\'"]+)[\'"]\s*,\s*["\']w["\']',
            "path_pattern": r'Path\([\'"]?([^\'")\s]+)[\'"]?\)',
        }

        for file_path in self.raw_files:
            if file_path.suffix == ".py":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            rel_path = str(file_path.relative_to(self.project_root))
                            if pattern_name not in self.io_patterns:
                                self.io_patterns[pattern_name] = []
                            self.io_patterns[pattern_name].extend([
                                {"file": rel_path, "match": m}
                                for m in matches
                            ])

                except (UnicodeDecodeError, PermissionError):
                    pass

        for pattern_name, matches in self.io_patterns.items():
            print(f"   📄 {pattern_name}: {len(matches)} ocurrencias")

    def discover_dependencies(self) -> None:
        """Paso 1.3: Extraer dependencias entre fases."""
        print("\n🔗 Descubriendo dependencias entre fases...")

        # Buscar imports entre fases
        phase_import_pattern = re.compile(
            r'from\s+farfan_pipeline\.phases\.Phase_(\d+)'
        )

        for phase_num, files in self.executables.items():
            self.dependencies[f"Phase_{phase_num}"] = set()

            for file_info in files:
                for imp in file_info.get("imports", []):
                    match = phase_import_pattern.search(imp)
                    if match:
                        dep_phase = match.group(1)
                        self.dependencies[f"Phase_{phase_num}"].add(f"Phase_{dep_phase}")

        # Imprimir dependencias descubiertas
        for phase, deps in sorted(self.dependencies.items()):
            if deps:
                print(f"   🔗 {phase} -> {', '.join(sorted(deps))}")

    def generate_inventory(self) -> Dict:
        """Genera el inventario completo del pipeline."""
        print("\n📋 Generando inventario del pipeline...")

        inventory = {
            "metadata": {
                "project": "FARFAN_MCDPP",
                "description": "Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives",
                "phases_count": len(self.executables),
                "total_files": len(self.raw_files)
            },
            "phases": {}
        }

        for phase_num in sorted(self.executables.keys(), key=int):
            phase_key = f"Phase_{phase_num}"
            files = self.executables[phase_num]

            inventory["phases"][phase_key] = {
                "name": self._get_phase_name(phase_num),
                "executable_count": len(files),
                "executables": files,
                "dependencies": list(self.dependencies.get(phase_key, [])),
                "inputs": self._get_phase_inputs(phase_num),
                "outputs": self._get_phase_outputs(phase_num)
            }

        return inventory

    def _get_phase_name(self, phase_num: str) -> str:
        """Obtiene el nombre descriptivo de la fase."""
        phase_names = {
            "0": "Bootstrap & Validation Gate",
            "1": "Document Ingestion & Structural Parsing (CPP)",
            "2": "Method Execution (30 D×Q Executors)",
            "3": "Quality Scoring & Layer Evaluation",
            "4": "Dimension Aggregation",
            "5": "Policy Area Aggregation",
            "6": "Cluster Aggregation",
            "7": "Macro Evaluation",
            "8": "Recommendation Generation",
            "9": "Report Assembly & Artifact Finalization"
        }
        return phase_names.get(phase_num, f"Phase {phase_num}")

    def _get_phase_inputs(self, phase_num: str) -> List[Dict]:
        """Obtiene las entradas de una fase."""
        # Esto se completará con análisis más profundo
        return []

    def _get_phase_outputs(self, phase_num: str) -> List[Dict]:
        """Obtiene las salidas de una fase."""
        # Esto se completará con análisis más profundo
        return []

    def save_results(self, output_dir: Path) -> None:
        """Guarda los resultados del descubrimiento."""
        print(f"\n💾 Guardando resultados en {output_dir}...")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Guardar lista cruda de archivos
        raw_files_list = output_dir / "raw_files.txt"
        with open(raw_files_list, "w") as f:
            for file_path in sorted(self.raw_files):
                f.write(f"{file_path.relative_to(self.project_root)}\n")
        print(f"   ✅ raw_files.txt: {len(self.raw_files)} archivos")

        # Guardar inventario YAML
        inventory = self.generate_inventory()
        inventory_file = output_dir / "pipeline_inventory.yaml"
        with open(inventory_file, "w", encoding="utf-8") as f:
            # Convertir sets a lists para JSON serializable
            import yaml
            yaml.dump(inventory, f, default_flow_style=False, sort_keys=False)
        print(f"   ✅ pipeline_inventory.yaml generado")

        # Guardar patrones de E/S
        io_file = output_dir / "io_patterns.json"
        with open(io_file, "w", encoding="utf-8") as f:
            # Convertir sets a lists
            io_serializable = {
                k: [{"file": m["file"], "match": m["match"]} for m in v]
                for k, v in self.io_patterns.items()
            }
            json.dump(io_serializable, f, indent=2)
        print(f"   ✅ io_patterns.json generado")


def main():
    """Función principal."""
    project_root = Path("/Users/recovered/Downloads/FARFAN_MCDPP")
    output_dir = project_root / "pipeline_orchestrator" / "inventory"

    print("=" * 60)
    print("FARFAN Pipeline Discovery - Step 1: Inventory")
    print("=" * 60)

    discoverer = PipelineDiscoverer(project_root)

    # Paso 1: Descubrir todos los archivos
    discoverer.discover_all_files()

    # Paso 2: Analizar estructura de fases
    discoverer.analyze_phase_structure()

    # Paso 3: Descubrir patrones de E/S
    discoverer.discover_io_patterns()

    # Paso 4: Descubrir dependencias
    discoverer.discover_dependencies()

    # Paso 5: Guardar resultados
    discoverer.save_results(output_dir)

    print("\n" + "=" * 60)
    print("✅ Descubrimiento completado")
    print("=" * 60)


if __name__ == "__main__":
    main()
