"""
Tests for Interphase Signature Inspection and Validation Tools
==============================================================

This module tests the interphase signature inspection tools to ensure
they correctly identify and validate function signatures.

Author: F.A.R.F.A.N Test Suite
Version: 1.0.0
"""

import json
import pytest
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "audit"))

from scripts.audit.inspect_interphase_signatures import (
    InterphaseSignatureInspector,
    InspectionReport,
    FunctionSignatureInfo,
    InterfaceContract,
)


class TestInterphaseSignatureInspector:
    """Test suite for the interphase signature inspector."""
    
    @pytest.fixture
    def inspector(self):
        """Create an inspector instance."""
        return InterphaseSignatureInspector(project_root)
    
    def test_inspector_initialization(self, inspector):
        """Test that inspector initializes correctly."""
        assert inspector.project_root == project_root
        assert inspector.phases_dir.exists()
        assert inspector.phases_dir.name == "phases"
    
    def test_inspect_all_phases(self, inspector):
        """Test that inspection runs and produces a report."""
        report = inspector.inspect_all_phases()
        
        assert isinstance(report, InspectionReport)
        assert report.total_phases > 0
        assert report.total_interphase_modules > 0
        assert report.total_functions > 0
        assert report.total_contracts > 0
    
    def test_signature_extraction(self, inspector):
        """Test that signatures are correctly extracted."""
        report = inspector.inspect_all_phases()
        
        # Check that we have signatures
        assert len(report.signatures) > 0
        
        # Verify signature structure
        for sig in report.signatures[:5]:  # Check first 5
            assert isinstance(sig, FunctionSignatureInfo)
            assert sig.function_name
            assert sig.module_path
            assert sig.phase
            assert isinstance(sig.parameters, list)
            assert isinstance(sig.return_type, str)
            assert isinstance(sig.is_public, bool)
    
    def test_contract_identification(self, inspector):
        """Test that contracts are correctly identified."""
        report = inspector.inspect_all_phases()
        
        # Check that we have contracts
        assert len(report.contracts) > 0
        
        # Verify contract structure
        for contract in report.contracts[:5]:  # Check first 5
            assert isinstance(contract, InterfaceContract)
            assert contract.source_phase
            assert contract.target_phase
            assert contract.interface_type in ['bridge', 'adapter', 'validator']
            assert contract.compatibility_status in ['compatible', 'incompatible', 'warning', 'unknown']
    
    def test_no_critical_issues(self, inspector):
        """Test that there are no critical incompatibilities."""
        report = inspector.inspect_all_phases()
        
        # Should have zero incompatible contracts
        assert report.compatibility_summary['incompatible'] == 0, \
            "Should have no critical incompatibilities"
    
    def test_report_serialization(self, inspector):
        """Test that report can be serialized to dict/JSON."""
        report = inspector.inspect_all_phases()
        
        # Convert to dict
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert 'timestamp' in report_dict
        assert 'total_phases' in report_dict
        assert 'signatures' in report_dict
        assert 'contracts' in report_dict
        
        # Verify it can be serialized to JSON
        json_str = json.dumps(report_dict, indent=2)
        assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
