# Testing Guide

This document provides detailed information about the test suite for the Greenhouse API.

## Overview

The test suite is designed to achieve **100% code coverage** and includes:
- Unit tests for all modules
- Integration tests for API endpoints
- Error handling tests
- Authentication and authorization tests
- Database operation tests

## Test Dependencies

The following packages are required for testing (included in `requirements.txt`):
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for testing (used by FastAPI TestClient)

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_main.py

# Run specific test class
pytest tests/test_main.py::TestHealthEndpoint

# Run specific test method
pytest tests/test_main.py::TestHealthEndpoint::test_health_endpoint_no_auth
```

### Coverage Commands

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html in your browser

# Generate XML coverage report (for CI/CD)
pytest --cov=app --cov-report=xml

# Fail if coverage is below 100%
pytest --cov=app --cov-fail-under=100
```

### Using pytest.ini Configuration

The `pytest.ini` file is configured to:
- Automatically run coverage on the `app` module
- Generate terminal, HTML, and XML coverage reports
- Fail if coverage is below 100%
- Use verbose output by default

So you can simply run:
```bash
pytest
```

And it will automatically include coverage reporting.

## Test Structure

### Test Files

1. **test_main.py** - Tests for API endpoints
   - Health check endpoint
   - Create reading endpoint
   - List readings endpoint
   - Authentication requirements
   - Validation errors
   - Pagination

2. **test_auth.py** - Authentication tests
   - Valid token acceptance
   - Invalid token rejection
   - Missing token handling
   - Case-insensitive bearer prefix
   - Timing attack protection

3. **test_schemas.py** - Pydantic schema validation
   - ReadingCreate validation
   - ReadingOut serialization
   - PaginatedReadings structure
   - Field constraints

4. **test_models.py** - Database model tests
   - Reading model creation
   - Default values
   - Database queries
   - Indexes

5. **test_db.py** - Database configuration tests
   - SQLite connection args
   - Session management
   - Base declarative

6. **test_config.py** - Configuration tests
   - Environment variable loading
   - Default values

7. **test_error_handling.py** - Error handling tests
   - Database error handling
   - Unexpected error handling
   - Proper error responses

### Fixtures (conftest.py)

The test suite uses several pytest fixtures:

- **`db_session`** - Creates a fresh in-memory database session for each test
- **`client`** - Creates a FastAPI TestClient with database override
- **`auth_headers`** - Provides authentication headers for requests
- **`sample_reading_data`** - Sample reading data for testing
- **`multiple_readings`** - Creates multiple test readings in the database

## Test Coverage Details

### Main Module (app/main.py)
- ✅ Health endpoint (no auth required)
- ✅ Create reading endpoint (with auth)
- ✅ List readings endpoint (with auth)
- ✅ Error handling (database errors, unexpected errors)
- ✅ Pagination (limit, offset)
- ✅ Filtering (device_id, sensor)
- ✅ Validation errors

### Auth Module (app/auth.py)
- ✅ Valid token acceptance
- ✅ Invalid token rejection
- ✅ Missing header handling
- ✅ Empty header handling
- ✅ Wrong prefix handling
- ✅ Case-insensitive bearer prefix
- ✅ Whitespace handling
- ✅ Timing attack protection (hmac.compare_digest)

### Schemas Module (app/schemas.py)
- ✅ ReadingCreate validation
- ✅ Field length constraints
- ✅ Required field validation
- ✅ Default values
- ✅ ReadingOut from_attributes
- ✅ PaginatedReadings structure

### Models Module (app/models.py)
- ✅ Reading creation
- ✅ Default values (unit, recorded_at)
- ✅ Database queries
- ✅ Index usage

### Database Module (app/db.py)
- ✅ SQLite connection args
- ✅ Session management
- ✅ Base declarative

### Config Module (app/config.py)
- ✅ Environment variable loading
- ✅ Default DATABASE_URL

## Writing New Tests

### Example: Testing a New Endpoint

```python
def test_new_endpoint_success(client, auth_headers):
    """Test successful request to new endpoint."""
    response = client.get("/api/v1/new-endpoint", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data

def test_new_endpoint_unauthorized(client):
    """Test endpoint requires authentication."""
    response = client.get("/api/v1/new-endpoint")
    assert response.status_code == 401
```

### Example: Testing Database Operations

```python
def test_create_model(db_session):
    """Test creating a new model."""
    model = MyModel(field="value")
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    
    assert model.id is not None
    assert model.field == "value"
```

## Continuous Integration

The test suite is designed to work in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml --cov-fail-under=100
```

## Troubleshooting

### Tests fail with "API_TOKEN is required"
Make sure the test environment sets `API_TOKEN` before importing app modules. This is handled in `conftest.py`.

### Database errors in tests
Tests use an in-memory SQLite database that's created fresh for each test. If you see database errors, check that fixtures are properly scoped.

### Coverage not reaching 100%
Run with `--cov-report=term-missing` to see which lines are not covered, then add tests for those lines.

### Import errors
Make sure you're running tests from the project root directory and that the virtual environment is activated.

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Fixtures**: Use fixtures for common setup/teardown
3. **Naming**: Use descriptive test names that explain what is being tested
4. **Coverage**: Aim for 100% coverage but focus on meaningful tests
5. **Speed**: Keep tests fast by using in-memory databases and mocking external services

