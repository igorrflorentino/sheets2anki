#!/usr/bin/env python3
"""
Configurations and fixtures for Sheets2Anki tests.

This file contains reusable fixtures and common
configurations for all project tests.
"""

import os
import sys
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_tsv_data():
    """Sample TSV data for tests."""
    return [
        {
            "ID": "Q001",
            "PERGUNTA": "What is the capital of Brazil?",
            "LEVAR PARA PROVA": "Brasília",
            "SYNC": "true",
            "ALUNOS": "John, Mary, Peter",
            "INFO COMPLEMENTAR": "Founded in 1960",
            "INFO DETALHADA": "Planned capital of Brazil",
            "IMAGEM HTML": '<img src="https://example.com/brasilia.jpg" width="200">',
            "VÍDEO HTML": "",
            "EXEMPLO 1": "Located in the Federal District",
            "EXEMPLO 2": "Designed by Oscar Niemeyer",
            "EXEMPLO 3": "Inaugurated on April 21, 1960",
            "TOPICO": "Geography",
            "SUBTOPICO": "Capitals",
            "CONCEITO": "Brazil",
            "BANCAS": "CESPE, FCC",
            "ULTIMO ANO EM PROVA": "2024",
            "CARREIRA": "Public Exams",
            "IMPORTANCIA": "High",
            "TAGS ADICIONAIS": "fundamental, basic",
            "EXTRA 1": "",
            "EXTRA 2": "",
            "EXTRA 3": "",
        },
        {
            "ID": "Q002",
            "PERGUNTA": "The capital of {{c1::Brazil}} is {{c2::Brasília}}",
            "LEVAR PARA PROVA": "Cloze card about geography",
            "SYNC": "true",
            "ALUNOS": "Mary, Ann",
            "INFO COMPLEMENTAR": "Cloze card example",
            "INFO DETALHADA": "Automatic detection test",
            "IMAGEM HTML": "",
            "VÍDEO HTML": "",
            "EXEMPLO 1": "",
            "EXEMPLO 2": "",
            "EXEMPLO 3": "",
            "TOPICO": "Geography",
            "SUBTOPICO": "Cloze",
            "CONCEITO": "Cards",
            "BANCAS": "VUNESP",
            "ULTIMO ANO EM PROVA": "2023",
            "CARREIRA": "High School",
            "IMPORTANCIA": "Medium",
            "TAGS ADICIONAIS": "cloze, example",
            "EXTRA 1": "",
            "EXTRA 2": "",
            "EXTRA 3": "",
        },
    ]


@pytest.fixture
def sample_students():
    """Sample student list."""
    return ["John", "Mary", "Peter", "Ann", "Charles"]


@pytest.fixture
def sample_url():
    """Sample URL for tests."""
    return (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key123/pub?output=tsv"
    )


@pytest.fixture
def sample_tsv_content():
    """Sample TSV content in string format."""
    return """ID	PERGUNTA	LEVAR PARA PROVA	SYNC	ALUNOS	INFO COMPLEMENTAR	INFO DETALHADA	IMAGEM HTML	VÍDEO HTML	EXEMPLO 1	EXEMPLO 2	EXEMPLO 3	TOPICO	SUBTOPICO	CONCEITO	BANCAS	ULTIMO ANO EM PROVA	CARREIRA	IMPORTANCIA	TAGS ADICIONAIS	EXTRA 1	EXTRA 2	EXTRA 3
Q001	What is the capital of Brazil?	Brasília	true	John, Mary	Founded in 1960	Planned capital	<img src="https://example.com/brasilia.jpg" width="200">		DF	Oscar Niemeyer	April 21, 1960	Geography	Capitais	Brazil	CESPE	2024	Exams	High	fundamental			
Q002	{{c1::Python}} is a {{c2::programming}} language	Card about programming	true	Mary, Peter	Popular language	Easy to learn		<iframe src="https://youtube.com/embed/test"></iframe>	Simple syntax	Many libraries	Open source	Programming	Languages	Python	FCC	2023	IT	Medium	python			"""


# =============================================================================
# ANKI MOCK FIXTURES
# =============================================================================


@pytest.fixture
def mock_mw():
    """Anki main window object mock."""
    mw = Mock()

    # Collection mock
    mw.col = Mock()
    mw.col.decks = Mock()
    mw.col.models = Mock()
    mw.col.newNote = Mock()
    mw.col.addNote = Mock()
    mw.col.updateNote = Mock()
    mw.col.findNotes = Mock(return_value=[])
    mw.col.getNote = Mock()

    # Decks mock
    mw.col.decks.id = Mock(return_value=1)
    mw.col.decks.get = Mock(return_value={"name": "Test Deck"})
    mw.col.decks.new = Mock(return_value={"name": "New Deck", "id": 1})
    mw.col.decks.save = Mock()

    # Models mock (note types)
    mw.col.models.new = Mock(return_value={"name": "Test Model"})
    mw.col.models.save = Mock()
    mw.col.models.byName = Mock(return_value=None)

    return mw


@pytest.fixture
def mock_note():
    """Anki note mock."""
    note = Mock()
    note.fields = ["Front", "Back"]
    note.tags = []
    note.id = 12345
    note.model = Mock()
    note.model.return_value = {"name": "Basic"}
    return note


@pytest.fixture
def mock_note_type():
    """Anki note type mock."""
    note_type = {
        "name": "Sheets2Anki - TestDeck - John - Basic",
        "id": 1,
        "flds": [
            {"name": "Question", "ord": 0},
            {"name": "Answer", "ord": 1},
            {"name": "Complementary_Info", "ord": 2},
            {"name": "Detailed_Info", "ord": 3},
            {"name": "Example_1", "ord": 4},
            {"name": "Example_2", "ord": 5},
            {"name": "Example_3", "ord": 6},
        ],
        "tmpls": [{"name": "Card 1", "ord": 0}],
    }
    return note_type


# =============================================================================
# CONFIGURATION FIXTURES
# =============================================================================


@pytest.fixture
def sample_config():
    """Sample configuration."""
    return {
        "remote_decks": {
            "Test Deck": "https://docs.google.com/spreadsheets/d/e/sample/pub?output=tsv"
        },
        "global_students": ["John", "Mary", "Peter"],
        "ankiweb_sync": {"enabled": False, "auto_sync": False},
        "backup_before_sync": True,
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Temporary configuration file for tests."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "remote_decks": {},
        "global_students": [],
        "ankiweb_sync": {"enabled": False},
    }

    import json

    config_file.write_text(json.dumps(config_data, indent=2))
    return str(config_file)


# =============================================================================
# ENVIRONMENT FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatic test environment setup."""
    # Mock Anki to avoid import errors
    mock_anki_modules = {
        "aqt": Mock(),
        "aqt.main": Mock(),
        "aqt.utils": Mock(),
        "aqt.qt": Mock(),
        "anki": Mock(),
        "anki.collection": Mock(),
        "anki.decks": Mock(),
        "anki.models": Mock(),
        "anki.notes": Mock(),
    }

    for module_name, mock_module in mock_anki_modules.items():
        monkeypatch.setitem(sys.modules, module_name, mock_module)


@pytest.fixture
def clean_sys_path():
    """Cleans and restores sys.path after each test."""
    original_path = sys.path.copy()
    yield
    sys.path[:] = original_path


# =============================================================================
# TEST HELPERS
# =============================================================================


def create_mock_response(content: str, status_code: int = 200):
    """Creates a mock HTTP response."""
    response = Mock()
    response.content = content.encode("utf-8")
    response.status_code = status_code
    response.text = content
    return response


def assert_tags_contain(tags: List[str], expected_patterns: List[str]):
    """Checks if tags contain expected patterns."""
    for pattern in expected_patterns:
        assert any(
            pattern.lower() in tag.lower() for tag in tags
        ), f"Pattern '{pattern}' not found in tags: {tags}"


# =============================================================================
# CUSTOM MARKERS
# =============================================================================


def pytest_configure(config):
    """Custom pytest configuration."""
    config.addinivalue_line("markers", "unit: marks a test as a unit test")
    config.addinivalue_line(
        "markers", "integration: marks a test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: marks a test as slow (skipped in quick mode)"
    )
    config.addinivalue_line(
        "markers", "requires_anki: marks a test that requires an Anki environment"
    )

    # Configure Anki environment if available
    try:
        # Try to import Anki modules to check if available
        import anki
        import aqt

        print("✅ Anki environment detected and configured for tests")
    except ImportError as e:
        print(f"⚠️  Anki not available for tests: {e}")
        print("   Some tests may use mocks instead of the real environment")
