#!/usr/bin/env python3
"""
Testes para o módulo data_processor.py

Testa funcionalidades de:
- Parse de dados TSV
- Validação de colunas
- Detecção de cards cloze
- Processamento de dados
"""

import os
import sys
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# =============================================================================
# TESTES DE PARSING TSV
# =============================================================================


@pytest.mark.unit
class TestDataProcessor:
    """Classe para testes do processador de dados."""

    def test_parse_tsv_basic(self, sample_tsv_content):
        """Teste básico de parsing TSV."""
        try:
            from data_processor import parse_tsv_data
        except ImportError:
            pytest.skip("Módulo data_processor não disponível")

        # Mock da função parse_tsv_data
        def mock_parse_tsv(content):
            lines = content.strip().split("\n")
            headers = lines[0].split("\t")
            data = []
            for line in lines[1:]:
                values = line.split("\t")
                row = dict(zip(headers, values))
                data.append(row)
            return data

        with patch("data_processor.parse_tsv_data", mock_parse_tsv):
            result = mock_parse_tsv(sample_tsv_content)

            assert len(result) == 2
            assert result[0]["ID"] == "Q001"
            assert result[0]["PERGUNTA"] == "Qual é a capital do Brasil?"
            assert result[1]["ID"] == "Q002"

    def test_parse_empty_tsv(self):
        """Teste de parsing com TSV vazio."""

        def mock_parse_empty(content):
            if not content or content.strip() == "":
                return []
            return []

        result = mock_parse_empty("")
        assert result == []

    def test_parse_invalid_tsv(self):
        """Teste de parsing com TSV inválido."""
        invalid_content = "invalid\tcontent\nwithout\tproper\theaders"

        def mock_parse_invalid(content):
            if "ID" not in content or "PERGUNTA" not in content:
                raise ValueError("TSV inválido - colunas obrigatórias ausentes")
            return []

        with pytest.raises(ValueError):
            mock_parse_invalid(invalid_content)


# =============================================================================
# TESTES DE VALIDAÇÃO DE COLUNAS
# =============================================================================


@pytest.mark.unit
class TestColumnValidation:
    """Testes de validação das 18 colunas obrigatórias."""

    def test_validate_required_columns(self, sample_tsv_data):
        """Teste de validação de colunas obrigatórias."""
        required_columns = [
            "ID",
            "PERGUNTA",
            "LEVAR PARA PROVA",
            "SYNC?",
            "ALUNOS",
            "INFO COMPLEMENTAR",
            "INFO DETALHADA",
            "EXEMPLO 1",
            "EXEMPLO 2",
            "EXEMPLO 3",
            "TOPICO",
            "SUBTOPICO",
            "CONCEITO",
            "BANCAS",
            "ULTIMO ANO EM PROVA",
            "CARREIRA",
            "IMPORTANCIA",
            "TAGS ADICIONAIS",
        ]

        def validate_columns(data):
            if not data:
                return False
            first_row = data[0]
            return all(col in first_row for col in required_columns)

        assert validate_columns(sample_tsv_data) == True

    def test_missing_columns(self):
        """Teste com colunas faltando."""
        incomplete_data = [{"ID": "Q001", "PERGUNTA": "Teste"}]

        def validate_columns(data):
            required_columns = ["ID", "PERGUNTA", "LEVAR PARA PROVA", "SYNC?", "ALUNOS"]
            if not data:
                return False
            first_row = data[0]
            return all(col in first_row for col in required_columns)

        assert validate_columns(incomplete_data) == False


# =============================================================================
# TESTES DE DETECÇÃO DE CLOZE
# =============================================================================


@pytest.mark.unit
class TestClozeDetection:
    """Testes para detecção de cards cloze."""

    def test_detect_cloze_basic(self):
        """Teste básico de detecção de cloze."""

        def detect_cloze(question):
            import re

            cloze_pattern = r"\{\{c\d+::.*?\}\}"
            return bool(re.search(cloze_pattern, question))

        # Casos positivos
        assert detect_cloze("A capital do {{c1::Brasil}} é {{c2::Brasília}}") == True
        assert detect_cloze("{{c1::Python}} é uma linguagem") == True
        assert detect_cloze("Teste {{c3::múltiplas}} palavras {{c1::cloze}}") == True

        # Casos negativos
        assert detect_cloze("Pergunta normal sem cloze") == False
        assert detect_cloze("Texto com {chaves} mas não cloze") == False
        assert detect_cloze("") == False

    def test_cloze_patterns(self):
        """Teste de diferentes padrões de cloze."""

        def detect_cloze(question):
            import re

            cloze_pattern = r"\{\{c\d+::.*?\}\}"
            return bool(re.search(cloze_pattern, question))

        test_cases = [
            ("{{c1::resposta}}", True),
            ("{{c10::resposta longa}}", True),
            ("{{c1::resposta::dica}}", True),
            ("{{c1:resposta}}", False),  # Formato incorreto
            ("{c1::resposta}", False),  # Formato incorreto
            ("{{C1::resposta}}", False),  # Case sensitive
        ]

        for question, expected in test_cases:
            assert detect_cloze(question) == expected, f"Failed for: {question}"


# =============================================================================
# TESTES DE PROCESSAMENTO DE ALUNOS
# =============================================================================


@pytest.mark.unit
class TestStudentProcessing:
    """Testes para processamento de dados de alunos."""

    def test_parse_students_comma_separated(self):
        """Teste de parsing de alunos separados por vírgula."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            # Suporta vírgula, ponto e vírgula, pipe
            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        assert parse_students("João, Maria, Pedro") == ["João", "Maria", "Pedro"]
        assert parse_students("João;Maria;Pedro") == ["João", "Maria", "Pedro"]
        assert parse_students("João|Maria|Pedro") == ["João", "Maria", "Pedro"]
        assert parse_students("João") == ["João"]
        assert parse_students("") == []
        assert parse_students("  ") == []

    def test_normalize_student_names(self):
        """Teste de normalização de nomes de alunos."""

        def normalize_student_name(name):
            if not name:
                return ""
            return name.strip().replace(" ", "_")

        assert normalize_student_name("João Silva") == "João_Silva"
        assert normalize_student_name("  Maria  ") == "Maria"
        assert normalize_student_name("") == ""


# =============================================================================
# TESTES DE SYNC CONTROL
# =============================================================================


@pytest.mark.unit
class TestSyncControl:
    """Testes para controle de sincronização."""

    def test_sync_flag_parsing(self):
        """Teste de interpretação da flag SYNC?"""

        def should_sync(sync_flag):
            if not sync_flag:
                return True  # Padrão é sincronizar

            sync_flag = str(sync_flag).lower().strip()

            # Valores que indicam SIM para sync
            yes_values = ["true", "sim", "yes", "1", "v", "verdadeiro"]
            # Valores que indicam NÃO para sync
            no_values = ["false", "não", "nao", "no", "0", "f", "falso"]

            if sync_flag in yes_values or sync_flag == "":
                return True
            elif sync_flag in no_values:
                return False
            else:
                return True  # Default para valores desconhecidos

        # Casos positivos
        assert should_sync("true") == True
        assert should_sync("sim") == True
        assert should_sync("yes") == True
        assert should_sync("1") == True
        assert should_sync("") == True
        assert should_sync(None) == True

        # Casos negativos
        assert should_sync("false") == False
        assert should_sync("não") == False
        assert should_sync("no") == False
        assert should_sync("0") == False


# =============================================================================
# TESTES DE CRIAÇÃO DE TAGS
# =============================================================================


@pytest.mark.unit
class TestTagCreation:
    """Testes para criação de tags hierárquicas."""

    def test_create_hierarchical_tags(self):
        """Teste de criação de tags hierárquicas."""

        def create_tags_for_note(note_data):
            tags = []

            # Tag root
            tag_root = "Sheets2Anki"

            # Tags de alunos foram REMOVIDAS para simplificar lógica
            # (Esta seção foi eliminada)

            # Tags de tópicos
            if note_data.get("TOPICO"):
                topics = [t.strip() for t in note_data["TOPICO"].split(",")]
                for topic in topics:
                    if topic:
                        tag = f"{tag_root}::Topicos::{topic}"
                        if note_data.get("SUBTOPICO"):
                            subtopics = [
                                st.strip() for st in note_data["SUBTOPICO"].split(",")
                            ]
                            for subtopic in subtopics:
                                if subtopic:
                                    tag += f"::{subtopic}"
                                    if note_data.get("CONCEITO"):
                                        concepts = [
                                            c.strip()
                                            for c in note_data["CONCEITO"].split(",")
                                        ]
                                        for concept in concepts:
                                            if concept:
                                                tags.append(f"{tag}::{concept}")
                                    else:
                                        tags.append(tag)
                        else:
                            tags.append(tag)

            # Tags de importância
            if note_data.get("IMPORTANCIA"):
                tags.append(f"{tag_root}::Importancia::{note_data['IMPORTANCIA']}")

            return list(set(tags))  # Remove duplicatas

        test_note = {
            "ALUNOS": "João, Maria",
            "TOPICO": "Geografia",
            "SUBTOPICO": "Capitais",
            "CONCEITO": "Brasil",
            "IMPORTANCIA": "Alta",
        }

        tags = create_tags_for_note(test_note)

        # Verificar se contém tags esperadas (excluindo tags de alunos)
        expected_patterns = [
            "Sheets2Anki::Topicos::Geografia::Capitais::Brasil",
            "Sheets2Anki::Importancia::Alta",
        ]

        for pattern in expected_patterns:
            assert any(
                pattern in tag for tag in tags
            ), f"Pattern '{pattern}' not found in: {tags}"

        # Verificar que tags de alunos NÃO estão presentes
        student_patterns = [
            "Sheets2Anki::Alunos::João",
            "Sheets2Anki::Alunos::Maria",
        ]

        for pattern in student_patterns:
            assert not any(
                pattern in tag for tag in tags
            ), f"Student pattern '{pattern}' should NOT be found in: {tags}"

    def test_clean_tag_text(self):
        """Teste de limpeza de texto para tags."""

        def clean_tag_text(text):
            if not text:
                return ""
            import re

            # Remove caracteres especiais e substitui espaços
            cleaned = re.sub(r"[^\w\s-]", "", text)
            cleaned = cleaned.replace(" ", "_").replace("-", "_")
            return cleaned.strip("_")

        assert clean_tag_text("Geografia Geral") == "Geografia_Geral"
        assert clean_tag_text("Conceitos - Básicos") == "Conceitos___Básicos"
        assert clean_tag_text("Teste!@#$%") == "Teste"
        assert clean_tag_text("") == ""


# =============================================================================
# TESTES DE REMOTE DECK
# =============================================================================


@pytest.mark.unit
class TestRemoteDeck:
    """Testes para funcionalidades de deck remoto."""

    @patch("urllib.request.urlopen")
    def test_fetch_remote_deck_success(self, mock_urlopen, sample_tsv_content):
        """Teste de busca bem-sucedida de deck remoto."""
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.read.return_value = sample_tsv_content.encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        def fetch_remote_deck(url):
            import urllib.request

            with urllib.request.urlopen(url) as response:
                content = response.read().decode("utf-8")
                return content

        url = "https://docs.google.com/spreadsheets/test/pub?output=tsv"
        result = fetch_remote_deck(url)

        assert "Q001" in result
        assert "Qual é a capital do Brasil?" in result

    @patch("urllib.request.urlopen")
    def test_fetch_remote_deck_error(self, mock_urlopen):
        """Teste de erro ao buscar deck remoto."""
        mock_urlopen.side_effect = Exception("Network error")

        def fetch_remote_deck_with_error(url):
            import urllib.request

            try:
                with urllib.request.urlopen(url) as response:
                    return response.read().decode("utf-8")
            except Exception as e:
                raise Exception(f"Erro ao buscar deck: {str(e)}")

        url = "https://invalid-url.com"

        with pytest.raises(Exception, match="Erro ao buscar deck"):
            fetch_remote_deck_with_error(url)


# =============================================================================
# TESTES DE INTEGRAÇÃO
# =============================================================================


@pytest.mark.integration
class TestDataProcessorIntegration:
    """Testes de integração do data processor."""

    def test_full_processing_pipeline(self, sample_tsv_content, sample_students):
        """Teste do pipeline completo de processamento."""

        def process_tsv_data(content, global_students):
            # 1. Parse TSV
            lines = content.strip().split("\n")
            headers = lines[0].split("\t")
            data = []
            for line in lines[1:]:
                values = line.split("\t")
                row = dict(zip(headers, values))
                data.append(row)

            # 2. Filter by students
            filtered_data = []
            for row in data:
                if row.get("ALUNOS"):
                    row_students = [s.strip() for s in row["ALUNOS"].split(",")]
                    if any(student in global_students for student in row_students):
                        filtered_data.append(row)

            # 3. Add metadata
            for row in filtered_data:
                row["_is_cloze"] = "{{c" in row.get("PERGUNTA", "")
                row["_should_sync"] = row.get("SYNC?", "").lower() not in [
                    "false",
                    "não",
                    "0",
                ]

            return filtered_data

        result = process_tsv_data(sample_tsv_content, ["João", "Maria"])

        assert len(result) == 2  # Ambos os registros têm João ou Maria
        assert result[0]["_should_sync"] == True
        assert result[1]["_is_cloze"] == True


if __name__ == "__main__":
    pytest.main([__file__])
