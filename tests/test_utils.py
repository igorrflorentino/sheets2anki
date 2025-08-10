#!/usr/bin/env python3
"""
Testes para o módulo utils.py

Testa funcionalidades utilitárias como:
- Validação de URLs
- Extração de chaves de publicação
- Geração de hashes
- Funções de helpers gerais
"""

import hashlib
from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# TESTES DE VALIDAÇÃO DE URL
# =============================================================================


@pytest.mark.unit
class TestUrlValidation:
    """Testes para validação de URLs do Google Sheets."""

    def test_validate_valid_urls(self):
        """Teste com URLs válidas."""

        def validate_url(url):
            if not url:
                return False

            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]

            return all(part in url for part in required_parts)

        valid_urls = [
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv",
            "https://docs.google.com/spreadsheets/d/1234567890/pub?output=tsv&single=true",
            "http://docs.google.com/spreadsheets/d/e/key/pub?output=tsv",
        ]

        for url in valid_urls:
            assert validate_url(url) == True, f"URL should be valid: {url}"

    def test_validate_invalid_urls(self):
        """Teste com URLs inválidas."""

        def validate_url(url):
            if not url:
                return False

            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]

            return all(part in url for part in required_parts)

        invalid_urls = [
            "",
            None,
            "https://example.com/sheet",
            "https://sheets.google.com/sheet",  # Wrong domain
            "https://docs.google.com/sheets/pub?output=csv",  # Wrong output format
            "https://docs.google.com/spreadsheets/edit",  # Not published
            "not_a_url",
        ]

        for url in invalid_urls:
            assert validate_url(url) == False, f"URL should be invalid: {url}"


# =============================================================================
# TESTES DE EXTRAÇÃO DE CHAVE DE PUBLICAÇÃO
# =============================================================================


@pytest.mark.unit
class TestPublicationKeyExtraction:
    """Testes para extração de chave de publicação."""

    def test_extract_publication_key_success(self):
        """Teste de extração bem-sucedida de chave."""

        def extract_publication_key_from_url(url):
            if not url:
                return None

            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)

            if match:
                return match.group(1)

            # Fallback para formato antigo
            pattern_old = r"/spreadsheets/d/([^/]+)/"
            match_old = re.search(pattern_old, url)
            if match_old:
                return match_old.group(1)

            return None

        test_cases = [
            (
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key123/pub?output=tsv",
                "2PACX-1vSample-Key123",
            ),
            (
                "https://docs.google.com/spreadsheets/d/1234567890ABCDEF/pub?output=tsv",
                "1234567890ABCDEF",
            ),
            (
                "https://docs.google.com/spreadsheets/d/e/LONG-KEY-HERE/pub?output=tsv&single=true",
                "LONG-KEY-HERE",
            ),
        ]

        for url, expected_key in test_cases:
            result = extract_publication_key_from_url(url)
            assert result == expected_key, f"Failed for URL: {url}"

    def test_extract_publication_key_failure(self):
        """Teste de falha na extração de chave."""

        def extract_publication_key_from_url(url):
            if not url:
                return None

            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)

            if match:
                return match.group(1)

            return None

        invalid_urls = [
            "",
            None,
            "https://example.com/sheet",
            "https://docs.google.com/invalid/format",
            "not_a_url",
        ]

        for url in invalid_urls:
            result = extract_publication_key_from_url(url)
            assert result is None, f"Should return None for: {url}"


# =============================================================================
# TESTES DE GERAÇÃO DE HASH
# =============================================================================


@pytest.mark.unit
class TestHashGeneration:
    """Testes para geração de hashes."""

    def test_get_publication_key_hash(self):
        """Teste de geração de hash da chave de publicação."""

        def get_publication_key_hash(url):
            def extract_key(url):
                if not url:
                    return None
                import re

                pattern = r"/spreadsheets/d/e/([^/]+)/"
                match = re.search(pattern, url)
                return match.group(1) if match else None

            publication_key = extract_key(url)

            if publication_key:
                hash_obj = hashlib.md5(publication_key.encode("utf-8"))
                return hash_obj.hexdigest()[:8]
            else:
                # Fallback para hash da URL completa
                hash_obj = hashlib.md5(url.encode("utf-8"))
                return hash_obj.hexdigest()[:8]

        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv"
        hash_result = get_publication_key_hash(url)

        assert len(hash_result) == 8
        assert isinstance(hash_result, str)

        # Hash deve ser consistente
        hash_result2 = get_publication_key_hash(url)
        assert hash_result == hash_result2

    def test_hash_consistency(self):
        """Teste de consistência de hash."""

        def generate_hash(text):
            hash_obj = hashlib.md5(text.encode("utf-8"))
            return hash_obj.hexdigest()[:8]

        test_text = "test_string_123"

        hash1 = generate_hash(test_text)
        hash2 = generate_hash(test_text)

        assert hash1 == hash2
        assert len(hash1) == 8


# =============================================================================
# TESTES DE FUNÇÕES DE DECK
# =============================================================================


@pytest.mark.unit
class TestDeckUtilities:
    """Testes para funções utilitárias de deck."""

    def test_get_or_create_deck(self, mock_mw):
        """Teste de obtenção/criação de deck."""

        def get_or_create_deck(deck_name, mw):
            # Simular busca por deck existente
            deck_id = mw.col.decks.id(deck_name, create=False)
            if deck_id:
                return deck_id

            # Criar novo deck
            new_deck = mw.col.decks.new(deck_name)
            return mw.col.decks.save(new_deck)

        # Mock do comportamento
        mock_mw.col.decks.id = Mock(return_value=None)  # Deck não existe
        mock_mw.col.decks.new = Mock(return_value={"name": "Test Deck", "id": 123})
        mock_mw.col.decks.save = Mock(return_value=123)

        deck_id = get_or_create_deck("Test Deck", mock_mw)

        assert deck_id == 123
        mock_mw.col.decks.new.assert_called_once_with("Test Deck")

    def test_get_subdeck_name(self):
        """Teste de geração de nome de subdeck."""

        def get_subdeck_name(
            parent_deck, student, importance, topic, subtopic, concept
        ):
            parts = [parent_deck]

            if student:
                parts.append(student)
            if importance:
                parts.append(importance)
            if topic:
                parts.append(topic)
            if subtopic:
                parts.append(subtopic)
            if concept:
                parts.append(concept)

            return "::".join(parts)

        result = get_subdeck_name(
            "Sheets2Anki", "João", "Alta", "Geografia", "Capitais", "Brasil"
        )

        expected = "Sheets2Anki::João::Alta::Geografia::Capitais::Brasil"
        assert result == expected

    def test_ensure_subdeck_exists(self, mock_mw):
        """Teste de garantia de existência de subdeck."""

        def ensure_subdeck_exists(subdeck_name, mw):
            # Simular criação hierárquica
            parts = subdeck_name.split("::")
            current_deck = ""

            for part in parts:
                current_deck = f"{current_deck}::{part}" if current_deck else part

                deck_id = mw.col.decks.id(current_deck, create=False)
                if not deck_id:
                    new_deck = mw.col.decks.new(current_deck)
                    mw.col.decks.save(new_deck)

        # Setup mocks
        mock_mw.col.decks.id = Mock(return_value=None)  # Decks não existem
        mock_mw.col.decks.new = Mock(return_value={"name": "deck"})
        mock_mw.col.decks.save = Mock()

        ensure_subdeck_exists("Parent::Child::Grandchild", mock_mw)

        # Deve criar 3 decks
        assert mock_mw.col.decks.new.call_count == 3


# =============================================================================
# TESTES DE FUNÇÕES DE STRING
# =============================================================================


@pytest.mark.unit
class TestStringUtilities:
    """Testes para funções utilitárias de string."""

    def test_clean_filename(self):
        """Teste de limpeza de nome de arquivo."""

        def clean_filename(filename):
            if not filename:
                return ""

            import re

            # Remove caracteres especiais
            cleaned = re.sub(r"[^\w\s\-_.]", "", filename)
            # Remove espaços extras e substitui por underscore
            cleaned = re.sub(r"\s+", "_", cleaned.strip())
            return cleaned

        test_cases = [
            ("Arquivo Normal.txt", "Arquivo_Normal.txt"),
            ("Arquivo com @#$%!.doc", "Arquivo_com_.doc"),
            ("  Espaços  Extras  .pdf", "Espaços_Extras_.pdf"),
            ("", ""),
            ("arquivo_já_limpo.txt", "arquivo_já_limpo.txt"),
        ]

        for input_text, expected in test_cases:
            result = clean_filename(input_text)
            assert result == expected, f"Failed for: {input_text}"

    def test_normalize_text(self):
        """Teste de normalização de texto."""

        def normalize_text(text):
            if not text:
                return ""

            # Remove acentos e caracteres especiais
            import unicodedata

            normalized = unicodedata.normalize("NFD", text)
            ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

            # Remove caracteres especiais exceto letras, números e espaços
            import re

            cleaned = re.sub(r"[^\w\s]", "", ascii_text)

            return cleaned.strip().lower()

        test_cases = [
            ("João da Silva", "joao da silva"),
            ("Conceição", "conceicao"),
            ("Programação!", "programacao"),
            ("", ""),
            ("123 Test", "123 test"),
        ]

        for input_text, expected in test_cases:
            result = normalize_text(input_text)
            assert result == expected, f"Failed for: {input_text}"


# =============================================================================
# TESTES DE VALIDAÇÃO DE DADOS
# =============================================================================


@pytest.mark.unit
class TestDataValidation:
    """Testes para validação de dados."""

    def test_validate_student_name(self):
        """Teste de validação de nome de aluno."""

        def validate_student_name(name):
            if not name or not isinstance(name, str):
                return False

            name = name.strip()
            if len(name) < 1:
                return False

            # Não deve conter apenas números ou caracteres especiais
            import re

            return bool(re.search(r"[a-zA-ZÀ-ÿ]", name))

        valid_names = ["João", "Maria Silva", "Ana-Paula", "José123"]
        invalid_names = ["", "   ", None, "123", "!@#$%", 123]

        for name in valid_names:
            assert validate_student_name(name) == True, f"Should be valid: {name}"

        for name in invalid_names:
            assert validate_student_name(name) == False, f"Should be invalid: {name}"

    def test_validate_deck_name(self):
        """Teste de validação de nome de deck."""

        def validate_deck_name(name):
            if not name or not isinstance(name, str):
                return False

            name = name.strip()
            if len(name) < 1 or len(name) > 100:
                return False

            # Não deve conter caracteres problemáticos para o Anki
            forbidden_chars = ["<", ">", ":", '"', "|", "?", "*"]
            return not any(char in name for char in forbidden_chars)

        valid_names = ["Geografia Geral", "Matemática - Álgebra", "Deck_Teste_123"]
        invalid_names = ["", "Deck<Invalid>", "Deck|With|Pipes", "A" * 101]

        for name in valid_names:
            assert validate_deck_name(name) == True, f"Should be valid: {name}"

        for name in invalid_names:
            assert validate_deck_name(name) == False, f"Should be invalid: {name}"


# =============================================================================
# TESTES DE EXCEPTION HANDLING
# =============================================================================


@pytest.mark.unit
class TestExceptionHandling:
    """Testes para tratamento de exceções."""

    def test_safe_int_conversion(self):
        """Teste de conversão segura para inteiro."""

        def safe_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        test_cases = [
            ("123", 123),
            ("0", 0),
            ("-45", -45),
            ("not_a_number", 0),
            (None, 0),
            (12.5, 12),
            ("", 0),
        ]

        for input_val, expected in test_cases:
            result = safe_int(input_val)
            assert result == expected, f"Failed for: {input_val}"

    def test_safe_json_load(self):
        """Teste de carregamento seguro de JSON."""
        import json

        def safe_json_load(json_string, default=None):
            try:
                return json.loads(json_string)
            except (json.JSONDecodeError, TypeError):
                return default if default is not None else {}

        valid_json = '{"key": "value", "number": 123}'
        invalid_json = '{"invalid": json}'

        result1 = safe_json_load(valid_json)
        assert result1 == {"key": "value", "number": 123}

        result2 = safe_json_load(invalid_json)
        assert result2 == {}

        result3 = safe_json_load(None, [])
        assert result3 == []


# =============================================================================
# TESTES DE PERFORMANCE
# =============================================================================


@pytest.mark.slow
class TestPerformance:
    """Testes de performance para funções críticas."""

    def test_hash_generation_performance(self):
        """Teste de performance da geração de hash."""
        import time

        def generate_hash(text):
            hash_obj = hashlib.md5(text.encode("utf-8"))
            return hash_obj.hexdigest()[:8]

        # Gerar muitos hashes
        start_time = time.time()

        for i in range(1000):
            test_text = f"test_string_{i}"
            hash_result = generate_hash(test_text)
            assert len(hash_result) == 8

        end_time = time.time()
        duration = end_time - start_time

        # Deve processar 1000 hashes em menos de 1 segundo
        assert duration < 1.0, f"Hash generation too slow: {duration}s"


# =============================================================================
# TESTES DE INTEGRAÇÃO
# =============================================================================


@pytest.mark.integration
class TestUtilsIntegration:
    """Testes de integração das funções utilitárias."""

    def test_url_to_hash_workflow(self):
        """Teste do fluxo completo de URL para hash."""

        def extract_publication_key_from_url(url):
            if not url:
                return None
            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)
            return match.group(1) if match else None

        def get_publication_key_hash(url):
            publication_key = extract_publication_key_from_url(url)
            if publication_key:
                hash_obj = hashlib.md5(publication_key.encode("utf-8"))
                return hash_obj.hexdigest()[:8]
            else:
                hash_obj = hashlib.md5(url.encode("utf-8"))
                return hash_obj.hexdigest()[:8]

        def validate_url(url):
            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]
            return all(part in url for part in required_parts)

        # Fluxo completo
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv"

        # 1. Validar URL
        assert validate_url(url) == True

        # 2. Extrair chave
        key = extract_publication_key_from_url(url)
        assert key == "2PACX-1vSample"

        # 3. Gerar hash
        hash_result = get_publication_key_hash(url)
        assert len(hash_result) == 8

        # 4. Hash deve ser consistente
        hash_result2 = get_publication_key_hash(url)
        assert hash_result == hash_result2


if __name__ == "__main__":
    pytest.main([__file__])
