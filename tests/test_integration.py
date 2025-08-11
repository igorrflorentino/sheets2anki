#!/usr/bin/env python3
"""
Testes de integração geral para o Sheets2Anki

Testa o fluxo completo de:
- Carregamento de configuração
- Busca de planilhas remotas
- Processamento de dados
- Criação de notes no Anki
- Sincronização com AnkiWeb
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# TESTES DE INTEGRAÇÃO COMPLETA
# =============================================================================


@pytest.mark.integration
class TestFullIntegration:
    """Testes de integração do sistema completo."""

    def test_complete_sync_workflow(
        self, sample_tsv_content, sample_students, mock_mw, tmp_path
    ):
        """Teste do fluxo completo de sincronização."""

        # === SETUP ===
        config_file = tmp_path / "integration_config.json"
        config = {
            "remote_decks": {
                "Test Deck": "https://docs.google.com/spreadsheets/test/pub?output=tsv"
            },
            "global_students": sample_students[:3],  # João, Maria, Pedro
            "ankiweb_sync": {"enabled": False},
        }

        with open(config_file, "w") as f:
            json.dump(config, f)

        # === MOCK FUNCTIONS ===
        def load_config(config_path):
            if not Path(config_path).exists():
                return {}
            with open(config_path) as f:
                return json.load(f)

        def fetch_remote_deck(url):
            """Simula o download de uma planilha remota."""
            return sample_tsv_content

        def parse_tsv_data(content):
            lines = content.strip().split("\n")
            headers = lines[0].split("\t")
            data = []
            for line in lines[1:]:
                values = line.split("\t")
                row = dict(zip(headers, values))
                data.append(row)
            return data

        def filter_by_students(data, global_students):
            filtered = []
            for row in data:
                alunos = row.get("ALUNOS", "")
                if alunos:
                    import re

                    row_students = [s.strip() for s in re.split(r"[,;|]", alunos)]
                    matching = [s for s in row_students if s in global_students]
                    if matching:
                        filtered.append({**row, "_target_students": matching})
            return filtered

        def create_anki_notes(filtered_data, deck_name, mw):
            created_notes = []

            for row in filtered_data:
                for student in row["_target_students"]:
                    # Simular criação de nota
                    note = Mock()
                    note.id = len(created_notes) + 1
                    note.fields = [row["PERGUNTA"], row["LEVAR PARA PROVA"]]
                    # Tags de alunos removidas - agora só tags de tópicos/outros campos
                    note.tags = [f"Sheets2Anki::Topicos::Geografia"]

                    # Mock das operações do Anki
                    mw.col.newNote.return_value = note
                    mw.col.addNote.return_value = note.id

                    created_notes.append(note)

            return created_notes

        # === EXECUÇÃO DO FLUXO COMPLETO ===

        # 1. Carregar configuração
        loaded_config = load_config(config_file)
        assert "remote_decks" in loaded_config

        # 2. Para cada deck configurado
        for deck_name, url in loaded_config["remote_decks"].items():
            # 3. Buscar dados remotos
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = Mock()
                mock_response.read.return_value = sample_tsv_content.encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                raw_content = fetch_remote_deck(url)
                assert "Q001" in raw_content

                # 4. Processar dados TSV
                parsed_data = parse_tsv_data(raw_content)
                assert len(parsed_data) == 2

                # 5. Filtrar por alunos globais
                filtered_data = filter_by_students(
                    parsed_data, loaded_config["global_students"]
                )
                assert len(filtered_data) > 0

                # 6. Criar notas no Anki
                created_notes = create_anki_notes(filtered_data, deck_name, mock_mw)
                assert len(created_notes) > 0

                # 7. Verificar se as notas foram criadas corretamente
                for note in created_notes:
                    assert hasattr(note, "id")
                    assert hasattr(note, "fields")
                    assert hasattr(note, "tags")
                    # Verificar por tags de tópicos ao invés de alunos
                    assert any("Sheets2Anki::Topicos::" in tag for tag in note.tags)

    def test_error_handling_integration(self, mock_mw):
        """Teste de tratamento de erros em integração."""

        def sync_with_error_handling(deck_name, url, global_students, mw):
            errors = []
            success_count = 0

            try:
                # 1. Validar URL
                if not url or "docs.google.com" not in url:
                    raise ValueError(f"URL inválida: {url}")

                # 2. Simular erro de rede
                if "error" in url:
                    raise ConnectionError("Erro de conexão com a planilha")

                # 3. Validar alunos
                if not global_students:
                    raise ValueError("Nenhum aluno configurado")

                # 4. Simular processamento bem-sucedido
                success_count = len(global_students)

            except ValueError as e:
                errors.append(f"Erro de validação: {str(e)}")
            except ConnectionError as e:
                errors.append(f"Erro de conexão: {str(e)}")
            except Exception as e:
                errors.append(f"Erro inesperado: {str(e)}")

            return {
                "success": len(errors) == 0,
                "errors": errors,
                "success_count": success_count if len(errors) == 0 else 0,
            }

        # Caso de sucesso
        result = sync_with_error_handling(
            "Test Deck",
            "https://docs.google.com/spreadsheets/valid/pub?output=tsv",
            ["João", "Maria"],
            mock_mw,
        )
        assert result["success"] == True
        assert result["success_count"] == 2

        # Caso com erro de URL
        result = sync_with_error_handling("Test Deck", "invalid_url", ["João"], mock_mw)
        assert result["success"] == False
        assert len(result["errors"]) > 0
        assert "URL inválida" in result["errors"][0]

        # Caso com erro de conexão
        result = sync_with_error_handling(
            "Test Deck",
            "https://docs.google.com/spreadsheets/error/pub?output=tsv",
            ["João"],
            mock_mw,
        )
        assert result["success"] == False
        assert "Erro de conexão" in result["errors"][0]


# =============================================================================
# TESTES DE PERFORMANCE
# =============================================================================


@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceIntegration:
    """Testes de performance em cenários de integração."""

    def test_large_dataset_processing(self):
        """Teste com dataset grande."""
        import time

        # Gerar dataset grande
        def generate_large_dataset(size):
            headers = [
                "ID",
                "PERGUNTA",
                "LEVAR PARA PROVA",
                "SYNC?",
                "ALUNOS",
                "TOPICO",
            ]
            data = []

            for i in range(size):
                row = {
                    "ID": f"Q{i:04d}",
                    "PERGUNTA": f"Pergunta {i}",
                    "LEVAR PARA PROVA": f"Resposta {i}",
                    "SYNC?": "true",
                    "ALUNOS": f"Aluno{i % 10}",  # 10 alunos diferentes
                    "TOPICO": f"Topico{i % 5}",  # 5 tópicos diferentes
                }
                data.append(row)

            return data

        def process_large_dataset(data, global_students):
            start_time = time.time()

            # Simular processamento
            filtered_data = []
            for row in data:
                if row["ALUNOS"] in global_students:
                    # Simular algum processamento
                    processed_row = {**row}
                    processed_row["_processed"] = True
                    filtered_data.append(processed_row)

            processing_time = time.time() - start_time
            return filtered_data, processing_time

        # Teste com 1000 registros
        large_data = generate_large_dataset(1000)
        global_students = [f"Aluno{i}" for i in range(5)]  # 5 alunos

        result, processing_time = process_large_dataset(large_data, global_students)

        # Verificações
        assert len(result) == 500  # Metade dos registros (5 de 10 alunos)
        assert processing_time < 1.0  # Deve processar em menos de 1 segundo
        assert all(row["_processed"] for row in result)


# =============================================================================
# TESTES DE COMPATIBILIDADE
# =============================================================================


@pytest.mark.integration
class TestCompatibilityIntegration:
    """Testes de compatibilidade com diferentes versões."""

    def test_anki_version_compatibility(self, mock_mw):
        """Teste de compatibilidade com diferentes versões do Anki."""

        def get_anki_version_mock():
            return "2.1.54"  # Versão moderna

        def sync_with_version_check(mw, version_getter=get_anki_version_mock):
            version = version_getter()
            major, minor, patch = map(int, version.split("."))

            compatibility = {
                "modern_api": major > 2 or (major == 2 and minor >= 1 and patch >= 50),
                "supports_cloze": True,
                "supports_hierarchical_decks": True,
            }

            # Usar APIs apropriadas baseado na versão
            if compatibility["modern_api"]:
                # API moderna
                mw.col.decks.id_for_name = Mock(return_value=123)
                result = {"api": "modern", "deck_id": mw.col.decks.id_for_name("test")}
            else:
                # API legada
                mw.col.decks.id = Mock(return_value=456)
                result = {"api": "legacy", "deck_id": mw.col.decks.id("test")}

            return result

        # Teste com versão moderna
        result = sync_with_version_check(mock_mw)
        assert result["api"] == "modern"
        assert result["deck_id"] == 123

        # Teste com versão antiga
        def old_version_getter():
            return "2.1.40"

        result = sync_with_version_check(mock_mw, old_version_getter)
        assert result["api"] == "legacy"
        assert result["deck_id"] == 456


# =============================================================================
# TESTES DE CENÁRIOS REAIS
# =============================================================================


@pytest.mark.integration
class TestRealWorldScenarios:
    """Testes baseados em cenários reais de uso."""

    def test_professor_multi_class_scenario(self, tmp_path):
        """Cenário: Professor com múltiplas turmas."""

        # Configuração do professor
        config = {
            "global_students": [
                "João_Turma_A",
                "Maria_Turma_A",
                "Pedro_Turma_A",
                "Ana_Turma_B",
                "Carlos_Turma_B",
                "Lucia_Turma_B",
            ],
            "remote_decks": {
                "Geografia_Geral": "https://docs.google.com/spreadsheets/geo/pub?output=tsv",
                "Historia_Brasil": "https://docs.google.com/spreadsheets/hist/pub?output=tsv",
            },
        }

        # Dados da planilha simulando conteúdo diferente por turma
        geo_data = [
            {
                "ID": "GEO001",
                "PERGUNTA": "Capital do Brasil?",
                "ALUNOS": "João_Turma_A, Maria_Turma_A",
                "TOPICO": "Capitais",
                "IMPORTANCIA": "Alta",
            },
            {
                "ID": "GEO002",
                "PERGUNTA": "Maior rio do mundo?",
                "ALUNOS": "Ana_Turma_B, Carlos_Turma_B",
                "TOPICO": "Hidrografia",
                "IMPORTANCIA": "Média",
            },
        ]

        def process_multi_class_scenario(config, data_by_deck):
            results = {}

            for deck_name in config["remote_decks"]:
                deck_data = data_by_deck.get(deck_name, [])

                # Filtrar por alunos globais
                filtered_data = []
                for row in deck_data:
                    alunos = row.get("ALUNOS", "")
                    if alunos:
                        import re

                        row_students = [s.strip() for s in re.split(r"[,;|]", alunos)]
                        matching = [
                            s for s in row_students if s in config["global_students"]
                        ]
                        if matching:
                            filtered_data.append({**row, "_target_students": matching})

                # Agrupar por turma
                turma_a_count = 0
                turma_b_count = 0

                for row in filtered_data:
                    for student in row["_target_students"]:
                        if "Turma_A" in student:
                            turma_a_count += 1
                        elif "Turma_B" in student:
                            turma_b_count += 1

                results[deck_name] = {
                    "total_notes": len(filtered_data),
                    "turma_a_notes": turma_a_count,
                    "turma_b_notes": turma_b_count,
                }

            return results

        data_by_deck = {"Geografia_Geral": geo_data}
        results = process_multi_class_scenario(config, data_by_deck)

        assert "Geografia_Geral" in results
        assert results["Geografia_Geral"]["turma_a_notes"] > 0
        assert results["Geografia_Geral"]["turma_b_notes"] > 0

    def test_student_group_collaborative_scenario(self):
        """Cenário: Grupo de estudos colaborativo."""

        # Simulação de grupo de estudos
        group_config = {
            "global_students": ["João", "Maria", "Pedro", "Ana"],
            "study_areas": {
                "João": ["Matemática", "Física"],
                "Maria": ["Química", "Biologia"],
                "Pedro": ["História", "Geografia"],
                "Ana": ["Literatura", "Filosofia"],
            },
        }

        collaborative_data = [
            {"ID": "MAT001", "TOPICO": "Matemática", "ALUNOS": "João, Maria"},
            {"ID": "QUI001", "TOPICO": "Química", "ALUNOS": "Maria, Pedro"},
            {"ID": "HIS001", "TOPICO": "História", "ALUNOS": "Pedro, Ana"},
            {"ID": "LIT001", "TOPICO": "Literatura", "ALUNOS": "Ana, João"},
        ]

        def analyze_collaboration_patterns(config, data):
            collaboration_matrix = {}
            topic_coverage = {}

            for row in data:
                topic = row.get("TOPICO", "Geral")
                alunos = row.get("ALUNOS", "")

                if alunos:
                    students = [s.strip() for s in alunos.split(",")]

                    # Registrar cobertura por tópico
                    if topic not in topic_coverage:
                        topic_coverage[topic] = set()
                    topic_coverage[topic].update(students)

                    # Matriz de colaboração
                    for i, student1 in enumerate(students):
                        for student2 in students[i + 1 :]:
                            pair = tuple(sorted([student1, student2]))
                            if pair not in collaboration_matrix:
                                collaboration_matrix[pair] = 0
                            collaboration_matrix[pair] += 1

            return {
                "collaboration_pairs": collaboration_matrix,
                "topic_coverage": {
                    topic: list(students) for topic, students in topic_coverage.items()
                },
                "most_collaborative_pair": (
                    max(collaboration_matrix.items(), key=lambda x: x[1])
                    if collaboration_matrix
                    else None
                ),
            }

        analysis = analyze_collaboration_patterns(group_config, collaborative_data)

        assert len(analysis["collaboration_pairs"]) > 0
        assert len(analysis["topic_coverage"]) > 0
        assert analysis["most_collaborative_pair"] is not None


if __name__ == "__main__":
    pytest.main([__file__])
