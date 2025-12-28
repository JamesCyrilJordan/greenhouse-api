"""
Tests for security-related configuration in config.py.
"""
import pytest
import os
from unittest.mock import patch


class TestCORSConfiguration:
    """Tests for CORS origins configuration."""
    
    def test_cors_origins_default(self):
        """Test that CORS_ORIGINS defaults to ['*']."""
        from app.config import CORS_ORIGINS
        assert CORS_ORIGINS == ["*"]
    
    def test_cors_origins_single_origin(self):
        """Test CORS_ORIGINS with single origin."""
        with patch.dict(os.environ, {"CORS_ORIGINS": "https://example.com"}, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import CORS_ORIGINS
            assert CORS_ORIGINS == ["https://example.com"]
    
    def test_cors_origins_multiple_origins(self):
        """Test CORS_ORIGINS with multiple comma-separated origins."""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "https://example.com,https://app.example.com,https://admin.example.com"
        }, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import CORS_ORIGINS
            assert len(CORS_ORIGINS) == 3
            assert "https://example.com" in CORS_ORIGINS
            assert "https://app.example.com" in CORS_ORIGINS
            assert "https://admin.example.com" in CORS_ORIGINS
    
    def test_cors_origins_with_whitespace(self):
        """Test CORS_ORIGINS handles whitespace correctly."""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": " https://example.com , https://app.example.com "
        }, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import CORS_ORIGINS
            assert len(CORS_ORIGINS) == 2
            assert all(not origin.startswith(" ") and not origin.endswith(" ") for origin in CORS_ORIGINS)


class TestRateLimitConfiguration:
    """Tests for rate limiting configuration."""
    
    def test_rate_limit_enabled_default(self):
        """Test that rate limiting is enabled by default."""
        from app.config import RATE_LIMIT_ENABLED
        assert RATE_LIMIT_ENABLED is True
    
    def test_rate_limit_enabled_false(self):
        """Test rate limiting can be disabled."""
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "false"}, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import RATE_LIMIT_ENABLED
            assert RATE_LIMIT_ENABLED is False
    
    def test_rate_limit_per_minute_default(self):
        """Test default rate limit per minute."""
        from app.config import RATE_LIMIT_PER_MINUTE
        assert RATE_LIMIT_PER_MINUTE == 60
    
    def test_rate_limit_per_minute_custom(self):
        """Test custom rate limit per minute."""
        with patch.dict(os.environ, {"RATE_LIMIT_PER_MINUTE": "100"}, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import RATE_LIMIT_PER_MINUTE
            assert RATE_LIMIT_PER_MINUTE == 100


class TestRequestSizeConfiguration:
    """Tests for request size limit configuration."""
    
    def test_max_request_size_default(self):
        """Test default max request size (1MB)."""
        from app.config import MAX_REQUEST_SIZE
        assert MAX_REQUEST_SIZE == 1024 * 1024  # 1MB
    
    def test_max_request_size_custom(self):
        """Test custom max request size."""
        with patch.dict(os.environ, {"MAX_REQUEST_SIZE": "2048000"}, clear=False):
            import importlib
            import sys
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            from app.config import MAX_REQUEST_SIZE
            assert MAX_REQUEST_SIZE == 2048000

