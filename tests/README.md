# 🧪 Sheets2Anki Tests

This directory contains the complete test suite for the Sheets2Anki add-on, developed with pytest.

## 📋 Test Structure

### 📁 Test Files

| File | Description | Coverage |
|---------|-----------|-----------|
| `conftest.py` | Common configurations and fixtures | Reusable fixtures |
| `test_data_processor.py` | TSV data processing | Parsing, validation, cloze detection |
| `test_config_manager.py` | Settings management | Settings CRUD, persistence |
| `test_utils.py` | Utility functions | URLs, hashes, validations |
| `test_student_manager.py` | Student management | Global students, filtering |
| `test_integration.py` | Integration tests | Complete flows |
| `test_new_tags.py` | Tag system (legacy) | Hierarchical tags |
| `run_tests.py` | Executor script | Test automation |

### 🏷️ Test Categories

#### **🔬 Unit Tests** (`@pytest.mark.unit`)
- Test isolated functions
- Fast execution
- Mocks for external dependencies
- Edge case coverage

#### **🔗 Integration Tests** (`@pytest.mark.integration`) 
- Test complete flows
- Interaction between modules
- Real usage scenarios
- End-to-end validation

#### **🐌 Slow Tests** (`@pytest.mark.slow`)
- Performance tests
- Large datasets
- Time-consuming operations
- Skipped in fast execution

## 🚀 How to Run Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock
```

### Basic Execution

```bash
# All tests
python tests/run_tests.py

# Or directly with pytest
python -m pytest tests/
```

### Advanced Options

```bash
# 🔬 Unit tests only
python tests/run_tests.py --unit

# 🔗 Integration tests only  
python tests/run_tests.py --integration

# 📊 With code coverage
python tests/run_tests.py --coverage

# 🏃 Fast execution (skips slow tests)
python tests/run_tests.py --fast

# 🔍 Detailed output
python tests/run_tests.py --verbose

# 📁 Specific file
python tests/run_tests.py --file data_processor

# 🎯 Specific function
python tests/run_tests.py --function test_parse_students

# ℹ️ Information about available tests
python tests/run_tests.py --info
```

### Useful Combinations

```bash
# Development: unit tests with detailed output
python tests/run_tests.py --unit --verbose

# CI/CD: all tests with coverage
python tests/run_tests.py --coverage

# Debug: specific file with verbose
python tests/run_tests.py --file utils --verbose

# Performance: only slow tests
python -m pytest tests/ -m slow -v
```

## 🏗️ Available Fixtures

### 📊 Test Data

- `sample_tsv_data`: Structured TSV data for testing
- `sample_tsv_content`: TSV content in string format  
- `sample_students`: List of students for testing
- `sample_url`: Example Google Sheets URL
- `sample_config`: Default configuration for testing

### 🎭 Anki Mocks

- `mock_mw`: Anki main window mock
- `mock_note`: Anki note mock
- `mock_note_type`: Note type mock
- `setup_test_environment`: Automatic mock configuration

### 📁 Temporary Files

- `temp_config_file`: Temporary configuration file
- `clean_sys_path`: sys.path cleanup after tests

## 📝 Writing New Tests

### Basic Structure

```python
import pytest

@pytest.mark.unit
class TestMyModule:
    """Tests for the MyModule module."""
    
    def test_basic_functionality(self):
        """Basic functionality test."""
        # Arrange
        input_data = "test_input"
        expected = "expected_output"
        
        # Act  
        result = my_function(input_data)
        
        # Assert
        assert result == expected
    
    def test_edge_cases(self):
        """Edge cases test."""
        assert my_function("") == ""
        assert my_function(None) is None
        
    def test_error_handling(self):
        """Error handling test."""
        with pytest.raises(ValueError):
            my_function("invalid_input")
```

### Using Fixtures

```python
def test_with_fixtures(self, sample_tsv_data, mock_mw):
    """Test using fixtures."""
    # Use sample data
    assert len(sample_tsv_data) > 0
    
    # Use Anki mock
    mock_mw.col.findNotes.return_value = [123, 456]
    result = my_anki_function(mock_mw)
    assert len(result) == 2
```

### Integration Tests

```python
@pytest.mark.integration
def test_complete_workflow(self, tmp_path):
    """Complete flow test."""
    # Create temporary environment
    config_file = tmp_path / "test_config.json"
    
    # Execute complete flow
    result = complete_workflow(str(config_file))
    
    # Check result
    assert result['success'] == True
```

## 📊 Code Coverage

### Generate Report

```bash
# HTML Report (recommended)
python tests/run_tests.py --coverage

# Open in browser
open htmlcov/index.html
```

### Target Metrics

- **Total Coverage**: > 80%
- **Critical Modules**: > 90%
- **Public Functions**: 100%

### View Coverage

The HTML report shows:
- ✅ Covered lines (green)
- ❌ Uncovered lines (red)  
- ⚠️ Partial branches (yellow)
- 📊 Percentage per file

## 🐛 Test Debugging

### Debug Execution

```bash
# Stop on first error
python -m pytest tests/ -x

# Show local variables on failure
python -m pytest tests/ -l

# Interactive debug mode
python -m pytest tests/ --pdb

# Capture prints
python -m pytest tests/ -s
```

### Debug Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Debug info")
    
    # Test continues...
```

## 🔧 Custom Configuration

### pytest.ini (already configured)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: mark a test as a unit test
    integration: mark a test as an integration test
    slow: mark a test as slow (skipped in quick mode)
addopts = -v
```

### Customize Markers

```bash
# Run only marked tests
python -m pytest tests/ -m "unit and not slow"

# Run tests with custom tag
python -m pytest tests/ -m "requires_anki"
```

## 🎯 Best Practices

### ✅ Do's

- **Use fixtures** for common data
- **Test edge cases** (null, empty, invalid values)
- **Descriptive names** for test functions
- **Clear documentation** of what is being tested
- **Arrange-Act-Assert** pattern
- **Mocks** for external dependencies

### ❌ Don'ts

- **Don't test implementation**, test behavior
- **Don't use hardcoded data** unnecessarily
- **Don't ignore intermittent failures**
- **Don't test third-party code**
- **Don't make tests too complex**

### 🏗️ Recommended Structure

```python
class TestMyFeature:
    """Tests grouped by feature."""
    
    def test_happy_path(self):
        """Main success scenario."""
        pass
    
    def test_edge_cases(self):
        """Edge cases."""
        pass
    
    def test_error_handling(self):
        """Error handling."""
        pass
```

## 📈 Metrics and Reports

### Perform Complete Analysis

```bash
# Coverage + detailed reports
python tests/run_tests.py --coverage --verbose

# View statistics
python tests/run_tests.py --info
```

### CI/CD Integration

```bash
# For automated pipelines
python -m pytest tests/ \
  --cov=src \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results.xml
```

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/
```

#### Mock Issues
```python
# Check if mocks are being applied correctly
def test_debug_mock(self, mock_mw):
    print(f"Mock type: {type(mock_mw)}")
    print(f"Mock methods: {dir(mock_mw)}")
```

#### Fixture Conflicts
```python
# Use specific fixtures when necessary
def test_specific_fixture(self, sample_tsv_data):
    # Instead of generic fixture, create specific data
    specific_data = [{'ID': 'TEST001', 'PERGUNTA': 'Test?'}]
```

### Debug Logs

```bash
# View detailed test logs
python -m pytest tests/ --log-cli-level=DEBUG
```

## 🚀 Next Steps

### Planned Improvements

- [ ] Automated performance tests
- [ ] Mutation testing coverage
- [ ] Load tests for large datasets
- [ ] GitHub Actions integration
- [ ] Multi-version compatibility tests

### How to Contribute

1. **Identify gaps** in coverage
2. **Write tests** following standards
3. **Run the full suite** before committing
4. **Document** complex cases
5. **Keep fixtures** updated

---

For more information on pytest: https://docs.pytest.org/
