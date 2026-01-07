#!/usr/bin/env python3
"""
Configurações e fixtures para os testes do Sheets2Anki.

Este arquivo contém fixtures reutilizáveis e configurações
comuns para todos os testes do projeto.
"""

import os
import sys
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

# Adicionar src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# =============================================================================
# FIXTURES DE DADOS DE TESTE
# =============================================================================


@pytest.fixture
def sample_tsv_data():
    """Dados TSV de exemplo para testes."""
    return [
        {
            "ID": "Q001",
            "PERGUNTA": "Qual é a capital do Brasil?",
            "LEVAR PARA PROVA": "Brasília",
            "SYNC?": "true",
            "ALUNOS": "João, Maria, Pedro",
            "INFO COMPLEMENTAR": "Fundada em 1960",
            "INFO DETALHADA": "Capital planejada do Brasil",
            "IMAGEM HTML": '<img src="https://example.com/brasilia.jpg" width="200">',
            "VÍDEO HTML": "",
            "EXEMPLO 1": "Localizada no Distrito Federal",
            "EXEMPLO 2": "Projetada por Oscar Niemeyer",
            "EXEMPLO 3": "Inaugurada em 21 de abril de 1960",
            "TOPICO": "Geografia",
            "SUBTOPICO": "Capitais",
            "CONCEITO": "Brasil",
            "BANCAS": "CESPE, FCC",
            "ULTIMO ANO EM PROVA": "2024",
            "CARREIRA": "Concursos Públicos",
            "IMPORTANCIA": "Alta",
            "TAGS ADICIONAIS": "fundamental, básico",
            "EXTRA 1": "",
            "EXTRA 2": "",
            "EXTRA 3": "",
        },
        {
            "ID": "Q002",
            "PERGUNTA": "A capital do {{c1::Brasil}} é {{c2::Brasília}}",
            "LEVAR PARA PROVA": "Card cloze sobre geografia",
            "SYNC?": "true",
            "ALUNOS": "Maria, Ana",
            "INFO COMPLEMENTAR": "Exemplo de card cloze",
            "INFO DETALHADA": "Teste de detecção automática",
            "IMAGEM HTML": "",
            "VÍDEO HTML": "",
            "EXEMPLO 1": "",
            "EXEMPLO 2": "",
            "EXEMPLO 3": "",
            "TOPICO": "Geografia",
            "SUBTOPICO": "Cloze",
            "CONCEITO": "Cards",
            "BANCAS": "VUNESP",
            "ULTIMO ANO EM PROVA": "2023",
            "CARREIRA": "Ensino Médio",
            "IMPORTANCIA": "Média",
            "TAGS ADICIONAIS": "cloze, exemplo",
            "EXTRA 1": "",
            "EXTRA 2": "",
            "EXTRA 3": "",
        },
    ]


@pytest.fixture
def sample_students():
    """Lista de alunos de exemplo."""
    return ["João", "Maria", "Pedro", "Ana", "Carlos"]


@pytest.fixture
def sample_url():
    """URL de exemplo para testes."""
    return (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key123/pub?output=tsv"
    )


@pytest.fixture
def sample_tsv_content():
    """Conteúdo TSV de exemplo em formato string."""
    return """ID	PERGUNTA	LEVAR PARA PROVA	SYNC?	ALUNOS	INFO COMPLEMENTAR	INFO DETALHADA	IMAGEM HTML	VÍDEO HTML	EXEMPLO 1	EXEMPLO 2	EXEMPLO 3	TOPICO	SUBTOPICO	CONCEITO	BANCAS	ULTIMO ANO EM PROVA	CARREIRA	IMPORTANCIA	TAGS ADICIONAIS	EXTRA 1	EXTRA 2	EXTRA 3
Q001	Qual é a capital do Brasil?	Brasília	true	João, Maria	Fundada em 1960	Capital planejada	<img src="https://example.com/brasilia.jpg" width="200">		DF	Oscar Niemeyer	21 abril 1960	Geografia	Capitais	Brasil	CESPE	2024	Concursos	Alta	fundamental			
Q002	{{c1::Python}} é uma linguagem de {{c2::programação}}	Card sobre programação	true	Maria, Pedro	Linguagem popular	Fácil de aprender		<iframe src="https://youtube.com/embed/test"></iframe>	Sintaxe simples	Muitas bibliotecas	Open source	Programação	Linguagens	Python	FCC	2023	TI	Média	python			"""


# =============================================================================
# FIXTURES DE MOCK PARA ANKI
# =============================================================================


@pytest.fixture
def mock_mw():
    """Mock do objeto main window do Anki."""
    mw = Mock()

    # Mock da collection
    mw.col = Mock()
    mw.col.decks = Mock()
    mw.col.models = Mock()
    mw.col.newNote = Mock()
    mw.col.addNote = Mock()
    mw.col.updateNote = Mock()
    mw.col.findNotes = Mock(return_value=[])
    mw.col.getNote = Mock()

    # Mock de decks
    mw.col.decks.id = Mock(return_value=1)
    mw.col.decks.get = Mock(return_value={"name": "Test Deck"})
    mw.col.decks.new = Mock(return_value={"name": "New Deck", "id": 1})
    mw.col.decks.save = Mock()

    # Mock de models (note types)
    mw.col.models.new = Mock(return_value={"name": "Test Model"})
    mw.col.models.save = Mock()
    mw.col.models.byName = Mock(return_value=None)

    return mw


@pytest.fixture
def mock_note():
    """Mock de uma nota do Anki."""
    note = Mock()
    note.fields = ["Front", "Back"]
    note.tags = []
    note.id = 12345
    note.model = Mock()
    note.model.return_value = {"name": "Basic"}
    return note


@pytest.fixture
def mock_note_type():
    """Mock de um note type do Anki."""
    note_type = {
        "name": "Sheets2Anki - TestDeck - João - Basic",
        "id": 1,
        "flds": [
            {"name": "Pergunta", "ord": 0},
            {"name": "Resposta", "ord": 1},
            {"name": "Info_Complementar", "ord": 2},
            {"name": "Info_Detalhada", "ord": 3},
            {"name": "Exemplo_1", "ord": 4},
            {"name": "Exemplo_2", "ord": 5},
            {"name": "Exemplo_3", "ord": 6},
        ],
        "tmpls": [{"name": "Card 1", "ord": 0}],
    }
    return note_type


# =============================================================================
# FIXTURES DE CONFIGURAÇÃO
# =============================================================================


@pytest.fixture
def sample_config():
    """Configuração de exemplo."""
    return {
        "remote_decks": {
            "Test Deck": "https://docs.google.com/spreadsheets/d/e/sample/pub?output=tsv"
        },
        "global_students": ["João", "Maria", "Pedro"],
        "ankiweb_sync": {"enabled": False, "auto_sync": False},
        "backup_before_sync": True,
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Arquivo de configuração temporário para testes."""
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
# FIXTURES DE AMBIENTE
# =============================================================================


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Configuração automática do ambiente de teste."""
    # Mock do Anki para evitar import errors
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
    """Limpa e restaura sys.path após cada teste."""
    original_path = sys.path.copy()
    yield
    sys.path[:] = original_path


# =============================================================================
# HELPERS PARA TESTES
# =============================================================================


def create_mock_response(content: str, status_code: int = 200):
    """Cria uma resposta HTTP mock."""
    response = Mock()
    response.content = content.encode("utf-8")
    response.status_code = status_code
    response.text = content
    return response


def assert_tags_contain(tags: List[str], expected_patterns: List[str]):
    """Verifica se as tags contêm os padrões esperados."""
    for pattern in expected_patterns:
        assert any(
            pattern.lower() in tag.lower() for tag in tags
        ), f"Pattern '{pattern}' not found in tags: {tags}"


# =============================================================================
# MARKERS PERSONALIZADOS
# =============================================================================


def pytest_configure(config):
    """Configuração personalizada do pytest."""
    config.addinivalue_line("markers", "unit: marca teste como teste unitário")
    config.addinivalue_line(
        "markers", "integration: marca teste como teste de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca teste como lento (pulado em modo rápido)"
    )
    config.addinivalue_line(
        "markers", "requires_anki: marca teste que requer ambiente Anki"
    )

    # Configurar ambiente do Anki se disponível
    try:
        # Tentar importar módulos do Anki para verificar se estão disponíveis
        import anki
        import aqt

        print("✅ Ambiente Anki detectado e configurado para testes")
    except ImportError as e:
        print(f"⚠️  Anki não disponível para testes: {e}")
        print("   Alguns testes podem usar mocks ao invés do ambiente real")
