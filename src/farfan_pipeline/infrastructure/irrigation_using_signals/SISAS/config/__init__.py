# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/__init__.py

import yaml
from pathlib import Path
from typing import Any, Dict

def load_yaml_config(file_path: str | Path) -> Dict[str, Any]:
    """Carga un archivo de configuración YAML"""
    config_path = Path(file_path)
    if not config_path.exists():
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_bus_config() -> Dict[str, Any]:
    """Obtiene la configuración de buses"""
    base_path = Path(__file__).parent
    return load_yaml_config(base_path / "bus_config.yaml")

def get_irrigation_config() -> Dict[str, Any]:
    """Obtiene la configuración de irrigación"""
    base_path = Path(__file__).parent
    return load_yaml_config(base_path / "irrigation_config.yaml")

def get_vocabulary_config() -> Dict[str, Any]:
    """Obtiene la configuración de vocabularios"""
    base_path = Path(__file__).parent
    return load_yaml_config(base_path / "vocabulary_config.yaml")

__all__ = [
    "load_yaml_config",
    "get_bus_config",
    "get_irrigation_config",
    "get_vocabulary_config"
]
