#!/usr/bin/env python3
"""
BASELINE VERIFICATION SCRIPT
============================
Script de verificación de línea base para SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.

Este script captura y verifica métricas críticas del repositorio.
Ejecutar ANTES y DESPUÉS de cada fase de normalización.

Principios operativos:
- Cada métrica es verificable empíricamente
- Permite comparación temporal (baseline vs current)
- Detecta regresiones de calidad

Author: F.A.R.F.A.N Pipeline
Date: 2026-01-04
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Rutas relativas al proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
CANONIC_QC = PROJECT_ROOT / "canonic_questionnaire_central"
SRC_DIR = PROJECT_ROOT / "src"


@dataclass
class BaselineMetrics:
    """Métricas de línea base del repositorio."""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Imports fantasma
    phantom_imports_count: int = 0
    phantom_imports_files: list[str] = field(default_factory=list)
    
    # Schema/Monolith
    provenance_in_monolith: int = 0
    provenance_in_schema: int = 0
    monolith_hash: str = ""
    schema_hash: str = ""
    
    # Ports
    ports_hash: str = ""
    port_method_signatures: dict[str, list[str]] = field(default_factory=dict)
    
    # Signal Registry
    registry_method_signatures: dict[str, list[str]] = field(default_factory=dict)
    
    # Signature mismatches
    signature_mismatches: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return {
            "timestamp": self.timestamp,
            "phantom_imports": {
                "count": self.phantom_imports_count,
                "files": self.phantom_imports_files[:20],  # Limitar para legibilidad
            },
            "schema_monolith": {
                "provenance_in_monolith": self.provenance_in_monolith,
                "provenance_in_schema": self.provenance_in_schema,
                "monolith_hash": self.monolith_hash,
                "schema_hash": self.schema_hash,
            },
            "ports": {
                "hash": self.ports_hash,
                "method_signatures": self.port_method_signatures,
            },
            "registry": {
                "method_signatures": self.registry_method_signatures,
            },
            "signature_mismatches": self.signature_mismatches,
        }
    
    def save(self, filepath: Path) -> None:
        """Guarda métricas a archivo JSON."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✓ Baseline guardado en: {filepath}")


def compute_file_hash(filepath: Path) -> str:
    """Calcula SHA-256 de un archivo."""
    if not filepath.exists():
        return "FILE_NOT_FOUND"
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def count_pattern_in_file(filepath: Path, pattern: str) -> int:
    """Cuenta ocurrencias de patrón en archivo."""
    if not filepath.exists():
        return 0
    content = filepath.read_text(encoding="utf-8")
    return len(re.findall(pattern, content))


def find_phantom_imports(src_dir: Path) -> tuple[int, list[str]]:
    """Encuentra imports a namespaces fantasma."""
    phantom_pattern = re.compile(r"(cross_cutting_infrastructure|canonic_phases)")
    files_with_phantoms: list[str] = []
    total_count = 0
    
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            matches = phantom_pattern.findall(content)
            if matches:
                rel_path = str(py_file.relative_to(src_dir.parent))
                files_with_phantoms.append(rel_path)
                total_count += len(matches)
        except Exception:
            continue
    
    return total_count, files_with_phantoms


def extract_method_signatures_from_protocol(filepath: Path) -> dict[str, list[str]]:
    """Extrae firmas de métodos de un Protocol."""
    if not filepath.exists():
        return {}
    
    content = filepath.read_text(encoding="utf-8")
    
    # Buscar métodos def dentro de SignalRegistryPort
    signatures: dict[str, list[str]] = {}
    
    # Patrón para capturar def method_name(self, param: type, ...) -> return_type:
    method_pattern = re.compile(
        r"def\s+(\w+)\s*\(\s*self\s*(?:,\s*([^)]*))?\)\s*(?:->\s*([^:]+))?\s*:"
    )
    
    for match in method_pattern.finditer(content):
        method_name = match.group(1)
        params_str = match.group(2) or ""
        return_type = match.group(3) or "None"
        
        # Parsear parámetros
        params = []
        if params_str.strip():
            for param in params_str.split(","):
                param = param.strip()
                if param:
                    params.append(param)
        
        signatures[method_name] = params
    
    return signatures


def compare_signatures(
    port_sigs: dict[str, list[str]], 
    impl_sigs: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """Compara firmas entre Port e Implementation."""
    mismatches: list[dict[str, Any]] = []
    
    # Métodos críticos a verificar
    critical_methods = [
        "get_validation_signals",
        "get_scoring_signals",
        "get_micro_answering_signals",
        "get_assembly_signals",
        "get_chunking_signals",
    ]
    
    for method in critical_methods:
        port_params = port_sigs.get(method, ["NOT_FOUND"])
        impl_params = impl_sigs.get(method, ["NOT_FOUND"])
        
        if port_params != impl_params:
            mismatches.append({
                "method": method,
                "port_params": port_params,
                "impl_params": impl_params,
                "status": "MISMATCH",
            })
    
    return mismatches


def collect_baseline() -> BaselineMetrics:
    """Recolecta todas las métricas baseline."""
    metrics = BaselineMetrics()
    
    print("=" * 60)
    print("BASELINE VERIFICATION - Recolectando métricas...")
    print("=" * 60)
    
    # 1. Phantom imports
    print("\n[1/6] Buscando imports fantasma...")
    count, files = find_phantom_imports(SRC_DIR)
    metrics.phantom_imports_count = count
    metrics.phantom_imports_files = files
    print(f"      → {count} imports fantasma en {len(files)} archivos")
    
    # 2. Provenance counts
    print("\n[2/6] Contando provenance...")
    monolith_path = CANONIC_QC / "questionnaire_monolith.json"
    schema_path = CANONIC_QC / "questionnaire_schema.json"
    
    metrics.provenance_in_monolith = count_pattern_in_file(monolith_path, r'"provenance"')
    metrics.provenance_in_schema = count_pattern_in_file(schema_path, r'"provenance"')
    print(f"      → Monolith: {metrics.provenance_in_monolith}, Schema: {metrics.provenance_in_schema}")
    
    # 3. File hashes
    print("\n[3/6] Calculando hashes...")
    metrics.monolith_hash = compute_file_hash(monolith_path)
    metrics.schema_hash = compute_file_hash(schema_path)
    print(f"      → Monolith: {metrics.monolith_hash[:16]}...")
    print(f"      → Schema: {metrics.schema_hash[:16]}...")
    
    # 4. Ports hash and signatures
    print("\n[4/6] Analizando ports.py...")
    ports_path = SRC_DIR / "farfan_pipeline/infrastructure/irrigation_using_signals/ports.py"
    metrics.ports_hash = compute_file_hash(ports_path)
    metrics.port_method_signatures = extract_method_signatures_from_protocol(ports_path)
    print(f"      → Hash: {metrics.ports_hash[:16]}...")
    print(f"      → Métodos: {list(metrics.port_method_signatures.keys())}")
    
    # 5. Registry signatures
    print("\n[5/6] Analizando signal_registry.py...")
    registry_path = SRC_DIR / "farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signal_registry.py"
    metrics.registry_method_signatures = extract_method_signatures_from_protocol(registry_path)
    print(f"      → Métodos: {list(metrics.registry_method_signatures.keys())[:5]}...")
    
    # 6. Compare signatures
    print("\n[6/6] Comparando firmas Port vs Implementation...")
    metrics.signature_mismatches = compare_signatures(
        metrics.port_method_signatures,
        metrics.registry_method_signatures
    )
    if metrics.signature_mismatches:
        print(f"      → ⚠️  {len(metrics.signature_mismatches)} discrepancias detectadas:")
        for mm in metrics.signature_mismatches:
            print(f"         - {mm['method']}: port={mm['port_params']} vs impl={mm['impl_params']}")
    else:
        print("      → ✓ Todas las firmas coinciden")
    
    print("\n" + "=" * 60)
    print("BASELINE COMPLETADO")
    print("=" * 60)
    
    return metrics


def print_summary(metrics: BaselineMetrics) -> None:
    """Imprime resumen de métricas."""
    print("\n" + "═" * 60)
    print("                    RESUMEN BASELINE")
    print("═" * 60)
    print(f"  Timestamp:             {metrics.timestamp}")
    print(f"  Phantom imports:       {metrics.phantom_imports_count}")
    print(f"  Provenance (monolith): {metrics.provenance_in_monolith}")
    print(f"  Provenance (schema):   {metrics.provenance_in_schema}")
    print(f"  Signature mismatches:  {len(metrics.signature_mismatches)}")
    print("═" * 60)
    
    # Indicadores de salud
    print("\n  INDICADORES DE SALUD:")
    
    health_score = 100
    
    if metrics.phantom_imports_count > 0:
        print(f"  🔴 CRÍTICO: {metrics.phantom_imports_count} imports fantasma")
        health_score -= 30
    else:
        print("  🟢 OK: Sin imports fantasma")
    
    if metrics.provenance_in_schema == 0 and metrics.provenance_in_monolith > 0:
        print(f"  🔴 CRÍTICO: provenance en monolith ({metrics.provenance_in_monolith}) pero no en schema")
        health_score -= 20
    else:
        print("  🟢 OK: Schema incluye provenance")
    
    if metrics.signature_mismatches:
        print(f"  🔴 CRÍTICO: {len(metrics.signature_mismatches)} firmas no coinciden")
        health_score -= 25
    else:
        print("  🟢 OK: Firmas Port/Impl coinciden")
    
    print(f"\n  PUNTUACIÓN DE SALUD: {max(0, health_score)}/100")
    print("═" * 60)


def main() -> int:
    """Punto de entrada principal."""
    metrics = collect_baseline()
    print_summary(metrics)
    
    # Guardar baseline
    output_dir = PROJECT_ROOT / "artifacts" / "reports" / "audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"baseline_{timestamp}.json"
    metrics.save(output_file)
    
    # Exit code basado en estado crítico
    if metrics.phantom_imports_count > 0 or metrics.signature_mismatches:
        return 1  # Indica que hay trabajo pendiente
    return 0


if __name__ == "__main__":
    sys.exit(main())
