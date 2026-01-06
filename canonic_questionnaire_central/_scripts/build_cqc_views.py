#!/usr/bin/env python3
"""
Build script para CQC (Canonic Questionnaire Central).

Genera vistas materializadas, valida integridad, y produce artefactos de build.

Uso:
    python _scripts/build_cqc_views.py [--target TARGET] [--validate-only] [--verbose]

Targets disponibles:
    - all: Todos los targets (default)
    - patterns: Solo pattern_question_matrix
    - keywords: Solo keyword_pa_matrix
    - views: Todas las vistas materializadas
    - monolith: Genera questionnaire_monolith.json
    - validate: Solo validación de integridad
"""

import json
import hashlib
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CQC_ROOT = Path(__file__).parent.parent
REGISTRY = CQC_ROOT / "_registry"
DIMENSIONS = CQC_ROOT / "dimensions"
POLICY_AREAS = CQC_ROOT / "policy_areas"
CLUSTERS = CQC_ROOT / "clusters"
CROSS_CUTTING = CQC_ROOT / "cross_cutting"
VIEWS = CQC_ROOT / "_views"
BUILD = CQC_ROOT / "_build"


@dataclass
class BuildMetrics:
    """Métricas del proceso de build."""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    patterns_processed: int = 0
    questions_processed: int = 0
    keywords_processed: int = 0
    views_generated: int = 0
    integrity_errors: int = 0
    warnings: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class IntegrityError:
    """Error de integridad referencial."""
    error_type: str
    source: str
    target: str
    message: str
    severity: str = "ERROR"


class CQCBuilder:
    """Builder principal para CQC."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.metrics = BuildMetrics()
        self.errors: List[IntegrityError] = []
        self.warnings: List[str] = []
        
        # Caches
        self._patterns: Dict[str, Any] = {}
        self._questions: Dict[str, Any] = {}
        self._keywords: Dict[str, List[str]] = {}
        self._entities: Dict[str, Any] = {}
        self._membership_criteria: Dict[str, Any] = {}
        self._cross_cutting_themes: Dict[str, Any] = {}
    
    def build_all(self) -> bool:
        """Ejecuta build completo."""
        logger.info("🔨 Starting CQC build...")
        
        # Crear directorios de output
        VIEWS.mkdir(exist_ok=True)
        BUILD.mkdir(exist_ok=True)
        
        try:
            # 1. Cargar recursos
            self._load_patterns()
            self._load_questions()
            self._load_keywords()
            self._load_membership_criteria()
            self._load_cross_cutting_themes()
            
            # 2. Validar integridad
            self._validate_referential_integrity()
            
            # 3. Generar vistas materializadas
            self._build_pattern_question_matrix()
            self._build_keyword_pa_matrix()
            self._build_mc_question_matrix()
            self._build_cc_pa_matrix()
            self._build_capability_coverage_matrix()
            self._build_questionnaire_flat()
            self._build_signal_flow_graph()
            
            # 4. Generar artefactos de build
            self._build_monolith_legacy()
            
            # 5. Generar reportes
            self._generate_integrity_report()
            self._generate_build_manifest()
            
            self.metrics.end_time = datetime.now(timezone.utc)
            
            # Resultado
            success = self.metrics.integrity_errors == 0
            status = "✅ SUCCESS" if success else "⚠️ COMPLETED WITH ERRORS"
            
            logger.info(f"{status} - Build completed in {self.metrics.duration_seconds:.2f}s")
            logger.info(f"  Patterns: {self.metrics.patterns_processed}")
            logger.info(f"  Questions: {self.metrics.questions_processed}")
            logger.info(f"  Keywords: {self.metrics.keywords_processed}")
            logger.info(f"  Views: {self.metrics.views_generated}")
            logger.info(f"  Errors: {self.metrics.integrity_errors}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            raise
    
    def _load_patterns(self) -> None:
        """Carga todos los patterns del registry."""
        logger.info("  Loading patterns...")
        
        # Try registry first
        pattern_index = REGISTRY / "patterns" / "index.json"
        if pattern_index.exists():
            with open(pattern_index) as f:
                data = json.load(f)
                self._patterns = data.get("patterns", {})
        else:
            # Fallback: load from legacy pattern_registry.json
            legacy_registry = CQC_ROOT / "pattern_registry.json"
            if legacy_registry.exists():
                with open(legacy_registry) as f:
                    patterns_list = json.load(f)
                    for p in patterns_list:
                        pat_id = p.get("pattern_id", f"PAT-{len(self._patterns):04d}")
                        self._patterns[pat_id] = p
        
        self.metrics.patterns_processed = len(self._patterns)
        logger.info(f"    Loaded {len(self._patterns)} patterns")
    
    def _load_questions(self) -> None:
        """Carga todas las preguntas de dimensions y policy_areas."""
        logger.info("  Loading questions...")
        
        # Load from dimensions
        for dim_folder in DIMENSIONS.iterdir():
            if not dim_folder.is_dir() or not dim_folder.name.startswith("DIM"):
                continue
            
            questions_file = dim_folder / "questions.json"
            if questions_file.exists():
                with open(questions_file) as f:
                    data = json.load(f)
                    questions = data.get("questions", [])
                    for q in questions:
                        q_id = q.get("question_id")
                        if q_id:
                            self._questions[q_id] = q
        
        # Load from policy_areas
        for pa_folder in POLICY_AREAS.iterdir():
            if not pa_folder.is_dir() or not pa_folder.name.startswith("PA"):
                continue
            
            questions_file = pa_folder / "questions.json"
            if questions_file.exists():
                with open(questions_file) as f:
                    data = json.load(f)
                    questions = data.get("questions", [])
                    for q in questions:
                        q_id = q.get("question_id")
                        if q_id and q_id not in self._questions:
                            self._questions[q_id] = q
        
        self.metrics.questions_processed = len(self._questions)
        logger.info(f"    Loaded {len(self._questions)} questions")
    
    def _load_keywords(self) -> None:
        """Carga keywords del registry o de policy_areas."""
        logger.info("  Loading keywords...")
        
        # Try registry first
        kw_by_pa = REGISTRY / "keywords" / "by_policy_area"
        if kw_by_pa.exists():
            for kw_file in kw_by_pa.glob("PA*.json"):
                pa_id = kw_file.stem
                with open(kw_file) as f:
                    data = json.load(f)
                    self._keywords[pa_id] = data.get("keywords", [])
        
        # Fallback: load from policy_areas
        if not self._keywords:
            for pa_folder in POLICY_AREAS.iterdir():
                if not pa_folder.is_dir():
                    continue
                kw_file = pa_folder / "keywords.json"
                if kw_file.exists():
                    with open(kw_file) as f:
                        data = json.load(f)
                        # Extract PA ID from folder name (e.g., PA01_mujeres_genero -> PA01)
                        pa_id = pa_folder.name.split("_")[0]
                        keywords = data.get("keywords", [])
                        if keywords:
                            self._keywords[pa_id] = keywords
        
        total_kw = sum(len(kws) for kws in self._keywords.values())
        self.metrics.keywords_processed = total_kw
        logger.info(f"    Loaded {total_kw} keywords across {len(self._keywords)} PAs")
    
    def _load_membership_criteria(self) -> None:
        """Carga membership criteria del registry."""
        logger.info("  Loading membership criteria...")
        
        mc_folder = REGISTRY / "membership_criteria"
        if mc_folder.exists():
            for mc_file in mc_folder.glob("MC*.json"):
                with open(mc_file) as f:
                    mc = json.load(f)
                    mc_id = mc.get("criterion_id", mc_file.stem)
                    self._membership_criteria[mc_id] = mc
        
        logger.info(f"    Loaded {len(self._membership_criteria)} membership criteria")
    
    def _load_cross_cutting_themes(self) -> None:
        """Carga cross-cutting themes."""
        logger.info("  Loading cross-cutting themes...")
        
        # Try new structure first
        themes_folder = CROSS_CUTTING / "themes"
        if themes_folder.exists():
            for theme_folder in themes_folder.iterdir():
                if theme_folder.is_dir():
                    detection_file = theme_folder / "detection_rules.json"
                    if detection_file.exists():
                        with open(detection_file) as f:
                            self._cross_cutting_themes[theme_folder.name] = json.load(f)
        
        # Also load from legacy file
        themes_file = CROSS_CUTTING / "cross_cutting_themes.json"
        if themes_file.exists():
            with open(themes_file) as f:
                data = json.load(f)
                for theme in data.get("themes", []):
                    theme_id = theme.get("theme_id")
                    if theme_id and theme_id not in self._cross_cutting_themes:
                        self._cross_cutting_themes[theme_id] = theme
        
        logger.info(f"    Loaded {len(self._cross_cutting_themes)} cross-cutting themes")
    
    def _validate_referential_integrity(self) -> None:
        """Valida integridad referencial entre componentes."""
        logger.info("  Validating referential integrity...")
        
        pattern_ids = set(self._patterns.keys())
        question_ids = set(self._questions.keys())
        mc_ids = set(self._membership_criteria.keys())
        
        # Validate MC references in bindings
        mc_bindings_file = REGISTRY / "membership_criteria" / "_bindings" / "mc_to_questions.json"
        if mc_bindings_file.exists():
            with open(mc_bindings_file) as f:
                bindings = json.load(f)
                for mc_id, binding in bindings.get("mc_to_questions", {}).items():
                    if mc_id not in mc_ids:
                        self.errors.append(IntegrityError(
                            error_type="INVALID_MC_REF",
                            source="mc_to_questions.json",
                            target=mc_id,
                            message=f"MC binding references non-existent MC {mc_id}",
                            severity="WARNING"
                        ))
        
        self.metrics.integrity_errors = len([e for e in self.errors if e.severity == "ERROR"])
        self.metrics.warnings = len([e for e in self.errors if e.severity == "WARNING"])
        
        if self.errors:
            logger.warning(f"    Found {self.metrics.integrity_errors} errors, {self.metrics.warnings} warnings")
        else:
            logger.info("    ✅ All references valid")
    
    def _build_pattern_question_matrix(self) -> None:
        """Construye matriz Pattern → Questions."""
        logger.info("  Building pattern-question matrix...")
        
        matrix = {}
        inverse_index = {}
        
        for p_id, p in self._patterns.items():
            matrix[p_id] = {
                "pattern_id": p_id,
                "category": p.get("category", "GENERAL"),
                "questions": [],
                "dimension_distribution": {},
                "policy_area_distribution": {}
            }
        
        for q_id, q in self._questions.items():
            pattern_refs = q.get("references", {}).get("pattern_refs", [])
            if not pattern_refs:
                # Check method_sets for pattern usage
                method_sets = q.get("method_sets", [])
                # Extract from expected_elements hints
                pass
            
            inverse_index[q_id] = {
                "question_id": q_id,
                "patterns": pattern_refs,
                "pattern_count": len(pattern_refs)
            }
        
        stats = {
            "total_patterns": len(self._patterns),
            "total_questions": len(self._questions),
            "patterns_with_bindings": len([p for p in matrix if matrix[p]["questions"]]),
            "questions_with_patterns": len([q for q in inverse_index if inverse_index[q]["pattern_count"] > 0])
        }
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "_generator": "build_cqc_views.py",
            "matrix": matrix,
            "inverse_index": inverse_index,
            "statistics": stats
        }
        
        with open(VIEWS / "pattern_question_matrix.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created pattern_question_matrix.json")
    
    def _build_keyword_pa_matrix(self) -> None:
        """Construye matriz Keyword → Policy Areas."""
        logger.info("  Building keyword-PA matrix...")
        
        matrix = {}
        for pa_id, keywords in self._keywords.items():
            for kw in keywords:
                if kw not in matrix:
                    matrix[kw] = {"keyword": kw, "policy_areas": []}
                matrix[kw]["policy_areas"].append(pa_id)
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "matrix": matrix,
            "statistics": {
                "total_keywords": len(matrix),
                "avg_pas_per_keyword": round(
                    sum(len(m["policy_areas"]) for m in matrix.values()) / len(matrix), 2
                ) if matrix else 0
            }
        }
        
        with open(VIEWS / "keyword_pa_matrix.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created keyword_pa_matrix.json ({len(matrix)} keywords)")
    
    def _build_mc_question_matrix(self) -> None:
        """Construye matriz MC → Questions desde bindings."""
        logger.info("  Building MC-question matrix...")
        
        matrix = {}
        
        # Load from bindings file
        bindings_file = REGISTRY / "membership_criteria" / "_bindings" / "mc_to_questions.json"
        if bindings_file.exists():
            with open(bindings_file) as f:
                data = json.load(f)
                matrix = data.get("mc_to_questions", {})
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "matrix": matrix,
            "statistics": {
                "total_mcs": len(self._membership_criteria),
                "mcs_with_bindings": len(matrix)
            }
        }
        
        with open(VIEWS / "mc_question_matrix.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created mc_question_matrix.json")
    
    def _build_cc_pa_matrix(self) -> None:
        """Construye matriz Cross-Cutting → Policy Areas."""
        logger.info("  Building CC-PA matrix...")
        
        matrix = {}
        for theme_id, theme in self._cross_cutting_themes.items():
            applies_to = theme.get("applies_to", {})
            matrix[theme_id] = {
                "theme_id": theme_id,
                "name": theme.get("name"),
                "policy_areas": applies_to.get("policy_areas", []),
                "dimensions": applies_to.get("dimensions", []),
                "has_detection_rules": "detection_strategy" in theme
            }
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "matrix": matrix
        }
        
        with open(VIEWS / "cc_pa_matrix.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created cc_pa_matrix.json")
    
    def _build_capability_coverage_matrix(self) -> None:
        """Construye matriz de cobertura de capabilities."""
        logger.info("  Building capability coverage matrix...")
        
        cap_file = REGISTRY / "capabilities" / "capability_definitions.json"
        map_file = REGISTRY / "capabilities" / "signal_capability_map.json"
        
        capabilities = {}
        signal_map = {}
        
        if cap_file.exists():
            with open(cap_file) as f:
                data = json.load(f)
                capabilities = data.get("capabilities", {})
        
        if map_file.exists():
            with open(map_file) as f:
                data = json.load(f)
                signal_map = data.get("signal_capability_requirements", {})
        
        coverage_analysis = {}
        all_caps = set(capabilities.keys())
        
        for signal_type, reqs in signal_map.items():
            required = set(reqs.get("required", []))
            coverage_analysis[signal_type] = {
                "required": list(required),
                "optional": reqs.get("optional", []),
                "all_required_defined": required <= all_caps,
                "missing_caps": list(required - all_caps)
            }
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "capabilities": capabilities,
            "signal_requirements": signal_map,
            "coverage_analysis": coverage_analysis
        }
        
        with open(VIEWS / "capability_coverage_matrix.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created capability_coverage_matrix.json")
    
    def _build_questionnaire_flat(self) -> None:
        """Construye vista plana de todas las preguntas."""
        logger.info("  Building questionnaire flat view...")
        
        flat = []
        for q_id in sorted(self._questions.keys()):
            q = self._questions[q_id]
            # Handle text field which can be string or dict
            text_field = q.get("text", "")
            if isinstance(text_field, dict):
                text_es = text_field.get("es", "")
            else:
                text_es = str(text_field)
            
            # Handle scoring which can be dict or direct string
            scoring = q.get("scoring", {})
            if isinstance(scoring, dict):
                modality = scoring.get("modality", q.get("scoring_modality"))
            else:
                modality = q.get("scoring_modality")
            
            flat.append({
                "question_id": q_id,
                "dimension_id": q.get("dimension_id"),
                "policy_area_id": q.get("policy_area_id"),
                "cluster_id": q.get("cluster_id"),
                "base_slot": q.get("base_slot"),
                "text_es": text_es,
                "modality": modality,
                "expected_elements_count": len(q.get("expected_elements", []))
            })
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "total_questions": len(flat),
            "questions": flat
        }
        
        with open(VIEWS / "questionnaire_flat.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created questionnaire_flat.json ({len(flat)} questions)")
    
    def _build_signal_flow_graph(self) -> None:
        """Construye grafo de flujo de señales."""
        logger.info("  Building signal flow graph...")
        
        nodes = []
        edges = []
        
        # Add MC nodes
        for mc_id, mc in self._membership_criteria.items():
            nodes.append({
                "id": mc_id,
                "type": "MEMBERSHIP_CRITERIA",
                "signal_type": mc.get("signal_type"),
                "implementation_status": mc.get("implementation_status", "UNKNOWN")
            })
        
        # Add Phase nodes
        phases = [
            {"id": "PHASE_1", "type": "PHASE", "name": "Extraction"},
            {"id": "PHASE_2", "type": "PHASE", "name": "Routing"},
            {"id": "PHASE_3", "type": "PHASE", "name": "Scoring"},
            {"id": "PHASE_4_7", "type": "PHASE", "name": "Aggregation"}
        ]
        nodes.extend(phases)
        
        # Add edges from MC to Phase 1
        for mc_id in self._membership_criteria.keys():
            edges.append({
                "source": mc_id,
                "target": "PHASE_1",
                "type": "PRODUCES"
            })
        
        output = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "nodes": nodes,
            "edges": edges
        }
        
        with open(VIEWS / "signal_flow_graph.json", "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.metrics.views_generated += 1
        logger.info(f"    Created signal_flow_graph.json")
    
    def _build_monolith_legacy(self) -> None:
        """Genera questionnaire_monolith.json para backward compatibility."""
        logger.info("  Building legacy monolith (backward compatibility)...")
        
        micro_questions = []
        for q_id in sorted(self._questions.keys()):
            q = self._questions[q_id]
            
            # Handle text field which can be string or dict
            text_field = q.get("text", "")
            if isinstance(text_field, dict):
                text_str = text_field.get("es", "")
            else:
                text_str = str(text_field)
            
            # Handle scoring which can be dict or direct string
            scoring = q.get("scoring", {})
            if isinstance(scoring, dict):
                modality = scoring.get("modality", q.get("scoring_modality"))
            else:
                modality = q.get("scoring_modality")
            
            micro_questions.append({
                "question_id": q_id,
                "dimension_id": q.get("dimension_id"),
                "policy_area_id": q.get("policy_area_id"),
                "cluster_id": q.get("cluster_id"),
                "base_slot": q.get("base_slot"),
                "text": text_str,
                "expected_elements": q.get("expected_elements", []),
                "scoring_modality": modality,
                "failure_contract": q.get("failure_contract", {}),
                "method_sets": q.get("method_sets", [])
            })
        
        monolith = {
            "_schema_version": "2.0.0",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "_generator": "build_cqc_views.py",
            "_deprecated": True,
            "_deprecation_notice": "This file is auto-generated. Do not edit manually.",
            "blocks": {
                "micro_questions": micro_questions
            }
        }
        
        content = json.dumps(monolith, sort_keys=True)
        sha256 = hashlib.sha256(content.encode()).hexdigest()
        monolith["sha256"] = sha256
        
        with open(BUILD / "questionnaire_monolith.json", "w") as f:
            json.dump(monolith, f, indent=2, ensure_ascii=False)
        
        logger.info(f"    Created questionnaire_monolith.json (SHA256: {sha256[:16]}...)")
    
    def _generate_integrity_report(self) -> None:
        """Genera reporte de integridad."""
        logger.info("  Generating integrity report...")
        
        report = {
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PASS" if self.metrics.integrity_errors == 0 else "FAIL",
            "error_count": self.metrics.integrity_errors,
            "warning_count": self.metrics.warnings,
            "errors": [asdict(e) for e in self.errors if e.severity == "ERROR"],
            "warnings": [asdict(e) for e in self.errors if e.severity == "WARNING"]
        }
        
        with open(BUILD / "integrity_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"    Created integrity_report.json")
    
    def _generate_build_manifest(self) -> None:
        """Genera manifest del build."""
        logger.info("  Generating build manifest...")
        
        manifest = {
            "_generated_at": datetime.now(timezone.utc).isoformat(),
            "build_duration_seconds": self.metrics.duration_seconds,
            "metrics": {
                "patterns_processed": self.metrics.patterns_processed,
                "questions_processed": self.metrics.questions_processed,
                "keywords_processed": self.metrics.keywords_processed,
                "views_generated": self.metrics.views_generated,
                "integrity_errors": self.metrics.integrity_errors,
                "warnings": self.metrics.warnings
            },
            "views_generated": [
                "pattern_question_matrix.json",
                "keyword_pa_matrix.json",
                "mc_question_matrix.json",
                "cc_pa_matrix.json",
                "capability_coverage_matrix.json",
                "questionnaire_flat.json",
                "signal_flow_graph.json"
            ],
            "legacy_artifacts": [
                "questionnaire_monolith.json"
            ],
            "success": self.metrics.integrity_errors == 0
        }
        
        with open(BUILD / "build_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"    Created build_manifest.json")


def main():
    parser = argparse.ArgumentParser(description="Build CQC views and artifacts")
    parser.add_argument("--target", default="all", help="Build target")
    parser.add_argument("--validate-only", action="store_true", help="Only validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    builder = CQCBuilder(verbose=args.verbose)
    
    if args.validate_only:
        builder._load_patterns()
        builder._load_questions()
        builder._load_membership_criteria()
        builder._validate_referential_integrity()
        success = builder.metrics.integrity_errors == 0
    else:
        success = builder.build_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
