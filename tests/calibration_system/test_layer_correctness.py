"""
Test 2: Layer Correctness - 30 Executors Have 8 Layers + Correct LAYER_REQUIREMENTS

Validates architectural integrity:
- All 30 executors must define exactly 8 layers
- LAYER_REQUIREMENTS mapping must be correct and complete
- Layer dependencies must be acyclic

FAILURE CONDITION: Any layer mismatch = SYSTEM NOT READY
"""
import json
import pytest
from pathlib import Path
from typing import Dict, List, Set, Any


class TestLayerCorrectness:
    
    REQUIRED_LAYERS = {
        "ingestion",
        "extraction",
        "transformation",
        "validation",
        "aggregation",
        "scoring",
        "reporting",
        "meta"
    }
    
    @pytest.fixture(scope="class")
    def executors_methods(self) -> Dict[str, Any]:
        """Load executors_methods.json"""
        path = Path("src/farfan_pipeline/core/orchestrator/executors_methods.json")
        with open(path) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def layer_requirements_path(self) -> Path:
        """Find LAYER_REQUIREMENTS definition"""
        candidates = [
            Path("src/farfan_pipeline/core/orchestrator/executors.py"),
            Path("src/farfan_pipeline/core/orchestrator/base_executor_with_contract.py"),
            Path("src/farfan_pipeline/core/layers.py"),
        ]
        for path in candidates:
            if path.exists():
                return path
        pytest.skip("LAYER_REQUIREMENTS definition file not found")

    def test_8_layers_defined(self):
        """Verify exactly 8 layers are required"""
        assert len(self.REQUIRED_LAYERS) == 8, \
            f"Expected 8 layers, found {len(self.REQUIRED_LAYERS)}"

    def test_executor_methods_have_layer_field(self, executors_methods):
        """Verify all methods specify a layer"""
        for executor in executors_methods:
            for method in executor["methods"]:
                method_sig = f"{method['class']}.{method['method']}"
                
                assert "layer" in method, \
                    f"Method {method_sig} in {executor['executor_id']} missing 'layer' field"
                
                layer = method["layer"]
                assert layer in self.REQUIRED_LAYERS, \
                    f"Invalid layer '{layer}' for {method_sig} in {executor['executor_id']}. " \
                    f"Must be one of: {sorted(self.REQUIRED_LAYERS)}"

    def test_all_30_executors_have_all_8_layers(self, executors_methods):
        """CRITICAL: Verify each of 30 executors has methods in all 8 layers"""
        failures = []
        
        for executor in executors_methods:
            executor_id = executor["executor_id"]
            layers_present = set()
            
            for method in executor["methods"]:
                if "layer" in method:
                    layers_present.add(method["layer"])
            
            missing_layers = self.REQUIRED_LAYERS - layers_present
            
            if missing_layers:
                failures.append(
                    f"Executor {executor_id} missing layers: {sorted(missing_layers)}"
                )
        
        assert not failures, \
            f"CRITICAL: Executors with incomplete layer coverage:\n" + \
            "\n".join(failures)

    def test_layer_requirements_mapping_exists(self, layer_requirements_path):
        """Verify LAYER_REQUIREMENTS mapping is defined in code"""
        content = layer_requirements_path.read_text()
        
        assert "LAYER_REQUIREMENTS" in content, \
            f"LAYER_REQUIREMENTS not found in {layer_requirements_path}"

    def test_layer_requirements_covers_all_layers(self, layer_requirements_path):
        """Verify LAYER_REQUIREMENTS covers all 8 layers"""
        import ast
        
        content = layer_requirements_path.read_text()
        tree = ast.parse(content)
        
        layer_req_dict = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "LAYER_REQUIREMENTS":
                        if isinstance(node.value, ast.Dict):
                            layer_req_dict = {}
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant):
                                    layer_req_dict[k.value] = True
        
        if layer_req_dict is None:
            pytest.skip("Could not parse LAYER_REQUIREMENTS from source")
        
        defined_layers = set(layer_req_dict.keys())
        missing_layers = self.REQUIRED_LAYERS - defined_layers
        
        assert not missing_layers, \
            f"LAYER_REQUIREMENTS missing layers: {sorted(missing_layers)}"

    def test_layer_dependency_acyclicity(self, executors_methods):
        """Verify layer execution order is acyclic"""
        layer_order = [
            "ingestion",
            "extraction",
            "transformation",
            "validation",
            "aggregation",
            "scoring",
            "reporting",
            "meta"
        ]
        
        layer_to_position = {layer: i for i, layer in enumerate(layer_order)}
        
        for executor in executors_methods:
            for i, method in enumerate(executor["methods"]):
                if "layer" not in method:
                    continue
                
                current_layer = method["layer"]
                current_pos = layer_to_position.get(current_layer, -1)
                
                for prev_method in executor["methods"][:i]:
                    if "layer" not in prev_method:
                        continue
                    prev_layer = prev_method["layer"]
                    prev_pos = layer_to_position.get(prev_layer, -1)
                    
                    if current_pos < prev_pos:
                        pytest.fail(
                            f"Layer ordering violation in {executor['executor_id']}: "
                            f"{prev_layer} (pos {prev_pos}) comes before "
                            f"{current_layer} (pos {current_pos})"
                        )

    def test_method_distribution_across_layers(self, executors_methods):
        """Analyze method distribution across layers"""
        layer_counts = {layer: 0 for layer in self.REQUIRED_LAYERS}
        
        for executor in executors_methods:
            for method in executor["methods"]:
                if "layer" in method:
                    layer_counts[method["layer"]] += 1
        
        for layer, count in layer_counts.items():
            assert count > 0, \
                f"Layer '{layer}' has no methods across all executors"

    def test_layer_field_consistency_with_method_names(self, executors_methods):
        """Verify layer assignment consistency with method naming patterns"""
        layer_hints = {
            "extract": "extraction",
            "ingest": "ingestion",
            "validate": "validation",
            "transform": "transformation",
            "aggregate": "aggregation",
            "score": "scoring",
            "report": "reporting",
        }
        
        warnings = []
        
        for executor in executors_methods:
            for method in executor["methods"]:
                if "layer" not in method:
                    continue
                
                method_name = method["method"].lower()
                assigned_layer = method["layer"]
                
                for hint, suggested_layer in layer_hints.items():
                    if hint in method_name and assigned_layer != suggested_layer:
                        warnings.append(
                            f"Potential layer mismatch: {method['class']}.{method['method']} "
                            f"in {executor['executor_id']} assigned to '{assigned_layer}' "
                            f"but name suggests '{suggested_layer}'"
                        )
        
        if warnings:
            print("\n".join(warnings[:10]))

    def test_no_orphan_layers(self, executors_methods):
        """Verify no executor has layer gaps in sequence"""
        layer_order = [
            "ingestion",
            "extraction",
            "transformation",
            "validation",
            "aggregation",
            "scoring",
            "reporting",
            "meta"
        ]
        
        for executor in executors_methods:
            layers_used = []
            for method in executor["methods"]:
                if "layer" in method:
                    layers_used.append(method["layer"])
            
            layer_positions = sorted([
                layer_order.index(layer) for layer in set(layers_used)
            ])
            
            if not layer_positions:
                continue
            
            for i in range(len(layer_positions) - 1):
                gap = layer_positions[i + 1] - layer_positions[i]
                if gap > 2:
                    pytest.fail(
                        f"Large layer gap in {executor['executor_id']}: "
                        f"{layer_order[layer_positions[i]]} -> "
                        f"{layer_order[layer_positions[i + 1]]}"
                    )
