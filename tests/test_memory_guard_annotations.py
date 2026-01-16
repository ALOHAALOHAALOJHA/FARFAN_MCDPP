"""Tests for memory guard degradation annotations."""

import pytest
from farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller import ResourceLimits


class TestMemoryGuardAnnotations:
    """Test memory guard degradation annotations."""

    def test_resource_limits_degradation_metadata(self):
        # Check that class variables exist
        assert hasattr(ResourceLimits, "_DEGRADATION_INSTANCE")
        assert hasattr(ResourceLimits, "_FALLBACK_STRATEGY")

        # Check specific values
        assert ResourceLimits._DEGRADATION_INSTANCE == "MEMORY_GUARD_8"
        assert ResourceLimits._FALLBACK_STRATEGY == "PREFLIGHT_FAIL_FAST"

    def test_resource_limits_attributes(self):
        limits = ResourceLimits(memory_mb=1024, cpu_seconds=180, disk_mb=250, file_descriptors=512)

        assert limits.memory_mb == 1024
        assert limits.cpu_seconds == 180
        assert limits.disk_mb == 250
        assert limits.file_descriptors == 512

    def test_resource_limits_validation(self):
        # Valid limits
        limits = ResourceLimits(memory_mb=512, cpu_seconds=60, disk_mb=100, file_descriptors=128)
        assert limits.memory_mb == 512

        # Invalid memory_mb
        with pytest.raises(ValueError, match="memory_mb must be >= 256"):
            ResourceLimits(memory_mb=128)

        # Invalid cpu_seconds
        with pytest.raises(ValueError, match="cpu_seconds must be >= 10"):
            ResourceLimits(cpu_seconds=5)

        # Invalid disk_mb
        with pytest.raises(ValueError, match="disk_mb must be >= 50"):
            ResourceLimits(disk_mb=25)

        # Invalid file_descriptors
        with pytest.raises(ValueError, match="file_descriptors must be >= 64"):
            ResourceLimits(file_descriptors=32)

    def test_resource_limits_docstring_contains_degradation_info(self):
        limits = ResourceLimits()

        # Check that the class docstring contains degradation information
        docstring = ResourceLimits.__doc__
        assert "Degradation Instance: 8" in docstring
        assert "Pattern: MEMORY_GUARD" in docstring
        assert "Fallback Behavior" in docstring
        assert "Recovery:" in docstring
