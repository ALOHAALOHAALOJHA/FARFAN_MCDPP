# F.A.R.F.A.N Phase 9 Template Catalogue

## Overview

This catalogue provides a sophisticated collection of report templates for Phase 9, each designed for specific audiences and use cases. All templates are fully integrated with the F.A.R.F.A.N pipeline's data structures including Phase 2 (V4 contracts, Carver, Nexus) and scoring/aggregation systems.

---

## Template Index

| Template | File | Purpose | Audience | Page Layout |
|----------|------|---------|----------|-------------|
| **Enhanced Report** | `report_enhanced.html.j2` | Comprehensive full-featured report | General stakeholders | A4 Portrait |
| **Executive Dashboard** | `executive_dashboard.html.j2` | High-level KPI overview | C-level executives | A4 Landscape |
| **Technical Deep-Dive** | `technical_deep_dive.html.j2` | Detailed technical analysis | Data scientists, auditors | A4 Portrait |
| **Original Report** | `report.html.j2` | Legacy template (simple) | Basic reporting | A4 Portrait |

---

## Template Details

### 1. Enhanced Report (`report_enhanced.html.j2`)

**Purpose:** Production-grade comprehensive policy analysis report with SOTA features

**Key Features:**
- ✨ Modern gradient design with professional color scheme
- 📊 KPI cards with visual metrics
- 🔷 Meso cluster cards with detailed breakdowns
- 🔬 Micro-question analysis with Carver synthesis display
- 📝 Evidence extraction visualization
- 🏷️ Pattern tag clouds
- 🔐 Cryptographic verification panel
- ⚖️ Penalty breakdown with visual bars
- 🎯 Strategic recommendations with severity indicators
- 📈 Quality level badges

**Data Integration:**
- **Phase 2 Alignment:**
  - Displays V4 contract types and modalities
  - Shows Carver doctoral answers with proper formatting
  - Evidence items from Nexus assembly
  - Pattern application statistics from signal registry

- **Scoring & Aggregation:**
  - Macro summary with Bayesian posterior
  - Meso cluster scores with dispersion metrics
  - Micro question scores with quality levels (EXCELENTE, BUENO, ACEPTABLE, INSUFICIENTE)
  - Penalty breakdowns (coverage, dispersion, contradiction)

**Visual Elements:**
- Gradient cover page with logo
- Color-coded score circles
- Progress bars for penalties
- Metadata cards in grid layout
- Evidence boxes with left border accent
- Pattern tags with monospace font
- Dark provenance panel with hash displays

**Best For:**
- Comprehensive policy analysis reports
- Stakeholder presentations
- Formal documentation
- PDF archival

**Usage:**
```python
from farfan_pipeline.phases.Phase_9.report_generator import ReportGenerator

generator = ReportGenerator(output_dir="./reports", plan_name="my_plan")
artifacts = generator.generate_all(
    report=analysis_report,
    template_name="report_enhanced"
)
```

---

### 2. Executive Dashboard (`executive_dashboard.html.j2`)

**Purpose:** Single-page high-density dashboard for executive decision making

**Key Features:**
- 📊 **4 KPI Cards:**
  - Overall Score with trend indicators
  - Contradictions count with status
  - Coverage percentage
  - Total penalty adjustment

- 🎯 **Risk Matrix:** 3×3 grid with color-coded risk levels (Critical/High/Medium/Low)
- 🔷 **Cluster Performance:** Bar charts for each meso cluster
- 📊 **Quality Distribution:** Vertical bar chart showing EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE breakdown
- 🗺️ **Policy Area Heatmap:** 10-cell grid showing average scores per policy area (PA01-PA10)
- 🎯 **Top 5 Recommendations:** Compact list with icons and severity badges

**Layout:**
- Landscape orientation (A4)
- Grid-based responsive design (12-column)
- High information density
- Optimized for single-page printing

**Data Integration:**
- **Macro Level:** Overall scores, penalties, contradictions
- **Meso Level:** Cluster scores with progress bars
- **Micro Level:** Quality distribution statistics, policy area averages

**Visual Design:**
- Header with gradient background (blue theme)
- KPI cards with large numbers and trend arrows
- Color-coded cells (green/cyan/amber/red)
- Compact font sizes (9pt base)
- Shadow effects for depth

**Best For:**
- Board meetings
- Executive briefings
- Quick status checks
- Decision support

**When to Use:**
- When time is limited
- For non-technical audiences
- When visual impact is priority
- For monitoring dashboards

---

### 3. Technical Deep-Dive (`technical_deep_dive.html.j2`)

**Purpose:** Comprehensive technical analysis for auditors, data scientists, and methodology reviewers

**Key Features:**
- 🖥️ **Terminal-Style Header:** Monospace font with green-on-black aesthetic
- 🔐 **Cryptographic Verification Table:** SHA-256 hashes for monolith, report, evidence chain
- 📊 **Macro-Level Analysis:**
  - Detailed penalty calculation formulas
  - Bayesian posterior computation breakdown
  - Contradiction analysis

- 🔷 **Meso-Level Analysis:**
  - Cluster performance matrix (7 columns)
  - Dispersion metrics in JSON format
  - Statistical summaries (mean, min, max, median)

- 🔬 **Micro-Level Analysis:**
  - Quality distribution table with percentages
  - Scoring modality breakdown (TYPE_A through TYPE_F)
  - Pattern usage statistics
  - Detailed question samples (first 10) with full metadata

- 📝 **Code Blocks:** JSON snippets showing data structures
- 🔢 **Formulas:** Mathematical expressions for calculations
- 📋 **Comprehensive Tables:** 8pt font with dense data

**Data Integration:**
- **Phase 2:**
  - Contract type display
  - Scoring modality taxonomy (TYPE_A-F descriptions)
  - Evidence chain hash from Nexus
  - Pattern application counts

- **Aggregation:**
  - Complete penalty breakdown with 6-decimal precision
  - Cluster dispersion metrics (variance, std, etc.)
  - Statistical distributions

**Visual Design:**
- Monospace fonts (Consolas, Monaco, Courier)
- Green-on-black code blocks
- Professional blue headers (Segoe UI)
- High-density tables (8pt font)
- Technical aesthetic

**Best For:**
- Technical audits
- Methodology validation
- Peer review
- Research documentation
- Reproducibility verification

**When to Use:**
- When full transparency is required
- For technical stakeholders
- When debugging or validating results
- For academic/research contexts

---

### 4. Original Report (`report.html.j2`)

**Purpose:** Legacy baseline template with essential features

**Key Features:**
- Simple cover page
- Basic metadata table
- Executive summary box
- Meso cluster table
- First 10 questions detailed + summary table for rest
- Basic styling with Segoe UI font
- Provenance hashes

**Best For:**
- Basic reporting needs
- Legacy compatibility
- Minimal styling preference

---

## Data Structure Reference

All templates have access to the following Jinja2 variables:

### Core Variables

```jinja2
{{ metadata }}              # ReportMetadata object
{{ macro_summary }}         # MacroSummary object (optional)
{{ meso_clusters }}         # dict[str, MesoCluster]
{{ micro_analyses }}        # list[QuestionAnalysis]
{{ report_digest }}         # SHA-256 hash string
{{ evidence_chain_hash }}   # SHA-256 hash string (optional)
```

### ReportMetadata Fields

```python
metadata.report_id          # str: Unique report identifier
metadata.generated_at       # str: ISO-8601 timestamp (UTC)
metadata.monolith_version   # str: Questionnaire version
metadata.monolith_hash      # str: SHA-256 (64 chars)
metadata.plan_name          # str: Development plan name
metadata.total_questions    # int: Total questions in monolith
metadata.questions_analyzed # int: Questions with results
metadata.correlation_id     # str: UUID for request tracking
metadata.metadata           # dict: Additional metadata (SISAS, etc.)
```

### MacroSummary Fields

```python
macro_summary.overall_posterior      # float [0.0, 1.0]: Raw Bayesian estimate
macro_summary.adjusted_score         # float [0.0, 1.0]: Post-penalty score
macro_summary.coverage_penalty       # float [0.0, 1.0]: Coverage adjustment
macro_summary.dispersion_penalty     # float [0.0, 1.0]: Variance adjustment
macro_summary.contradiction_penalty  # float [0.0, 1.0]: Conflict adjustment
macro_summary.total_penalty          # float [0.0, 1.0]: Sum of penalties
macro_summary.contradiction_count    # int: Number of contradictions
macro_summary.recommendations        # list[Recommendation]: Strategic recs
```

### MesoCluster Fields

```python
cluster.cluster_id           # str: Cluster identifier
cluster.raw_meso_score       # float [0.0, 1.0]: Pre-penalty score
cluster.adjusted_score       # float [0.0, 1.0]: Post-penalty score
cluster.dispersion_penalty   # float [0.0, 1.0]: Variance penalty
cluster.peer_penalty         # float [0.0, 1.0]: Cross-cluster penalty
cluster.total_penalty        # float [0.0, 1.0]: Combined penalties
cluster.dispersion_metrics   # dict[str, float]: Statistical metrics
cluster.micro_scores         # list[float]: Underlying question scores
```

### QuestionAnalysis Fields

```python
analysis.question_id         # str: Question identifier (e.g., "Q005_PA10")
analysis.question_global     # int: Global question number [1-300]
analysis.base_slot           # str: Slot identifier (e.g., "D1-Q5")
analysis.scoring_modality    # str|None: TYPE_A through TYPE_F
analysis.score               # float|None [0.0, 1.0]: Question score
analysis.evidence            # list[str]: Evidence items extracted
analysis.patterns_applied    # list[str]: Pattern IDs used
analysis.recommendation      # str|None: Question-level recommendation
analysis.human_answer        # str|None: Carver doctoral synthesis
analysis.metadata            # dict: {dimension, policy_area, ...}
```

### Recommendation Fields

```python
rec.type        # str: Type (RISK, PRIORITY, OMISSION, etc.)
rec.severity    # str: CRITICAL, HIGH, MEDIUM, LOW, INFO
rec.description # str: Actionable recommendation text
rec.source      # str: Origin level (micro, meso, macro)
```

---

## Quality Level Thresholds

All templates use consistent quality classification:

| Level | Score Range (0-1) | Score Range (%) | Color |
|-------|-------------------|-----------------|-------|
| **EXCELENTE** | [0.85, 1.00] | [85%, 100%] | Green (#28a745) |
| **BUENO** | [0.70, 0.85) | [70%, 85%) | Cyan (#17a2b8) |
| **ACEPTABLE** | [0.55, 0.70) | [55%, 70%) | Amber (#ffc107) |
| **INSUFICIENTE** | [0.00, 0.55) | [0%, 55%) | Red (#dc3545) |

---

## Color Scheme Reference

All templates follow the F.A.R.F.A.N brand color palette:

```css
--primary-blue: #2c5aa0      /* Main brand color */
--secondary-blue: #4a7dc7    /* Lighter accent */
--accent-gold: #d4af37       /* Highlights, borders */
--success-green: #28a745     /* Excellent quality */
--warning-amber: #ffc107     /* Acceptable quality */
--danger-red: #dc3545        /* Critical issues */
--info-cyan: #17a2b8         /* Good quality */
--neutral-gray: #6c757d      /* Secondary info */
```

---

## Template Selection Guide

### Decision Tree

```
┌─ Need single-page overview? ───→ Executive Dashboard
│
├─ Need technical details? ───────→ Technical Deep-Dive
│
├─ Need comprehensive report? ────→ Enhanced Report
│
└─ Need basic report? ────────────→ Original Report
```

### By Audience

| Audience | Primary Template | Secondary Template |
|----------|-----------------|-------------------|
| **C-Level Executives** | Executive Dashboard | Enhanced Report |
| **Policy Makers** | Enhanced Report | Executive Dashboard |
| **Data Scientists** | Technical Deep-Dive | - |
| **Auditors** | Technical Deep-Dive | Enhanced Report |
| **General Stakeholders** | Enhanced Report | - |
| **Technical Reviewers** | Technical Deep-Dive | - |

### By Use Case

| Use Case | Template |
|----------|----------|
| Board Presentation | Executive Dashboard |
| Formal Documentation | Enhanced Report |
| Methodology Validation | Technical Deep-Dive |
| Peer Review | Technical Deep-Dive |
| Stakeholder Communication | Enhanced Report |
| Quick Status Check | Executive Dashboard |
| PDF Archival | Enhanced Report |
| Research Publication | Technical Deep-Dive |

---

## Implementation Notes

### Adding a New Template

1. Create Jinja2 template in `src/farfan_pipeline/phases/Phase_9/templates/`
2. Use `.html.j2` extension
3. Ensure compatibility with `AnalysisReport` data structure
4. Follow F.A.R.F.A.N color scheme
5. Include cryptographic verification section
6. Test with sample data
7. Update this catalogue
8. Update `report_generator.py` template selection logic

### Template Best Practices

- **Print Optimization:** Use `@page` rules for PDF generation
- **Page Breaks:** Use `page-break-after: avoid` on headers
- **Font Sizes:** Base at 9-10pt for readability in PDF
- **Color Contrast:** Ensure WCAG AA compliance
- **Monospace Fonts:** Use for hashes, IDs, code blocks
- **Null Safety:** Always check `if variable` before accessing
- **Jinja2 Filters:** Use built-in filters for formatting (`round`, `length`, etc.)

### Jinja2 Filter Examples

```jinja2
{# Round to 2 decimals #}
{{ score | round(2) }}

{# Format as percentage #}
{{ (score * 100) | round(1) }}%

{# List length #}
{{ evidence | length }}

{# Conditional display #}
{% if score is not none %}{{ score }}{% else %}N/A{% endif %}

{# Slice first 10 items #}
{% for item in items[:10] %}

{# Filter by attribute #}
{% set excellent = analyses | selectattr('score', 'ge', 0.85) | list %}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **4.0.0** | 2026-01-10 | Initial sophisticated template catalogue |
| | | - Enhanced Report with SOTA features |
| | | - Executive Dashboard (landscape) |
| | | - Technical Deep-Dive for auditors |
| | | - Full Phase 2 integration (V4, Carver, Nexus) |
| | | - Scoring/aggregation alignment |

---

## Support & Feedback

For questions, feature requests, or bug reports related to templates:

1. Check this catalogue first
2. Review `report_assembly.py` for data structure details
3. Inspect template source code for implementation
4. Test with sample data using `report_generator.py`

**Technical Contact:** F.A.R.F.A.N Pipeline Team
**Documentation:** This file (`TEMPLATE_CATALOGUE.md`)

---

## License & Credits

**Framework:** F.A.R.F.A.N v4.0
**Templates:** Phase 9 Reporting Module
**Design:** Aligned with Phase 2 epistemological foundations (N1-N4)
**Integration:** V4 Contracts, Carver Synthesizer, Evidence Nexus, SISAS Signal Registry

---

*Last Updated: 2026-01-10*
*F.A.R.F.A.N - Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives*
