import os
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Force testing environment before loading Settings
os.environ["ENVIRONMENT"] = "testing"
os.environ["LOG_LEVEL"] = "WARNING"

from app.main import app
from app.database.base import Base
from app.database.session import get_db

# Create a test-specific engine with NullPool to prevent event loop sharing errors
test_engine = create_async_engine(
    "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true",
    poolclass=NullPool
)
test_session = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provides a TestClient instance for route verification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


async def mock_async_true() -> bool:
    return True


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mocks external network health checks for testing isolation."""
    monkeypatch.setattr("app.api.v1.routes.health.check_supabase_connection", mock_async_true)
    monkeypatch.setattr("app.api.v1.routes.health.check_storage_connection", mock_async_true)


@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop to prevent 'attached to a different loop' errors."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(event_loop):
    """Autouse session-scoped fixture that builds and tears down the database schema."""
    # Open and hold a connection to prevent SQLite from discarding the shared memory DB when connection count drops to zero
    keep_alive_conn = event_loop.run_until_complete(test_engine.connect())

    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    event_loop.run_until_complete(create_tables())
    yield
    event_loop.run_until_complete(drop_tables())
    event_loop.run_until_complete(keep_alive_conn.close())


@pytest.fixture(autouse=True)
def override_db_dependency(monkeypatch):
    """Overrides the global database session dependency with our test-specific session."""
    async def _get_test_db():
        async with test_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _get_test_db
    monkeypatch.setattr("app.database.session.async_session", test_session)
    yield
    app.dependency_overrides.clear()
