#!/usr/bin/env python3
"""
Script ejecutable para generar contratos.
USO: python3 run.py
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Importar módulos locales SIN usar relativos
import importlib.util

# Cargar todos los módulos del contract_generator
base_dir = Path(__file__).parent
modules = [
    'input_registry',
    'method_expander', 
    'chain_composer',
    'contract_assembler',
    'contract_validator',
    'json_emitter',
    'contract_generator'
]

loaded = {}
for mod_name in modules:
    spec = importlib.util.spec_from_file_location(
        mod_name,
        base_dir / f"{mod_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    loaded[mod_name] = module

# Ejecutar generación
ContractGenerator = loaded['contract_generator'].ContractGenerator
InputLoader = loaded['input_registry'].InputLoader

gen = ContractGenerator(
    assets_path=Path(__file__).parent.parent / "epistemological_assets",
    output_path=Path(__file__).parent.parent / "generated_contracts"
)

result = gen.generate()
print(f"✅ {result}")
