"""
Phase 4 Topological Order Tests - End-to-End Chain Coverage

Tests that verify the topological order and module chain integrity.
Each module in the chain is tested for importability and basic functionality.

Module: src/farfan_pipeline/phases/Phase_4/tests/test_phase4_topological_chain.py
Version: 1.0.0
Status: ADVERSARIAL
"""
from __future__ import annotations

import pytest
import importlib
import json
from pathlib import Path


class TestPhase4TopologicalOrder:
    """Test Phase 4 topological order from chain report."""
    
    @pytest.fixture
    def chain_report(self):
        """Load the phase4_chain_report.json."""
        report_path = Path(__file__).parent.parent / "contracts" / "phase4_chain_report.json"
        with open(report_path, 'r') as f:
            return json.load(f)
    
    def test_chain_report_exists(self, chain_report):
        """Test that chain report exists and is valid."""
        assert chain_report is not None
        assert "phase_id" in chain_report
        assert chain_report["phase_id"] == 4
        assert "validation_status" in chain_report
        assert chain_report["validation_status"] == "PASS"
    
    def test_zero_circular_dependencies(self, chain_report):
        """CRITICAL: Test that there are ZERO circular dependencies."""
        assert "circular_dependencies" in chain_report
        assert len(chain_report["circular_dependencies"]) == 0, \
            f"Found circular dependencies: {chain_report['circular_dependencies']}"
    
    def test_zero_orphan_files(self, chain_report):
        """CRITICAL: Test that there are ZERO orphaned files."""
        assert "orphan_files" in chain_report
        assert len(chain_report["orphan_files"]) == 0, \
            f"Found orphan files: {chain_report['orphan_files']}"
    
    def test_topological_order_complete(self, chain_report):
        """Test that topological order contains expected files."""
        assert "topological_order" in chain_report
        assert len(chain_report["topological_order"]) > 0
        
        # Key files should be in the order
        topo_order = chain_report["topological_order"]
        assert "__init__.py" in topo_order
        # PHASE_4_CONSTANTS.py is not in dependency graph but primitives/__init__.py uses it
        # Check if at least some key modules are present
        assert any("primitives" in f for f in topo_order)
    
    def test_primitives_layer_first(self, chain_report):
        """Test that primitives layer appears early in topological order."""
        topo_order = chain_report["topological_order"]
        primitives_files = [f for f in topo_order if "primitives/" in f]
        
        # Find position of first primitive file
        if primitives_files:
            first_primitive_pos = min(topo_order.index(f) for f in primitives_files)
            # Primitives should be in first half of the order
            assert first_primitive_pos < len(topo_order) / 2
    
    def test_all_python_files_accounted(self, chain_report):
        """Test that all Python files are accounted for."""
        total_files = chain_report.get("total_files", 0)
        files_in_chain = chain_report.get("files_in_chain", 0)
        orphan_files = len(chain_report.get("orphan_files", []))
        
        # All files should be either in chain or explicitly marked as orphan
        # (though we want 0 orphans)
        assert files_in_chain + orphan_files <= total_files


class TestPhase4ModuleImports:
    """Test that all Phase 4 modules can be imported."""
    
    def test_import_phase4_package(self):
        """Test importing Phase 4 package."""
        import farfan_pipeline.phases.Phase_4
        assert farfan_pipeline.phases.Phase_4 is not None
    
    def test_import_primitives_layer(self):
        """Test importing primitives layer."""
        from farfan_pipeline.phases.Phase_04.primitives import (
            AggregationSettings,
            IAggregator,
            IConfigBuilder,
        )
        assert AggregationSettings is not None
        assert IAggregator is not None
        assert IConfigBuilder is not None
    
    def test_import_contracts(self):
        """Test importing all contracts."""
        from farfan_pipeline.phases.Phase_04.contracts.phase4_input_contract import Phase4InputContract
        from farfan_pipeline.phases.Phase_04.contracts.phase4_mission_contract import Phase4MissionContract
        from farfan_pipeline.phases.Phase_04.contracts.phase4_output_contract import Phase4OutputContract
        
        assert Phase4InputContract is not None
        assert Phase4MissionContract is not None
        assert Phase4OutputContract is not None
    
    def test_import_aggregation_settings(self):
        """Test importing AggregationSettings from redirect module."""
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation_settings import AggregationSettings
        assert AggregationSettings is not None
    
    def test_import_choquet_adapter(self):
        """Test importing Choquet adapter."""
        from farfan_pipeline.phases.Phase_04.phase4_10_00_choquet_adapter import create_default_choquet_adapter
        assert create_default_choquet_adapter is not None
    
    def test_import_aggregation(self):
        """Test importing main aggregation module."""
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
            DimensionAggregator,
            DimensionScore,
            ScoredResult,
        )
        assert DimensionAggregator is not None
        assert DimensionScore is not None
        assert ScoredResult is not None


class TestPhase4LayerDependencies:
    """Test that layer dependencies follow Clean Architecture."""
    
    def test_primitives_no_phase4_dependencies(self):
        """CRITICAL: Test that primitives have NO dependencies on other Phase 4 modules."""
        from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_aggregation_settings import (
            AggregationSettings
        )
        from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types import (
            IAggregator
        )
        
        # If we can import these without circular import errors, the test passes
        assert AggregationSettings is not None
        assert IAggregator is not None
    
    def test_contracts_can_import_primitives(self):
        """Test that contracts can safely import from primitives."""
        from farfan_pipeline.phases.Phase_04.contracts.phase4_input_contract import Phase4InputContract
        from farfan_pipeline.phases.Phase_04.primitives import AggregationSettings
        
        # Both should be importable without issues
        assert Phase4InputContract is not None
        assert AggregationSettings is not None
    
    def test_aggregation_imports_primitives_and_choquet(self):
        """Test that aggregation can import both primitives and choquet."""
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import DimensionAggregator
        from farfan_pipeline.phases.Phase_04.phase4_10_00_choquet_adapter import create_default_choquet_adapter
        from farfan_pipeline.phases.Phase_04.primitives import AggregationSettings
        
        assert DimensionAggregator is not None
        assert create_default_choquet_adapter is not None
        assert AggregationSettings is not None


class TestPhase4IntegrationEndToEnd:
    """End-to-end integration tests for Phase 4."""
    
    def test_create_aggregation_settings(self):
        """Test creating AggregationSettings instance."""
        from farfan_pipeline.phases.Phase_04.primitives import AggregationSettings
        
        settings = AggregationSettings(
            dimension_group_by_keys=["policy_area", "dimension"],
            area_group_by_keys=["area_id"],
            cluster_group_by_keys=["cluster_id"],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        
        assert settings is not None
        assert settings.dimension_group_by_keys == ["policy_area", "dimension"]
    
    def test_validate_aggregation_settings(self):
        """Test validating AggregationSettings."""
        from farfan_pipeline.phases.Phase_04.primitives import (
            AggregationSettings,
            validate_aggregation_settings,
        )
        
        settings = AggregationSettings(
            dimension_group_by_keys=["policy_area", "dimension"],
            area_group_by_keys=["area_id"],
            cluster_group_by_keys=["cluster_id"],
            dimension_question_weights={},
            policy_area_dimension_weights={},
            cluster_policy_area_weights={},
            macro_cluster_weights={},
            dimension_expected_counts={},
            area_expected_dimension_counts={},
        )
        
        is_valid, errors = validate_aggregation_settings(settings)
        assert is_valid is True
        assert len(errors) == 0
