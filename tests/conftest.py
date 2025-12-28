"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables before importing app modules
os.environ["API_TOKEN"] = "test-token-12345"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db import Base, get_db
from app.main import app
from app.models import Reading


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Return authorization headers for authenticated requests."""
    return {"Authorization": "Bearer test-token-12345"}


@pytest.fixture
def sample_reading_data():
    """Sample reading data for testing."""
    return {
        "device_id": "sensor-001",
        "sensor": "temperature",
        "value": 23.5,
        "unit": "celsius"
    }


@pytest.fixture
def multiple_readings(db_session):
    """Create multiple test readings in the database."""
    readings = [
        Reading(
            device_id="sensor-001",
            sensor="temperature",
            value=23.5,
            unit="celsius"
        ),
        Reading(
            device_id="sensor-001",
            sensor="humidity",
            value=65.2,
            unit="percent"
        ),
        Reading(
            device_id="sensor-002",
            sensor="temperature",
            value=25.0,
            unit="celsius"
        ),
        Reading(
            device_id="sensor-002",
            sensor="pressure",
            value=1013.25,
            unit="hPa"
        ),
    ]
    for reading in readings:
        db_session.add(reading)
    db_session.commit()
    return readings

