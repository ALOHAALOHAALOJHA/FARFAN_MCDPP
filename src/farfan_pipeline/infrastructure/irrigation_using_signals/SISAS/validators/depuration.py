# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/validators/depuration.py

"""
PILAR 1: DEPURACIÓN - Validación de archivos ANTES de irrigación

Este módulo implementa el primer pilar de SISAS: la depuración de archivos canónicos.
Todos los archivos deben pasar por DepurationValidator ANTES de entrar al sistema de irrigación.

AXIOMA: Ningún archivo corrupto o inválido entra al sistema de señales.
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import fnmatch


# =============================================================================
# RESULT TYPES
# =============================================================================

class SeverityLevel(Enum):
    """Niveles de severidad para issues de depuración"""
    CRITICAL = "CRITICAL"   # Bloquea irrigación completamente
    HIGH = "HIGH"           # Debería bloquear, puede permitir con warning
    MEDIUM = "MEDIUM"       # Warning, pero permite continuar
    LOW = "LOW"             # Info, no afecta irrigación
    INFO = "INFO"           # Informacional


@dataclass
class DepurationError:
    """
    Error de depuración que bloquea la irrigación.

    Los errores CRITICAL/HIGH impiden que el archivo se irrigue.
    """
    type: str  # "FILE_NOT_FOUND", "INVALID_JSON", "SCHEMA_VIOLATION", etc.
    severity: SeverityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    line: Optional[int] = None
    path: Optional[List[str]] = None  # Para errores de schema (JSON path)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "line": self.line,
            "path": self.path
        }


@dataclass
class DepurationWarning:
    """
    Warning de depuración que NO bloquea la irrigación.

    Los warnings informan sobre issues que no impiden la irrigación
    pero deberían ser revisados.
    """
    type: str
    severity: SeverityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details
        }


@dataclass
class DepurationResult:
    """
    Resultado de la depuración de un archivo.

    Atributos:
        valid: True si el archivo puede irrigarse, False si tiene errores críticos
        depurated: True si pasó por el proceso de depuración
        file_path: Path del archivo depurado
        file_size_bytes: Tamaño del archivo
        errors: Lista de errores encontrados
        warnings: Lista de warnings encontrados
        role: Rol del archivo (metadata, questions, keywords, etc.)
        references: Lista de referencias encontradas
        metadata: Metadatos adicionales del resultado
    """
    valid: bool = False
    depurated: bool = False
    file_path: str = ""
    file_size_bytes: int = 0
    errors: List[DepurationError] = field(default_factory=list)
    warnings: List[DepurationWarning] = field(default_factory=list)
    role: Optional[str] = None
    references: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_critical_errors(self) -> bool:
        """Tiene errores críticos que bloquean irrigación"""
        return any(e.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
                   for e in self.errors)

    @property
    def error_count_by_severity(self) -> Dict[str, int]:
        """Conteo de errores por severidad"""
        counts = {}
        for error in self.errors:
            sev = error.severity.value
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    @property
    def warning_count_by_severity(self) -> Dict[str, int]:
        """Conteo de warnings por severidad"""
        counts = {}
        for warning in self.warnings:
            sev = warning.severity.value
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "depurated": self.depurated,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "role": self.role,
            "references_count": len(self.references),
            "metadata": self.metadata
        }


# =============================================================================
# FILE ROLES
# =============================================================================

class FileRole(Enum):
    """Roles que puede tener un archivo en el questionnaire canónico"""
    METADATA = "metadata"
    QUESTIONS = "questions"
    KEYWORDS = "keywords"
    PATTERNS = "patterns"
    MEMBERSHIP_CRITERIA = "membership_criteria"
    ENTITIES = "entities"
    CAPABILITIES = "capabilities"
    AGGREGATION_RULES = "aggregation_rules"
    CONTEXTUAL_ENRICHMENT = "contextual_enrichment"
    SCORING_SYSTEM = "scoring_system"
    GOVERNANCE = "governance"
    CONFIG = "config"
    VALIDATIONS = "validations"
    SEMANTIC = "semantic"
    UNKNOWN = "unknown"


# Roles que pueden irrigarse (generan señales)
IRRIGABLE_ROLES: Set[FileRole] = {
    FileRole.METADATA,
    FileRole.QUESTIONS,
    FileRole.KEYWORDS,
    FileRole.PATTERNS,
    FileRole.MEMBERSHIP_CRITERIA,
    FileRole.AGGREGATION_RULES,
    FileRole.CONTEXTUAL_ENRICHMENT,
    FileRole.SCORING_SYSTEM,
    FileRole.GOVERNANCE,
}


# =============================================================================
# DEPURATION SCHEMAS
# =============================================================================

# Schemas mínimos por rol
SCHEMAS_BY_ROLE: Dict[FileRole, Dict[str, Any]] = {
    FileRole.METADATA: {
        "type": "object",
        "required": ["id", "name", "description", "version"],
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "version": {"type": "string"}
        }
    },
    FileRole.QUESTIONS: {
        "type": "object",
        "required": ["questions"],
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "text"]
                }
            }
        }
    },
    FileRole.KEYWORDS: {
        "type": "object",
        "required": ["keywords"],
        "properties": {
            "keywords": {"type": "array"}
        }
    },
    FileRole.PATTERNS: {
        "type": "object",
        "required": ["patterns"],
        "properties": {
            "patterns": {"type": "array"}
        }
    },
    FileRole.MEMBERSHIP_CRITERIA: {
        "type": "object",
        "required": ["id", "name", "description", "criteria"],
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "criteria": {"type": "array"}
        }
    },
    FileRole.ENTITIES: {
        "type": "object",
        "required": ["entities"],
        "properties": {
            "entities": {"type": "array"}
        }
    },
    FileRole.CAPABILITIES: {
        "type": "object",
        "required": ["capabilities"],
        "properties": {
            "capabilities": {"type": "array"}
        }
    },
    FileRole.AGGREGATION_RULES: {
        "type": "object",
        "required": ["rules", "weights"],
        "properties": {
            "rules": {"type": "array"},
            "weights": {"type": "object"}
        }
    },
    FileRole.CONTEXTUAL_ENRICHMENT: {
        "type": "object",
        "required": ["context"],
        "properties": {
            "context": {"type": "object"}
        }
    },
    FileRole.SCORING_SYSTEM: {
        "type": "object",
        "required": ["dimensions", "thresholds"],
        "properties": {
            "dimensions": {"type": "array"},
            "thresholds": {"type": "object"}
        }
    },
    FileRole.GOVERNANCE: {
        "type": "object",
        "required": ["policies", "actors", "mechanisms"],
        "properties": {
            "policies": {"type": "array"},
            "actors": {"type": "array"},
            "mechanisms": {"type": "array"}
        }
    },
}


# =============================================================================
# MAIN DEPURATION VALIDATOR
# =============================================================================

class DepurationValidator:
    """
    Validador de depuración de archivos canónicos.

    Responsabilidad: Validar que los archivos son válidos ANTES de entrar al sistema de irrigación.

    Este es el PILAR 1 de SISAS: DEPURACIÓN.

    Checks implementados:
        1. EXISTENCIA - El archivo existe en disco
        2. FORMATO JSON - El archivo tiene JSON válido
        3. SCHEMA COMPLIANCE - Cumple el schema según su rol
        4. INTEGRIDAD REFERENCIAL - Las referencias a otros archivos existen
        5. REQUISITOS DE IRRIGACIÓN - Tiene vehicle y consumers asignados
        6. COHERENCIA DE DATOS - Los datos son lógicamente consistentes

    Uso:
        validator = DepurationValidator(base_path="canonic_questionnaire_central")
        result = validator.depurate("dimensions/DIM01_INSUMOS/metadata.json")

        if not result.valid:
            print(f"Errors: {result.errors}")
            return  # No irrigar

        # Continuar con irrigación
        irrigator.irrigate_file(...)
    """

    def __init__(
        self,
        base_path: str = "canonic_questionnaire_central",
        vehicle_assignments: Optional[Dict[str, List[str]]] = None,
        consumer_assignments: Optional[Dict[str, List[str]]] = None
    ):
        """
        Inicializa el validador de depuración.

        Args:
            base_path: Path base al questionnaire canónico
            vehicle_assignments: Mapeo file_pattern → vehicles (opcional)
            consumer_assignments: Mapeo file_pattern → consumers (opcional)
        """
        self.base_path = base_path
        self.vehicle_assignments = vehicle_assignments or self._get_default_vehicle_assignments()
        self.consumer_assignments = consumer_assignments or self._get_default_consumer_assignments()

        # Caché de referencias
        self._reference_cache: Dict[str, bool] = {}

    # =========================================================================
    # MAIN API
    # =========================================================================

    def depurate(self, file_path: str) -> DepurationResult:
        """
        Depura un archivo canónico ejecutando todos los checks.

        Args:
            file_path: Path relativo al base_path

        Returns:
            DepurationResult con el resultado de la depuración
        """
        result = DepurationResult(
            file_path=file_path,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )

        # ═══════════════════════════════════════════════════════
        # CHECK 1: EXISTENCIA
        # ═══════════════════════════════════════════════════════
        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path):
            result.errors.append(DepurationError(
                type="FILE_NOT_FOUND",
                severity=SeverityLevel.CRITICAL,
                message=f"Archivo no existe: {full_path}",
                details={"full_path": full_path}
            ))
            result.valid = False
            result.depurated = True
            return result

        # Obtener tamaño
        result.file_size_bytes = os.path.getsize(full_path)

        # ═══════════════════════════════════════════════════════
        # CHECK 2: FORMATO JSON VÁLIDO
        # ═══════════════════════════════════════════════════════
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            result.errors.append(DepurationError(
                type="INVALID_JSON",
                severity=SeverityLevel.CRITICAL,
                message=f"JSON corrupto: {e.msg}",
                details={"error": str(e)},
                line=e.lineno
            ))
            result.valid = False
            result.depurated = True
            return result
        except Exception as e:
            result.errors.append(DepurationError(
                type="FILE_READ_ERROR",
                severity=SeverityLevel.CRITICAL,
                message=f"Error leyendo archivo: {str(e)}",
                details={"error": str(e)}
            ))
            result.valid = False
            result.depurated = True
            return result

        # Determinar rol del archivo
        result.role = self._determine_role(file_path)
        result.metadata["detected_role"] = result.role

        # ═══════════════════════════════════════════════════════
        # CHECK 3: SCHEMA COMPLIANCE
        # ═══════════════════════════════════════════════════════
        schema_errors = self._check_schema_compliance(content, result.role, file_path)
        result.errors.extend(schema_errors)

        # ═══════════════════════════════════════════════════════
        # CHECK 4: INTEGRIDAD REFERENCIAL
        # ═══════════════════════════════════════════════════════
        references = self._extract_references(content, result.role, file_path)
        result.references = references

        reference_errors = self._check_referential_integrity(references, file_path)
        result.errors.extend(reference_errors)

        # ═══════════════════════════════════════════════════════
        # CHECK 5: REQUISITOS DE IRRIGACIÓN
        # ═══════════════════════════════════════════════════════
        if FileRole(result.role) in IRRIGABLE_ROLES:
            irrigation_warnings = self._check_irrigation_requirements(file_path, result.role)
            result.warnings.extend(irrigation_warnings)

        # ═══════════════════════════════════════════════════════
        # CHECK 6: COHERENCIA DE DATOS
        # ═══════════════════════════════════════════════════════
        coherence_warnings = self._check_data_coherence(content, result.role, file_path)
        result.warnings.extend(coherence_warnings)

        # ═══════════════════════════════════════════════════════
        # RESULTADO FINAL
        # ═══════════════════════════════════════════════════════
        result.valid = not result.has_critical_errors
        result.depurated = True

        return result

    def depurate_batch(
        self,
        file_paths: List[str],
        fail_fast: bool = False
    ) -> Dict[str, DepurationResult]:
        """
        Depura múltiples archivos en lote.

        Args:
            file_paths: Lista de paths a depurar
            fail_fast: Si True, detiene al primer error crítico

        Returns:
            Dict mapeando file_path → DepurationResult
        """
        results = {}

        for file_path in file_paths:
            result = self.depurate(file_path)
            results[file_path] = result

            if fail_fast and not result.valid and result.has_critical_errors:
                break

        return results

    def depurate_all(
        self,
        pattern: Optional[str] = None,
        relative_path: str = ""
    ) -> Dict[str, DepurationResult]:
        """
        Depura todos los archivos que coinciden con un patrón.

        Args:
            pattern: Patrón de archivo (ej: "metadata.json", "*.json")
            relative_path: Path relativo para buscar

        Returns:
            Dict mapeando file_path → DepurationResult + summary
        """
        # Descubrir archivos
        search_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(search_path):
            return {}

        all_files = []
        for root, dirs, files in os.walk(search_path):
            for filename in files:
                if filename.endswith(".json"):
                    if pattern is None or fnmatch.fnmatch(filename, pattern):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, self.base_path)
                        all_files.append(rel_path)

        # Depurar todos
        results = {}
        for file_path in all_files:
            results[file_path] = self.depurate(file_path)

        return results

    # =========================================================================
    # CHECK 1: EXISTENCIA (ya implementado en depurate())
    # =========================================================================

    # =========================================================================
    # CHECK 2: FORMATO JSON (ya implementado en depurate())
    # =========================================================================

    # =========================================================================
    # CHECK 3: SCHEMA COMPLIANCE
    # =========================================================================

    def _check_schema_compliance(
        self,
        content: Dict[str, Any],
        role: str,
        file_path: str
    ) -> List[DepurationError]:
        """Verifica que el contenido cumple el schema según su rol"""
        errors = []

        try:
            file_role = FileRole(role)
        except ValueError:
            # Rol desconocido - warning, no error
            return []

        schema = SCHEMAS_BY_ROLE.get(file_role)
        if not schema:
            # No hay schema definido para este rol
            return []

        # Verificar campos requeridos
        required = schema.get("required", [])
        for field in required:
            if field not in content:
                errors.append(DepurationError(
                    type="SCHEMA_VIOLATION",
                    severity=SeverityLevel.HIGH,
                    message=f"Campo requerido faltante: {field}",
                    details={"field": field, "file": file_path}
                ))

        # Verificar tipos de campos conocidos
        properties = schema.get("properties", {})
        for field, spec in properties.items():
            if field in content:
                expected_type = spec.get("type")
                actual_value = content[field]
                actual_type = type(actual_value).__name__

                # Mapeo de tipos Python → JSON schema
                type_mapping = {
                    "str": "string",
                    "int": "integer",
                    "float": "number",
                    "bool": "boolean",
                    "list": "array",
                    "dict": "object"
                }

                if expected_type and expected_type != type_mapping.get(actual_type):
                    # Verificar si es compatible
                    if expected_type == "array" and not isinstance(actual_value, list):
                        errors.append(DepurationError(
                            type="SCHEMA_VIOLATION",
                            severity=SeverityLevel.MEDIUM,
                            message=f"Campo '{field}' debe ser {expected_type}, es {actual_type}",
                            details={
                                "field": field,
                                "expected": expected_type,
                                "actual": actual_type,
                                "file": file_path
                            }
                        ))

        return errors

    # =========================================================================
    # CHECK 4: INTEGRIDAD REFERENCIAL
    # =========================================================================

    def _extract_references(
        self,
        content: Dict[str, Any],
        role: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Extrae referencias a otros archivos del contenido"""
        references = []

        # Referencias a dimensiones
        if "dimension_id" in content:
            dim_id = content["dimension_id"]
            references.append({
                "type": "dimension",
                "target": dim_id,
                "field": "dimension_id",
                "expected_path": f"dimensions/{dim_id}/metadata.json"
            })

        if "dimension" in content:
            dim_id = content["dimension"]
            references.append({
                "type": "dimension",
                "target": dim_id,
                "field": "dimension",
                "expected_path": f"dimensions/{dim_id}/metadata.json"
            })

        # Referencias a policy_areas
        if "policy_area" in content:
            pa_id = content["policy_area"]
            references.append({
                "type": "policy_area",
                "target": pa_id,
                "field": "policy_area",
                "expected_path": f"policy_areas/{pa_id}/metadata.json"
            })

        if "policy_areas" in content and isinstance(content["policy_areas"], list):
            for pa_id in content["policy_areas"]:
                references.append({
                    "type": "policy_area",
                    "target": pa_id,
                    "field": "policy_areas",
                    "expected_path": f"policy_areas/{pa_id}/metadata.json"
                })

        # Referencias a clusters
        if "cluster_id" in content:
            cl_id = content["cluster_id"]
            references.append({
                "type": "cluster",
                "target": cl_id,
                "field": "cluster_id",
                "expected_path": f"clusters/{cl_id}/metadata.json"
            })

        # Referencias normativas (si existen como archivos)
        if "normative_references" in content and isinstance(content["normative_references"], list):
            for ref in content["normative_references"]:
                if isinstance(ref, dict) and "file_path" in ref:
                    references.append({
                        "type": "normative",
                        "target": ref["file_path"],
                        "field": "normative_references"
                    })

        return references

    def _check_referential_integrity(
        self,
        references: List[Dict[str, Any]],
        source_file: str
    ) -> List[DepurationError]:
        """Verifica que las referencias existan"""
        errors = []

        for ref in references:
            expected_path = ref.get("expected_path")
            if not expected_path:
                continue

            # Usar caché si está disponible
            if expected_path in self._reference_cache:
                exists = self._reference_cache[expected_path]
            else:
                full_path = os.path.join(self.base_path, expected_path)
                exists = os.path.exists(full_path)
                self._reference_cache[expected_path] = exists

            if not exists:
                errors.append(DepurationError(
                    type="BROKEN_REFERENCE",
                    severity=SeverityLevel.HIGH,
                    message=f"Referencia rota: {ref['target']} ({ref['type']})",
                    details={
                        "target": ref["target"],
                        "type": ref["type"],
                        "field": ref["field"],
                        "expected_path": expected_path,
                        "source_file": source_file
                    }
                ))

        return errors

    # =========================================================================
    # CHECK 5: REQUISITOS DE IRRIGACIÓN
    # =========================================================================

    def _check_irrigation_requirements(
        self,
        file_path: str,
        role: str
    ) -> List[DepurationWarning]:
        """Verifica que el archivo tenga vehicle y consumers asignados"""
        warnings = []

        # Buscar vehicle assignment
        vehicles_assigned = self._get_vehicles_for_file(file_path)
        if not vehicles_assigned:
            warnings.append(DepurationWarning(
                type="NO_VEHICLE",
                severity=SeverityLevel.MEDIUM,
                message=f"Archivo irrigable sin vehicle asignado",
                details={"file": file_path, "role": role}
            ))

        # Buscar consumer assignment
        consumers_assigned = self._get_consumers_for_file(file_path)
        if not consumers_assigned:
            warnings.append(DepurationWarning(
                type="NO_CONSUMERS",
                severity=SeverityLevel.MEDIUM,
                message=f"Archivo irrigable sin consumers",
                details={"file": file_path, "role": role}
            ))

        return warnings

    # =========================================================================
    # CHECK 6: COHERENCIA DE DATOS
    # =========================================================================

    def _check_data_coherence(
        self,
        content: Dict[str, Any],
        role: str,
        file_path: str
    ) -> List[DepurationWarning]:
        """Verifica coherencia lógica de los datos"""
        warnings = []

        # Coherencia para metadata
        if role == FileRole.METADATA.value:
            # Verificar que id sea consistente con nombre
            if "id" in content and "name" in content:
                id_val = content["id"]
                name_val = content["name"]
                # El ID debería aparecer en el nombre o viceversa
                if id_val and name_val and id_val not in name_val and name_val not in id_val:
                    warnings.append(DepurationWarning(
                        type="COHERENCE_ID_NAME",
                        severity=SeverityLevel.LOW,
                        message=f"ID y nombre parecen no relacionados",
                        details={"id": id_val, "name": name_val, "file": file_path}
                    ))

            # Verificar version format
            if "version" in content:
                version = content["version"]
                if not isinstance(version, str) or not version.replace(".", "").isdigit():
                    warnings.append(DepurationWarning(
                        type="COHERENCE_VERSION",
                        severity=SeverityLevel.LOW,
                        message=f"Version no sigue formato esperado (x.y.z)",
                        details={"version": version, "file": file_path}
                    ))

        # Coherencia para questions
        if role == FileRole.QUESTIONS.value:
            # Verificar que questions sea una lista
            if "questions" in content and not isinstance(content["questions"], list):
                warnings.append(DepurationWarning(
                    type="COHERENCE_QUESTIONS_TYPE",
                    severity=SeverityLevel.MEDIUM,
                    message=f"Campo 'questions' debe ser una lista",
                    details={"type": type(content["questions"]).__name__, "file": file_path}
                ))

            # Verificar IDs únicos si existe la lista
            if "questions" in content and isinstance(content["questions"], list):
                questions = content["questions"]
                ids = [q.get("id") for q in questions if isinstance(q, dict) and "id" in q]
                if len(ids) != len(set(ids)):
                    warnings.append(DepurationWarning(
                        type="COHERENCE_DUPLICATE_IDS",
                        severity=SeverityLevel.HIGH,
                        message=f"IDs duplicados en questions",
                        details={"total": len(ids), "unique": len(set(ids)), "file": file_path}
                    ))

        # Coherencia para keywords
        if role == FileRole.KEYWORDS.value:
            if "keywords" in content and not isinstance(content["keywords"], list):
                warnings.append(DepurationWarning(
                    type="COHERENCE_KEYWORDS_TYPE",
                    severity=SeverityLevel.MEDIUM,
                    message=f"Campo 'keywords' debe ser una lista",
                    details={"file": file_path}
                ))

        # Coherencia para aggregation_rules
        if role == FileRole.AGGREGATION_RULES.value:
            # Si hay rules y weights, verificar coherencia
            if "rules" in content and "weights" in content:
                rules = content["rules"]
                weights = content["weights"]
                if isinstance(rules, list) and isinstance(weights, dict):
                    # Verificar que cada rule tenga un weight
                    for rule in rules:
                        if isinstance(rule, dict) and "id" in rule:
                            rule_id = rule["id"]
                            if rule_id not in weights:
                                warnings.append(DepurationWarning(
                                    type="COHERENCE_MISSING_WEIGHT",
                                    severity=SeverityLevel.MEDIUM,
                                    message=f"Rule sin weight: {rule_id}",
                                    details={"rule": rule_id, "file": file_path}
                                ))

        return warnings

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _determine_role(self, file_path: str) -> str:
        """Determina el rol de un archivo desde su path"""
        filename = os.path.basename(file_path).lower()
        dirname = os.path.dirname(file_path).lower()

        # Prioridad 1: Por filename
        if "metadata" in filename:
            return FileRole.METADATA.value
        elif "questions" in filename:
            return FileRole.QUESTIONS.value
        elif "keywords" in filename:
            return FileRole.KEYWORDS.value
        elif "aggregation_rules" in filename or "aggregation" in filename:
            return FileRole.AGGREGATION_RULES.value
        elif "contextual" in filename or "enrichment" in filename:
            return FileRole.CONTEXTUAL_ENRICHMENT.value
        elif "scoring" in filename:
            return FileRole.SCORING_SYSTEM.value
        elif "governance" in filename:
            return FileRole.GOVERNANCE.value

        # Prioridad 2: Por directorio
        if "dimensions" in dirname or "policy_areas" in dirname or "clusters" in dirname:
            # Es un archivo dentro de una entidad, probablemente metadata si no se identificó antes
            return FileRole.METADATA.value
        elif "patterns" in dirname:
            return FileRole.PATTERNS.value
        elif "membership_criteria" in dirname:
            return FileRole.MEMBERSHIP_CRITERIA.value
        elif "entities" in dirname:
            return FileRole.ENTITIES.value
        elif "capabilities" in dirname:
            return FileRole.CAPABILITIES.value
        elif "config" in dirname:
            return FileRole.CONFIG.value
        elif "validations" in dirname:
            return FileRole.VALIDATIONS.value
        elif "semantic" in dirname:
            return FileRole.SEMANTIC.value

        # Prioridad 3: Por extensión y contexto
        if file_path.endswith(".json"):
            # Intentar inferir del contenido
            return FileRole.UNKNOWN.value

        return FileRole.UNKNOWN.value

    def _get_vehicles_for_file(self, file_path: str) -> List[str]:
        """Obtiene vehículos asignados para un archivo"""
        # Buscar en vehicle_assignments
        for pattern, vehicles in self.vehicle_assignments.items():
            if fnmatch.fnmatch(file_path, pattern):
                return vehicles

        # Valores predeterminados por rol
        role = self._determine_role(file_path)
        default_vehicles = {
            FileRole.METADATA.value: ["signal_quality_metrics", "signal_enhancement_integrator"],
            FileRole.QUESTIONS.value: ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"],
            FileRole.KEYWORDS.value: ["signal_registry", "signal_context_scoper"],
        }
        return default_vehicles.get(role, [])

    def _get_consumers_for_file(self, file_path: str) -> List[str]:
        """Obtiene consumidores asignados para un archivo"""
        # Valores predeterminados por fase
        role = self._determine_role(file_path)

        if role in [FileRole.METADATA.value, FileRole.CONFIG.value, FileRole.VALIDATIONS.value]:
            return ["phase0_bootstrap", "phase0_providers", "phase0_wiring_types"]
        elif role in [FileRole.PATTERNS.value, FileRole.MEMBERSHIP_CRITERIA.value]:
            return ["phase1_signal_enrichment", "phase1_cpp_ingestion"]
        elif role in [FileRole.QUESTIONS.value, FileRole.AGGREGATION_RULES.value]:
            return ["phase2_factory_consumer", "phase2_evidence_consumer"]
        else:
            return ["phase1_signal_enrichment"]

    def _get_default_vehicle_assignments(self) -> Dict[str, List[str]]:
        """Asignaciones predeterminadas de vehículos por patrón de archivo"""
        return {
            "*/metadata.json": ["signal_quality_metrics", "signal_enhancement_integrator"],
            "*/questions.json": ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"],
            "*/keywords.json": ["signal_registry", "signal_context_scoper"],
            "*/aggregation_rules.json": ["signal_quality_metrics", "signal_intelligence_layer"],
            "dimensions/*/metadata.json": ["signal_enhancement_integrator"],
            "policy_areas/*/metadata.json": ["signal_enhancement_integrator"],
            "clusters/*/metadata.json": ["signal_enhancement_integrator"],
        }

    def _get_default_consumer_assignments(self) -> Dict[str, List[str]]:
        """Asignaciones predeterminadas de consumidores por patrón de archivo"""
        return {
            "_registry/**/*.json": ["phase0_bootstrap", "phase0_providers"],
            "dimensions/**/*.json": ["phase1_signal_enrichment", "phase1_cpp_ingestion"],
            "policy_areas/**/*.json": ["phase1_signal_enrichment"],
            "clusters/**/*.json": ["phase2_factory_consumer"],
            "questions/**/*.json": ["phase2_evidence_consumer"],
        }


# =============================================================================
# BATCH DEPURATION
# =============================================================================

@dataclass
class BatchDepurationResult:
    """Resultado de depuración en lote"""
    total_files: int = 0
    valid_files: int = 0
    invalid_files: int = 0
    files_with_warnings: int = 0
    results: Dict[str, DepurationResult] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files": self.total_files,
            "valid_files": self.valid_files,
            "invalid_files": self.invalid_files,
            "files_with_warnings": self.files_with_warnings,
            "valid_rate": f"{(self.valid_files / self.total_files * 100):.1f}%" if self.total_files > 0 else "N/A",
            "summary": self.summary
        }


def depurate_all_files(
    base_path: str = "canonic_questionnaire_central",
    output_path: Optional[str] = None,
    fail_on_critical: bool = False
) -> BatchDepurationResult:
    """
    Depura todos los archivos del questionnaire canónico.

    Args:
        base_path: Path al questionnaire canónico
        output_path: Path donde guardar el reporte (opcional)
        fail_on_critical: Si True, falla si hay errores críticos

    Returns:
        BatchDepurationResult con el resumen de depuración
    """
    validator = DepurationValidator(base_path=base_path)

    # Depurar todos los archivos
    all_results = validator.depurate_all()

    # Calcular estadísticas
    batch_result = BatchDepurationResult(
        total_files=len(all_results),
        valid_files=sum(1 for r in all_results.values() if r.valid),
        invalid_files=sum(1 for r in all_results.values() if not r.valid),
        files_with_warnings=sum(1 for r in all_results.values() if r.warnings),
        results=all_results,
        summary={
            "timestamp": datetime.utcnow().isoformat(),
            "base_path": base_path,
            "errors_by_type": _count_errors_by_type(all_results),
            "warnings_by_type": _count_warnings_by_type(all_results),
            "files_by_role": _count_files_by_role(all_results)
        }
    )

    # Guardar reporte si se especificó output_path
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_result.to_dict(), f, indent=2, ensure_ascii=False, default=str)

    # Fallar si se solicitó y hay críticos
    if fail_on_critical and batch_result.invalid_files > 0:
        critical_files = [
            fp for fp, r in all_results.items()
            if not r.valid and r.has_critical_errors
        ]
        raise ValueError(
            f"Depuración falló con {len(critical_files)} archivos críticos: {critical_files[:5]}..."
        )

    return batch_result


def _count_errors_by_type(results: Dict[str, DepurationResult]) -> Dict[str, int]:
    """Cuenta errores por tipo"""
    counts = {}
    for result in results.values():
        for error in result.errors:
            error_type = error.type
            counts[error_type] = counts.get(error_type, 0) + 1
    return counts


def _count_warnings_by_type(results: Dict[str, DepurationResult]) -> Dict[str, int]:
    """Cuenta warnings por tipo"""
    counts = {}
    for result in results.values():
        for warning in result.warnings:
            warning_type = warning.type
            counts[warning_type] = counts.get(warning_type, 0) + 1
    return counts


def _count_files_by_role(results: Dict[str, DepurationResult]) -> Dict[str, int]:
    """Cuenta archivos por rol"""
    counts = {}
    for result in results.values():
        role = result.role or "unknown"
        counts[role] = counts.get(role, 0) + 1
    return counts
