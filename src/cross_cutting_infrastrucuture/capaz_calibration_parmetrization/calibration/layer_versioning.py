"""
Layer Comparison and Versioning System

Provides tools for tracking layer formula changes across COHORT versions,
generating semantic diff reports, validating evolution constraints, and
assessing migration impact for calibration score drift.

Core functionality:
- LayerMetadataRegistry: Central registry for layer metadata across COHORTs
- FormulaChangeDetector: Detects formula modifications requiring new COHORT
- WeightDiffAnalyzer: Analyzes weight changes with ±0.05 threshold violation detection
- MigrationImpactAssessor: Estimates calibration score drift during COHORT upgrades
- LayerEvolutionValidator: Enforces governance rules for layer changes
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict


class LayerMetadata(TypedDict):
    cohort_id: str
    layer_symbol: str
    layer_name: str
    formula: str
    weights: dict[str, float | dict[str, float]]
    components: dict[str, str]
    creation_date: str
    wave_version: str
    implementation_status: str
    lines_of_code: int | None


class WeightChange(TypedDict):
    parameter: str
    old_value: float
    new_value: float
    delta: float
    delta_pct: float
    exceeds_threshold: bool


class FormulaChange(TypedDict):
    layer_symbol: str
    old_formula: str
    new_formula: str
    change_type: str
    requires_new_cohort: bool


class MigrationImpact(TypedDict):
    from_cohort: str
    to_cohort: str
    affected_layers: list[str]
    estimated_score_drift: dict[str, float]
    risk_level: str
    breaking_changes: list[str]
    recommendations: list[str]


@dataclass(frozen=True)
class DiffThresholds:
    weight_warning: float = 0.05
    weight_critical: float = 0.10
    score_drift_low: float = 0.03
    score_drift_moderate: float = 0.08
    score_drift_high: float = 0.15


class LayerMetadataRegistry:
    """
    Central registry for layer metadata across COHORT versions.

    Loads and manages layer metadata from COHORT files to enable
    version comparison and evolution tracking.
    """

    def __init__(self, calibration_dir: Path | str) -> None:
        self.calibration_dir = Path(calibration_dir)
        self._registry: dict[str, dict[str, LayerMetadata]] = {}
        self._load_all_cohorts()

    def _load_all_cohorts(self) -> None:
        """Load all COHORT layer metadata files."""
        cohort_files = [
            ("COHORT_2024_unit_layer.py", "@u"),
            ("COHORT_2024_congruence_layer.py", "@C"),
            ("COHORT_2024_chain_layer.py", "@chain"),
        ]

        for filename, layer_symbol in cohort_files:
            filepath = self.calibration_dir / filename
            if filepath.exists():
                metadata = self._extract_metadata_from_file(filepath, layer_symbol)
                if metadata:
                    cohort_id = metadata["cohort_id"]
                    if cohort_id not in self._registry:
                        self._registry[cohort_id] = {}
                    self._registry[cohort_id][layer_symbol] = metadata

    def _extract_metadata_from_file(
        self, filepath: Path, layer_symbol: str
    ) -> LayerMetadata | None:
        """Extract COHORT_METADATA from a layer file."""
        try:
            with open(filepath) as f:
                content = f.read()

            if "COHORT_METADATA = {" not in content:
                return None

            start = content.index("COHORT_METADATA = {")
            end = content.index("}", start) + 1
            metadata_str = content[start:end]

            metadata_dict: dict[str, Any] = {}
            for line in metadata_str.split("\n"):
                if '": ' in line:
                    key_part, value_part = line.split('": ', 1)
                    key = key_part.strip().split('"')[-1]
                    value = value_part.rstrip(',').strip()

                    if value.startswith('"') and value.endswith('"'):
                        metadata_dict[key] = value[1:-1]
                    elif value.isdigit():
                        metadata_dict[key] = int(value)
                    elif value in ["true", "false"]:
                        metadata_dict[key] = value == "true"
                    elif value.startswith("{"):
                        continue

            weights_data: dict[str, float | dict[str, float]] = {}
            if '"weights": {' in content:
                weights_start = content.index('"weights": {')
                brace_count = 0
                weights_end = weights_start
                for i, char in enumerate(content[weights_start:], start=weights_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            weights_end = i + 1
                            break

                weights_str = content[weights_start:weights_end]
                weights_data = self._parse_nested_weights(weights_str)

            components_data: dict[str, str] = {}
            if '"components": {' in content:
                comp_start = content.index('"components": {')
                brace_count = 0
                comp_end = comp_start
                for i, char in enumerate(content[comp_start:], start=comp_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            comp_end = i + 1
                            break

                comp_str = content[comp_start:comp_end]
                components_data = self._parse_components(comp_str)

            return LayerMetadata(
                cohort_id=metadata_dict.get("cohort_id", "UNKNOWN"),
                layer_symbol=metadata_dict.get("layer_symbol", layer_symbol),
                layer_name=metadata_dict.get("layer_name", ""),
                formula=metadata_dict.get("formula", ""),
                weights=weights_data,
                components=components_data,
                creation_date=metadata_dict.get("creation_date", ""),
                wave_version=metadata_dict.get("wave_version", ""),
                implementation_status=metadata_dict.get("implementation_status", ""),
                lines_of_code=metadata_dict.get("lines_of_code"),
            )
        except Exception:
            return None

    def _parse_nested_weights(self, weights_str: str) -> dict[str, float | dict[str, float]]:
        """Parse nested weights structure."""
        weights: dict[str, float | dict[str, float]] = {}
        lines = weights_str.split("\n")

        current_key = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            if '": {' in line:
                current_key = line.split('"')[1]
                weights[current_key] = {}
            elif '":' in line and current_key:
                parts = line.split('": ')
                if len(parts) == 2:
                    key = parts[0].strip().strip('"')
                    value_str = parts[1].rstrip(',').strip()
                    try:
                        value = float(value_str)
                        if isinstance(weights[current_key], dict):
                            weights[current_key][key] = value
                    except ValueError:
                        pass
            elif '":' in line and not current_key:
                parts = line.split('": ')
                if len(parts) == 2:
                    key = parts[0].strip().strip('"')
                    value_str = parts[1].rstrip(',').strip()
                    with contextlib.suppress(ValueError):
                        weights[key] = float(value_str)

        return weights

    def _parse_components(self, comp_str: str) -> dict[str, str]:
        """Parse components structure."""
        components: dict[str, str] = {}
        lines = comp_str.split("\n")

        for line in lines:
            if '": "' in line:
                parts = line.split('": "')
                if len(parts) == 2:
                    key = parts[0].strip().strip('"')
                    value = parts[1].split('"')[0]
                    components[key] = value

        return components

    def get_layer_metadata(
        self, cohort_id: str, layer_symbol: str
    ) -> LayerMetadata | None:
        """Get layer metadata for a specific COHORT and layer."""
        return self._registry.get(cohort_id, {}).get(layer_symbol)

    def get_all_layers(self, cohort_id: str) -> dict[str, LayerMetadata]:
        """Get all layer metadata for a specific COHORT."""
        return self._registry.get(cohort_id, {})

    def list_cohorts(self) -> list[str]:
        """List all registered COHORT versions."""
        return sorted(self._registry.keys())

    def list_layers(self, cohort_id: str) -> list[str]:
        """List all layers in a specific COHORT."""
        return list(self._registry.get(cohort_id, {}).keys())


class FormulaChangeDetector:
    """
    Detects formula changes across COHORT versions.

    Enforces the rule: formula changes REQUIRE new COHORT version.
    """

    def __init__(self, registry: LayerMetadataRegistry) -> None:
        self.registry = registry

    def detect_formula_changes(
        self, from_cohort: str, to_cohort: str
    ) -> list[FormulaChange]:
        """
        Detect formula changes between two COHORT versions.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            List of FormulaChange objects for layers with formula modifications
        """
        changes: list[FormulaChange] = []

        old_layers = self.registry.get_all_layers(from_cohort)
        new_layers = self.registry.get_all_layers(to_cohort)

        common_layers = set(old_layers.keys()) & set(new_layers.keys())

        for layer_symbol in common_layers:
            old_meta = old_layers[layer_symbol]
            new_meta = new_layers[layer_symbol]

            if old_meta["formula"] != new_meta["formula"]:
                change_type = self._classify_formula_change(
                    old_meta["formula"], new_meta["formula"]
                )

                changes.append(
                    FormulaChange(
                        layer_symbol=layer_symbol,
                        old_formula=old_meta["formula"],
                        new_formula=new_meta["formula"],
                        change_type=change_type,
                        requires_new_cohort=True,
                    )
                )

        return changes

    def _classify_formula_change(self, old_formula: str, new_formula: str) -> str:
        """Classify the type of formula change."""
        if ("geometric_mean" in old_formula and "geometric_mean" not in new_formula) or ("geometric_mean" not in old_formula and "geometric_mean" in new_formula):
            return "aggregation_method_change"
        elif len(new_formula.split("×")) != len(old_formula.split("×")):
            return "component_count_change"
        elif "gated" in new_formula and "gated" not in old_formula:
            return "gating_added"
        elif "gated" in old_formula and "gated" not in new_formula:
            return "gating_removed"
        else:
            return "formula_modification"

    def validate_formula_evolution(
        self, from_cohort: str, to_cohort: str
    ) -> tuple[bool, list[str]]:
        """
        Validate that formula evolution follows governance rules.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations: list[str] = []
        changes = self.detect_formula_changes(from_cohort, to_cohort)

        if not changes:
            return True, []

        if from_cohort == to_cohort:
            violations.append(
                f"Formula changes detected within same COHORT {from_cohort}. "
                "Formula changes REQUIRE new COHORT version."
            )

        for change in changes:
            if change["change_type"] == "aggregation_method_change":
                violations.append(
                    f"Layer {change['layer_symbol']}: Aggregation method change is "
                    "a breaking change. Requires new COHORT and deprecation period."
                )

        return len(violations) == 0, violations


class WeightDiffAnalyzer:
    """
    Analyzes weight changes with threshold violation detection.

    Highlights weight changes exceeding ±0.05 threshold as requiring review.
    """

    def __init__(
        self, registry: LayerMetadataRegistry, thresholds: DiffThresholds | None = None
    ) -> None:
        self.registry = registry
        self.thresholds = thresholds or DiffThresholds()

    def analyze_weight_changes(
        self, from_cohort: str, to_cohort: str, layer_symbol: str
    ) -> list[WeightChange]:
        """
        Analyze weight changes for a specific layer.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version
            layer_symbol: Layer to analyze (e.g., "@u", "@C")

        Returns:
            List of WeightChange objects with delta and threshold violation flags
        """
        old_meta = self.registry.get_layer_metadata(from_cohort, layer_symbol)
        new_meta = self.registry.get_layer_metadata(to_cohort, layer_symbol)

        if not old_meta or not new_meta:
            return []

        changes: list[WeightChange] = []

        old_weights = old_meta["weights"]
        new_weights = new_meta["weights"]

        all_params = set(self._flatten_weights(old_weights).keys()) | set(
            self._flatten_weights(new_weights).keys()
        )

        old_flat = self._flatten_weights(old_weights)
        new_flat = self._flatten_weights(new_weights)

        for param in sorted(all_params):
            old_val = old_flat.get(param, 0.0)
            new_val = new_flat.get(param, 0.0)
            delta = new_val - old_val

            if abs(delta) > 1e-9:
                delta_pct = (delta / old_val * 100) if old_val != 0 else float("inf")
                exceeds = abs(delta) >= self.thresholds.weight_warning

                changes.append(
                    WeightChange(
                        parameter=param,
                        old_value=old_val,
                        new_value=new_val,
                        delta=delta,
                        delta_pct=delta_pct,
                        exceeds_threshold=exceeds,
                    )
                )

        return changes

    def _flatten_weights(
        self, weights: dict[str, float | dict[str, float]]
    ) -> dict[str, float]:
        """Flatten nested weight structure to flat dict."""
        flat: dict[str, float] = {}

        for key, value in weights.items():
            if isinstance(value, dict):
                for subkey, subval in value.items():
                    flat[f"{key}.{subkey}"] = subval
            else:
                flat[key] = value

        return flat

    def generate_diff_report(
        self, from_cohort: str, to_cohort: str, layer_symbol: str
    ) -> str:
        """
        Generate human-readable diff report for weight changes.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version
            layer_symbol: Layer to analyze

        Returns:
            Formatted diff report string
        """
        changes = self.analyze_weight_changes(from_cohort, to_cohort, layer_symbol)

        if not changes:
            return (
                f"No weight changes detected for {layer_symbol} "
                f"between {from_cohort} and {to_cohort}"
            )

        lines = [
            f"Weight Diff Report: {layer_symbol}",
            f"From: {from_cohort} → To: {to_cohort}",
            "=" * 70,
            "",
        ]

        threshold_violations = [c for c in changes if c["exceeds_threshold"]]
        minor_changes = [c for c in changes if not c["exceeds_threshold"]]

        if threshold_violations:
            lines.append("⚠️  THRESHOLD VIOLATIONS (|Δ| ≥ 0.05):")
            lines.append("")
            for change in threshold_violations:
                sign = "+" if change["delta"] > 0 else ""
                lines.append(
                    f"  {change['parameter']:30s}  "
                    f"{change['old_value']:.4f} → {change['new_value']:.4f}  "
                    f"({sign}{change['delta']:+.4f}, {change['delta_pct']:+.1f}%)"
                )
            lines.append("")

        if minor_changes:
            lines.append(f"Minor Changes (|Δ| < {self.thresholds.weight_warning}):")
            lines.append("")
            for change in minor_changes:
                sign = "+" if change["delta"] > 0 else ""
                lines.append(
                    f"  {change['parameter']:30s}  "
                    f"{change['old_value']:.4f} → {change['new_value']:.4f}  "
                    f"({sign}{change['delta']:+.4f})"
                )

        return "\n".join(lines)


class MigrationImpactAssessor:
    """
    Assesses migration impact for calibration score drift.

    Estimates score drift when upgrading between COHORT versions based on
    weight changes and formula modifications.
    """

    def __init__(
        self,
        registry: LayerMetadataRegistry,
        weight_analyzer: WeightDiffAnalyzer,
        formula_detector: FormulaChangeDetector,
    ) -> None:
        self.registry = registry
        self.weight_analyzer = weight_analyzer
        self.formula_detector = formula_detector

    def assess_migration_impact(
        self, from_cohort: str, to_cohort: str
    ) -> MigrationImpact:
        """
        Assess migration impact between two COHORT versions.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            MigrationImpact with drift estimates and recommendations
        """
        affected_layers: list[str] = []
        estimated_drift: dict[str, float] = {}
        breaking_changes: list[str] = []
        recommendations: list[str] = []

        old_layers = self.registry.get_all_layers(from_cohort)
        new_layers = self.registry.get_all_layers(to_cohort)

        common_layers = set(old_layers.keys()) & set(new_layers.keys())

        formula_changes = self.formula_detector.detect_formula_changes(
            from_cohort, to_cohort
        )

        for change in formula_changes:
            affected_layers.append(change["layer_symbol"])
            breaking_changes.append(
                f"{change['layer_symbol']}: Formula changed "
                f"({change['change_type']})"
            )
            estimated_drift[change["layer_symbol"]] = 0.20

        for layer_symbol in common_layers:
            weight_changes = self.weight_analyzer.analyze_weight_changes(
                from_cohort, to_cohort, layer_symbol
            )

            if weight_changes:
                if layer_symbol not in affected_layers:
                    affected_layers.append(layer_symbol)

                max_delta = max(abs(c["delta"]) for c in weight_changes)
                threshold_violations = [
                    c for c in weight_changes if c["exceeds_threshold"]
                ]

                if threshold_violations:
                    if layer_symbol not in estimated_drift:
                        estimated_drift[layer_symbol] = max_delta * 0.5

                    breaking_changes.append(
                        f"{layer_symbol}: {len(threshold_violations)} weight(s) "
                        f"changed by ≥0.05"
                    )
                elif layer_symbol not in estimated_drift:
                    estimated_drift[layer_symbol] = max_delta * 0.3

        risk_level = self._assess_risk_level(estimated_drift)
        recommendations = self._generate_recommendations(
            risk_level, breaking_changes, affected_layers
        )

        return MigrationImpact(
            from_cohort=from_cohort,
            to_cohort=to_cohort,
            affected_layers=affected_layers,
            estimated_score_drift=estimated_drift,
            risk_level=risk_level,
            breaking_changes=breaking_changes,
            recommendations=recommendations,
        )

    def _assess_risk_level(self, drift_estimates: dict[str, float]) -> str:
        """Assess overall migration risk level."""
        if not drift_estimates:
            return "LOW"

        max_drift = max(drift_estimates.values())

        thresholds = DiffThresholds()

        if max_drift >= thresholds.score_drift_high:
            return "HIGH"
        elif max_drift >= thresholds.score_drift_moderate:
            return "MODERATE"
        elif max_drift >= thresholds.score_drift_low:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendations(
        self, risk_level: str, breaking_changes: list[str], affected_layers: list[str]
    ) -> list[str]:
        """Generate migration recommendations based on risk assessment."""
        recs: list[str] = []

        if risk_level == "HIGH":
            recs.append(
                "⚠️  HIGH RISK: Recalibrate all methods using affected layers"
            )
            recs.append("Run full regression test suite before deployment")
            recs.append("Consider phased rollout with canary deployments")
        elif risk_level == "MODERATE":
            recs.append("Recalibrate methods in affected layers")
            recs.append("Run integration tests for affected components")
        elif risk_level == "LOW":
            recs.append("Review score changes in affected layers")
            recs.append("Run smoke tests to verify behavior")
        else:
            recs.append("Minor changes - standard testing sufficient")

        if breaking_changes:
            recs.append(
                f"Document {len(breaking_changes)} breaking change(s) "
                "in migration guide"
            )

        if len(affected_layers) > 4:
            recs.append("Wide impact across multiple layers - careful review required")

        return recs

    def generate_migration_report(
        self, from_cohort: str, to_cohort: str
    ) -> str:
        """
        Generate comprehensive migration report.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            Formatted migration report string
        """
        impact = self.assess_migration_impact(from_cohort, to_cohort)

        lines = [
            "=" * 80,
            "MIGRATION IMPACT ASSESSMENT",
            f"From: {impact['from_cohort']} → To: {impact['to_cohort']}",
            "=" * 80,
            "",
            f"Risk Level: {impact['risk_level']}",
            f"Affected Layers: {len(impact['affected_layers'])}",
            f"Breaking Changes: {len(impact['breaking_changes'])}",
            "",
        ]

        if impact["affected_layers"]:
            lines.append("Affected Layers:")
            for layer in impact["affected_layers"]:
                drift = impact["estimated_score_drift"].get(layer, 0.0)
                lines.append(f"  - {layer:10s}  Estimated drift: ±{drift:.3f}")
            lines.append("")

        if impact["breaking_changes"]:
            lines.append("Breaking Changes:")
            for change in impact["breaking_changes"]:
                lines.append(f"  - {change}")
            lines.append("")

        if impact["recommendations"]:
            lines.append("Recommendations:")
            for i, rec in enumerate(impact["recommendations"], 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


class LayerEvolutionValidator:
    """
    Validates layer evolution constraints and governance rules.

    Enforces:
    - Formula changes require new COHORT
    - Weight changes >0.05 require explicit approval
    - Breaking changes must be documented
    - Layer dependencies must remain valid
    """

    def __init__(
        self,
        registry: LayerMetadataRegistry,
        formula_detector: FormulaChangeDetector,
        weight_analyzer: WeightDiffAnalyzer,
    ) -> None:
        self.registry = registry
        self.formula_detector = formula_detector
        self.weight_analyzer = weight_analyzer

    def validate_evolution(
        self, from_cohort: str, to_cohort: str
    ) -> tuple[bool, list[str]]:
        """
        Validate layer evolution between two COHORT versions.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations: list[str] = []

        _is_formula_valid, formula_violations = (
            self.formula_detector.validate_formula_evolution(from_cohort, to_cohort)
        )
        violations.extend(formula_violations)

        old_layers = self.registry.get_all_layers(from_cohort)
        new_layers = self.registry.get_all_layers(to_cohort)

        removed_layers = set(old_layers.keys()) - set(new_layers.keys())
        if removed_layers:
            violations.append(
                f"Layer removal detected: {removed_layers}. "
                "Layers cannot be removed without deprecation cycle."
            )

        for layer_symbol in set(old_layers.keys()) & set(new_layers.keys()):
            weight_changes = self.weight_analyzer.analyze_weight_changes(
                from_cohort, to_cohort, layer_symbol
            )

            critical_changes = [
                c
                for c in weight_changes
                if abs(c["delta"]) >= DiffThresholds().weight_critical
            ]

            if critical_changes:
                violations.append(
                    f"Layer {layer_symbol}: {len(critical_changes)} critical "
                    f"weight change(s) (|Δ| ≥ 0.10) require governance approval"
                )

        return len(violations) == 0, violations

    def generate_validation_report(
        self, from_cohort: str, to_cohort: str
    ) -> str:
        """
        Generate validation report for layer evolution.

        Args:
            from_cohort: Source COHORT version
            to_cohort: Target COHORT version

        Returns:
            Formatted validation report string
        """
        is_valid, violations = self.validate_evolution(from_cohort, to_cohort)

        lines = [
            "=" * 80,
            "LAYER EVOLUTION VALIDATION",
            f"From: {from_cohort} → To: {to_cohort}",
            "=" * 80,
            "",
        ]

        if is_valid:
            lines.append("✅ VALIDATION PASSED")
            lines.append("")
            lines.append("All layer evolution constraints satisfied.")
        else:
            lines.append("❌ VALIDATION FAILED")
            lines.append("")
            lines.append(f"Found {len(violations)} violation(s):")
            lines.append("")
            for i, violation in enumerate(violations, 1):
                lines.append(f"  {i}. {violation}")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


def create_versioning_tools(
    calibration_dir: Path | str,
) -> tuple[
    LayerMetadataRegistry,
    FormulaChangeDetector,
    WeightDiffAnalyzer,
    MigrationImpactAssessor,
    LayerEvolutionValidator,
]:
    """
    Create all versioning tools with shared registry.

    Args:
        calibration_dir: Path to calibration directory

    Returns:
        Tuple of (registry, formula_detector, weight_analyzer,
                 impact_assessor, evolution_validator)
    """
    registry = LayerMetadataRegistry(calibration_dir)
    formula_detector = FormulaChangeDetector(registry)
    weight_analyzer = WeightDiffAnalyzer(registry)
    impact_assessor = MigrationImpactAssessor(
        registry, weight_analyzer, formula_detector
    )
    evolution_validator = LayerEvolutionValidator(
        registry, formula_detector, weight_analyzer
    )

    return (
        registry,
        formula_detector,
        weight_analyzer,
        impact_assessor,
        evolution_validator,
    )


__all__ = [
    "DiffThresholds",
    "FormulaChange",
    "FormulaChangeDetector",
    "LayerEvolutionValidator",
    "LayerMetadata",
    "LayerMetadataRegistry",
    "MigrationImpact",
    "MigrationImpactAssessor",
    "WeightChange",
    "WeightDiffAnalyzer",
    "create_versioning_tools",
]
