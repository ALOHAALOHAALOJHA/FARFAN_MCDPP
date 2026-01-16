"""
FARFAN Pipeline Orchestrator
Central engine for coordinating Extraction, PDM Adjustment, Scoring, and Recommendation phases.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FarfanOrchestrator")

class FarfanOrchestrator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.configs = {}
        self.themes = {}
        self.pdm_rules = {}
        self.scoring_weights = {}
        self.recommendation_rules = {}
        
        # Define paths
        self.paths = {
            "pdm": self.base_path / "src/farfan_pipeline/infrastructure/calibration/pdm_rules/n2_inferential_pdm_rules.json",
            "weights": self.base_path / "canonic_questionnaire_central/scoring/calibration/empirical_weights.json",
            "recommendations": self.base_path / "src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced.json",
            "themes_dir": self.base_path / "canonic_questionnaire_central/cross_cutting/themes"
        }

    def bootstrap(self):
        """Initialize the pipeline by loading and validating all configurations."""
        logger.info("Bootstrapping FARFAN Pipeline Orchestrator...")
        
        self._load_pdm_rules()
        self._load_scoring_weights()
        self._load_cross_cutting_themes()
        self._load_recommendation_rules()
        
        self._validate_pipeline_integrity()
        logger.info("Bootstrap complete. Pipeline ready.")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            logger.error(f"Configuration missing: {path}")
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_pdm_rules(self):
        """Load N2 Inferential PDM Rules."""
        data = self._load_json(self.paths["pdm"])
        self.pdm_rules = data
        logger.info(f"Loaded PDM Rules: {data.get('name')} v{data.get('version')}")

    def _load_scoring_weights(self):
        """Load Empirical Weights for Scoring."""
        data = self._load_json(self.paths["weights"])
        self.scoring_weights = data
        logger.info(f"Loaded Scoring Weights (Calibration: {data.get('calibration_date')})")

    def _load_cross_cutting_themes(self):
        """Load all Cross-Cutting Theme detection rules."""
        theme_dir = self.paths["themes_dir"]
        if not theme_dir.exists():
            logger.warning(f"Themes directory not found: {theme_dir}")
            return

        for rule_file in theme_dir.glob("**/detection_rules.json"):
            data = self._load_json(rule_file)
            theme_id = data.get("theme_id")
            self.themes[theme_id] = data
            logger.info(f"Loaded Theme: {data.get('name')} ({theme_id})")

    def _load_recommendation_rules(self):
        """Load Enhanced Recommendation Rules."""
        data = self._load_json(self.paths["recommendations"])
        self.recommendation_rules = data
        logger.info(f"Loaded {len(data.get('rules', []))} Recommendation Rules")

    def _validate_pipeline_integrity(self):
        """Ensure all components are compatible."""
        # Example check: Ensure PDM layer matches expected level
        if self.pdm_rules.get("epistemic_layer", {}).get("level") != "N2-INF":
            raise ValueError("PDM Rules file mismatch: Expected N2-INF layer")
        
        # Check if recommendation rules have integrity section
        if "integrity" not in self.recommendation_rules:
            logger.warning("Recommendation rules missing integrity section. Run repair script.")

    def execute_flow(self, document_context: Dict[str, Any]):
        """
        Executes the full pipeline flow for a given document context.
        
        Flow:
        1. PDM Adjustment (Sensitivity Analysis)
        2. Cross-Cutting Theme Detection
        3. Scoring (Phase 3-7)
        4. Recommendation Generation (Phase 8)
        """
        logger.info("Starting pipeline execution flow...")

        # Step 1: PDM Adjustment
        inference_params = self._apply_pdm_adjustments(document_context)
        
        # Step 2: Theme Detection
        detected_themes = self._detect_themes(document_context)
        
        # Step 3: Scoring
        scores = self._calculate_scores(document_context, detected_themes, inference_params)
        
        # Step 4: Recommendations
        recommendations = self._generate_recommendations(scores)
        
        return {
            "metadata": {"timestamp": "2026-01-16T..."},
            "pdm_adjustments": inference_params,
            "themes": detected_themes,
            "scores": scores,
            "recommendations": recommendations
        }

    def _apply_pdm_adjustments(self, context: Dict) -> Dict:
        """Apply N2 PDM rules to adjust inference parameters."""
        logger.info("Applying PDM adjustments...")
        params = {"prior_strength": 0.5, "mcmc_samples": 10000} # Defaults
        
        triggers = self.pdm_rules.get("pdm_triggers", {}).get("triggers", [])
        adjustments = self.pdm_rules.get("adjustment_rules", [])
        
        # Logic to evaluate triggers against context would go here
        # For now, we simulate a trigger
        active_triggers = ["HISTORICAL_BASELINES_DETECTED"] 
        
        for rule in adjustments:
            if rule["trigger"] in active_triggers:
                adj = rule["adjustment"]
                param = adj["parameter"]
                val = adj["value"]
                op = adj["operation"]
                
                if op == "set":
                    params[param] = val
                elif op == "multiply":
                    params[param] *= val
                
                logger.info(f"PDM Rule {rule['rule_id']} applied: {param} -> {params[param]}")
                
        return params

    def _detect_themes(self, context: Dict) -> Dict:
        """Run detection rules for all loaded themes."""
        logger.info("Detecting cross-cutting themes...")
        results = {}
        for theme_id, rules in self.themes.items():
            # Logic to match signals against document text would go here
            # Simulating detection
            results[theme_id] = {"detected": True, "confidence": 0.85}
        return results

    def _calculate_scores(self, context: Dict, themes: Dict, params: Dict) -> Dict:
        """Calculate scores using empirical weights and theme boosts."""
        logger.info("Calculating scores (Phase 3-7)...")
        # Apply boosts from themes
        # Example: CC_PERSPECTIVA_GENERO boosts PA01
        
        # Mock scores
        return {
            "PA01": {"DIM01": 0.5, "DIM02": 1.8}, # Crisis, Aceptable
            "PA02": {"DIM01": 2.5} # Bueno
        }

    def _generate_recommendations(self, scores: Dict) -> List[Dict]:
        """Select recommendations based on scores and bands."""
        logger.info("Generating recommendations (Phase 8)...")
        output = []
        rules = self.recommendation_rules.get("rules", [])
        
        for pa_id, dims in scores.items():
            for dim_id, score in dims.items():
                # Find matching rule
                for rule in rules:
                    cond = rule.get("when", {})
                    if (cond.get("pa_id") == pa_id and 
                        cond.get("dim_id") == dim_id and
                        cond.get("score_gte") <= score < cond.get("score_lt")):
                        
                        output.append({
                            "rule_id": rule["rule_id"],
                            "action": rule["template"]["intervention"],
                            "score": score
                        })
        return output

if __name__ == "__main__":
    # Example usage
    orchestrator = FarfanOrchestrator("/Users/recovered/Downloads/FARFAN_MCDPP")
    orchestrator.bootstrap()
    
    # Mock context
    context = {"text": "Plan de desarrollo con enfoque PDET...", "tables": []}
    result = orchestrator.execute_flow(context)
    print(json.dumps(result["recommendations"], indent=2, ensure_ascii=False))