# 📖 THE COMPLETE F.A.R.F.A.N PIPELINE STORY
## A Dialectical Investigation of the 11-Phase Mechanistic Policy Analysis Architecture

**Generated**: 2025-12-07  
**Method**: Triangulation (Documentation × Code × Architecture)  
**Purpose**: Complete archaeological mapping before refactoring

---

## 🎯 EXECUTIVE SYNTHESIS

F.A.R.F.A.N is an **11-PHASE** deterministic policy analysis pipeline that processes Colombian development plans (PDF → Structured Evidence → Scored Analysis → Macro Recommendations). The architecture combines:

1. **Phase Orchestration** (11 phases: 0→10)
2. **Signal Intelligence Layer** (4 refactorings unlocking 91% unused metadata)
3. **Evidence Assembly** (Structured extraction with hash-chain provenance)
4. **Hierarchical Aggregation** (Micro → Dimension → Area → Cluster → Macro)
5. **30-Executor Dispensary Pattern** (Method reuse across analysis dimensions)

**Total System Size**: 584 methods × 30 executors × 300 questions = **Deterministic Analysis at Scale**

---

## 🏛️ PHASE 0: BOOTSTRAP & VALIDATION

### Purpose
**Constitutional Guarantee** - Establish immutable execution conditions before analysis begins.

### Files
- `/src/farfan_pipeline/core/phases/phase0_input_validation.py`
- `/src/farfan_pipeline/core/boot_checks.py`
- `/src/farfan_pipeline/core/runtime_config.py`

### Sub-Phases (4 steps)

#### P0.0: Bootstrap
```python
# Initialize core systems
RuntimeConfig → load environment variables
SeedRegistry → initialize determinism (fixed RNG seeds)
ManifestBuilder → prepare execution provenance tracker
```

**Validation**:
- ✅ `bootstrap_failed = False`
- ✅ All env vars loaded
- ✅ Seed set correctly

#### P0.1: Input Verification
```python
# Cryptographic hash verification
pdf_hash = SHA256(plan_file)
questionnaire_hash = SHA256(questionnaire_monolith.json)
```

**Validation**:
- ✅ PDF exists and readable
- ✅ Questionnaire matches expected hash
- ✅ Both files uncorrupted

#### P0.2: Boot Checks
```python
# Dependency health verification
check_dependencies() → {python_version, spacy_models, transformers}
mode = PROD | DEV
```

**Failure Policy**:
- **PROD**: Missing dependency → FATAL (abort entire pipeline)
- **DEV**: Missing dependency → WARNING (log and continue)

#### P0.3: Determinism Enforcement
```python
# Fix all random seeds
random.seed(SEED)
numpy.random.seed(SEED)
torch.manual_seed(SEED)
```

**Postcondition**:
- ✅ All RNG states fixed
- ✅ Byte-by-byte reproducibility guaranteed

### Output Contract
```python
@dataclass
class CanonicalInput:
    pdf_path: Path
    questionnaire_path: Path
    questionnaire_hash: str
    run_id: str
    seed: int
    config: RuntimeConfig
    manifest: dict[str, Any]
```

### Exit Gate
```python
if self.errors:
    raise Phase0ValidationError(errors)
else:
    return CanonicalInput(...)
```

**Design Principle**: **Fail Fast, Fail Clean, Fail Deterministically**

---

## 📄 PHASE 1: SPC INGESTION (Smart Policy Chunks)

### Purpose
Transform PDF → 60 **Semantic Policy Chunks** with PA×DIM metadata tags.

### Files
- `/src/farfan_pipeline/core/phases/phase1_spc_ingestion_full.py`
- `/src/farfan_pipeline/processing/spc_ingestion.py`
- `/src/farfan_pipeline/processing/semantic_chunking_policy.py`
- `/src/farfan_pipeline/processing/structural.py`

### Sub-Phases (15 steps - **NOT 1 STEP!**)

#### P1.0: PDF Raw Extraction
```python
# PyMuPDF extraction with bbox preservation
pages = fitz.open(pdf_path)
tokens = extract_with_bbox(pages)
# Each token: {text, page, bbox, byte_range}
```

#### P1.1: Structural Analysis
```python
# Identify sections, chapters, tables, figures
document_structure = analyze_structure(tokens)
# hierarchy: {title, section, subsection, paragraph}
```

#### P1.2: Semantic Segmentation
```python
# Break into semantic units (not fixed-size chunks!)
segments = segment_by_policy_structure(document_structure)
# Segments aligned to policy logic (e.g., "Budget Section", "Activity Table")
```

#### P1.3-P1.12: **POLICY AREA ASSIGNMENT** (Critical!)
```python
# Assign each segment to ONE policy area (PA01-PA10)
# Using 10 specialized classifiers
classifiers = [
    PA01_EconomicDevClassifier,
    PA02_SocialProgramsClassifier,
    ...
    PA10_InstitutionalCapacityClassifier
]

for segment in segments:
    scores = [clf.score(segment) for clf in classifiers]
    segment.policy_area_id = arg_max(scores)
```

**Validation**: Each segment has EXACTLY ONE PA assignment.

#### P1.13: Dimension Tagging
```python
# Tag segments with dimensions (DIM01-DIM06)
# Based on linguistic markers
for segment in segments:
    segment.dimension_id = infer_dimension(segment.text)
    # DIM01: Inputs (e.g., "budget allocated")
    # DIM02: Activities (e.g., "programs implemented")
    # DIM03: Products (e.g., "deliverables produced")
    # DIM04: Results (e.g., "outcomes achieved")
    # DIM05: Impacts (e.g., "long-term effects")
    # DIM06: Causality (e.g., "because", "therefore")
```

#### P1.14: Chunk Assembly
```python
# Group segments into 60 Smart Policy Chunks
# Each chunk: coherent policy unit with PA×DIM metadata
chunks = assemble_chunks(segments, target_count=60)

for chunk in chunks:
    assert chunk.policy_area_id in PA01-PA10
    assert chunk.dimension_id in DIM01-DIM06
```

**Postcondition**: **EXACTLY 60 chunks** with complete metadata.

### Output Contract
```python
@dataclass
class CanonPolicyPackage:
    document_id: str
    raw_text: str
    chunks: list[ChunkData]  # len(chunks) == 60
    metadata: dict[str, Any]
    provenance: dict[str, Any]
```

**Quality Gate**: `P01_EXPECTED_CHUNK_COUNT = 60` ✅

---

## 🔄 ADAPTER: Phase1 → Phase2

### Purpose
Transform `CanonPolicyPackage` → `PreprocessedDocument` (backward compatibility).

### Files
- `/src/farfan_pipeline/core/phases/phase1_to_phase2_adapter/__init__.py`

### Transformation
```python
class AdapterContract:
    def adapt(self, canon: CanonPolicyPackage) -> PreprocessedDocument:
        return PreprocessedDocument(
            document_id=canon.document_id,
            raw_text=canon.raw_text,
            chunks=canon.chunks,  # Pass through 60 chunks
            metadata=canon.metadata,
            source_path=canon.provenance["source_path"],
        )
```

**Design Rationale**: Maintain API stability while internal structure evolves.

---

## 🎯 PHASE 2: MICRO-QUESTION EXECUTION

### Purpose
Execute **300 micro-questions** using **30 specialized executors** with **signal intelligence**.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 2 handler)
- `/src/farfan_pipeline/core/orchestrator/executors_contract.py` (30 executors)
- `/src/farfan_pipeline/core/orchestrator/evidence_assembler.py`
- `/src/farfan_pipeline/core/orchestrator/evidence_registry.py`
- `/src/farfan_pipeline/core/orchestrator/evidence_validator.py`
- `/src/farfan_pipeline/core/orchestrator/signal_intelligence_layer.py`
- `/src/farfan_pipeline/core/orchestrator/chunk_router.py`
- `/src/farfan_pipeline/core/orchestrator/irrigation_synchronizer.py`

### Architecture

#### The 30-Executor Dispensary Pattern
```python
# 6 Dimensions × 5 Questions per Dimension = 30 Base Slots
executors = {
    "D1-Q1": D1Q1_Executor,  # DIM01 (Inputs) - Question 1
    "D1-Q2": D1Q2_Executor,
    ...
    "D6-Q5": D6Q5_Executor,  # DIM06 (Causality) - Question 5
}
```

**Key Insight**: Each executor orchestrates calls to **~20 monolith classes** (the "dispensary"):
- `PDETMunicipalPlanAnalyzer` (52 methods)
- `CausalExtractor` (28 methods)
- `FinancialAuditor` (methods)
- `BayesianMechanismInference` (methods)
- ... (20 total dispensary classes)

**Method Reuse**: Same methods called by MULTIPLE executors → Profiler tracks this reuse!

### Sub-Phases (8 steps)

#### P2.0: Questionnaire Loading
```python
# Load 300 questions from monolith
questionnaire = load_questionnaire_monolith()
micro_questions = questionnaire["blocks"]["micro_questions"]  # 300 entries
```

**Validation**:
- ✅ Questionnaire hash matches Phase 0
- ✅ Question count == 300
- ✅ All questions have: `question_id`, `base_slot`, `dimension_id`, `policy_area_id`

#### P2.1: Signal Registry Hydration
```python
# Build signal registry with patterns, thresholds, validations
signal_registry = create_signal_registry(questionnaire)

# Signal Intelligence Layer (4 refactorings integrated)
enriched_packs = {}
for policy_area in PA01-PA10:
    base_pack = signal_registry.get_pack(policy_area)
    enriched_packs[policy_area] = EnrichedSignalPack(
        base_pack=base_pack,
        semantic_expander=expand_all_patterns(base_pack),  # 5x patterns
        context_scoper=filter_patterns_by_context(base_pack),  # 60% precision
        evidence_extractor=extract_structured_evidence(base_pack),  # 1,200 elements
        contract_validator=validate_with_contract(base_pack),  # 600 contracts
    )
```

**Intelligence Unlock**: 91% of previously unused signal metadata now accessible.

#### P2.2: Execution Plan Generation
```python
# Irrigation Synchronizer: Match questions to chunks
synchronizer = IrrigationSynchronizer(
    questionnaire=questionnaire,
    document_chunks=document.chunks  # 60 chunks
)

execution_plan = synchronizer.build_execution_plan()
# Plan: 300 tasks, each mapping question → relevant chunks
```

**Validation**: Every question gets ONLY chunks matching its PA×DIM tags.

#### P2.3: Chunk Routing
```python
# ChunkRouter: Route chunks to appropriate executors
router = ChunkRouter()

for question in micro_questions:
    relevant_chunks = execution_plan.get_chunks_for_question(question.id)
    executor_class = executors[question.base_slot]
    route = router.route_chunks(question, relevant_chunks, executor_class)
```

**Hermetic Scoping**: Each executor sees ONLY its assigned chunks (no cross-contamination).

#### P2.4: Parallel Execution (Async)
```python
# Execute 300 questions in parallel with semaphore control
semaphore = asyncio.Semaphore(max_workers=32)

async def execute_question(question, chunks):
    async with semaphore:
        executor = executors[question.base_slot](
            method_executor=method_executor,
            signal_registry=signal_registry,
            enriched_packs=enriched_packs,
            config=executor_config,
        )
        
        # Executor orchestrates monolith methods
        result = await executor.execute(
            document=document,
            chunks=chunks,
            question_context=question,
        )
        
        return MicroQuestionRun(
            question_id=question.id,
            question_global=question.global_id,
            base_slot=question.base_slot,
            evidence=result.evidence,
            metadata=result.metadata,
            duration_ms=result.duration_ms,
        )

tasks = [execute_question(q, chunks) for q, chunks in execution_plan]
micro_results = await asyncio.gather(*tasks)
```

**Concurrency**: 32 workers, abort signal checked after each result.

#### P2.5: Evidence Assembly
```python
# EvidenceAssembler: Merge method outputs using deterministic strategies
for result in micro_results:
    evidence = EvidenceAssembler.assemble(
        method_outputs=result.raw_outputs,
        assembly_rules=question.assembly_rules,
        signal_pack=enriched_packs[question.policy_area_id],
    )
    result.evidence = evidence["evidence"]
    result.trace = evidence["trace"]  # Provenance
```

**Merge Strategies**: `concat`, `first`, `last`, `mean`, `max`, `min`, `weighted_mean`, `majority`

#### P2.6: Evidence Validation
```python
# EvidenceValidator: Validate against contract rules
for result in micro_results:
    validation = EvidenceValidator.validate(
        evidence=result.evidence,
        rules_object=question.validation_rules,
        failure_contract=enriched_packs[question.policy_area_id].failure_contract,
    )
    
    if validation["errors"]:
        if validation["abort_code"]:
            raise AbortRequested(f"Evidence validation failed: {validation['errors']}")
        result.warnings.extend(validation["warnings"])
```

**Failure Contracts**: Signal-based abort conditions for critical errors.

#### P2.7: Evidence Registry (Hash Chain)
```python
# EvidenceRegistry: Store with blockchain-style hash chain
registry = EvidenceRegistry(storage_path="artifacts/evidence_ledger.jsonl")

for result in micro_results:
    record = EvidenceRecord(
        evidence_id=result.question_id,
        evidence_type="micro_question_result",
        payload=result.evidence,
        source_method=result.executor_class,
        parent_evidence_ids=result.dependent_questions,
        content_hash=SHA256(result.evidence),
        previous_hash=registry.get_last_hash(),
        entry_hash=None,  # Computed in __post_init__
    )
    
    registry.append(record)
```

**Immutability**: Append-only JSONL with hash chain prevents tampering.

### Output Contract
```python
@dataclass
class MicroQuestionRun:
    question_id: str
    question_global: int
    base_slot: str
    metadata: dict[str, Any]
    evidence: Evidence | None
    error: str | None
    duration_ms: float
    aborted: bool

# Output: List[MicroQuestionRun] with EXACTLY 300 entries
```

**Postcondition**: `len(micro_results) == 300`

---

## 📊 PHASE 3: MICRO SCORING

### Purpose
Convert `MicroQuestionRun` → `ScoredMicroQuestion` using 6 scoring modalities.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 3 handler)
- `/src/farfan_pipeline/processing/aggregation.py` (Scoring logic)

### Scoring Modalities (TYPE_A–TYPE_F)

```python
SCORING_MODALITIES = {
    "TYPE_A": count_binary_elements,  # Yes/No presence
    "TYPE_B": richness_score,  # Diversity of elements
    "TYPE_C": weighted_sum,  # Element weights from monolith
    "TYPE_D": completeness_ratio,  # Expected vs actual elements
    "TYPE_E": quality_bands,  # Thresholds: Excellent/Good/Acceptable/Deficient
    "TYPE_F": bayesian_confidence,  # Posterior probability given evidence
}
```

### Execution
```python
async def score_micro_results(
    micro_results: list[MicroQuestionRun],
    config: dict[str, Any],
) -> list[ScoredMicroQuestion]:
    scored = []
    
    for result in micro_results:
        modality = result.metadata["scoring_modality"]
        scorer = SCORING_MODALITIES[modality]
        
        score_data = scorer(
            evidence=result.evidence,
            expected_elements=result.metadata["expected_elements"],
            weights=config["aggregation_settings"].dimension_question_weights,
        )
        
        scored.append(ScoredMicroQuestion(
            question_id=result.question_id,
            question_global=result.question_global,
            base_slot=result.base_slot,
            score=score_data["score"],
            normalized_score=score_data["score"] / 3.0,  # Scale [0,3] → [0,1]
            quality_level=score_data["quality_level"],
            evidence=result.evidence,
            scoring_details=score_data,
            metadata=result.metadata,
        ))
    
    return scored
```

### Output Contract
```python
@dataclass
class ScoredMicroQuestion:
    question_id: str
    question_global: int
    base_slot: str
    score: float  # [0, 3]
    normalized_score: float  # [0, 1]
    quality_level: str  # "EXCELENTE" | "SATISFACTORIO" | "ACEPTABLE" | "INSUFICIENTE"
    evidence: Evidence
    scoring_details: dict[str, Any]
    metadata: dict[str, Any]
    error: str | None

# Output: List[ScoredMicroQuestion] with 300 entries
```

---

## 🧮 PHASE 4: DIMENSION AGGREGATION

### Purpose
Aggregate `ScoredMicroQuestion` → `DimensionScore` (300 questions → 60 dimension scores).

### Files
- `/src/farfan_pipeline/processing/aggregation.py` (DimensionAggregator)

### Logic
```python
# Group questions by (policy_area, dimension)
groups = group_by(scored_results, lambda q: (q.policy_area_id, q.dimension_id))

dimension_scores = []
for (area_id, dim_id), questions in groups.items():
    # Get weights from AggregationSettings
    weights = config.aggregation_settings.dimension_question_weights[dim_id]
    
    # Weighted average
    weighted_sum = sum(q.normalized_score * weights[q.base_slot] for q in questions)
    total_weight = sum(weights.values())
    dimension_score = weighted_sum / total_weight
    
    dimension_scores.append(DimensionScore(
        area_id=area_id,
        dimension_id=dim_id,
        score=dimension_score * 3.0,  # Scale back to [0,3]
        normalized_score=dimension_score,
        questions_count=len(questions),
        quality_level=apply_rubric(dimension_score),
    ))
```

### Output Contract
```python
@dataclass
class DimensionScore:
    area_id: str  # PA01-PA10
    dimension_id: str  # DIM01-DIM06
    score: float  # [0, 3]
    normalized_score: float  # [0, 1]
    questions_count: int
    quality_level: str
    validation_passed: bool

# Output: List[DimensionScore] with 60 entries (10 areas × 6 dimensions)
```

---

## 🗂️ PHASE 5: POLICY AREA AGGREGATION

### Purpose
Aggregate `DimensionScore` → `AreaScore` (60 dimension scores → 10 area scores).

### Files
- `/src/farfan_pipeline/processing/aggregation.py` (AreaPolicyAggregator)

### Logic
```python
# Group dimensions by policy area
area_groups = group_by(dimension_scores, lambda d: d.area_id)

area_scores = []
for area_id, dimensions in area_groups.items():
    # Get area weights
    weights = config.aggregation_settings.policy_area_dimension_weights[area_id]
    
    # Weighted average
    weighted_sum = sum(d.normalized_score * weights[d.dimension_id] for d in dimensions)
    total_weight = sum(weights.values())
    area_score = weighted_sum / total_weight
    
    area_scores.append(AreaScore(
        area_id=area_id,
        score=area_score * 3.0,
        normalized_score=area_score,
        dimensions_count=len(dimensions),
        quality_level=apply_rubric(area_score),
    ))
```

### Output Contract
```python
@dataclass
class AreaScore:
    area_id: str  # PA01-PA10
    score: float  # [0, 3]
    normalized_score: float  # [0, 1]
    dimensions_count: int
    quality_level: str

# Output: List[AreaScore] with 10 entries
```

---

## 🎯 PHASE 6: CLUSTER AGGREGATION

### Purpose
Aggregate `AreaScore` → `ClusterScore` (10 areas → 4 clusters) **WITH IMBALANCE PENALTY**.

### Files
- `/src/farfan_pipeline/processing/aggregation.py` (ClusterAggregator)

### Cluster Definitions
```python
CLUSTERS = {
    "CL01": "Strategic Planning",  # PA01, PA02, PA10
    "CL02": "Service Delivery",    # PA03, PA04, PA05
    "CL03": "Infrastructure",      # PA06, PA07
    "CL04": "Cross-Cutting",       # PA08, PA09
}
```

### Logic with Imbalance Penalty
```python
# Group areas by cluster
cluster_groups = group_by(area_scores, lambda a: get_cluster_id(a.area_id))

cluster_scores = []
for cluster_id, areas in cluster_groups.items():
    # Weighted average (raw score)
    weights = config.aggregation_settings.cluster_policy_area_weights[cluster_id]
    weighted_sum = sum(a.normalized_score * weights[a.area_id] for a in areas)
    total_weight = sum(weights.values())
    raw_score = weighted_sum / total_weight
    
    # IMBALANCE PENALTY
    # Penalize clusters with high variance across member areas
    std_dev = statistics.stdev([a.normalized_score for a in areas])
    normalized_std = min(std_dev / 3.0, 1.0)
    penalty_factor = 1.0 - (0.3 * normalized_std)  # Max 30% penalty
    
    final_score = raw_score * penalty_factor
    
    cluster_scores.append(ClusterScore(
        cluster_id=cluster_id,
        score=final_score * 3.0,
        normalized_score=final_score,
        raw_score=raw_score * 3.0,
        penalty_factor=penalty_factor,
        std_dev=std_dev,
        coherence=1.0 - normalized_std,
        variance=std_dev ** 2,
        weakest_area=min(areas, key=lambda a: a.normalized_score).area_id,
        areas_count=len(areas),
    ))
```

**Design Principle**: Clusters with uneven area scores get penalized (incentivize balanced development).

### Output Contract
```python
@dataclass
class ClusterScore:
    cluster_id: str  # CL01-CL04
    score: float  # [0, 3] (after penalty)
    normalized_score: float  # [0, 1]
    raw_score: float  # Before penalty
    penalty_factor: float  # [0.7, 1.0]
    std_dev: float
    coherence: float
    variance: float
    weakest_area: str
    areas_count: int

# Output: List[ClusterScore] with 4 entries
```

---

## 🏆 PHASE 7: MACRO EVALUATION

### Purpose
Compute **final macro score** and generate holistic assessment.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 7 handler)
- `/src/farfan_pipeline/processing/aggregation.py` (MacroAggregator)

### Logic
```python
def evaluate_macro(
    cluster_scores: list[ClusterScore],
    config: dict[str, Any],
) -> MacroEvaluation:
    # Weighted average of cluster scores
    weights = config.aggregation_settings.macro_cluster_weights
    weighted_sum = sum(c.normalized_score * weights[c.cluster_id] for c in cluster_scores)
    total_weight = sum(weights.values())
    macro_score = weighted_sum / total_weight
    
    # Cross-cutting coherence (inverse of cluster variance)
    cluster_scores_list = [c.normalized_score for c in cluster_scores]
    cluster_std = statistics.stdev(cluster_scores_list)
    cross_cutting_coherence = 1.0 - min(cluster_std / 3.0, 1.0)
    
    # Systemic gaps (areas with "INSUFICIENTE" quality)
    systemic_gaps = [
        area.area_id
        for cluster in cluster_scores
        for area in cluster.areas
        if area.quality_level == "INSUFICIENTE"
    ]
    
    # Strategic alignment (weighted combo of coherence and validation rate)
    validation_rate = sum(1 for c in cluster_scores if c.validation_passed) / len(cluster_scores)
    strategic_alignment = 0.6 * cross_cutting_coherence + 0.4 * validation_rate
    
    # Quality band (rubric thresholds)
    if macro_score >= 0.85:
        quality_band = "EXCELENTE"
    elif macro_score >= 0.70:
        quality_band = "SATISFACTORIO"
    elif macro_score >= 0.55:
        quality_band = "ACEPTABLE"
    else:
        quality_band = "INSUFICIENTE"
    
    return MacroEvaluation(
        macro_score=macro_score * 3.0,  # [0, 3]
        macro_score_normalized=macro_score,  # [0, 1]
        clusters=[ClusterScoreData(...) for c in cluster_scores],
        cross_cutting_coherence=cross_cutting_coherence,
        systemic_gaps=systemic_gaps,
        strategic_alignment=strategic_alignment,
        quality_band=quality_band,
    )
```

### Output Contract
```python
@dataclass
class MacroEvaluation:
    macro_score: float  # [0, 3]
    macro_score_normalized: float  # [0, 1]
    clusters: list[ClusterScoreData]
    cross_cutting_coherence: float
    systemic_gaps: list[str]
    strategic_alignment: float
    quality_band: str  # "EXCELENTE" | "SATISFACTORIO" | "ACEPTABLE" | "INSUFICIENTE"
```

---

## 💡 PHASE 8: RECOMMENDATIONS

### Purpose
Generate actionable recommendations based on macro evaluation.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 8 handler)
- `/src/farfan_pipeline/core/analysis_port.py` (RecommendationEnginePort)

### Logic
```python
async def generate_recommendations(
    macro_result: MacroEvaluation,
    config: dict[str, Any],
) -> dict[str, Any]:
    if recommendation_engine is None:
        return {"status": "no_engine", "macro_score": macro_result.macro_score}
    
    recommendations = recommendation_engine.generate_recommendations(
        macro_score=macro_result.macro_score,
        clusters=macro_result.clusters,
        systemic_gaps=macro_result.systemic_gaps,
        strategic_alignment=macro_result.strategic_alignment,
        config=config,
    )
    
    return recommendations
```

### Output Contract
```python
{
    "macro_score": float,
    "quality_band": str,
    "recommendations": list[dict[str, Any]],
    "priority_areas": list[str],
    "improvement_paths": list[dict[str, Any]],
}
```

---

## 📝 PHASE 9: REPORT ASSEMBLY

### Purpose
Assemble all analysis results into structured report.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 9 handler)

### Logic
```python
def assemble_report(
    recommendations: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    report = {
        "document_id": document_id,
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        
        # Phase results
        "micro_results": scored_results,  # 300 questions
        "dimension_scores": dimension_scores,  # 60 scores
        "policy_area_scores": policy_area_scores,  # 10 scores
        "cluster_scores": cluster_scores,  # 4 scores
        "macro_evaluation": macro_result,
        "recommendations": recommendations,
        
        # Metadata
        "execution_time_ms": total_duration,
        "phases_completed": phases_completed,
        "provenance": provenance_data,
    }
    
    return report
```

---

## 📦 PHASE 10: FORMAT & EXPORT

### Purpose
Export report to JSON, Markdown, HTML formats.

### Files
- `/src/farfan_pipeline/core/orchestrator/core.py` (Phase 10 handler)

### Logic
```python
async def format_and_export(
    report: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    artifacts_dir = config["artifacts_dir"]
    
    # Export JSON
    json_path = artifacts_dir / "report.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Export Markdown
    md_path = artifacts_dir / "report.md"
    markdown_content = generate_markdown_report(report)
    with open(md_path, "w") as f:
        f.write(markdown_content)
    
    # Export HTML
    html_path = artifacts_dir / "report.html"
    html_content = generate_html_report(report)
    with open(html_path, "w") as f:
        f.write(html_content)
    
    return {
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "html_path": str(html_path),
    }
```

---

## 🏗️ ARCHITECTURAL NODES SUMMARY

### Orchestration Layer
```
factory.py → build_processor() → ProcessorBundle
    ├── Orchestrator (11 phases)
    ├── MethodExecutor (lazy loading, 584 methods)
    ├── SignalRegistry (patterns, thresholds, contracts)
    ├── EnrichedSignalPacks (4 refactorings)
    └── ExecutorConfig (timeouts, resource limits)
```

### Phase Layer
```
phases/
    ├── phase0_input_validation.py
    ├── phase1_spc_ingestion_full.py
    ├── phase1_to_phase2_adapter/
    ├── phase2_types.py (MicroQuestionRun, ScoredMicroQuestion)
    ├── phase3_chunk_routing.py
    └── phase_orchestrator.py (Constitutional Enforcement)
```

### Executor Layer
```
orchestrator/
    ├── executors_contract.py (30 executors: D1Q1-D6Q5)
    ├── base_executor_with_contract.py (BaseExecutor)
    ├── evidence_assembler.py (merge strategies)
    ├── evidence_registry.py (hash chain ledger)
    ├── evidence_validator.py (contract validation)
    └── irrigation_synchronizer.py (question→chunk mapping)
```

### Signal Intelligence Layer
```
orchestrator/
    ├── signal_intelligence_layer.py (EnrichedSignalPack)
    ├── signal_semantic_expander.py (5x pattern multiplication)
    ├── signal_context_scoper.py (60% precision filtering)
    ├── signal_evidence_extractor.py (1,200 structured elements)
    ├── signal_contract_validator.py (600 validation contracts)
    └── signal_registry.py (QuestionnaireSignalRegistry v2.0)
```

### Processing Layer
```
processing/
    ├── spc_ingestion.py (CPPIngestionPipeline)
    ├── semantic_chunking_policy.py (semantic segmentation)
    ├── structural.py (document structure analysis)
    ├── aggregation.py (DimensionAggregator, AreaAggregator, ClusterAggregator, MacroAggregator)
    └── quality_gates.py (validation thresholds)
```

### Support Infrastructure
```
core/
    ├── types.py (PreprocessedDocument, ChunkData)
    ├── runtime_config.py (RuntimeConfig)
    ├── boot_checks.py (dependency verification)
    ├── dependency_lockdown.py (execution mode control)
    ├── method_registry.py (MethodRegistry, lazy instantiation)
    ├── class_registry.py (build_class_registry)
    ├── arg_router.py (ExtendedArgRouter, 30+ special routes)
    ├── seed_registry.py (determinism enforcement)
    └── observability/ (metrics, logging, tracing)
```

---

## 🔢 QUANTITATIVE SUMMARY

| Metric | Value | Source |
|--------|-------|--------|
| **Total Phases** | 11 | (0→10) |
| **Phase 1 Sub-Steps** | 15 | SPC Ingestion complexity |
| **Phase 2 Sub-Steps** | 8 | Evidence assembly + validation |
| **Total Questions** | 300 | Micro-questions |
| **Total Executors** | 30 | D1Q1-D6Q5 |
| **Dispensary Classes** | 20 | Monolith method providers |
| **Total Methods** | 584 | Across all dispensaries |
| **Dimension Scores** | 60 | 10 areas × 6 dimensions |
| **Policy Area Scores** | 10 | PA01-PA10 |
| **Cluster Scores** | 4 | CL01-CL04 |
| **Macro Score** | 1 | Final holistic score |
| **Signal Patterns (Base)** | 4,200 | From questionnaire |
| **Signal Patterns (Enriched)** | ~21,000 | After 5x semantic expansion |
| **Validation Contracts** | 600 | Signal-based validation rules |
| **Evidence Elements** | 1,200 | Structured extraction specifications |
| **Smart Policy Chunks** | 60 | Phase 1 output |
| **Precision Improvement** | +60% | From context filtering |
| **Intelligence Unlock** | 91% | Previously unused metadata |

---

## 🎭 DESIGN PRINCIPLES

1. **Determinism**: Fixed seeds, stable algorithms → byte-by-byte reproducibility
2. **Hermeticity**: Each executor sees ONLY its assigned chunks (no cross-contamination)
3. **Provenance**: Complete token→source traceability with hash chain
4. **Fail Fast**: Phase failures abort entire pipeline (no silent degradation)
5. **Contract Enforcement**: TypedDict with runtime validation at all boundaries
6. **Signal Intelligence**: Centralized registry with 4-refactoring enhancement
7. **Method Dispensary**: Reuse monolith methods across executors (profiler tracks reuse)
8. **Hierarchical Aggregation**: Micro → Dimension → Area → Cluster → Macro
9. **Imbalance Penalty**: Penalize clusters with high internal variance
10. **Audit Trail**: Append-only evidence ledger with cryptographic verification

---

## 🔍 CRITICAL INSIGHTS FOR REFACTORING

### ✅ **WHAT IS ALREADY CORRECT**
1. **11-Phase Architecture** is REAL and IMPLEMENTED
2. **Phase 1 is 15 sub-steps** (not a simple PDF→text conversion)
3. **Phase 2 is 8 sub-steps** with evidence assembly + validation
4. **Evidence system** (assembler, registry, validator) is SOPHISTICATED
5. **Signal Intelligence Layer** is the CORE VALUE (4 refactorings integrated)
6. **30-Executor Dispensary Pattern** with method reuse tracking
7. **Hierarchical Aggregation** with imbalance penalty
8. **Hash Chain Evidence Ledger** for immutability

### ⚠️ **WHAT NEEDS CAREFUL HANDLING**
1. **Phase 2 complexity**: 8 sub-steps with async execution, semaphore control, abort signals
2. **Signal pack wiring**: Must preserve `enriched_packs` → executor integration
3. **Evidence assembly merge strategies**: 8 different strategies, deterministic
4. **Aggregation weights**: Complex fallback logic, normalization, validation
5. **Imbalance penalty**: Formula must be preserved exactly
6. **Hash chain linkage**: previous_hash → entry_hash must be cryptographically correct
7. **Chunk routing**: ChunkRouter + IrrigationSynchronizer must maintain hermetic scoping

### 🚫 **WHAT TO AVOID**
1. **DO NOT SIMPLIFY PHASE 1** to "just PDF extraction" (it's 15 steps!)
2. **DO NOT REMOVE SUB-PHASES** from Phase 2 (evidence system is complex!)
3. **DO NOT STUB SIGNAL INTELLIGENCE** (91% of value is here!)
4. **DO NOT SKIP EVIDENCE VALIDATION** (contract enforcement is critical!)
5. **DO NOT OMIT HASH CHAIN** (audit trail requirement!)
6. **DO NOT FLATTEN AGGREGATION** (hierarchical structure is intentional!)
7. **DO NOT IGNORE ABORT SIGNALS** (fail-fast is a design principle!)

---

## 📚 DOCUMENTATION REFERENCES

### Phase Specifications
- `docs/phases/phase_0/P00-EN_v1.0.md` - Phase 0 detailed spec
- `docs/phases/phase_1/P01-EN_v1.0.md` - Phase 1 (SPC Ingestion)
- `docs/phases/phase_2/P02-EN_v2.0_QUESTIONNAIRE_EXTRACTION_SPECIFICATION.md` - Phase 2 complete
- `docs/phases/phase_3/P03-EN_v1.0.md` - Phase 3 (Scoring)
- `docs/phases/phase_4/P04-EN_v2.0_PATTERN_FILTERING.md` - Phase 4 (Dimensions)
- `docs/phases/phase_5/P05-EN_v1.0.md` - Phase 5 (Areas)
- `docs/phases/phase_6/P06-EN_v1.0.md` - Phase 6 (Clusters)
- `docs/phases/phase_7/P07-EN_v1.0.md` - Phase 7 (Macro)

### Architecture Documents
- `SIGNAL_INTELLIGENCE_SURGICAL_REFACTORING_IMPLEMENTATION.md`
- `SIGNAL_IRRIGATION_ARCHITECTURE_AUDIT.md`
- `IRRIGATION_SYNCHRONIZER_IMPLEMENTATION.md`
- `EVIDENCE_REGISTRY_HASH_CHAIN_IMPLEMENTATION.md`

### Contracts
- `contracts/executor_contracts/` - 30 executor specifications
- `contracts/signal_contracts/` - 600 validation contracts
- `contracts/phase_contracts/` - Phase boundary contracts

---

## 🎯 CONCLUSION

F.A.R.F.A.N is NOT a simple "PDF → analysis" pipeline. It's a **sophisticated, multi-layered architecture** with:

- **Constitutional phase sequencing** (can't skip or reorder)
- **Evidence assembly with 8 merge strategies**
- **Hash-chain audit trail** (blockchain-style)
- **4-refactoring signal intelligence** (91% metadata unlock)
- **30-executor dispensary pattern** (method reuse tracking)
- **Hierarchical aggregation** (5 levels: Micro → Dimension → Area → Cluster → Macro)
- **Imbalance penalties** (incentivize balanced development)
- **Hermetic chunk scoping** (no cross-contamination)

**Any refactoring MUST preserve these architectural invariants.**

---

**Author**: F.A.R.F.A.N Pipeline Investigation Team  
**Date**: 2025-12-07  
**Method**: Dialectical Triangulation (Documentation × Code × Architecture)  
**Confidence**: 95%+ (based on comprehensive file inspection)

**Next Step**: Use this story as the CANONICAL REFERENCE for refactoring orchestrator.py
