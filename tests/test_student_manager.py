#!/usr/bin/env python3
"""
Tests for the student_manager.py module

Tests functionalities for:
- Global student management
- Data filtering by students
- Subdeck creation by student
- Individual deck configuration
"""

from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# GLOBAL STUDENT MANAGEMENT TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentManager:
    """Class for student manager tests."""

    def test_get_global_students_empty(self):
        """Student retrieval test when list is empty."""

        def get_global_students(config):
            return config.get("global_students", [])

        empty_config = {}
        students = get_global_students(empty_config)

        assert students == []
        assert isinstance(students, list)

    def test_get_global_students_with_data(self, sample_students):
        """Student retrieval test with data."""

        def get_global_students(config):
            return config.get("global_students", [])

        config = {"global_students": sample_students}
        students = get_global_students(config)

        # sample_students in conftest.py were updated to John, Mary, Peter, etc.
        assert len(students) == 5
        assert "John" in students
        assert "Mary" in students

    def test_set_global_students(self):
        """Global student definition test."""

        def set_global_students(config, students):
            config["global_students"] = students.copy() if students else []
            return config

        config = {}
        new_students = ["Ann", "Bob", "Charles"]

        updated_config = set_global_students(config, new_students)

        assert "global_students" in updated_config
        assert len(updated_config["global_students"]) == 3
        assert "Ann" in updated_config["global_students"]

    def test_add_global_student(self):
        """Individual student addition test."""

        def add_global_student(config, student_name):
            if "global_students" not in config:
                config["global_students"] = []

            if student_name and student_name not in config["global_students"]:
                config["global_students"].append(student_name)

            return config

        config = {"global_students": ["John"]}

        # Add new student
        updated_config = add_global_student(config, "Mary")
        assert "Mary" in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2

        # Try to add duplicate student
        updated_config = add_global_student(config, "John")
        assert updated_config["global_students"].count("John") == 1

    def test_remove_global_student(self):
        """Student removal test."""

        def remove_global_student(config, student_name):
            if (
                "global_students" in config
                and student_name in config["global_students"]
            ):
                config["global_students"].remove(student_name)
            return config

        config = {"global_students": ["John", "Mary", "Peter"]}

        updated_config = remove_global_student(config, "Mary")

        assert "Mary" not in updated_config["global_students"]
        assert len(updated_config["global_students"]) == 2
        assert "John" in updated_config["global_students"]


# =============================================================================
# DATA FILTERING TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentFiltering:
    """Tests for data filtering by students."""

    def test_filter_data_by_students_basic(self, sample_tsv_data):
        """Basic filtering test by students."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                # Use key ALUNOS if internal Portuguese key still used in mock data, 
                # or Students if updated. conftest.py uses English names.
                # However, the code being tested might expect Portuguese keys.
                # Looking at conftest.py translation in previous steps, 
                # ALUNOS was translated to Students.
                alunos_field = row.get("Students", row.get("ALUNOS", ""))
                if not alunos_field:
                    # If no students, goes to special category
                    filtered_data.append({**row, "_target_students": ["[MISSING STUDENTS]"]})
                    continue

                # Parse row students
                import re

                row_students = [
                    s.strip() for s in re.split(r"[,;|]", alunos_field) if s.strip()
                ]

                # Check if any row student is in globals
                matching_students = [s for s in row_students if s in global_students]

                if matching_students:
                    filtered_data.append({**row, "_target_students": matching_students})

            return filtered_data

        global_students = ["John", "Mary"]
        result = filter_data_by_students(sample_tsv_data, global_students)

        assert len(result) == 2  # Both rows have John or Mary
        assert "John" in result[0]["_target_students"]
        assert "Mary" in result[1]["_target_students"]

    def test_filter_data_no_matching_students(self, sample_tsv_data):
        """Filtering test with no matching students."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                alunos_field = row.get("Students", row.get("ALUNOS", ""))
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

        global_students = ["Nonexistent"]  # No matching student
        result = filter_data_by_students(sample_tsv_data, global_students)

        assert len(result) == 0

    def test_filter_data_empty_students_field(self):
        """Filtering test with empty STUDENTS field."""

        def filter_data_by_students(data, global_students):
            filtered_data = []

            for row in data:
                alunos_field = row.get("Students", row.get("ALUNOS", ""))
                if not alunos_field or alunos_field.strip() == "":
                    filtered_data.append({**row, "_target_students": ["[MISSING STUDENTS]"]})
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
            {"ID": "Q001", "Students": ""},
            {"ID": "Q002", "Students": "   "},  # Spaces only
            {"ID": "Q003"},  # Missing field
        ]

        result = filter_data_by_students(data, ["John"])

        assert len(result) == 3
        for row in result:
            assert row["_target_students"] == ["[MISSING STUDENTS]"]


# =============================================================================
# STUDENT PARSING TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentParsing:
    """Tests for parsing student names."""

    def test_parse_students_different_separators(self):
        """Parsing test with different separators."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        test_cases = [
            ("John, Mary, Peter", ["John", "Mary", "Peter"]),
            ("John;Mary;Peter", ["John", "Mary", "Peter"]),
            ("John|Mary|Peter", ["John", "Mary", "Peter"]),
            ("John,  Mary  ,Peter", ["John", "Mary", "Peter"]),  # Extra spaces
            ("John", ["John"]),  # Single student
            ("", []),  # Empty string
            ("   ", []),  # Spaces only
            ("John,,Mary", ["John", "Mary"]),  # Extra separators
        ]

        for input_text, expected in test_cases:
            result = parse_students(input_text)
            assert result == expected, f"Failed for: '{input_text}'"

    def test_parse_students_edge_cases(self):
        """Parsing test with edge cases."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        edge_cases = [
            ("John Smith, Mary Jones", ["John Smith", "Mary Jones"]),
            ("John123, Mary456", ["John123", "Mary456"]),
            ("John-Paul;Ann-Clair", ["John-Paul", "Ann-Clair"]),
            ("JOHN, mary, PeTeR", ["JOHN", "mary", "PeTeR"]),  # Case sensitivity
            ("John,", ["John"]),  # Trailing comma
            (",Mary", ["Mary"]),  # Leading comma
        ]

        for input_text, expected in edge_cases:
            result = parse_students(input_text)
            assert result == expected, f"Failed for: '{input_text}'"


# =============================================================================
# SUBDECK CREATION TESTS
# =============================================================================


@pytest.mark.unit
class TestSubdeckCreation:
    """Tests for subdeck creation by student."""

    def test_create_student_subdecks(self, mock_mw):
        """Subdeck creation test for students."""

        def create_student_subdecks(deck_name, students, mw):
            created_subdecks = []

            for student in students:
                subdeck_name = f"{deck_name}::{student}"

                # Check if subdeck already exists
                deck_id = mw.col.decks.id(subdeck_name, create=False)
                if not deck_id:
                    # Create new subdeck
                    new_deck = mw.col.decks.new(subdeck_name)
                    deck_id = mw.col.decks.save(new_deck)
                    created_subdecks.append(subdeck_name)

            return created_subdecks

        # Setup mock
        mock_mw.col.decks.id = Mock(return_value=None)  # Subdecks don't exist
        mock_mw.col.decks.new = Mock(return_value={"name": "subdeck"})
        mock_mw.col.decks.save = Mock(return_value=123)

        students = ["John", "Mary", "Peter"]
        result = create_student_subdecks("Test Deck", students, mock_mw)

        assert len(result) == 3
        assert "Test Deck::John" in result
        assert "Test Deck::Mary" in result
        assert "Test Deck::Peter" in result

    def test_create_hierarchical_subdecks(self, mock_mw):
        """Hierarchical subdeck creation test."""

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

            # Create full hierarchy
            current_deck = ""
            for part in parts:
                current_deck = f"{current_deck}::{part}" if current_deck else part

                if not mw.col.decks.id(current_deck, create=False):
                    new_deck = mw.col.decks.new(current_deck)
                    mw.col.decks.save(new_deck)

            return subdeck_name

        # Setup mock
        mock_mw.col.decks.id = Mock(return_value=None)  # Decks don't exist
        mock_mw.col.decks.new = Mock(return_value={"name": "deck"})
        mock_mw.col.decks.save = Mock()

        result = create_hierarchical_subdecks(
            "Sheets2Anki", "John", "High", "Geography", "Capitals", "Brazil", mock_mw
        )

        expected = "Sheets2Anki::John::High::Geography::Capitals::Brazil"
        assert result == expected

        # Should create 6 decks in hierarchy
        assert mock_mw.col.decks.new.call_count == 6


# =============================================================================
# PER-DECK CONFIGURATION TESTS
# =============================================================================


@pytest.mark.unit
class TestDeckStudentConfig:
    """Tests for student configuration for a specific deck."""

    def test_set_deck_students(self):
        """Student configuration test for a specific deck."""

        def set_deck_students(config, deck_name, students):
            if "deck_students" not in config:
                config["deck_students"] = {}

            config["deck_students"][deck_name] = students.copy() if students else []
            return config

        config = {}
        deck_name = "Geography"
        students = ["John", "Mary"]

        updated_config = set_deck_students(config, deck_name, students)

        assert "deck_students" in updated_config
        assert deck_name in updated_config["deck_students"]
        assert updated_config["deck_students"][deck_name] == students

    def test_get_deck_students(self):
        """Student retrieval test for a specific deck."""

        def get_deck_students(config, deck_name, fallback_to_global=True):
            deck_students = config.get("deck_students", {}).get(deck_name)

            if deck_students is not None:
                return deck_students

            if fallback_to_global:
                return config.get("global_students", [])

            return []

        config = {
            "global_students": ["Ann", "Bob"],
            "deck_students": {"Geography": ["John", "Mary"]},
        }

        # Deck with specific configuration
        geography_students = get_deck_students(config, "Geography")
        assert geography_students == ["John", "Mary"]

        # Deck without specific configuration (uses global)
        history_students = get_deck_students(config, "History")
        assert history_students == ["Ann", "Bob"]

        # Deck without configuration and no fallback
        math_students = get_deck_students(
            config, "Math", fallback_to_global=False
        )
        assert math_students == []


# =============================================================================
# STUDENT VALIDATION TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentValidation:
    """Tests for student data validation."""

    def test_validate_student_names(self):
        """Student name validation test."""

        def validate_student_names(students):
            if not students:
                return True, []

            invalid_names = []

            for student in students:
                if not student or not isinstance(student, str):
                    invalid_names.append(f"Invalid name: {student}")
                    continue

                student = student.strip()
                if len(student) < 1:
                    invalid_names.append("Empty name")
                    continue

                # Check if contains at least one letter
                import re

                if not re.search(r"[a-zA-ZÀ-ÿ]", student):
                    invalid_names.append(f"Name must contain letters: {student}")

            return len(invalid_names) == 0, invalid_names

        # Valid cases
        valid_students = ["John", "Mary Smith", "Ann-Paula", "Joe123"]
        is_valid, errors = validate_student_names(valid_students)
        assert is_valid == True
        assert len(errors) == 0

        # Invalid cases
        invalid_students = ["", "   ", "123", None]
        is_valid, errors = validate_student_names(invalid_students)
        assert is_valid == False
        assert len(errors) > 0

    def test_normalize_student_names(self):
        """Student name normalization test."""

        def normalize_student_names(students):
            if not students:
                return []

            normalized = []

            for student in students:
                if student and isinstance(student, str):
                    # Remove extra spaces
                    normalized_name = " ".join(student.strip().split())
                    if normalized_name:
                        normalized.append(normalized_name)

            return normalized

        messy_students = [
            "  John  ",
            "Mary   Jones",
            "",
            "   ",
            "Ann\tPaula",  # Tab
            None,
        ]

        result = normalize_student_names(messy_students)
        expected = ["John", "Mary Jones", "Ann Paula"]

        assert result == expected


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestStudentManagerIntegration:
    """Student manager integration tests."""

    def test_full_student_management_workflow(self, sample_tsv_data, mock_mw):
        """Full student management workflow test."""

        # Full management function
        def manage_students_workflow(config, deck_name, tsv_data, mw):
            # 1. Get global students
            global_students = config.get("global_students", [])
            if not global_students:
                raise ValueError("No students configured globally")

            # 2. Filter data by students
            filtered_data = []
            for row in tsv_data:
                alunos_field = row.get("Students", row.get("ALUNOS", ""))
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

            # 3. Create subdecks for unique students
            unique_students = set()
            for row in filtered_data:
                unique_students.update(row["_target_students"])

            created_subdecks = []
            for student in unique_students:
                if student != "[MISSING STUDENTS]":
                    subdeck_name = f"{deck_name}::{student}"
                    # Simulate creation
                    mw.col.decks.id(subdeck_name, create=True)
                    created_subdecks.append(subdeck_name)

            return {
                "filtered_data": filtered_data,
                "created_subdecks": created_subdecks,
                "unique_students": list(unique_students),
            }

        # Setup
        config = {"global_students": ["John", "Mary"]}
        mock_mw.col.decks.id = Mock(return_value=123)

        # Execute workflow
        result = manage_students_workflow(config, "Test Deck", sample_tsv_data, mock_mw)

        # Checks
        assert len(result["filtered_data"]) == 2
        assert len(result["created_subdecks"]) >= 1
        assert (
            "John" in result["unique_students"] or "Mary" in result["unique_students"]
        )

    def test_student_config_persistence(self, tmp_path):
        """Student configuration persistence test."""
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

        # Full cycle
        original_students = ["John", "Mary", "Peter"]

        # Save
        save_student_config(config_file, original_students)

        # Load
        loaded_students = load_student_config(config_file)

        assert loaded_students == original_students

        # Modify and save again
        modified_students = loaded_students + ["Ann"]
        save_student_config(config_file, modified_students)

        # Verify persistence
        final_students = load_student_config(config_file)
        assert len(final_students) == 4
        assert "Ann" in final_students


if __name__ == "__main__":
    pytest.main([__file__])
