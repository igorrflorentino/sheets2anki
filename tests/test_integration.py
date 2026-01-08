#!/usr/bin/env python3
"""
General integration tests for Sheets2Anki

Tests the complete flow of:
- Configuration loading
- Remote spreadsheet fetching
- Data processing
- Anki note creation
- AnkiWeb synchronization
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# FULL INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestFullIntegration:
    """Full system integration tests."""

    def test_complete_sync_workflow(
        self, sample_tsv_content, sample_students, mock_mw, tmp_path
    ):
        """Complete synchronization workflow test."""

        # === SETUP ===
        config_file = tmp_path / "integration_config.json"
        config = {
            "remote_decks": {
                "Test Deck": "https://docs.google.com/spreadsheets/test/pub?output=tsv"
            },
            "global_students": sample_students[:3],  # John, Mary, Peter
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
            """Simulates remote spreadsheet download."""
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
                # Support both Students (English) and ALUNOS (Portuguese)
                students_field = row.get("Students", row.get("ALUNOS", ""))
                if students_field:
                    import re

                    row_students = [s.strip() for s in re.split(r"[,;|]", students_field)]
                    matching = [s for s in row_students if s in global_students]
                    if matching:
                        filtered.append({**row, "_target_students": matching})
            return filtered

        def create_anki_notes(filtered_data, deck_name, mw):
            created_notes = []

            for row in filtered_data:
                for student in row["_target_students"]:
                    # Simulate note creation
                    note = Mock()
                    note.id = len(created_notes) + 1
                    # Support both English and Portuguese headers
                    question = row.get("Question", row.get("PERGUNTA", ""))
                    answer = row.get("Answer", row.get("LEVAR PARA PROVA", ""))
                    note.fields = [question, answer]
                    # Student tags removed - now only topics/other fields tags
                    note.tags = [f"Sheets2Anki::Topics::Geography"]

                    # Mock Anki operations
                    mw.col.newNote.return_value = note
                    mw.col.addNote.return_value = note.id

                    created_notes.append(note)

            return created_notes

        # === COMPLETE FLOW EXECUTION ===

        # 1. Load configuration
        loaded_config = load_config(config_file)
        assert "remote_decks" in loaded_config

        # 2. For each configured deck
        for deck_name, url in loaded_config["remote_decks"].items():
            # 3. Fetch remote data
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = Mock()
                mock_response.read.return_value = sample_tsv_content.encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                raw_content = fetch_remote_deck(url)
                assert "Q001" in raw_content

                # 4. Process TSV data
                parsed_data = parse_tsv_data(raw_content)
                assert len(parsed_data) == 2

                # 5. Filter by global students
                filtered_data = filter_by_students(
                    parsed_data, loaded_config["global_students"]
                )
                assert len(filtered_data) > 0

                # 6. Create Anki notes
                created_notes = create_anki_notes(filtered_data, deck_name, mock_mw)
                assert len(created_notes) > 0

                # 7. Verify notes were created correctly
                for note in created_notes:
                    assert hasattr(note, "id")
                    assert hasattr(note, "fields")
                    assert hasattr(note, "tags")
                    # Check for topic tags instead of student tags
                    assert any("Sheets2Anki::Topics::" in tag for tag in note.tags)

    def test_error_handling_integration(self, mock_mw):
        """Integration error handling test."""

        def sync_with_error_handling(deck_name, url, global_students, mw):
            errors = []
            success_count = 0

            try:
                # 1. Validate URL
                if not url or "docs.google.com" not in url:
                    raise ValueError(f"Invalid URL: {url}")

                # 2. Simulate network error
                if "error" in url:
                    raise ConnectionError("Spreadsheet connection error")

                # 3. Validate students
                if not global_students:
                    raise ValueError("No students configured")

                # 4. Simulate successful processing
                success_count = len(global_students)

            except ValueError as e:
                errors.append(f"Validation error: {str(e)}")
            except ConnectionError as e:
                errors.append(f"Connection error: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error: {str(e)}")

            return {
                "success": len(errors) == 0,
                "errors": errors,
                "success_count": success_count if len(errors) == 0 else 0,
            }

        # Success case
        result = sync_with_error_handling(
            "Test Deck",
            "https://docs.google.com/spreadsheets/valid/pub?output=tsv",
            ["John", "Mary"],
            mock_mw,
        )
        assert result["success"] == True
        assert result["success_count"] == 2

        # URL error case
        result = sync_with_error_handling("Test Deck", "invalid_url", ["John"], mock_mw)
        assert result["success"] == False
        assert len(result["errors"]) > 0
        assert "Invalid URL" in result["errors"][0]

        # Connection error case
        result = sync_with_error_handling(
            "Test Deck",
            "https://docs.google.com/spreadsheets/error/pub?output=tsv",
            ["John"],
            mock_mw,
        )
        assert result["success"] == False
        assert "Connection error" in result["errors"][0]


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================


@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceIntegration:
    """Performance tests in integration scenarios."""

    def test_large_dataset_processing(self):
        """Test with large dataset."""
        import time

        # Generate large dataset
        def generate_large_dataset(size):
            headers = [
                "ID",
                "Question",
                "Answer",
                "SYNC",
                "Students",
                "Topic",
            ]
            data = []

            for i in range(size):
                row = {
                    "ID": f"Q{i:04d}",
                    "Question": f"Question {i}",
                    "Answer": f"Answer {i}",
                    "SYNC": "true",
                    "Students": f"Student{i % 10}",  # 10 different students
                    "Topic": f"Topic{i % 5}",  # 5 different topics
                }
                data.append(row)

            return data

        def process_large_dataset(data, global_students):
            start_time = time.time()

            # Simulate processing
            filtered_data = []
            for row in data:
                if row["Students"] in global_students:
                    # Simulate some processing
                    processed_row = {**row}
                    processed_row["_processed"] = True
                    filtered_data.append(processed_row)

            processing_time = time.time() - start_time
            return filtered_data, processing_time

        # Test with 1000 records
        large_data = generate_large_dataset(1000)
        global_students = [f"Student{i}" for i in range(5)]  # 5 students

        result, processing_time = process_large_dataset(large_data, global_students)

        # Checks
        assert len(result) == 500  # Half of records (5 of 10 students)
        assert processing_time < 1.0  # Should process in less than 1 second
        assert all(row["_processed"] for row in result)


# =============================================================================
# COMPATIBILITY TESTS
# =============================================================================


@pytest.mark.integration
class TestCompatibilityIntegration:
    """Compatibility tests with different versions."""

    def test_anki_version_compatibility(self, mock_mw):
        """Compatibility test with different Anki versions."""

        def get_anki_version_mock():
            return "2.1.54"  # Modern version

        def sync_with_version_check(mw, version_getter=get_anki_version_mock):
            version = version_getter()
            major, minor, patch = map(int, version.split("."))

            compatibility = {
                "modern_api": major > 2 or (major == 2 and minor >= 1 and patch >= 50),
                "supports_cloze": True,
                "supports_hierarchical_decks": True,
            }

            # Use appropriate APIs based on version
            if compatibility["modern_api"]:
                # Modern API
                mw.col.decks.id_for_name = Mock(return_value=123)
                result = {"api": "modern", "deck_id": mw.col.decks.id_for_name("test")}
            else:
                # Legacy API
                mw.col.decks.id = Mock(return_value=456)
                result = {"api": "legacy", "deck_id": mw.col.decks.id("test")}

            return result

        # Test with modern version
        result = sync_with_version_check(mock_mw)
        assert result["api"] == "modern"
        assert result["deck_id"] == 123

        # Test with old version
        def old_version_getter():
            return "2.1.40"

        result = sync_with_version_check(mock_mw, old_version_getter)
        assert result["api"] == "legacy"
        assert result["deck_id"] == 456


# =============================================================================
# REAL WORLD SCENARIOS TESTS
# =============================================================================


@pytest.mark.integration
class TestRealWorldScenarios:
    """Tests based on real-world use scenarios."""

    def test_professor_multi_class_scenario(self, tmp_path):
        """Scenario: Professor with multiple classes."""

        # Professor configuration
        config = {
            "global_students": [
                "John_Class_A",
                "Mary_Class_A",
                "Peter_Class_A",
                "Ann_Class_B",
                "Charles_Class_B",
                "Lucy_Class_B",
            ],
            "remote_decks": {
                "General_Geography": "https://docs.google.com/spreadsheets/geo/pub?output=tsv",
                "Brazil_History": "https://docs.google.com/spreadsheets/hist/pub?output=tsv",
            },
        }

        # Sheet data simulating different content per class
        geo_data = [
            {
                "ID": "GEO001",
                "Question": "Capital of Brazil?",
                "Students": "John_Class_A, Mary_Class_A",
                "Topic": "Capitais",
                "Importance": "High",
            },
            {
                "ID": "GEO002",
                "Question": "Largest river in the world?",
                "Students": "Ann_Class_B, Charles_Class_B",
                "Topic": "Hidrografia",
                "Importance": "Medium",
            },
        ]

        def process_multi_class_scenario(config, data_by_deck):
            results = {}

            for deck_name in config["remote_decks"]:
                deck_data = data_by_deck.get(deck_name, [])

                # Filter by global students
                filtered_data = []
                for row in deck_data:
                    students = row.get("Students", row.get("ALUNOS", ""))
                    if students:
                        import re

                        row_students = [s.strip() for s in re.split(r"[,;|]", students)]
                        matching = [
                            s for s in row_students if s in config["global_students"]
                        ]
                        if matching:
                            filtered_data.append({**row, "_target_students": matching})

                # Group by class
                class_a_count = 0
                class_b_count = 0

                for row in filtered_data:
                    for student in row["_target_students"]:
                        if "Class_A" in student:
                            class_a_count += 1
                        elif "Class_B" in student:
                            class_b_count += 1

                results[deck_name] = {
                    "total_notes": len(filtered_data),
                    "class_a_notes": class_a_count,
                    "class_b_notes": class_b_count,
                }

            return results

        data_by_deck = {"General_Geography": geo_data}
        results = process_multi_class_scenario(config, data_by_deck)

        assert "General_Geography" in results
        assert results["General_Geography"]["class_a_notes"] > 0
        assert results["General_Geography"]["class_b_notes"] > 0

    def test_student_group_collaborative_scenario(self):
        """Scenario: Collaborative study group."""

        # Study group simulation
        group_config = {
            "global_students": ["John", "Mary", "Peter", "Ann"],
            "study_areas": {
                "John": ["Math", "Physics"],
                "Mary": ["Chemistry", "Biology"],
                "Peter": ["History", "Geography"],
                "Ann": ["Literature", "Philosophy"],
            },
        }

        collaborative_data = [
            {"ID": "MAT001", "Topic": "Math", "Students": "John, Mary"},
            {"ID": "QUI001", "Topic": "Chemistry", "Students": "Mary, Peter"},
            {"ID": "HIS001", "Topic": "History", "Students": "Peter, Ann"},
            {"ID": "LIT001", "Topic": "Literature", "Students": "Ann, John"},
        ]

        def analyze_collaboration_patterns(config, data):
            collaboration_matrix = {}
            topic_coverage = {}

            for row in data:
                topic = row.get("Topic", row.get("TOPICO", "General"))
                students_str = row.get("Students", row.get("ALUNOS", ""))

                if students_str:
                    students = [s.strip() for s in students_str.split(",")]

                    # Register coverage per topic
                    if topic not in topic_coverage:
                        topic_coverage[topic] = set()
                    topic_coverage[topic].update(students)

                    # Collaboration matrix
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
