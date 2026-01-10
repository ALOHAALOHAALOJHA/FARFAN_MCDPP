"""
AUDIT SCRIPT: Empirical Alignment Analysis (Part I) - SOTA ENHANCED
====================================================================

OBJECTIVE:
Conduct Part I of the Audit Specification with State-of-the-Art (SOTA) NLP techniques
to maximize accuracy in mapping Colombian Development Plans to the CQC.

INTEGRATION:
- Uses EvidenceTypeMapper from phase2_80_00_evidence_nexus.py
- Uses ExpectedElement schema from phase2_90_00_carver.py
- Scans data/plans (relative to project root)
- Reads Canonic Questionnaire Central (Dimensions, Policy Areas, Cross-cutting)

METHODOLOGY (SOTA V3.1):
1. Hybrid Retrieval: Bi-Encoder (Sentence-Transformers) -> Candidate Generation.
2. Re-Ranking: Cross-Encoder (MS MARCO) for Precision Scoring.
3. Contextual Window: Paragraph-based chunking instead of sentence splitting.
4. Negation Handling: Dependency parsing (spaCy) to remove false positives.
5. Entity Injection: Custom EntityRuler for Colombian Government context.

Author: F.A.R.F.A.N Pipeline Audit Agent
Version: 3.1-SOTA-Enhanced
Date: 2026-01-05
"""

from __future__ import annotations

import json
import math
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable, Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
# Use centralized path management (requires package installation: pip install -e .)
try:
    from farfan_pipeline.utils.paths import PROJECT_ROOT, CONFIG_DIR, DATA_DIR
    ROOT = PROJECT_ROOT
    CQC_ROOT = CONFIG_DIR
    PLANS_ROOT = DATA_DIR / "plans"
except ImportError as e:
    # Fallback: detect from script location
    logger.warning(f"Could not import farfan_pipeline paths module: {e}")
    logger.warning("Please install package with: pip install -e .")
    logger.info("Using fallback path detection...")
    _SCRIPT_DIR = Path(__file__).resolve().parent
    ROOT = _SCRIPT_DIR.parent.parent  # Go up to project root
    if not (ROOT / "pyproject.toml").exists():
        raise RuntimeError(
            "Could not detect project root. Please run from the repository root or install the package."
        )
    CQC_ROOT = ROOT / "canonic_questionnaire_central"
    PLANS_ROOT = ROOT / "data" / "plans"

OUTPUT_DIR = ROOT / "artifacts" / "audit_reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# GRACEFUL IMPORTS (SOTA LIBS)
# =============================================================================
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder, util
    import torch
    HAS_ST = True
except ImportError:
    HAS_ST = False
    logger.error("sentence-transformers or torch not found. SOTA features disabled.")

try:
    import spacy
    from spacy.pipeline import EntityRuler
    try:
        NLP = spacy.load("es_core_news_lg")
        # Disable unnecessary pipes for speed
        NLP.disable_pipes("parser", "tagger", "lemmatizer") 
        NLP.enable_pipe("ner") # Keep NER
    except OSError:
        try:
            NLP = spacy.load("en_core_web_lg")
        except OSError:
            NLP = None
    HAS_SPACY = NLP is not None
except ImportError:
    HAS_SPACY = False
    NLP = None

try:
    from rapidfuzz import fuzz, process
    HAS_FUZZ = True
except ImportError:
    HAS_FUZZ = False

try:
    import numpy as np
    from scipy import stats as sp_stats
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# =============================================================================
# SCHEMA INTEGRATION
# =============================================================================

class EvidenceType(Enum):
    """Replicated from phase2_80_00_evidence_nexus.py"""
    INDICATOR_NUMERIC = "indicador_cuantitativo"
    TEMPORAL_SERIES = "serie_temporal"
    BUDGET_AMOUNT = "monto_presupuestario"
    COVERAGE_METRIC = "metrica_cobertura"
    GOAL_TARGET = "meta_cuantificada"
    OFFICIAL_SOURCE = "fuente_oficial"
    TERRITORIAL_COVERAGE = "cobertura_territorial"
    INSTITUTIONAL_ACTOR = "actor_institucional"
    POLICY_INSTRUMENT = "instrumento_politica"
    NORMATIVE_REFERENCE = "referencia_normativa"
    CAUSAL_LINK = "vinculo_causal"
    TEMPORAL_DEPENDENCY = "dependencia_temporal"
    CONTRADICTION = "contradiccion"
    CORROBORATION = "corroboracion"
    METHOD_OUTPUT = "salida_metodo"
    AGGREGATED = "agregado"
    SYNTHESIZED = "sintetizado"

    def to_contract_format(self) -> str:
        mapping = {
            "indicador_cuantitativo": "indicadores_cuantitativos",
            "serie_temporal": "series_temporales_años",
            "monto_presupuestario": "montos_presupuestarios",
            "metrica_cobertura": "metricas_cobertura",
            "meta_cuantificada": "metas_cuantificadas",
            "fuente_oficial": "fuentes_oficiales",
            "cobertura_territorial": "cobertura_territorial_especificada",
            "actor_institucional": "actores_institucionales",
            "instrumento_politica": "instrumentos_politica",
            "referencia_normativa": "referencias_normativas",
            "vinculo_causal": "logica_causal_explicita",
            "dependencia_temporal": "dependencias_temporales",
            "contradiccion": "contradicciones",
            "corroboracion": "corroboraciones",
            "salida_metodo": "salidas_metodo",
            "agregado": "agregados",
            "sintetizado": "sintetizados",
        }
        return mapping.get(self.value, self.value)


class EvidenceTypeMapper:
    SINGULAR_TO_PLURAL = {e.value: e.to_contract_format() for e in EvidenceType}
    PLURAL_TO_SINGULAR = {v: k for k, v in SINGULAR_TO_PLURAL.items()}

    @classmethod
    def to_contract_format(cls, evidence_type: str) -> str:
        return cls.SINGULAR_TO_PLURAL.get(evidence_type, evidence_type)

    @classmethod
    def to_nexus_format(cls, contract_type: str) -> str:
        return cls.PLURAL_TO_SINGULAR.get(contract_type, contract_type)


@dataclass(frozen=True)
class ExpectedElement:
    element_type: str
    required: bool
    minimum_count: int
    category: str
    weight: float


@dataclass
class DetectionResult:
    element_type: str
    found_count: int
    expected_count: int
    score: float
    snippets: List[str]
    method_used: str
    is_sufficient: bool
    confidence: float # SOTA addition: Raw model confidence

# =============================================================================
# SOTA ANALYZERS
# =============================================================================

class SotaNegationHandler:
    """
    Uses dependency parsing to determine if a matched snippet contains a negation
    related to the query keywords.
    """
    def __init__(self, nlp):
        self.nlp = nlp
        # Only enable parser if we actually need it to save RAM
        if self.nlp and "parser" not in self.nlp.pipe_names:
             # Lazy load parser
             try:
                 self.nlp.enable_pipe("parser")
             except ValueError:
                 pass 

    def is_negated(self, text: str, keywords: List[str]) -> bool:
        if not self.nlp or not keywords:
            return False
        
        doc = self.nlp(text[:500]) # Limit scope for performance
        negation_tokens = {"no", "sin", "ni", "nunca", "jamás", "ninguno", "ninguna"}
        
        # Check if any keyword is governed by a negation
        for token in doc:
            if token.text.lower() in keywords or token.lemma_.lower() in keywords:
                # Check ancestors for negation
                for ancestor in token.ancestors:
                    if ancestor.text.lower() in negation_tokens:
                        return True
                # Check children for negation (e.g. "presupuesto no asignado")
                for child in token.children:
                    if child.text.lower() in negation_tokens:
                        return True
        return False

class SemanticAnalyzer:
    def __init__(self):
        self.bi_encoder = None
        self.cross_encoder = None
        if HAS_ST:
            try:
                # Bi-encoder for retrieval (Fast, good coverage)
                self.bi_encoder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
                
                # Cross-encoder for ranking (Slow, high precision)
                # Using a smaller cross-encoder to balance speed vs accuracy
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') 
                logger.info("SOTA Models loaded: MPNet (Bi) + MS-MARCO (Cross)")
            except Exception as e:
                logger.warning(f"SOTA Model loading failed: {e}")

    def search(self, query: str, text: str, threshold: float = 0.6, top_k: int = 5) -> List[Tuple[str, float]]:
        if not self.bi_encoder:
            return []
        
        # 1. Chunk into paragraphs (Context Aware)
        # This is better than sentences because evidence often spans 2-3 sentences.
        paragraphs = [p.strip() for p in re.split(r'\n+', text) if len(p.strip()) > 50]
        
        # If paragraphs are too few or too long, split by sentence as fallback
        if not paragraphs or len(max(paragraphs, key=len)) > 1000:
             paragraphs = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]

        if not paragraphs:
            return []

        # 2. Bi-Encoder Retrieval (Embed everything)
        # Limit to first 300 chunks to manage memory/VRAM
        corpus = paragraphs[:300]
        
        query_emb = self.bi_encoder.encode(query, convert_to_tensor=True)
        doc_embs = self.bi_encoder.encode(corpus, convert_to_tensor=True)
        
        cos_scores = util.cos_sim(query_emb, doc_embs)[0]
        
        # 3. Filter top 20 candidates for Cross-Encoder
        top_results = torch.topk(cos_scores, k=min(20, len(corpus)))
        
        # 4. Cross-Encoder Re-ranking (Accuracy Booster)
        if self.cross_encoder:
            cross_inp = [[query, corpus[idx]] for idx in top_results.indices]
            cross_scores = self.cross_encoder.predict(cross_inp)
            
            # Sort by cross-encoder score
            ranked_results = sorted(zip(cross_scores, top_results.indices), key=lambda x: x[0], reverse=True)
            
            final_results = []
            for score, idx in ranked_results:
                # MS MARCO outputs logits, usually > 0 indicates relevance, but let's be strict
                # Normalize roughly to 0-1 or use raw threshold
                norm_score = float(score) 
                if norm_score > 0.0: # Tunable threshold for CrossEncoder
                    final_results.append((corpus[idx], min(1.0, max(0.0, (norm_score + 5) / 10)))) # Rough normalization
                if len(final_results) >= top_k:
                    break
            return final_results
        else:
            # Fallback to Bi-Encoder scores
            results = []
            for score, idx in zip(top_results.values, top_results.indices):
                if score >= threshold:
                    results.append((corpus[idx], score.item()))
            return results


class NERAnalyzer:
    def __init__(self, nlp):
        self.nlp = nlp
        self._inject_domain_patterns()

    def _inject_domain_patterns(self):
        """Injects Colombian Government entities into the NER pipeline."""
        if not self.nlp:
            return
        
        # Check if EntityRuler is already present
        if "entity_ruler" in self.nlp.pipe_names:
            return

        ruler = EntityRuler(self.nlp, overwrite_ents=True, before_ner=True) # Before default NER
        
        patterns = [
            {"label": "ORG", "pattern": [{"LOWER": "dnp"}]},
            {"label": "ORG", "pattern": [{"LOWER": "dane"}]},
            {"label": "ORG", "pattern": [{"LOWER": "minhacienda"}]},
            {"label": "ORG", "pattern": [{"LOWER": "minsalud"}]},
            {"label": "ORG", "pattern": [{"LOWER": "mineducación"}]},
            {"label": "ORG", "pattern": [{"LOWER": "minambiente"}]},
            {"label": "ORG", "pattern": [{"LOWER": "mincultura"}]},
            {"label": "ORG", "pattern": [{"LOWER": "icbf"}]},
            {"label": "ORG", "pattern": [{"LOWER": "colciencias"}, {"LOWER": "minciencias"}]},
            {"label": "ORG", "pattern": [{"LOWER": "sgp"}]}, # Sistema General de Participaciones
            {"label": "GPE", "pattern": [{"LOWER": "norte"}, {"LOWER": "de"}, {"LOWER": "santander"}]},
            # Add generic fund patterns
            {"label": "ORG", "pattern": [{"LOWER": "fondo"}, {"LOWER": "de"}, {"POS": "NOUN"}]},
        ]
        
        ruler.add_patterns(patterns)
        self.nlp.add_pipe(ruler)
        logger.info("Injected domain patterns into NER pipeline.")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        if not self.nlp:
            return {}
        
        # Process in larger chunks, pipe attribute for batch processing
        doc = self.nlp(text[:800000]) 
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        return dict(entities)

# =============================================================================
# PATTERN REGISTRY & DETECTION ENGINE
# =============================================================================

class PatternRegistry:
    def __init__(self, cqc_root: Path):
        self.patterns = defaultdict(list)
        self._load_repo_patterns(cqc_root)
        self._load_sota_defaults()

    def _load_repo_patterns(self, root: Path):
        pattern_file = root / "patterns" / "pattern_registry_v3.json"
        if pattern_file.exists():
            try:
                data = json.loads(pattern_file.read_text(encoding="utf-8"))
                for cat, items in data.items():
                    for item in items:
                        if "regex" in item:
                            try:
                                self.patterns[cat].append(re.compile(item["regex"], re.I | re.M))
                            except re.error:
                                pass
            except Exception as e:
                logger.warning(f"Failed to load repo patterns: {e}")

    def _load_sota_defaults(self):
        # Enhanced defaults with more specificity
        self._add_regex('quant', [
            r'\b\d+[.,]?\d*\s*%\b', 
            r'\b(tasa|índice|indicador|cobertura|tasa de)\b.*?\d+'
        ])
        self._add_regex('territorial', [r'\b(municipio|vereda|corregimiento|cabecera|inspección|departamento)\b'])
        self._add_regex('institution', [r'\b(DANE|ICBF|DNP|MinSalud|MinEducación|MinHacienda|SGP)\b'])
        self._add_regex('temporal', [r'\b(19\d{2}|20\d{2})\b', r'\b(año|período|vigencia)\b'])
        self._add_regex('budget', [r'\b(presupuesto|inversión|recursos|apropiación|gasto)\b.*?\b[\d.]+\b', r'\b\$\s*[\d.]+\b'])
        self._add_regex('causal', [r'\b(supuesto|riesgo|premisa)\b', r'\b(teoría\s+del\s+cambio)\b', r'\b(porque|debido a|dado que)\b'])

    def _add_regex(self, key, patterns):
        for p in patterns:
            self.patterns[key].append(re.compile(p, re.I | re.M))

    def get_patterns(self, key: str) -> List:
        return self.patterns.get(key, [])


class IrrigationAuditor:
    """
    Core logic with SOTA enhancements:
    1. Semantic Search (Re-ranking)
    2. Negation Filtering
    3. Pattern Injection
    """
    def __init__(self):
        self.sem = SemanticAnalyzer()
        self.ner = NERAnalyzer(NLP)
        self.negation_handler = SotaNegationHandler(NLP)
        self.registry = PatternRegistry(CQC_ROOT)

    def audit_element(
        self, 
        element: ExpectedElement, 
        text: str, 
        question_text: str
    ) -> DetectionResult:
        et = element.element_type.lower()
        nexus_type = EvidenceTypeMapper.to_nexus_format(et)
        
        hits = 0
        snippets = []
        method = "none"
        confidence_list = []
        
        # 1. Regex / Structural Detection (Fast, high recall for structured data)
        patterns = self.registry.get_patterns(nexus_type)
        if not patterns:
            patterns = self._get_fallback_patterns(nexus_type)

        for pat in patterns:
            matches = pat.findall(text)
            if matches:
                # Check for negation in regex matches
                valid_matches = []
                for m in matches:
                    snippet = str(m)
                    # Simple keyword check for negation logic
                    keywords = re.findall(r'\b[a-záéíóúñ]+\b', snippet)
                    if not self.negation_handler.is_negated(snippet, keywords):
                        valid_matches.append(snippet)
                        if len(valid_matches) < 3:
                            snippets.append(snippet[:100])
                
                hits += len(valid_matches)
                if hits > 0:
                    method = "regex"

        # 2. NER Enhancement for Institutions/Locations (SOTA: EntityRuler)
        if "institucional" in nexus_type or "territorial" in nexus_type or "actor" in nexus_type:
            entities = self.ner.extract_entities(text)
            if nexus_type == "actor_institucional":
                # Filter generic entities if needed, but here we count them
                orgs = entities.get("ORG", [])
                hits += len(orgs)
                snippets.extend(orgs[:3])
                method = "ner" if len(orgs) > 0 else method
            elif "territorial" in nexus_type:
                locs = entities.get("LOC", []) + entities.get("GPE", [])
                hits += len(locs)
                method = "ner" if len(locs) > 0 else method

        # 3. Semantic Search (Deep Context) - Expensive, use for high weight items
        # OR if we didn't find enough structural evidence
        if (element.weight > 0.5 and HAS_ST) or (hits < element.minimum_count and HAS_ST):
            query = f"{question_text} {element.element_type}"
            sem_results = self.sem.search(query, text, threshold=0.1) # Low threshold, cross-encoder will sort
            
            if sem_results:
                # Add semantic hits, but don't double count too aggressively
                # Confidence is the score returned by semantic search
                for snippet, conf in sem_results:
                    hits += 1
                    confidence_list.append(conf)
                    if len(snippets) < 5:
                        snippets.append(f"[SEM: {conf:.2f}] " + snippet[:80])
                method = "semantic" if len(sem_results) > 0 else method

        # 4. Calculate Score
        avg_confidence = mean(confidence_list) if confidence_list else 0.0
        
        if element.required and hits == 0:
            score = 0.0
        else:
            # Improved scoring: Sigmoid-like function based on expected count
            # This prevents linear explosion of scores
            ratio = hits / (element.minimum_count + 1e-5)
            # Logarithmic scaling
            raw_score = math.log(1 + ratio) / math.log(2) # log2(1+x)
            # Cap at 1.0
            score = min(1.0, raw_score)
            
            # Adjust by confidence if semantic search was primary
            if method == "semantic":
                score = score * (0.5 + 0.5 * avg_confidence)

        score = round(score, 4)
        is_sufficient = hits >= element.minimum_count
        
        return DetectionResult(
            element_type=element.element_type,
            found_count=hits,
            expected_count=element.minimum_count,
            score=score,
            snippets=snippets,
            method_used=method,
            is_sufficient=is_sufficient,
            confidence=round(avg_confidence, 3)
        )

    def _get_fallback_patterns(self, nexus_type: str) -> List:
        mapping = {
            "indicador_cuantitativo": [r'\b\d+\s*%?\b'],
            "serie_temporal": [r'\b(19|20)\d{2}\b'],
            "monto_presupuestario": [r'\bpresupuesto\b', r'\b\$[\d.,]+\b'],
            "fuente_oficial": [r'\b(DANE|DNP|Banco Mundial)\b'],
        }
        pats = mapping.get(nexus_type, [])
        return [re.compile(p, re.I) for p in pats]


# =============================================================================
# DATA LOADERS
# =============================================================================

def load_cqc_contracts() -> List[Dict]:
    contracts = []
    dim_dirs = sorted([d for d in (CQC_ROOT / "dimensions").iterdir() if d.is_dir()])
    
    for dim_dir in dim_dirs:
        q_file = dim_dir / "questions.json"
        if not q_file.exists():
            continue
            
        try:
            data = json.loads(q_file.read_text(encoding="utf-8"))
            dim_id = data.get("dimension_id", dim_dir.name)
            
            for q in data.get("questions", []):
                expected_elements = []
                for el in q.get("expected_elements", []):
                    et = el.get("type", "")
                    req = el.get("required", False)
                    min_c = el.get("minimum", 1 if req else 0)
                    
                    cat = "qualitative"
                    if "indicador" in et or "monto" in et or "meta" in et:
                        cat = "quantitative"
                    elif "causal" in et or "vinculo" in et:
                        cat = "relational"
                    
                    w = 0.9 if req else 0.4
                    
                    expected_elements.append(
                        ExpectedElement(et, req, min_c, cat, w)
                    )
                
                contracts.append({
                    "question_id": q.get("question_id"),
                    "dimension_id": dim_id,
                    "text": q.get("question_text", ""),
                    "base_slot": q.get("base_slot", ""),
                    "expected_elements": expected_elements
                })
        except Exception as e:
            logger.error(f"Loading {q_file}: {e}")
            
    logger.info(f"Loaded {len(contracts)} contracts from CQC.")
    return contracts

def load_plans() -> Dict[str, str]:
    plans = {}
    if not PLANS_ROOT.exists():
        raise FileNotFoundError(f"Plans directory not found: {PLANS_ROOT}")
    
    # Try TXT files first (extracted from PDFs)
    txt_files = list(PLANS_ROOT.glob("*.txt"))
    if txt_files:
        for f in sorted(txt_files):
            plans[f.stem] = f.read_text(encoding="utf-8", errors="replace")
            logger.info(f"Loaded {f.stem}: {len(plans[f.stem]):,} chars")
    else:
        # Fallback: check artifacts for extracted plans
        artifacts_plans = ROOT / "artifacts" / "plans_text"
        if artifacts_plans.exists():
            for f in sorted(artifacts_plans.glob("*.txt")):
                if not f.name.endswith(".meta.txt"):
                    plans[f.stem] = f.read_text(encoding="utf-8", errors="replace")
                    logger.info(f"Loaded {f.stem} from artifacts: {len(plans[f.stem]):,} chars")
    
    if not plans:
        raise FileNotFoundError(f"No plan text files found in {PLANS_ROOT} or artifacts/plans_text")
    
    return plans

# =============================================================================
# MAIN AUDIT LOGIC
# =============================================================================

def run_audit():
    print("\n" + "="*80)
    print(" STARTING PART I: EMPIRICAL ALIGNMENT AUDIT (SOTA V3.1)")
    print("="*80)
    
    # 1. Load SOTA Models
    print("\n[1/4] Initializing SOTA Analyzers (Bi-Encoder + Cross-Encoder + NER)...")
    auditor = IrrigationAuditor()
    
    # 2. Load Data
    print("\n[2/4] Loading CQC Contracts and Development Plans...")
    contracts = load_cqc_contracts()
    plans = load_plans()
    
    # 3. Execute Irrigation Audit
    print("\n[3/4] Executing Irrigation Analysis (Precision Optimized)...")
    
    audit_results = {
        "metadata": {
            "timestamp": "2026-01-05",
            "plans_analyzed": list(plans.keys()),
            "total_questions": len(contracts),
            "methodology": "SOTA V3.1 (Bi-Enc + Cross-Enc + Negation + EntityRuler)"
        },
        "plans_summary": {},
        "convergence_analysis": {}
    }
    
    all_plan_scores = defaultdict(dict) 
    
    # Iterator for progress bar
    plan_iter = plans.items()
    if HAS_TQDM:
        plan_iter = tqdm(plan_iter, desc="Auditing Plans")
    
    for plan_name, plan_text in plan_iter:
        if not HAS_TQDM:
            print(f"\n  >>> Auditing Plan: {plan_name}")
        
        plan_report = {
            "dimension_performance": defaultdict(list),
            "critical_gaps": [],
            "overall_alignment": 0.0
        }
        
        # Iterate questions
        q_iter = contracts
        if HAS_TQDM:
            # Nested progress bar is tricky in tqdm, just show log
            pass
            
        for contract in q_iter:
            qid = contract['question_id']
            dim = contract['dimension_id']
            
            element_results = []
            for el in contract['expected_elements']:
                res = auditor.audit_element(el, plan_text, contract['text'])
                element_results.append(res)
            
            # Calculate Question Score
            total_weight = sum(e.weight for e in contract['expected_elements'])
            weighted_score = sum(r.score * e.weight for r, e in zip(element_results, contract['expected_elements']))
            
            missing_critical = any(not r.is_sufficient and e.required for r, e in zip(element_results, contract['expected_elements']))
            
            final_q_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
            
            # Penalize missing critical elements
            if missing_critical:
                final_q_score = final_q_score * 0.5 
            
            # Store
            plan_report["dimension_performance"][dim].append(final_q_score)
            all_plan_scores[plan_name][qid] = final_q_score
            
            if missing_critical:
                plan_report["critical_gaps"].append({
                    "question_id": qid,
                    "dimension": dim,
                    "missing_elements": [r.element_type for r in element_results if not r.is_sufficient]
                })
        
        # Summarize
        dim_stats = {}
        all_scores = []
        for d, scores in plan_report["dimension_performance"].items():
            all_scores.extend(scores)
            dim_stats[d] = {
                "mean": round(mean(scores), 3),
                "min": round(min(scores), 3),
                "coverage": len(scores)
            }
        
        plan_report["dimension_stats"] = dim_stats
        plan_report["overall_alignment"] = round(mean(all_scores), 3) if all_scores else 0.0
        audit_results["plans_summary"][plan_name] = plan_report
        
        if not HAS_TQDM:
            print(f"      Overall Alignment: {plan_report['overall_alignment']:.2%}")
            print(f"      Critical Gaps Found: {len(plan_report['critical_gaps'])}")

    # 4. Convergence Analysis
    print("\n[4/4] Computing Convergence & Sufficiency Metrics...")
    
    common_questions = set.intersection(*(set(d.keys()) for d in all_plan_scores.values()))
    
    if len(common_questions) > 0:
        q_std_devs = []
        for qid in common_questions:
            scores = [all_plan_scores[p][qid] for p in plans.keys()]
            if len(scores) > 1:
                q_std_devs.append(pstdev(scores))
        
        avg_divergence = mean(q_std_devs) if q_std_devs else 0.0
        
        audit_results["convergence_analysis"] = {
            "common_questions_analyzed": len(common_questions),
            "average_score_divergence": round(avg_divergence, 3),
            "interpretation": "LOW" if avg_divergence < 0.1 else "HIGH"
        }
    
    # 5. Output
    print("\n" + "="*80)
    print(" GENERATING REPORTS")
    print("="*80)
    
    json_out = OUTPUT_DIR / "part1_empirical_alignment_audit_sota.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False, default=str)
    
    md_lines = [
        "# Part I: Empirical Alignment Audit Report (SOTA V3.1)",
        f"**Date:** 2026-01-05",
        f"**Method:** Bi-Encoder + Cross-Encoder + Dependency Negation Check",
        f"**Plans Analyzed:** {', '.join(plans.keys())}",
        "",
        "## Executive Summary",
        ""
    ]
    
    for pname, data in audit_results["plans_summary"].items():
        md_lines.append(f"### {pname}")
        md_lines.append(f"- **Overall Alignment Score:** {data['overall_alignment']:.2%}")
        md_lines.append(f"- **Critical Gaps:** {len(data['critical_gaps'])}")
        
        worst_dims = sorted(data["dimension_stats"].items(), key=lambda x: x[1]["mean"])[:3]
        md_lines.append("- **Weakest Dimensions:**")
        for dim, stats in worst_dims:
            md_lines.append(f"  - {dim}: {stats['mean']:.2%}")
        md_lines.append("")
    
    if "convergence_analysis" in audit_results:
        conv = audit_results["convergence_analysis"]
        md_lines.append("## Convergence Analysis")
        md_lines.append(f"- **Average Divergence:** {conv['average_score_divergence']}")
        md_lines.append(f"- **Interpretation:** {conv['interpretation']} consistency.")
        md_lines.append("")
    
    avg_alignment = mean([v['overall_alignment'] for v in audit_results["plans_summary"].values()])
    md_lines.append("## Conclusion")
    if avg_alignment >= 0.7:
        md_lines.append(f"**VERDICT:** SUFFICIENT. (Score: {avg_alignment:.2%}).")
    else:
        md_lines.append(f"**VERDICT:** INSUFFICIENT. (Score: {avg_alignment:.2%}). Recommend enriching patterns.")
    
    md_content = "\n".join(md_lines)
    md_out = OUTPUT_DIR / "part1_empirical_alignment_audit_sota.md"
    md_out.write_text(md_content, encoding="utf-8")
    
    print(f"\n✅ Audit Complete.")
    print(f"   📄 JSON: {json_out}")
    print(f"   📄 Markdown: {md_out}")
    print("\n" + md_content.split("## Conclusion")[-1])

if __name__ == "__main__":
    run_audit()
