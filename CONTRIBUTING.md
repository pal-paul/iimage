# Contributing to Image Object Detection API

Thank you for your interest in contributing! This document provides guidelines and best practices.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install development tools:
   ```bash
   pip install black isort mypy flake8
   ```

## Code Standards

### Python Style Guide

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Code Formatting

Format code with Black:
```bash
black lib/ api/ tests/
```

Sort imports with isort:
```bash
isort lib/ api/ tests/
```

### Type Checking

Run mypy for type checking:
```bash
mypy lib/ api/
```

### Linting

Run flake8:
```bash
flake8 lib/ api/ tests/ --max-line-length=100
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=lib --cov=api --cov-report=html tests/

# Specific test file
pytest tests/test_detector.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names
- Aim for >80% code coverage
- Include both positive and negative test cases

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

## Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

Example:
```
feat: add batch processing endpoint

- Implement /api/v1/detect/batch endpoint
- Add validation for multiple files
- Update documentation
```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

3. Run tests and checks:
   ```bash
   pytest tests/
   black lib/ api/ tests/
   flake8 lib/ api/ tests/
   mypy lib/ api/
   ```

4. Push and create PR:
   ```bash
   git push origin feat/your-feature-name
   ```

5. Ensure CI passes
6. Request review from maintainers

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Check for code quality, tests, and documentation
- Verify functionality works as expected
- Approve when all issues are resolved

### As a Contributor

- Respond to feedback promptly
- Make requested changes
- Update tests and documentation
- Keep PR scope focused

## Architecture Guidelines

### Directory Structure

```
iimage/
├── lib/              # Core library code
│   ├── detector.py   # Object detection logic
│   ├── validators.py # Input validation
│   ├── config.py     # Configuration
│   └── exceptions.py # Custom exceptions
├── api/              # REST API
│   ├── main.py       # FastAPI application
│   └── middleware.py # Custom middleware
├── tests/            # Test suite
└── examples/         # Usage examples
```

### Adding New Features

1. **Library Feature**: Add to `lib/` with tests
2. **API Endpoint**: Add to `api/main.py` with integration tests
3. **Documentation**: Update README.md and relevant docs
4. **Examples**: Add usage examples if applicable

### Error Handling

- Use custom exceptions from `lib/exceptions.py`
- Provide detailed error messages
- Include error context in logs
- Return appropriate HTTP status codes

### Logging

- Use structured logging from `lib/logging_config.py`
- Include relevant context (request_id, user_id, etc.)
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Avoid logging sensitive information

### Security

- Validate all inputs
- Use rate limiting for public endpoints
- Implement proper authentication for sensitive operations
- Keep dependencies updated
- Follow OWASP best practices

## Documentation

### Code Documentation

- Use Google-style docstrings
- Document all public APIs
- Include examples for complex functions
- Keep documentation up-to-date

### API Documentation

- Update OpenAPI schema (automatic via FastAPI)
- Add detailed descriptions for endpoints
- Include request/response examples
- Document error codes

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build Docker image
6. Create GitHub release
7. Deploy to production

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Contact maintainers for security issues

Thank you for contributing!
