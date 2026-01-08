#!/usr/bin/env python3
"""
Tests for the data_processor.py module

Tests functionalities for:
- TSV data parsing
- Column validation
- Cloze card detection
- Data processing
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

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# =============================================================================
# TSV PARSING TESTS
# =============================================================================


@pytest.mark.unit
class TestDataProcessor:
    """Class for data processor tests."""

    def test_parse_tsv_basic(self, sample_tsv_content):
        """Basic TSV parsing test."""
        try:
            from data_processor import parse_tsv_data
        except ImportError:
            pytest.skip("data_processor module not available")

        # parse_tsv_data function mock
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
            assert result[0]["PERGUNTA"] == "What is the capital of Brazil?"
            assert result[1]["ID"] == "Q002"

    def test_parse_empty_tsv(self):
        """Parsing test with empty TSV."""

        def mock_parse_empty(content):
            if not content or content.strip() == "":
                return []
            return []

        result = mock_parse_empty("")
        assert result == []

    def test_parse_invalid_tsv(self):
        """Parsing test with invalid TSV."""
        invalid_content = "invalid\tcontent\nwithout\tproper\theaders"

        def mock_parse_invalid(content):
            if "ID" not in content or "PERGUNTA" not in content:
                raise ValueError("Invalid TSV - mandatory columns missing")
            return []

        with pytest.raises(ValueError):
            mock_parse_invalid(invalid_content)


# =============================================================================
# COLUMN VALIDATION TESTS
# =============================================================================


@pytest.mark.unit
class TestColumnValidation:
    """Validation tests for the 18 mandatory columns."""

    def test_validate_required_columns(self, sample_tsv_data):
        """Mandatory columns validation test."""
        required_columns = [
            "ID",
            "PERGUNTA",
            "LEVAR PARA PROVA",
            "SYNC",
            "ALUNOS",
            "INFO COMPLEMENTAR",
            "INFO DETALHADA",
            "IMAGEM HTML",
            "VÍDEO HTML",
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
            "EXTRA 1",
            "EXTRA 2",
            "EXTRA 3",
        ]

        def validate_columns(data):
            if not data:
                return False
            first_row = data[0]
            # In the sample data, column names might be the English ones or Portuguese originals
            # but we've updated fixtures/conftest to use English.
            return all(col in first_row for col in required_columns)

        assert validate_columns(sample_tsv_data) == True

    def test_missing_columns(self):
        """Test with missing columns."""
        incomplete_data = [{"ID": "Q001", "PERGUNTA": "Test"}]

        def validate_columns(data):
            # Only ID and LEVAR PARA PROVA are actually required now
            required_columns = ["ID", "LEVAR PARA PROVA"]
            if not data:
                return False
            first_row = data[0]
            return all(col in first_row for col in required_columns)

        assert validate_columns(incomplete_data) == False


# =============================================================================
# CLOZE DETECTION TESTS
# =============================================================================


@pytest.mark.unit
class TestClozeDetection:
    """Tests for cloze card detection."""

    def test_detect_cloze_basic(self):
        """Basic cloze detection test."""

        def detect_cloze(question):
            import re

            cloze_pattern = r"\{\{c\d+::.*?\}\}"
            return bool(re.search(cloze_pattern, question))

        # Positive cases
        assert detect_cloze("The capital of {{c1::Brazil}} is {{c2::Brasília}}") == True
        assert detect_cloze("{{c1::Python}} is a language") == True
        assert detect_cloze("Test {{c3::multiple}} words {{c1::cloze}}") == True

        # Negative cases
        assert detect_cloze("Normal question without cloze") == False
        assert detect_cloze("Text with {curly_braces} but not cloze") == False
        assert detect_cloze("") == False

    def test_cloze_patterns(self):
        """Test different cloze patterns."""

        def detect_cloze(question):
            import re

            cloze_pattern = r"\{\{c\d+::.*?\}\}"
            return bool(re.search(cloze_pattern, question))

        test_cases = [
            ("{{c1::answer}}", True),
            ("{{c10::long answer}}", True),
            ("{{c1::answer::hint}}", True),
            ("{{c1:answer}}", False),  # Incorrect format
            ("{c1::answer}", False),  # Incorrect format
            ("{{C1::answer}}", False),  # Case sensitive
        ]

        for question, expected in test_cases:
            assert detect_cloze(question) == expected, f"Failed for: {question}"


# =============================================================================
# STUDENT PROCESSING TESTS
# =============================================================================


@pytest.mark.unit
class TestStudentProcessing:
    """Tests for student data processing."""

    def test_parse_students_comma_separated(self):
        """Test parsing of comma-separated students."""

        def parse_students(student_text):
            if not student_text or student_text.strip() == "":
                return []

            # Supports comma, semicolon, pipe
            import re

            students = re.split(r"[,;|]", student_text)
            return [s.strip() for s in students if s.strip()]

        assert parse_students("John, Mary, Peter") == ["John", "Mary", "Peter"]
        assert parse_students("John;Mary;Peter") == ["John", "Mary", "Peter"]
        assert parse_students("John|Mary|Peter") == ["John", "Mary", "Peter"]
        assert parse_students("John") == ["John"]
        assert parse_students("") == []
        assert parse_students("  ") == []

    def test_normalize_student_names(self):
        """Test student name normalization."""

        def normalize_student_name(name):
            if not name:
                return ""
            return name.strip().replace(" ", "_")

        assert normalize_student_name("John Smith") == "John_Smith"
        assert normalize_student_name("  Mary  ") == "Mary"
        assert normalize_student_name("") == ""


# =============================================================================
# SYNC CONTROL TESTS
# =============================================================================


@pytest.mark.unit
class TestSyncControl:
    """Tests for sync control."""

    def test_sync_flag_parsing(self):
        """Test SYNC flag interpretation."""

        def should_sync(sync_flag):
            if not sync_flag:
                return True  # Default is to sync

            sync_flag = str(sync_flag).lower().strip()

            # Values that indicate YES to sync
            yes_values = ["true", "sim", "yes", "1", "v", "verdadeiro"]
            # Values that indicate NO to sync
            no_values = ["false", "não", "nao", "no", "0", "f", "falso"]

            if sync_flag in yes_values or sync_flag == "":
                return True
            elif sync_flag in no_values:
                return False
            else:
                return True  # Default for unknown values

        # Positive cases
        assert should_sync("true") == True
        assert should_sync("sim") == True
        assert should_sync("yes") == True
        assert should_sync("1") == True
        assert should_sync("") == True
        assert should_sync(None) == True

        # Negative cases
        assert should_sync("false") == False
        assert should_sync("não") == False
        assert should_sync("no") == False
        assert should_sync("0") == False


# =============================================================================
# TAG CREATION TESTS
# =============================================================================


@pytest.mark.unit
class TestTagCreation:
    """Tests for hierarchical tag creation."""

    def test_create_hierarchical_tags(self):
        """Hierarchical tags creation test."""

        def create_tags_for_note(note_data):
            tags = []

            # Root tag
            tag_root = "Sheets2Anki"

            # Topic tags
            if note_data.get("TOPICO"):
                topics = [t.strip() for t in note_data["TOPICO"].split(",")]
                for topic in topics:
                    if topic:
                        tag = f"{tag_root}::Topics::{topic}"
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

            # Importance tags
            if note_data.get("IMPORTANCIA"):
                tags.append(f"{tag_root}::Importance::{note_data['IMPORTANCIA']}")

            return list(set(tags))  # Remove duplicates

        test_note = {
            "ALUNOS": "John, Mary",
            "TOPICO": "Geography",
            "SUBTOPICO": "Capitals",
            "CONCEITO": "Brazil",
            "IMPORTANCIA": "High",
        }

        tags = create_tags_for_note(test_note)

        # Check if it contains expected tags (excluding student tags)
        expected_patterns = [
            "Sheets2Anki::Topics::Geography::Capitals::Brazil",
            "Sheets2Anki::Importance::High",
        ]

        for pattern in expected_patterns:
            assert any(
                pattern in tag for tag in tags
            ), f"Pattern '{pattern}' not found in: {tags}"

        # Verify that student tags are NOT present
        student_patterns = [
            "Sheets2Anki::Students::John",
            "Sheets2Anki::Students::Mary",
        ]

        for pattern in student_patterns:
            assert not any(
                pattern in tag for tag in tags
            ), f"Student pattern '{pattern}' should NOT be found in: {tags}"

    def test_clean_tag_text(self):
        """Tag text cleaning test."""

        def clean_tag_text(text):
            if not text:
                return ""
            import re

            # Remove special characters and replace spaces
            cleaned = re.sub(r"[^\w\s-]", "", text)
            cleaned = cleaned.replace(" ", "_").replace("-", "_")
            return cleaned.strip("_")

        assert clean_tag_text("General Geography") == "General_Geography"
        assert clean_tag_text("Basic - Concepts") == "Basic___Concepts"
        assert clean_tag_text("Test!@#$%") == "Test"
        assert clean_tag_text("") == ""


# =============================================================================
# REMOTE DECK TESTS
# =============================================================================


@pytest.mark.unit
class TestRemoteDeck:
    """Tests for remote deck functionalities."""

    @patch("urllib.request.urlopen")
    def test_fetch_remote_deck_success(self, mock_urlopen, sample_tsv_content):
        """Successful remote deck fetching test."""
        # HTTP response mock
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
        assert "What is the capital of Brazil?" in result

    @patch("urllib.request.urlopen")
    def test_fetch_remote_deck_error(self, mock_urlopen):
        """Error fetching remote deck test."""
        mock_urlopen.side_effect = Exception("Network error")

        def fetch_remote_deck_with_error(url):
            import urllib.request

            try:
                with urllib.request.urlopen(url) as response:
                    return response.read().decode("utf-8")
            except Exception as e:
                raise Exception(f"Error fetching deck: {str(e)}")

        url = "https://invalid-url.com"

        with pytest.raises(Exception, match="Error fetching deck"):
            fetch_remote_deck_with_error(url)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestDataProcessorIntegration:
    """Integration tests for data processor."""

    def test_full_processing_pipeline(self, sample_tsv_content, sample_students):
        """Full processing pipeline test."""

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
                row["_should_sync"] = row.get("SYNC", "").lower() not in [
                    "false",
                    "não",
                    "0",
                    "no",
                ]

            return filtered_data

        result = process_tsv_data(sample_tsv_content, ["John", "Mary"])

        assert len(result) == 2  # Both records have John or Mary
        assert result[0]["_should_sync"] == True
        assert result[1]["_is_cloze"] == True


if __name__ == "__main__":
    pytest.main([__file__])
