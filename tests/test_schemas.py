"""
Tests for schemas.py Pydantic models.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas import ReadingCreate, ReadingOut, PaginatedReadings


class TestReadingCreate:
    """Tests for ReadingCreate schema."""
    
    def test_reading_create_valid(self):
        """Test valid reading creation."""
        data = {
            "device_id": "sensor-001",
            "sensor": "temperature",
            "value": 23.5,
            "unit": "celsius"
        }
        reading = ReadingCreate(**data)
        assert reading.device_id == "sensor-001"
        assert reading.sensor == "temperature"
        assert reading.value == 23.5
        assert reading.unit == "celsius"
        assert reading.recorded_at is None
    
    def test_reading_create_with_recorded_at(self):
        """Test reading creation with recorded_at timestamp."""
        recorded_at = datetime.now(timezone.utc)
        data = {
            "device_id": "sensor-001",
            "sensor": "temperature",
            "value": 23.5,
            "recorded_at": recorded_at
        }
        reading = ReadingCreate(**data)
        assert reading.recorded_at == recorded_at
    
    def test_reading_create_default_unit(self):
        """Test that unit defaults to empty string."""
        data = {
            "device_id": "sensor-001",
            "sensor": "temperature",
            "value": 23.5
        }
        reading = ReadingCreate(**data)
        assert reading.unit == ""
    
    def test_reading_create_validation_device_id_too_short(self):
        """Test validation error for device_id too short."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(
                device_id="",
                sensor="temperature",
                value=23.5
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("device_id",) for error in errors)
    
    def test_reading_create_validation_device_id_too_long(self):
        """Test validation error for device_id too long."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(
                device_id="a" * 65,  # 65 characters, max is 64
                sensor="temperature",
                value=23.5
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("device_id",) for error in errors)
    
    def test_reading_create_validation_sensor_too_short(self):
        """Test validation error for sensor too short."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(
                device_id="sensor-001",
                sensor="",
                value=23.5
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("sensor",) for error in errors)
    
    def test_reading_create_validation_sensor_too_long(self):
        """Test validation error for sensor too long."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(
                device_id="sensor-001",
                sensor="a" * 65,  # 65 characters, max is 64
                value=23.5
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("sensor",) for error in errors)
    
    def test_reading_create_validation_unit_too_long(self):
        """Test validation error for unit too long."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(
                device_id="sensor-001",
                sensor="temperature",
                value=23.5,
                unit="a" * 17  # 17 characters, max is 16
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("unit",) for error in errors)
    
    def test_reading_create_validation_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ReadingCreate(device_id="sensor-001")
        errors = exc_info.value.errors()
        # Should have errors for missing sensor and value
        error_locs = [error["loc"] for error in errors]
        assert ("sensor",) in error_locs
        assert ("value",) in error_locs


class TestReadingOut:
    """Tests for ReadingOut schema."""
    
    def test_reading_out_from_attributes(self):
        """Test ReadingOut can be created from ORM attributes."""
        # Simulate ORM object
        class MockReading:
            id = 1
            device_id = "sensor-001"
            sensor = "temperature"
            value = 23.5
            unit = "celsius"
            recorded_at = datetime.now(timezone.utc)
        
        mock_reading = MockReading()
        reading_out = ReadingOut.model_validate(mock_reading)
        assert reading_out.id == 1
        assert reading_out.device_id == "sensor-001"
        assert reading_out.sensor == "temperature"
        assert reading_out.value == 23.5
        assert reading_out.unit == "celsius"
        assert reading_out.recorded_at == mock_reading.recorded_at


class TestPaginatedReadings:
    """Tests for PaginatedReadings schema."""
    
    def test_paginated_readings_valid(self):
        """Test valid paginated readings."""
        items = [
            ReadingOut(
                id=1,
                device_id="sensor-001",
                sensor="temperature",
                value=23.5,
                unit="celsius",
                recorded_at=datetime.now(timezone.utc)
            ),
            ReadingOut(
                id=2,
                device_id="sensor-001",
                sensor="humidity",
                value=65.2,
                unit="percent",
                recorded_at=datetime.now(timezone.utc)
            )
        ]
        paginated = PaginatedReadings(
            items=items,
            total=100,
            limit=10,
            offset=0
        )
        assert len(paginated.items) == 2
        assert paginated.total == 100
        assert paginated.limit == 10
        assert paginated.offset == 0
    
    def test_paginated_readings_empty(self):
        """Test paginated readings with empty items."""
        paginated = PaginatedReadings(
            items=[],
            total=0,
            limit=100,
            offset=0
        )
        assert len(paginated.items) == 0
        assert paginated.total == 0

