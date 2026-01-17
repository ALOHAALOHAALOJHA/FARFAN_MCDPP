#!/usr/bin/env python3
"""
Script Destructivo de Borrado Completo de Artefactos Contractuales
==================================================================

Este script ejecuta el borrado total de TODOS los artefactos contractuales
preexistentes del sistema F.A.R.F.A.N, con auditoría rigurosa y verificación
inmediata.

SEVERIDAD: Este es un script DESTRUCTIVO. No se permite recuperación.
MANDATO: Zero-tolerance para residuos. Cualquier archivo restante = FALLO TOTAL.

Autor: Sistema F.A.R.F.A.N - Contrato de Reseteo
Fecha: 2026-01-11
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set


class ContractPurgeAuditor:
    """Auditor riguroso de borrado contractual con zero-tolerance."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.audit_log: List[Dict] = []
        self.deleted_items: Set[Path] = set()
        self.failed_deletions: List[Dict] = []
        
        # Definición EXHAUSTIVA de artefactos contractuales
        self.contract_directories = [
            "artifacts/data/contracts",
            "src/farfan_pipeline/infrastructure/contractual",
            "src/farfan_pipeline/phases/Phase_1/contracts",
            "src/farfan_pipeline/phases/Phase_2/contract_generator",
            "src/farfan_pipeline/phases/Phase_2/contracts",
            "src/farfan_pipeline/phases/Phase_2/generated_contracts",
            "src/farfan_pipeline/phases/Phase_3/contracts",
            "src/farfan_pipeline/phases/Phase_4/contracts",
            "tests/phase2_contracts",
        ]
        
        # Archivos específicos de contratos
        self.contract_files = [
            "scripts/generation/run_contract_generator.py",
            "scripts/enforcement/enforce_contracts.py",
            "scripts/extract_300_contracts.py",
            "scripts/validation/sync_contracts_from_questionnaire.py",
            "scripts/validation/verify_contract_signal_wiring.py",
        ]
    
    def log_event(self, event_type: str, message: str, path: str = None, 
                  status: str = "INFO", metadata: Dict = None):
        """Registra evento en log de auditoría."""
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
        
        self.audit_log.append(event)
        
        # Output en tiempo real para transparencia
        status_symbol = "✓" if status == "SUCCESS" else "✗" if status == "ERROR" else "ℹ"
        print(f"[{status_symbol}] {event_type}: {message}")
        if path:
            print(f"    Path: {path}")
    
    def enumerate_targets(self) -> Dict[str, List[Path]]:
        """Enumera TODOS los artefactos que deben ser eliminados."""
        self.log_event("ENUMERATION", "Iniciando enumeración de artefactos contractuales")
        
        targets = {
            "directories": [],
            "files": []
        }
        
        # Verificar directorios
        for dir_path in self.contract_directories:
            full_path = self.repo_root / dir_path
            if full_path.exists():
                targets["directories"].append(full_path)
                self.log_event("FOUND_DIR", f"Directorio encontrado: {dir_path}", 
                             str(full_path), "INFO")
                
                # Contar archivos dentro
                if full_path.is_dir():
                    file_count = sum(1 for _ in full_path.rglob("*") if _.is_file())
                    self.log_event("DIR_CONTENT", 
                                 f"Directorio contiene {file_count} archivos",
                                 str(full_path), "INFO", 
                                 {"file_count": file_count})
        
        # Verificar archivos específicos
        for file_path in self.contract_files:
            full_path = self.repo_root / file_path
            if full_path.exists():
                targets["files"].append(full_path)
                self.log_event("FOUND_FILE", f"Archivo encontrado: {file_path}",
                             str(full_path), "INFO")
        
        # Buscar archivos contract* adicionales (no en backups ni .git)
        self.log_event("DEEP_SCAN", "Realizando escaneo profundo de archivos contract*")
        
        additional_contract_files = []
        for pattern in ["*contract*.py", "*contract*.json", "*contract*.md"]:
            for path in self.repo_root.rglob(pattern):
                # Excluir backups y .git
                if "backups" not in path.parts and ".git" not in path.parts:
                    rel_path = path.relative_to(self.repo_root)
                    # Verificar si ya está en lista de directorios a borrar
                    already_covered = any(
                        path.is_relative_to(self.repo_root / d) 
                        for d in self.contract_directories
                    )
                    if not already_covered and path not in targets["files"]:
                        additional_contract_files.append(path)
        
        if additional_contract_files:
            targets["files"].extend(additional_contract_files)
            self.log_event("DEEP_SCAN_RESULT", 
                         f"Encontrados {len(additional_contract_files)} archivos adicionales",
                         status="WARNING",
                         metadata={"count": len(additional_contract_files)})
        
        total_dirs = len(targets["directories"])
        total_files = len(targets["files"])
        self.log_event("ENUMERATION_COMPLETE", 
                      f"Enumeración completa: {total_dirs} directorios, {total_files} archivos",
                      status="SUCCESS",
                      metadata={"directories": total_dirs, "files": total_files})
        
        return targets
    
    def execute_purge(self, targets: Dict[str, List[Path]], dry_run: bool = False) -> bool:
        """Ejecuta el borrado DESTRUCTIVO de todos los artefactos."""
        if dry_run:
            self.log_event("PURGE_MODE", "MODO DRY-RUN - Simulación sin borrado real", 
                         status="WARNING")
        else:
            self.log_event("PURGE_MODE", "MODO DESTRUCTIVO - Borrado permanente activado",
                         status="WARNING")
        
        success = True
        
        # Borrar archivos individuales primero
        for file_path in targets["files"]:
            try:
                if not dry_run:
                    file_path.unlink()
                self.deleted_items.add(file_path)
                self.log_event("DELETE_FILE", f"Archivo eliminado: {file_path.name}",
                             str(file_path), "SUCCESS")
            except Exception as e:
                self.failed_deletions.append({
                    "path": str(file_path),
                    "type": "file",
                    "error": str(e)
                })
                self.log_event("DELETE_FAILED", f"Fallo al eliminar archivo: {e}",
                             str(file_path), "ERROR")
                success = False
        
        # Borrar directorios (recursivamente)
        for dir_path in targets["directories"]:
            try:
                if not dry_run:
                    shutil.rmtree(dir_path)
                self.deleted_items.add(dir_path)
                self.log_event("DELETE_DIR", f"Directorio eliminado: {dir_path.name}",
                             str(dir_path), "SUCCESS")
            except Exception as e:
                self.failed_deletions.append({
                    "path": str(dir_path),
                    "type": "directory",
                    "error": str(e)
                })
                self.log_event("DELETE_FAILED", f"Fallo al eliminar directorio: {e}",
                             str(dir_path), "ERROR")
                success = False
        
        return success
    
    def verify_complete_removal(self) -> bool:
        """Verifica que NO QUEDEN artefactos contractuales residuales."""
        self.log_event("VERIFICATION", "Iniciando verificación de remoción completa")
        
        residual_items = []
        
        # Verificar que directorios no existan
        for dir_path in self.contract_directories:
            full_path = self.repo_root / dir_path
            if full_path.exists():
                residual_items.append(str(full_path))
                self.log_event("RESIDUAL_DIR", f"DIRECTORIO RESIDUAL ENCONTRADO: {dir_path}",
                             str(full_path), "ERROR")
        
        # Verificar que archivos no existan
        for file_path in self.contract_files:
            full_path = self.repo_root / file_path
            if full_path.exists():
                residual_items.append(str(full_path))
                self.log_event("RESIDUAL_FILE", f"ARCHIVO RESIDUAL ENCONTRADO: {file_path}",
                             str(full_path), "ERROR")
        
        # Escaneo final de seguridad
        for pattern in ["*contract*.py", "*contract*.json"]:
            for path in self.repo_root.rglob(pattern):
                if "backups" not in path.parts and ".git" not in path.parts:
                    # Verificar si está en áreas permitidas (ej. este mismo script)
                    if path.name == "purge_contratos.py" or path.name == "setup_infraestructura.py":
                        continue
                    residual_items.append(str(path))
                    self.log_event("RESIDUAL_UNEXPECTED", 
                                 f"ARCHIVO RESIDUAL INESPERADO: {path.name}",
                                 str(path), "ERROR")
        
        if residual_items:
            self.log_event("VERIFICATION_FAILED",
                         f"VERIFICACIÓN FALLIDA: {len(residual_items)} items residuales",
                         status="ERROR",
                         metadata={"residual_count": len(residual_items),
                                  "residual_items": residual_items})
            return False
        else:
            self.log_event("VERIFICATION_SUCCESS",
                         "NO QUEDAN ARCHIVOS NI CARPETAS RESTRINGIDAS",
                         status="SUCCESS")
            return True
    
    def generate_audit_report(self, output_path: Path):
        """Genera reporte de auditoría completo."""
        report = {
            "purge_execution": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repo_root": str(self.repo_root),
                "total_events": len(self.audit_log),
                "deleted_items_count": len(self.deleted_items),
                "failed_deletions_count": len(self.failed_deletions),
            },
            "deleted_items": [str(p) for p in self.deleted_items],
            "failed_deletions": self.failed_deletions,
            "audit_log": self.audit_log,
        }
        
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        self.log_event("AUDIT_REPORT", f"Reporte generado: {output_path}",
                      str(output_path), "SUCCESS")
        
        # También generar versión legible
        summary_path = output_path.with_suffix('.txt')
        with summary_path.open('w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE AUDITORÍA - PURGA DE CONTRATOS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {report['purge_execution']['timestamp']}\n")
            f.write(f"Items eliminados: {report['purge_execution']['deleted_items_count']}\n")
            f.write(f"Fallos: {report['purge_execution']['failed_deletions_count']}\n\n")
            
            if self.failed_deletions:
                f.write("FALLOS EN BORRADO:\n")
                for failure in self.failed_deletions:
                    f.write(f"  - {failure['path']}: {failure['error']}\n")
                f.write("\n")
            
            f.write("LOG DE EVENTOS:\n")
            for event in self.audit_log:
                f.write(f"[{event['timestamp']}] {event['event_type']}: {event['message']}\n")


def main():
    """Función principal de ejecución."""
    print("=" * 80)
    print("SCRIPT DESTRUCTIVO DE PURGA DE CONTRATOS F.A.R.F.A.N")
    print("=" * 80)
    print()
    print("⚠️  ADVERTENCIA: Este script realizará borrado PERMANENTE")
    print("⚠️  No se permite recuperación de datos")
    print()
    
    # Determinar modo
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    
    if dry_run:
        print("🔍 MODO: DRY-RUN (Simulación)")
    else:
        print("💣 MODO: DESTRUCTIVO (Borrado real)")
        if not force:
            print()
            response = input("⚠️  ¿Confirma la ejecución destructiva? (escriba 'DELETE' para confirmar): ")
            if response != "DELETE":
                print("❌ Operación cancelada por el usuario")
                return 1
    
    print()
    print("-" * 80)
    
    # Inicializar auditor
    repo_root = Path(__file__).resolve().parent
    auditor = ContractPurgeAuditor(repo_root)
    
    # Fase 1: Enumeración
    print("\n📋 FASE 1: ENUMERACIÓN DE ARTEFACTOS")
    print("-" * 80)
    targets = auditor.enumerate_targets()
    
    # Fase 2: Purga
    print("\n💣 FASE 2: EJECUCIÓN DE PURGA")
    print("-" * 80)
    purge_success = auditor.execute_purge(targets, dry_run=dry_run)
    
    # Fase 3: Verificación
    print("\n✓ FASE 3: VERIFICACIÓN DE REMOCIÓN COMPLETA")
    print("-" * 80)
    verify_success = auditor.verify_complete_removal() if not dry_run else True
    
    # Fase 4: Reporte
    print("\n📊 FASE 4: GENERACIÓN DE REPORTE")
    print("-" * 80)
    report_path = repo_root / "PURGE_AUDIT_REPORT.json"
    auditor.generate_audit_report(report_path)
    
    # Resultado final
    print("\n" + "=" * 80)
    if dry_run:
        print("✓ DRY-RUN COMPLETADO - No se realizaron cambios reales")
        return 0
    elif purge_success and verify_success:
        print("✓ PURGA EXITOSA - Todos los artefactos contractuales eliminados")
        print(f"✓ Reporte de auditoría: {report_path}")
        return 0
    else:
        print("✗ PURGA FALLIDA - Verificar log de errores")
        print(f"✗ Reporte de auditoría: {report_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
