"""
Tests for auth.py authentication module.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

from app.auth import require_token


class TestRequireToken:
    """Tests for the require_token dependency."""
    
    def test_require_token_valid(self):
        """Test with valid bearer token."""
        with patch("app.auth.API_TOKEN", "test-token-12345"):
            # Should not raise an exception
            require_token("Bearer test-token-12345")
    
    def test_require_token_missing_header(self):
        """Test with missing authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            require_token(None)
        assert exc_info.value.status_code == 401
        assert "Missing Bearer token" in exc_info.value.detail
    
    def test_require_token_empty_header(self):
        """Test with empty authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            require_token("")
        assert exc_info.value.status_code == 401
        assert "Missing Bearer token" in exc_info.value.detail
    
    def test_require_token_wrong_prefix(self):
        """Test with wrong prefix (not 'bearer ')."""
        with pytest.raises(HTTPException) as exc_info:
            require_token("Token test-token-12345")
        assert exc_info.value.status_code == 401
        assert "Missing Bearer token" in exc_info.value.detail
    
    def test_require_token_case_insensitive(self):
        """Test that bearer prefix is case-insensitive."""
        with patch("app.auth.API_TOKEN", "test-token-12345"):
            # Should work with lowercase
            require_token("bearer test-token-12345")
            # Should work with uppercase
            require_token("BEARER test-token-12345")
            # Should work with mixed case
            require_token("BeArEr test-token-12345")
    
    def test_require_token_invalid_token(self):
        """Test with invalid token."""
        with patch("app.auth.API_TOKEN", "correct-token"):
            with pytest.raises(HTTPException) as exc_info:
                require_token("Bearer wrong-token")
            assert exc_info.value.status_code == 403
            assert "Invalid token" in exc_info.value.detail
    
    def test_require_token_with_whitespace(self):
        """Test token extraction with whitespace."""
        with patch("app.auth.API_TOKEN", "test-token-12345"):
            # Should handle extra whitespace
            require_token("Bearer  test-token-12345  ")
            require_token("Bearer test-token-12345 ")
            require_token("Bearer  test-token-12345")
    
    def test_require_token_constant_time_comparison(self):
        """Test that hmac.compare_digest is used for timing attack protection."""
        with patch("app.auth.hmac") as mock_hmac:
            mock_hmac.compare_digest.return_value = True
            with patch("app.auth.API_TOKEN", "test-token"):
                require_token("Bearer test-token")
                # Verify hmac.compare_digest was called
                assert mock_hmac.compare_digest.called
                # Verify it was called with encoded strings
                call_args = mock_hmac.compare_digest.call_args[0]
                assert isinstance(call_args[0], bytes)
                assert isinstance(call_args[1], bytes)

