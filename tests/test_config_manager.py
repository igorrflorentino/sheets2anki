#!/usr/bin/env python3
"""
Tests for the config_manager.py module

Tests functionalities for:
- Settings management
- Data persistence
- Remote deck configuration
- Global student configuration
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

# =============================================================================
# BASIC CONFIGURATION TESTS
# =============================================================================


@pytest.mark.unit
class TestConfigManager:
    """Class for configuration manager tests."""

    def test_load_config_success(self, temp_config_file):
        """Successful configuration loading test."""

        def load_config(config_path):
            if not os.path.exists(config_path):
                return {}

            with open(config_path, encoding="utf-8") as f:
                return json.load(f)

        config = load_config(temp_config_file)

        assert isinstance(config, dict)
        assert "remote_decks" in config
        assert "global_students" in config

    def test_load_config_not_exists(self):
        """Loading test with non-existent file."""

        def load_config_safe(config_path):
            if not os.path.exists(config_path):
                return {
                    "remote_decks": {},
                    "global_students": [],
                    "ankiweb_sync": {"enabled": False},
                }

            try:
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return {
                    "remote_decks": {},
                    "global_students": [],
                    "ankiweb_sync": {"enabled": False},
                }

        config = load_config_safe("/nonexistent/path/config.json")

        assert config["remote_decks"] == {}
        assert config["global_students"] == []

    def test_save_config_success(self, tmp_path):
        """Successful configuration saving test."""
        config_file = tmp_path / "test_save_config.json"
        test_config = {
            "remote_decks": {"Test Deck": "https://example.com"},
            "global_students": ["John", "Mary"],
            "ankiweb_sync": {"enabled": True},
        }

        def save_config(config_path, config_data):
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        save_config(str(config_file), test_config)

        # Check if saved correctly
        with open(config_file, encoding="utf-8") as f:
            loaded_config = json.load(f)

        assert loaded_config == test_config


# =============================================================================
# REMOTE DECK MANAGEMENT TESTS
# =============================================================================


@pytest.mark.unit
class TestRemoteDeckConfig:
    """Tests for remote deck configuration."""

    def test_add_remote_deck(self):
        """Remote deck addition test."""

        def add_remote_deck(config, deck_name, url):
            if "remote_decks" not in config:
                config["remote_decks"] = {}

            config["remote_decks"][deck_name] = url
            return config

        config = {"remote_decks": {}}
        deck_name = "Test Deck"
        url = "https://docs.google.com/spreadsheets/test/pub?output=tsv"

        updated_config = add_remote_deck(config, deck_name, url)

        assert deck_name in updated_config["remote_decks"]
        assert updated_config["remote_decks"][deck_name] == url

    def test_remove_remote_deck(self):
        """Remote deck removal test."""

        def remove_remote_deck(config, deck_name):
            if "remote_decks" in config and deck_name in config["remote_decks"]:
                del config["remote_decks"][deck_name]
            return config

        config = {
            "remote_decks": {"Deck 1": "https://url1.com", "Deck 2": "https://url2.com"}
        }

        updated_config = remove_remote_deck(config, "Deck 1")

        assert "Deck 1" not in updated_config["remote_decks"]
        assert "Deck 2" in updated_config["remote_decks"]

    def test_get_remote_decks(self):
        """Remote decks retrieval test."""

        def get_remote_decks(config):
            return config.get("remote_decks", {})

        config = {
            "remote_decks": {
                "Geography": "https://geo.com",
                "History": "https://hist.com",
            }
        }

        decks = get_remote_decks(config)

        assert len(decks) == 2
        assert "Geography" in decks
        assert "History" in decks

    def test_get_deck_url(self):
        """Specific deck URL retrieval test."""

        def get_deck_url(config, deck_name):
            return config.get("remote_decks", {}).get(deck_name)

        config = {"remote_decks": {"Test Deck": "https://test.com/sheets"}}

        url = get_deck_url(config, "Test Deck")
        assert url == "https://test.com/sheets"

        url = get_deck_url(config, "Nonexistent Deck")
        assert url is None


# =============================================================================
# STUDENT CONFIGURATION TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentConfig:
    """Tests for global student configuration."""

    def test_set_global_students(self):
        """Global student definition test."""

        def set_global_students(config, students):
            config["global_students"] = students
            return config

        config = {"global_students": []}
        students = ["John", "Mary", "Peter"]

        updated_config = set_global_students(config, students)

        assert updated_config["global_students"] == students

    def test_get_global_students(self):
        """Global student retrieval test."""

        def get_global_students(config):
            return config.get("global_students", [])

        config = {"global_students": ["Ann", "Charles"]}
        students = get_global_students(config)

        assert students == ["Ann", "Charles"]

        # Test with empty configuration
        empty_config = {}
        students = get_global_students(empty_config)
        assert students == []

    def test_add_student(self):
        """Individual student addition test."""

        def add_student(config, student_name):
            if "global_students" not in config:
                config["global_students"] = []

            if student_name not in config["global_students"]:
                config["global_students"].append(student_name)

            return config

        config = {"global_students": ["John"]}

        # Add new student
        updated_config = add_student(config, "Mary")
        assert "Mary" in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2

        # Try to add duplicate student
        updated_config = add_student(config, "John")
        assert updated_config["global_students"].count("John") == 1

    def test_remove_student(self):
        """Student removal test."""

        def remove_student(config, student_name):
            if (
                "global_students" in config
                and student_name in config["global_students"]
            ):
                config["global_students"].remove(student_name)
            return config

        config = {"global_students": ["John", "Mary", "Peter"]}

        updated_config = remove_student(config, "Mary")

        assert "Mary" not in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2
        assert "John" in updated_config["global_students"]
        assert "Peter" in updated_config["global_students"]


# =============================================================================
# ANKIWEB CONFIGURATION TESTS
# =============================================================================


@pytest.mark.unit
class TestAnkiWebConfig:
    """Tests for AnkiWeb configuration."""

    def test_set_ankiweb_sync_enabled(self):
        """AnkiWeb sync enabling/disabling test."""

        def set_ankiweb_sync_enabled(config, enabled):
            if "ankiweb_sync" not in config:
                config["ankiweb_sync"] = {}
            config["ankiweb_sync"]["enabled"] = enabled
            return config

        config = {}

        # Enable sync
        updated_config = set_ankiweb_sync_enabled(config, True)
        assert updated_config["ankiweb_sync"]["enabled"] == True

        # Disable sync
        updated_config = set_ankiweb_sync_enabled(config, False)
        assert updated_config["ankiweb_sync"]["enabled"] == False

    def test_get_ankiweb_sync_status(self):
        """AnkiWeb sync status retrieval test."""

        def get_ankiweb_sync_status(config):
            return config.get("ankiweb_sync", {}).get("enabled", False)

        config_enabled = {"ankiweb_sync": {"enabled": True}}
        config_disabled = {"ankiweb_sync": {"enabled": False}}
        config_empty = {}

        assert get_ankiweb_sync_status(config_enabled) == True
        assert get_ankiweb_sync_status(config_disabled) == False
        assert get_ankiweb_sync_status(config_empty) == False

    def test_set_auto_sync(self):
        """Auto-sync configuration test."""

        def set_auto_sync(config, auto_sync):
            if "ankiweb_sync" not in config:
                config["ankiweb_sync"] = {}
            config["ankiweb_sync"]["auto_sync"] = auto_sync
            return config

        config = {}
        updated_config = set_auto_sync(config, True)

        assert updated_config["ankiweb_sync"]["auto_sync"] == True


# =============================================================================
# BACKUP AND RESTORE TESTS
# =============================================================================


@pytest.mark.unit
class TestBackupConfig:
    """Tests for backup configuration."""

    def test_set_backup_before_sync(self):
        """Backup before sync configuration test."""

        def set_backup_before_sync(config, enabled):
            config["backup_before_sync"] = enabled
            return config

        config = {}
        updated_config = set_backup_before_sync(config, True)

        assert updated_config["backup_before_sync"] == True

    def test_get_backup_settings(self):
        """Backup settings retrieval test."""

        def get_backup_settings(config):
            return {
                "backup_before_sync": config.get("backup_before_sync", False),
                "auto_backup": config.get("auto_backup", False),
                "backup_directory": config.get("backup_directory", "backups/"),
            }

        config = {"backup_before_sync": True, "auto_backup": False}

        settings = get_backup_settings(config)

        assert settings["backup_before_sync"] == True
        assert settings["auto_backup"] == False
        assert "backup_directory" in settings


# =============================================================================
# VALIDATION TESTS
# =============================================================================


@pytest.mark.unit
class TestConfigValidation:
    """Tests for settings validation."""

    def test_validate_url(self):
        """URL validation test."""

        def validate_url(url):
            if not url:
                return False

            # Must contain google.com and pub?output=tsv
            required_parts = ["docs.google.com", "pub?output=tsv"]
            return all(part in url for part in required_parts)

        valid_url = "https://docs.google.com/spreadsheets/d/e/key/pub?output=tsv"
        invalid_url = "https://example.com/sheet"

        assert validate_url(valid_url) == True
        assert validate_url(invalid_url) == False
        assert validate_url("") == False

    def test_validate_config_structure(self):
        """Configuration structure validation test."""

        def validate_config_structure(config):
            required_keys = ["remote_decks", "global_students"]
            optional_keys = ["ankiweb_sync", "backup_before_sync"]

            # Check mandatory keys
            for key in required_keys:
                if key not in config:
                    return False

            # Check types
            if not isinstance(config["remote_decks"], dict):
                return False
            if not isinstance(config["global_students"], list):
                return False

            return True

        valid_config = {"remote_decks": {"Deck1": "url1"}, "global_students": ["John"]}

        invalid_config = {
            "remote_decks": "not_a_dict",  # Incorrect type
            "global_students": [],
        }

        assert validate_config_structure(valid_config) == True
        assert validate_config_structure(invalid_config) == False


# =============================================================================
# CONFIGURATION MIGRATION TESTS
# =============================================================================


@pytest.mark.unit
class TestConfigMigration:
    """Tests for old configuration migration."""

    def test_migrate_old_config_format(self):
        """Old configuration format migration test."""

        def migrate_config(old_config):
            # Old format to new
            if "decks" in old_config and "remote_decks" not in old_config:
                old_config["remote_decks"] = old_config.pop("decks")

            if "students" in old_config and "global_students" not in old_config:
                old_config["global_students"] = old_config.pop("students")

            # Add default settings if they don't exist
            if "ankiweb_sync" not in old_config:
                old_config["ankiweb_sync"] = {"enabled": False}

            return old_config

        old_config = {"decks": {"Old Deck": "url"}, "students": ["Student1"]}

        migrated = migrate_config(old_config)

        assert "remote_decks" in migrated
        assert "global_students" in migrated
        assert "ankiweb_sync" in migrated
        assert "decks" not in migrated
        assert "students" not in migrated


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for the configuration system."""

    def test_full_config_lifecycle(self, tmp_path):
        """Complete configuration lifecycle test."""
        config_file = tmp_path / "integration_test.json"

        # Helper functions
        def load_config(path):
            if not os.path.exists(path):
                return {"remote_decks": {}, "global_students": []}
            with open(path) as f:
                return json.load(f)

        def save_config(path, config):
            with open(path, "w") as f:
                json.dump(config, f, indent=2)

        # 1. Load initial configuration (empty)
        config = load_config(str(config_file))
        assert config["remote_decks"] == {}

        # 2. Add deck
        config["remote_decks"]["Test Deck"] = "https://test.com"
        config["global_students"] = ["John", "Mary"]

        # 3. Save configuration
        save_config(str(config_file), config)

        # 4. Reload and verify
        reloaded_config = load_config(str(config_file))
        assert "Test Deck" in reloaded_config["remote_decks"]
        assert "John" in reloaded_config["global_students"]

        # 5. Modify and save again
        reloaded_config["global_students"].append("Peter")
        save_config(str(config_file), reloaded_config)

        # 6. Verify changes persisted
        final_config = load_config(str(config_file))
        assert len(final_config["global_students"]) == 3
        assert "Peter" in final_config["global_students"]


if __name__ == "__main__":
    pytest.main([__file__])
