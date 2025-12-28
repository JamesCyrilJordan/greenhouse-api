"""
Tests for main.py API endpoints.
"""
import pytest
from datetime import datetime, timezone
from fastapi import status


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_endpoint_no_auth(self, client):
        """Health endpoint should not require authentication."""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert "time" in data
        # Verify time is valid ISO format
        datetime.fromisoformat(data["time"].replace("Z", "+00:00"))


class TestCreateReading:
    """Tests for creating readings."""
    
    def test_create_reading_success(self, client, auth_headers, sample_reading_data):
        """Test successful reading creation."""
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["device_id"] == sample_reading_data["device_id"]
        assert data["sensor"] == sample_reading_data["sensor"]
        assert data["value"] == sample_reading_data["value"]
        assert data["unit"] == sample_reading_data["unit"]
        assert "id" in data
        assert "recorded_at" in data
    
    def test_create_reading_with_recorded_at(self, client, auth_headers):
        """Test creating reading with explicit recorded_at timestamp."""
        reading_data = {
            "device_id": "sensor-001",
            "sensor": "temperature",
            "value": 23.5,
            "unit": "celsius",
            "recorded_at": "2024-01-15T10:30:00Z"
        }
        response = client.post(
            "/api/v1/readings",
            json=reading_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["recorded_at"].startswith("2024-01-15")
    
    def test_create_reading_without_unit(self, client, auth_headers):
        """Test creating reading without unit (should default to empty string)."""
        reading_data = {
            "device_id": "sensor-001",
            "sensor": "temperature",
            "value": 23.5
        }
        response = client.post(
            "/api/v1/readings",
            json=reading_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unit"] == ""
    
    def test_create_reading_missing_auth(self, client, sample_reading_data):
        """Test creating reading without authentication."""
        response = client.post("/api/v1/readings", json=sample_reading_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing Bearer token" in response.json()["detail"]
    
    def test_create_reading_invalid_token(self, client, sample_reading_data):
        """Test creating reading with invalid token."""
        headers = {"Authorization": "Bearer wrong-token"}
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid token" in response.json()["detail"]
    
    def test_create_reading_invalid_bearer_format(self, client, sample_reading_data):
        """Test creating reading with invalid bearer format."""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_reading_validation_error_empty_device_id(self, client, auth_headers):
        """Test validation error for empty device_id."""
        reading_data = {
            "device_id": "",
            "sensor": "temperature",
            "value": 23.5
        }
        response = client.post(
            "/api/v1/readings",
            json=reading_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_reading_validation_error_missing_fields(self, client, auth_headers):
        """Test validation error for missing required fields."""
        reading_data = {
            "device_id": "sensor-001"
            # Missing sensor and value
        }
        response = client.post(
            "/api/v1/readings",
            json=reading_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListReadings:
    """Tests for listing readings."""
    
    def test_list_readings_empty(self, client, auth_headers):
        """Test listing readings when database is empty."""
        response = client.get("/api/v1/readings", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 100
        assert data["offset"] == 0
    
    def test_list_readings_with_data(self, client, auth_headers, multiple_readings):
        """Test listing all readings."""
        response = client.get("/api/v1/readings", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 4
        assert data["total"] == 4
        # Should be ordered by recorded_at desc
        assert data["items"][0]["id"] >= data["items"][1]["id"]
    
    def test_list_readings_filter_by_device_id(self, client, auth_headers, multiple_readings):
        """Test filtering readings by device_id."""
        response = client.get(
            "/api/v1/readings?device_id=sensor-001",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert all(item["device_id"] == "sensor-001" for item in data["items"])
    
    def test_list_readings_filter_by_sensor(self, client, auth_headers, multiple_readings):
        """Test filtering readings by sensor type."""
        response = client.get(
            "/api/v1/readings?sensor=temperature",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert all(item["sensor"] == "temperature" for item in data["items"])
    
    def test_list_readings_filter_by_both(self, client, auth_headers, multiple_readings):
        """Test filtering by both device_id and sensor."""
        response = client.get(
            "/api/v1/readings?device_id=sensor-001&sensor=temperature",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["device_id"] == "sensor-001"
        assert data["items"][0]["sensor"] == "temperature"
    
    def test_list_readings_pagination(self, client, auth_headers, multiple_readings):
        """Test pagination with limit and offset."""
        response = client.get(
            "/api/v1/readings?limit=2&offset=1",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 4
        assert data["limit"] == 2
        assert data["offset"] == 1
    
    def test_list_readings_limit_validation(self, client, auth_headers):
        """Test limit validation (must be between 1 and 2000)."""
        response = client.get(
            "/api/v1/readings?limit=0",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        response = client.get(
            "/api/v1/readings?limit=2001",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_readings_offset_validation(self, client, auth_headers):
        """Test offset validation (must be >= 0)."""
        response = client.get(
            "/api/v1/readings?offset=-1",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_readings_missing_auth(self, client):
        """Test listing readings without authentication."""
        response = client.get("/api/v1/readings")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_readings_invalid_token(self, client):
        """Test listing readings with invalid token."""
        headers = {"Authorization": "Bearer wrong-token"}
        response = client.get("/api/v1/readings", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

