"""
Tests for error handling in API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from app.main import create_reading, list_readings
from app.schemas import ReadingCreate
from app.models import Reading


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_create_reading_database_error(self, db_session, sample_reading_data):
        """Test handling of database errors when creating reading."""
        # Mock a database error
        mock_exception = SQLAlchemyError("Database connection failed")
        
        with patch.object(db_session, "commit", side_effect=mock_exception):
            payload = ReadingCreate(**sample_reading_data)
            
            # Mock the require_token dependency
            with patch("app.main.require_token", return_value=None):
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    create_reading(
                        payload=payload,
                        db=db_session,
                        _auth=None
                    )
                assert exc_info.value.status_code == 500
                assert "Failed to create reading" in exc_info.value.detail
    
    def test_create_reading_unexpected_error(self, db_session, sample_reading_data):
        """Test handling of unexpected errors when creating reading."""
        # Mock an unexpected error
        mock_exception = ValueError("Unexpected error")
        
        with patch.object(db_session, "add", side_effect=mock_exception):
            payload = ReadingCreate(**sample_reading_data)
            
            with patch("app.main.require_token", return_value=None):
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    create_reading(
                        payload=payload,
                        db=db_session,
                        _auth=None
                    )
                assert exc_info.value.status_code == 500
                assert "Internal server error" in exc_info.value.detail
    
    def test_list_readings_database_error(self, db_session):
        """Test handling of database errors when listing readings."""
        from app.models import Reading
        mock_exception = SQLAlchemyError("Query failed")
        
        # Create a mock query that raises an error
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.side_effect = mock_exception
        
        with patch.object(db_session, "query", return_value=mock_query):
            with patch("app.main.require_token", return_value=None):
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    list_readings(
                        device_id=None,
                        sensor=None,
                        limit=100,
                        offset=0,
                        db=db_session,
                        _auth=None
                    )
                assert exc_info.value.status_code == 500
                assert "Failed to retrieve readings" in exc_info.value.detail
    
    def test_list_readings_unexpected_error(self, db_session):
        """Test handling of unexpected errors when listing readings."""
        from app.models import Reading
        mock_exception = RuntimeError("Unexpected error")
        
        # Create a mock query that raises an error
        mock_query = MagicMock()
        mock_query.order_by.side_effect = mock_exception
        
        with patch.object(db_session, "query", return_value=mock_query):
            with patch("app.main.require_token", return_value=None):
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    list_readings(
                        device_id=None,
                        sensor=None,
                        limit=100,
                        offset=0,
                        db=db_session,
                        _auth=None
                    )
                assert exc_info.value.status_code == 500
                assert "Internal server error" in exc_info.value.detail

