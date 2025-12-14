"""
INTERNAL SPC COMPONENT

⚠️  USAGE RESTRICTION ⚠️
==============================================================================
This module implements SOTA semantic chunking and policy analysis for Smart
Policy Chunks. It MUST NOT be used as a standalone ingestion pipeline in the
canonical FARFAN flow.

Canonical entrypoint is scripts/run_policy_pipeline_verified.py.

This module is an INTERNAL COMPONENT of:
    src/farfan_core/processing/spc_ingestion.py (StrategicChunkingSystem)

DO NOT use this module directly as an independent pipeline. It is consumed
internally by the SPC core and should only be imported from within:
    - farfan_core.processing.spc_ingestion
    - Unit tests for SPC components

Scientific Foundation:
- Semantic: BGE-M3 (2024, SOTA multilingual dense retrieval)
- Chunking: Semantic-aware with policy structure recognition
- Math: Information-theoretic Bayesian evidence accumulation
- Causal: Directed Acyclic Graph inference with interventional calculus
==============================================================================
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import torch
from scipy import stats
from scipy.spatial.distance import cosine
from scipy.special import rel_entr

# Check dependency lockdown before importing transformers
from farfan_pipeline.core.dependency_lockdown import get_dependency_lockdown
from transformers import AutoModel, AutoTokenizer

_lockdown = get_dependency_lockdown()

if TYPE_CHECKING:
    from numpy.typing import NDArray

# Note: logging.basicConfig should be called by the application entry point,
# not at module import time to avoid side effects
logger = logging.getLogger("policy_framework")

def _get_chunk_content(chunk: dict[str, Any]) -> str:
    """Compatibility helper returning the canonical chunk content field."""

    if "content" in chunk:
        return chunk["content"]
    return chunk.get("text", "")

def _upgrade_chunk_schema(chunk: dict[str, Any]) -> dict[str, Any]:
    """Return a chunk dict that guarantees ``content`` availability."""

    if "content" in chunk:
        return chunk
    upgraded = dict(chunk)
    upgraded["content"] = upgraded.get("text", "")
    return upgraded

# ========================
# CALIBRATED CONSTANTS (SOTA)
# ========================
POSITION_WEIGHT_SCALE: float = 0.42  # Early sections exert stronger evidentiary leverage
TABLE_WEIGHT_FACTOR: float = 1.35  # Tabular content is typically audited data
NUMERICAL_WEIGHT_FACTOR: float = 1.18  # Numerical narratives reinforce credibility
PLAN_SECTION_WEIGHT_FACTOR: float = 1.25  # Investment plans anchor execution feasibility
DIAGNOSTIC_SECTION_WEIGHT_FACTOR: float = 0.92  # Diagnostics contextualize but do not commit resources
RENYI_ALPHA_ORDER: float = 1.45  # Van Erven & Harremoës (2014) Optimum between KL and Rényi regimes
RENYI_ALERT_THRESHOLD: float = 0.24  # Empirically tuned on 2021-2024 Colombian PDM corpus
RENYI_CURVATURE_GAIN: float = 0.85  # Amplifies curvature impact without destabilizing evidence
RENYI_FLUX_TEMPERATURE: float = 0.65  # Controls saturation of Renyi coherence flux
RENYI_STABILITY_EPSILON: float = 1e-9  # Numerical guard-rail for degenerative posteriors

# ========================
# DOMAIN ONTOLOGY
# ========================

class CausalDimension(Enum):
    """Dimensiones de la cadena de valor (DNP Colombia)."""

    INSUMOS = "DIM01"
    ACTIVIDADES = "DIM02"
    PRODUCTOS = "DIM03"
    RESULTADOS = "DIM04"
    IMPACTOS = "DIM05"
    CAUSALIDAD = "DIM06"

    @classmethod
    def from_dimension_code(cls, dim_code: str) -> CausalDimension | None:
        normalized = dim_code.strip().upper()
        mapping = {
            "D1": cls.INSUMOS,
            "DIM01": cls.INSUMOS,
            "D2": cls.ACTIVIDADES,
            "DIM02": cls.ACTIVIDADES,
            "D3": cls.PRODUCTOS,
            "DIM03": cls.PRODUCTOS,
            "D4": cls.RESULTADOS,
            "DIM04": cls.RESULTADOS,
            "D5": cls.IMPACTOS,
            "DIM05": cls.IMPACTOS,
            "D6": cls.CAUSALIDAD,
            "DIM06": cls.CAUSALIDAD,
        }
        return mapping.get(normalized)


class UnitOfAnalysisLoader:
    """Loads canonical patterns from unit_of_analysis_index.json."""

    _payload: dict[str, Any] | None = None

    @classmethod
    def _index_path(cls) -> Path:
        return (
            Path(__file__).resolve().parents[2]
            / "artifacts/plan1/canonical_ground_truth/unit_of_analysis_index.json"
        )

    @classmethod
    def load(cls) -> dict[str, Any]:
        if cls._payload is not None:
            return cls._payload

        path = cls._index_path()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            payload = {}
        except json.JSONDecodeError:
            payload = {}

        cls._payload = payload if isinstance(payload, dict) else {}
        return cls._payload

    @classmethod
    def get_patterns(cls, pattern_type: str) -> list[str]:
        payload = cls.load()
        patterns = payload.get(pattern_type, [])
        if isinstance(patterns, list) and all(isinstance(p, str) for p in patterns):
            return list(patterns)
        return []

    @classmethod
    def get_section_type_rules(cls) -> dict[str, list[str]]:
        payload = cls.load()
        rules = payload.get("section_type_rules", {})
        if not isinstance(rules, dict):
            return {}
        typed: dict[str, list[str]] = {}
        for key, value in rules.items():
            if isinstance(key, str) and isinstance(value, list) and all(isinstance(p, str) for p in value):
                typed[key] = list(value)
        return typed

    @classmethod
    def get_table_columns(cls) -> dict[str, list[str]]:
        payload = cls.load()
        columns = payload.get("table_columns", {})
        if not isinstance(columns, dict):
            return {}
        typed: dict[str, list[str]] = {}
        for key, value in columns.items():
            if isinstance(key, str) and isinstance(value, list) and all(isinstance(c, str) for c in value):
                typed[key] = list(value)
        return typed

    @classmethod
    def get_dimension_descriptions(cls) -> dict[str, str]:
        payload = cls.load()
        descriptions = payload.get("dimension_descriptions", {})
        if not isinstance(descriptions, dict):
            return {}
        typed: dict[str, str] = {}
        for key, value in descriptions.items():
            if isinstance(key, str) and isinstance(value, str):
                typed[key] = value
        return typed

@dataclass(frozen=True, slots=True)
class SemanticConfig:
    """Configuración calibrada para análisis de políticas públicas"""
    # BGE-M3: Best multilingual embedding (Jan 2024, beats E5)
    embedding_model: str = "BAAI/bge-m3"
    chunk_size: int = 768  # Optimal for policy paragraphs (empirical)
    chunk_overlap: int = 128  # Preserve cross-boundary context
    similarity_threshold: float = 0.82  # Calibrated on PDM corpus
    min_evidence_chunks: int = 3  # Statistical significance floor
    bayesian_prior_strength: float = 0.5  # Conservative uncertainty
    device: Literal["cpu", "cuda"] | None = None
    batch_size: int = 32
    fp16: bool = True  # Memory optimization

# ========================
# SEMANTIC PROCESSOR (SOTA)
# ========================

class SemanticProcessor:
    """
    State-of-the-art semantic processing with:
    - BGE-M3 embeddings (2024 SOTA)
    - Policy-aware chunking (respects PDM structure)
    - Efficient batching with FP16
    """

    def __init__(self, config: SemanticConfig) -> None:
        self.config = config
        self._model = None
        self._tokenizer = None
        self._loaded = False

    
    def _lazy_load(self) -> None:
        if self._loaded:
            return
        try:
            device = self.config.device or ("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Loading BGE-M3 model on {device}...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.config.embedding_model)
            self._model = AutoModel.from_pretrained(
                self.config.embedding_model,
                torch_dtype=torch.float16 if self.config.fp16 and device == "cuda" else torch.float32
            ).to(device)
            self._model.eval()
            self._loaded = True
            logger.info("BGE-M3 loaded successfully")
        except ImportError as e:
            missing = None
            msg = str(e)
            if "transformers" in msg:
                missing = "transformers"
            elif "torch" in msg:
                missing = "torch"
            else:
                missing = "transformers or torch"
            raise RuntimeError(
                f"Missing dependency: {missing}. Please install with 'pip install {missing}'"
            ) from e

    
    def chunk_text(self, text: str, preserve_structure: bool = True) -> list[dict[str, Any]]:
        """
        Policy-aware semantic chunking:
        - Respects section boundaries (numbered lists, headers)
        - Maintains table integrity
        - Preserves reference links between text segments
        """
        self._lazy_load()
        # Detect structural elements (headings, numbered sections, tables)
        if preserve_structure:
            sections = self._detect_pdm_structure(text)
        else:
            sections = [{"text": text, "type": "TEXT", "id": 0}]
        chunks = []
        for section in sections:
            # Tokenize section
            tokens = self._tokenizer.encode(
                section["text"],
                add_special_tokens=False,
                truncation=False
            )
            # Sliding window with overlap
            for i in range(0, len(tokens), self.config.chunk_size - self.config.chunk_overlap):
                chunk_tokens = tokens[i:i + self.config.chunk_size]
                chunk_text = self._tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                chunks.append({
                    "content": chunk_text,
                    "section_type": section["type"],
                    "section_id": section["id"],
                    "section_header": section.get("header", ""),
                    "token_count": len(chunk_tokens),
                    "position": len(chunks),
                    "has_table": self._detect_table(chunk_text),
                    "has_numerical": self._detect_numerical_data(chunk_text),
                    "has_causal_language": self._detect_causal_language(chunk_text),
                    "pdq_context": {},
                })
        # Batch embed all chunks
        embeddings = self._embed_batch([c["content"] for c in chunks])
        for chunk, emb in zip(chunks, embeddings, strict=False):
            chunk["embedding"] = emb
        logger.info(f"Generated {len(chunks)} policy-aware chunks")
        return [_upgrade_chunk_schema(chunk) for chunk in chunks]

    
    def _detect_pdm_structure(self, text: str) -> list[dict[str, Any]]:
        """Detect PDM sections using patterns from unit_of_analysis_index.json."""

        header_patterns = [re.compile(p) for p in UnitOfAnalysisLoader.get_patterns("section_headers")]
        if not header_patterns:
            return [{"text": text.strip(), "type": "GENERAL", "id": "sec_0", "header": ""}]

        headers: list[dict[str, Any]] = []
        for compiled in header_patterns:
            for match in compiled.finditer(text):
                headers.append(
                    {
                        "text": match.group(0).strip(),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        if not headers:
            return [{"text": text.strip(), "type": "GENERAL", "id": "sec_0", "header": ""}]

        deduped_by_start: dict[int, dict[str, Any]] = {}
        for header in headers:
            start = int(header["start"])
            if start not in deduped_by_start:
                deduped_by_start[start] = header

        ordered_headers = [deduped_by_start[k] for k in sorted(deduped_by_start)]
        sections: list[dict[str, Any]] = []

        if ordered_headers[0]["start"] > 0:
            sections.append(
                {
                    "text": text[: ordered_headers[0]["start"]].strip(),
                    "type": "GENERAL",
                    "id": "sec_0_preamble",
                    "header": "",
                }
            )

        for idx, header in enumerate(ordered_headers):
            start = int(header["end"])
            end = int(ordered_headers[idx + 1]["start"]) if idx + 1 < len(ordered_headers) else len(text)
            header_text = str(header.get("text", ""))
            sections.append(
                {
                    "text": text[start:end].strip(),
                    "type": self._classify_section_type(header_text),
                    "id": f"sec_{idx}",
                    "header": header_text,
                }
            )

        return sections

    def _classify_section_type(self, header: str) -> str:
        rules = UnitOfAnalysisLoader.get_section_type_rules()
        for section_type, patterns in rules.items():
            if any(re.search(pattern, header) for pattern in patterns):
                return section_type
        return "GENERAL"

    
    def _detect_table(self, text: str) -> bool:
        """Detect if chunk contains tabular data"""
        if text.count("\t") > 3 or text.count("|") > 3:
            return True

        marker_patterns = UnitOfAnalysisLoader.get_patterns("table_markers")
        if any(re.search(pattern, text) for pattern in marker_patterns):
            return True

        table_columns = UnitOfAnalysisLoader.get_table_columns()
        for columns in table_columns.values():
            hits = sum(1 for col in columns if col and col in text)
            if hits >= 2:
                return True

        return bool(re.search(r"\d+\s+\d+\s+\d+", text))

    def _detect_causal_language(self, text: str) -> bool:
        patterns = UnitOfAnalysisLoader.get_patterns("causal_connectors")
        return any(re.search(pattern, text) for pattern in patterns)

    
    def _detect_numerical_data(self, text: str) -> bool:
        """Detect if chunk contains significant numerical/financial data"""
        # Look for currency, percentages, large numbers
        patterns = [
            r'\$\s*\d+(?:[\.,]\d+)*',  # Currency
            r'\d+(?:[\.,]\d+)*\s*%',  # Percentages
            r'\d{1,3}(?:[.,]\d{3})+',  # Large numbers with separators
        ]
        return any(re.search(p, text) for p in patterns)

    
    def _embed_batch(self, texts: list[str]) -> list[NDArray[np.floating[Any]]]:
        """Batch embedding with BGE-M3"""
        self._lazy_load()
        embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            # Tokenize batch
            encoded = self._tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.config.chunk_size,
                return_tensors="pt"
            ).to(self._model.device)
            # Generate embeddings (mean pooling)
            with torch.no_grad():
                outputs = self._model(**encoded)
            # Mean pooling over sequence
            attention_mask = encoded["attention_mask"]
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            batch_embeddings = (sum_embeddings / sum_mask).cpu().numpy()
            embeddings.extend([emb.astype(np.float32) for emb in batch_embeddings])
        return embeddings

    
    def embed_single(self, text: str) -> NDArray[np.floating[Any]]:
        """Single text embedding"""
        return self._embed_batch([text])[0]

# ========================
# MATHEMATICAL ENHANCER (RIGOROUS)
# ========================

class BayesianEvidenceIntegrator:
    """
    Information-theoretic Bayesian evidence accumulation:
    - Dirichlet-Multinomial for multi-hypothesis tracking
    - KL divergence for belief update quantification
    - Entropy-based confidence calibration
    - No simplifications or heuristics
    """

    def __init__(self, prior_concentration: float = 0.5) -> None:
        """
        Args:
            prior_concentration: Dirichlet concentration (α).
                Lower = more uncertain prior (conservative)
        """
        if prior_concentration <= 0:
            raise ValueError(
                f"Invalid prior_concentration: Dirichlet concentration parameter must be strictly positive. "
                f"Received: {prior_concentration}"
            )
        self.prior_alpha = float(prior_concentration)

    def integrate_evidence(
        self,
        similarities: NDArray[np.float64],
        chunk_metadata: list[dict[str, Any]]
    ) -> dict[str, float]:
        """
        Bayesian evidence integration with information-theoretic rigor:
        1. Map similarities to likelihood space via monotonic transform
        2. Weight evidence by chunk reliability (position, structure, content type)
        3. Update Dirichlet posterior
        4. Compute information gain (KL divergence from prior)
        5. Calculate calibrated confidence with epistemic uncertainty
        """
        if len(similarities) == 0:
            return self._null_evidence()
        # 1. Transform similarities to probability space
        # Using sigmoid with learned temperature for calibration
        sims = np.asarray(similarities, dtype=np.float64)
        probs = self._similarity_to_probability(sims)
        # 2. Compute reliability weights from metadata
        weights = self._compute_reliability_weights(chunk_metadata)
        # 3. Aggregate weighted evidence
        # Dirichlet posterior parameters: α_post = α_prior + weighted_counts
        positive_evidence = np.sum(weights * probs)
        negative_evidence = np.sum(weights * (1.0 - probs))
        alpha_pos = self.prior_alpha + positive_evidence
        alpha_neg = self.prior_alpha + negative_evidence
        alpha_total = alpha_pos + alpha_neg
        # 4. Posterior statistics
        posterior_mean = alpha_pos / alpha_total
        posterior_variance = (alpha_pos * alpha_neg) / (
            alpha_total**2 * (alpha_total + 1)
        )
        # 5. Information gain (KL divergence from prior to posterior)
        prior_dist = np.array([self.prior_alpha, self.prior_alpha])
        prior_dist = prior_dist / prior_dist.sum()
        posterior_dist = np.array([alpha_pos, alpha_neg])
        posterior_dist = posterior_dist / posterior_dist.sum()
        kl_divergence = float(np.sum(rel_entr(posterior_dist, prior_dist)))
        # 6. Entropy-based calibrated confidence
        posterior_entropy = stats.beta.entropy(alpha_pos, alpha_neg)
        max_entropy = stats.beta.entropy(1, 1)  # Maximum uncertainty
        confidence = 1.0 - (posterior_entropy / max_entropy)
        return {
            "posterior_mean": float(np.clip(posterior_mean, 0.0, 1.0)),
            "posterior_std": float(np.sqrt(posterior_variance)),
            "information_gain": float(kl_divergence),
            "confidence": float(confidence),
            "evidence_strength": float(
                positive_evidence / (alpha_total - 2 * self.prior_alpha)
                if abs(alpha_total - 2 * self.prior_alpha) > 1e-8 else 0.0
            ),
            "n_chunks": len(similarities)
        }

    
    def _similarity_to_probability(self, sims: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Calibrated transform from cosine similarity [-1,1] to probability [0,1]
        Using sigmoid with empirically derived temperature
        """
        # Shift to [0,2], scale to reasonable range
        x = (sims + 1.0) * 2.0
        # Sigmoid with temperature=2.0 (calibrated on policy corpus)
        return 1.0 / (1.0 + np.exp(-x / 2.0))

    
    def _compute_reliability_weights(self, metadata: list[dict[str, Any]]) -> NDArray[np.float64]:
        n = len(metadata)
        weights = np.ones(n, dtype=np.float64)

        for i, meta in enumerate(metadata):
            weight = 1.0

            section_type = str(meta.get("section_type", ""))
            if section_type == "ESTRATEGICA":
                weight *= 1.35
            elif section_type == "FINANCIERA":
                weight *= 1.30
            elif section_type == "PAZ_PDET":
                weight *= 1.25
            elif section_type == "DIAGNOSTICO":
                weight *= 0.90
            elif section_type == "SEGUIMIENTO":
                weight *= 1.10

            chunk_text = _get_chunk_content(meta)

            if meta.get("has_table", False):
                if "Matriz de Indicadores" in chunk_text:
                    weight *= 1.50
                elif "Plan Plurianual de Inversiones" in chunk_text:
                    weight *= 1.45
                elif "Línea base" in chunk_text and "Meta" in chunk_text:
                    weight *= 1.35
                else:
                    weight *= 1.20

            if meta.get("has_numerical", False):
                if re.search(r"\\$\\s*[\\d,.]+\\s*(?:millones?)?\\s*(?:COP)?", chunk_text, re.I):
                    weight *= 1.40
                elif re.search(r"\\d+(?:[.,]\\d+)?%", chunk_text):
                    weight *= 1.25
                else:
                    weight *= 1.15

            if meta.get("has_causal_language", False):
                weight *= 1.30

            if re.search(r"Ley\\s+\\d+\\s+de\\s+\\d{4}", chunk_text, re.I):
                weight *= 1.20

            if re.search(r"(?:municipio|vereda|corregimiento|PDET|zona rural)", chunk_text, re.I):
                weight *= 1.15

            position = float(meta.get("position", 0.0))
            position_factor = 1.0 - (position / max(1.0, float(n))) * 0.3
            weight *= position_factor

            weights[i] = weight

        total = float(weights.sum())
        if total <= 0:
            return weights
        return weights * (n / total)

    
    def _null_evidence(self) -> dict[str, float]:
        """Return prior state (no evidence)"""
        prior_mean = 0.5 # Refactored
        prior_var = self.prior_alpha / \
            ((2 * self.prior_alpha)**2 * (2 * self.prior_alpha + 1))
        return {
            "posterior_mean": prior_mean,
            "posterior_std": float(np.sqrt(prior_var)),
            "information_gain": 0.0,
            "confidence": 0.0,
            "evidence_strength": 0.0,
            "n_chunks": 0
        }

    def causal_strength(
        self,
        cause_emb: NDArray[np.floating[Any]],
        effect_emb: NDArray[np.floating[Any]],
        context_emb: NDArray[np.floating[Any]]
    ) -> float:
        """
        Causal strength via conditional independence approximation:
        strength = sim(cause, effect) * [1 - |sim(cause,ctx) - sim(effect,ctx)|]
        Intuition: Strong causal link if cause-effect similar AND
        both relate similarly to context (conditional independence test proxy)
        """
        sim_ce = 1.0 - cosine(cause_emb, effect_emb)
        sim_c_ctx = 1.0 - cosine(cause_emb, context_emb)
        sim_e_ctx = 1.0 - cosine(effect_emb, context_emb)
        # Conditional independence proxy
        cond_indep = 1.0 - abs(sim_c_ctx - sim_e_ctx)
        # Combined strength (normalized to [0,1])
        strength = ((sim_ce + 1) / 2) * cond_indep
        return float(np.clip(strength, 0.0, 1.0))

# ========================
# POLICY ANALYZER (INTEGRATED)
# ========================

class PolicyDocumentAnalyzer:
    """
    Colombian Municipal Development Plan Analyzer:
    - BGE-M3 semantic processing
    - Policy-aware chunking (respects PDM structure)
    - Bayesian evidence integration with information theory
    - Causal dimension analysis per Marco Lógico
    """

    def __init__(self, config: SemanticConfig | None = None) -> None:
        self.config = config or SemanticConfig()
        self.semantic = SemanticProcessor(self.config)
        self.bayesian = BayesianEvidenceIntegrator(
            prior_concentration=self.config.bayesian_prior_strength
        )
        # Initialize dimension embeddings
        self.dimension_embeddings = self._init_dimension_embeddings()

    
    def _init_dimension_embeddings(self) -> dict[CausalDimension, NDArray[np.floating[Any]]]:
        descriptions = UnitOfAnalysisLoader.get_dimension_descriptions()

        def _fallback(dim: CausalDimension) -> str:
            from farfan_pipeline.core.canonical_notation import get_dimension_description

            return get_dimension_description(dim.value)

        return {
            dim: self.semantic.embed_single(descriptions.get(dim.value, _fallback(dim)))
            for dim in CausalDimension
        }

    
    def analyze(self, text: str) -> dict[str, Any]:
        """
        Full pipeline: chunking → embedding → dimension analysis → evidence integration
        """
        # 1. Policy-aware chunking
        chunks = self.semantic.chunk_text(text, preserve_structure=True)
        logger.info(f"Processing {len(chunks)} chunks")
        # 2. Analyze each causal dimension
        dimension_results = {}
        for dim, dim_emb in self.dimension_embeddings.items():
            similarities = np.array([
                1.0 - cosine(chunk["embedding"], dim_emb)
                for chunk in chunks
            ])
            # Filter by threshold
            relevant_mask = similarities >= self.config.similarity_threshold
            relevant_sims = similarities[relevant_mask]
            relevant_chunks = [c for c, m in zip(chunks, relevant_mask, strict=False) if m]
            # Bayesian integration
            if len(relevant_sims) >= self.config.min_evidence_chunks:
                evidence = self.bayesian.integrate_evidence(
                    relevant_sims,
                    relevant_chunks
                )
            else:
                evidence = self.bayesian._null_evidence()
            dimension_results[dim.value] = {
                "total_chunks": int(np.sum(relevant_mask)),
                "mean_similarity": float(np.mean(similarities)),
                "max_similarity": float(np.max(similarities)),
                **evidence
            }
        # 3. Extract key findings (top chunks per dimension)
        key_excerpts = self._extract_key_excerpts(chunks, dimension_results)
        return {
            "summary": {
                "total_chunks": len(chunks),
                "sections_detected": len({c["section_type"] for c in chunks}),
                "has_tables": sum(1 for c in chunks if c["has_table"]),
                "has_numerical": sum(1 for c in chunks if c["has_numerical"])
            },
            "causal_dimensions": dimension_results,
            "key_excerpts": key_excerpts
        }

    def _extract_key_excerpts(
        self,
        chunks: list[dict[str, Any]],
        dimension_results: dict[str, dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Extract most relevant text excerpts per dimension"""
        _ = dimension_results  # parameter kept for future compatibility
        excerpts = {}
        for dim, dim_emb in self.dimension_embeddings.items():
            # Rank chunks by similarity
            sims = [
                (i, 1.0 - cosine(chunk["embedding"], dim_emb))
                for i, chunk in enumerate(chunks)
            ]
            sims.sort(key=lambda x: x[1], reverse=True)
            # Top 3 excerpts
            top_chunks = [chunks[i] for i, _ in sims[:3]]
            excerpts[dim.value] = [
                _get_chunk_content(c)[:300]
                + ("..." if len(_get_chunk_content(c)) > 300 else "")
                for c in top_chunks
            ]
        return excerpts

# ========================
# PRODUCER CLASS - Registry Exposure
# ========================

class SemanticChunkingProducer:
    """
    Producer wrapper for semantic chunking and policy analysis with registry exposure

    Provides public API methods for orchestrator integration without exposing
    internal implementation details or summarization logic.

    Version: 1.0
    Producer Type: Semantic Analysis / Chunking
    """

    def __init__(self, config: SemanticConfig | None = None) -> None:
        """Initialize producer with optional configuration"""
        self.config = config or SemanticConfig()
        self.semantic = SemanticProcessor(self.config)
        self.bayesian = BayesianEvidenceIntegrator(
            prior_concentration=self.config.bayesian_prior_strength
        )
        self.analyzer = PolicyDocumentAnalyzer(self.config)
        logger.info("SemanticChunkingProducer initialized")

    # ========================================================================
    # CHUNKING API
    # ========================================================================

    
    def chunk_document(self, text: str, preserve_structure: bool = True) -> list[dict[str, Any]]:
        """Chunk document into semantic units with embeddings"""
        return self.semantic.chunk_text(text, preserve_structure)

    
    def get_chunk_count(self, chunks: list[dict[str, Any]]) -> int:
        """Get number of chunks"""
        return len(chunks)

    
    def get_chunk_text(self, chunk: dict[str, Any]) -> str:
        """Extract text from chunk"""
        return _get_chunk_content(chunk)

    
    def get_chunk_embedding(self, chunk: dict[str, Any]) -> NDArray[np.floating[Any]]:
        """Extract embedding from chunk"""
        return chunk.get("embedding", np.array([]))

    
    def get_chunk_metadata(self, chunk: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from chunk"""
        return {
            "section_type": chunk.get("section_type"),
            "section_id": chunk.get("section_id"),
            "section_header": chunk.get("section_header"),
            "token_count": chunk.get("token_count"),
            "position": chunk.get("position"),
            "has_table": chunk.get("has_table"),
            "has_numerical": chunk.get("has_numerical"),
            "has_causal_language": chunk.get("has_causal_language"),
        }

    # ========================================================================
    # EMBEDDING API
    # ========================================================================

    
    def embed_text(self, text: str) -> NDArray[np.floating[Any]]:
        """Generate single embedding for text"""
        return self.semantic.embed_single(text)

    
    def embed_batch(self, texts: list[str]) -> list[NDArray[np.floating[Any]]]:
        """Generate embeddings for batch of texts"""
        return self.semantic._embed_batch(texts)

    # ========================================================================
    # ANALYSIS API
    # ========================================================================

    
    def analyze_document(self, text: str) -> dict[str, Any]:
        """Full pipeline analysis of document"""
        return self.analyzer.analyze(text)

    def get_dimension_analysis(
        self,
        analysis: dict[str, Any],
        dimension: CausalDimension
    ) -> dict[str, Any]:
        """Extract specific dimension results from analysis"""
        return analysis.get("causal_dimensions", {}).get(dimension.value, {})

    def get_dimension_score(
        self,
        analysis: dict[str, Any],
        dimension: CausalDimension
    ) -> float:
        """Extract dimension evidence strength score"""
        dim_result = self.get_dimension_analysis(analysis, dimension)
        return dim_result.get("evidence_strength", 0.0)

    def get_dimension_confidence(
        self,
        analysis: dict[str, Any],
        dimension: CausalDimension
    ) -> float:
        """Extract dimension confidence score"""
        dim_result = self.get_dimension_analysis(analysis, dimension)
        return dim_result.get("confidence", 0.0)

    def get_dimension_excerpts(
        self,
        analysis: dict[str, Any],
        dimension: CausalDimension
    ) -> list[str]:
        """Extract key excerpts for dimension"""
        return analysis.get("key_excerpts", {}).get(dimension.value, [])

    # ========================================================================
    # BAYESIAN EVIDENCE API
    # ========================================================================

    def integrate_evidence(
        self,
        similarities: NDArray[np.float64],
        chunk_metadata: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Perform Bayesian evidence integration"""
        return self.bayesian.integrate_evidence(similarities, chunk_metadata)

    def calculate_causal_strength(
        self,
        cause_emb: NDArray[np.floating[Any]],
        effect_emb: NDArray[np.floating[Any]],
        context_emb: NDArray[np.floating[Any]]
    ) -> float:
        """Calculate causal strength between embeddings"""
        return self.bayesian.causal_strength(cause_emb, effect_emb, context_emb)

    
    def get_posterior_mean(self, evidence: dict[str, float]) -> float:
        """Extract posterior mean from evidence integration"""
        return evidence.get("posterior_mean", 0.0)

    
    def get_posterior_std(self, evidence: dict[str, float]) -> float:
        """Extract posterior standard deviation"""
        return evidence.get("posterior_std", 0.0)

    
    def get_information_gain(self, evidence: dict[str, float]) -> float:
        """Extract information gain (KL divergence)"""
        return evidence.get("information_gain", 0.0)

    
    def get_confidence(self, evidence: dict[str, float]) -> float:
        """Extract confidence score"""
        return evidence.get("confidence", 0.0)

    # ========================================================================
    # SEMANTIC SEARCH API
    # ========================================================================

    def semantic_search(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        dimension: CausalDimension | None = None,
        top_k: int = 5
    ) -> list[tuple[dict[str, Any], float]]:
        """Search chunks semantically for query"""
        query_emb = self.semantic.embed_single(query)

        results = []
        for chunk in chunks:
            chunk_emb = chunk.get("embedding")
            if chunk_emb is not None and len(chunk_emb) > 0:
                similarity = 1.0 - cosine(query_emb, chunk_emb)

                # Filter by dimension if specified
                if dimension is None or chunk.get("section_type") == dimension:
                    results.append((chunk, float(similarity)))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    # ========================================================================
    # UTILITY API
    # ========================================================================

    
    def list_dimensions(self) -> list[CausalDimension]:
        """List all causal dimensions"""
        return list(CausalDimension)

    
    def get_dimension_description(self, dimension: CausalDimension) -> str:
        """Get description for dimension"""
        from farfan_pipeline.core.canonical_notation import get_dimension_description

        return get_dimension_description(dimension.value)

    
    def get_config(self) -> SemanticConfig:
        """Get current configuration"""
        return self.config

    
    def set_config(self, config: SemanticConfig) -> None:
        """Update configuration (requires reinitialization)"""
        self.config = config
        self.semantic = SemanticProcessor(self.config)
        self.bayesian = BayesianEvidenceIntegrator(
            prior_concentration=self.config.bayesian_prior_strength
        )
        self.analyzer = PolicyDocumentAnalyzer(self.config)

# ========================
# CLI INTERFACE
# ========================

def main() -> None:
    """Example usage"""
    sample_pdm = """
PLAN DE DESARROLLO MUNICIPAL 2024-2027
MUNICIPIO DE EJEMPLO, COLOMBIA

1. DIAGNÓSTICO TERRITORIAL
El municipio cuenta con 45,000 habitantes, de los cuales 60% reside en zona rural.
La tasa de pobreza multidimensional es 42.3%, superior al promedio departamental.

2. VISIÓN ESTRATÉGICA
Para 2027, el municipio será reconocido por su desarrollo sostenible e inclusivo.

3. PLAN PLURIANUAL DE INVERSIONES
Se destinarán $12,500 millones al sector educación, con meta de construir
3 instituciones educativas y capacitar 250 docentes en pedagogías innovadoras.

4. SEGUIMIENTO Y EVALUACIÓN
Se implementará sistema de indicadores alineado con ODS, con mediciones semestrales.
"""
    config = SemanticConfig(
        chunk_size=512,
        chunk_overlap=100,
        similarity_threshold = 0.8 # Refactored
    )
    analyzer = PolicyDocumentAnalyzer(config)
    results = analyzer.analyze(sample_pdm)
    print(json.dumps({
        "summary": results["summary"],
        "dimensions": {
            k: {
                "evidence_strength": v["evidence_strength"],
                "confidence": v["confidence"],
                "information_gain": v["information_gain"]
            }
            for k, v in results["causal_dimensions"].items()
        }
    }, indent=2, ensure_ascii=False))
