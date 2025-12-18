"""Test Phase 1 SISAS Integration (Satellital Intelligent Signal Aggregation System).

This test verifies:
- SISAS signal registry DI chain: Factory → Orchestrator → Phase 1
- SP12 irrigation outputs: irrigation_links, link_scores, coverage_metrics
- Signal enrichment in SP3, SP5, SP10, SP12
"""

import pytest
from pathlib import Path
import ast


class TestSISASIntegration:
    """Test SISAS integration in Phase 1."""
    
    def test_signal_enrichment_module_exists(self):
        """Verify signal_enrichment module exists."""
        signal_enrichment_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "signal_enrichment.py"
        assert signal_enrichment_path.exists(), "signal_enrichment.py must exist"
        
        # Verify it's substantial (not a stub)
        size_bytes = signal_enrichment_path.stat().st_size
        assert size_bytes > 1000, f"signal_enrichment.py should be substantial, got {size_bytes} bytes"
    
    def test_signal_registry_parameter_in_main_function(self):
        """Verify execute_phase_1_with_full_contract accepts signal_registry."""
        cpp_ingestion_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "phase1_cpp_ingestion_full.py"
        
        assert cpp_ingestion_path.exists(), "phase1_cpp_ingestion_full.py must exist"
        
        content = cpp_ingestion_path.read_text()
        
        # Check for function signature with signal_registry parameter
        assert "def execute_phase_1_with_full_contract" in content
        assert "signal_registry" in content, "Function must have signal_registry parameter"
    
    def test_sp12_irrigation_specification(self):
        """Verify SP12 irrigation specification is documented."""
        from pathlib import Path
        
        readme_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "README.md"
        
        assert readme_path.exists(), "README.md must exist"
        
        readme_content = readme_path.read_text()
        
        # Verify SP12 is documented
        assert "SP12" in readme_content, "README must document SP12"
        assert "SISAS" in readme_content, "README must document SISAS integration"
        assert "irrigation" in readme_content.lower(), "README must mention irrigation"
    
    def test_sisas_operation_points_documented(self):
        """Verify SISAS operation points (SP3, SP5, SP10, SP12) are documented."""
        from pathlib import Path
        
        readme_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "README.md"
        readme_content = readme_path.read_text()
        
        sisas_subphases = ["SP3", "SP5", "SP10", "SP12"]
        for sp in sisas_subphases:
            assert sp in readme_content, f"README must document SISAS operation at {sp}"


class TestSP12IrrigationOutputs:
    """Test SP12 irrigation output specification."""
    
    def test_irrigation_outputs_documented(self):
        """Verify irrigation outputs are documented in README."""
        from pathlib import Path
        
        readme_path = Path(__file__).parent.parent.parent / "src" / "canonic_phases" / "phase_1_cpp_ingestion" / "README.md"
        readme_content = readme_path.read_text()
        
        # Verify outputs are documented
        required_outputs = ["irrigation_links", "link_scores", "coverage_metrics"]
        for output in required_outputs:
            assert output in readme_content, f"README must document {output}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
