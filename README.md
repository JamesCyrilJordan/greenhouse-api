# Greenhouse API

A RESTful API for managing greenhouse sensor readings, built with FastAPI and SQLAlchemy.

## Features

- 🔐 Bearer token authentication
- 📊 Sensor reading management (create and query)
- 🔍 Filtering by device ID and sensor type
- 📄 Pagination support
- 🏥 Health check endpoint
- 📝 Automatic API documentation
- 🔄 CORS enabled for cross-origin requests

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Example Requests](#example-requests)
- [Error Handling](#error-handling)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd greenhouse-api
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
# Required: API Bearer Token for authentication
API_TOKEN=your-secret-token-here

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./greenhouse.db
```

### Setting Up the API Token

1. **Generate a secure token**:
   You can generate a secure random token using Python:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Or use any secure random string generator. For example:
   ```bash
   openssl rand -hex 32
   ```

2. **Add the token to `.env`**:
   ```env
   API_TOKEN=your-generated-token-here
   ```

3. **Keep your token secure**:
   - Never commit the `.env` file to version control (it's already in `.gitignore`)
   - Use different tokens for development and production
   - Rotate tokens periodically

### Database Configuration

The API uses SQLite by default. To use PostgreSQL or another database, update `DATABASE_URL`:

```env
# PostgreSQL example
DATABASE_URL=postgresql://user:password@localhost/greenhouse

# MySQL example
DATABASE_URL=mysql+pymysql://user:password@localhost/greenhouse
```

**Note**: For PostgreSQL or MySQL, you'll need to install additional drivers:
```bash
# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install pymysql
```

## Running the Server

### Method 1: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 2: Using the run script
```bash
python run.py
```

### Method 3: Using Python module
```bash
python -m app
```

The server will start on `http://0.0.0.0:8000` (accessible at `http://localhost:8000`).

### Development vs Production

- **Development**: Use `--reload` flag for auto-reload on code changes
- **Production**: Remove `--reload` and use a production ASGI server like Gunicorn with Uvicorn workers:
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
  ```

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Understand authentication requirements

## Authentication

All API endpoints (except `/api/v1/health`) require Bearer token authentication.

### How to Use Bearer Tokens

Include the token in the `Authorization` header of your HTTP requests:

```
Authorization: Bearer your-api-token-here
```

### Getting Your Bearer Token

The bearer token is the value you set in the `.env` file as `API_TOKEN`. This is a shared secret token that all clients use to authenticate.

**Important**: 
- The token is configured server-side in the `.env` file
- All clients must use the same token to access the API
- For production, consider implementing per-client tokens or OAuth2

### Example: Setting Authorization Header

**cURL**:
```bash
curl -H "Authorization: Bearer your-api-token-here" \
     http://localhost:8000/api/v1/readings
```

**Python (requests)**:
```python
import requests

headers = {
    "Authorization": "Bearer your-api-token-here"
}
response = requests.get("http://localhost:8000/api/v1/readings", headers=headers)
```

**JavaScript (fetch)**:
```javascript
fetch('http://localhost:8000/api/v1/readings', {
  headers: {
    'Authorization': 'Bearer your-api-token-here'
  }
})
```

**Postman**:
1. Go to the "Authorization" tab
2. Select "Bearer Token" type
3. Enter your token in the "Token" field

## API Endpoints

### Health Check

**GET** `/api/v1/health`

Check if the API is running. No authentication required.

**Response**:
```json
{
  "status": "ok",
  "time": "2024-01-15T10:30:00.123456+00:00"
}
```

---

### Create Reading

**POST** `/api/v1/readings`

Create a new sensor reading. Requires authentication.

**Request Body**:
```json
{
  "device_id": "sensor-001",
  "sensor": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "recorded_at": "2024-01-15T10:30:00Z"  // Optional, defaults to current time
}
```

**Field Constraints**:
- `device_id`: Required, 1-64 characters
- `sensor`: Required, 1-64 characters
- `value`: Required, float
- `unit`: Optional, max 16 characters (defaults to empty string)
- `recorded_at`: Optional, ISO 8601 datetime (defaults to current UTC time)

**Response** (201 Created):
```json
{
  "id": 1,
  "device_id": "sensor-001",
  "sensor": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "recorded_at": "2024-01-15T10:30:00+00:00"
}
```

---

### List Readings

**GET** `/api/v1/readings`

Retrieve sensor readings with filtering and pagination. Requires authentication.

**Query Parameters**:
- `device_id` (optional): Filter by device ID
- `sensor` (optional): Filter by sensor type
- `limit` (optional): Number of results per page (1-2000, default: 100)
- `offset` (optional): Number of results to skip (default: 0)

**Example Requests**:
```
GET /api/v1/readings
GET /api/v1/readings?device_id=sensor-001
GET /api/v1/readings?sensor=temperature
GET /api/v1/readings?device_id=sensor-001&sensor=temperature
GET /api/v1/readings?limit=50&offset=0
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "device_id": "sensor-001",
      "sensor": "temperature",
      "value": 23.5,
      "unit": "celsius",
      "recorded_at": "2024-01-15T10:30:00+00:00"
    },
    {
      "id": 2,
      "device_id": "sensor-001",
      "sensor": "humidity",
      "value": 65.2,
      "unit": "percent",
      "recorded_at": "2024-01-15T10:31:00+00:00"
    }
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

**Response Fields**:
- `items`: Array of reading objects
- `total`: Total number of readings matching the filters
- `limit`: Number of results per page
- `offset`: Number of results skipped

## Example Requests

### Using cURL

**Health Check**:
```bash
curl http://localhost:8000/api/v1/health
```

**Create Reading**:
```bash
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor-001",
    "sensor": "temperature",
    "value": 23.5,
    "unit": "celsius"
  }'
```

**List All Readings**:
```bash
curl -H "Authorization: Bearer your-api-token-here" \
     http://localhost:8000/api/v1/readings
```

**List with Filters**:
```bash
curl -H "Authorization: Bearer your-api-token-here" \
     "http://localhost:8000/api/v1/readings?device_id=sensor-001&sensor=temperature&limit=10"
```

### Using Python

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "your-api-token-here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create a reading
reading_data = {
    "device_id": "sensor-001",
    "sensor": "temperature",
    "value": 23.5,
    "unit": "celsius"
}

response = requests.post(
    f"{BASE_URL}/api/v1/readings",
    json=reading_data,
    headers=headers
)
print(response.json())

# List readings
response = requests.get(
    f"{BASE_URL}/api/v1/readings",
    headers=headers,
    params={"device_id": "sensor-001", "limit": 10}
)
data = response.json()
print(f"Total readings: {data['total']}")
for reading in data['items']:
    print(f"{reading['sensor']}: {reading['value']} {reading['unit']}")
```

### Using JavaScript (Node.js)

```javascript
const fetch = require('node-fetch'); // or use native fetch in Node 18+

const BASE_URL = 'http://localhost:8000';
const TOKEN = 'your-api-token-here';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Create a reading
async function createReading() {
  const response = await fetch(`${BASE_URL}/api/v1/readings`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      device_id: 'sensor-001',
      sensor: 'temperature',
      value: 23.5,
      unit: 'celsius'
    })
  });
  const data = await response.json();
  console.log('Created:', data);
}

// List readings
async function listReadings() {
  const response = await fetch(
    `${BASE_URL}/api/v1/readings?device_id=sensor-001&limit=10`,
    { headers: headers }
  );
  const data = await response.json();
  console.log(`Total: ${data.total}`);
  data.items.forEach(reading => {
    console.log(`${reading.sensor}: ${reading.value} ${reading.unit}`);
  });
}
```

## Error Handling

The API returns standard HTTP status codes:

### Success Codes
- `200 OK`: Request successful (GET requests)
- `201 Created`: Resource created successfully (POST requests)

### Client Error Codes
- `401 Unauthorized`: Missing or invalid Bearer token
- `403 Forbidden`: Invalid token provided
- `422 Unprocessable Entity`: Validation error (invalid request body)
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

**Missing Token**:
```json
{
  "detail": "Missing Bearer token"
}
```

**Invalid Token**:
```json
{
  "detail": "Invalid token"
}
```

**Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "device_id"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Database Error**:
```json
{
  "detail": "Failed to create reading"
}
```

## Development

### Project Structure

```
greenhouse-api/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # Entry point for python -m app
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── db.py                # Database configuration
│   ├── auth.py              # Authentication logic
│   └── config.py            # Configuration management
├── .env                     # Environment variables (not in git)
├── .gitignore
├── requirements.txt
├── run.py                   # Simple run script
└── README.md
```

### Database

The database is automatically created on first run using SQLAlchemy's `create_all()`. For production, consider using Alembic migrations (already included in requirements).

### Logging

The API logs all operations and errors. Logs are output to stdout with INFO level by default.

## Security Considerations

1. **Token Security**: 
   - Use strong, randomly generated tokens
   - Never commit tokens to version control
   - Rotate tokens regularly
   - Use different tokens for different environments

2. **CORS**: 
   - Currently allows all origins (`*`) for development
   - In production, restrict to specific domains:
     ```python
     allow_origins=["https://yourdomain.com"]
     ```

3. **HTTPS**: 
   - Always use HTTPS in production
   - Never send tokens over unencrypted connections

4. **Rate Limiting**: 
   - Consider adding rate limiting for production use
   - Use tools like `slowapi` or API gateway rate limiting

## Troubleshooting

### Server won't start
- Check that `.env` file exists and contains `API_TOKEN`
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Authentication errors
- Verify the token in `.env` matches the token in your requests
- Check that the `Authorization` header format is correct: `Bearer <token>`
- Ensure there are no extra spaces in the token

### Database errors
- Check database file permissions (for SQLite)
- Verify `DATABASE_URL` is correct
- Ensure database driver is installed (for PostgreSQL/MySQL)

## Testing

The project includes a comprehensive test suite with 100% code coverage target.

### Running Tests

**Install test dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

**Run all tests**:
```bash
pytest
```

**Run tests with coverage report**:
```bash
pytest --cov=app --cov-report=term-missing
```

**Generate HTML coverage report**:
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

**Run specific test file**:
```bash
pytest tests/test_main.py
```

**Run specific test**:
```bash
pytest tests/test_main.py::TestHealthEndpoint::test_health_endpoint_no_auth
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_main.py            # API endpoint tests
├── test_auth.py            # Authentication tests
├── test_schemas.py         # Pydantic schema tests
├── test_models.py          # Database model tests
├── test_db.py              # Database configuration tests
├── test_config.py          # Configuration tests
└── test_error_handling.py  # Error handling tests
```

### Test Coverage

The test suite aims for 100% code coverage and includes:
- ✅ All API endpoints (health, create, list)
- ✅ Authentication and authorization
- ✅ Request validation
- ✅ Error handling (database errors, unexpected errors)
- ✅ Pagination and filtering
- ✅ Database operations
- ✅ Schema validation

### Using Make Commands

If you have `make` installed, you can use:

```bash
make test          # Run tests
make test-cov      # Run tests with coverage
make test-html      # Generate HTML coverage report
make clean          # Clean test artifacts
```

## License

[Add your license here]

## Support

[Add support/contact information here]

