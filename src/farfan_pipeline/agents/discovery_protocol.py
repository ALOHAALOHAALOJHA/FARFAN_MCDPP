"""
Discovery Protocol: Mandatory Inventory Acquisition

Implements triangulation phase with comprehensive repository scanning.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


MetadataDict: TypeAlias = dict[str, int | str | list[str] | dict[str, str]]
ArchitectureSummary: TypeAlias = dict[str, bool | list[str]]


@dataclass
class InventoryComponent:
    """Single inventory component discovered in repository."""

    component_type: str
    path: str
    metadata: MetadataDict


@dataclass
class RepositoryInventory:
    """Complete repository inventory from triangulation."""

    python_files: list[Path]
    test_files: list[Path]
    config_files: list[Path]
    documentation_files: list[Path]
    data_files: list[Path]
    dependencies: dict[str, str]
    architecture_summary: ArchitectureSummary
    total_files: int
    total_lines_of_code: int


class DiscoveryProtocol:
    """Implements mandatory inventory acquisition protocol."""

    def __init__(self, repository_root: Path) -> None:
        """
        Initialize discovery protocol.

        Args:
            repository_root: Root path of repository to scan
        """
        self.repository_root = repository_root

    def execute_repository_scan(self) -> RepositoryInventory:
        """
        Execute Step 1.1.1: Repository Scan Commands.

        Performs comprehensive triangulation of repository structure.

        Returns:
            Complete repository inventory

        Raises:
            FileNotFoundError: If repository root does not exist
        """
        if not self.repository_root.exists():
            raise FileNotFoundError(
                f"Repository root does not exist: {self.repository_root}"
            )

        python_files = self._scan_python_files()
        test_files = self._scan_test_files()
        config_files = self._scan_config_files()
        documentation_files = self._scan_documentation_files()
        data_files = self._scan_data_files()
        dependencies = self._extract_dependencies()
        architecture_summary = self._analyze_architecture()
        total_files = len(python_files) + len(test_files) + len(config_files)
        total_lines = self._count_lines_of_code(python_files)

        return RepositoryInventory(
            python_files=python_files,
            test_files=test_files,
            config_files=config_files,
            documentation_files=documentation_files,
            data_files=data_files,
            dependencies=dependencies,
            architecture_summary=architecture_summary,
            total_files=total_files,
            total_lines_of_code=total_lines,
        )

    def _scan_python_files(self) -> list[Path]:
        """Scan for Python source files."""
        return sorted(self.repository_root.rglob("*.py"))

    def _scan_test_files(self) -> list[Path]:
        """Scan for test files."""
        test_patterns = ["test_*.py", "*_test.py"]
        test_files: list[Path] = []
        for pattern in test_patterns:
            test_files.extend(self.repository_root.rglob(pattern))
        return sorted(set(test_files))

    def _scan_config_files(self) -> list[Path]:
        """Scan for configuration files."""
        config_patterns = [
            "*.toml",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.ini",
            "*.cfg",
            ".env*",
        ]
        config_files: list[Path] = []
        for pattern in config_patterns:
            config_files.extend(self.repository_root.rglob(pattern))
        return sorted(set(config_files))

    def _scan_documentation_files(self) -> list[Path]:
        """Scan for documentation files."""
        doc_patterns = ["*.md", "*.rst", "*.txt"]
        doc_files: list[Path] = []
        for pattern in doc_patterns:
            doc_files.extend(self.repository_root.rglob(pattern))
        return sorted(set(doc_files))

    def _scan_data_files(self) -> list[Path]:
        """Scan for data files."""
        data_patterns = ["*.csv", "*.pdf", "*.xlsx", "*.parquet"]
        data_files: list[Path] = []
        for pattern in data_patterns:
            data_files.extend(self.repository_root.rglob(pattern))
        return sorted(set(data_files))

    def _extract_dependencies(self) -> dict[str, str]:
        """Extract project dependencies from requirements files."""
        dependencies: dict[str, str] = {}

        req_files = [
            self.repository_root / "requirements.txt",
            self.repository_root / "pyproject.toml",
        ]

        for req_file in req_files:
            if req_file.exists():
                if req_file.name == "requirements.txt":
                    dependencies.update(self._parse_requirements_txt(req_file))
                elif req_file.name == "pyproject.toml":
                    dependencies.update(self._parse_pyproject_toml(req_file))

        return dependencies

    def _parse_requirements_txt(self, path: Path) -> dict[str, str]:
        """Parse requirements.txt file."""
        deps: dict[str, str] = {}
        content = path.read_text(encoding="utf-8")

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#"):
                if ">=" in line:
                    name, version = line.split(">=", 1)
                    deps[name.strip()] = version.split(",")[0].strip()
                elif "==" in line:
                    name, version = line.split("==", 1)
                    deps[name.strip()] = version.strip()

        return deps

    def _parse_pyproject_toml(self, path: Path) -> dict[str, str]:
        """Parse pyproject.toml file for dependencies."""
        deps: dict[str, str] = {}
        content = path.read_text(encoding="utf-8")

        in_dependencies = False
        for raw_line in content.splitlines():
            line = raw_line.strip()

            if line == "dependencies = [":
                in_dependencies = True
                continue

            if in_dependencies:
                if line == "]":
                    break

                if line.startswith('"') or line.startswith("'"):
                    dep_line = line.strip('"').strip("'").strip(",")
                    if ">=" in dep_line:
                        name, version = dep_line.split(">=", 1)
                        deps[name.strip()] = version.split(",")[0].strip()
                    elif "==" in dep_line:
                        name, version = dep_line.split("==", 1)
                        deps[name.strip()] = version.strip()

        return deps

    def _analyze_architecture(self) -> ArchitectureSummary:
        """Analyze repository architecture."""
        src_path = self.repository_root / "src"
        architecture: ArchitectureSummary = {
            "has_src_layout": src_path.exists(),
            "package_structure": [],
            "top_level_modules": [],
        }

        if src_path.exists():
            architecture["package_structure"] = [
                str(p.relative_to(src_path))
                for p in src_path.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ]

        architecture["top_level_modules"] = [
            str(p.relative_to(self.repository_root))
            for p in self.repository_root.iterdir()
            if p.suffix == ".py" and not p.name.startswith(".")
        ]

        return architecture

    def _count_lines_of_code(self, python_files: list[Path]) -> int:
        """Count total lines of Python code."""
        total_lines = 0

        for py_file in python_files:
            if py_file.exists():
                try:
                    content = py_file.read_text(encoding="utf-8")
                    total_lines += len(content.splitlines())
                except (UnicodeDecodeError, PermissionError):
                    continue

        return total_lines

    def generate_inventory_report(
        self, inventory: RepositoryInventory
    ) -> str:
        """
        Generate human-readable inventory report.

        Args:
            inventory: Repository inventory

        Returns:
            Formatted inventory report
        """
        report_lines = [
            "=" * 80,
            "REPOSITORY INVENTORY REPORT",
            "=" * 80,
            "",
            "[OBSERVATION] Repository Scan Completed",
            "",
            f"Total Files: {inventory.total_files}",
            f"Total Lines of Code: {inventory.total_lines_of_code:,}",
            "",
            "FILE CATEGORIES:",
            f"  - Python Files: {len(inventory.python_files)}",
            f"  - Test Files: {len(inventory.test_files)}",
            f"  - Config Files: {len(inventory.config_files)}",
            f"  - Documentation: {len(inventory.documentation_files)}",
            f"  - Data Files: {len(inventory.data_files)}",
            "",
            "ARCHITECTURE:",
        ]

        for key, value in inventory.architecture_summary.items():
            if isinstance(value, list):
                report_lines.append(f"  - {key}: {len(value)} items")
            else:
                report_lines.append(f"  - {key}: {value}")

        report_lines.extend(
            [
                "",
                "KEY DEPENDENCIES:",
            ]
        )

        for dep_name, dep_version in sorted(inventory.dependencies.items())[:20]:
            report_lines.append(f"  - {dep_name}: {dep_version}")

        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)
