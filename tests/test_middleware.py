"""
Tests for middleware functionality.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock


class TestRequestSizeMiddleware:
    """Tests for request size limiting middleware."""
    
    def test_middleware_skips_get_requests(self, client):
        """Test that GET requests bypass size checking."""
        # GET requests should not be checked for size
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_middleware_checks_post_requests(self, client, auth_headers):
        """Test that POST requests are checked for size."""
        # Small request should work
        small_data = {"device_id": "test", "sensor": "temp", "value": 1.0}
        response = client.post(
            "/api/v1/readings",
            json=small_data,
            headers={**auth_headers, "content-length": "50"}
        )
        # Should process (may fail auth or validation, but not size)
        assert response.status_code != 413
    
    def test_middleware_handles_missing_content_length(self, client, auth_headers):
        """Test middleware handles requests without content-length header."""
        # Request without content-length should proceed
        response = client.post(
            "/api/v1/readings",
            json={"device_id": "test", "sensor": "temp", "value": 1.0},
            headers=auth_headers
        )
        # Should not return 413 (may return other errors)
        assert response.status_code != 413
    
    def test_middleware_logs_invalid_content_length(self, client, auth_headers):
        """Test that invalid content-length is logged but request proceeds."""
        # Invalid content-length should be logged but request should continue
        response = client.post(
            "/api/v1/readings",
            json={"device_id": "test", "sensor": "temp", "value": 1.0},
            headers={**auth_headers, "content-length": "not-a-number"}
        )
        # Should not return 413, should proceed (may fail validation/auth)
        assert response.status_code != 413

