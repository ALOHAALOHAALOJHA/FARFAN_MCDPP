"""
Tests for Discovery Protocol: Mandatory Inventory Acquisition
"""

import pytest
from pathlib import Path
from farfan_pipeline.agents.discovery_protocol import (
    DiscoveryProtocol,
    RepositoryInventory,
    InventoryComponent,
)


class TestDiscoveryProtocol:
    """Test discovery protocol implementation."""

    @pytest.fixture
    def repository_root(self) -> Path:
        """Get actual repository root for testing."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not find repository root")

    @pytest.fixture
    def discovery_protocol(self, repository_root: Path) -> DiscoveryProtocol:
        """Create discovery protocol instance."""
        return DiscoveryProtocol(repository_root)

    def test_discovery_protocol_initialization(
        self, repository_root: Path
    ) -> None:
        """Test discovery protocol can be initialized."""
        protocol = DiscoveryProtocol(repository_root)
        assert protocol.repository_root == repository_root

    def test_execute_repository_scan(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test full repository scan execution."""
        inventory = discovery_protocol.execute_repository_scan()

        assert isinstance(inventory, RepositoryInventory)
        assert inventory.total_files > 0
        assert inventory.total_lines_of_code > 0
        assert len(inventory.python_files) > 0

    def test_scan_python_files(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test Python file scanning."""
        python_files = discovery_protocol._scan_python_files()

        assert len(python_files) > 0
        assert all(f.suffix == ".py" for f in python_files)
        assert all(f.exists() for f in python_files)

    def test_scan_test_files(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test test file scanning."""
        test_files = discovery_protocol._scan_test_files()

        assert len(test_files) > 0
        assert all(
            f.name.startswith("test_") or f.name.endswith("_test.py")
            for f in test_files
        )

    def test_scan_config_files(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test configuration file scanning."""
        config_files = discovery_protocol._scan_config_files()

        assert len(config_files) > 0
        assert any(f.name == "pyproject.toml" for f in config_files)

    def test_scan_documentation_files(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test documentation file scanning."""
        doc_files = discovery_protocol._scan_documentation_files()

        assert len(doc_files) > 0
        assert any(f.name == "README.md" for f in doc_files)

    def test_extract_dependencies(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test dependency extraction."""
        dependencies = discovery_protocol._extract_dependencies()

        assert len(dependencies) > 0
        assert "fastapi" in dependencies
        assert "pydantic" in dependencies
        assert "pytest" in dependencies

    def test_parse_requirements_txt(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test requirements.txt parsing."""
        req_file = discovery_protocol.repository_root / "requirements.txt"

        if req_file.exists():
            deps = discovery_protocol._parse_requirements_txt(req_file)
            assert len(deps) > 0
            assert all(isinstance(name, str) for name in deps.keys())
            assert all(isinstance(ver, str) for ver in deps.values())

    def test_parse_pyproject_toml(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test pyproject.toml parsing."""
        toml_file = discovery_protocol.repository_root / "pyproject.toml"

        if toml_file.exists():
            deps = discovery_protocol._parse_pyproject_toml(toml_file)
            assert len(deps) > 0

    def test_analyze_architecture(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test architecture analysis."""
        arch = discovery_protocol._analyze_architecture()

        assert isinstance(arch, dict)
        assert "has_src_layout" in arch
        assert "package_structure" in arch
        assert "top_level_modules" in arch

    def test_count_lines_of_code(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test line counting functionality."""
        python_files = discovery_protocol._scan_python_files()
        total_lines = discovery_protocol._count_lines_of_code(python_files)

        assert total_lines > 0

    def test_generate_inventory_report(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test inventory report generation."""
        inventory = discovery_protocol.execute_repository_scan()
        report = discovery_protocol.generate_inventory_report(inventory)

        assert isinstance(report, str)
        assert len(report) > 0
        assert "REPOSITORY INVENTORY REPORT" in report
        assert "[OBSERVATION]" in report
        assert "Total Files:" in report
        assert "Total Lines of Code:" in report
        assert "FILE CATEGORIES:" in report
        assert "ARCHITECTURE:" in report
        assert "KEY DEPENDENCIES:" in report

    def test_repository_not_found_raises_error(self) -> None:
        """Test error handling for non-existent repository."""
        fake_path = Path("/nonexistent/repository")
        protocol = DiscoveryProtocol(fake_path)

        with pytest.raises(FileNotFoundError):
            protocol.execute_repository_scan()

    def test_inventory_component_creation(self) -> None:
        """Test InventoryComponent dataclass."""
        component = InventoryComponent(
            component_type="module",
            path="src/farfan_pipeline/agents",
            metadata={"files": 3, "lines": 1000},
        )

        assert component.component_type == "module"
        assert component.path == "src/farfan_pipeline/agents"
        assert component.metadata["files"] == 3

    def test_repository_inventory_structure(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test repository inventory has correct structure."""
        inventory = discovery_protocol.execute_repository_scan()

        assert isinstance(inventory.python_files, list)
        assert isinstance(inventory.test_files, list)
        assert isinstance(inventory.config_files, list)
        assert isinstance(inventory.documentation_files, list)
        assert isinstance(inventory.data_files, list)
        assert isinstance(inventory.dependencies, dict)
        assert isinstance(inventory.architecture_summary, dict)
        assert isinstance(inventory.total_files, int)
        assert isinstance(inventory.total_lines_of_code, int)

    def test_scan_results_sorted(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test that scan results are sorted."""
        python_files = discovery_protocol._scan_python_files()
        assert python_files == sorted(python_files)

        test_files = discovery_protocol._scan_test_files()
        assert test_files == sorted(test_files)

    def test_scan_filters_hidden_files(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test that scans exclude hidden files appropriately."""
        python_files = discovery_protocol._scan_python_files()
        assert not any(".git" in str(f) for f in python_files)

    def test_dependencies_have_versions(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test that extracted dependencies include versions."""
        dependencies = discovery_protocol._extract_dependencies()

        for name, version in dependencies.items():
            assert len(name) > 0
            assert len(version) > 0
            assert version[0].isdigit()

    def test_report_includes_statistics(
        self, discovery_protocol: DiscoveryProtocol
    ) -> None:
        """Test report includes key statistics."""
        inventory = discovery_protocol.execute_repository_scan()
        report = discovery_protocol.generate_inventory_report(inventory)

        assert str(inventory.total_files) in report
        assert "Python Files:" in report
        assert "Test Files:" in report
        assert "Config Files:" in report
