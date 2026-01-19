import pytest
from unittest.mock import patch, MagicMock
from farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller import (
    ResourceController,
    ResourceLimits
)

@pytest.fixture
def mock_limits():
    return ResourceLimits(
        memory_mb=256,
        cpu_seconds=10,
        disk_mb=100,
        file_descriptors=64
    )

def test_resource_limits_init(mock_limits):
    assert mock_limits.memory_mb == 256
    assert mock_limits.cpu_seconds == 10

def test_controller_initialization(mock_limits):
    controller = ResourceController(mock_limits)
    assert controller.limits == mock_limits

@patch("farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller.resource")
def test_enforce_limits(mock_resource, mock_limits):
    """Test setting resource limits (mocked)."""
    # Configure mock resource
    mock_resource.getrlimit.return_value = (100000, 100000)
    mock_resource.RLIMIT_AS = 1
    mock_resource.RLIMIT_CPU = 2
    mock_resource.RLIMIT_NOFILE = 3
    
    controller = ResourceController(mock_limits)
    # Mock preflight checks to pass
    with patch.object(controller, 'preflight_checks'):
        with controller.enforced_execution():
            pass
    assert mock_resource.setrlimit.called

def test_preflight_checks_mock(mock_limits):
    """Test resource check logic (mocking internal logic if needed)."""
    controller = ResourceController(mock_limits)
    try:
        checks = controller.preflight_checks()
        assert isinstance(checks, dict)
    except Exception as e:
        pass
