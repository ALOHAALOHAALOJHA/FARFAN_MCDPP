#!/usr/bin/env python3
"""
Question Atomization Script for CQC Restructure.

SPEC REFERENCE: Section 4.3, 9.1
PURPOSE: Transform questionnaire_monolith.json into atomic question files

Input: questionnaire_monolith.json (300 questions embedded)
Output: dimensions/DIM*/questions/Q*.json (300 individual files)

Schema per SPEC 4.3:
- question_id, dimension_id, policy_area_id, cluster_id
- identifiers (base_slot, legacy_id, canonical_notation)
- text (es, en)
- expected_elements
- references (pattern_refs, keyword_refs, mc_refs, entity_refs, cc_refs)
- scoring (modality, max_score, threshold, weights)
- method_binding
- failure_contract
- interdependencies
- context_requirements
- metadata
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CQC_ROOT = Path(__file__).parent.parent
DIMENSIONS = CQC_ROOT / "dimensions"


# Dimension mapping based on base question number (Q001-Q030 base)
DIMENSION_MAPPING = {
    range(1, 6): "DIM01",    # Q001-Q005 -> DIM01 INSUMOS
    range(6, 11): "DIM02",   # Q006-Q010 -> DIM02 ACTIVIDADES
    range(11, 16): "DIM03",  # Q011-Q015 -> DIM03 PRODUCTOS
    range(16, 21): "DIM04",  # Q016-Q020 -> DIM04 RESULTADOS
    range(21, 26): "DIM05",  # Q021-Q025 -> DIM05 IMPACTOS
    range(26, 31): "DIM06",  # Q026-Q030 -> DIM06 CAUSALIDAD
}

DIMENSION_NAMES = {
    "DIM01": "INSUMOS",
    "DIM02": "ACTIVIDADES",
    "DIM03": "PRODUCTOS",
    "DIM04": "RESULTADOS",
    "DIM05": "IMPACTOS",
    "DIM06": "CAUSALIDAD",
}

# Cluster mapping
CLUSTER_MAPPING = {
    "PA02": "CL01", "PA05": "CL01", "PA08": "CL01",  # Seguridad y Paz
    "PA01": "CL02", "PA03": "CL02", "PA06": "CL02", "PA07": "CL02",  # Grupos Poblacionales
    "PA04": "CL03",  # Territorio y Ambiente
    "PA09": "CL04", "PA10": "CL04",  # Derechos Sociales y Crisis
}


def get_dimension_from_base_question(base_q: int) -> str:
    """Get dimension ID from base question number (1-30)."""
    for q_range, dim_id in DIMENSION_MAPPING.items():
        if base_q in q_range:
            return dim_id
    return "DIM01"


def get_policy_area_from_question_id(q_id: str) -> str:
    """Extract policy area from question ID (Q001-Q030 -> PA01, Q031-Q060 -> PA02, etc.)."""
    match = re.match(r'Q(\d+)', q_id)
    if match:
        q_num = int(match.group(1))
        pa_num = ((q_num - 1) // 30) + 1
        if 1 <= pa_num <= 10:
            return f"PA{pa_num:02d}"
    return "PA01"


def get_base_question_number(q_id: str) -> int:
    """Get base question number (1-30) from question ID."""
    match = re.match(r'Q(\d+)', q_id)
    if match:
        q_num = int(match.group(1))
        return ((q_num - 1) % 30) + 1
    return 1


class QuestionAtomizer:
    """Atomizes questionnaire monolith into individual question files."""
    
    def __init__(self):
        self.questions: Dict[str, Dict] = {}
        self.pattern_registry: Dict[str, Any] = {}
        self.stats = {
            "questions_loaded": 0,
            "questions_atomized": 0,
            "dimensions_created": set(),
            "errors": []
        }
    
    def load_monolith(self) -> None:
        """Load questionnaire monolith."""
        monolith_path = CQC_ROOT / "questionnaire_monolith.json"
        
        if not monolith_path.exists():
            raise FileNotFoundError(f"Monolith not found: {monolith_path}")
        
        with open(monolith_path) as f:
            data = json.load(f)
        
        # Handle different monolith structures
        if "blocks" in data:
            questions = data["blocks"].get("micro_questions", [])
        elif "micro_questions" in data:
            questions = data["micro_questions"]
        elif isinstance(data, list):
            questions = data
        else:
            questions = data.get("questions", [])
        
        for q in questions:
            q_id = q.get("question_id", "")
            if q_id:
                self.questions[q_id] = q
        
        self.stats["questions_loaded"] = len(self.questions)
        logger.info(f"Loaded {len(self.questions)} questions from monolith")
    
    def load_pattern_registry(self) -> None:
        """Load pattern registry for reference extraction."""
        pattern_index = CQC_ROOT / "_registry" / "patterns" / "index.json"
        
        if pattern_index.exists():
            with open(pattern_index) as f:
                data = json.load(f)
                self.pattern_registry = data.get("patterns", {})
            logger.info(f"Loaded {len(self.pattern_registry)} patterns")
        else:
            logger.warning("Pattern index not found, proceeding without pattern refs")
    
    def _extract_pattern_refs(self, q_id: str) -> List[str]:
        """Extract pattern references for a question."""
        refs = []
        for p_id, p in self.pattern_registry.items():
            bindings = p.get("bindings", {})
            if q_id in bindings.get("applies_to_questions", []):
                refs.append(p_id)
        return refs
    
    def _extract_mc_refs(self, dimension_id: str, expected_elements: List) -> List[str]:
        """Infer membership criteria refs from dimension and expected elements."""
        mc_refs = []
        
        # Map dimensions to likely MCs
        dim_mc_map = {
            "DIM01": ["MC01", "MC02", "MC03"],  # Structural, Quantitative, Normative
            "DIM02": ["MC04", "MC05"],          # Hierarchy, Financial
            "DIM03": ["MC02", "MC05"],          # Quantitative, Financial
            "DIM04": ["MC02", "MC07"],          # Quantitative, Temporal
            "DIM05": ["MC02", "MC08"],          # Quantitative, Causal
            "DIM06": ["MC08", "MC10"],          # Causal, Semantic
        }
        
        mc_refs = dim_mc_map.get(dimension_id, ["MC01", "MC02"])
        
        # Add MC06 if population-related elements
        for ee in expected_elements:
            ee_type = ee.get("type", "") if isinstance(ee, dict) else str(ee)
            if any(kw in ee_type.lower() for kw in ["poblacion", "genero", "desagregacion", "diferencial"]):
                if "MC06" not in mc_refs:
                    mc_refs.append("MC06")
        
        return mc_refs
    
    def _extract_cc_refs(self, policy_area: str, text: str) -> List[str]:
        """Infer cross-cutting theme refs from policy area and text."""
        cc_refs = []
        
        # PA to CC mapping
        pa_cc_map = {
            "PA01": ["CC_PERSPECTIVA_GENERO", "CC_ENFOQUE_DIFERENCIAL"],
            "PA02": ["CC_COHERENCIA_NORMATIVA"],
            "PA03": ["CC_ENFOQUE_DIFERENCIAL"],
            "PA04": ["CC_SOSTENIBILIDAD_PRESUPUESTAL"],
            "PA05": ["CC_ENFOQUE_DIFERENCIAL", "CC_COHERENCIA_NORMATIVA"],
            "PA06": ["CC_ENFOQUE_DIFERENCIAL"],
            "PA07": ["CC_ENFOQUE_DIFERENCIAL", "CC_PARTICIPACION_CIUDADANA"],
            "PA08": ["CC_COHERENCIA_NORMATIVA"],
            "PA09": ["CC_ENFOQUE_DIFERENCIAL"],
            "PA10": ["CC_ENFOQUE_DIFERENCIAL", "CC_INTEROPERABILIDAD"],
        }
        
        cc_refs = pa_cc_map.get(policy_area, [])
        
        # Add based on text content
        text_lower = text.lower() if text else ""
        if "seguimiento" in text_lower or "monitoreo" in text_lower:
            if "CC_MECANISMOS_SEGUIMIENTO" not in cc_refs:
                cc_refs.append("CC_MECANISMOS_SEGUIMIENTO")
        if "territorial" in text_lower or "rural" in text_lower:
            if "CC_ENTORNO_TERRITORIAL" not in cc_refs:
                cc_refs.append("CC_ENTORNO_TERRITORIAL")
        
        return cc_refs
    
    def atomize(self) -> None:
        """Atomize all questions into individual files."""
        for q_id, q in self.questions.items():
            try:
                self._atomize_question(q_id, q)
                self.stats["questions_atomized"] += 1
            except Exception as e:
                self.stats["errors"].append(f"{q_id}: {str(e)}")
                logger.error(f"Error atomizing {q_id}: {e}")
        
        logger.info(f"Atomized {self.stats['questions_atomized']} questions")
        logger.info(f"Dimensions: {sorted(self.stats['dimensions_created'])}")
        if self.stats["errors"]:
            logger.warning(f"Errors: {len(self.stats['errors'])}")
    
    def _atomize_question(self, q_id: str, q: Dict) -> None:
        """Atomize a single question to its dimension folder."""
        # Determine dimension and policy area
        base_q = get_base_question_number(q_id)
        dimension_id = q.get("dimension_id") or get_dimension_from_base_question(base_q)
        policy_area_id = q.get("policy_area_id") or get_policy_area_from_question_id(q_id)
        cluster_id = q.get("cluster_id") or CLUSTER_MAPPING.get(policy_area_id, "CL01")
        
        # Get dimension folder
        dim_name = DIMENSION_NAMES.get(dimension_id, "UNKNOWN")
        dim_folder = DIMENSIONS / f"{dimension_id}_{dim_name}" / "questions"
        dim_folder.mkdir(parents=True, exist_ok=True)
        
        self.stats["dimensions_created"].add(dimension_id)
        
        # Extract text
        text_raw = q.get("text", "")
        if isinstance(text_raw, dict):
            text_es = text_raw.get("es", "")
            text_en = text_raw.get("en", "")
        else:
            text_es = str(text_raw)
            text_en = ""
        
        # Build expected elements
        expected_elements = q.get("expected_elements", [])
        
        # Build references
        pattern_refs = self._extract_pattern_refs(q_id)
        mc_refs = self._extract_mc_refs(dimension_id, expected_elements)
        cc_refs = self._extract_cc_refs(policy_area_id, text_es)
        
        # Build scoring
        scoring_raw = q.get("scoring", {})
        if isinstance(scoring_raw, dict):
            modality = scoring_raw.get("modality", q.get("scoring_modality", "TYPE_A"))
        else:
            modality = q.get("scoring_modality", "TYPE_A")
        
        # Build atomic question per SPEC 4.3
        atomic_q = {
            "$schema": "../../question_schema.json",
            "_schema_version": "2.0.0",
            
            "question_id": q_id,
            "dimension_id": dimension_id,
            "policy_area_id": policy_area_id,
            "cluster_id": cluster_id,
            
            "identifiers": {
                "base_slot": q.get("base_slot", f"D{dimension_id[-1]}-Q{base_q}"),
                "legacy_id": q.get("legacy_id", q_id),
                "canonical_notation": f"{dimension_id}.{policy_area_id}.{q_id}"
            },
            
            "text": {
                "es": text_es,
                "en": text_en
            },
            
            "expected_elements": expected_elements,
            
            "references": {
                "pattern_refs": pattern_refs,
                "keyword_refs": [],  # Will be populated by build script
                "membership_criteria_refs": mc_refs,
                "entity_refs": [],  # Will be populated by build script
                "cross_cutting_refs": cc_refs
            },
            
            "scoring": {
                "modality": modality,
                "max_score": 3,
                "threshold": 0.70,
                "weights": {
                    "expected_elements": 0.30,
                    "pattern_matches": 0.25,
                    "keyword_density": 0.10,
                    "membership_criteria": 0.20,
                    "entity_presence": 0.05,
                    "cross_cutting_alignment": 0.10
                }
            },
            
            "method_binding": q.get("method_binding", {
                "executor_contract_version": "v4",
                "executor_contract_path": f"executor_contracts/specialized/{q_id}.v4.json",
                "methods": q.get("method_sets", []),
                "fallback_method": "GenericQuestionProcessor.process"
            }),
            
            "failure_contract": q.get("failure_contract", {
                "abort_if": ["missing_required_element", "section_not_found"],
                "emit_code": f"ABORT-{q_id}-REQ",
                "fallback_score": 0.0
            }),
            
            "interdependencies": {
                "informs": [],
                "informed_by": [],
                "coherence_check_with": [],
                "validates_with": []
            },
            
            "context_requirements": {
                "preferred_sections": self._get_preferred_sections(dimension_id),
                "acceptable_sections": ["INTRODUCCION", "CONTEXTO"],
                "excluded_sections": ["ANEXOS", "GLOSARIO"]
            },
            
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "version": "2.0.0",
                "author": "atomize_questions.py",
                "validated": False,
                "test_coverage": 0.0
            }
        }
        
        # Write atomic question
        q_file = dim_folder / f"{q_id}.json"
        with open(q_file, "w") as f:
            json.dump(atomic_q, f, indent=2, ensure_ascii=False)
    
    def _get_preferred_sections(self, dimension_id: str) -> List[str]:
        """Get preferred document sections for a dimension."""
        section_map = {
            "DIM01": ["DIAGNOSTICO", "LINEA_BASE"],
            "DIM02": ["ESTRATEGICO", "PROGRAMAS"],
            "DIM03": ["PRODUCTOS", "METAS", "PLAN_INDICATIVO"],
            "DIM04": ["RESULTADOS", "INDICADORES"],
            "DIM05": ["IMPACTOS", "OBJETIVOS"],
            "DIM06": ["CAUSALIDAD", "TEORIA_CAMBIO", "ESTRATEGICO"],
        }
        return section_map.get(dimension_id, ["DIAGNOSTICO"])
    
    def run(self) -> Dict[str, Any]:
        """Execute full atomization."""
        logger.info("Starting question atomization...")
        
        self.load_monolith()
        self.load_pattern_registry()
        self.atomize()
        
        return {
            "questions_loaded": self.stats["questions_loaded"],
            "questions_atomized": self.stats["questions_atomized"],
            "dimensions_created": sorted(self.stats["dimensions_created"]),
            "errors": self.stats["errors"]
        }


def main():
    atomizer = QuestionAtomizer()
    result = atomizer.run()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
