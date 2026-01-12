#!/usr/bin/env python3
"""
Script de Setup de Infraestructura de Contratos Matemáticos
============================================================

Este script crea la estructura EXACTA de infraestructura para contratos
matemáticos del sistema F.A.R.F.A.N, bajo tolerancia CERO a variaciones.

MANDATO: Estructura exacta /infraestructura/contratos_matematicos/
SEVERIDAD: Cualquier elemento ambiguo o preexistente = ERROR SEVERO

Autor: Sistema F.A.R.F.A.N - Contrato de Setup
Fecha: 2026-01-11
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


class InfrastructureSetupValidator:
    """Validador estricto de setup de infraestructura."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.setup_log: List[Dict] = []
        self.target_path = repo_root / "infraestructura" / "contratos_matematicos"
        
    def log_event(self, event_type: str, message: str, path: str = None,
                  status: str = "INFO", metadata: Dict = None):
        """Registra evento en log de setup."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "status": status,
            "message": message,
        }
        if path:
            event["path"] = str(path)
        if metadata:
            event["metadata"] = metadata
        
        self.setup_log.append(event)
        
        status_symbol = "✓" if status == "SUCCESS" else "✗" if status == "ERROR" else "ℹ"
        print(f"[{status_symbol}] {event_type}: {message}")
        if path:
            print(f"    Path: {path}")
    
    def verify_clean_state(self) -> bool:
        """Verifica que NO exista ningún elemento preexistente."""
        self.log_event("PRE_CHECK", "Verificando estado limpio")
        
        infraestructura_root = self.repo_root / "infraestructura"
        
        if self.target_path.exists():
            self.log_event("PRE_CHECK_FAILED",
                         "DIRECTORIO YA EXISTE - Estado no limpio",
                         str(self.target_path), "ERROR")
            return False
        
        if infraestructura_root.exists():
            # Verificar contenido
            existing_items = list(infraestructura_root.iterdir())
            if existing_items:
                self.log_event("PRE_CHECK_FAILED",
                             f"DIRECTORIO /infraestructura/ contiene {len(existing_items)} items",
                             str(infraestructura_root), "ERROR",
                             {"existing_items": [str(i) for i in existing_items]})
                return False
        
        self.log_event("PRE_CHECK_SUCCESS", "Estado limpio verificado", status="SUCCESS")
        return True
    
    def create_structure(self) -> bool:
        """Crea la estructura EXACTA de directorios."""
        self.log_event("CREATION", "Iniciando creación de estructura")
        
        try:
            # Crear estructura exacta
            self.target_path.mkdir(parents=True, exist_ok=False)
            self.log_event("DIR_CREATED", "Directorio creado exitosamente",
                         str(self.target_path), "SUCCESS")
            
            # Crear archivo README mandatorio
            readme_path = self.target_path / "README.md"
            readme_content = """# Contratos Matemáticos F.A.R.F.A.N

Este directorio contiene los contratos matemáticos del sistema F.A.R.F.A.N.

## Estructura

```
/infraestructura/
    /contratos_matematicos/
        README.md (este archivo)
```

## Propósito

Infraestructura para contratos matemáticos creada mediante proceso de 
reseteo total y setup controlado.

## Metadata

- Creado: {}
- Versión: 1.0.0
- Mandato: Estructura exacta, zero-tolerance a variaciones
""".format(datetime.now(timezone.utc).isoformat())
            
            readme_path.write_text(readme_content, encoding='utf-8')
            self.log_event("FILE_CREATED", "README.md creado",
                         str(readme_path), "SUCCESS")
            
            # Crear .gitkeep para asegurar commit de directorio vacío
            gitkeep_path = self.target_path / ".gitkeep"
            gitkeep_path.write_text("# Directorio de contratos matemáticos\n", encoding='utf-8')
            self.log_event("FILE_CREATED", ".gitkeep creado",
                         str(gitkeep_path), "SUCCESS")
            
            return True
            
        except FileExistsError:
            self.log_event("CREATION_FAILED",
                         "Directorio ya existe - abortar setup",
                         str(self.target_path), "ERROR")
            return False
        except Exception as e:
            self.log_event("CREATION_FAILED",
                         f"Error durante creación: {e}",
                         str(self.target_path), "ERROR")
            return False
    
    def verify_structure(self) -> bool:
        """Verifica que la estructura creada sea EXACTA."""
        self.log_event("VERIFICATION", "Verificando estructura creada")
        
        # Verificar existencia
        if not self.target_path.exists():
            self.log_event("VERIFY_FAILED", "Directorio no existe",
                         str(self.target_path), "ERROR")
            return False
        
        if not self.target_path.is_dir():
            self.log_event("VERIFY_FAILED", "Path no es un directorio",
                         str(self.target_path), "ERROR")
            return False
        
        # Verificar path exacto
        expected_parts = ["infraestructura", "contratos_matematicos"]
        actual_parts = self.target_path.relative_to(self.repo_root).parts
        
        if list(actual_parts) != expected_parts:
            self.log_event("VERIFY_FAILED",
                         f"Path incorrecto: esperado {expected_parts}, actual {actual_parts}",
                         str(self.target_path), "ERROR")
            return False
        
        # Verificar contenido
        expected_files = {"README.md", ".gitkeep"}
        actual_files = {f.name for f in self.target_path.iterdir()}
        
        if actual_files != expected_files:
            self.log_event("VERIFY_WARNING",
                         f"Contenido inesperado: esperado {expected_files}, actual {actual_files}",
                         str(self.target_path), "WARNING")
        
        self.log_event("VERIFY_SUCCESS",
                     "Estructura verificada correctamente",
                     status="SUCCESS")
        return True
    
    def generate_setup_manifest(self, output_path: Path):
        """Genera manifiesto de setup."""
        manifest = {
            "setup_execution": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repo_root": str(self.repo_root),
                "target_path": str(self.target_path),
                "total_events": len(self.setup_log),
            },
            "structure_created": {
                "base_path": "/infraestructura",
                "contracts_path": "/infraestructura/contratos_matematicos",
                "files_created": ["README.md", ".gitkeep"],
            },
            "setup_log": self.setup_log,
        }
        
        output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        self.log_event("MANIFEST", f"Manifiesto generado: {output_path}",
                      str(output_path), "SUCCESS")
        
        # Versión legible
        summary_path = output_path.with_suffix('.txt')
        with summary_path.open('w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MANIFIESTO DE SETUP - INFRAESTRUCTURA DE CONTRATOS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {manifest['setup_execution']['timestamp']}\n")
            f.write(f"Path creado: {manifest['setup_execution']['target_path']}\n\n")
            f.write("ESTRUCTURA CREADA:\n")
            f.write(f"  {manifest['structure_created']['base_path']}/\n")
            f.write(f"      {manifest['structure_created']['contracts_path'].split('/')[-1]}/\n")
            for file in manifest['structure_created']['files_created']:
                f.write(f"          {file}\n")
            f.write("\nLOG DE EVENTOS:\n")
            for event in self.setup_log:
                f.write(f"[{event['timestamp']}] {event['event_type']}: {event['message']}\n")


def main():
    """Función principal de ejecución."""
    print("=" * 80)
    print("SCRIPT DE SETUP - INFRAESTRUCTURA DE CONTRATOS F.A.R.F.A.N")
    print("=" * 80)
    print()
    print("📁 ESTRUCTURA A CREAR: /infraestructura/contratos_matematicos/")
    print("⚠️  MANDATO: Estructura exacta, zero-tolerance a variaciones")
    print()
    print("-" * 80)
    
    # Inicializar validator
    repo_root = Path(__file__).parent
    validator = InfrastructureSetupValidator(repo_root)
    
    # Fase 1: Pre-verificación
    print("\n🔍 FASE 1: VERIFICACIÓN DE ESTADO LIMPIO")
    print("-" * 80)
    if not validator.verify_clean_state():
        print("\n✗ FALLO: Estado no limpio - abortar setup")
        print("  ACCIÓN REQUERIDA: Ejecutar purge_contratos.py primero")
        return 1
    
    # Fase 2: Creación
    print("\n📁 FASE 2: CREACIÓN DE ESTRUCTURA")
    print("-" * 80)
    if not validator.create_structure():
        print("\n✗ FALLO: Error durante creación de estructura")
        return 1
    
    # Fase 3: Verificación
    print("\n✓ FASE 3: VERIFICACIÓN DE ESTRUCTURA")
    print("-" * 80)
    if not validator.verify_structure():
        print("\n✗ FALLO: Estructura no coincide con especificación")
        return 1
    
    # Fase 4: Manifiesto
    print("\n📊 FASE 4: GENERACIÓN DE MANIFIESTO")
    print("-" * 80)
    manifest_path = repo_root / "SETUP_MANIFEST.json"
    validator.generate_setup_manifest(manifest_path)
    
    # Resultado final
    print("\n" + "=" * 80)
    print("✓ SETUP EXITOSO - Infraestructura creada correctamente")
    print(f"✓ Path: {validator.target_path}")
    print(f"✓ Manifiesto: {manifest_path}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
