"""
CQC Loader with Backward Compatibility.

Provides a unified interface for loading CQC resources
from both legacy monolith structure and new modular structure.
"""

import warnings
from pathlib import Path
from typing import Optional, Dict, List, Any
import json


class CQCLoader:
    """Loader con backward compatibility para CQC."""
    
    def __init__(self, cqc_root: Optional[Path] = None):
        if cqc_root is None:
            cqc_root = Path(__file__).parent.parent
        self.cqc_root = Path(cqc_root)
        self._structure_version = self._detect_structure()
        
        if self._structure_version == "legacy_monolith":
            warnings.warn(
                "Using legacy monolith structure. This is deprecated. "
                "Migrate to modular structure using: python _scripts/build_cqc_views.py "
                "See SPECIFICATION.md for details.",
                DeprecationWarning,
                stacklevel=2
            )
        
        # Caches
        self._questionnaire_cache: Optional[Dict] = None
        self._patterns_cache: Optional[Dict] = None
        self._keywords_cache: Optional[Dict] = None
        self._membership_criteria_cache: Optional[Dict] = None
        self._cross_cutting_cache: Optional[Dict] = None
    
    def _detect_structure(self) -> str:
        """Detecta versión de estructura CQC."""
        if (self.cqc_root / "_registry").exists() and (self.cqc_root / "_views").exists():
            return "modular_v2"
        elif (self.cqc_root / "questionnaire_monolith.json").exists():
            return "legacy_monolith"
        else:
            raise ValueError(f"Unknown CQC structure at {self.cqc_root}")
    
    @property
    def is_modular(self) -> bool:
        return self._structure_version.startswith("modular")
    
    @property
    def structure_version(self) -> str:
        return self._structure_version
    
    def load_questionnaire(self) -> Dict[str, Any]:
        """Carga questionnaire con compatibilidad."""
        if self._questionnaire_cache is not None:
            return self._questionnaire_cache
        
        if self.is_modular:
            self._questionnaire_cache = self._load_modular_questionnaire()
        else:
            self._questionnaire_cache = self._load_legacy_questionnaire()
        
        return self._questionnaire_cache
    
    def _load_modular_questionnaire(self) -> Dict[str, Any]:
        """Carga desde estructura modular."""
        # Preferir build artifact si existe
        build_monolith = self.cqc_root / "_build" / "questionnaire_monolith.json"
        if build_monolith.exists():
            with open(build_monolith) as f:
                return json.load(f)
        
        # Fallback: usar vista plana
        flat_view = self.cqc_root / "_views" / "questionnaire_flat.json"
        if flat_view.exists():
            with open(flat_view) as f:
                data = json.load(f)
                return {
                    "_structure_version": "modular_v2",
                    "_from_view": True,
                    "blocks": {
                        "micro_questions": data.get("questions", [])
                    }
                }
        
        # Last resort: construir en memoria
        return self._build_questionnaire_in_memory()
    
    def _load_legacy_questionnaire(self) -> Dict[str, Any]:
        """Carga desde monolito legacy."""
        monolith = self.cqc_root / "questionnaire_monolith.json"
        with open(monolith) as f:
            return json.load(f)
    
    def _build_questionnaire_in_memory(self) -> Dict[str, Any]:
        """Construye questionnaire desde archivos modulares."""
        questions = []
        dimensions_dir = self.cqc_root / "dimensions"
        
        if dimensions_dir.exists():
            for dim_folder in dimensions_dir.iterdir():
                if not dim_folder.is_dir():
                    continue
                
                questions_file = dim_folder / "questions.json"
                if questions_file.exists():
                    with open(questions_file) as f:
                        data = json.load(f)
                        questions.extend(data.get("questions", []))
        
        return {
            "_structure_version": "modular_v2",
            "_built_in_memory": True,
            "blocks": {
                "micro_questions": questions
            }
        }
    
    def load_patterns(self) -> Dict[str, Any]:
        """Carga patterns con compatibilidad."""
        if self._patterns_cache is not None:
            return self._patterns_cache
        
        if self.is_modular:
            # Try registry first
            index = self.cqc_root / "_registry" / "patterns" / "index.json"
            if index.exists():
                with open(index) as f:
                    self._patterns_cache = json.load(f)
                    return self._patterns_cache
        
        # Legacy or fallback
        registry = self.cqc_root / "pattern_registry.json"
        if registry.exists():
            with open(registry) as f:
                patterns_list = json.load(f)
                self._patterns_cache = {"patterns": patterns_list}
                return self._patterns_cache
        
        self._patterns_cache = {"patterns": []}
        return self._patterns_cache
    
    def load_keywords(self) -> Dict[str, List[str]]:
        """Carga keywords por policy area."""
        if self._keywords_cache is not None:
            return self._keywords_cache
        
        self._keywords_cache = {}
        
        # Try registry first
        kw_by_pa = self.cqc_root / "_registry" / "keywords" / "by_policy_area"
        if kw_by_pa.exists() and list(kw_by_pa.glob("PA*.json")):
            for kw_file in kw_by_pa.glob("PA*.json"):
                pa_id = kw_file.stem
                with open(kw_file) as f:
                    data = json.load(f)
                    self._keywords_cache[pa_id] = data.get("keywords", [])
            return self._keywords_cache
        
        # Fallback: policy_areas folder
        policy_areas = self.cqc_root / "policy_areas"
        if policy_areas.exists():
            for pa_folder in policy_areas.iterdir():
                if not pa_folder.is_dir() or not pa_folder.name.startswith("PA"):
                    continue
                kw_file = pa_folder / "keywords.json"
                if kw_file.exists():
                    with open(kw_file) as f:
                        data = json.load(f)
                        pa_id = pa_folder.name.split("_")[0]
                        keywords = data.get("keywords", [])
                        if keywords:
                            self._keywords_cache[pa_id] = keywords
        
        return self._keywords_cache
    
    def load_membership_criteria(self) -> Dict[str, Any]:
        """Carga membership criteria."""
        if self._membership_criteria_cache is not None:
            return self._membership_criteria_cache
        
        self._membership_criteria_cache = {}
        mc_folder = self.cqc_root / "_registry" / "membership_criteria"
        
        if mc_folder.exists():
            for mc_file in mc_folder.glob("MC*.json"):
                with open(mc_file) as f:
                    mc = json.load(f)
                    mc_id = mc.get("criterion_id", mc_file.stem)
                    self._membership_criteria_cache[mc_id] = mc
        
        return self._membership_criteria_cache
    
    def load_cross_cutting_themes(self) -> Dict[str, Any]:
        """Carga themes con compatibilidad."""
        if self._cross_cutting_cache is not None:
            return self._cross_cutting_cache
        
        self._cross_cutting_cache = {"themes": {}}
        
        if self.is_modular:
            themes_folder = self.cqc_root / "cross_cutting" / "themes"
            if themes_folder.exists():
                for theme_folder in themes_folder.iterdir():
                    if theme_folder.is_dir():
                        detection_file = theme_folder / "detection_rules.json"
                        if detection_file.exists():
                            with open(detection_file) as f:
                                self._cross_cutting_cache["themes"][theme_folder.name] = json.load(f)
        
        # Also load from legacy file
        themes_file = self.cqc_root / "cross_cutting" / "cross_cutting_themes.json"
        if themes_file.exists():
            with open(themes_file) as f:
                data = json.load(f)
                for theme in data.get("themes", []):
                    theme_id = theme.get("theme_id")
                    if theme_id and theme_id not in self._cross_cutting_cache["themes"]:
                        self._cross_cutting_cache["themes"][theme_id] = theme
        
        return self._cross_cutting_cache
    
    def load_capabilities(self) -> Dict[str, Any]:
        """Carga sistema de capabilities."""
        result = {
            "definitions": {},
            "signal_map": {}
        }
        
        cap_defs = self.cqc_root / "_registry" / "capabilities" / "capability_definitions.json"
        cap_map = self.cqc_root / "_registry" / "capabilities" / "signal_capability_map.json"
        
        if cap_defs.exists():
            with open(cap_defs) as f:
                result["definitions"] = json.load(f).get("capabilities", {})
        
        if cap_map.exists():
            with open(cap_map) as f:
                result["signal_map"] = json.load(f).get("signal_capability_requirements", {})
        
        return result
    
    def load_view(self, view_name: str) -> Dict[str, Any]:
        """Carga una vista materializada específica."""
        view_file = self.cqc_root / "_views" / f"{view_name}.json"
        if view_file.exists():
            with open(view_file) as f:
                return json.load(f)
        raise FileNotFoundError(f"View not found: {view_name}")
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una pregunta específica por ID."""
        questionnaire = self.load_questionnaire()
        questions = questionnaire.get("blocks", {}).get("micro_questions", [])
        
        for q in questions:
            if q.get("question_id") == question_id:
                return q
        
        return None
    
    def get_questions_by_dimension(self, dimension_id: str) -> List[Dict[str, Any]]:
        """Obtiene preguntas de una dimensión."""
        questionnaire = self.load_questionnaire()
        questions = questionnaire.get("blocks", {}).get("micro_questions", [])
        
        return [q for q in questions if q.get("dimension_id") == dimension_id]
    
    def get_questions_by_policy_area(self, policy_area_id: str) -> List[Dict[str, Any]]:
        """Obtiene preguntas de una policy area."""
        questionnaire = self.load_questionnaire()
        questions = questionnaire.get("blocks", {}).get("micro_questions", [])
        
        return [q for q in questions if q.get("policy_area_id") == policy_area_id]
    
    def clear_cache(self) -> None:
        """Limpia todos los caches."""
        self._questionnaire_cache = None
        self._patterns_cache = None
        self._keywords_cache = None
        self._membership_criteria_cache = None
        self._cross_cutting_cache = None


# Singleton instance
_default_loader: Optional[CQCLoader] = None


def get_loader(cqc_root: Optional[Path] = None) -> CQCLoader:
    """Obtiene el loader singleton o crea uno nuevo."""
    global _default_loader
    
    if cqc_root is not None:
        return CQCLoader(cqc_root)
    
    if _default_loader is None:
        _default_loader = CQCLoader()
    
    return _default_loader
