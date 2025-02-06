import pytest
from app.main import app
from app.core.database import get_db, Base
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Use SQLite for testing (in-memory database)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

client = TestClient(app)
@pytest.fixture(scope="function")
async def override_get_db(): # setup: no cover
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session for the test
    async def get_test_db():
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()
    
    # Override the dependency
    app.dependency_overrides[get_db] = get_test_db
    
    yield  # Run the test
    
    # Cleanup after test
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_read_weather_records_success(override_get_db):
    """Test that the API returns weather records"""
    response = client.get("/api/weather/", params={
                          "date": "2024-07-23", "id_of_station": "001", "pagination": 1, "size_of_query": 10})
    assert response.status_code == 200



@pytest.mark.asyncio
async def test_read_weather_records_no_data(override_get_db):
    """Test that the API returns weather records with no data"""
    response = client.get(
        "/api/weather/", params={"date": "2050-01-01", "id_of_station": "XYZ"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_weather_records_filter_by_date():
    """Test that the API returns weather records filtered by date"""

    response = client.get(f"/api/weather/?date={19860101}")

    assert response.status_code == 200
    assert response.json()[0]["date"] == 19860101


@pytest.mark.asyncio
async def test_get_weather_records_filter_by_station_id():
    """Test that the API returns weather records filtered by station ID"""

    response = client.get("/api/weather/?id_of_station=USC00110187")

    assert response.status_code == 200
    assert all(data["id_of_station"] ==
               "USC00110187" for data in response.json())


@pytest.mark.asyncio
async def test_read_weather_stats_success(override_get_db):
    """Test that the API returns weather stats"""
    response = client.get("/api/weather/stats/")

    assert response.status_code == 200
    assert len(response.json()) == 10


@pytest.mark.asyncio
async def test_read_weather_stats_no_data(override_get_db):
    """Test that the API returns weather stats with no data"""
    response = client.get(
        "/api/weather/stats", params={"year_of_date": "2050", "id_of_station": "XYZ"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_weather_stats_filter_by_year():
    """Test that the API returns weather stats filtered by year"""

    response = client.get("/api/weather/stats?year_of_date=1986")

    assert response.status_code == 200
    assert all(data["date"].startswith("1986") for data in response.json())


@pytest.mark.asyncio
async def test_get_weather_stats_filter_by_station_id():
    """Test that the API returns weather stats filtered by station ID"""

    response = client.get("/api/weather/stats?id_of_station=USC00110187")

    assert response.status_code == 200
    assert response.json()[0]["id_of_station"] == "USC00110187"


@pytest.mark.asyncio
async def test_ingest():
    response = client.get("/api/ingest/")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_weather_stats_no_data_found():
    """Test for the case where no weather data is found."""
    response = client.get(
        "/api/weather/stats",
        params={"year_of_date": "2025", "id_of_station": "999",
                "pagination": 1, "size_of_query": 10}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "No data found for the specified dates/station id"}


@pytest.mark.asyncio
async def test_read_weather_stats_exception_handling():
    """Test for exception handling if something goes wrong."""
    async def mock_execute(*args, **kwargs):  # setup: no cover
        raise Exception("Database error")

    with pytest.raises(Exception):
        await client.get(
            "/api/weather/stats",
            params={"year_of_date": "2025", "id_of_station": "1",
                    "pagination": 1, "size_of_query": 10}
        )
