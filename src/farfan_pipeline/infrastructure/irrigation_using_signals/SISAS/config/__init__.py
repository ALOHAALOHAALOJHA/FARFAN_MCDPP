# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config/__init__.py

import yaml
import os
from typing import Any, Dict

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Carga un archivo de configuración YAML"""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_bus_config() -> Dict[str, Any]:
    """Obtiene la configuración de buses"""
    base_path = os.path.dirname(__file__)
    return load_yaml_config(os.path.join(base_path, "bus_config.yaml"))

def get_irrigation_config() -> Dict[str, Any]:
    """Obtiene la configuración de irrigación"""
    base_path = os.path.dirname(__file__)
    return load_yaml_config(os.path.join(base_path, "irrigation_config.yaml"))

def get_vocabulary_config() -> Dict[str, Any]:
    """Obtiene la configuración de vocabularios"""
    base_path = os.path.dirname(__file__)
    return load_yaml_config(os.path.join(base_path, "vocabulary_config.yaml"))

__all__ = [
    "load_yaml_config",
    "get_bus_config",
    "get_irrigation_config",
    "get_vocabulary_config"
]
