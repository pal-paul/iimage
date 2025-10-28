# Tests

This directory contains the test suite for the Image Object Detection API.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_detector.py` - Unit tests for the ObjectDetector class
- `test_validators.py` - Unit tests for input validators
- `test_api.py` - Integration tests for API endpoints

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest --cov=lib --cov=api --cov-report=html tests/
```

### Run specific test file
```bash
pytest tests/test_detector.py
```

### Run specific test
```bash
pytest tests/test_detector.py::TestObjectDetector::test_initialization
```

### Run with verbose output
```bash
pytest -v tests/
```

### Skip slow tests
```bash
pytest -m "not slow" tests/
```

## Test Coverage

Aim for at least 80% code coverage across all modules.

View coverage report:
```bash
open htmlcov/index.html
```
