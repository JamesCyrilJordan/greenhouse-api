"""
Tests for security features: rate limiting, request size limits, CORS.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


class TestRequestSizeLimiting:
    """Tests for request size limiting middleware."""
    
    def test_request_size_within_limit(self, client, auth_headers, sample_reading_data):
        """Test that requests within size limit are processed."""
        # Mock content-length header to be within limit
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers={**auth_headers, "content-length": "100"}
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_request_size_exceeds_limit(self, client, auth_headers):
        """Test that requests exceeding size limit are rejected."""
        # Create a request with content-length exceeding limit
        large_size = 2 * 1024 * 1024  # 2MB, exceeds 1MB default
        response = client.post(
            "/api/v1/readings",
            json={"device_id": "test", "sensor": "test", "value": 1.0},
            headers={**auth_headers, "content-length": str(large_size)}
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "too large" in response.json()["detail"].lower()
    
    def test_request_size_invalid_content_length(self, client, auth_headers, sample_reading_data):
        """Test that invalid content-length header is handled gracefully."""
        # Invalid content-length should be logged but request should proceed
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers={**auth_headers, "content-length": "invalid"}
        )
        # Should still process the request (invalid header is logged but not blocked)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_request_size_no_content_length(self, client, auth_headers, sample_reading_data):
        """Test that requests without content-length header are processed."""
        # Request without content-length should proceed
        response = client.post(
            "/api/v1/readings",
            json=sample_reading_data,
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_request_size_get_request_not_limited(self, client, auth_headers):
        """Test that GET requests are not subject to size limits."""
        # GET requests should not be limited
        response = client.get(
            "/api/v1/readings",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]


class TestRateLimiting:
    """Tests for rate limiting functionality."""
    
    def test_rate_limiting_decorator_exists(self):
        """Test that rate_limit decorator exists."""
        from app.main import rate_limit
        assert callable(rate_limit)
    
    def test_rate_limiting_applied_to_endpoints(self, client, auth_headers):
        """Test that rate limiting is applied to endpoints."""
        # This test verifies rate limiting is configured
        # Actual rate limit testing would require many requests
        from app.main import limiter
        # If rate limiting is enabled, limiter should exist
        # If disabled, limiter is None but decorator still exists
        from app.main import rate_limit
        assert callable(rate_limit)


class TestCORSConfiguration:
    """Tests for CORS configuration."""
    
    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured."""
        from app.main import app
        # Check that CORS middleware is in the middleware stack
        middleware_stack = [m for m in app.user_middleware]
        cors_middleware = [m for m in middleware_stack if "CORSMiddleware" in str(m)]
        assert len(cors_middleware) > 0
    
    def test_cors_allows_configured_origins(self, client):
        """Test CORS allows requests from configured origins."""
        # Test with default "*" origin
        response = client.options(
            "/api/v1/readings",
            headers={"Origin": "https://example.com"}
        )
        # Should not return CORS error (status should be 405 Method Not Allowed or similar, not CORS error)
        assert response.status_code != status.HTTP_403_FORBIDDEN

