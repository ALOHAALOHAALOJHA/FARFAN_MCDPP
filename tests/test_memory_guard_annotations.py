# tests/test_memory_guard_annotations.py
import pytest
from farfan_pipeline.phases.Phase_zero.phase0_30_00_resource_controller import ResourceLimits


class TestMemoryGuardAnnotations:
    """Validate memory guard degradation annotations."""
    
    def test_resource_limits_has_degradation_metadata(self):
        limits = ResourceLimits()
        
        # Check that degradation metadata exists as class variables
        assert hasattr(ResourceLimits, '_DEGRADATION_INSTANCE')
        assert hasattr(ResourceLimits, '_FALLBACK_STRATEGY')
        
        # Check specific values
        assert ResourceLimits._DEGRADATION_INSTANCE == "MEMORY_GUARD_8"
        assert ResourceLimits._FALLBACK_STRATEGY == "PREFLIGHT_FAIL_FAST"
    
    def test_resource_limits_functionality(self):
        limits = ResourceLimits(
            memory_mb=4096,
            cpu_seconds=600,
            disk_mb=1000,
            file_descriptors=2048
        )
        
        assert limits.memory_mb == 4096
        assert limits.cpu_seconds == 600
        assert limits.disk_mb == 1000
        assert limits.file_descriptors == 2048
    
    def test_resource_limits_validation(self):
        # Test valid limits
        limits = ResourceLimits(memory_mb=512, cpu_seconds=60, disk_mb=100, file_descriptors=128)
        assert limits.memory_mb == 512
        
        # Test invalid memory_mb
        with pytest.raises(ValueError, match="memory_mb must be >= 256"):
            ResourceLimits(memory_mb=128)
        
        # Test invalid cpu_seconds
        with pytest.raises(ValueError, match="cpu_seconds must be >= 10"):
            ResourceLimits(cpu_seconds=5)
        
        # Test invalid disk_mb
        with pytest.raises(ValueError, match="disk_mb must be >= 50"):
            ResourceLimits(disk_mb=25)
        
        # Test invalid file_descriptors
        with pytest.raises(ValueError, match="file_descriptors must be >= 64"):
            ResourceLimits(file_descriptors=32)