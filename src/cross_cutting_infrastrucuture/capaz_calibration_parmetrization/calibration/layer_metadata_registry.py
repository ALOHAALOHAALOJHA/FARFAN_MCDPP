"""
COHORT_2024 Layer Metadata Registry

Discovers and aggregates metadata from all COHORT_2024 layer modules, providing:
- Unified metadata access via get_all_layer_metadata()
- Layer lookup by symbol via get_layer_by_symbol()
- Metadata completeness validation
- Layer compatibility matrix based on LAYER_REQUIREMENTS
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, TypedDict

__all__ = [
    "LayerMetadata",
    "LayerMetadataRegistry",
    "create_default_registry",
]


class LayerMetadata(TypedDict, total=False):
    cohort_id: str
    creation_date: str
    wave_version: str
    layer_symbol: str
    layer_name: str
    production_path: str
    implementation_status: str
    lines_of_code: int
    formula: str
    components: dict[str, Any]
    weights: dict[str, Any]
    description: str
    thresholds: dict[str, Any]
    discrete_scores: dict[str, Any]
    validation_rules: dict[str, Any]
    dependencies: list[str]
    required_methods: list[str]


class LayerMetadataRegistry:
    """
    Registry for COHORT_2024 layer metadata discovery and validation.

    Discovers metadata from all layer modules, provides unified access,
    validates completeness, and generates compatibility matrices.
    """

    LAYER_SYMBOLS: ClassVar[list[str]] = ["@b", "@chain", "@u", "@C", "@q", "@d", "@p", "@m"]

    LAYER_MODULE_MAP: ClassVar[dict[str, str]] = {
        "@b": "COHORT_2024_intrinsic_calibration_loader",
        "@chain": "COHORT_2024_chain_layer",
        "@u": "COHORT_2024_unit_layer",
        "@C": "COHORT_2024_congruence_layer",
        "@q": "COHORT_2024_contextual_layers",
        "@d": "COHORT_2024_contextual_layers",
        "@p": "COHORT_2024_contextual_layers",
        "@m": "COHORT_2024_meta_layer",
    }

    REQUIRED_METADATA_FIELDS: ClassVar[list[str]] = [
        "cohort_id",
        "layer_symbol",
        "layer_name",
        "formula",
        "components",
        "weights",
    ]

    def __init__(
        self,
        calibration_dir: Path | None = None,
        layer_requirements_path: Path | None = None,
    ) -> None:
        """
        Initialize registry with optional custom paths.

        Args:
            calibration_dir: Directory containing COHORT_2024 layer modules
            layer_requirements_path: Path to COHORT_2024_layer_requirements.json
        """
        if calibration_dir is None:
            calibration_dir = Path(__file__).parent

        if layer_requirements_path is None:
            layer_requirements_path = calibration_dir / "COHORT_2024_layer_requirements.json"

        self.calibration_dir = calibration_dir
        self.layer_requirements_path = layer_requirements_path
        self._metadata: dict[str, LayerMetadata] = {}
        self._layer_requirements: dict[str, Any] = {}
        self._compatibility_matrix: dict[tuple[str, str], bool] = {}

    def load(self) -> None:
        """Load all layer metadata and requirements."""
        self._load_layer_requirements()
        self._discover_layer_metadata()
        self._generate_compatibility_matrix()

    def _load_layer_requirements(self) -> None:
        """Load layer requirements from JSON configuration."""
        if not self.layer_requirements_path.exists():
            raise FileNotFoundError(
                f"Layer requirements not found: {self.layer_requirements_path}"
            )

        with self.layer_requirements_path.open() as f:
            self._layer_requirements = json.load(f)

        if "layers" not in self._layer_requirements:
            raise ValueError("Invalid layer requirements: missing 'layers' key")

    def _discover_layer_metadata(self) -> None:
        """Discover and load metadata from all COHORT_2024 layer modules."""
        for symbol in self.LAYER_SYMBOLS:
            metadata = self._load_layer_metadata(symbol)
            if metadata:
                self._metadata[symbol] = metadata

    def _load_layer_metadata(self, symbol: str) -> LayerMetadata | None:
        """
        Load metadata for a specific layer.

        Args:
            symbol: Layer symbol (e.g., '@u', '@chain')

        Returns:
            LayerMetadata dict or None if not found
        """
        if symbol == "@b":
            return self._load_base_layer_metadata()

        module_name = self.LAYER_MODULE_MAP.get(symbol)
        if not module_name:
            return None

        module_path = self.calibration_dir / f"{module_name}.py"
        if not module_path.exists():
            return None

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if symbol in ["@q", "@d", "@p"]:
                metadata_func_name = {
                    "@q": "get_question_metadata",
                    "@d": "get_dimension_metadata",
                    "@p": "get_policy_metadata",
                }[symbol]

                if hasattr(module, metadata_func_name):
                    metadata = getattr(module, metadata_func_name)()
                    return self._enrich_metadata(symbol, metadata)
            elif hasattr(module, "get_cohort_metadata"):
                metadata = module.get_cohort_metadata()
                return self._enrich_metadata(symbol, metadata)
            elif hasattr(module, "COHORT_METADATA"):
                metadata = module.COHORT_METADATA.copy()
                return self._enrich_metadata(symbol, metadata)

        except Exception:
            pass

        return None

    def _load_base_layer_metadata(self) -> LayerMetadata:
        """
        Load @b (Base Layer) metadata from layer_requirements.json.

        The base layer uses JSON configuration rather than code metadata.
        """
        layer_req = self._layer_requirements.get("layers", {}).get("@b", {})

        return LayerMetadata(
            cohort_id="COHORT_2024",
            wave_version="REFACTOR_WAVE_2024_12",
            layer_symbol="@b",
            layer_name=layer_req.get("name", "Base Theory Layer"),
            production_path="COHORT_2024_intrinsic_calibration_loader",
            implementation_status="complete",
            formula="b_aggregate = w_th·b_theory + w_imp·b_impl + w_dep·b_deploy",
            components={
                "b_theory": "Theoretical/conceptual soundness",
                "b_impl": "Implementation quality",
                "b_deploy": "Operational stability"
            },
            weights={
                "b_theory": 0.40,
                "b_impl": 0.35,
                "b_deploy": 0.25
            },
            description=layer_req.get("description", ""),
            dependencies=layer_req.get("dependencies", []),
            required_methods=layer_req.get("required_methods", []),
            validation_rules=layer_req.get("validation_rules", {}),
        )

    def _enrich_metadata(self, symbol: str, metadata: dict[str, Any]) -> LayerMetadata:
        """
        Enrich layer metadata with information from layer_requirements.json.

        Args:
            symbol: Layer symbol
            metadata: Base metadata from module

        Returns:
            Enriched LayerMetadata
        """
        layer_req = self._layer_requirements.get("layers", {}).get(symbol, {})

        enriched = LayerMetadata(**metadata)

        if "dependencies" not in enriched and "dependencies" in layer_req:
            enriched["dependencies"] = layer_req["dependencies"]

        if "required_methods" not in enriched and "required_methods" in layer_req:
            enriched["required_methods"] = layer_req["required_methods"]

        if "validation_rules" not in enriched and "validation_rules" in layer_req:
            enriched["validation_rules"] = layer_req["validation_rules"]

        if "description" not in enriched and "description" in layer_req:
            enriched["description"] = layer_req["description"]

        return enriched

    def _generate_compatibility_matrix(self) -> None:
        """
        Generate layer compatibility matrix based on LAYER_REQUIREMENTS.

        Two layers are compatible if:
        1. Neither has a dependency on the other (no circular deps)
        2. Their combined dependencies don't create cycles
        3. They don't have conflicting validation rules
        """
        layers = self._layer_requirements.get("layers", {})

        for symbol1 in self.LAYER_SYMBOLS:
            for symbol2 in self.LAYER_SYMBOLS:
                if symbol1 == symbol2:
                    self._compatibility_matrix[(symbol1, symbol2)] = True
                    continue

                compatible = self._check_layer_compatibility(
                    symbol1, symbol2, layers
                )
                self._compatibility_matrix[(symbol1, symbol2)] = compatible

    def _check_layer_compatibility(
        self,
        layer1: str,
        layer2: str,
        layers: dict[str, Any]
    ) -> bool:
        """
        Check if two layers can coexist.

        Args:
            layer1: First layer symbol
            layer2: Second layer symbol
            layers: Layer definitions from requirements

        Returns:
            True if layers are compatible
        """
        layer1_info = layers.get(layer1, {})
        layer2_info = layers.get(layer2, {})

        deps1 = set(layer1_info.get("dependencies", []))
        deps2 = set(layer2_info.get("dependencies", []))

        if layer1 in deps2 and layer2 in deps1:
            return False

        if layer1 in deps2 and self._creates_cycle(layer1, deps1, layers):
            return False

        if layer2 in deps1 and self._creates_cycle(layer2, deps2, layers):
            return False

        critical1 = layer1_info.get("validation_rules", {}).get("critical", False)
        critical2 = layer2_info.get("validation_rules", {}).get("critical", False)

        if critical1 and critical2:
            return True

        return True

    def _creates_cycle(
        self,
        start_layer: str,
        dependencies: set[str],
        layers: dict[str, Any]
    ) -> bool:
        """
        Check if adding dependencies would create a cycle.

        Args:
            start_layer: Starting layer
            dependencies: Dependencies to check
            layers: All layer definitions

        Returns:
            True if a cycle would be created
        """
        visited = set()

        def visit(layer: str) -> bool:
            if layer in visited:
                return True
            if layer == start_layer and visited:
                return True

            visited.add(layer)

            layer_deps = layers.get(layer, {}).get("dependencies", [])
            return any(visit(dep) for dep in layer_deps)

        for dep in dependencies:
            visited.clear()
            if visit(dep):
                return True

        return False

    def get_all_layer_metadata(self) -> dict[str, LayerMetadata]:
        """
        Get unified metadata for all COHORT_2024 layers.

        Returns:
            Dictionary mapping layer symbols to LayerMetadata
        """
        return self._metadata.copy()

    def get_layer_by_symbol(self, symbol: str) -> LayerMetadata | None:
        """
        Lookup layer metadata by symbol.

        Args:
            symbol: Layer symbol (@u, @C, @chain, @m, @q, @d, @p, @b)

        Returns:
            LayerMetadata or None if not found
        """
        return self._metadata.get(symbol)

    def validate_metadata_completeness(self) -> dict[str, Any]:
        """
        Validate metadata completeness across all layers.

        Returns:
            Validation report with:
            - complete: List of layers with complete metadata
            - incomplete: Dict of layers with missing fields
            - missing_layers: List of expected layers not found
            - validation_passed: Overall validation status
        """
        complete = []
        incomplete = {}
        missing_layers = []

        for symbol in self.LAYER_SYMBOLS:
            if symbol not in self._metadata:
                missing_layers.append(symbol)
                continue

            metadata = self._metadata[symbol]
            missing_fields = []

            for field in self.REQUIRED_METADATA_FIELDS:
                if field not in metadata or not metadata[field]:
                    missing_fields.append(field)

            if missing_fields:
                incomplete[symbol] = missing_fields
            else:
                complete.append(symbol)

        return {
            "complete": complete,
            "incomplete": incomplete,
            "missing_layers": missing_layers,
            "validation_passed": len(incomplete) == 0 and len(missing_layers) == 0,
            "total_layers": len(self.LAYER_SYMBOLS),
            "discovered_layers": len(self._metadata),
        }

    def get_layer_compatibility_matrix(self) -> dict[str, dict[str, bool]]:
        """
        Get layer compatibility matrix showing which layers can coexist.

        Returns:
            Nested dict: {layer1: {layer2: compatible_bool}}
        """
        matrix = {}

        for symbol1 in self.LAYER_SYMBOLS:
            matrix[symbol1] = {}
            for symbol2 in self.LAYER_SYMBOLS:
                matrix[symbol1][symbol2] = self._compatibility_matrix.get(
                    (symbol1, symbol2), True
                )

        return matrix

    def get_layer_dependencies(self, symbol: str) -> list[str]:
        """
        Get dependencies for a specific layer.

        Args:
            symbol: Layer symbol

        Returns:
            List of dependency layer symbols
        """
        metadata = self._metadata.get(symbol)
        if metadata and "dependencies" in metadata:
            return metadata["dependencies"]

        layer_info = self._layer_requirements.get("layers", {}).get(symbol, {})
        return layer_info.get("dependencies", [])

    def get_compatible_layers(self, symbol: str) -> list[str]:
        """
        Get all layers compatible with the given layer.

        Args:
            symbol: Layer symbol

        Returns:
            List of compatible layer symbols
        """
        compatible = []

        for other_symbol in self.LAYER_SYMBOLS:
            if self._compatibility_matrix.get((symbol, other_symbol), False):
                compatible.append(other_symbol)

        return compatible

    def export_metadata_summary(self) -> dict[str, Any]:
        """
        Export comprehensive metadata summary for all layers.

        Returns:
            Summary dict with all layers, validation, and compatibility
        """
        return {
            "cohort_id": "COHORT_2024",
            "wave_version": "REFACTOR_WAVE_2024_12",
            "total_layers": len(self.LAYER_SYMBOLS),
            "layers": self.get_all_layer_metadata(),
            "validation": self.validate_metadata_completeness(),
            "compatibility_matrix": self.get_layer_compatibility_matrix(),
            "dependency_graph": {
                symbol: self.get_layer_dependencies(symbol)
                for symbol in self.LAYER_SYMBOLS
            },
        }


def create_default_registry() -> LayerMetadataRegistry:
    """
    Create LayerMetadataRegistry with default paths and load all metadata.

    Returns:
        Initialized and loaded LayerMetadataRegistry
    """
    registry = LayerMetadataRegistry()
    registry.load()
    return registry
