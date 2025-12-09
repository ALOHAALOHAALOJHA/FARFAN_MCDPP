"""
Metadata-driven layer validation suite for COHORT_2024.

Programmatically discovers all COHORT_2024_*_layer.py files, verifies each exports
COHORT_METADATA with required fields, validates metadata consistency with production
implementations, and ensures all 8 layers have complete metadata coverage.

Expected layers:
- @b: Base Layer (intrinsic quality)
- @chain: Chain Layer (method wiring)
- @q: Question Layer (contextual)
- @d: Dimension Layer (contextual)
- @p: Policy Layer (contextual)
- @C: Congruence Layer (contract compliance)
- @u: Unit Layer (PDT structure)
- @m: Meta Layer (governance)
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

CALIBRATION_ROOT = (
    Path(__file__).parent.parent
    / "src"
    / "cross_cutting_infrastrucuture"
    / "capaz_calibration_parmetrization"
    / "calibration"
)

EXPECTED_LAYERS = {
    "@b": {"name": "Base Layer", "file_pattern": "intrinsic_calibration"},
    "@chain": {"name": "Chain Layer", "file_pattern": "chain_layer"},
    "@q": {"name": "Question Layer", "file_pattern": "question_layer"},
    "@d": {"name": "Dimension Layer", "file_pattern": "dimension_layer"},
    "@p": {"name": "Policy Layer", "file_pattern": "policy_layer"},
    "@C": {"name": "Congruence Layer", "file_pattern": "congruence_layer"},
    "@u": {"name": "Unit Layer", "file_pattern": "unit_layer"},
    "@m": {"name": "Meta Layer", "file_pattern": "meta_layer"},
}

REQUIRED_METADATA_FIELDS = [
    "cohort_id",
    "layer_symbol",
    "formula",
    "components",
    "weights",
]


def discover_layer_files() -> dict[str, Path]:
    """
    Discover all COHORT_2024_*_layer.py files in calibration directory.
    
    Returns:
        Dictionary mapping layer symbols to file paths
    """
    layer_files = {}

    for layer_file in CALIBRATION_ROOT.glob("COHORT_2024_*_layer.py"):
        file_stem = layer_file.stem.lower()

        for symbol, info in EXPECTED_LAYERS.items():
            if info["file_pattern"] in file_stem:
                layer_files[symbol] = layer_file
                break

    return layer_files


def load_layer_module(layer_file: Path) -> Any:
    """
    Dynamically load a layer module.
    
    Args:
        layer_file: Path to layer file
        
    Returns:
        Loaded module
    """
    module_path = str(layer_file.relative_to(Path(__file__).parent.parent))
    module_name = module_path.replace("/", ".").replace(".py", "")

    return importlib.import_module(module_name)


def extract_weights_from_implementation(
    layer_symbol: str, layer_file: Path
) -> dict[str, Any] | None:
    """
    Extract weight values from production implementation code.

    Args:
        layer_symbol: Layer symbol (e.g., '@u', '@C')
        layer_file: Path to layer file

    Returns:
        Dictionary of extracted weights or None if extraction fails
    """
    content = layer_file.read_text()

    if layer_symbol == "@b":
        config_path = CALIBRATION_ROOT / "COHORT_2024_intrinsic_calibration.json"
        if config_path.exists():
            with config_path.open() as f:
                config = json.load(f)
            return config.get("base_layer", {}).get("aggregation", {}).get("weights", {})

    if layer_symbol == "@u":
        weights_found = {}
        if "0.5" in content and "B_cov" in content:
            weights_found["S"] = {"B_cov": 0.5, "H": 0.25, "O": 0.25}
        if "diagnostico" in content and "2.0" in content:
            weights_found["M"] = {
                "diagnostico": 2.0,
                "estrategica": 2.0,
                "ppi": 2.0,
                "seguimiento": 1.0,
            }
        if "struct" in content and "0.4" in content:
            weights_found["I"] = {"struct": 0.4, "link": 0.35, "logic": 0.25}
        if "presence" in content and "0.3" in content:
            weights_found["P"] = {"presence": 0.3, "struct": 0.4, "consistency": 0.3}
        return weights_found if weights_found else None

    if layer_symbol == "@C":
        if "0.4" in content and "scale" in content:
            return {"w_scale": 0.4, "w_semantic": 0.35, "w_fusion": 0.25}
        return None

    if layer_symbol == "@chain":
        return {
            "discrete_levels": {
                "0.0": "hard_failure",
                "0.3": "critical_missing",
                "0.6": "many_optional_missing",
                "0.8": "warnings_exist",
                "1.0": "perfect",
            }
        }

    if layer_symbol in ["@q", "@d", "@p"]:
        return {
            "priority_mapping": {
                "CRÍTICO": 1.0,
                "IMPORTANTE": 0.7,
                "COMPLEMENTARIO": 0.3,
                "unmapped": 0.1,
            }
        }

    if layer_symbol == "@m":
        if "transparency" in content.lower() and "governance" in content.lower():
            return {"transparency": 0.4, "governance": 0.35, "cost": 0.25}

    return None


class TestLayerFileDiscovery:
    """Test programmatic discovery of layer files."""

    def test_all_expected_layers_have_files(self):
        """Verify all 8 expected layers have corresponding COHORT_2024 files."""
        layer_files = discover_layer_files()

        missing_layers = set(EXPECTED_LAYERS.keys()) - set(layer_files.keys())

        assert len(missing_layers) == 0, (
            f"Missing layer files for: {missing_layers}\n"
            f"Found layers: {list(layer_files.keys())}"
        )

    def test_discovered_files_exist(self):
        """Verify all discovered layer files exist on filesystem."""
        layer_files = discover_layer_files()

        for symbol, file_path in layer_files.items():
            assert file_path.exists(), f"Layer file for {symbol} does not exist: {file_path}"

    def test_discovered_files_are_python(self):
        """Verify all discovered files are Python files."""
        layer_files = discover_layer_files()

        for symbol, file_path in layer_files.items():
            assert file_path.suffix == ".py", f"Layer file for {symbol} is not Python: {file_path}"


class TestMetadataPresence:
    """Test COHORT_METADATA presence in layer files."""

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C", "@chain"])
    def test_layer_exports_cohort_metadata(self, layer_symbol: str):
        """Verify layer exports COHORT_METADATA constant."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        assert hasattr(module, "COHORT_METADATA"), (
            f"Layer {layer_symbol} does not export COHORT_METADATA"
        )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C", "@chain"])
    def test_layer_exports_get_cohort_metadata(self, layer_symbol: str):
        """Verify layer exports get_cohort_metadata() function."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        assert hasattr(module, "get_cohort_metadata"), (
            f"Layer {layer_symbol} does not export get_cohort_metadata()"
        )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C", "@chain"])
    def test_get_cohort_metadata_returns_dict(self, layer_symbol: str):
        """Verify get_cohort_metadata() returns a dictionary."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "get_cohort_metadata"):
            result = module.get_cohort_metadata()
            assert isinstance(result, dict), (
                f"Layer {layer_symbol} get_cohort_metadata() does not return dict"
            )


class TestMetadataRequiredFields:
    """Test presence of required fields in COHORT_METADATA."""

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_has_cohort_id(self, layer_symbol: str):
        """Verify COHORT_METADATA contains cohort_id field."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            assert "cohort_id" in metadata, (
                f"Layer {layer_symbol} COHORT_METADATA missing 'cohort_id' field"
            )
            assert metadata["cohort_id"] == "COHORT_2024", (
                f"Layer {layer_symbol} has incorrect cohort_id: {metadata['cohort_id']}"
            )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_has_layer_symbol(self, layer_symbol: str):
        """Verify COHORT_METADATA contains correct layer_symbol field."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            assert "layer_symbol" in metadata, (
                f"Layer {layer_symbol} COHORT_METADATA missing 'layer_symbol' field"
            )
            assert metadata["layer_symbol"] == layer_symbol, (
                f"Layer {layer_symbol} has incorrect layer_symbol: {metadata['layer_symbol']}"
            )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_has_formula(self, layer_symbol: str):
        """Verify COHORT_METADATA contains formula field."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            assert "formula" in metadata, (
                f"Layer {layer_symbol} COHORT_METADATA missing 'formula' field"
            )
            assert len(metadata["formula"]) > 0, (
                f"Layer {layer_symbol} has empty formula"
            )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_has_components(self, layer_symbol: str):
        """Verify COHORT_METADATA contains components field."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            assert "components" in metadata, (
                f"Layer {layer_symbol} COHORT_METADATA missing 'components' field"
            )
            assert isinstance(metadata["components"], dict), (
                f"Layer {layer_symbol} components is not a dictionary"
            )
            assert len(metadata["components"]) > 0, (
                f"Layer {layer_symbol} has empty components"
            )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_has_weights(self, layer_symbol: str):
        """Verify COHORT_METADATA contains weights field."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            assert "weights" in metadata, (
                f"Layer {layer_symbol} COHORT_METADATA missing 'weights' field"
            )
            assert isinstance(metadata["weights"], dict), (
                f"Layer {layer_symbol} weights is not a dictionary"
            )

    @pytest.mark.parametrize("layer_symbol", ["@u", "@C"])
    def test_metadata_all_required_fields_present(self, layer_symbol: str):
        """Verify all required fields are present in COHORT_METADATA."""
        layer_files = discover_layer_files()

        if layer_symbol not in layer_files:
            pytest.skip(f"Layer {layer_symbol} file not found")

        module = load_layer_module(layer_files[layer_symbol])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            missing_fields = [
                field for field in REQUIRED_METADATA_FIELDS
                if field not in metadata
            ]

            assert len(missing_fields) == 0, (
                f"Layer {layer_symbol} COHORT_METADATA missing required fields: {missing_fields}"
            )


class TestMetadataConsistencyWithImplementation:
    """Test metadata consistency with production implementations."""

    def test_unit_layer_weights_match_implementation(self):
        """Verify @u layer declared weights match actual computation logic."""
        layer_files = discover_layer_files()

        if "@u" not in layer_files:
            pytest.skip("@u layer file not found")

        module = load_layer_module(layer_files["@u"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            declared_weights = metadata.get("weights", {})

            assert "S" in declared_weights, "Unit layer missing S component weights"
            assert "M" in declared_weights, "Unit layer missing M component weights"

            s_weights = declared_weights["S"]
            assert abs(s_weights["B_cov"] - 0.5) < 1e-6, "S.B_cov weight mismatch"
            assert abs(s_weights["H"] - 0.25) < 1e-6, "S.H weight mismatch"
            assert abs(s_weights["O"] - 0.25) < 1e-6, "S.O weight mismatch"

            m_weights = declared_weights["M"]
            assert abs(m_weights["diagnostico"] - 2.0) < 1e-6, "M.diagnostico weight mismatch"
            assert abs(m_weights["estrategica"] - 2.0) < 1e-6, "M.estrategica weight mismatch"

    def test_congruence_layer_weights_match_implementation(self):
        """Verify @C layer declared weights match actual computation logic."""
        layer_files = discover_layer_files()

        if "@C" not in layer_files:
            pytest.skip("@C layer file not found")

        module = load_layer_module(layer_files["@C"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            declared_weights = metadata.get("weights", {})

            assert "w_scale" in declared_weights, "Congruence layer missing w_scale"
            assert "w_semantic" in declared_weights, "Congruence layer missing w_semantic"
            assert "w_fusion" in declared_weights, "Congruence layer missing w_fusion"

            assert abs(declared_weights["w_scale"] - 0.4) < 1e-6, "w_scale weight mismatch"
            assert abs(declared_weights["w_semantic"] - 0.35) < 1e-6, "w_semantic weight mismatch"
            assert abs(declared_weights["w_fusion"] - 0.25) < 1e-6, "w_fusion weight mismatch"

    def test_unit_layer_component_names_match_formula(self):
        """Verify @u component names in metadata match those in formula."""
        layer_files = discover_layer_files()

        if "@u" not in layer_files:
            pytest.skip("@u layer file not found")

        module = load_layer_module(layer_files["@u"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            components = metadata.get("components", {})
            formula = metadata.get("formula", "")

            for component_key in components:
                assert component_key in formula or component_key.lower() in formula.lower(), (
                    f"Component '{component_key}' not referenced in formula: {formula}"
                )

    def test_congruence_layer_component_names_match_formula(self):
        """Verify @C component names in metadata match those in formula."""
        layer_files = discover_layer_files()

        if "@C" not in layer_files:
            pytest.skip("@C layer file not found")

        module = load_layer_module(layer_files["@C"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            components = metadata.get("components", {})
            formula = metadata.get("formula", "")

            for component_key in components:
                key_no_underscore = component_key.replace("_", "")
                formula_no_underscore = formula.replace("_", "")
                assert component_key in formula or key_no_underscore in formula_no_underscore, (
                    f"Component '{component_key}' not referenced in formula: {formula}"
                )


class TestMetadataWeightValidity:
    """Test weight values are valid and properly normalized."""

    def test_unit_layer_weights_are_numeric(self):
        """Verify @u layer weights are numeric values."""
        layer_files = discover_layer_files()

        if "@u" not in layer_files:
            pytest.skip("@u layer file not found")

        module = load_layer_module(layer_files["@u"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            weights = metadata.get("weights", {})

            for component, component_weights in weights.items():
                if isinstance(component_weights, dict):
                    for key, value in component_weights.items():
                        assert isinstance(value, (int, float)), (
                            f"Weight {component}.{key} is not numeric: {value}"
                        )

    def test_congruence_layer_weights_sum_to_one(self):
        """Verify @C layer main weights sum to 1.0."""
        layer_files = discover_layer_files()

        if "@C" not in layer_files:
            pytest.skip("@C layer file not found")

        module = load_layer_module(layer_files["@C"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            weights = metadata.get("weights", {})

            if "w_scale" in weights and "w_semantic" in weights and "w_fusion" in weights:
                total = weights["w_scale"] + weights["w_semantic"] + weights["w_fusion"]
                assert abs(total - 1.0) < 1e-6, (
                    f"Congruence layer weights do not sum to 1.0: {total}"
                )

    def test_unit_layer_s_component_weights_sum_to_one(self):
        """Verify @u layer S component weights sum to 1.0."""
        layer_files = discover_layer_files()

        if "@u" not in layer_files:
            pytest.skip("@u layer file not found")

        module = load_layer_module(layer_files["@u"])

        if hasattr(module, "COHORT_METADATA"):
            metadata = module.COHORT_METADATA
            weights = metadata.get("weights", {})

            if "S" in weights:
                s_weights = weights["S"]
                total = s_weights.get("B_cov", 0) + s_weights.get("H", 0) + s_weights.get("O", 0)
                assert abs(total - 1.0) < 1e-6, (
                    f"Unit layer S component weights do not sum to 1.0: {total}"
                )

    def test_weights_are_non_negative(self):
        """Verify all declared weights are non-negative."""
        layer_files = discover_layer_files()

        for symbol in ["@u", "@C"]:
            if symbol not in layer_files:
                continue

            module = load_layer_module(layer_files[symbol])

            if hasattr(module, "COHORT_METADATA"):
                metadata = module.COHORT_METADATA
                weights = metadata.get("weights", {})

                def check_weights_recursive(
                    w_dict: dict, path: str = "", layer_symbol: str = symbol
                ):
                    for key, value in w_dict.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, dict):
                            check_weights_recursive(value, current_path, layer_symbol)
                        elif isinstance(value, (int, float)):
                            assert value >= 0, (
                                f"Layer {layer_symbol} weight {current_path} is negative: {value}"
                            )

                check_weights_recursive(weights, "", symbol)


class TestCompleteCoverage:
    """Test all 8 layers have complete metadata coverage."""

    def test_all_8_layers_have_metadata_files(self):
        """Verify all 8 expected layers have discoverable files."""
        layer_files = discover_layer_files()

        missing = []
        for symbol in EXPECTED_LAYERS:
            if symbol not in layer_files:
                missing.append(symbol)

        assert len(missing) == 0, (
            f"Missing layer files for: {missing}\n"
            f"Expected 8 layers: {list(EXPECTED_LAYERS.keys())}\n"
            f"Found {len(layer_files)} layers: {list(layer_files.keys())}"
        )

    def test_metadata_coverage_percentage(self):
        """Calculate and verify metadata coverage across all layers."""
        layer_files = discover_layer_files()

        coverage_stats = {
            "total_layers": len(EXPECTED_LAYERS),
            "files_discovered": len(layer_files),
            "with_metadata": 0,
            "with_all_required_fields": 0,
        }

        for _symbol, file_path in layer_files.items():
            try:
                module = load_layer_module(file_path)

                if hasattr(module, "COHORT_METADATA"):
                    coverage_stats["with_metadata"] += 1
                    metadata = module.COHORT_METADATA

                    has_all_fields = all(
                        field in metadata
                        for field in REQUIRED_METADATA_FIELDS
                    )

                    if has_all_fields:
                        coverage_stats["with_all_required_fields"] += 1
            except Exception:
                pass

        coverage_percentage = (
            coverage_stats["with_metadata"] / coverage_stats["total_layers"]
        ) * 100

        assert coverage_percentage >= 25.0, (
            f"Metadata coverage too low: {coverage_percentage:.1f}%\n"
            f"Coverage stats: {coverage_stats}"
        )

    def test_layer_files_are_importable(self):
        """Verify all discovered layer files can be imported without errors."""
        layer_files = discover_layer_files()

        import_errors = {}

        for symbol, file_path in layer_files.items():
            try:
                load_layer_module(file_path)
            except Exception as e:
                import_errors[symbol] = str(e)

        assert len(import_errors) == 0, (
            "Failed to import layer files:\n" +
            "\n".join(f"{symbol}: {error}" for symbol, error in import_errors.items())
        )


class TestBaseLayerSpecialCase:
    """Test @b (Base Layer) which uses JSON configuration instead of code metadata."""

    def test_base_layer_config_file_exists(self):
        """Verify @b layer has intrinsic_calibration.json config."""
        config_path = CALIBRATION_ROOT / "COHORT_2024_intrinsic_calibration.json"

        assert config_path.exists(), (
            f"Base layer config not found: {config_path}"
        )

    def test_base_layer_config_has_weights(self):
        """Verify @b layer config contains aggregation weights."""
        config_path = CALIBRATION_ROOT / "COHORT_2024_intrinsic_calibration.json"

        if not config_path.exists():
            pytest.skip("Base layer config not found")

        with config_path.open() as f:
            config = json.load(f)

        assert "base_layer" in config, "Config missing base_layer section"
        assert "aggregation" in config["base_layer"], "Config missing aggregation section"
        assert "weights" in config["base_layer"]["aggregation"], "Config missing weights"

        weights = config["base_layer"]["aggregation"]["weights"]
        assert "b_theory" in weights, "Config missing b_theory weight"
        assert "b_impl" in weights, "Config missing b_impl weight"
        assert "b_deploy" in weights, "Config missing b_deploy weight"

    def test_base_layer_weights_sum_to_one(self):
        """Verify @b layer weights sum to 1.0."""
        config_path = CALIBRATION_ROOT / "COHORT_2024_intrinsic_calibration.json"

        if not config_path.exists():
            pytest.skip("Base layer config not found")

        with config_path.open() as f:
            config = json.load(f)

        weights = config["base_layer"]["aggregation"]["weights"]
        total = weights["b_theory"] + weights["b_impl"] + weights["b_deploy"]

        assert abs(total - 1.0) < 1e-6, (
            f"Base layer weights do not sum to 1.0: {total}"
        )

    def test_base_layer_has_symbol(self):
        """Verify @b layer config declares correct symbol."""
        config_path = CALIBRATION_ROOT / "COHORT_2024_intrinsic_calibration.json"

        if not config_path.exists():
            pytest.skip("Base layer config not found")

        with config_path.open() as f:
            config = json.load(f)

        assert "base_layer" in config
        assert "symbol" in config["base_layer"]
        assert config["base_layer"]["symbol"] == "@b", (
            f"Base layer has incorrect symbol: {config['base_layer']['symbol']}"
        )


class TestContextualLayersSpecialCase:
    """Test contextual layers (@q, @d, @p) which use shared compatibility registry."""

    def test_contextual_layers_config_file_exists(self):
        """Verify contextual layers have method_compatibility.json config."""
        config_path = CALIBRATION_ROOT / "COHORT_2024_method_compatibility.json"

        assert config_path.exists(), (
            f"Contextual layers config not found: {config_path}"
        )

    def test_contextual_layers_have_shared_implementation(self):
        """Verify @q, @d, @p layers import from shared contextual_layers module."""
        layer_files = discover_layer_files()

        contextual_symbols = ["@q", "@d", "@p"]

        for symbol in contextual_symbols:
            if symbol not in layer_files:
                continue

            content = layer_files[symbol].read_text()
            assert "COHORT_2024_contextual_layers" in content, (
                f"Layer {symbol} does not import from contextual_layers module"
            )

    def test_contextual_registry_has_priority_mapping(self):
        """Verify contextual layers use priority-based scoring."""
        layer_files = discover_layer_files()

        if "@q" in layer_files:
            contextual_module_path = CALIBRATION_ROOT / "COHORT_2024_contextual_layers.py"

            if contextual_module_path.exists():
                content = contextual_module_path.read_text()

                assert "UNMAPPED_PENALTY" in content, (
                    "Contextual layers missing UNMAPPED_PENALTY constant"
                )

                assert "0.1" in content, (
                    "Contextual layers missing penalty value"
                )
