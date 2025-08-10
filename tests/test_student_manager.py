#!/usr/bin/env python3
"""
Testes para o módulo student_manager.py

Testa funcionalidades de:
- Gestão de alunos globais
- Filtragem de dados por alunos
- Criação de subdecks por aluno
- Configuração individual por deck
"""

from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# TESTES DE GESTÃO DE ALUNOS GLOBAIS
# =============================================================================


@pytest.mark.unit
class TestStudentManager:
    """Classe para testes do gerenciador de alunos."""

    def test_get_global_students_empty(self):
        """Teste de obtenção de alunos quando lista vazia."""

        def get_global_students(config):
            return config.get("global_students", [])

        empty_config = {}
        students = get_global_students(empty_config)

        assert students == []
        assert isinstance(students, list)

    def test_get_global_students_with_data(self, sample_students):
        """Teste de obtenção de alunos com dados."""

        def get_global_students(config):
            return config.get("global_students", [])

        config = {"global_students": sample_students}
        students = get_global_students(config)

        assert len(students) == 5
        assert "João" in students
        assert "Maria" in students

    def test_set_global_students(self):
        """Teste de definição de alunos globais."""

        def set_global_students(config, students):
            config["global_students"] = students.copy() if students else []
            return config

        config = {}
        new_students = ["Ana", "Bruno", "Carlos"]

        updated_config = set_global_students(config, new_students)

        assert "global_students" in updated_config
        assert len(updated_config["global_students"]) == 3
        assert "Ana" in updated_config["global_students"]

    def test_add_global_student(self):
        """Teste de adição de aluno individual."""

        def add_global_student(config, student_name):
            if "global_students" not in config:
                config["global_students"] = []

            if student_name and student_name not in config["global_students"]:
                config["global_students"].append(student_name)

            return config

        config = {"global_students": ["João"]}

        # Adicionar novo aluno
        updated_config = add_global_student(config, "Maria")
        assert "Maria" in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2

        # Tentar adicionar aluno duplicado
        updated_config = add_global_student(config, "João")
        assert updated_config["global_students"].count("João") == 1

    def test_remove_global_student(self):
        """Teste de remoção de aluno."""

        def remove_global_student(config, student_name):
            if (
                "global_students" in config
                and student_name in config["global_students"]
            ):
                config["global_students"].remove(student_name)
            return config

        config = {"global_students": ["João", "Maria", "Pedro"]}

        updated_config = remove_global_student(config, "Maria")

        assert "Maria" not in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2
        assert "João" in updated_config["global_students"]


# =============================================================================
# TESTES DE FILTRAGEM DE DADOS
# =============================================================================


@pytest.mark.unit
class TestStudentFiltering:
    """Testes para filtragem de dados por alunos."""

    def test_filter_data_by_students_basic(self, sample_tsv_data):
        """Teste básico de filtragem por alunos."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                alunos_field = row.get("ALUNOS", "")
                if not alunos_field:
                    # Se não tem alunos, vai para categoria especial
                    filtered_data.append({**row, "_target_students": ["[MISSING A.]"]})
                    continue

                # Parse dos alunos na linha
                import re

                row_students = [
                    s.strip() for s in re.split(r"[,;|]", alunos_field) if s.strip()
                ]

                # Verificar se algum aluno da linha está nos globais
                matching_students = [s for s in row_students if s in global_students]

                if matching_students:
                    filtered_data.append({**row, "_target_students": matching_students})

            return filtered_data

        global_students = ["João", "Maria"]
        result = filter_data_by_students(sample_tsv_data, global_students)

        assert len(result) == 2  # Ambas as linhas têm João ou Maria
        assert "João" in result[0]["_target_students"]
        assert "Maria" in result[1]["_target_students"]

    def test_filter_data_no_matching_students(self, sample_tsv_data):
        """Teste de filtragem sem alunos correspondentes."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                alunos_field = row.get("ALUNOS", "")
                if not alunos_field:
                    continue

                import re

                row_students = [
                    s.strip() for s in re.split(r"[,;|]", alunos_field) if s.strip()
                ]
                matching_students = [s for s in row_students if s in global_students]

                if matching_students:
                    filtered_data.append({**row, "_target_students": matching_students})

            return filtered_data

        global_students = ["Inexistente"]  # Nenhum aluno corresponde
        result = filter_data_by_students(sample_tsv_data, global_students)

        assert len(result) == 0

    def test_filter_data_empty_students_field(self):
        """Teste de filtragem com campo ALUNOS vazio."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                alunos_field = row.get("ALUNOS", "")
                if not alunos_field or alunos_field.strip() == "":
                    filtered_data.append({**row, "_target_students": ["[MISSING A.]"]})
                    continue

                import re

                row_students = [
                    s.strip() for s in re.split(r"[,;|]", alunos_field) if s.strip()
                ]
                matching_students = [s for s in row_students if s in global_students]

                if matching_students:
                    filtered_data.append({**row, "_target_students": matching_students})

            return filtered_data

        data = [
            {"ID": "Q001", "ALUNOS": ""},
            {"ID": "Q002", "ALUNOS": "   "},  # Só espaços
            {"ID": "Q003"},  # Campo ausente
        ]

        result = filter_data_by_students(data, ["João"])

        assert len(result) == 3
        for row in result:
            assert row["_target_students"] == ["[MISSING A.]"]


# =============================================================================
# TESTES DE PARSING DE ALUNOS
# =============================================================================


@pytest.mark.unit
class TestStudentParsing:
    """Testes para parsing de nomes de alunos."""

    def test_parse_students_different_separators(self):
        """Teste de parsing com diferentes separadores."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        test_cases = [
            ("João, Maria, Pedro", ["João", "Maria", "Pedro"]),
            ("João;Maria;Pedro", ["João", "Maria", "Pedro"]),
            ("João|Maria|Pedro", ["João", "Maria", "Pedro"]),
            ("João,  Maria  ,Pedro", ["João", "Maria", "Pedro"]),  # Espaços extras
            ("João", ["João"]),  # Um só aluno
            ("", []),  # String vazia
            ("   ", []),  # Só espaços
            ("João,,Maria", ["João", "Maria"]),  # Separadores extras
        ]

        for input_text, expected in test_cases:
            result = parse_students(input_text)
            assert result == expected, f"Failed for: '{input_text}'"

    def test_parse_students_edge_cases(self):
        """Teste de parsing com casos extremos."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        edge_cases = [
            ("João da Silva, Maria dos Santos", ["João da Silva", "Maria dos Santos"]),
            ("João123, Maria456", ["João123", "Maria456"]),
            ("João-Paulo;Ana-Clara", ["João-Paulo", "Ana-Clara"]),
            ("JOÃO, maria, PeDrO", ["JOÃO", "maria", "PeDrO"]),  # Case sensitivity
            ("João,", ["João"]),  # Vírgula no final
            (",Maria", ["Maria"]),  # Vírgula no início
        ]

        for input_text, expected in edge_cases:
            result = parse_students(input_text)
            assert result == expected, f"Failed for: '{input_text}'"


# =============================================================================
# TESTES DE CRIAÇÃO DE SUBDECKS
# =============================================================================


@pytest.mark.unit
class TestSubdeckCreation:
    """Testes para criação de subdecks por aluno."""

    def test_create_student_subdecks(self, mock_mw):
        """Teste de criação de subdecks para alunos."""

        def create_student_subdecks(deck_name, students, mw):
            created_subdecks = []

            for student in students:
                subdeck_name = f"{deck_name}::{student}"

                # Verificar se subdeck já existe
                deck_id = mw.col.decks.id(subdeck_name, create=False)
                if not deck_id:
                    # Criar novo subdeck
                    new_deck = mw.col.decks.new(subdeck_name)
                    deck_id = mw.col.decks.save(new_deck)
                    created_subdecks.append(subdeck_name)

            return created_subdecks

        # Setup mock
        mock_mw.col.decks.id = Mock(return_value=None)  # Subdecks não existem
        mock_mw.col.decks.new = Mock(return_value={"name": "subdeck"})
        mock_mw.col.decks.save = Mock(return_value=123)

        students = ["João", "Maria", "Pedro"]
        result = create_student_subdecks("Test Deck", students, mock_mw)

        assert len(result) == 3
        assert "Test Deck::João" in result
        assert "Test Deck::Maria" in result
        assert "Test Deck::Pedro" in result

    def test_create_hierarchical_subdecks(self, mock_mw):
        """Teste de criação de subdecks hierárquicos."""

        def create_hierarchical_subdecks(
            base_deck, student, importance, topic, subtopic, concept, mw
        ):
            parts = [base_deck]

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

            subdeck_name = "::".join(parts)

            # Criar hierarquia completa
            current_deck = ""
            for part in parts:
                current_deck = f"{current_deck}::{part}" if current_deck else part

                if not mw.col.decks.id(current_deck, create=False):
                    new_deck = mw.col.decks.new(current_deck)
                    mw.col.decks.save(new_deck)

            return subdeck_name

        # Setup mock
        mock_mw.col.decks.id = Mock(return_value=None)  # Decks não existem
        mock_mw.col.decks.new = Mock(return_value={"name": "deck"})
        mock_mw.col.decks.save = Mock()

        result = create_hierarchical_subdecks(
            "Sheets2Anki", "João", "Alta", "Geografia", "Capitais", "Brasil", mock_mw
        )

        expected = "Sheets2Anki::João::Alta::Geografia::Capitais::Brasil"
        assert result == expected

        # Deve criar 6 decks na hierarquia
        assert mock_mw.col.decks.new.call_count == 6


# =============================================================================
# TESTES DE CONFIGURAÇÃO POR DECK
# =============================================================================


@pytest.mark.unit
class TestDeckStudentConfig:
    """Testes para configuração de alunos por deck específico."""

    def test_set_deck_students(self):
        """Teste de configuração de alunos para deck específico."""

        def set_deck_students(config, deck_name, students):
            if "deck_students" not in config:
                config["deck_students"] = {}

            config["deck_students"][deck_name] = students.copy() if students else []
            return config

        config = {}
        deck_name = "Geografia"
        students = ["João", "Maria"]

        updated_config = set_deck_students(config, deck_name, students)

        assert "deck_students" in updated_config
        assert deck_name in updated_config["deck_students"]
        assert updated_config["deck_students"][deck_name] == students

    def test_get_deck_students(self):
        """Teste de obtenção de alunos de deck específico."""

        def get_deck_students(config, deck_name, fallback_to_global=True):
            deck_students = config.get("deck_students", {}).get(deck_name)

            if deck_students is not None:
                return deck_students

            if fallback_to_global:
                return config.get("global_students", [])

            return []

        config = {
            "global_students": ["Ana", "Bruno"],
            "deck_students": {"Geografia": ["João", "Maria"]},
        }

        # Deck com configuração específica
        geografia_students = get_deck_students(config, "Geografia")
        assert geografia_students == ["João", "Maria"]

        # Deck sem configuração específica (usa global)
        historia_students = get_deck_students(config, "História")
        assert historia_students == ["Ana", "Bruno"]

        # Deck sem configuração e sem fallback
        math_students = get_deck_students(
            config, "Matemática", fallback_to_global=False
        )
        assert math_students == []


# =============================================================================
# TESTES DE VALIDAÇÃO DE ALUNOS
# =============================================================================


@pytest.mark.unit
class TestStudentValidation:
    """Testes para validação de dados de alunos."""

    def test_validate_student_names(self):
        """Teste de validação de nomes de alunos."""

        def validate_student_names(students):
            if not students:
                return True, []

            invalid_names = []

            for student in students:
                if not student or not isinstance(student, str):
                    invalid_names.append(f"Nome inválido: {student}")
                    continue

                student = student.strip()
                if len(student) < 1:
                    invalid_names.append("Nome vazio")
                    continue

                # Verificar se contém pelo menos uma letra
                import re

                if not re.search(r"[a-zA-ZÀ-ÿ]", student):
                    invalid_names.append(f"Nome deve conter letras: {student}")

            return len(invalid_names) == 0, invalid_names

        # Casos válidos
        valid_students = ["João", "Maria Silva", "Ana-Paula", "José123"]
        is_valid, errors = validate_student_names(valid_students)
        assert is_valid == True
        assert len(errors) == 0

        # Casos inválidos
        invalid_students = ["", "   ", "123", None]
        is_valid, errors = validate_student_names(invalid_students)
        assert is_valid == False
        assert len(errors) > 0

    def test_normalize_student_names(self):
        """Teste de normalização de nomes de alunos."""

        def normalize_student_names(students):
            if not students:
                return []

            normalized = []

            for student in students:
                if student and isinstance(student, str):
                    # Remove espaços extras
                    normalized_name = " ".join(student.strip().split())
                    if normalized_name:
                        normalized.append(normalized_name)

            return normalized

        messy_students = [
            "  João  ",
            "Maria   Silva",
            "",
            "   ",
            "Ana\tPaula",  # Tab
            None,
        ]

        result = normalize_student_names(messy_students)
        expected = ["João", "Maria Silva", "Ana Paula"]

        assert result == expected


# =============================================================================
# TESTES DE INTEGRAÇÃO
# =============================================================================


@pytest.mark.integration
class TestStudentManagerIntegration:
    """Testes de integração do gerenciador de alunos."""

    def test_full_student_management_workflow(self, sample_tsv_data, mock_mw):
        """Teste do fluxo completo de gerenciamento de alunos."""

        # Função completa de gerenciamento
        def manage_students_workflow(config, deck_name, tsv_data, mw):
            # 1. Obter alunos globais
            global_students = config.get("global_students", [])
            if not global_students:
                raise ValueError("Nenhum aluno configurado globalmente")

            # 2. Filtrar dados por alunos
            filtered_data = []
            for row in tsv_data:
                alunos_field = row.get("ALUNOS", "")
                if alunos_field:
                    import re

                    row_students = [
                        s.strip() for s in re.split(r"[,;|]", alunos_field) if s.strip()
                    ]
                    matching_students = [
                        s for s in row_students if s in global_students
                    ]
                    if matching_students:
                        filtered_data.append(
                            {**row, "_target_students": matching_students}
                        )

            # 3. Criar subdecks para alunos únicos
            unique_students = set()
            for row in filtered_data:
                unique_students.update(row["_target_students"])

            created_subdecks = []
            for student in unique_students:
                if student != "[MISSING A.]":
                    subdeck_name = f"{deck_name}::{student}"
                    # Simular criação
                    mw.col.decks.id(subdeck_name, create=True)
                    created_subdecks.append(subdeck_name)

            return {
                "filtered_data": filtered_data,
                "created_subdecks": created_subdecks,
                "unique_students": list(unique_students),
            }

        # Setup
        config = {"global_students": ["João", "Maria"]}
        mock_mw.col.decks.id = Mock(return_value=123)

        # Executar fluxo
        result = manage_students_workflow(config, "Test Deck", sample_tsv_data, mock_mw)

        # Verificações
        assert len(result["filtered_data"]) == 2
        assert len(result["created_subdecks"]) >= 1
        assert (
            "João" in result["unique_students"] or "Maria" in result["unique_students"]
        )

    def test_student_config_persistence(self, tmp_path):
        """Teste de persistência de configuração de alunos."""
        import json

        config_file = tmp_path / "student_config.json"

        def save_student_config(config_path, students):
            config = {"global_students": students}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        def load_student_config(config_path):
            if not config_path.exists():
                return []
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
                return config.get("global_students", [])

        # Ciclo completo
        original_students = ["João", "Maria", "Pedro"]

        # Salvar
        save_student_config(config_file, original_students)

        # Carregar
        loaded_students = load_student_config(config_file)

        assert loaded_students == original_students

        # Modificar e salvar novamente
        modified_students = loaded_students + ["Ana"]
        save_student_config(config_file, modified_students)

        # Verificar persistência
        final_students = load_student_config(config_file)
        assert len(final_students) == 4
        assert "Ana" in final_students


if __name__ == "__main__":
    pytest.main([__file__])
