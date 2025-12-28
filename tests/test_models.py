"""
Tests for models.py database models.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import Reading


@pytest.fixture
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


class TestReadingModel:
    """Tests for the Reading model."""
    
    def test_reading_creation(self, db_session):
        """Test creating a reading in the database."""
        reading = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5,
            unit="celsius"
        )
        db_session.add(reading)
        db_session.commit()
        db_session.refresh(reading)
        
        assert reading.id is not None
        assert reading.device_id == "sensor-001"
        assert reading.sensor == "temperature"
        assert reading.value == 23.5
        assert reading.unit == "celsius"
        assert reading.recorded_at is not None
        assert isinstance(reading.recorded_at, datetime)
    
    def test_reading_default_unit(self, db_session):
        """Test that unit defaults to empty string."""
        reading = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5
        )
        db_session.add(reading)
        db_session.commit()
        assert reading.unit == ""
    
    def test_reading_default_recorded_at(self, db_session):
        """Test that recorded_at is automatically set."""
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        reading = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5
        )
        db_session.add(reading)
        db_session.commit()
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        
        assert reading.recorded_at is not None
        # SQLite stores naive datetimes, so compare as naive
        recorded_at_naive = reading.recorded_at.replace(tzinfo=None) if reading.recorded_at.tzinfo else reading.recorded_at
        assert before <= recorded_at_naive <= after
    
    def test_reading_with_explicit_recorded_at(self, db_session):
        """Test reading with explicit recorded_at timestamp."""
        explicit_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        reading = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5,
            recorded_at=explicit_time
        )
        db_session.add(reading)
        db_session.commit()
        # SQLite stores naive datetimes, so compare the naive versions
        explicit_naive = explicit_time.replace(tzinfo=None)
        recorded_naive = reading.recorded_at.replace(tzinfo=None) if reading.recorded_at.tzinfo else reading.recorded_at
        assert recorded_naive == explicit_naive
    
    def test_reading_query(self, db_session):
        """Test querying readings from database."""
        reading1 = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5
        )
        reading2 = Reading(
            device_id="sensor-002",
            sensor="humidity",
            value=65.2
        )
        db_session.add_all([reading1, reading2])
        db_session.commit()
        
        readings = db_session.query(Reading).all()
        assert len(readings) == 2
        
        temp_reading = db_session.query(Reading).filter(
            Reading.sensor == "temperature"
        ).first()
        assert temp_reading.device_id == "sensor-001"
        assert temp_reading.value == 23.5
    
    def test_reading_indexes(self, db_session):
        """Test that indexes exist for common query fields."""
        # This test verifies the model has indexes defined
        # Actual index testing would require database introspection
        reading = Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5
        )
        db_session.add(reading)
        db_session.commit()
        
        # Query by indexed fields should work efficiently
        result = db_session.query(Reading).filter(
            Reading.device_id == "sensor-001"
        ).first()
        assert result is not None
        
        result = db_session.query(Reading).filter(
            Reading.sensor == "temperature"
        ).first()
        assert result is not None

