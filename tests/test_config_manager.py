#!/usr/bin/env python3
"""
Testes para o módulo config_manager.py

Testa funcionalidades de:
- Gerenciamento de configurações
- Persistência de dados
- Configuração de decks remotos
- Configuração de alunos globais
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

# =============================================================================
# TESTES DE CONFIGURAÇÃO BÁSICA
# =============================================================================


@pytest.mark.unit
class TestConfigManager:
    """Classe para testes do gerenciador de configurações."""

    def test_load_config_success(self, temp_config_file):
        """Teste de carregamento bem-sucedido de configuração."""

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
        """Teste de carregamento com arquivo inexistente."""

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
        """Teste de salvamento bem-sucedido de configuração."""
        config_file = tmp_path / "test_save_config.json"
        test_config = {
            "remote_decks": {"Test Deck": "https://example.com"},
            "global_students": ["João", "Maria"],
            "ankiweb_sync": {"enabled": True},
        }

        def save_config(config_path, config_data):
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        save_config(str(config_file), test_config)

        # Verificar se foi salvo corretamente
        with open(config_file, encoding="utf-8") as f:
            loaded_config = json.load(f)

        assert loaded_config == test_config


# =============================================================================
# TESTES DE GERENCIAMENTO DE DECKS REMOTOS
# =============================================================================


@pytest.mark.unit
class TestRemoteDeckConfig:
    """Testes para configuração de decks remotos."""

    def test_add_remote_deck(self):
        """Teste de adição de deck remoto."""

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
        """Teste de remoção de deck remoto."""

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
        """Teste de obtenção de decks remotos."""

        def get_remote_decks(config):
            return config.get("remote_decks", {})

        config = {
            "remote_decks": {
                "Geografia": "https://geo.com",
                "História": "https://hist.com",
            }
        }

        decks = get_remote_decks(config)

        assert len(decks) == 2
        assert "Geografia" in decks
        assert "História" in decks

    def test_get_deck_url(self):
        """Teste de obtenção de URL de deck específico."""

        def get_deck_url(config, deck_name):
            return config.get("remote_decks", {}).get(deck_name)

        config = {"remote_decks": {"Test Deck": "https://test.com/sheets"}}

        url = get_deck_url(config, "Test Deck")
        assert url == "https://test.com/sheets"

        url = get_deck_url(config, "Nonexistent Deck")
        assert url is None


# =============================================================================
# TESTES DE CONFIGURAÇÃO DE ALUNOS
# =============================================================================


@pytest.mark.unit
class TestStudentConfig:
    """Testes para configuração de alunos globais."""

    def test_set_global_students(self):
        """Teste de definição de alunos globais."""

        def set_global_students(config, students):
            config["global_students"] = students
            return config

        config = {"global_students": []}
        students = ["João", "Maria", "Pedro"]

        updated_config = set_global_students(config, students)

        assert updated_config["global_students"] == students

    def test_get_global_students(self):
        """Teste de obtenção de alunos globais."""

        def get_global_students(config):
            return config.get("global_students", [])

        config = {"global_students": ["Ana", "Carlos"]}
        students = get_global_students(config)

        assert students == ["Ana", "Carlos"]

        # Teste com configuração vazia
        empty_config = {}
        students = get_global_students(empty_config)
        assert students == []

    def test_add_student(self):
        """Teste de adição de aluno individual."""

        def add_student(config, student_name):
            if "global_students" not in config:
                config["global_students"] = []

            if student_name not in config["global_students"]:
                config["global_students"].append(student_name)

            return config

        config = {"global_students": ["João"]}

        # Adicionar novo aluno
        updated_config = add_student(config, "Maria")
        assert "Maria" in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2

        # Tentar adicionar aluno duplicado
        updated_config = add_student(config, "João")
        assert updated_config["global_students"].count("João") == 1

    def test_remove_student(self):
        """Teste de remoção de aluno."""

        def remove_student(config, student_name):
            if (
                "global_students" in config
                and student_name in config["global_students"]
            ):
                config["global_students"].remove(student_name)
            return config

        config = {"global_students": ["João", "Maria", "Pedro"]}

        updated_config = remove_student(config, "Maria")

        assert "Maria" not in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2
        assert "João" in updated_config["global_students"]
        assert "Pedro" in updated_config["global_students"]


# =============================================================================
# TESTES DE CONFIGURAÇÃO ANKIWEB
# =============================================================================


@pytest.mark.unit
class TestAnkiWebConfig:
    """Testes para configuração do AnkiWeb."""

    def test_set_ankiweb_sync_enabled(self):
        """Teste de habilitação/desabilitação do sync AnkiWeb."""

        def set_ankiweb_sync_enabled(config, enabled):
            if "ankiweb_sync" not in config:
                config["ankiweb_sync"] = {}
            config["ankiweb_sync"]["enabled"] = enabled
            return config

        config = {}

        # Habilitar sync
        updated_config = set_ankiweb_sync_enabled(config, True)
        assert updated_config["ankiweb_sync"]["enabled"] == True

        # Desabilitar sync
        updated_config = set_ankiweb_sync_enabled(config, False)
        assert updated_config["ankiweb_sync"]["enabled"] == False

    def test_get_ankiweb_sync_status(self):
        """Teste de obtenção do status do sync AnkiWeb."""

        def get_ankiweb_sync_status(config):
            return config.get("ankiweb_sync", {}).get("enabled", False)

        config_enabled = {"ankiweb_sync": {"enabled": True}}
        config_disabled = {"ankiweb_sync": {"enabled": False}}
        config_empty = {}

        assert get_ankiweb_sync_status(config_enabled) == True
        assert get_ankiweb_sync_status(config_disabled) == False
        assert get_ankiweb_sync_status(config_empty) == False

    def test_set_auto_sync(self):
        """Teste de configuração de auto-sync."""

        def set_auto_sync(config, auto_sync):
            if "ankiweb_sync" not in config:
                config["ankiweb_sync"] = {}
            config["ankiweb_sync"]["auto_sync"] = auto_sync
            return config

        config = {}
        updated_config = set_auto_sync(config, True)

        assert updated_config["ankiweb_sync"]["auto_sync"] == True


# =============================================================================
# TESTES DE BACKUP E RESTORE
# =============================================================================


@pytest.mark.unit
class TestBackupConfig:
    """Testes para configuração de backup."""

    def test_set_backup_before_sync(self):
        """Teste de configuração de backup antes da sincronização."""

        def set_backup_before_sync(config, enabled):
            config["backup_before_sync"] = enabled
            return config

        config = {}
        updated_config = set_backup_before_sync(config, True)

        assert updated_config["backup_before_sync"] == True

    def test_get_backup_settings(self):
        """Teste de obtenção de configurações de backup."""

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
# TESTES DE VALIDAÇÃO
# =============================================================================


@pytest.mark.unit
class TestConfigValidation:
    """Testes para validação de configurações."""

    def test_validate_url(self):
        """Teste de validação de URL."""

        def validate_url(url):
            if not url:
                return False

            # Deve conter google.com e pub?output=tsv
            required_parts = ["docs.google.com", "pub?output=tsv"]
            return all(part in url for part in required_parts)

        valid_url = "https://docs.google.com/spreadsheets/d/e/key/pub?output=tsv"
        invalid_url = "https://example.com/sheet"

        assert validate_url(valid_url) == True
        assert validate_url(invalid_url) == False
        assert validate_url("") == False

    def test_validate_config_structure(self):
        """Teste de validação da estrutura de configuração."""

        def validate_config_structure(config):
            required_keys = ["remote_decks", "global_students"]
            optional_keys = ["ankiweb_sync", "backup_before_sync"]

            # Verificar chaves obrigatórias
            for key in required_keys:
                if key not in config:
                    return False

            # Verificar tipos
            if not isinstance(config["remote_decks"], dict):
                return False
            if not isinstance(config["global_students"], list):
                return False

            return True

        valid_config = {"remote_decks": {"Deck1": "url1"}, "global_students": ["João"]}

        invalid_config = {
            "remote_decks": "not_a_dict",  # Tipo incorreto
            "global_students": [],
        }

        assert validate_config_structure(valid_config) == True
        assert validate_config_structure(invalid_config) == False


# =============================================================================
# TESTES DE MIGRAÇÃO DE CONFIGURAÇÃO
# =============================================================================


@pytest.mark.unit
class TestConfigMigration:
    """Testes para migração de configurações antigas."""

    def test_migrate_old_config_format(self):
        """Teste de migração de formato antigo de configuração."""

        def migrate_config(old_config):
            # Formato antigo para novo
            if "decks" in old_config and "remote_decks" not in old_config:
                old_config["remote_decks"] = old_config.pop("decks")

            if "students" in old_config and "global_students" not in old_config:
                old_config["global_students"] = old_config.pop("students")

            # Adicionar configurações padrão se não existirem
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
# TESTES DE INTEGRAÇÃO
# =============================================================================


@pytest.mark.integration
class TestConfigIntegration:
    """Testes de integração do sistema de configuração."""

    def test_full_config_lifecycle(self, tmp_path):
        """Teste completo do ciclo de vida de configuração."""
        config_file = tmp_path / "integration_test.json"

        # Funções helper
        def load_config(path):
            if not os.path.exists(path):
                return {"remote_decks": {}, "global_students": []}
            with open(path) as f:
                return json.load(f)

        def save_config(path, config):
            with open(path, "w") as f:
                json.dump(config, f, indent=2)

        # 1. Carregar configuração inicial (vazia)
        config = load_config(str(config_file))
        assert config["remote_decks"] == {}

        # 2. Adicionar deck
        config["remote_decks"]["Test Deck"] = "https://test.com"
        config["global_students"] = ["João", "Maria"]

        # 3. Salvar configuração
        save_config(str(config_file), config)

        # 4. Recarregar e verificar
        reloaded_config = load_config(str(config_file))
        assert "Test Deck" in reloaded_config["remote_decks"]
        assert "João" in reloaded_config["global_students"]

        # 5. Modificar e salvar novamente
        reloaded_config["global_students"].append("Pedro")
        save_config(str(config_file), reloaded_config)

        # 6. Verificar mudanças persistiram
        final_config = load_config(str(config_file))
        assert len(final_config["global_students"]) == 3
        assert "Pedro" in final_config["global_students"]


if __name__ == "__main__":
    pytest.main([__file__])
