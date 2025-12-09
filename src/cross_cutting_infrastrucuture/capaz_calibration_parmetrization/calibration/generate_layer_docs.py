"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Automated Layer Documentation Generator

Consumes LayerMetadataRegistry to produce comprehensive Markdown documentation
for each calibration layer including:
- Mathematical formula rendering with LaTeX
- Component breakdowns with weight tables
- Threshold specifications with rationale
- Implementation status and LOC metrics
- Cross-references to production modules and test coverage

Authority: Doctrina SIN_CARRETA
Compliance: SUPERPROMPT Three-Pillar Calibration System
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict


class LayerMetadata(TypedDict):
    symbol: str
    name: str
    description: str
    formula: str
    formula_latex: str
    components: dict[str, str]
    weights: dict[str, Any]
    thresholds: dict[str, Any]
    production_path: str
    lines_of_code: int
    implementation_status: str
    test_coverage_path: str
    cohort_id: str
    creation_date: str
    wave_version: str


@dataclass(frozen=True)
class LayerMetadataRegistry:
    """
    Registry containing metadata for all calibration layers.

    Attributes:
        layers: Dict mapping layer symbol (e.g., "@b") to LayerMetadata
        cohort_id: COHORT identifier
        wave_version: Implementation wave version
        metadata: Additional registry metadata
    """
    layers: dict[str, LayerMetadata]
    cohort_id: str
    wave_version: str
    metadata: dict[str, Any]

    @classmethod
    def from_json(cls, json_path: Path | str) -> LayerMetadataRegistry:
        """
        Load LayerMetadataRegistry from JSON file.

        Args:
            json_path: Path to JSON configuration file

        Returns:
            Initialized LayerMetadataRegistry
        """
        with open(json_path) as f:
            data = json.load(f)

        return cls(
            layers=data["layers"],
            cohort_id=data["cohort_id"],
            wave_version=data["wave_version"],
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_calibration_configs(cls, calibration_dir: Path | str) -> LayerMetadataRegistry:
        """
        Build LayerMetadataRegistry by scanning calibration configuration files.

        Args:
            calibration_dir: Path to calibration configuration directory

        Returns:
            Initialized LayerMetadataRegistry with discovered layer metadata
        """
        calibration_path = Path(calibration_dir)

        layers: dict[str, LayerMetadata] = {}

        base_layer_meta = cls._extract_base_layer_metadata(calibration_path)
        if base_layer_meta:
            layers["@b"] = base_layer_meta

        chain_layer_meta = cls._extract_chain_layer_metadata(calibration_path)
        if chain_layer_meta:
            layers["@chain"] = chain_layer_meta

        contextual_meta = cls._extract_contextual_layers_metadata(calibration_path)
        layers.update(contextual_meta)

        congruence_meta = cls._extract_congruence_layer_metadata(calibration_path)
        if congruence_meta:
            layers["@C"] = congruence_meta

        unit_layer_meta = cls._extract_unit_layer_metadata(calibration_path)
        if unit_layer_meta:
            layers["@u"] = unit_layer_meta

        meta_layer_meta = cls._extract_meta_layer_metadata(calibration_path)
        if meta_layer_meta:
            layers["@m"] = meta_layer_meta

        return cls(
            layers=layers,
            cohort_id="COHORT_2024",
            wave_version="REFACTOR_WAVE_2024_12",
            metadata={
                "generated_from": str(calibration_path),
                "total_layers": len(layers),
            },
        )

    @staticmethod
    def _extract_base_layer_metadata(calibration_path: Path) -> LayerMetadata | None:
        """Extract @b base layer metadata."""
        intrinsic_path = calibration_path / "COHORT_2024_intrinsic_calibration.json"

        if not intrinsic_path.exists():
            return None

        with open(intrinsic_path) as f:
            data = json.load(f)

        base_layer = data.get("base_layer", {})
        components = data.get("components", {})

        return LayerMetadata(
            symbol="@b",
            name="Base Layer",
            description="Intrinsic quality of method code - theory, implementation, and deployment",
            formula="b = 0.40·b_theory + 0.35·b_impl + 0.25·b_deploy",
            formula_latex=r"b = 0.40 \cdot b_{\text{theory}} + 0.35 \cdot b_{\text{impl}} + 0.25 \cdot b_{\text{deploy}}",
            components={
                "b_theory": "Conceptual and methodological soundness",
                "b_impl": "Code implementation quality",
                "b_deploy": "Operational stability and reliability",
            },
            weights={
                "linear": base_layer.get("aggregation", {}).get("weights", {}),
                "components": {k: v.get("weight", 0.0) for k, v in components.items()},
            },
            thresholds={
                "min_score_SCORE_Q": data.get("role_requirements", {}).get("SCORE_Q", {}).get("min_base_score", 0.7),
                "min_score_INGEST_PDM": data.get("role_requirements", {}).get("INGEST_PDM", {}).get("min_base_score", 0.6),
            },
            production_path="src.orchestration.calibration_orchestrator.BaseLayerEvaluator",
            lines_of_code=30,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_orchestrator.py",
            cohort_id=data.get("_cohort_metadata", {}).get("cohort_id", "COHORT_2024"),
            creation_date=data.get("_cohort_metadata", {}).get("creation_date", "2024-12-15T00:00:00+00:00"),
            wave_version=data.get("_cohort_metadata", {}).get("wave_version", "REFACTOR_WAVE_2024_12"),
        )

    @staticmethod
    def _extract_chain_layer_metadata(calibration_path: Path) -> LayerMetadata | None:
        """Extract @chain layer metadata."""
        chain_path = calibration_path / "COHORT_2024_chain_layer.py"

        if not chain_path.exists():
            return None

        return LayerMetadata(
            symbol="@chain",
            name="Chain Layer",
            description="Method wiring and orchestration compatibility via contract validation",
            formula="chain = discrete({0.0, 0.3, 0.6, 0.8, 1.0}) based on contract satisfaction",
            formula_latex=r"\text{chain} \in \{0.0, 0.3, 0.6, 0.8, 1.0\} \text{ (discrete scoring)}",
            components={
                "missing_required": "Hard failure - required input unavailable or schema incompatible",
                "missing_critical": "Critical optional input missing",
                "missing_optional": "Optional input missing with ratio >50%",
                "warnings": "Soft schema violations",
            },
            weights={
                "discrete_mapping": {
                    "0.0": "missing_required OR schema_incompatible",
                    "0.3": "missing_critical",
                    "0.6": "many_missing (ratio>0.5) OR soft_schema_violation",
                    "0.8": "all contracts pass AND warnings exist",
                    "1.0": "all inputs present AND no warnings",
                }
            },
            thresholds={
                "missing_optional_ratio": 0.5,
                "weakest_link_principle": "chain_quality = min(method_scores)",
            },
            production_path="src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_chain_layer.ChainLayerEvaluator",
            lines_of_code=332,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_chain_layer.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

    @staticmethod
    def _extract_contextual_layers_metadata(calibration_path: Path) -> dict[str, LayerMetadata]:
        """Extract @q, @d, @p contextual layer metadata."""
        contextual_path = calibration_path / "COHORT_2024_method_compatibility.json"

        layers = {}

        if not contextual_path.exists():
            return layers

        priority_mapping = {
            "Priority 3 (CRÍTICO)": 1.0,
            "Priority 2 (IMPORTANTE)": 0.7,
            "Priority 1 (COMPLEMENTARIO)": 0.3,
            "Unmapped": 0.1,
        }

        layers["@q"] = LayerMetadata(
            symbol="@q",
            name="Question Layer",
            description="Method compatibility with specific questionnaire questions",
            formula="q = compatibility_score(method_id, question_id)",
            formula_latex=r"q = \text{CompatibilityScore}(I, Q) \in [0.0, 1.0]",
            components={
                "priority_3": "Critical compatibility (CRÍTICO)",
                "priority_2": "Important compatibility (IMPORTANTE)",
                "priority_1": "Complementary compatibility (COMPLEMENTARIO)",
                "unmapped": "Method not declared for question",
            },
            weights={
                "priority_mapping": priority_mapping,
            },
            thresholds={
                "unmapped_penalty": 0.1,
                "anti_universality_threshold": 0.9,
                "anti_universality_note": "No method can score >0.9 across all contexts",
            },
            production_path="src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers.QuestionEvaluator",
            lines_of_code=320,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_contextual_layers.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

        layers["@d"] = LayerMetadata(
            symbol="@d",
            name="Dimension Layer",
            description="Method compatibility with policy dimensions (DIM01-DIM06)",
            formula="d = compatibility_score(method_id, dimension_id)",
            formula_latex=r"d = \text{CompatibilityScore}(I, D) \in [0.0, 1.0]",
            components={
                "priority_3": "Critical compatibility (CRÍTICO)",
                "priority_2": "Important compatibility (IMPORTANTE)",
                "priority_1": "Complementary compatibility (COMPLEMENTARIO)",
                "unmapped": "Method not declared for dimension",
            },
            weights={
                "priority_mapping": priority_mapping,
            },
            thresholds={
                "unmapped_penalty": 0.1,
                "anti_universality_threshold": 0.9,
            },
            production_path="src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers.DimensionEvaluator",
            lines_of_code=320,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_contextual_layers.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

        layers["@p"] = LayerMetadata(
            symbol="@p",
            name="Policy Layer",
            description="Method compatibility with policy areas (PA01-PA10)",
            formula="p = compatibility_score(method_id, policy_id)",
            formula_latex=r"p = \text{CompatibilityScore}(I, P) \in [0.0, 1.0]",
            components={
                "priority_3": "Critical compatibility (CRÍTICO)",
                "priority_2": "Important compatibility (IMPORTANTE)",
                "priority_1": "Complementary compatibility (COMPLEMENTARIO)",
                "unmapped": "Method not declared for policy",
            },
            weights={
                "priority_mapping": priority_mapping,
            },
            thresholds={
                "unmapped_penalty": 0.1,
                "anti_universality_threshold": 0.9,
            },
            production_path="src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers.PolicyEvaluator",
            lines_of_code=320,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_contextual_layers.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

        return layers

    @staticmethod
    def _extract_congruence_layer_metadata(calibration_path: Path) -> LayerMetadata | None:
        """Extract @C congruence layer metadata."""
        congruence_path = calibration_path / "COHORT_2024_congruence_layer.py"

        if not congruence_path.exists():
            return None

        return LayerMetadata(
            symbol="@C",
            name="Congruence Layer",
            description="Contract compliance evaluation - output range, semantic alignment, fusion validity",
            formula="C_play = 0.4·c_scale + 0.35·c_sem + 0.25·c_fusion",
            formula_latex=r"C_{\text{play}} = 0.4 \cdot c_{\text{scale}} + 0.35 \cdot c_{\text{sem}} + 0.25 \cdot c_{\text{fusion}}",
            components={
                "c_scale": "Output range compatibility (min/max overlap analysis)",
                "c_sem": "Semantic tag alignment (Jaccard similarity >= 0.3 threshold)",
                "c_fusion": "Fusion rule validity (aggregation operators)",
            },
            weights={
                "w_scale": 0.4,
                "w_semantic": 0.35,
                "w_fusion": 0.25,
            },
            thresholds={
                "min_jaccard_similarity": 0.3,
                "max_range_mismatch_ratio": 0.5,
                "min_fusion_validity_score": 0.6,
            },
            production_path="src.orchestration.congruence_layer.CongruenceLayerEvaluator",
            lines_of_code=220,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_congruence_layer.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

    @staticmethod
    def _extract_unit_layer_metadata(calibration_path: Path) -> LayerMetadata | None:
        """Extract @u unit layer metadata."""
        unit_path = calibration_path / "COHORT_2024_unit_layer.py"

        if not unit_path.exists():
            return None

        return LayerMetadata(
            symbol="@u",
            name="Unit Layer",
            description="PDT structure analysis - structural compliance, mandatory sections, indicator quality, PPI completeness",
            formula="U = geometric_mean(S, M, gated(I), gated(P)) × (1 - anti_gaming_penalty)",
            formula_latex=r"U = \sqrt[4]{S \cdot M \cdot I_{\text{gated}} \cdot P_{\text{gated}}} \times (1 - \text{penalty})",
            components={
                "S": "Structural Compliance: 0.5·B_cov + 0.25·H + 0.25·O",
                "M": "Mandatory Sections: Critical sections with 2.0x weights",
                "I": "Indicator Quality (gated): 0.4·struct + 0.35·link + 0.25·logic",
                "P": "PPI Completeness (gated): 0.3·presence + 0.4·struct + 0.3·consistency",
            },
            weights={
                "S": {"B_cov": 0.5, "H": 0.25, "O": 0.25},
                "M": {
                    "diagnostico": 2.0,
                    "estrategica": 2.0,
                    "ppi": 2.0,
                    "seguimiento": 1.0,
                },
                "I": {"struct": 0.4, "link": 0.35, "logic": 0.25},
                "P": {"presence": 0.3, "struct": 0.4, "consistency": 0.3},
            },
            thresholds={
                "gate_threshold_I": 0.5,
                "gate_threshold_P": 0.4,
                "anti_gaming_boilerplate_threshold": 0.7,
                "token_thresholds": {
                    "excellent": 10000,
                    "good": 5000,
                    "acceptable": 2000,
                },
            },
            production_path="src.orchestration.unit_layer.UnitLayerEvaluator",
            lines_of_code=489,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_unit_layer.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )

    @staticmethod
    def _extract_meta_layer_metadata(calibration_path: Path) -> LayerMetadata | None:
        """Extract @m meta layer metadata."""
        meta_path = calibration_path / "COHORT_2024_meta_layer.py"

        if not meta_path.exists():
            return None

        return LayerMetadata(
            symbol="@m",
            name="Meta Layer",
            description="Governance maturity - transparency, governance artifacts, cost efficiency",
            formula="m = 0.40·transparency + 0.35·governance + 0.25·cost_efficiency",
            formula_latex=r"m = 0.40 \cdot t + 0.35 \cdot g + 0.25 \cdot c",
            components={
                "transparency": "Formula export, trace completeness, log conformance",
                "governance": "Version tag, config hash, signature",
                "cost_efficiency": "Execution time, memory usage",
            },
            weights={
                "w_transparency": 0.40,
                "w_governance": 0.35,
                "w_cost": 0.25,
            },
            thresholds={
                "transparency_discrete": {3: 1.0, 2: 0.7, 1: 0.4, 0: 0.0},
                "governance_discrete": {3: 1.0, 2: 0.66, 1: 0.33, 0: 0.0},
                "cost_fast_threshold": 1.0,
                "cost_acceptable_threshold": 5.0,
                "memory_normal_threshold": 100.0,
            },
            production_path="src.orchestration.meta_layer.MetaLayerEvaluator",
            lines_of_code=266,
            implementation_status="complete",
            test_coverage_path="tests/calibration/test_meta_layer.py",
            cohort_id="COHORT_2024",
            creation_date="2024-12-15T00:00:00+00:00",
            wave_version="REFACTOR_WAVE_2024_12",
        )


class LayerDocumentationGenerator:
    """
    Generates comprehensive Markdown documentation for calibration layers.

    Produces structured documentation with:
    - Header and metadata
    - Formula rendering (LaTeX)
    - Component breakdowns
    - Weight tables
    - Threshold specifications
    - Implementation details
    - Cross-references
    """

    def __init__(self, registry: LayerMetadataRegistry) -> None:
        self.registry = registry

    def generate_all_layer_docs(self, output_dir: Path | str) -> dict[str, Path]:
        """
        Generate documentation for all layers in registry.

        Args:
            output_dir: Directory to write Markdown files

        Returns:
            Dict mapping layer symbol to output file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        for symbol, metadata in self.registry.layers.items():
            filename = f"LAYER_{symbol.replace('@', '')}_DOCUMENTATION.md"
            filepath = output_path / filename

            doc_content = self.generate_layer_doc(metadata)

            with open(filepath, "w") as f:
                f.write(doc_content)

            generated_files[symbol] = filepath

        index_path = output_path / "LAYER_DOCUMENTATION_INDEX.md"
        index_content = self.generate_index()
        with open(index_path, "w") as f:
            f.write(index_content)
        generated_files["_index"] = index_path

        return generated_files

    def generate_layer_doc(self, metadata: LayerMetadata) -> str:
        """
        Generate Markdown documentation for a single layer.

        Args:
            metadata: LayerMetadata for the layer

        Returns:
            Formatted Markdown string
        """
        sections = [
            self._generate_header(metadata),
            self._generate_overview(metadata),
            self._generate_formula_section(metadata),
            self._generate_components_section(metadata),
            self._generate_weights_section(metadata),
            self._generate_thresholds_section(metadata),
            self._generate_implementation_section(metadata),
            self._generate_cross_references(metadata),
            self._generate_metadata_footer(metadata),
        ]

        return "\n\n".join(sections)

    def _generate_header(self, metadata: LayerMetadata) -> str:
        """Generate document header."""
        return f"""# {metadata['name']} ({metadata['symbol']})

**Calibration Layer Documentation**

---"""

    def _generate_overview(self, metadata: LayerMetadata) -> str:
        """Generate overview section."""
        return f"""## Overview

**Symbol**: `{metadata['symbol']}`
**Name**: {metadata['name']}
**Status**: {metadata['implementation_status'].upper()}
**Lines of Code**: {metadata['lines_of_code']}

{metadata['description']}"""

    def _generate_formula_section(self, metadata: LayerMetadata) -> str:
        """Generate mathematical formula section with LaTeX."""
        latex = metadata.get("formula_latex", "")
        ascii_formula = metadata.get("formula", "")

        return f"""## Mathematical Formula

### LaTeX Representation

```latex
{latex}
```

### ASCII Representation

```
{ascii_formula}
```

**Rendering**:

$$
{latex}
$$"""

    def _generate_components_section(self, metadata: LayerMetadata) -> str:
        """Generate component breakdown section."""
        components = metadata.get("components", {})

        if not components:
            return "## Components\n\n*No component breakdown available*"

        lines = ["## Components", ""]
        lines.append("| Component | Description |")
        lines.append("|-----------|-------------|")

        for comp_name, comp_desc in components.items():
            lines.append(f"| `{comp_name}` | {comp_desc} |")

        return "\n".join(lines)

    def _generate_weights_section(self, metadata: LayerMetadata) -> str:
        """Generate weights table section."""
        weights = metadata.get("weights", {})

        if not weights:
            return "## Weights\n\n*No weight configuration available*"

        lines = ["## Weights", ""]

        for weight_type, weight_data in weights.items():
            lines.append(f"### {weight_type.replace('_', ' ').title()}")
            lines.append("")

            if isinstance(weight_data, dict):
                lines.append("| Parameter | Weight |")
                lines.append("|-----------|--------|")

                for param, weight in weight_data.items():
                    if isinstance(weight, (int, float)):
                        lines.append(f"| `{param}` | {weight:.4f} |")
                    else:
                        lines.append(f"| `{param}` | {weight} |")
            else:
                lines.append(f"**Value**: {weight_data}")

            lines.append("")

        return "\n".join(lines)

    def _generate_thresholds_section(self, metadata: LayerMetadata) -> str:
        """Generate threshold specifications with rationale."""
        thresholds = metadata.get("thresholds", {})

        if not thresholds:
            return "## Thresholds\n\n*No threshold specifications available*"

        lines = ["## Thresholds", ""]
        lines.append("| Threshold | Value | Rationale |")
        lines.append("|-----------|-------|-----------|")

        for threshold_name, threshold_value in thresholds.items():
            if isinstance(threshold_value, dict):
                lines.append(f"| `{threshold_name}` | *(see below)* | Structured threshold |")
                lines.append("")
                lines.append(f"**{threshold_name}**:")
                lines.append("")
                lines.append("```json")
                lines.append(json.dumps(threshold_value, indent=2))
                lines.append("```")
                lines.append("")
            else:
                rationale = self._get_threshold_rationale(threshold_name, threshold_value)
                lines.append(f"| `{threshold_name}` | `{threshold_value}` | {rationale} |")

        return "\n".join(lines)

    def _get_threshold_rationale(self, name: str, value: Any) -> str:
        """Get rationale for threshold value."""
        rationale_map = {
            "unmapped_penalty": "Penalty for methods not declared in compatibility registry",
            "anti_universality_threshold": "Maximum score to enforce specialization constraint",
            "min_jaccard_similarity": "Minimum semantic overlap for tag alignment",
            "max_range_mismatch_ratio": "Maximum acceptable output range deviation",
            "min_fusion_validity_score": "Minimum score for fusion rule validity",
            "gate_threshold_I": "Minimum score to activate indicator quality gate",
            "gate_threshold_P": "Minimum score to activate PPI completeness gate",
            "missing_optional_ratio": "Threshold for many_missing classification",
        }

        return rationale_map.get(name, "Calibration threshold parameter")

    def _generate_implementation_section(self, metadata: LayerMetadata) -> str:
        """Generate implementation details section."""
        return f"""## Implementation

**Production Module**: `{metadata['production_path']}`
**Lines of Code**: {metadata['lines_of_code']}
**Implementation Status**: {metadata['implementation_status']}

### Import Statement

```python
from {'.'.join(metadata['production_path'].rsplit('.', 1)[:-1])} import {metadata['production_path'].rsplit('.', 1)[-1]}
```"""

    def _generate_cross_references(self, metadata: LayerMetadata) -> str:
        """Generate cross-references section."""
        return f"""## Cross-References

### Test Coverage

**Test Module**: `{metadata['test_coverage_path']}`

```bash
pytest {metadata['test_coverage_path']} -v
```

### Related Documentation

- **Calibration Orchestrator**: `COHORT_2024_calibration_orchestrator_README.md`
- **Layer Assignment System**: `COHORT_2024_layer_assignment.py`
- **Fusion Weights**: `COHORT_2024_fusion_weights.json`

### Configuration Files

- **Intrinsic Calibration**: `COHORT_2024_intrinsic_calibration.json`
- **Method Compatibility**: `COHORT_2024_method_compatibility.json`
- **Layer Requirements**: `COHORT_2024_layer_requirements.json`"""

    def _generate_metadata_footer(self, metadata: LayerMetadata) -> str:
        """Generate metadata footer."""
        return f"""---

## Metadata

**Cohort ID**: {metadata['cohort_id']}
**Creation Date**: {metadata['creation_date']}
**Wave Version**: {metadata['wave_version']}
**Authority**: Doctrina SIN_CARRETA
**Compliance**: SUPERPROMPT Three-Pillar Calibration System

*Generated by automated layer documentation generator*"""

    def generate_index(self) -> str:
        """Generate master index of all layer documentation."""
        lines = [
            "# Calibration Layer Documentation Index",
            "",
            f"**Cohort**: {self.registry.cohort_id}  ",
            f"**Wave**: {self.registry.wave_version}  ",
            f"**Total Layers**: {len(self.registry.layers)}",
            "",
            "---",
            "",
            "## All Layers",
            "",
        ]

        layer_order = ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]

        for symbol in layer_order:
            if symbol in self.registry.layers:
                metadata = self.registry.layers[symbol]
                filename = f"LAYER_{symbol.replace('@', '')}_DOCUMENTATION.md"
                lines.append(f"### [{metadata['name']}](./{filename}) (`{symbol}`)")
                lines.append("")
                lines.append(f"**Status**: {metadata['implementation_status']}  ")
                lines.append(f"**LOC**: {metadata['lines_of_code']}  ")
                lines.append(f"**Description**: {metadata['description']}")
                lines.append("")
                lines.append(f"**Formula**: `{metadata['formula']}`")
                lines.append("")

        lines.extend([
            "---",
            "",
            "## Layer System Overview",
            "",
            "The F.A.R.F.A.N. calibration system uses 8 layers to evaluate method quality:",
            "",
            "1. **@b (Base)**: Intrinsic code quality",
            "2. **@chain (Chain)**: Method wiring compatibility",
            "3. **@q (Question)**: Question-specific compatibility",
            "4. **@d (Dimension)**: Dimension alignment",
            "5. **@p (Policy)**: Policy area fit",
            "6. **@C (Congruence)**: Contract compliance",
            "7. **@u (Unit)**: Document quality (PDT structure)",
            "8. **@m (Meta)**: Governance maturity",
            "",
            "### Fusion Formula",
            "",
            "Layers are aggregated using Choquet integral:",
            "",
            "$$",
            r"\text{Cal}(I) = \sum_{\ell} a_{\ell} \cdot x_{\ell} + \sum_{\ell,k} a_{\ell k} \cdot \min(x_{\ell}, x_k)",
            "$$",
            "",
            "Where:",
            "- $a_{\\ell}$ = linear weights",
            "- $a_{\\ell k}$ = interaction weights",
            "- $x_{\\ell}$ = layer scores",
            "",
            "### Role-Based Layer Activation",
            "",
            "Different method roles require different layer subsets:",
            "",
            "- **SCORE_Q**: All 8 layers",
            "- **INGEST_PDM**: @b, @chain, @u, @m",
            "- **AGGREGATE**: @b, @chain, @d, @p, @C, @m",
            "- **REPORT**: @b, @chain, @C, @m",
            "",
            "---",
            "",
            f"*Generated from {self.registry.metadata.get('generated_from', 'calibration configurations')}*",
        ])

        return "\n".join(lines)


def generate_documentation(
    calibration_dir: Path | str,
    output_dir: Path | str,
    registry_json: Path | str | None = None,
) -> dict[str, Path]:
    """
    Main entry point for layer documentation generation.

    Args:
        calibration_dir: Path to calibration configuration directory
        output_dir: Path to output directory for Markdown files
        registry_json: Optional path to pre-built LayerMetadataRegistry JSON

    Returns:
        Dict mapping layer symbol to generated file path
    """
    if registry_json:
        registry = LayerMetadataRegistry.from_json(registry_json)
    else:
        registry = LayerMetadataRegistry.from_calibration_configs(calibration_dir)

    generator = LayerDocumentationGenerator(registry)

    return generator.generate_all_layer_docs(output_dir)


def main() -> None:
    """CLI entry point for documentation generation."""
    import sys

    if len(sys.argv) < 2:
        sys.exit(1)

    calibration_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./layer_docs"

    generated = generate_documentation(calibration_dir, output_dir)

    for _symbol, _path in generated.items():
        pass


if __name__ == "__main__":
    main()


__all__ = [
    "LayerDocumentationGenerator",
    "LayerMetadata",
    "LayerMetadataRegistry",
    "generate_documentation",
]
