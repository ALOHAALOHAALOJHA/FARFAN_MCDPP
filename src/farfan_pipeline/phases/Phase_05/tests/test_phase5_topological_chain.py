"""
Phase 5 Topological Order Tests - End-to-End Chain Coverage

Tests that verify the topological order and module chain integrity.

Module: src/farfan_pipeline/phases/Phase_5/tests/test_phase5_topological_chain.py
Version: 1.0.0
Status: ADVERSARIAL
"""
from __future__ import annotations

import pytest
import json
from pathlib import Path


class TestPhase5TopologicalOrder:
    """Test Phase 5 topological order from chain report."""
    
    @pytest.fixture
    def chain_report(self):
        """Load the phase5_chain_report.json."""
        report_path = Path(__file__).resolve().parent.parent / "contracts" / "phase5_chain_report.json"
        with open(report_path, 'r') as f:
            return json.load(f)
    
    def test_chain_report_exists(self, chain_report):
        """Test that chain report exists and is valid."""
        assert chain_report is not None
        assert "phase_id" in chain_report
        assert chain_report["phase_id"] == 5
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
        
        topo_order = chain_report["topological_order"]
        assert "__init__.py" in topo_order


class TestPhase5ModuleImports:
    """Test that all Phase 5 modules can be imported."""
    
    def test_import_phase5_package(self):
        """Test importing Phase 5 package."""
        import farfan_pipeline.phases.Phase_5
        assert farfan_pipeline.phases.Phase_5 is not None
    
    def test_import_constants(self):
        """Test importing Phase 5 constants."""
        from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
            DIMENSIONS_PER_AREA,
            EXPECTED_AREA_SCORE_COUNT,
        )
        assert DIMENSIONS_PER_AREA == 6
        assert EXPECTED_AREA_SCORE_COUNT == 10
    
    def test_import_contracts(self):
        """Test importing all Phase 5 contracts."""
        from farfan_pipeline.phases.Phase_05.contracts.phase5_input_contract import Phase5InputContract
        from farfan_pipeline.phases.Phase_05.contracts.phase5_mission_contract import Phase5MissionContract
        from farfan_pipeline.phases.Phase_05.contracts.phase5_output_contract import Phase5OutputContract
        
        assert Phase5InputContract is not None
        assert Phase5MissionContract is not None
        assert Phase5OutputContract is not None
    
    def test_import_area_aggregation(self):
        """Test importing area aggregation module."""
        from farfan_pipeline.phases.Phase_05.phase5_10_00_area_aggregation import (
            AreaScore,
            AreaPolicyAggregator,
        )
        assert AreaScore is not None
        assert AreaPolicyAggregator is not None
    
    def test_import_area_validation(self):
        """Test importing area validation module."""
        from farfan_pipeline.phases.Phase_05.phase5_10_00_area_validation import (
            validate_phase5_output,
        )
        assert validate_phase5_output is not None
    
    def test_import_area_integration(self):
        """Test importing area integration module."""
        from farfan_pipeline.phases.Phase_05.phase5_10_00_area_integration import (
            run_phase5_aggregation,
        )
        assert run_phase5_aggregation is not None


class TestPhase5Dependencies:
    """Test Phase 5 dependencies."""
    
    def test_phase5_imports_from_phase4(self):
        """Test that Phase 5 can import DimensionScore from Phase 4."""
        from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import DimensionScore
        from farfan_pipeline.phases.Phase_05.phase5_10_00_area_aggregation import AreaScore
        
        assert DimensionScore is not None
        assert AreaScore is not None
    
    def test_phase5_contracts_validate_compatibility(self):
        """Test that Phase 5 contracts validate Phase 4 compatibility."""
        from farfan_pipeline.phases.Phase_05.contracts.phase5_input_contract import Phase5InputContract
        
        # Phase 5 input should match Phase 4 output
        assert Phase5InputContract.EXPECTED_INPUT_COUNT == 60


class TestPhase5IntegrationEndToEnd:
    """End-to-end integration tests for Phase 5."""
    
    def test_phase5_constants_consistency(self):
        """Test that Phase 5 constants are mathematically consistent."""
        from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
            DIMENSIONS_PER_AREA,
            EXPECTED_AREA_SCORE_COUNT,
        )
        
        # 60 dimension scores = 6 dimensions × 10 areas
        # 10 area scores = 1 per policy area
        assert DIMENSIONS_PER_AREA * EXPECTED_AREA_SCORE_COUNT == 60
