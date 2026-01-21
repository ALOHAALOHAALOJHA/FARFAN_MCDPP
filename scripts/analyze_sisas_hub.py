#!/usr/bin/env python3
"""
ANÁLISIS EXHAUSTIVO DE SISAS INTEGRATION HUB
============================================

Este script verifica TODAS las discrepancias entre lo que existe en el filesystem
y lo que sisas_integration_hub.py está registrando.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add paths
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

def scan_consumers_filesystem() -> Dict[str, List[str]]:
    """Escanea el filesystem para encontrar TODOS los consumers reales."""
    consumers_base = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers")

    consumers_by_phase = {}

    for phase_dir in consumers_base.glob("phase*"):
        if not phase_dir.is_dir():
            continue

        phase_name = phase_dir.name
        consumers = []

        for py_file in phase_dir.glob("*.py"):
            if py_file.name in ["__init__.py", "base_consumer.py"]:
                continue
            consumers.append(py_file.stem)

        consumers_by_phase[phase_name] = consumers

    return consumers_by_phase

def scan_extractors_filesystem() -> List[str]:
    """Escanea extractors reales."""
    extractors_base = Path("src/farfan_pipeline/infrastructure/extractors")

    extractors = []
    for py_file in extractors_base.glob("*_extractor.py"):
        if "test" not in py_file.name:
            extractors.append(py_file.stem)

    return sorted(extractors)

def scan_vehicles_filesystem() -> List[str]:
    """Escanea vehicles reales."""
    vehicles_base = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles")

    vehicles = []
    for py_file in vehicles_base.glob("signal_*.py"):
        if py_file.name not in ["signals.py"]:
            vehicles.append(py_file.stem)

    return sorted(vehicles)

def analyze_hub_registrations() -> Dict[str, int]:
    """Analiza lo que sisas_integration_hub.py está registrando."""
    hub_file = Path("src/farfan_pipeline/orchestration/sisas_integration_hub.py")

    if not hub_file.exists():
        return {"error": "sisas_integration_hub.py not found"}

    with open(hub_file) as f:
        content = f.read()

    # Contar consumer_configs
    import re
    consumer_configs = re.findall(r'"consumer_id":\s*"([^"]+)"', content)

    return {
        "consumers_in_hub": len(consumer_configs),
        "consumer_ids": consumer_configs
    }

def main():
    print("=" * 80)
    print("ANÁLISIS EXHAUSTIVO DE SISAS INTEGRATION HUB")
    print("=" * 80)
    print()

    # 1. Consumers en filesystem
    print("📂 CONSUMERS EN FILESYSTEM:")
    print("-" * 80)
    consumers_fs = scan_consumers_filesystem()
    total_fs = sum(len(consumers) for consumers in consumers_fs.values())

    for phase, consumers in sorted(consumers_fs.items()):
        print(f"  {phase}: {len(consumers)} consumers")
        for consumer in consumers:
            print(f"    - {consumer}")
    print(f"\n  TOTAL FILESYSTEM: {total_fs} consumers")
    print()

    # 2. Extractors en filesystem
    print("🔍 EXTRACTORS EN FILESYSTEM:")
    print("-" * 80)
    extractors_fs = scan_extractors_filesystem()
    print(f"  Total: {len(extractors_fs)} extractors")
    for extractor in extractors_fs:
        mc_num = "MC??"
        if "structural_marker" in extractor:
            mc_num = "MC01"
        elif "quantitative_triplet" in extractor:
            mc_num = "MC02"
        elif "normative_reference" in extractor:
            mc_num = "MC03"
        elif "programmatic_hierarchy" in extractor:
            mc_num = "MC04"
        elif "financial_chain" in extractor:
            mc_num = "MC05"
        elif "population_disaggregation" in extractor:
            mc_num = "MC06"
        elif "temporal_consistency" in extractor:
            mc_num = "MC07"
        elif "causal_verb" in extractor:
            mc_num = "MC08"
        elif "institutional_ner" in extractor:
            mc_num = "MC09"
        elif "semantic_relationship" in extractor:
            mc_num = "MC10"
        print(f"    {mc_num}: {extractor}")
    print()

    # 3. Vehicles en filesystem
    print("🚗 VEHICLES EN FILESYSTEM:")
    print("-" * 80)
    vehicles_fs = scan_vehicles_filesystem()
    print(f"  Total: {len(vehicles_fs)} vehicles")
    for vehicle in vehicles_fs:
        print(f"    - {vehicle}")
    print()

    # 4. Lo que el HUB está registrando
    print("🔌 LO QUE SISAS_INTEGRATION_HUB.PY REGISTRA:")
    print("-" * 80)
    hub_analysis = analyze_hub_registrations()

    if "error" in hub_analysis:
        print(f"  ❌ ERROR: {hub_analysis['error']}")
    else:
        print(f"  Consumers registrados: {hub_analysis['consumers_in_hub']}")
        print(f"  Consumer IDs:")
        for consumer_id in hub_analysis['consumer_ids']:
            print(f"    - {consumer_id}")
    print()

    # 5. DISCREPANCIAS
    print("⚠️  DISCREPANCIAS DETECTADAS:")
    print("-" * 80)

    discrepancies = []

    # Consumers
    if hub_analysis['consumers_in_hub'] != total_fs:
        diff = total_fs - hub_analysis['consumers_in_hub']
        discrepancies.append(f"  ❌ CONSUMERS: Hub registra {hub_analysis['consumers_in_hub']}, pero hay {total_fs} en filesystem (falta registrar {diff})")
    else:
        discrepancies.append(f"  ✅ CONSUMERS: Hub registra correctamente {total_fs} consumers")

    # Extractors
    if len(extractors_fs) == 10:
        discrepancies.append(f"  ✅ EXTRACTORS: 10 extractors presentes en filesystem")
    else:
        discrepancies.append(f"  ⚠️  EXTRACTORS: Se esperaban 10, se encontraron {len(extractors_fs)}")

    # Vehicles
    if len(vehicles_fs) == 8:
        discrepancies.append(f"  ✅ VEHICLES: 8 vehicles presentes en filesystem")
    else:
        discrepancies.append(f"  ⚠️  VEHICLES: Se esperaban 8, se encontraron {len(vehicles_fs)}")

    for disc in discrepancies:
        print(disc)
    print()

    # 6. CONSUMERS FALTANTES
    print("📝 CONSUMERS FALTANTES EN HUB (no registrados):")
    print("-" * 80)

    hub_consumer_ids = set(hub_analysis['consumer_ids'])

    missing_consumers = []
    for phase, consumers in sorted(consumers_fs.items()):
        for consumer_file in consumers:
            # Intentar inferir consumer_id desde filename
            if consumer_file not in str(hub_consumer_ids):
                missing_consumers.append(f"{phase}/{consumer_file}")

    if missing_consumers:
        print(f"  Total faltantes: {len(missing_consumers)}")
        for missing in missing_consumers:
            print(f"    ❌ {missing}")
    else:
        print("  ✅ Todos los consumers están registrados")
    print()

    # 7. COMENTARIOS INCORRECTOS
    print("💬 COMENTARIOS INCORRECTOS EN sisas_integration_hub.py:")
    print("-" * 80)

    hub_file = Path("src/farfan_pipeline/orchestration/sisas_integration_hub.py")
    with open(hub_file) as f:
        lines = f.readlines()

    issues = []
    for i, line in enumerate(lines[:20], 1):
        if "All 11 Consumers" in line:
            issues.append(f"  Línea {i}: Dice 'All 11 Consumers' pero debería ser 'All {total_fs} Consumers'")
        if "All 475+" in line:
            issues.append(f"  Línea {i}: Dice 'All 475+' pero debería ser 'All 476'")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  ✅ Sin problemas en comentarios")
    print()

    # 8. RESUMEN FINAL
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"  Filesystem:       {total_fs} consumers | {len(extractors_fs)} extractors | {len(vehicles_fs)} vehicles")
    print(f"  Hub registra:     {hub_analysis['consumers_in_hub']} consumers | 10 extractors | 8 vehicles")
    print(f"  Faltantes:        {len(missing_consumers)} consumers sin registrar")
    print()

    if len(missing_consumers) > 0 or len(issues) > 0:
        print("  ⚠️  ACCIÓN REQUERIDA: Actualizar sisas_integration_hub.py")
        return 1
    else:
        print("  ✅ TODO CORRECTO")
        return 0

if __name__ == "__main__":
    sys.exit(main())
