"""Test suite for configuration governance system.

Tests:
- Directory structure creation
- ConfigManager functionality
- Hash registry operations
- Backup creation and restoration
- Pre-commit hook detection

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

import json
from pathlib import Path

import pytest
from config_manager import ConfigManager


class TestConfigGovernance:
    """Test configuration governance system."""

    @pytest.fixture
    def temp_config_root(self, tmp_path):
        """Create temporary config root with structure."""
        config_root = tmp_path / "config"
        config_root.mkdir()

        (config_root / "calibration").mkdir()
        (config_root / "questionnaire").mkdir()
        (config_root / "environments").mkdir()
        (config_root / ".backup").mkdir()

        return config_root

    @pytest.fixture
    def config_manager(self, temp_config_root):
        """Create ConfigManager instance."""
        return ConfigManager(temp_config_root)

    def test_directory_structure(self, temp_config_root):
        """Test required directories exist."""
        assert (temp_config_root / "calibration").exists()
        assert (temp_config_root / "questionnaire").exists()
        assert (temp_config_root / "environments").exists()
        assert (temp_config_root / ".backup").exists()

    def test_save_config_json(self, config_manager):
        """Test JSON config saving."""
        test_data = {"version": "1.0.0", "values": {"key1": 0.65, "key2": 0.75}}

        saved_path = config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        assert saved_path.exists()
        loaded = json.loads(saved_path.read_text())
        assert loaded == test_data

    def test_load_config_json(self, config_manager):
        """Test JSON config loading."""
        test_data = {"test": "value"}
        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        loaded = config_manager.load_config_json("calibration/test.json")
        assert loaded == test_data

    def test_hash_computation(self, config_manager):
        """Test SHA256 hash computation."""
        test_data = {"version": "1.0.0"}
        file_path = config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        hash1 = config_manager._compute_sha256(file_path)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)

        hash2 = config_manager._compute_sha256(file_path)
        assert hash1 == hash2

    def test_registry_operations(self, config_manager):
        """Test hash registry operations."""
        test_data = {"version": "1.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        registry = config_manager.get_registry()
        assert "calibration/test.json" in registry

        entry = registry["calibration/test.json"]
        assert "hash" in entry
        assert "last_modified" in entry
        assert "size_bytes" in entry

    def test_verify_hash(self, config_manager):
        """Test hash verification."""
        test_data = {"version": "1.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        assert config_manager.verify_hash("calibration/test.json")

        file_path = config_manager.config_root / "calibration/test.json"
        file_path.write_text('{"modified": true}')

        assert not config_manager.verify_hash("calibration/test.json")

    def test_backup_creation(self, config_manager):
        """Test automatic backup creation."""
        test_data = {"version": "1.0.0"}

        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        backups_before = config_manager.list_backups("calibration/test.json")

        config_manager.save_config_json(
            "calibration/test.json", {"version": "2.0.0"}, create_backup=True
        )

        backups_after = config_manager.list_backups("calibration/test.json")
        assert len(backups_after) == len(backups_before) + 1

    def test_backup_filename_format(self, config_manager):
        """Test backup filename format."""
        test_data = {"version": "1.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        config_manager.save_config_json(
            "calibration/test.json", {"version": "2.0.0"}, create_backup=True
        )

        backups = config_manager.list_backups("calibration/test.json")
        assert len(backups) > 0

        backup_name = backups[0].name
        parts = backup_name.split("_")

        assert len(parts) >= 4

        date_part = parts[0]
        assert len(date_part) == 8
        assert date_part.isdigit()

        time_part = parts[1]
        assert len(time_part) == 6
        assert time_part.isdigit()

    def test_restore_backup(self, config_manager):
        """Test backup restoration."""
        original_data = {"version": "1.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", original_data, create_backup=False
        )

        modified_data = {"version": "2.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", modified_data, create_backup=True
        )

        backups = config_manager.list_backups("calibration/test.json")
        assert len(backups) > 0

        restored_path = config_manager.restore_backup(backups[0], create_backup=False)

        restored_content = config_manager.load_config_json("calibration/test.json")
        assert restored_content == original_data

    def test_rebuild_registry(self, config_manager):
        """Test registry rebuild."""
        config_manager.save_config_json("calibration/test1.json", {"v": 1}, False)
        config_manager.save_config_json("calibration/test2.json", {"v": 2}, False)
        config_manager.save_config_json("questionnaire/test3.json", {"v": 3}, False)

        registry = config_manager.rebuild_registry()

        assert "calibration/test1.json" in registry
        assert "calibration/test2.json" in registry
        assert "questionnaire/test3.json" in registry

    def test_get_file_info(self, config_manager):
        """Test file info retrieval."""
        test_data = {"version": "1.0.0"}
        config_manager.save_config_json(
            "calibration/test.json", test_data, create_backup=False
        )

        info = config_manager.get_file_info("calibration/test.json")

        assert info is not None
        assert "hash" in info
        assert "last_modified" in info
        assert "size_bytes" in info
        assert info["size_bytes"] > 0

    def test_list_backups_filtering(self, config_manager):
        """Test backup listing with filtering."""
        config_manager.save_config_json("calibration/test1.json", {"v": 1}, False)
        config_manager.save_config_json("calibration/test2.json", {"v": 2}, False)

        config_manager.save_config_json("calibration/test1.json", {"v": 1.1}, True)
        config_manager.save_config_json("calibration/test2.json", {"v": 2.1}, True)

        all_backups = config_manager.list_backups()
        test1_backups = config_manager.list_backups("calibration/test1.json")
        test2_backups = config_manager.list_backups("calibration/test2.json")

        assert len(test1_backups) >= 1
        assert len(test2_backups) >= 1
        assert len(all_backups) >= len(test1_backups) + len(test2_backups)


class TestPreCommitHook:
    """Test pre-commit hook functionality."""

    def test_hook_exists(self):
        """Test pre-commit hook file exists."""
        hook_path = Path(".git/hooks/pre-commit")
        assert hook_path.exists()
        assert hook_path.is_file()

    def test_hook_executable(self):
        """Test pre-commit hook is executable."""
        hook_path = Path(".git/hooks/pre-commit")
        import stat

        mode = hook_path.stat().st_mode
        assert mode & stat.S_IXUSR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
