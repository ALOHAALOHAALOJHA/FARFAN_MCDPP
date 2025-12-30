#!/usr/bin/env python3
"""
VALIDATOR GOVERNANCE LAYER (VGL) - Meta-epistemic Control
==========================================================

N0 — VALIDATOR GOVERNANCE (Meta-epistemic)
Función: Decidir qué correcciones están permitidas, bajo qué condiciones,
con qué grado de automatización, y qué queda protegido.

Este módulo evita que el validador se convierta en un "formatter agresivo"
que aplane la diversidad epistemológica de los contratos.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import json


class CorrectionClass(Enum):
    """Clasificación de correcciones según su impacto epistemológico"""
    STRUCTURAL = "STRUCTURAL"      # Infraestructura, sin impacto semántico
    EPISTEMIC = "EPISTEMIC"        # Afecta epistemología pero no introduce supuestos nuevos
    SEMANTIC = "SEMANTIC"          # Afecta significado sustantivo


class AutomationLevel(Enum):
    """Nivel de automatización permitido"""
    AUTO = "AUTO"                  # Ejecución automática sin intervención
    SEMI_AUTO = "SEMI_AUTO"        # Requiere validación de contexto
    MANUAL = "MANUAL"              # Requiere análisis experto


class RiskLevel(Enum):
    """Nivel de riesgo epistemológico"""
    LOW = "LOW"                    # Sin riesgo de aplanamiento
    MEDIUM = "MEDIUM"              # Riesgo controlado con salvaguardas
    HIGH = "HIGH"                  # Riesgo alto, requiere revisión


@dataclass
class CorrectionRule:
    """Regla de corrección con metadata de governance"""
    rule_id: str
    scope: str  # "contract" | "method" | "phase" | "section"
    risk_level: RiskLevel
    correction_class: CorrectionClass
    automation_level: AutomationLevel
    requires_context: bool
    can_modify_core_semantics: bool
    description: str
    allowed_actions: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    protected_fields: List[str] = field(default_factory=list)


@dataclass
class CorrectionLog:
    """Registro de corrección aplicada"""
    rule_id: str
    contract_name: str
    correction_class: CorrectionClass
    automation_level: AutomationLevel
    fields_modified: List[str]
    epistemic_impact: str  # "NONE" | "MINOR" | "MODERATE" | "MAJOR"
    timestamp: str
    requires_epistemic_review: bool = False


class ValidatorGovernanceLayer:
    """
    Capa de governance que controla qué correcciones pueden aplicarse
    y bajo qué condiciones.
    """
    
    # Meta-regla suprema
    META_RULE = {
        "id": "NO_EPISTEMIC_FLATTENING",
        "statement": "The validator SHALL NOT reduce epistemological diversity across contracts through automatic corrections.",
        "enforced_by": [
            "N1_protection_guard",
            "gate_logic_guard",
            "asymmetry_guard",
            "argumentative_role_guard"
        ],
        "violation_action": "HARD_FAIL"
    }
    
    def __init__(self):
        """Inicializa el VGL con reglas de corrección y guards"""
        self.correction_rules = self._initialize_correction_rules()
        self.guards = self._initialize_guards()
        self.correction_log: List[CorrectionLog] = []
    
    def _initialize_correction_rules(self) -> Dict[str, CorrectionRule]:
        """Define todas las reglas de corrección con su metadata"""
        rules = {}
        
        # FASE 1: Correcciones estructurales (AUTO permitido)
        rules["incorrect_dependencies"] = CorrectionRule(
            rule_id="incorrect_dependencies",
            scope="contract",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Corrige dependencies usando nombres de fases",
            allowed_actions=["SET_DEPENDENCIES_BY_PHASE"],
            forbidden_actions=["MODIFY_PHASE_STRUCTURE"]
        )
        
        rules["method_count_mismatch"] = CorrectionRule(
            rule_id="method_count_mismatch",
            scope="contract",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Recalcula method_count desde suma de métodos",
            allowed_actions=["RECALCULATE_METHOD_COUNT"],
            forbidden_actions=["MODIFY_METHODS"]
        )
        
        rules["missing_cross_layer_fusion"] = CorrectionRule(
            rule_id="missing_cross_layer_fusion",
            scope="contract",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Agrega relaciones faltantes en cross_layer_fusion",
            allowed_actions=["ADD_MISSING_RELATIONS"],
            forbidden_actions=["MODIFY_EXISTING_RELATIONS"]
        )
        
        rules["missing_placeholders"] = CorrectionRule(
            rule_id="missing_placeholders",
            scope="section",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Agrega placeholders estándar a S1_verdict",
            allowed_actions=["ADD_STANDARD_PLACEHOLDERS"],
            forbidden_actions=["MODIFY_EXISTING_PLACEHOLDERS"]
        )
        
        rules["r1_sources_issue"] = CorrectionRule(
            rule_id="r1_sources_issue",
            scope="section",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Sincroniza R1.sources con phase_A provides",
            allowed_actions=["SYNC_R1_SOURCES"],
            forbidden_actions=["MODIFY_PHASE_A_METHODS"]
        )
        
        rules["incorrect_requires"] = CorrectionRule(
            rule_id="incorrect_requires",
            scope="method",
            risk_level=RiskLevel.LOW,
            correction_class=CorrectionClass.STRUCTURAL,
            automation_level=AutomationLevel.AUTO,
            requires_context=False,
            can_modify_core_semantics=False,
            description="Corrige requires de métodos N2 a raw_facts",
            allowed_actions=["SET_REQUIRES_RAW_FACTS"],
            forbidden_actions=["MODIFY_METHOD_LOGIC"]
        )
        
        # FASE 2: Correcciones por tipo (SEMI_AUTO con validación)
        rules["fusion_strategy_mismatch"] = CorrectionRule(
            rule_id="fusion_strategy_mismatch",
            scope="contract",
            risk_level=RiskLevel.MEDIUM,
            correction_class=CorrectionClass.EPISTEMIC,
            automation_level=AutomationLevel.SEMI_AUTO,
            requires_context=True,
            can_modify_core_semantics=False,
            description="Corrige fusion strategies según contract_type",
            allowed_actions=["SET_FUSION_BY_TYPE"],
            forbidden_actions=["INFER_CONTRACT_TYPE", "MODIFY_CONTRACT_TYPE"],
            required_fields=["identity.contract_type"],
            protected_fields=["identity.contract_type"]
        )
        
        rules["r2_merge_strategy_issue"] = CorrectionRule(
            rule_id="r2_merge_strategy_issue",
            scope="section",
            risk_level=RiskLevel.MEDIUM,
            correction_class=CorrectionClass.EPISTEMIC,
            automation_level=AutomationLevel.SEMI_AUTO,
            requires_context=True,
            can_modify_core_semantics=False,
            description="Corrige R2.merge_strategy según contract_type",
            allowed_actions=["SET_R2_MERGE_BY_TYPE"],
            forbidden_actions=["INFER_CONTRACT_TYPE"],
            required_fields=["identity.contract_type"],
            protected_fields=["identity.contract_type"]
        )
        
        # FASE 3: Correcciones semánticas (MANUAL o SEMI_AUTO con salvaguardas)
        rules["missing_asymmetry"] = CorrectionRule(
            rule_id="missing_asymmetry",
            scope="phase",
            risk_level=RiskLevel.MEDIUM,
            correction_class=CorrectionClass.EPISTEMIC,
            automation_level=AutomationLevel.SEMI_AUTO,
            requires_context=True,
            can_modify_core_semantics=False,
            description="Agrega asymmetry_principle con dominio específico",
            allowed_actions=["ADD_ASYMMETRY_SKELETON"],
            forbidden_actions=["USE_GENERIC_TEXT_ONLY"],
            required_fields=["asymmetry_domain_note"],
            protected_fields=["phase_C.methods", "gate_logic"]
        )
        
        rules["missing_argumentative_roles"] = CorrectionRule(
            rule_id="missing_argumentative_roles",
            scope="section",
            risk_level=RiskLevel.MEDIUM,
            correction_class=CorrectionClass.EPISTEMIC,
            automation_level=AutomationLevel.SEMI_AUTO,
            requires_context=True,
            can_modify_core_semantics=False,
            description="Agrega roles argumentativos faltantes sin sobrescribir",
            allowed_actions=["ADD_MISSING_ROLES"],
            forbidden_actions=["OVERWRITE_EXISTING_ROLES", "MODIFY_NARRATIVE_WEIGHT"],
            required_fields=["identity.contract_type"],
            protected_fields=["existing_roles"]
        )
        
        rules["gate_logic_issues"] = CorrectionRule(
            rule_id="gate_logic_issues",
            scope="method",
            risk_level=RiskLevel.HIGH,
            correction_class=CorrectionClass.SEMANTIC,
            automation_level=AutomationLevel.MANUAL,
            requires_context=True,
            can_modify_core_semantics=True,
            description="Corrige estructura de gate_logic sin modificar semántica",
            allowed_actions=[
                "ADD_MISSING_CONDITION_STRUCTURE",
                "NORMALIZE_CONFIDENCE_MULTIPLIER_RANGE"
            ],
            forbidden_actions=[
                "MODIFY_TRIGGER_SEMANTICS",
                "RENAME_EXISTING_TRIGGERS",
                "DELETE_CONDITIONS"
            ],
            protected_fields=["trigger", "scope", "semantic_content"]
        )
        
        # ZONA ROJA: No corregir automáticamente
        rules["empty_phase_A"] = CorrectionRule(
            rule_id="empty_phase_A",
            scope="phase",
            risk_level=RiskLevel.HIGH,
            correction_class=CorrectionClass.SEMANTIC,
            automation_level=AutomationLevel.MANUAL,
            requires_context=True,
            can_modify_core_semantics=True,
            description="NO CORREGIR: Requiere análisis epistemológico específico",
            allowed_actions=["FLAG_FOR_REVIEW"],
            forbidden_actions=["ADD_METHOD", "INFER_METHOD"],
            protected_fields=["phase_A.methods"]
        )
        
        return rules
    
    def _initialize_guards(self) -> Dict[str, Dict]:
        """Inicializa guards que protegen contra aplanamiento"""
        guards = {}
        
        # Guard 1: Contract-Type Guard
        guards["contract_type_guard"] = {
            "description": "Blocks corrections that assume a contract type without explicit identity.contract_type",
            "trigger": "correction.requires_contract_type == true",
            "condition": "identity.contract_type IS NULL",
            "action": "BLOCK_CORRECTION",
            "severity": "CRITICAL"
        }
        
        # Guard 2: N1 Protection Rule
        guards["N1_protection_guard"] = {
            "description": "Prevents automatic insertion of N1 methods",
            "trigger": "correction.targets == 'phase_A.methods'",
            "condition": "correction.action == 'ADD_METHOD'",
            "action": "BLOCK_AND_FLAG",
            "flag": "requires_epistemic_completion",
            "severity": "CRITICAL"
        }
        
        # Guard 3: Gate Logic Guard
        guards["gate_logic_guard"] = {
            "description": "Ensures gate_logic corrections are structural only",
            "trigger": "correction.targets == 'gate_logic'",
            "allowed_actions": [
                "ADD_MISSING_CONDITION_STRUCTURE",
                "NORMALIZE_CONFIDENCE_MULTIPLIER_RANGE"
            ],
            "forbidden_actions": [
                "MODIFY_TRIGGER_SEMANTICS",
                "RENAME_EXISTING_TRIGGERS",
                "DELETE_CONDITIONS"
            ],
            "action_on_violation": "BLOCK_CORRECTION",
            "severity": "CRITICAL"
        }
        
        # Guard 4: Asymmetry Semantic Guard
        guards["asymmetry_guard"] = {
            "description": "Prevents generic asymmetry text without domain anchoring",
            "trigger": "correction.rule_id == 'missing_asymmetry'",
            "condition": "asymmetry_domain_note IS NULL",
            "action": "DOWNGRADE_AUTOMATION",
            "from": "AUTO",
            "to": "SEMI_AUTO",
            "required_fields": ["asymmetry_domain_note"]
        }
        
        # Guard 5: Argumentative Role Guard
        guards["argumentative_role_guard"] = {
            "description": "Prevents overwriting existing argumentative roles",
            "trigger": "correction.rule_id == 'missing_argumentative_roles'",
            "constraints": {
                "overwrite_existing_roles": False,
                "modify_narrative_weight": False
            },
            "action_on_violation": "BLOCK_CORRECTION",
            "severity": "HIGH"
        }
        
        return guards
    
    def can_apply_correction(
        self,
        rule_id: str,
        contract: Dict,
        correction_action: str,
        context: Optional[Dict] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Determina si una corrección puede aplicarse.
        
        Returns:
            (allowed, reason, guard_triggered)
        """
        if rule_id not in self.correction_rules:
            return False, f"Unknown correction rule: {rule_id}", None
        
        rule = self.correction_rules[rule_id]
        
        # Verificar meta-regla suprema
        if rule.can_modify_core_semantics and rule.automation_level == AutomationLevel.AUTO:
            return False, "Violates NO_EPISTEMIC_FLATTENING: AUTO corrections cannot modify core semantics", "META_RULE"
        
        # Verificar guards específicos
        guard_result = self._check_guards(rule_id, contract, correction_action, context)
        if not guard_result[0]:
            return False, guard_result[1], guard_result[2]
        
        # Verificar campos requeridos
        if rule.requires_context:
            missing_fields = []
            for field_path in rule.required_fields:
                if not self._path_exists(contract, field_path):
                    missing_fields.append(field_path)
            
            if missing_fields:
                return False, f"Missing required context fields: {missing_fields}", "CONTEXT_GUARD"
        
        # Verificar acción permitida
        if correction_action not in rule.allowed_actions:
            return False, f"Action '{correction_action}' not allowed for rule '{rule_id}'", "ACTION_GUARD"
        
        # Verificar acción prohibida
        if correction_action in rule.forbidden_actions:
            return False, f"Action '{correction_action}' is forbidden for rule '{rule_id}'", "FORBIDDEN_ACTION"
        
        return True, None, None
    
    def _check_guards(
        self,
        rule_id: str,
        contract: Dict,
        correction_action: str,
        context: Optional[Dict]
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """Verifica todos los guards aplicables"""
        
        # Guard 1: Contract-Type Guard
        if rule_id in ["fusion_strategy_mismatch", "r2_merge_strategy_issue", "missing_argumentative_roles"]:
            contract_type = self._get_path(contract, "identity.contract_type")
            if not contract_type:
                return False, "Contract type guard: identity.contract_type must be explicit", "contract_type_guard"
        
        # Guard 2: N1 Protection Rule
        if rule_id == "empty_phase_A" and correction_action == "ADD_METHOD":
            return False, "N1 protection guard: Cannot automatically add N1 methods", "N1_protection_guard"
        
        # Guard 3: Gate Logic Guard
        if rule_id == "gate_logic_issues":
            if correction_action in ["MODIFY_TRIGGER_SEMANTICS", "RENAME_EXISTING_TRIGGERS", "DELETE_CONDITIONS"]:
                return False, "Gate logic guard: Cannot modify trigger semantics", "gate_logic_guard"
        
        # Guard 4: Asymmetry Guard
        if rule_id == "missing_asymmetry":
            if not context or "asymmetry_domain_note" not in context:
                return False, "Asymmetry guard: Requires asymmetry_domain_note", "asymmetry_guard"
        
        # Guard 5: Argumentative Role Guard
        if rule_id == "missing_argumentative_roles":
            existing_roles = self._get_path(contract, "human_answer_structure.argumentative_roles", {})
            if correction_action == "OVERWRITE_EXISTING_ROLES" and existing_roles:
                return False, "Argumentative role guard: Cannot overwrite existing roles", "argumentative_role_guard"
        
        return True, None, None
    
    def log_correction(
        self,
        rule_id: str,
        contract_name: str,
        fields_modified: List[str],
        epistemic_impact: str = "NONE"
    ):
        """Registra una corrección aplicada"""
        rule = self.correction_rules[rule_id]
        
        log_entry = CorrectionLog(
            rule_id=rule_id,
            contract_name=contract_name,
            correction_class=rule.correction_class,
            automation_level=rule.automation_level,
            fields_modified=fields_modified,
            epistemic_impact=epistemic_impact,
            timestamp=self._get_timestamp(),
            requires_epistemic_review=(epistemic_impact != "NONE")
        )
        
        self.correction_log.append(log_entry)
    
    def get_epistemic_review_hooks(self, contract_name: str) -> Dict:
        """Genera hooks de revisión epistemológica para un contrato"""
        contract_logs = [log for log in self.correction_log if log.contract_name == contract_name]
        
        auto_corrected = [log.rule_id for log in contract_logs if log.automation_level == AutomationLevel.AUTO]
        protected = ["contract_type", "phase_A.methods", "gate_logic", "core_methods"]
        review_required = [log.rule_id for log in contract_logs if log.requires_epistemic_review]
        
        return {
            "auto_corrected_fields": auto_corrected,
            "protected_fields": protected,
            "review_required_for": review_required
        }
    
    def _path_exists(self, contract: Dict, path: str) -> bool:
        """Verifica si existe un path en el contrato"""
        keys = path.split(".")
        value = contract
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return False
        return True
    
    def _get_path(self, contract: Dict, path: str, default=None):
        """Obtiene valor de un path"""
        keys = path.split(".")
        value = contract
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp ISO"""
        from datetime import datetime
        return datetime.now().isoformat() + "Z"
    
    def export_governance_report(self, output_path: str):
        """Exporta reporte de governance"""
        report = {
            "meta_rule": self.META_RULE,
            "correction_rules": {
                rule_id: {
                    "rule_id": rule.rule_id,
                    "correction_class": rule.correction_class.value,
                    "automation_level": rule.automation_level.value,
                    "risk_level": rule.risk_level.value,
                    "can_modify_core_semantics": rule.can_modify_core_semantics
                }
                for rule_id, rule in self.correction_rules.items()
            },
            "guards": self.guards,
            "correction_log": [
                {
                    "rule_id": log.rule_id,
                    "contract_name": log.contract_name,
                    "correction_class": log.correction_class.value,
                    "epistemic_impact": log.epistemic_impact,
                    "requires_epistemic_review": log.requires_epistemic_review,
                    "timestamp": log.timestamp
                }
                for log in self.correction_log
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


if __name__ == "__main__":
    # Ejemplo de uso
    vgl = ValidatorGovernanceLayer()
    
    # Test: Verificar si puede aplicar corrección
    test_contract = {
        "identity": {
            "contract_type": "TYPE_E"
        },
        "method_binding": {
            "execution_phases": {
                "phase_A_construction": {
                    "methods": []
                }
            }
        }
    }
    
    # Test 1: Corrección estructural permitida
    allowed, reason, guard = vgl.can_apply_correction(
        "incorrect_dependencies",
        test_contract,
        "SET_DEPENDENCIES_BY_PHASE"
    )
    print(f"Test 1 - incorrect_dependencies: {allowed} ({reason})")
    
    # Test 2: Corrección que requiere tipo (permitida porque tiene TYPE_E)
    allowed, reason, guard = vgl.can_apply_correction(
        "fusion_strategy_mismatch",
        test_contract,
        "SET_FUSION_BY_TYPE"
    )
    print(f"Test 2 - fusion_strategy_mismatch: {allowed} ({reason})")
    
    # Test 3: N1 protection (bloqueada)
    allowed, reason, guard = vgl.can_apply_correction(
        "empty_phase_A",
        test_contract,
        "ADD_METHOD"
    )
    print(f"Test 3 - empty_phase_A ADD_METHOD: {allowed} ({reason}) - Guard: {guard}")
    
    # Test 4: Asymmetry sin domain_note (bloqueada)
    allowed, reason, guard = vgl.can_apply_correction(
        "missing_asymmetry",
        test_contract,
        "ADD_ASYMMETRY_SKELETON",
        context={}
    )
    print(f"Test 4 - missing_asymmetry sin domain_note: {allowed} ({reason}) - Guard: {guard}")
    
    # Exportar reporte
    vgl.export_governance_report("validator_governance_report.json")
    print("\n✅ Governance report exported")


